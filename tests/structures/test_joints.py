"""Tests of the joints module.

Sources read: NASA-STD-5020B (2021) Eqs. 8-13, 19-22; de Sá Martins et al. ICAS 2018-0659 Eq. (2);
Roymech "Joint Stiffness" numerical example (d = 10 mm, two 20 mm plates, E = 207 GPa).
"""
import math

import numpy as np

from aerokit.structures import joints as bg
from aerokit.verification import check, check_true, expect_error


def test_single_fastener_strengths():
    d, Fsu = 0.006, 331e6
    check("single shear πd²Fsu/4", bg.shear_strength(d, Fsu), math.pi * d ** 2 / 4 * Fsu, rtol=1e-12,
          source="NASA-STD-5020B Eq. (12)")
    check("double shear = 2 × single", bg.shear_strength(d, Fsu, 2), 2 * bg.shear_strength(d, Fsu), rtol=1e-12,
          source="derivation")
    check("bearing d·t·Fbru", bg.bearing_strength(d, 0.002, 800e6), d * 0.002 * 800e6, rtol=1e-12,
          source="derivation")
    check("net section (w − 2d)·t·Ftu", bg.net_section_strength(0.05, 0.002, d, 2, 470e6),
          (0.05 - 0.012) * 0.002 * 470e6, rtol=1e-12, source="derivation")
    check("edge tear-out 2(e − d/2)·t·Fsu", bg.edge_tearout(2 * d, d, 0.002, 280e6),
          2 * 1.5 * d * 0.002 * 280e6, rtol=1e-12, source="derivation: simple model")
    ms = bg.joint_margins(10e3, d, 0.002, 331e6, 800e6, 470e6, 0.05, 2 * d, n_holes=2, n_fasteners=2, FS=1.5)
    check("margins: shear MS = Psu/(1.5·P/2) − 1", ms["shear"], bg.shear_strength(d, 331e6) / (1.5 * 5e3) - 1,
          rtol=1e-12, source="derivation: beam.safety_margin")
    check_true("margins: critical mode has the smallest MS",
               ms[ms["critical"]] == min(v for k, v in ms.items() if k != "critical"), ms["critical"],
               source="derivation")
    expect_error("edge distance e ≤ d/2 is rejected", bg.edge_tearout, 0.002, d, 0.002, 1e8, error=ValueError)
    expect_error("net width ≤ 0 is rejected", bg.net_section_strength, 0.01, 0.002, d, 2, 1e8, error=ValueError)
    expect_error("zero shear planes are rejected", bg.shear_strength, d, Fsu, 0, error=ValueError)


def test_bolt_group():
    square = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1)]
    r = bg.bolt_group(square, 0.0, -4000.0)
    check("pure shear: equal sharing", r["F"][2], 1000.0, rtol=1e-12, source="derivation: P/n")
    check("pure shear: centroid", r["center"][0], 0.05, rtol=1e-12, source="derivation")
    m = bg.bolt_group(square, 0.0, 0.0, M=200.0)
    ri = math.hypot(0.05, 0.05)
    check("pure moment: F = M·r/Σr²", m["F"][0], 200.0 * ri / (4 * ri ** 2), rtol=1e-12,
          source="derivation: polar moment")
    check("pure moment: force perpendicular to r", m["Fx"][0] * (0 - 0.05) + m["Fy"][0] * (0 - 0.05), 0.0, atol=1e-9,
          source="derivation")
    # proportionality: different radii
    line = [(-0.1, 0), (-0.05, 0), (0.05, 0), (0.1, 0)]
    mh = bg.bolt_group(line, 0.0, 0.0, M=60.0)
    check("pure moment: F ∝ r", mh["F"][0] / mh["F"][1], 2.0, rtol=1e-12, source="derivation")
    check("pure moment: ΣF·r = M", sum(mh["F"] * np.array([0.1, 0.05, 0.05, 0.1])), 60.0, rtol=1e-12,
          source="derivation")
    # eccentric load: P = 4000 N downwards, 0.2 m to the right of the centroid → M = −800 N·m
    e = bg.bolt_group(square, 0.0, -4000.0, point=(0.25, 0.05))
    check("eccentric: moment about the centroid = P·e", e["M_center"], -4000.0 * 0.2, rtol=1e-12, source="derivation")
    # most loaded fastener (bottom right, (0.1, 0)): direct (0, −1000) + moment share M·(−ry, rx)/Σr²
    J = 4 * ri ** 2
    Fx = -(-800.0) * (-0.05) / J
    Fy = -1000.0 + (-800.0) * 0.05 / J
    check("eccentric: bottom-right fastener |F|", e["F"][1], math.hypot(Fx, Fy), rtol=1e-12,
          source="derivation: by hand")
    check("eccentric: ΣFy = Py", e["Fy"].sum(), -4000.0, rtol=1e-12, source="derivation: equilibrium")
    weighted = bg.bolt_group([(0, 0), (0.1, 0)], 0.0, 300.0, areas=[1.0, 2.0])
    check("area-weighted direct share", weighted["Fy"][1], 200.0, rtol=1e-12, source="derivation")
    expect_error("moment on a single point is rejected", bg.bolt_group, [(0, 0)], 0.0, 0.0, 5.0, error=ValueError)


