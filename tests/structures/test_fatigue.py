"""Tests of the fatigue module: S-N, strain-life, Marin, mean stress, rainflow, Miner, Kt, Neuber."""
import math

import numpy as np

from aerokit.structures import fatigue as y
from aerokit.verification import check, check_true, expect_error

MPA = 1e6
HIJAZI6 = "Shigley 10th ed. Ch. 6, Hijazi CH6 lecture notes"
GANTEP = "Gaziantep Univ. 'Tutorial – Fatigue Design-1' (based on Shigley-Mischke)"
ASTM = ("ASTM E1049-85 Sec. 5.4.4 example sequence (the same sequence read in the ffpack documentation); expected "
        "counts as quoted from the ASTM table in iamlikeme/rainflow #4 (read) + hand tracing")
DEGH = "Deghboudj, Satha & Boukhedena, U.P.B. Sci. Bull. D 78(4) 2016, Table 1 (read)"


def test_sn_shigley_example():
    # 1045 CD, Sut = 630 MPa (Hijazi CH6 p. 11 example)
    check("S'e = 0.5 Sut = 315 MPa", y.se_estimated(630 * MPA) / MPA, 315, source=HIJAZI6 + " pp. 5, 11")
    check("S'e upper limit 700 MPa (Sut > 1400)", y.se_estimated(1600 * MPA) / MPA, 700, source=HIJAZI6 + " p. 5")
    s = y.shigley_sn(630 * MPA, 315 * MPA)
    check("σ'f = Sut + 345 = 975 MPa", s["sigma_f"] / MPA, 975, source=HIJAZI6 + " p. 11")
    check("b = −0.0779", s["b"], -0.0779, rtol=1e-3, source=HIJAZI6 + " p. 11")
    check("f = 0.856", s["f"], 0.856, rtol=1e-3, source=HIJAZI6 + " p. 11")
    # The source rounds f to 0.856 and computes a from it → ~0.05 % difference in a and Sf; rtol 1e-3
    check("a = 923.4 MPa", s["a"] / MPA, 923.4, rtol=1e-3, source=HIJAZI6 + " p. 11")
    check("Sf(5·10⁴) = 397.5 MPa", y.sn_strength(s["a"], s["b"], 5e4) / MPA, 397.5, rtol=1e-3,
          source=HIJAZI6 + " p. 11")
    # Life is very sensitive to b; checked with the source's rounded a = 923.4, b = −0.0779
    check("N(400 MPa) = 46.14·10³ (with the source's a, b)", y.sn_life(923.4 * MPA, -0.0779, 400 * MPA), 46.14e3,
          rtol=1e-3, source=HIJAZI6 + " p. 11")
    check("sn_life ∘ sn_strength = identity", y.sn_life(s["a"], s["b"], y.sn_strength(s["a"], s["b"], 2.5e5)), 2.5e5,
          rtol=1e-10, source="derivation")
    check("Shigley line reaches Se at Ne = 10⁶", y.sn_strength(s["a"], s["b"], 1e6) / MPA, 315, rtol=2e-3,
          source="derivation: a = (fSut)²/Se, b = −log(fSut/Se)/3 → a·10^(6b) = Se")
    check("Basquin round trip", y.basquin_life(y.basquin_amplitude(900 * MPA, -0.09, 1e5), 900 * MPA, -0.09), 1e5,
          rtol=1e-10, source="derivation")
    expect_error("Se ≥ Sut is rejected", y.shigley_sn, 300 * MPA, 400 * MPA, error=ValueError)


