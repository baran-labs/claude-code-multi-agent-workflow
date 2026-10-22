"""Ajan kaydı: Bir işte hangi alt ajanların gerçekten çalıştığını oturum kayıtlarından bulur.

Satır biçimi:
    Ajan kaydı: geliştirici ✓ · modelci – · test ✓ · inceleme ✓
    ✓ çalıştı (test için: son çalıştırma geçti) · ✗ test son çalıştırmada başarısız
    ? test çalıştı ama sonucu çıktıdan anlaşılamadı · – çalışmadı

Kapsam, kullanıcının son mesajından beri olanlardır; görev bildirimleri kullanıcı mesajı sayılmaz. Testler ana sohbetin, gelistirici'nin ve test-calistirici'nin çalıştırdığı
`araclar/test.sh` (ya da `--autotest`) komutlarıdır; inceleyici'nin deneme amaçlı testleri sayılmaz.

İki kullanım:
- Elle: `python3 araclar/ajan_kaydi.py` bu oturumun satırını yazar (oturumu CLAUDE_CODE_SESSION_ID'den bulur).
- Stop kancası (`--kanca`, .claude/settings.json): İş yapılan bir turun son mesajında satır yoksa Claude'un durmasını engeller
  ve kayıtlardan üretilen satırı eklemesini ister. Satırı kayıtlar belirler, Claude'un kendi beyanı değil.
"""
import glob
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

DEGISTIREN_ARACLAR = {"Agent", "Task", "Edit", "Write", "MultiEdit", "NotebookEdit"}
# En çok bu kadar kez durdurulur; sonra Claude'un durmasına izin verilir (sonsuz döngü olmasın).
EN_COK_ENGEL = 3


def zaman(kayit):
    return datetime.fromisoformat(kayit["timestamp"].replace("Z", "+00:00"))


def oku(yol):
    kayitlar = []
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            try:
                kayitlar.append(json.loads(satir))
            except ValueError:
                pass
    return [k for k in kayitlar if "timestamp" in k]


def icerik(kayit):
    c = (kayit.get("message") or {}).get("content")
    return [{"type": "text", "text": c}] if isinstance(c, str) else [b for b in c or [] if isinstance(b, dict)]


def kullanici_mesaji_mi(kayit):
    # Masaüstü uygulaması kullanıcı mesajını origin.kind = "human" diye işaretler, komut satırı hiç işaretlemez.
    # Görev bildirimleri gibi diğer kaynaklar sayılmaz.
    kaynak = kayit.get("origin")
    if kayit.get("type") != "user" or kayit.get("isMeta") or (kaynak and kaynak.get("kind") != "human"):
        return False
    bloklar = icerik(kayit)
    return bool(bloklar) and all(b.get("type") != "tool_result" for b in bloklar)


def son_kullanici_mesaji(kayitlar):
    mesajlar = [k for k in kayitlar if kullanici_mesaji_mi(k)]
    return mesajlar[-1] if mesajlar else None


def arac_cagrilari(kayitlar, baslangic):
    for k in kayitlar:
        if k.get("type") == "assistant" and zaman(k) >= baslangic:
            for b in icerik(k):
                if b.get("type") == "tool_use":
                    yield k, b


def arac_sonuclari(kayitlar):
    sonuclar = {}
    for k in kayitlar:
        for b in icerik(k):
            if b.get("type") == "tool_result":
                c = b.get("content")
                sonuclar[b.get("tool_use_id")] = c if isinstance(c, str) else "\n".join(
                    x.get("text", "") for x in c or [] if isinstance(x, dict))
    return sonuclar


def alt_ajanlar(oturum_klasoru, baslangic):
    """Bu turda çalışan alt ajanlar: [(tür, kayıtlar)]. Önceki turda başlayıp bu turda SendMessage ile devam
    eden ajan da sayılır (kayıtlarından biri bu turdaysa)."""
    bulunan = []
    for meta_yolu in glob.glob(os.path.join(oturum_klasoru, "subagents", "*.meta.json")):
        kayit_yolu = meta_yolu[:-len(".meta.json")] + ".jsonl"
        if not os.path.exists(kayit_yolu):
            continue
        kayitlar = oku(kayit_yolu)
        if any(zaman(k) >= baslangic for k in kayitlar):
            with open(meta_yolu, encoding="utf-8") as f:
                bulunan.append((json.load(f).get("agentType"), kayitlar))
    return bulunan


