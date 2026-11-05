"""Tests of the section module. Where no literature value exists an independent derivation ("derivation: ...")
is used."""
import math

import numpy as np

from aerokit.structures import beam, section
from aerokit.verification import check, expect_error


def test_polygon_basic():
    b, h = 0.03, 0.05
    s = section.polygon_properties(section.rectangle_polygon(b, h, 0.2, -0.1))
    check("rectangle A = bh", s["A"], b * h, source="derivation: closed form")
    check("rectangle Ix = bh³/12", s["Ix"], b * h ** 3 / 12, source="derivation: closed form")
    check("rectangle Iy = hb³/12", s["Iy"], h * b ** 3 / 12, source="derivation: closed form")
    check("rectangle Ixy = 0", s["Ixy"], 0.0, atol=1e-18, source="derivation: symmetry")
    check("rectangle xc", s["xc"], 0.2 + b / 2, source="derivation")
    check("rectangle Sx = bh²/6", s["Sx_upper"], b * h ** 2 / 6, source="derivation: closed form")
    check("rectangle rx = h/√12", s["rx"], h / math.sqrt(12), source="derivation")
    # clockwise vertices must give the same result
    s2 = section.polygon_properties(section.rectangle_polygon(b, h, 0.2, -0.1)[::-1])
    check("independent of vertex orientation (Ix)", s2["Ix"], s["Ix"], rtol=1e-12, source="derivation")
    # right triangle with the right angle at the origin: Ix_c = bh³/36, Ixy_c = −b²h²/72
    u = section.polygon_properties([(0, 0), (b, 0), (0, h)])
    check("triangle Ix = bh³/36", u["Ix"], b * h ** 3 / 36, source="derivation: closed form")
    check("triangle Ixy = −b²h²/72", u["Ixy"], -b ** 2 * h ** 2 / 72, source="derivation: closed form")
    check("triangle yc = h/3", u["yc"], h / 3, source="derivation")


def test_circle_and_hole():
    r = 0.05
    # inscribed n-gon: relative error ≈ (2π/n)²/6 → 4e-7 for n = 4096; hence the 1e-5 tolerance
    s = section.polygon_properties(section.circle_polygon(r, 4096))
    check("polygon n → ∞: A = πr²", s["A"], math.pi * r ** 2, rtol=1e-5, source="derivation: closed form")
    check("polygon n → ∞: I = πr⁴/4", s["Ix"], math.pi * r ** 4 / 4, rtol=1e-5, source="derivation: closed form")
    # tube = outer circle − inner circle, compared with beam.tube
    D, t = 0.1, 0.004
    tube_poly = section.polygon_properties(section.circle_polygon(D / 2, 4096),
                                           [section.circle_polygon(D / 2 - t, 4096)])
    kb = beam.tube(D, t)
    check("polygon with hole: tube I = beam.tube", tube_poly["Ix"], kb["I"], rtol=1e-5,
          source="derivation: beam.tube")
    check("polygon with hole: tube polar moment = beam.tube J", tube_poly["J_polar"], kb["J"], rtol=1e-5,
          source="derivation: beam.tube")


def test_i_section_and_parallel_axis():
    bf, tf, h, tw = 0.1, 0.008, 0.2, 0.005
    s = section.polygon_properties(section.i_section_polygon(bf, tf, h, tw))
    ki = beam.i_section(bf, tf, h, tw)
    check("I-section polygon I = beam.i_section", s["Ix"], ki["I"], rtol=1e-12, source="derivation: beam.i_section")
    check("I-section polygon A = beam.i_section", s["A"], ki["A"], rtol=1e-12, source="derivation: beam.i_section")
    # parallel axis: a shifted section has the same centroidal values, origin moment I + A·d²
    dx, dy = 0.37, -0.21
    shifted = [(x + dx, y + dy) for x, y in section.i_section_polygon(bf, tf, h, tw)]
    s2 = section.polygon_properties(shifted)
    check("translation: Ix unchanged", s2["Ix"], s["Ix"], rtol=1e-9, source="derivation: parallel axis")
    v = section._ring_integrals(shifted)
    check("parallel axis: ∫y² = Ix + A·yc²", v[4], s2["Ix"] + s2["A"] * s2["yc"] ** 2, rtol=1e-12,
          source="derivation: Steiner")


