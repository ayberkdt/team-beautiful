# 2. ADVIONICS Challenge — Automated Approach Guidance

**Kaynak görsel:** `images/02_Advionics_original.jpg`  
**Temel tema:** Tower-to-cockpit information, voice/radio, signal translation, degraded communications.

## A. El yazısının yeniden okunması

### A1. Harfiyen okunabilen ifadeler — [NOT]

> Advionics Challenge  
> Automated Approach Guidance  
> Advionics → Radar Expertise  
> Friday Morning Challenge  
> İletişim kesilirse  
> Translate signal  
> Kule ile iletişim kesilirse [voice] sinyal display'e nasıl ulaşır gibi bir şey.

Son Türkçe satır bir **konuşmacı ifadesinin aceleyle yazılmış özeti** gibi görünüyor; tam İngilizce cümle değil. “Voice” kelimesi “signal” üzerinde ayrıca yazılmış. Kullanıcının sonraki hatırlatmasında konuşmacının **voice, radio, translate** kelimelerini kullandığı da belirtiliyor.

### A2. Nelerin yazmadığı — önemli sınırlar

Notta **CPDLC**, **ADS-B**, **SSR**, **AI**, **speech recognition**, **Kalman filter**, **radar fusion**, **primary/secondary communication** veya belirli bir donanım zorunluluğu açıkça yazmıyor. Bunlar aşağıdaki bölümde *ihtimal* olarak değerlendirilir. Tam sinyal kesildiğinde sesin nasıl görüntüleneceği sorusunun bağlamı da belirsiz.

## B. Resmî açıklama yerine kullanılabilecek düzenlenmiş İngilizce özet — [ÇIKARIM]

> **Conceptual challenge:** Develop an approach-guidance support concept that translates ATC radio/voice information into clear, pilot-interpretable cockpit indications. Consider how the interface behaves when radio communication is degraded, interrupted, or unavailable. Identify the communication sources, failure modes, and safe fallback behavior.

Bu metin **resmî görev şartnamesi değildir**. Eldeki en güçlü ipuçlarını birleştiren çalışma tanımıdır.

## C. Başlıktaki teknik anlamlar: hangisi daha olası?

### C1. Hipotez 1 — ATC Voice → Cockpit Display (**en güçlü çıkarım**)

1. Kule veya yaklaşma kontrolörü VHF telsizde bir talimat söyler.
2. Uçaktaki radyo sesi alır.
3. Yazılım konuşmayı metne çevirir (*automatic speech recognition*, ASR).
4. Cümleden uçuşa ilişkin alanlar ayrıştırılır (*call sign, altitude, heading, runway*).
5. Kokpit ekranı bu bilgileri **doğrulanmamış öneri** olarak gösterir.
6. Pilot orijinal sesli talimat ve mevcut usullerle doğrular.

Örnek (tamamen sentetik):

```text
VOICE: "Example One Two Three, turn left heading two seven zero,
        descend and maintain three thousand feet."

ASR TEXT: "EXAMPLE123 TURN LEFT HEADING 270 DESCEND AND MAINTAIN 3000 FT"

PARSER:
  call_sign: EXAMPLE123
  lateral_instruction: turn_left
  heading_deg: 270
  altitude_ft: 3000
  transcript_verified: false

DISPLAY:
  HEADING 270°   ALTITUDE 3000 ft
  Source: VHF voice recognition
  Status: UNVERIFIED — cross-check required
```

**Güvenlik notu:** Bu prototip, ATC iznini otomatik değiştirmemeli veya uçuş kontrolüne emir göndermemeli. Uçuşa uygun, sertifikalı sistem geliştirildiği iddia edilmemeli.

### C2. Hipotez 2 — İletişim kaybında bilgi yönetimi (**güçlü tamamlayıcı**) 

- **Ses bozuldu, ama duyulabilir:** ASR güveni düşebilir; hatalı metnin kesin talimat gibi gösterilmesi tehlikelidir.
- **Tek yönlü arıza:** Uçak duyar fakat iletemez; veya ATC'nin sesi alınamaz. Ayrı tespit ve prosedür gerekir.
- **VHF tamamen kayboldu:** Sistem gelen yeni sesi **üretemez/çeviremez**. Kullanılabilir başka iletişim vasıtaları denenebilir; güncel clearance üretilemez.
- **Son geçerli talimat:** Zamana duyarlı bilgiler zaman damgası ve kaynak ile sunulmalı. “Son duyulan” ile “yeni geçerli izin” aynı değildir.

