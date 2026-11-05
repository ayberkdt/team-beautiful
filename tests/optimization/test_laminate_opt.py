"""Tests of aerokit.optimization.laminate: lamination parameters, feasibility, vectorized ↔ composites
consistency, Le Riche (1994) buckling-optimization tables, exhaustive search / GA / permutation search,
continuous angles.

[LR94] R. Le Riche, PhD thesis, Virginia Tech 1994, Chapter 3 — READ from the vtechworks PDF
(the page image of Table 3.1 was also checked by eye). Units: load 1 lbf/in (the load factors in the
tables were produced with this unit load; the tests below confirm this).
"""
import math

import numpy as np

from aerokit.composites import laminate
from aerokit.optimization import laminate as KO
from aerokit.verification import check, check_true, expect_error

LR = "Le Riche 1994 thesis, Table {} (p. {}; read)"
M_LR, T_LR, INCH, LBF = KO.LR94_MATERIAL, KO.LR94_T, KO.INCH, KO.LBF_PER_INCH


def _lr(codes, objective, phi, a, b):
    return KO.evaluate_stack(KO.stack_angles(codes), M_LR, T_LR, objective, (LBF, phi * LBF), a * INCH, b * INCH,
                             KO.LR94_STRAIN, 1.5)


def test_lamination_parameters():
    m = laminate.KAW_GLASS_EPOXY
    rng = np.random.default_rng(0)
    ac = rng.uniform(-90, 90, 7)                      # neither symmetric nor balanced
    t = 0.2e-3
    A, B, D, _ = laminate.abd_matrix(laminate.layers(m, [(x, t) for x in ac]))
    lp = KO.lamination_parameters(ac)
    h = 7 * t
    A2, D2 = KO.abd_lp(m, h, lp["V"], lp["W"])
    check("A(U, V) = composites.abd_matrix A (random laminate)", np.max(np.abs(A2 - A)) / np.max(np.abs(A)), 0.0,
          atol=1e-12, source="derivation: Q̄ = Tsai–Pagano trigonometric expansion")
    check("D(U, W) = composites.abd_matrix D (random laminate)", np.max(np.abs(D2 - D)) / np.max(np.abs(D)), 0.0,
          atol=1e-12, source="derivation")
    B2 = h ** 2 / 4 * KO._lp_matrix(np.r_[0.0, KO.U_invariants(m)[1:3], 0.0, 0.0], lp["B"])
    check("B(U2, U3, V_B) = composites B (U1, U4, U5 terms vanish since ∫z = 0)",
          np.max(np.abs(B2 - B)) / np.max(np.abs(B)), 0.0, atol=1e-12, source="derivation")
    v = KO.lamination_parameters([0.0])["V"]
    check("[0]: V1 = 1", v[0], 1.0, rtol=1e-15, source="definition: cos 0 = 1")
    check("[0]: V2 = 1", v[1], 1.0, rtol=1e-15, source="definition")
    check("[90]: V1 = −1", KO.lamination_parameters([90.0])["V"][0], -1.0, rtol=1e-15, source="definition")
    q = KO.lamination_parameters([0, 45, -45, 90, 90, -45, 45, 0])
    for i in range(4):
        check(f"quasi-isotropic [0/±45/90]s: V{i + 1} = 0", q["V"][i], 0.0, atol=1e-15, source="definition")
    check("[0/±45/90]s: W1 = 0.5625", q["W"][0], 0.5625, rtol=1e-13,
          source="derivation: 12/h³·(2/3)·(37 − 1)/… (z = 0…4t)")
    check("[0/±45/90]s: W2 = 0.1875", q["W"][1], 0.1875, rtol=1e-13, source="derivation: (37 − 19 − 7 + 1)/64")
    check("[0/±45/90]s: B = 0 (symmetric)", np.max(np.abs(q["B"])), 0.0, atol=1e-15, source="definition")
    a45 = KO.lamination_parameters([45, -45, -45, 45])["V"]
    check("[±45]s: V2 = −1", a45[1], -1.0, rtol=1e-15, source="definition: cos 180° = −1")
    U = KO.U_invariants(m)
    Q = laminate.Q_material(m)
    check("U1 + U2 + U3 = Q11 (θ = 0)", U[0] + U[1] + U[2], Q[0, 0], rtol=1e-13, source="derivation")
    check("U5 − U3 = Q66 (θ = 0)", U[4] - U[2], Q[2, 2], rtol=1e-13, source="derivation")


