"""Tests of aerokit.aero.drag: Anderson flat-plate examples, reference-temperature method, wetted areas,
component build-up, polar, K_LD comparison and a King Air 350-class build-up.

Book values are from J. D. Anderson, Fundamentals of Aerodynamics, 6th ed. (2017), read from the user's
PDF on 2026-10-25 (PDF page = book page + 23). Values are compared at the precision printed in the book.
Where the book doubles or combines already-rounded intermediates the full-precision result can differ
in the last printed digit; those cases are checked with a stated tolerance and the reason is given.
"""
import math

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from aerokit.aero import drag as D
from aerokit.aero.geometry import naca4
from aerokit.aero.propulsion import Turboprop
from aerokit.verification import check, check_true, expect_error

AND = "Anderson 2017"


def g3(x: float) -> str:
    return f"{x:.3g}"


# ----------------------------------------------------------------------------- Anderson Ch. 4 examples
def test_example_4_8_laminar():
    Re, c = 3.1e6, 1.5
    src = f"{AND} Example 4.8, PDF p. 405"
    check_true("δ_lam = 0.00426 m (as printed)", g3(D.bl_thickness_laminar(c, Re)) == "0.00426",
               D.bl_thickness_laminar(c, Re), source=src)
    cf = D.cf_laminar(Re)
    check_true("Cf_lam = 7.54e-4 (as printed)", g3(cf) == "0.000754", cf, source=src)
    check_true("net Cf_lam = 0.0015 (as printed, 2 s.f.)", f"{2 * cf:.2g}" == "0.0015", 2 * cf, source=src)
    check("cf_mixed with Re_cr >= Re is fully laminar", D.cf_mixed(Re, 1e7), cf, rtol=1e-15, source="Eq. 4.92")


def test_example_4_9_turbulent():
    Re, c = 3.1e6, 1.5
    src = f"{AND} Example 4.9, PDF p. 406"
    d = D.bl_thickness_turbulent(c, Re)
    check_true("δ_turb = 0.0279 m (as printed)", g3(d) == "0.0279", d, source=src)
    cf = D.cf_turbulent(Re)
    check_true("Cf_turb = 0.00372 (as printed)", g3(cf) == "0.00372", cf, source=src)
    # the book doubles the rounded 0.00372 → 0.00744; full precision 2·0.0037235 = 0.007447
    check("net Cf_turb = 2·(printed 0.00372) = 0.00744", 2 * round(cf, 5), 0.00744, rtol=1e-12, source=src)
    check("net Cf_turb full precision vs printed 0.00744", 2 * cf, 0.00744, rtol=1.5e-3,
          source=src + " (book doubles a rounded value)")
    check("cf_mixed(Re, None) = fully turbulent", D.cf_mixed(Re, None), cf, rtol=1e-15, source="definition")
    check("Example 19.1a: Cf(1.36e7) = 2.77e-3", float(g3(D.cf_turbulent(1.36e7))), 2.77e-3, rtol=1e-12,
          source=f"{AND} Example 19.1, PDF p. 1077")
    check("Example 19.1a: Re^(1/5) = 26.71", 1.36e7 ** 0.2, 26.71, rtol=2e-4, source=f"{AND} PDF p. 1077")


def test_transition_location_p408():
    src = f"{AND} Sec. 4.12.3, Eq. 4.89, PDF p. 408"
    x50 = D.transition_location(5e5, 50.0, 1.23, 1.789e-5)
    x100 = D.transition_location(5e5, 100.0, 1.23, 1.789e-5)
    check_true("x_cr = 0.145 m at 50 m/s", g3(x50) == "0.145", x50, source=src)
    check_true("x_cr = 0.0727 m at 100 m/s", g3(x100) == "0.0727", x100, source=src)
    check("doubling V halves x_cr", x100, x50 / 2, rtol=1e-12, source=src)