# Komutun bir parçasının başı: komutun başı ya da "&&", "||", ";", "|", "(" ve satır sonundan sonrası. Önünde ortam
# değişkeni (ZAMAN_ASIMI=400), time, bash, python ya da timeout olabilir (Linux, macOS ve Windows uyumlu).
_PARCA_BASI = (
    r"(?:^|&&|\|\||[;|(\n])\s*(?:\w+=\S*\s+)*"
    r"(?:(?:time|bash|sh|env|python3?|py(?:\s+-\S+)*|timeout(?:\s+-\S+)*\s+\d+\S*)\s+)*"
)
# araclar/test.sh ya da araclar/test.py'yi çalıştıran komut ("cd ... && araclar/test.sh pc", "python araclar/test.py");
# "git add araclar/test.sh" ya da "cat araclar/test.sh" sayılmaz.
TEST_SH = re.compile(_PARCA_BASI + r"(?:\S*[/\\])?araclar[/\\]test\.(?:sh|py)(?=$|[\s;&|)])")
# Godot'yu --autotest ile doğrudan çalıştıran komut ("godot --headless --path oyun -- --autotest").
AUTOTEST = re.compile(_PARCA_BASI + r"(?:\S*[/\\])?godot(?:\.exe)?\b[^;&|\n]*\s--autotest\b")


# Heredoc gövdesi (<<'EOF' ... EOF) ve tırnak içleri komut değil metindir (ör. commit mesajı).
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n[ \t]*\2[ \t]*(?=\n|$)", re.DOTALL)
TIRNAK = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")


def komut_kismi(komut):
    """Komutun çalıştırılan kısmı: heredoc gövdeleri ve tırnak içleri boşaltılır."""
    return TIRNAK.sub('""', HEREDOC.sub("<<metin", komut))


def test_isareti(komut, cikti):
    """Test çalıştıran komutun sonucu: ✓, ✗, ? ya da test çalıştırmıyorsa None. Sonuç çıktının son
    "SONUÇ:" (test.sh) ya da "AUTOTEST" (godot --autotest) satırından alınır."""
    komut = komut_kismi(komut)
    if TEST_SH.search(komut):
        satirlar = re.findall(r"^SONUÇ: (TAMAM|BAŞARISIZ)", cikti, re.MULTILINE)
    elif AUTOTEST.search(komut):
        satirlar = re.findall(r"^AUTOTEST (TAMAM|BAŞARISIZ)", cikti, re.MULTILINE)
    else:
        return None
    if not satirlar:
        return "?"
    return "✓" if satirlar[-1] == "TAMAM" else "✗"


def test_durumu(kayit_kumeleri, baslangic):
    """Son test çalıştırmasının işareti: ✓ geçti, ✗ başarısız, ? sonucu çıktıdan anlaşılamadı, – çalışmadı."""
    calismalar = []
    for kayitlar in kayit_kumeleri:
        sonuclar = arac_sonuclari(kayitlar)
        for k, b in arac_cagrilari(kayitlar, baslangic):
            if b.get("name") != "Bash":
                continue
            isaret = test_isareti(str((b.get("input") or {}).get("command", "")), sonuclar.get(b.get("id"), ""))
            if isaret is not None:
                calismalar.append((zaman(k), isaret))
    return max(calismalar)[1] if calismalar else "–"


