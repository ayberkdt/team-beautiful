# E_07 — Venus-GRAM (VIRA-based) profiles from the AMAT repository, 5 Nov 2026

- **Source:** A. P. Girija, AMAT toolkit,
  `https://raw.githubusercontent.com/athulpg007/AMAT/master/atmdata/Venus/` files `venus-gram-avg.dat` (z, T, p, ρ, a)
  and `LAT10N.txt`, `LAT40N.txt`, `LAT60N.txt`, `LAT80N.txt` (header: Var_X, DENSLO, DENSAV, DENSHI, DENSTOT, Radius,
  Rref 6051.89, Grav, …; first profile block used).
- **Accessed:** 2026-11-05. **Tag [D-ag]**: tertiary (GRAM output based on VIRA, Seiff et al. 1985; VIRA itself is still
  not obtained). The GRAM options used to make the files are not documented.
- Average profile [D-ag]: 40 km 417.6 K, 3.501 bar, 4.404 kg/m³, a 320.1 m/s; 50 km 350.5 K, 1.066 bar, 1.594 kg/m³;
  55 km 302.3 K, 0.5314 bar, 0.9207 kg/m³, a 272.8 m/s; 60 km 262.8 K, 0.2357 bar, 0.4694 kg/m³; 65 km 244.3 K,
  0.0960 bar, 0.2055 kg/m³; 70 km 229.8 K, 0.0369 bar, 0.0839 kg/m³.
- Latitude, DENSLO / DENSAV / DENSHI (kg/m³): 55 km 10N 0.897/0.921/0.945, 80N 0.863/0.886/0.909; 65 km 10N
  0.198/0.206/0.214, 60N 0.180/0.187/0.195, 80N 0.153/0.159/0.165; 70 km 10N 0.0802/0.0839/0.0878, 80N
  0.0586/0.0613/0.0641.
- Read-out [K]: below ~55 km latitude changes ρ by < 5 %; at 65–70 km ρ falls 25–30 % from 10°N to 80°N. The GRAM
  low/high bands are about ±2.5 %.
- GRAM is 2.5–5 K warmer and 3–4 % denser than the PV probe mean at 50–60 km (csv columns `T_K_gram`, `rho_kgm3_gram`),
  as the earlier note A_seiff1985_vira found.