def test_strain_life():
    E, sf, b, ef, c = 200e9, 1000 * MPA, -0.09, 0.6, -0.6
    N = 3.7e4
    ea = y.coffin_manson_amplitude(N, E, sf, b, ef, c)
    check("Coffin-Manson inverse", y.coffin_manson_life(ea, E, sf, b, ef, c), N, rtol=1e-9, source="derivation")
    twoNt = y.transition_life(E, sf, b, ef, c)
    check("transition life: elastic = plastic amplitude", sf / E * twoNt ** b, ef * twoNt ** c, rtol=1e-12,
          source="derivation: (σ'f/E)(2Nt)^b = ε'f(2Nt)^c")
    check("Morrow σm = 0 → uncorrected", y.coffin_manson_amplitude(N, E, sf, b, ef, c, 0.0, "morrow"), ea,
          source="derivation")
    Nm = y.coffin_manson_life(ea, E, sf, b, ef, c, 200 * MPA, "morrow")
    check_true("Morrow: a tensile mean shortens life", Nm < N, f"{Nm:.4g} < {N:.4g}", source="derivation")
    # SWT: σm = 0 and a stabilised cycle with σmax = σa = σ'f(2N)^b → life unchanged
    smax = sf * (2 * N) ** b
    check("SWT σm = 0 → same life as Coffin-Manson", y.coffin_manson_life(ea, E, sf, b, ef, c, smax, "swt"), N,
          rtol=1e-9, source="derivation: σmax εa = σa εa")


def test_marin():
    check("ka machined, Sut 620 MPa = 0.821", y.marin_ka(620 * MPA, "machined"), 0.821, rtol=1e-3,
          source=HIJAZI6 + " p. 12 example")
    check("ka machined, Sut 630 MPa = 0.817", y.marin_ka(630 * MPA, "machined"), 0.817, rtol=1e-3,
          source=HIJAZI6 + " p. 19 example")
    check("ka forged, Sut 620 MPa = 0.453", y.marin_ka(620 * MPA, "forged"), 0.453, rtol=1e-3,
          source=GANTEP + ", Problem 2")
    check("kb = 1.24 d^−0.107 (d = 25 mm)", y.marin_kb(0.025), 1.24 * 25 ** -0.107, source=HIJAZI6 + " p. 6")
    check("kb = 1.51 d^−0.157 (d = 100 mm)", y.marin_kb(0.1), 1.51 * 100 ** -0.157, source=HIJAZI6 + " p. 6")
    check("kb axial = 1", y.marin_kb(0.1, "axial"), 1.0, source=HIJAZI6 + " p. 6")
    for load, value in (("bending", 1.0), ("axial", 0.85), ("torsion", 0.59)):
        check(f"kc {load} = {value}", y.marin_kc(load), value, source=HIJAZI6 + " p. 7")
    check("kd(100 °C) ≈ 1.02", y.marin_kd(100), 1.02, rtol=5e-3,
          source=GANTEP + ", Problem 1 (table value 1.02; polynomial Hijazi CH6 p. 7)")
    check("ke(90 %) = 0.897", y.marin_ke(0.90), 0.897, rtol=1e-3, source=GANTEP + ", Problem 1 (table A3-19)")
    check("ke(50 %) = 1", y.marin_ke(0.5), 1.0, source="derivation: z = 0")
    check("Se = ka kc S'e = 218.8 MPa", y.marin_se(315 * MPA, ka=0.817, kc=0.85) / MPA, 218.8, rtol=1e-3,
          source=HIJAZI6 + " p. 19")
    expect_error("kb rejects a diameter outside the validity range", y.marin_kb, 0.5, error=ValueError)
    expect_error("unknown surface is rejected", y.marin_ka, 600 * MPA, "sandblasted", error=ValueError)


