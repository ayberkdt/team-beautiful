# 05 · Venüs görevi için çıkarımlar

Tarih: 2026-11-06. **Bu dosyanın tamamı yorumdur [Y].** İçindeki olgular ayrıca kaynak kodu taşır. Resmî ölçütler artık biliniyor: konseptin gerçekçiliği, simülatörde uygulanabilirlik, teslim kalitesi (`../official_2026-11-06/`). Aşağısı şirket davranışından çıkarımdır.

## 1. Önce şu ayrımı yapın

- Organizatör notunun istediği çıktı bir rotorcraft konseptidir: görsel tasarım, irtifa gerekçesi, alt sistemler, fizibilite ve riskler. [D, L3]
- Resmî görev simülatör teslimi istemiyor, ama simülatörde uygulanabilirliği ölçüt yapıyor. En iyi fikirler Liftoff: Offworld'de uçulabilir göreve dönüşebilir. [D, resmî görev PDF'i]
- Mars işi notta LuGus'un geçmişi olarak yazıyor. [D, L3]
- Ana çıktı yine rotorcraft konseptidir; simülatör parametreleri ve uçuş sonuçları bunun fizibilite kanıtıdır. [Y]
- Doc 26 §9'daki "pilot simülatörü mü, mühendislik motoru mu" sorusu hâlâ açık. [D, L2]

## 2. LuGus jürisi neye değer verebilir

1. **Parçadan çıkan davranış.** Stüdyonun temel iddiası, uçuşun parçaların birlikte çalışmasından doğmasıdır. [D, S11] Aracınızı batarya, motor, rotor, gövde, kontrolcü diye ayrı parçalarla anlatın. [Y]
2. **Ölçülmüş veri.** Üretici verisine güvenmeyip test verisiyle ölçekliyorlar. [D, N02] Sayıların yanında kaynağı ve belirsizliği yazın. [Y]
3. **Bilinçli yaklaşıklık.** Hesap maliyeti için 42 açılı ön hesap yapıyorlar ve bunu açıkça anlatıyorlar. [D, S11, S24] Basitleştirmeyi saklamak yerine neden seçtiğinizi söyleyin. [Y]
4. **Tek düğme çözüme karşı olmak.** Yerçekimi çubuğu isteğini reddediyorlar. [D, S11] Venüs'te de asıl değişen yerçekimi değil, yoğunluk, sıcaklık ve rüzgârdır. [Y]
5. **Eğitim ve iş değeri.** Slogan ciddi oyunlardır; portfolyonun yarıdan fazlası eğitim, sağlık ve kamu işidir. [D, S01, S02] "Bu tasarım kimi neyle eğitir?" sorusuna tek cümle hazırlayın. [Y]
6. **Pilot hissi.** Son doğrulayıcı olarak pilotu gösteriyorlar. [D, N07] Kontrol hissini de konuşun; yalnız güç tablosu yetmez. [Y]
7. **İyi görsel, açık anlatım.** Ortam kalitesi ve gerçek parça kopyası ürünün parçasıdır. [D, S17] Görsel, bileşenleri ayırt ettirmeli. [Y]

## 3. Görsel tarafta neyi taklit etmeli

- **Bir sahne, bir hikâye.** Mars görseli rover, drone ve örnek tüplerini bir karede veriyor. [D, S75] Venüs için bulut katmanında aracı, bilim yükünü ve görev anını tek kareye koyun. [Y]
- **Ölçek için tanıdık nesne.** Mars karesinde ölçeği rover veriyor. [D, S75] Venüs'te yer görünmez; araç üzerinde kişi siluetiyle ya da ölçek çubuğuyla ölçek verin. [Y]
- **Simge nokta.** Permafrost sorununda her yerin aynı görünmesi yön kaybı yarattı. [D, N12] Bulut içi sahne aynı riski taşıyor. Doc 26 görüş mesafesini orta bulutta yaklaşık 2 km veriyor. [D, L2] Katman sınırı, güneş yönü, rüzgâr çizgileri ile yön verin. [Y]
- **Görünmeyeni göster.** Liftoff rüzgârı isteğe bağlı görselleştiriyor. [D, N10] Süper rotasyon ve iniş akımını okla ya da akış çizgisiyle gösterin. [Y]
- **OSD dili.** Liftoff batarya akımı, mAh ve hücre voltajı gösteriyor. [D, N10] Görsele irtifa, ρ, T, rotor rpm, batarya, güneş gücü göstergesi ekleyin. [Y]
- **FPV lens etkisi.** Liftoff'ta kamera bükülmesi seçeneği var. [D, N07] Aracın kamerasından bir kare, tanıdık bir dil olur. [Y]
- **Gündüz ve gece.** Micro Drones aynı mekânın iki sürümüyle çalışıyor. [D, N14] Venüs'te gündüz ve gece farkı enerji anlatımı için doğal iki kare verir. [Y]
- **Parça sayfası.** Workbench mantığıyla kütle ve güç tablosunu parça kartları gibi gösterin. [D, S17] [Y]

## 4. Simülasyon tarafında neyi taklit etmeli

Sıralama, doc 26 §7'deki etki sırasına dayanıyor. [D, L2]