def test_rotation_invariance():
    L = [(0, 0), (0.08, 0), (0.08, 0.01), (0.01, 0.01), (0.01, 0.06), (0, 0.06)]   # L angle
    s = section.polygon_properties(L)
    phi = 0.6
    c, si = math.cos(phi), math.sin(phi)
    rotated = section.polygon_properties([(x * c - y * si, x * si + y * c) for x, y in L])
    check("rotation preserves Ix + Iy", rotated["Ix"] + rotated["Iy"], s["Ix"] + s["Iy"], rtol=1e-12,
          source="derivation")
    check("rotation preserves I1", rotated["I1"], s["I1"], rtol=1e-12, source="derivation")
    check("rotation preserves I2", rotated["I2"], s["I2"], rtol=1e-12, source="derivation")
    Ix, Iy, Ixy = section.rotate_axis(s["Ix"], s["Iy"], s["Ixy"], s["theta_p"])
    check("principal axes: Ixy' = 0", Ixy, 0.0, atol=1e-14 * s["I1"], source="derivation")
    check("principal axes: Ix' = I1", Ix, s["I1"], rtol=1e-12, source="derivation")
    # rotating the body by φ = rotating the axes by −φ
    a, b_, c_ = section.rotate_axis(s["Ix"], s["Iy"], s["Ixy"], -phi)
    check("axis transformation = body rotation (Ixy)", c_, rotated["Ixy"], rtol=1e-10, source="derivation")


def test_plastic_modulus():
    b, h = 0.02, 0.04
    Z, yp = section.plastic_modulus(section.rectangle_polygon(b, h))
    check("rectangle Zp = bh²/4", Z, b * h ** 2 / 4, rtol=1e-10, source="derivation: closed form")
    bf, tf, H, tw = 0.1, 0.008, 0.2, 0.005
    Zi, _ = section.plastic_modulus(section.i_section_polygon(bf, tf, H, tw))
    check("I-section Zp = bf·tf·(H−tf) + tw(H−2tf)²/4", Zi, bf * tf * (H - tf) + tw * (H - 2 * tf) ** 2 / 4,
          rtol=1e-10, source="derivation: closed form")
    # T-section: flange 0.1×0.01 on top, web 0.01×0.09
    T = [(0.045, 0), (0.055, 0), (0.055, 0.09), (0.1, 0.09), (0.1, 0.1), (0, 0.1), (0, 0.09), (0.045, 0.09)]
    Zt, ypt = section.plastic_modulus(T)
    # A = 0.0019, upper half 0.00095: flange 0.001 > 0.00095 → y_p inside the flange: 0.1 − 0.00095/0.1 = 0.0905
    yp_expected = 0.1 - 0.00095 / 0.1
    Z_expected = (0.1 * (0.1 - yp_expected) ** 2 / 2 + 0.1 * (yp_expected - 0.09) ** 2 / 2
                  + 0.0009 * (yp_expected - 0.045))
    check("T-section equal-area axis", ypt, yp_expected, rtol=1e-9, source="derivation: by hand")
    check("T-section Zp", Zt, Z_expected, rtol=1e-9, source="derivation: by hand")
    Zy, _ = section.plastic_modulus(section.rectangle_polygon(b, h), axis="y")
    check("rectangle Zp (y axis) = hb²/4", Zy, h * b ** 2 / 4, rtol=1e-10, source="derivation")


def test_compound_section():
    # lower layer E2 = 2E1: the transformed section has twice the width at the bottom
    b, h1, h2, E1 = 0.05, 0.02, 0.01, 70e9
    part = [{"outer": section.rectangle_polygon(b, h2, 0, 0), "E": 2 * E1},
            {"outer": section.rectangle_polygon(b, h1, 0, h2), "E": E1}]
    s = section.compound_section(part, E_ref=E1)
    tr = section.polygon_properties([(-b / 2, 0), (1.5 * b, 0), (1.5 * b, h2), (b, h2), (b, h2 + h1),
                                     (0, h2 + h1), (0, h2), (-b / 2, h2)])
    check("compound = transformed width (Ix)", s["Ix"], tr["Ix"], rtol=1e-12, source="derivation: transformed section")
    check("compound = transformed width (yc)", s["yc"], tr["yc"], rtol=1e-12, source="derivation")
    check("compound EA = ΣE·A", s["EA"], 2 * E1 * b * h2 + E1 * b * h1, rtol=1e-12, source="derivation")
    single = section.compound_section([{"outer": section.rectangle_polygon(b, h1), "E": E1}])
    check("single-material compound = polygon", single["Ix"], b * h1 ** 3 / 12, rtol=1e-12, source="derivation")


