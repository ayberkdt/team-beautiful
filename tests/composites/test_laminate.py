"""Tests of the composites.laminate module.

Source labels:
  "Kaw 2006, Ex. x" → A. K. Kaw, Mechanics of Composite Materials, 2nd ed.; the author's worked-example
      PDFs (kaw.eng.usf.edu/compositesOCW) were downloaded and READ in the session that wrote these tests.
  "Dávila & Camanho 2003" → NASA/TM-2003-212663, READ.
  "Gu & Chen 2019" → Materials 12:3292 (open access), READ.
  "MIL-HDBK-17-3F" → §5.7.1, READ.  "Ley et al. 1999" → NASA/CR-1999-208994, READ.
  "derivation: ..." → not a number from a source, an independent theoretical check.
Tolerances: Kaw's results are printed with 4 significant digits → rtol 1e-3 (rounding margin);
every looser tolerance is justified next to it.
"""
import math

import numpy as np

from aerokit.composites import lamina
from aerokit.composites import laminate as k
from aerokit.materials import library
from aerokit.verification import check, check_true, expect_error

GE = k.KAW_GLASS_EPOXY
R4 = 1e-3  # rounding margin for 4 significant digits
KAW_SIG = np.array([2.0, -3.0, 4.0])  # Kaw Ex. 2.8 load direction σx = 2S, σy = −3S, τxy = 4S


def test_micromechanics():
    lf, mt, Vf = k.KAW_GLASS_FIBER, k.KAW_EPOXY, 0.6
    E1 = k.rom_E1(lf["E"], mt["E"], Vf)
    check("ROM E1 = 52.36 GPa", E1, 52.36e9, rtol=R4, source="Kaw 2006, §3.3 MoM example")
    check("fibre load share Ff/Fc = 0.974", lf["E"] * Vf / E1, 0.974, rtol=R4, source="Kaw 2006, §3.3 MoM example")
    check("inverse ROM E2 = 8.019 GPa", k.inverse_rom(lf["E"], mt["E"], Vf), 8.019e9, rtol=R4,
          source="Kaw 2006, §3.3 MoM example")
    check("ROM ν12 = 0.24", k.rom_nu12(lf["nu"], mt["nu"], Vf), 0.24, rtol=1e-12, source="Kaw 2006, §3.3 MoM example")
    check("inverse ROM G12 = 3.099 GPa", k.inverse_rom(lf["G"], mt["G"], Vf), 3.099e9, rtol=R4,
          source="Kaw 2006, §3.3 MoM example")
    check("Halpin-Tsai E2 (ξ=2) = 15.06 GPa", k.halpin_tsai(lf["E"], mt["E"], Vf, 2), 15.06e9, rtol=R4,
          source="Kaw 2006, §3.3 Halpin-Tsai example, circular fibres / square array")
    check("Halpin-Tsai G12 (ξ=1) = 4.601 GPa", k.halpin_tsai(lf["G"], mt["G"], Vf, 1), 4.601e9, rtol=R4,
          source="Kaw 2006, §3.3 Halpin-Tsai example, circular fibres / square array")
    check("Halpin-Tsai E2 (ξ=2a/b=4) = 20.17 GPa", k.halpin_tsai(lf["E"], mt["E"], Vf, 4), 20.17e9, rtol=R4,
          source="Kaw 2006, §3.3 Halpin-Tsai example, rectangular fibres / hexagonal array")
    # Kaw rounds ξ = √3·ln 2 = 1.2006 to 1.2; the comparison uses the same rounded ξ.
    check("Halpin-Tsai G12 (ξ=1.2) = 4.873 GPa", k.halpin_tsai(lf["G"], mt["G"], Vf, 1.2), 4.873e9, rtol=R4,
          source="Kaw 2006, §3.3 Halpin-Tsai example, rectangular fibres / hexagonal array")
    check("Halpin-Tsai E3 (ξ=1) = 11.84 GPa", k.halpin_tsai(lf["E"], mt["E"], Vf, 1), 11.84e9, rtol=R4,
          source="Kaw 2006, §3.3 Halpin-Tsai example, rectangular fibres / hexagonal array")
    m = k.micromechanics(lf, mt, Vf)
    check("α1 = 6.506e-6 /°C", m["alpha1"], 6.506e-6, rtol=R4, source="Kaw 2006, §3.5 α1 example")
    check("α2 = 34.80e-6 /°C", m["alpha2"], 34.80e-6, rtol=R4, source="Kaw 2006, §3.5 α2 example")
    check("ρc = 1980 kg/m³", m["rho"], 1980, rtol=1e-12, source="Kaw 2006, §3.6 β1 example")
    check("β1 = 0.03536", m["beta1"], 0.03536, rtol=R4, source="Kaw 2006, §3.6 β1 example")
    check("β2 = 0.6994", m["beta2"], 0.6994, rtol=R4, source="Kaw 2006, §3.6 β2 example")
    hib = [(2600, 0.4), (1800, 0.2), (1200, 0.4)]
    check("hybrid density 1880 kg/m³", k.density(hib), 1880, rtol=1e-12, source="Kaw 2006, solution of Problem 3.2")
    Mk = k.mass_fractions(hib)
    check("hybrid glass mass fraction 0.5532", Mk[0], 0.5532, rtol=R4, source="Kaw 2006, solution of Problem 3.2")
    check("hybrid graphite mass fraction 0.1915", Mk[1], 0.1915, rtol=R4, source="Kaw 2006, solution of Problem 3.2")
    # Kaw gives the epoxy mass fraction as 0.4255 (0.4·1200 taken as 800; correct is 480) → sum 1.17 ≠ 1.
    check("hybrid epoxy mass fraction 480/1880 = 0.2553", Mk[2], 480 / 1880, rtol=1e-12,
          source="derivation: ΣM = 1 (the 0.4255 in Kaw Problem 3.2 is an arithmetic error)")
    check("mass fractions sum to 1", sum(Mk), 1.0, rtol=1e-12, source="derivation")
    Mf = 2.595 / 3.697
    rct = k.theoretical_density_from_mass([(2500, Mf), (1200, 1 - Mf)])
    rce = 3.697 / (3.697 - 1.636) * 1000
    check("theoretical density ≈ 1890 kg/m³", rct, 1890, rtol=R4, source="Kaw 2006, solution of Problem 3.3")
    # Kaw rounds Mf to 0.702 and the densities to integers and gets 0.0508; with the raw masses 0.0507 → rtol 0.5%.
    check("void fraction ≈ 0.0508", k.void_ratio(rct, rce), 0.0508, rtol=5e-3, source="Kaw 2006, solution of Problem 3.3")
    # Independent checks
    check("Halpin-Tsai ξ→∞ → rule of mixtures", k.halpin_tsai(85e9, 3.4e9, 0.6, 1e12), E1, rtol=1e-9,
          source="derivation: η→(r−1)/ξ, ξη→r−1")
    check("Halpin-Tsai ξ=0 → inverse rule of mixtures", k.halpin_tsai(85e9, 3.4e9, 0.6, 0.0),
          k.inverse_rom(85e9, 3.4e9, 0.6), rtol=1e-12, source="derivation: ξ=0 → M = Mm/(1 − ηVf), η = 1 − Mm/Mf")
    V = k.volume_fractions([(2600, Mk[0]), (1800, Mk[1]), (1200, Mk[2])])
    check("mass→volume round trip Vgraphite = 0.2", V[1], 0.2, rtol=1e-12, source="derivation: inverse transformation")
    check("Vf = 0 → E2 = Em (both methods)", k.halpin_tsai(85e9, 3.4e9, 0.0, 2), 3.4e9, rtol=1e-12,
          source="derivation: limit")
    expect_error("Vf > 1 is rejected", k.rom_E1, 85e9, 3.4e9, 1.2, error=ValueError)
    expect_error("ξ < 0 is rejected", k.halpin_tsai, 85e9, 3.4e9, 0.5, -1, error=ValueError)
    expect_error("ΣV ≠ 1 is rejected", k.density, [(2500, 0.5), (1200, 0.4)], error=ValueError)


