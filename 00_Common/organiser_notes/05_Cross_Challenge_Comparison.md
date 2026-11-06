# 5. Görev karşılaştırması ve takım hazırlığı

**Kaynak sınıfları:** El yazısı notları, şirketlerin teknik faaliyetleri, AAIB/EASA/NASA/EUROCONTROL kaynakları.  
**Uyarı:** Aşağıdaki “beklenen ürün” ve “takım stratejisi” alanları **öneridir**, ek zorunlu görev şartı değildir.

## A. Sadece nottan kesin çıkarılabilen kapsam

| Görev | Ana konu | Notta açık geçen teslim/istek | Belirsiz olan |
|---|---|---|---|
| Ansys | Aircraft bracket redesign | Initial CAD; material selection report & comparison; initial Eco Audit; material cards | Yükler, geometri, malzeme sayısı (notta “3”), 3D baskı zorunluluğu |
| Advionics | Automated Approach Guidance | “Radar expertise”; “translate signal”; iletişim kesilmesi; “voice”, display | Asıl sinyal türü, tam arıza mı parazit mi, zorunlu teslim, data link kullanımı |
| EASA | Canopy alert retrofit | Bir örnek uçak seç; adım adım retrofit süreci; unlocked canopy events riskini azalt | Donanım/prototip kapsamı, bütçe ifadesinin pratik anlamı, belirsiz “word 1st” |
| LuGus | Venus rotorcraft | Altitude + atmosfer; rotor/propulsion/material/power/thermal/control/comms; teslim görseli; feasibility/risks | Kütle/operasyon süresi/araç tipi varyantları ve yazılım seviyesi |

## B. Teknik ağırlık ve hızlı teslim (editoryal değerlendirme)

| Görev | Başlıca disiplinler | Önemli güçlük | Güçlü gösterim |
|---|---|---|---|
| Ansys | CAD, FEA, malzeme, yaşam döngüsü | Sıcaklık ve yük altında anlamlı optimizasyon | Başlangıç/son geometri + mekanik ve Eco Audit kıyası |
| Advionics | Ses/sinyal işleme, yazılım, HMI, safety | Yanlış talimat verme ve veri kaynağı belirsizliği | Gürültü/kayıp senaryosunda çalışan kokpit arayüzü |
| EASA | Uçuş emniyeti, sensör, retrofit, insan faktörleri | Kilitli ile sadece kapalı olmayı ayırmak | Sensör mantığı + retrofit süreç akışı + arıza testleri |
| LuGus | Atmosfer fiziği, rotor aerodinamiği, görev tasarımı | Tutarlı sistem/kütle/güç/irtifa hesabı | Etiketli 3D eskiz + veri kaynaklı irtifa ve güç bütçesi |

## C. Görev seçerken dört kontrol sorusu

1. **Girdiler açık mı?** Ansys için yükler; Advionics için sinyal kaynağı; EASA için örnek uçak ve kilit geometrisi; LuGus için atmosfer profili.
2. **Çalışan küçük bir kanıt üretebilir miyiz?** Harika görünen bir sunumdan önce doğrulanabilir bir hesap, demo veya kontrollü test.
3. **En pahalı/önemli hata ne?** Ansys'de doğrulanmamış malzeme; Advionics'te yanlış clearance; EASA'da yanlış “LOCKED” göstergesi; LuGus'ta fiziki olarak karşılanamayan güç.
4. **Sunumda zorunlu ile opsiyoneli ayırdık mı?** Notta yazmayan analizi “resmî zorunluluk” diye anlatmayın.

## D. Önerilen dört kişilik rol bölüşümü (takım 4 kişi ise)

- **Mühendislik modeli:** Görev fiziği/sistem performansı ve sayısal doğrulama.
- **Prototip / CAD:** Görsel, arayüz, mekanik konsept veya simülasyon.
- **Kaynaklar / güvenlik:** Gereksinimler, hata modları, kaynak ve varsayım denetimi.
- **Sunum / entegrasyon:** Hikâye, kapsam yönetimi, sonuç kıyası ve görsel tutarlılık.

Ekip sayısı farklıysa görevleri birleştirin. Görevler **yarışma sırasında aynı zaman diliminde mi** veriliyor, bunu takvimden doğrulayın.

## E. Sunumda izlenecek güvenilir yapı

1. Problem ve hedef — 1 slayt.
2. Gereksinimler, sınırlar, ölçülen/varsayılan girdiler — 1 slayt.
3. Mühendislik yaklaşımı ve mimari — 1–2 slayt.
4. Sayısal sonuç / demo / hata testi — 1–2 slayt.
5. Kalan riskler, mümkün olmayan iddialar ve sonraki adım — 1 slayt.

**Ana ilke:** Çekici bir fikir ile **kanıtlanmış bir mühendislik sonucu** aynı şey değildir. İkisini ayrı etiketleyin.

## F. Son kontrol: Görev bazında kritik düzeltmeler

- **Ansys:** “300°C'ye dayanır” ifadesini gerçek malzeme verisi olmadan kullanmayın.
- **Advionics:** Tamamen kaybolmuş bir RF/voice mesajını sistem yeniden üretemez.
- **EASA:** G-MIIL vakasının AAIB kök nedenini eksik kilitlenme olarak anlatmayın.
- **LuGus:** NASA ile Skypersonic'in Mars **analog simülasyon** iş birliğini gerçek Mars uçuşu olarak sunmayın.

## G. Kaynaklar

Göreve özel birincil bağlantılar `00_README.md` ve ilgili Markdown dosyalarında listelenmiştir.
