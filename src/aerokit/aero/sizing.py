"""Conceptual sizing (Raymer method): takeoff weight, mission fuel fractions, constraint diagram.

Data sources (read 2026-10-25):

- Empty-weight regression and mission-segment fractions: Raymer Table 3.1 / 3.2, VT AOE 4065 A4
  slides (they cite the 5th edition; not compared with the 6th edition).
- Propeller C_bhp: METU AE172 lecture 5. Jet SFC: VT A4 (Raymer Table 3.3).
- CLmax ranges: Scholz, HAW Hamburg, Aircraft Design ch. 5 Table 5.1 (based on Roskam).
- Service-ceiling definition (100 ft/min ~ 0.5 m/s): VT A5 slides.

The constraint equations are derived from first principles (steady climb, L ~ W); each function
docstring states its assumptions.

The aircraft-type keys of :data:`EMPTY_WEIGHT` and :data:`CLMAX_INTERVAL` are kept in Turkish
because the CLI exposes them as ``--kind`` choices and other packages pass them through.
"""
from __future__ import annotations

import math
from collections.abc import Callable

from aerokit.aero.atmosphere import G0, isa
from aerokit.references import cite

LB_N = 4.4482216152605        # 1 lbf [N]
HP_W = 745.69987              # 1 hp [W]

# Raymer Table 3.1: We/W0 = A·W0^C, W0 [lb]. (A, C)
EMPTY_WEIGHT = {
    "sailplane": (0.86, -0.05), "powered sailplane": (0.91, -0.05),
    "homebuilt metal/wood": (1.19, -0.09), "homebuilt composite": (1.15, -0.09),
    "GA single engine": (2.36, -0.18), "GA twin engine": (1.51, -0.10),
    "agricultural": (0.74, -0.03), "twin turboprop": (0.96, -0.05), "flying boat": (1.09, -0.05),
    "jet trainer": (1.59, -0.10), "jet fighter": (2.34, -0.13),
    "military cargo/bomber": (0.93, -0.07), "jet transport": (1.02, -0.06),
    "UAV tactical": (1.67, -0.16), "UAV high altitude": (2.75, -0.18), "UAV small": (0.97, -0.06),
}

# Raymer Table 3.2 historical mission-segment weight fractions
SEGMENT = {"heating_takeoff": 0.970, "climb": 0.985, "landing": 0.995}   # heating_takeoff = warm-up + takeoff

# Fuel consumption: propeller C_bhp [lb/(hp·h)] (cruise, loiter); jet C [1/h] (cruise, loiter)
C_BHP = {"piston": (0.4, 0.5), "turboprop": (0.5, 0.6)}
C_JET = {"turbojet": (0.9, 0.8), "low-bypass turbofan": (0.8, 0.7),
         "high-bypass turbofan": (0.5, 0.4)}

# Scholz Table 5.1 (Roskam I): CLmax ranges (clean, takeoff, landing).
CLMAX_INTERVAL = {"twin engine propeller": ((1.2, 1.8), (1.4, 2.0), (1.6, 2.5)),
                  "jet transport": ((1.2, 1.8), (1.6, 2.2), (1.8, 2.8))}

RESERVE_FACTOR = 1.06              # 5 % reserve + 1 % trapped fuel (Raymer, VT A4)
SERVICE_CEILING_VV = 100 * 0.3048 / 60      # 100 ft/min [m/s]


# --- unit conversions ---
def c_bhp_si(c_bhp: float) -> float:
    """Convert a brake specific fuel consumption from lb/(hp h) to N/J (fuel weight per unit energy).

    Parameters
    ----------
    c_bhp : float
        Specific fuel consumption [lb/(hp h)].

    Returns
    -------
    float
        Specific fuel consumption [N/J].
    """
    return c_bhp * LB_N / (HP_W * 3600)


# --- mission-segment fractions ---
@cite("raymer_2012", note="Breguet range equation, propeller form (Ch. 3), via VT AOE 4065 A4 slides")
def cruise_propeller(R: float, c_bhp: float, eta_p: float, LD: float) -> float:
    """Breguet cruise weight fraction of a propeller aircraft.

    Parameters
    ----------
    R : float
        Range [m].
    c_bhp : float
        Brake specific fuel consumption [lb/(hp h)].
    eta_p : float
        Propeller efficiency [-].
    LD : float
        Lift-to-drag ratio in cruise [-].

    Returns
    -------
    float
        W_end/W_start = exp(-R c / (eta_p L/D)) [-], with c in N/J.
    """
    return math.exp(-R * c_bhp_si(c_bhp) / (eta_p * LD))


