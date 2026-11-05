"""Tests of the buckling module.

Sources read: Gerard & Becker 1957 (NACA TN 3781), Gerard 1957 (NACA TN 3784), NASA SP-8007 (1968),
Wierzbicki, MIT 2.080 lecture notes (LibreTexts Sec. 10.3, citing the Timoshenko & Gere approximations).
"""
import math

import numpy as np
from scipy.optimize import brentq

from aerokit.structures import beam, section
from aerokit.structures import buckling as bk
from aerokit.verification import check, check_true, expect_error

E, NU = 71.7e9, 0.33


def test_euler_johnson():
    check("Euler = beam.euler_column", bk.euler_critical(E, 2e-8, 1.2, "fixed-free"),
          beam.euler_column(E, 2e-8, 1.2, 2.0), rtol=1e-12, source="derivation: beam module")
    x1 = brentq(lambda x: math.tan(x) - x, 4.0, 4.6)
    check("fixed-pinned K = π/4.4934 (tan x = x)", bk.END_CONDITION_K["fixed-pinned"], math.pi / x1, rtol=1e-4,
          source="derivation: first root of tan(kL) = kL")
    sc = 400e6
    lg = bk.johnson_transition_slenderness(sc, E)
    check("Johnson at transition: σ = σc/2", bk.johnson_stress(sc, E, lg * (1 - 1e-12)), sc / 2, rtol=1e-9,
          source="derivation: parabola-Euler tangency")
    check("Johnson at transition: σ = σ_Euler", bk.euler_stress(E, lg), sc / 2, rtol=1e-12, source="derivation")
    h = 1e-4 * lg
    slope_j = (bk.johnson_stress(sc, E, lg - h) - bk.johnson_stress(sc, E, lg - 2 * h)) / h
    slope_e = (bk.euler_stress(E, lg + 2 * h) - bk.euler_stress(E, lg + h)) / h
    # one-sided differences with h = 1e-4·lg have an O(h) error, hence the 0.1 % tolerance
    check("Johnson at transition: slope = Euler slope", slope_j, slope_e, rtol=1e-3, source="derivation: tangency")
    check("Johnson L/ρ → 0: σ = σc", bk.johnson_stress(sc, E, 0.0), sc, source="derivation")
    expect_error("Euler rejects a negative length", bk.euler_critical, E, 1e-8, -1.0, error=ValueError)
    expect_error("unknown end condition is rejected", bk.euler_critical, E, 1e-8, 1.0, "no", error=KeyError)


def test_secant():
    A, rho, c, Le = 4e-4, 0.01, 0.015, 1.5
    PE = math.pi ** 2 * E * A * rho ** 2 / Le ** 2
    P = PE / 4                     # (Le/2ρ)√(P/EA) = (π/2)·½ = π/4 → sec = √2
    e = 0.002
    check("secant σ_max at P = P_E/4: sec(π/4) = √2", bk.secant_max_stress(P, A, E, rho, e, c, Le),
          P / A * (1 + e * c / rho ** 2 * math.sqrt(2)), rtol=1e-12, source="derivation: closed form")
    sy = 500e6
    Pk = bk.secant_critical_load(sy, A, E, rho, e, c, Le)
    check("secant root: σ_max = σ_yield", bk.secant_max_stress(Pk, A, E, rho, e, c, Le), sy, rtol=1e-9,
          source="derivation: root")
    # e → 0, slender column: P → P_E (the sec term grows only near P_E); here P_E/A ≪ σ_y
    check("secant e → 0, slender: P → P_E", bk.secant_critical_load(sy, A, E, rho, 1e-12, c, Le), PE, rtol=1e-4,
          source="derivation: limit")
    check("secant e → 0, short column: P → σ_y·A", bk.secant_critical_load(sy, A, E, rho, 1e-12, c, 0.05), sy * A,
          rtol=1e-6, source="derivation: limit")
    check_true("eccentricity reduces the load", Pk < min(PE, sy * A), f"{Pk:.4g}", source="derivation")


