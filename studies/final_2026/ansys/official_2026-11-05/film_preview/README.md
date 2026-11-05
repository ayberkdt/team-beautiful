# PREVIEW — geometry and loads only, no analysis

Film input package for the **official** EUROAVIA Ideathon 2026 Ansys bracket (organiser CAD + card, 5 Nov 2026), in the
film pipeline's own input format (`D:\Video Simulations\Ideathon-2026-Ansys`: `hazirla.mjs` + manifest `ansys-film/1`).
Built 2026-11-05 by `build_preview.py`, checked by `validate_preview.py` (record: `validation_report.txt`).

**There are no FEA, topology, Eco Audit or material-property numbers in this package.** Every such field is `null`
and listed in `film.json["_missing"]`. Status is `"preview"` (not `"final"`), so the film prints **PROVISIONAL** on
every source line. This is not a hand-off: it lives outside `studies/final_2026/ansys/handoff/` on purpose.

## Files

| File | What |
|---|---|
| `girdi.json` | film input: `"ansys": "film.json"`, `"yukler": "yukler.json"`, `"geometri"`: `baslangic.stl` (mm, z up, `hizala: yok`) |
| `film.json` | manifest `ansys-film/1`, `status: "preview"`; baseline, temperature, CAD holes, material **names** |
| `yukler.json` | supports + load cases in the film format, written by the pipeline's own `aerokit.bracket.report._film_loads` |
| `baslangic.stl` | initial CAD (binary STL, mm, z up, same frame as `yukler.json`); header relabelled "PREVIEW…", triangles byte-identical to the source |
| `build_preview.py` | rebuilds everything above from the official files (writes only into this folder) |
| `validate_preview.py` | deterministic checks (below); exit 1 on any FAIL |
| `validation_report.txt` | output of the last validation run |

Not here, on purpose: `result.json`, `yogunluk.json`, `parca.stl`, `gerilme.txt`, `eco_audit.*`, `materials/`.

## Field map (film field ← source)

Paths relative to `studies/final_2026/ansys/official_2026-11-05/`. `[D-org]` organiser file, `[K]` computed here, `[Y]` our interpretation.

| Film field (`hazirla.mjs` → screen) | Value | Source |
|---|---|---|
| `geometri` (girdi.json) → part drawn in shots 01, 03, closing | `baslangic.stl` | `visuals/initial_exact.stl` (smooth exact model from the other agent; 129 088 triangles) — fallback `derived/initial_from_facets.stl` if absent. Chosen by `build_preview.py` `main()`; source SHA-256 in `film.json._kaynak` |
| `ansys.baseline.geometry` → `film/veri/taban.stl` (shot 01) | `baslangic.stl` | same file |
| `ansys.baseline.material` → shot 01 title | `Structural steel, S275N` | `unpacked/dsco/SpaceClaim/document.xml`, `MaterialEntitySurrogate` `<label>` [D-org] |
| `ansys.baseline.mass_kg` → shot 01 title "152 kg" | 152.2653 kg | `unpacked/dsco/SpaceClaim/document.xml` (one line), Discovery **Mass** monitor `<value>152.26533757522702` [D-org]; file holds 4 mass monitors (206.06, 206.09, 182.26, 152.27 kg, other geometries) — the one within 0.5 % of STL volume × density is taken. Check: STL volume 0.019397 m³ × 7850 kg/m³ (`Discovery/table__a314c4f3…dt1.xml`, `table__ab2a4cd6…dt1.xml`, `Density value="7850"`) = 152.269 kg (+0.002 %) [K] |
| `ansys.sicaklik_C` (`temperature_C`) → "at 300 °C" | 300 | `setup/setup_official_fixed_bores.json` line 9 [D-org card, "> 300 °C"] |
| `ansys.cad.delikler` (`cad_setup.holes`) → shot 01 rings + "4 fixed, 2 loaded" | H1, H2 load (Ø60, axis y); H3–H6 support (Ø60, axis z) | `setup/setup_official_fixed_bores.json` lines 10–118; centres/diameters cross-checked against `derived/features.json` (Δ ≤ 0.014 mm) |
| `cad_setup.roles_source` → "(roles edited by hand)" | `edited` | roles come from the organiser card via `setup/boundary_conditions.md` §2–3 [Y], not from the automatic scan |
| `yukler.destekler` → hatched fixed bores | 4 cylinders r 30 mm, z 30–100 at (245, 95), (245, 305), (755, 95), (755, 305) | `setup/…fixed_bores.json` `supports` (line 120) + hole geometry, via `_film_loads` (`src/aerokit/bracket/report.py` line 66) |
| `yukler.kuvvetler` → arrows + load panel | LC1a, LC1b, LC1c: (0, ±24 000, 97 000) N per pin = 99.9 kN at each pin centre; LC2: My 1000 N·m per pin (panel only, `buyukluk_N: 0`, `moment_Nm`) | `setup/…fixed_bores.json` `load_cases` lines 138–231; card numbers in `setup/boundary_conditions.md` §3 (line 38–) |
| `yukler.tasarim_alani` | STL bbox 170–831.01 × 30–371.12 × 30–321.37 mm | `baslangic.stl` (same as `boundary_conditions.md` §1) |
| `ansys.kart` (source line) | "PREVIEW — geometry and loads only, no analysis · official EUROAVIA 2026 bracket (organiser CAD + card)" | written by `build_preview.py` |
| `ansys.malzemeler[].ad` | Structural steel, S275N (`baseline: true`) · Aluminum 2618-T6 · Ti-8Al-1Mo-1V (single annealed) | task brief 2026-11-05 — **names only** |
| `materials_catalogue`, `materials[].catalogue_key` | `catalogue/materials_catalogue.json`; keys `S275N`, `Al2618`, `Ti811` | the catalogue appeared at 11:37 while this package was built; the build links it and writes the join key of each material (keys checked to exist in its `materials`), **no values copied**. Catalogue names differ from the screen names ("Structural steel, S275N, normalized (reference)", "Aluminum, 2618, T6 (organisers) -- MIL-HDBK-5J covers only 2618-T61", "Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed") → join by `catalogue_key`, not by name |
| `redesign.*`, `density`, `print`, `stress`, `eco_audit`, `convergence`, `crosscheck`, every `materials[]` number | `null` / absent | no analysis on the official part yet (`film.json._missing` says why for each) |