- **Korunacak iskelet:** Parça tabanlı güç zinciri, uçuş kontrolcüsü, batarya sag, gerçek zamanlı 6-DOF. [D, S11] [Y]
- **Değişecek ilk şey:** Sabit havadan irtifaya bağlı yoğunluğa geçiş. Doc 26: ρ(52)/ρ(55) = 1,40. [D, L2]
- **Rüzgâr:** Liftoff rüzgârı arazi çevresinde akıyor. [D, N07] Venüs'te referans çerçevesi hava kütlesi olmalı. Doc 26: 50-60 km'de 60-85 m/s rüzgâr, aracın azami hava hızı yaklaşık 23 m/s. [D, L2]
- **Rotor:** Liftoff'un itki modeli küçük FPV parçaları üzerine kurulu. [D, S11] Doc 26 yavaş büyük rotor, collective kontrol ve 1,2-3,9 m/s inişte VRS riski yazıyor. [D, L2] Doğrudan taşınır demeyin. [Y]
- **Yerçekimi:** Sabit kalsın. Doc 26 §6.2 8,71 m/s² kullanıyor; organizatör notu 8,87 m/s² yazıyor. [D, L2, L3] Biri irtifa, diğeri yüzey değeri gibi duruyor; slaytta hangisini kullandığınızı söyleyin. [Y]
- **Sinyal:** Liftoff RC bozulmasını endüstri ürünlerinde açıyor. [D, S11] Röle penceresi ve bağlantı kaybını aynı mantıkla anlatın. [Y]
- **Pilot:** Canlı kumanda değil denetimli özerklik. Doc 26: 2,3-14,3 dakika ışık süresi. [D, L2]
- **Doğrulama dili:** "Doğrulandı" demeyin. "Şu kaynakla karşılaştırıldı, şurası yaklaşık" deyin. [Y]

## 5. Kaçınılacaklar

- NASA ile LuGus arasında doğrudan iş varmış gibi konuşmayın; `04_mars_drone_simulator.md` bölüm 7'ye bakın. [Y]
- Liftoff: Offworld'ü çıkmış ürün gibi anmayın; bugünkü durum bilinmiyor. [D, S13, S38]
- Red Cat satın almasını gerçekleşmiş gibi anlatmayın. [D, S44-S48]
- Mars simülatörünün yerçekimi ya da atmosfer değerini biliyormuş gibi konuşmayın. [D, S07]
- Ukrayna ve askerî kullanım konusunu siz açmayın; şirket için kişisel ve hassas bir konu. [D, S09] [Y]
- Dinamik rüzgârı 2022 Mars işine bağlamayın. [D, N10]
- "Oyun" sözcüğünü küçümseyici kullanmayın; şirket simülasyon teknolojisi sağlayıcısı olarak ödül aldı. [D, S53] [Y]

## 6. Jürinin sorabileceği sorular

Cevap hazırlığı, doc 25 ve doc 26'dan yapılmalı. Doc 25'i bu oturumda okumadım.

1. Bu aracı bir pilot nasıl uçurur? Gecikmede pilotun görevi nedir? [Y]
2. Kontrol hissi nasıl? Düşük disk yüklemeli büyük rotor ne kadar hızlı tepki verir? [Y]
3. Yoğunluk değişince itki ne olur? Kontrolcü bunu nasıl telafi eder? [Y]
4. Rüzgâr 60-85 m/s iken yerden konum tutmak gerekmiyorsa görev neyi ölçer? [Y]
5. Sayılarınızın hangisi ölçüm, hangisi model, hangisi varsayım? [Y]
6. Modelinizi neyle doğrularsınız? Rüzgâr tüneli ya da CO₂ ortamında nasıl test edersiniz? [Y]
7. Bulut içinde pilot ya da otonomi neyi görür? Görüş 2 km ise navigasyon neye dayanır? [Y]
8. Ana parça arızası: Bir motor durunca ne olur? [Y]
9. Bu tasarım simülatöre girse hangi parçaları ayrı modellersiniz? [Y]
10. Aracın en güzel ve en anlatıcı görüntüsü hangi sahnedir? [Y]
11. Neden rotorcraft? Balon neden yetmez? [D, L3] [Y]
12. Eğitim senaryosu olarak hangi üç görevi önerirsiniz? Doc 26 §6.2 bırakma ve toparlanma, iniş akımı ve röle penceresi gibi adaylar veriyor. [D, L2]

## 7. Mentöre sorulabilecekler

Doc 26 §9'daki listeyi şu hâle getirin. [D, L2]

- Soru 1 hâlâ açık. Mars işi eğitim aracıydı, ama Venüs görevinin çıktısı konsept. [D, S07, L3]
- Soru 2 kısmen yanıtlandı: Core hizmet olarak satılıyor, kamuya açık SDK bulunamadı. [D, S12]
- Soru 3 yanıtsız: Mars işinde yerçekimi, yoğunluk, rüzgâr, gecikme neydi? [D, S07]
- Ek soru: Physics 6.0'daki rüzgâr, yoğunluğu değişen bir atmosfere genişletilebilir mi? [Y]
- Ek soru: Offworld fikri hâlâ yaşıyor mu? Venüs onun için ilginç mi? [Y]
- Ek soru: Sizin için iyi bir görsel, mühendislik çizimi mi, oyun içi sahne mi? [Y]

## 8. Sohbet açıcı üç güncel konu

- Physics 6.0 rüzgâr sistemi, Şubat 2026. [D, N10]
- Liftoff 2.0 deneysel dalı; duyuru 6 Kasım 2026, yani bugün. [D, N13]
- Best Tech Provider ödülü, Aralık 2025. [D, S53]
