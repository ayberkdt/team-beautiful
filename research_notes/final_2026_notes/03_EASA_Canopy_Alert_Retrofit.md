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
