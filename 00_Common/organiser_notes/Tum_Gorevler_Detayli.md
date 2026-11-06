# EUROAVIA Ideathon 2026 — Tüm görevler ayrıntılı dosyası

Bu tek Markdown dosyası, kaynak notlar ve dört challenge analizi ile karşılaştırma bölümünü birleştirir. Aynı klasördeki `images/` altındaki özgün görseller ayrı ZIP içinde sunulmuştur.



---

# EUROAVIA Ideathon 2026 — Dört görevin ayrıntılı analizi

**Hazırlanma tarihi:** 4 Kasım 2026  
**Kaynaklar:** Etkinlik sırasında alınan dört el yazısı not sayfası ve açık erişimli birincil/kurumsal teknik kaynaklar.  
**Dil:** Açıklamalar Türkçe; düzenlenmiş görev ifadeleri ve bazı teslim adları İngilizce.

## Okuma yöntemi ve güven düzeyleri

- **[NOT / kesin]** — Kullanıcının gönderdiği el yazısında açıkça görülen ifade. Bu, organizatörün resmi görev dokümanı olduğu anlamına gelmez; konuşmacıdan alınmış nottur.
- **[OKUMA / belirsiz]** — El yazısında net olmayan veya anlamı birden çok şekilde yorumlanabilecek ifade.
- **[DOĞRULANDI]** — Şirketin, düzenleyici kurumun veya resmi incelemenin çevrimiçi kaynağıyla doğrulanan bilgi.
- **[ÇIKARIM]** — Görev başlığı ve şirketin teknik alanına dayanarak üretilmiş **tahmini** kapsam.
- **[ÖNERİ]** — Görevin resmi gereksinimi olmayabilir; yarışma çözümünü güçlendirmek için önerilen çıktı, yöntem veya kontrol.

**Önemli:** Aşağıdaki dört dosya, özgün yarışma şartnamesi değil; notların dikkatli transkripsiyonu ve kaynağı belirtilen teknik tasarım yorumlarıdır.

## Dosyalar

| Dosya | Konu | Görsel kaynak |
|---|---|---|
| `01_Ansys_Bracket_Redesign.md` | Braket yeniden tasarımı, malzeme seçimi, Eco Audit | `images/01_Ansys_original.jpg` |
| `02_Advionics_Automated_Approach_Guidance.md` | ATC radyo/ses sinyallerinin gösterimi, iletişim kaybı | `images/02_Advionics_original.jpg` |
| `03_EASA_Canopy_Alert_Retrofit.md` | Kanopi uyarı sistemi retrofit ve AAIB vaka incelemesi | `images/03_EASA_original.jpg` |
| `04_LuGus_Venus_Rotorcraft.md` | Venüs'te döner kanatlı hava aracı tasarımı | `images/04_LuGus_original.jpg` |
| `05_Cross_Challenge_Comparison.md` | Görev karşılaştırması, hazırlık ve ekip planı | — |
| `Tum_Gorevler_Detayli.md` | Tüm raporların tek Markdown dosyası | — |

## En önemli düzeltmeler

1. **EASA 2 Nisan 2022 vakası**: Uçak **Extra NG, tescil G-MIIL**. AAIB, olayın nedenini yetersiz kanopi çerçevesi yapışması → gerilme yığılması → yorulma çatlakları → uçuşta yapısal parçalanma şeklinde belirledi. Bu olayın kesin nedeni *kilitlenmemiş kanopi* değildir. Bununla birlikte görev notu **unlocked canopy events** riskini azaltan bir retrofit uyarı sistemi tasarlamayı öneriyor.
2. **LuGus**: Orijinal not **rotorcraft** diyor; otomatik olarak balon/sabit kanat seçimini resmi izin gibi varsaymayın.
3. **Advionics**: “Voice / radio / translate / display” kelimeleri, sesin **yazıya/komuta ve kokpit görselleştirmesine dönüşmesini** düşündürüyor. Ancak tam radyo kaybında alınmayan konuşma çözülemez. Gerçek yedek haberleşme ayrıca gerekir.
4. **Ansys**: Notta dört **asgari** teslim var. “3” işaretinin malzeme adedi veya başka bir kod olduğu kesin değil; ek bir zorunluluk olarak yazılmadı.
5. **Takvim**: Notlarda Advionics “Friday morning”, LuGus “Friday afternoon – 6 hour” diye geçiyor. Bunlar not edilmiş oturum bilgileri; organizatör takvimini ayrıca kontrol edin.

## Resmî ve kurumsal kaynaklar

- AAIB, Extra NG G-MIIL, 2 Nisan 2022: https://www.gov.uk/aaib-reports/aaib-investigation-to-extra-ng-g-miil
- AAIB tam soruşturma raporu: https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf
- EASA AD 2025-0156 (kanopi kilitleme işaretleri / uçuş el kitabı): https://ad.easa.europa.eu/ad/2025-0156
- Advionics kurumsal profil: https://advionics.be/about/
- EUROCONTROL veri bağlantısı / CPDLC: https://www.eurocontrol.int/function/datalink
- EASA SERA.14083: https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-standardised-european
- Ansys Granta EduPack Eco Audit: https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Getting_Started/sel_edu/eco_tool_exercises.html
- Ansys aeronautical bracket additive manufacturing case study: https://ansys.synopsys.com/academic/educators/education-resources/am-case-study-part-1
- LuGus Mars Drone Simulator / Skypersonic: https://www.lugus-studios.be/portfolio/mars-drone-simulator
- NASA Venus facts: https://science.nasa.gov/venus/venus-facts/
- NASA/JPL Venus aerial platforms: https://science.nasa.gov/resource/aerial-platforms-for-the-scientific-exploration-of-venus/


