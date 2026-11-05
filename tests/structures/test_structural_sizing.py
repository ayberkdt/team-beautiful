"""Tests of structural_sizing.py: Megson examples (via the FOSSEE notebooks) and derivation checks."""
import math

import numpy as np

from aerokit.materials.library import find
from aerokit.structures import beam
from aerokit.structures import structural_sizing as Y
from aerokit.verification import check, check_true, expect_error

MEG20 = "Megson 4th ed. Example {} (p. {}), read via FOSSEE Chapter20.ipynb"
MEG21 = "Megson 4th ed. Example 21.2 (p. 589), read via FOSSEE Chapter21.ipynb"


def test_spar_cap_area():
    M, h, s = 120e3, 0.18, 400e6
    r = Y.spar_cap_area(M, h, s, FS=1.5)
    check("cap area = FS·M/(h·σ)", r["required"], 1.5 * M / (h * s), rtol=1e-12, source="derivation: P = M/h")
    check("MS = 0 at the required area", r["MS"], 0.0, atol=1e-12, source="derivation")
    r2 = Y.spar_cap_area(M, h, s, FS=1.5, A_current=2 * r["required"])
    check("twice the area → MS = 1", r2["MS"], 1.0, rtol=1e-12, source="derivation")
    r3 = Y.spar_cap_area(M, h, s, FS=1.5, sigma_compression=250e6)
    check_true("lower compression allowable governs", r3["mod"].startswith("spar cap compression"), r3["mod"],
               source="derivation")
    check("compression governs → area from σ_compression", r3["required"], 1.5 * M / (h * 250e6), rtol=1e-12,
          source="derivation")
    # consistency with beam.bending_stress for a two-flange section (web neglected, thin flanges)
    A = r["required"]
    I = 2 * A * (h / 2) ** 2
    check("flange stress = M·(h/2)/I (thin flanges)", beam.bending_stress(M, {"I": I, "c": h / 2}),
          s / 1.5, rtol=1e-12, source="derivation: beam.bending_stress")
    expect_error("h ≤ 0 raises", Y.spar_cap_area, M, 0.0, s, error=ValueError)


def test_skin_web():
    V, T, b, h, tau = 40e3, 6e3, 0.5, 0.15, 200e6
    r = Y.skin_web_thickness(V, T, b, h, tau, FS=1.5)
    qT = T / (2 * b * h)
    check("skin flow = Bredt T/(2A)", r["q_skin"], beam.bredt_shear_flow(T, b * h), rtol=1e-12,
          source="Bredt-Batho (beam.py)")
    check("web flow = V/(2h) + T/(2A)", r["q_web"], V / (2 * h) + qT, rtol=1e-12, source="derivation")
    check("MS = 0 at the required thickness", r["MS"], 0.0, atol=1e-12, source="derivation")
    check_true("the web governs for this loading", r["mod"].startswith("spar web"), r["mod"], source="derivation")
    rm = Y.skin_web_thickness(10.0, 1.0, b, h, tau, t_min=0.8e-3)
    check_true("t_min governs at small loads", rm["mod"].startswith("minimum"), rm["mod"], source="derivation")
    check("t_min is applied", rm["required"], 0.8e-3, source="derivation")
    rk = Y.skin_web_thickness(0.0, T, b, h, tau, FS=1.0)
    check("pure torsion: web = skin thickness", rk["required_web"], rk["required_skin"], rtol=1e-12,
          source="derivation: Bredt constant q")
    expect_error("tau ≤ 0 raises", Y.skin_web_thickness, V, T, b, h, 0.0, error=ValueError)