def test_example_4_10_mixed():
    src = f"{AND} Example 4.10, PDF pp. 408–410"
    Re, Rcr = 3.1e6, 5e5
    check_true("x1/c = 0.1613", f"{Rcr / Re:.4f}" == "0.1613", Rcr / Re, source=src)
    check_true("(Cf,1)lam = 0.00188", g3(D.cf_laminar(Rcr)) == "0.00188", D.cf_laminar(Rcr), source=src)
    check_true("(Cf,1)turb = 0.00536", g3(D.cf_turbulent(Rcr)) == "0.00536", D.cf_turbulent(Rcr), source=src)
    cf = D.cf_mixed(Re, Rcr)
    # book: 0.1613(0.00188) + 0.00372 − 0.1613(0.00536) = 0.003158 with rounded intermediates;
    # full precision gives 0.0031613 (+0.10 %)
    check("Cf (one side) = 0.003158 within rounding of intermediates", cf, 0.003158, rtol=1.5e-3, source=src)
    check_true("net Cf = 0.0063 (as printed, 2 s.f.)", f"{2 * cf:.2g}" == "0.0063", 2 * cf, source=src)


def test_example_4_11_mixed():
    src = f"{AND} Example 4.11, PDF p. 411"
    Re, Rcr = 3.1e6, 1e6
    check_true("x1/c = 0.3226", f"{Rcr / Re:.4f}" == "0.3226", Rcr / Re, source=src)
    check("(Cf,1)lam = 0.001328", D.cf_laminar(Rcr), 0.001328, rtol=1e-12, source=src)
    check_true("(Cf,1)turb = 0.004669", f"{D.cf_turbulent(Rcr):.4g}" == "0.004669", D.cf_turbulent(Rcr), source=src)
    cf = D.cf_mixed(Re, Rcr)
    # book 0.002642 uses (Cf,c)turb = 0.00372 (3 s.f.); full precision 0.0026457 → net 0.00529 vs printed 0.00528
    check("Cf (one side) = 0.002642 within rounding of intermediates", cf, 0.002642, rtol=2e-3, source=src)
    check("net Cf vs printed 0.00528", 2 * cf, 0.00528, rtol=3e-3, source=src + " (rounded intermediates)")
    drop = 1 - cf / D.cf_mixed(Re, 5e5)
    check_true("Re_cr 5e5 → 1e6 lowers Cf by about 16 %", f"{drop:.2f}" == "0.16", drop, source=src)


# ----------------------------------------------------------------------------- compressibility
def test_reference_temperature_examples_18_2_and_19_2():
    src = f"{AND} Examples 18.2 (PDF pp. 1057–1058) and 19.2 (PDF p. 1078)"
    check("T*/Te = 2.1275 (Eq. 18.53)", D.reference_temperature_ratio(2.94, 2.467), 2.1275, rtol=5e-5, source=src)
    rc = D.reference_conditions(2.94, 288.0, 2.467)
    check_true("μ*/μ0 = 1.709 (Sutherland, S = 110 K)", f"{rc['mu_ratio']:.4g}" == "1.709", rc["mu_ratio"],
               source=src)
    # book: ρ* = 0.574 from p = 1.01e5 Pa against ρ∞ = 1.22 → ρ*/ρe = 0.4705; here Te/T* = 0.4700
    check("ρ*/ρe = 0.574/1.22", rc["rho_ratio"], 0.574 / 1.22, rtol=2e-3, source=src)
    Re_star = 1.36e8 * rc["Re_ratio"]
    check("Re*_c = 3.754e7", Re_star, 3.754e7, rtol=5e-3, source=src + " (book uses rounded ρ*, Re)")
    q_S = 0.5 * 1.22 * 1000.0 ** 2 * 40.0
    Df_turb = D.cf_flat_plate(1.36e8, None, M=2.94, Te=288.0, Tw_Te=2.467) * q_S
    check("turbulent friction drag (one side) = 25 945 N", Df_turb, 25945.0, rtol=1e-2, source=src)
    Df_lam = D.cf_flat_plate(1.36e8, 2e8, M=2.94, Te=288.0, Tw_Te=2.467) * q_S
    check("laminar friction drag (one side) = 2488 N", Df_lam, 2488.0, rtol=1e-2, source=src)
    check_true("C*_f turbulent = 2.26e-3 at the printed Re*", g3(D.cf_turbulent(3.754e7)) == "0.00226",
               D.cf_turbulent(3.754e7), source=src)
    check_true("C*_f laminar = 2.167e-4 at the printed Re*", f"{D.cf_laminar(3.754e7):.4g}" == "0.0002167",
               D.cf_laminar(3.754e7), source=src)