def test_mean_stress():
    sa, Sut, Sy, sf = 120 * MPA, 600 * MPA, 450 * MPA, 900 * MPA
    for method in ("goodman", "gerber", "soderberg", "morrow", "swt"):
        check(f"{method}: σm = 0 → σar = σa",
              y.equivalent_fully_reversed(sa, 0.0, method, Sut=Sut, Sy=Sy, sigma_f=sf), sa, source="derivation")
    check("walker: σm = 0 → σar = σa", y.equivalent_fully_reversed(sa, 0.0, "walker", gamma=0.65), sa,
          source="derivation")
    sm = 100 * MPA
    check("walker γ = 0.5 = SWT", y.equivalent_fully_reversed(sa, sm, "walker", gamma=0.5),
          y.equivalent_fully_reversed(sa, sm, "swt"), rtol=1e-12, source="derivation: special case of Walker 1970")
    g = y.equivalent_fully_reversed(sa, sm, "goodman", Sut=Sut)
    ge = y.equivalent_fully_reversed(sa, sm, "gerber", Sut=Sut)
    so = y.equivalent_fully_reversed(sa, sm, "soderberg", Sy=Sy)
    check_true("ordering: Gerber < Goodman < Soderberg", ge < g < so,
               f"{ge/MPA:.1f} < {g/MPA:.1f} < {so/MPA:.1f}", source="derivation: Sy < Sut, parabola outside the line")
    # Goodman safety factor ↔ equivalent amplitude: (nσa, nσm) on the Goodman line → σar(nσa, nσm) = Se
    # (the first version stated "n = Se/σar"; that holds only for a fixed σm, not along the load line)
    Se = 250 * MPA
    ng = y.safety_coefficient(sa, sm, Se, Sut)
    check("Goodman: σar = Se for (nσa, nσm)", y.equivalent_fully_reversed(ng * sa, ng * sm, "goodman", Sut=Sut), Se,
          rtol=1e-12, source="derivation")
    check("Gerber n (σm → 0) → Se/σa", y.safety_coefficient(sa, 1e-3, Se, Sut, method="gerber"), Se / sa,
          rtol=1e-6, source="derivation: limit")
    # Gerber safety factor: (nσa/Se) + (nσm/Sut)² = 1 must hold
    n = y.safety_coefficient(sa, sm, Se, Sut, method="gerber")
    check("Gerber n lies on the curve", n * sa / Se + (n * sm / Sut) ** 2, 1.0, rtol=1e-12, source="derivation")
    # Hijazi pp. 19-20 example: σa = σm = 73.6 MPa, Se = 218.8, Sut = 630
    check("Goodman intersection Sa = 162.4 MPa", y.goodman_intersection(1.0, 218.8, 630)["Sa"], 162.4, rtol=1e-3,
          source=HIJAZI6 + " p. 20 (the formula shows 620, the number matches 630)")
    check("Goodman nf = 2.21", y.safety_coefficient(73.6, 73.6, 218.8, 630), 2.21, rtol=2e-3,
          source=HIJAZI6 + " p. 20")
    # The source truncated 3.288 to 3.28 (not rounded) → rtol 3e-3
    check("Goodman n = 3.28 (σ'a 62.4, σ'm 7.43, Se 212.7, Sut 690)",
          y.safety_coefficient(62.4, 7.43, 212.7, 690), 3.28, rtol=3e-3, source=GANTEP + ", Problem 1")
    expect_error("Goodman σm ≥ Sut is rejected", y.equivalent_fully_reversed, sa, Sut, "goodman", Sut=Sut,
                 error=ValueError)
    expect_error("SWT σmax ≤ 0 is rejected", y.equivalent_fully_reversed, 50 * MPA, -80 * MPA, "swt",
                 error=ValueError)


def test_rainflow_astm():
    series = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    summary = y.rainflow_summary(series)
    expected = {3.0: 0.5, 4.0: 1.5, 6.0: 0.5, 8.0: 1.0, 9.0: 0.5}
    check_true("ASTM example: set of ranges {3, 4, 6, 8, 9}", set(summary) == set(expected), str(summary),
               source=ASTM)
    for interval, n in expected.items():
        check(f"ASTM example: range {interval:g} → {n} cycles", summary.get(interval, 0.0), n, source=ASTM)
    check("ASTM example: 4.0 cycles in total", sum(summary.values()), 4.0, source=ASTM)
    full = [r for r in y.rainflow(series) if r[2] == 1.0]
    check_true("ASTM example: a single full cycle, range 4, mean 1 (E–F: −1/3)",
               len(full) == 1 and full[0][0] == 4.0 and full[0][1] == 1.0, str(full),
               source="derivation: hand tracing")


