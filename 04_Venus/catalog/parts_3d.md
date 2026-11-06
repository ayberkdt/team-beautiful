# 3B mekanizma kataloğu

Üretildi: `node 04_Venus/code/visual/build_parts_catalog.mjs`. Elle değiştirmeyin.
Kaynak: Sunumatik `presets/venus_rotorcraft/arac/`. Tasarım: 0.8 · 38.226 kg. Bütün araç: 506 mesh, 129952 üçgen.

Kütle tasarım dosyasından, bileşen düzeyindedir. Alt parçaların yerleşimi ve oranı çizim seçimidir; ayrı kütleleri hesaplanmadı.

| Mekanizma | Kod | Kütle kg | Mesh | Üçgen | Boyut m |
|:---|:---|---:|---:|---:|:---|
| Pervane | `arac/pervane.mjs` | 5.40 (grup kütlesi, 6 rotora bölünür) | 21 | 6376 | 3.528 × 3.528 × 0.083 |
| Rotor göbeği | `arac/pervane.mjs` | 5.40 (grup kütlesi, 6 rotora bölünür) | 21 | 6376 | 3.528 × 3.528 × 0.083 |
| Tahrik kabı | `arac/tahrik.mjs` | 5.40 (grup kütlesi, 6 rotora bölünür) | 9 | 3632 | 0.252 × 0.209 × 0.249 |
| Katlanır kol | `arac/kol.mjs` | 7.66 (grup kütlesi, 6 rotora bölünür) | 26 | 4888 | 2.524 × 0.153 × 0.136 |
| Gövde ve termal | `arac/govde.mjs` | 3.86 (body + thermal) | 25 | 13792 | 0.743 × 0.743 × 0.329 |
| Batarya ve aviyonik | `arac/ic-donanim.mjs` | 7.02 (battery + avionics) | 29 | 6712 | 0.42 × 0.445 × 0.242 |
| Güneş güvertesi | `arac/gunes.mjs` | 4.01 (solar) | 66 | 3048 | 2.7 × 2.347 × 0.042 |
| Bilim yükü | `arac/yuk.mjs` | 0.50 (payload) | 9 | 3804 | 0.204 × 0.179 × 0.156 |
| Anten ve dizgin | `arac/anten-baglanti.mjs` | 1.60 (antenna + attach) | 22 | 5012 | 0.27 × 0.271 × 0.596 |

## Pervane

Kaldırma kuvveti üretir. İki pala, doğrusal burulma, katlanır kök.

- Pala: NACA tipi kesit, uca doğru incelir
- Hücum kenarı PFA şeridi
- Uç bandı
- Katlama mafsalı

## Rotor göbeği

Palaları mile bağlar. Kolektif hatve burada değişir; tutum denetimi bu yolla yapılır.

- Pala kavrama yuvası
- Hatve kolu ve çubuğu
- Dönen kolektif bilezik
- Ti mil

## Tahrik kabı

Motor gücünü 5:1 dişliyle rotora verir. Asitli havaya karşı tek kapalı kap.

- Sm₂Co₁₇ motor, soğutma kanatçıkları
- 5:1 gezegen dişli kabı
- PFA şaft contası
- ESC kutusu
- Kuyruk konisi

## Katlanır kol

Rotoru gövdeye bağlar. Kapsüle sığmak için iki yerden Z biçiminde katlanır.

- 80 mm CFRP tüp, FEP kılıf
- Kök ve orta Ti menteşe
- Burulma yayı, kilit bileziği
- Kablo kanalı
- Motor beşiği

## Gövde ve termal

İç donanımı asitten ve ısıdan korur. Isıyı kanatçıklara tek yönlü borudan atar.

- Ti basınçlı kap, bulonlu flanş
- Aerojel battaniye
- Değişken iletkenlikli ısı borusu
- Kanatçık halkası
- Kol yuvaları

## Batarya ve aviyonik

Gündüz güneş fazlasını depolar, gece uçuşu değil rezervi taşır. Uçuş bilgisayarı ve IMU burada.

- 14S8P hücre dizisi
- Bara ve BMS
- Kart yığını
- IMU ve barometre

## Güneş güvertesi

Uçuş gücünü üretir. Altı yaprak gövdeye doğru yukarı katlanır.

- Üç eklemli hücre, çift yüz
- Yaprak çerçevesi ve kaburga
- Menteşe mili
- Bağlantı kutusu

## Bilim yükü

Aerosolü ve bulut yapısını ölçer. Giriş ileri bakar, kamera aşağı.

- İzokinetik aerosol girişi
- Nefelometre kolları
- Safir pencereler
- Kamera kubbesi
- T/p/rüzgâr bumu

## Anten ve dizgin

Veriyi röle yörüngecisine yollar. Dizgin aracı paraşüt altında tutar, piro somunlar bırakır.

- UHF çapraz dipol
- Yer düzlemi radyalleri
- Radom
- Dizgin halkası ve üç kulak
- Piro somunlar

## Modelden çıkan tasarım notu

Kol tüpleri güvertenin altından geçer. Üst yüzü gölgelemez, arka yüzün 0.42 m²'sini kapatır: güverte alanının yaklaşık %9.4'i [K on Y].
Bu kayıp `aerokit.venus.power` içinde yoktur. Doc 25 §4.4 yalnız kabın gölgesini (%6) not eder. Arka yüz güç payı 0,42 olduğundan etkisi toplam güçte üst sınır olarak yaklaşık %4 olur; ışık yaygın olduğu için gerçek kayıp daha küçük olabilir, ölçülmedi.