def test_compressibility_limits():
    check("M = 0, adiabatic wall: no correction", D.cf_flat_plate(1e7, 5e5, M=0.0), D.cf_mixed(1e7, 5e5),
          rtol=1e-15, source="Eq. 18.53 at Me = 0, Tw = Te")
    check("adiabatic wall ratio from Eq. 8.40/16.49", D.adiabatic_wall_ratio(2.0, recovery=0.892),
          1 + 0.892 * 0.2 * 4.0, rtol=1e-12, source=f"{AND} Eqs. 8.40, 18.56")
    check_true("turbulent recovery factor Pr^(1/3) = 0.892", f"{D.PR_AIR ** (1 / 3):.3f}" == "0.892",
               source=f"{AND} PDF p. 1079")
    lo = D.cf_flat_plate(1e7, None, M=0.5, Te=250.0)
    check_true("compressibility lowers Cf at M = 0.5 (small effect)", 0.95 < lo / D.cf_turbulent(1e7) < 1.0,
               lo / D.cf_turbulent(1e7), source=f"{AND} Fig. 19.1 trend, PDF p. 1077")
    check_true("Raymer Cf model higher than Anderson's at Re = 1e8 (reported, unverified model)",
               D.cf_turbulent_raymer(1e8) > D.cf_turbulent(1e8), (D.cf_turbulent_raymer(1e8), D.cf_turbulent(1e8)))
    expect_error("Re <= 0 raises", D.cf_turbulent, 0.0, error=ValueError)
    expect_error("unknown Cf model raises", D.cf_flat_plate, 1e6, model="x", error=ValueError)


# ----------------------------------------------------------------------------- property tests
@settings(max_examples=200, deadline=None)
@given(st.floats(1e3, 1e9), st.floats(1.001, 100.0))
def test_cf_monotone_decreasing_in_re(Re, k):
    for name, f in (("laminar", D.cf_laminar), ("turbulent", D.cf_turbulent),
                    ("raymer turbulent", D.cf_turbulent_raymer),
                    ("compressible turbulent M 0.5", lambda r: D.cf_flat_plate(r, None, M=0.5, Te=250.0))):
        assert f(Re * k) < f(Re), name


@settings(max_examples=200, deadline=None)
@given(st.floats(2e4, 5e6), st.floats(1.0, 1e3))
def test_mixed_between_laminar_and_turbulent(Rcr, k):
    Re = Rcr * k
    cf = D.cf_mixed(Re, Rcr)
    assert D.cf_laminar(Re) * (1 - 1e-12) <= cf <= D.cf_turbulent(Re) * (1 + 1e-12)


def test_mixed_continuous_at_transition():
    check("Eq. 4.92 continuous at Re = Re_cr", D.cf_mixed(5e5 * (1 + 1e-9), 5e5), D.cf_laminar(5e5), rtol=1e-6,
          source="derivation: x1/c → 1")


# ----------------------------------------------------------------------------- geometry
def test_wetted_areas():
    x, y = naca4("0012", n=121, closed_trailing_edge=True)
    poly = float(np.sum(np.hypot(np.diff(x), np.diff(y))))
    check("perimeter = NACA 0012 polygon of geometry.naca4", D.airfoil_perimeter_ratio(0.12, n=121), poly,
          rtol=1e-12, source="same thickness equation (Abbott & von Doenhoff)")
    check("perimeter of a flat plate = 2c", D.airfoil_perimeter_ratio(0.0), 2.0, rtol=1e-12, source="definition")
    check("perimeter fit vs Raymer 1.977 + 0.52 t/c at t/c 0.12 (cross-check of an unverified fit)",
          D.wetted_area_lifting(1.0, 0.12), D.wetted_area_lifting(1.0, 0.12, "raymer"), rtol=1e-3,
          source="derivation vs commonly quoted fit")
    ex = D.exposed_area(10.0, 10.0, 1.0, 0.5)
    check("rectangular wing: S_exp = S − w c", ex["S_exposed"], 10.0 - 0.5 * 1.0, rtol=1e-12, source="derivation")
    check("rectangular panel MAC = c", ex["MAC_exposed"], 1.0, rtol=1e-12, source="derivation")
    ex0 = D.exposed_area(20.0, 8.0, 0.4, 0.0)
    check("zero body width: S_exp = S", ex0["S_exposed"], 20.0, rtol=1e-12, source="derivation")
    check("zero-length cones are flat end discs: π d L + 2 π r²", D.wetted_area_body(10.0, 1.0, 0.0, 0.0),
          math.pi * 10.0 + 2 * math.pi * 0.25, rtol=1e-12, source="derivation")
    cone = D.wetted_area_body(3.0, 2.0, 3.0, 0.0)
    check("cone + flat base disc: π r √(r² + L²) + π r²", cone, math.pi * math.hypot(1.0, 3.0) + math.pi, rtol=1e-12,
          source="derivation")
    expect_error("nose + tail > length raises", D.wetted_area_body, 5.0, 1.0, 3.0, 3.0, error=ValueError)
    expect_error("body wider than span raises", D.exposed_area, 10.0, 10.0, 1.0, 20.0, error=ValueError)


