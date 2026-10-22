#!/bin/bash
# Otomatik testler: Önce içe aktarma, sonra PC ve iki telefon ölçeğindeki testler aynı anda (yaklaşık 35 sn).
# Pencere açılmaz. Her test kendi test kaydını kullandığı için testler birbirini bozmaz. İçe aktarma
# (araclar/ice_aktar.sh) sürerken testler bekler, testler sürerken de içe aktarma bekler (araclar/.kilit).
#
# Kullanım (herhangi bir klasörden):
#   araclar/test.sh             # üç test
#   araclar/test.sh pc 20:9     # sadece seçilenler: pc, 20:9, 16:9
#
# Her test için sonucu, süreyi ve hata satırlarını kısaca yazar. Çıkış kodu 0 ise hepsi geçti.
# Godot çıktısında ERROR, SCRIPT ERROR ya da WARNING satırı varsa test geçse de başarısız sayılır.
# Takılan test beklenmez: Derleme hatası (Parse Error) görülünce hemen, SESSIZLIK saniye (varsayılan 120) hiç
# çıktı gelmezse ya da toplam süre ZAMAN_ASIMI saniyeyi (varsayılan 300) geçerse durdurulur. Normal bir test
# ~15 sn sürer ve en çok ~3 sn sessiz kalır. Kilit KILIT_BEKLEME saniyede (varsayılan 600) alınamazsa çıkar.
# Ctrl-C ya da dışarıdan durdurulunca çalışan testler de durdurulur.
set -u
cd "$(dirname "$0")/.."

