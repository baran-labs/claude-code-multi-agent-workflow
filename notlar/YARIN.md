# Sonraki oturum için notlar (21.10.2026 güncellendi)

## 21.10 akşam: Cihaz seviyeleri (SÜRÜYOR)
Kullanıcı döndü: cila için "biraz belirginleştir" (huzme ve yaprak), sıradaki konu cihaz seviyeleri. Kararlar tasarim/01,
03, 08, 09'da (01bdf96): orta hız (pişirme ×0,75 / ×0,55, elektrik ×1,5 / ×2), fiyat 2 ve 4 kat, satın alma sayfası +
Düzenle'de Yükselt, bulaşık 12/8 → 16/6, depo buzdolabı 20/30/40 + dolap 10/15/20, 3. seviye dolap 2 hücre
(kullanıcı seçti; ikinci hücre model -Y, çevrikte game +y).
- İş 10 (geliştirici): huzmeleri ve yaprakları belirginleştir. BİTTİ (huzme 0.2, yaprak en az 14 px; inceleme temiz).
- Modelci: dolap_s3 iki hücre. BİTTİ (26e0a63; foot y -1.516..0.516, çevrikte x -0.516..1.516).
- İş 11 (geliştirici): cihaz seviyeleri. SÜRÜYOR. Tarif: notlar/is_11_cihaz_seviyeleri.md. İnceleme bitti, kesin hata
  yok (düşük notlar). Geliştiriciye son tur gönderildi: yorum yerleri, build_mode SHOP okuması, kilitli alımda
  _finish, uzun yazıların kısaltılması (yeni kural, tasarim/00) ve kullanıcı kararıyla (8628f3d) başlangıç eşyalarının
  taşınabilmesi. Bitince kısa inceleme (sadece bu tur), commit; devices.gd + .uid de eklenecek.
- Kullanıcı kararları 21.10: şefin kullandığı cihaz yükseltilebilir; bulaşık/buzdolabı/dolap taşınabilir, kaldırılamaz.
- Sonraki aday: oyunun geri kalanındaki uzun yazıların taranması (kısa yazı kuralı), öğretici ise MVP öncesi.
- Kullanıcının bildirdiği "temel 1. günde": hata değil, açık penceredeki eski kayıt (14.10, v4) 10. günde; "Sv 1" seviye.

## 21.10: Görsel cila (BİTTİ, kullanıcıya gösterildi; önce/sonra: notlar/cila_once_sonra.png)
Kullanıcı: İşler bitince bilgisayarı uyku moduna al (systemctl suspend). Sorun çıkan işi sonraya ertele; kullanıcı
bilgisayarın başına geçince haber verecek.
Kullanıcı oyunun cilalanmış bir resmini verdi (aynı sahne; adsız, kabartmalı arayüz, belirgin çizgi, canlı dış mekân,
ağaç gölgeleri, güneş huzmeleri, yapraklar). "Yüzde yüz aynısı olmak zorunda değil, yapılabileceklere kendin karar
ver" dedi. Kararlar tasarim/00 "Görsel cila (21.10)". Örnekteki şimşek/kahve baloncukları ve "Seviye 3" etiketi
yapılmadı (karşılığı olan kural yok).
- İş 8 (geliştirici): adlar yerine üzerine gelince bilgi kutucuğu (kullanıcı 21.10 istedi; telefonda kısa dokunuşta
  kısa süre, basılı tutunca sadece kutucuk; boş zeminde tutma yutulmaz), "Adlar: Üzerine gelince / Her zaman" ayarı,
  arayüz kabartması, altın ana düğme. BİTTİ (0c65256; inceleme 6 bulgu, düzeltildi). Testler artık ölçek başına ~30 sn.
- Sprite (ana sohbet, worktree scratchpad/wt_sprite, dal cila-sprite): OUTLINE_WIDTH 0.012 -> 0.026, TONES
  koyu taraf 0.70 -> 0.64, GRASS/LEAF canlı, dolgun ağaç ve çalı. Hata bulundu: iskele için ikinci `PLANK`
  tanımı salon parkesini eziyordu (tam üretimde parke sararırdı) -> SCAFFOLD_PLANK. Tam üretim BİTTİ (17,5 dk),
  c1f66b3, main'e birleşti (3c2de89), testler geçti. Worktree ve dal silindi.
