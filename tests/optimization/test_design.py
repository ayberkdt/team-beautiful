"""Tests of aerokit.optimization.design: constraint diagram + KKT, Raymer carpet and optimizer, wing box, tube,
scan/Pareto/sensitivity, FORM and Monte Carlo.

There are hardly any literature numbers here: the checks are derivations (closed forms, KKT, consistency) and
cross-checks against existing modules (aero.sizing, structures.structural_sizing, structures.buckling). Every
check carries a source=.
"""
import math

import numpy as np
from scipy import stats

from aerokit.aero import sizing
from aerokit.structures import buckling
from aerokit.structures import structural_sizing
from aerokit.aero.atmosphere import isa, G0
from aerokit.materials.library import find
from aerokit.optimization import design as T
from aerokit.verification import check, check_true, expect_error

KIND = "twin turboprop"                     # key of aerokit.aero.sizing.EMPTY_WEIGHT (twin turboprop); not translated
W_FIXED = (14 * 91 + 200) * G0              # CLI defaults: 14 persons × 91 kg + 200 kg


def test_constraint_functions_match_sizing():
    g = T.requirement()
    WS = sizing.ws_stall(g["V_stall"], g["CLmax_landing"])
    check("W/S_stall = ½ρV²CLmax", WS, 0.5 * isa(0)["rho"] * g["V_stall"] ** 2 * g["CLmax_landing"], rtol=1e-12,
            source="derivation: L = W at stall")
    e = sizing.oswald_raymer(9.0)
    LD = 11.0 * math.sqrt(9.0 / 5.5)
    CD0, K = sizing.cd0_ldmax(LD, 9.0, e)
    fk = T.constraint_functions(g, precise=False)
    expected = {
        "climb": sizing.pw_en_good_climb(WS, 10.0, 0, CD0, K, 0.8, 1.5, 500 / 3.6)[0],
        "ceiling": sizing.pw_en_good_climb(WS, sizing.SERVICE_CEILING_VV, 10000.0, CD0, K, 0.8, 1.5, 500 / 3.6)[0],
        "vmax": sizing.pw_required(WS, 500 / 3.6, 0, 0.0, CD0, K, 0.8),
        "takeoff": sizing.pw_takeoff(WS, 800.0, 1.7, 0.6),
    }
    for name, v in expected.items():
        check(f"constraint '{name}' = aero.sizing (CLI sizing chain)", fk[name](WS), v, rtol=1e-12,
                source="consistency: CLI sizing command")
    fh = T.constraint_functions(g, precise=True)
    for name in ("climb", "ceiling"):
        check_true(f"continuous climb ({name}) ≤ 400-point grid", fh[name](WS) <= fk[name](WS) * (1 + 1e-12),
              f"{fh[name](WS):.8g} vs {fk[name](WS):.8g}", source="derivation: continuous min ≤ discrete min")
        # grid step ΔV ≈ (V_upper − V_lower)/400; near the minimum the error is O(ΔV²)·f'' — relative 1e-4 bound
        check(f"continuous ≈ grid ({name}, within grid resolution)", fh[name](WS), fk[name](WS), rtol=1e-4,
                source="derivation: grid error O(ΔV²)")
    d = T.constraint_diagram(g, n=50)
    stack = np.vstack(list(d["PW"].values()))
    check("envelope = largest constraint", np.max(np.abs(d["envelope"] - stack.max(0))), 0.0, atol=0.0,
            source="definition")
    check_true("feasible region W/S ≤ W/S_stall", np.array_equal(d["feasible"], d["WS"] <= d["WS_stall"]),
               source="definition")


