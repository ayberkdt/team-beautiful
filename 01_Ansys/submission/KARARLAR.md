# Ansys raporu — kararlar ve mentor cevapları

Bu dosya rapora girecek varsayımların tek kaydıdır. Her satır: ne, kaynağı, tarih.
[Kart] = `official_2026-11-05/files/Ideathon_Challenge_Ansys_2026.docx`; [Mentor] = kullanıcının ilettiği mentor
cevabı; [Y] = ekibin yorumu (raporda "assumption" diye yazılır).

| # | Konu | Karar | Kaynak | Tarih |
|---|---|---|---|---|
| 1 | Güvenlik katsayısı 1.5 neye uygulanır | **Akma dayanımına (yield)**, tercihen: 1.5 × σ_vM,max ≤ σ_y | [Mentor] | 5 Kas 2026 ~13:45 |
| 2 | σ_y hangi sıcaklıkta | 300 °C değeri (organizatör yalnız 23 °C veriyor; düşüm katsayısı katalogdan) | [Y], mentora sorulmadı | 5 Kas 2026 |
| 3 | LC1 ve LC2 | Ayrı yük durumları; topoloji optimizasyonu hepsini birlikte (çok yük durumlu, normalize ağırlıklı esneklik); doğrulamada LC1+LC2 birlikte de kontrol | [Y] (kart iki ayrı numaralı madde) | 5 Kas 2026 |
| 4 | 97 kN / ±24 kN | Her pim deliğine ayrı ayrı | [Y], mentora sorulacak | 5 Kas 2026 |
| 5 | Yer değiştirme sınırı | 661 mm / 400 = 1.65 mm | [Kart] + [Y] (en büyük boyut = sınır kutusu) | 5 Kas 2026 |

Not (5 Kas 13:50): Analiz betikleri (`analysis/t10check.py`, `final_choice.py`, `evaluate_layouts.py`) karar 1'i zaten
kullanıyor. `aerokit.bracket.pipeline` ise `max(σ/Fty, 1.5σ/Ftu)` kullanıyor → düzeltme isteği dosyaların sahibi olan
"Ansys challenge incelemesi" oturumuna iletildi; o düzeltilene kadar `runs/*/report.md` içindeki geçti/kaldı satırlarını
rapora doğrudan aktarma.

Güncelleme (5 Kas ~14:00): o oturum `pipeline.strength_util()` ekledi (`strength_basis: "yield"` → U = 1.5σ/Fty(T)),
resmî v2 kurulumunda açık; `tests/test_bracket_strength_basis.py` burada da koşuldu: 3 passed. Kalan: `report.py`
satır 350'deki kriter cümlesi hâlâ eski (Ftu) kuralı yazıyor → o oturuma bildirildi. `finalize_v2_45.json` (542 MPa)
o oturuma göre GEÇERSİZ; rapor sayıları `analysis/verify_v2.json` ve `analysis/finalize_v2_<tag>.json` son hâlinden alınacak.
