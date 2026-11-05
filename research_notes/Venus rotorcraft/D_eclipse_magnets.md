# D_eclipse_magnets — NdFeB grade and SmCo maximum working temperatures (manufacturer)

## Citations
1. Eclipse Magnetics. *NdFeB Magnets / Neodymium Iron Boron Magnets Datasheet* (standard NdFeB
   range, rev1, 4 pp.).
   https://www.eclipsemagnetics.com/site/assets/files/19485/ndfeb_neodymium_iron_boron-standard_ndfeb_range_datasheet_rev1.pdf
2. Eclipse Magnetics. *SmCo (Samarium Cobalt) datasheet* (1 p.).
   https://www.eclipsemagnetics.com/site/assets/files/19544/eclipsemagnetics_smco_datasheet.pdf
**Manufacturer data.**

## What I read
Text extraction of both PDFs; NdFeB suffix table on p.2; SmCo text blocks (layout scrambled
by extraction, values read where unambiguous).

## NdFeB — suffix table (1) p.2 [D-ag, manufacturer]
| Suffix | α(Br) %/°C (20–100 °C) | β(Hci) %/°C | Max working temp (high working point) |
|---|---|---|---|
| (none, Nxx) | −0.120 | −0.70 | **80 °C** |
| M | −0.115 | −0.65 | 100 °C |
| H | −0.110 | −0.60 | 120 °C |
| **SH** | −0.105 | −0.55 | **150 °C** |
| UH | −0.100 | −0.55 | 180 °C |
| EH | −0.095 | −0.50 | 200 °C |
| VH / AH | −0.090 | −0.49 | **230 °C** |
- **N52, N50 and N50M are rated to max 60 °C** [D-ag].
- Ratings are "guideline values"; the magnetic circuit (Pc) changes the real limit [D-ag].
- NdFeB Curie temperature 310 °C; must be coated (default Ni-Cu-Ni) [D-ag].
- Example: N42 Br 1.28 T, Hci 955 kA/m, BHmax 318 kJ/m³, +80 °C max [D-ag].

## SmCo (2) [D-ag, manufacturer]
- SmCo usable "from near −273 °C up to +350 °C".
- **Sm2Co17 standard ≈ +300 °C; "H" versions of Sm2Co17 up to +350 °C** (e.g. SmCo26H:
  Br 1.02 T, Hci > 1990 kA/m, BHmax 191 kJ/m³, +350 °C max working temp).
- Curie temperature Sm1Co5 700–750 °C, Sm2Co17 800–850 °C.
- Rev. temp. coef. of Br: −0.035 %/°C (Sm2Co17) (block partially scrambled — verify).
- Corrosion: Sm1Co5 excellent (no iron), Sm2Co17 good to very good.
- Plastic-bonded SmCo limited to +120 °C by binder.
- Sm1Co5 max working temperature: value not unambiguously readable in extraction; other
  suppliers quote ~250 °C [A, search snippets].

## Relevance (mine)
At 50–60 km (≈ 0–75 °C ambient per JPL) a standard N-grade motor magnet runs close to its
80 °C limit once copper losses heat the rotor; SH (150 °C) gives margin with ~13 % lower
remanence temperature sensitivity; SmCo only needed for excursions below the clouds.

## Caveats
Supplier guideline values; demagnetisation depends on load line and stator field.