def test_design_point_kkt():
    g = T.requirement()
    r1 = T.design_point(g, "ws_max")
    check("ws_max: W/S = W/S_stall", r1["WS"], r1["WS_stall"], rtol=1e-15, source="definition")
    check("ws_max: P/W = governing constraint", r1["PW"], max(r1["PW_constraints"].values()), rtol=1e-15,
            source="definition")
    check_true("ws_max: 'stall' active", "stall" in r1["active"], r1["active"], source="definition")
    r2 = T.design_point(g, "pw_min")
    check_true("pw_min: P/W ≤ ws_max P/W", r2["PW"] <= r1["PW"] * (1 + 1e-12), f"{r2['PW']:.6g} vs {r1['PW']:.6g}",
          source="derivation: minimum over the feasible region")
    WS = np.linspace(0.2 * r2["WS_stall"], r2["WS_stall"], 2001)
    fk = T.constraint_functions(g)
    envelope = np.array([max(f(w) for f in fk.values()) for w in WS])
    check_true("pw_min: ≤ minimum on a dense grid", r2["PW"] <= envelope.min() * (1 + 1e-9),
          f"{r2['PW']:.8g} vs {envelope.min():.8g}", source="derivation")
    kkt = r2["kkt"]
    check("pw_min: KKT stationarity residual ≈ 0", kkt["residual"], 0.0, atol=1e-6,
            source="KKT: ∇f + Σλ∇g = 0 (NNLS)")
    lam = kkt["factors"]
    check("pw_min: sum of constraint multipliers = 1 (∂/∂(P/W) row)",
            sum(v for k, v in lam.items() if k != "stall"), 1.0, rtol=1e-6, source="derivation: KKT P/W component")
    check_true("pw_min: multipliers ≥ 0", all(v >= 0 for v in lam.values()), lam, source="KKT")
    if len(r2["active"]) >= 2:
        a, b = [k for k in r2["active"] if k != "stall"][:2]
        check("pw_min: two active constraints equal at the intersection", r2["PW_constraints"][a],
                r2["PW_constraints"][b], rtol=1e-6, source="derivation: corner optimum")
        check_true("pw_min: active constraint slopes of opposite sign (one increasing, one decreasing)",
              r2["slopes"][a] * r2["slopes"][b] < 0, r2["slopes"], source="derivation: KKT λ ≥ 0")
    # known problem: min x² + y² s.t. 1 − x − y ≤ 0 → (½, ½), λ = 1
    k = T.kkt_check(np.array([1.0, 1.0]), {"g": np.array([-1.0, -1.0])})
    check("kkt_check: known problem λ = 1", k["factors"]["g"], 1.0, rtol=1e-12, source="derivation")
    check("kkt_check: residual 0", k["residual"], 0.0, atol=1e-14, source="derivation")


def _cli_W0(AR, g, mission):
    """Verbatim copy of the CLI sizing command's W0 computation (independent reference)."""
    LD = g["KLD"] * math.sqrt(AR / g["swet_sref"])
    fractions = [sizing.SEGMENT["heating_takeoff"], sizing.SEGMENT["climb"],
                 sizing.cruise_propeller(mission["range_m"], mission["cbhp_cruise"], mission["eta"], LD),
                 sizing.loiter_propeller(mission["loiter_s"], mission["V_loiter"], mission["cbhp_loiter"],
                                         mission["eta"], 0.866 * LD),
                 sizing.SEGMENT["landing"]]
    return sizing.takeoff_weight(W_FIXED, sizing.fuel_ratio(math.prod(fractions)), KIND, tol=1e-13)["W0"]


