"""References specific to aerokit.aero (owned by that sub-package)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- airfoils and span loading -------------------------------------------------------------
    Reference("schrenk_1940", "O. Schrenk", 1940,
              "A Simple Approximation Method for Obtaining the Spanwise Lift Distribution", "NACA TM-948",
              note="Schrenk span loading: mean of the planform and elliptic chord distributions"),
    # --- airworthiness regulations -------------------------------------------------------------
    Reference("cfr14_part25", "U.S. Federal Aviation Administration", 2011,
              "14 CFR Part 25 — Airworthiness Standards: Transport Category Airplanes",
              "Code of Federal Regulations, Title 14 Vol. 1 (2011 edition)", url="https://www.govinfo.gov/",
              note="maneuver load factor (25.337) and discrete-gust design velocity (25.341(a))"),
    # --- aircraft design (editions other than the shared raymer_2018) ---------------------------
    Reference("raymer_1992", "D. P. Raymer", 1992, "Aircraft Design: A Conceptual Approach", "AIAA",
              "2nd ed.", note="Table 6.4 tail volume coefficients (read via scholz_2013)"),
    Reference("raymer_2006", "D. P. Raymer", 2006, "Aircraft Design: A Conceptual Approach", "AIAA, Reston VA",
              "4th ed.", note="general-aviation group weights, pp. 460-461 (read via the SUAVE re-implementation)"),
    Reference("raymer_2012", "D. P. Raymer", 2012, "Aircraft Design: A Conceptual Approach", "AIAA, Reston VA",
              "5th ed.", note="Tables 3.1-3.3 (read via VT AOE 4065 slides); Sec. 15.3.3 group weights "
                              "(read via the AeroSandbox re-implementation)"),
    Reference("scholz_2013", "D. Scholz", 2013, "Tail sizing (technical note AERO_TN_TailSizing_13-04-15)",
              "HAW Hamburg, Aircraft Design and Systems Group (AERO)",
              note="tail volume definitions Eq. 2.6-2.7; Raymer column of Tables 2.3/2.4, pp. 51-52"),
    # --- stability and control course notes ----------------------------------------------------
    Reference("how_2004", "J. P. How", 2004, "16.333 Aircraft Stability and Control, Lecture 2 (Fall 2004)",
              "MIT OpenCourseWare, Massachusetts Institute of Technology",
              note="downwash gradient, stick-fixed neutral point, static margin, trim, pp. 2-6 to 2-10"),
    Reference("lutze_2003", "Lutze", 2003, "AOE 3104 problem-sheet solutions (Problem Sheets 4 and 5)",
              "Virginia Tech, Department of Aerospace and Ocean Engineering",
              note="DATCOM (Helmbold) lift-curve slope, MATLAB 'liftcurve' tables; sweep conversion (24.997 deg)"),
    # --- open-source re-implementations used as secondary sources -------------------------------
    Reference("sharpe_2021", "P. D. Sharpe", 2021,
              "AeroSandbox: A Differentiable Framework for Aircraft Design Optimization",
              "Massachusetts Institute of Technology (S.M. thesis)",
              url="https://github.com/peterdsharpe/AeroSandbox",
              note="raymer_general_aviation_weights.py (cites Raymer 5th ed. Sec. 15.3.3), read 2026-10-25"),
    Reference("lukaczyk_2015", "T. W. Lukaczyk et al.", 2015,
              "SUAVE: An Open-Source Environment for Multi-Fidelity Conceptual Vehicle Design",
              "16th AIAA/ISSMO Multidisciplinary Analysis and Optimization Conference",
              url="https://github.com/suavecode/SUAVE",
              note="Methods/Weights/Correlations/General_Aviation/*.py (cites Raymer 4th ed. pp. 460-461), "
                   "read 2026-10-25"),
    # --- mission planning: geodesy, search theory, performance (aerokit.mission) -----------------
    Reference("vincenty_1975", "T. Vincenty", 1975,
              "Direct and inverse solutions of geodesics on the ellipsoid with application of nested equations",
              "Survey Review 23(176):88-93",
              note="inverse and direct iterations implemented from the standard formulation; the paper itself "
                   "was not re-read in this session"),
    Reference("karney_2013", "C. F. F. Karney", 2013, "Algorithms for geodesics", "Journal of Geodesy 87:43-55",
              note="named as the robust alternative (geographiclib) for nearly antipodal lines where Vincenty's "
                   "iteration fails; used only if geographiclib is installed"),
    Reference("snyder_1987", "J. P. Snyder", 1987, "Map Projections: A Working Manual",
              "U.S. Geological Survey Professional Paper 1395, Washington DC",
              note="authalic latitude and Lambert azimuthal equal-area projection (equation numbers not checked "
                   "in this session)"),
    Reference("iamsar_1998", "International Maritime Organization, International Civil Aviation Organization", 1998,
              "IAMSAR Manual: International Aeronautical and Maritime Search and Rescue Manual, Vol. II Mission "
              "Co-ordination", "IMO/ICAO, London/Montreal",
              note="search-pattern names PS, CS, SS, VS; year is that of the first edition; no edition was read in "
                   "this session, the geometry follows the standard pattern definitions"),
    Reference("koopman_1980", "B. O. Koopman", 1980,
              "Search and Screening: General Principles with Historical Applications", "Pergamon Press, New York",
              note="random-search formula POD = 1 - exp(-W L / A) (not re-read in this session)"),
    Reference("hepperle_2012", "M. Hepperle", 2012, "Electric Flight – Potential and Limitations",
              "NATO STO AVT-209 Workshop, Lisbon, 22–24 October 2012 (DLR)",
              url="https://elib.dlr.de/78726",
              note="read 2026-10-25 (slide text; the equations are images): battery range from E*, total efficiency, "
                   "L/D, g and battery mass fraction, mass constant in flight; sizing for range from payload, empty-"
                   "mass fraction, E*, efficiency and L/D; payload-zero limit; example E* 180 Wh/kg, 70 %, L/D 30"),
    Reference("wikipedia_queues_2026", "Wikipedia contributors", 2026,
              "Pollaczek–Khinchine formula; M/M/c queue; Erlang (unit)", "Wikipedia, The Free Encyclopedia",
              url="https://en.wikipedia.org/wiki/M/M/c_queue",
              note="read 2026-10-25: P-K mean L and W_q for M/G/1; Erlang C and W = C/(cμ − λ) + 1/μ for M/M/c; "
                   "secondary source (no queueing textbook read)"),
    Reference("icao_cec_2015", "International Civil Aviation Organization", 2015,
              "ICAO Carbon Emissions Calculator Methodology", "ICAO, Montreal", "Version 8",
              url="https://www.icao.int/sites/default/files/sp-files/environmental-protection/CarbonOffset/Documents/"
                  "Methodology%20ICAO%20Carbon%20Calculator_v8-2015.pdf",
              note="read 2026-10-25 (PDF text): CO2 per pax = 3.16 x (total fuel x pax-to-freight factor)/(y-seats x "
                   "load factor); 3.16 = tonnes of CO2 per tonne of aviation fuel"),
    Reference("uk_corsia_order_2021", "UK Government", 2021, "The Air Navigation (Carbon Offsetting and Reduction "
              "Scheme for International Aviation) Order 2021, SI 2021/534", "legislation.gov.uk",
              url="https://www.legislation.gov.uk/uksi/2021/534/article/28",
              note="read 2026-10-25: art. 28(5) 3.16 kg CO2/kg Jet-A, 3.10 AvGas and Jet-B"),
    Reference("gps_sps_ps_2008", "U.S. Department of Defense", 2008,
              "Global Positioning System Standard Positioning Service Performance Standard", "DoD, Washington DC",
              "4th ed.", url="https://rosap.ntl.bts.gov/view/dot/16930",
              note="read 2026-10-25 (PDF text): Table 3.2-1 baseline 24-slot assignments (RAAN, argument of latitude, "
                   "GEC) at 00:00 UTC 1 July 1993, GHA 18h36m14.4s; Table 3.2-3 a = 26 559.7 km, e = 0, i = 55 deg; "
                   "mean nodal regression -0.04187 deg/day. The 5th ed. (2020) was not read; secondary sources say "
                   "the baseline constellation is unchanged"),
    Reference("gsc_galileo_2026", "European GNSS Service Centre", 2026,
              "Galileo Reference Constellation: Orbital and Technical Parameters", "EUSPA GSC",
              url="https://www.gsc-europa.eu/system-service-status/orbital-and-technical-parameters",
              note="read 2026-10-25 via a fetch summary: Walker 24/3/1, a = 29 599.8 km, e = 0, i = 56 deg, plane RAAN "
                   "317.632/77.632/197.632 deg and nominal mean anomalies at 2016-11-21 00:00 UTC"),
    Reference("cospas_sarsat_2024", "Cospas-Sarsat Secretariat", 2024, "Cospas-Sarsat Update (Beacon Manufacturers "
              "Workshop, Jacksonville, 10 May 2024)", "NOAA SARSAT",
              url="https://www.sarsat.noaa.gov/wp-content/uploads/2024-BMW_Cospas-Sarsat-Update.pdf",
              note="read 2026-10-25 (PDF text): MEOSAR payloads in use: Galileo 23, GPS DASS 21, GLONASS 2 (BeiDou 6 "
                   "operational, not in use); 4 LEO and 10 GEO payloads in operation; no orbit elements given"),
    Reference("wikipedia_pt6_2026", "Wikipedia contributors", 2026, "Pratt & Whitney Canada PT6",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Pratt_%26_Whitney_Canada_PT6",
              note="read 2026-10-25 (WebFetch): PT6A-60A 1,050 hp / 780 kW, dry weight 487 lb / 221 kg (King Air "
                   "300/350); PT6A-67B 890 kW / 240 kg; PT6A-67D 948 kW / 234 kg. Secondary source; the engine "
                   "type certificate data sheet was not read"),
    Reference("wikipedia_king_air_2026", "Wikipedia contributors", 2026, "Beechcraft Super King Air",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Beechcraft_Super_King_Air",
              note="Specifications table, 350i column, read 2026-10-25: MTOW 6 804 kg, OEW 4 516 kg, 2 × 783 kW "
                   "PT6A-60A; secondary source citing the 2016 Beechcraft product cards (not read)"),
    Reference("anderson_1999", "J. D. Anderson Jr.", 1999, "Aircraft Performance and Design", "WCB/McGraw-Hill, Boston",
              note="named by the Ansys challenge card; Breguet range/endurance for propeller aircraft (equation "
                   "numbers not checked in this session)"),
)
