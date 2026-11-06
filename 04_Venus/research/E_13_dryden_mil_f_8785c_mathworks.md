# E_13 — Dryden turbulence model (MIL-F-8785C / MIL-HDBK-1797) as documented by MathWorks

- **Source:** MathWorks, Aerospace Blockset, "Dryden Wind Turbulence Model (Continuous)",
  `https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html`, accessed 2026-11-05 (WebFetch).
- **Tag [D-ag]:** secondary documentation of the military specifications (MIL-F-8785C, 1980; MIL-HDBK-1797, 1997;
  MIL-HDBK-1797B, 2012). The specifications themselves were not read. The WebFetch text lost some radicals and fraction
  bars; the forms below match the standard Dryden filters but check them on the page before coding.

## Shaping filters (MIL-F-8785C form) [D-ag]
- H_u(s) = σ_u · sqrt(2 L_u / (π V)) · 1 / (1 + (L_u/V) s)
- H_v(s) = σ_v · sqrt(L_v / (π V)) · (1 + √3 (L_v/V) s) / (1 + (L_v/V) s)²
- H_w(s) = σ_w · sqrt(L_w / (π V)) · (1 + √3 (L_w/V) s) / (1 + (L_w/V) s)²
- Angular rates: H_p uses σ_w, L_w and the span b; H_q = ±(s/V)/(1 + (4b/(πV)) s) · H_w; H_r = ∓(s/V)/(1 + (3b/(πV)) s) · H_v.
- MIL-HDBK-1797 form uses 2L_v, 2L_w (same physics, different convention).

## Scales [D-ag]
- Low altitude (< 1000 ft): L_w = h; L_u = L_v = h/(0.177 + 0.000823 h)^1.2 (h in ft); σ_w = 0.1 W20.
- Medium/high altitude (> 2000 ft): **L_u = L_v = L_w = 1750 ft (533 m)**; σ from a table of altitude and exceedance
  probability.
- Frozen-turbulence assumption: valid when mean wind and rms turbulence are small relative to the vehicle speed. The
  filters contain 1/V, so V must be > 0 (my inference).

## Venus use (see `data/venus_turbulence_model.json`)
Use the Dryden form only for the small-scale part (σ_u ≈ 1 m/s, L ≈ 533 m [Y]) and a separate slow Gauss–Markov
process for the convective vertical wind (σ_w 0.7 m/s, T ≈ 1500 s from VEGA, E_04). A hovering rotorcraft needs a
speed floor in the filters (V = max(V_air, 2 m/s) [Y]).
