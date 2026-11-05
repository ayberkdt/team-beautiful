# B_izraelevitz2025_aerobot — JPL/Aerostar variable-altitude Venus aerobot flight tests

## Citation
Izraelevitz, J. S., Krishnamoorthy, S., Goel, A., Aiazzi, C., Pauken, M., Walsh, G., Leake, C., Lim, C., Jain, A., Dorsky, L., Baines, K. H., Cutts, J. A., Hall, J. L., Turner, C., Quintana, C., Carlson, K., Lachenmeier, T., & Byrne, P. K. (2025). Flight Demonstration and Model Validation of a Prototype Variable-Altitude Venus Aerobot. *AIAA Journal of Aircraft*. https://doi.org/10.2514/1.C038314 ; accepted version arXiv:2411.06643v2 (https://arxiv.org/abs/2411.06643), 42 pp., downloaded 2026-11-04.
Note: "Near Space Corporation" (Tillamook OR) in the brief = **Aerostar LLC**, Tillamook OR in this paper.

## What I read
Full text of arXiv v2 via pypdf: abstract, §I (background, Table 2), §II.A balloon design, §II.B instrumentation masses, §II flight ops, §IV full-scale prediction, §V conclusions/deployment discussion, reference list.

## Numbers [D-ag]
- Two outdoor flights, Black Rock desert, Nevada, **July 2022**; flown at Earth densities equal to Venus **54–55 km** (Venus 54 km: 1.03 kg/m³, 39.7 °C ↔ Earth 1.1 km ASL; Venus 55 km: 0.92 kg/m³, 29.2 °C ↔ 2.2 km ASL) (Table 2, p. 5).
- Prototype is "approximately **one-third diameter scale**" of the favoured mission design (p. 5).
- Architecture: balloon-in-balloon. Outer **zero-pressure (ZP)** envelope = metalized bilaminate **Teflon FEP + Kapton polyimide** (Teflon for H2SO4 resistance; Kapton = He barrier + strength); silver metallization α = 0.08, ε = 0.52; ZP shape 60° sphere-cone-sphere, upper diameter **5 m**, lower **2.5 m** (p. 8).
- Inner **superpressure (SP)** balloon = **2.5 m** sphere, **Vectran** fabric (200 denier, 2×2 basket weave, 76 tpi) + heat-sealed thermoplastic urethane bladder; proof-tested 14 kPa, identical unit taken to 61 kPa (p. 8–9).
- Altitude control by pumping helium ZP→SP (descend) and venting SP→ZP (ascend); 2 × fixed-rate diaphragm pumps, 7 mm solenoid vent (p. 9–10).
- Masses: balloon system **21.3 kg**; balloon control module (BCM) **19.5 kg**; gondola **7.0 kg**, hung ~3 m below BCM (p. 9–10).
- Ground inflation used 14 T-bottles of He (8.5 m³ each) for two flights (p. 12).
- Materials target Venus conditions 60 °C and **>94% sulfuric acid** aerosols (p. 37).
- Full-scale designs (Hall et al. 2019/2021 ref [5]): **100 kg gondola**, altitude range **52–62 km**, ~3× diameter of prototype (27× volume); example **12.5 m** diameter aerobot (case B2); goal 117 Earth days (1 Venus day); designs scale 15–230 kg payload; JPL aerobot gondolas 40–100 kg (p. 4, p. 36).
- Vega reference: "two small **7 kg** gondolas", ~**46 h** flight (p. 4, citing Sagdeev 1986).

## Deployment (key for "how does it get there")
- Inflation for Venus: vertically oriented **hanging inflation** under a parachute during atmospheric descent, enabled by an internal load line between SP apex and ZP apex (p. 9).
- Required steps listed (p. 38): packaging for cruise → extraction to hanging configuration beneath a parachute → inflation from **disposable helium tanks** → transition to free flight.
- Status: demonstrated end-to-end only by VeGa (1985); larger JPL constant-altitude balloons demonstrated "most of the process (but not yet the transition to free flight)" (Hall et al. 2011); "no end-to-end deployment demonstration has been attempted for a variable altitude balloon-in-balloon"; inflation timeline + indoor experiments in Gatto et al. 2024 (Acta Astronautica 214:757–773) (p. 38).
- **No inflation duration (minutes) is given in this paper** — see Gatto et al. 2024 if accessible.

## Caveats
- Earth test: 1 km altitude excursions; Venus temperatures ~15 °C warmer than test.

## Quote
"the aerobot should therefore be deployed mid-air during atmospheric descent" (p. 38).