def test_layer():
    S = k.S_matrix(GE["E1"], GE["E2"], GE["nu12"], GE["G12"])
    for (i, j), v in {(0, 0): 2.591e-11, (0, 1): -6.736e-12, (2, 2): 2.415e-10}.items():
        check(f"S{i + 1}{j + 1 if j < 2 else 6} glass/epoxy", S[i, j], v, rtol=R4, source="Kaw 2006, Ex. §2.4")
    # Kaw prints S22 = 1.206e-10; 1/8.27e9 = 1.2092e-10 (rounding drift in the example, 0.27%). Kaw's own
    # ε2 = −3.762e-4 is consistent with the correct value (1.209e-10) → S22 is tested as 1/E2.
    check("S22 = 1/E2 = 1.209e-10", S[1, 1], 1.209e-10, rtol=R4, source="Kaw 2006, Ex. §2.4 (printed 1.206e-10 is off)")
    Q = k.Q_material(GE)
    # The §2.4 example gives Q11 = 38.66 GPa (typo ν21 = 0.0057); §4.3/4.4/5.3 use the correct 39.17 GPa.
    check("Q11 = 39.17 GPa", Q[0, 0], 39.17e9, rtol=R4, source="Kaw 2006, Ex. §4.3 (the 38.66 in §2.4 is a typo)")
    check("Q12 = 2.182 GPa", Q[0, 1], 2.182e9, rtol=R4, source="Kaw 2006, Ex. §4.3")
    check("Q22 = 8.392 GPa", Q[1, 1], 8.392e9, rtol=R4, source="Kaw 2006, Ex. §4.3")
    e12 = S @ np.array([2e6, -3e6, 4e6])
    for name, v, b in zip(("ε1", "ε2", "γ12"), e12, (7.202e-5, -3.762e-4, 9.662e-4)):
        check(f"local strain {name}", v, b, rtol=R4, source="Kaw 2006, Ex. §2.4")
    Sb = k.Sbar(S, 30)
    expected = {(0, 0): 6.489e-11, (0, 1): -2.197e-11, (0, 2): -5.873e-11, (1, 1): 1.124e-10,
                (1, 2): -2.355e-11, (2, 2): 1.806e-10}
    for (i, j), v in expected.items():
        check(f"S̄{'126'[i]}{'126'[j]}(30°)", Sb[i, j], v, rtol=R4, source="Kaw 2006, Ex. §2.5")
    Qb = lamina.Qbar(Q, 30)
    for (i, j), v in {(0, 0): 2.648e10, (0, 1): 7.176e9, (0, 2): 9.546e9, (1, 1): 1.109e10, (2, 2): 9.134e9}.items():
        check(f"Q̄{'126'[i]}{'126'[j]}(30°)", Qb[i, j], v, rtol=R4, source="Kaw 2006, Ex. §2.5")
    check("S̄ = Q̄⁻¹ (30°)", float(np.max(np.abs(Sb @ Qb - np.eye(3)))), 0.0, atol=1e-12,
          source="derivation: two independent transformation paths")
    exy = Sb @ np.array([2e6, -3e6, 4e6])
    for name, v, b in zip(("εx", "εy", "γxy"), exy, (-3.923e-5, -4.753e-4, 6.756e-4)):
        check(f"global strain {name} (30°)", v, b, rtol=R4, source="Kaw 2006, Ex. §2.5")
    s12 = lamina.T_stress(30) @ np.array([2e6, -3e6, 4e6])
    check("local σ1 (30°) = 4.214 MPa", s12[0], 4.214e6, rtol=R4, source="Kaw 2006, Ex. §2.5")
    check("local τ12 (30°) = −0.1651 MPa", s12[2], -1.651e5, rtol=R4, source="Kaw 2006, Ex. §2.5")
    e = k.axis_off_constants(GE["E1"], GE["E2"], GE["nu12"], GE["G12"], 30)
    for name, v in (("Ex", 15.41e9), ("Ey", 8.897e9), ("Gxy", 5.537e9), ("nuxy", 0.3386), ("mx", 2.267), ("my", 0.9090)):
        check(f"30° glass/epoxy {name}", e[name], v, rtol=R4, source="Kaw 2006, Ex. §2.6")
    B = k.KAW_BORON_EPOXY
    eb = k.axis_off_constants(B["E1"], B["E2"], B["nu12"], B["G12"], 45)
    check("boron/epoxy Ex(45°) = 2.463 Msi", eb["Ex"] / k.MSI, 2.463, rtol=R4, source="Kaw 2006, solution of Problem 2.29")
    check("boron/epoxy νxy(45°) = 0.5185 (maximum)", eb["nuxy"], 0.5185, rtol=R4,
          source="Kaw 2006, solution of Problem 2.29")
    # Kaw's solution says "νxy is largest at 45°"; a scan gives 0.594 > 0.5185 at 25° → the stationary-point
    # solution is wrong (its νxy(0°) = 0.0191 also contradicts ν12 = 0.23). The independent truth is tested here.
    nus = [k.axis_off_constants(B["E1"], B["E2"], B["nu12"], B["G12"], t)["nuxy"] for t in range(0, 91, 5)]
    check_true("boron/epoxy νxy peaks at 25° (contradicts Kaw's 45° claim)", int(np.argmax(nus)) * 5 == 25,
               f"argmax {int(np.argmax(nus)) * 5}°", source="derivation: angle scan; Kaw Problem 2.29 result is wrong")
    check("νxy(0°) = ν12", nus[0], B["nu12"], rtol=1e-12, source="derivation")
    # Independent checks
    iso = [k.axis_off_constants(70e9, 70e9, 0.3, 70e9 / 2.6, t) for t in (0, 17, 45, 73)]
    check("isotropic limit: Ex(θ) = E", max(abs(x["Ex"] - 70e9) for x in iso), 0.0, atol=1e-3,
          source="derivation: E1 = E2, G = E/2(1+ν) → independent of θ")
    check("isotropic limit: mx = 0", max(abs(x["mx"]) for x in iso), 0.0, atol=1e-9, source="derivation")
    check("0° ply: mx = 0", k.axis_off_constants(38.6e9, 8.27e9, 0.26, 4.14e9, 0)["mx"], 0.0, atol=1e-12,
          source="derivation: S̄16(0°) = 0")
    U = [lamina.Qbar(Q, t) for t in (0, 25, 60, 90)]
    check("invariant Q̄11 + Q̄22 + 2Q̄12 independent of angle",
          max(abs((u[0, 0] + u[1, 1] + 2 * u[0, 1]) - (Q[0, 0] + Q[1, 1] + 2 * Q[0, 1])) for u in U), 0.0, atol=1e-2,
          source="derivation: Tsai-Pagano invariants")
    check("invariant Q̄66 − Q̄12 independent of angle", max(abs((u[2, 2] - u[0, 1]) - (Q[2, 2] - Q[0, 1])) for u in U),
          0.0, atol=1e-2, source="derivation: Tsai-Pagano invariants")
    U2, U3 = (Q[0, 0] - Q[1, 1]) / 2, (Q[0, 0] + Q[1, 1] - 2 * Q[0, 1] - 4 * Q[2, 2]) / 8
    t = math.radians(25)
    check("Q̄16 = (U2/2) sin2θ + U3 sin4θ", U[1][0, 2], U2 / 2 * math.sin(2 * t) + U3 * math.sin(4 * t), rtol=1e-12,
          source="derivation: intermediate step ¼(Q11−Q22)sin2θ of Kaw's 'invariant' example (trailing ½ is a typo)")
    expect_error("|ν12| ≥ √(E1/E2) is rejected", k.S_matrix, 10e9, 10e9, 1.5, 4e9, error=ValueError)
    expect_error("negative modulus is rejected", k.S_matrix, -10e9, 10e9, 0.3, 4e9, error=ValueError)


