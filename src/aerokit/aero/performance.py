"""Point performance of a conceptual aircraft (steady, quasi-steady flight; SI; weights in N).

Core relations for the parabolic polar ``C_D = C_D0 + K C_L²`` (Anderson 2017, Eq. 6.24):

* minimum-drag (max L/D) speed:  C_L = √(C_D0/K)
* minimum-power speed:           C_L = √(3 C_D0/K)
* rate of climb (energy method):  ROC = (P_A − P_R)/W  (small climb angle)

Speeds are true airspeeds at altitude ``h``. Functions that use the engine take an
:class:`aerokit.aero.aircraft.Aircraft`.

Extended relations (P0-2 of ``docs/06_development_plan.md``):

* ceilings: absolute (max ROC = 0) and service (max ROC = 0.508 m/s = 100 ft/min), solved by root
  finding over 0–20 000 m (the ISA model range); time to climb ∫ dh / ROC_max(h) at constant weight;
* maximum level speed (largest V with P_A = P_R) and the flight envelope V_stall(h), V_max(h);
* take-off and landing distances (ground roll with forces evaluated at 0.7 of the end speed, transition
  arc and air distance to a 50 ft obstacle);
* range and endurance by numerical integration of dW/dt = −ẇ_f, with closed-form Breguet helpers for
  verification; the three-corner payload–range diagram; a requirement compliance table.

Sources: the parabolic polar is Anderson (2017) Eq. 6.24 (read from the user's PDF). Anderson's
*Fundamentals of Aerodynamics* has no performance chapters; the performance models follow the standard
treatment of Raymer (2018) Ch. 17, **which has not been read in this session** — every model is
therefore also derived in the docstring Notes, and numerical constants that are conventions
(1.1 V_stall lift-off, 0.7 V_LOF averaging, 1.3 V_stall approach, braking μ 0.4, ...) are parameters
labelled as assumptions.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Literal, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq, minimize_scalar

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.atmosphere import isa
from aerokit.references import cite

__all__ = ["speed_for_CL", "speed_max_LD", "speed_min_power", "rate_of_climb", "max_rate_of_climb",
           "best_climb_speed", "best_endurance_speed", "best_range_speed",
           "SERVICE_CEILING_ROC", "OBSTACLE_HEIGHT", "absolute_ceiling", "service_ceiling", "climb_time",
           "time_to_climb", "max_speed", "flight_envelope", "takeoff_distance", "landing_distance",
           "range_and_endurance", "breguet_range_propeller", "breguet_endurance_propeller",
           "breguet_range_jet", "breguet_endurance_jet", "payload_range", "ComplianceRow", "compliance",
           "REQUIREMENT_KEYS"]


def speed_for_CL(ac: Aircraft, CL: float, h: float, W: float | None = None) -> float:
    """True airspeed giving lift coefficient ``CL`` in 1-g flight [m/s]."""
    if not CL > 0:
        raise ValueError("CL must be > 0")
    return math.sqrt(2.0 * (ac.W0 if W is None else W) / (isa(h)["rho"] * ac.S * CL))


@cite("anderson_2017", note="parabolic polar, Eq. 6.24; optimum C_L = √(C_D0/K) follows by differentiation")
def speed_max_LD(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Minimum-drag speed, C_L = √(C_D0/K) [m/s] (best range of a propeller aircraft)."""
    return speed_for_CL(ac, math.sqrt(ac.CD0 / ac.K), h, W)


