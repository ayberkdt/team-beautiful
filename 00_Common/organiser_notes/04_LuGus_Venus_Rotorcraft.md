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