def test_weight_and_optimize():
    g = T.requirement()
    mission = dict(T.DEFAULT_MISSION)
    WSs = T.ws_stall_limit(g)
    r = T.weight_calc(g, mission, W_FIXED, KIND, 9.0, WSs)
    check("weight_calc W0 = CLI chain (sizing.takeoff_weight)", r["W0"], _cli_W0(9.0, g, mission), rtol=1e-12,
            source="consistency: CLI sizing command")
    # cruise L/D: at W/S* = q·√(CD0/K) L/D = L/Dmax (parabolic polar)
    gv = dict(mission, V_cruise=110.0)
    a = T.aero_coefficients(9.0)
    q = 0.5 * isa(0)["rho"] * 110.0 ** 2
    WS_opt = q * math.sqrt(a["CD0"] / a["K"])
    check("cruise L/D equals L/Dmax at W/S = q√(CD0/K)",
          T.weight_calc(g, gv, W_FIXED, KIND, 9.0, WS_opt)["LD_cruise"],
          a["LDmax"], rtol=1e-12, source="derivation: d(L/D)/d(W/S) = 0")
    AR = [7.0, 9.0, 11.0]
    WSl = [0.6 * WSs, 0.8 * WSs, WSs]
    h = T.design_carpet(g, mission, W_FIXED, KIND, AR, WSl)
    check("carpet cell = single-point computation", h["W0"][1, 2], r["W0"], rtol=1e-14, source="consistency")
    check_true("carpet: W0 decreases with AR (L/D increases, pure Raymer)", np.all(np.diff(h["W0"], axis=0) < 0),
               source="derivation")
    scan = T.parametric_scan(lambda AR: T.weight_calc(g, mission, W_FIXED, KIND, AR, WSs)["W0"], {"AR": [7.0, 11.0]})
    check("parametric scan reproduces the sizing output (AR = 11)", scan["Y"][1], _cli_W0(11.0, g, mission),
          rtol=1e-12, source="consistency: sizing.takeoff_weight")
    # pure Raymer: power minimization → AR on its upper bound, W/S at stall (active bounds), KKT
    o = T.design_optimize(g, mission, W_FIXED, KIND, objective="P")
    check_true("P minimum: AR upper bound active", "AR_upper" in o["active"], o["active"],
               source="derivation: W0 decreasing in AR")
    check_true("P minimum: stall bound active", "stall" in o["active"], o["active"], source="derivation")
    check("P minimum: KKT residual ≈ 0", o["kkt"]["residual"], 0.0, atol=1e-5,
          source="KKT (finite-difference gradients)")
    hP = T.design_carpet(g, mission, W_FIXED, KIND, np.linspace(6, 14, 9), np.linspace(0.5 * WSs, WSs, 11))
    check_true("P minimum ≤ smallest feasible P on the carpet", o["P"] <= hP["P"][hP["feasible"]].min() * (1 + 1e-8),
          f"{o['P']:.8g} vs {hP['P'][hP['feasible']].min():.8g}", source="derivation")
    # interior AR optimum with the Raymer wing-weight difference
    kd = dict(AR_ref=9.0, WS_ref=WSs, Lambda=0.0, taper=0.5, t_c=0.15, q=0.5 * 1.225 * 120 ** 2, Nz=5.7)
    o2 = T.design_optimize(g, mission, W_FIXED, KIND, objective="W0", wing_correction=kd)
    check_true("with wing-weight difference AR is interior",
               6.0 < o2["AR"] < 14.0 and not {"AR_lower", "AR_upper"} & set(o2["active"]),
               f"AR = {o2['AR']:.4g}", source="derivation: L/D gain ↔ wing weight")
    check("W0 minimum: KKT residual ≈ 0", o2["kkt"]["residual"], 0.0, atol=1e-4,
          source="KKT (finite-difference gradients)")
    ARi = np.linspace(o2["AR"] - 1.0, o2["AR"] + 1.0, 21)
    W0i = [T.weight_calc(g, mission, W_FIXED, KIND, x, o2["WS"], wing_correction=kd)["W0"] for x in ARi]
    check_true("W0 minimum ≤ smallest value of an AR scan", o2["W0"] <= min(W0i) * (1 + 1e-10), source="derivation")
    # engine mass: fixed-point equation
    rm = T.weight_calc(g, mission, W_FIXED, KIND, 9.0, WSs, engine_kg_W=0.2e-3)  # 0.2 kg/kW, ASSUMPTION (turboprop order)
    share = 1 - rm["Wf_W0"] - sizing.empty_weight_ratio(rm["W0"], KIND)
    check("W0 fixed point with engine mass: W0·(1 − Wf/W0 − We/W0) = W_fixed + W_engine", rm["W0"] * share,
            W_FIXED + 0.2e-3 * G0 * rm["PW"] * rm["W0"], rtol=1e-10, source="derivation: Raymer W0 equation")
    check_true("engine mass increases W0", rm["W0"] > r["W0"], source="derivation")
    expect_error("V_cruise without W/S → error", T.mission_fraction, gv, a, None, error=ValueError)