def test_ramberg_osgood():
    F, n = 450e6, 12.0
    check("RO: plastic strain 0.002 at σ = F", bk.ro_strain(F, E, F, n) - F / E, 0.002, rtol=1e-12,
          source="derivation: definition")
    # find σ0.7 and σ0.85 on the curve and recover n (derivation of the Ramberg & Osgood 1943 relation)
    s07 = brentq(lambda s: bk.ro_secant_modulus(s, E, F, n) - 0.7 * E, 1e6, 2 * F)
    s085 = brentq(lambda s: bk.ro_secant_modulus(s, E, F, n) - 0.85 * E, 1e6, 2 * F)
    check("RO n = 1 + ln(17/7)/ln(σ0.7/σ0.85) round trip", bk.ro_n_secant(s07, s085), n, rtol=1e-9,
          source="derivation: from the RO equation")
    s = 380e6
    h = 1e3
    numeric = 2 * h / (bk.ro_strain(s + h, E, F, n) - bk.ro_strain(s - h, E, F, n))
    check("RO tangent modulus = numerical dσ/dε", bk.ro_tangent_modulus(s, E, F, n), numeric, rtol=1e-7,
          source="derivation: central difference")
    # tangent-modulus column: reduces to Euler for very slender columns
    check("tangent-modulus column, slender → Euler", bk.tangent_modulus_column(E, F, n, 300.0),
          bk.euler_stress(E, 300.0), rtol=1e-6, source="derivation: limit")
    s_t = bk.tangent_modulus_column(E, F, n, 40.0)
    check("tangent-modulus column equation residual", s_t, math.pi ** 2 * bk.ro_tangent_modulus(s_t, E, F, n) / 40.0 ** 2,
          rtol=1e-9, source="derivation: Engesser")
    expect_error("ro_n_secant order check", bk.ro_n_secant, 100e6, 200e6, error=ValueError)


def test_plate_compression():
    for ab in (0.6, 1.0, 1.41, 2.0, 3.5):
        check(f"SS-SS exact Lévy solution = closed form (a/b={ab})", bk.plate_compression_k(ab, "SS-SS"),
              bk.plate_compression_k_ss_closed(ab), rtol=1e-9, source="Gerard & Becker 1957, TN 3781 Eq. (20)")
    check("SS-SS integer a/b → k = 4", bk.plate_compression_k_ss_closed(3.0), 4.0, rtol=1e-12,
          source="Gerard & Becker 1957, TN 3781 Table 7 (k_c = 4.0)")
    check("SS-SS a/b = √2: m = 1 and 2 cross at k = 4.5", bk.plate_compression_k_ss_closed(math.sqrt(2)), 4.5,
          rtol=1e-12, source="derivation: (1/√2 + √2)² = 4.5")
    cc = min(bk.plate_compression_k(x, "C-C") for x in np.linspace(0.6, 0.72, 13))
    # table value has 3 digits; the Lévy solution takes the loaded edges SS (no effect on a long plate) -- 0.3 %
    check("C-C long plate k = 6.98", cc, 6.98, rtol=3e-3, source="Gerard & Becker 1957, TN 3781 Table 7")
    cf = min(bk.plate_compression_k(x, "C-F", 0.3) for x in np.linspace(1.45, 1.85, 17))
    check("C-F long plate k = 1.28", cf, 1.28, rtol=3e-3, source="Gerard & Becker 1957, TN 3781 Table 7")
    for nu, k_ in ((0.25, 0.456), (0.30, 0.426), (0.35, 0.395)):
        # Fig. 2(b) value at a/b = ∞; at a/b = 60, (b/a)² = 2.8e-4 remains; 3-digit reading: 0.3 % tolerance
        check(f"SS-F long flange k (ν={nu})", bk.plate_compression_k(60.0, "SS-F", nu), k_, rtol=3e-3,
              source="Gerard & Becker 1957, TN 3781 Fig. 2(b)")
    check("SS-F long flange k ≈ 0.43 (table)", bk.plate_compression_k(60.0, "SS-F", 0.3), 0.43, rtol=0.01,
          source="Gerard & Becker 1957, TN 3781 Table 7 (2 digits)")
    # Timoshenko & Gere approximation (ν = 0.25): k = 0.456 + (b/a)², a/b = 2 → 0.706 (energy: upper bound)
    k2 = bk.plate_compression_k(2.0, "SS-F", 0.25)
    check_true("SS-F a/b = 2: exact ≤ approximate 0.706", k2 <= 0.706, f"{k2:.4f}",
               source="Wierzbicki, MIT 2.080 (LibreTexts Sec. 10.3), Timoshenko & Gere approximation")
    check("SS-F a/b = 2: exact ≈ 0.706 (1.5 %)", k2, 0.706, rtol=0.015,
          source="Wierzbicki, MIT 2.080 (LibreTexts Sec. 10.3)")
    for ab in (1.0, 3.0):
        g = bk.flange_k_gerard(ab, 0.3, "SS")
        full = bk.plate_compression_k(ab, "SS-F", 0.3)
        check_true(f"TN 3781 Eq. (18) energy ≥ exact (a/b={ab})", g >= full * (1 - 1e-9), f"{g:.4f} vs {full:.4f}",
                   source="Gerard & Becker 1957, TN 3781 Eq. (18)")
    lam = np.linspace(1.0, 2.5, 3001)
    k19 = min(bk.flange_k_gerard(x, 0.3, "C") for x in lam)
    check("TN 3781 Eq. (19) minimum ≈ Table 7 value 1.28", k19, 1.28, rtol=3e-3,
          source="Gerard & Becker 1957, TN 3781 Eq. (19), Table 7")
    # TN 3784 Eq. (70): long SS flange, ν = 0.3 → σ = 0.388E(t/b)², i.e. k = 0.43
    check("k = 0.43 → σ = 0.388E(t/b)²", bk.plate_critical_stress(0.43, 1.0, 0.3, 1.0, 1.0), 0.388, rtol=2e-3,
          source="Gerard 1957, TN 3784 Eq. (70)")
    check("plate σ = beam.plate_buckling", bk.plate_critical_stress(4.0, E, NU, 0.002, 0.1),
          beam.plate_buckling(E, NU, 0.002, 0.1, 4.0), rtol=1e-12, source="derivation: beam module")
    expect_error("F-F edges are rejected", bk.plate_compression_k, 2.0, "F-F", error=ValueError)
    expect_error("invalid edge type", bk.plate_compression_k, 2.0, "SS-X", error=ValueError)
    expect_error("negative a/b", bk.plate_compression_k, -1.0, error=ValueError)