def test_rib_spacing():
    E, nu, t, b = 71.7e9, 0.33, 1.6e-3, 0.15
    check("k(a = b) = 4 (same as beam.plate_buckling)", Y.plate_k(b, b), 4.0, rtol=1e-12,
          source="derivation: m = 1, a/b = 1")
    check("k(a = b/2) = 6.25", Y.plate_k(b / 2, b), 6.25, rtol=1e-12, source="derivation: (2 + 1/2)²")
    check("k(a = √2·b): m = 1 and m = 2 equal at 4.5", Y.plate_k(math.sqrt(2) * b, b), 4.5, rtol=1e-12,
          source="derivation: transition point")
    check("k(a → ∞) → 4", Y.plate_k(1000 * b, b), 4.0, rtol=1e-3, source="derivation")
    D4 = beam.plate_buckling(E, nu, t, b)        # k = 4
    sigma = 1.6 * D4 / 1.5                         # required k = 6.4 > 4
    r = Y.rib_spacing(sigma, t, b, E, nu, FS=1.5)
    check("required k = FS·σ/(π²E/(12(1−ν²))(t/b)²)", r["k_required"], 6.4, rtol=1e-12, source="derivation")
    check("MS = 0 at the largest rib spacing", r["MS"], 0.0, atol=1e-10, source="derivation")
    check("a/b closed-form solution: k(a) = k_required", Y.plate_k(r["required"], b), 6.4, rtol=1e-10,
          source="derivation")
    check_true("closer ribs → positive margin",
               Y.rib_spacing(sigma, t, b, E, nu, 1.5, a_current=0.8 * r["required"])["MS"] > 0,
               source="derivation: k increases as a decreases")
    rs = Y.rib_spacing(0.5 * D4, t, b, E, nu, FS=1.5)
    check_true("low stress: spacing unconstrained", math.isinf(rs["required"]), rs["mod"], source="derivation: k ≥ 4")
    ra = Y.rib_spacing(300e6, t, b, E, nu, FS=1.5, Fcy=400e6)
    check_true("FS·σ > Fcy → yield governs", ra["mod"].startswith("material"), ra["mod"], source="derivation")
    expect_error("t ≤ 0 raises", Y.rib_spacing, 1e6, 0.0, b, E, nu, error=ValueError)


def test_megson_boom_areas():
    # Example 20.1: stringer/spar flange 300 mm²; stress ratios and panel lengths from the notebook
    B1 = 300 + Y.boom_area(3, 400, -1.0) + Y.boom_area(2, 600, 150 / 200)
    B2 = (600 + Y.boom_area(2, 600, 200 / 150) + Y.boom_area(2.5, 300, -1.0)
          + Y.boom_area(1.5, 600, 100 / 150))
    B3 = 300 + Y.boom_area(1.5, 600, 150 / 100) + Y.boom_area(2, 200, -1.0)
    check("Megson 20.1: B1 = B6 = 1050 mm²", B1, 1050.0, rtol=1e-12, source=MEG20.format("20.1", 560))
    check("Megson 20.1: B2 = B5 = 1791.67 mm²", B2, 1791.67, rtol=3e-6, source=MEG20.format("20.1", 560))
    check("Megson 20.1: B3 = B4 = 891.67 mm²", B3, 891.67, rtol=5e-6, source=MEG20.format("20.1", 560))
    check("linear distribution: contributions to both booms sum to t·b",
          Y.boom_area(2, 600, 0.75) + Y.boom_area(2, 600, 1 / 0.75),
          2 * 600 * (4 + 0.75 + 1 / 0.75) / 6, rtol=1e-12, source="derivation")
    check("uniform stress (σ2 = σ1): t·b/2 to each boom", Y.boom_area(2, 600, 1.0), 600.0, rtol=1e-12,
          source="derivation: B = tb/6·3")