@cite("raymer_2012", note="Breguet endurance equation, propeller form (Ch. 3), via VT AOE 4065 A4 slides")
def loiter_propeller(E: float, V: float, c_bhp: float, eta_p: float, LD: float) -> float:
    """Loiter weight fraction of a propeller aircraft.

    Parameters
    ----------
    E : float
        Endurance [s].
    V : float
        Loiter speed [m/s].
    c_bhp : float
        Brake specific fuel consumption [lb/(hp h)].
    eta_p : float
        Propeller efficiency [-].
    LD : float
        Lift-to-drag ratio in loiter [-].

    Returns
    -------
    float
        W_end/W_start = exp(-E V c / (eta_p L/D)) [-].
    """
    return math.exp(-E * V * c_bhp_si(c_bhp) / (eta_p * LD))


@cite("raymer_2012", note="Breguet range equation, jet form (Ch. 3), via VT AOE 4065 A4 slides")
def cruise_jet(R: float, C_hour: float, V: float, LD: float) -> float:
    """Breguet cruise weight fraction of a jet aircraft.

    Parameters
    ----------
    R : float
        Range [m].
    C_hour : float
        Thrust specific fuel consumption [1/h].
    V : float
        Cruise speed [m/s].
    LD : float
        Lift-to-drag ratio in cruise [-].

    Returns
    -------
    float
        W_end/W_start = exp(-R C / (V L/D)) [-], with C in 1/s.
    """
    return math.exp(-R * (C_hour / 3600) / (V * LD))


@cite("raymer_2012", note="Breguet endurance equation, jet form (Ch. 3), via VT AOE 4065 A4 slides")
def loiter_jet(E: float, C_hour: float, LD: float) -> float:
    """Loiter weight fraction of a jet aircraft.

    Parameters
    ----------
    E : float
        Endurance [s].
    C_hour : float
        Thrust specific fuel consumption [1/h].
    LD : float
        Lift-to-drag ratio in loiter [-].

    Returns
    -------
    float
        W_end/W_start = exp(-E C / (L/D)) [-], with C in 1/s.
    """
    return math.exp(-E * (C_hour / 3600) / LD)


@cite("raymer_2012", note="6 % reserve and trapped fuel allowance (Ch. 3), via VT AOE 4065 A4 slides")
def fuel_ratio(mission_fraction: float) -> float:
    """Fuel weight fraction from the overall mission weight fraction.

    Parameters
    ----------
    mission_fraction : float
        Product of all segment weight fractions W_x/W_0 [-].

    Returns
    -------
    float
        W_f/W_0 = 1.06 (1 - W_x/W_0) [-].
    """
    return RESERVE_FACTOR * (1 - mission_fraction)


@cite("raymer_2012", note="Table 3.1 empty-weight fraction regression, via VT AOE 4065 A4 slides")
def empty_weight_ratio(W0: float, kind: str) -> float:
    """Statistical empty-weight fraction We/W0.

    Parameters
    ----------
    W0 : float
        Takeoff gross weight [N].
    kind : str
        Aircraft type, a key of :data:`EMPTY_WEIGHT` (e.g. ``"GA single engine"``).

    Returns
    -------
    float
        We/W0 = A W0^C [-], with W0 converted to lb because the regression is fitted in lb.

    Raises
    ------
    KeyError
        If ``kind`` is not a key of :data:`EMPTY_WEIGHT`.
    """
    A, C = EMPTY_WEIGHT[kind]
    return A * (W0 / LB_N) ** C


