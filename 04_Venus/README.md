# 04_Venus: VESPER (LuGus "Fly on Venus", final 2026)

Bu klasör Venüs görevinin her şeyini tutar. Ortak kütüphane `src/aerokit/venus/` ve `src/aerokit/venus_flight.py`
içindedir, testleri `tests/test_venus_*.py`. Görev açıklanmadan önceki tahminler ("Drones on Venus", doc 19):
`prev_guess/04_Venus/`. Sahibi: Venüs oturumu (bkz. `00_Common/docs/21_final_challenges_coordination.md`).

## Seçilen tasarım (6 Kasım)

Resmî görev kısa bir teknoloji gösterimi istiyor; bilim hedefi yok. Kullanıcı kararı: **0,5 kg uçuş kamerası, 38,23 kg**.
Geçerli dosyalar `outputs/variants/short_demo/files_0p5kg/` altındadır (`design.json`, `sim_params.json`). `outputs/design.json` (v0.6, 43,66 kg) tarihî taban olarak durur; testler ona bağlıdır. Görev metni: `official_2026-11-06/`.

## Nereden başlanır

1. Ana belge: `docs/25_lugus_venus_rotorcraft.md`.
2. Bir şeyi aramak için: `catalog/README.md`. Bileşen, figür, betik, not ve veri dosyası listeleri oradadır.
3. Sonuçları yeniden üretmek için: `code/README.md`.

## Klasörler

| Klasör | İçerik |
|---|---|
| `catalog/` | üretilmiş kataloglar ve 6 Kasım taşımasının kaydı (`reorg_manifest.json`) |
| `code/` | betikler: `pipeline/`, `analysis/`, `data/`, `variants/`, `catalog/` |
| `literature/` | kaynak notları, konuya göre: `atmosphere/`, `missions/`, `rotorcraft/`, `engineering/`, `simulator/`, `data/` |
| `reviews/` | hesap kontrolleri (`K_*`), denetimler ve jüri soruları (`R_*`); literatür değildir |
| `docs/` | `25_lugus_venus_rotorcraft.md` ana belge, `26_venus_sim_databook.md` veri kitabı, `versions/` eski hâller |
| `outputs/` | üretilen bütün dosyalar, aşağıda listeli |
| `submission/` | teslim raporu (LaTeX) |
| `company/` | LuGus Studios şirket dosyası: profil, oyunlar, iş tarzı, Mars simülatörü, Venüs için çıkarımlar, kaynaklar |
| `visual/` | üretilmiş 3B kareler ve filmler; kodu Sunumatik deposunda (`code/visual/README.md`) |

Notlardaki yalın dosya adı atıfları geçerlidir: dosya adları değişmedi, yalnız klasör değişti. Adı bilinen bir notun
klasörü `catalog/literature.md` dosyasındadır.

## `outputs/` içindekiler

Yollar `outputs/` klasörüne göredir. Komutlar proje kökünden koşulur.

| Dosya | İçerik | Üreten komut |
|---|---|---|
| `design.json` | **3B görsele teslim dosyası** (şema `venus_rotorcraft_design/1`): 30–80 km atmosfer, bantlar ve güneş oranı, çalışma bandı, rotor, gövde ve güneş paneli geometrisi, 13 etiketli bileşen (konum, boyut, kütle, malzeme, renk, etiket), katlı zarf, giriş ve açılma sırası (irtifa, zaman), görev olayları ve saatlik seriler | `python 04_Venus/code/pipeline/venus_design.py` (`venus_day.py --final` de koşar) |
| `versions/` | önceki her `design.json`, üzerine yazılmadan önce saklanır (ad = sürüm + hash) | aynı |
| `result.json`, `result.md` | hesaplanan bütün sayılar (araç, giriş, görev, haberleşme, hibrit, BEMT doğrulaması, riskler) | `python 04_Venus/code/pipeline/venus_day.py --final` |
| `F1…F15.{png,pdf}`, `*.denetim.txt` | denetlenmiş slayt figürleri (datawiz, `sunum-tam`); set sözleşmesi `vesper.seti.json`, tutarlılık `vesper.tutarlilik.txt` | aynı |
| `trade_sizing.json` | 72 kapalı tasarım (rotor çapı × uç hızı × güneş seçeneği) | `python 04_Venus/code/analysis/venus_trade.py` (~8 dk) |
| `variants/out_variant_*/`, `variants/design_variant_*.json` | mentor sayılarıyla "ya şöyle olsaydı" koşuları (`--payload-kg`, `--cruise-km`, `--rotor-d`); taban dosyaların üzerine yazmaz | `python 04_Venus/code/pipeline/venus_day.py --final --payload-kg 5` |
| `variants/budget_update/` | 6 Kasım bütçesi: rotor–rotor etkileşimi, VEGA rüzgâr zaman ölçeği, uçulabilir iniş, kapalı tasarım seçenekleri (`result.json`, `result.md`, B1–B3, `sim_runs/`) | `python 04_Venus/code/analysis/venus_budget_update.py` (~13 dk; `guc_egrisi.json` okur) |
| `variants/v0_7_44p6kg/` | 44,63 kg varyantı, onaylanmadı; önce `CHANGES.md` okunur | `python 04_Venus/code/variants/venus_variant_v07.py` |
| `sensitivity.json` | tek tek duyarlılık (19 kapalı tasarım yeniden uçuruldu) | `python 04_Venus/code/analysis/venus_sensitivity.py` (~6 dk) |
| `sim_params.json`, `sim_params_README.md` | **LuGus simülatör parametreleri**: 30–80 km atmosfer, rüzgâr ve güneş tablosu, rotor eğrisi, kütle ve atalet, sınırlar, arıza modları, açılma tekrarı, görev serisi; her değerde birim, etiket ve kaynak | `python 04_Venus/code/pipeline/venus_sim_params.py` |
| `crosscheck.json`, `.md` | başlık sayıları daha basit yöntemlerle yeniden çıkarılır (momentum teorisi + FM aralığı, yukarıdan aşağı kütle oranı, elle enerji dengesi) | `python 04_Venus/code/analysis/venus_crosscheck.py` |
| `entry_validation.json`, `.md` | giriş modeli, 12 tarihsel Venüs girişi ve DAVINCI ile karşılaştırılır | `python 04_Venus/code/analysis/venus_entry_validation.py` |

## Görsel için sabit sözleşme

Kimlikler ve anahtarlar sürümler arasında değişmez, sayılar değişebilir. Birimler SI. Çerçeve: başlangıç gövde
merkezi, x ileri (1. ve 6. kol arası), y sol, z yukarı, kollar açık havada asılı. Her blokta etiket vardır:
`D` bu oturumda birincil veriden okundu, `D-ag` araştırma ajanı okudu, `K` hesaplandı, `Y` varsayım.
