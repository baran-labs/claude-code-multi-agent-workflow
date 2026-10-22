#!/usr/bin/env python3
"""Otomatik testler (Windows, macOS ve Linux uyumlu): Önce içe aktarma, sonra PC ve iki telefon ölçeğindeki testler
aynı anda (yaklaşık 35 sn).

Pencere açılmaz. Her test kendi test kaydını kullandığı için testler birbirini bozmaz. İçe aktarma sürerken testler
bekler, testler sürerken de içe aktarma bekler (araclar/.kilit).

Kullanım (herhangi bir klasörden):
    python3 araclar/test.py             # üç test
    python3 araclar/test.py pc 20:9     # sadece seçilenler: pc, 20:9, 16:9
"""
import glob
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "araclar"))
import ice_aktar  # noqa: E402

ARGS = {
    "pc": ["--path", "oyun", "--fixed-fps", "60", "--", "--autotest", "--win=1280x720", "--view=1920x1080"],
    "20:9": [
        "--path", "oyun", "--fixed-fps", "60", "--", "--autotest",
        "--win=1200x540", "--view=1333x600", "--ui-scale=1.8", "--touch",
    ],
    "16:9": [
        "--path", "oyun", "--fixed-fps", "60", "--", "--autotest",
        "--win=1280x720", "--view=1067x600", "--ui-scale=1.8", "--touch",
    ],
}
GODOT_HATA_RE = re.compile(r"^(USER )?(SCRIPT )?(ERROR|WARNING):")
DERLEME_RE = re.compile(r"Parse Error|Failed to load script")


def godot_kullanici_klasoru(proje_adi):
    """İşletim sistemine göre Godot app_userdata klasörü (Windows, macOS, Linux)."""
    if sys.platform == "win32":
        taban = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        return os.path.join(taban, "Godot", "app_userdata", proje_adi)
    if sys.platform == "darwin":
        return os.path.expanduser(f"~/Library/Application Support/Godot/app_userdata/{proje_adi}")
    xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(xdg, "godot", "app_userdata", proje_adi)


def surec_calisiyor_mu(pid):
    if os.name == "nt":
        cikti = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, check=False,
        ).stdout
        return str(pid) in cikti
    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except OSError:
        return False


def eski_test_kayitlarini_temizle():
    proje_dosyasi = os.path.join(KOK, "oyun", "project.godot")
    if not os.path.exists(proje_dosyasi):
        return
    proje_adi = None
    with open(proje_dosyasi, encoding="utf-8", errors="replace") as f:
        for s in f:
            m = re.match(r'^config/name="(.*)"$', s.strip())
            if m:
                proje_adi = m.group(1)
                break
    if not proje_adi:
        return
    klasor = godot_kullanici_klasoru(proje_adi)
    for yol in glob.glob(os.path.join(klasor, "test_kayit_*")):
        ad = os.path.basename(yol)[len("test_kayit_"):].split(".")[0]
        if ad.isdigit() and not surec_calisiyor_mu(int(ad)):
            try:
                if os.path.isdir(yol):
                    os.chmod(yol, stat.S_IRWXU)
                    shutil.rmtree(yol, ignore_errors=True)
                else:
                    os.remove(yol)
            except OSError:
                pass


def hata_satirlari(satirlar):
    cikti = []
    n = 0
    for s in satirlar:
        if GODOT_HATA_RE.search(s):
            cikti.append("      " + s.lstrip())
            n = 4
        elif n > 0 and re.match(r"^ +(at: |GDScript backtrace|\[[0-9]+\] )", s):
            cikti.append("      " + s.lstrip())
            n -= 1
        else:
            n = 0
    return cikti[:20]


