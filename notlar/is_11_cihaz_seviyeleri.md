İş 11: Cihaz seviyeleri. Ana klasör proje kök dizini, `cd` ile başka klasöre geçme.

Tasarım (oku, 21.10 onaylı): tasarim/01_esyalar.md "Cihaz seviyeleri (21.10)", Bulaşık makinesi, Buzdolabı, Dolap;
tasarim/08_sayilar.md "Cihaz seviyeleri" (iki tablo); tasarim/03_calisma_sekilleri.md Yerleşim (Düzenle), Elektrik, Stok;
tasarim/09_ilerleme.md açılış tablosu (9: 2. seviye cihazlar, 19: 3. seviye cihazlar). Dekordaki satın alma sayfası ve
Yükselt düzeni (decor.gd, decor_screen.gd, edit_mode.gd) örnek alınacak; aynı dil ve davranış.

Sprite'lar hazır (oyun/assets/sprites, sprites.json): `<id>_s2`, `<id>_s3` ve `_cevrik`leri: ocak, izgara, firin,
doner_makinesi, fritoz, dondurma_makinesi, kahve_makinesi, bulasik_makinesi, buzdolabi, dolap. 1. seviye bugünkü
sprite'tır (`<id>`). DİKKAT: dolap_s3 iki hücre kaplar (modelci yeniden üretiyor; foot y yaklaşık -1.5..0.5, çevrikte x
-0.5..1.5; başlangıçtaki (0,2) çevrik dolap için ikinci hücre (0,3)). İkinci hücreyi sprite'ın foot'undan türet, sabit yazma.

İstenenler:
1. Veri: Dishes.SHOP'taki 7 pişirme cihazına seviyeler (fiyat ×2 / ×4; günlük elektrik ×1,5 / ×2, yarım yukarı; pişirme
   süresi ×0,75 / ×0,55). Başlangıç eşyaları (bulaşık makinesi, buzdolabı, dolap) için taban fiyat 1.200 / 1.000 / 600
   (satılmazlar, sadece yükseltme farkı için), bulaşık 8 tabak/10 sn → 12/8 → 16/6, depo buzdolabı 20/30/40 + dolap
   10/15/20. 08'deki tablolarla aynı olduğunu autotest denetlesin. Sayılar tek yerde dursun.
2. Oyun: Pişirme cihazının seviyesi o cihazdaki pişirme süresini kısaltır (doğrama aynı). Günlük elektrik (gün sonu,
   gün özeti) seviyeye göre. Bulaşık makinesinin bir seferde aldığı tabak ve yıkama süresi seviyeye göre. Depo
   (yemek başına porsiyon sınırı; bugün GameState.STOCK_CAPACITY 30) = buzdolabı + dolap kapasitesi: stok ekranı,
   sipariş sınırı ("en çok N"), bedava ilk stok (30, ama depoyu aşmasın), stok göstergesi bununla çalışsın.
   Seviye düşürülmediği için depo küçülmez; yine de depodan fazla stok varsa atılmaz, sadece yeni sipariş sınırlanır.
3. Mağaza: Mutfak sekmesinde cihaza dokununca dekordaki gibi satın alma sayfası: seviye seçimi (1-3), her seviyenin
   fiyatı, kilitli seviye görünür, "N. seviyede açılır" yazar, seçilemez; önizleme o seviyenin sprite'ı; "Al" o
   seviyeyle yerleştirme başlatır (var olan BuildMode düzeni). Mağaza satırında fiyat 1. seviyeninki. Kilitli cihaz
   (restoran seviyesi) bugünkü gibi. Açıkken zaman durur, Esc/geri kapatır. Üç ölçek ve üç arayüz boyutunda sığsın.