@cite("raymer_2012", note="Ch. 3 takeoff-weight sizing iteration")
def takeoff_weight(W_fixed: float, fuel_fraction: float, kind: str, W0_initial: float | None = None,
                   tol: float = 1e-9, maxit: int = 500, we_factor: float = 1.0,
                   we_add: float = 0.0) -> dict[str, float]:
    """Takeoff gross weight by fixed-point iteration.

    Parameters
    ----------
    W_fixed : float
        Crew + payload (+ fixed equipment) weight [N].
    fuel_fraction : float
        Fuel weight fraction W_f/W_0 [-].
    kind : str
        Aircraft type, a key of :data:`EMPTY_WEIGHT`.
    W0_initial : float, optional
        Starting guess [N]; default 3 ``W_fixed``.
    tol : float, optional
        Relative convergence tolerance on W0.
    maxit : int, optional
        Maximum number of iterations.

    Returns
    -------
    dict[str, float]
        ``W0`` takeoff weight [N], ``We_W0`` empty-weight fraction [-], ``Wf_W0`` fuel fraction [-],
        ``We`` empty weight [N], ``Wf`` fuel weight [N].

    Raises
    ------
    ValueError
        If the fuel plus empty-weight fractions reach 1 (no solution: the mission is too heavy for
        this aircraft type) or the iteration does not converge.
    KeyError
        If ``kind`` is not a key of :data:`EMPTY_WEIGHT`.

    Notes
    -----
    W0 = W_fixed / (1 - W_f/W_0 - W_e/W_0(W0)). ``we_factor`` scales the statistical W_e/W_0 (e.g. 1.118
    calibrates the twin-turboprop regression to the King Air 350i, :mod:`aerokit.design.validation`);
    ``we_add`` is added to the scaled fraction afterwards (e.g. an engine-mass correction for a
    power loading that differs from the class, :func:`aerokit.design.sizing.size`).
    """
    if not we_factor > 0:
        raise ValueError("we_factor must be > 0")
    W0 = W0_initial or 3 * W_fixed
    for _ in range(maxit):
        we = we_factor * empty_weight_ratio(W0, kind) + we_add
        denominator = 1 - fuel_fraction - we
        if denominator <= 0:
            raise ValueError("no solution: fuel + empty-weight fraction >= 1 (mission too heavy for this type)")
        W0_new = W_fixed / denominator
        if abs(W0_new - W0) < tol * W0:
            return {"W0": W0_new, "We_W0": we, "Wf_W0": fuel_fraction,
                    "We": we * W0_new, "Wf": fuel_fraction * W0_new}
        W0 = W0_new
    raise ValueError("takeoff-weight iteration did not converge")


# --- aerodynamic estimates ---
@cite("raymer_2018", note="straight-wing Oswald efficiency; read via an ADRpy notebook, "
                          "edition and equation number not checked")
def oswald_raymer(AR: float) -> float:
    """Oswald span efficiency of a straight (unswept) wing.

    Parameters
    ----------
    AR : float
        Aspect ratio [-].

    Returns
    -------
    float
        e = 1.78 (1 - 0.045 AR^0.68) - 0.64 [-].
    """
    return 1.78 * (1 - 0.045 * AR ** 0.68) - 0.64


def cd0_ldmax(LD_max: float, AR: float, e: float) -> tuple[float, float]:
    """Zero-lift drag coefficient implied by a maximum lift-to-drag ratio (parabolic polar).

    Parameters
    ----------
    LD_max : float
        Maximum lift-to-drag ratio [-].
    AR : float
        Aspect ratio [-].
    e : float
        Oswald efficiency [-].

    Returns
    -------
    CD0 : float
        Zero-lift drag coefficient [-].
    K : float
        Induced-drag factor 1/(pi AR e) [-].

    Notes
    -----
    (L/D)max = 1 / (2 sqrt(CD0 K))  =>  CD0 = 1 / (4 K (L/D)max^2).
    """
    K = 1 / (math.pi * AR * e)
    return 1 / (4 * K * LD_max ** 2), K


# --- constraint diagram (propeller aircraft) ---
def ws_stall(V_stall: float, CLmax: float, h: float = 0.0) -> float:
    """Wing loading that gives a required stall speed.

    Parameters
    ----------
    V_stall : float
        Stall speed [m/s].
    CLmax : float
        Maximum lift coefficient in the relevant configuration [-].
    h : float, optional
        ISA altitude [m].

    Returns
    -------
    float
        W/S = rho V_s^2 CLmax / 2 [N/m^2].
    """
    return 0.5 * isa(h)["rho"] * V_stall ** 2 * CLmax