def test_form_and_interference_factors():
    check("fuselage FF at f = 10", D.form_factor_body(10.0), 1 + 0.06 + 0.025, rtol=1e-12,
          source="formula as implemented (Raymer, unverified)")
    check("nacelle FF at f = 5", D.form_factor_nacelle(5.0), 1.07, rtol=1e-12, source="formula as implemented")
    check("lifting FF of a flat plate at M where 1.34 M^0.18 = 1", D.form_factor_lifting(0.0, 0.3, (1 / 1.34) ** (1 / 0.18)),
          1.0, rtol=1e-12, source="formula as implemented")
    check("Q midpoint of the low-wing range", D.interference_factor("wing_low_unfilleted", "mid"), 1.25, rtol=1e-12)
    expect_error("unknown Q kind raises", D.interference_factor, "canard", error=ValueError)


# ----------------------------------------------------------------------------- build-up, polar, K_LD
def test_buildup_bookkeeping():
    plate = D.Component("plate", "lifting", Swet=20.0, length=2.0, FF=1.0, Q=1.0, Re_transition=None)
    b = D.component_buildup([plate], 50.0, 0.0, S_ref=10.0)
    from aerokit.aero.atmosphere import isa
    a = isa(0.0)
    Re = 50.0 * 2.0 / a["nu"]
    check("single flat plate: CD0 = Cf Swet/Sref", b.CD0, D.cf_flat_plate(Re, None, 50 / a["a"], a["T"]) * 2.0,
          rtol=1e-12, source="definition")
    comps = [plate, D.nacelle("nac", 3.0, 0.8, 0.5, 1.0, count=2, Q=1.3)]
    b2 = D.component_buildup(comps, 120.0, 3000.0, S_ref=10.0, misc=[("upsweep", 0.05)], leakage_fraction=0.05)
    parts = sum(r.CD0 for r in b2.rows) + sum(c for _, c in b2.misc)
    check("CD0 = (Σ rows + misc)(1 + leakage)", b2.CD0, parts * 1.05, rtol=1e-12, source="definition")
    check("shares sum to 1", sum(float(r["share"]) for r in b2.as_rows()), 1.0, rtol=1e-12, source="definition")
    check("count multiplies wetted area", b2.rows[1].Swet, 2 * comps[1].Swet, rtol=1e-12, source="definition")
    expect_error("empty component list raises", D.component_buildup, [], 50.0, 0.0, S_ref=10.0, error=ValueError)