def test_flexibility_and_load_distribution():
    d, Ef, t1, E1, t2, E2 = 0.0048, 110e9, 0.002, 71e9, 0.003, 71e9
    check("Swift f = 5/(Ef·d) + 0.8/(t1E1) + 0.8/(t2E2)", bg.swift_flexibility(d, Ef, t1, E1, t2, E2),
          5 / (Ef * d) + 0.8 / (t1 * E1) + 0.8 / (t2 * E2), rtol=1e-12,
          source="de Sá Martins et al. 2018, ICAS 2018-0659 Eq. (2)")
    ch = bg.huth_flexibility(d, Ef, t1, E1, t2, E2, "rivet_metal", 1)
    check("Huth rivet (a = 2/5, b = 2.2)", ch, ((t1 + t2) / (2 * d)) ** 0.4 * 2.2 *
          (1 / (t1 * E1) + 1 / (t2 * E2) + 1 / (2 * t1 * Ef) + 1 / (2 * t2 * Ef)), rtol=1e-12,
          source="constants: Altair Inspire glossary; form not verified")
    check_true("Huth double shear < single-shear flexibility", bg.huth_flexibility(d, Ef, t1, E1, t2, E2, n=2) <
               bg.huth_flexibility(d, Ef, t1, E1, t2, E2, n=1), source="derivation")
    P, EA, p = 10e3, 71e9 * 0.03 * 0.002, 0.02
    s = p / EA
    F2 = bg.load_distribution(P, 2, p, EA, EA, 1e-8)
    check("2 fasteners, equal sheets: equal share", F2[0], P / 2, rtol=1e-12, source="derivation: symmetry")
    for c in (0.0, 0.5 * s, 3 * s):
        F3 = bg.load_distribution(P, 3, p, EA, EA, c)
        check(f"3 fasteners F1 = P(c+s)/(3c+2s) (c/s={c / s:.1f})", F3[0], P * (c + s) / (3 * c + 2 * s), rtol=1e-10,
              source="derivation: compatibility by hand")
        check(f"3 fasteners symmetry F1 = F3 (c/s={c / s:.1f})", F3[2], F3[0], rtol=1e-10, source="derivation")
    F3r = bg.load_distribution(P, 3, p, EA, EA, 0.0)
    check("rigid fasteners, equal sheets: middle fastener carries no load", F3r[1], 0.0, atol=1e-9 * P,
          source="derivation")
    s1, s2, c = p / EA, p / (2 * EA), 2e-9
    Fu = bg.load_distribution(P, 2, p, EA, 2 * EA, c)
    check("2 fasteners, different sheets F1 = P(c+s1)/(2c+s1+s2)", Fu[0], P * (c + s1) / (2 * c + s1 + s2),
          rtol=1e-10, source="derivation: compatibility by hand")
    Fn = bg.load_distribution(P, 6, p, EA, EA, bg.swift_flexibility(d, Ef, t1, E1, t1, E1))
    check("6 fasteners ΣF = P", Fn.sum(), P, rtol=1e-12, source="derivation: equilibrium")
    check_true("6 fasteners: end fasteners most loaded", Fn[0] == Fn.max() and Fn[-1] > Fn[2],
               f"{np.round(Fn / P, 3)}", source="derivation")
    expect_error("load distribution rejects a negative C", bg.load_distribution, P, 3, p, EA, EA,
                 [1e-9, -1e-9, 1e-9], error=ValueError)