def test_plate_shear_bending_interaction():
    check("shear SS a/b → ∞: k_s = 5.35", bk.plate_shear_k(1e6, "SS"), 5.35, rtol=1e-9,
          source="Gerard & Becker 1957, TN 3781 Table 7")
    check("shear C a/b → ∞: k_s = 8.98", bk.plate_shear_k(1e6, "C"), 8.98, rtol=1e-9,
          source="Gerard & Becker 1957, TN 3781 Table 7")
    check("shear SS square plate k_s = 9.35", bk.plate_shear_k(1.0, "SS"), 9.35, rtol=1e-12,
          source="Wierzbicki, MIT 2.080 (LibreTexts Sec. 10.3), Timoshenko & Gere")
    check("shear k_s symmetric about the short side", bk.plate_shear_k(0.5), bk.plate_shear_k(2.0), rtol=1e-12,
          source="derivation")
    check("bending SS k_b = 23.9", bk.plate_bending_k("SS"), 23.9, source="Gerard & Becker 1957, TN 3781 Table 7")
    Rc, Rs = 0.4, 0.5
    lam = bk.interaction_load_factor([Rc, Rs], [1, 2])
    check("R_c + R_s² = 1: closed-form MS = general solver", bk.ms_compression_shear(Rc, Rs), lam - 1, rtol=1e-12,
          source="derivation; curve: TN 3781 Table 5")
    check("R_c + R_s² = 1: MS = 0 on the boundary", bk.ms_compression_shear(0.75, 0.5), 0.0, atol=1e-12,
          source="Gerard & Becker 1957, TN 3781 Table 5")
    check("R_b² + R_s² = 1: MS = 0 on the boundary", bk.ms_bending_shear(0.6, 0.8), 0.0, atol=1e-12,
          source="Gerard & Becker 1957, TN 3781 Eq. (58)")
    check("R_c² + R_s² = 1 (inelastic): MS = 0 on the boundary", bk.ms_plastic_compression_shear(0.6, 0.8), 0.0,
          atol=1e-12, source="Gerard & Becker 1957, TN 3781 Table 5")
    check("R_x + R_y = 1: MS", bk.ms_biaxial(0.3, 0.2), 1.0, rtol=1e-12, source="derivation; TN 3781 Table 5")
    expect_error("interaction with all-zero ratios", bk.interaction_load_factor, [0, 0], [1, 2], error=ValueError)


