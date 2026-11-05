"""Tests of the rotating module: solid/annular disk, ring, bar, speed limits, burst, thermal term."""
import math

import numpy as np
from scipy import integrate

from aerokit.structures import rotating
from aerokit.verification import check, check_true, expect_error

RHO, NU, E = 7800.0, 0.3, 207e9
NAFEMS = "NAFEMS NBC08 (2017) 'Calculation of the Hoop Burst Speed for Rotating Discs' (read)"
HIJAZI3 = "Shigley 10th ed. Ch. 3, Hijazi CH3 notes p. 23 (read)"


def _derivative(f, r, h=1e-7):
    return (f(r + h) - f(r - h)) / (2 * h)


def test_solid_disk():
    w, b = 1500.0, 0.2
    s0 = rotating.solid_disk(RHO, w, b, NU, 0.0)
    center = (3 + NU) * RHO * w ** 2 * b ** 2 / 8
    check("solid disk centre σr = (3+ν)ρω²b²/8", s0["sr"], center,
          source="derivation: Timoshenko & Goodier rotating disk")
    check("solid disk centre σθ = σr", s0["st"], center, source="derivation: axial symmetry")
    check("solid disk σr(b) = 0 (free edge)", rotating.solid_disk(RHO, w, b, NU, b)["sr"], 0.0, atol=1e-6,
          source="derivation: boundary condition")
    check("solid disk σθ(b) = (1−ν)ρω²b²/4", rotating.solid_disk(RHO, w, b, NU, b)["st"],
          (1 - NU) * RHO * w ** 2 * b ** 2 / 4, source="derivation")
    f_sr = lambda r: rotating.solid_disk(RHO, w, b, NU, r)["sr"]
    for r in (0.05, 0.12, 0.18):
        s = rotating.solid_disk(RHO, w, b, NU, r)
        residual = _derivative(f_sr, r) + (s["sr"] - s["st"]) / r + RHO * w ** 2 * r
        check(f"solid disk equilibrium residual r = {r}", residual / center * b, 0.0, atol=1e-6,
              source="derivation: dσr/dr + (σr − σθ)/r + ρω²r = 0")
    # one-to-one with the Shigley/Hijazi form for ri = 0
    r = 0.13
    st_sh = RHO * w ** 2 * (3 + NU) / 8 * (b ** 2 - (1 + 3 * NU) / (3 + NU) * r ** 2)
    check("solid disk σθ = Shigley rotating-ring relation (ri = 0)", rotating.solid_disk(RHO, w, b, NU, r)["st"],
          st_sh, rtol=1e-12, source=HIJAZI3)


def test_annular_disk():
    w, a, b = 1200.0, 0.03, 0.25
    check("annular disk σr(a) = 0", rotating.annular_disk(RHO, w, a, b, NU, a)["sr"], 0.0, atol=1e-6,
          source="derivation: boundary condition")
    check("annular disk σr(b) = 0", rotating.annular_disk(RHO, w, a, b, NU, b)["sr"], 0.0, atol=1e-6,
          source="derivation: boundary condition")
    rr = np.linspace(a, b, 2001)
    st = rotating.annular_disk(RHO, w, a, b, NU, rr)["st"]
    check_true("annular disk: largest σθ at the hole edge", int(np.argmax(st)) == 0, f"argmax = {np.argmax(st)}",
               source="derivation")
    check("hole edge σθ = ρω²[(3+ν)b² + (1−ν)a²]/4", st[0],
          RHO * w ** 2 * ((3 + NU) * b ** 2 + (1 - NU) * a ** 2) / 4, rtol=1e-12, source="derivation")
    f_sr = lambda r: rotating.annular_disk(RHO, w, a, b, NU, r)["sr"]
    r = 0.1
    s = rotating.annular_disk(RHO, w, a, b, NU, r)
    residual = _derivative(f_sr, r) + (s["sr"] - s["st"]) / r + RHO * w ** 2 * r
    check("annular disk equilibrium residual", residual * b / st[0], 0.0, atol=1e-6, source="derivation")
    r = 0.17
    st_sh = RHO * w ** 2 * (3 + NU) / 8 * (a ** 2 + b ** 2 + a ** 2 * b ** 2 / r ** 2 - (1 + 3 * NU) / (3 + NU) * r ** 2)
    sr_sh = RHO * w ** 2 * (3 + NU) / 8 * (a ** 2 + b ** 2 - a ** 2 * b ** 2 / r ** 2 - r ** 2)
    s = rotating.annular_disk(RHO, w, a, b, NU, r)
    check("annular disk σθ = Shigley rotating-ring relation", s["st"], st_sh, rtol=1e-12, source=HIJAZI3)
    check("annular disk σr = Shigley rotating-ring relation", s["sr"], sr_sh, rtol=1e-12, source=HIJAZI3)
    # very small hole: σθ(hole) → 2 × solid-disk centre value (stress concentration 2)
    small = rotating.annular_disk(RHO, w, 1e-6, b, NU, 1e-6)["st"]
    center = rotating.solid_disk(RHO, w, b, NU, 0.0)["st"]
    check("small-hole disk σθ(a) ≈ 2 × solid-disk centre", small / center, 2.0, rtol=1e-9,
          source="derivation: a → 0 limit, (3+ν)b²/4 ÷ (3+ν)b²/8")
    # displacement: u(b) = r σθ/E (σr = 0)
    u = rotating.annular_disk(RHO, w, a, b, NU, b, E=E)["u"]
    check("annular disk u(b) = b σθ(b)/E", u, b * rotating.annular_disk(RHO, w, a, b, NU, b)["st"] / E, rtol=1e-12,
          source="derivation: plane-stress Hooke")
    expect_error("annular disk rejects a ≥ b", rotating.annular_disk, RHO, w, 0.3, 0.2, NU, error=ValueError)
    expect_error("r outside the disk is rejected", rotating.solid_disk, RHO, w, 0.2, NU, 0.3, error=ValueError)


