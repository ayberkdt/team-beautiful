# D_panasonic_ncr18650b — COTS high-energy 18650 cell limits (manufacturer datasheet)

## Citation
Panasonic (SANYO Energy (U.S.A.) Corp.). *NCR18650B Lithium Ion datasheet*, version 13.11 R1,
© 2012. Copy hosted on TI E2E forum:
https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/Panasonic-NCR18650B-datasheet.pdf
**Manufacturer data** (third-party-hosted copy).

## What I read
Full one-page datasheet (text extraction).

## Numbers [D-ag, manufacturer]
- Rated capacity min 3200 mAh (20 °C); capacity min 3250 / typ 3350 mAh (25 °C); nominal 3.6 V.
- Charging CC-CV std 1625 mA, 4.20 V, 4.0 h; **below 10 °C charge at 0.25C**.
- **Weight max 48.5 g.**
- **Temperature: charge 0…+45 °C; discharge −20…+60 °C; storage −20…+50 °C.**
- **Energy density 243 Wh/kg, 676 Wh/l** (bare cell).

## Caveats
High-energy, low-power cell (std discharge ~1C; datasheet curves only); not a rotor-power
cell — compare Ingenuity's VTC4 (163 Wh/kg, >25 A). Capacity derates at −20 °C and cycle
life falls at 45–60 °C (curves on datasheet, values not transcribed). Not space-qualified.
