# 03 · LuGus nasıl çalışıyor

Tarih: 2026-11-06. Etiket ve kaynak kodları: `sources.md`.

## 1. Ana fikir: uçuş yazılmıyor, parçalar simüle ediliyor

- Stüdyo, drone'un nasıl uçacağını senaryo olarak yazmadığını söylüyor. [D, S11]
- Her ana parça ayrı modelleniyor: LiPo batarya, motor, pervane, gövde, uçuş kontrolcüsü. [D, S11]
- Uçuş davranışı bu parçaların birlikte çalışmasından çıkıyor. [D, S11]
- Oyun motoru Unity; uçuş fiziğinin büyük bölümü stüdyonun kendi kodudur. [D, S11, N02, N05]

## 2. Fizik modeli: sürümler

Stüdyo fizik sürümlerini numaralandırıyor. Her sürümün konusu farklı. [D, S11]

- **Physics 1.0 (2015):** Senaryo yerine simülasyon temeli. [D, S11]
- **Physics 2.0 (2017):** Lift, RPM, drag, yer etkisi, propwash; Betaflight'tan esinli uçuş kontrolcüsü. [D, S11]
- **Physics 3.0 (2018):** Rüzgâr tüneli ve laboratuvar verisine dayalı yeni itki modelleri. [D, S11, N02]
- **Physics 4.0 (2020):** Drag'ın drone'un gerçek aerodinamik profiline göre yeniden yazılması. [D, S24, N03]
- **Physics 5.0 (2022):** Özel uçuş kontrolcüsü, A.I. PID ayarı, çoklu rate modeli. [D, N05]
- **Physics 6.0 (duyuru Kasım 2025, yayın Şubat 2026):** Drag yeniden, motor güç sınırı, pervane aerodinamiği, dinamik rüzgâr. [D, N07, N10]

Dikkat: 2018 notu oyun motoru fizik işlevlerini artık kullanmadıklarını söylüyor. [D, N02] 2022 notu ise Unity fiziğine daha az dayandıklarını söylüyor. [D, N05] İki cümle tam örtüşmüyor; "tamamen Unity dışı" demeyin. [Y]

## 3. Fizik modeli: sistemler

### Kuvvetler

- Dört kuvvet modelleniyor: ağırlık, itki, drag, lift. [D, S11]
- **Ağırlık:** Kütle seçilen parçalardan geliyor. [D, S11]
- **Yerçekimi:** Stüdyoya göre sabittir; ayar çubuğu gerekmez. Sayfanın ifadesi: "gravity needs no sliding". [D, S11]
- **İtki:** Parça verisinden yüklü motorun azami RPM'i, sonra statik itki, sonra dinamik itki çıkıyor. [D, S11]
- **Veri tabanı:** İtki modeli on binlerce laboratuvar test noktasına dayanıyor. [D, S11]
- **Dinamik itki:** Hava hızıyla düşüyor, belli hızda sıfıra iniyor, sonrasında negatif olabiliyor. [D, N02]
- **Yer etkisi:** Yüzey tipi, mesafe ve pervane adımına bağlı. [D, S11]
- **Drag:** Ana etken hız yönündeki izdüşüm alanıdır. [D, S11]
- **Hesap kısayolu:** 42 açı uçuştan önce hesaplanıyor, uçuşta enterpole ediliyor. [D, S11]
- **%98 sayısı:** Bu değer izdüşüm alanı örneklemesinin doğruluğudur; uçuş doğruluğu değildir. [D, S11] [Y]
- **Motor gücü:** Physics 6.0, gerçek dışı motor ve pervane kombinasyonlarını güç sınırına çekiyor. [D, N07, N10]

### Uçuş kontrolcüsü

- Sanal sensörler: jiroskop, ivmeölçer, GPS, barometre, irtifa sensörü. [D, S11]
- Stüdyoya göre en gelişmiş kontrolcü gerçek kontrolcüyle aynı hesabı yapıyor. [D, S11]
- A.I. PID ayarı otomatik; elle ayar da açık. [D, N05]
- Rate modelleri: Betaflight, Raceflight, Actual, Quick, KISS. [D, N05]