def test_wing_box():
    for ab in (0.7, 1.0, 2.3):
        check(f"SS-SS k(a/b = {ab}) closed form = exact Lévy solution", buckling.plate_compression_k_ss_closed(ab),
                buckling.plate_compression_k(ab, "SS-SS"), rtol=1e-8,
                source="NACA TN 3781 Eq. 20 / structures.buckling")
    m = find("7075-T6")
    W, n, b, ck, cu, tc = 6000 * G0, 3.8, 17.0, 2.2, 1.1, 0.15
    S = 0.5 * (ck + cu) * b
    ray = dict(S=S, A=b ** 2 / S, Lambda=0.0, taper=cu / ck, t_c=tc, W_fw=800.0, q=0.5 * 1.225 * 120 ** 2, W_dg=6000)
    r = T.wing_box_optimize(W, n, b, ck, cu, tc, m, n_region=5, raymer=ray)
    check_true("all MS ≥ 0 (every region, every mode)", r["MS_min"] >= -1e-9, f"MS_min = {r['MS_min']:.3g}",
          source="constraint definition")
    for j, bg in enumerate(r["regions"]):
        if "t_min" not in bg["mod_skin"]:
            check(f"region {j + 1}: skin MS ≈ 0 in its governing mode ({bg['mod_skin']})",
                    bg["MS"][bg["mod_skin"]], 0.0, atol=1e-8, source="derivation: MS monotonically increasing in t_s")
        if "t_min" not in bg["mod_web"]:
            check(f"region {j + 1}: web MS ≈ 0 in its governing mode ({bg['mod_web']})",
                    bg["MS"][bg["mod_web"]], 0.0, atol=1e-8, source="derivation: closed-form t_w")
    check("mass = sum of items", r["mass"], sum(r["items"].values()), rtol=1e-12, source="definition")
    box = r["_model"]

    def mass_a(a):
        box.configure(r["b_s"], a, r["h_ratio"])
        return box.mass(*box.solve_inner())[0]
    if "a_lower" not in r["active_bounds"] and "a_upper" not in r["active_bounds"]:
        check_true("rib pitch is a local optimum (±2 % perturbation does not reduce the mass)",
              min(mass_a(r["a"] * 1.02), mass_a(r["a"] * 0.98)) >= r["mass"] * (1 - 1e-9), source="derivation")
    rs = T.wing_box_optimize(W, n, b, ck, cu, tc, m, n_region=3, method="slsqp")
    ri = T.wing_box_optimize(W, n, b, ck, cu, tc, m, n_region=3)
    check_true("SLSQP (all variables) is not lighter than the nested solution", rs["mass"] >= ri["mass"] * (1 - 1e-6),
          f"{rs['mass']:.6g} vs {ri['mass']:.6g}", source="derivation: inner problem exact (monotone MS)")
    check_true("SLSQP result feasible", rs["MS_min"] >= -1e-7, f"{rs['MS_min']:.3g}", source="constraint definition")
    # sanity: Raymer statistics (not verification; the box is primary structure only)
    o = r["comparison"]["ratio_raymer"]
    check_true("sanity: box mass / Raymer wing weight ∈ (0.2, 2)", 0.2 < o < 2.0, f"ratio = {o:.3f}",
          source="aero.weight.raymer_wing (sanity check, not verification)")
    check_true("buckling constraints increase the mass (heavier than the structural_sizing estimate)",
               r["comparison"]["ratio_estimate"] > 1,
               f"{r['comparison']['ratio_estimate']:.3f}", source="derivation: additional constraint")
    r38 = T.wing_box_optimize(W, 1.2 * n, b, ck, cu, tc, m, n_region=3)
    check_true("mass increases with load factor", r38["mass"] > ri["mass"], source="derivation")
    rT = T.wing_box_optimize(W, n, b, ck, cu, tc, m, n_region=3, torsion=lambda y: 4000.0 * (1 - 2 * y / b))
    check_true("solution with torsion (R_c + R_s² interaction) feasible", rT["MS_min"] >= -1e-9,
               source="structures.buckling.ms_compression_shear")
    check_true("torsion increases the mass", rT["mass"] > ri["mass"], source="derivation")


