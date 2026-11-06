# E_16 — Yoon, Lee & Pulliam 2016: computational analysis of multi-rotor flows (rotor spacing)

- **Citation:** Yoon, S., Lee, H. C., Pulliam, T. H. (2016), "Computational Analysis of Multi-Rotor Flows", AIAA SciTech
  2016, San Diego; NTRS 20160004754 (NASA Ames).
- **URL:** `https://ntrs.nasa.gov/api/citations/20160004754/downloads/20160004754.pdf`, accessed 2026-11-05;
  local `D:\tmp_ideathon\venus_research\pdf\yoon2016.pdf`. Read level: results text (pdftotext) **[D]**.

## Values [D]
- Notional quadrotor built from four XV-15 isolated-rotor grids (3 highly twisted blades each), hover, M_tip 0.69,
  Re_ctip 4.9 million; unsteady Navier–Stokes with DDES.
- Tip-to-tip separations studied: 0.3D, 0.5D, 1D, 2D. At 2D the mean vertical force is close to an isolated rotor;
  it falls as spacing shrinks; **at 0.3D the loss in rotor efficiency is about 2 percent** (Sect. on Fig. 8).
- At 0.3D–0.5D: ingested vortices and high-frequency pressure waves between rotors; at 1D these disappear and
  low-frequency waves (~50 Hz) remain; at 2D the interaction is small.
- With a quad tilt-rotor fuselage and wings: rotors give ~3 % more thrust than four isolated rotors, but wing download
  makes total vertical force ~16 % lower.
- Secondary [A] (citations seen in search snippets, not read): up to 4 % hover thrust penalty (VFS 2019 eVTOL paper);
  rear rotors of a small quadcopter at 10 m/s cruise give 28 % less thrust than isolated. **Correction 6 Nov:** this
  snippet is a misquote. Yoon et al. 2017 [D-ag]: 28 percentage points (aft 30 % vs 58 % more thrust than fore);
  aft-rotor loss −17.7 % at 10 m/s, −12.8 % at 5 m/s.

## VESPER relevance [K]
Rotor centres 2.70 m apart, D = 2.6 m → tip gap 0.10 m = **0.04D**, far closer than the 0.3D case. Expect > 2 % loss in
hover and strong unsteady loads; in forward flight the downstream rotors lose much more. The simulator should carry a
per-rotor interference factor (start: −3 % thrust at equal power in hover [Y]; azimuth-dependent wake ingestion in
forward flight [Y]).