### Batarya

- LiPo boşalma eğrisi, akım çekişi, sürekli ve anlık C değerleri modelleniyor. [D, S11]
- Yük altında voltaj düşüşü (sag) ve ısı etkisi var. [D, S11]
- Sag özelliği 1.4.0 ile eklendi. [D, N05]
- 1.7.0 ile OSD'ye akım, çekilen mAh ve hücre başına voltaj geldi. [D, N10]

### Rüzgâr

- Physics 6.0 rüzgârı sabit kuvvet değil: Şiddet, türbülans ve yön değişiyor. [D, N07]
- Rüzgâr araziden ve binalardan etkileniyor. [D, S11, N07]
- Drone'a rüzgâra göre drag ve asimetrik pervane yükü olarak uygulanıyor. [D, S11]
- F10 ile rüzgâr görselleştirilebiliyor. [D, N10]
- Şimdilik yalnız tek oyunculu Free Flight modunda ve beş hazır ayarla sunuluyor. [D, N10]

### Sinyal ve kamera

- Video sinyali, konuma ve engellere göre bozuluyor. [D, S11]
- RC sinyal bozulması da simüle edilebiliyor; genelde yalnız endüstri ürünlerinde açılıyor. [D, S11]
- Lens etkisi gerçek FPV kamera bükülmesini taklit ediyor. [D, N07, N10]

### Kamuya açık olmayanlar

- Hava yoğunluğu ya da atmosfer modeli açıklanmıyor; yoğunluk yalnız lift anlatımında genel etken olarak geçiyor. [D, S11]
- Gecikme (latency) modeli anlatılmıyor. [D, S11]
- İtki, sag ya da propwash formülü yayımlanmamış. [D, S11]
- Yorum: Sayfadaki çerçeve Dünya'da küçük multirotor içindir. Başka bir gezegen için hangi parametrelerin açıldığı kamuya kapalıdır. [Y]

## 4. Doğrulama yöntemi

- Veri kaynakları: Bağımsız test laboratuvarları, rüzgâr tüneli verisi, CFD. [D, S11, S24, N02]
- Üretici veri sayfalarına güvenmiyorlar; parça değerlerini test verisine göre ölçekliyorlar. [D, N02]
- Yeni fizik önce Experimental Branch'e gidiyor; ana sürüme test sonucu iyiyse geçiyor. [D, N07, N08]
- Physics 6.0 için Discord'da adlandırılmış test pilotları var. [D, N08]
- Stüdyo pilot onayını son doğrulama olarak tanımlıyor. [D, N07, S25]
- Micro Drones testindeki temel soru sadeydi: Daha iyi hissettiriyor mu? [D, N15]
- Physics 4.0'da yarışçı ve freestyle pilotların beklentisi çelişti; stüdyo bunu açıkça yazdı. [D, N03]
- Eğitim programları için Physics 5.0 belirli süre ayrı dalda tutuluyor. [D, N10]
- Bağımsız doğrulama belgesi bulunamadı; bu iddialar stüdyonun kendi iddialarıdır. [D, S11]
- Pilot yorumları karışık: Bazı 2026 blog rehberleri Liftoff'u yumuşak ve bağışlayıcı buluyor. [A, S79]

## 5. Gerçek donanım, eğitim, B2B

### Gerçek FPV kumanda

- Liftoff oyunu için oyun kumandası ya da radyo kumandası gerekiyor. [D, S33]
- Steam metni vericilerle uyumu öne çıkarıyor. [D, S33]
- Gerçek ürünler parça olarak var: Marka ortaklığı olmadan parça ekleyemediklerini söylüyorlar. [D, S17, S18]

### Eğitim amaçlı kullanım

- Çok sayıda pilotun gerçek drone almadan önce Liftoff'ta başladığını söylüyorlar. [D, S18]
- Red Cat de ürünü pilot eğitim platformu olarak tanımlamış. [D, S41]
- Kasım 2022: Drone Legends ile lise öğrencilerine pilotaj eğitimi ortaklığı. [D, S05] Ayrıntılı bülten açılamadı (403).
- Aralık 2025: Stüdyo, sürümlerinin yapay zekâ eğitimi, NASA projesi, organ taşıma simülasyonu ve STEM eğitiminde kullanıldığını yazıyor. [D, N09]

