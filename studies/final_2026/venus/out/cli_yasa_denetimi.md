# YASA DENETİMİ — `python scripts/venus_day.py --final` (CLI çıktısı) · 4 Kas 2026 · denetleyici: koşmadı (yüzey: cli)

GÖREV BÜTÇESİ (geç yazıldı: kod önce vardı; bütçe sonradan uygulandı ve bulduğu tek eksik — Zirve-Son — düzeltildi)
- Birincil görev: koşu başarılı mı + başlık sayıları · Birincil eylem: 1 (son satırdaki "Next:" adımı)
- Komut: 2 mod (kart, final) ≤ 7 · Tablo sütunu: 3 ≤ 7 · Geri bildirim: 5 ilerleme satırı (stderr) · Vurgu: yok (düz metin; hata = çıkış kodu 1)

Sonuç: 20/20 yasa ölçüldü · 0 HATA · 1 UYARI (gerekçeli) · karar: TESLİM

| #  | Yasa             | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe (yalnız UYARI) |
|----|------------------|---------------------|------|-------|------------------------|
| 1  | Hick             | 2 mod (kart dosyası, `final`); final modunda 4 isteğe bağlı seçenek (`--payload-kg`, `--cruise-km`, `--rotor-d`, `--reuse`) | ≤ 7 · seçenek ≤ 5 | geçti | |
| 2  | Fitts            | kapsam dışı: tıklanacak hedef yok (terminal metni) | — | kapsam dışı | |
| 3  | Jakob            | `-h/--help`, dosya argümanı, çıkış kodu 0/1 — mevcut `*_day.py` betikleriyle aynı desen | 0 sapma | geçti | |
| 4  | Seçim Yükü       | 4 seçenek, hepsinin varsayılanı var (taban tasarım, tam hesap) | ≤ 5 / varsayılan | geçti | |
| 5  | Yakınlık         | 3 blok: ilerleme (stderr) · sonuç tablosu + olaylar · denetim + sonuç satırı; bloklar boş satırla ayrık | gruplu | geçti | |
| 6  | Benzerlik        | tablo satırları tek biçim "nicelik · değer · etiket"; olaylar tek biçim "- t h — olay" | tek biçim | geçti | |
| 7  | Tekdüze Bağlılık | 14 tablo satırı tek tabloda, 7 olay tek listede | ≤ 12 grup başına | UYARI | sonuç tablosu 14 satır: hepsi docs/25'in "tek sayfa kanıt" listesi, bölünürse kopyalanabilirlik kaybolur |
| 8  | Ortak Bölge      | kutu/çerçeve yok; Markdown tablosu tek bölge | 0 tek öğeli kutu | geçti | |
| 9  | Prägnanz         | renk/emoji/süs yok; 32 satır stdout | 0 süs | geçti | |
| 10 | Von Restorff     | tek vurgu: son satır (sonuç + sonraki adım); renk kullanılmıyor | 1 | geçti | |
| 11 | Miller           | tablo 3 sütun; olay listesi 7 madde | ≤ 7 | geçti | |
| 12 | Sıra Konumu      | ilk: kütle/atmosfer satırları (55 km koşulu); son: görev özeti + sonraki adım | birincil görev uçlarda | geçti | |
| 13 | Zirve-Son        | son satır: "VESPER 43.7 kg, 49 h flight; figures audited, deliverable. Next: read docs/25…" (önce: son satır bir olaydı → düzeltildi) | sonuç + tek adım | geçti | |
| 14 | Zeigarnik        | 5 ilerleme satırı (`> closing…`, `> power…`, `> Pioneer…`, `> BEMT…`, `> drawing… F1-F10`) | çok adımlı işte ilerleme | geçti | |
| 15 | Doherty          | > 400 ms her aşama ilerleme satırıyla başlıyor (tam koşu ~2 dk; `--reuse` ~1 dk) | gösterge var | geçti | |
| 16 | Postel           | `final`/`--final`/`-FINAL`; `--payload-kg 5`, `--payload-kg=5`, `--payload_kg 5,0` hepsi kabul; bilinmeyen seçenekte tek satır doğru kullanım; çıktı tek biçim | hoşgörülü girdi | geçti | |
| 17 | Tesler           | süpürme dosyaları kendiliğinden okunuyor; mentor sayılarıyla koşu ayrı klasöre yazılıyor, taban dosyaları korunuyor (kullanıcıya sorulmuyor) | sisteme taşındı | geçti | |
| 18 | Parkinson        | zorunlu girdi 0 | ≤ %50 | geçti | |
| 19 | Occam            | birim/etiket her satırda bir kez; tekrar eden açıklama yok | gereksiz öğe 0 | geçti | |
| 20 | Pareto           | ilk 6 satır sorunun %80'i: atmosfer, kütle, rotor, güç, güneş, pil | birincil önde | geçti | |

Riskler: Windows cp857/1254 konsolunda özel karakterler `day_common.console_text` ile ASCII'ye çevriliyor (ölçüm UTF-8 terminalde yapıldı).