def test_polar_oswald_and_kld():
    check_true("Oswald Eq. 6.25 at AR 9 = 0.783 (rehearsal value)", f"{D.oswald_e(9.0).value:.3f}" == "0.783",
               D.oswald_e(9.0), source=f"{AND} Eq. 6.25, PDF p. 538; docs/04")
    check_true("swept-wing estimate is flagged unverified", not D.oswald_e(9.0, 0.6, "raymer_swept").verified)
    k = D.compare_with_kld(9.0, 5.5, 11.0)
    check_true("rehearsal K_LD estimate = 14.1", f"{k.LD_kld:.1f}" == "14.1", k.LD_kld, source="docs/04 §1")
    plate = D.Component("plate", "lifting", Swet=60.0, length=1.8, FF=1.3, Q=1.0)
    b = D.component_buildup([plate], 140.0, 5000.0, S_ref=27.5)
    p = D.drag_polar_from_buildup(b, 9.0)
    CD0, e, LD = p[:3]
    check("L/Dmax = 1/(2√(CD0 K))", LD, 0.5 * math.sqrt(math.pi * e * 9.0 / CD0), rtol=1e-12,
          source=f"derivation from {AND} Eq. 6.24")
    check("CL* = √(CD0/K)", p.CL_LDmax, math.sqrt(CD0 * math.pi * e * 9.0), rtol=1e-12, source="derivation")
    ac = D.aircraft_from_polar(p, "test", 5974 * 9.80665, Turboprop(P_sl=1.667e6))
    check("Aircraft.LD_max equals the polar's", ac.LD_max, LD, rtol=1e-12, source="same Eq. 6.24")
    expect_error("passing CD0 twice raises", D.aircraft_from_polar, p, "x", 5e4, Turboprop(P_sl=1e6), CD0=0.02,
                 error=ValueError)
    kc = D.compare_with_kld(9.0, 5.5, 11.0, p)
    check("K_LD implied reproduces the build-up", kc.KLD_implied * math.sqrt(9.0 / 5.5), LD, rtol=1e-12,
          source="definition")


# ----------------------------------------------------------------------------- King Air 350-class build-up
# Every input with its source. [W] = Wikipedia "Beechcraft Super King Air", Specifications (350i column),
# read 2026-10-25 via WebFetch (table garbled in the fetch, values matched by column; not checked against a
# primary source). [U] = UIUC "Incomplete Guide to Airfoil Usage" (m-selig.ae.illinois.edu/ads/aircraft.html),
# read 2026-10-25. [D4] = docs/04 §2 ([A] source there). [A] = assumption of this test.
KING_AIR = {
    "S_ref": (28.8, "D4: King Air 350 wing area 28.8 m²"),
    "b": (17.65, "W: wingspan 57 ft 11 in"),
    "taper": (0.45, "A"),
    "wing_t_c": (0.15, "A: mean of root NACA 23018 / tip NACA 23012 [U]"),
    "x_c_max": (0.30, "derivation: max thickness of the 4-digit/230xx thickness law at x/c = 0.2995"),
    "fuselage_length": (14.22, "W: overall length 46 ft 8 in, used as body length (A: upper bound)"),
    "fuselage_diameter": (1.60, "A: equivalent circular diameter"),
    "nose_length": (2.5, "A"),
    "tail_cone_length": (5.5, "A"),
    "wing_Q": (1.10, "A: low end of the unverified low-wing range 1.1–1.4"),
    "nacelle_length": (4.0, "A"),
    "nacelle_diameter": (0.80, "A"),
    "nacelle_nose_tail": ((0.8, 1.5), "A"),
    "nacelle_Q": (1.5, "unverified Raymer table: nacelle directly on the wing"),
    "htail": ((6.5, 4.5, 0.6, 0.12), "A: S [m²], AR, taper, t/c (T-tail)"),
    "vtail": ((4.0, 2.3, 0.6, 0.12, 30.0), "A: S [m²], height [m], taper, t/c, sweep of max-t line [deg]"),
    "tail_Q": (1.04, "unverified Raymer table: conventional tail (T-tail treated as conventional, A)"),
    "upsweep": (0.14, "A: aft-fuselage upsweep [rad] (≈ 8°)"),
    "leakage_fraction": (0.05, "A: no source read"),
    "Re_transition": (5e5, "A: Anderson's 'very conservative' example value, PDF p. 411"),
    "V": (558 / 3.6, "D4: King Air 350 cruise 558 km/h"),
    "h": (7000.0, "A: cruise altitude"),
}


def _v(key):
    return KING_AIR[key][0]


