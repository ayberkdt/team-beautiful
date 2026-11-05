"""Blade-element momentum theory (BEMT) for a rotor in hover and axial flight, single or coaxial.

**Per annulus** (non-dimensional radius ``r = y/R``, inflow ``λ = (V_c + v_i)/ΩR``, climb ``λ_c``), the momentum
thrust with Prandtl's tip-loss factor ``F`` equals the blade-element thrust (Leishman 2006, ch. 3)::

    dC_T = 4 F λ (λ − λ_c) r dr = ½ σ(r) (C_l cos φ − C_d sin φ) (r² + λ²) dr ,   φ = atan(λ / r)
    dC_Q = ½ σ(r) (C_l sin φ + C_d cos φ) (r² + λ²) r dr ,   C_P = C_Q
    F = (2/π) arccos(exp(−f)),  f = (N_b/2)(1 − r)/(r φ)

``λ`` is found per station by bracketing root search (so non-linear polars and stall are allowed); ``F`` is iterated.
The airfoil polar (:class:`Airfoil`) is a lift line with stall, the Prandtl–Glauert factor ``1/√(1 − M²)`` on the
lift, and a drag ``C_d = C_d0 (Re_ref/Re)^n + d₁ α + d₂ α²``; Reynolds and Mach numbers are computed locally from
the gas state (``aerokit.venus.gas`` for Venus, or any ``(ρ, μ, a)`` triple for validation against Earth tests).

**Coaxial rotors.** The upper rotor is solved as isolated. Its wake is taken as fully contracted to radius ``r_c``
(``1/√2`` for an ideal far wake) when it reaches the lower rotor, carrying the upper rotor's mass flow with uniform
velocity; the lower rotor therefore sees an extra climb inflow ``λ̄_u / r_c²`` inside ``r_c`` — the simplified
approach of Leishman & Ananthan (2008, read by the research agent, see ``C_*`` notes). :func:`coaxial_trim` finds
the rotor speeds for a given total thrust with zero net torque (torque-balanced).

**Validation**: :mod:`tests.test_venus_bemt` compares the model with the measured static thrust/power of
Harrington's (1951) rotors (data read by the research agent) and with the closed-form ideal-twist results.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np
from scipy.optimize import brentq

from aerokit.references import cite

__all__ = ["Airfoil", "Rotor", "FlowState", "BEMTResult", "solve", "solve_for_thrust", "solve_collective", "coaxial",
           "coaxial_trim", "CoaxialResult", "NACA0012_LEISHMAN", "venus_flow"]


@dataclass(frozen=True)
class Airfoil:
    """Section polar. Angles in radians."""

    cl_alpha: float = 5.73              # per rad, incompressible
    alpha0: float = 0.0                 # zero-lift angle
    cl_max: float = 1.2
    cd0: float = 0.011
    d1: float = -0.025
    d2: float = 0.65
    re_ref: float = 2.0e6
    re_exponent: float = 0.2            # cd0 ∝ Re^-n (turbulent-skin-friction-like; assumption)
    cd_stall: float = 0.3               # extra drag above stall (assumption)

    def coefficients(self, alpha: float, re: float, mach: float) -> tuple[float, float]:
        beta = math.sqrt(max(1.0 - mach * mach, 0.05))
        a = alpha - self.alpha0
        cl_lin = self.cl_alpha * a / beta
        clmax = self.cl_max
        if abs(cl_lin) <= clmax:
            cl = cl_lin
            stall = 0.0
        else:                            # simple post-stall: hold cl_max, add drag
            cl = math.copysign(clmax, cl_lin)
            stall = self.cd_stall * min(1.0, abs(cl_lin) / clmax - 1.0)
        cd0 = self.cd0 * (self.re_ref / max(re, 1.0)) ** self.re_exponent
        cd = cd0 + self.d1 * abs(alpha) + self.d2 * alpha * alpha + stall
        return cl, max(cd, 0.25 * cd0)


def _polar(af: Airfoil, alpha: np.ndarray, re: np.ndarray, mach: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised :meth:`Airfoil.coefficients`."""
    beta = np.sqrt(np.maximum(1.0 - mach * mach, 0.05))
    cl_lin = af.cl_alpha * (alpha - af.alpha0) / beta
    over = np.abs(cl_lin) > af.cl_max
    cl = np.where(over, np.sign(cl_lin) * af.cl_max, cl_lin)
    stall = np.where(over, af.cd_stall * np.minimum(1.0, np.abs(cl_lin) / af.cl_max - 1.0), 0.0)
    cd0 = af.cd0 * (af.re_ref / np.maximum(re, 1.0)) ** af.re_exponent
    cd = cd0 + af.d1 * np.abs(alpha) + af.d2 * alpha * alpha + stall
    return cl, np.maximum(cd, 0.25 * cd0)