def test_wing_box_strength_convergence():
    """With buckling/stringers/ribs off the box must converge to structural_sizing.wing_mass_estimated.

    Webs: same q = V/(2h), τ_allowed = Fsu (ultimate) → the ratio tends to 1 as the number of regions grows
    (error O(1/n), Richardson). Skin: the skin carries bending; with the web contribution
    w·t_s = M/(hσ) − t_w·h/3 (derivation: I = 2wt(h/2)² + 2t_w h³/12).
    """
    m = find("7075-T6")
    W, n, b, ck, cu, tc = 6000 * G0, 3.8, 17.0, 2.2, 1.1, 0.15
    est = structural_sizing.wing_mass_estimated(W, n, b, ck, cu, tc, m["rho"], m["Ftu"], m["Fsu"], t_min=1e-7,
                                                n_station=2001)
    r = {}
    for nb in (100, 200):
        r[nb] = T.wing_box_optimize(W, n, b, ck, cu, tc, m, n_region=nb, stringer_A=None, t_rib=0,
                                    include_buckling=False, t_min=1e-7, n_point=2001, grid=1)["items"]
    web = 2 * r[200]["spar webs"] - r[100]["spar webs"]
    # "spar webs" is the item key produced by structures.structural_sizing (outside this scope)
    check("web mass (Richardson) = web of wing_mass_estimated", web, est["masses"]["spar webs"],
            rtol=1e-3, source="derivation + structures.structural_sizing.wing_mass_estimated")
    y = est["y"]
    tr = lambda f: 2 * float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(y)))
    skin_theory = tr(m["rho"] * 2 * (est["A_title"] - est["t_web"] * est["h"] / 3))
    skin = 2 * r[200]["skin"] - r[100]["skin"]
    check("skin mass (Richardson) = flange area − web bending contribution", skin, skin_theory, rtol=1e-3,
            source="derivation: w·t_s = M/(hσ) − t_w h/3")