def test_plasticity():
    for d in ("flange_ss", "flange_c", "plate_ss", "plate_c", "short_column", "square_column", "long_column", "shear"):
        check(f"η({d}) = 1 in the elastic range", bk.plasticity_eta(d, E, E, E, 0.33), 1.0, rtol=1e-12,
              source="Gerard & Becker 1957, TN 3781 Table 2 (Et = Es = E)")
    Es, Et = 0.8 * E, 0.3 * E
    sp = Es / E * (0.5 + 0.5 * math.sqrt(0.25 + 0.75 * Et / Es))
    check("TN 3781 plate_ss η = SP-8007 Eq. (22) (no ν correction)", bk.plasticity_eta("plate_ss", Es, Et, E, 0.5),
          sp, rtol=1e-12, source="TN 3781 Table 2 ↔ NASA SP-8007 Eq. (22)")
    nu = 0.5 - 0.8 * (0.5 - 0.3)
    check("η with the ν transition of Eq. (25)", bk.plasticity_eta("flange_ss", Es, Et, E, 0.3),
          0.8 * (1 - 0.09) / (1 - nu ** 2), rtol=1e-12, source="Gerard & Becker 1957, TN 3781 Eq. (25), Table 2")
    F, n = 450e6, 15.0
    se = 1e6
    check("plastic plate: η ≈ 1 for small σ_e", bk.plate_plastic_critical(se, E, F, n), se, rtol=1e-6,
          source="derivation: elastic limit")
    s = bk.plate_plastic_critical(900e6, E, F, n)
    check_true("plastic plate: σ < σ_e and σ < 1.2F", s < 900e6 and s < 1.2 * F, f"{s / 1e6:.1f} MPa",
               source="derivation")


def test_crippling():
    sy, t = 400e6, 0.0016
    # TN 3784 Eqs. (69)+(70) → (71): 0.81·0.388^0.2 = 0.670
    check("TN 3784 Eq. (71) coefficient 0.81·0.388^0.20", 0.81 * 0.388 ** 0.2, 0.670, rtol=1e-3,
          source="Gerard 1957, TN 3784 Eqs. (69)-(71)")
    A = 2 * 0.03 * t                    # equal-leg angle, 2 flanges
    expected = 0.565 * ((2 * t ** 2 / A) * (E / sy) ** 0.5) ** 0.85 * sy
    check("single corner Eq. (67), β_f = 0.565", bk.crippling_gerard("single_corner", sy, E, t, A, count=2), expected,
          rtol=1e-12, source="Gerard 1957, TN 3784 Eq. (67), p. 38")
    Au = (0.04 + 2 * 0.02) * t
    check("two corner Eq. (72), β = 4.00", bk.crippling_gerard("two_corner", sy, E, t, Au),
          4.0 * ((t ** 2 / Au) * (E / sy) ** (1 / 3)) ** 0.75 * sy, rtol=1e-12, source="Gerard 1957, TN 3784 Eq. (72)")
    t2 = 0.0008                         # thin hat section staying below the cut-off (σ_cy)
    Ah = (0.03 + 2 * 0.02 + 2 * 0.012) * t2
    ratio = 1.30 * ((4 * t2 ** 2 / Ah) * (E / sy) ** 0.5) ** 0.85
    check_true("multi-corner example below the cut-off", ratio < 1, f"{ratio:.3f}", source="derivation")
    check("multi corner Eq. (75), β_c = 1.30", bk.crippling_gerard("multi_corner", sy, E, t2, Ah, count=4), ratio * sy,
          rtol=1e-12, source="Gerard 1957, TN 3784 Eq. (75)")
    check("crippling capped at σ_cy (thick section)", bk.crippling_gerard("multi_corner", sy, E, 0.01, 0.0002, count=4),
          sy, source="derivation: cut-off")
    expect_error("crippling with an unknown kind", bk.crippling_gerard, "x", sy, E, t, A, error=KeyError)