def test_rainflow_properties():
    k = 7
    t = np.linspace(0, 2 * math.pi * k, 2000 * k + 1)
    summary = y.rainflow_summary(np.cos(t), decimals=6)
    check("cosine series: k cycles in k periods (range 2)", summary.get(2.0, 0.0), k, source="derivation")
    check_true("cosine series: no other range", list(summary) == [2.0], str(summary), source="derivation")
    # small cycle embedded in a large one: 0 → 10 → 4 → 6 → −10 → 0
    r = y.rainflow([0, 10, 4, 6, -10, 0])
    full = [(a, n) for a, _, n in r if n == 1.0]
    check("embedded small cycle counted as full (range 2)", full[0][0] if full else -1, 2.0, source="derivation")
    check_true("plateaus and intermediate points are removed",
               y.turn_points([0, 1, 1, 2, 3, 3, 1, 0, 0, 5]) == [0, 3, 0, 5],
               str(y.turn_points([0, 1, 1, 2, 3, 3, 1, 0, 0, 5])), source="derivation")
    # total count ≈ (reversals − 1)/2 (each range contributes as a half cycle)
    rng = np.random.default_rng(1)
    s = rng.normal(size=500)
    tp = y.turn_points(s)
    check("random series: Σ counts = (reversals − 1)/2", sum(n for *_, n in y.rainflow(s)), (len(tp) - 1) / 2,
          source="derivation: each pair of reversals is counted once")
    expect_error("single-point series is rejected", y.rainflow, [1.0], error=ValueError)
    expect_error("series containing NaN is rejected", y.rainflow, [0, float("nan"), 1], error=ValueError)


def test_miner():
    a, b = 1500 * MPA, -0.1
    N_f = lambda s: y.sn_life(a, b, s)
    n = 2e4
    check("Miner constant amplitude D = n/N", y.miner_damage([(300 * MPA, n)], N_f), n / N_f(300 * MPA), rtol=1e-12,
          source="derivation: Palmgren-Miner definition")
    spectrum = [(400 * MPA, 1e3), (300 * MPA, 1e4), (200 * MPA, 1e5)]
    D = y.miner_damage(spectrum, N_f)
    check("Miner block life = 1/D", y.miner_life(spectrum, N_f), 1 / D, source="derivation")
    m = -1 / b
    Seq = y.equivalent_constant_amplitude([s for s, _ in spectrum], [c for _, c in spectrum], m)
    check("equivalent constant amplitude gives the same Miner damage", y.miner_damage([(Seq, 1e3 + 1e4 + 1e5)], N_f),
          D, rtol=1e-12, source="derivation: Basquin m = −1/b")
    check("single amplitude: equivalent amplitude is itself", y.equivalent_constant_amplitude([250.0], [10], 6.0),
          250.0, source="derivation")
    # rainflow + Miner chain: amplitude = range/2
    series = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    count = [(r / 2 * 100 * MPA, c) for r, _, c in y.rainflow(series)]
    D_hand = sum(c / N_f(s) for s, c in count)
    check("rainflow → Miner chain", y.miner_damage(count, N_f), D_hand, rtol=1e-12, source="derivation")
    expect_error("negative cycle count is rejected", y.miner_damage, [(1e8, -5)], N_f, error=ValueError)