# Generic symmetric-section polar (assumption [Y]): cl_alpha 5.73/rad (thin-airfoil 2π reduced ~9 %, the value
# Harrington 1951 used, p. 6, via the research note), cd = cd0 − 0.025|α| + 0.65α² (a commonly used NACA 0012 fit,
# not verified against a primary source in this session). cd0 is set per case from measured zero-thrust torque.
NACA0012_LEISHMAN = Airfoil()


@dataclass(frozen=True)
class Rotor:
    """Rotor geometry. Chord linear from root (at ``root_cutout``) to tip; twist linear, ``theta75`` at r = 0.75."""

    radius: float
    blades: int
    root_chord: float
    tip_chord: float
    theta75_deg: float
    twist_deg: float = 0.0              # tip minus root, linear (negative = washout)
    root_cutout: float = 0.15
    airfoil: Airfoil = field(default_factory=Airfoil)
    ideal_twist: bool = False           # θ = θ75 · 0.75 / r (hyperbolic, uniform inflow) instead of linear

    def chord(self, r: np.ndarray | float) -> np.ndarray | float:
        x = (np.asarray(r) - self.root_cutout) / (1.0 - self.root_cutout)
        return self.root_chord + (self.tip_chord - self.root_chord) * x

    def theta(self, r: np.ndarray | float) -> np.ndarray | float:
        if self.ideal_twist:
            return np.radians(self.theta75_deg * 0.75 / np.asarray(r))
        return np.radians(self.theta75_deg + self.twist_deg * (np.asarray(r) - 0.75))

    @property
    def solidity(self) -> float:
        """Thrust-weighted solidity ≈ chord at 0.75 R."""
        return self.blades * float(self.chord(0.75)) / (math.pi * self.radius)

    @property
    def disk_area(self) -> float:
        return math.pi * self.radius ** 2


@dataclass(frozen=True)
class FlowState:
    """Ambient gas: density [kg/m³], dynamic viscosity [Pa s], speed of sound [m/s]."""

    rho: float
    mu: float
    a: float


def venus_flow(h: float) -> FlowState:
    """Flow state at Venus altitude ``h`` [m] from :mod:`aerokit.planetary` and :mod:`aerokit.venus.gas`."""
    from aerokit import planetary as P
    from aerokit.venus import gas

    s = P.venus_atmosphere(h)
    return FlowState(s.rho, gas.viscosity(s.T), gas.speed_of_sound(s.T))


@dataclass
class BEMTResult:
    CT: float
    CP: float
    thrust: float
    power: float
    torque: float
    FM: float
    omega: float
    tip_speed: float
    tip_mach: float
    re75: float
    r: np.ndarray
    lam: np.ndarray
    alpha_deg: np.ndarray
    cl: np.ndarray
    dCT: np.ndarray
    induced_CP: float
    profile_CP: float
    stalled_fraction: float


def _prandtl_F(blades: int, r: float, phi: float) -> float:
    if phi <= 1e-9:
        return 1.0
    f = 0.5 * blades * (1.0 - r) / (r * phi)
    return (2.0 / math.pi) * math.acos(min(1.0, math.exp(-f)))


