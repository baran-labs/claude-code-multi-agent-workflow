# Restoran Tycoon: Claude için çalışma notları

Kullanıcıyla Türkçe konuş. Genel bilgi ve komutlar `README.md`'de, onaylı tasarım kararları `tasarim/` altında,
sonraki oturumun notları `notlar/YARIN.md`'de.

## Kurallar
- Tasarım kararlarını (oyuncunun göreceği davranış, denge sayıları) kullanıcı verir. `tasarim/`'a sadece onaylananlar yazılır.
- Godot penceresi açılabilir (ör. `--shots` ile ekran görüntüsü). Pencereli çalıştırmada `--audio-driver Dummy` ver,
  ses aygıtı boşta kalsın. Otomatik testler (`araclar/test.sh`) yine `--headless` çalışır.
- Tam sprite üretiminden (~20-25 dk) önce kullanıcıya süreyi ve o sırada oyunun açılmayabileceğini söyle.
  Tek model birkaç saniye sürer.
- Testler: `araclar/test.sh` (önce içe aktarma, sonra üç ölçek aynı anda, ~35 sn, kısa özet). Sadece PC: `araclar/test.sh pc`.
  Bash'te zaman aşımını 600000 ms ver. Takılan testi script keser (DERLEME HATASI, TAKILDI, ZAMAN AŞIMI).
- Yeni sprite ya da `class_name`'li script eklenince içe aktarma gerekir: `araclar/ice_aktar.sh` (`test.sh` bunu kendisi yapar).
- Git: commit serbest, push yok.

