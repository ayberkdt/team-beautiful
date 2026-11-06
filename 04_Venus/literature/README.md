# Venüs literatürü: kaynak notları

Her kaynak için bir dosya vardır. Notlar konuya göre klasörlere ayrıldı, dosya adları değişmedi. Bütün notların listesi:
`catalog/literature.md`.

| Klasör | Ön ek | Okuyan | Konu | Dizin |
|---|---|---|---|---|
| `atmosphere/` | `A_` | araştırma ajanı A | atmosfer: Pioneer Venus sondaları (PDS ham verisi), VEGA balonları, rüzgârlar (VEX, Akatsuki), güneş akısı, bulutlar, şimşek, CO₂ özellikleri; VIRA'ya erişilemedi | `A_00_index.md` |
| `missions/` | `B_` | araştırma ajanı B | görev örnekleri: Venera 4–14, Vega, Pioneer Venus, DAVINCI, JPL aerobotları, VAPS, Landis uçağı, NASA Ames Venüs döner kanadı (Young 2026) | `B_00_index.md` |
| `rotorcraft/` | `C_` | araştırma ajanı C | rotorlu hava aracı: Ingenuity, MSH, Dragonfly, Harrington 1951 ve Knight–Hefner 1937 (BEMT doğrulama verisi), eş eksenli teori, düşük Re kanat kesitleri | `C_00_index.md` |
| `engineering/` | `D_` | araştırma ajanı D | mühendislik sabitleri: Sutton–Graves, Tauber ışınımı, H₂SO₄ karşısında malzemeler, piller, güneş hücreleri, haberleşme, mıknatıslar, elektronik | `D_00_index.md` |
| `simulator/` | `E_` | simülatör veri kitabı ajanı (5 Kasım 2026) | PV, VEGA, NIST ve JPL verileri yeniden okundu; RO ısıl yapısı, LES konveksiyonu, dinamik derlemesi, bulut mikrofiziği, Dryden, VRS, dinamik akış, çok rotorlu etkileşim, MSH ağırlıkları, LuGus/Skypersonic simülatörü, Venus Flagship aerobotu | `E_00_index.md` |
| `data/` | | aynı ajan | `venus_atmosphere_40_70km.csv` (+ `.md`), `venus_turbulence_model.json` | |

`K_*` ve `R_*` dosyaları burada değildir. Onlar `reviews/` klasöründedir, çünkü literatür değil, bu çalışmanın kendi
kontrolleridir:

| Ön ek | Okuyan | İçerik |
|---|---|---|
| `K_` | Venüs oturumu | oturumun kendi okuduğu kaynaklar ve hesap kontrolleri: NIST CO₂ verisi (`K_nist_co2_properties`), giriş modeli karşılaştırmaları (`K_entry_crosschecks`), doc 25 incelemesi (`K_review_doc25`) |
| `R_` | bağımsız denetim ajanı, sonra Venüs oturumu | `R_audit_2026-11-04`: doc 25'ten rastgele seçilen 15 [D]/[D-ag] değer kaynağında yeniden okundu, işaretlenen her madde çözüldü; `R_jury_questions_2026-11-04`: jüri soruları |

## Etiketler

Notların içinde: **[D-ag]** ajan kaynakta okudu, **[A]** yalnız özet, parça ya da ikincil kaynak, *derived* ya da *[calc]*
ajanın kendi hesabı. Kodda ve `04_Venus/docs/25_lugus_venus_rotorcraft.md` belgesinde bunlar [D-ag] olur. Venüs oturumunun
kendi okuduğu ya da çıkardığı değerler [D] olur: NIST tabloları, JPL SSD sabitleri ve
`04_Venus/code/data/venus_pds_extract.py` ile çıkarılan Pioneer Venus PDS tabloları.

İndirilen dosyalar yalnız veridir, depoda değildir: `D:\tmp_ideathon\venus\downloads\{atmo,missions,rotor,eng,nist}\`.
