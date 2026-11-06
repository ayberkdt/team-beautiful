# Bracket hand-off for the film — dryrun_cold

Written by `aerokit.bracket.handoff` (2026-11-04 23:20) from `01_Ansys/inputs/dryrun_bracket.step`. Same coordinate frame (mm, z up) in every file.

| File | What | Film key |
|---|---|---|
| `girdi.json` | film input (paths relative to this folder) | `node film.mjs <this>/girdi.json` |
| `result.json` | `ranking[]`: chosen material first; mass, CO₂e production/use, retained volume, σ at ultimate, utilisation | `sonuc` |
| `yukler.json` | supports (fixed hole bores as cylinders) and forces/moments, mm and N | `yukler` |
| `yogunluk.json` | density fields `runs[i].density` [x][y][z], `runs[i].volume`, `meta.voxel_mm`, `meta.origin_mm` | `yogunluk` |
| `parca.stl` | smooth STL of the chosen layout (topo 25 %) | `geometri` |
| `baslangic.stl` | initial design surface | (extra) |
| `gerilme.txt` | von Mises at ultimate load on the chosen layout's surface (Mechanical export layout) | `gerilme_csv` |
| `eco_audit.json`, `eco_audit.md` | Eco Audit by phase, baseline and every candidate | (extra) |
| `materials/` | MatML Engineering Data XML + one card per material (E, Fty, Ftu at 20 °C and T, sources) | (extra) |

`result.json` also carries `details` (the full study record: materials with `stress_basis` T10/voxel per layout,
eco, T10 checks, bolt check). Rows on the T10-verified layout use the T10 stress for every material.

Numbers on screen must come from these files. Chosen: **Ti-6Al-4V (L-PBF, stress relieved / HIP)**, 0.080 kg vs baseline 0.577 kg
(86.1 % lighter), working temperature 300 °C. The load set-up is `Editable bracket set-up (lengths mm, forces N, moments N m). Roles and loads are a PROPOSAL from aerokit.bracket.features [Y]: check every hole role, load direction and magnitude against the organiser`.
Peak in `gerilme.txt` outside the hole zones should equal `ranking[0].sigma_ult_Pa` / 1e6 =
582.8 MPa (film checks within 5 %; exclusion zone 3.9 mm around the support/load bores).
