# Görsel kod

3B araç, Venüs ortamı ve uçuş simülatörü bu klasörde değildir. Sunumatik deposundadır, çünkü oradaki çekirdek modülleri kullanır.

| Ne | Yer |
|---|---|
| Worktree | `D:\Custom Yetenekler\sunumatik\.claude\worktrees\venus-rotorcraft-visual-44d0d1` |
| Sayfa | `presets/venus_rotorcraft/index.html` |
| Araç mekanizmaları | `presets/venus_rotorcraft/arac/` |
| Ortam | `presets/venus_rotorcraft/ortam/` |
| Uçuş simülatörü | `presets/venus_rotorcraft/sim.html`, `sim/` |
| Doğrulayıcı | `node scripts/validate-venus-rotorcraft.mjs` |
| Kare ve film üretimi | `node scripts/venus-yenile.mjs --zorla` (~30 dk) |

Sayfayı açmak: Claude uygulamasında `venus-sim` önizlemesi ya da worktree içinde `python demo/serve.py 8797`, sonra
`http://localhost:8797/presets/venus_rotorcraft/index.html`.

Tek veri kaynağı `04_Venus/outputs/design.json`. `node scripts/venus-tasarim-al.mjs` onu `tasarim.json` olarak kopyalar.

Bu klasördeki `build_parts_catalog.mjs` mekanizma listesini ölçer, `catalog/parts_3d.md` dosyasını yazar. Üretilmiş kareler ve filmler `04_Venus/visual/` altındadır.
