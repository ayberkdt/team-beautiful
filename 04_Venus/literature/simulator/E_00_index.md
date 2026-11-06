# E_00_index — Venus simulator data book: sources read on 5 Nov 2026

Purpose: deepen the research behind VESPER (doc 25) for a high-fidelity Venus rotorcraft simulator. The data book is
`04_Venus/docs/26_venus_sim_databook.md`; data files are in `04_Venus/literature/data/`.

**Tags:** **[D]** read at the primary source in this session · **[D-ag]** secondary source, or read by an earlier
agent/session (A_–D_ notes; not re-read today) · **[A]** abstract/snippet only · **[K]** computed today from [D] ·
**[Y]** judgement.
Downloads (untrusted data, read only): `D:\tmp_ideathon\venus_research\{pv,vega,nist,gram,pdf}\`; scripts
`build_atm.py`, `vega_stats.py` in `D:\tmp_ideathon\venus_research\`.

## Notes

| File | Source | Read level | Key content |
|---|---|---|---|
| `E_01_pv_sed_probe_tables.md` | Pioneer Venus LAS/SAS descent + entry tables (PDS SED) | full data [D] | T, p, ρ at 4 sites, 40–70 km; accuracy 0.5 %/1 K; 65–70 km thin |
| `E_02_pv_dlbi_winds.md` | Pioneer Venus DLBI winds (PDS) | full data [D] | zonal 38→98 m/s at 40→64 km; meridional −7…+8 m/s |
| `E_03_pv_lsfr_solar_flux.md` | Pioneer Venus LSFR solar flux (PDS) | full data [D] | down flux shape, up/down 0.78–0.89 |
| `E_04_vega_balloons_lander_pds.md` | VEGA-1/2 balloons + VEGA-2 lander (PDS, Lorenz) | full data [D] | σ_w 0.66/0.73 m/s, −3.5…+2.0 m/s, **correlation ~1500 s**; U 65–69 m/s |
| `E_05_nist_co2_n2_properties.md` | NIST WebBook CO2, N2 isobars | data [D] | a, µ, γ, cp, k; mixture rules |
| `E_06_jpl_ssd_venus_constants.md` | JPL SSD | page [D] | GM 324858.592 km³/s², R 6051.8 km, −243.018 d |
| `E_07_venus_gram_amat.md` | Venus-GRAM via AMAT (VIRA-based) | data [D-ag tertiary] | low-lat profile; ρ vs latitude (−25…−30 % at 65–70 km, 80°N) |
| `E_08_ando2020_radio_occultation.md` | Ando et al. 2020 Sci. Rep. (VEX + Akatsuki RO) | full text [D]; Tellmann 2009 [A] | stability 0–1 K/km at 50–58 km; polar layer to 42 km; LT not analysed |
| `E_09_lefevre2017_les_convective_layer.md` | Lefèvre, Spiga, Lebonnois 2017 JGR | full text [D] | cells 6–15 km, w −2.9…+2.2 m/s, narrow downdrafts |
| `E_10_lefevre2018_les_wind_shear.md` | Lefèvre, Lebonnois, Spiga 2018 JGR | full text [D] | layer 46–55 km; w +2/−3 m/s; cells ~20 km; GW ≤ 20 km |
| `E_11_sanchezlavega2017_dynamics_review.md` | Sánchez-Lavega et al. 2017 SSR | Sects. 2.1–2.4 [D] | ~100 m/s cloud top ±45°; 70 m/s at 60 km; v ±5 m/s; LT +5–15 m/s only at 65–70 km |
| `E_12_knollenberg_hunten1980_clouds.md` | Knollenberg & Hunten 1980 JGR | Tables 1, 4, 5 [D] | layers, modes, τ 7.3/11.1/12.2, mass ~0.8/7.5/21 mg/m³ [K] |
| `E_13_dryden_mil_f_8785c_mathworks.md` | MathWorks Dryden page (MIL-F-8785C/1797) | page [D-ag] | filter forms, L = 533 m default |
| `E_14_johnson2005_vortex_ring_state.md` | Johnson 2005 NASA/TP-2005-213477 | model sections [D] | VRS −0.45…−1.5 v_h; vanishes at Vx ≥ 0.95 v_h; parameter table |
| `E_15_chen1989_dynamic_inflow.md` | Chen 1989 NASA TM-102219 | inflow section [D] | Pitt–Peters M, hover τ = (4/3π)/v0 |
| `E_16_yoon2016_multirotor_interaction.md` | Yoon, Lee, Pulliam 2016 (NASA Ames) | results [D] | 0.3D spacing → ~2 % loss; VESPER gap is 0.04D |
| `E_17_johnson2020_msh_weights_flap.md` | Johnson et al. 2020 NASA/TM-2020-220485 | pp. 17–23, 42 [D] | NDARC weight relations; MH Lock number 0.3, ~3 % damping |
| `E_18_lugus_skypersonic_mars_simulator.md` | LuGus portfolio, Liftoff news, Skypersonic press | pages [D]/[D-ag] | "Powered by Liftoff", NASA analog training, Unity, GPS-denied, CHAPEA |
| `E_19_venus_flagship_2020_aerobot.md` | Venus Flagship Mission Study 2020 | Sect. 3.2.3 [D] | 15 m + 7.5 m balloon, 52–62 km, 1403 kg MEV, 125/36 W |
| `E_20_seals_and_other_snippets.md` | various | snippets [A] | FFKM 98 % acid 150 °C; mode-3 debate; aerobot gondola 216 kg |

## Data files

| File | What |
|---|---|
| `../data/venus_atmosphere_40_70km.csv` (+ `.md`) | 40–70 km every 0.5 km: T/p/ρ mean + envelope, 5 soundings, a, µ, ν, γ, cp, k, g, winds, solar flux shape, GRAM latitude columns |
| `../data/venus_turbulence_model.json` | recommended mean wind, convective gusts, downdraft events, Dryden small-scale turbulence, gravity waves, presets — each value with source |

## Not obtained (searched, not found or blocked)
- VIRA tables (Seiff et al. 1985) — still only via GRAM (E_07).
- Numeric T(z, latitude, local time) tables from VeRa/Akatsuki — only figures (E_08); no afternoon in-situ profile.
- Tellmann 2009 full text (VeRa) — abstract only; Venus-specific turbulence spectra at < 75 s scales — not found.
- Liftoff / Mars Drone Simulator physics documentation — not public (E_18).
- Kalrez/Chemours official acid ratings — only press snippets (E_20).