def test_ring_bar_speed():
    w, R = 900.0, 0.4
    check("thin ring σθ = ρω²R²", rotating.thin_ring(RHO, w, R), RHO * (w * R) ** 2,
          source="derivation: ring equilibrium")
    # annular disk with a → b (thin ring): average σθ → ρω²R²
    a, b = 0.399, 0.401
    avg = rotating.mean_hoop_stress(RHO, w, b, a)
    check("annular disk a → b: average σθ → thin ring", avg, rotating.thin_ring(RHO, w, 0.4), rtol=1e-5,
          source="derivation: ρω²(b³ − a³)/(3(b − a)) → ρω²R²")
    check("ring speed limit round trip", rotating.thin_ring(RHO, rotating.ring_speed_limit(300e6, RHO, R), R),
          300e6, source="derivation")
    rk, ru, Ac, m_tip = 0.2, 0.5, 2e-4, 0.05
    check("rotating bar root stress ρω²(ru² − rk²)/2", rotating.rotating_bar(RHO, w, rk, ru),
          RHO * w ** 2 * (ru ** 2 - rk ** 2) / 2, source="derivation: section equilibrium")
    # root force = ∫ρAω²r dr + m ω² ru (independent numerical integral)
    force = integrate.quad(lambda r: RHO * Ac * w ** 2 * r, rk, ru)[0] + m_tip * w ** 2 * ru
    check("bar with tip mass: σ_root·A = centrifugal force",
          rotating.rotating_bar(RHO, w, rk, ru, tip_mass=m_tip, A=Ac) * Ac,
          force, rtol=1e-10, source="derivation: numerical integral")
    check("rotating bar σ = 0 at the tip", rotating.rotating_bar(RHO, w, rk, ru, r=ru), 0.0, atol=1e-9,
          source="derivation")
    ws = rotating.disk_speed_limit(400e6, RHO, 0.25, NU, a=0.03)
    check("at the disk speed limit max σ = σ_allow", rotating.disk_max_stress(RHO, ws, 0.25, NU, a=0.03), 400e6,
          source="derivation: σ ∝ ω²")
    expect_error("tip mass without area is rejected", rotating.rotating_bar, RHO, w, rk, ru, None, 0.1,
                 error=ValueError)