def test_feasibility():
    f1 = [KO.lp_feasible(*KO._trig([th])[0])[1] for th in np.linspace(-90, 90, 37)]
    check("single-angle ply lies exactly on the four-parameter boundary", max(abs(x - 1) for x in f1), 0.0, atol=1e-12,
          source="derivation: identity via c² + s² = 1")
    rng = np.random.default_rng(4)
    ok = True
    for _ in range(300):
        lp = KO.lamination_parameters(rng.uniform(-90, 90, rng.integers(2, 12)))
        ok &= KO.lp_feasible(*lp["V"])[0] and KO.lp_feasible(*lp["W"])[0]
    check_true("V and W of 300 random laminates lie in the feasible region", ok, source="convex hull (derivation)")
    th = np.radians(30.0)
    check("angle-ply ±θ on the Miki boundary: V2 = 2V1² − 1", math.cos(4 * th), 2 * math.cos(2 * th) ** 2 - 1,
          rtol=1e-14, source="derivation: cos4θ = 2cos²2θ − 1")
    check_true("Miki: (0, −1) feasible ([±45])", KO.miki_feasible(0.0, -1.0), source="definition")
    check_true("Miki: (0.9, 0) infeasible (2·0.81 − 1 = 0.62 > 0)", not KO.miki_feasible(0.9, 0.0), source="derivation")
    keep = all(KO.miki_feasible(v1, v2) == KO.lp_feasible(v1, v2)[0]
               for v1, v2 in rng.uniform(-1, 1, (500, 2)))
    check_true("for orthotropic laminates the four-parameter condition reduces to the Miki bound", keep,
               source="derivation: (1−V2)(2V1²−1−V2) ≤ 0")
    lo, hi = KO.lp_vw_bounds(0.0)
    w = KO.lamination_parameters([0, 0, 90, 90, 90, 90, 0, 0])["W"][0]
    check("[0₂/90₂]s: W1 = W_max(V1 = 0) = 0.75 (on the bound)", w, hi, rtol=1e-14,
          source="derivation: bang-bang, 1 − (1 − V)³/4")
    check("W_min(0) = −0.75", lo, -0.75, rtol=1e-15, source="derivation")
    inner = True
    for _ in range(300):
        half = list(rng.uniform(-90, 90, rng.integers(1, 7)))
        lp = KO.lamination_parameters(half + half[::-1])
        for i in range(4):
            a, b = KO.lp_vw_bounds(lp["V"][i])
            inner &= a - 1e-12 <= lp["W"][i] <= b + 1e-12
    check_true("300 random symmetric laminates: W_i within the bounds set by V_i", inner, source="derivation")
    expect_error("|V| > 1 → error", KO.lp_vw_bounds, 1.2, error=ValueError)