## Which film shots this package can build (film code read 2026-11-05: `film/src/ana.mjs` `gerekVar` line 30, `film/sahne.json`)

| Shot | Today | Why |
|---|---|---|
| **01 Baseline** (part reveal, holes, supports, LC arrows, load panel, mass, 300 °C) | **buildable** | needs only this package. Frames checked (below); one film-side label gate fails — see "Mismatches" 1–2 |
| 02 300 °C strength curves | skipped by the film | needs `materials[].curve` + density (catalogue) |
| 03 Optimisation | **runs, but must NOT be used** | has no `gerek` rule: with no density field the film voxelises the baseline STL (`ana.mjs` line 95) and shows "The exported part keeps 30 % of the envelope", "Removal order rebuilt from the exported geometry (illustrative)" and a RETAINED VOLUME counter — a fake optimisation of the steel part |
| 04 Printability | skipped (`print: null`) | printability belongs to the redesign |
| 05 Stress | skipped | needs `gerilme.txt` / a selected material with results |
| 06 Materials | skipped | needs ≥ 2 materials with `mass_kg` (catalogue density + analysis) |
| 07 Eco Audit | skipped | needs `eco_audit` numbers |
| 08 Cross-check | skipped | needs Ansys numbers |
| Closing card | runs, **summary line invalid** | `kapanis_ozet_v2` (`sahne.json` line 433) prints "{parca} · 70 % of the envelope removed" from the voxelised baseline — not a result |

Film length with this package: 80 s − 57 s of skipped shots = 23 s (01 0–8.5 s, 03 8.5–18 s, closing 18–23 s; from
`sahne.json` `bas`/`son`). Usable today: **shot 01 only** (and the closing card without its summary line).

## Command for the film session (TEST output, never into `teslim/` of the live film)

`hazirla.mjs` / `film.mjs` always write into their own folder (`film/veri/` — the live film's input —, `kayitlar/`,
`teslim/`), so run them from a copy:

```bash
export TEMP=D:/tmp_ideathon/film TMP=D:/tmp_ideathon/film
C=D:/tmp_ideathon/film/official_preview_TEST
P="D:/Masaustu/Ideathon 2026/studies/final_2026/ansys/official_2026-11-05/film_preview"
python "$P/validate_preview.py"                       # must say ALL PASS (re-run build_preview.py if the STL changed)
mkdir -p $C && cp -r "D:/Video Simulations/Ideathon-2026-Ansys/"{film,araclar,hazirla.mjs,film.mjs} $C/
cd $C && node film.mjs "$P/girdi.json" --yalniz-kareler --kareler 4,7.5      # shot 01 frames -> $C/kayitlar/kareler/
# full TEST cut (23 s) -> $C/teslim/:  node film.mjs "$P/girdi.json" --kalite 1080p
```