def test_burst():
    # NBC08: parallel disk, average σθ = 26 MPa at ω = 1000 rad/s; centre "just over 32 MPa".
    # The geometry is in a figure, not the text; ρ = 7800, b = 0.1 m, ν = 0.3 are consistent with both values
    # (inferred).
    check("NBC08 average σθ = 26 MPa (ω = 1000 rad/s)", rotating.mean_hoop_stress(RHO, 1000, 0.1) / 1e6,
          26.0, rtol=1e-3, source=NAFEMS + " pp. 2-3; geometry inferred")
    center = rotating.solid_disk(RHO, 1000, 0.1, NU, 0.0)["st"] / 1e6
    check_true("NBC08 centre stress 'just over 32 MPa'", 32.0 < center < 32.5, f"{center:.3f} MPa", source=NAFEMS)
    check("NBC08 theoretical burst speed 6202 rad/s (UTS 1000 MPa)", rotating.burst_speed(1000e6, 26e6, 1000), 6202,
          rtol=1e-4, source=NAFEMS + " PDF p. 5: theoretical plastic limit speed 6202 rad/s (Tresca)")
    ratio = rotating.disk_burst_speed(1000e6, RHO, 0.1) / rotating.disk_speed_limit(1000e6, RHO, 0.1, NU)
    check_true("NBC08 plastic/elastic limit speed ratio 'just over 10%'", 1.10 < ratio < 1.12, f"{ratio:.4f}",
               source=NAFEMS + " Eq. 7")
    check("plastic/elastic ratio = √(3(3+ν)/8)", ratio, math.sqrt(3 * (3 + NU) / 8), rtol=1e-12,
          source="derivation: centre (3+ν)/8 ÷ average 1/3")
    # static closed form of the average σθ = numerical integral of the elastic solution (independent of ν)
    for nu in (0.25, 0.33):
        check(f"average σθ statics = numerical integral (annular, ν = {nu})",
              rotating.mean_hoop_stress(RHO, 1000, 0.25, 0.05, nu=nu, numeric=True),
              rotating.mean_hoop_stress(RHO, 1000, 0.25, 0.05), rtol=1e-10,
              source="derivation: half-disk equilibrium")
    check("η = 0.9 scales the burst speed by √0.9", rotating.burst_speed(1000e6, 26e6, 1000, eta=0.9),
          6201.7367 * math.sqrt(0.9), rtol=1e-6, source="derivation")
    expect_error("η > 1 is rejected", rotating.burst_speed, 1e9, 26e6, 1000, 1.2, error=ValueError)


def test_thermal():
    alpha, b, a = 12e-6, 0.2, 0.04
    check("uniform ΔT, solid disk: σθ = 0", rotating.thermal_disk(lambda r: 100.0, alpha, E, b, r=0.1)["st"], 0.0,
          atol=1e-3, source="derivation: free expansion")
    check("uniform ΔT, annular disk: σr = 0",
          rotating.thermal_disk(lambda r: 100.0, alpha, E, b, a=a, r=0.1)["sr"], 0.0, atol=1e-3, source="derivation")
    T = lambda r: 150.0 * (r / b) ** 2
    check("thermal annular disk σr(a) = 0", rotating.thermal_disk(T, alpha, E, b, a=a, r=a)["sr"], 0.0, atol=1e-3,
          source="derivation: boundary condition")
    check("thermal annular disk σr(b) = 0", rotating.thermal_disk(T, alpha, E, b, a=a, r=b)["sr"], 0.0, atol=1e-3,
          source="derivation: boundary condition")
    check("thermal solid disk σr(b) = 0", rotating.thermal_disk(T, alpha, E, b, r=b)["sr"], 0.0, atol=1e-3,
          source="derivation")
    # equilibrium (no body force): dσr/dr + (σr − σθ)/r = 0
    f = lambda r: rotating.thermal_disk(T, alpha, E, b, a=a, r=r)["sr"]
    r = 0.11
    s = rotating.thermal_disk(T, alpha, E, b, a=a, r=r)
    check("thermal disk equilibrium residual",
          (_derivative(f, r, 1e-6) + (s["sr"] - s["st"]) / r) * b / (alpha * E * 150), 0.0,
          atol=1e-6, source="derivation")
    # T = c r²: at the solid-disk centre σr = σθ = αE c b²/4 (closed-form integral)
    c = 150.0 / b ** 2
    check("thermal solid disk centre σr = αE c b²/4 − 0 (T = c r²)", rotating.thermal_disk(T, alpha, E, b, r=0.0)["sr"],
          alpha * E * c * b ** 2 / 4, rtol=1e-9, source="derivation: (1/b²)∫₀ᵇ c r³ dr")
