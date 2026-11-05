"""Tests of aerokit.aero.loads: 14 CFR 23.333/335/337/341/473/725 and 25.337/341 values and derivation checks.

Regulation text: 2011 CFR Title 14 Vol. 1 (govinfo.gov), read 2026-10-25.
"""
import math

import numpy as np

from aerokit.aero import loads as Y
from aerokit.aero.atmosphere import isa
from aerokit.verification import check, check_true, expect_error

LB = Y.LB_N
CFR23 = "14 CFR (2011) §23."
CFR25 = "14 CFR (2011) §25."


def _aircraft(WS_psf=15.0, S=15.0):
    """Light GA example: wing loading given in psf; returns (W [N], S [m²])."""
    return WS_psf * Y.PSF * S, S


def test_maneuver_load_factor():
    check("23.337 normal n(14 000 lb) = 3.1", Y.n_maneuver(14000 * LB)[0], 3.1, source=CFR23 + "337(a)(1)")
    check("23.337 normal n upper limit 3.8 (2000 lb)", Y.n_maneuver(2000 * LB)[0], 3.8, source=CFR23 + "337(a)(1)")
    check("23.337 negative = −0.4n (normal)", Y.n_maneuver(14000 * LB)[1], -1.24, source=CFR23 + "337(b)(1)")
    check("23.337 utility n = 4.4", Y.n_maneuver(3000 * LB, "utility")[0], 4.4, source=CFR23 + "337(a)(2)")
    check("23.337 utility negative = −1.76", Y.n_maneuver(3000 * LB, "utility")[1], -1.76, source=CFR23 + "337(b)(1)")
    check("23.337 acrobatic n = 6.0", Y.n_maneuver(3000 * LB, "acrobatic")[0], 6.0, source=CFR23 + "337(a)(3)")
    check("23.337 acrobatic negative = −0.5n = −3", Y.n_maneuver(3000 * LB, "acrobatic")[1], -3.0,
          source=CFR23 + "337(b)(2)")
    check("25.337 lower limit 2.5 (200 000 lb)", Y.n_maneuver(200000 * LB, "far25")[0], 2.5, source=CFR25 + "337(b)")
    check("25.337 upper limit 3.8 (1000 lb)", Y.n_maneuver(1000 * LB, "far25")[0], 3.8, source=CFR25 + "337(b)")
    check("25.337 formula range (40 000 lb) 2.1+24000/50000", Y.n_maneuver(40000 * LB, "far25")[0],
          2.1 + 24000 / 50000, source=CFR25 + "337(b)")
    check("25.337 negative −1.0", Y.n_maneuver(40000 * LB, "far25")[1], -1.0, source=CFR25 + "337(c)(1)")
    expect_error("invalid category raises", Y.n_maneuver, 1e4, "sport", error=ValueError)
    expect_error("negative weight raises", Y.n_maneuver, -1.0, error=ValueError)