def test_tube():
    E, nu, sy = 71.7e9, 0.33, 503e6
    P, L, gam = 5e3, 1.2, 0.6
    r = T.tube_optimize(P_start=P, L=L, E=E, nu=nu, sigma_y=sy, gamma=gam, t_min=1e-5)
    k = T.tube_euler_closed(P, L, E, nu, gam)
    # The closed form is thin-walled (I = πr³t); tube_check uses the exact I = πr³t(1 + t²/4r²) → difference
    # O((t/D)²) ≈ 1e-5 (D/t ≈ 270); a 1e-3 tolerance safely covers this term and the SLSQP stopping criterion.
    check("pure Euler optimum: area = closed form", r["A"], k["A"], rtol=1e-3,
            source="derivation: Euler and local buckling active together")
    check("pure Euler optimum: t = √(FS·P/(2πcE))", r["t"], k["t"], rtol=1e-3, source="derivation")
    check("pure Euler optimum: D/t", r["D_t"], k["D_t"], rtol=1e-3, source="derivation")
    check_true("active constraints: column + local buckling", {"column", "local buckling"} <= set(r["active"]),
               r["active"], source="derivation")
    kb = structural_sizing.tube_check(r["D"], r["t"], P_start=P, L=L, E=E, sigma_y=sy)
    check_true("column mode at the optimum is Euler (validity condition of the closed form)",
               kb["mod"].startswith("Euler") or kb["MS_column"] < kb["MS_vm"], kb["mod"],
               source="structures.structural_sizing column stress")
    M, Tq, Pb, L2 = 800.0, 300.0, 3e3, 0.8
    r2 = T.tube_optimize(M=M, T=Tq, P_start=Pb, L=L2, E=E, nu=nu, sigma_y=sy, t_min=0.5e-3)
    check_true("bending+torsion+compression: all MS ≥ 0", r2["MS_min"] >= -1e-9, r2["MS"],
               source="constraint definition")
    check("bending+torsion+compression: smallest MS ≈ 0", r2["MS_min"], 0.0, atol=1e-6,
          source="derivation: active at the optimum")
    Ds = np.geomspace(0.01, 0.3, 120)
    best = math.inf
    for D in Ds:
        for t in np.geomspace(0.5e-3, D / 2.3, 120):
            if (D - t) / (2 * t) >= 1490:
                continue
            ms = T.tube_margins(D, t, M, Tq, Pb, L2, 1.0, E, nu, sy)
            if min(ms.values()) >= 0:
                best = min(best, math.pi / 4 * (D ** 2 - (D - 2 * t) ** 2))
    check_true("optimum area ≤ smallest feasible area on a 120×120 grid", r2["A"] <= best * (1 + 1e-9),
          f"{r2['A']:.6g} vs {best:.6g}", source="derivation")
    r3 = T.tube_optimize(T=500.0, E=E, nu=nu, sigma_y=sy, D_interval=(5e-3, 0.03), t_min=1e-4, local=False)
    check_true("pure torsion, no local buckling: D on its upper bound", "D_max" in r3["active"], r3["active"],
          source="derivation: thin wall J/A ∝ r²")
    check("pure torsion: von Mises MS = 0", r3["MS"]["von Mises"], 0.0, atol=1e-7, source="derivation")
    expect_error("missing sigma_y → error", T.tube_optimize, P_start=1.0, L=1.0, error=ValueError)


