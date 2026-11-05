# D_venus_microwave_absorption — Radio absorption at cloud level (H2SO4 vapour, X/S band)

## Citations
1. Banerjee, S., Choudhary, R. K., Tripathi, K. R., Imamura, T., & Ando, H. (2026, draft
   14 Jan 2026). *On the estimation of Sulfuric Acid Vapor concentrations below the Venus cloud
   deck using the Akatsuki Radio Science Experiment.* arXiv 2601.08507 (AASTeX draft, not yet
   peer-reviewed as far as I saw). https://arxiv.org/pdf/2601.08507
2. Kolodner, M. A. & Steffes, P. G. (1998). *The microwave absorption and abundance of sulfuric
   acid vapor in the Venus atmosphere based on new laboratory measurements.* Icarus 132(1),
   151–169. (abstract via search only)
3. Steffes group conference abstract (c.1992), NTRS 19930005127 — H2SO4 absorptivity at 94.1 GHz
   (lab, 1–2 atm); only skimmed.

## What I read
(1) full text extraction + rendered Fig. 6 (p.11). (2) search-snippet abstract only.

## Numbers
- **Akatsuki X-band (8.4 GHz) absorptivity profile, 22 Jul 2020 ingress, lat −43° (Fig. 6)**
  [D-ag, read off plot]: total α ≈ 0.000–0.003 dB/km above ~53 km; ≈ **0.005 dB/km at 50 km**;
  ≈ 0.02 dB/km at 46.5 km; ≈ 0.07 dB/km at 42.5 km.
- H2SO4 vapour follows saturation curve; vanishingly small above ~50 km (cloud base); peak
  > 15 ppm at ~42.5 km in this profile [D-ag].
- X-band occultation absorption loss ~15–20 dB below 50 km (limb path, citing Cimino 1982,
  Oschlisniok 2020) [D-ag secondary-within-source]; saturation ~ −35 dB.
- SO2 X-band absorptivity relation (Janssen & Poynter 1981 updated): eq. 7 in (1) [D-ag; form
  partly garbled in extraction — re-read before use].
- Minor absorbers (H2O, OCS…) < 1 % of total α (citing Akins et al. 2023) [D-ag].
- Kolodner & Steffes 1998: power-law opacity expressions for gaseous H2SO4 in CO2 at S and X
  band; sub-cloud H2SO4 10–14 ppm equator, 3–7 ppm at 67°, 6–10 ppm at 88° [A — abstract].
- Gaseous H2SO4 is the dominant microwave absorber, mainly 35–50 km [A — abstract/snippets].

## Implication for a 50–60 km rotorcraft (my calc)
A near-vertical path from 50–60 km up to an orbiter crosses essentially no absorbing layer:
≤ ~0.005 dB/km × few km ≈ < 0.05 dB at X-band; UHF/S-band are expected to be lower still
(absorption rises with frequency — general physics, not verified numerically here). Limb
(low-elevation) paths and any descent below ~48 km change this. Occultation dB figures are
for grazing paths of hundreds of km, not for up-looking links.

## Caveats
Single profile at one latitude; no UHF (400 MHz) or S-band numeric dB/km found this session.
Cloud droplet (liquid) attenuation at UHF/S not quantified here.