4. Düzenle: Pişirme cihazı ve başlangıçtaki bulaşık makinesi, buzdolabı, dolap seçilince "Yükselt" (fiyat farkı; para
   yetmezse var olan davranış; üst seviye kilitliyse düğme görünür, "N. seviyede açılır"; 3. seviyede "En üst seviye",
   devre dışı). Dolabı 3. seviyeye çıkarırken ikinci hücre boş ve uygun olmalı (yerleştirme kuralları: dolu, önü
   kapalı, ayrılmış hücre, yol kapanması); değilse "Yanında boş yer yok" ve para ödenmez. 3. seviye dolap taşınırken
   iki hücreyle yerleşir ve iki hücre de kontrol edilir; yol, gölge, isabet (tıklama ve bilgi kutucuğu) iki hücreyi
   kapsar. Başlangıç eşyalarının taşınıp kaldırılabilmesi bugünkü kurala göre (değiştirme).
5. Kaldırma: Ödenen paranın tamamı (alış + yükseltmeler) geri verilir; başlangıç eşyasında sadece yükseltmelere
   ödenen döner (bugün kaldırılamıyorsa bu durum oluşmaz).
6. Bilgi kutucuğu (info_tip.gd): pişirme cihazında "Sv. N · Elektrik X/gün" (bugünkü menü ve durum satırları
   kalsın); bulaşıkta "Sv. N · 12 tabak, 8 sn"; buzdolabı ve dolapta "Sv. N · Depo +20" gibi. Kısa tut, kutucuk
   çok genişlemesin.
7. İlerleme: progress.gd'de 9 ve 19'daki "2./3. seviye cihazlar" açılışları gerçekten çalışsın (kilitli gösterim,
   kutlama şeridi/paneli). Önceden açılmış (pre_unlocked) düzenine uyar.
8. Kayıt: Her konmuş cihazın ve başlangıç eşyasının seviyesi ve ödenen tutarı kaydedilir. SAVE_VERSION artırılır,
   _migrate_save/_apply_save düzeninde; eski kayıtta hepsi 1. seviye. Geçersiz seviye ya da 2 hücresi sığmayan
   3. seviye dolap (ör. elle bozulmuş kayıt) load_problems'a yazılır ve güvenli bir hâle düşer (1. seviye ya da 2.).
9. Performans: Kare başına iş eklenmesin.

Kabul ölçütü:
- `araclar/test.sh` üç ölçekte geçer, hata/uyarı satırı yok (Bash zaman aşımı 600000 ms).
- autotest denetimleri: 08 tablolarıyla aynı fiyat/elektrik/süre/tabak/depo; satın alma sayfasında seviye seçimi,
  kilitli seviye alınamaz (9 ve 19'da açılır); 2. seviye ocakta pişirme gerçekten ×0,75 (gerçek bir yemekte ölçülmüş);
  gün sonu elektrik seviyeye göre; Yükselt fark öder, kilitliyken olmaz, 3. seviyede devre dışı; bulaşık 2. seviyede
  12 tabak alır, 8 sn'de yıkar; depo buzdolabı+dolap toplamı (sipariş sınırı, stok ekranı); dolap 3. seviye: yanı
  doluyken yükseltilemez ve para ödenmez, boşken iki hücre kaplar, yol ve yerleştirme iki hücreyi sayar, taşınınca da;
  kaldırma iadesi (alış + yükseltmeler; başlangıç eşyasında sadece yükseltmeler); kutucuk satırları; kayıt turu ve
  eski sürümden geçiş, bozuk seviye kaydı.
- `--shots` (`--audio-driver Dummy`) PC ve 20:9: mağaza satın alma sayfası (kilitli seviyeyle), 2. ve 3. seviye
  cihazlar yerleşmiş (dolap 3. seviye iki hücre), Düzenle'de Yükselt (açık ve kilitli), "Yanında boş yer yok",
  kutucuk (ocak Sv. 2), stok ekranı (depo 45 gibi). Kendin bak, yolları yaz.
- README güncel. tasarim/ ve notlar/'a dokunma. Commit atma. Tasarımda karşılığı olmayan karar gerekirse dur, sor.
