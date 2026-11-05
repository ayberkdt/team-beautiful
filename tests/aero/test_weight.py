"""Tests of aerokit.aero.weight: mass properties (derivations), loading envelope, Raymer GA group weights."""
import numpy as np

from aerokit.aero import weight as A
from aerokit.verification import check, check_true, expect_error

LB = A.LB_KG
ASB = "AeroSandbox raymer_general_aviation_weights.py (Raymer 5th ed. §15.3.3), read 2026-10-25"
SUAVE = "SUAVE General_Aviation/*.py (Raymer 4th ed. pp. 460–461), read 2026-10-25"


def test_mass_properties():
    sym = [("fuselage", 300, 3.0, 0.0, 0.0), ("left wing", 60, 2.5, -3.0, 0.5), ("right wing", 60, 2.5, 3.0, 0.5),
           ("left tank", 40, 2.4, -1.5, 0.4), ("right tank", 40, 2.4, 1.5, 0.4)]
    r = A.mass_properties(sym)
    check("symmetric layout: y_cg = 0", r["cg"][1], 0.0, atol=1e-12, source="derivation: symmetry")
    check("symmetric layout: Ixy = 0", r["Ixy"], 0.0, atol=1e-9, source="derivation: symmetry")
    check("total mass", r["m"], 500.0, source="derivation")
    check("x_cg = Σmx/Σm", r["cg"][0], (900 + 300 + 192) / 500, rtol=1e-12, source="derivation")
    # parallel axis: J_origin = J_cg + m(|d|²I − d dᵀ)
    d = r["cg"]
    J_p = r["J"] + r["m"] * (d @ d * np.eye(3) - np.outer(d, d))
    check("parallel-axis theorem (Ixx)", r["J_origin"][0, 0], J_p[0, 0], rtol=1e-12, source="derivation: Steiner")
    check("parallel-axis theorem (Iyy)", r["J_origin"][1, 1], J_p[1, 1], rtol=1e-12, source="derivation: Steiner")
    check("parallel-axis theorem (Ixz)", r["J_origin"][0, 2], J_p[0, 2], rtol=1e-12, atol=1e-12,
          source="derivation: Steiner")
    # two point masses: I = μ·L² (reduced mass)
    two = A.mass_properties([("a", 2.0, 0, -1.0, 0), ("b", 6.0, 0, 3.0, 0)])
    check("two masses: Ixx = m1m2/(m1+m2)·L²", two["Ixx"], 2 * 6 / 8 * 16, rtol=1e-12, source="derivation")
    check("masses on the y axis: Iyy = 0", two["Iyy"], 0.0, atol=1e-12, source="derivation")
    check("perpendicular axis: Izz = Ixx + Iyy (planar, z = 0)", two["Izz"], two["Ixx"] + two["Iyy"], rtol=1e-12,
          source="derivation: perpendicular-axis theorem")
    # slender rod: N point masses → mL²/12, and the same through the own-inertia input
    N, L, m = 2001, 2.0, 10.0
    bar = [("p", m / N, 0.0, -L / 2 + L * i / (N - 1), 0.0) for i in range(N)]
    check("slender rod discrete sum → mL²/12", A.mass_properties(bar)["Ixx"], m * L ** 2 / 12, rtol=2e-3,
          source="derivation: ∫y²dm (discrete end points give an excess factor (N+1)/(N−1))")
    own = A.mass_properties([{"name": "rod", "m": m, "x": 1.0, "J_own": (m * L ** 2 / 12, 0.0, m * L ** 2 / 12)}])
    check("own-inertia input is preserved", own["Ixx"], m * L ** 2 / 12, rtol=1e-12, source="derivation")
    xz = A.mass_properties([("a", 1.0, 1.0, 0.0, 1.0), ("b", 1.0, -1.0, 0.0, -1.0)])
    check("Ixz positive convention Σm·x·z = 2", xz["Ixz"], 2.0, rtol=1e-12,
          source="derivation: flight-dynamics convention")
    check("%MAC: LEMAC + 0.25·MAC → 25", A.cg_percent_mac(2.3, 2.0, 1.2), 25.0, rtol=1e-12, source="definition")
    expect_error("negative mass raises", A.mass_properties, [("x", -1, 0, 0, 0)], error=ValueError)
    expect_error("empty list raises", A.mass_properties, [], error=ValueError)
    expect_error("MAC ≤ 0 raises", A.cg_percent_mac, 1.0, 0.5, 0.0, error=ValueError)


