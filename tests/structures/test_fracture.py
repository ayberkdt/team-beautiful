"""Tests of the fracture module: K, finite width, critical crack, plastic zone, Paris/Walker/Forman."""
import math

import numpy as np

from aerokit.structures import fracture as k
from aerokit.verification import check, check_true, expect_error

MPA = 1e6
ARANDA = "Aranda et al., arXiv:2009.06588 App. A.1 (read): Eq. A.2 [NASA TN D-2395], Eq. A.4 [Tada-Paris-Irwin]"


def test_sif_and_finite_width():
    check("infinite plate centre crack K = σ√(πa)", k.sif(100 * MPA, 0.01), 100 * MPA * math.sqrt(math.pi * 0.01),
          source="Irwin definition")
    for W in (1e3, 1e6):
        check(f"secant correction W → ∞ (W/a = {W:g})", k.Y_center_secant(1.0, W), 1.0, rtol=2 * (math.pi / W) ** 2,
              source="derivation: √sec(x) = 1 + x²/4 + …")
    check("secant: small-a/W series expansion", k.Y_center_secant(0.01, 1.0), 1 + (math.pi * 0.01) ** 2 / 4,
          rtol=1e-7, source="derivation: √sec(x) ≈ 1 + x²/4")
    check("Tada centre crack W → ∞", k.Y_center_tada(1.0, 1e6), 1.0, rtol=1e-10, source="derivation")
    for alpha in (0.2, 0.4, 0.6):
        check(f"Tada ≈ Feddersen secant (2a/W = {alpha})", k.Y_center_tada(alpha / 2, 1.0),
              k.Y_center_secant(alpha / 2, 1.0), rtol=3e-3,
              source="consistency: neither formula read from a source; agreement within 0.3 % expected")
        check(f"Isida-Brown ≈ secant (2a/W = {alpha})", k.Y_center_isida(alpha / 2, 1.0),
              k.Y_center_secant(alpha / 2, 1.0), rtol=1.2e-2,
              source="consistency: Brown polynomial not read from a source; ~1 % agreement expected")
    check_true("secant correction increases monotonically with a/W",
               all(np.diff([k.Y_center_secant(a, 1.0) for a in np.linspace(0.01, 0.45, 30)]) > 0),
               source="derivation")
    expect_error("secant 2a ≥ W is rejected", k.Y_center_secant, 0.5, 1.0, error=ValueError)
    expect_error("negative crack length is rejected", k.sif, 1e8, -0.01, error=ValueError)


def test_edge_crack():
    check("edge crack a/W → 0: Gross F → 1.122", k.Y_edge_gross(1e-9, 1.0), 1.122, rtol=1e-6, source=ARANDA)
    check("edge crack a/W → 0: Tada F → 1.122", k.Y_edge_tada(1e-9, 1.0), 1.122, rtol=1e-6, source=ARANDA)
    # each relation is accurate to 0.5 % → they must differ by ≤ 1 %
    for alpha in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        check(f"Gross ≈ Tada edge crack (a/W = {alpha})", k.Y_edge_gross(alpha, 1.0), k.Y_edge_tada(alpha, 1.0),
              rtol=1e-2, source=ARANDA + " (0.5 % each)")
    expect_error("Gross polynomial rejects a/W > 0.6", k.Y_edge_gross, 0.7, 1.0, error=ValueError)


def test_critical_and_residual():
    K_Ic, s = 30 * MPA, 200 * MPA
    ac = k.critical_crack(K_Ic, s)
    check("K = KIc at the critical crack (constant Y)", k.sif(s, ac), K_Ic, rtol=1e-12, source="derivation")
    check("critical crack (1/π)(KIc/σ)²", ac, (K_Ic / s) ** 2 / math.pi, source="derivation")
    W = 0.1
    acW = k.critical_crack(K_Ic, s, Y=lambda a: k.Y_center_secant(a, W), a_max=0.4999 * W)
    check("finite width: K = KIc at the critical crack", k.sif(s, acW, k.Y_center_secant(acW, W)), K_Ic, rtol=1e-10,
          source="derivation")
    check_true("finite width shortens the critical crack", acW < ac, f"{acW*1e3:.3f} < {ac*1e3:.3f} mm",
               source="derivation")
    check("residual strength ∘ critical crack = σ",
          k.residual_strength(K_Ic, acW, lambda a: k.Y_center_secant(a, W)), s, rtol=1e-10, source="derivation")
    expect_error("callable Y without a_max is rejected", k.critical_crack, K_Ic, s, lambda a: 1.0, error=ValueError)


