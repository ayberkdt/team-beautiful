# B_vega_balloon — Vega 1/2 balloon deployment sequence (PDS catalog + 1986 Science abstracts + Cutts et al. 1999)

## Citations
1. NASA Planetary Data System (PDS3), Vega archive, instrument-host catalog `vega1_host.cat` (label revision R. Lorenz, 17 Mar 2017). https://pds.nasa.gov/data/pds3/releases/backup/2020/202002.vega/vega1_host.cat (also `vega2_host.cat`, identical overview text). The catalog cites SAGDEEV1986H, KREMNEV1986, LINKIN1987. Authoritative NASA archive text written by R. Lorenz summarising the primary papers → treat as authoritative secondary.
2. Science vol. 231 no. 4744 (21 Mar 1986), VEGA balloon special section — **abstracts only** read via PubMed E-utilities:
   - Sagdeev, Linkin, Blamont, Preston, "The VEGA Venus Balloon Experiment", 1407–1408, doi:10.1126/science.231.4744.1407
   - Kremnev, Linkin, Lipatov, Pichkadze, Shurupov, Terterashvili, Bakitko, Blamont, Malique, Ragent, Preston, Elson, Crisp, "VEGA Balloon System and Instrumentation", 1408–1411, doi:10.1126/science.231.4744.1408
   - Sagdeev et al., "Overview of VEGA Venus Balloon in Situ Meteorological Measurements", 1411–1414, doi:10.1126/science.231.4744.1411
   - Preston et al., "Determination of Venus Winds by Ground-Based Radio Tracking of the VEGA Balloons", 1414–1416, doi:10.1126/science.231.4744.1414
   - Linkin et al., "VEGA Balloon Dynamics and Vertical Winds...", 1417–1419
3. Cutts, J. A., Kerzhanovich, V., Balaram, J., Campbell, B., Gershman, R., Greeley, R., Hall, J. L., Cameron, J., Klaasen, K., & Hansen, D. M. (1999). *Venus Aerobot Multisonde Mission*. AIAA Balloon Technology Conference 1999. NTRS 20000052454 (full text read; poor OCR, one passage printed upside down).

Full texts of the 1986 Science papers were NOT accessed (paywall).

## Numbers

### PDS catalog (Vega 1 sequence) [A — authoritative NASA archive summary of the primary papers]
| Event | Time / altitude |
|---|---|
| Entry interface | **125 km**, 02:06:10 UT (Earth-received), 11 June 1985, "roughly **11 km/sec**" |
| Parachute on landing-craft cap opens | ~02:06:25 UT, **64 km** |
| Cap + parachute released | 15 s later, **63 km** |
| Balloon package pulled out of compartment by parachute | 40 s later, **61 km** (8.1°N, 176.9°E) |
| Second parachute opens, extracts furled balloon | **55 km**, **200 s after entry** |
| Balloon inflated; parachute + inflation system jettisoned | **100 s later, 54 km** |
| Ballast jettisoned | when balloon reached **~50 km** |
| Floats back up to stable height | **53–54 km**, **15–25 min after entry** |
- Mean float height **53.6 km**, 535 mbar, 300–310 K. Mean westward drift **~69 m/s**; night→day terminator crossed after 8,500 km; last transmission 00:38 UT 13 June after **11,600 km** total.
- Vega-1 lander: "operated for **20 minutes**" on the surface (CONFLICTS with Siddiqi's 56 min — see caveats).
- Vega 2 entered ~02:00 UT 15 June 1985, 3–7°S; similar profile; stronger vertical winds over Aphrodite Terra.
- Note the "200 s after entry" is ambiguous with the clock-time list (entry 02:06:10, cap chute 02:06:25 = 15 s after entry) — the catalog is internally a little loose.

### 1986 Science abstracts [A — abstracts only]
- Each balloon travelled ~30% of the way around Venus at float altitude "near 54 kilometers" (Sagdeev et al.).
- Tracked by 20 radio observatories (VLBI); each balloon blown westward ~**11,500 km** (8,000 km on night side), mean zonal speed ~**70 m/s** (Preston et al.).
- Downdrafts up to **3.5 m/s** pushed balloons up to **2.5 km** below float altitude (Sagdeev et al. overview); vertical wind peak 3 m/s (Linkin et al.); typical 1–2 m/s (Blamont et al.).

### Cutts et al. 1999 [D-ag]
- Table 1 (VEVA vs VEGA): VEGA **mass of balloon system 121 kg**, **floating mass 21 kg**, payload/floating mass **0.33**, payload/balloon-system mass **0.06** (VEVA design: 94 kg, 63 kg, 0.65, 0.44).
- VEGA balloon: "heavy Teflon cloth impregnated balloon"; VEGA balloons "heavy and over-designed".
- Each Vega balloon "tracked for two days".
- VEVA concept (not flown): after separation from aeroshell, a **7-m diameter parachute** slows payload; balloon inflates during descent; float 60 km; gondola battery 7 days; bottom-inflation system (decoded from upside-down OCR, medium confidence).

## Derived
- Vega balloon ballistic margin: 121 kg delivered to get 21 kg floating ⇒ ~83% of the balloon-system mass is parachutes, inflation gear (He tanks), ballast and container. A deployable rotorcraft has a comparable "deployment overhead" question.

## Caveats
- Siddiqi (B_siddiqi2018) says balloon released "at 61 km", balloon mass "around 20.8 kg" — consistent with PDS 61 km (package extraction) and Cutts 21 kg floating mass.
- Lander surface time: PDS "20 minutes" (Vega 1) vs Siddiqi 56 min (Vega 1) / 57 min (Vega 2). Unresolved; both cited.
- Balloon diameter: VAPS 2018 says 3.5 m; not in the PDS text; Kremnev 1986 full text needed.

## Quote
"The balloon was inflated 100 seconds later at 54 km" (PDS vega1_host.cat).