def test_megson_direct_stress():
    # Example 20.2: fuselage with 16 stringers; booms 1 and 9 on the axis, 2-8 in pairs (both sides)
    y = [660, 600, 420, 228, 25, -204, -396, -502, -540]
    B = [640, 600, 600, 600, 620, 640, 640, 850, 640]
    sig_book = [35.6, 32.4, 22.7, 12.3, 1.3, -11.0, -21.4, -27.1, -29.1]
    xs, ys, Bs = [0.0], [y[0]], [B[0]]
    for i in range(1, 8):
        xs.append(+100.0 * i)
        ys.append(y[i])
        Bs.append(B[i])
    xs.append(0.0)
    ys.append(y[8])
    Bs.append(B[8])
    for i in range(7, 0, -1):
        xs.append(-100.0 * i)
        ys.append(y[i])
        Bs.append(B[i])
    r = Y.multi_boom_section(xs, ys, Bs, Mx=100e6, center=(0.0, 0.0), closed=True)
    check("Megson 20.2: Ixx ≈ 1854e6 mm⁴", r["Ixx"], 1854e6, rtol=1e-3, source=MEG20.format("20.2", 562))
    for i in (0, 2, 4, 7, 8):
        j = i if i < 8 else 8
        check(f"Megson 20.2: boom {i + 1} σ = {sig_book[i]} N/mm²", r["sigma"][j], sig_book[i], atol=0.06,
              source=MEG20.format("20.2", 562) + " (the book rounds to 0.1; Ixx = 1854e6 vs 1854.6e6)")
    r2 = Y.multi_boom_section(xs, ys, Bs, Mx=100e6)
    xr = np.array(ys) - r2["center"][1]
    check("ΣB·y = 0 about the centroid", float(np.sum(np.array(Bs) * xr)), 0.0, atol=1e-6,
          source="derivation: neutral-axis definition")
    check("pure bending: ΣP = 0 (no axial force)", float(np.sum(r2["P"])), 0.0, atol=1e-3, source="derivation")
    check("pure bending: ΣP·y = Mx", float(np.sum(r2["P"] * xr)), 100e6, rtol=1e-12, source="derivation")


def test_megson_shear_flow():
    # Example 20.3: open channel, 4 booms of 300 mm², y = ±200, Sy = 4.8 kN
    r = Y.multi_boom_section([100, 0, 0, 100], [200, 200, -200, -200], [300] * 4, Sy=4.8e3, closed=False)
    check("Megson 20.3: Ixx = 48e6 mm⁴", r["Ixx"], 48e6, rtol=1e-12, source=MEG20.format("20.3", 566))
    check("Megson 20.3: q12 = −6 N/mm", r["q"][0], -6.0, rtol=1e-12, source=MEG20.format("20.3", 566))
    check("Megson 20.3: q23 = −12 N/mm", r["q"][1], -12.0, rtol=1e-12, source=MEG20.format("20.3", 566))
    check("Megson 20.3: q34 = −6 N/mm", r["q"][2], -6.0, rtol=1e-12, source=MEG20.format("20.3", 566))
    check("open section: ΣqΔy = Sy", r["Fy"], 4.8e3, rtol=1e-12, source="derivation: force equilibrium")
    # Example 21.2 open-section flows (S_y,w = 66.6 kN), 6 booms, y = ±300
    r6 = Y.multi_boom_section([1200, 600, 0, 0, 600, 1200], [300, 300, 300, -300, -300, -300],
                              [900, 1200, 900, 900, 1200, 900], Sy=66.6e3)
    check("Megson 21.2: Ixx = 540e6 mm⁴", r6["Ixx"], 540e6, rtol=1e-12, source=MEG21)
    for i, expected in enumerate([-33.3, -77.7, -111.0, -77.7, -33.3]):
        check(f"Megson 21.2: q_b panel {i + 1}{i + 2} = {expected} N/mm", r6["q_b"][i], expected, atol=0.05,
              source=MEG21)
    check("q_b = 0 in the cut panel (ΣBy = 0)", r6["q_b"][5], 0.0, atol=1e-9, source="derivation")