def test_laminate():
    ply = k.layers(GE, [(30, 5e-3), (-45, 5e-3), (-60, 5e-3)])
    A, B, D, z = k.abd_matrix(ply)
    for name, X, (i, j), v in (("A11", A, (0, 0), 2.735e8), ("A12", A, (0, 1), 1.160e8), ("A16", A, (0, 2), -9.636e6),
                               ("A26", A, (1, 2), -6.730e7), ("A66", A, (2, 2), 1.453e8), ("B11", B, (0, 0), -3.847e5),
                               ("B16", B, (0, 2), -3.332e5), ("B22", B, (1, 1), 3.847e5), ("D11", D, (0, 0), 5.266e3),
                               ("D12", D, (0, 1), 2.036e3), ("D16", D, (0, 2), 7.008e2), ("D26", D, (1, 2), -8.611e2),
                               ("D66", D, (2, 2), 2.586e3)):
        check(f"[30/−45/−60] {name}", X[i, j], v, rtol=R4, source="Kaw 2006, Ex. §4.3")
    r = k.laminate_analysis(ply, N=(1500, 0, 0), M=(0, 1500, 0))
    for name, v, b in zip(("ε0x", "ε0y", "γ0xy", "κx", "κy", "κxy"), np.concatenate([r["eps0"], r["kappa"]]),
                          (1.624e-4, -3.532e-4, 4.908e-4, -1.403e-1, 4.210e-1, 1.536e-1)):
        check(f"[30/−45/−60] {name}", v, b, rtol=R4, source="Kaw 2006, Ex. §4.3")
    p = r["layers"][1]["points"]["lower"]  # Kaw's "top" face of the −45° ply is z = −2.5 mm (Kaw's z points down)
    check("−45° face z = −2.5 mm", p["z"], -0.0025, rtol=1e-12, source="Kaw 2006, Ex. §4.3")
    for name, v, b in zip(("σx", "σy", "τxy"), p["sig_xy"], (-4.466e6, -2.035e7, 8.022e6)):
        check(f"−45° face global {name}", v, b, rtol=2e-3, source="Kaw 2006, Ex. §4.3")  # Kaw rounds intermediate steps
    for name, v, b in zip(("σ1", "σ2", "τ12"), p["sig12"], (-2.043e7, -4.388e6, 7.944e6)):
        check(f"−45° face local {name}", v, b, rtol=2e-3, source="Kaw 2006, Ex. §4.3")
    # [45/60]s
    ply2 = k.layers(GE, [(45, 5e-3), (60, 5e-3), (60, 5e-3), (45, 5e-3)])
    L = k.laminate_constants(ply2)
    check("[45/60]s A11 = 2.821e8", L["A"][0, 0], 2.821e8, rtol=R4, source="Kaw 2006, Ex. §4.4")
    check("[45/60]s A26 = 1.724e8", L["A"][1, 2], 1.724e8, rtol=R4, source="Kaw 2006, Ex. §4.4")
    check("[45/60]s a*11 = 4.923e-9", L["a"][0, 0], 4.923e-9, rtol=R4, source="Kaw 2006, Ex. §4.4")
    for name, v in (("Ex", 10.16e9), ("Ey", 13.48e9), ("Gxy", 5.966e9), ("nuxy", 0.2123), ("nuyx", 0.2818),
                    ("Efy", 11.44e9), ("Gfxy", 6.180e9), ("nufxy", 0.2622), ("nufyx", 0.2826)):
        check(f"[45/60]s {name}", L[name], v, rtol=R4, source="Kaw 2006, Ex. §4.4")
    check("[45/60]s D11 = 1.091e4", L["D"][0, 0], 1.091e4, rtol=R4, source="Kaw 2006, Ex. §4.4")
    check("[45/60]s d*11 = 1.413e-4", L["d"][0, 0], 1.413e-4, rtol=R4, source="Kaw 2006, Ex. §4.4")
    # Kaw prints Ef_x = 10.65 GPa, but his own d*11 = 1.413e-4 gives 12/(h³d*11) = 10.62 GPa: an arithmetic
    # slip in the example. The formula is tested with Kaw's d*11 value.
    check("[45/60]s Ef_x = 12/(h³·1.413e-4)", L["Efx"], 12 / (0.02 ** 3 * 1.413e-4), rtol=R4,
          source="Kaw 2006, Ex. §4.4 (printed 10.65 GPa is an arithmetic error)")
    # [90/0/90]
    ply3 = k.layers(GE, [(90, 5e-3), (0, 5e-3), (90, 5e-3)])
    L3 = k.laminate_constants(ply3)
    for name, (i, j), v in (("A11", (0, 0), 2.798e8), ("A12", (0, 1), 3.273e7), ("A22", (1, 1), 4.336e8),
                            ("A66", (2, 2), 6.210e7)):
        check(f"[90/0/90] {name}", L3["A"][i, j], v, rtol=R4, source="Kaw 2006, Ex. §5.3")
    e = k.laminate_analysis(ply3, N=(0, 1, 0))["eps0"]
    check("[90/0/90] Ny=1 → ε0x = −2.722e-10", e[0], -2.722e-10, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check("[90/0/90] Ny=1 → ε0y = 2.327e-9", e[1], 2.327e-9, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check("[90/0/90] Ey = 28.65 GPa (initial slope)", L3["Ey"], 28.65e9, rtol=R4, source="Kaw 2006, §5.3 slide (slope)")
    # Independent checks
    A0, B0, D0, _ = lamina.abd(k.Q_material(GE), [(30, 5e-3), (-45, 5e-3), (-60, 5e-3)])
    check("abd_matrix = lamina.abd (single material)", float(np.max(np.abs(D0 - D))), 0.0, atol=1e-9,
          source="derivation: two implementations")
    T = k.abd_inverse(A, B, D)
    check("abd′·ABD = I", float(np.max(np.abs(T["full"] @ np.block([[A, B], [B, D]]) - np.eye(6)))), 0.0, atol=1e-9,
          source="derivation")
    check("abd′ symmetric: c = bᵀ", float(np.max(np.abs(T["c"] - T["b"].T))), 0.0, atol=1e-18, source="derivation")
    im7 = library.find("IM7-8552")
    t = im7["t_layer"]
    qi = k.layers(im7, [(0, t), (45, t), (-45, t), (90, t), (90, t), (-45, t), (45, t), (0, t)])
    Lq = k.laminate_constants(qi)
    check("quasi-isotropic: Ex = Ey", Lq["Ey"], Lq["Ex"], rtol=1e-10,
          source="derivation: [0/±45/90]s is in-plane isotropic")
    check("quasi-isotropic: Gxy = Ex/(2(1+νxy))", Lq["Gxy"], Lq["Ex"] / (2 * (1 + Lq["nuxy"])), rtol=1e-10,
          source="derivation: in-plane isotropy")
    check("symmetric: bending-free Ex = A⁻¹ Ex", k.laminate_constants(qi, bending_free=True)["Ex"], Lq["Ex"],
          rtol=1e-12, source="derivation: B = 0 → full inverse is block diagonal")
    s = k.symmetry_balance(qi)
    check_true("[0/±45/90]s symmetric, balanced, B = 0, A16 = 0", s["symmetric"] and s["balanced"] and s["B_zero"]
               and s["A16_A26_zero"], str(s), source="derivation")
    check_true("[0/±45/90]s is NOT specially orthotropic (D16 ≠ 0)", not s["specially_orthotropic"], str(s),
               source="derivation")
    s2 = k.symmetry_balance(ply)
    check_true("[30/−45/−60] unsymmetric and B ≠ 0", not s2["symmetric"] and not s2["B_zero"], str(s2),
               source="derivation")
    s3 = k.symmetry_balance(ply2)
    check_true("[45/60]s symmetric but unbalanced (A16 ≠ 0)", s3["symmetric"] and not s3["balanced"]
               and not s3["A16_A26_zero"], str(s3), source="derivation")
    expect_error("empty sequence is rejected", k.layers, GE, [], error=ValueError)
    expect_error("zero thickness is rejected", k.layers, GE, [(0, 0.0)], error=ValueError)


def test_hygrothermal():
    b = k.alpha_global(0.0, 0.6, 60)
    check("βx(60°) = 0.45", b[0], 0.45, rtol=1e-12, source="Kaw 2006, 'beta angle ply' example")
    check("βy(60°) = 0.15", b[1], 0.15, rtol=1e-12, source="Kaw 2006, 'beta angle ply' example")
    check("βxy(60°) = −0.5196", b[2], -0.5196, rtol=R4, source="Kaw 2006, 'beta angle ply' example")
    a45, a60 = k.alpha_global(8.6e-6, 22.1e-6, 45), k.alpha_global(8.6e-6, 22.1e-6, 60)
    check("αx(45°) = 1.535e-5", a45[0], 1.535e-5, rtol=R4, source="Kaw 2006, §4.5 thermal load slide")
    check("αxy(45°) = −1.350e-5", a45[2], -1.350e-5, rtol=R4, source="Kaw 2006, §4.5 thermal load slide")
    for name, v, bb in zip(("αx", "αy", "αxy"), a60, (1.873e-5, 1.198e-5, -1.169e-5)):
        check(f"{name}(60°)", v, bb, rtol=R4, source="Kaw 2006, §4.5 thermal load slide")
    ply = k.layers(GE, [(45, 5e-3), (60, 5e-3)])
    r = k.laminate_analysis(ply, dT=50)
    for name, v, bb in zip(("NxT", "NyT", "NxyT", "MxT", "MyT", "MxyT"), np.concatenate([r["NT"], r["MT"]]),
                           (1.360e5, 1.586e5, 4.218e4, -28.26, 28.26, -7.571)):
        check(f"[45/60] ΔT=50 {name}", v, bb, rtol=R4, source="Kaw 2006, §4.5 thermal load slide")
    for name, v, bb in zip(("ε0x", "ε0y", "γ0xy", "κx", "κy", "κxy"), np.concatenate([r["eps0"], r["kappa"]]),
                           (8.500e-4, 6.802e-4, -6.336e-4, 2.480e-2, -2.480e-2, 1.329e-2)):
        check(f"[45/60] ΔT=50 {name}", v, bb, rtol=R4, source="Kaw 2006, §4.5 thermal load slide")
    p = r["layers"][1]["points"]["upper"]  # Kaw's "bottom face of the 60° ply" is z = +5 mm (Kaw's z points down)
    for name, v, bb in zip(("σx", "σy", "τxy"), p["sig_xy"], (1.788e5, -6.900e5, -1.048e5)):
        check(f"[45/60] 60° face residual {name}", v, bb, rtol=2e-3,  # Kaw rounds the mechanical strain to 3 digits
              source="Kaw 2006, §4.5 thermal load slide")
    # Independent checks
    single = k.laminate_analysis(k.layers(GE, [(30, 1e-3)]), dT=-120)
    check("free single ply: stress 0",
          max(float(np.max(np.abs(n["sig_xy"]))) for n in single["layers"][0]["points"].values()),
          0.0, atol=1e-3, source="derivation: an unconstrained ply expands freely")
    check("free single ply: ε0 = α_xy ΔT",
          float(np.max(np.abs(single["eps0"] - k.alpha_global(8.6e-6, 22.1e-6, 30) * -120))),
          0.0, atol=1e-15, source="derivation")
    cp = k.layers(GE, [(0, 1e-3), (90, 1e-3), (90, 1e-3), (0, 1e-3)])
    rc = k.laminate_analysis(cp, dT=-150)
    check("symmetric cross-ply under ΔT: κ = 0", float(np.max(np.abs(rc["kappa"]))), 0.0, atol=1e-12,
          source="derivation: B = 0, M^T = 0")
    N_residual = sum(k_["points"]["middle"]["sig_xy"] * 1e-3 for k_ in rc["layers"])
    check("residual stresses self-equilibrated: Σσx·t = 0", N_residual[0], 0.0, atol=1e-6,
          source="derivation: no external load")
    check_true("on cool-down the 0° ply has σ2 > 0 (matrix tension)", rc["layers"][0]["points"]["middle"]["sig12"][1] > 0,
               source="derivation: α2 > α1, cross-ply constraint")
    r1 = k.laminate_analysis(ply, dT=50)
    r2 = k.laminate_analysis(ply, N=(1e4, -2e3, 500), M=(3, 0, -1))
    r3 = k.laminate_analysis(ply, N=(1e4, -2e3, 500), M=(3, 0, -1), dT=50)
    check("mechanical + thermal superposition", float(np.max(np.abs(r3["layers"][1]["points"]["lower"]["sig12"]
                                                                   - r1["layers"][1]["points"]["lower"]["sig12"]
                                                                   - r2["layers"][1]["points"]["lower"]["sig12"]))),
          0.0, atol=1e-6, source="derivation: linear CLT")
    # Strength ratio with residual stress: index is exactly 1 at R
    s0 = rc["layers"][1]["points"]["middle"]["sig12"]
    s1 = k.laminate_analysis(cp, N=(0, 1, 0))["layers"][1]["points"]["middle"]["sig12"]
    R = k.strength_ratio("tsai_wu", s1, GE, s0)
    check("thermal + mechanical: Tsai-Wu index(σ0 + Rσ) = 1", k.tsai_wu(s0 + R * s1, GE)["index"], 1.0, rtol=1e-9,
          source="derivation: definition of the root")
    expect_error("ΔT on a material without alpha raises", k.laminate_analysis,
                 k.layers({"E1": 1e11, "E2": 1e10, "nu12": 0.3, "G12": 5e9}, [(0, 1e-3)]), dT=10, error=KeyError)


def test_criteria():
    s = lamina.T_stress(30) @ KAW_SIG  # local stresses per S = 1 Pa
    check("max. stress S = 22.63 MPa", k.max_stress(s, GE)["R"], 22.63e6, rtol=R4,
          source="Kaw 2006, Ex. §2.8 maximum stress")
    check("max. strain S = 21.66 MPa", k.max_strain(s, GE)["R"], 21.66e6, rtol=R4,
          source="Kaw 2006, Ex. §2.8 maximum strain")
    check("Tsai-Hill S = 5.941 MPa", k.tsai_hill(s, GE, signed=False)["R"], 5.941e6, rtol=R4,
          source="Kaw 2006, Ex. §2.8 Tsai-Hill")
    check("modified Tsai-Hill S = 22.18 MPa", k.tsai_hill(s, GE, signed=True)["R"], 22.18e6, rtol=R4,
          source="Kaw 2006, Ex. §2.8 Tsai-Hill")
    check("Tsai-Wu S = 21.82 MPa", k.tsai_wu(s, GE)["R"], 21.82e6, rtol=R4, source="Kaw 2006, Ex. §2.8 Tsai-Wu")
    sp = lamina.T_stress(60) @ np.array([0, 0, 1.0])
    check("60° off-axis +τ strength 136.2 MPa", k.max_stress(sp, GE)["R"], 136.2e6, rtol=R4,
          source="Kaw 2006, 'off-axis shear strength' example")
    check("60° off-axis −τ strength 35.80 MPa", k.max_stress(-sp, GE)["R"], 35.80e6, rtol=R4,
          source="Kaw 2006, 'off-axis shear strength' example")
    check("[90/0/90] 90° ply Tsai-Wu SR 1.004e7", k.tsai_wu((90.53, 2.792, 0), GE)["R"], 1.004e7, rtol=R4,
          source="Kaw 2006, Ex. §5.3")
    check("[90/0/90] 0° ply Tsai-Wu SR 1.622e6", k.tsai_wu((-5.584, 18.93, 0), GE)["R"], 1.622e6, rtol=R4,
          source="Kaw 2006, Ex. §5.3")
    check("[90/0/90] 90° ply max. strain SR 1.183e7", k.max_strain((90.53, 2.792, 0), GE)["R"], 1.183e7,
          rtol=R4, source="Kaw 2006, §5.3 slide table")
    check("[90/0/90] 0° ply max. strain SR 1.611e6", k.max_strain((-5.584, 18.93, 0), GE)["R"], 1.611e6,
          rtol=R4, source="Kaw 2006, §5.3 slide table")
    # In uniaxial cases every criterion returns the strength exactly
    single = {"σ1 = Xt": ((1.0, 0, 0), GE["Xt"]), "σ1 = −Xc": ((-1.0, 0, 0), GE["Xc"]),
              "σ2 = Yt": ((0, 1.0, 0), GE["Yt"]), "σ2 = −Yc": ((0, -1.0, 0), GE["Yc"]),
              "τ12 = S": ((0, 0, 1.0), GE["S12"])}
    for name_c in ("max_stress", "max_strain", "tsai_hill", "hoffman", "tsai_wu", "hashin", "puck", "larc03"):
        f = k.CRITERIA[name_c]
        errors = []
        for name, (sg, expected) in single.items():
            if name_c == "max_strain" and name == "σ1 = −Xc":
                continue  # Poisson: ε2 = ν12·Xc/E1 > Yt/E2 → max. strain fails first in transverse tension (below)
            if name_c == "tsai_hill":
                R = f(sg, GE, signed=True)["R"]
            else:
                R = f(sg, GE)["R"]
            errors.append(abs(R / expected - 1))
        check(f"{name_c}: R = strength/stress in the 5 uniaxial cases", max(errors), 0.0, atol=1e-7,
              source="derivation: the criteria reduce to the strengths in uniaxial stress")
    mg = k.max_strain((-1.0, 0, 0), GE)
    check("max. strain, σ1 compression fails by Poisson transverse tension: R = (Yt/E2)·E1/ν12", mg["R"],
          GE["Yt"] / GE["E2"] * GE["E1"] / GE["nu12"], rtol=1e-12, source="derivation: ε2 = −ν12σ1/E1")
    check_true("max. strain mode is 'matrix' in this case", mg["mode"] == "matrix", mg["mode"], source="derivation")
    # Tsai-Wu scaling and independent root finding
    sg = np.array([310e6, -45e6, 38e6])
    tw = k.tsai_wu(sg, GE)
    check("Tsai-Wu index(R·σ) = 1", k.tsai_wu(tw["R"] * sg, GE)["index"], 1.0, rtol=1e-12, source="derivation")
    check("Tsai-Wu closed-form R = bisection R", k._general_R(lambda x: k.tsai_wu(x, GE)["index"], sg, np.zeros(3)),
          tw["R"], rtol=1e-10, source="derivation: independent numerical path")
    hs = k.hashin(sg, GE, ST=0.378 * GE["Yc"])
    check("Hashin (with linear term) closed-form R = bisection R",
          k._general_R(lambda x: k.hashin(x, GE, ST=0.378 * GE["Yc"])["index"], sg, np.zeros(3)), hs["R"], rtol=1e-10,
          source="derivation: independent numerical path")
    check("Hoffman = Tsai-Wu(F12 = −1/(2XtXc))", k.hoffman(sg, GE)["index"],
          k.tsai_wu(sg, GE, F12=-1 / (2 * GE["Xt"] * GE["Xc"]))["index"], rtol=1e-14, source="derivation")
    # Hashin
    st = np.array([0, -80e6, 30e6])
    h73 = (st[1] / GE["Yc"]) ** 2 + (st[2] / GE["S12"]) ** 2
    check("Hashin 1980 matrix compression, S_T = Yc/2 → 1973 form", k.hashin(st, GE)["matrix"]["index"], h73,
          rtol=1e-12, source="Dávila & Camanho 2003, p. 7")
    check("Hashin σ2 = −Yc gives R = 1 for any S_T", k.hashin((0, -GE["Yc"], 0), GE, ST=0.378 * GE["Yc"])["R"], 1.0,
          rtol=1e-12, source="derivation: (Yc/2ST)² − [(Yc/2ST)² − 1] = 1")
    check_true("Hashin mode label: fibre compression", k.hashin((-700e6, 5e6, 1e6), GE)["mode"] == "fiber_compression",
               source="derivation")
    # Puck
    pp = k.puck_parameters({"Xt": 1, "Xc": 1, "Yt": 62.3e6, "Yc": 199.8e6, "S12": 92.3e6}, "CFRP")
    check("Puck p⊥⊥(−) = 0.258 (IM7/8552)", pp["p_dd"], 0.258, rtol=2e-3,  # the source gives 3 digits
          source="Gu & Chen 2019, Table 1 and §3.1 (Eq. 28)")
    check("Puck R⊥⊥A = Yc/(2(1+p⊥⊥))", pp["R_AA"], 199.8e6 / (2 * (1 + pp["p_dd"])), rtol=1e-12,
          source="derivation: identity of the Altair and Gu & Chen Eq. 26 forms")
    p = k.puck_parameters(GE, "GFRP")
    sB = k.puck((0, -p["R_AA"], p["tau21c"] * (1 + 1e-12)), GE, "GFRP")  # |σ2/τ| slightly smaller → B
    sC = k.puck((0, -p["R_AA"], p["tau21c"] * (1 - 1e-12)), GE, "GFRP")  # |σ2/τ| slightly larger → C
    check("Puck B/C turning point: mode B fE = 1", sB["fE_IFF"], 1.0, rtol=1e-9,
          source="derivation: (−R⊥⊥A, τ21c) lies on the fracture envelope")
    check("Puck B/C turning point: mode C fE = 1", sC["fE_IFF"], 1.0, rtol=1e-9, source="derivation")
    check_true("Puck modes B and C at the turning point", sB["mode"] == "IFF-B" and sC["mode"] == "IFF-C",
               f"{sB['mode']}/{sC['mode']}", source="derivation")
    a_ = k.puck((0, 1e-9, 40e6), GE)["fE_IFF"]
    b_ = k.puck((0, -1e-9, 40e6), GE)["fE_IFF"]
    check("Puck A/B continuity at σ2 = 0 (|τ|/S)", a_, b_, rtol=1e-9, source="derivation")
    check("Puck FF = σ1/Xt", k.puck((800e6, 0, 0), GE)["fE_FF"], 800e6 / GE["Xt"], rtol=1e-14, source="derivation")
    pz = k.puck((0, -20e6, 50e6), GE)
    check("Puck fE homogeneous of degree 1: fE(Rσ) = 1", k.puck(pz["R"] * np.array([0, -20e6, 50e6]), GE)["index"],
          1.0, rtol=1e-12, source="derivation")
    check_true("Puck: mild compression + shear → mode B, fE < |τ|/S (friction)",
               pz["mode"] == "IFF-B" and pz["fE_IFF"] < 50e6 / GE["S12"],
               pz["mode"], source="derivation: p⊥∥(−)σ2 < 0 term")
    pc = k.puck((0, -60e6, 25e6), GE)
    check_true("Puck: dominant compression → mode C", pc["mode"] == "IFF-C", pc["mode"],
               source="derivation: |σ2/τ| > R⊥⊥A/τ21c")
    # LaRC03
    t300 = {"E1": 138e9, "E2": 11e9, "nu12": 0.28, "G12": 5.5e9,  # elastic/Xt/Yt do not affect these three quantities (placeholders)
            "Xt": 1500e6, "Xc": 900e6, "Yt": 27e6, "Yc": 200e6, "S12": 80e6}
    lp = k.larc03_parameters(t300, 53.0)
    check("LaRC03 ηL = 0.304 (T300/914C)", lp["etaL"], 0.304, rtol=2e-3, source="Dávila & Camanho 2003, p. 16")
    # φC = 5.3° is given to one decimal → rounding margin ±0.05° (≈1%)
    check("LaRC03 φC = 5.3° (T300/914C)", math.degrees(lp["phiC"]), 5.3, rtol=1e-2, source="Dávila & Camanho 2003, p. 16")
    phi = lp["phiC"]
    check("LaRC03 Eq. 37 k = 1.07", 1 / (1 - phi ** 2 - 2 * lp["etaL"] * phi), 1.07, rtol=5e-3,
          source="Dávila & Camanho 2003, p. 16 (two digits → rtol 0.5%)")
    # The source writes 0.378 for α0 = 53°; its own Eq. 10 gives 0.3768 at 53.000° (0.33% difference; rounding in
    # the source). Eq. 10 is used, with a tolerance covering this difference: rtol 4e-3.
    check("LaRC03 S_T ≈ 0.378·Yc (α0 = 53°)", lp["ST"] / t300["Yc"], 0.378, rtol=4e-3,
          source="Dávila & Camanho 2003, p. 7, Fig. 2")
    check("LaRC03 ηT(51°) ≈ 0.21", k.larc03_parameters(t300, 51.0)["etaT"], 0.21, atol=5e-3,
          source="Dávila & Camanho 2003, p. 6 (0.21 ≤ ηT ≤ 0.36)")
    check("LaRC03 ηT(55°) ≈ 0.36", k.larc03_parameters(t300, 55.0)["etaT"], 0.36, atol=5e-3,
          source="Dávila & Camanho 2003, p. 6 (0.21 ≤ ηT ≤ 0.36)")
    check("LaRC03 σ11 = −Xc → kink FI = 1", k.larc03((-t300["Xc"], 0, 0), t300)["index"], 1.0, rtol=1e-12,
          source="derivation: definition of φC (Eq. 30)")
    r1 = k.larc03((0, -t300["Yc"], 0), t300)
    check("LaRC03 σ22 = −Yc → FI = 1 (α = α0)", r1["index"], 1.0, rtol=1e-9,
          source="derivation: definition of ηT, S_T (Eqs. 7-10)")
    check_true("LaRC03 σ22 = −Yc is mode #1", r1["mode"].startswith("LaRC03#1"), r1["mode"], source="derivation")
    rr = k.larc03((0, -100e6, 60e6), t300)
    check_true("LaRC03 compression raises the shear strength (R > Hashin 1973 R)",
               rr["R"] > k.hashin((0, -100e6, 60e6), t300)["R"],
               f"{rr['R']:.4g}", source="Dávila & Camanho 2003, pp. 2-3 (σ22 < 0 strengthens against shear)")
    expect_error("negative strength is rejected", k.tsai_wu, (1, 0, 0), dict(GE, Xt=-1), error=ValueError)
    expect_error("F12² ≥ F11F22 is rejected", k.tsai_wu, (1, 0, 0), GE, F12_ply=-1.2, error=ValueError)
    expect_error("Puck invalid kind", k.puck, (0, 1, 0), GE, "wood", error=ValueError)
    expect_error("LaRC03 α0 ≤ 45° is rejected", k.larc03_parameters, t300, 40.0, error=ValueError)


def test_progressive_failure():
    ply = k.layers(GE, [(90, 5e-3), (0, 5e-3), (90, 5e-3)])
    r = k.progressive_failure(ply, [0, 1, 0, 0, 0, 0], criterion="tsai_wu", reduction="full")
    check("[90/0/90] FPF Ny = 1.622e6 N/m", r["fpf"], 1.622e6, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check("[90/0/90] LPF Ny = 1.062e7 N/m", r["lpf"], 1.062e7, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check_true("ply failed at FPF is the 0° ply (index 1)", r["history"][0]["layers"] == [1],
               str(r["history"][0]["layers"]), source="Kaw 2006, Ex. §5.3")
    check("εy at FPF = 0.003774", r["history"][0]["eps0"][1], 0.003774, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check("εy at LPF = 0.02752", r["history"][1]["eps0"][1], 0.02752, rtol=R4, source="Kaw 2006, Ex. §5.3")
    check("stiffness ratio after FPF 25.73/28.65", r["history"][0]["stiffness_ratio"], 25.73 / 28.65, rtol=R4,
          source="Kaw 2006, §5.3 slide (slopes 28.65 → 25.73 GPa)")
    rm = k.progressive_failure(ply, [0, 1, 0, 0, 0, 0], criterion="tsai_wu", reduction="mode")
    load = [g["load_factor"] for g in rm["history"]]
    check_true("mode-dependent reduction: monotonic load history", all(b >= a for a, b in zip(load, load[1:])),
               str(load), source="derivation")
    check_true("mode-dependent reduction: collapse detected", rm["collapse"], source="derivation")
    check("mode-dependent reduction: LPF = 90° fibre fracture (σ1 = Xt, uniaxial)", rm["lpf"], 1.062e7, rtol=R4,
          source="derivation: 0° matrix-failed, Ny carried only by the 90° fibres → Ny = Xt·2t")
    im7 = library.find("IM7-8552")
    t = im7["t_layer"]
    qi = k.layers(im7, [(0, t), (45, t), (-45, t), (90, t), (90, t), (-45, t), (45, t), (0, t)])
    for kr in ("tsai_wu", "hashin", "puck", "max_stress"):
        h = k.progressive_failure(qi, [1, 0, 0, 0, 0, 0], criterion=kr)
        load = [g["load_factor"] for g in h["history"]]
        check_true(f"QI Nx {kr}: monotonic, FPF ≤ LPF, collapse",
                   all(b >= a for a, b in zip(load, load[1:])) and h["fpf"] <= h["lpf"]
                   and h["collapse"], f"FPF {h['fpf']:.4g}, LPF {h['lpf']:.4g}", source="derivation")
    # QI under Nx: LPF ≈ 0° fibre fracture: the 0° plies must break at Xt (index ≈ 1 check)
    h = k.progressive_failure(qi, [1, 0, 0, 0, 0, 0], criterion="max_stress")
    check_true("QI Nx max. stress: last event is a fibre failure", "fiber" in h["history"][-1]["kinds"],
               str(h["history"][-1]["kinds"]), source="derivation")
    # FPF with curing residual stress (cool-down): index exactly 1 in the critical ply
    imt = dict(im7, alpha1=-0.1e-6, alpha2=30e-6)  # α values are PLACEHOLDERS (no source), for consistency only
    cp = k.layers(imt, [(0, t), (90, t), (90, t), (0, t)])
    h0 = k.progressive_failure(cp, [0, 1, 0, 0, 0, 0], criterion="tsai_wu")
    hT = k.progressive_failure(cp, [0, 1, 0, 0, 0, 0], criterion="tsai_wu", dT=-160)
    check_true("cool-down residual stress lowers FPF under Ny (0° matrix pre-loaded in tension)", hT["fpf"] < h0["fpf"],
               f"{hT['fpf']:.4g} < {h0['fpf']:.4g}", source="derivation: α2 > α1")
    i = hT["history"][0]["layers"][0]
    s0 = k.laminate_analysis(cp, dT=-160)["layers"][i]["points"]["middle"]["sig12"]
    s1 = k.laminate_analysis(cp, N=(0, hT["fpf"], 0))["layers"][i]["points"]["middle"]["sig12"]
    check("thermal FPF: Tsai-Wu index of the critical ply = 1", k.tsai_wu(s0 + s1, imt)["index"], 1.0, rtol=1e-8,
          source="derivation: definition of the root")
    expect_error("zero load vector is rejected", k.progressive_failure, ply, [0] * 6, error=ValueError)
    expect_error("invalid reduction is rejected", k.progressive_failure, ply, [1, 0, 0, 0, 0, 0], reduction="half",
                 error=ValueError)


def test_buckling():
    E, nu, tt = 70e9, 0.3, 2e-3
    Di = E * tt ** 3 / (12 * (1 - nu ** 2))
    D = np.array([[Di, nu * Di, 0], [nu * Di, Di, 0], [0, 0, (1 - nu) * Di / 2]])
    b = 0.3
    check("isotropic square plate, uniaxial: N = 4π²D/b²", k.plate_buckling(D, b, b)["Nx_cr"],
          4 * math.pi ** 2 * Di / b ** 2, rtol=1e-12, source="derivation: isotropic limit (k = 4)")
    check("isotropic square plate, equal biaxial: N = 2π²D/a²", k.plate_buckling(D, b, b, phi=1.0)["Nx_cr"],
          2 * math.pi ** 2 * Di / b ** 2, rtol=1e-12, source="derivation: (m² + n²)²/(m² + n²), m = n = 1")
    r3 = k.plate_buckling(D, 3 * b, b)
    check_true("isotropic a/b = 3 → m = 3 half-waves", r3["m"] == 3 and r3["n"] == 1, f"m={r3['m']}, n={r3['n']}",
               source="derivation: square cells")
    im7 = library.find("IM7-8552")
    t = im7["t_layer"]
    cp = k.layers(im7, [(0, t), (90, t), (0, t), (90, t), (90, t), (0, t), (90, t), (0, t)])
    Dl = k.laminate_constants(cp)["D"]
    a_, b_ = 0.5, 0.2
    r = k.plate_buckling(Dl, a_, b_, phi=0.5)
    m, n = r["m"], r["n"]
    D11, D12, D22, D66 = Dl[0, 0], Dl[0, 1], Dl[1, 1], Dl[2, 2]
    ab = a_ / b_
    user = math.pi ** 2 * (D11 * m ** 4 + 2 * (D12 + 2 * D66) * m ** 2 * n ** 2 * ab ** 2 + D22 * n ** 4 * ab ** 4) / (
        a_ ** 2 * (m ** 2 + 0.5 * n ** 2 * ab ** 2))
    check("MIL-HDBK-17 form = a² form (same m, n)", r["Nx_cr"], user, rtol=1e-12,
          source="derivation: MIL-HDBK-17-3F Eq. 5.7.1.6(a) expanded with (a/b)⁴")
    check("Ny_cr = φ·Nx_cr", r["Ny_cr"], 0.5 * r["Nx_cr"], rtol=1e-15, source="MIL-HDBK-17-3F Eq. 5.7.1.6(c)")
    check_true("cross-ply: D16 = D26 = 0 → no warning", r["warning"] == "", r["warning"], source="derivation")
    # Long-plate limit: at a/b = 20 the discrete-m loss is of order (Δm/m)² → rtol 2e-3
    check("long-plate limit (a/b = 20) = MIL Eq. 5.7.1.3", k.plate_buckling(Dl, 20 * b_, b_, m_max=80)["Nx_cr"],
          k.long_plate_buckling(Dl, b_), rtol=2e-3, source="MIL-HDBK-17-3F Eq. 5.7.1.3 (limit by derivation)")
    check_true("long-plate value is a lower bound (for every a/b)",
               all(k.plate_buckling(Dl, x * b_, b_, m_max=60)["Nx_cr"]
                   >= k.long_plate_buckling(Dl, b_) * (1 - 1e-12) for x in (1, 1.3, 2.7, 4.1, 7.5)),
               source="derivation: AM-GM")
    qi = k.layers(im7, [(45, t), (-45, t), (0, t), (90, t), (90, t), (0, t), (-45, t), (45, t)])
    check_true("D16/D26 warning for a laminate with ±45 outer plies",
               k.plate_buckling(k.laminate_constants(qi)["D"], a_, b_)["warning"] != "",
               source="MIL-HDBK-17-3F §5.7.1.8 (effect of D16, D26)")
    rc = k.plate_buckling(Dl, a_, b_, phi=-0.3)
    check_true("tension in y (φ < 0) raises the buckling load", rc["Nx_cr"] > k.plate_buckling(Dl, a_, b_)["Nx_cr"],
               f"{rc['Nx_cr']:.4g}", source="derivation")
    expect_error("a ≤ 0 is rejected", k.plate_buckling, Dl, 0.0, b_, error=ValueError)
    expect_error("pure tension (φ ≪ 0, large b/a) does not buckle", k.plate_buckling, Dl, 0.05, 1.0, -1e6, 3, 3,
                 error=ValueError)


def test_sandwich():
    Ef, tf, tc, Ec = 70e9, 0.5e-3, 20e-3, 0.1e9
    r = k.sandwich_beam(Ef, tf, tc, Ec, M=100.0, Q=1000.0)
    d = tc + tf
    check("exact D = Ef tf d²/2 + Ef tf³/6 + Ec tc³/12", r["D"],
          Ef * tf * d ** 2 / 2 + Ef * tf ** 3 / 6 + Ec * tc ** 3 / 12,
          rtol=1e-12, source="derivation: parallel-axis theorem")
    thin = k.sandwich_beam(Ef, 1e-6, tc, 0.0, M=100.0, Q=1000.0)
    check("thin-face limit D/D_thin → 1", thin["D"] / thin["D_thin"], 1.0, rtol=1e-4, source="derivation: tf/d → 0")
    check("Ec = 0 → core shear = (Q/d)/(1 + tf²/(3d²))", k.sandwich_beam(Ef, tf, tc, 0.0, Q=1000.0)["tau_core"],
          1000.0 / d / (1 + tf ** 2 / (3 * d ** 2)), rtol=1e-12, source="derivation: τ = Q·(Ef tf d/2)/D")
    check("thin-face limit τc → Q/d", thin["tau_core"] / thin["tau_core_thin"], 1.0, rtol=1e-6, source="derivation")
    check("thin-face limit σf → M/(tf d)", thin["sig_face"] / thin["sig_face_thin"], 1.0, rtol=1e-4,
          source="derivation")
    check("wrinkling k1 = 0.5 (Hoff & Mautner design)", k.face_crippling(Ef, 0.1e9, 0.05e9),
          0.5 * (Ef * 0.1e9 * 0.05e9) ** (1 / 3), rtol=1e-12, source="Ley et al. 1999, Table 3 (formula)")
    check("wrinkling theoretical/design ratio 0.91/0.5", k.face_crippling(Ef, 0.1e9, 0.05e9, k1=0.910)
          / k.face_crippling(Ef, 0.1e9, 0.05e9), 1.82, rtol=1e-12, source="Ley et al. 1999, Eq. 8 and Table 3")
    check("honeycomb wrinkling σ = k2 Ef √(Ec tf/(Ef tc))", k.face_crippling_honeycomb(Ef, 0.1e9, tf, tc),
          0.82 * Ef * math.sqrt(0.1e9 * tf / (Ef * tc)), rtol=1e-12, source="Ley et al. 1999, Table 3 (formula)")
    expect_error("negative core modulus is rejected", k.sandwich_beam, Ef, tf, tc, -1.0, error=ValueError)
    expect_error("zero face thickness is rejected", k.sandwich_beam, Ef, 0.0, tc, error=ValueError)