def test_stress_concentration():
    check("circular hole Kt = 3 (Kirsch, a = b)", y.kt_ellipse(1.0, 1.0), 3.0, source="derivation: Inglis a = b")
    check("elliptical hole Kt = 1 + 2a/b (a/b = 3)", y.kt_ellipse(3.0, 1.0), 7.0, source="Inglis 1913 relation")
    for dW, net, gross in ((0.1, 2.729, 3.032), (0.3, 2.343, 3.347), (0.5, 2.125, 4.250)):
        check(f"Heywood Ktn (d/W = {dW})", y.kt_hole_heywood(dW, 1.0), net, rtol=5e-4, source=DEGH)
        check(f"Heywood Ktg (d/W = {dW})", y.kt_hole_heywood(dW, 1.0, "gross"), gross, rtol=5e-4, source=DEGH)
    for dW, gross in ((0.1, 3.035), (0.2, 3.148), (0.5, 4.314)):
        check(f"Howland fit Ktg (d/W = {dW})", y.kt_hole_howland(dW, 1.0, "gross"), gross, rtol=5e-4,
              source=DEGH)
    check("Heywood d/W → 0: Kt → 3", y.kt_hole_heywood(1e-9, 1.0), 3.0, rtol=1e-8, source="derivation: Kirsch limit")
    check("Howland d/W → 0: Kt → 3.004", y.kt_hole_howland(1e-9, 1.0), 0.284 + 2 - 0.6 + 1.32, rtol=1e-8,
          source="derivation (sum of the fit constants; 0.13 % off Kirsch's 3)")
    check("Kf = 1 + q(Kt − 1) (q 0.81, Kt 2.38) = 2.12", y.kf(2.38, 0.81), 2.12, rtol=2e-3,
          source=HIJAZI6 + " p. 12")
    check("Kf (q 0.82, Kt 1.5) = 1.41", y.kf(1.5, 0.82), 1.41, rtol=1e-3, source=GANTEP + ", Problem 1")
    r, ka = 0.003, 0.0018 ** 0.5
    check("Neuber q → Kf = 1 + (Kt − 1)/(1 + √a/√r)", y.kf(2.5, y.neuber_q(r, ka)),
          1 + 1.5 / (1 + ka / math.sqrt(r)), rtol=1e-12, source=HIJAZI6 + " p. 9")
    check("Peterson q = 1/(1 + α/r)", y.peterson_q(0.002, 0.0005), 0.8, source="derivation: relation")
    expect_error("q > 1 is rejected", y.kf, 2.0, 1.2, error=ValueError)
    expect_error("d ≥ W is rejected", y.kt_hole_heywood, 1.0, 1.0, error=ValueError)


def test_neuber_rule():
    E, K, n, Kt = 200e9, 1200 * MPA, 0.15, 2.5
    el = y.neuber_rule(20 * MPA, Kt, E, 1e15, n)
    check("Neuber: σ = Kt S for an elastic material", el["sigma"], Kt * 20 * MPA, rtol=1e-9, source="derivation")
    r = y.neuber_rule(250 * MPA, Kt, E, K, n)
    check("Neuber hyperbola σ ε = (Kt S)²/E", r["sigma"] * r["eps"], (Kt * 250 * MPA) ** 2 / E, rtol=1e-10,
          source="Neuber 1961 rule (definition)")
    check("Neuber point lies on the Ramberg-Osgood curve", r["eps"], y.ramberg_osgood(r["sigma"], E, K, n), rtol=1e-12,
          source="derivation")
    check_true("plastic range: σ < Kt S and ε > Kt S/E",
               r["sigma"] < Kt * 250 * MPA and r["eps"] > Kt * 250 * MPA / E,
               f"σ = {r['sigma']/MPA:.1f} MPa", source="derivation")
    ar = y.neuber_range(500 * MPA, Kt, E, K, n)
    check("cyclic Neuber Δσ Δε = (Kt ΔS)²/E", ar["d_sigma"] * ar["d_eps"], (Kt * 500 * MPA) ** 2 / E, rtol=1e-10,
          source="derivation: Masing")
    check("Masing Δε = Δσ/E + 2(Δσ/2K')^(1/n')", ar["d_eps"],
          ar["d_sigma"] / E + 2 * (ar["d_sigma"] / (2 * K)) ** (1 / n), rtol=1e-12, source="derivation")
    check("Neuber sign symmetry in compression", y.neuber_rule(-250 * MPA, Kt, E, K, n)["sigma"], -r["sigma"],
          rtol=1e-12, source="derivation")