def test_design_speeds():
    check("23.335 V_C factor 33 (W/S ≤ 20)", Y.vc_factor(15), 33.0, source=CFR23 + "335(a)(1)(i)")
    check("23.335 V_C factor 28.6 (W/S = 100)", Y.vc_factor(100), 28.6, source=CFR23 + "335(a)(2)")
    check("23.335 V_C factor W/S = 60 → 30.8 (linear)", Y.vc_factor(60), 30.8,
          source="derivation: 23.335(a)(2) linear interpolation 33 − 4.4·40/80")
    check("23.335 acrobatic factor 36", Y.vc_factor(10, "acrobatic"), 36.0, source=CFR23 + "335(a)(1)(ii)")
    check("23.335 acrobatic W/S = 60 → 32.3", Y.vc_factor(60, "acrobatic"), 32.3,
          source="derivation: 23.335(a)(2) 36 → 28.6 linear")
    check("23.335 V_D factor normal 1.40", Y.vd_factor(15), 1.40, source=CFR23 + "335(b)(2)(i)")
    check("23.335 V_D factor utility 1.50", Y.vd_factor(15, "utility"), 1.50, source=CFR23 + "335(b)(2)(ii)")
    check("23.335 V_D factor acrobatic 1.55", Y.vd_factor(15, "acrobatic"), 1.55, source=CFR23 + "335(b)(2)(iii)")
    check("23.335 V_D factor W/S = 100 → 1.35", Y.vd_factor(100, "utility"), 1.35, source=CFR23 + "335(b)(3)")
    W, S = _aircraft(15.0)
    speeds = Y.design_speeds(W, S, 1.5, 3.8)
    check("V_C,min = 33√15 knot (W/S = 15 psf)", speeds["VC_min"] / Y.KT, 33 * math.sqrt(15), rtol=1e-9,
          source=CFR23 + "335(a)(1)(i)")
    check("V_D,min = 1.40·V_C,min (greater than 1.25·V_C)", speeds["VD"], 1.40 * speeds["VC_min"], rtol=1e-12,
          source=CFR23 + "335(b)(1)-(2)")
    check("V_A = V_S√n", speeds["VA"], speeds["VS"] * math.sqrt(3.8), rtol=1e-12, source=CFR23 + "335(c)(1)")
    check("V_S = √(2W/(ρ0 S CLmax))", speeds["VS"], math.sqrt(2 * W / (1.225 * S * 1.5)), rtol=1e-4,
          source="derivation: L = W, ISA ρ0 = 1.225")
    speeds_vh = Y.design_speeds(W, S, 1.5, 3.8, VH=60.0)
    check("V_C,min limited to 0.9·V_H", speeds_vh["VC_min"], 54.0, source=CFR23 + "335(a)(3)")
    speeds_hi = Y.design_speeds(W, S, 1.5, 3.8, Vc=speeds["VC_min"] * 1.3)
    check("high chosen V_C → V_D = 1.25·V_C", speeds_hi["VD"], 1.25 * speeds_hi["VC"], rtol=1e-12,
          source=CFR23 + "335(b)(1)")
    check_true("low V_C is flagged 'not suitable'", not Y.design_speeds(W, S, 1.5, 3.8, Vc=30.0)["suitable_VC"],
               source=CFR23 + "335(a)")
    speeds_acro = Y.design_speeds(W, S, 0.5, 6.0, category="acrobatic")
    check("V_A does not exceed V_C", speeds_acro["VA"], speeds_acro["VC"], source=CFR23 + "335(c)(2)")
    expect_error("far25 requires Vc/Vd", Y.design_speeds, W, S, 1.5, 2.5, "far25", error=ValueError)
    expect_error("V_D ≤ V_C raises", Y.design_speeds, W, S, 1.5, 3.8, "normal", 80.0, 70.0, error=ValueError)


def test_wind():
    check("K_g(μ = 5.3) = 0.44", Y.kg_reduction(5.3), 0.44, source=CFR23 + "341(c) K_g = 0.88μ/(5.3+μ)")
    check("K_g(μ → ∞) → 0.88", Y.kg_reduction(1e12), 0.88, rtol=1e-9, source="derivation: 23.341(c) limit")
    expect_error("μ_g ≤ 0 raises", Y.kg_reduction, 0.0, error=ValueError)
    check("U_de(V_C, 10 000 ft) = 50 ft/s", Y.ude_far23(3048.0) / Y.FT, 50.0, source=CFR23 + "333(c)(1)(i)")
    check("U_de(V_C, 35 000 ft) = 37.5 ft/s", Y.ude_far23(35000 * Y.FT) / Y.FT, 37.5,
          source="derivation: 23.333(c)(1)(i) 50 → 25 linear (20–50 kft)")
    check("U_de(V_D, sea level) = 25 ft/s", Y.ude_far23(0, "VD") / Y.FT, 25.0, source=CFR23 + "333(c)(1)(ii)")
    check("U_de(V_D, 50 000 ft) = 12.5 ft/s", Y.ude_far23(50000 * Y.FT, "VD") / Y.FT, 12.5,
          source=CFR23 + "333(c)(1)(ii)")
    check("U_de(V_B commuter, sea level) = 66 ft/s", Y.ude_far23(0, "VB") / Y.FT, 66.0,
          source=CFR23 + "333(c)(1)(iii)")
    expect_error("U_de above 50 000 ft raises", Y.ude_far23, 16000.0, error=ValueError)
    # μ_g computed independently in imperial units (slug/ft³, ft, ft/s²)
    W, S, c, a = _aircraft(15.0) + (1.4, 5.0)
    rho_slug = isa(0)["rho"] / Y.SLUG_FT3
    mu_imperial = 2 * 15.0 / (rho_slug * (c / Y.FT) * a * Y.G_FT)
    check("μ_g SI = imperial (dimensionless)", Y.mass_ratio_mu(W, S, c, a), mu_imperial, rtol=1e-5,
          source=CFR23 + "341(c) μ_g = 2(W/S)/(ρ c̄ a g)")
    # the 498 constant: Δn = ρ0·V·U·a·Kg/(2 W/S) (SI) → 2/(ρ0[slug/ft³]·1.68781) = 498.5; the rule rounds to 498
    V, U = 60.0, Y.ude_far23(0)
    r = Y.wind_load_factor(V, U, W, S, c, a)
    dn_si = isa(0)["rho"] * V * U * a * r["Kg"] / (2 * W / S)
    check("23.341 constant 498 ↔ SI derivation (rounding ≈ 0.1 %)", r["dn"], dn_si, rtol=2e-3,
          source="derivation: Δn = ρ0 V U a Kg/(2W/S); 23.341(c) constant 498")
    check("gust symmetric: n_plus + n_minus = 2", r["n_plus"] + r["n_minus"], 2.0, source="derivation: ± gust")