@cite("anderson_2017", note="parabolic polar, Eq. 6.24; minimum P = DV at C_L = √(3 C_D0/K)")
def speed_min_power(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Minimum-power speed, C_L = √(3 C_D0/K) [m/s] (best endurance of a propeller aircraft)."""
    return speed_for_CL(ac, math.sqrt(3.0 * ac.CD0 / ac.K), h, W)


def rate_of_climb(ac: Aircraft, V: float, h: float, W: float | None = None) -> float:
    """Steady rate of climb (P_A − P_R)/W at speed ``V`` [m/s] (negative: cannot hold altitude)."""
    w = ac.W0 if W is None else W
    return (ac.power_available(V, h) - ac.power_required(V, h, w)) / w


def best_climb_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Speed of maximum rate of climb at ``h`` (bounded search above 1.1 V_stall) [m/s]."""
    w = ac.W0 if W is None else W
    vs = ac.stall_speed(h, w)
    hi = max(4.0 * vs, 2.0 * speed_max_LD(ac, h, w))
    res = minimize_scalar(lambda v: -rate_of_climb(ac, v, h, w), bounds=(1.1 * vs, hi), method="bounded",
                          options={"xatol": 1e-4})
    return float(res.x)


def max_rate_of_climb(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Maximum steady rate of climb at ``h`` [m/s]."""
    return rate_of_climb(ac, best_climb_speed(ac, h, W), h, W)


def best_endurance_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Speed of minimum fuel flow [m/s] (propeller: minimum power; jet: minimum drag), ≥ 1.2 V_stall."""
    w = ac.W0 if W is None else W
    from aerokit.aero.propulsion import Turbofan
    v = speed_max_LD(ac, h, w) if isinstance(ac.engine, Turbofan) else speed_min_power(ac, h, w)
    return max(v, 1.2 * ac.stall_speed(h, w))


def best_range_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Speed of maximum distance per fuel [m/s] (propeller: max L/D; jet: C_L = √(C_D0/(3K))), ≥ 1.2 V_stall."""
    w = ac.W0 if W is None else W
    from aerokit.aero.propulsion import Turbofan
    v = (speed_for_CL(ac, math.sqrt(ac.CD0 / (3.0 * ac.K)), h, w) if isinstance(ac.engine, Turbofan)
         else speed_max_LD(ac, h, w))
    return max(v, 1.2 * ac.stall_speed(h, w))


# ====================================================================== extended performance (P0-2)
SERVICE_CEILING_ROC = 0.508     # m/s = 100 ft/min, the conventional service-ceiling climb rate
OBSTACLE_HEIGHT = 15.24         # m = 50 ft screen height for take-off and landing distances
_H_MAX = 20000.0                # upper limit of the ISA model used here [m]
_RAYMER_NOTE = "Ch. 17 (aircraft performance) — not read in this session; model derived in the Notes"


def _weight(ac: Aircraft, W: float | None) -> float:
    w = ac.W0 if W is None else float(W)
    if not (math.isfinite(w) and w > 0):
        raise ValueError(f"weight must be a positive finite number [N], got {W!r}")
    return w


def _ceiling(ac: Aircraft, W: float | None, roc: float) -> float:
    """Altitude where max ROC = ``roc``; ``inf`` if ROC_max(20 km) still exceeds it."""
    if not (math.isfinite(roc) and roc >= 0):
        raise ValueError("target rate of climb must be finite and >= 0")
    w = _weight(ac, W)

    def f(h: float) -> float:
        return max_rate_of_climb(ac, h, w) - roc

    f0 = f(0.0)
    if not f0 > 0:
        raise ValueError(f"maximum rate of climb at sea level ({f0 + roc:.4g} m/s) does not exceed "
                         f"{roc:g} m/s: no ceiling bracketed in [0, {_H_MAX:g}] m")
    if f(_H_MAX) > 0:
        return math.inf
    return float(brentq(f, 0.0, _H_MAX, xtol=1e-6, rtol=1e-12, maxiter=200))


def _finite_ceiling(ac: Aircraft, W: float | None, roc: float, what: str) -> float:
    h = _ceiling(ac, W, roc)
    if not math.isfinite(h):
        raise ValueError(f"{what} lies above {_H_MAX:g} m (ISA model limit): not bracketed in [0, {_H_MAX:g}] m")
    return h


@cite("raymer_2018", note=_RAYMER_NOTE)
def absolute_ceiling(ac: Aircraft, W: float | None = None) -> float:
    """Absolute ceiling: altitude where the maximum steady rate of climb is zero [m].

    Parameters
    ----------
    ac : Aircraft
    W : float, optional
        Weight [N] (default ``ac.W0``, the conservative choice).

    Returns
    -------
    float
        Altitude [m] in (0, 20 000).

    Raises
    ------
    ValueError
        If the root is not bracketed in [0, 20 000] m (no climb at sea level, or a ceiling above the
        ISA model range).

    Notes
    -----
    Solves ``max_rate_of_climb(ac, h, W) = 0`` with Brent's method (``xtol`` 1 µm); ROC_max(h) is
    evaluated by :func:`max_rate_of_climb` (energy method, small climb angle). Derivation: definition.
    """
    return _finite_ceiling(ac, W, 0.0, "absolute ceiling")


@cite("raymer_2018", note=_RAYMER_NOTE)
def service_ceiling(ac: Aircraft, W: float | None = None, roc: float = SERVICE_CEILING_ROC) -> float:
    """Service ceiling: altitude where the maximum rate of climb equals ``roc`` (100 ft/min) [m].

    Parameters
    ----------
    ac : Aircraft
    W : float, optional
        Weight [N] (default ``ac.W0``).
    roc : float
        Rate of climb defining the ceiling [m/s]; 0.508 m/s = 100 ft/min (convention).

    Returns
    -------
    float
        Altitude [m].

    Raises
    ------
    ValueError
        If the root is not bracketed in [0, 20 000] m.
    """
    return _finite_ceiling(ac, W, roc, "service ceiling")


def climb_time(roc: Callable[[float], float], h1: float, h2: float, ceiling: float | None = None,
               n: int = 50) -> float:
    """Time to climb ∫_{h1}^{h2} dh / ROC(h) for a given rate-of-climb profile [s].

    Parameters
    ----------
    roc : callable
        Rate of climb [m/s] as a function of altitude [m]; must be > 0 on [h1, h2].
    h1, h2 : float
        Start and end altitude [m], ``h2 > h1``.
    ceiling : float, optional
        Altitude where ROC → 0 (absolute ceiling). When given, the integral is taken in the variable
        z = ln(ceiling − h), which removes the 1/(ceiling − h) growth of the integrand near the ceiling.
    n : int
        Number of Gauss–Legendre points.

    Returns
    -------
    float
        Time [s].

    Raises
    ------
    ValueError
        If ``h2 <= h1``, ``h2 >= ceiling``, ``n < 2`` or ROC ≤ 0 at a quadrature point.

    Notes
    -----
    Derivation: with dh = −(H − h) dz, t = ∫_{z(h2)}^{z(h1)} (H − h)/ROC(h) dz. For a linear profile
    ROC = ROC_0 (1 − h/H) the transformed integrand is the constant H/ROC_0, so the rule is exact and
    t = (H/ROC_0) ln((H − h1)/(H − h2)).
    """
    if not (math.isfinite(h1) and math.isfinite(h2) and h2 > h1):
        raise ValueError("need finite altitudes with h2 > h1")
    if n < 2:
        raise ValueError("n must be >= 2")
    x, wq = np.polynomial.legendre.leggauss(int(n))
    if ceiling is None:
        mid, half = 0.5 * (h1 + h2), 0.5 * (h2 - h1)
        hs = mid + half * x
        scale = np.ones_like(hs)
    else:
        if not h2 < ceiling:
            raise ValueError(f"h2 = {h2:g} m must be below the ceiling {ceiling:g} m (1/ROC is singular there)")
        z_lo, z_hi = math.log(ceiling - h2), math.log(ceiling - h1)
        mid, half = 0.5 * (z_lo + z_hi), 0.5 * (z_hi - z_lo)
        scale = np.exp(mid + half * x)
        hs = ceiling - scale
    r = np.array([float(roc(float(h))) for h in hs])
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        raise ValueError("rate of climb must be > 0 over the climb interval")
    return float(half * np.sum(wq * scale / r))


@cite("raymer_2018", note=_RAYMER_NOTE)
def time_to_climb(ac: Aircraft, h1: float, h2: float, W: float | None = None, n: int = 50) -> float:
    """Minimum time to climb from ``h1`` to ``h2`` at the best-climb speed, constant weight [s].

    Parameters
    ----------
    ac : Aircraft
    h1, h2 : float
        Start and end altitude [m], 0 ≤ h1 < h2.
    W : float, optional
        Weight [N], held constant (fuel burned in the climb is neglected; default ``ac.W0``).
    n : int
        Gauss–Legendre points of :func:`climb_time`.

    Returns
    -------
    float
        Time [s].

    Raises
    ------
    ValueError
        If ``h2`` is at or above the absolute ceiling (the integrand 1/ROC is singular there).

    Notes
    -----
    t = ∫ dh / ROC_max(h) (quasi-steady climb, the kinetic-energy change with speed is neglected).
    Integrated in z = ln(H_abs − h) (see :func:`climb_time`).
    """
    w = _weight(ac, W)
    if not h1 >= 0:
        raise ValueError("h1 must be >= 0")
    H = _ceiling(ac, w, 0.0)
    if not h2 < H:
        raise ValueError(f"h2 = {h2:g} m is at or above the absolute ceiling {H:.6g} m: time to climb is infinite")
    return climb_time(lambda h: max_rate_of_climb(ac, h, w), h1, h2, ceiling=None if math.isinf(H) else H, n=n)


@cite("anderson_2017", note="parabolic polar Eq. 6.24 for P_R = D V; P_A = P_R solved numerically (derivation)")
def max_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Maximum level-flight true airspeed: the largest V with P_A(V) = P_R(V) [m/s].

    Parameters
    ----------
    ac : Aircraft
    h : float
        Altitude [m].
    W : float, optional
        Weight [N] (default ``ac.W0``).

    Returns
    -------
    float
        Speed [m/s].

    Raises
    ------
    ValueError
        If level flight is impossible at ``h`` (P_A ≤ P_R at the minimum-power / minimum-drag speed).

    Notes
    -----
    Root bracketed above the minimum-power speed (propeller; P_A independent of V) or the minimum-drag
    speed (jet; P_A = T V), where P_R − P_A is increasing, so the root is the unique high-speed one.
    No compressibility drag rise and no Mach / structural speed limit are included.
    """
    from aerokit.aero.propulsion import Turbofan
    w = _weight(ac, W)
    v_lo = speed_max_LD(ac, h, w) if isinstance(ac.engine, Turbofan) else speed_min_power(ac, h, w)

    def excess(v: float) -> float:
        return ac.power_available(v, h) - ac.power_required(v, h, w)

    if not excess(v_lo) > 0:
        raise ValueError(f"level flight impossible at h = {h:g} m (P_A <= P_R at the best speed)")
    v_hi = 2.0 * v_lo
    for _ in range(60):
        if excess(v_hi) < 0:
            break
        v_lo, v_hi = v_hi, 2.0 * v_hi
    else:                                            # pragma: no cover - P_R grows as V³
        raise ValueError("maximum speed not bracketed")
    return float(brentq(excess, v_lo, v_hi, xtol=1e-9, rtol=1e-13, maxiter=200))


def flight_envelope(ac: Aircraft, heights: NDArray[np.float64] | list[float] | tuple[float, ...],
                    W: float | None = None) -> dict[str, NDArray[np.float64]]:
    """Level-flight envelope: stall and maximum speed against altitude.

    Parameters
    ----------
    ac : Aircraft
    heights : array_like
        Altitudes [m] in 0–20 000.
    W : float, optional
        Weight [N] (default ``ac.W0``).

    Returns
    -------
    dict
        ``h`` [m], ``V_stall`` (clean CLmax) [m/s], ``V_max`` [m/s] — NaN where level flight is
        impossible or V_max < V_stall (above the envelope).
    """
    w = _weight(ac, W)
    hs = np.asarray(heights, dtype=float).ravel()
    vs = np.array([ac.stall_speed(float(h), w) for h in hs])
    vm = np.full_like(hs, np.nan)
    for i, h in enumerate(hs):
        try:
            v = max_speed(ac, float(h), w)
        except ValueError:
            continue
        if v >= vs[i]:
            vm[i] = v
    return {"h": hs, "V_stall": vs, "V_max": vm}


@cite("raymer_2018", note=_RAYMER_NOTE)
def takeoff_distance(ac: Aircraft, h: float = 0.0, W: float | None = None, CLmax: float | None = None,
                     mu: float | None = None, obstacle: float = OBSTACLE_HEIGHT, *,
                     CL_ground: float | None = None, t_rotation: float = 0.0, ground_effect: float = 1.0,
                     liftoff_factor: float = 1.1, transition_factor: float = 1.15,
                     n_transition: float = 1.2) -> dict[str, float]:
    """Take-off distance: ground roll, rotation and air distance to the obstacle [m].

    Parameters
    ----------
    ac : Aircraft
    h : float
        Runway altitude [m].
    W : float, optional
        Take-off weight [N] (default ``ac.W0``).
    CLmax : float, optional
        Take-off CLmax (default ``ac.CLmax_takeoff``).
    mu : float, optional
        Rolling friction coefficient (default ``ac.mu_roll``).
    obstacle : float
        Screen height [m] (default 50 ft); 0 gives the ground roll only.
    CL_ground : float, optional
        Lift coefficient in the ground-roll attitude. Default: μ/(2 φ K), the attitude of minimum
        resistance D + μ(W − L) (derivation: d/dC_L[C_D0 + φK C_L² − μ C_L] = 0) — an **assumption**.
    t_rotation : float
        Rotation time at V_LOF [s] (default 0, **assumption**); adds V_LOF·t_rotation.
    ground_effect : float
        Factor φ on the induced drag K during the ground roll (default 1: no ground effect).
    liftoff_factor, transition_factor : float
        V_LOF = 1.1 V_stall,TO and transition speed 1.15 V_stall,TO (conventions, **assumptions**).
    n_transition : float
        Load factor of the transition arc (default 1.2, **assumption**).

    Returns
    -------
    dict
        ``V_stall``, ``V_LOF`` [m/s]; ``a_mean`` [m/s²]; ``ground_roll``, ``rotation``,
        ``transition``, ``climb``, ``air_distance``, ``total`` [m]; ``climb_angle`` [rad].

    Raises
    ------
    ValueError
        If the net accelerating force on the runway or the climb gradient at the transition speed is
        not positive.

    Notes
    -----
    Model (all derived here; Raymer Ch. 17 not read in this session):

    * Ground roll: m dV/dt = T − D − μ(W − L). The forces are evaluated once at V = 0.7 V_LOF (≈ the
      rms speed V_LOF/√2, which makes the result exact for forces linear in V²), giving a constant
      a_mean = g [T − D − μ(W − L)]/W and s_G = V_LOF²/(2 a_mean). Thrust at full take-off power,
      ``engine.thrust(0.7 V_LOF, h, takeoff=True)`` (propeller: η_TO P/V).
    * Rotation: s_R = V_LOF · t_rotation.
    * Transition: circular arc at V_TR = 1.15 V_stall with load factor n: R = V_TR²/(g(n − 1));
      climb angle sin γ = (T − D)/W at V_TR; h_TR = R(1 − cos γ). If h_TR ≥ obstacle the obstacle is
      cleared in the arc, s_T = √(R² − (R − h_obs)²); otherwise s_T = R sin γ and the straight climb
      s_C = (h_obs − h_TR)/tan γ.
    """
    w = _weight(ac, W)
    clmax = ac.CLmax_takeoff if CLmax is None else float(CLmax)
    mu_r = ac.mu_roll if mu is None else float(mu)
    if not (clmax > 0 and mu_r >= 0 and obstacle >= 0 and t_rotation >= 0 and ground_effect > 0):
        raise ValueError("need CLmax > 0, mu >= 0, obstacle >= 0, t_rotation >= 0, ground_effect > 0")
    if not (liftoff_factor >= 1 and transition_factor >= 1 and n_transition > 1):
        raise ValueError("need liftoff/transition factors >= 1 and n_transition > 1")
    rho = isa(h)["rho"]
    vs = ac.stall_speed(h, w, clmax)
    v_lof = liftoff_factor * vs
    k_g = ground_effect * ac.K
    cl_g = min(mu_r / (2.0 * k_g) if CL_ground is None else float(CL_ground), clmax)
    v7 = 0.7 * v_lof
    q = 0.5 * rho * v7 * v7
    thrust = ac.engine.thrust(v7, h, True)
    drag = q * ac.S * (ac.CD0 + k_g * cl_g * cl_g)
    lift = q * ac.S * cl_g
    force = thrust - drag - mu_r * (w - lift)
    if not force > 0:
        raise ValueError(f"no net accelerating force on the runway (T - D - mu(W - L) = {force:.4g} N)")
    a_mean = G0 * force / w
    s_g = v_lof * v_lof / (2.0 * a_mean)
    s_r = v_lof * t_rotation
    s_t = s_c = gamma = 0.0
    if obstacle > 0:
        v_tr = transition_factor * vs
        radius = v_tr * v_tr / (G0 * (n_transition - 1.0))
        sin_g = (ac.engine.thrust(v_tr, h, True) - ac.drag(v_tr, h, w)) / w
        if not sin_g > 0:
            raise ValueError("no climb gradient at the transition speed (T <= D)")
        gamma = math.asin(min(sin_g, 1.0))
        h_tr = radius * (1.0 - math.cos(gamma))
        if h_tr >= obstacle:
            s_t = math.sqrt(radius * radius - (radius - obstacle) ** 2)
        else:
            s_t = radius * math.sin(gamma)
            s_c = (obstacle - h_tr) / math.tan(gamma)
    return {"V_stall": vs, "V_LOF": v_lof, "a_mean": a_mean, "ground_roll": s_g, "rotation": s_r,
            "transition": s_t, "climb": s_c, "air_distance": s_t + s_c, "climb_angle": gamma,
            "total": s_g + s_r + s_t + s_c}


@cite("raymer_2018", note=_RAYMER_NOTE)
def landing_distance(ac: Aircraft, h: float = 0.0, W: float | None = None, CLmax: float | None = None,
                     mu: float = 0.4, obstacle: float = OBSTACLE_HEIGHT, *, approach_factor: float = 1.3,
                     flare_factor: float = 1.23, touchdown_factor: float = 1.15, approach_angle: float = 3.0,
                     n_flare: float = 1.2, t_free_roll: float = 1.0, CL_ground: float = 0.0,
                     reverse_thrust: float = 0.0) -> dict[str, float]:
    """Landing distance from the obstacle: approach, flare, free roll and braking [m].

    Parameters
    ----------
    ac : Aircraft
    h : float
        Runway altitude [m].
    W : float, optional
        Landing weight [N] (default ``ac.W0`` — conservative: landing at take-off weight).
    CLmax : float, optional
        Landing CLmax (default ``ac.CLmax_landing``).
    mu : float
        Braking friction coefficient — **assumption** 0.4 (dry hard runway, typical value; not from a
        source read here).
    obstacle : float
        Screen height [m] (default 50 ft); 0 gives the ground roll only.
    approach_factor, flare_factor, touchdown_factor : float
        Approach 1.3, flare 1.23 and touchdown 1.15 × V_stall,L (conventions, **assumptions**).
    approach_angle : float
        Glide-path angle [deg] (default 3°, **assumption**).
    n_flare : float
        Load factor of the flare arc (default 1.2, **assumption**).
    t_free_roll : float
        Time between touchdown and braking at V_TD [s] (default 1 s, **assumption**).
    CL_ground : float
        Lift coefficient during braking (default 0: lift dumped — optimistic, **assumption**).
    reverse_thrust : float
        Reverse thrust as a fraction of the full take-off thrust at 0.7 V_TD (default 0: thrust
        reverse off; idle forward thrust neglected).

    Returns
    -------
    dict
        ``V_stall``, ``V_approach``, ``V_flare``, ``V_TD`` [m/s]; ``a_mean`` (deceleration) [m/s²];
        ``approach``, ``flare``, ``air_distance``, ``free_roll``, ``braking``, ``ground_roll``,
        ``total`` [m].

    Raises
    ------
    ValueError
        Invalid parameters.

    Notes
    -----
    Model (derived here; Raymer Ch. 17 not read in this session): straight approach at γ_a to the flare
    height h_F = R(1 − cos γ_a) with R = V_F²/(g(n − 1)), s_A = (h_obs − h_F)/tan γ_a, flare
    s_F = R sin γ_a (if h_F > h_obs the arc starts below the screen: s_A = 0,
    s_F = √(R² − (R − h_obs)²)); free roll s_FR = V_TD t_FR; braking with a constant deceleration
    evaluated at 0.7 V_TD, a = g [T_rev + D + μ(W − L)]/W, s_B = V_TD²/(2a).
    """
    w = _weight(ac, W)
    clmax = ac.CLmax_landing if CLmax is None else float(CLmax)
    if not (clmax > 0 and mu > 0 and obstacle >= 0 and 0 < approach_angle < 90 and n_flare > 1
            and t_free_roll >= 0 and CL_ground >= 0 and 0 <= reverse_thrust <= 1):
        raise ValueError("invalid landing parameters")
    if not approach_factor >= flare_factor >= touchdown_factor >= 1:
        raise ValueError("need approach_factor >= flare_factor >= touchdown_factor >= 1")
    rho = isa(h)["rho"]
    vs = ac.stall_speed(h, w, clmax)
    v_a, v_f, v_td = approach_factor * vs, flare_factor * vs, touchdown_factor * vs
    s_a = s_f = 0.0
    if obstacle > 0:
        gam = math.radians(approach_angle)
        radius = v_f * v_f / (G0 * (n_flare - 1.0))
        h_f = radius * (1.0 - math.cos(gam))
        if h_f > obstacle:
            s_f = math.sqrt(radius * radius - (radius - obstacle) ** 2)
        else:
            s_f = radius * math.sin(gam)
            s_a = (obstacle - h_f) / math.tan(gam)
    v7 = 0.7 * v_td
    q = 0.5 * rho * v7 * v7
    cl = min(CL_ground, clmax)
    drag = q * ac.S * (ac.CD0 + ac.K * cl * cl)
    lift = q * ac.S * cl
    t_rev = reverse_thrust * ac.engine.thrust(v7, h, True) if reverse_thrust > 0 else 0.0
    decel = G0 * (t_rev + drag + mu * max(w - lift, 0.0)) / w
    s_fr = v_td * t_free_roll
    s_b = v_td * v_td / (2.0 * decel)
    return {"V_stall": vs, "V_approach": v_a, "V_flare": v_f, "V_TD": v_td, "a_mean": decel,
            "approach": s_a, "flare": s_f, "air_distance": s_a + s_f, "free_roll": s_fr, "braking": s_b,
            "ground_roll": s_fr + s_b, "total": s_a + s_f + s_fr + s_b}


# ---------------------------------------------------------------------- range and endurance
def _check_weights(W0: float, W1: float) -> None:
    if not (math.isfinite(W0) and math.isfinite(W1) and W0 > W1 > 0):
        raise ValueError(f"need W_start > W_end > 0 [N], got {W0!r}, {W1!r}")


@cite("raymer_2018", note="Breguet range, " + _RAYMER_NOTE)
def breguet_range_propeller(eta: float, psfc: float, LD: float, W0: float, W1: float) -> float:
    """Breguet range of a propeller aircraft at constant L/D, η and c: R = (η/c)(L/D) ln(W0/W1) [m].

    ``psfc`` is weight-specific [N/(W·s)] = [1/m]. Derivation: dW/dt = −c P_R/η with P_R = W V/(L/D),
    so dR = V dt = −(η/c)(L/D) dW/W.
    """
    _check_weights(W0, W1)
    return eta / psfc * LD * math.log(W0 / W1)


@cite("raymer_2018", note="Breguet endurance, " + _RAYMER_NOTE)
def breguet_endurance_propeller(eta: float, psfc: float, CL: float, CD: float, rho: float, S: float,
                                W0: float, W1: float) -> float:
    """Endurance of a propeller aircraft at constant C_L and altitude [s].

    E = (η/c) (C_L^1.5/C_D) √(2ρS) (W1^−½ − W0^−½). Derivation: dt = −η dW/(c P_R) with
    P_R = W^1.5 √(2/(ρS)) C_D/C_L^1.5.
    """
    _check_weights(W0, W1)
    return eta / psfc * math.pow(CL, 1.5) / CD * math.sqrt(2.0 * rho * S) * (1.0 / math.sqrt(W1) - 1.0 / math.sqrt(W0))


@cite("raymer_2018", note="Breguet range, " + _RAYMER_NOTE)
def breguet_range_jet(tsfc: float, CL: float, CD: float, rho: float, S: float, W0: float, W1: float) -> float:
    """Range of a jet at constant C_L and altitude [m]: R = (2/c_t) √(2/(ρS)) (√C_L/C_D)(√W0 − √W1).

    ``tsfc`` weight-specific [1/s]. Derivation: dW/dt = −c_t D, D = W C_D/C_L, V = √(2W/(ρ S C_L)).
    """
    _check_weights(W0, W1)
    return 2.0 / tsfc * math.sqrt(2.0 / (rho * S)) * math.sqrt(CL) / CD * (math.sqrt(W0) - math.sqrt(W1))


@cite("raymer_2018", note="Breguet endurance, " + _RAYMER_NOTE)
def breguet_endurance_jet(tsfc: float, LD: float, W0: float, W1: float) -> float:
    """Endurance of a jet at constant L/D [s]: E = (1/c_t)(L/D) ln(W0/W1) (dt = −dW/(c_t W/(L/D)))."""
    _check_weights(W0, W1)
    return LD / tsfc * math.log(W0 / W1)


@cite("raymer_2018", note="Breguet consistency; " + _RAYMER_NOTE)
def range_and_endurance(ac: Aircraft, h: float, W_start: float, W_end: float, V: float | None = None, *,
                        speed: Literal["range", "endurance"] = "range", n: int = 64) -> dict[str, float]:
    """Range and time of steady level flight burning fuel from ``W_start`` down to ``W_end``.

    Parameters
    ----------
    ac : Aircraft
    h : float
        Constant altitude [m].
    W_start, W_end : float
        Weights at the start and end of the segment [N], ``W_start > W_end``.
    V : float, optional
        Constant true airspeed [m/s]. Default: the schedule of :func:`best_range_speed`
        (``speed="range"``) or :func:`best_endurance_speed` (``speed="endurance"``) at the current
        weight (constant C_L, so V ∝ √W).
    speed : {"range", "endurance"}
        Speed schedule used when ``V`` is None.
    n : int
        Gauss–Legendre points over the weight interval.

    Returns
    -------
    dict
        ``range`` [m], ``time`` [s], ``mean_speed`` = range/time [m/s], ``fuel`` [N],
        ``V_start``, ``V_end`` [m/s].

    Raises
    ------
    ValueError
        Bad weights, or the speed cannot be held at ``W_start`` (P_R > P_A or V < V_stall).

    Notes
    -----
    t = ∫_{W_end}^{W_start} dW / ẇ_f(V, h, W) and R = ∫ V dW / ẇ_f with ẇ_f = ``ac.fuel_flow``. For a
    propeller at the max-L/D speed this reproduces :func:`breguet_range_propeller` exactly (constant C_L,
    η, c), which is the verification of the integration.
    """
    _check_weights(W_start, W_end)
    if speed not in ("range", "endurance"):
        raise ValueError("speed must be 'range' or 'endurance'")
    if n < 2:
        raise ValueError("n must be >= 2")

    def v_of(w: float) -> float:
        if V is not None:
            return float(V)
        return best_range_speed(ac, h, w) if speed == "range" else best_endurance_speed(ac, h, w)

    v0 = v_of(W_start)
    if not v0 >= ac.stall_speed(h, W_start):
        raise ValueError(f"V = {v0:.4g} m/s is below the clean stall speed at W_start")
    if ac.power_required(v0, h, W_start) > ac.power_available(v0, h):
        raise ValueError(f"level flight at V = {v0:.4g} m/s, h = {h:g} m needs more power than available")
    x, wq = np.polynomial.legendre.leggauss(int(n))
    mid, half = 0.5 * (W_start + W_end), 0.5 * (W_start - W_end)
    ws = mid + half * x
    vs = np.array([v_of(float(w)) for w in ws])
    ff = np.array([ac.fuel_flow(float(v), h, float(w)) for v, w in zip(vs, ws, strict=True)])
    t = float(half * np.sum(wq / ff))
    r = float(half * np.sum(wq * vs / ff))
    return {"range": r, "time": t, "mean_speed": r / t, "fuel": W_start - W_end, "V_start": v0,
            "V_end": v_of(W_end)}


@cite("raymer_2018", note="payload–range diagram; " + _RAYMER_NOTE)
def payload_range(ac: Aircraft, payload_max: float, fuel_max: float, W_max: float | None = None, *,
                  h_cruise: float, reserve_fraction: float = 0.06, W_empty: float | None = None,
                  V: float | None = None, n: int = 64) -> dict[str, NDArray[np.float64]]:
    """Three-corner payload–range diagram.

    Parameters
    ----------
    ac : Aircraft
    payload_max : float
        Maximum (structural) payload [N].
    fuel_max : float
        Usable fuel capacity [N].
    W_max : float, optional
        Maximum take-off weight [N] (default ``ac.W0``).
    h_cruise : float
        Cruise altitude [m] (keyword-only, required).
    reserve_fraction : float
        Fraction of the fuel on board held as reserve and not burned (default 0.06, **assumption**,
        cf. the ×1.06 reserve + trapped fuel of the rehearsal sizing).
    W_empty : float, optional
        Operating empty weight [N] (default ``ac.W_empty``; must be > 0).
    V : float, optional
        Constant cruise speed [m/s]; default the best-range schedule.
    n : int
        Gauss–Legendre points of :func:`range_and_endurance`.

    Returns
    -------
    dict
        Arrays of the four diagram points [start, A (max payload), B (max fuel at MTOW), C (ferry)]:
        ``range`` [m], ``payload`` [N], ``fuel`` [N], ``takeoff_weight`` [N].

    Raises
    ------
    ValueError
        Missing empty weight, or no fuel can be carried with the maximum payload.

    Notes
    -----
    A: payload_max with fuel min(fuel_max, W_max − W_e − payload_max); B: fuel_max with payload
    min(payload_max, W_max − W_e − fuel_max) (≥ 0); C: fuel_max, zero payload (take-off weight below
    MTOW). Each range is the pure cruise at ``h_cruise`` burning (1 − reserve) of the fuel; no
    allowance for take-off, climb, descent or loiter.
    """
    w_max = _weight(ac, W_max)
    w_e = ac.W_empty if W_empty is None else float(W_empty)
    if not w_e > 0:
        raise ValueError("payload_range needs the operating empty weight (ac.W_empty or W_empty > 0)")
    if not (payload_max > 0 and fuel_max > 0 and 0 <= reserve_fraction < 1):
        raise ValueError("need payload_max > 0, fuel_max > 0 and 0 <= reserve_fraction < 1")
    fuel_a = min(fuel_max, w_max - w_e - payload_max)
    if not fuel_a > 0:
        raise ValueError("W_empty + payload_max leaves no fuel within W_max")
    pl_b = max(min(payload_max, w_max - w_e - fuel_max), 0.0)
    points = [(payload_max, 0.0), (payload_max, fuel_a), (pl_b, fuel_max), (0.0, fuel_max)]
    rng, pl, fu, tow = [], [], [], []
    for payload, fuel in points:
        w_to = w_e + payload + fuel
        if fuel > 0:
            rng.append(range_and_endurance(ac, h_cruise, w_to, w_to - (1.0 - reserve_fraction) * fuel, V,
                                           n=n)["range"])
        else:
            rng.append(0.0)
        pl.append(payload)
        fu.append(fuel)
        tow.append(w_to)
    return {"range": np.array(rng), "payload": np.array(pl), "fuel": np.array(fu),
            "takeoff_weight": np.array(tow)}


# ---------------------------------------------------------------------- requirement compliance
class ComplianceRow(TypedDict):
    """One line of the compliance table (SI values; ``margin`` relative, ≥ 0 means met)."""

    requirement: str
    required: float
    achieved: float
    margin: float
    unit: str
    passed: bool
    method: str


REQUIREMENT_KEYS: dict[str, str] = {
    # checked requirements
    "range": "m", "loiter": "s", "stall_speed": "m/s", "max_speed": "m/s", "service_ceiling": "m",
    "rate_of_climb": "m/s", "takeoff_ground_roll": "m", "landing_distance": "m", "payload": "N",
    # modifiers (defaults in brackets)
    "max_speed_altitude": "m [0]", "rate_of_climb_altitude": "m [0]", "cruise_altitude": "m [3000, assumption]",
    "loiter_altitude": "m [cruise_altitude]", "reserve_fraction": "- [0.06]",
    "stall_speed_CLmax": "- [ac.CLmax_landing]", "runway_altitude": "m [0]",
}
_CHECK_ORDER = ("range", "loiter", "stall_speed", "max_speed", "service_ceiling", "rate_of_climb",
                "takeoff_ground_roll", "landing_distance", "payload")


def _row(name: str, required: float, achieved: float, unit: str, method: str, at_least: bool) -> ComplianceRow:
    if not required > 0:
        raise ValueError(f"requirement {name!r} must be > 0")
    margin = (achieved - required) / required if at_least else (required - achieved) / required
    return {"requirement": name, "required": float(required), "achieved": float(achieved), "margin": margin,
            "unit": unit, "passed": bool(margin >= 0), "method": method}


def _mission(ac: Aircraft, req: Mapping[str, float]) -> tuple[float, float, str]:
    """(achieved range given the required loiter, achieved loiter given the required range, method)."""
    if not ac.W_fuel > 0:
        raise ValueError("range/loiter compliance needs the usable fuel weight ac.W_fuel > 0")
    r = float(req.get("reserve_fraction", 0.06))
    if not 0 <= r < 1:
        raise ValueError("reserve_fraction must be in [0, 1)")
    hc = float(req.get("cruise_altitude", 3000.0))
    hl = float(req.get("loiter_altitude", hc))
    r_req, l_req = float(req.get("range", 0.0)), float(req.get("loiter", 0.0))
    w0 = ac.W0
    w_end = w0 - (1.0 - r) * ac.W_fuel

    def loiter(w1: float) -> float:
        return range_and_endurance(ac, hl, w1, w_end, speed="endurance")["time"] if w1 > w_end else 0.0

    def cruise(w1: float) -> float:
        return range_and_endurance(ac, hc, w0, w1, speed="range")["range"] if w1 < w0 else 0.0

    if l_req <= 0:
        r_ach = cruise(w_end)
    elif loiter(w0) < l_req:
        r_ach = 0.0
    else:
        r_ach = cruise(float(brentq(lambda w: loiter(w) - l_req, w_end, w0, xtol=1e-6, rtol=1e-12)))
    if r_req <= 0:
        l_ach = loiter(w0)
    elif cruise(w_end) < r_req:
        l_ach = 0.0
    else:
        l_ach = loiter(float(brentq(lambda w: cruise(w) - r_req, w_end, w0, xtol=1e-6, rtol=1e-12)))
    method = (f"one mission from W0: cruise at the best-range speed (h = {hc:g} m) then loiter at the "
              f"best-endurance speed (h = {hl:g} m) on (1 - {r:g})*W_fuel (reserve {r:g}); numerical "
              f"dW/dt integral; no take-off/climb/descent fuel")
    return r_ach, l_ach, method


def compliance(ac: Aircraft, requirements: Mapping[str, float]) -> list[ComplianceRow]:
    """Requirement → computed value → margin → PASS/FAIL table.

    Parameters
    ----------
    ac : Aircraft
        The design (``W_fuel`` needed for range/loiter, ``W_empty`` or ``W_payload`` for payload).
    requirements : mapping
        SI values; any of ``range`` [m], ``loiter`` [s], ``stall_speed`` [m/s, maximum],
        ``max_speed`` [m/s, minimum], ``service_ceiling`` [m], ``rate_of_climb`` [m/s],
        ``takeoff_ground_roll`` [m, maximum], ``landing_distance`` [m, maximum, from 50 ft],
        ``payload`` [N], plus the modifiers of :data:`REQUIREMENT_KEYS`.

    Returns
    -------
    list of ComplianceRow
        One row per requirement present, in a fixed order. ``margin`` is relative:
        (achieved − required)/required for minimum requirements and (required − achieved)/required for
        maximum ones (stall speed, distances); ``passed`` is ``margin >= 0``.

    Raises
    ------
    ValueError
        Unknown key, non-positive requirement, or data missing for a requested check.

    Notes
    -----
    All point-performance checks are at W0 (conservative). Range and loiter are evaluated together as one
    mission (cruise, then loiter at the best-endurance speed, with a fuel reserve): the achieved range is the
    one left after the required loiter and vice versa. The payload achieved is W0 − W_empty − W_fuel
    (if ``ac.W_empty`` > 0), otherwise ``ac.W_payload``. A service ceiling above 20 km is reported as
    ``inf`` (passes).
    """
    unknown = sorted(set(requirements) - set(REQUIREMENT_KEYS))
    if unknown:
        raise ValueError(f"unknown requirement key(s): {', '.join(unknown)}")
    req = {k: float(v) for k, v in requirements.items()}
    rows: list[ComplianceRow] = []
    mission: tuple[float, float, str] | None = None
    if "range" in req or "loiter" in req:
        mission = _mission(ac, req)
    h_rw = req.get("runway_altitude", 0.0)
    for key in _CHECK_ORDER:
        if key not in req:
            continue
        need = req[key]
        if key in ("range", "loiter") and mission is not None:
            r_ach, l_ach, how = mission
            rows.append(_row(key, need, r_ach if key == "range" else l_ach, REQUIREMENT_KEYS[key], how, True))
        elif key == "stall_speed":
            cl = req.get("stall_speed_CLmax", ac.CLmax_landing)
            rows.append(_row(key, need, ac.stall_speed(0.0, ac.W0, cl), "m/s",
                             f"1-g stall at sea level, W0, CLmax = {cl:g}", False))
        elif key == "max_speed":
            h = req.get("max_speed_altitude", 0.0)
            rows.append(_row(key, need, max_speed(ac, h, ac.W0), "m/s",
                             f"largest V with P_A = P_R at h = {h:g} m, W0 (no compressibility)", True))
        elif key == "service_ceiling":
            rows.append(_row(key, need, _ceiling(ac, ac.W0, SERVICE_CEILING_ROC), "m",
                             "altitude of max ROC = 0.508 m/s at W0 (root finding, 0-20 km)", True))
        elif key == "rate_of_climb":
            h = req.get("rate_of_climb_altitude", 0.0)
            rows.append(_row(key, need, max_rate_of_climb(ac, h, ac.W0), "m/s",
                             f"max steady ROC (P_A - P_R)/W at h = {h:g} m, W0", True))
        elif key == "takeoff_ground_roll":
            to = takeoff_distance(ac, h_rw, ac.W0, obstacle=0.0)
            rows.append(_row(key, need, to["ground_roll"], "m",
                             f"ground roll to V_LOF = 1.1 V_stall,TO (CLmax {ac.CLmax_takeoff:g}, "
                             f"mu {ac.mu_roll:g}), forces at 0.7 V_LOF, h = {h_rw:g} m, W0", False))
        elif key == "landing_distance":
            ld = landing_distance(ac, h_rw, ac.W0)
            rows.append(_row(key, need, ld["total"], "m",
                             f"from 50 ft, approach 1.3 V_stall,L (CLmax {ac.CLmax_landing:g}), braking mu 0.4 "
                             f"(assumption), no reverse thrust, landing at W0, h = {h_rw:g} m", False))
        elif key == "payload":
            if ac.W_empty > 0:
                pl, how = ac.W0 - ac.W_empty - ac.W_fuel, "W0 - W_empty - W_fuel"
            elif ac.W_payload > 0:
                pl, how = ac.W_payload, "design payload ac.W_payload"
            else:
                raise ValueError("payload compliance needs ac.W_empty or ac.W_payload > 0")
            rows.append(_row(key, need, pl, "N", how, True))
    return rows
