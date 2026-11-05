"""Shared references used by more than one sub-package (edited only by the maintainer)."""
from aerokit.references import Reference

REFERENCES = (
    # --- elasticity, stability, plates -------------------------------------------------------
    Reference("timoshenko_goodier_1970", "S. P. Timoshenko, J. N. Goodier", 1970, "Theory of Elasticity",
              "McGraw-Hill, New York", "3rd ed.", note="Kirsch plate, Lamé cylinder, rotating disk"),
    Reference("timoshenko_gere_1961", "S. P. Timoshenko, J. M. Gere", 1961, "Theory of Elastic Stability",
              "McGraw-Hill, New York", "2nd ed.", note="column and plate buckling"),
    Reference("timoshenko_woinowsky_1959", "S. P. Timoshenko, S. Woinowsky-Krieger", 1959,
              "Theory of Plates and Shells", "McGraw-Hill, New York", "2nd ed.", note="Navier plate series"),
    Reference("budynas_nisbett_2015", "R. G. Budynas, J. K. Nisbett", 2015,
              "Shigley's Mechanical Engineering Design", "McGraw-Hill, New York", "10th ed."),
    Reference("pilkey_2008", "W. D. Pilkey, D. F. Pilkey", 2008, "Peterson's Stress Concentration Factors",
              "Wiley, Hoboken", "3rd ed."),
    # --- aircraft structures ------------------------------------------------------------------
    Reference("bruhn_1973", "E. F. Bruhn", 1973, "Analysis and Design of Flight Vehicle Structures",
              "Jacobs Publishing, Indianapolis"),
    Reference("megson_2017", "T. H. G. Megson", 2017, "Aircraft Structures for Engineering Students",
              "Butterworth-Heinemann, Oxford", "6th ed."),
    Reference("nasa_sp8007", "NASA", 1968, "Buckling of Thin-Walled Circular Cylinders (NASA SP-8007)",
              "NASA Space Vehicle Design Criteria", url="https://ntrs.nasa.gov/citations/19690013955"),
    Reference("mil_hdbk_5j_2003", "U.S. Department of Defense", 2003,
              "MIL-HDBK-5J: Metallic Materials and Elements for Aerospace Vehicle Structures",
              "DoD, Washington DC", note="design allowables, Ramberg-Osgood exponents"),
    Reference("ramberg_osgood_1943", "W. Ramberg, W. R. Osgood", 1943,
              "Description of stress-strain curves by three parameters", "NACA TN-902"),
    # --- aircraft design ----------------------------------------------------------------------
    Reference("raymer_2018", "D. P. Raymer", 2018, "Aircraft Design: A Conceptual Approach",
              "AIAA, Reston VA", "6th ed.", note="weight fractions, constraint diagram, group weights"),
    Reference("cfr14_part23", "U.S. Federal Aviation Administration", 2017,
              "14 CFR Part 23 — Airworthiness Standards: Normal Category Airplanes (pre-amendment 64 load rules)",
              "FAA, Washington DC", note="maneuver and gust load factors (FAR 23.333/23.337/23.341)"),
    Reference("iso_2533_1975", "International Organization for Standardization", 1975,
              "ISO 2533: Standard Atmosphere", "ISO, Geneva", note="ISA 0–20 km"),
    Reference("anderson_2017", "J. D. Anderson Jr.", 2017, "Fundamentals of Aerodynamics",
              "McGraw-Hill Education, New York", "6th ed.",
              note="read from the user's PDF on 2026-10-25: skin friction Eqs. 4.86/4.88, drag polar Eq. 6.24, "
                   "lift slope Eqs. 5.69/5.70 (AR > 4) and Helmbold 5.81 (AR < 4), standard atmosphere Appendix D; "
                   "page citations re-checked against the PDF by script on 2026-10-25"),
    Reference("abbott_vondoenhoff_1959", "I. H. Abbott, A. E. von Doenhoff", 1959,
              "Theory of Wing Sections, Including a Summary of Airfoil Data", "Dover, New York",
              note="NACA 4-digit thickness and mean-line equations"),
    # --- numerical methods --------------------------------------------------------------------
    Reference("cook_2002", "R. D. Cook, D. S. Malkus, M. E. Plesha, R. J. Witt", 2002,
              "Concepts and Applications of Finite Element Analysis", "Wiley, New York", "4th ed."),
    Reference("bathe_2014", "K.-J. Bathe", 2014, "Finite Element Procedures", "K.-J. Bathe, Watertown MA",
              "2nd ed."),
    Reference("zienkiewicz_taylor_2013", "O. C. Zienkiewicz, R. L. Taylor, J. Z. Zhu", 2013,
              "The Finite Element Method: Its Basis and Fundamentals", "Butterworth-Heinemann, Oxford", "7th ed."),
    Reference("hughes_2000", "T. J. R. Hughes", 2000, "The Finite Element Method: Linear Static and Dynamic "
              "Finite Element Analysis", "Dover, Mineola NY"),
    Reference("celik_2008", "I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, H. Coleman, P. E. Raad", 2008,
              "Procedure for estimation and reporting of uncertainty due to discretization in CFD applications",
              "ASME J. Fluids Eng. 130(7):078001", doi="10.1115/1.2960953", note="GCI, apparent order"),
    Reference("roache_1998", "P. J. Roache", 1998, "Verification and Validation in Computational Science and "
              "Engineering", "Hermosa Publishers, Albuquerque"),
    Reference("saad_2003", "Y. Saad", 2003, "Iterative Methods for Sparse Linear Systems", "SIAM, Philadelphia",
              "2nd ed.", doi="10.1137/1.9780898718003"),
    Reference("golub_vanloan_2013", "G. H. Golub, C. F. Van Loan", 2013, "Matrix Computations",
              "Johns Hopkins University Press, Baltimore", "4th ed."),
    Reference("nocedal_wright_2006", "J. Nocedal, S. J. Wright", 2006, "Numerical Optimization", "Springer, New York",
              "2nd ed.", doi="10.1007/978-0-387-40065-5"),
    Reference("haftka_gurdal_1992", "R. T. Haftka, Z. Gürdal", 1992, "Elements of Structural Optimization",
              "Kluwer, Dordrecht", "3rd ed.", doi="10.1007/978-94-011-2550-5"),
    Reference("nist_sematech_2012", "NIST/SEMATECH", 2012, "e-Handbook of Statistical Methods",
              "National Institute of Standards and Technology", url="https://www.itl.nist.gov/div898/handbook/",
              note="read 2026-10-25: §8.1.6.2 Weibull pdf, CDF, R(t), h(t), mean α Γ(1+1/γ); §8.4.1.2 likelihood "
                   "with right-censored units (f(t_i) for failures, 1 − F(t_i) for survivors)"),
    # --- materials / fatigue / fracture -------------------------------------------------------
    Reference("dowling_2013", "N. E. Dowling", 2013, "Mechanical Behavior of Materials", "Pearson, Boston", "4th ed."),
    Reference("tada_paris_irwin_2000", "H. Tada, P. C. Paris, G. R. Irwin", 2000, "The Stress Analysis of Cracks "
              "Handbook", "ASME Press, New York", "3rd ed.", doi="10.1115/1.801535"),
    Reference("kaw_2006", "A. K. Kaw", 2006, "Mechanics of Composite Materials", "CRC Press, Boca Raton", "2nd ed."),
    Reference("jones_1999", "R. M. Jones", 1999, "Mechanics of Composite Materials", "Taylor & Francis, Philadelphia",
              "2nd ed."),
)
