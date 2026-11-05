# C_lorenz2018_dragonfly — Dragonfly: A Rotorcraft Lander Concept for Scientific Exploration at Titan

## Citation
Lorenz, R. D.; Turtle, E. P.; Barnes, J. W.; Trainer, M. G.; Adams, D. S.; Hibbard, K. E.; Sheldon, C. Z.; Zacny, K.; Peplowski, P. N.; Lawrence, D. J.; Ravine, M. A.; McGee, T. G.; Sotzen, K. S.; MacKenzie, S. M.; Langelaan, J. W.; Schmitz, S.; Wolfarth, L. S.; Bedini, P. D. (2018). *Dragonfly: A Rotorcraft Lander Concept for Scientific Exploration at Titan.* Johns Hopkins APL Technical Digest 34(3): 374-387.
PDF: https://secwww.jhuapl.edu/techdigest/Content/techdigest/pdf/V34-N03/34-03-Lorenz.pdf
(Author list checked against p. 374 of the PDF [D-ag].)

## What was read
Full text, 14 pages (pypdf). Box 1 (Titan parameters), configuration section, power section, atmospheric flight performance section, Fig. 2, 4 and 6 captions.

Tag: [D-ag] read in this paper. [A] not verified in this paper. [derived] mine.

## Numbers [D-ag]
**Titan environment (Box, p. 376):** diameter 5150 km; g = **1.35 m/s²**; p = **1.47 bar**; T = **94 K**; ρ = **5.4 kg/m³** (4× Earth SL; the text elsewhere says 4.4×); 95 % N2, 5 % CH4; speed of sound **195 m/s** (194 m/s in the text); near-surface winds 1-2 m/s max (GCM).

**Configuration (p. 376-377):** "over-under" **quad octocopter** (coaxial pair at each of 4 corners). Small aerodynamic penalty versus a pure quad, but it tolerates the loss of at least one rotor or motor. Four rotor positions came out optimal from the trade of unblocked rotor disk area against number of rotors, under the hypersonic-aeroshell packaging constraint. Heatshield **3.7 m** diameter (Fig. 2). Launched "upside-down" in the aeroshell. Rotors "~1 m" (p. 379); the blade section is a **wind-turbine airfoil**, chosen for efficiency and roughness tolerance.

**EDL (Fig. 1 caption):** after delivery in an aeroshell and **parachute descent, the vehicle lands under rotor power**. No release altitude is given in this paper.

**Power (p. 378-379):** single MMRTG (~2 kW waste heat), ~**70 W electrical** at Titan. Titan sol = 384 h (16 Earth days). Battery that would capture a full night of MMRTG output: 75 × 192 = 14 kWh, ~140 kg at 100 Wh/kg. A smaller battery was expected in practice.

**Flight performance (p. 379-380):** maximum-range speed ~**10 m/s**, maximum-endurance ~8 m/s (Fig. 4). Flight power for a **420 kg** vehicle at 10 m/s "a little over **2 kW**". A 30 kg battery at 100 Wh/kg could theoretically give 2 h and ~60 km. Flight power scales ~mass^1.5. **Titan flight power for a given mass is ~40× lower than on Earth** (Fig. 4 caption). A tip Mach of 0.4 is "not a strong design factor". The design goal was a ~40 km single hop. Vertical descent is avoided because of the vortex ring state, so descents are flown at ~20° glide in forward flight. Boundary-layer profiling flights go to 500 m-4 km.

**Ops concept (Fig. 6):** "leapfrog" strategy: vertical take-off to 50 m, energy-optimal climb at 20°, cruise at 500 m, survey a prospective site, then land at a pre-surveyed site.

## Later Dragonfly values (not in this paper) [A]
- Rotor diameter 1.35 m (NASA Langley test paper and Wikipedia, via search snippets); "3-bladed rotor diameter 1.3 m" (2026 Lorenz slides, via snippet).
- Mass ~875 kg for the selected mission and a mid-air release from the backshell at ~1.2 km altitude. I have no source read for these; the task brief mentions them. **Do not cite them without reading a source.** The release altitude has now been read in C_pensado2025_dragonfly_edl [D-ag]: release trigger at a nominal 1000 m, window 1000-800 m, down velocity < 2.9 m/s, entry mass 2309-2600 kg incl. 4.5 m aeroshell. The lander mass itself is still unverified.

## Lessons for Venus (my inference)
- [derived] Hover power scales as P ∝ W^1.5/√(ρ·A), and W ∝ g. Titan (ρ 5.4, g 1.35) against Venus 55 km (ρ ≈ 1, g 8.87): Venus hover power per kg is roughly (8.87/1.35)^1.5 · √(5.4/1.0) ≈ 39 times higher than Titan's. Titan's 40× advantage over Earth largely disappears at Venus; Venus at ρ ≈ 1 is close to Earth.
- An octocopter with coaxial corners was chosen for redundancy, which is a useful precedent for a single-shot Venus vehicle that cannot be serviced.
