"""Tests of the pressure module: thin/thick cylinder and sphere, interference fit, autofrettage."""
import math

import numpy as np

from aerokit.structures import pressure
from aerokit.verification import check, check_true, expect_error

HIJAZI3 = "Shigley 10th ed. Ch. 3, Hijazi CH3 lecture notes pp. 22-23 (read)"


def test_thin_wall():
    s = pressure.thin_cylinder(2e6, 0.5, 0.005)
    check("thin cylinder σθ = p r/t", s["hoop"], 2e6 * 0.5 / 0.005, source=HIJAZI3 + ", σt = P d/(2t)")
    check("thin cylinder σz = σθ/2", s["axial"], s["hoop"] / 2, source=HIJAZI3 + ", σl = P d/(4t)")
    k = pressure.thin_sphere(2e6, 0.5, 0.005)
    check("thin sphere σ = σθ(cylinder)/2", k["hoop"], s["hoop"] / 2, source="derivation: hemisphere equilibrium")
    expect_error("thin cylinder rejects t ≤ 0", pressure.thin_cylinder, 1e6, 0.5, 0.0, error=ValueError)


def test_lame_boundary_conditions_and_equilibrium():
    ri, ro, pi, po = 0.05, 0.08, 30e6, 5e6
    check("Lamé σr(ri) = −pi", pressure.lame_cylinder(ri, ro, pi, po, r=ri)["sr"], -pi,
          source="derivation: boundary condition")
    check("Lamé σr(ro) = −po", pressure.lame_cylinder(ri, ro, pi, po, r=ro)["sr"], -po,
          source="derivation: boundary condition")
    # equilibrium: dσr/dr + (σr − σθ)/r = 0 (central difference, h = 1e-6 m)
    h = 1e-6
    for r in (0.055, 0.065, 0.075):
        dsr = (pressure.lame_cylinder(ri, ro, pi, po, r=r + h)["sr"]
               - pressure.lame_cylinder(ri, ro, pi, po, r=r - h)["sr"]) / (2 * h)
        s = pressure.lame_cylinder(ri, ro, pi, po, r=r)
        check(f"Lamé equilibrium residual r = {r}", (dsr + (s["sr"] - s["st"]) / r) / pi, 0.0, atol=1e-7,
              source="derivation: dσr/dr + (σr − σθ)/r = 0")
    # one-to-one comparison with Shigley's general form in pi, po (read in the notes)
    r = 0.062
    st_shigley = (pi * ri ** 2 - po * ro ** 2 - ri ** 2 * ro ** 2 * (po - pi) / r ** 2) / (ro ** 2 - ri ** 2)
    sr_shigley = (pi * ri ** 2 - po * ro ** 2 + ri ** 2 * ro ** 2 * (po - pi) / r ** 2) / (ro ** 2 - ri ** 2)
    s = pressure.lame_cylinder(ri, ro, pi, po, r=r)
    check("Lamé σθ = Shigley general (pi, po) form", s["st"], st_shigley, rtol=1e-12, source=HIJAZI3)
    check("Lamé σr = Shigley general (pi, po) form", s["sr"], sr_shigley, rtol=1e-12, source=HIJAZI3)
    check("closed end σz = pi ri²/(ro² − ri²) (po = 0)",
          pressure.lame_cylinder(ri, ro, pi, r=r)["sz"], pi * ri ** 2 / (ro ** 2 - ri ** 2), source=HIJAZI3)
    # array input
    rr = np.linspace(ri, ro, 5)
    dz = pressure.lame_cylinder(ri, ro, pi, po, r=rr)
    check_true("Lamé with array input: σθ − σr = 2B/r²", np.allclose(dz["st"] - dz["sr"], 2 * dz["B"] / rr ** 2),
               source="derivation")


def test_lame_thin_wall_limit():
    p, rm = 10e6, 1.0
    for t in (1e-2, 1e-3, 1e-4):
        ri, ro = rm - t / 2, rm + t / 2
        st_inner = pressure.lame_cylinder(ri, ro, p, r=ri)["st"]
        # exact: σθ(ri) = p(rm/t + t/(4rm)) → relative difference of order t²/(4rm²)
        check(f"Lamé → thin wall (t/r = {t:g})", st_inner, p * rm / t, rtol=t ** 2 / 4 * 1.01 + 1e-12,
              source="derivation: (ri² + ro²)/(ro² − ri²) = rm/t + t/(4rm)")
    # the through-thickness average σθ is exactly p·ri/t (half-cylinder equilibrium)
    ri, ro = 0.05, 0.09
    rr = np.linspace(ri, ro, 20001)
    avg = np.trapezoid(pressure.lame_cylinder(ri, ro, p, r=rr)["st"], rr) / (ro - ri)
    check("Lamé average σθ = p ri/t (equilibrium)", avg, p * ri / (ro - ri), rtol=1e-7,
          source="derivation: ∫σθ dr = p·ri")