### Liftoff Core örnekleri

- **University of Zurich Robotics & Perception Group (Ekim 2020):** Araştırmacılara ek araç ve veri veren özel sürüm. [D, S22]
- **IUDRO (Ağustos 2020):** Üniversiteler arası drone yarışı için e-spor sürümü, Steam Betas sekmesinden erişiliyor. [D, S23]
- **Skypersonic (Mayıs 2020):** Skycopter sahipleri için bağımsız simülatör; Skypersonic ilk Core ortağı. [D, S21]
- **Mars Drone Simulator:** `04_mars_drone_simulator.md`.
- **BeNeDrone:** Eylül 2025'te başlayan Interreg projesi, tıbbi taşıma ve sanal eğitim ortamı. [D, P02]
- Core motorunun faydası olarak on yıllık geliştirmeyi ve halka açık simülatörlerdeki doğrulamayı gösteriyorlar. [D, S12]
- Müşteri projelerinden öğrenilenlerin ana ürüne döndüğünü söylüyorlar. [D, N09]
- Yorum: İş modeli şudur: Kitlesel oyun motoru geliştirir ve sınar, B2B işi aynı motoru satar. [Y]

### Ukrayna (hassas konu)

- Şubat 2023'te Haelterman, Ukraynalılara yüzlerce Liftoff lisansı verdiklerini yazdı. [D, S09]
- Aynı yazı drone okullarına destek verdiklerini söylüyor. [D, S09]
- Yazıda Liftoff'un Rus propagandasında kullanıldığı görüntülerden şikâyet var. [D, S09]
- Arama özetleri askerî odaklı bir Liftoff sürümünden ve yüksek eğitim sayılarından söz ediyor; sayıları doğrulayamadım, kullanmayın. [A, S81]

## 6. Portfolyo: tüm projeler

Proje sayfası 21 proje gösteriyor. [D, S02] Aşağıdaki sayfaların hepsini açtım. Tarihler sayfadaki biçimdedir (GG/AA/YYYY). "Tarih yok" sayfada tarih görünmediğini söyler; görsel yükleme tarihini proje tarihi saymadım. Tablo başlığı benim sayımımdır. [Y]

**Portfolyodaki 21 projenin 11'i eğitim, sağlık veya kamu amaçlı; 5'i Liftoff tabanlı.**

