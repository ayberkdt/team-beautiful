# A_counselman1980_pv_dlbi_winds — Pioneer Venus 4-probe wind profiles (DLBI), raw PDS tables

## Citations

1. **Data (read in full):** Pioneer Venus Multiprobe DLBI Relative Crustal and Atmospheric Velocity Components
   Data Bundle, NASA PDS Atmospheres Node, `urn:nasa:pds:pvmp_dlbi`, reformatted from NSSDCA datasets
   PSPA-00344, -00126, -00308, -00035. User guide by Y.-I. Won and S. A. McLaughlin, NSSDCA, Nov 2025.
   `https://atmos.nmsu.edu/PDS/data/PDS4/pvmp_dlbi/data/dlbi_{large,day,night,north}_atm_vel.tab` (+ .xml),
   `.../document/bundle_user_guide.pdf` (read all 6 pages).
2. **Paper the data reproduce (NOT read):** Counselman, C. C. III, Gourevitch, S. A., King, R. W.,
   Loriot, G. B., Ginsberg, E. S. (1980), "Zonal and meridional circulation of the lower atmosphere of Venus
   determined by radio interferometry", *J. Geophys. Res.* 85(A13):8026–8030, doi:10.1029/JA085iA13p08026
   (pages/authors from memory, not verified; user guide confirms title and author "Counselman III et al., 1980").

## What I read / did

- Columns [D-ag, from XML label]: GRT (s since 0 UTC 9 Dec 1978), probe velocity down/west/north relative to
  crust, probe velocity west/north relative to ambient atmosphere (m/s). Time resolution 6.3 s (Large), 18.9 s
  (small probes).
- **Wind = (probe velocity rel. crust) − (probe velocity rel. atmosphere)** — my derivation from the column
  definitions. Altitude assigned by matching GRT to the LAS/SAS state tables of the same probe
  (`A_pv_probes_seiff1980_pds.md`), linear interpolation. Values below are means of all samples within
  ±0.5 km of the target altitude. Script: `D:\tmp_ideathon\venus\scripts\dlbi.py`.
- User guide [D-ag]: overall uncertainty **10 cm/s**; wind ~1 m/s or less near surface and **about 100 m/s
  near 65 km at all four probes**; high shear centred at 15, 45 and 60 km; direction very close to due west
  except within a few km of the surface. The numerical data match Counselman et al. Figs 1–3, which plot
  50-s averages.

## Zonal (westward) wind, m/s [D-ag data, my altitude mapping/averaging]

| z (km) | Large 4.4N | Day 31.3S | Night 28.7S | North 59.3N | range |
|---|---|---|---|---|---|
| 10 | 5.9 | 4.2 | 2.8 | 1.9 | 2–6 |
| 20 | 30.8 | 21.3 | 22.0 | 10.2 | 10–31 |
| 30 | 41.2 | 27.9 | 29.4 | 23.4 | 23–41 |
| 40 | 41.9 | 38.4 | 35.1 | 38.2 | 35–42 |
| 45 | 60.1 | 49.2 | 48.0 | 54.2 | 48–60 |
| 48 | 60.4 | 56.2 | 56.0 | 60.1 | 56–60 |
| 50 | 61.9 | 57.3 | 53.0 | 67.5 | 53–68 |
| 52 | 62.0 | 58.7 | 52.8 | 70.3 | 53–70 |
| 54 | 65.1 | 58.8 | 57.9 | 69.7 | 58–70 |
| 55 | 63.0 | 59.0 | n/a | 74.1 | 59–74 |
| 56 | 66.0 | 60.9 | 60.4 | n/a | 60–66 |
| 58 | 78.2 | 65.4 | n/a | 85.7 | 65–86 |
| 60 | 91.2 | n/a | 79.4 | n/a | 79–91 |
| 62 | 96.3 | n/a | n/a | n/a | — |
| 64 | 97.9 | n/a | n/a | n/a | — |

(n/a = no DLBI sample within ±0.5 km; small probes sampled every 18.9 s while falling fast.)

## Meridional (northward +) wind, m/s [D-ag, same processing]

| z (km) | Large | Day | Night | North |
|---|---|---|---|---|
| 45 | 0.1 | 4.9 | −0.5 | −0.7 |
| 48 | 5.6 | 1.0 | 2.7 | 0.3 |
| 50 | 1.6 | 0.7 | 4.0 | −3.1 |
| 52 | −1.1 | 1.6 | 4.7 | −7.1 |
| 54 | −1.4 | 1.7 | 3.6 | −7.1 |
| 55 | −0.9 | 1.2 | n/a | −5.8 |
| 56 | −2.3 | 1.0 | 0.1 | n/a |
| 58 | 1.2 | 1.6 | n/a | 3.7 |
| 60 | 5.6 | n/a | 4.2 | n/a |
| 62 | 7.5 | n/a | n/a | n/a |

Meridional magnitudes at 45–62 km: |v| ≲ 7.5 m/s, typically 1–5 m/s [D-ag].

## Engineering reading (my inference)

- 50–56 km (the near-neutral layer): zonal wind 53–74 m/s across 4 sites, i.e. ~**62 ± 8 m/s**, and
  **weak vertical shear** (Large probe: 61.9 → 66.0 m/s from 50 to 56 km, ≈0.7 m/s per km).
- Shear zones **below 48 km** (45→48 km) and **above 56 km** (Large: 66 → 91 m/s from 56 to 60 km,
  ≈6 m/s per km) — a rotorcraft changing altitude across 56–60 km sees ~25 m/s change in headwind.

## Caveats

- Single snapshot (9 Dec 1978), early-morning/night local times, no afternoon sounding.
- Altitude mapping relies on LAS/SAS GRT; both data sets use ground-received time since 0 UT 9 Dec 1978
  (stated in both labels), so the match should be exact, but I did not cross-check with Counselman's figures.
- "Relative to atmosphere" component is a model-derived correction (drag/gravity/inertia) — user guide says
  components "were derived by theoretical calculation"; large at the top of small-probe descents (~8 m/s).