# Headless'ta --resolution işlemez (pencere 64x64 kalır); pencere boyutunu test --win= ile kendisi ayarlar.
# --view: beklenen görünür alan (arayüz ölçeği 1.8 olunca 1080 piksellik yükseklik 600'e iner).
# --fixed-fps 60: Her kare oyunun 1/60 saniyesidir (oyunun 60 FPS'i gibi), kareler gerçek zamanı beklemeden
# olabildiğince hızlı çizilir. Test her çalıştırmada aynı sonucu verir; makine yüklüyse sadece daha uzun sürer.
declare -A ARGS=(
    [pc]="--path oyun --fixed-fps 60 -- --autotest --win=1280x720 --view=1920x1080"
    [20:9]="--path oyun --fixed-fps 60 -- --autotest --win=1200x540 --view=1333x600 --ui-scale=1.8 --touch"
    [16:9]="--path oyun --fixed-fps 60 -- --autotest --win=1280x720 --view=1067x600 --ui-scale=1.8 --touch"
)
# Motorun ya da betiklerin hata ve uyarı satırları (autotest'in kendi hata kaydının yakalayamadıkları dahil).
GODOT_HATA='^(USER )?(SCRIPT )?(ERROR|WARNING):'
names=("$@")
[ ${#names[@]} -eq 0 ] && names=(pc 20:9 16:9)
for name in "${names[@]}"; do
    if [ -z "${ARGS[$name]+x}" ]; then
        echo "Bilinmeyen test: $name (seçenekler: pc, 20:9, 16:9)"
        exit 2
    fi
done

declare -A PIDS STARTS ENDS STATES
# Çıkarken (Ctrl-C, dıştaki zaman aşımı) testler arka planda kalıp kilidi tutmasın. timeout sinyali godot'ya iletir.
# İçe aktarma sırasında gelen sinyal o bitince işlenir; testlere geçilmez.
durdur() {
    local pid
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2> /dev/null
    done
}
trap durdur EXIT
trap 'echo "SONUÇ: BAŞARISIZ (durduruldu)"; exit 130' INT
trap 'echo "SONUÇ: BAŞARISIZ (durduruldu)"; exit 143' TERM HUP

# Çıkış 3: Sadece betik derleme hatası; testler başlar ve hatanın yerini DERLEME HATASI olarak gösterir.
araclar/ice_aktar.sh
rc=$?
if [ $rc -ne 0 ] && [ $rc -ne 3 ]; then
    echo "SONUÇ: BAŞARISIZ (içe aktarma)"
    exit 1
fi

# Godot'nun hata ve uyarı satırları, ardından gelen yer ("at:") ve geri izleme satırlarıyla.
hata_satirlari() {
    awk -v re="$GODOT_HATA" '$0 ~ re { print; n = 4; next }
        n > 0 && /^ +(at: |GDScript backtrace|\[[0-9]+\] )/ { print; n--; next } { n = 0 }' "$1" |
        head -n 20 | sed 's/^ */      /'
}

exec 9> araclar/.kilit
if ! flock -s -w "${KILIT_BEKLEME:-600}" 9; then
    echo "Kilit ${KILIT_BEKLEME:-600} sn içinde alınamadı: Bir içe aktarma sürüyor ya da takıldı (araclar/.kilit)."
    echo "Çalışan godot süreçleri: pgrep -a godot"
    echo "SONUÇ: BAŞARISIZ (kilit)"
    exit 1
fi

# Yarıda kesilen (zaman aşımı) testlerin kayıtları kalır; süreci artık çalışmayanları sil. Silinemeyen kayıt
# denemesinin klasörü (.kilitli) salt okunur kalmış olabilir.
user_dir="${XDG_DATA_HOME:-$HOME/.local/share}/godot/app_userdata/$(sed -n 's/^config\/name="\(.*\)"$/\1/p' oyun/project.godot)"
for f in "$user_dir"/test_kayit_*; do
    pid=${f##*/test_kayit_}
    pid=${pid%%.*}
    [[ $pid =~ ^[0-9]+$ ]] && ! kill -0 "$pid" 2> /dev/null && { [ -d "$f" ] && chmod u+w "$f"; rm -rf "$f"; }
done

logs=$(mktemp -d)
for name in "${names[@]}"; do
    STARTS[$name]=$(date +%s)
    # shellcheck disable=SC2086
    timeout "${ZAMAN_ASIMI:-300}" godot --headless ${ARGS[$name]} > "$logs/${name/:/-}.log" 2>&1 &
    PIDS[$name]=$!
done

# Testleri izle. STATES: çıkış kodu, "derleme" (derleme hatası) ya da "sessiz" (uzun süre çıktı yok).
running=${#names[@]}
while [ "$running" -gt 0 ]; do
    sleep 1
    for name in "${names[@]}"; do
        [ -n "${STATES[$name]:-}" ] && continue
        log="$logs/${name/:/-}.log"
        pid=${PIDS[$name]}
        state=""
        if ! kill -0 "$pid" 2> /dev/null; then
            wait "$pid"
            state=$?
        elif grep -a -q -E "Parse Error|Failed to load script" "$log"; then
            state=derleme
        elif [ $(( $(date +%s) - $(stat -c %Y "$log") )) -ge "${SESSIZLIK:-120}" ]; then
            state=sessiz
        fi
        [ -z "$state" ] && continue
        if [ "$state" = derleme ] || [ "$state" = sessiz ]; then
            kill "$pid" 2> /dev/null
            wait "$pid" 2> /dev/null
        fi
        STATES[$name]=$state
        ENDS[$name]=$(date +%s)
        running=$((running - 1))
    done
done
trap - EXIT

ok=1
for name in "${names[@]}"; do
    state=${STATES[$name]}
    log="$logs/${name/:/-}.log"
    took=$(( ENDS[$name] - STARTS[$name] ))
    if [ "$state" = 0 ] && grep -a -q "^AUTOTEST TAMAM" "$log" && ! grep -a -q -E "$GODOT_HATA" "$log"; then
        printf '%-5s TAMAM      %3d sn\n' "$name" "$took"
    else
        ok=0
        case "$state" in
            derleme)
                printf '%-5s DERLEME HATASI %3d sn (test başlayamadı)\n' "$name" "$took"
                grep -a -E "SCRIPT ERROR|ERROR:|at: " "$log" | head -n 12 | sed 's/^ */      /' ;;
            sessiz)
                printf '%-5s TAKILDI    %3d sn (%s sn çıktı yok, son satırlar)\n' "$name" "$took" "${SESSIZLIK:-120}"
                tail -n 15 "$log" | sed 's/^/      /' ;;
            124)
                printf '%-5s ZAMAN AŞIMI %3d sn (son satırlar)\n' "$name" "$took"
                tail -n 15 "$log" | sed 's/^/      /' ;;
            0)
                if grep -a -q "^AUTOTEST TAMAM" "$log"; then
                    printf '%-5s BAŞARISIZ  %3d sn (test geçti ama Godot hata ya da uyarı yazdı)\n' "$name" "$took"
                else
                    printf '%-5s BAŞARISIZ  %3d sn (çıkış 0 ama "AUTOTEST TAMAM" yok)\n' "$name" "$took"
                fi
                hata_satirlari "$log" ;;
            *)
                printf '%-5s BAŞARISIZ  %3d sn (çıkış %s)\n' "$name" "$took" "$state"
                grep -a -E "\[HATA\]|SCRIPT ERROR|ERROR:|WARNING:" "$log" | head -n 20 | sed 's/^ */      /' ;;
        esac
    fi
    grep -a -m1 "Görünür alan" "$log" | sed 's/^ */      /'
    grep -a -m1 "Gün özeti" "$log" | sed 's/^ */      /' | cut -c1-220
done

if [ $ok -eq 1 ]; then
    echo "SONUÇ: TAMAM (loglar: $logs)"
    exit 0
fi
echo "SONUÇ: BAŞARISIZ (loglar: $logs)"
exit 1