### C3. Hipotez 3 — Radar/Surveillance ile birleşik yaklaşma durumu (**daha zayıf çıkarım**) 

Advionics ve bağlı olduğu Intersoft Electronics grubunun radar/RF alanında uzmanlığı bulunuyor. Ancak radar/SSR/ADS-B gözetim verisi, kuleden gelen **sesli ATC talimatının eşdeğeri değildir**. Radar konum/hareket durumu sağlamaya yardımcı olur; radyo sesini geri getirmez. “Primary/secondary” ifadesi **haberleşme kanalları** veya **primary/secondary surveillance radar** anlamına gelebilir. Not tek başına hangisi olduğunu kanıtlamıyor.

## D. Önerilen uçtan uca sistem mimarisi

```text
                       ATC / APPROACH CONTROL
                                  |
                    +-------------+-------------+
                    |                           |
              VHF Voice RF               Other authorized
                    |                      communications
              Audio interface              (if available)
                    |                           |
            ASR / speech parser          Message/status input
                    |                           |
                    +-------------+-------------+
                                  |
                      Validity and source layer
             (timestamp, call sign, ambiguity, consistency)
                                  |
                 +----------------+----------------+
                 |                                 |
       Cockpit advisory display            Communication health
          (pilot confirmation)             and fallback prompts
```

**Bu mimari, aynı komutun iki ayrı gerçek kaynaktan geldiğini varsaymamalıdır.** Dijital veri bağlantısı varsa mesajın kapsama/operasyon sınırları korunur.

## E. Yalın çalışan prototip: kapsam ve bileşenler — [ÖNERİ]

### E1. Dört ana modül

1. **Audio input / synthetic radio channel:** Kaydedilmiş veya sentetik ATC cümleleri, beyaz gürültü, clipping, kesinti ve sessizlik.
2. **ASR + structured parser:** Konuşmayı metne çevirme; sayısal değer, yön, irtifa, çağrı işareti çıkarma.
3. **Communication-state monitor:** Ses kalitesi / zaman aşımı / bağlantı durumu gibi tanımlanmış girdilerden açık durum üretme.
4. **Cockpit HMI mockup:** Son mesaj, durumu, kaynağı, güven uyarıları ve iletişim durumu.

### E2. Durum makinesi

| Durum | Koşul (örnek tasarım) | Arayüz davranışı |
|---|---|---|
| NORMAL | Kaynak etkin; mesaj anlaşılır | Algılanan komutu ve doğrulama işaretini göster |
| DEGRADED | Kalite düşük veya ASR tutarsız | “UNCONFIRMED” göster; emin olunmayan sayıyı gizle |
| RX_LOST | Yeni ses alınamıyor | Yeni ses talimatı gösterme; eski mesajı tarihli/eskimiş olarak işaretle |
| TX_LOST | İletim başarısızlığı tespit edilmiş | Geri bildirimin ulaşmadığını ve ilgili prosedür gereğini bildir |
| ALTERNATE_AVAILABLE | Yetkili başka kanal/servis kullanılabilir | Kaynağını açık göster; operasyona uygunluk kontrolü |
| ALL_COMMS_LOST | Uygun iletişim sağlanamıyor | Son izin bilgisi + resmî haberleşme kaybı kontrol listesi bağlantısı |

**İşletim sınırlaması:** Bunlar demo durum adlarıdır; uçuşta uygulanacak usulü otomatik belirleyen bir sertifikasyon mantığı olarak sunulamaz.

### E3. Kritik testler