def test_unsymmetric_bending():
    L = [(0, 0), (0.08, 0), (0.08, 0.01), (0.01, 0.01), (0.01, 0.06), (0, 0.06)]
    s = section.polygon_properties(L)
    Ix, Iy, Ixy = s["Ix"], s["Iy"], s["Ixy"]
    Mx, My = 1200.0, -300.0
    x, y = 0.08 - s["xc"], 0.0 - s["yc"]
    sig = section.bending_stress(Mx, My, Ix, Iy, Ixy, x, y)
    # independent route: transform to principal axes (M' = (My, Mx) rotates like a vector)
    th = s["theta_p"]
    c, si = math.cos(th), math.sin(th)
    u, v = x * c + y * si, -x * si + y * c
    Mu, Mv = My * c + Mx * si, -My * si + Mx * c
    I_uu, I_vv = section.rotate_axis(Ix, Iy, Ixy, th)[1], section.rotate_axis(Ix, Iy, Ixy, th)[0]
    check("general formula = principal-axis method", sig, Mu * u / I_uu + Mv * v / I_vv, rtol=1e-10,
          source="derivation: principal-axis transformation")
    a = section.neutral_axis_angle(Mx, My, Ix, Iy, Ixy)
    check("σ = 0 on the neutral axis", section.bending_stress(Mx, My, Ix, Iy, Ixy, math.cos(a), math.sin(a)),
          0.0, atol=1e-6 * abs(sig), source="derivation")
    check("Ixy = 0: σ = Mx·y/Ix + My·x/Iy", section.bending_stress(Mx, My, 2e-6, 1e-6, 0.0, 0.01, 0.02),
          Mx * 0.02 / 2e-6 + My * 0.01 / 1e-6, rtol=1e-12, source="derivation")
    check("symmetric section, pure Mx: neutral axis = x axis", section.neutral_axis_angle(5.0, 0.0, 2.0, 1.0, 0.0),
          0.0, atol=1e-15, source="derivation")
    expect_error("zero moment: neutral axis undefined", section.neutral_axis_angle, 0, 0, 1, 1, 0, error=ValueError)