def test_closed_cell_balance():
    # rectangular box with 4 corner booms, b = 600, h = 200 (mm); counter-clockwise order
    x, y, B = [600, 0, 0, 600], [100, 100, -100, -100], [500, 500, 500, 500]
    Sy = 10e3
    r = Y.multi_boom_section(x, y, B, Sy=Sy, x_s=300.0)     # load on the symmetry axis (shear centre)
    check("closed: ΣqΔx = Sx = 0", r["Fx"], 0.0, atol=1e-9, source="derivation: force equilibrium")
    check("closed: ΣqΔy = Sy", r["Fy"], Sy, rtol=1e-12, source="derivation: force equilibrium")
    check("closed: moment equilibrium Σq·2A = x_s·Sy", r["Mz"], 300.0 * Sy, rtol=1e-12, source="derivation")
    check("symmetric box: each web Sy/(2h)", abs(r["q"][1]), Sy / (2 * 200), rtol=1e-12,
          source="derivation: corner-boom box, load at the shear centre")
    check("symmetric box: top panel q = 0", r["q"][0], 0.0, atol=1e-12, source="derivation")
    T = 5e6
    rt = Y.multi_boom_section(x, y, B, T=T, t=2.0, G=27e3)
    check("pure torsion: q = T/(2A) (Bredt)", rt["q"][2], beam.bredt_shear_flow(T, 600 * 200), rtol=1e-12,
          source="Bredt-Batho (beam.py)")
    check("pure torsion: dθ/dz = T/(G·J_Bredt)", rt["dtheta_dz"],
          T / (27e3 * beam.box(600, 200, 2.0, 2.0)["J"]), rtol=1e-12, source="derivation: J = 4A²/∮ds/t")
    # unsymmetric section: equilibrium also with Ixy ≠ 0
    ru = Y.multi_boom_section([0, 400, 500, 50], [80, 120, -60, -90], [300, 700, 400, 900], Sx=2e3, Sy=-7e3,
                              x_s=120.0, y_s=15.0, Mx=3e6, My=-1e6)
    check("unsymmetric: ΣqΔx = Sx", ru["Fx"], 2e3, rtol=1e-10, source="derivation")
    check("unsymmetric: ΣqΔy = Sy", ru["Fy"], -7e3, rtol=1e-10, source="derivation")
    check("unsymmetric: moment equilibrium", ru["Mz"], 120.0 * -7e3 - 15.0 * 2e3, rtol=1e-10, source="derivation")
    xr = np.array([0, 400, 500, 50]) - ru["center"][0]
    yr = np.array([80, 120, -60, -90]) - ru["center"][1]
    check("unsymmetric: ΣP·y = Mx", float(np.sum(ru["P"] * yr)), 3e6, rtol=1e-10, source="derivation")
    check("unsymmetric: ΣP·x = My", float(np.sum(ru["P"] * xr)), -1e6, rtol=1e-10, source="derivation")
    rm = Y.multi_boom_section(x, y, B, Mx=20e6, sigma_allowed=300.0, FS=1.5)
    check("boom direct-stress margin", rm["MS"], 300 / (1.5 * 20e6 * 100 / (4 * 500 * 100 ** 2)) - 1,
          rtol=1e-12, source="derivation: σ = M y/I")
    expect_error("boom area ≤ 0 raises", Y.multi_boom_section, x, y, [500, 0, 500, 500], error=ValueError)
    expect_error("collinear (singular) booms raise", Y.multi_boom_section, [0, 1, 2], [0, 0, 0], [1, 1, 1],
                 error=ValueError)
    expect_error("torsion of an open section raises", Y.multi_boom_section, x, y, B, T=1.0, closed=False,
                 error=ValueError)