def test_scan_pareto_sensitivity():
    t = T.parametric_scan(lambda x, y: x + 10 * y, {"x": (0.0, 1.0), "y": (0.0, 2.0)}, n=4)
    check("grid point count = 4²", len(t["X"]), 16, source="definition")
    check("grid values f(x, y)", np.max(np.abs(t["Y"] - (t["X"][:, 0] + 10 * t["X"][:, 1]))), 0.0, atol=1e-15,
            source="definition")
    lh = T.parametric_scan(lambda a, b: {"t": a * b, "s": a + b}, {"a": (0.0, 1.0), "b": (10.0, 20.0)},
                           method="lhs", n=25, seed=3)
    stratum_a = np.floor(lh["X"][:, 0] * 25).astype(int)
    stratum_b = np.floor((lh["X"][:, 1] - 10) / 10 * 25).astype(int)
    check_true("LHS: exactly one point in each of the 25 strata of every variable",
          sorted(stratum_a) == list(range(25)) and sorted(stratum_b) == list(range(25)), source="LHS definition")
    check_true("scan with dict output", set(lh["Y"]) == {"t", "s"} and len(lh["Y"]["t"]) == 25, source="definition")
    F = np.array([[1, 5], [2, 3], [3, 4], [4, 1], [5, 5], [2, 2], [2, 2]], float)
    check_true("Pareto (minimize): {(1,5), (2,2)×2, (4,1)}", sorted(T.pareto_front(F)) == [0, 3, 5, 6],
               T.pareto_front(F), source="definition: non-dominance (counted by hand)")
    check_true("Pareto ranks", list(T.pareto_ranks(F)) == [0, 1, 2, 0, 3, 0, 0], T.pareto_ranks(F),
          source="definition (counted by hand)")
    check_true("Pareto (maximize)", sorted(T.pareto_front(F, maximize=[True, True])) == [4],
               T.pareto_front(F, maximize=[True, True]), source="definition")
    rng = np.random.default_rng(1)
    f1 = np.sort(rng.random(50))
    on = np.column_stack([f1, 1 - np.sqrt(f1)])
    rear = on + rng.uniform(0.01, 0.3, (50, 2))
    all_items = np.vstack([on, rear])
    check_true("ZDT1-like set: the front is exactly the 50 points on the curve",
               sorted(T.pareto_front(all_items)) == list(range(50)),
               source="derivation: f2 = 1 − √f1 strictly decreasing")
    check_true("ZDT1-like set: shifted points have rank ≥ 1", np.all(T.pareto_ranks(all_items)[50:] >= 1),
               source="derivation")
    e = T.sensitivity(lambda x: 3 * x[0] ** 2 * x[1] ** -0.5 * x[2] ** 1.3, [2.0, 5.0, 0.7])
    for i, p in enumerate((2.0, -0.5, 1.3)):
        check(f"elasticity of a power law, exponent {p}", e[i], p, rtol=1e-8, source="derivation: ∂ln f/∂ln x = p")
    # Raymer: W0·(1 − wf − A·W0^C) = Ws → e_Ws = 1/(1 − C·we/den), e_wf = (wf/den)/(1 − C·we/den)
    wf = 0.3
    f = lambda x: sizing.takeoff_weight(x[0], x[1], KIND, tol=1e-15)["W0"]
    e = T.sensitivity(f, [W_FIXED, wf], h=1e-4)
    W0 = f([W_FIXED, wf])
    we = sizing.empty_weight_ratio(W0, KIND)
    C = sizing.EMPTY_WEIGHT[KIND][1]
    den = 1 - wf - we
    check("Raymer W0 elasticity (W_fixed)", e[0], 1 / (1 - C * we / den), rtol=1e-6,
            source="derivation: log derivative of the W0 equation")
    check("Raymer W0 elasticity (Wf/W0)", e[1], (wf / den) / (1 - C * we / den), rtol=1e-6, source="derivation")
    ed = T.sensitivity(lambda x: {"a": x[0] * x[1], "b": x[0] ** 3}, [2.0, 3.0])
    check("elasticity with dict output", ed["b"][0], 3.0, rtol=1e-8, source="derivation")