def test_thin_open_section():
    b, h, t = 0.05, 0.1, 0.002
    u = section.u_section_thin(b, h, t, t)
    e = 3 * b ** 2 / (6 * b + h)
    xs_sec, ys_sec = u.shear_center()
    check("channel shear centre e = 3b²/(6b+h) (sectorial)", -xs_sec, e, rtol=1e-12,
          source="derivation: shear-flow integral by hand (Megson type; not read in the book this session)")
    check("channel shear centre (shear-flow moment) = sectorial", u.shear_center_flow()[0], xs_sec, rtol=1e-12,
          source="derivation: two independent routes")
    check("channel on the symmetry axis: y_s = 0", ys_sec, 0.0, atol=1e-15, source="derivation")
    tf, tw = 0.003, 0.0015
    u2 = section.u_section_thin(b, h, tf, tw)
    check("channel (different t) e = 3b²tf/(6b·tf + h·tw)", -u2.shear_center()[0],
          3 * b ** 2 * tf / (6 * b * tf + h * tw), rtol=1e-12, source="derivation: shear-flow integral by hand")
    check("channel Cw = tf b³h²/12·(3b·tf+2h·tw)/(6b·tf+h·tw)", u2.sectorial()["Cw"],
          tf * b ** 3 * h ** 2 / 12 * (3 * b * tf + 2 * h * tw) / (6 * b * tf + h * tw), rtol=1e-12,
          source="closed form (same as AISC DG9 from memory; not read in this session)")
    check("channel J = Σ b t³/3", u2.J, (2 * b * tf ** 3 + h * tw ** 3) / 3, rtol=1e-12,
          source="derivation: St Venant")
    # I-section
    bi, hi, tfi, twi = 0.08, 0.2, 0.003, 0.002
    I = section.i_section_thin(bi, hi, tfi, twi)
    check("I Cw = tf·b³·h²/24", I.sectorial()["Cw"], tfi * bi ** 3 * hi ** 2 / 24, rtol=1e-12,
          source="derivation: Cw = Iy_flange·h²/2")
    check("I Cw = Iy·h²/4 (web contribution neglected)", I.sectorial()["Cw"], 2 * tfi * bi ** 3 / 12 * hi ** 2 / 4,
          rtol=1e-12, source="derivation")
    check("thin I Ix = tw h³/12 + 2 b tf (h/2)²", I.Ix, twi * hi ** 3 / 12 + 2 * bi * tfi * (hi / 2) ** 2,
          rtol=1e-12, source="derivation")
    # shear flow on the neutral axis of the web q = V·Q/I
    V = 1000.0
    flow = I.shear_flow(0.0, V)
    q_web = max(abs(e_["q_mid"]) for e_ in flow["elements"] if (e_["i"], e_["j"]) == (1, 4))
    Q = bi * tfi * hi / 2 + twi * (hi / 2) ** 2 / 2
    check("I web mid q = VQ/I", q_web, V * Q / I.Ix, rtol=1e-12, source="derivation: VQ/I")
    check("shear-flow resultant Fy = Sy", flow["Fy"], V, rtol=1e-12, source="derivation: equilibrium")
    check("shear-flow resultant Fx = 0", flow["Fx"], 0.0, atol=1e-9 * V, source="derivation: equilibrium")
    # Z-section: Ixy ≠ 0, shear centre = centroid (antisymmetry)
    z = section.z_section_thin(b, h, t)
    zx, zy = z.shear_center()
    check("Z shear centre x = 0 (antisymmetry)", zx, 0.0, atol=1e-15, source="derivation")
    check("Z Ixy = t·b²·h/2", z.Ixy, 2 * b * t * (h / 2) * (b / 2), rtol=1e-12, source="derivation")
    check("Z Cw = t b³ h²(b+2h)/(12(2b+h))", z.sectorial()["Cw"], t * b ** 3 * h ** 2 * (b + 2 * h) / (12 * (2 * b + h)),
          rtol=1e-12, source="closed form (from memory; not read in this session) -- agrees with the numerical result")
    zs = z.shear_flow(700.0, -300.0)
    check("Z oblique shear: Fx = Sx", zs["Fx"], 700.0, rtol=1e-10, source="derivation: equilibrium")
    check("Z oblique shear: Fy = Sy", zs["Fy"], -300.0, rtol=1e-10, source="derivation: equilibrium")
    # slit thin tube (open): J = 2πR t³/3
    R, n = 0.05, 400
    angle = np.linspace(0.0, 2 * math.pi * (1 - 1e-4), n + 1)
    node = [(R * math.cos(a_), R * math.sin(a_)) for a_ in angle]
    slit = section.ThinOpenSection(node, [(i, i + 1, t) for i in range(n)])
    # modelled arc 2πR(1 − 1e-4) (slit); chords are shorter than the arc (Δ²/24 ≈ 1e-5): tolerance 2e-5
    check("slit tube J = 2πRt³/3", slit.J, 2 * math.pi * R * (1 - 1e-4) * t ** 3 / 3, rtol=2e-5,
          source="derivation")
    # the shear centre of a slit tube is 2R from the centre (opposite the slit)
    check("slit tube shear centre at 2R", math.hypot(*slit.shear_center()), 2 * R, rtol=1e-3,
          source="derivation: closed form (open thin ring)")
    expect_error("closed loop is rejected", section.ThinOpenSection, [(0, 0), (1, 0), (1, 1)],
                 [(0, 1, 0.1), (1, 2, 0.1), (2, 0, 0.1)], error=ValueError)
    expect_error("negative thickness is rejected", section.ThinOpenSection, [(0, 0), (1, 0)], [(0, 1, -0.1)],
                 error=ValueError)