def pw_required(WS: float, V: float, Vv: float, h: float, CD0: float, K: float, eta_p: float,
                power_drop: Callable[[float], float] | None = None) -> float:
    """Sea-level power loading required for steady climb or level flight.

    Parameters
    ----------
    WS : float
        Wing loading [N/m^2].
    V : float
        True airspeed [m/s].
    Vv : float
        Rate of climb [m/s] (0 for level flight).
    h : float
        ISA altitude [m].
    CD0, K : float
        Parabolic drag polar coefficients [-].
    eta_p : float
        Propeller efficiency [-].
    power_drop : callable, optional
        ``power_drop(h)`` = P(h)/P_SL. Default sigma = rho/rho0 (ASSUMPTION, used when no engine
        data are available).

    Returns
    -------
    float
        P_SL/W [W/N].

    Notes
    -----
    T/W = Vv/V + q CD0/(W/S) + K (W/S)/q (L ~ W, small climb angle), P/W = (T/W) V / eta_p.
    """
    rho = isa(h)["rho"]
    q = 0.5 * rho * V ** 2
    tw = Vv / V + q * CD0 / WS + K * WS / q
    ratio = power_drop(h) if power_drop else rho / isa(0)["rho"]
    return tw * V / eta_p / ratio


def pw_en_good_climb(WS: float, Vv: float, h: float, CD0: float, K: float, eta_p: float, CLmax_clean: float,
                     V_upper: float, power_drop: Callable[[float], float] | None = None,
                     n: int = 400) -> tuple[float, float | None]:
    """Power loading at the best (minimum-power) climb speed, found by a speed sweep.

    The name means "best climb" (from the Turkish *en iyi*); it is kept because the CLI and the
    optimization package call it.

    Parameters
    ----------
    WS : float
        Wing loading [N/m^2].
    Vv : float
        Required rate of climb [m/s].
    h : float
        ISA altitude [m].
    CD0, K : float
        Parabolic drag polar coefficients [-].
    eta_p : float
        Propeller efficiency [-].
    CLmax_clean : float
        Clean maximum lift coefficient; the sweep starts at 1.1 V_stall [-].
    V_upper : float
        Upper end of the speed sweep [m/s].
    power_drop : callable, optional
        Altitude power lapse, see :func:`pw_required`.
    n : int, optional
        Number of sweep intervals.

    Returns
    -------
    PW : float
        Minimum P_SL/W over the sweep [W/N].
    V : float or None
        Speed at which it occurs [m/s] (None only if every evaluation is infinite).
    """
    rho = isa(h)["rho"]
    V_lower = 1.1 * math.sqrt(2 * WS / (rho * CLmax_clean))
    best: tuple[float, float | None] = (math.inf, None)
    for i in range(n + 1):
        V = V_lower + (V_upper - V_lower) * i / n
        pw = pw_required(WS, V, Vv, h, CD0, K, eta_p, power_drop)
        if pw < best[0]:
            best = (pw, V)
    return best


def pw_takeoff(WS: float, s_g: float, CLmax_TO: float, eta_TO: float, mu: float = 0.03, h: float = 0.0) -> float:
    """Power loading required for a given takeoff ground roll.

    Parameters
    ----------
    WS : float
        Wing loading [N/m^2].
    s_g : float
        Ground-roll distance [m].
    CLmax_TO : float
        Takeoff maximum lift coefficient [-].
    eta_TO : float
        Propeller efficiency during takeoff [-] (ASSUMPTION, user-supplied).
    mu : float, optional
        Rolling friction coefficient [-] (ASSUMPTION).
    h : float, optional
        ISA altitude of the runway [m].

    Returns
    -------
    float
        P/W [W/N].

    Notes
    -----
    Lift-off speed V_LO = 1.1 V_s(TO), constant acceleration, drag neglected (optimistic):
    s_g = 1.21 (W/S) / (g rho CLmax_TO (T/W - mu))  =>  T/W.
    Thrust is evaluated at 0.7 V_LO with T = eta_TO P / V.
    """
    rho = isa(h)["rho"]
    tw = 1.21 * WS / (G0 * rho * CLmax_TO * s_g) + mu
    V_LO = 1.1 * math.sqrt(2 * WS / (rho * CLmax_TO))
    return tw * 0.7 * V_LO / eta_TO