def test_reliability():
    mR, sR, mS, sS = 300.0, 30.0, 200.0, 25.0
    R, S = T.distribution("normal", mR, sR), T.distribution("normal", mS, sS)
    beta = (mR - mS) / math.hypot(sR, sS)
    f = T.form(lambda x: x[..., 0] - x[..., 1], [R, S])
    check("FORM linear g = R − S, normal: β = (μR − μS)/√(σR² + σS²)", f["beta"], beta, rtol=1e-10,
            source="Cornell/Hasofer–Lind closed form (derivation; papers not read)")
    check("FORM P_f = Φ(−β) (exact in the linear-normal case)", f["Pf"], stats.norm.cdf(-beta), rtol=1e-9,
            source="derivation")
    check("design point on the limit state: R* = S*", f["x"][0], f["x"][1], rtol=1e-9, source="derivation: g(x*) = 0")
    check("sensitivity α_R = σR/√(σR² + σS²)", f["alpha"][0], sR / math.hypot(sR, sS), rtol=1e-8, source="derivation")
    check_true("FORM converged (linear: ≤ 3 iterations)", f["converged"] and f["iteration"] <= 3, f["iteration"],
          source="HL-RF is exact in one step on a linear limit state")
    mc = T.monte_carlo_pf(lambda X: X[:, 0] - X[:, 1], [R, S], n=400_000, seed=11)
    Pf = stats.norm.cdf(-beta)
    check_true("MC P_f within 3σ_MC of the exact value", abs(mc["Pf"] - Pf) <= 3 * mc["std_error"],
          f"{mc['Pf']:.5g} vs {Pf:.5g} (σ={mc['std_error']:.2g})", source="central limit theorem (binomial)")
    check_true("MC 95 % Wilson interval contains the exact value", mc["interval"][0] <= Pf <= mc["interval"][1],
               mc["interval"], source="Wilson score")
    check("MC standard error = √(P(1−P)/n)", mc["std_error"], math.sqrt(mc["Pf"] * (1 - mc["Pf"]) / mc["n"]),
          rtol=1e-12, source="binomial variance")
    # lognormal R, S: the R = S surface is a plane in u-space → FORM exact; β = (λR − λS)/√(ζR² + ζS²)
    Rl, Sl = T.distribution("lognormal", 300.0, 45.0), T.distribution("lognormal", 150.0, 30.0)
    zR, zS = math.sqrt(math.log(1 + 0.15 ** 2)), math.sqrt(math.log(1 + 0.2 ** 2))
    bl = ((math.log(300) - zR ** 2 / 2) - (math.log(150) - zS ** 2 / 2)) / math.hypot(zR, zS)
    fl = T.form(lambda x: x[..., 0] - x[..., 1], [Rl, Sl])
    check("FORM lognormal R, S (g nonlinear in x-space): closed-form β", fl["beta"], bl, rtol=1e-8,
            source="derivation: ln R = ln S plane")
    check("exact P_f integral (∫F_R f_S) = Φ(−β) lognormal", T.pf_strength_load(Rl, Sl), stats.norm.cdf(-bl),
          rtol=1e-7, source="derivation")
    mcl = T.monte_carlo_pf(lambda X: X[:, 0] - X[:, 1], [Rl, Sl], n=400_000, seed=5)
    check_true("MC lognormal within 3σ_MC", abs(mcl["Pf"] - stats.norm.cdf(-bl)) <= 3 * mcl["std_error"],
          f"{mcl['Pf']:.5g} vs {stats.norm.cdf(-bl):.5g}", source="central limit theorem")
    # lognormal R, Gumbel S: no closed form → numerical integral as reference
    Sg = T.distribution("gumbel", 150.0, 30.0)
    Pg = T.pf_strength_load(Rl, Sg)
    mcg = T.monte_carlo_pf(lambda X: X[:, 0] - X[:, 1], [Rl, Sg], n=1_000_000, seed=2)
    check_true("MC (lognormal/Gumbel) within 3σ_MC of the numerical integral",
               abs(mcg["Pf"] - Pg) <= 3 * mcg["std_error"],
               f"{mcg['Pf']:.5g} vs {Pg:.5g}", source="central limit theorem")
    fg = T.form(lambda x: x[..., 0] - x[..., 1], [Rl, Sg])
    # FORM is approximate here (limit-state surface curved in u-space); the 10 % band is an order-of-magnitude check
    check("FORM (lognormal/Gumbel) within 10 % of the exact P_f (approximate method)", fg["Pf"], Pg, rtol=0.1,
            source="FORM first-order approximation")
    for name, dgl in (("lognormal", Rl), ("gumbel", Sg)):
        check(f"{name}: scipy mean = input", dgl["d"].mean(), dgl["mean"], rtol=1e-12, source="moment relation")
        check(f"{name}: scipy std = input", dgl["d"].std(), dgl["std"], rtol=1e-12, source="moment relation")
    fn = T.form(lambda x: x[..., 0] - x[..., 1],
                [T.distribution("normal", 100.0, 10.0), T.distribution("normal", 120.0, 10.0)])
    check_true("g(mean) < 0 → β < 0, P_f > 0.5", fn["beta"] < 0 and fn["Pf"] > 0.5, fn["beta"], source="definition")
    expect_error("lognormal mean ≤ 0 → error", T.distribution, "lognormal", -1.0, 1.0, error=ValueError)
    expect_error("std ≤ 0 → error", T.distribution, "normal", 1.0, 0.0, error=ValueError)