Do not run `araclar/handoff_uyarla.py` on this folder: it needs `result.json`; it sees `film.json` and exits with
"adaptöre gerek yok", which is correct.

## Validation run (record: `validation_report.txt`)

`python validate_preview.py --film-veri <copy>/film/veri/film-veri.json` after `node hazirla.mjs girdi.json` in a copy
of the film code (`D:/tmp_ideathon/film_pkg/film_copy/`, SHA-256 of the copied sources in `SOURCE_SHA256.txt` there):

- STL: binary, 129 088 triangles, payload identical to `visuals/initial_exact.stl`; **closed 2-manifold** (193 632 edges,
  0 open, 0 non-manifold), consistent orientation, 0 degenerate, genus 6 (4 bolt + 2 pin bores), signed volume
  +0.019397 m³ → 152.269 kg at 7850 kg/m³ vs organiser 152.265 kg (+0.002 %); bbox = `boundary_conditions.md` §1.
- Holes: all 6 set-up holes match `features.json` (≤ 0.014 mm, Ø60 vs measured 59.96); ray-parity: each hole axis point
  lies outside the solid and a point 5 mm into the wall inside — the arrows' anchor (pin centre) sits in a real bore.
- `yukler.json`: every field `hazirla.mjs` reads is present and numeric; 8 entries recomputed from the set-up (direction,
  99 924.97 N, 1000 N·m moments).
- `film.json`: schema, status `preview`, PREVIEW tag in `film.json`, `girdi.json`, `yukler.json`, STL header; 26 numbers in
  the manifest, all temperature / baseline mass / hole geometry; redesign, density, print, stress, eco, convergence,
  cross-check null; materials names + catalogue keys only (keys exist in the catalogue).
- `hazirla.mjs` (copy): no error; one warning ("preview" → PROVISIONAL). Shots 02, 04–08 skipped by the film's own rules.
- `film.mjs --yalniz-kareler` (copy, frames in `D:/tmp_ideathon/film_pkg/film_copy/kayitlar/kareler/`): arrows 6 × 0°
  off the data, anchors 0.6 mm; reading time 01/03 passed; closed mesh 0 open edges; **data trace 18 numbers on screen,
  0 without a source**; label gate 01/03 **failed** (see below).

## Mismatches between our format and the film (for the film session; nothing here edits film code)

1. **Arrow labels collide in shot 01** (film gate "etiketler … KALDI", 2 collisions per check time): LC1c is a mix of
   LC1a and LC1b, so at each pin two load cases carry the identical vector (H1: LC1a = LC1c, H2: LC1b = LC1c) and their
   arrows and labels coincide. Options on the film side: one arrow per distinct vector with joined labels, or leave the
   sensitivity case LC1c out of the drawing. The package keeps all four cases as in the set-up.
2. **Support labels:** the pipeline names are `H3 fixed (fixed_bore)` …; the film's adapter (`handoff_uyarla.py`
   `yukler_kopya`) normally shortens them to "Bolt hole (fixed)" and strips the LC prefix from load names, but it is not
   in this path (no `result.json`). Tested in a temp variant: short names collapse the four support labels into one and
   remove the "forbidden zone" hit, but the arrow collisions of item 1 remain. The long LC2 name also runs into the part
   in the load panel.
3. LC2 gets the film's "(force pair on the arms)" suffix (`sahne.json` `cift_not`, line 434) because both pins carry an
   entry — for LC2 it is a moment split over two bores, not a force pair.
4. Shot 03 and the closing summary have no data gate (see table): with geometry only they show an "illustrative"
   optimisation and "% of the envelope removed" of the steel baseline.
5. `hazirla.mjs` needs `geometri` or `yogunluk` (line 274); with no redesign the baseline STL is passed as `geometri`
   (same choice as the film's own 5 Nov layout test `D:/tmp_ideathon/film/sketch2_test/`). `redesign.geometry` stays null.
6. Load anchor: `nokta` = pin centre (pipeline convention, as in `handoff/sketch/`); `handoff_requests.md` (5 Nov 11:30)
   asks for points ON the arch surface for loads on arches. The pins are bores, so the centre is the physical load axis;
   the film drew tails at the point with 0.6 mm anchor error.