def test_vectorized_consistency():
    m = laminate.KAW_GLASS_EPOXY
    t = 0.15e-3
    rng = np.random.default_rng(7)
    code = rng.integers(0, 3, (12, 6))
    for objective, load in (("buckling", (1e3, 300.0)), ("strain", (1e3, 300.0, 200.0)), ("stiffness", (1.0, -0.4, 0.7))):
        ev = KO.StackEvaluator(m, t, 6, objective, load, a=0.4, b=0.25, strain_allowed=(0.01, 0.02, 0.015), FS=1.2)
        v = ev.values(code)
        ref = [KO.evaluate_stack(KO.stack_angles(k), m, t, objective, load, 0.4, 0.25, (0.01, 0.02, 0.015), 1.2)
               for k in code]
        check(f"vectorized '{objective}' = evaluate_stack (composites)", np.max(np.abs(v / ref - 1)), 0.0, atol=1e-10,
              source="consistency: composites.plate_buckling / laminate_analysis / abd_matrix")
    run = KO.StackEvaluator.adjacency(code)
    check_true("vectorized adjacency = adjacency_max", list(run) == [KO.adjacency_max(KO.stack_angles(k)) for k in code],
               source="consistency")
    check("[0₂/0₂]s: 8 contiguous plies at the mid-plane", KO.adjacency_max(KO.stack_angles([0, 0])), 8,
          source="[LR94] Fig. 3.2 (the inner stack doubles because of the mirror)")
    check("[±45/±45]s: ±45 are different angles → longest run 2", KO.adjacency_max(KO.stack_angles([1, 1])), 2,
          source="[LR94] §3.1")
    ac = KO.stack_angles([2, 1, 0, 1])
    sb = laminate.symmetry_balance(laminate.layers(m, [(x, t) for x in ac]))
    check_true("stack encoding is symmetric + balanced (composites.symmetry_balance)", sb["symmetric"] and sb["balanced"]
               and sb["B_zero"] and sb["A16_A26_zero"] and KO.balance_symmetry(ac) == (True, True), sb,
               source="[LR94] §3.1.2 data structure")
    check_true("balance_symmetry: [30/0] is neither balanced nor symmetric",
               KO.balance_symmetry([30.0, 0.0]) == (False, False), source="definition")
    r = laminate.progressive_failure(laminate.layers(m, [(x, t) for x in ac]), [1e4, 2e3, 1e3, 0, 0, 0])
    check("FPF objective = composites.progressive_failure first-ply load", KO.evaluate_stack(ac, m, t, "fpf",
          (1e4, 2e3, 1e3)), r["fpf"], rtol=1e-9, source="consistency: composites.progressive_failure")


def test_le_riche_tables():
    # Table 3.2: 64 plies, a = 20 in, b = 10 in, Ny/Nx = 1, buckling only; five different stacks with the same λ
    t32 = {"(90₁₀,±45₂,90₂,±45₃,90₂,±45₄)s": ([2] * 5 + [1, 1, 2, 1, 1, 1, 2] + [1] * 4, 14205.18),
           "(±45,90₁₀,±45,90₈,±45,90₈)s": ([1] + [2] * 5 + [1] + [2] * 4 + [1] + [2] * 4, 8935.74),
           "(90₄,±45₂,90₁₆,±45,90₆)s": ([2, 2, 1, 1] + [2] * 8 + [1] + [2] * 3, 8935.74),
           "(90₂,±45,90₆,±45,90₈,±45,90₁₀)s": ([2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1] + [2] * 5, 8935.74),
           "(90₈,±45,90₂,±45,90₂,±45,90₂,±45₆)s": ([2, 2, 2, 2, 1, 2, 1, 2, 1, 2] + [1] * 6, 14205.18)}
    for name, (code, strength) in t32.items():
        # the table is printed with 2 decimals: rounding 0.005/3973 ≈ 1.3e-6 → rtol 3e-6
        check(f"LR94 T3.2 {name}: buckling λ = 3973.01", _lr(code, "buckling", 1.0, 20, 10), 3973.01, rtol=3e-6,
              source=LR.format("3.2", 51))
        check(f"LR94 T3.2 {name}: strain λ = {strength}", _lr(code, "strain", 1.0, 20, 10), strength, rtol=1e-6,
              source=LR.format("3.2", 51))
    # Table 3.1: 48 plies, a = 20, b = 5, Ny/Nx = 0.5; buckling + strain + contiguity
    t31 = [([2, 1, 1, 2, 1, 2] + [1] * 6, 9998.19), ([2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 1], 9997.60),
           ([1, 2, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1], 9976.58)]
    for code, lam in t31:
        check(f"LR94 T3.1 {KO.stack_text(code)}: buckling λ = {lam}", _lr(code, "buckling", 0.5, 20, 5), lam,
              rtol=3e-6, source=LR.format("3.1", 51))
        check_true(f"LR94 T3.1 {KO.stack_text(code)}: contiguity ≤ 4", KO.adjacency_max(KO.stack_angles(code)) <= 4,
                   source=LR.format("3.1", 51))
    for code, _ in t31[1:]:
        check(f"LR94 T3.1 {KO.stack_text(code)}: strain λ = 10187.93", _lr(code, "strain", 0.5, 20, 5), 10187.93,
              rtol=1e-6, source=LR.format("3.1", 51))
    # NOTE: the "Strength" value of Table 3.1 row 1 is printed as 10394.81; 10398.14 is computed here
    # (difference 3.2e-4). With the same material/allowables rows 2–3 and the five rows of Table 3.2 agree
    # to 7 digits; the difference could not be resolved, so that number is not tested (tolerance not relaxed).


