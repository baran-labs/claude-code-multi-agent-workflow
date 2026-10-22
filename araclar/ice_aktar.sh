#!/bin/bash
# Godot içe aktarması: Yeni sprite ya da class_name'li script eklenince gerekir; yoksa oyun açılmaz.
# Testler sürerken bekler, kendisi sürerken de testler bekler (kilit: araclar/.kilit, bkz. test.sh).
# Çıktıda ERROR satırı varsa godot'nun çıkış kodu 0 olsa da başarısız sayılır (çıkış 1). Hatalar yalnızca betik
# derleme hatasıysa çıkış 3'tür: Varlıklar içe aktarıldı; test.sh testleri yine başlatır, onlar hatanın dosya ve
# satırını DERLEME HATASI olarak gösterir. İçe aktarma SURE saniyeyi (varsayılan 300), kilit beklemesi
# KILIT_BEKLEME saniyeyi (varsayılan 600) geçerse durur.
#
# Kullanım (herhangi bir klasörden): araclar/ice_aktar.sh
set -u
cd "$(dirname "$0")/.."

# macOS (Darwin), Windows (Git Bash / MSYS) veya flock/timeout olmayan ortamlarda çapraz platform Python sürümünü çalıştır.
if [ "$(uname -s 2>/dev/null)" != "Linux" ] || ! command -v flock >/dev/null 2>&1 || ! command -v timeout >/dev/null 2>&1; then
    PY_BIN=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
    exec "$PY_BIN" araclar/ice_aktar.py "$@"
fi

exec 9> araclar/.kilit
if ! flock -x -w "${KILIT_BEKLEME:-600}" 9; then
    echo "İÇE AKTARMA BAŞARISIZ: Kilit ${KILIT_BEKLEME:-600} sn içinde alınamadı; testler sürüyor ya da takıldı (araclar/.kilit)."
    echo "Çalışan godot süreçleri: pgrep -a godot"
    exit 1
fi

HATA='^(USER )?(SCRIPT )?ERROR'
# Betik derlenmiyor: İçe aktarma çıktısı asıl hatanın yerini göstermez, test gösterir (DERLEME HATASI).
BETIK='^(SCRIPT ERROR: (Parse|Compile) Error|ERROR: Failed to load script|ERROR: Failed to create an autoload, script .* is not compiling)'

log=$(mktemp)
# --foreground: Ctrl-C godot'ya da ulaşsın (timeout kendi süreç grubunu kurmasın).
timeout --foreground "${SURE:-300}" godot --headless --path oyun --import > "$log" 2>&1
rc=$?
# Hata satırları, ardından gelen yer ("at:") satırlarıyla.
awk -v re="$HATA" '$0 ~ re { print; n = 1; next } n > 0 && /^ +at: / { print } { n = 0 }' "$log" | head -20
if [ $rc -eq 124 ]; then
    echo "İÇE AKTARMA BAŞARISIZ: ${SURE:-300} sn içinde bitmedi (log: $log)"
    exit 1
fi
if [ $rc -eq 0 ] && grep -a -q -E "$HATA" "$log"; then
    if ! grep -a -E "$HATA" "$log" | grep -a -q -v -E "$BETIK"; then
        echo "İÇE AKTARMA BAŞARISIZ: Bir betik derlenmiyor (çıkış 3; dosya ve satırı test DERLEME HATASI olarak gösterir, log: $log)"
        exit 3
    fi
    echo "İÇE AKTARMA BAŞARISIZ (çıkış 0 ama ERROR satırı var, log: $log)"
    exit 1
fi
if [ $rc -eq 0 ]; then
    echo "İÇE AKTARMA TAMAM"
    rm -f "$log"
else
    echo "İÇE AKTARMA BAŞARISIZ (çıkış $rc, log: $log)"
fi
exit $rc
