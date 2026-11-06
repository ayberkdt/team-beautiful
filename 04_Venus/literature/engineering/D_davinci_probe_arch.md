# D_davinci_probe_arch — DAVINCI Descent Sphere: battery, relay link, thermal design

## Citation
Ripley, R. & Goodloe, C. (NASA GSFC) (2024). *Venus Probe Architecture.* IEEE (Aerospace)
conference paper, U.S. Government work. NTRS 20240015826.
https://ntrs.nasa.gov/api/citations/20240015826/downloads/IEEE_conference_Venus_Probe_Architecture_v4.pdf

## What I read
Full 8-page paper (text extraction).

## Numbers / facts [D-ag]
- ~1 hour descent through the Venus atmosphere (abstract).
- Probe Flight System and Descent Sphere (DS) talk to the carrier CRIS via an **Adjustable
  Data Rate (ADR) S-band link**; DS does **not** transmit direct-to-Earth; CRIS stores and
  forwards.
- Radio: APL **Frontier Lite** radio card with adaptive data rate.
- Data return estimates: **worst 154 Mbit, most likely 636.2 Mbit, best 1.2 Gbit** (Fig. 6).
  Link rate first rises, then falls, during descent (range geometry).
- Fixed-rate fallback mode printed as "up to 500 Mbps" — **almost certainly a typo** (1.2 Gbit
  in ~1 h ≈ 0.33 Mbit/s average, my calc); do not use.
- **Battery: rechargeable Li-ion, ~2400 Wh**, sized for 2-day coast + descent; charged from
  CRIS bus via Descent Sphere Charge Card until release. A primary battery was initially
  baselined; secondary chosen for ground-testability and risk despite lower energy density.
- 2-day hibernation coast between release and entry interface.
- Thermal: titanium shell ("resistant to sulfuric acid" per authors), **evacuated interior**
  (< 1e-3 Torr), high-temperature MLI + conventional MLI forming a **1-inch barrier**,
  **beryllium decks** (heat capacity ×4 aluminium) as heat sinks, CRIS-powered pre-heat,
  PCM around the camera; internal environment kept above −30 °C and below 50 °C.
- Thermal battery used for an ES (entry system) function, fired via NSI.

## Caveats
Paper says Ti is acid resistant; manufacturer data (D_timet_titanium_h2so4.md) show CP Ti
attacked by liquid concentrated H2SO4 at room temperature (1.57 mm/y) but nil in 96 % acid
vapour — for a ~1 h transit the claim is fine, for a months-long rotorcraft it is not.
No link budget (power, antenna gain, range) is given in the paper.