def test_lame_inner_surface_criteria():
    ri, ro, p = 0.04, 0.07, 50e6
    d = pressure.lame_inner_surface(ri, ro, p, ends="closed", yield_=500e6)
    A, B = pressure.lame_constants(ri, ro, p)
    check("closed ends, bore von Mises = √3·B/ri²", d["von_mises"], math.sqrt(3) * B / ri ** 2, rtol=1e-12,
          source="derivation: σz = (σr + σθ)/2 → deviatoric ±B/ri²")
    check("bore Tresca = 2B/ri² = 2p ro²/(ro² − ri²)", d["tresca"], 2 * p * ro ** 2 / (ro ** 2 - ri ** 2),
          rtol=1e-12, source="derivation")
    check("bore safety factor (von Mises)", d["n_von_mises"], 500e6 / d["von_mises"], source="definition")
    open_ends = pressure.lame_inner_surface(ri, ro, p, ends="open")
    check_true("open ends: von Mises larger than with closed ends", open_ends["von_mises"] > d["von_mises"],
               f"{open_ends['von_mises']:.4g} > {d['von_mises']:.4g}", source="derivation")
    gz = pressure.lame_cylinder(ri, ro, p, r=ri, ends="plane_strain", nu=0.3)
    check("plane strain σz = 2νA", gz["sz"], 2 * 0.3 * A, source="derivation: εz = 0")
    expect_error("Lamé rejects ri ≥ ro", pressure.lame_cylinder, 0.08, 0.05, 1e6, error=ValueError)
    expect_error("Lamé rejects an unknown end condition", pressure.lame_cylinder, 0.05, 0.08, 1e6, ends="x",
                 error=ValueError)


def test_thick_sphere():
    ri, ro, pi, po = 0.1, 0.15, 40e6, 2e6
    check("thick sphere σr(ri) = −pi", pressure.thick_sphere(ri, ro, pi, po, ri)["sr"], -pi, source="derivation")
    check("thick sphere σr(ro) = −po", pressure.thick_sphere(ri, ro, pi, po, ro)["sr"], -po, source="derivation")
    h, r = 1e-6, 0.12
    dsr = (pressure.thick_sphere(ri, ro, pi, po, r + h)["sr"]
           - pressure.thick_sphere(ri, ro, pi, po, r - h)["sr"]) / (2 * h)
    s = pressure.thick_sphere(ri, ro, pi, po, r)
    check("thick sphere equilibrium dσr/dr + 2(σr − σθ)/r = 0", (dsr + 2 * (s["sr"] - s["st"]) / r) / pi, 0.0,
          atol=1e-7, source="derivation: spherical equilibrium equation")
    t, rm, p = 1e-4, 1.0, 1e6
    check("thick sphere → thin sphere p r/(2t)", pressure.thick_sphere(rm - t / 2, rm + t / 2, p, r=rm)["st"],
          p * rm / (2 * t), rtol=1e-3, source="derivation: t/r → 0 limit")


def test_interference_fit():
    R, ri, ro, delta, E, nu = 0.025, 0.0, 0.05, 15e-6, 207e9, 0.29
    p_general = pressure.interference_pressure(delta, R, ri, ro, E, nu)
    p_same = pressure.interference_pressure_same(delta, R, ri, ro, E)
    check("interference fit general = same-material closed form (solid shaft)", p_general, p_same, rtol=1e-12,
          source=HIJAZI3 + " (same-material relation)")
    p2 = pressure.interference_pressure(delta, R, 0.01, ro, E, nu)
    check("interference fit general = same material (hollow shaft)", p2,
          pressure.interference_pressure_same(delta, R, 0.01, ro, E), rtol=1e-12, source=HIJAZI3)
    # compatibility: hub bore expansion − shaft surface contraction = δ (two materials)
    Eh, nuh, Es, nus = 71.7e9, 0.33, 207e9, 0.29
    p = pressure.interference_pressure(delta, R, 0.01, ro, Es, nus, Eh, nuh)
    uh = pressure.lame_cylinder(R, ro, pi=p, r=R, ends="open", E=Eh, nu=nuh)["u"]
    us = pressure.lame_cylinder(0.01, R, po=p, r=R, ends="open", E=Es, nu=nus)["u"]
    check("interference fit compatibility u_hub − u_shaft = δ", uh - us, delta, rtol=1e-12,
          source="derivation: Lamé displacements, open ends")
    # swapping the materials (shaft ↔ hub) changes the pressure, compatibility still holds
    pt = pressure.interference_pressure(delta, R, 0.01, ro, Eh, nuh, Es, nus)
    check_true("a soft hub gives a lower pressure", p < pt, f"{p:.4g} < {pt:.4g}", source="derivation")
    g = pressure.interference_stresses(delta, R, 0.0, ro, E, nu)
    check("solid shaft σθ = σr = −p", g["shaft_hoop"], -g["p"], source="derivation: Lamé ri → 0, B = 0")
    check("hub σθ(R) = p(ro² + R²)/(ro² − R²)", g["hub_hoop"], g["p"] * (ro ** 2 + R ** 2) / (ro ** 2 - R ** 2),
          rtol=1e-12, source=HIJAZI3 + " (Po = 0 form)")
    expect_error("interference fit rejects R ≥ ro", pressure.interference_pressure, delta, 0.06, 0.0, 0.05, E, nu,
                 error=ValueError)


def test_autofrettage():
    ri, ro, sy = 0.05, 0.1, 800e6
    p_first = pressure.autofrettage_pressure(ri, ro, sy, c=ri)
    # pressure at which the bore Tresca stress of a closed-end Lamé cylinder equals σy
    tresca1 = pressure.lame_inner_surface(ri, ro, 1.0, ends="closed")["tresca"]
    check("autofrettage c = ri → Lamé first-yield pressure", p_first, sy / tresca1, rtol=1e-12,
          source="derivation: Tresca, σz intermediate principal stress")
    check("autofrettage c = ro → σy ln(ro/ri)", pressure.autofrettage_pressure(ri, ro, sy, c=ro), sy * math.log(2),
          rtol=1e-12, source="derivation: fully plastic cylinder (Hill 1950 Ch. V form)")
    expect_error("autofrettage rejects c > ro", pressure.autofrettage_pressure, ri, ro, sy, 0.2, error=ValueError)