def king_air(S_ref=None, AR=None, taper=None, cf_model="anderson"):
    S = _v("S_ref") if S_ref is None else S_ref
    AR = _v("b") ** 2 / _v("S_ref") if AR is None else AR
    lam = _v("taper") if taper is None else taper
    Rcr, d = _v("Re_transition"), _v("fuselage_diameter")
    hs, har, hl, htc = _v("htail")
    vs, vh, vl, vtc, vsw = _v("vtail")
    nn, nt = _v("nacelle_nose_tail")
    comps = [
        D.lifting_surface("wing", S, AR, lam, _v("wing_t_c"), body_width=d, x_c_max=_v("x_c_max"), Q=_v("wing_Q"),
                          Re_transition=Rcr),
        D.body("fuselage", _v("fuselage_length"), d, _v("nose_length"), _v("tail_cone_length"), Re_transition=Rcr),
        D.nacelle("nacelles", _v("nacelle_length"), _v("nacelle_diameter"), nn, nt, count=2, Q=_v("nacelle_Q"),
                  Re_transition=Rcr),
        D.lifting_surface("horizontal tail", hs, har, hl, htc, Q=_v("tail_Q"), Re_transition=Rcr),
        D.lifting_surface("vertical tail", vs, vh ** 2 / vs, vl, vtc, sweep_max_t=math.radians(vsw), Q=_v("tail_Q"),
                          Re_transition=Rcr),
    ]
    misc = [("aft-fuselage upsweep", D.upsweep_drag_area(_v("upsweep"), math.pi * d ** 2 / 4))]
    b = D.component_buildup(comps, _v("V"), _v("h"), S_ref=S, misc=misc, leakage_fraction=_v("leakage_fraction"),
                            cf_model=cf_model)
    return D.drag_polar_from_buildup(b, AR)


def test_king_air_350_class_buildup(capsys):
    polar = king_air()
    kc = D.compare_with_kld(polar.AR, 5.5, 11.0, polar)
    rehearsal = king_air(S_ref=27.5, AR=9.0, taper=0.5)          # docs/04 §1/§3 wing on the same body
    kr = D.compare_with_kld(9.0, 5.5, 11.0, rehearsal)
    raymer_cf = king_air(cf_model="raymer")
    with capsys.disabled():
        print("\nKing Air 350-class build-up (V = 155 m/s, h = 7000 m)")
        for r in polar.buildup.as_rows():
            print("  " + "  ".join(f"{k}={v:.4g}" if isinstance(v, float) else f"{v}" for k, v in r.items()))
        print(f"  CD0 {polar.CD0:.4f}  e {polar.e:.3f}  L/Dmax {polar.LD_max:.2f}  Swet/Sref "
              f"{polar.buildup.Swet_Sref:.2f}  AR {polar.AR:.2f}  M {polar.buildup.M:.3f}")
        print(f"  K_LD 11, Swet/Sref 5.5: {kc.LD_kld:.2f}; with build-up Swet/Sref: {kc.LD_kld_buildup_wetted:.2f}; "
              f"implied K_LD {kc.KLD_implied:.2f}")
        print(f"  Raymer Cf model: CD0 {raymer_cf.CD0:.4f}  L/Dmax {raymer_cf.LD_max:.2f}")
        print(f"  rehearsal wing (S 27.5, AR 9, taper 0.5): CD0 {rehearsal.CD0:.4f}  e {rehearsal.e:.3f}  L/Dmax "
              f"{rehearsal.LD_max:.2f} vs K_LD 14.07 (diff {kr.rel_difference:+.1%}); Swet/Sref "
              f"{rehearsal.buildup.Swet_Sref:.2f}")
    check_true("Oswald e within Anderson's typical 0.7–0.85", 0.70 <= polar.e <= 0.85, polar.e,
               source=f"{AND} PDF p. 538")
    # sanity band only — NOT a literature value for the King Air 350 (none was read in this session)
    check_true("CD0 in a broad sanity band 0.015–0.035", 0.015 < polar.CD0 < 0.035, polar.CD0,
               source="sanity band, no source")
    check_true("Swet/Sref in a broad sanity band 4–6.5", 4.0 < polar.buildup.Swet_Sref < 6.5,
               polar.buildup.Swet_Sref, source="sanity band, no source")
    check_true("Raymer Cf model gives a higher CD0 than Anderson's (reported)", raymer_cf.CD0 > polar.CD0,
               (raymer_cf.CD0, polar.CD0))