def test_cg_envelope():
    basic = [("empty", 600.0, 2.0, 0, 0), ("pilot", 80.0, 1.5, 0, 0)]
    passenger = ("rear passenger", 80.0, 2.6, 0, 0)
    baggage = ("baggage", 20.0, 3.2, 0, 0)
    fuel = ("fuel", 100.0, 2.1, 0, 0)
    z = A.cg_envelope(basic, [passenger, baggage], fuel, fuel_step=5, x_lemac=1.7, mac=1.4)
    check("number of cases = 2² × 5", len(z["cases"]), 20, source="derivation: number of combinations")
    # most forward: no optional items, no fuel (fuel x = 2.1 > basic x_cg ≈ 1.94 → fuel pulls the CG aft)
    x_basic = (1200 + 120) / 680
    check("forward limit = basic, no fuel", z["x_front"], x_basic, rtol=1e-12, source="derivation: moment sum")
    x_rear = (1200 + 120 + 208 + 64 + 210) / 880
    check("aft limit = passenger + baggage + full fuel", z["x_rear"], x_rear, rtol=1e-12, source="derivation")
    check("aft limit %MAC", z["rear"]["percent_mac"], 100 * (x_rear - 1.7) / 1.4, rtol=1e-12, source="definition")
    check("mass range upper end = 880 kg", z["m_max"], 880.0, source="derivation")
    expect_error("too many optional items raises", A.cg_envelope, basic, [passenger] * 20, error=ValueError)


def _example_ga():
    """Single-engine four-seat GA aircraft (conceptual inputs, not a measured aircraft)."""
    W0 = 1100.0
    return {"W_dg": W0, "Nz": 5.7, "q": 0.5 * 0.9 * 60 ** 2,
            "wing": dict(S=16.0, A=7.5, Lambda=0.0, taper=0.7, t_c=0.15, W_fw=120.0),
            "horizontal": dict(S=3.2, A=4.0, Lambda=0.0, taper=0.8, t_c=0.10),
            "vertical": dict(S=1.6, A=1.5, Lambda=30.0, taper=0.5, t_c=0.10),
            "fuselage": dict(S_f=32.0, L_t=4.6, L_D=6.0),
            "main_gear": dict(N_l=4.5, W_l=1050.0, L_m=0.6),
            "nose_gear": dict(N_l=4.5, W_l=1050.0, L_n=0.5),
            "engine": dict(W_en=130.0, N_en=1),
            "fuel": dict(V_t=0.19, V_i=0.0, N_t=2),
            "control": dict(L=8.0, b=11.0),
            "avionics": dict(W_uav=15.0), "floor": True}


def test_raymer_wing_forrester():
    # Forrester, Sóbester & Keane 2008 wing-weight test function = Raymer GA wing + Sw·Wp paint term.
    # UQTestFuns documentation: Monte Carlo mean for uniform distributions of the 10 inputs is 268.07 lb (1e7 samples).
    rng = np.random.default_rng(20261025)
    N = 40000
    u = lambda a, b: rng.uniform(a, b, N)
    Sw, Wfw, Ar, Lam, q, lam, tc, Nz, Wdg, Wp = (u(150, 200), u(220, 300), u(6, 10), u(-10, 10), u(16, 45),
                                                 u(0.5, 1), u(0.08, 0.18), u(2.5, 6), u(1700, 2500), u(0.025, 0.08))
    f = np.array([A.raymer_wing(Sw[i] * A.FT ** 2, Wfw[i] * LB, Ar[i], Lam[i], q[i] * A.PSF, lam[i], tc[i], Nz[i],
                                Wdg[i] * LB) / LB for i in range(N)]) + Sw * Wp
    # standard error √(2312/40000) = 0.24 lb (0.09 %); tolerance 0.5 % ≈ 5.6σ
    check("Raymer GA wing: Forrester test function MC mean 268.07 lb", f.mean(), 268.07, rtol=5e-3,
          source="Forrester, Sóbester & Keane 2008 (Wiley) wing weight fn; UQTestFuns docs MC mean 2.6807e+02")