---

# 1. ANSYS Challenge — Aircraft Bracket Redesign

**Kaynak görsel:** `images/01_Ansys_original.jpg`  
**Temel tema:** Aircraft bracket / topology optimization / material selection / environmental impact.

## A. El yazısının yeniden okunması

### A1. Başlık ve ana ifade — [NOT]

> ANSYS CHALLENGE
>
> Re-design an aircraft bracket; re-design material and shape [to change / minimize] component weight and/or optionally extend life expectancy. Assess the improvement of CO₂-eq emissions over [the] full life of the component.

**Okuma notları:** “mini” kısa notu, ağırlığı **minimize et** anlamında görünüyor; ana cümledeki gramer bozukluğunu teknik hedefe dönüştürürken bu anlamı kullandım. “Life expectancy” hizmet/çalışma ömrüdür; otomatik olarak yorulma analizi zorunlu anlamına gelmez.

### A2. Expected deliverables (bare minimum) — [NOT]

1. CAD of initial design.
2. Material selection report and comparison table. Yanında **“3”** işareti var; üç malzeme istendiğini *kesinleştirmek mümkün değil*.
3. Eco Audit report for initial design.
4. Material card files.

### A3. Diğer notlar — [NOT]

- Working temperature: **300 °C** (notta “working tem 300°C”).
- **3D-printability** (“3D printed ability” şeklinde yazılmış olabilir).
- **Structural steel** (başlangıç/referans malzeme olası; tam kalite belirtilmiyor).
- Çizim: Birden fazla montaj deliği ve kavisli takviye/kol özellikleri olan bir **mounting bracket** taslağı. Tam boyutlar, yük yönleri ve parçanın uçakta yeri görünmüyor.

## B. Düzeltilmiş, önerilen İngilizce görev tanımı — [ÇIKARIM]

> **Redesign an aircraft mounting bracket** by selecting suitable materials and modifying its geometry to reduce its mass and, where feasible, improve its service life. Evaluate the CO₂-equivalent impact throughout the component life cycle, considering the stated 300 °C operating condition and additive-manufacturing suitability. Document the baseline geometry, material selection, baseline Eco Audit, and material data cards.

Bu paragraf **resmî görev metni değildir**. Notun anlamı açıklaştırılarak yeniden yazılmıştır.

## C. Teknik amaç ve temel denklemler

### C1. Kütle ve rijitlik

Sabit yoğunluklu bir parça için:

\[
 m=\rho V.
\]

SIMP tabanlı topoloji optimizasyonuna örnek amaç:

\[
\min_{\rho_e} C=\mathbf F^T\mathbf u,\qquad
\mathbf K(\boldsymbol\rho)\mathbf u=\mathbf F,
\]

\[
\sum_e \rho_e V_e\leq fV_0,\qquad 0\leq\rho_e\leq1.
\]

- Bu formül **rijitlik odaklı** örnek modeldir; notta matematiksel formül/amaç fonksiyonu verilmemiştir.
- Gerilme, yer değiştirme, burkulma, yorulma ve izin verilen maksimum sıcaklık gerekleri ayrıca tanımlanmalıdır.
- Kütle azaltımı tek başına dayanıklılık kanıtı değildir.

### C2. Yüksek sıcaklık

**300 °C koşulunu** malzeme verisinin seçildiği sıcaklıkla eşleştirin. Akma dayanımı, elastisite modülü, yorulma ve uzun süreli yük altındaki davranış oda sıcaklığından farklı olabilir. “Structural steel” için tam alaşım/ısıl işlem seçilmeden güvenilir değerlendirme yapılamaz.

### C3. Yaşam döngüsü / Eco Audit

Örnek ayrıştırma:

\[
\mathrm{CO}_{2e,\mathrm{total}}=
E_{\mathrm{material}}+E_{\mathrm{manufacture}}+
E_{\mathrm{transport}}+E_{\mathrm{use}}+E_{\mathrm{EOL}}.
\]

Buradaki her terim kg CO₂e birimindeki katkıdır; üretim enerjisi değil, emisyon etkisidir. Uçak kütlesi azalmasının yakıt/enerji tasarrufuna nasıl dönüştüğü bilinmiyorsa **kullanım aşaması etkisini varsayım olarak ayrıca göstermelisiniz**. Ansys Granta Eco Audit malzeme, imalat, taşımacılık, kullanım ve ömür sonu aşamalarını analiz eder.

## D. Yapısal tasarım ve malzeme seçimi yaklaşımı — [ÖNERİ]

### D1. Başlangıç modelini oluşturma

1. Görünür delik yerlerini ve göreli geometrik özellikleri kaydedin.
2. Resmî veri verilmediğinde boyutları **assumption** olarak işaretleyin.
3. Bağlantı arayüzlerini ve tasarım dışı bırakılamayacak bölgeleri belirleyin (*non-design regions*).
4. Yüklerin hangi deliklerden aktarıldığını çizimle gösterin.
5. İlk modelin kütlesini, malzeme kartını ve mümkünse FEA yanıtını raporlayın.

