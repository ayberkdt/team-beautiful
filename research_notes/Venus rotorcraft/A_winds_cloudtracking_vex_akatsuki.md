# A_winds_cloudtracking_vex_akatsuki — Cloud-tracked winds 47–66 km (Venus Express VIRTIS, Akatsuki IR2)

## Citations (all read as full PDFs unless noted)

1. Sánchez-Lavega, A., Hueso, R., Piccioni, G., Drossart, P., Peralta, J., Pérez-Hoyos, S., Wilson, C. F.,
   Taylor, F. W., Baines, K. H., Luz, D., Erard, S., Lebonnois, S. (2008), "Variable winds on Venus mapped in
   three dimensions", *Geophys. Res. Lett.* 35:L13204, doi:10.1029/2008GL033817.
   PDF: `https://web.lmd.jussieu.fr/~sllmd/pub/REF/2008GeoRL..3513204S.pdf` (5 pp., read pp. 1–4).
2. Horinouchi, T. et al. (2017), "Equatorial jet in the lower to middle cloud layer of Venus revealed by
   Akatsuki", *Nature Geoscience* 10, doi:10.1038/ngeo3016. **Read the submitted manuscript** (arXiv:1709.02216v1),
   which the authors say differs from the published paper (layer naming, added discussion, one more author).
3. Peralta, J. et al. (2018), "Nightside winds at the lower clouds of Venus with Akatsuki/IR2: longitudinal,
   local time and decadal variations from comparison with previous measurements", *ApJS* (7 Dec 2018).
   **Read the original manuscript** arXiv:1810.05418v2 (abstract, Sec. on decadal variability, conclusions).
4. Not accessed: Hueso et al. 2015 (PSS), Khatuntsev et al., Kouyama, Horinouchi 2018/2020, Kerzhanovich &
   Limaye 1985 (VIRA wind model, *Adv. Space Res.* 5(11):59–83). The VIRA wind chapter is cited in ref. 2's
   reference list as "Advances in Space Research, 5(11), 59-83 (1985)".

## Numbers [D-ag]

### Sánchez-Lavega et al. 2008 (VIRTIS, southern hemisphere, Apr 2006 – Jul 2007)

| Level (tracer) | Altitude | Mean zonal wind | Lat range of mean | Meridional |
|---|---|---|---|---|
| 380 nm UV, day | ~66 km (62–70) | **−102 ± 10 m/s** (westward) | 0–55°S | poleward, peak ~10 m/s at 55°S |
| 980 nm, day | ~61 km (58–64) | **−62 ± 10 m/s** (−75 ± 10 at orbit insertion Apr 2006) | 0–55°S | < 5 m/s mean |
| 1.74 µm, night | ~47 km | **−60 ± 10 m/s** | 0–65°S | < 5 m/s mean |

- Abstract: 105 m/s at cloud tops, **60–70 m/s at the cloud base (~47 km)** at low latitudes.
- Vertical shear (0–55°S): **8 ± 2 m/s per km between 61 and 66 km; < 1 m/s per km between 47 and 61 km.**
  Poleward of 50–60°S, shear within 47–66 km ~2 m/s per km or lower.
- Poleward of ~55° (65° at 47 km) zonal wind decreases roughly linearly to zero at the pole
  (meridional shear 0.026 m/s per km at 66 km; 0.021 m/s per km at 47 km).
- Measurement scatter r.m.s. 9 m/s (all filters).
- Solar tide at 66 km, 50–75°S: ~2.5 ± 0.5 m/s per hour increase from 09 to 15 h LT, amplitude ~10 m/s;
  not detected at 61 km or 47 km.

### Horinouchi et al. 2017 (Akatsuki IR2 2.26 µm, night, Jul–Aug 2016; sensed layer 45–60 km)

- Past studies: 50–70 m/s at low-to-mid latitude in the lower cloud levels.
- **Equatorial jet: longitudinal-mean zonal wind maximum ~85 m/s slightly north of the equator**
  (rotation period ~5 days); low-latitude winds > 80 m/s.
- Tracking error estimates: b = 1.7 m/s (six-hourly tracking, Jul–Aug 2016), 2.5 m/s for other periods.

### Peralta et al. 2018 (Akatsuki IR2 2016 + ground-based 2012–2017)

- >149,000 automatic + 2,947 manual wind vectors; 2016 Mar 22 – Oct 31.
- Zonal means consistent in shape with VEX 2006–2008 but **systematically ~10 m/s faster**.
- **Decadal variation of nightside lower-cloud zonal winds (30°S–30°N, 1978–2017): up to 30 m/s**;
  suggested oscillation amplitude ~15 m/s, period ~30 years.
- In-situ points used for comparison: PV Night probe (1978) and VEGA landers (1985) averaged over 50–60 km.

## Engineering reading (my synthesis)

At 50–56 km, low latitudes: mean zonal wind ~60–70 m/s (VEX 2006–07) to ~80–85 m/s (Akatsuki 2016 jet
episode); in-situ 1978/1985 values 53–74 m/s (PV DLBI, VEGA). A defensible design band for **zonal wind at
54 km: 65 m/s nominal, 50–90 m/s envelope**. Meridional < 5–10 m/s. Weak vertical shear (<1 m/s per km)
from 47 to ~58 km, strong shear (~6–8 m/s per km) from ~58 to 66 km.

## Caveats

- Cloud-tracking altitude assignment is uncertain (several km); nightside near-IR tracers sample a
  weighted layer of 45–60 km, not a single altitude.
- Ref. 2 and 3 read as preprint versions.