def test_thickness_term():
    # thin model with t³ terms (thick walls) approaches the exact I-section
    bf, tf, H, tw = 0.1, 0.01, 0.2, 0.006
    h = H - tf
    d = [(-bf / 2, h / 2), (0, h / 2), (bf / 2, h / 2), (-bf / 2, -h / 2), (0, -h / 2), (bf / 2, -h / 2)]
    e = [(0, 1, tf), (1, 2, tf), (3, 4, tf), (4, 5, tf), (1, 4, tw)]
    m = section.ThinOpenSection(d, e, thickness_term=True)
    exact = beam.i_section(bf, tf, H, tw)["I"]
    # the web is modelled between the flange mid-lines, so the region y ∈ [H/2 − tf, h/2] (at both ends) is
    # counted twice; adding exactly this overlap must leave no difference
    overlap = 2 * tw * ((h / 2) ** 3 - (H / 2 - tf) ** 3) / 3
    check("thin model with t³ terms = exact I + overlap", m.Ix, exact + overlap, rtol=1e-12,
          source="derivation: beam.i_section")
    check("thin model with t³ terms ≈ exact I (3 %)", m.Ix, exact, rtol=0.03, source="derivation: overlap 2.4 %")


def test_multi_cell():
    b, h, t = 0.4, 0.1, 0.002
    single = section.multi_cell_torsion([b * h], [[2 * b / t + 2 * h / t]], T=1.0, G=1.0)
    check("single cell J = beam.box J", single["J"], beam.box(b, h, t, t)["J"], rtol=1e-12,
          source="derivation: Bredt")
    R = 0.05
    ring = section.multi_cell_torsion([math.pi * R ** 2], [[2 * math.pi * R / t]])
    check("thin tube J = 2πR³t", ring["J"], 2 * math.pi * R ** 3 * t, rtol=1e-12, source="derivation: Bredt")
    # two symmetric cells: no flow in the shared wall, J equal to a single box
    A = b / 2 * h
    d_ii = b / t + 2 * h / t        # b/2 top + b/2 bottom + two verticals (one shared)
    d_ij = h / t
    two = section.multi_cell_torsion([A, A], [[d_ii, d_ij], [d_ij, d_ii]], T=500.0, G=27e9)
    check("two symmetric cells: q1 = q2", two["q"][0], two["q"][1], rtol=1e-12, source="derivation: symmetry")
    check("two symmetric cells: J = single box J", two["J"], beam.box(b, h, t, t)["J"], rtol=1e-12,
          source="derivation: no flow in the shared wall")
    check("two cells: T = Σ2Aq", 2 * A * two["q"].sum(), 500.0, rtol=1e-12, source="derivation: equilibrium")
    # unsymmetric three cells: the same θ' in every cell (compatibility) -- equation residual
    Ah = [0.02, 0.05, 0.03]
    dl = [[300.0, 60.0, 0.0], [60.0, 420.0, 80.0], [0.0, 80.0, 350.0]]
    three = section.multi_cell_torsion(Ah, dl, T=1000.0, G=27e9)
    q = three["q"]
    th = [(q[i] * dl[i][i] - sum(q[j] * dl[i][j] for j in range(3) if j != i)) / (2 * Ah[i] * 27e9) for i in range(3)]
    check("three cells compatibility: θ'1 = θ'3", th[0], th[2], rtol=1e-10, source="derivation: compatibility")
    check("three cells: θ' = T/(GJ)", three["twist_rate"], 1000.0 / (27e9 * three["J"]), rtol=1e-12,
          source="derivation")
    # very thin shared wall (δ → ∞): the two-cell box approaches the single outer box
    thin = section.multi_cell_torsion([A, A * 1.5], [[d_ii - h / t + 1e9, 1e9], [1e9, 1.5 * b / t + h / t + 1e9]])
    outer = section.multi_cell_torsion([2.5 * A], [[(b / 2 + 0.75 * b) * 2 / t + 2 * h / t]])
    check("shared wall δ → ∞: outer box J", thin["J"], outer["J"], rtol=1e-5, source="derivation: limit")
    expect_error("non-symmetric delta is rejected", section.multi_cell_torsion, [1, 1], [[1, 2], [3, 1]],
                 error=ValueError)