### D2. Malzeme karşılaştırması

Aşağıdaki sınıflar **aday örnekleridir**, kabul edilmiş malzeme listesi değildir.

| Malzeme sınıfı | Olası güçlü yön | Kritik kontrol |
|---|---|---|
| Referans yapısal çelik | Düşük maliyet / veri bulunabilirliği | Tam kalite, 300 °C dayanım, üretim yöntemi |
| Paslanmaz çelik (uygun kalite) | Sıcaklık/koroz­yon direnci seçenekleri | Kütle, baskı sonrası özellik, maliyet |
| Titanyum alaşımı (uygun kalite) | Yüksek özgül dayanım potansiyeli | 300 °C uzun süreli davranış, baskı kalitesi, maliyet |
| Nikel esaslı alaşım | Sıcaklık dayanımı potansiyeli | Yüksek yoğunluk, kaynak tüketimi, maliyet |
| Alüminyum alaşımı | Düşük yoğunluk | 300 °C'de mekanik özellik kaybı; çoğu standart kalite için sorunlu olabilir |

Önerilen değerlendirme sütunları: yoğunluk, $E(T)$, akma dayanımı $\sigma_y(T)$, çekme dayanımı, yorulma verisi, üretim uygunluğu, maliyet, kaynak/ikincil işleme ihtiyacı, birincil malzeme CO₂e, geri dönüşüm senaryosu.

### D3. Optimizasyon ve doğrulama

- İlk tasarımla **aynı yükler ve mesnetler** altında kıyas yapın.
- Topoloji optimizasyonu → CAD yeniden yapılandırma → FEA doğrulama sırasını uygulayın.
- Aşırı ince kollar, kapalı iç boşluklar, desteksiz çıkıntılar, delik toleransları ve yüzey işleme gereksinimleri değerlendirilmelidir.
- En az üç ağ yoğunluğunda yakınsama veya en azından kaba/orta/ince çözüm karşılaştırması idealdir.
- Karşılaştırma metrikleri: $m$, maksimum yer değiştirme, kritik gerilme/izin verilen gerilme oranı, baskı hacmi ve CO₂e.

## E. Teslimlerin ayrıntılı biçimi

### E1. Notta açıkça bulunan asgari dört teslim — [NOT]

**1. Initial CAD model:** Geometri dosyası ve montaj deliklerinin tanımlandığı ekran görüntüsü.  
**2. Material selection report and comparison table:** Adayların hangi sıcaklık ve veri kaynaklarıyla karşılaştırıldığını belirtin.  
**3. Baseline Eco Audit report:** Başlangıç tasarımına ait sınırlar ve varsayımlar görünür olsun.  
**4. Material cards:** Her malzeme için seçilen veri kaynağı, kalite, sıcaklık, malzeme özellikleri ve birimler.

### E2. Rekabet avantajı sağlayacak ek teslimler — [ÖNERİ]

- Optimize CAD ve önce/sonra çizimi.
- Yapısal performans kontrolü, emniyet katsayısı/gerilme raporu.
- Başlangıç ve optimize tasarıma ait Eco Audit karşılaştırması.
- Parçanın üretim oryantasyonu ve destek gereksinimi.
- Varsayımları açıkça gösteren tek sayfalık teknik özet.

## F. Riskler, açık sorular ve değerlendirme

**Büyük riskler:** Belirsiz yükler; 300 °C'de uygun olmayan malzeme; optimizasyon çıktısının üretilememesi; yalnızca birim kütle üzerinden gerekçesiz CO₂ tasarrufu; FEA sınır koşullarının gerçek montajı yansıtmaması.

**Mentora sorulacak sorular:**
1. 300 °C sürekli servis sıcaklığı mı, geçici maksimum mu?
2. Yük vakaları ve sınır koşulları sağlanacak mı?
3. Parçanın boyutları/CAD dosyası verilecek mi?
4. “3” üç farklı malzeme anlamına mı geliyor?
5. 3D baskı kesin zorunluluk mu yoksa değerlendirme kriteri mi?
6. Sadece başlangıç Eco Audit raporu mu zorunlu; son tasarım da isteniyor mu?
7. Seçili Ansys modülleri / lisansları sağlanıyor mu?

## G. Kurumsal doğrulama

- Ansys'in **aeronautics bracket** için Granta EduPack + additive manufacturing çalışması, malzeme seçimi ve üretilebilirliğin görevle bağlantılı olduğunu destekliyor: https://ansys.synopsys.com/academic/educators/education-resources/am-case-study-part-1
- Ansys Discovery örneklerinde uçak motoru braketi topoloji optimizasyonu bulunuyor: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/pdf/Ansys_Discovery_Technology_Showcase.pdf
- Granta EduPack Eco Audit işlevi ve fazları: https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Getting_Started/sel_edu/eco_tool_exercises.html

**Sonuç:** Bu görevde en güçlü çözüm sadece hafif bir şekil değil; **sıcaklıkta mekanik yeterlilik + üretilebilirlik + karşılaştırılabilir yaşam döngüsü etkisi** sunan doğrulanmış bir tasarımdır.


---

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


---

# 3. EASA Challenge — Canopy Alert System Retrofit