- İş 9 (geliştirici): dış gölgeler, güneş huzmeleri, düşen yapraklar. BİTTİ (e6344f4; inceleme temiz, 3 küçük test
  sağlamlaştırması ana sohbette yapıldı). Geliştiricinin küçük kararları: dış gölge sağa-biraz arkaya (örnekteki gibi),
  koyuluk dış 0.42 / eşya 0.34 / ayak 0.42; yaprak ağaç başına 4-9 sn'de bir, en çok 10; huzme en parlak 0.12.
  Riskler: telefonda huzmeler sol üst panellerin altında kalıp neredeyse görünmüyor; en uzak görünümde yaprak çok küçük.
- Kullanıcıya sorulacak: cila beğenildi mi (huzme/yaprak yeterince görünür mü, kutucuk içerikleri), sonra sıradaki
  adaylar (aşağıda).

## 16-21.10: Tarama, düzeltmeler, arayüz, dekor, ilerleme (BİTTİ, kullanıcıya haber verildi)
Kullanıcı istekleri: projeyi taratıp düzelt; arayüze renk paletleri ve ayarlar; dekorasyonlar; oyunu uzun vadeye
hazırla (yemekler, cihazlar, menü ilerledikçe açılsın). Bitince kullanıcıya haber ver.

### İş sırası
Geliştirme hattı (ana klasör, sırayla; her biri gelistirici → inceleyici → commit):
1. Test düzeni ve telefon arayüzü: BİTTİ (f941666).
2. Yerleştirme ve karakter hataları: BİTTİ (c165ea0).
3. Kayıt ve durum: BİTTİ (8ed7e76). Bozuk kayıtta masasız dükkân, menü 3'ün altına düşüp kilitlenme, kapalıyken stok siparişinde
   kayıt yok, today["food"] kaydedilmiyor, load_game testi yok (kayıt turu, sürüm geçişi, bozuk dosya, append).
4a. İlerleme BİTTİ (38e94ad): seviye/deneyim, kutlama (serviste şerit + gün sonu panel), açılışlar ve kilitli gösterim,
   menü sınırı (en az 3, en çok seviye sınırı), sabit başlangıç menüsü, eski kayıt geçişi. Arayüz dalı birleşince başlar.
4b. Günlük görevler BİTTİ (106f7b2): 3 görev/gün, köşede liste, gün özetinde; yarım yukarı yuvarlanır.
5. Dekor sistemi BİTTİ (4fb9564): mağazada dekor, satın alma sayfası (renk + seviye), küçük/büyük halı, duvar süsleri
   (süsü dörtte birden fazla örten eşyanın önüne asılmaz), Düzenle'de Taşı/Kaldır/Yükselt/Renk, masa Görünümü, kayıt v7.
