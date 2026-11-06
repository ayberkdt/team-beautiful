# B_young2004_rwd_husseyin2016 — NASA Ames Venus rotary-wing concepts (rotary-wing decelerator; stopped-rotor cyclocopter)

## Citations
1. Young, L. A., Briggs, G., Aiken, E., & Pisanich, G. (2005). Rotary-Wing Decelerators for Probe Descent Through the Atmosphere of Venus. In *2nd International Planetary Probe Workshop* (Ames, 23–27 Aug 2004), NASA CP-2004-213456, pp. 209–214. NTRS 20070014645. https://ntrs.nasa.gov/citations/20070014645
2. Husseyin, S. (& Warmbrodt, W. G., NTRS listing) (2016). *Design Considerations for a Stopped-Rotor Cyclocopter for Venus Exploration*. NASA Ames / ISU internship report. NTRS 20160012563. https://ntrs.nasa.gov/citations/20160012563
(Also downloaded: Young, "Vertical Lift – Not Just For Terrestrial Flight", NTRS 20090023136 — only grep'd: notional Venusian hybrid airship, Venus surface 735.3 K, 9.21×10⁶ Pa, 64.79 kg/m³ (table p. ~4); not analysed further.)

## What I read
(1) Full text, 7 pp. (2) Abstract, §II.D mission description, §III design discussion, Table 1 — full text skimmed via grep + targeted reading.

## Numbers [D-ag]

### Young et al. 2004 — rotary-wing (RW) decelerator
- Concept: one or more rotors in **autorotation / windmill state on the aft end** of a Venus lander probe for controlled descent, hazard avoidance, soft "flare" landing, possibly power generation (Summary, §2).
- Deployment illustration (Fig. 2): sequence = **release of probe from aeroshell → deployment and extension of rotor booms and rotors → deployment of landing gear**; 3-rotor system. Authors note folding support arms may be unnecessary: "rigid (always deployed) support arms are likely feasible" because the rotors are compact (§3).
- Sizing example: near-surface design descent speed **8.5 m/s**, **200 kg** probe (without aeroshell), **0.42 m** diameter per rotor in a **three-rotor** system, ideal autorotation; pressure vessel ~**0.7 m** diameter (§5).
- Descent phases: (1) release from aeroshell, initial rotor **spin-up** and high-speed deceleration; (2) transition through **turbulent-wake and vortex-ring states**; (3) low-speed terminal descent; (4) rotor flare and soft landing. Paper analyses only phases 3–4 (§6).
- Fig. 5: ideal-autorotation descent speed vs altitude 0–15 km for disk loadings 2000, 4500, 6000 N/m² (printed "N/m³") — 8–10 m/s near surface; plus probe-drag-only terminal velocity curve (values graphical only).
- Fig. 6: tip Mach up to ~0.8 for low solidity 0.05; tip Re up to ~3×10⁶; "within the range of engineering experience" (§6).
- Venera flat-plate (disk) decelerator = passive; RW decelerator "can at best only match a flat-plate ... decelerator" in pure drag; advantage is control (§3). 3-rotor packs better in aeroshell than 4-rotor (§5).

### Husseyin 2016 — stopped-rotor cyclocopter
- Mission profile (§II.D): enter at **200 km** → vehicle **ejected** (from entry system) → glide (rotors stopped, blades acting as wings) to measurement altitude → descend to **25 km** → radar → cyclorotors switched on → hover, vertical landing, surface work, vertical take-off.
- Foldable cyclorotor concepts: blades become wing surface for gliding/stowage (Fig. 14).
- CFD (RotCFD) flow properties: 60 km ρ = 1.225 kg/m³ (Earth sea-level analogue); 5 km ρ = **67 kg/m³** (Table 1).
- Background claims (secondary, not used): Vega balloons "around 53 km ... up to 60 hours" — conflicts with 46.5 h (Siddiqi/VAPS); treat as error.

## Relevance
- Gives the only quantitative rotor-sizing data point found for a Venus rotary-wing descent vehicle (0.42 m rotors, 200 kg, 8.5 m/s).
- Spells out the spin-up / vortex-ring transition as a deployment risk, which the Ideathon design must address.

## Caveats
- Conceptual/intern-level studies; no flight hardware; no deployment altitudes or timings.

## Quote
"rigid (always deployed) support arms are likely feasible instead" (Young et al. 2004, §3).
