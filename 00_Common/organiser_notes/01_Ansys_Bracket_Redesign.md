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