**Kaynak görsel:** `images/03_EASA_original.jpg`  
**Temel tema:** Hava aracı kanopisinin yanlış/eksik kilitlenmesi riskini azaltan retrofit uyarı sistemi ve adım adım tasarım/entegrasyon süreci.

## A. El yazısının yeniden okunması

### A1. Başlık ve olay — [NOT]

> EASA Challenge  
> 2nd April 2022 → accident to Extra NG, G-MI[I/L]

Notta tescilin son harfleri okunması zor; **resmî AAIB kaynağıyla tescil kesin olarak `G-MIIL`** düzeltildi.

### A2. Görev metni — [NOT]

> Propose alert system for canopy retrofit.  
> Propose retrofit for a canopy alert system.  
> Pick your example aircraft (Any).  
> Outline a step-by-step process that details how to retrofit an alert device to an aircraft for the purpose of reducing unlocked canopy events.

### A3. Son satırlar — [NOT / OKUMA]

> We will get **word 1st / word list?** [okuma belirsiz].  
> There is no limits; no budget limit.  
> Be creative and find best design.

- “We will get word 1st” şeklinde görünen satırın anlamı **kesin değil**. Bunu organizatörün “word list verecek” taahhüdü olarak yazmak hatalı olur.
- “No budget limit” konuşmacının bir beyin fırtınası serbestliği vurgusu olabilir; tasarımın gerçek sertifikasyon ve montaj kısıtlarının ortadan kalktığı anlamına gelmez.

## B. Çok önemli: Kazanın gerçek nedeni ve görev hedefi aynı şey değil

### B1. Doğrulanan olay — [DOĞRULANDI]

- **Tarih:** 2 Nisan 2022.
- **Uçak:** Extra NG, **G-MIIL**.
- **Konum:** Upper Heyford, Oxfordshire, Birleşik Krallık.
- **Olay:** 184 KIAS düz uçuşta kanopi aniden parçalandı; pilot ciddi yaralandı, paraşütle uçağı terk etti.
- **AAIB sonucu:** İç ve dış kanopi çerçevesi arasındaki yetersiz yapıştırma, yerel gerilme yığılmalarına ve akrilik saydamlıkta yorulma çatlaklarına yol açtı. Çatlakların ilerlemesi felaket niteliğinde yapısal arızayla sonuçlandı.

**Bu spesifik kazanın açıklaması, “kanopi açık kaldı / pilot kilitlemedi” değildir.** AAIB kilitlenme ihtimalini değerlendirmiş olsa da ana sonuç kanopi yapısal yorulma hasarıdır.

### B2. Farklı ama ilgili gerçek tehlike — [DOĞRULANDI]

EASA **AD 2025-0156**, Extra NG için uçuşta açılma veya ayrılma olayları bağlamında eksik/yanlış kanopi kilitlenmesine ilişkin riski ele alır; yeni kol işaretlemeleri (*placards*) ve uçuş el kitabı güncellemesi ister. Bu, kilitlenme tehlikesinin gerçek olduğunu gösterir, ancak 2 Nisan 2022 kazasının kök nedenini değiştirmez.

**Tasarım sonucu:** Bir **latch alert retrofit**, yanlış kilitleme riskini azaltmayı hedefler; **yapıştırma kusurunu veya yorulma çatlağını tek başına tespit ettiği iddia edilmemelidir**. İsterseniz yapısal bütünlük için ayrı bir izleme önerisi opsiyonel olarak tartışılabilir.

## C. Düzeltilmiş İngilizce görev tanımı — [ÇIKARIM]

> **Propose a retrofit canopy warning/alert system** for an aircraft of your choice that helps prevent take-off or flight with an improperly secured canopy. Specify how the system detects the hazardous condition, alerts the pilot, is installed and verified on the selected aircraft, and reduces operational risk. Present a step-by-step retrofit and validation process, including failure modes and human-factors considerations.

Bu tanım notların anlamını düzenler; EASA'nın resmî şartname metni değildir.

## D. Neden “canopy closed” ile “canopy locked” ayrı ölçülmeli?

Kapak/kanopi gövdeye oturmuş olabilir ama kilitleme cıvataları/mandalları tamamen devreye girmemiş olabilir. Tek bir manyetik anahtar, **kapalı** konumu gösterebilir fakat **gerçek kilit angajmanını** garanti etmez.

Önerilen sensör yaklaşımı:

- Sensör A: kanopinin fiziksel olarak kapalı/oturmuş konumu.
- Sensör B: kilitleme cıvatasının veya mandal mekanizmasının gerçekten tam angaje olması.
- Uygunsa sensör C: ikinci kilit noktası veya bağımsız tutarlılık doğrulaması.
- Arıza kontrolü: sensör açık devre, kısa devre, birbirini tutmayan sensörler ve besleme kaybı.

**Dikkat:** Bir sensörün gerçekten kilit angajmanını ölçebildiği seçilen uçaktaki mekanizmaya göre kanıtlanmalıdır.

## E. Olası mimari — [ÖNERİ]

```text
[Canopy seated switch] ----+
                           |
[Latch engagement sensor] -+--> [Health + Logic] ---> [Visual warning]
                           |                   +---> [Optional audio alert]
[Power/self-test input] ---+                   +---> [Maintenance/fault flag]

                 Aircraft operating state
              (ground / taxi / take-off / flight)
                          |
                       Warning logic
```

### E1. Örnek uyarı mantığı

