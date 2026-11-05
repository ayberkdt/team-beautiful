"""References for the 2026 final-challenge work on the venus2 task (owned by one parallel session; add entries here only)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    Reference("nist_webbook_co2_2026", "P. J. Linstrom, W. G. Mallard (eds.); E. W. Lemmon, M. O. McLinden, D. G. Friend; "
              "M. W. Chase", 2026, "NIST Chemistry WebBook, SRD 69: carbon dioxide and nitrogen (Shomate Cp; "
              "thermophysical properties of fluid systems)", "National Institute of Standards and Technology",
              url="https://webbook.nist.gov/chemistry/",
              note="read by the Venus session 2026-11-04: CO2 Shomate 298-1200 K, N2 100-500 K; CO2 isobars 0.05 and "
                   "0.1 MPa: speed of sound, viscosity, conductivity, Cp 225-400 K "
                   "(research_notes/Venus rotorcraft/K_nist_co2_properties.md)"),
    Reference("jpl_ssd_constants_2026", "JPL Solar System Dynamics", 2026, "Astrodynamic parameters",
              "NASA Jet Propulsion Laboratory", url="https://ssd.jpl.nasa.gov/astro_par.html",
              note="read by the Venus session 2026-11-04: GM Sun 1.32712440041279419e20 m3/s2, GM Venus system "
                   "324858.592 km3/s2, au 149597870700 m"),
    Reference("allen_eggers_1958", "H. J. Allen, A. J. Eggers Jr.", 1958,
              "A study of the motion and aerodynamic heating of ballistic missiles entering the Earth's atmosphere "
              "at high supersonic speeds", "NACA Report 1381",
              note="NOT read in this session: the closed-form peak deceleration V^2 sin(gamma)/(2 e H) is used as a "
                   "textbook result and checked against our own numerical integration (tests/test_venus_entry.py)"),
    Reference("vinh_1980_hypersonic", "N. X. Vinh, A. Busemann, R. D. Culp", 1980,
              "Hypersonic and Planetary Entry Flight Mechanics", "University of Michigan Press, Ann Arbor",
              note="NOT read in this session: standard planar point-mass entry equations over a spherical "
                   "non-rotating planet"),
    Reference("sutton_graves_1971", "K. Sutton, R. A. Graves Jr.", 1971,
              "A general stagnation-point convective-heating equation for arbitrary gas mixtures",
              "NASA TR R-376", url="https://ntrs.nasa.gov/citations/19720003329",
              note="q = k sqrt(rho/Rn) V^3; the constant for the Venus mixture is taken from the research agent's "
                   "note research_notes/Venus rotorcraft/D_*sutton* (see that file for what was read)"),
    Reference("leishman_2006_helicopter", "J. G. Leishman", 2006, "Principles of Helicopter Aerodynamics",
              "Cambridge University Press, Cambridge", edition="2nd ed.",
              note="NOT read in this session: standard BEMT relations (momentum + blade element per annulus, Prandtl "
                   "tip loss, figure of merit); implementation checked by closed-form limits (ideal twist -> FM = 1 "
                   "without profile drag/tip loss) and against Harrington 1951 test data (tests/test_venus_bemt.py)"),
    Reference("leishman_ananthan_2008_coaxial", "J. G. Leishman, S. Ananthan", 2008,
              "An optimum coaxial rotor system for axial flight", "Journal of the American Helicopter Society "
              "53(4):366-381", doi="10.4050/JAHS.53.366",
              note="simplified coaxial BEMT: lower rotor inside the contracted upper wake; what was read is in "
                   "research_notes/Venus rotorcraft/C_* (research agent)"),
    Reference("tauber_palmer_prabhu_2012", "M. E. Tauber, G. E. Palmer, D. K. Prabhu", 2012,
              "Stagnation point radiative heating relations for Venus entry", "NASA Ames preprint ARC-E-DAA-TN2887, "
              "NTRS 20120001655", url="https://ntrs.nasa.gov/citations/20120001655",
              note="read by the research agent (D_tauber_venus_rad_2012.md): eq. 2a/2b fits and the Pioneer Venus "
                   "large-probe trajectory table (beta 190 kg/m2, 11.584 km/s, -31.829 deg at 137.78 km, r_N 0.363 m)"),
    Reference("seiff_1980_pv_structure", "A. Seiff, V. E. Suomi, A. Barnes, G. M. Keating, M. G. Tomasko (data); "
              "A. Seiff et al. (paper)", 1980, "Pioneer Venus probes atmospheric structure (LAS/SAS) and solar flux "
              "radiometer (LSFR) data, PDS4 pv_sed_bundle; paper: Measurements of thermal structure and thermal "
              "contrasts in the atmosphere of Venus and related dynamical observations, JGR 85(A13):7903-7933",
              "NASA Planetary Data System, Atmospheres Node", doi="10.17189/m5zf-6f12",
              url="https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/",
              note="raw CSV tables downloaded by the research agent and extracted by the Venus session itself "
                   "(scripts/venus_pds_extract.py -> src/aerokit/venus/data/pv_profiles.json); the JGR paper was "
                   "NOT read"),
    Reference("counselman_1980_pv_winds", "C. C. Counselman III et al. (data, PDS DLBI bundle)", 1980,
              "Pioneer Venus differential long-baseline interferometry probe velocities; paper: Zonal and "
              "meridional circulation of the lower atmosphere of Venus determined by radio interferometry, "
              "JGR 85(A13)", "NASA Planetary Data System, Atmospheres Node",
              note="raw .tab files extracted by the Venus session (wind = crust-relative minus atmosphere-relative "
                   "probe velocity, altitude via the probe's state table time); paper NOT read"),
    Reference("tomasko_1980_solar_flux", "M. G. Tomasko, L. R. Doose, P. H. Smith, A. P. Odell", 1980,
              "Measurements of the flux of sunlight in the atmosphere of Venus (data: PV LSFR table, PDS4 "
              "pv_sed_bundle)", "J. Geophys. Res. 85(A13):8167-8186 (paper NOT read)",
              doi="10.1029/JA085iA13p08167",
              note="LSFR passband fluxes up/down at SZA 65.7 deg extracted by the Venus session from the PDS CSV"),
    Reference("landis_haag_2013_solar", "G. A. Landis, E. Haag", 2013,
              "Analysis of solar cell efficiency for Venus atmosphere and surface missions",
              "11th AIAA International Energy Conversion Engineering Conference, NTRS 20150016298",
              url="https://ntrs.nasa.gov/citations/20150016298",
              note="read by the research agent (D_landis_haag_2013_solar.md): Table 1 triple-junction array output "
                   "at overhead sun 256 / 404 / 559 W/m2 at 50 / 55 / 60 km (29 % AM0 array)"),
    Reference("titov_2018_clouds", "D. V. Titov et al.", 2018, "Clouds and hazes of Venus",
              "Space Science Reviews 214:126", doi="10.1007/s11214-018-0552-z",
              note="read by the research agent (A_titov2018_clouds.md): layers 47.5-50.5/50.5-56.5/56.5-70 km; "
                   "H2SO4 75-98 wt%"),
    Reference("vega_balloon_1986", "R. Z. Sagdeev et al.; V. M. Linkin et al. (NASA TM-88516 translation); "
              "PDS VEGA balloon archive (Lorenz et al. 2020)", 1986,
              "VEGA balloon experiment: meteorological measurements, vertical winds and turbulence",
              "Science 231:1407-1419 (abstracts); NASA TM-88516; NASA PDS",
              note="read by the research agent (A_vega1985_balloons_lander.md, B_vega_balloon.md): vertical wind "
                   "sd 0.65-0.75 m/s, -3.5..+2 m/s; downdrafts 2-4 m/s; zonal 66-69 m/s at 53-54 km; deployment "
                   "sequence 64/63/61/55/54 km"),
    Reference("johnson_2020_msh", "W. Johnson, S. Withrow-Maser, L. Young, C. Malpica, W. J. F. Koning et al.", 2020,
              "Mars Science Helicopter conceptual design", "NASA/TM-2020-220485, NTRS 20200002139",
              url="https://ntrs.nasa.gov/citations/20200002139",
              note="read by the research agent (C_johnson2020_msh.md): 31 kg hexacopter in a 2.5 m aeroshell; "
                   "C_T/sigma 0.10-0.115; 40 % thrust margin to stall; 20 % contingency; avionics 1.2 kg; "
                   "motor+electronics efficiency 80 %; pack 230 Wh/kg"),
    Reference("balaram_2018_ingenuity", "J. Balaram, T. Canham, C. Duncan et al.", 2018,
              "Mars Helicopter Technology Demonstrator", "AIAA SciTech 2018, AIAA 2018-0023",
              doi="10.2514/6.2018-0023",
              note="read by the research agent (C_balaram2018.md): 1.8 kg, coaxial 1.21 m, max 2800 rpm, 6 VTC4 "
                   "cells 273 g, 360 W continuous / 510 W peak, ~90 s flights"),
    Reference("harrington_1951_coaxial", "R. D. Harrington", 1951,
              "Full-scale-tunnel investigation of the static-thrust performance of a coaxial helicopter rotor",
              "NACA TN 2318", url="https://ntrs.nasa.gov/citations/19930083001",
              note="read by the research agent, figures 4 and 8 digitised (C_harrington1951.md); used as the BEMT "
                   "validation set (tests/test_venus_bemt.py)"),
    Reference("landis_2026_planetary_aircraft", "G. A. Landis", 2026, "Planetary aircraft: concepts and design evolution",
              "Presentation, National Academies ASEB/SSB joint meeting, NTRS 20260004489",
              note="read by the research agent (B_landis_venus_airplane.md): folded 103 kg Venus airplane in a 3.7 m "
                   "aeroshell; entry mass fractions vehicle 20 %, heat shield 7+13 %, backshell 12+8 %, parachute 10 %, "
                   "deployment mechanism 15 %, misc 15 %; +30 % contingency"),
    Reference("pensado_2025_dragonfly_edl", "A. Pensado et al. (as recorded by the research agent)", 2025,
              "Dragonfly entry, descent and landing", "conference paper (see C_pensado2025_dragonfly_edl.md)",
              note="read by the research agent: rotors spun under the 16.7 m main parachute, release at 1000-800 m "
                   "with descent below 2.9 m/s, entry mass 2309-2600 kg, 4.5 m aeroshell"),
    Reference("delaune_2022_mahd", "J. Delaune et al.", 2022, "Mid-Air Helicopter Delivery at Mars using a jetpack",
              "IEEE Aerospace Conference 2022", note="read by the research agent (C_delaune2022_mahd.md): separation "
                   "600 m above ground, 3 s free fall, 12 s rotor spin-up, 275 kg entry mass"),
    Reference("dutta_2023_davinci", "S. Dutta et al.; J. B. Garvin et al.", 2023,
              "DAVINCI entry, descent and probe architecture; Revealing the mysteries of Venus (PSJ 3:117, 2022)",
              "AIAA SciTech 2023; Planetary Science Journal", note="read by the research agent (B_davinci.md, "
                   "D_davinci_probe_arch.md): entry 10.4 km/s at -6.3 deg, 32 g; pilot 1.8 m DGB at Mach 0.8, main "
                   "5.8 m at ~70 km; ~1 h descent; S-band relay 154-1200 Mbit"),
    Reference("fimmel_1983_pioneer_venus", "R. O. Fimmel, L. Colin, E. Burgess", 1983, "Pioneer Venus",
              "NASA SP-461", url="https://ntrs.nasa.gov/citations/19830022069",
              note="read by the research agent (B_fimmel1983_sp461.md): large probe 315 kg, 1.5 m, 280 g, heat shield "
                   "off ~67 km, 17 min on parachute, chute released 47 km; small probes 90 kg, 223-458 g"),
    Reference("siddiqi_2018_beyond_earth", "A. A. Siddiqi", 2018, "Beyond Earth: a chronicle of deep space "
              "exploration, 1958-2016", "NASA SP-2018-4041", note="read by the research agent (B_siddiqi2018.md): "
                   "Venera 4-16 and Vega entries, parachutes, landing speeds, surface lifetimes"),
    Reference("young_2004_rwd", "L. A. Young et al.", 2004, "Rotary-wing decelerators for probe descent through "
              "the atmosphere of Venus", "2nd International Planetary Probe Workshop, NASA CP-2004-213456",
              note="read by the research agent (B_young2004_rwd_husseyin2016.md): 200 kg probe, three 0.42 m rotors, "
                   "8.5 m/s design descent; release -> deploy -> spin-up -> autorotation"),
    Reference("dutta_2012_low_beta", "S. Dutta, B. Smith, D. Prabhu, E. Venkatapathy", 2012,
              "Mission sizing and trade studies for low ballistic coefficient entry systems to Venus",
              "IEEE Aerospace Conference 2012, NTRS 20120006657",
              note="read by the research agent (D_dutta_2012_venus_entry.md): Table 1 beta, gamma, V (200 km "
                   "interface), D, n_max, q_max for Venera 4-14, Vega, Pioneer Venus; Fig. 1 low-beta contours"),
)