def test_raymer_groups():
    # Unit conversion: SI interface ↔ imperial equation (lb, ft², psf) directly
    S, Wfw, Ar, q, lam, tc, Nz, W = 174.0, 252.0, 7.52, 34.0, 0.672, 0.12, 3.8, 2000.0
    imperial = (0.036 * S ** 0.758 * Wfw ** 0.0035 * Ar ** 0.6 * q ** 0.006 * lam ** 0.04 * (100 * tc) ** -0.3
                * (Nz * W) ** 0.49)
    si = A.raymer_wing(S * A.FT ** 2, Wfw * LB, Ar, 0.0, q * A.PSF, lam, tc, Nz, W * LB) / LB
    check("wing SI interface = imperial equation", si, imperial, rtol=1e-10, source=ASB + "; " + SUAVE)
    b = dict(S_w=16.0, W_fw=100.0, A=7.0, Lambda=5.0, q=2000.0, taper=0.6, t_c=0.14, Nz=5.7, W_dg=1100.0)
    check("wing ∝ Sw^0.758", A.raymer_wing(**{**b, "S_w": 32.0}) / A.raymer_wing(**b), 2 ** 0.758,
          rtol=1e-10, source=ASB)
    check("wing ∝ (Nz·Wdg)^0.49", A.raymer_wing(**{**b, "Nz": 11.4}) / A.raymer_wing(**b), 2 ** 0.49,
          rtol=1e-10, source=ASB)
    check("wing ∝ (t/c)^−0.3", A.raymer_wing(**{**b, "t_c": 0.28}) / A.raymer_wing(**b), 2 ** -0.3,
          rtol=1e-10, source=ASB)
    check("no wing fuel → Wfw term = 1", A.raymer_wing(**{**b, "W_fw": 0.0}),
          A.raymer_wing(**{**b, "W_fw": LB}), rtol=1e-12, source=ASB + " (W_fw = 1 lb ↔ 1^0.0035 = 1)")
    h = dict(S_ht=3.0, A_ht=4.0, Lambda_ht=0.0, q=2000.0, taper_ht=0.8, t_c_ht=0.1, Nz=5.7, W_dg=1100.0)
    check("horizontal tail ∝ Sht^0.896", A.raymer_horizontal_tail(**{**h, "S_ht": 6.0}) / A.raymer_horizontal_tail(**h),
          2 ** 0.896, rtol=1e-10, source=ASB + "; " + SUAVE)
    v = dict(S_vt=1.5, A_vt=1.5, Lambda_vt=30.0, q=2000.0, taper_vt=0.5, t_c_vt=0.1, Nz=5.7, W_dg=1100.0)
    check("T-tail factor 1.2", A.raymer_vertical_tail(**v, Ht_Hv=1.0) / A.raymer_vertical_tail(**v), 1.2,
          rtol=1e-12, source=ASB + "; " + SUAVE)
    check("vertical tail ∝ Svt^0.873", A.raymer_vertical_tail(**{**v, "S_vt": 3.0}) / A.raymer_vertical_tail(**v),
          2 ** 0.873, rtol=1e-10, source=SUAVE + " (ASB 0.876 — sources disagree)")
    g0 = A.raymer_fuselage(30.0, 5.7, 1100.0, 4.5, 6.0, 2000.0)
    g1 = A.raymer_fuselage(30.0, 5.7, 1100.0, 4.5, 6.0, 2000.0, V_pr=10.0, dP=30000.0)
    check("pressurization term 11.9(V·ΔP)^0.271 is added", (g1 - g0) / LB,
          11.9 * (10.0 / A.FT ** 3 * 30000.0 / A.PSI) ** 0.271, rtol=1e-10, source=ASB + "; " + SUAVE)
    check("fuselage ∝ Sf^1.086", A.raymer_fuselage(60.0, 5.7, 1100.0, 4.5, 6.0, 2000.0) / g0, 2 ** 1.086,
          rtol=1e-10, source=ASB + "; " + SUAVE)
    check("main gear: Lm = 12 in → 0.095(Nl·Wl)^0.768 lb", A.raymer_main_landing_gear(4.5, 1000 * LB, 12 * A.INC) / LB,
          0.095 * 4500 ** 0.768, rtol=1e-10, source=SUAVE + " (Lm in inches)")
    check("nose gear: Ln = 12 in → 0.125(Nl·Wl)^0.566 lb",
          A.raymer_nose_landing_gear(4.5, 1000 * LB, 12 * A.INC) / LB, 0.125 * 4500 ** 0.566, rtol=1e-10,
          source=SUAVE)
    check("installed engine 2.575·Wen^0.922·Nen (200 lb, 2 engines)", A.raymer_engine_installed(200 * LB, 2) / LB,
          2 * 2.575 * 200 ** 0.922, rtol=1e-10, source=ASB)
    check("fuel system: Vi = Vt → ×2^−0.363", A.raymer_fuel_system(0.2, 0.2, 2) / A.raymer_fuel_system(
        0.2, 0.0, 2), 2 ** -0.363, rtol=1e-10, source=ASB + "; " + SUAVE + " (identical forms)")
    check("fuel system 50 gal, 2 tanks, 1 engine", A.raymer_fuel_system(50 * A.GAL, 0.0, 2) / LB,
          2.49 * 50 ** 0.726 * 2 ** 0.242, rtol=1e-10, source=ASB)
    check("flight controls unit conversion", A.raymer_flight_controls(25 * A.FT, 36 * A.FT, 5.7, 2400 * LB) / LB,
          0.053 * 25 ** 1.536 * 36 ** 0.371 * (5.7 * 2400 * 1e-4) ** 0.8, rtol=1e-10, source=ASB)
    check("avionics 2.117·W^0.933 (30 lb)", A.raymer_avionics(30 * LB) / LB, 2.117 * 30 ** 0.933, rtol=1e-10,
          source=ASB + "; " + SUAVE)
    check("electrical 12.57·(Wfs + Wav)^0.51", A.raymer_electrical(40 * LB, 60 * LB) / LB, 12.57 * 100 ** 0.51,
          rtol=1e-10, source=ASB + "; " + SUAVE)
    check("furnishings 0.0582·2000 − 65 = 51.4 lb", A.raymer_floor(2000 * LB) / LB, 51.4, rtol=1e-10,
          source=ASB + "; " + SUAVE)
    check("furnishings clipped to 0 for a small aircraft", A.raymer_floor(500 * LB), 0.0,
          source="implementation choice")
    check("hydraulics K_h·W^0.8·M^0.5", A.raymer_hydraulic(0.013, 4 * A.FT, 0.1) / LB, 0.013 * 4 ** 0.8 * 0.1 ** 0.5,
          rtol=1e-10, source=ASB)
    check("air conditioning/anti-icing unit conversion", A.raymer_air_conditioning_icing(2400 * LB, 4, 50 * LB, 0.2)
          / LB, 0.265 * 2400 ** 0.52 * 4 ** 0.68 * 50 ** 0.17 * 0.2 ** 0.08, rtol=1e-10, source=ASB + "; " + SUAVE)
    expect_error("negative area raises", A.raymer_wing, -1, 0, 7, 0, 2000, .6, .12, 5.7, 1000, error=ValueError)
    expect_error("negative integral-tank volume raises", A.raymer_fuel_system, 0.2, -0.1, 2, error=ValueError)


def test_raymer_summary():
    r = A.raymer_ga_empty_weight(_example_ga())
    check("summary total = sum of groups", r["We"], sum(r["groups"].values()), rtol=1e-12, source="derivation")
    check("We/W0 = We/W_dg", r["We_W0"], r["We"] / 1100.0, rtol=1e-12, source="definition")
    from aerokit.aero import sizing
    check("regression We/W0 = sizing.empty_weight_ratio", r["We_W0_regression"],
          sizing.empty_weight_ratio(1100 * 9.80665, "GA single engine"), rtol=1e-12,
          source="Raymer Table 3.1 (sizing.py)")
    check_true("GA example: statistical total within ±35 % of the regression", abs(r["difference_percent"]) < 35,
               f"We/W0 groups {r['We_W0']:.3f}, regression {r['We_W0_regression']:.3f}",
               source="sanity check (not a literature value)")