| Evre | Canopy closed | Latch locked | Önerilen davranış |
|---|---|---|---|
| Power-up / preflight | Evet | Evet | Normal; self-test tamamlanmalı |
| Preflight | Evet | Hayır | Belirgin “CANOPY NOT LOCKED” uyarısı |
| Taxi | Hayır veya belirsiz | Herhangi | Kalıcı dikkat uyarısı |
| Take-off öncesi | Evet | Hayır / belirsiz | Yüksek öncelikli ikaz; pilotun kontrol listesine yönlendirme |
| Uçuş | Kilitlenme kaybı şüphesi | Hayır / belirsiz | Uyarı, durum ve uygun AFM/POH prosedürünün izlenmesi |
| Sensör uyuşmazlığı | Çelişkili | Çelişkili | “SENSOR FAULT”; yanlış “LOCKED” güveni vermeme |

Bu tablo **kavramsal** mantıktır; gerçek uçakta pilot prosedürü, onaylı ikaz öncelikleri, elektrik mimarisi ve uçuşa elverişlilik gereksinimleriyle tasarlanmalıdır.

### E2. İnsan faktörleri

- Uyarı yeterince görünür olmalı ama normal kokpit ikazlarını bastırmamalı.
- Sürekli gereksiz ikaz, pilotun uyarıyı görmezden gelmesine yol açabilir.
- “Closed” ile “Locked” bilgileri grafiksel olarak açık ayrılmalı.
- Beklenmedik uçuş içi ikazlar için pilotun değerlendirme yükü azaltılmalı.
- Sessiz arıza ve hatalı güvenli duruma geçiş önlenmeli.

## F. Adım adım retrofit süreci — görev notunun ana çıktısı

1. **Hava aracı seçimi:** Kanopi mekanizması tanımlanabilen bir örnek seçin. Extra NG seçilebilir; ancak notta “any aircraft” yazdığı için başka bir uygun model de kullanılabilir.
2. **Mevcut durum tespiti:** AFM/POH, kanopi mekanizması, kilit noktaları, fiziksel erişim ve elektrik beslemesini inceleyin.
3. **Tehlike tanımı:** Kanopinin kapalı görünmesine rağmen kilitlenmemesi, yanlış durum göstergesi, uçuşta mekanik arıza vb. için ayrı senaryolar yazın.
4. **Gereksinim oluşturma:** Hangi durumda uyarı, tepki süresi, güç tüketimi, test edilebilirlik, bakım ve pilot görünürlüğü tanımlansın.
5. **Sensör seçimi:** Konum anahtarı mı, limit switch mi, endüktif/hall etkili algılayıcı mı; seçim mekanik kanıtla gerekçelendirilsin.
6. **Montaj tasarımı:** Yerleşim, kablo güzergâhı, fiziksel/çevresel dayanım, kanopinin acil açılma yoluyla çakışmama kontrolü.
7. **Elektronik ve ikaz mantığı:** Arıza algılama, güç kaybı davranışı, görsel/sesli uyarı, self-test.
8. **Bench test:** Sensörleri bilinen kilit durumlarında test edin; takılı kalma ve kopma arızalarını deneyin.
9. **Ground / functional test:** Kanopi hareketi ve kilit angajmanının ayrımını doğrulayın; bakım erişimi ve pilot görüşünü değerlendirin.
10. **Emniyet değerlendirmesi:** FMEA/FHA, yanlış alarm ve yanlış güvenli durum senaryoları.
11. **Uygunluk/onay planı:** Yetkili tasarım/değişiklik onayı, uygun bakım/veri kaydı ve uygulanacak uçuşa elverişlilik kuralları belirlenmeli.
12. **Kullanım ve bakım:** Pilot kontrol listesi, kullanım eğitimi, periyodik kontroller ve arızalı sistemle uçuş kısıtları açıkça ele alınmalı.

Bu süreç kavramsal tasarım içindir; onaysız bir değişikliğin gerçek uçağa monte edilmesine yetki vermez.

## G. Risk tablosu / FMEA başlangıcı

| Failure mode | Muhtemel sonuç | Önerilen kontrol |
|---|---|---|
| Kapalı sensörü “kapalı” fakat mandal eksik angaje | Yanlış emniyet hissi | Ayrı kilit angajman sensörü |
| Sensör stuck-high | Sistemin kilitli gösterme riski | Uyuşmazlık kontrolü / self-test |
| Sensör stuck-low | Gereksiz uyarı / ikaz yorgunluğu | Arıza ayırma, bakım teşhisi |
| Uyarı güç beslemesi kaybı | Uyarı işlevi kaybı | Arıza bildirme mimarisi, doğrulama |
| Kablonun acil açılmayı engellemesi | Acil tahliye riski | Mekanik bağımsızlık, montaj kontrolü |
| Pilotun ikazı yanlış yorumlaması | Emniyetsiz kalkış/operasyon | Tutarlı kelimeler, ikaz önceliği, insan faktörleri |

## H. Ölçülebilir başarı kriterleri — [ÖNERİ]

- Doğru kilitlenmiş / yarı kilitlenmiş / açık durumları ayırma doğruluğu.
- Uyarı gecikmesi ve durum değişimindeki belirsizlik.
- Sensör arızalarının tespit kapsamı.
- Yanlış-pozitif ve özellikle yanlış-negatif oranı.
- Montajda delme/kalıcı modifikasyon ihtiyacı, ek kütle ve güç tüketimi.
- Bakım/test süresi ve pilot arayüzünün anlaşılabilirliği.

