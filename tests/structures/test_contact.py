"""Tests of the contact module: Hertz sphere, cylinder, elliptical (crossed cylinders)."""
import math

from scipy import integrate

from aerokit.structures import contact
from aerokit.verification import check, check_true, expect_error

TUTORIAL = "Budynas & Nisbett, Shigley Tutorial 3-19 'Hertz Contact Stresses' (read)"
E_S, NU_S = 207e9, 0.3


def test_sphere():
    F, R1 = 500.0, 0.0125
    d = contact.hertz_sphere(F, R1, math.inf, E_S, NU_S, E_S, NU_S)
    check("sphere: p0 = 1.5 × mean pressure", d["p0"], 1.5 * d["p_avg"],
          source="derivation: semi-ellipsoidal distribution")
    check("sphere: δ = a²/R", d["delta"], d["a"] ** 2 / R1, source="derivation")
    # Shigley Eq. 3-68 form (with diameters): a = [3F/8 · ((1−ν1²)/E1 + (1−ν2²)/E2)/(1/d1 + 1/d2)]^(1/3)
    d1, d2 = 0.025, 0.04
    a_sh = (3 * F / 8 * (2 * (1 - NU_S ** 2) / E_S) / (1 / d1 + 1 / d2)) ** (1 / 3)
    check("sphere-sphere a = Shigley Eq. 3-68 form",
          contact.hertz_sphere(F, d1 / 2, d2 / 2, E_S, NU_S, E_S, NU_S)["a"], a_sh, rtol=1e-12, source=TUTORIAL)
    check("sphere pmax = 3F/(2πa²) (Eq. 3-69)", d["p0"], 3 * F / (2 * math.pi * d["a"] ** 2), source=TUTORIAL)
    # sphere-plane is the R2 → ∞ limit of sphere-sphere
    large = contact.hertz_sphere(F, R1, 1e9, E_S, NU_S, E_S, NU_S)
    check("sphere-sphere R2 → ∞ = sphere-plane (a)", large["a"], d["a"], rtol=1e-9, source="derivation: limit")
    check("sphere-sphere R2 → ∞ = sphere-plane (p0)", large["p0"], d["p0"], rtol=1e-9, source="derivation: limit")
    seat = contact.hertz_sphere(F, R1, -0.02, E_S, NU_S, E_S, NU_S)
    check_true("concave seat: contact radius larger than on a plane", seat["a"] > d["a"], f"{seat['a']:.4g}",
               source="derivation")
    check("sphere (ν = 0.3) critical depth ≈ 0.48a", d["z_tau_max"] / d["a"], 0.48, atol=0.005,
          source=TUTORIAL + " p. 3: 'approximately 0.48a below the sphere surface'")
    check("sphere (ν = 0.3) τmax ≈ 0.31 p0", d["tau_max"] / d["p0"], 0.31, rtol=0.01,
          source="Johnson 1985 -- search summary only (USPTO text); book not read")
    s0 = contact.sphere_stresses(1.0, 1.0, 0.0, 0.3)
    check("sphere surface σz = −p0", s0["sz"], -1.0, source="derivation: Eq. 3-71, ζ = 0")
    check("sphere surface σr = −(1+2ν)p0/2", s0["sr"], -(1 + 2 * 0.3) / 2, rtol=1e-12,
          source="derivation: Eq. 3-70, ζ = 0")
    expect_error("sphere rejects F ≤ 0", contact.hertz_sphere, 0.0, R1, math.inf, E_S, NU_S, E_S, NU_S,
                 error=ValueError)
    expect_error("seat smaller than the sphere is rejected", contact.hertz_sphere, F, 0.02, -0.01, E_S, NU_S, E_S,
                 NU_S, error=ValueError)