def test_vn_envelope():
    W, S = _aircraft(15.0)
    z = Y.vn_diagram(W, S, 1.4, 1.5, 5.0)
    speeds = z["speeds"]
    i0 = 0
    check("gust line n = 1 at V = 0", z["n_wind_upper"][i0], 1.0, source="derivation: 23.341 n = 1 + kV")
    check("negative gust line n = 1 at V = 0", z["n_wind_lower"][i0], 1.0, source="derivation")
    iS = int(np.argmin(abs(z["V"] - speeds["VS"])))
    check("stall line n = 1 at V_S", z["n_maneuver_upper"][iS], 1.0, rtol=1e-9, source="derivation: n = (V/V_S)²")
    iA = int(np.argmin(abs(z["V"] - speeds["VA"])))
    check("corner A continuity: stall line = n_poz", z["n_maneuver_upper"][iA], z["n_poz"], rtol=1e-9,
          source="derivation: V_A = V_S√n")
    nD = [p for p in z["points"] if p["name"].startswith("D− (maneuver)")][0]
    check("normal category: negative maneuver n = 0 at V_D", nD["n"], 0.0, source=CFR23 + "333(b)(3)")
    zu = Y.vn_diagram(W, S, 1.4, 1.5, 5.0, category="utility")
    check("utility: negative maneuver n = −1 at V_D", zu["n_maneuver_lower"][-1], -1.0, source=CFR23 + "333(b)(3)")
    iC = int(np.argmin(abs(z["V"] - speeds["VC"])))
    check("positive gust at V_C = 23.341 directly", z["n_wind_upper"][iC],
          Y.wind_load_factor(speeds["VC"], Y.ude_far23(0), W, S, 1.4, 5.0)["n_plus"], rtol=1e-12,
          source=CFR23 + "341(c)")
    check("gust at V_D uses U_de = 25 ft/s", z["n_wind_upper"][-1],
          Y.wind_load_factor(speeds["VD"], Y.ude_far23(0, "VD"), W, S, 1.4, 5.0)["n_plus"], rtol=1e-12,
          source=CFR23 + "333(c)(1)(ii)")
    # linear between V_C and V_D: midpoint = mean of the end values
    Vm = 0.5 * (speeds["VC"] + speeds["VD"])
    dn_C = z["wind_C"]["dn"]
    dn_D = z["wind_D"]["dn"]
    n_mid = float(np.interp(Vm, z["V"], z["n_wind_upper"]))
    check("gust V_C→V_D linear (midpoint)", n_mid, 1 + 0.5 * (dn_C + dn_D), rtol=1e-3,
          source=CFR23 + "333(c)(2)(ii)")
    check_true("upper envelope ≥ upper maneuver line at every speed",
               bool(np.all(z["n_envelope_upper"] >= z["n_maneuver_upper"] - 1e-12)),
               source="derivation: combined envelope = max")
    check_true("upper envelope ≤ stall line ∨ n_poz", bool(np.all(
        z["n_envelope_upper"] <= np.maximum(1.225 * z["V"] ** 2 * 1.5 / (2 * W / S) * (1 + 1e-4), z["n_poz"]) + 1e-9)),
        source="derivation: CLmax limit")
    # light wing loading + high CLa → gust critical; heavy wing loading → maneuver critical
    W2, S2 = _aircraft(8.0, 20.0)
    zr = Y.vn_diagram(W2, S2, 1.0, 1.4, 5.5)
    check_true("gust critical at low W/S", zr["critical"] == "gust", f"n_max {zr['n_max']:.2f}",
               source="derivation: Δn ∝ V·a/(W/S)")
    check("if gust critical, n_max = max(V_C, V_D gust)", zr["n_max"],
          max(zr["wind_C"]["n_plus"], zr["wind_D"]["n_plus"]), rtol=1e-9, source="derivation")
    z25 = Y.vn_diagram(20000 * LB, 30.0, 1.8, 1.6, 5.5, category="far25", Vc=150.0, Vd=180.0)
    check("far25 envelope n_max = 25.337 value (20 000 lb → 2.9)", z25["n_max"], 2.1 + 24000 / 30000, rtol=1e-12,
          source=CFR25 + "337(b)")
    check("far25 negative −1.0 at V_C", float(np.interp(150.0, z25["V"], z25["n_maneuver_lower"])), -1.0,
          source=CFR25 + "337(c)(1)")
    check("far25 negative 0 at V_D", z25["n_maneuver_lower"][-1], 0.0, source=CFR25 + "337(c)(2)")
    check_true("far25: no gust line computed", z25["n_wind_upper"] is None, source=CFR25 + "341(a)(1)")
    zc = Y.vn_diagram(*_aircraft(30.0, 25.0), 1.8, 1.6, 5.5, category="commuter")
    check_true("commuter V_B ≤ V_C", zc["VB"] <= zc["speeds"]["VC"] + 1e-9, source=CFR23 + "335(d)(2)")
    # 23.335(d)(1): V_B = min(CNmax ∩ 66 ft/s line, V_S1√n_g); intersection by an independent sweep
    speeds_c = zc["speeds"]
    WSc = 30.0 * Y.PSF
    dnB1 = Y.wind_load_factor(1.0, Y.ude_far23(0, "VB"), WSc * 25.0, 25.0, 1.8, 5.5)["dn"]
    Vt = np.linspace(1.0, speeds_c["VC"], 200001)
    V_cross = Vt[np.argmax(1.225 * Vt ** 2 * 1.6 / (2 * WSc) >= 1 + dnB1 * Vt)]
    VB_expected = min(V_cross, speeds_c["VS"] * math.sqrt(zc["wind_C"]["n_plus"]), speeds_c["VC"])
    check("commuter V_B = min(intersection, V_S√n_g, V_C)", zc["VB"], VB_expected, rtol=1e-4,
          source=CFR23 + "335(d)")