## I. Mentora sorulacak sorular

1. 2022 G-MIIL kazası yalnızca motivasyon mu, yoksa o kazanın **belirli arıza mekanizmasına** çözüm mü isteniyor?
2. Gereksinim **unlocked canopy** ile mi sınırlı, yoksa yapısal çatlak/bonding kontrolü de bekleniyor mu?
3. “Any aircraft” tamamen serbest mi; gerçek montaj geometrisi olan bir model gerekli mi?
4. Sensör demo/prototip mi bekleniyor, yoksa yalnızca konsept ve süreç mi?
5. Bütçe serbestliği, sertifikasyon ve entegrasyon gereksinimlerini nasıl etkiliyor?
6. Belirsiz satırdaki “word 1st / word list?” organizatörün sonradan vereceği veri seti veya gereksinim listesi mi?

## J. Birincil kaynaklar

- **AAIB olay ve kök neden:** https://www.gov.uk/aaib-reports/aaib-investigation-to-extra-ng-g-miil
- **AAIB ayrıntılı rapor:** https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf
- **EASA AD 2025-0156:** https://ad.easa.europa.eu/ad/2025-0156

**Sonuç:** Görev, notlara göre bir **kanopi kilit/ikaz sistemi retrofit süreci** tasarlamaktır. Fakat kaynak kazanın yapısal nedenini uyarı sistemiyle çözülmüş gibi sunmak teknik olarak yanlış olur; bu ayrımı göstermek sunumu güçlendirir.


---

# 4. LuGus Studios Challenge — Fly on Venus

**Kaynak görsel:** `images/04_LuGus_original.jpg`  
**Temel tema:** Venüs atmosferinde çalışan bir **rotorcraft** tasarımı ve kavramsal fizibilite.

## A. El yazısının yeniden okunması

### A1. Başlık, süre, şirket geçmişi — [NOT]

> LuGus Studio [resmî şirket adı: **LuGus Studios**]  
> (Friday — 6 hour) afternoon  
> Fly on Venus  
> Drone that fly in Venus  
> Skypersonic as a training tool for a NASA Mars analog mission.  
> Design a **rotorcraft** that can fly on Venus.

Notta Skypersonic kelimesi biraz bozuk, ancak LuGus'un kendi sayfasındaki Mars Drone Simulator–Skypersonic ilişkisiyle **doğrulanıyor**. Bu, Venüs görevinin NASA tarafından verildiği anlamına gelmez; LuGus'un **önceki deneyimini** anlatır. Ayrıca NASA **Mars analog mission**, Dünya üzerindeki analog çalışma bağlamındadır; gerçek Mars yüzeyinde kullanılan bir drone olarak sunulmamalıdır.

### A2. Üç ana soru — [NOT]

1. **Where should it fly?** — Temperature, pressure, density, wind.
2. **Rotors, propulsion, material, power, thermal; what does it look like?**
3. **How does it get there?**

### A3. Beklenen çıktılar — [NOT]

> Visual design with main components.  
> Operating altitude justified with atmospheric data.  
> Propulsion, power, thermal, control, communications explained.  
> Feasibility, risks, open technical challenges.

**Önemli düzeltme:** Önceki serbest yorumlarda “her tür Venüs hava aracı” diye genişletilmişti. **Orijinal satır açıkça `rotorcraft` diyor.** Bu nedenle temel öneri döner kanatlı olmalı; balon veya sabit kanat ancak mentor alternatif mimariye izin verirse seçenek olarak değerlendirilmeli.

## B. Teknik olarak düzenlenmiş İngilizce problem tanımı — [ÇIKARIM]

> **Design a concept for a rotorcraft capable of controlled flight in Venus's atmosphere.** Select and justify its operating altitude using temperature, pressure, density, and wind data. Define the rotor/propulsion architecture, materials, power, thermal management, control, communications, and visual layout. Describe the Venus transfer, entry, deployment, and operational concept, together with feasibility, key risks, and unresolved engineering challenges.

Bu ifadeler özgün notların içeriğine oldukça yakındır, fakat **resmî şirket şartnamesi değildir**.

## C. Neden irtifa seçimi tasarımın merkezinde?

Venüs yüzeyindeki sıcaklık yaklaşık **465 °C**, basınç ise yaklaşık **92 bar** düzeyindedir. NASA'ya göre yaklaşık **50 km irtifada** sıcaklık kabaca **30–70 °C**, basınç ise Dünya deniz seviyesine yakın olabilir. Fakat bu irtifa sülfürik asit içeren bulut ortamına ve güçlü atmosferik dolaşıma karşı koruma gerektirir.

**Bu değerleri kesin operasyonel aralık gibi değil, önce kontrol edilmesi gereken tipik atmosfere ait yaklaşık referanslar gibi kullanın.** Modelin enlem, yerel zaman, irtifa ve kaynak belirsizlikleri ayrıca belirtilmeli.

### C1. Değişkenleri açık tanımlayın

- $h$: yüzeyden yükseklik [km]
- $T(h)$: atmosfer sıcaklığı [K veya °C, birim açık yazılmalı]
- $p(h)$: basınç [Pa/bar]
- $\rho(h)$: atmosfer yoğunluğu [kg/m³]
- $u_{wind}(h)$: yerel rüzgâr ve atmosfer dolaşımı [m/s]
- $g_V$: Venüs yerçekimi ivmesi, yaklaşık **8.87 m/s²**

