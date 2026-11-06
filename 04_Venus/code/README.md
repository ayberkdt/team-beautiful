# Venüs kodu

Bütün komutlar proje kökünden koşulur. Her betiğin amacı, girdisi ve çıktısı: `catalog/scripts.md`.

Windows'ta önce:

```
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
```

| Klasör | Ne yapar | Betikler |
|---|---|---|
| `pipeline/` | taban sonuçları üretir | `venus_day.py` (giriş komutu), `venus_final.py` ve `final_*.py`, `venus_design.py`, `venus_sim_params.py` |
| `analysis/` | ayrı çalışmalar | `venus_trade.py`, `venus_sensitivity.py`, `venus_crosscheck.py`, `venus_entry_validation.py`, `venus_budget_update.py` |
| `data/` | ham veriden kütüphane verisi çıkarır | `venus_pds_extract.py` |
| `variants/` | tabana dokunmayan varyantlar | `venus_variant_v07.py` |
| `catalog/` | `04_Venus/catalog/` dosyalarını üretir | `build_catalog.py` |

## Nereden başlanır

```
python 04_Venus/code/pipeline/venus_day.py --final      # sayılar, F1-F15, design.json, simülatör dosyası
python 04_Venus/code/pipeline/venus_sim_params.py       # sim_params.json (--final sonrasında)
python 04_Venus/code/catalog/build_catalog.py           # kataloglar
```

Uyarı: `--final` taban dosyaların üzerine yazar. `outputs/` altındaki eski `design.json` sürümü `versions/` içine alınır,
ötekiler alınmaz. Yalnız denemek için projenin bir kopyasında koşun: kök `pyproject.toml` dosyasına yürüyerek bulunur,
yani kopya kendi `outputs/` klasörüne yazar.

## Betikler birbirini nasıl bulur

- Kök: her betik `pyproject.toml` dosyasına kadar yukarı yürür. Klasör derinliği önemli değildir.
- `aerokit`: `<kök>/src` yola eklenir. `day_common`: `<kök>/scripts` yola eklenir.
- Aynı klasördeki betik: Python betiğin klasörünü kendisi ekler.
- Başka klasördeki betik: yalnız iki yerde gerekir ve iki yerde de `sys.path` satırı vardır.
  `pipeline/final_compute.py`, `analysis/` klasörünü ekler (`venus_entry_validation`).
  `variants/venus_variant_v07.py`, `pipeline/` ve `analysis/` klasörlerini ekler.

## `venus_final.py` modülleri

`venus_final.py` ince giriştir: `OUT`, `BASE`, komut satırı ve `main()` burada kalır. `OUT` ve `BASE` aşağıdaki modüllere
parametre olarak geçer. Bu yüzden `venus_variant_v07.py` içindeki `mock.patch.object(VFN, "OUT", ...)` bütün yazıcılara ulaşır.
Modüllerde genel durum yoktur.

| Modül | Görev |
|---|---|
| `final_compute.py` | `bemt_validation()`, `compute(BASE, OUT)`: bütün sayılar |
| `final_figures.py` | `figures(c, OUT)`, `figures_extra(...)`, `plt_size()`: F1–F15 |
| `final_sim.py` | `simulator_parameters(c, BASE)`: `vesper_for_simulator.json` içeriği |
| `final_report.py` | `markdown(out)`: `result.md` metni |

## `analysis/venus_budget_update.py` bölüm haritası

Bu dosya bölünmedi. Satır aralıkları dosyadaki bölüm başlıklarına göredir.

| Satırlar | Bölüm | Görev |
|---:|---|---|
| 1–78 | başlık | belge, importlar, yollar, pil sabitleri |
| 79–188 | interaction curves | `Interaction`, `read_curves`, `build_models`, `proximity_f`: `guc_egrisi.json` okuma, etkileşim oranı, rotor aralığı yasası |
| 189–279 | power table | `Profile`, `PowerTable`, `power_table`: görev profili, irtifa ve hıza göre güç tablosu |
| 280–466 | mission | `Flight`, `battery_step`, `fly`, `threshold_mu0`, `window_budget`: görev uçuşu, pil, güneş eşiği |
| 467–550 | gust model | `gust_system`, `gust_model`, `correlation_time`, `ou_series`: rüzgâr modeli, Lyapunov RMS, tohumlu koşular |
| 551–659 | closed designs | `hover_loss`, `close_with_interaction`, `tuned_flight`, `summarise`, `fly_case`: etkileşimle kapanan tasarımlar |
| 660–849 | studies | `gust_study`, `dive_study`, `sim_crosscheck`, `option_rows`, `compute`: çalışmalar, `result.json` içeriği |
| 850–1072 | outputs | `markdown`, `figures`, `main`: `result.md`, B1–B3, komut satırı |

## `variants/venus_variant_v07.py` bölüm haritası

Bu dosya bölünmedi. Satır aralıkları dosyadaki bölüm başlıklarına göredir.

| Satırlar | Bölüm | Görev |
|---:|---|---|
| 1–83 | başlık | belge, importlar, yollar, sabitler |
| 84–181 | the design and its flight | `models`, `recommended`, `vehicle_chain`, `patched`: önerilen tasarımı kapatma ve uçurma |
| 182–264 | sweeps for F7, F9, F10 | `sweep_trade`, `sweep_sensitivity`: varyant için tarama ve duyarlılık |
| 265–322 | numbers of `compute()` | `corrected`, `max_airspeed`: yamalı girdilerden çıkmayan sayıları düzeltme |
| 323–382 | design.json | `design_doc`: varyant tasarım belgesi |
| 383–528 | sim_params.json | `sim_doc`, `mark_sim`, `sim_readme`: varyant simülatör dosyası, değişiklik kaydı, README notu |
| 529–636 | figures | `_f6`…`_f13`, `draw`, `figure_status`: çizim düzeltmeleri |
| 637–769 | CHANGES.md | `leaf_diff`, `mass_table`, `changes_md`: değişiklik raporu |
| 770–904 | promotion | `promote`, `run_sweeps`, `main`: yalnız kullanıcı onayıyla tabana taşıma, komut satırı |

## Testler

```
$env:MPLBACKEND="Agg"; python -m pytest -q -p no:cacheprovider tests/test_venus_*.py tests/test_planetary.py
```

Script hash çapası `tests/test_venus_variant_v07.py::test_existing_scripts_unchanged` içindedir. Bir betik bilerek
değişirse `catalog/reorg_manifest.json` içindeki `script_anchor_changes` kaydı güncellenir.

## Görsel kod

3B araç, ortam ve simülatör Sunumatik deposundadır. Yerini ve komutlarını `visual/README.md` anlatır.
