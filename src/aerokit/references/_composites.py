"""References specific to aerokit.composites (owned by that sub-package)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- laminate theory, micromechanics ----------------------------------------------------
    Reference("reddy_2004", "J. N. Reddy", 2004, "Mechanics of Laminated Composite Plates and Shells: Theory and "
              "Analysis", "CRC Press, Boca Raton", "2nd ed.", note="classical lamination theory (CLT), ABD matrices"),
    Reference("tsai_pagano_1968", "S. W. Tsai, N. J. Pagano", 1968, "Invariant properties of composite materials",
              "in S. W. Tsai, J. C. Halpin, N. J. Pagano (eds.), Composite Materials Workshop, Technomic, "
              "Stamford CT", note="material invariants U1..U5"),
    Reference("halpin_kardos_1976", "J. C. Halpin, J. L. Kardos", 1976, "The Halpin-Tsai equations: a review",
              "Polymer Engineering & Science 16(5):344-352", doi="10.1002/pen.760160512",
              note="Halpin-Tsai interpolation for E2 and G12"),
    Reference("schapery_1968", "R. A. Schapery", 1968,
              "Thermal expansion coefficients of composite materials based on energy principles",
              "J. Composite Materials 2(3):380-404", doi="10.1177/002199836800200308",
              note="longitudinal and transverse CTE of a UD ply"),
    # --- failure criteria -------------------------------------------------------------------
    Reference("hill_1948", "R. Hill", 1948, "A theory of the yielding and plastic flow of anisotropic metals",
              "Proc. Royal Society of London A 193(1033):281-297", doi="10.1098/rspa.1948.0045",
              note="anisotropic quadratic yield function underlying Tsai-Hill"),
    Reference("azzi_tsai_1965", "V. D. Azzi, S. W. Tsai", 1965, "Anisotropic strength of composites",
              "Experimental Mechanics 5(9):283-288", doi="10.1007/BF02326292", note="Tsai-Hill criterion"),
    Reference("hoffman_1967", "O. Hoffman", 1967, "The brittle strength of orthotropic materials",
              "J. Composite Materials 1(2):200-206", doi="10.1177/002199836700100210", note="Hoffman criterion"),
    Reference("tsai_wu_1971", "S. W. Tsai, E. M. Wu", 1971, "A general theory of strength for anisotropic materials",
              "J. Composite Materials 5(1):58-80", doi="10.1177/002199837100500106", note="Tsai-Wu tensor criterion"),
    Reference("hashin_rotem_1973", "Z. Hashin, A. Rotem", 1973,
              "A fatigue failure criterion for fiber reinforced materials",
              "J. Composite Materials 7(4):448-464", doi="10.1177/002199837300700404",
              note="1973 form of the Hashin matrix criteria (not read in this repository)"),
    Reference("hashin_1980", "Z. Hashin", 1980, "Failure criteria for unidirectional fiber composites",
              "J. Applied Mechanics 47(2):329-334", doi="10.1115/1.3153664",
              note="plane-stress forms taken from davila_camanho_2003, Table 1 (original not read)"),
    Reference("puck_schurmann_2002", "A. Puck, H. Schürmann", 2002,
              "Failure analysis of FRP laminates by means of physically based phenomenological models",
              "Composites Science and Technology 62(12-13):1633-1662", doi="10.1016/S0266-3538(01)00208-1",
              note="Puck action-plane criterion, IFF modes A/B/C (original not read)"),
    Reference("puck_kopp_2002", "A. Puck, J. Kopp, M. Knops", 2002,
              "Guidelines for the determination of the parameters in Puck's action plane strength criterion",
              "Composites Science and Technology 62(3):371-378", doi="10.1016/S0266-3538(01)00202-0",
              note="recommended inclination parameters p⊥∥(±) (quoted via gu_chen_2019; original not read)"),
    Reference("gu_chen_2019", "J. Gu, P. Chen", 2019, "(open-access article on Puck criterion parameters; "
              "title not recorded)", "Materials 12:3292",
              note="Puck parameter recommendations (citing Puck, Kopp & Knops 2002), Eqs. 26 and 28 for p⊥⊥ and R⊥⊥A"),
    Reference("davila_camanho_2003", "C. G. Dávila, P. P. Camanho", 2003,
              "Failure Criteria for FRP Laminates in Plane Stress", "NASA/TM-2003-212663",
              note="LaRC03 criteria #1-#6 and their parameters; Table 1 plane-stress Hashin forms"),
    Reference("davila_camanho_2005", "C. G. Dávila, P. P. Camanho, C. A. Rose", 2005, "Failure criteria for FRP "
              "laminates", "J. Composite Materials 39(4):323-345", doi="10.1177/0021998305046452",
              note="archival journal version of LaRC03 (implementation follows the 2003 NASA TM)"),
    # --- plates, sandwich -------------------------------------------------------------------
    Reference("mil_hdbk_17_3f_2002", "U.S. Department of Defense", 2002,
              "MIL-HDBK-17-3F: Composite Materials Handbook, Volume 3 — Polymer Matrix Composites: Materials Usage, "
              "Design, and Analysis", "DoD, Washington DC", note="§5.7.1 orthotropic plate buckling"),
    Reference("allen_1969", "H. G. Allen", 1969, "Analysis and Design of Structural Sandwich Panels",
              "Pergamon Press, Oxford", note="thin-face sandwich approximations (not read in this repository)"),
    Reference("zenkert_1995", "D. Zenkert", 1995, "An Introduction to Sandwich Construction",
              "Engineering Materials Advisory Services (EMAS)", note="sandwich beam stiffness and stresses"),
    Reference("ley_lin_1999", "R. P. Ley, W. Lin, U. Mbanefo", 1999, "Facesheet Wrinkling in Sandwich Structures",
              "NASA/CR-1999-208994", note="Table 3 and Eqs. 7-8: wrinkling coefficients k1, k2"),
    Reference("hoff_mautner_1945", "N. J. Hoff, S. E. Mautner", 1945, "The buckling of sandwich-type panels",
              "J. Aeronautical Sciences 12(3):285-297",
              note="wrinkling design coefficient 0.5 (quoted via ley_lin_1999; original not read)"),
)