### C2. İrtifa seçim matrisi — önce sayısal kaynakla doldurulacak

| Kriter | Daha alçak irtifa | 50–60 km çevresi | Daha yüksek irtifa |
|---|---|---|---|
| Sıcaklık | Artar; sistemleri zorlaştırır | Nispeten ılımlı olabilir | Genelde azalır |
| Basınç/yoğunluk | Artar; mekanik yük artabilir | Uçuş için araştırmaya değer | Düşer; rotor alanı/gücü etkilenir |
| Kimyasal ortam | Bölgeye bağlı risk | Sülfürik asit bulutları önemli | Bulut/haze profilini kontrol et |
| Enerji | Güneş ışığı sınırlı olabilir | Optik geçirgenlik ayrıca incelenmeli | Solar potansiyel daha iyi olabilir |
| Kontrol/iletişim | Görev geometrisine bağlı | Rüzgâr sürüklenmesi ve röle tasarımı | Uzun menzil/enerji sorunları |

Bu tablo **nitel** değerlendirmedir; kesin trend ve sayılar resmi atmosfer profilinden seçilmeli.

## D. Rotorcraft için ilk fizik modeli — [ÖNERİ]

### D1. Havırda kalma kuvveti

Rotorların toplam itkisinin en az ağırlığı dengelemesi gerekir:

\[
T_\mathrm{total}\geq mg_V.
\]

### D2. İdeal indüklenmiş güç ilk yaklaşımı

Tek bir eşdeğer aktüatör disk alanı $A$ ve durağan atmosfer varsayımıyla:

\[
P_{i,ideal}=\frac{T^{3/2}}{\sqrt{2\rho A}}.
\]

Bu, **momentum teorisinin ideal alt sınırıdır**; gerçek elektrik gücünü hesaplamak için rotor profil sürüklemesi, motor/verim, kontrol rezervi ve irtifa/rüzgâr koşulları eklenmelidir. Olası çok rotorlu düzen için toplam disk alanı hesap yöntemi açık yazılmalıdır.

### D3. Rotor boyutlandırma girdileri

- Araç toplam kütlesi, bilim yükü, batarya/enerji sistemi.
- Rotor sayısı, yarıçapı, disk yüklemesi, devir/dönme yönü.
- Hava yoğunluğu ve kinematik viskozite; rotor Reynolds/Mach rejimi.
- Rotor malzemesinin kimyasal dayanımı ve yorulma ömrü.
- Sürekli hover yerine ileri uçuş/dolaşım konsepti varsa uçuş zarfı.
- Yedekli itki/arıza toleransı ve denge kontrolü.

**Varsayım uyarısı:** “Venüs yoğun atmosferli, o yüzden drone kolay uçar” demek yeterli değildir. Yerel yoğunluk, rotor momentleri, enerji ve korozyon etkileri birlikte değerlendirilmelidir.

## E. Temel alt sistemler — [ÖNERİ]

### E1. Rotor ve sevk sistemi

- Quadrotor / hexarotor gibi rotorcraft konfigürasyonu seçin.
- Kaldırma kuvveti ve güç bütçesini atmosfer profiline bağlayın.
- Motorsuz aerostat/hibrid eklenirse bu seçeneğin mentor onayına bağlı olduğunu belirtin.

### E2. Enerji

- Güneş paneli: seçilen yükseklikte güneş akısı, bulut optik etkisi, gece döngüsü.
- Batarya: kullanım süresi, enerji yoğunluğu, ısı yönetimi, yaşlanma.
- Daha uzun süreli görev için başka güç seçenekleri ancak görev kısıtlarına göre gerekçelendirilmeli.

Basit görev enerjisi:

\[
E_\mathrm{req}=\int_0^{t_m}(P_\mathrm{prop}+P_\mathrm{avionics}+P_\mathrm{thermal}+P_\mathrm{payload})\,dt.
\]

### E3. Termal ve kimyasal dayanım

- İrtifa sıcaklığına uygun kapalı elektronik muhafaza.
- Asitli aerosol ve gazlara karşı malzeme/kaplama/conta konsepti.
- Motor, elektronik ve güç elemanlarından kaynaklanan atık ısı.
- Malzemenin sıcaklık ve kimyasal dayanımını ayrı değerlendirme.

### E4. Kontrol / navigasyon

- Dünya benzeri GPS varsayılmamalı.
- Ataletsel ölçüm (IMU), optik/uygun çevresel referanslar, basınç tabanlı irtifa ve olası radyo/röle konumlandırması.
- Aşırı rüzgârda **hava hızını** ve **yer hızını** ayrı değerlendirin.
- Haberleşme gecikmesi nedeniyle kapalı çevrim kontrol yerel ve otonom olmalı.

### E5. Haberleşme

- Araç ↔ Venüs yörünge rölesi ↔ Dünya mimarisi düşünülebilir.
- Bulut içi zayıflama, anten yönelimi, veri hızı, güç bütçesi ve bağlantı pencereleri değerlendirilmelidir.
- Yörünge rölesi zorunluluğu notta yazmıyor; **olası çözüm**.

## F. “How does it get there?” — ulaştırma ve konuşlandırma