def test_cylinder_budynas_example():
    # Example T3.19.1: 6 in cast-iron wheel (E 14.5 Mpsi, ν 0.211), 2 in wide, on a steel plane
    # (E 30 Mpsi, ν 0.292), F = 800 lbf. Units in/lbf/psi (the functions are unit-agnostic).
    d = contact.hertz_cylinder(800.0, 2.0, 3.0, math.inf, 14.5e6, 0.211, 30e6, 0.292)
    check("T3.19.1 b = 1.214e-2 in", d["b"], 1.214e-2, rtol=5e-4, source=TUTORIAL + " p. 8")
    check("T3.19.1 pmax = 20 980 psi", d["p0"], 20980, rtol=5e-4, source=TUTORIAL + " p. 8")
    s = contact.cylinder_stresses(d["p0"], d["b"], 0.786 * d["b"], 0.211)
    # source values are rounded to 4 significant digits → rtol 1e-3
    check("T3.19.1 σx(0.786b) = −4302 psi", s["sx"], -4302, rtol=1e-3, source=TUTORIAL + " p. 8")
    check("T3.19.1 σy(0.786b) = −3895 psi", s["sy"], -3895, rtol=1e-3, source=TUTORIAL + " p. 8")
    check("T3.19.1 σz(0.786b) = −16 490 psi", s["sz"], -16490, rtol=1e-3, source=TUTORIAL + " p. 8")
    check("T3.19.1 τ(0.786b) = 6298 psi", s["tau"], 6298, rtol=1e-3, source=TUTORIAL + " p. 9")
    s2 = contact.cylinder_stresses(d["p0"], d["b"], 0.015, 0.211)
    check("T3.19.1 σx(0.015 in) = −3133 psi", s2["sx"], -3133, rtol=1e-3, source=TUTORIAL + " p. 10")
    check("T3.19.1 σy(0.015 in) = −1652 psi", s2["sy"], -1652, rtol=1e-3, source=TUTORIAL + " p. 10")
    check("T3.19.1 σz(0.015 in) = −13 200 psi", s2["sz"], -13200, rtol=1e-3, source=TUTORIAL + " p. 10")
    check("T3.19.1 τ(0.015 in) = 5774 psi", s2["tau"], 5774, rtol=1e-3, source=TUTORIAL + " p. 10")
    # At ν = 0.211 the overall maximum shear lies on the (σz − σx)/2 branch, closer to the surface; the source
    # takes 0.786b from the ν = 0.3 chart, so the overall value must exceed 6298.
    check_true("ν = 0.211: overall τmax ≥ value at 0.786b", d["tau_max"] >= s["tau"] - 1e-9,
               f"{d['tau_max']:.1f} psi", source="derivation: piecewise definition of Eq. 3-77")


def test_cylinder_general():
    d = contact.hertz_cylinder(1e4, 0.02, 0.01, 0.015, E_S, NU_S, E_S, NU_S)
    check("cylinder (ν = 0.3) critical depth 0.786b", d["z_tau_max"] / d["b"], 0.786, atol=5e-4,
          source=TUTORIAL + " p. 6: 'ζ = z/b = 0.786 and 0.3pmax'")
    check("cylinder (ν = 0.3) τmax = 0.3 pmax", d["tau_max"] / d["p0"], 0.3, rtol=2e-3, source=TUTORIAL + " p. 6")
    check("cylinder p0 = 2F'/(πb)", d["p0"], 2 * (1e4 / 0.02) / (math.pi * d["b"]), source=TUTORIAL + " Eq. 3-74")
    flat = contact.hertz_cylinder(1e4, 0.02, 0.01, math.inf, E_S, NU_S, E_S, NU_S)
    large = contact.hertz_cylinder(1e4, 0.02, 0.01, 1e9, E_S, NU_S, E_S, NU_S)
    check("cylinder R2 → ∞ = cylinder-plane", large["b"], flat["b"], rtol=1e-9, source="derivation: limit")
    s = contact.cylinder_stresses(1.0, 1.0, 0.0, 0.3)
    check("cylinder surface σy = σz = −p0", s["sy"], s["sz"], source="derivation: ζ = 0")
    expect_error("cylinder rejects L ≤ 0", contact.hertz_cylinder, 1e3, 0.0, 0.01, math.inf, E_S, NU_S, E_S, NU_S,
                 error=ValueError)