def test_tube():
    mat = find("7075-T6")
    E, sy = mat["E"], mat["Fty"]
    M, D, FS = 900.0, 0.04, 1.5
    r = Y.size_tube(M=M, E=E, sigma_y=sy, FS=FS, D=D)
    d = (D ** 4 - 32 * FS * M * D / (math.pi * sy)) ** 0.25
    check("pure bending: closed-form t (D⁴ − d⁴ = 32·FS·M·D/(πσ))", r["required"], (D - d) / 2, rtol=1e-9,
          source="derivation: σ = M(D/2)/I")
    check("MS ≈ 0 at the required thickness", r["MS"], 0.0, atol=1e-9, source="derivation")
    T = 600.0
    rt = Y.size_tube(T=T, E=E, sigma_y=sy, FS=FS, D=D)
    check("pure torsion: von Mises = √3·τ", rt["check"]["von_mises"], math.sqrt(3) * rt["check"]["tau"],
          rtol=1e-12, source="derivation")
    check("pure torsion: √3·τ·FS = σ_y", math.sqrt(3) * rt["check"]["tau"] * FS, sy, rtol=1e-8,
          source="derivation")
    rb = Y.size_tube(M=M, T=T, E=E, sigma_y=sy, FS=FS, D_t=20)
    check("fixed D/t: ratio preserved", rb["D"] / rb["t"], 20.0, rtol=1e-12, source="derivation")
    check("fixed D/t: MS ≈ 0", rb["MS"], 0.0, atol=1e-9, source="derivation")
    # column: long thin tube → Euler governs, at the required D P = σ_cr·A/FS
    rc = Y.size_tube(P_start=20e3, L=1.5, K=1.0, E=E, sigma_y=sy, FS=FS, t=1.5e-3)
    check_true("long column: Euler governs", rc["mod"] == "Euler buckling", rc["mod"], source="derivation: λ > λ_c")
    k = beam.tube(rc["D"], rc["t"])
    check("Euler: π²EI/L² = FS·P", beam.euler_column(E, k["I"], 1.5), FS * 20e3, rtol=1e-8,
          source="derivation: beam.euler_column")
    rj = Y.size_tube(P_start=150e3, L=0.25, K=1.0, E=E, sigma_y=sy, FS=FS, t=3e-3)
    check_true("short column: Johnson or von Mises governs",
               rj["mod"] in ("Johnson buckling", "von Mises (bending + torsion + axial)"), rj["mod"],
               source="derivation")
    lam_c = math.sqrt(2 * math.pi ** 2 * E / sy)
    check("Johnson = Euler = σ_y/2 at the transition (Euler side)", Y.column_stress(E, sy, lam_c)[0], sy / 2,
          rtol=1e-12, source="derivation: λ_c = √(2π²E/σ_y)")
    check("Johnson σ_y/2 at the transition (Johnson side)", Y.column_stress(E, sy, lam_c * (1 - 1e-12))[0], sy / 2,
          rtol=1e-9, source="derivation")
    check("Johnson λ = 0 → σ_y", Y.column_stress(E, sy, 0.0)[0], sy, source="derivation")
    expect_error("two of D, t, D_t given raises", Y.size_tube, M, 0, 0, None, 1, E, sy, 1.5, D, 1e-3,
                 error=ValueError)
    expect_error("2t > D raises", Y.tube_check, 0.01, 0.006, M, 0, 0, None, 1, E, sy, error=ValueError)


def test_wing_mass():
    mat = find("7075-T6")
    W, n, b, c, tc = 10e3, 3.8, 10.0, 1.2, 0.15
    s, tau = 400e6, 200e6
    r = Y.wing_mass_estimated(W, n, b, c, c, tc, mat["rho"], s, tau, FS=1.5, distribution="trapezoid",
                              n_station=4001, t_min=0.0)
    # uniform load w = n_ult·W/b, constant h: ∫A dy = w·L³/(6hσ), 2 flanges × 2 half wings
    w, L, h = 1.5 * n * W / b, b / 2, 0.85 * tc * c
    check("cap mass analytic (uniform load, constant h)", r["masses"]["spar caps"],
          2 * 2 * mat["rho"] * w * L ** 3 / (6 * h * s), rtol=1e-4, source="derivation: M = w(L−y)²/2")
    check("web mass analytic (t_min = 0)", r["masses"]["spar webs"],
          2 * mat["rho"] * 2 * h * w * L ** 2 / (2 * 2 * h * tau), rtol=1e-4, source="derivation: V = w(L−y)")
    raymer = dict(S=b * c, A=b / c, Lambda=0.0, taper=1.0, t_c=tc, W_fw=50.0, q=0.5 * 1.225 * 60 ** 2,
                  W_dg=W / 9.80665)
    rr = Y.wing_mass_estimated(W, n, b, c, 0.6 * c, tc, mat["rho"], s, tau, raymer=raymer, secondary_factor=1.0)
    check_true("Raymer statistical ratio is reported (primary box < statistical total)",
               0 < rr["ratio_raymer"] < 1.0, f"ratio = {rr['ratio_raymer']:.2f}",
               source="sanity check: the primary box is a part of the total wing")
    check("secondary factor is linear", Y.wing_mass_estimated(W, n, b, c, c, tc, mat["rho"], s, tau,
                                                              secondary_factor=1.4)["total"],
          1.4 * Y.wing_mass_estimated(W, n, b, c, c, tc, mat["rho"], s, tau)["primary"], rtol=1e-12,
          source="derivation")
    expect_error("negative span raises", Y.wing_mass_estimated, W, n, -b, c, c, tc, 2800, s, tau,
                 error=ValueError)
