"""References for the 2026 challenge modules (aerokit.planetary, aerokit.approach, aerokit.investigation)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- Venus -------------------------------------------------------------------------------------
    Reference("wikipedia_venus_atmosphere_2026", "Wikipedia contributors", 2026, "Atmosphere of Venus",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Atmosphere_of_Venus",
              note="read 2026-11-03: temperature [°C] and pressure table 0-100 km (the column is labelled atm; the "
                   "numbers are those usually quoted from the Venus International Reference Atmosphere in bar, "
                   "Seiff et al. 1985, which was not read); 96.5 % CO2, 3.5 % N2; cloud-top wind ~100 m/s, surface "
                   "wind < 2 m/s; cloud deck ~48-70 km; 52.5-54 km at 293-310 K"),
    Reference("wikipedia_venus_2026", "Wikipedia contributors", 2026, "Venus",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Venus",
              note="read 2026-11-03: mean radius 6051.8 km, surface gravity 8.87 m/s2, sidereal rotation "
                   "-243.0226 d, solar day 116.75 d, semi-major axis 0.723332 AU, Bond albedo 0.76, solar "
                   "irradiance 2600 W/m2"),
    Reference("iupac_2019_constants", "BIPM / IUPAC", 2019,
              "SI Brochure (9th ed.) exact constants; IUPAC standard atomic weights",
              "BIPM, Sèvres; IUPAC CIAAW",
              note="R = N_A k = 8.314462618 J/(mol K) exact since 2019; c = 299 792 458 m/s; astronomical unit "
                   "149 597 870 700 m (IAU 2012 B2); molar masses CO2 44.0095, N2 28.0134, He 4.002602, "
                   "H2 2.01588 g/mol (values as tabulated; not re-read in this session)"),
    Reference("landis_2001_venus", "G. A. Landis", 2001, "Exploring Venus by Solar Airplane",
              "NASA Glenn Research Center (STAIF 2001), NTRS 20020022923",
              url="https://ntrs.nasa.gov/citations/20020022923",
              note="read by the research agent 2026-11-03 (PDF text), not by us: Table 1 zonal wind ~44-45 m/s at "
                   "45 km, 65 m/s at 53 km, 100 m/s at 60 km; surface wind 0.3-1 m/s"),
    Reference("landis_2002_venus", "G. A. Landis, C. LaMarre, A. Colozza", 2002,
              "Atmospheric Flight on Venus", "IAC 2002 / NASA NTRS 20030022791",
              url="https://ntrs.nasa.gov/citations/20030022791",
              note="read by the research agent 2026-11-03, not by us: cloud-top wind ~95 m/s; downward solar flux "
                   "20-50 % of the top value at the cloud base, ~95 % at 65 km (citing Ekonomov et al. 1983); "
                   "upward reflected flux ~90 % of downward at 60 km"),
    # --- guidance and flight mechanics ---------------------------------------------------------------
    Reference("park_deyst_how_2004", "S. Park, J. Deyst, J. P. How", 2004,
              "A New Nonlinear Guidance Logic for Trajectory Tracking",
              "AIAA Guidance, Navigation, and Control Conference, AIAA 2004-4900",
              doi="10.2514/6.2004-4900",
              note="L1 guidance: a_cmd = 2 V^2 sin(eta) / L1 (not re-read in this session)"),
    Reference("hypsometric_equation", "J. M. Wallace, P. V. Hobbs", 2006,
              "Atmospheric Science: An Introductory Survey", "Academic Press, Burlington MA", "2nd ed.",
              note="hypsometric equation dz = (R T / g) dp/p, applied here to a column warmer/colder than ISA "
                   "(derivation in the code; book not re-read in this session)"),
    Reference("fsf_alar_bn71_2009", "Flight Safety Foundation", 2009,
              "ALAR Briefing Note 7.1 - Stabilized Approach", "FSF ALAR Tool Kit",
              url="https://skybrary.aero/sites/default/files/bookshelf/864.pdf",
              note="read 2026-11-03 (PDF text): stable by 1000 ft IMC / 500 ft VMC; VREF to VREF + 20 kt; sink "
                   "<= 1000 fpm; ILS within one dot; go-around if unstable below the gate (year of the tool-kit "
                   "edition assumed, not printed on the extracted pages)"),
    Reference("rippl_perea_2018", "M. Rippl, S. Perea", 2018,
              "Global Integrity combining ARAIM and SBAS - Method and Operational Benefit",
              "Proceedings of ION GNSS+ 2018 (German Aerospace Center DLR / Airbus Defence and Space)",
              url="https://elib.dlr.de/122351/1/ION2018_D5_Rippl_ARAIMSBAS_Paper_final_1.00.pdf",
              note="read 2026-11-03 (PDF text): 'The inflation factor K_v,SBAS = 5.33 corresponds with a two-sided "
                   "tail probability P_HMI = 2 Q(5.33) ~ 1e-7'; K(0) = Q^-1(0.5 P_HMI) = 5.33"),
    Reference("friis_1946", "H. T. Friis", 1946, "A Note on a Simple Transmission Formula",
              "Proceedings of the IRE 34(5), 254-256", doi="10.1109/JRPROC.1946.234568",
              note="free-space transmission formula (standard result; paper not re-read in this session)"),
    Reference("monopulse_accuracy", "RF Essentials (web knowledge base); D. K. Barton", 2004,
              "How do I design a monopulse tracking radar for precision angle measurement?",
              "rfessentials.com; Barton, Radar System Analysis and Modeling, Artech House (book not read)",
              url="https://rfessentials.com/rf-knowledge-base/how-do-i-design-a-monopulse-tracking-radar-for-"
                  "precision-angle-measurement/",
              note="search summary 2026-11-03: sigma_theta ~ theta_3dB / (k_m sqrt(2 SNR)), k_m typically 1.5-1.8; "
                   "secondary source only — treat k_m = 1.6 as an assumption"),
    # --- accident investigation ----------------------------------------------------------------------
    Reference("savitzky_golay_1964", "A. Savitzky, M. J. E. Golay", 1964,
              "Smoothing and Differentiation of Data by Simplified Least Squares Procedures",
              "Analytical Chemistry 36(8), 1627-1639", doi="10.1021/ac60214a047",
              note="local polynomial smoothing and derivative (implemented by scipy.signal.savgol_filter)"),
    Reference("easa_ercs_2020_2034", "European Commission / EASA", 2020,
              "European Risk Classification Scheme, Commission Delegated Regulation (EU) 2020/2034",
              "EASA Easy Access Rules for Occurrence Reporting, ERCS chapter",
              url="https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/"
                  "easy-access-rules-occurrence-reporting?page=8",
              note="read 2026-11-03 through a fetch summary (tables restated by the fetch tool): severity "
                   "A/E/I/M/S/X; barriers design 5, tactical planning 2, regulations/procedures 3, situational "
                   "awareness 2, warning systems 3, late recovery 1, protections 1, low energy 1 (low-energy key "
                   "risk areas only); only stopped and remaining barriers count; sum 0 -> 0, 1-2 -> 1 ... 17-18 -> 9; "
                   "RED X0-X2 S0-S2 M0-M1 I0, YELLOW X3-X4 S3-S4 M2-M3 I1-I2 E0-E1, else GREEN; numerical "
                   "equivalents X0 = 1e6 falling a decade per digit, S = X/2, M = X/10, I = X/100, E = X/1000"),
    Reference("shappell_wiegmann_2000", "S. A. Shappell, D. A. Wiegmann", 2000,
              "The Human Factors Analysis and Classification System - HFACS",
              "FAA Office of Aviation Medicine, DOT/FAA/AM-00/7",
              note="four levels: unsafe acts, preconditions, unsafe supervision, organisational influences "
                   "(category names as commonly used; not re-read in this session)"),
)