@cite("leishman_2006_helicopter", note="BEMT with Prandtl tip loss, hover and axial climb (ch. 3)")
def solve(rotor: Rotor, omega: float, flow: FlowState, climb: float = 0.0, n: int = 60,
          extra_inflow: tuple[float, float] | None = None, tip_loss: bool = True) -> BEMTResult:
    """BEMT at rotor speed ``omega`` [rad/s] and climb speed ``climb`` [m/s].

    ``extra_inflow = (r_c, λ_extra)`` adds an axial inflow inside ``r_c`` (lower rotor of a coaxial pair)."""
    if omega <= 0 or n < 10:
        raise ValueError("omega > 0 and n >= 10")
    R = rotor.radius
    vt = omega * R
    edges = np.linspace(rotor.root_cutout, 1.0, n + 1)
    r = 0.5 * (edges[1:] + edges[:-1])
    dr = np.diff(edges)
    lam_c0 = climb / vt
    lam_c = np.full(n, lam_c0)
    if extra_inflow:
        lam_c = lam_c + np.where(r <= extra_inflow[0], extra_inflow[1], 0.0)
    c = np.asarray(rotor.chord(r), dtype=float)
    sig = rotor.blades * c / (math.pi * R)
    th = np.asarray(rotor.theta(r), dtype=float)
    af = rotor.airfoil

    def be(lmb: np.ndarray):
        phi = np.arctan2(lmb, r)
        u2 = r * r + lmb * lmb
        U = np.sqrt(u2) * vt
        cl, cd = _polar(af, th - phi, flow.rho * U * c / flow.mu, U / flow.a)
        return phi, cl, cd, u2

    def g(lmb: np.ndarray, F: np.ndarray) -> np.ndarray:
        phi, cl, cd, u2 = be(lmb)
        return 4.0 * F * lmb * (lmb - lam_c) * r - 0.5 * sig * (cl * np.cos(phi) - cd * np.sin(phi)) * u2

    base = np.maximum(lam_c, 0.0)
    F = np.ones(n)
    lmb = base + 1e-9
    for _ in range(40):                      # tip-loss fixed point
        lo, hi = base + 1e-9, base + 0.6
        glo, ghi = g(lo, F), g(hi, F)
        ok = glo * ghi <= 0                  # no bracket: windmill / negative-thrust station -> λ = λ_c
        for _b in range(44):                 # vectorised bisection (0.6 / 2^44 ~ 3e-14)
            mid = 0.5 * (lo + hi)
            gm = g(mid, F)
            left = glo * gm <= 0
            hi = np.where(left, mid, hi)
            lo = np.where(left, lo, mid)
            glo = np.where(left, glo, gm)
        new = np.where(ok, 0.5 * (lo + hi), base + 1e-9)
        if tip_loss:
            phi_n = np.maximum(np.arctan2(new, r), 1e-9)
            f = 0.5 * rotor.blades * (1.0 - r) / (r * phi_n)
            F_new = np.maximum((2.0 / math.pi) * np.arccos(np.minimum(1.0, np.exp(-f))), 1e-4)
        else:
            F_new = np.ones(n)
        done = np.max(np.abs(new - lmb)) < 1e-9 and np.max(np.abs(F_new - F)) < 1e-7
        lmb, F = new, F_new
        if done:
            break
    phi, cl, cd, u2 = be(lmb)
    lam = lmb
    alpha = th - phi
    cl_arr = cl
    dCT = 0.5 * sig * (cl * np.cos(phi) - cd * np.sin(phi)) * u2 * dr
    dCP_i = 0.5 * sig * cl * np.sin(phi) * u2 * r * dr
    dCP_0 = 0.5 * sig * cd * np.cos(phi) * u2 * r * dr
    stalled = float(np.sum(dr[np.abs(cl) >= af.cl_max * 0.999]))
    CT, CPi, CP0 = float(dCT.sum()), float(dCP_i.sum()), float(dCP_0.sum())
    CP = CPi + CP0
    A = rotor.disk_area
    T = CT * flow.rho * A * vt ** 2
    Pw = CP * flow.rho * A * vt ** 3
    FM = CT ** 1.5 / (math.sqrt(2.0) * CP) if CT > 0 and CP > 0 and climb == 0.0 else float("nan")
    re75 = flow.rho * 0.75 * vt * float(rotor.chord(0.75)) / flow.mu
    return BEMTResult(CT, CP, T, Pw, Pw / omega, FM, omega, vt, vt / flow.a, re75, r, lam, np.degrees(alpha),
                      cl_arr, dCT, CPi, CP0, stalled / (1.0 - rotor.root_cutout))


def solve_for_thrust(rotor: Rotor, thrust: float, flow: FlowState, climb: float = 0.0,
                     omega_bounds: tuple[float, float] = (5.0, 2000.0), **kw: Any) -> BEMTResult:
    """Fixed-pitch rotor: find the rotor speed that gives ``thrust`` [N]."""
    if thrust <= 0:
        raise ValueError("thrust must be > 0")
    lo, hi = omega_bounds
    f = lambda w: solve(rotor, w, flow, climb, **kw).thrust - thrust  # noqa: E731
    if f(lo) > 0 or f(hi) < 0:
        raise ValueError("thrust not reachable inside the rotor-speed bounds (stall or too small a rotor)")
    w = brentq(f, lo, hi, xtol=1e-6)
    return solve(rotor, w, flow, climb, **kw)


@dataclass
class CoaxialResult:
    upper: BEMTResult
    lower: BEMTResult
    thrust: float
    power: float
    torque_imbalance: float
    FM: float                     # system FM referred to one disk area: C_T^{3/2}/(√2 C_P) with T, P totals
    kappa_int: float              # induced power / (two isolated rotors each with half the thrust, ideal)