def test_root_bending():
    W, S = _aircraft(15.0)
    z = Y.vn_diagram(W, S, 1.4, 1.5, 5.0)
    k = Y.root_bending(W, 11.0, 1.4, 1.4, z, distribution="ellipse")
    check("root moment (ellipse) = n_max·W·b/(3π)", k["M_root"], k["n"] * W * 11.0 / (3 * math.pi), rtol=3e-3,
          source="derivation: elliptic loading, wing.ellipse_root_moment")
    check("ultimate = 1.5 × limit", k["M_root_ultimate"], 1.5 * k["M_root"], source="14 CFR 23.303 (FS 1.5)")


def test_discrete_wind_far25():
    r = Y.discrete_wind_far25(350 * Y.FT, 0.0, 0.0, 1.0, 1.0)
    check("25.341 U_ref at sea level 56 ft/s", r["Uref"] / Y.FT, 56.0, source=CFR25 + "341(a)(5)(i)")
    check("25.341 H = 350 ft, F_g = 1 → U_ds = 56 ft/s", r["Uds"] / Y.FT, 56.0, source=CFR25 + "341(a)(4)")
    r30 = Y.discrete_wind_far25(30 * Y.FT, 0.0, 0.0, 1.0, 1.0)
    check("25.341 H = 30 ft → 56·(30/350)^(1/6)", r30["Uds"] / Y.FT, 56 * (30 / 350) ** (1 / 6), rtol=1e-12,
          source=CFR25 + "341(a)(4)")
    check("25.341 U_ref at 15 000 ft = 44 ft/s", Y.discrete_wind_far25(100.0, 15000 * Y.FT, 41000 * Y.FT, .8, .7)
          ["Uref"] / Y.FT, 44.0, source=CFR25 + "341(a)(5)(i)")
    check("25.341 U_ref at 50 000 ft = 26 ft/s", Y.discrete_wind_far25(100.0, 50000 * Y.FT, 51000 * Y.FT, .8, .7)
          ["Uref"] / Y.FT, 26.0, source=CFR25 + "341(a)(5)(i)")
    check("25.341 U_ref halved at V_D", Y.discrete_wind_far25(100.0, 0.0, 1e4, .8, .7, "VD")["Uref"] / Y.FT,
          28.0, source=CFR25 + "341(a)(5)(ii)")
    f = Y.discrete_wind_far25(100.0, 0.0, 41000 * Y.FT, 0.8, 0.7)
    Fgz = 1 - 41000 / 250000
    Fgm = math.sqrt(0.7 * math.tan(math.pi * 0.8 / 4))
    check("25.341 F_g at sea level = 0.5(F_gz + F_gm)", f["Fg"], 0.5 * (Fgz + Fgm), rtol=1e-12,
          source=CFR25 + "341(a)(6)")
    check("25.341 F_g(Z_mo) = 1.0", Y.discrete_wind_far25(100.0, 41000 * Y.FT, 41000 * Y.FT, .8, .7)["Fg"], 1.0,
          source=CFR25 + "341(a)(6)")
    expect_error("25.341 H < 30 ft raises", Y.discrete_wind_far25, 5.0, 0.0, 1e4, .8, .7, error=ValueError)