| Test | Giriş örneği | Başarı ölçütü |
|---|---|---|
| Sakin kanal | Temiz ses | Doğru çağrı işareti ve parametre çıkarımı |
| Yoğun gürültü | Ses + parazit | Sistem belirsizlik bildirir; uydurma talimat üretmez |
| Sayı benzerliği | “two seven zero” / “two zero zero” | Yanlış değer yüksek güvenle sunulmaz |
| Çağrı işareti karışması | İki farklı uçak | Yanlış uçağa atanan komut işaretlenir |
| Sessizlik / RX kaybı | Akış kesilir | Yeni mesaj geldiği izlenimi verilmez |
| Veri gecikmesi | Geç ulaşan mesaj | Mesajın zamanı/kaynağı görünür |
| Ortak neden | Güç kaybı | Yedek sayılan kanalların bağımsızlığı sorgulanır |

Önerilen metrikler: **command extraction accuracy**, kritik sayı hatası oranı, yanlış güven oranı, komut işleme gecikmesi, arıza algılama gecikmesi, yanlış alarm oranı. Örnek veri setinde sonuçları gerçek uçuş performansı gibi genelleştirmeyin.

## F. Haberleşme güvenliği ve yedeklilik

EUROCONTROL'e göre **CPDLC**, sesli radyo yerine **acil olmayan** uygun ATC mesajlarının veri bağlantısıyla aktarımını sağlar; söz konusu hizmet her uçakta/hava sahasında/operasyon aşamasında mevcut değildir. CPDLC, bir ses kayıt transkripsiyon sistemi değildir.

EASA'nın SERA.14083 kuralı radyo iletişim kaybında diğer frekanslar ve mevcut uygun iletişim araçlarıyla temas kurma girişimlerini ve koşullara bağlı prosedürleri düzenler. Prototip, bu kuralları kendi uydurduğu talimatlarla değiştirmemelidir.

**En ciddi tasarım hatası:** Tam VHF kaybında “Voice → display” işlemeye devam ettiğini varsaymak. Giriş yoksa yeni sesli talimat da yoktur.

## G. Muhtemel teslimler — [ÇIKARIM / ÖNERİ]

Notta Advionics için resmî teslim listesi görünmüyor. Aşağıdakiler öneridir:

- Problem kapsamı ve kullanım senaryosu (1 sayfa).
- Sistem blok diyagramı ve sinyal/mesaj akışı.
- Bir kokpit arayüzü tasarımı (normal, bozuk ve kayıp iletişim ekranları).
- En az bir gerçekçi senaryonun ses/sinyal simülasyonu.
- Temel güvenlik/arıza analizi ve yanlış tanıma savunması.
- 1–2 dakikalık çalışan demo; açık sınırlamalar.

## H. Mentora sorulacak kritik sorular

1. **“Translate signal”**, sesin yazıya dönüştürülmesi mi, RF/sinyal verilerinin grafik arayüzü mü?
2. İletişim **tamamen mi kesiliyor**, yoksa parazitli fakat alınabilir mi?
3. İstenen kaynak **voice radio**, **radar**, **transponder** veya birkaçının birleşimi mi?
4. “Automated” kelimesi otomatik veri yorumlama mı, otomatik uçuş kontrolü mü?
5. Uçuş safhası: yaklaşma, final approach, iniş, veya hepsi mi?
6. Müşteri/pilot için başarının ölçüsü ne: gecikme, doğruluk, kullanılabilirlik veya güvenlik?
7. Donanım gösterimi mi yoksa yazılım konsepti mi gerekiyor?

## I. Kaynaklar

- Advionics resmî profil: https://advionics.be/about/
- Intersoft Electronics/Advionics radar ve yüksek güvenilirlik profili: https://belgianeconomicmission.be/organisation/intersoft-electronics-advionics
- EUROCONTROL Data Link/CPDLC: https://www.eurocontrol.int/function/datalink
- EUROCONTROL CPDLC recommended practices: https://www.eurocontrol.int/publication/controller-pilot-datalink-communications-cpdlc-recommended-practices
- EASA SERA.14083: https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-standardised-european

**Sonuç:** Eldeki sözcükler ışığında en güçlü yorum **ATC VHF sesini kokpitte açık ve güvenli bir görsel bilgiye dönüştürme**, iletişim kaybında ise **dürüst bağlantı durumu ve güvenli fallback davranışı** tasarlamadır. Radar ve ikinci veri kanalı ancak mentor doğrularsa zorunlu kapsam olur.