def ana():
    adlar = sys.argv[1:] or ["pc", "20:9", "16:9"]
    for ad in adlar:
        if ad not in ARGS:
            print(f"Bilinmeyen test: {ad} (seçenekler: pc, 20:9, 16:9)")
            return 2

    rc = ice_aktar.calistir()
    if rc not in (0, 3):
        print("SONUÇ: BAŞARISIZ (içe aktarma)")
        return 1

    bekleme = int(os.environ.get("KILIT_BEKLEME", "600"))
    zaman_asimi = int(os.environ.get("ZAMAN_ASIMI", "300"))
    sessizlik = int(os.environ.get("SESSIZLIK", "120"))
    godot = os.environ.get("GODOT_BIN") or shutil.which("godot") or "godot"

    try:
        with ice_aktar.dosya_kilidi(ice_aktar.KILIT_YOLU, paylasimli=True, bekleme=bekleme):
            eski_test_kayitlarini_temizle()
            log_klasoru = tempfile.mkdtemp(prefix="test_log_")
            surecler = {}
            log_dosyalari = {}
            log_yollari = {}
            baslangiclar = {}
            bitisler = {}
            durumlar = {}

            def hepsini_durdur(*_):
                for p in surecler.values():
                    if p.poll() is None:
                        try:
                            p.kill()
                        except OSError:
                            pass

            eski_int = signal.signal(signal.SIGINT, lambda *_: (hepsini_durdur(), print("SONUÇ: BAŞARISIZ (durduruldu)"), sys.exit(130)))
            eski_term = signal.signal(signal.SIGTERM, lambda *_: (hepsini_durdur(), print("SONUÇ: BAŞARISIZ (durduruldu)"), sys.exit(143)))

            try:
                for ad in adlar:
                    log_yolu = os.path.join(log_klasoru, f"{ad.replace(':', '-')}.log")
                    log_yollari[ad] = log_yolu
                    log_f = open(log_yolu, "wb")
                    log_dosyalari[ad] = log_f
                    baslangiclar[ad] = time.monotonic()
                    surecler[ad] = subprocess.Popen(
                        [godot, "--headless"] + ARGS[ad],
                        cwd=KOK,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                    )

                kalan = len(adlar)
                while kalan > 0:
                    time.sleep(1)
                    simdi = time.monotonic()
                    for ad in adlar:
                        if ad in durumlar:
                            continue
                        proc = surecler[ad]
                        log_yolu = log_yollari[ad]
                        durum = None

                        with open(log_yolu, encoding="utf-8", errors="replace") as f:
                            icerik = f.read()

                        if proc.poll() is not None:
                            durum = proc.returncode
                        elif DERLEME_RE.search(icerik):
                            durum = "derleme"
                        elif simdi - baslangiclar[ad] >= zaman_asimi:
                            durum = 124
                        else:
                            try:
                                son_yazim = time.time() - os.path.getmtime(log_yolu)
                            except OSError:
                                son_yazim = 0
                            if son_yazim >= sessizlik:
                                durum = "sessiz"

                        if durum is None:
                            continue
                        if durum in ("derleme", "sessiz", 124) and proc.poll() is None:
                            proc.kill()
                            proc.wait()
                        log_dosyalari[ad].close()
                        durumlar[ad] = durum
                        bitisler[ad] = time.monotonic()
                        kalan -= 1
            finally:
                hepsini_durdur()
                for f in log_dosyalari.values():
                    if not f.closed:
                        f.close()
                signal.signal(signal.SIGINT, eski_int)
                signal.signal(signal.SIGTERM, eski_term)

            tamam = True
            for ad in adlar:
                durum = durumlar[ad]
                sure = int(bitisler[ad] - baslangiclar[ad])
                with open(log_yollari[ad], encoding="utf-8", errors="replace") as f:
                    satirlar = [s.rstrip("\r\n") for s in f]

                autotest_tamam = any(s.startswith("AUTOTEST TAMAM") for s in satirlar)
                godot_hatasi = any(GODOT_HATA_RE.search(s) for s in satirlar)

                if durum == 0 and autotest_tamam and not godot_hatasi:
                    print(f"{ad:<5} TAMAM      {sure:3d} sn")
                else:
                    tamam = False
                    if durum == "derleme":
                        print(f"{ad:<5} DERLEME HATASI {sure:3d} sn (test başlayamadı)")
                        for s in [x for x in satirlar if re.search(r"SCRIPT ERROR|ERROR:|at: ", x)][:12]:
                            print("      " + s.lstrip())
                    elif durum == "sessiz":
                        print(f"{ad:<5} TAKILDI    {sure:3d} sn ({sessizlik} sn çıktı yok, son satırlar)")
                        for s in satirlar[-15:]:
                            print("      " + s)
                    elif durum == 124:
                        print(f"{ad:<5} ZAMAN AŞIMI {sure:3d} sn (son satırlar)")
                        for s in satirlar[-15:]:
                            print("      " + s)
                    elif durum == 0:
                        if autotest_tamam:
                            print(f"{ad:<5} BAŞARISIZ  {sure:3d} sn (test geçti ama Godot hata ya da uyarı yazdı)")
                        else:
                            print(f"{ad:<5} BAŞARISIZ  {sure:3d} sn (çıkış 0 ama \"AUTOTEST TAMAM\" yok)")
                        for s in hata_satirlari(satirlar):
                            print(s)
                    else:
                        print(f"{ad:<5} BAŞARISIZ  {sure:3d} sn (çıkış {durum})")
                        for s in [x for x in satirlar if re.search(r"\[HATA\]|SCRIPT ERROR|ERROR:|WARNING:", x)][:20]:
                            print("      " + s.lstrip())

                for s in satirlar:
                    if "Görünür alan" in s:
                        print("      " + s.lstrip())
                        break
                for s in satirlar:
                    if "Gün özeti" in s:
                        print(("      " + s.lstrip())[:220])
                        break

            if tamam:
                print(f"SONUÇ: TAMAM (loglar: {log_klasoru})")
                return 0
            print(f"SONUÇ: BAŞARISIZ (loglar: {log_klasoru})")
            return 1
    except TimeoutError:
        print(f"Kilit {bekleme} sn içinde alınamadı: Bir içe aktarma sürüyor ya da takıldı (araclar/.kilit).")
        print("SONUÇ: BAŞARISIZ (kilit)")
        return 1


if __name__ == "__main__":
    sys.exit(ana())
