#!/usr/bin/env python3
"""Godot içe aktarması (Windows, macOS ve Linux uyumlu): Yeni sprite ya da class_name'li script eklenince gerekir.

Testler sürerken bekler, kendisi sürerken de testler bekler (kilit: araclar/.kilit).
Çıktıda ERROR satırı varsa godot'nun çıkış kodu 0 olsa da başarısız sayılır (çıkış 1).
Hatalar yalnızca betik derleme hatasıysa çıkış 3'tür: Varlıklar içe aktarıldı; test.py / test.sh testleri yine
başlatır ve hatanın dosya/satırını DERLEME HATASI olarak gösterir.

Kullanım (herhangi bir klasörden):
    python3 araclar/ice_aktar.py
    python araclar/ice_aktar.py
"""
from contextlib import contextmanager
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KILIT_YOLU = os.path.join(KOK, "araclar", ".kilit")

HATA_RE = re.compile(r"^(USER )?(SCRIPT )?ERROR")
BETIK_RE = re.compile(
    r"^(SCRIPT ERROR: (Parse|Compile) Error|ERROR: Failed to load script|"
    r"ERROR: Failed to create an autoload, script .* is not compiling)"
)


@contextmanager
def dosya_kilidi(yol, paylasimli=False, bekleme=600):
    """İşletim sistemine uygun dosya kilidi (POSIX'te fcntl.flock, Windows'ta msvcrt.locking)."""
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    f = open(yol, "a+b")
    f.seek(0, os.SEEK_END)
    if f.tell() == 0:
        f.write(b"\0")
        f.flush()
    f.seek(0)
    bitis = time.monotonic() + bekleme
    if os.name == "nt":
        import msvcrt
        while True:
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.monotonic() >= bitis:
                    f.close()
                    raise TimeoutError()
                time.sleep(0.2)
        try:
            yield
        finally:
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            f.close()
    else:
        import fcntl
        bayrak = (fcntl.LOCK_SH if paylasimli else fcntl.LOCK_EX) | fcntl.LOCK_NB
        while True:
            try:
                fcntl.flock(f.fileno(), bayrak)
                break
            except OSError:
                if time.monotonic() >= bitis:
                    f.close()
                    raise TimeoutError()
                time.sleep(0.2)
        try:
            yield
        finally:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            f.close()


def hata_ozeti(satirlar):
    cikti = []
    sonraki_at = False
    for s in satirlar:
        if HATA_RE.search(s):
            cikti.append(s)
            sonraki_at = True
        elif sonraki_at and re.match(r"^ +at: ", s):
            cikti.append(s)
            sonraki_at = False
        else:
            sonraki_at = False
    return cikti[:20]


def calistir():
    bekleme = int(os.environ.get("KILIT_BEKLEME", "600"))
    sure = int(os.environ.get("SURE", "300"))
    godot = os.environ.get("GODOT_BIN") or shutil.which("godot") or "godot"

    try:
        with dosya_kilidi(KILIT_YOLU, paylasimli=False, bekleme=bekleme):
            fd, log_yolu = tempfile.mkstemp(prefix="ice_aktar_", suffix=".log")
            os.close(fd)
            zaman_asimi = False
            try:
                with open(log_yolu, "wb") as log_f:
                    proc = subprocess.Popen(
                        [godot, "--headless", "--path", "oyun", "--import"],
                        cwd=KOK,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                    )
                    try:
                        rc = proc.wait(timeout=sure)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                        zaman_asimi = True
                        rc = 124
            except FileNotFoundError:
                print(f"İÇE AKTARMA BAŞARISIZ: '{godot}' komutu bulunamadı (log: {log_yolu})")
                return 1

            with open(log_yolu, encoding="utf-8", errors="replace") as f:
                satirlar = [s.rstrip("\r\n") for s in f]

            for s in hata_ozeti(satirlar):
                print(s)

            if zaman_asimi:
                print(f"İÇE AKTARMA BAŞARISIZ: {sure} sn içinde bitmedi (log: {log_yolu})")
                return 1

            hatalar = [s for s in satirlar if HATA_RE.search(s)]
            if rc == 0 and hatalar:
                if all(BETIK_RE.search(s) for s in hatalar):
                    print(
                        "İÇE AKTARMA BAŞARISIZ: Bir betik derlenmiyor (çıkış 3; dosya ve satırı test "
                        f"DERLEME HATASI olarak gösterir, log: {log_yolu})"
                    )
                    return 3
                print(f"İÇE AKTARMA BAŞARISIZ (çıkış 0 ama ERROR satırı var, log: {log_yolu})")
                return 1

            if rc == 0:
                print("İÇE AKTARMA TAMAM")
                try:
                    os.remove(log_yolu)
                except OSError:
                    pass
            else:
                print(f"İÇE AKTARMA BAŞARISIZ (çıkış {rc}, log: {log_yolu})")
            return rc
    except TimeoutError:
        print(
            f"İÇE AKTARMA BAŞARISIZ: Kilit {bekleme} sn içinde alınamadı; testler sürüyor ya da takıldı "
            "(araclar/.kilit)."
        )
        return 1


if __name__ == "__main__":
    sys.exit(calistir())