def hesapla(oturum_yolu):
    """(iş yapıldı mı, satır, son kullanıcı mesajının kimliği)"""
    kayitlar = oku(oturum_yolu)
    mesaj = son_kullanici_mesaji(kayitlar)
    if mesaj is None:
        return False, None, None
    baslangic = zaman(mesaj)
    ajanlar = alt_ajanlar(oturum_yolu[:-len(".jsonl")], baslangic)
    turler = {tur for tur, _ in ajanlar}
    is_yapildi = bool(ajanlar) or any(
        b.get("name") in DEGISTIREN_ARACLAR or "git commit" in str((b.get("input") or {}).get("command", ""))
        for _, b in arac_cagrilari(kayitlar, baslangic))
    test = test_durumu([kayitlar] + [k for tur, k in ajanlar if tur != "inceleyici"], baslangic)

    def isaret(var):
        return "✓" if var else "–"

    satir = "Ajan kaydı: geliştirici {} · modelci {} · test {} · inceleme {}".format(
        isaret("gelistirici" in turler), isaret("esya-modelci" in turler), test, isaret("inceleyici" in turler))
    return is_yapildi, satir, mesaj.get("uuid")


def sade(metin):
    """Karşılaştırma için: markdown işaretleri ve boşluk farkları önemsiz."""
    metin = re.sub(r"[*`_>]", "", metin or "").replace("✔", "✓").replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", metin)


def kancaya_yetisti(oturum_yolu, son_mesaj):
    """Kayıt dosyası arkadan yazılır; son mesaj dosyaya geçene kadar biraz bekle."""
    iz = sade(son_mesaj).strip()[:60]
    for _ in range(10):
        metinler = [b.get("text", "") for k in oku(oturum_yolu)[-40:] if k.get("type") == "assistant"
                    for b in icerik(k) if b.get("type") == "text"]
        if not iz or iz in sade(" ".join(metinler)):
            return
        time.sleep(0.3)


def engel_sayisi(oturum, mesaj_kimligi):
    yol = os.path.join(tempfile.gettempdir(), "ajan_kaydi_%s.json" % oturum)
    try:
        with open(yol, encoding="utf-8") as f:
            sayac = json.load(f)
    except (OSError, ValueError):
        sayac = {}
    sayac[mesaj_kimligi] = sayac.get(mesaj_kimligi, 0) + 1
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(sayac, f)
    return sayac[mesaj_kimligi]


def kanca(girdi):
    if girdi.get("hook_event_name") != "Stop":
        return
    # Arka planda süren bir ajan ya da komut varsa iş bitmemiştir; rapor sonra gelecek.
    if any(g.get("status") in ("running", "pending") for g in girdi.get("background_tasks") or []):
        return
    oturum_yolu = girdi.get("transcript_path") or ""
    son_mesaj = girdi.get("last_assistant_message") or ""
    if not os.path.exists(oturum_yolu):
        return
    kancaya_yetisti(oturum_yolu, son_mesaj)
    is_yapildi, satir, mesaj_kimligi = hesapla(oturum_yolu)
    if not is_yapildi or sade(satir) in sade(son_mesaj):
        return
    if engel_sayisi(girdi.get("session_id", "oturum"), mesaj_kimligi) > EN_COK_ENGEL:
        return
    print(json.dumps({"decision": "block", "reason": (
        "Son mesajında ajan kaydı satırı yok ya da kayıtlarla uyuşmuyor. Bu satır oturum kayıtlarından "
        "üretildi; hiçbir şeyini değiştirmeden ayrı bir satır olarak yaz (sadece bu satırı yazman yeterli):\n"
        + satir)}, ensure_ascii=False))


def elle():
    oturum = os.environ.get("CLAUDE_CODE_SESSION_ID")
    ayar = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    yollar = glob.glob(os.path.join(ayar, "projects", "*", "%s.jsonl" % oturum)) if oturum else []
    if not yollar:
        sys.exit("Oturum kaydı bulunamadı (CLAUDE_CODE_SESSION_ID: %s)" % oturum)
    print(hesapla(yollar[0])[1])


if __name__ == "__main__":
    # Girdi sadece kanca olarak çalışırken okunur. Claude'un Bash'inde girdi açık kalır, okumaya kalkışmak takılır.
    if "--kanca" in sys.argv[1:]:
        kanca(json.loads(sys.stdin.read() or "{}"))
    else:
        elle()