| Proje | Tür | Müşteri veya ortak | Sayfadaki tarih | Konu | Kaynak |
|:---|:---|:---|:---|:---|:---|
| Runes of Brennos | Kendi oyunu | — | 01/01/2015 | Çok oyunculu rün savaşı | P19 |
| Battle for Donetsk | Kendi oyunu, güncel konu | — | 19/03/2015 | Savaş karşıtı mesajlı oyun; uluslararası basına yansıdı | P14 |
| Super Gerrit | Eğitim, ortak yapım | Pelckmans | 05/01/2016 | 6-8 yaş için matematik oyunu | P20 |
| Mendel | Eğitim | KU Leuven, LUCA ile | 08/11/2016 | Temel kimya bulmaca oyunu | P15 |
| Liftoff: FPV Drone Racing | Kendi ürünü | — | 13/09/2018 | Ana simülatör | P07 |
| De STEM | VR, kamu fonlu | SYNTRA Limburg | 25/11/2018 | 15 dakikalık VR; STEM'de cinsiyet ve azınlık etkisi | P11 |
| Battery Workbench | VR eğitim | InnoEnergy | 01/01/2019 | Batarya montajı ve EV paketi bakımı | P10 |
| Liftoff: Drone Racing | Kendi ürünü, konsol | — | tarih yok | Konsol sürümü | P06 |
| Liftoff: Micro Drones | Kendi ürünü | — | tarih yok | Mikro drone simülatörü | P01 |
| Midnight Protocol | Ortak yapım | Sixty Four, Iceberg ile | tarih yok | Hacking RPG | P05 |
| Mars Drone Simulator | Müşteri, Liftoff tabanlı | Skypersonic | 01/09/2022 | NASA analog görevi için eğitim aracı | S07 |
| Woodworks VR | VR eğitim | GO! Atheneum Geraardsbergen | 01/05/2023 | Sanal ahşap freze makinesi; öğretmen izleme ve sınav | P04 |
| Liftoff: XR Drone | Kendi ürünü, VR | — | 10/07/2024 | Quest için yeni başlayan odaklı uçuş | P03 |
| INTERREG BeNeDrone | AB projesi, teknoloji ortağı | Interreg | 01/09/2025 | Tıbbi drone taşımacılığı; sanal eğitim ortamı | P02 |
| CosmiClean | Eğitim | EIT RawMaterials projesi | tarih yok | Geri dönüşüm tesisi kurma bulmacası | P08 |
| Snoezel VR | VR, bakım | Sint Oda | tarih yok | Zihinsel engelli bakımında stres azaltma prototipi | P09 |
| CHARMING | AB eğitim ağı | 8 yararlanıcıdan biri | tarih yok | Kimya eğitiminde oyun ve karma gerçeklik | P12 |
| Coria | Konuma dayalı AR | Heerlen şehri, Goal043 ile | tarih yok | Şehir tarihini öğreten mobil oyun | P13 |
| Creature of Habit | Deneysel, prototip | VAF destekli | tarih yok | Bakıcıların rutin kurduğu sağlık oyunu | P16 |
| Kika & Bob | Müşteri, çocuk | Walking The Dog, Submarine ile | tarih yok | Dizi tabanlı 26 mini oyun | P17 |
| Pinball Planet | Mobil oyun | — | tarih yok | Android, iOS, Windows Phone pinball | P18 |

## 7. Müşteriyle çalışma biçimi

Stüdyo altı aşama anlatıyor: tanışma, ihtiyaç, vizyon, adım adım yapım, yineleme, yayın ve sonrası. [D, S03]

- Önce çekirdek mekaniğin prototipi yapılıyor, sonra ayrıntıya gidiliyor. [D, S03]
- Yineleme kullanıcı testine dayanıyor. [D, S03]
- Müşterinin dilini konuşmayı ve gerçekçi kapsamı vurguluyorlar. [D, S03]

## 8. Görsel dil

- Ürün sayfası ortamların kalitesini ve gerçek parça kopyalarını öne çıkarıyor. [D, S17]
- UZH araştırmacısı Liftoff'u fotogerçekçi ve özelleştirilebilir diye tanımlamış. [D, S22]
- Micro Drones ortamları hikâye anlatıyor; aynı mekânın gündüz ve gece hâli farklı uçuş yolları veriyor. [D, N14]
- Eski haritaları yeniliyorlar; Permafrost'ta her yerin aynı görünmesi yön kaybı yaratıyordu. [D, N12]
- Stüdyo bu sorunu yeni simge noktalarıyla çözdüğünü söylüyor. [D, S10]
- 2.0 UI ilkesi: Tanıdıklığı koru, okunurluğu artır. [D, N13]
- Mars görselleri için `04_mars_drone_simulator.md` bölüm 5.

## 9. Topluluk

- Sahip sayısı: Haziran 2023'te yarım milyonun üstü, Kasım 2025'te bir milyonun üstü pilot. [D, S18, N07]
- Şubat 2026'da yılın ilk altı haftasında 20 bin yeni pilot ve eşzamanlı oyuncu rekoru duyuruldu; rekor sayısı yazmıyor. [D, N11]
- Topluluk kanalları: Discord, Steam, Facebook grubu. [D, N15]
- Aralık 2019'da Workshop 10 bin kaydı geçti. [D, S35]
- Öncelikleri olarak topluluğu ve ekibin keyif almasını açıkça yazıyorlar. [D, S18]
- 2015'te ücretsiz güncelleme sözü verdiklerini, bunu sürdürdüklerini söylüyorlar. [D, S18]
- Haziran 2026 yazısına göre 2015'ten kalan kod kalmamış. [D, N12]
- Sektör içi çalışma: Spawn Point, VAF mentörlüğü, Limburg Game Guild. [A, S62, S63]
