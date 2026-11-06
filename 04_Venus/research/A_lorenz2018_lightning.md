# A_lorenz2018_lightning — Status of Venus lightning (contested)

## Citations

1. **Read (full PDF text, 25 pp.; closely: abstract, Table 4 p. 18–19, conclusions pp. 20–21):**
   Lorenz, R. D. (2018), "Lightning detection on Venus: a critical review", *Progress in Earth and Planetary
   Science* 5:34, doi:10.1186/s40645-018-0181-x (open access).
2. **Read (pp. 47–49):** Titov et al. (2018) *Space Sci. Rev.* 214:126, Sect. 8 "Lightning" (see `A_titov2018_clouds.md`).
3. **Search snippets only [A]:**
   - Lorenz, R. D., Imai, M., Takahashi, Y., Sato, M., Yamazaki, A., Sato, T. M., Imamura, T., Satoh, T.,
     Nakamura, M. (2019), "Constraints on Venus lightning from Akatsuki's first 3 years in orbit",
     *Geophys. Res. Lett.* 46:7955–7961, doi:10.1029/2019GL083311 (author list from memory, not verified).
   - Takahashi, Y. et al., JpGU 2021 abstract PPS02-P02 (`pub-files.atlas.jp/fs/public/jpgu2021/ver_3/abstract/en/PPS02-P02.pdf`) — not opened.

## Findings

From Lorenz 2018 [D-ag]:
- Claimed detections and non-detections are "qualitatively contradictory" (abstract).
- Most compelling evidence: VLF radio emissions recorded beneath the clouds by Venera 11–14 landers;
  ELF emissions from Pioneer Venus OEFD and Venus Express magnetometer consistent but with alternative
  explanations (conclusions).
- Optical emissions "not consistent with terrestrial levels of activity" (abstract).
- Table 4 verdicts: "no electrical activity" — Unlikely; "sporadic discharges with characteristics different
  from Earth" — **Not excluded**; "frequent lightning similar to Earth" — Unlikely.
- Akatsuki LAC: the 8 initial observations (Takahashi et al. 2018) cover a few million km² for ~20 min;
  many detections would have been expected at terrestrial optical rates; total survey 10–20 million km²·h.
  LAC opportunity ~20 min per 10-day orbit.
- Chemical argument: NO 5.5 ± 1.5 ppb below 60 km (Krasnopolsky 2006) would need ~90 flashes/s at
  ~10⁹ J per flash if lightning were the sole source.

From Titov et al. 2018 [D-ag]: Venera 9/10 flash report (mean flash 0.25 s, 2×10⁷ J optical, extrapolated
45 km⁻² yr⁻¹, single event collection); Cassini flybys detected nothing at 0.125–16 MHz; Galileo 6 pulses
>1 MHz; VEX magnetometer ~100 Hz circularly polarized whistler-mode signals interpreted as lightning (Russell
et al. 2007); VIRTIS flash search inconclusive; early LAC: no detections. Possible charging location: the
~57 km level where H2SO4 droplets may freeze (VIRA equatorial conditions).

From Lorenz et al. 2019 GRL (abstract/snippet) [A]: 42 nightside passes, 16.8 h, 81.6×10⁶ km²·h, **no
lightning flashes**; Venus optical lightning rate > ~1000× lower than Earth (or zero).
JpGU 2021 abstract [A]: one candidate optical flash recorded 1 March 2020; not confirmed as lightning.

## Design reading (my inference)

Lightning at Venus is unproven; if present it is rare/weak optically. Treat it as a low-probability hazard:
no lightning-strike requirement driven by data, but basic static-charge bleed / ESD protection is prudent
(droplet triboelectric charging is proposed around 57 km).