def test_le_riche_optimum_search():
    I, L = INCH, LBF
    r = KO.exhaustive_search(M_LR, T_LR, 12, "buckling_strain", load=(L, 0.5 * L), a=20 * I, b=5 * I,
                             strain_allowed=KO.LR94_STRAIN, FS=1.5, top_k=3)
    check("exhaustive search (3¹² designs) global optimum λ = 9998.19", r["value"], 9998.19, rtol=3e-6,
          source=LR.format("3.1", 51) + ": 'global optimum'")
    check_true("global optimum stack = (90₂,±45₂,90₂,±45,90₂,±45₆)s", r["codes"] == [2, 1, 1, 2, 1, 2] + [1] * 6,
               r["stack"], source=LR.format("3.1", 51))
    check("vectorized value = recomputation with composites", r["value"], r["value_composite"], rtol=1e-10,
          source="consistency")
    check("second best λ = 9997.60 (same value as table row 2)", r["top_designs"][1]["value"], 9997.60, rtol=3e-6,
          source=LR.format("3.1", 51))
    unconstrained = KO.exhaustive_search(M_LR, T_LR, 12, "buckling", load=(L, 0.5 * L), a=20 * I, b=5 * I,
                                         max_contiguous=None, top_k=1)
    check_true("unconstrained buckling optimum ≥ constrained optimum", unconstrained["value"] >= r["value"],
               source="derivation")
    g = KO.genetic_algorithm(M_LR, T_LR, 12, "buckling_strain", load=(L, 0.5 * L), a=20 * I, b=5 * I,
                             strain_allowed=KO.LR94_STRAIN, FS=1.5, seed=0)
    check("GA (48 plies) finds the exhaustive-search optimum", g["value"], r["value"], rtol=1e-12,
          source="cross-check: exhaustive search")
    check_true("GA: number of unique evaluations ≪ 3¹² = 531441", g["n_evaluation"] < 531441 // 20,
               g["n_evaluation"], source="definition")
    check_true("GA practical optima within ‰1 of the best", all(p["value"] >= g["value"] * 0.999
                                                               for p in g["practical_optima"]),
               source="[LR94] §3.3.1 definition of practical optimum")
    g64 = KO.genetic_algorithm(M_LR, T_LR, 16, "buckling", load=(L, L), a=20 * I, b=10 * I, max_contiguous=None,
                               seed=1, stagnation=200, max_generations=2000)
    check("GA (64 plies, 3¹⁶ ≈ 4.3e7 designs) λ = 3973.01", g64["value"], 3973.01, rtol=3e-6,
          source=LR.format("3.2", 51))
    p = KO.permutation_search(M_LR, T_LR, [2] * 13 + [1] * 3, "buckling", load=(L, L), a=20 * I, b=10 * I,
                              max_contiguous=None)
    check_true("permutation search is exact (560 permutations)", p["exact"] and p["n_permutation"] == 560,
               p["n_permutation"], source="16!/(13!·3!) = 560")
    check("permutation (13×90₂ + 3×±45) optimum λ = 3973.01", p["value"], 3973.01, rtol=3e-6,
          source=LR.format("3.2", 51) + " (different stack with the same λ)")
    ph = KO.permutation_search(M_LR, T_LR, [2] * 13 + [1] * 3, "buckling", load=(L, L), a=20 * I, b=10 * I,
                               max_contiguous=None, limit=10)
    start = _lr(sorted([2] * 13 + [1] * 3), "buckling", 1.0, 20, 10)
    check_true("hill climbing: better than the start, not better than the exact optimum",
               start <= ph["value"] <= p["value"] * (1 + 1e-12),
               f"{start:.6g} ≤ {ph['value']:.6g} ≤ {p['value']:.6g}", source="derivation")