def test_plastic_zone():
    K, sy = 40 * MPA, 400 * MPA
    ps = k.plastic_zone(K, sy, "plane_stress")
    pe = k.plastic_zone(K, sy, "plane_strain")
    check("Irwin plane stress r_y = (K/σy)²/(2π)", ps["r_y"], 0.01 / (2 * math.pi), rtol=1e-12,
          source="Irwin relation (general knowledge, not read from a source)")
    check("plane stress / plane strain = 3", ps["r_y"] / pe["r_y"], 3.0, source="derivation: 1/2π ÷ 1/6π")
    check("corrected diameter = 2 r_y", ps["diameter"], 2 * ps["r_y"], source="definition")
    expect_error("unknown case is rejected", k.plastic_zone, K, sy, "x", error=ValueError)


def test_paris_life():
    C, m, ds, a0, af = 6.9e-12, 3.0, 120.0, 1e-3, 2e-2      # C [m/cycle/(MPa√m)^m], Δσ in MPa
    N_closed = k.paris_life(C, m, ds, a0, af)
    N_numeric = k.paris_life_numeric(C, m, ds, a0, af)
    check("Paris closed form = numerical integral (Y = 1)", N_numeric, N_closed, rtol=1e-6,
          source="derivation: ∫da/(C(Δσ√πa)^m)")
    check("Paris closed form = numerical (Y = 1.12)", k.paris_life_numeric(C, m, ds, a0, af, 1.12),
          k.paris_life(C, m, ds, a0, af, 1.12), rtol=1e-6, source="derivation")
    check("Paris m = 2 branch = numerical", k.paris_life_numeric(C, 2.0, ds, a0, af), k.paris_life(C, 2.0, ds, a0, af),
          rtol=1e-6, source="derivation: ln(af/a0) branch")
    check("Paris m → 2 continuity", k.paris_life(C, 2.0 + 1e-7, ds, a0, af), k.paris_life(C, 2.0, ds, a0, af),
          rtol=1e-5, source="derivation: limit")
    check("Paris scaling: N ∝ Δσ^−m", k.paris_life(C, m, 2 * ds, a0, af), N_closed / 2 ** m, rtol=1e-12,
          source="derivation")
    # variable Y (edge crack, W = 50 mm): quad vs ODE (solve_ivp), two independent methods
    W = 0.05
    Y = lambda a: k.Y_edge_tada(a, W)
    rate = lambda a: k.paris_rate(Y(a) * ds * math.sqrt(math.pi * a), C, m)
    N_q = k.paris_life_numeric(C, m, ds, a0, 0.025, Y)
    Nt, at = k.crack_growth(rate, a0, 10 * N_q, 0.025)
    check("variable Y: quad life = ODE cycles to reach a_f", Nt[-1], N_q, rtol=1e-6,
          source="derivation: two independent numerical methods")
    check_true("variable Y (increasing F): life shorter than with constant 1.122",
               N_q < k.paris_life(C, m, ds, a0, 0.025, 1.122), source="derivation")
    expect_error("Paris af ≤ a0 is rejected", k.paris_life, C, m, ds, 0.02, 0.01, error=ValueError)


def test_rate_relations():
    C, m, dK = 1e-11, 3.2, 15.0
    check("Walker γ = 1 → Paris", k.walker_rate(dK, 0.5, C, m, 1.0), k.paris_rate(dK, C, m), rtol=1e-12,
          source="derivation: special case of Walker 1970")
    check("Walker R = 0 → Paris", k.walker_rate(dK, 0.0, C, m, 0.6), k.paris_rate(dK, C, m), rtol=1e-12,
          source="derivation")
    check_true("Walker: rate increases with R (γ < 1)",
               k.walker_rate(dK, 0.5, C, m, 0.6) > k.walker_rate(dK, 0.1, C, m, 0.6), source="derivation")
    Kc = 60.0
    check("Forman denominator (1−R)Kc − ΔK", k.forman_rate(dK, 0.2, C, m, Kc), C * dK ** m / (0.8 * Kc - dK),
          rtol=1e-12, source="Forman 1967 relation (definition)")
    check_true("Forman infinite as ΔK → (1−R)Kc", math.isinf(k.forman_rate(48.0, 0.2, C, m, Kc)), source="derivation")
    # Forman approaches Paris (C' = C/((1−R)Kc)) for a very large Kc
    Kb = 1e9
    check("Forman Kc → ∞: Paris (C/((1−R)Kc))", k.forman_rate(dK, 0.0, C, m, Kb), C / Kb * dK ** m, rtol=1e-7,
          source="derivation: limit")
    # Forman life: general numerical integral, shorter than the closed Paris life (rate larger everywhere,
    # with the C' mapping)
    ds, a0, af = 100.0, 1e-3, 1e-2
    Cp = C / Kc
    N_forman = k.life_numeric(lambda a: k.forman_rate(ds * math.sqrt(math.pi * a), 0.0, C, m, Kc), a0, af)
    check_true("Forman life shorter than the equivalent Paris life", N_forman < k.paris_life(Cp, m, ds, a0, af),
               f"{N_forman:.4g}", source="derivation: Kc/(Kc − ΔK) > 1")
    expect_error("Walker R ≥ 1 is rejected", k.walker_rate, dK, 1.0, C, m, 0.5, error=ValueError)
