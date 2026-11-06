# Bracket hand-off for the film — ge

Written by `aerokit.bracket.handoff` (2026-11-04 22:51) from `01_Ansys/inputs/ge_bracket.json`. Same coordinate frame (mm, z up) in every file.

| File | What | Film key |
|---|---|---|
| `girdi.json` | film input (paths relative to this folder) | `node film.mjs <this>/girdi.json` |
| `result.json` | `ranking[]`: chosen material first; mass, CO₂e production/use, retained volume, σ at ultimate, utilisation | `sonuc` |
| `yukler.json` | supports (fixed hole bores as cylinders) and forces/moments, mm and N | `yukler` |
| `yogunluk.json` | density fields `runs[i].density` [x][y][z], `runs[i].volume`, `meta.voxel_mm`, `meta.origin_mm` | `yogunluk` |
| `parca.stl` | smooth STL of the chosen layout (initial) | `geometri` |
| `baslangic.stl` | initial design surface | (extra) |
| `gerilme.txt` | von Mises at ultimate load on the chosen layout's surface (Mechanical export layout) | `gerilme_csv` |
| `eco_audit.json`, `eco_audit.md` | Eco Audit by phase, baseline and every candidate | (extra) |
| `materials/` | MatML Engineering Data XML + one card per material (E, Fty, Ftu at 20 °C and T, sources) | (extra) |

`result.json` also carries `details` (the full study record: materials with `stress_basis` T10/voxel per layout,
eco, T10 checks, bolt check). Rows on the T10-verified layout use the T10 stress for every material.

Numbers on screen must come from these files. Chosen: **Inconel 718 (L-PBF, solution + double age)**, 2.073 kg vs baseline 1.996 kg
(-3.8 % lighter), working temperature 300 °C. The load set-up is `GE-type bracket rehearsal set-up: roles from aerokit.bracket.features, loads from Carter et al. 2014 Fig. 2 (read by sub-agent), LC4 axis as in prev_guess/01_Ansys/scripts/ge_bracket_preview.py [Y].`.
Peak in `gerilme.txt` outside the hole zones should equal `ranking[0].sigma_ult_Pa` / 1e6 =
1210.3 MPa (film checks within 5 %; exclusion zone 6.6 mm around the support/load bores).