def test_stiffness_shear_buckling_optima():
    m = laminate.KAW_GLASS_EPOXY
    t = 0.15e-3
    r = KO.exhaustive_search(m, t, 6, "stiffness", load=(1.0, 0.0, 0.0), max_contiguous=None)
    check_true("uniaxial Nx, stiffness: optimum is all 0°", r["codes"] == [0] * 6, r["stack"], source="derivation: Ex ≤ E1")
    check("uniaxial: E_eff = E1", r["value"], m["E1"], rtol=1e-12, source="definition (UD laminate)")
    r = KO.exhaustive_search(m, t, 6, "stiffness", load=(0.0, 0.0, 1.0), max_contiguous=None)
    check_true("pure shear Nxy, stiffness: optimum is all ±45", r["codes"] == [1] * 6, r["stack"],
               source="derivation: A66 = h(U5 − U3V2), largest at V2 = −1")
    U = KO.U_invariants(m)
    check("pure shear: Gxy = U5 + U3 = (Q11 + Q22 − 2Q12)/4", r["value"], U[4] + U[2], rtol=1e-12, source="derivation")
    a = b = 0.3
    rb = KO.exhaustive_search(m, t, 6, "buckling", load=(1e3, 0.0), a=a, b=b)
    check_true("square plate, uniaxial buckling: optimum is all ±45", rb["codes"] == [1] * 6, rb["stack"],
               source="derivation: λ ∝ D11 + 2(D12 + 2D66) + D22 = h³/12(2U1 + 2U4 + 4U5 − 4U3W2)")
    D = laminate.abd_matrix(laminate.layers(m, [(x, t) for x in rb["angles"]]))[2]
    check("square plate: λ = π²(D11 + 2(D12 + 2D66) + D22)/(a²·Nx) (m = n = 1)", rb["value"],
          math.pi ** 2 * (D[0, 0] + 2 * (D[0, 1] + 2 * D[2, 2]) + D[1, 1]) / (a ** 2 * 1e3), rtol=1e-12,
          source="[MIL] 5.7.1.6(a), m = n = 1, composites.plate_buckling")
    gb = KO.genetic_algorithm(m, t, 6, "buckling", load=(1e3, 0.0), a=a, b=b, seed=3)
    check("GA square plate = exhaustive search", gb["value"], rb["value"], rtol=1e-12, source="cross-check")
    s = KO.continuous_angle_optimize(m, t, 2, "buckling", load=(1e3, 0.0), a=a, b=b)
    check("continuous angles, square plate buckling: θ = 45°", np.max(np.abs(s["theta"] - 45.0)), 0.0, atol=1e-2,
          source="derivation: W2 = cos4θ = −1")
    check_true("continuous optimum ≥ discrete optimum (same ply count, 8 plies)",
               s["value"] >= KO.exhaustive_search(m, t, 2, "buckling", load=(1e3, 0.0), a=a, b=b)["value"] * (1 - 1e-9),
               source="derivation: the discrete set is a subset of the continuous set")
    s0 = KO.continuous_angle_optimize(m, t, 2, "stiffness", load=(1.0, 0.0, 0.0))
    check("continuous angles, uniaxial stiffness: θ = 0°", np.max(np.abs(s0["theta"])), 0.0, atol=1e-3,
          source="derivation")
    sk = KO.continuous_angle_optimize(m, t, 2, "stiffness", load=(0.0, 0.0, 1.0))
    check("continuous angles, pure shear stiffness: θ = 45°", np.max(np.abs(sk["theta"] - 45.0)), 0.0, atol=1e-3,
          source="derivation")
    # FPF, uniaxial tension: all 0° and Tsai–Wu R = Xt·h/Nx (σ2 = τ12 = 0 → root of F1σ + F11σ² = 1 is Xt)
    rf = KO.exhaustive_search(m, t, 3, "fpf", load=(1e5, 0.0, 0.0), max_contiguous=None)
    check_true("FPF uniaxial tension: optimum is all 0°", rf["codes"] == [0] * 3, rf["stack"], source="derivation")
    check("FPF uniaxial: R = Xt·h/Nx", rf["value"], m["Xt"] * 12 * t / 1e5, rtol=1e-10,
          source="derivation: Tsai–Wu is exact at Xt in uniaxial loading")
    expect_error("buckling objective without a, b → error", KO.StackEvaluator, m, t, 4, "buckling", error=ValueError)
    expect_error("strain objective without allowables → error", KO.StackEvaluator, m, t, 4, "strain", error=ValueError)
    expect_error("unknown objective → error", KO.evaluate_stack, [0.0, 0.0], m, t, "no", error=ValueError)