@cite("leishman_ananthan_2008_coaxial", "leishman_2006_helicopter",
      note="lower rotor in the fully contracted upper wake (r_c = 1/√2), uniform wake velocity")
def _mean_lambda(res: BEMTResult) -> float:
    dr = np.gradient(res.r)
    return float(np.sum(res.lam * res.r * dr) / np.sum(res.r * dr))


def coaxial(upper: Rotor, lower: Rotor, omega_u: float, omega_l: float, flow: FlowState,
            r_contract: float = 1.0 / math.sqrt(2.0), k_upper: float = 0.0, **kw: Any) -> CoaxialResult:
    """Coaxial pair at given rotor speeds. Both rotors share the same radius reference for the wake mapping.

    ``k_upper`` is the fraction of the lower rotor's mean inflow velocity felt over the whole upper disk (the
    upward influence at close spacing); 0 = upper rotor isolated. It is the single calibrated interference
    parameter (fitted to Harrington rotor 1, checked on rotor 2 — tests)."""
    v_up_extra = 0.0
    for _ in range(12 if k_upper else 1):
        extra_u = (1.0, v_up_extra / (omega_u * upper.radius)) if v_up_extra else None
        up = solve(upper, omega_u, flow, extra_inflow=extra_u, **kw)
        v_wake = _mean_lambda(up) * up.tip_speed / r_contract ** 2
        lo = solve(lower, omega_l, flow, extra_inflow=(r_contract * upper.radius / lower.radius,
                                                       v_wake / (omega_l * lower.radius)), **kw)
        new = k_upper * _mean_lambda(lo) * lo.tip_speed
        if abs(new - v_up_extra) < 1e-6:
            break
        v_up_extra = new
    T = up.thrust + lo.thrust
    Pw = up.power + lo.power
    A = upper.disk_area
    vt = up.tip_speed
    CT = T / (flow.rho * A * vt ** 2)
    CP = Pw / (flow.rho * A * vt ** 3)
    FM = CT ** 1.5 / (math.sqrt(2.0) * CP) if CT > 0 else float("nan")
    p_ind = up.induced_CP * flow.rho * A * vt ** 3 + lo.induced_CP * flow.rho * lower.disk_area * lo.tip_speed ** 3
    p_iso = 2.0 * (T / 2.0) ** 1.5 / math.sqrt(2.0 * flow.rho * A)
    return CoaxialResult(up, lo, T, Pw, up.torque - lo.torque, FM, p_ind / p_iso)


def coaxial_trim(upper: Rotor, lower: Rotor, thrust: float, flow: FlowState,
                 omega_bounds: tuple[float, float] = (5.0, 2000.0), **kw: Any) -> CoaxialResult:
    """Torque-balanced coaxial pair producing ``thrust`` [N]: outer loop on total thrust (upper speed), inner loop
    on the lower rotor speed for zero net torque."""
    lo_b, hi_b = omega_bounds

    def balanced(wu: float) -> CoaxialResult:
        def dq(wl: float) -> float:
            return coaxial(upper, lower, wu, wl, flow, **kw).torque_imbalance

        a, b = 0.3 * wu, 3.0 * wu
        if dq(a) * dq(b) > 0:
            raise ValueError("no torque balance found")
        wl = brentq(dq, a, b, xtol=1e-6)
        return coaxial(upper, lower, wu, wl, flow, **kw)

    wu = brentq(lambda w: balanced(w).thrust - thrust, lo_b, hi_b, xtol=1e-5)
    return balanced(wu)


def with_collective(rotor: Rotor, theta75_deg: float) -> Rotor:
    return replace(rotor, theta75_deg=theta75_deg)


def solve_collective(rotor: Rotor, thrust: float, omega: float, flow: FlowState,
                     bounds_deg: tuple[float, float] = (-2.0, 30.0), **kw: Any) -> tuple[Rotor, BEMTResult]:
    """Collective pitch θ75 [deg] giving ``thrust`` at rotor speed ``omega`` (returns the re-pitched rotor)."""
    f = lambda th: solve(replace(rotor, theta75_deg=th), omega, flow, **kw).thrust - thrust  # noqa: E731
    lo, hi = bounds_deg
    if f(lo) > 0 or f(hi) < 0:
        raise ValueError("thrust not reachable by collective inside the bounds")
    th = brentq(f, lo, hi, xtol=1e-5)
    r = replace(rotor, theta75_deg=th)
    return r, solve(r, omega, flow, **kw)