Mantıklı kavramsal görev akışı:

1. Dünya'dan fırlatma.
2. Gezegenler arası Venüs transferi.
3. Venüs'e yaklaşma ve giriş geometrisinin belirlenmesi.
4. Isıl koruma sistemiyle atmosferik giriş.
5. Uygun hız/irtifada koruyucu kabuktan ayrılma ve rotorcraft açılımı.
6. Kanat/rotor açılımının ve motorların güvenli devreye girmesinin doğrulanması.
7. Hedef irtifa bandında kontrol ve bilim operasyonları.
8. Görev sonu/arıza durumunda çevreye ve araca ilişkin davranışın belirtilmesi.

**Kritik açık problem:** Rotorcraft atmosferik giriş yüklerine doğrudan dayanacak şekilde tasarlanmış kabul edilmemeli; giriş aracı/koruyucu kapsül ve açılma koşulları düşünülmeli.

## G. Altı saatlik çalışmaya uygun önerilen plan

El yazısında **Friday afternoon – 6 hour** var. Bu, yaklaşık altı saatlik oturuma göre tasarlanmış bir çalışma planıdır; resmî iş dağılımı değildir.

| Süre | Üretilecek çıktı |
|---|---|
| İlk 45 dk | Görev amacı, irtifa adayları, varsayım tablosu |
| Sonraki 60 dk | Atmosfer profili ve irtifa seçimi / gerekçesi |
| Sonraki 75 dk | Rotor boyutlandırma, kütle ve ilk güç hesabı |
| Sonraki 60 dk | Termal, güç, kontrol, iletişim, malzeme açıklaması |
| Sonraki 60 dk | Görsel tasarım, konuşlandırma sekansı, risk tablosu |
| Son 60 dk | Tutarlılık ve birim kontrolü, kısa sunum / teknik özet |

### G1. Teslim edilecek görselin içermesi gereken etiketler

- Rotor grubu ve motorlar
- Gövde, bilim yükü, batarya/güç
- Aviyonik ve kontrol bilgisayarı
- Anten/iletişim birimi
- Termal/kimyasal koruma
- Gerekirse açılma/iniş/giriş bağlantı noktaları

### G2. Tek sayfalık sayısal kanıt

Aşağıdaki maddelerden en az birkaçını **kaynaklı** biçimde göstermeye çalışın:

- Seçilen irtifa $h$ ve $T,p,\rho,u_\mathrm{wind}$.
- Toplam tasarım kütlesi ve hover itkisi.
- Rotor toplam alanı ve ideal indüklenmiş güç.
- Tahmini sistem güç bütçesi ve görev enerji gereği.
- En az üç baskın teknik risk ve bunlara karşı önlem.

## H. Muhtemel teknik riskler

| Risk | Neden | Çözüm konsepti |
|---|---|---|
| Asitli atmosferde degradasyon | Kaplama/elektrik/rotor etkilenir | Kimyasal dayanım ve sızdırmazlık tasarımı |
| Enerji yetersizliği | Rotorların sürekli güç çekmesi | Görev profili, güç bütçesi, uygun operasyon modu |
| Rüzgârla sürüklenme | Yüksek atmosferik hızlar | Yer hızı/iz planlama ve otonom kontrol |
| İrtifa kaybı | Yoğunluk/sıcaklık değişimi | İtki rezervi, irtifa kontrolü, güvenli mod |
| Konuşlandırma arızası | Açılma zamanı/kuvvetleri | Giriş–ayrılma–rotor devreye alma planı |
| İletişim kesilmesi | Görüş hattı / bulut / güç | Yerel veri saklama ve önceden tanımlı otonom mod |
| Bilim verisi kalitesizliği | Sensör kalibrasyonu/kimyasal etkiler | Kalibrasyon planı ve ölçüm hatası analizi |

## I. Mentora sorulacak sorular

1. **Rotorcraft kesin zorunlu mu?** Balon destekli bir hibrit sistem kabul ediliyor mu?
2. İrtifa, görev süresi, bilim yükü veya toplam kütle için sınır var mı?
3. **6 saat**, toplam tasarım süresi mi yoksa oturumun süresi mi?
4. CAD/görsel için belirli yazılım zorunluluğu var mı?
5. Sayısal analiz hangi düzeyde isteniyor (conceptual / sizing / detailed simulation)?
6. Venüs atmosfer modeli veya veri seti verilecek mi?
7. İletişim için yörünge rölesi varsayılabilir mi?

## J. Kaynaklar

- LuGus–Skypersonic **Mars Drone Simulator**: https://www.lugus-studios.be/portfolio/mars-drone-simulator
- LuGus çalışma alanı: https://www.lugus-studios.be/
- NASA **Venus facts** (yaklaşık 50 km atmosfer koşulları): https://science.nasa.gov/venus/venus-facts/
- NASA/JPL **Aerial Platforms for the Scientific Exploration of Venus**: https://science.nasa.gov/resource/aerial-platforms-for-the-scientific-exploration-of-venus/

**Sonuç:** LuGus için resmi notun en merkezi çıktısı **belirli bir Venüs irtifasında fiziksel olarak savunulabilir rotorcraft konsepti**, görsel alt sistem yerleşimi ve “nasıl gider / nasıl açılır / nasıl çalışır?” sorularının birbiriyle tutarlı yanıtıdır.


---

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