## Kod haritası
`oyun/scripts/`:
- `main.gd`: sahne; dükkânı, çevreyi, eşyaları ve karakterleri kurar, dokunuşları yönetir
- `restaurant.gd`: müşteri döngüsü · `customer_group.gd`: 1-4 kişilik grup, sabır, puan
- `worker.gd`: yürüyen ve iş yapan karakter (oyuncu, çalışanlar, müşteriler, yayalar)
- `chef_ai.gd`, `waiter_ai.gd`: aşçının ve garsonun iş sırası · `player_jobs.gd`: oyuncunun dokunarak yaptığı işler
- `station.gd`, `table.gd`, `plate_stack.gd`: istasyonlar, masalar, tabak yığınları · `dishes.gd`: yemekler ve cihazları
- `game_state.gd` (autoload `GameState`): gün, para, hız, menü, stok, eşyalar, puan, kayıt
- `screen.gd` (autoload `Screen`): PC ve telefon ekran uyumu · `camera_rig.gd`: kamera
- `hud.gd`: arayüz · `menu_screen.gd`, `shop_screen.gd`, `stock_screen.gd`: menü, mağaza, stok ekranları
- `build_mode.gd`, `edit_mode.gd`, `cell_overlay.gd`: yerleştirme, düzenleme, hücre gösterimi
- `iso.gd`: izometrik ızgara · `sprite_db.gd`: `sprites.json` okuma · `start_layout.gd`: başlangıç dükkânı
- `neighborhood.gd`, `pedestrians.gd`: mahalle binaları, yayalar · `world_labels.gd`: dünyadaki yazılar
- `info_tip.gd`: üzerine gelince (telefonda basılı tutunca) açılan bilgi kutucuğu
- `ground_shadow.gd`: eşya ve dış süs gölgeleri · `sun_rays.gd`: güneş huzmeleri · `leaves.gd`: düşen yapraklar
- `autotest.gd`: otomatik test (README'de anlatılıyor)

`blender/sprite_uret.py`: bütün sprite'lar. Bölümler `# ---` satırlarıyla ayrılır, kayıtlar en alttaki `ITEMS` ve `CHARACTERS`'tadır.

Büyük dosyaları (`sprite_uret.py`, `main.gd`, `restaurant.gd`, `hud.gd`, `autotest.gd`) baştan sona okuma.
Önce `grep -n "^func \|^def \|^# ---"` ile yeri bul, sadece ilgili bölümü oku.

## İş bölümü
Bağlamı küçük tutmak için ana sohbet yönetir, işi alt ajanlar (`.claude/agents/`) yapar. Ana sohbet kullanıcıyla
konuşur, tasarım sorularını sorar, işi tarif eder, sonucu kontrol eder, commit atar ve `notlar/YARIN.md`'yi günceller.

- `gelistirici` (Opus): oyun kodundaki uygulama işleri. Tarifte ne istendiğini, ilgili `tasarim/` maddesini ve
  kabul ölçütünü yaz. Tasarım sorusu kalmadan gönder. Oyuncunun göreceği yeni bir davranış ya da seçenek, tek satır
  olsa bile buraya gider: testine denetim eklenir, `inceleyici` bakar. Kendin yapabileceklerin sadece davranışı
  değiştirmeyen düzeltmeler (yazım, yorum, belge) ve var olan testlerin zaten denediği küçük değişikliklerdir.
- `inceleyici` (Sonnet): `gelistirici`'nin her işinden sonra, commit'ten önce. Bulgu varsa düzeltme için aynı
  geliştiriciye geri gönder (SendMessage).
- `esya-modelci` (Sonnet): yeni ya da düzeltilecek statik model (eşya, dekor, yemek, cihaz seviyesi, bina).
  Kabul etmeden önce ürettiği PNG'ye kendin bak.
- `test-calistirici` (Haiku): testler sürerken başka bir işe devam etmek istediğinde. Çıktısı kısa olduğu için
  `araclar/test.sh`'yi kendin de çalıştırabilirsin.
- `Explore` (yerleşik): "şu nerede?" türü geniş kod aramaları.

Ana sohbette kalanlar: kullanıcıyla tasarım konuşması, birçok sistemi birlikte değiştiren büyük yeniden
düzenlemeler, kullanıcıyla adım adım yapılan görsel ayarlar, karakter iskeleti ve animasyonları.

Paralel çalışma: Zaman kazanmak için birbirinden bağımsız işleri aynı anda yaptır.
- `esya-modelci` ile geliştirme hattı (`gelistirici` → `inceleyici` → commit) aynı anda çalışabilir, farklı
  dosyalara dokunuyorlar. Örnek: bir özellik ve ona gereken sprite aynı anda.
- Geliştirme hattı sıralıdır: Bir geliştirici işi incelenip commit edilmeden yenisini başlatma. İki `gelistirici`
  ya da iki `esya-modelci`'yi aynı anda çalıştırma, aynı dosyaları düzenliyorlar.
- `Explore` ve `test-calistirici` her zaman paralel çalışabilir. Testler ve içe aktarma kilitle sırayla çalışır,
  her test kendi kayıt dosyasını kullanır; aynı anda çalışan ajanlar birbirinin testini bozmaz.
- Paralel iş sürerken `inceleyici`'ye incelenecek dosyaları ver. Commit'e sadece o işin dosyalarını ekle
  (`git add <dosyalar>`, `git add -A` değil).

Ajanlar kullanıcıya soru soramaz. Ajan bir soruyla dönerse soruyu kullanıcıya sor, cevabıyla işi aynı ajana geri gönder.

Ajanların modelini ve eforunu değiştirme. Tek istisna: zor bir hata ayıklama işinde `gelistirici`'yi `effort: max`
ile çağırabilirsin. Kullanıcı başka bir şey isterse onun dediği geçerli.

## Son rapor: ajan kaydı
İş yapılan (ajan çalışan, dosya değişen ya da commit atılan) her turun son mesajına `python3 araclar/ajan_kaydi.py`
çıktısını değiştirmeden ayrı bir satır olarak ekle. Örnek: `Ajan kaydı: geliştirici ✓ · modelci – · test ✓ · inceleme ✓`.
Satırı oturum kayıtları belirler: ✓ çalıştı (test: son çalıştırma geçti), ✗ test başarısız, ? test sonucu
anlaşılamadı, – çalışmadı. Satırı kendin yazma ya da düzeltme. Satır eksikse Stop kancası durmanı engeller ve
doğrusunu ister (`.claude/settings.json`).

## Bağlam düzeni
Her alt adım bitince: testler geçti → commit → `notlar/YARIN.md` güncel. Bağlam 400 bin tokena gelince sohbet
otomatik özetlenir (`.claude/settings.json`). Özetten sonra ayrıntılar notlardan ve commit'lerden okunur.