def test_preload_stiffness():
    E, d = 207e9, 0.010
    k1 = bg.frustum_stiffness(E, d, 0.020, 1.5 * d)
    check("Roymech: single 20 mm frustum k = 3503 kN/mm", k1 / 1e6, 3503.0, rtol=2e-4,
          source="Roymech, Joint Stiffness (d = 10, t = 20 mm, 30°, D = 1.5d)")
    km = bg.member_stiffness([(0.020, E), (0.020, E)], d)
    check("Roymech: two plates in series k = 1751.3 kN/mm", km / 1e6, 1751.3, rtol=2e-4,
          source="Roymech, Joint Stiffness")
    check("Roymech: Wileman k = 1906 kN/mm", bg.wileman_stiffness(E, d, 0.040) / 1e6, 1906.0, rtol=5e-4,
          source="Roymech, Joint Stiffness (A = 0.78715, B = 0.62873)")
    l = 0.040
    shigley = 0.5774 * math.pi * E * d / (2 * math.log(5 * (0.5774 * l + 0.5 * d) / (0.5774 * l + 2.5 * d)))
    # rounding tan30° = 0.57735 to 0.5774: a difference of order 1e-4
    check("two equal halves: Shigley-type closed form", km, shigley, rtol=2e-4,
          source="derivation: frustum, t = l/2, D = 1.5d")
    km3 = bg.member_stiffness([(0.010, E), (0.015, E), (0.015, E)], d)
    check("splitting into layers does not change the stiffness", km3, km, rtol=1e-12,
          source="derivation: frusta in series")
    ka = bg.member_stiffness([(0.020, 71e9), (0.020, 207e9)], d)
    check("different materials: 1/k = 1/k_Al + 1/k_steel", 1 / ka, 1 / bg.frustum_stiffness(71e9, d, 0.02, 1.5 * d) +
          1 / bg.frustum_stiffness(E, d, 0.02, 1.5 * d), rtol=1e-12, source="derivation")
    Ad, At = math.pi * d ** 2 / 4, 58.0e-6
    kb = bg.bolt_stiffness(E, Ad, At, 0.025, 0.015)
    check("bolt stiffness, springs in series", 1 / kb, 0.025 / (Ad * E) + 0.015 / (At * E), rtol=1e-12,
          source="derivation")
    phi = bg.stiffness_coefficient(kb, km)
    y = bg.bolt_load(20e3, 8e3, phi)
    check("bolt load Pp + φPt", y["P_bolt"], 20e3 + phi * 8e3, rtol=1e-12, source="NASA-STD-5020B Eqs. (8)-(9)")
    check("separation load Pp/(1 − φ)", y["P_separation"], 20e3 / (1 - phi), rtol=1e-12,
          source="NASA-STD-5020B Eq. (11)")
    yy = bg.bolt_load(20e3, y["P_separation"], phi)
    check("member compression is zero at the separation load", yy["P_member"], 0.0, atol=1e-6, source="derivation")
    check("MS_sep = Pp,min/(FF·FS·PtL) − 1", bg.ms_separation(12e3, 8e3, 1.2, 1.15), 12e3 / (1.15 * 1.2 * 8e3) - 1,
          rtol=1e-12, source="NASA-STD-5020B Eq. (19)")
    expect_error("frustum D ≤ d is rejected", bg.frustum_stiffness, E, d, 0.02, d, error=ValueError)
    expect_error("nφ ≥ 1 is rejected", bg.bolt_load, 1e3, 1e3, 0.6, 2.0, error=ValueError)


def test_interaction_5020():
    check("shear only, R_s = 1: MS = 0", bg.ms_tension_shear(0.0, 1.0, 5e3, 5e3), 0.0, atol=1e-12,
          source="NASA-STD-5020B Eq. (20)")
    check("tension only, R_t = 0.5: MS = 1", bg.ms_tension_shear(5e3, 10e3, 0.0, 1.0), 1.0, rtol=1e-12,
          source="NASA-STD-5020B Eq. (20)")
    Rs = 0.6
    Rt = (1 - Rs ** 2.5) ** (1 / 1.5)
    check("shank in the shear plane, on the curve: R_s^2.5 + R_t^1.5 = 1 → MS = 0",
          bg.ms_tension_shear(Rt, 1.0, Rs, 1.0), 0.0, atol=1e-12, source="NASA-STD-5020B Eq. (20)")
    Rt2 = (1 - Rs ** 1.2) ** 0.5
    check("threads in the shear plane, on the curve: R_s^1.2 + R_t² = 1 → MS = 0",
          bg.ms_tension_shear(Rt2, 1.0, Rs, 1.0, thread_in_shear=True), 0.0, atol=1e-12,
          source="NASA-STD-5020B Eq. (22)")
    check_true("threads in the shear plane give a lower margin", bg.ms_tension_shear(0.4, 1, 0.4, 1, True) <
               bg.ms_tension_shear(0.4, 1, 0.4, 1), source="derivation")