5b. Mağaza sekmeleri (Mutfak, Servis, Dekorasyon, Çalışanlar "Yakında") ve 10x hızın kaldırılması (tasarim/03, 08;
   kullanıcı 20.10'da oyunu deneyip istedi). BİTTİ. Çalışan satırlarında resim yok (işe almayla gelecek).
6. Yeni 10 yemek ve 3 cihaz (fritöz, dondurma makinesi, kahve makinesi) BİTTİ (kahve/dondurma tezgâhsız, "Hazırla").
7. Performans ve test eksikleri BİTTİ (619b7f2): world_labels değişince yerleşir; testler --fixed-fps 60 ve sabit
   tohumla ölçek başına ~12 sn, üç ölçek aynı sonucu verir; 21:00/22:00, tabak bitmesi, tezgâh dolu, kaçan sayısı
   denetimleri (senaryoyla, tohumdan bağımsız).
Sıradaki adaylar (kullanıcıya sorulacak): cihaz seviyeleri (sprite'lar hazır, hız/fiyat/elektrik sayıları yok),
çalışan işe alma (stok sorumlusu 5. sv; mağazada "Yakında"; çalışan resimleri yok), dükkân büyütme (10 ve 20. sv),
özel müşteriler, özel günler, şube. Kullanıcı oyunu deneyip bulgularını söyleyecek.
Arayüz işi BİTTİ, ana dala birleşti (c0fa268): paletler (varsayılan Gece bistro), ayarlar, duraklatma menüsü,
bozuk kayıt bildirimi, yeni oyun bütün kayıt dosyalarını siler (silinemezse yeni oyun başlamaz; 18.10 onaylandı, tasarim/00).
Modelci (sırayla): dekor seti BİTTİ (bitkiler, lambalar, halı, duvar süsleri, masa görünümleri; c3b4370..cde0f17)
→ fritöz, dondurma makinesi, kahve makinesi ve 10 yeni yemek BİTTİ (8624b96; adlar patates, mercimek, lahmacun,
salata, tavuk, falafel, padthai, paella, dondurma, kahve) → cihazların 2-3. seviye görünümleri `<ad>_s2/_s3` BİTTİ (8f4028a). Modelcide sırada iş yok. Dekor adları `<ad>_s<seviye>_<renk>`, `dekor_kayit()` ile.

### Kararlar (hepsi tasarim/'da)
- 00: geri tuşu Esc gibi, duraklatma menüsü, ayarlar, ipucu üstte, palet Gece bistro.
- 01/08: dekor seti, 3 seviye (fiyat ×2), renkler satın alma sayfasında, Yükselt, masa görünümü masa başına, fiyatlar.
- 03: eşyanın önü kapıya/kasaya gelemez; eksi para olabilir, iflas yok.
- 04/06/08/09: sabit başlangıç (pilav, spagetti, hamburger), 20 yemek, açılış tablosu, deneyim 75 + 45 × (n − 1),
  görev ödülü 30 deneyim + 300 para, seviye başına +%10.
- 18.10: menüde en çok N yemek (en az 3); kutlama ikisi birden; görev hedefleri seviyeyle büyür, köşede liste,
  "daha zor" (08'deki tablo); stok sorumlusu 5. seviyede açılır (02/03/06 düzeltildi).
- Sonra sorulacak: cihaz seviyelerinin hız/fiyatı, maaşlar, dükkân büyütme, özel müşteriler, özel günler, şube.
- Pencere açma yasağı kalktı (--shots serbest, --audio-driver Dummy ile); testler yine headless.
- Taslak kalan küçük yorum: Ayrılırken yıldız = 1 + int(sabır/20) (80-100 → 5); kullanıcıya sorulmadı.

Dünkü yarım iş (müşteri döngüsü) bugün bitti. Oyun artık baştan sona oynanıyor:
1. Menü sabit başlar (pilav, spagetti, hamburger; 4a ile). Sonra stok kutusuna dokunup açık yemeklerden seçilir.
2. Mağazadan cihazlar alınıp yerleştirilir; restoran açılır.
3. Müşteriler gelir, oturur, sipariş verir. Aşçı pişirir, garson servis eder.
4. Müşteriler yer ve kasada öder. Bulaşık yıkanır.
5. Gün özeti çıkar, sonraki güne geçilir.

## Bugün onaylanan kararlar (tasarim/ dosyalarına yazıldı)
- Ayrı servis tezgâhı: Şef yemeği tezgâha bırakır, garson oradan alır.
- 16 tabak. Bulaşık makinesi (1. seviye) bir seferde 8 tabak alır, 10 saniyede yıkar. Temiz tabak bitince şef bekler.
- 21:00'den sonra yeni müşteri gelmez. 22:00'de içeridekiler ödemeden ve puan vermeden gider.
- Stok sistemi gelene kadar malzeme parası, şef yemeğe başlarken düşülür.
- Oyun yavaş-orta akışta geçer; hızlar 1x, 2x, 5x (10x 20.10'da kalktı).
- Bütün taslak sayılar onaylandı (tasarim/08_sayilar.md). Başlangıç parası 5.000 yerine 4.000 oldu.
- Başlangıçtaki iki masa bilerek yetmez; oyuncunun masa alması beklenir.
- Claude'un küçük kararları onaylandı. İlgili belgelere yazıldı:
  - Grubun biri kasada öder.
  - Sabır yüzü grubun bir üyesinin başında durur.
  - Gece temizlik yapılır.
  - Oyuncu boşluk doldurur.
  - Giden müşterinin yemeği başka bir müşteriye ya da bulaşığa gider.
  - Menü seçilince ve kapalıyken yapılan her satın almada oyun kaydedilir.
  - Yerleştirme kuralları uygulanır.
  - 2 kişilik masa döndürülebilir.
  - Servis tezgâhına en çok 4 yemek konur.
- Mağaza gün içinde de açılır. Mağaza ve yerleştirme açıkken oyun durur.
- Yerleştirirken eşya fareyi izlemez: Tıklanan yerde durur, "Yerleştir" ile konur.
- Stok yemek başına porsiyon:
  - Oyun dolu stokla başlar.
  - Bilgisayardan sipariş verilir, mal ertesi sabah gelir.
  - Biten yemeği müşteri seçmez.
  - Malzeme parası siparişte ödenir (pişerken değil).
- Mahalle: Dış arsalarda günler geçtikçe temel, iskele ve bina olur (ilk arsa 10. gün temel, 30. gün bina). Sadece görüntü.
- Kullanıcının eski kaydı onun onayıyla silindi; yeni oyun 4.000 ile başlar.

## Hâlâ taslak olanlar (tasarim/'a yazılmadı)
- Yürüme hızları: çalışanlar 2,6, müşteriler 2,2 hücre/sn. Başlangıç çalışanları "kasten daha yavaş" olmalı (tasarim/02); sayı henüz yok.
- Yayaların sıklığı ve sayısı (sadece görüntü).
- Başlangıç dükkânının yerleşimi (eşyaların yerleri).
- Buzdolabı, dolap, bilgisayar, bileme taşı gibi eşyaların "işi" (stok ve bıçak sistemleri gelene kadar boş iş yapıyorlar).
- Depoya her yemekten en çok 30 porsiyon sığar (oyun bu kadarla başlar). Günde bir yemekten ~15-20 porsiyon gidiyor.
- Stok sipariş ekranı açıkken de oyun duruyor (mağazadaki kurala uydurdum).
- Mahalledeki diğer arsaların yerleri ve başlangıç günleri (25, 40, 55) ve bina çeşitleri (ev, apartman, dükkân).

## Sıradaki adımlar
- Kullanıcı 13.10'da: "MVP için biraz daha kapsamlı olmasını bekliyorum, biraz deneyip test edeceğim." Onun deneme sonuçlarını bekle; MVP kararı ondan.
- MVP'den önce öğretici (eğitim) eklenecek (kullanıcı 21.10); oyun içi yazılar kısa kalır, anlatım öğreticide (tasarim/00).
- MVP bitince Android APK:
  - ~1 GB Godot Android şablonu gerekiyor; indirmeden önce sor.
  - Bu makinede Java, adb ve ~/Android/Sdk var.
- Eşyayı taşıma ve satma (şimdilik konan eşya kalıcı).
- Sonraya kalanlar:
  - Stok sistemi (malzeme kararları gerekiyor)
  - Bıçağın körelmesi
  - Paket servis
  - Eğitim
  - Çalışan alma ve maaşlar

## Teknik notlar
- **Sprite üretimi:**
  - Tamamı ~20-25 dk sürer; başlamadan kullanıcıya haber ver.
  - Tek eşya birkaç saniye sürer (`-- servis_tezgahi` gibi) ve `sprites.json`'daki diğer kayıtları korur.
- Yeni `class_name`'li script eklenince önce `godot --headless --path oyun --import` çalıştır.
- **Test:**
  - Üç ölçekte çalıştır (README'de): PC, telefon 20:9, telefon 16:9.
  - Testler `--fixed-fps 60` ile oyun zamanında koşar (gerçek zamanı beklemez, sonuç her seferinde aynı; ~35 sn).
  - Oyunda çıkan her hata ve uyarı testi düşürür (`ErrorLog`).
- **Godot tuzakları:**
  - Silinmiş nesne tipli parametreye verilemez ("previously freed" hatası). Gidebilecek grup tipsiz parametreyle denetlenir.
  - `Node2D`'nin kendi `rotate()` fonksiyonu var; aynı adla fonksiyon yazılamaz.
- **Ölçümler** (bu makinede, Intel UHD 10. nesil, 1280x720 pencere, müşterilerle dolu an):
  - 60 FPS sabit; dikey eşitleme kapalıyken ~144 FPS.
  - Doku belleği 299 MB (pencereli otomatik test yazar). Çoğu karakter sayfaları ve mipmap'leri; düşük segment telefon için fazla.
  - APK'dan önce sayfaları küçültmeyi ya da VRAM sıkıştırmasını düşün.