def test_landing():
    W, S = _aircraft(10.0)
    r = Y.landing_loads(W, S)
    check("23.473 descent velocity 4.4(W/S)^¼ (W/S = 10 psf)", r["V_sink_ft_s"], 4.4 * 10 ** 0.25, rtol=1e-9,
          source=CFR23 + "473(d)")
    check("23.473 descent velocity lower limit 7 ft/s", Y.landing_loads(*_aircraft(2.0))["V_sink_ft_s"], 7.0,
          source=CFR23 + "473(d)")
    check("23.473 descent velocity upper limit 10 ft/s", Y.landing_loads(*_aircraft(40.0))["V_sink_ft_s"], 10.0,
          source=CFR23 + "473(d)")
    check("23.725 drop height 3.6√(W/S) in", r["drop_height_in"], 3.6 * math.sqrt(10), rtol=1e-9,
          source=CFR23 + "725(a)")
    check("23.725 drop height lower limit 9.2 in", Y.landing_loads(*_aircraft(4.0))["drop_height_in"], 9.2,
          source=CFR23 + "725(a)")
    check("23.473(g) inertia n ≥ 2.67", r["n_inertia_min"], 2.67, source=CFR23 + "473(g)")
    e = Y.landing_loads(W, S, stroke=0.2, efficiency=1.0, lift_ratio=0.0)
    V = e["V_sink"]
    check("energy: η = 1, L = 0 → N = h/s + 1 (h = V²/2g)", e["N_ground_energy"], V ** 2 / (2 * 9.80665) / 0.2 + 1,
          rtol=1e-12, source="derivation: energy conservation")
    e2 = Y.landing_loads(W, S, stroke=0.2, efficiency=0.8)
    check("23.473(e) ground reaction = inertia − L/W", e2["n_inertia_energy"] - e2["N_ground_energy"], 2 / 3,
          source=CFR23 + "473(e)")
    expect_error("lift > 2/3 raises", Y.landing_loads, W, S, None, 0.7, 0.8, error=ValueError)
    expect_error("stroke ≤ 0 raises", Y.landing_loads, W, S, -0.1, error=ValueError)
