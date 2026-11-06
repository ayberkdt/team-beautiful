# Venüs kataloğu

Bu klasör, Venüs çalışmasının dizinidir. Üretilen dosyaları elle değiştirmeyin.

| Dosya | İçerik | Ne zaman |
|---|---|---|
| `components.md`, `components.json` | bileşenler: kütle, malzeme, renk, konum, boyut; v0.6 ile v0.7 yan yana | bir bileşeni ararken |
| `figures.md` | F1–F15, B1–B3, varyant figürleri: dosya, iddia, denetim | slayt ya da rapor için figür seçerken |
| `scripts.md` | her betik: amaç, komut, girdi, çıktı | bir sonucu yeniden üretirken |
| `literature.md` | her not: dosya, konu, başlık, etiket sayısı | kaynak ararken |
| `data_files.md` | `outputs/` ve `literature/data/`: boyut, sha256, üretici | bir dosyanın nereden geldiğini ararken |
| `parts_3d.md`, `parts_3d.json` | 3B mekanizmalar: görev, alt parça, kod, mesh sayısı; `code/visual/build_parts_catalog.mjs` üretir | aracın bir parçasını ararken |
| `reorg_manifest.json` | 6 Kasım taşıması: eski yol, yeni yol, hash, değişiklik nedeni; bir kez yazıldı, bu betik üretmez | eski bir yolu ararken |
| `baseline_hashes_before_2026-11-06.json` | `outputs/` içindeki çapa dosyasının birebir kopyası | çapanın eski değerine bakarken |

## Yeniden üretme

Proje kökünden:

```
python 04_Venus/code/catalog/build_catalog.py
```

Denetlemek için sona `--check` ekleyin. `tests/test_venus_catalog.py` aynı karşılaştırmayı yapar. `outputs/`, `docs/25*.md`, `literature/`, `reviews/` ya da `code/` değişince katalog eskir. Bu komut onu günceller.