def test_elliptic():
    F, R = 200.0, 0.02
    sphere = contact.hertz_sphere(F, R, math.inf, E_S, NU_S, E_S, NU_S)
    es = contact.e_star(E_S, NU_S, E_S, NU_S)
    near = contact.hertz_elliptic(F, 1 / (2 * R), 1 / (2 * R * (1 - 1e-7)), es)
    check("elliptical A ≈ B → sphere-plane a", near["a"], sphere["a"], rtol=1e-5, source="derivation: e → 0 limit")
    check("elliptical A ≈ B → sphere-plane p0", near["p0"], sphere["p0"], rtol=1e-5, source="derivation")
    check("elliptical A ≈ B → sphere-plane δ", near["delta"], sphere["delta"], rtol=1e-5, source="derivation")
    equal = contact.cross_cylinder(F, R, R, E_S, NU_S, E_S, NU_S)
    check("equal crossed cylinders = sphere of radius R on a plane", equal["a"], sphere["a"], rtol=1e-12,
          source="derivation: A = B = 1/(2R)")
    c = contact.cross_cylinder(F, 0.05, 0.01, E_S, NU_S, E_S, NU_S)
    check_true("crossed cylinders: major axis along the larger radius (a > b)", c["a"] > c["b"], source="derivation")
    check("elliptical: F = (2/3)π a b p0", 2 / 3 * math.pi * c["a"] * c["b"] * c["p0"], F, rtol=1e-12,
          source="derivation: semi-ellipsoidal pressure")
    # Independent check: Boussinesq surface displacement of the elliptical pressure, w(P) = (1/πE*)∬p/ρ dA;
    # inside the contact w = δ − A x² − B y² must hold (Hertz condition). Polar integral, singularity at P.
    # (An earlier attempt with the Re = √(R'R'') approximation was 3.3 % off; that approximation is crude
    # without its correction factor.)
    a, b, p0, A, B = c["a"], c["b"], c["p0"], 1 / (2 * 0.05), 1 / (2 * 0.01)

    def w(x0, y0):
        def smax(t):
            cx, cy = math.cos(t), math.sin(t)
            qa = (cx / a) ** 2 + (cy / b) ** 2
            qb = 2 * (x0 * cx / a ** 2 + y0 * cy / b ** 2)
            qc = (x0 / a) ** 2 + (y0 / b) ** 2 - 1
            return (-qb + math.sqrt(qb * qb - 4 * qa * qc)) / (2 * qa)

        def p(s, t):
            v = 1 - ((x0 + s * math.cos(t)) / a) ** 2 - ((y0 + s * math.sin(t)) / b) ** 2
            return p0 * math.sqrt(max(v, 0.0))
        return integrate.dblquad(p, 0, 2 * math.pi, 0, smax, epsrel=1e-10)[0] / (math.pi * es)

    w0 = w(0.0, 0.0)
    check("elliptical δ = Boussinesq displacement (centre)", w0, c["delta"], rtol=1e-8,
          source="derivation: numerical Boussinesq")
    check("elliptical w(0.5a, 0) = δ − A x²", w0 - w(0.5 * a, 0.0), A * (0.5 * a) ** 2, rtol=1e-8,
          source="derivation: numerical Boussinesq")
    check("elliptical w(0, 0.5b) = δ − B y²", w0 - w(0.0, 0.5 * b), B * (0.5 * b) ** 2, rtol=1e-8,
          source="derivation: numerical Boussinesq")
    expect_error("elliptical rejects a negative curvature", contact.hertz_elliptic, F, -1.0, 2.0, es,
                 error=ValueError)
