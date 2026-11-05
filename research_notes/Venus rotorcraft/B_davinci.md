# B_davinci — DAVINCI probe (Garvin 2022; Dutta et al. 2023; Dutta 2026 NESC deck)

## Citations
1. Garvin, J. B., Getty, S. A., Arney, G. N., et al. (2022). Revealing the Mysteries of Venus: The DAVINCI Mission. *Planetary Science Journal* 3:117 (17 pp). https://doi.org/10.3847/PSJ/ac63c2 (open access; PDF downloaded from iopscience 2026-11-04).
2. Dutta, S., Guecha-Ahumada, N. G., Garrison, M. B., Hughes, K. M., & Johnson, M. Z. (2023). *DAVINCI Venus Entry, Descent, and Landing Modeling and Simulation*. AIAA SciTech 2023. NTRS 20220017581, PDF "DAVINCI_SciTech2023_v4.pdf".
3. Dutta, S. (2026, 29 June). *Modeling the Big Plunge: DAVINCI Entry, Descent, and Landing*. NASA Langley/Ames Summer Internship Presentation, NESC Academy file 1537. https://nescacademy.nasa.gov/downloadFile/1537
(Also glanced: Andreini, Dutta et al., *Entry and Descent Modeling for DAVINCI*, NTRS 20240006669 — slide deck, only the title slides read; nothing used.)

## What I read
- (1) Full text: §1–2 incl. §2.1 mission design, §2.2 "Descent Sphere Design", Fig. 5/11/12 captions. Figure 12 timeline image itself not readable as text.
- (2) Full text of pages 1–11. NOTE: the PDF uses a shifted font: digits are encoded as letters (P=0, Q=1, R=2, S=3, T=4, U=5, V=6, W=7, X=8). I decoded with that mapping and cross-checked with known values (launch "RPR9"=2029, entry "RPSQ"=2031, PV year "Q9WX"=1978, AEI "QTU km"=145 km — matches Garvin's 145 km). Decoded numbers are tagged [D-ag] but with "(decoded)".
- (3) Full slide text (25 slides), incl. geometry table (slide 7) and requirements table (slide 19).

## Numbers

### Garvin et al. 2022 [D-ag]
- Probe Flight System (PFS = entry system + descent sphere) released **2 days** before arrival (§2.1, p. 7).
- "After atmospheric entry and parachute deployment (**~70 km** altitude), the heat shield is released" (p. 7).
- Science descent "59 minutes transect from ~70 km to the surface" (p. 6). Touchdown **57.04–66.7 min** (99% confidence), reference **59.7 min** (Fig. 12 caption).
- Touchdown speed **18.7 m/s**; DS not required to survive; if it does, ~18 min extra surface data (p. 7).
- Entry system: **45° half-angle sphere-cone**, **carbon–carbon** TPS, heat shield, **drogue and main parachutes**, back-shell; built by Lockheed Martin with Genesis/Stardust heritage + PVLP, Phoenix, MSL design aspects (p. 7).
- Descent sphere (DS): hermetically sealed **titanium** pressure vessel "0.98 m × 0.85 m; **200 kg**" (p. 8); two hemispheres + mid-ring; titanium aero-fairing, drag plates, spin vanes; main-parachute bridle attaches to mid-ring. Full-scale ETU diameter 0.98 m (Fig. 11).
- Entry interface **~145 km**; sequence: blackout → pilot chute → back-shell separates → main chute → heat shield separates → DS on main chute; main chute separates **~32 min after AEI** (p. 8).
- Mission data yield ≥ 60 Gbit (compressed), mostly flybys (abstract). Landing/imaging ellipse ~310 km long axis (Fig. 8 caption).
- Data relay: DS → CRIS (S-band... the paper says CRIS tracks PFS with HGA two-way S-band link; DS data relayed continuously to CRIS) — **no numeric DS data rate given in Garvin 2022**.

### Dutta et al. 2023 (SciTech) [D-ag, decoded]
- ES = **2.24 m diameter** 45° sphere-cone, relatively flat backshell (p. 2) — (decoded "RNRT"; the 2026 deck says 2.54 m "approximate", see below → design changed or decoding ambiguity; treat as 2.2–2.5 m).
- DS **0.87 m sphere diameter**, 0.98 m drag-plate-to-drag-plate; PVLP sphere 0.78 m, also 0.98 m across drag plates (p. 2).
- **Pilot DGB parachute 1.8 m**, **main DGB parachute 5.8 m** diameter; "not using conical ribbon parachutes" unlike PV (p. 3).
- **Entry velocity 10.4 km/s, EFPA −6.3°**, **peak deceleration 32 g**, peak convective heat flux **500 W/cm²** (p. 3). PV comparison EFPA "−33.8°" (p. 3; differs from −32.4° in NASA Ames decks).
- Most deceleration between 80 and 100 km altitude; AEI 145 km (p. 3).
- Pilot chute deploys **subsonic at Mach 0.8** via g-trigger + timer (PV-like); main chute "shortly after reaching **70 km**"; **30 min on main** then released and **another 30 min** free fall (p. 4).
- Entry portion: chute deploy within first 5% of EDL timeline; large deceleration in **~3 min** (p. 6).
- Peak g histogram axis 26–38 g (Fig. 7). Vertical speed at VMS sample start ~37–47 m/s, fastest ~46 m/s (Fig. 9, p. 7). Time from EI to 5 km AGL 50–58 min (Fig. 10).
- Landing ellipse 99%: **313 × 112 km** (p. 7).
- Parachute will traverse H2SO4 clouds at 40–60 km; acid effect on strength to be tested (p. 6).
- PFS spin-stabilized at **5 rpm** (p. 1).
- Data-rate plot (Fig. 14) axis up to 400 kbps, adaptive data rate; numeric values not readable from text.

### Dutta 2026 NESC deck [D-ag]
- Aeroshell diameter **2.54 m** ("approximate, some internal iterations occurring"), 45°, Xcg/D 0.24, Rn/D 0.25 (slide 7).
- Requirement MRD-355: **uplink rate at touchdown ≥ 36 kbps** (1%-tile sim value 123.3 kbps); total transmitted data during descent **> 154 Mbit** required (1%-tile 639.9 Mbit; 99%-tile 700.4 Mbit vs cap 2200 Mbit) (slide 19).
- Schedule note: "current baseline of Dec. 2031" launch, DS PDR early 2027, ES PDR early 2028 (slide 21) — launch has slipped from the June 2029 in the 2022/2023 papers.

## Not found
- DAVINCI entry mass / ballistic coefficient: not stated in the three sources read. (DS 200 kg known; ES mass unknown.)

## Caveats
- ES diameter conflict 2.24 m (2023, decoded) vs 2.54 m (2026, approx).
- Design-stage numbers; will change.

## Quote
"a subsonic dgb pilot parachute deploys at mach 0.8" (Dutta et al. 2023, p. 4, decoded).