def test_cylinder():
    check("SP-8007 Eq. (4): 1/√(3(1−ν²)) ≈ 0.6 (ν = 0.3)", bk.cylinder_axial(1.0, 0.3, 1.0, 1.0, 1.0), 0.6,
          rtol=0.01, source="NASA SP-8007 (1968) Eq. (4)")
    r, t = 0.5, 0.5 / 256
    check("cylinder axial default γ from SP-8007 Eq. (5)", bk.cylinder_axial(E, 0.3, r, t),
          (1 - 0.901 * (1 - math.exp(-1))) * E / math.sqrt(2.73) * t / r, rtol=1e-12,
          source="NASA SP-8007 (1968) Eqs. (4)-(6)")
    check("cylinder bending γ = 1 − 0.731(1 − e^−φ)",
          bk.cylinder_bending(E, 0.3, r, t) / bk.cylinder_axial(E, 0.3, r, t, 1.0),
          1 - 0.731 * (1 - math.exp(-1)), rtol=1e-12, source="NASA SP-8007 (1968) Eqs. (9)-(10)")
    check("SP-8007 Eq. (16) coefficient = 1.04π²/12 (from Eq. 15)", 1.04 * math.pi ** 2 / 12, 0.855, rtol=1e-3,
          source="NASA SP-8007 (1968) Eqs. (15)-(16)")
    L = 1.0
    p = bk.cylinder_external_pressure(E, 0.3, r, t, L)
    # The source's Eq. (17) gives 0.926 for ν = 0.3, Eq. (16) gives 0.918 (0.9 % internal inconsistency): 1 %
    check("SP-8007 Eq. (17) 0.926 (0.9 % internal inconsistency)", p / (E * 0.75 / ((r / t) ** 2.5 * (L / r))), 0.926,
          rtol=0.01, source="NASA SP-8007 (1968) Eq. (17)")
    p_long = bk.cylinder_external_pressure(E, 0.3, r, t, 1e4)
    check("very long cylinder: Eq. (19), γ = 0.90", p_long, 0.9 * E / (4 * 0.91) * (t / r) ** 3, rtol=1e-12,
          source="NASA SP-8007 (1968) Eqs. (19), (21)")
    Lt = 2.0
    tau = bk.cylinder_torsion(E, 0.3, r, t, Lt)
    # Eq. (26) is numerical for ν = 0.3; the general Eq. (25) gives 0.742: 1 % tolerance
    check("SP-8007 Eq. (26): 0.747γ^¾E/((r/t)^(5/4)(L/r)^½)", tau,
          0.747 * 0.67 * E / ((r / t) ** 1.25 * (Lt / r) ** 0.5), rtol=0.01,
          source="NASA SP-8007 (1968) Eqs. (25)-(28)")
    check("Z = L²/(rt)·√(1−ν²)", bk.cylinder_Z(2.0, 0.5, 0.001, 0.3), 4 / 0.0005 * math.sqrt(0.91), rtol=1e-12,
          source="NASA SP-8007 (1968) symbols")
    check("R_c + R_b = 1: MS = 0 on the boundary", bk.ms_cylinder_compression_bending(0.3, 0.7), 0.0, atol=1e-12,
          source="NASA SP-8007 (1968) Eq. (30)")
    expect_error("cylinder torsion rejects γZ < 50", bk.cylinder_torsion, E, 0.3, 0.5, 0.01, 0.1, error=ValueError)
    expect_error("SP-8007 rejects r/t ≥ 1500", bk.cylinder_axial, E, 0.3, 1.5, 0.001, error=ValueError)


def test_lateral_torsional():
    b, h, tf, tw = 0.1, 0.2, 0.008, 0.005
    I = section.i_section_thin(b, h, tf, tw)
    Iy = I.Iy
    Cw = I.sectorial()["Cw"]
    check("section Cw = Iy_flange·h²/4 (thin I)", Cw, 2 * tf * b ** 3 / 12 * h ** 2 / 4, rtol=1e-12,
          source="derivation: section.ThinOpenSection.sectorial")
    G, L = 27e9, 3.0
    M0 = bk.lateral_torsional_moment(E, G, Iy, I.J, 0.0, L)
    check("Cw = 0: M = (π/L)√(EIy·GJ)", M0, math.pi / L * math.sqrt(E * Iy * G * I.J), rtol=1e-12,
          source="derivation: narrow rectangular beam limit")
    M = bk.lateral_torsional_moment(E, G, Iy, I.J, Cw, L)
    check("M_cr² = (π/L)²EIy[GJ + π²ECw/L²]", M ** 2,
          (math.pi / L) ** 2 * E * Iy * (G * I.J + math.pi ** 2 * E * Cw / L ** 2),
          rtol=1e-12, source="derivation: equivalent algebraic form")
    expect_error("LTB rejects a negative Cw", bk.lateral_torsional_moment, E, G, Iy, I.J, -1.0, L, error=ValueError)
