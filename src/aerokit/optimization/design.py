"""Design-level optimization: constraint-diagram optimum, design carpet (AR × W/S), minimum-mass sizing of a
wing box and a tube, and general tools (parametric scan, Pareto, sensitivity, reliability).

Sections
--------
(a) Constraint diagram: feasible region from the :mod:`aerokit.aero.sizing` constraint functions, design point
    (largest W/S or least P/W), active constraints and KKT check; (AR, W/S) carpet and scipy minimization of
    W0 or installed power.
(b) Wing box: skin and spar-web thickness (per region), stringer and rib pitch (optionally box-height ratio);
    MS ≥ 0 constraints for yield (limit), ultimate (×FS), skin-panel buckling, stringer column buckling and
    web shear buckling.
(c) Tube / strut: least cross-section area under bending + torsion + axial compression; closed-form solution
    for pure Euler + local buckling.
(d) General tools: grid / Latin hypercube scan, non-dominated sorting, elasticities (∂ln f/∂ln x),
    Monte Carlo P_f (with a confidence interval), FORM (Hasofer–Lind / Rackwitz–Fiessler iteration).

Source status
-------------
- Constraint equations and the Raymer weight chain: :mod:`aerokit.aero.sizing` (with its own source notes); the
  aero chain (KLD, Swet/Sref → L/Dmax → CD0, K) is identical to the CLI ``sizing`` command.
- Plate buckling coefficients: :mod:`aerokit.structures.buckling` (NACA TN 3781, Eq. 20 and Table 7).
- Raymer wing weight: :func:`aerokit.aero.weight.raymer_wing`.
- FORM: Hasofer & Lind (1974) reliability-index definition, Rackwitz & Fiessler (1978) iteration — the papers
  were NOT read in this repository; the algorithm is the standard HL-RF form and is tested against the closed
  form for a linear limit state (β = (μR − μS)/√(σR² + σS²)).
- Optimum strut (Euler and local buckling simultaneously active): derived below; the literature
  (Shanley 1960 etc.) was NOT read in this repository.

Units are SI (N, m, Pa, kg, s, W) unless stated otherwise.
"""
from __future__ import annotations

import functools
import math
import warnings
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy import integrate, optimize, stats

from aerokit.aero import sizing, wing
from aerokit.aero.atmosphere import G0, isa
from aerokit.aero.weight import raymer_wing
from aerokit.references import cite
from aerokit.structures import beam, buckling, structural_sizing

# ---------------------------------------------------------------------------
# (a) Constraint diagram
# ---------------------------------------------------------------------------
# Defaults of the CLI "sizing raymer" command (2023 Ansys assignment); each one is an ASSUMPTION or an
# assignment input.
DEFAULT_REQUIREMENT = {
    "V_stall": 150 / 3.6, "CLmax_landing": 2.0, "CLmax_takeoff": 1.7, "CLmax_clean": 1.5,
    "Vmax": 500 / 3.6, "h_vmax": 0.0, "ceiling": 10000.0, "climb": 10.0, "takeoff_m": 800.0,
    "eta": 0.8, "eta_takeoff": 0.6, "mu": 0.03, "AR": 9.0, "KLD": 11.0, "swet_sref": 5.5,
}
DEFAULT_MISSION = {
    "range_m": 1300e3, "loiter_s": 30 * 60, "V_loiter": 250 / 3.6, "cbhp_cruise": 0.5,
    "cbhp_loiter": 0.6, "eta": 0.8, "V_cruise": None, "h_cruise": 0.0,
}


def requirement(**change: Any) -> dict[str, Any]:
    """Copy of :data:`DEFAULT_REQUIREMENT` with selected entries changed.

    Parameters
    ----------
    **change
        Entries to override. Keys (SI): ``V_stall`` stall speed [m/s], ``CLmax_landing``, ``CLmax_takeoff``,
        ``CLmax_clean`` maximum lift coefficients [-], ``Vmax`` maximum speed [m/s] at altitude ``h_vmax`` [m],
        ``ceiling`` service ceiling [m], ``climb`` rate of climb at sea level [m/s], ``takeoff_m`` ground roll
        [m], ``eta`` / ``eta_takeoff`` propeller efficiencies [-], ``mu`` rolling friction coefficient [-],
        ``AR`` aspect ratio [-], ``KLD`` Raymer L/Dmax coefficient [-], ``swet_sref`` wetted-area ratio [-].

    Returns
    -------
    dict
        The requirement dictionary.

    Raises
    ------
    KeyError
        If a key is not in :data:`DEFAULT_REQUIREMENT`.

    Examples
    --------
    >>> requirement(AR=10.0)["AR"]
    10.0
    """
    g = dict(DEFAULT_REQUIREMENT)
    for k, v in change.items():
        if k not in g:
            raise KeyError(f"unknown requirement key: {k}")
        g[k] = v
    return g


@cite("raymer_2018", note="Oswald factor (straight wing) and wetted-aspect-ratio L/Dmax estimate, "
                          "via aerokit.aero.sizing")
def aero_coefficients(AR: float, KLD: float = 11.0, swet_sref: float = 5.5) -> dict[str, float]:
    """Parabolic-polar coefficients from aspect ratio.

    Parameters
    ----------
    AR : float
        Aspect ratio [-], > 0.
    KLD : float
        Raymer coefficient in L/Dmax = KLD·√(AR/(Swet/Sref)) [-].
    swet_sref : float
        Wetted-to-reference area ratio [-].

    Returns
    -------
    dict
        ``e`` Oswald factor (Raymer straight wing), ``LDmax`` maximum lift-to-drag ratio, ``CD0`` zero-lift drag
        coefficient and ``K`` induced-drag factor of the parabolic polar CD = CD0 + K·CL².

    Raises
    ------
    ValueError
        If ``AR <= 0``.
    """
    if AR <= 0:
        raise ValueError("AR must be positive")
    e = sizing.oswald_raymer(AR)
    LDmax = KLD * math.sqrt(AR / swet_sref)
    CD0, K = sizing.cd0_ldmax(LDmax, AR, e)
    return {"e": e, "LDmax": LDmax, "CD0": CD0, "K": K}


@cite("raymer_2018", note="climb power loading, via aerokit.aero.sizing.pw_required")
def pw_climb_precise(WS: float, Vv: float, h: float, CD0: float, K: float, eta_p: float, CLmax_clean: float,
                     V_upper: float) -> tuple[float, float]:
    """Continuous version of ``sizing.pw_en_good_climb``: least climb power loading over the speed.

    Parameters
    ----------
    WS : float
        Wing loading W/S [N/m²].
    Vv : float
        Required rate of climb [m/s].
    h : float
        Altitude [m].
    CD0, K : float
        Parabolic-polar coefficients [-].
    eta_p : float
        Propeller efficiency [-].
    CLmax_clean : float
        Clean maximum lift coefficient [-]; the lower speed bound is 1.1·V_s.
    V_upper : float
        Upper speed bound [m/s].

    Returns
    -------
    tuple of float
        (P/W [W/N] referred to sea level, best climb speed V [m/s]).

    Notes
    -----
    The speed is minimized over [1.1·V_s, V_upper] with Brent's bounded method instead of the 400-point grid,
    so the result is smooth in W/S (suitable for gradient-based optimizers). The interval end points are also
    compared and the smallest of the three candidates is returned.
    """
    rho = isa(h)["rho"]
    V_lower = 1.1 * math.sqrt(2 * WS / (rho * CLmax_clean))
    lo, hi = min(V_lower, V_upper), max(V_lower, V_upper)
    f = lambda V: sizing.pw_required(WS, V, Vv, h, CD0, K, eta_p)
    if hi - lo < 1e-12:
        return f(lo), lo
    r = optimize.minimize_scalar(f, bounds=(lo, hi), method="bounded", options={"xatol": 1e-10 * hi})
    candidates = [(r.fun, r.x), (f(lo), lo), (f(hi), hi)]
    return min(candidates)


@cite("raymer_2018", note="constraint diagram (P/W vs W/S), via aerokit.aero.sizing")
def constraint_functions(g: Mapping[str, Any], AR: float | None = None,
                         precise: bool = True) -> dict[str, Callable[[float], float]]:
    """Constraint name → f(W/S) = required sea-level power loading P/W [W/N].

    Parameters
    ----------
    g : mapping
        Requirement dictionary (see :func:`requirement`).
    AR : float, optional
        Aspect ratio overriding ``g["AR"]``.
    precise : bool
        True: climb/ceiling use :func:`pw_climb_precise` (continuous); False: ``sizing.pw_en_good_climb``
        (400-point speed grid, identical to the CLI).

    Returns
    -------
    dict
        ``climb``, ``ceiling``, ``vmax`` and ``takeoff`` callables of W/S [N/m²].
    """
    a = aero_coefficients(g["AR"] if AR is None else AR, g["KLD"], g["swet_sref"])
    CD0, K = a["CD0"], a["K"]
    climb_pw = pw_climb_precise if precise else (lambda *z: sizing.pw_en_good_climb(*z))
    return {
        "climb": lambda WS: climb_pw(WS, g["climb"], 0.0, CD0, K, g["eta"], g["CLmax_clean"], g["Vmax"])[0],
        "ceiling": lambda WS: climb_pw(WS, sizing.SERVICE_CEILING_VV, g["ceiling"], CD0, K, g["eta"],
                                       g["CLmax_clean"], g["Vmax"])[0],
        "vmax": lambda WS: sizing.pw_required(WS, g["Vmax"], 0.0, g["h_vmax"], CD0, K, g["eta"]),
        "takeoff": lambda WS: sizing.pw_takeoff(WS, g["takeoff_m"], g["CLmax_takeoff"], g["eta_takeoff"], g["mu"]),
    }


@cite("raymer_2018", note="stall wing loading W/S = ½ρV_s²CLmax")
def ws_stall_limit(g: Mapping[str, Any]) -> float:
    """Largest wing loading allowed by the stall requirement, W/S_stall [N/m²].

    Parameters
    ----------
    g : mapping
        Requirement dictionary with ``V_stall`` [m/s] and ``CLmax_landing`` [-].

    Returns
    -------
    float
        W/S_stall = ½ρ₀V_s²CLmax [N/m²].
    """
    return sizing.ws_stall(g["V_stall"], g["CLmax_landing"])


@cite("raymer_2018", note="constraint diagram")
def constraint_diagram(g: Mapping[str, Any], WS: ArrayLike | None = None, n: int = 200, AR: float | None = None,
                       precise: bool = True) -> dict[str, Any]:
    """Constraint curves, their envelope and the governing constraint at each W/S.

    Parameters
    ----------
    g : mapping
        Requirement dictionary.
    WS : array_like, optional
        Wing loadings [N/m²]; default ``n`` points on [0.2, 1.5]·W/S_stall.
    n : int
        Number of default points.
    AR : float, optional
        Aspect ratio overriding ``g["AR"]``.
    precise : bool
        See :func:`constraint_functions`.

    Returns
    -------
    dict
        ``WS`` [N/m²]; ``PW`` {name: P/W array [W/N]}; ``envelope`` (largest P/W); ``governing`` (constraint name
        per point); ``WS_stall`` [N/m²]; ``feasible`` (W/S ≤ W/S_stall).
    """
    WSs = ws_stall_limit(g)
    WS = np.linspace(0.2 * WSs, 1.5 * WSs, n) if WS is None else np.asarray(WS, float)
    funcs = constraint_functions(g, AR, precise)
    PW = {name: np.array([f(w) for w in WS]) for name, f in funcs.items()}
    stack = np.vstack(list(PW.values()))
    names = list(PW)
    return {"WS": WS, "PW": PW, "envelope": stack.max(axis=0), "governing": [names[i] for i in stack.argmax(axis=0)],
            "WS_stall": WSs, "feasible": WSs >= WS}


def _component(fn: Callable[[np.ndarray], np.ndarray], z: np.ndarray, i: int) -> float:
    """Component i of the vector function fn at z."""
    return float(fn(z)[i])


def _derivative(f: Callable[[float], float], x: float, h_rel: float = 1e-5) -> float:
    """Central finite-difference derivative with relative step ``h_rel``."""
    h = h_rel * max(abs(x), 1.0)
    return (f(x + h) - f(x - h)) / (2 * h)


@cite("nocedal_wright_2006", note="KKT first-order conditions, Ch. 12")
def kkt_check(grad_objective: ArrayLike, active_grads: Mapping[str, ArrayLike]) -> dict[str, Any]:
    """KKT stationarity of min f s.t. g_i ≤ 0: ∇f + Σ λ_i ∇g_i = 0 with λ ≥ 0.

    Parameters
    ----------
    grad_objective : array_like, shape (n,)
        ∇f at the candidate point.
    active_grads : mapping
        {name: ∇g_i (n,)} of the active constraints, written as g_i ≤ 0.

    Returns
    -------
    dict
        ``factors`` {name: λ_i} (non-negative least squares) and ``residual`` = ‖∇f + Σλ∇g‖/‖∇f‖
        (0 → KKT satisfied).

    Examples
    --------
    min x² + y² s.t. 1 − x − y ≤ 0 at (½, ½): ∇f = (1, 1), ∇g = (−1, −1) → λ = 1.

    >>> round(float(kkt_check([1.0, 1.0], {"g": [-1.0, -1.0]})["factors"]["g"]), 12)
    1.0
    """
    gf = np.asarray(grad_objective, float)
    names = list(active_grads)
    scale = max(float(np.linalg.norm(gf)), 1e-300)
    if not names:
        return {"factors": {}, "residual": float(np.linalg.norm(gf) / scale)}
    G = np.column_stack([np.asarray(active_grads[a], float) for a in names])
    lam, res = optimize.nnls(G, -gf)
    return {"factors": dict(zip(names, lam, strict=True)), "residual": float(res / scale)}


@cite("raymer_2018", note="design point on the constraint diagram")
@cite("nocedal_wright_2006", note="KKT check of the pw_min optimum")
def design_point(g: Mapping[str, Any], rule: str = "ws_max", AR: float | None = None, WS_lower: float | None = None,
                 rtol_active: float = 1e-4, precise: bool = True, n: int = 400) -> dict[str, Any]:
    """Design point on the constraint diagram.

    Parameters
    ----------
    g : mapping
        Requirement dictionary.
    rule : {"ws_max", "pw_min"}
        ``"ws_max"``: W/S = W/S_stall (largest wing loading allowed by stall), P/W = envelope(W/S_stall).
        ``"pw_min"``: minimize the envelope (least installed power loading) on [WS_lower, W/S_stall].
    AR : float, optional
        Aspect ratio overriding ``g["AR"]``.
    WS_lower : float, optional
        Lower W/S bound for ``"pw_min"`` [N/m²]; default 0.2·W/S_stall.
    rtol_active : float
        Constraint i is active if P/W_i ≥ (1 − rtol_active)·P/W*.
    precise : bool
        See :func:`constraint_functions`.
    n : int
        Grid points for the coarse ``"pw_min"`` search before bounded refinement.

    Returns
    -------
    dict
        ``WS`` [N/m²], ``PW`` [W/N], ``PW_constraints`` {name: P/W at WS}, ``active`` (names, plus ``"stall"``
        if W/S is on its bound), ``slopes`` {active name: d(P/W)/d(W/S)}, ``kkt`` (see :func:`kkt_check`),
        ``WS_stall``, ``rule``.

    Raises
    ------
    ValueError
        For an unknown ``rule``.

    Notes
    -----
    KKT with variables x = (W/S, P/W): min P/W s.t. f_i(W/S) − P/W ≤ 0 and W/S − W/S_stall ≤ 0, so
    ∇objective = (0, 1), ∇g_i = (f_i', −1) and ∇g_stall = (1, 0).
    """
    WSs = ws_stall_limit(g)
    WS_lower = 0.2 * WSs if WS_lower is None else WS_lower
    funcs = constraint_functions(g, AR, precise)
    envelope = lambda w: max(f(w) for f in funcs.values())
    if rule == "ws_max":
        WS = WSs
    elif rule == "pw_min":
        grid = np.linspace(WS_lower, WSs, n)
        z = np.array([envelope(w) for w in grid])
        i = int(np.argmin(z))
        if i == len(grid) - 1:
            WS = WSs
        elif i == 0:
            WS = WS_lower
        else:
            r = optimize.minimize_scalar(envelope, bounds=(grid[i - 1], grid[i + 1]), method="bounded",
                                         options={"xatol": 1e-9 * WSs})
            WS = r.x if r.fun <= z[i] else grid[i]
    else:
        raise ValueError("rule must be 'ws_max' or 'pw_min'")
    PW_each = {name: f(WS) for name, f in funcs.items()}
    PW = max(PW_each.values())
    active = [name for name, v in PW_each.items() if v >= (1 - rtol_active) * PW]
    stall_active = WSs * (1 - 1e-12) <= WS
    slope = {name: _derivative(funcs[name], WS, 1e-6) for name in active}
    # KKT: x = (WS, PW), ∇objective = (0, 1); constraint i: (f_i', −1); stall: (1, 0)
    gr = {name: np.array([slope[name], -1.0]) for name in active}
    if stall_active:
        gr["stall"] = np.array([1.0, 0.0])
    kkt = kkt_check(np.array([0.0, 1.0]), gr)
    return {"WS": WS, "PW": PW, "PW_constraints": PW_each, "active": active + (["stall"] if stall_active else []),
            "slopes": slope, "kkt": kkt, "WS_stall": WSs, "rule": rule}


# --- mission, weight, carpet ---
@cite("raymer_2018", note="mission-segment weight fractions, Breguet propeller cruise and loiter")
def mission_fraction(mission: Mapping[str, Any], aero: Mapping[str, float],
                     WS: float | None = None) -> tuple[float, float]:
    """Mission weight fraction W_end/W0 and the cruise L/D used.

    Parameters
    ----------
    mission : mapping
        Mission dictionary (see :data:`DEFAULT_MISSION`): ``range_m`` [m], ``loiter_s`` [s], ``V_loiter`` [m/s],
        ``cbhp_cruise`` / ``cbhp_loiter`` brake specific fuel consumption [lb/(hp·h)], ``eta`` propeller
        efficiency [-], optional ``V_cruise`` [m/s] and ``h_cruise`` [m].
    aero : mapping
        Output of :func:`aero_coefficients` (``LDmax``, ``CD0``, ``K``).
    WS : float, optional
        Wing loading [N/m²]; required when ``mission["V_cruise"]`` is given.

    Returns
    -------
    tuple of float
        (product of the segment fractions, cruise L/D).

    Raises
    ------
    ValueError
        If ``V_cruise`` is given without ``WS``.

    Notes
    -----
    Segments (same as the CLI sizing command): warm-up/takeoff, climb, propeller cruise (Breguet), loiter
    (at 0.866·L/Dmax), landing. With ``V_cruise`` the cruise L/D follows from W/S with L = W on the parabolic
    polar, L/D = 1/(q·CD0/(W/S) + K·(W/S)/q) (derivation); otherwise L/Dmax is used (CLI assumption).
    """
    LD_cruise = aero["LDmax"]
    if mission.get("V_cruise") is not None:
        if WS is None:
            raise ValueError("W/S is required when V_cruise is given")
        q = 0.5 * isa(mission.get("h_cruise", 0.0))["rho"] * mission["V_cruise"] ** 2
        LD_cruise = 1.0 / (q * aero["CD0"] / WS + aero["K"] * WS / q)
    fractions = [sizing.SEGMENT["heating_takeoff"], sizing.SEGMENT["climb"],
                 sizing.cruise_propeller(mission["range_m"], mission["cbhp_cruise"], mission["eta"], LD_cruise),
                 sizing.loiter_propeller(mission["loiter_s"], mission["V_loiter"], mission["cbhp_loiter"],
                                         mission["eta"], 0.866 * aero["LDmax"]),
                 sizing.SEGMENT["landing"]]
    return math.prod(fractions), LD_cruise


@cite("raymer_2018", note="takeoff-weight fixed point (empty-weight regression) and wing group weight")
def weight_calc(g: Mapping[str, Any], mission: Mapping[str, Any], W_fixed: float, kind: str, AR: float, WS: float,
                PW: float | None = None, engine_kg_W: float | None = None,
                wing_correction: Mapping[str, float] | None = None, precise: bool = True,
                tol: float = 1e-13) -> dict[str, Any]:
    """Raymer takeoff weight and installed power at one (AR, W/S) point.

    Parameters
    ----------
    g : mapping
        Requirement dictionary.
    mission : mapping
        Mission dictionary (see :func:`mission_fraction`).
    W_fixed : float
        Fixed (crew + payload) weight [N].
    kind : str
        Aircraft kind key of ``aerokit.aero.sizing.EMPTY_WEIGHT``.
    AR : float
        Aspect ratio [-].
    WS : float
        Wing loading [N/m²].
    PW : float, optional
        Power loading [W/N]; default: the constraint envelope (least required P/W) at WS.
    engine_kg_W : float, optional
        Installed engine mass per power [kg/W] (ASSUMPTION): W_engine = engine_kg_W·g0·(P/W)·W0.
    wing_correction : mapping, optional
        ``AR_ref``, ``WS_ref`` [N/m²], ``Lambda`` [rad], ``taper``, ``t_c``, ``q`` [Pa], ``Nz``: the difference of
        the Raymer wing weight from a reference wing is added to the fixed weight,
        ΔW = g0·[W_wing(S, AR) − W_wing(S_ref, AR_ref)], S = W0/(W/S) (ASSUMPTION).
    precise : bool
        See :func:`constraint_functions`.
    tol : float
        Relative tolerance of the W0 fixed-point iterations.

    Returns
    -------
    dict
        ``W0`` [N], ``We_W0``, ``Wf_W0``, ``mission_fraction``, ``LD_cruise``, ``PW`` [W/N], ``P`` installed power
        [W], ``S`` wing area [m²], ``feasible_stall`` (W/S ≤ W/S_stall), ``extra_weight`` ΔW [N], plus the keys of
        :func:`aero_coefficients`.

    Raises
    ------
    ValueError
        If the W0 fixed point with extra weights does not converge in 500 iterations.

    Notes
    -----
    Raymer's Table 3.1 empty-weight regression contains a "typical" wing; the difference term carries the effect
    of AR and W/S. Without extras ``sizing.takeoff_weight`` is used directly; with extras the fixed point
    W0 = takeoff_weight(W_fixed + ΔW(W0)) is iterated.
    """
    aero = aero_coefficients(AR, g["KLD"], g["swet_sref"])
    frac, LD = mission_fraction(mission, aero, WS)
    wf = sizing.fuel_ratio(frac)
    if PW is None:
        PW = max(f(WS) for f in constraint_functions(g, AR, precise).values())

    def extra(W0: float) -> float:
        """Extra weight ΔW(W0) [N] from the engine and wing-correction terms."""
        dW = 0.0
        if engine_kg_W:
            dW += engine_kg_W * G0 * PW * W0
        if wing_correction:
            k = wing_correction
            m0 = W0 / G0
            dW += G0 * (raymer_wing(W0 / WS, 0.0, AR, k["Lambda"], k["q"], k["taper"], k["t_c"], k["Nz"], m0)
                        - raymer_wing(W0 / k["WS_ref"], 0.0, k["AR_ref"], k["Lambda"], k["q"], k["taper"],
                                      k["t_c"], k["Nz"], m0))
        return dW
    s = sizing.takeoff_weight(W_fixed, wf, kind, tol=tol)
    if engine_kg_W or wing_correction:
        W0 = s["W0"]
        for _ in range(500):
            s = sizing.takeoff_weight(W_fixed + extra(W0), wf, kind, W0_initial=W0, tol=tol)
            if abs(s["W0"] - W0) <= tol * W0:
                break
            W0 = s["W0"]
        else:
            raise ValueError("W0 fixed point with extra weights did not converge")
    W0 = s["W0"]
    return {"W0": W0, "We_W0": s["We_W0"], "Wf_W0": wf, "mission_fraction": frac, "LD_cruise": LD, "PW": PW,
            "P": PW * W0, "S": W0 / WS, "feasible_stall": ws_stall_limit(g) * (1 + 1e-12) >= WS,
            "extra_weight": extra(W0) if (engine_kg_W or wing_correction) else 0.0, **aero}


@cite("raymer_2018", note="design carpet plot")
def design_carpet(g: Mapping[str, Any], mission: Mapping[str, Any], W_fixed: float, kind: str, AR_list: ArrayLike,
                  WS_list: ArrayLike, **kw: Any) -> dict[str, np.ndarray]:
    """(AR, W/S) design carpet: W0, installed power, wing area and stall feasibility in each cell.

    Parameters
    ----------
    g, mission, W_fixed, kind
        As in :func:`weight_calc`.
    AR_list : array_like
        Aspect ratios [-] (rows).
    WS_list : array_like
        Wing loadings [N/m²] (columns).
    **kw
        Passed to :func:`weight_calc`.

    Returns
    -------
    dict
        ``AR``, ``WS`` (input axes), ``W0`` [N], ``P`` [W], ``S`` [m²] and ``feasible`` (bool), each of shape
        (len(AR_list), len(WS_list)).
    """
    AR_list, WS_list = np.asarray(AR_list, float), np.asarray(WS_list, float)
    shape = (len(AR_list), len(WS_list))
    W0, P, S = np.zeros(shape), np.zeros(shape), np.zeros(shape)
    ok = np.zeros(shape, bool)
    for i, AR in enumerate(AR_list):
        for j, WS in enumerate(WS_list):
            r = weight_calc(g, mission, W_fixed, kind, AR, WS, **kw)
            W0[i, j], P[i, j], S[i, j], ok[i, j] = r["W0"], r["P"], r["S"], r["feasible_stall"]
    return {"AR": AR_list, "WS": WS_list, "W0": W0, "P": P, "S": S, "feasible": ok}


@cite("raymer_2018", note="conceptual sizing with the constraint diagram")
@cite("nocedal_wright_2006", note="SQP and KKT conditions, Ch. 12 and 18")
def design_optimize(g: Mapping[str, Any], mission: Mapping[str, Any], W_fixed: float, kind: str,
                    objective: str = "W0", AR_interval: tuple[float, float] = (6.0, 14.0),
                    WS_interval: tuple[float, float] | None = None, engine_kg_W: float | None = None,
                    wing_correction: Mapping[str, float] | None = None, x0: tuple[float, float] | None = None,
                    rtol_active: float = 1e-5) -> dict[str, Any]:
    """SLSQP over (AR, W/S, P/W) minimizing W0 or the installed power P = (P/W)·W0.

    Parameters
    ----------
    g, mission, W_fixed, kind
        As in :func:`weight_calc`.
    objective : {"W0", "P"}
        Takeoff weight [N] or installed power [W].
    AR_interval : tuple of float
        Aspect-ratio bounds [-].
    WS_interval : tuple of float, optional
        W/S bounds [N/m²]; default (0.3, 1)·W/S_stall. The upper bound is capped at W/S_stall.
    engine_kg_W, wing_correction
        Extra weights, see :func:`weight_calc`.
    x0 : tuple of float, optional
        Start (AR, W/S); default (mid AR interval, upper W/S bound).
    rtol_active : float
        Relative tolerance for reporting a performance constraint as active.

    Returns
    -------
    dict
        ``AR``, ``WS`` [N/m²], ``PW`` [W/N], ``W0`` [N], ``P`` [W], ``S`` [m²]; ``active`` (performance
        constraints plus bound names ``AR_lower``, ``AR_upper``, ``WS_lower``, ``WS_upper`` or ``stall``);
        ``PW_constraints``; ``kkt`` (see :func:`kkt_check`, in scaled variables with central differences);
        ``success``; ``message``; ``detail`` (the :func:`weight_calc` result at the optimum).

    Raises
    ------
    ValueError
        For an unknown ``objective``.

    Notes
    -----
    Constraints: P/W − f_i(W/S, AR) ≥ 0 (four performance constraints), W/S ≤ W/S_stall (upper bound) and the AR
    bounds. The variables are scaled by their start values.
    """
    WSs = ws_stall_limit(g)
    WS_lo, WS_hi = WS_interval if WS_interval is not None else (0.3 * WSs, WSs)
    WS_hi = min(WS_hi, WSs)
    if x0 is None:
        x0 = (0.5 * sum(AR_interval), WS_hi)
    AR0, WS0 = x0
    PW0 = max(f(WS0) for f in constraint_functions(g, AR0).values())
    scale = np.array([AR0, WS0, PW0])
    names = list(constraint_functions(g, AR0))

    def unscale(z: np.ndarray) -> np.ndarray:
        """Scaled → physical (AR, W/S, P/W)."""
        return z * scale

    def objective_f(z: np.ndarray) -> float:
        """Objective (W0 or P) at the scaled point z."""
        AR, WS, PW = unscale(z)
        r = weight_calc(g, mission, W_fixed, kind, AR, WS, PW=PW, engine_kg_W=engine_kg_W,
                        wing_correction=wing_correction)
        return r["W0"] if objective == "W0" else r["P"]
    if objective not in ("W0", "P"):
        raise ValueError("objective must be 'W0' or 'P'")
    f0 = objective_f(np.ones(3))

    def constraint_vec(z: np.ndarray) -> np.ndarray:
        """Normalized performance margins (P/W − f_i)/PW0 ≥ 0."""
        AR, WS, PW = unscale(z)
        funcs = constraint_functions(g, AR)
        return np.array([(PW - funcs[a](WS)) / PW0 for a in names])
    bounds = [(AR_interval[0] / AR0, AR_interval[1] / AR0), (WS_lo / WS0, WS_hi / WS0), (1e-3, 1e3)]
    z0 = np.ones(3)
    z0[2] = 1.0 + 1e-6
    r = optimize.minimize(lambda z: objective_f(z) / f0, z0, method="SLSQP", bounds=bounds,
                          constraints=[{"type": "ineq", "fun": constraint_vec}],
                          options={"ftol": 1e-12, "maxiter": 300, "eps": 1e-7})
    AR, WS, PW = unscale(r.x)
    final = weight_calc(g, mission, W_fixed, kind, AR, WS, PW=PW, engine_kg_W=engine_kg_W,
                        wing_correction=wing_correction)
    funcs = constraint_functions(g, AR)
    PW_each = {a: funcs[a](WS) for a in names}
    active = [a for a in names if PW_each[a] >= (1 - rtol_active) * PW]
    bound_active = []
    if AR_interval[0] * (1 + 1e-6) >= AR:
        bound_active.append("AR_lower")
    if AR_interval[1] * (1 - 1e-6) <= AR:
        bound_active.append("AR_upper")
    if WS_hi * (1 - 1e-6) <= WS:
        bound_active.append("stall" if WS_hi == WSs else "WS_upper")
    if WS_lo * (1 + 1e-6) >= WS:
        bound_active.append("WS_lower")
    # KKT (in scaled variables, central differences): objective and active constraints written as g ≤ 0
    z = r.x

    def grad(fn: Callable[[np.ndarray], Any], z: np.ndarray, h: float = 1e-6) -> np.ndarray:
        """Central-difference gradient of fn at z."""
        return np.array([(fn(z + h * e) - fn(z - h * e)) / (2 * h) for e in np.eye(3)])
    gr = {}
    for i, a in enumerate(names):
        if a in active:
            gr[a] = -grad(functools.partial(_component, constraint_vec, i=i), z)
    unit = {"AR_lower": (0, -1), "AR_upper": (0, 1), "WS_lower": (1, -1), "WS_upper": (1, 1), "stall": (1, 1)}
    for s in bound_active:
        v = np.zeros(3)
        v[unit[s][0]] = unit[s][1]
        gr[s] = v
    kkt = kkt_check(grad(lambda zz: objective_f(zz) / f0, z), gr)
    return {"AR": AR, "WS": WS, "PW": PW, "W0": final["W0"], "P": final["P"], "S": final["S"],
            "active": active + bound_active, "PW_constraints": PW_each, "kkt": kkt, "success": bool(r.success),
            "message": r.message, "detail": final}


# ---------------------------------------------------------------------------
# (b) Minimum-mass wing box
# ---------------------------------------------------------------------------
def _box_geometry(y: np.ndarray, b: float, c_root: float, c_uc: float, t_c: float, h_ratio: float,
                  box_ratio: float) -> tuple[Any, Any, Any]:
    """Chord c, box width w = box_ratio·c and box height h = h_ratio·(t/c)·c at stations y [m]."""
    c = wing.trapezoid_chord(y, b, c_root, c_uc)
    return c, box_ratio * c, h_ratio * t_c * c


def _ms(allowed: ArrayLike, applied: ArrayLike, FS: float) -> np.ndarray:
    """Array margin MS = allowed/(FS·|applied|) − 1 (as beam.safety_margin; applied = 0 → +inf)."""
    u = FS * np.abs(applied)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(u > 0, allowed / np.where(u > 0, u, 1.0) - 1.0, np.inf)


class _WingBox:
    """Load/geometry cache and margin-of-safety evaluator of the wing box (internal)."""

    def __init__(self, W, n_limit, b, c_root, c_uc, t_c, mat, FS, n_region, box_ratio, stringer_A,
                 stringer_rho, t_rib, rib_fraction, t_min, include_buckling, torsion, distribution, n_point):
        """Compute span loads (limit) once and split the half span into ``n_region`` regions."""
        self.b, self.c_root, self.c_uc, self.t_c = b, c_root, c_uc, t_c
        self.m, self.FS, self.box_ratio = mat, FS, box_ratio
        self.A_st, self.rho_st = stringer_A, stringer_rho
        self.t_r, self.f_r, self.t_min = t_rib, rib_fraction, t_min
        self.buckling = include_buckling
        k = max(1, math.ceil((n_point - 1) / n_region))
        n_point = n_region * k + 1
        loads = wing.span_loads(W, n_limit, b, c_root, c_uc, distribution=distribution, n_point=n_point)
        self.y, self.M, self.V = loads["y"], np.abs(loads["M"]), np.abs(loads["V"])
        self.T = np.abs(np.array([torsion(v) for v in self.y])) if torsion is not None else np.zeros_like(self.y)
        self.region = [np.arange(j * k, (j + 1) * k + 1) for j in range(n_region)]
        self.n_region = n_region
        E, nu = mat["E"], mat["nu"]
        self.Dp = math.pi ** 2 * E / (12 * (1 - nu ** 2))

    def configure(self, b_s, a, h_ratio):
        """Set the pitch/height variables and compute the station quantities that depend on them (k factors)."""
        self.b_s, self.a, self.h_ratio = b_s, a, h_ratio
        _, self.w, self.h = _box_geometry(self.y, self.b, self.c_root, self.c_uc, self.t_c, h_ratio, self.box_ratio)
        if self.A_st:
            self.n_st = np.maximum(self.w / b_s - 1.0, 0.0)
        else:
            self.n_st = np.zeros_like(self.w)
        self.b_p = self.w / (self.n_st + 1.0)
        # TN 3781 Eq. 20 (SS-SS closed form; identical to the exact Lévy solution of buckling.plate_compression_k)
        self.k_c = np.array([buckling.plate_compression_k_ss_closed(a / bp) for bp in self.b_p])
        self.k_s_skin = np.array([buckling.plate_shear_k(a / bp, "SS") for bp in self.b_p])
        self.k_s_web = np.array([buckling.plate_shear_k(a / hh, "SS") for hh in self.h])
        if self.A_st:
            slenderness = a / self.rho_st
            self.sigma_column = buckling.johnson_stress(self.m["Fty"], self.m["E"], slenderness)
        self.qT = self.T / (2 * self.w * self.h)
        self.q_w = self.V / (2 * self.h) + self.qT

    # --- spar web: closed-form minimum thickness at each station ---
    def web_t(self, idx):
        """Least spar-web thickness [m] of a region (max over its stations of yield, ultimate, buckling)."""
        m, FS = self.m, self.FS
        q = self.q_w[idx]
        bs = np.minimum(self.a, self.h[idx])
        t_yield = q / (m["Fty"] / math.sqrt(3))
        t_ultimate = FS * q / m["Fsu"]
        t = np.maximum.reduce([np.full_like(q, self.t_min), t_yield, t_ultimate])
        if self.buckling:
            t = np.maximum(t, np.cbrt(FS * q * bs ** 2 / (self.k_s_web[idx] * self.Dp)))
        return float(np.max(t))

    def web_ms(self, idx, t_w):
        """Spar-web margins {mode: MS array} of a region for web thickness t_w [m]."""
        m, FS = self.m, self.FS
        tau = self.q_w[idx] / t_w
        bs = np.minimum(self.a, self.h[idx])
        ms = {"web yield (limit)": _ms(m["Fty"] / math.sqrt(3), tau, 1.0),
              "web ultimate shear": _ms(m["Fsu"], tau, FS)}
        if self.buckling:
            ms["web shear buckling"] = _ms(self.k_s_web[idx] * self.Dp * (t_w / bs) ** 2, tau, FS)
        return ms

    # --- skin ---
    def skin_ms(self, idx, t_s, t_w):
        """Skin and stringer margins {mode: MS array} of a region for skin/web thicknesses t_s, t_w [m]."""
        m, FS = self.m, self.FS
        h, w = self.h[idx], self.w[idx]
        A_eq = w * t_s + self.n_st[idx] * (self.A_st or 0.0)
        I = 2 * A_eq * (h / 2) ** 2 + 2 * t_w * h ** 3 / 12
        sig = self.M[idx] * (h / 2) / I
        tau = self.qT[idx] / t_s
        vm = np.sqrt(sig ** 2 + 3 * tau ** 2)
        ms = {"skin yield (limit)": _ms(m["Fty"], vm, 1.0), "skin ultimate": _ms(m["Ftu"], vm, FS)}
        if self.buckling:
            bp = self.b_p[idx]
            s_cr = self.k_c[idx] * self.Dp * (t_s / bp) ** 2
            if np.any(tau > 0):
                t_cr = self.k_s_skin[idx] * self.Dp * (t_s / np.minimum(bp, self.a)) ** 2
                Rc, Rs = FS * sig / s_cr, FS * tau / t_cr
                ms["skin panel buckling"] = np.array([buckling.ms_compression_shear(rc, rs) if rc > 0 or rs > 0
                                                      else np.inf for rc, rs in zip(Rc, Rs, strict=True)])
            else:
                ms["skin panel buckling"] = _ms(s_cr, sig, FS)
            if self.A_st:
                ms["stringer column buckling"] = np.where(self.n_st[idx] > 0, _ms(self.sigma_column, sig, FS), np.inf)
        return ms

    def skin_t(self, idx, t_w):
        """Least skin thickness [m] of a region with all skin margins ≥ 0 (bracketing + brentq)."""
        f = lambda t: min(float(np.min(v)) for v in self.skin_ms(idx, t, t_w).values())
        lo = self.t_min
        if f(lo) >= 0:
            return lo
        hi = 2 * lo
        while f(hi) < 0:
            hi *= 2
            if hi > 1.0:
                raise ValueError("skin thickness exceeds 1 m: inconsistent loads/geometry")
        return optimize.brentq(f, lo, hi, xtol=1e-14, rtol=1e-13, maxiter=300)

    def mass(self, t_s, t_w):
        """Whole-wing mass [kg] and item breakdown (both half wings)."""
        rho = self.m["rho"]
        items = {"skin": 0.0, "spar webs": 0.0, "stringers": 0.0, "ribs": 0.0}
        tr = lambda f, y: float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(y)))
        for j, idx in enumerate(self.region):
            y = self.y[idx]
            items["skin"] += 2 * rho * tr(2 * self.w[idx] * t_s[j], y)
            items["spar webs"] += 2 * rho * tr(2 * self.h[idx] * t_w[j], y)
            if self.A_st:
                items["stringers"] += 2 * rho * tr(2 * self.n_st[idx] * self.A_st, y)
        if self.t_r:
            items["ribs"] = 2 * rho * self.t_r * self.f_r * tr(self.w * self.h, self.y) / self.a
        return sum(items.values()), items

    def solve_inner(self):
        """Exact inner problem: per-region web thickness (closed form), then skin thickness (root)."""
        t_s, t_w = [], []
        for idx in self.region:
            tw = self.web_t(idx)
            t_w.append(tw)
            t_s.append(self.skin_t(idx, tw))
        return np.array(t_s), np.array(t_w)

    def all_ms(self, t_s, t_w):
        """Per-region {mode: minimum MS over the region's stations}."""
        result = []
        for j, idx in enumerate(self.region):
            ms = {**self.skin_ms(idx, t_s[j], t_w[j]), **self.web_ms(idx, t_w[j])}
            result.append({k: float(np.min(v)) for k, v in ms.items()})
        return result


@cite("bruhn_1973", note="shear flow in spar webs, skin-panel compression/shear buckling interaction "
                         "R_c + R_s² = 1, Johnson column; plate coefficients from NACA TN 3781 via "
                         "aerokit.structures.buckling")
@cite("megson_2017", note="Bredt-Batho torsion of a closed single-cell box")
def wing_box_optimize(W: float, n_limit: float, b: float, c_root: float, c_uc: float, t_c: float,
                      material: Mapping[str, Any], FS: float = 1.5, n_region: int = 6, h_ratio: float = 0.85,
                      box_ratio: float = 0.5, stringer_A: float | None = 40e-6, stringer_rho: float = 6e-3,
                      t_rib: float = 1.0e-3, rib_fraction: float = 0.5, t_min: float = 0.5e-3,
                      b_s_interval: tuple[float, float] = (0.04, 0.4), a_interval: tuple[float, float] = (0.1, 1.5),
                      h_ratio_variable: bool = False, h_ratio_interval: tuple[float, float] = (0.5, 0.9),
                      include_buckling: bool = True, torsion: Callable[[float], float] | None = None,
                      distribution: str = "schrenk", n_point: int = 401, method: str = "nested",
                      raymer: dict[str, float] | None = None, grid: int = 6) -> dict[str, Any]:
    """Minimum-mass sizing of a wing box (single-cell rectangular box, half span split into ``n_region`` regions).

    Parameters
    ----------
    W : float
        Aircraft weight [N].
    n_limit : float
        Limit load factor [-]; ultimate = FS × limit.
    b : float
        Wing span [m].
    c_root, c_uc : float
        Root and tip chord [m].
    t_c : float
        Thickness-to-chord ratio [-].
    material : mapping
        Isotropic metal record (``aerokit.materials.library.find``) with ``E``, ``Fty``, ``Ftu``, ``Fsu`` [Pa],
        ``nu`` [-], ``rho`` [kg/m³].
    FS : float
        Factor of safety (ultimate/limit) [-].
    n_region : int
        Number of spanwise regions (each with its own skin and web thickness).
    h_ratio : float
        Box height h = h_ratio·(t/c)·c (fixed unless ``h_ratio_variable``).
    box_ratio : float
        Box width w = box_ratio·c.
    stringer_A : float or None
        Stringer area [m²] (fixed input, ASSUMPTION); None/0 → no stringers.
    stringer_rho : float
        Stringer radius of gyration [m] (column length = rib pitch a).
    t_rib : float
        Rib thickness [m]; 0 → ribs not counted.
    rib_fraction : float
        Solid fraction of a rib (lightening-hole allowance, ASSUMPTION).
    t_min : float
        Minimum skin/web thickness [m].
    b_s_interval, a_interval : tuple of float
        Bounds of stringer pitch b_s and rib pitch a [m].
    h_ratio_variable : bool
        Treat h_ratio as a variable on ``h_ratio_interval``.
    include_buckling : bool
        Include skin-panel, stringer-column and web-shear buckling constraints.
    torsion : callable, optional
        Limit torsion moment T(y) [N·m] (carried by Bredt shear flow).
    distribution : str
        Spanwise lift distribution passed to :func:`aerokit.aero.wing.span_loads`.
    n_point : int
        Number of span stations (rounded up to a multiple of ``n_region`` plus one).
    method : {"nested", "slsqp"}
        ``"nested"``: grid + Nelder–Mead over the pitch variables; for each pitch the thicknesses are exact
        (margins monotone → web closed form, skin brentq). ``"slsqp"``: start from the nested solution and solve
        all variables together with SLSQP (cross-check).
    raymer : mapping, optional
        Raymer wing-weight inputs for the sanity comparison (see ``structural_sizing.wing_mass_estimated``).
    grid : int
        Grid points per pitch variable for the start of the outer search.

    Returns
    -------
    dict
        ``mass`` [kg]; ``items`` {skin, spar webs, stringers, ribs} [kg]; ``b_s``, ``a`` [m]; ``h_ratio``;
        ``t_skin``, ``t_web`` per region [m]; ``regions`` list of {``y0``, ``y1`` [m], ``t_skin``, ``t_web`` [m],
        ``MS`` {mode: MS}, ``mod_skin``, ``mod_web`` (governing modes), ``MS_min``}; ``MS_min``;
        ``active_bounds`` (e.g. ``"a_lower"``); ``comparison`` (sanity ratios to
        ``structural_sizing.wing_mass_estimated`` and optionally Raymer); ``n_stringer_root``; ``_model``
        (internal evaluator).

    Raises
    ------
    ValueError
        For a non-isotropic material record, non-positive inputs or an unknown ``method``.

    Notes
    -----
    Loads come from :func:`aerokit.aero.wing.span_loads`. Skin + stringers carry bending (stringer stress = skin
    stress), the webs carry shear (q = V/(2h)), torsion is Bredt shear flow. Constraints (MS ≥ 0 at every station
    of every region): skin yield (limit, von Mises ≤ Fty), skin ultimate (FS·σ_vm ≤ Ftu), skin panel buckling
    (ultimate; k from TN 3781 Eq. 20 on a × b_p; with torsion R_c + R_s² = 1), stringer column buckling
    (ultimate; Johnson/Euler, Le = a, ρ = stringer_rho), web yield (limit, τ ≤ Fty/√3), web ultimate shear
    (FS·τ ≤ Fsu), web shear buckling (ultimate; k_s = 5.35 + 4(b/a)², b = min(a, h)).
    Mass: skin + webs + stringers + ribs (ρ·t_rib·rib_fraction·w·h per rib).
    """
    for key in ("E", "nu", "rho", "Fty", "Ftu", "Fsu"):
        if key not in material:
            raise ValueError(f"material record has no {key} (an isotropic metal is required)")
    if min(W, n_limit, b, c_root, c_uc, t_c, FS) <= 0 or n_region < 1:
        raise ValueError("inputs must be positive")
    box = _WingBox(W, n_limit, b, c_root, c_uc, t_c, material, FS, n_region, box_ratio, stringer_A,
                   stringer_rho, t_rib, rib_fraction, t_min, include_buckling, torsion, distribution, n_point)
    bounds = [b_s_interval, a_interval] + ([h_ratio_interval] if h_ratio_variable else [])
    if not stringer_A:
        bounds[0] = (b_s_interval[1], b_s_interval[1])       # no stringers: b_s has no effect
    lo = np.log([s[0] for s in bounds])
    hi = np.log([s[1] for s in bounds])

    def solve(z):
        """Nested solve at unit-cube pitch variables z → (mass, t_s, t_w, physical variables)."""
        x = np.exp(lo + np.clip(z, 0, 1) * (hi - lo))
        box.configure(x[0], x[1], x[2] if h_ratio_variable else h_ratio)
        t_s, t_w = box.solve_inner()
        return box.mass(t_s, t_w)[0], t_s, t_w, x

    objective = lambda z: solve(z)[0]
    d = len(bounds)
    grid1 = np.linspace(0, 1, grid)
    candidates = np.array(np.meshgrid(*[grid1] * d, indexing="ij")).reshape(d, -1).T
    values = np.array([objective(z) for z in candidates])
    z0 = candidates[int(np.argmin(values))]
    # if the pitch variables have no effect (buckling, stringers, ribs and h variable all off) skip the outer search
    inactive = not (include_buckling or stringer_A or t_rib or h_ratio_variable)
    if inactive:
        z_best = z0
    else:
        r = optimize.minimize(objective, z0, method="Nelder-Mead", bounds=[(0, 1)] * d,
                              options={"xatol": 1e-7, "fatol": 1e-10 * values.min(), "maxiter": 2000})
        z_best = r.x if r.fun <= values.min() else z0
    mass, t_s, t_w, x = solve(z_best)
    b_s, a = x[0], x[1]
    h_o = x[2] if h_ratio_variable else h_ratio
    if method == "slsqp":
        t_s, t_w, b_s, a, mass = _wing_slsqp(box, t_s, t_w, b_s, a, h_o, bounds[:2], t_min)
        box.configure(b_s, a, h_o)
    elif method != "nested":
        raise ValueError("method must be 'nested' or 'slsqp'")
    mass, item = box.mass(t_s, t_w)
    ms = box.all_ms(t_s, t_w)
    regions = []
    for j, idx in enumerate(box.region):
        mj = ms[j]
        skin = {k: v for k, v in mj.items() if k.startswith(("skin", "stringer"))}
        web = {k: v for k, v in mj.items() if k.startswith("web")}
        mod_s = min(skin, key=lambda k: skin[k])
        mod_w = min(web, key=lambda k: web[k])
        if t_s[j] <= t_min * (1 + 1e-9) and skin[mod_s] > 1e-6:
            mod_s = "minimum thickness (t_min)"
        if t_w[j] <= t_min * (1 + 1e-9) and web[mod_w] > 1e-6:
            mod_w = "minimum thickness (t_min)"
        regions.append({"y0": float(box.y[idx[0]]), "y1": float(box.y[idx[-1]]), "t_skin": float(t_s[j]),
                        "t_web": float(t_w[j]), "MS": mj, "mod_skin": mod_s, "mod_web": mod_w,
                        "MS_min": min(mj.values())})
    active_limit = []
    for name, value, (s_lo, s_hi) in zip(("b_s", "a", "h_ratio"), (b_s, a, h_o), bounds, strict=False):
        if s_hi > s_lo and value <= s_lo * (1 + 1e-4):
            active_limit.append(name + "_lower")
        if s_hi > s_lo and value >= s_hi * (1 - 1e-4):
            active_limit.append(name + "_upper")
    # sanity comparisons (not verification)
    est = structural_sizing.wing_mass_estimated(W, n_limit, b, c_root, c_uc, t_c, material["rho"], material["Ftu"],
                                                material["Fsu"], FS=FS, h_ratio=h_o, box_ratio=box_ratio, t_min=t_min,
                                                distribution=distribution, raymer=raymer)
    comparison = {"wing_mass_estimated": est["primary"], "ratio_estimate": mass / est["primary"]}
    if raymer is not None:
        comparison["raymer"] = est["raymer"]
        comparison["ratio_raymer"] = mass / est["raymer"]
    return {"mass": mass, "items": item, "b_s": b_s, "a": a, "h_ratio": h_o, "t_skin": t_s, "t_web": t_w,
            "regions": regions, "MS_min": min(bg["MS_min"] for bg in regions), "active_bounds": active_limit,
            "comparison": comparison, "n_stringer_root": float(box.n_st[0]), "_model": box}


def _wing_slsqp(box, t_s0, t_w0, b_s0, a0, h_o, bounds, t_min):
    """All variables together (t_s_j, t_w_j, b_s, a) with SLSQP; scaled by the start values."""
    n = box.n_region
    x0 = np.concatenate([t_s0, t_w0, [b_s0, a0]])
    scale = x0.copy()

    def unscale(z):
        """Scaled → (t_s, t_w, b_s, a)."""
        x = z * scale
        return x[:n], x[n:2 * n], x[2 * n], x[2 * n + 1]

    def mass(z):
        """Wing mass [kg] at scaled z."""
        t_s, t_w, b_s, a = unscale(z)
        box.configure(b_s, a, h_o)
        return box.mass(t_s, t_w)[0]
    m0 = mass(np.ones_like(x0))

    def constraint(z):
        """All finite station margins (capped at 10), ≥ 0 required."""
        t_s, t_w, b_s, a = unscale(z)
        box.configure(b_s, a, h_o)
        v = []
        for j, idx in enumerate(box.region):
            ms = {**box.skin_ms(idx, t_s[j], t_w[j]), **box.web_ms(idx, t_w[j])}
            for arr in ms.values():
                arr = np.asarray(arr, float)
                v.append(np.minimum(arr[np.isfinite(arr)], 10.0))
        return np.concatenate(v)
    var_bounds = ([(t_min / t, 10.0) for t in scale[:2 * n]] + [(bounds[0][0] / b_s0, bounds[0][1] / b_s0),
                                                              (bounds[1][0] / a0, bounds[1][1] / a0)])
    z0 = np.ones_like(x0) * 1.02
    z0 = np.clip(z0, [s[0] for s in var_bounds], [s[1] for s in var_bounds])
    r = optimize.minimize(lambda z: mass(z) / m0, z0, method="SLSQP", bounds=var_bounds,
                          constraints=[{"type": "ineq", "fun": constraint}],
                          options={"ftol": 1e-12, "maxiter": 500, "eps": 1e-8})
    t_s, t_w, b_s, a = unscale(r.x)
    box.configure(b_s, a, h_o)
    return t_s, t_w, b_s, a, box.mass(t_s, t_w)[0]


# ---------------------------------------------------------------------------
# (c) Tube / strut
# ---------------------------------------------------------------------------
@cite("nasa_sp8007", note="axial buckling of thin cylinders with knock-down factor γ, via "
                          "aerokit.structures.buckling.cylinder_axial")
def tube_margins(D: float, t: float, M: float = 0.0, T: float = 0.0, P_start: float = 0.0, L: float | None = None,
                 K: float = 1.0, E: float = 70e9, nu: float = 0.33, sigma_y: float | None = None, FS: float = 1.5,
                 local: bool = True, gamma: float | None = None) -> dict[str, float]:
    """Margins of :func:`aerokit.structures.structural_sizing.tube_check` plus thin-wall local buckling.

    Parameters
    ----------
    D, t : float
        Outer diameter and wall thickness [m].
    M, T : float
        Bending and torsion moments [N·m].
    P_start : float
        Axial compressive load [N] (positive = compression).
    L : float, optional
        Column length [m] (needed for column buckling).
    K : float
        Effective-length factor [-].
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    sigma_y : float, optional
        Yield stress [Pa].
    FS : float
        Factor of safety [-].
    local : bool
        Include local (shell) buckling.
    gamma : float, optional
        Knock-down factor; default the SP-8007 axial reduction.

    Returns
    -------
    dict
        ``von Mises``, optionally ``column`` and ``local buckling`` margins MS [-].

    Notes
    -----
    Local: σ_comp = |M|·c/I + P/A ≤ γ·E/√(3(1−ν²))·t/r with r = (D − t)/2 the mid-surface radius;
    MS = σ_cr/(FS·σ_comp) − 1.
    """
    k = structural_sizing.tube_check(D, t, M, T, P_start, L, K, E, sigma_y, FS)
    ms = {"von Mises": k["MS_vm"]}
    if "MS_column" in k:
        ms["column"] = k["MS_column"]
    if local and (M or P_start > 0):
        r = (D - t) / 2
        s_cr = buckling.cylinder_axial(E, nu, r, t, gamma)
        section = beam.tube(D, t)
        sig_comp = abs(M) * (D / 2) / section["I"] + max(P_start, 0.0) / section["A"]
        ms["local buckling"] = beam.safety_margin(s_cr, sig_comp, FS)
    return ms


@cite("nasa_sp8007", note="validity limit r/t < 1500 of the axial-buckling knock-down")
def tube_optimize(M: float = 0.0, T: float = 0.0, P_start: float = 0.0, L: float | None = None, K: float = 1.0,
                  E: float = 70e9, nu: float = 0.33, sigma_y: float | None = None, rho: float = 2810.0,
                  FS: float = 1.5, D_interval: tuple[float, float] = (2e-3, 0.5), t_min: float = 0.3e-3,
                  local: bool = True, gamma: float | None = None, initial: tuple[float, float] | None = None,
                  rtol_active: float = 1e-5) -> dict[str, Any]:
    """Least cross-section-area (least mass) tube; variables (ln D, ln t), multi-start SLSQP.

    Parameters
    ----------
    M, T, P_start, L, K, E, nu, sigma_y, FS, local, gamma
        As in :func:`tube_margins`.
    rho : float
        Density [kg/m³] (for mass per length).
    D_interval : tuple of float
        Outer-diameter bounds [m].
    t_min : float
        Minimum wall thickness [m].
    initial : tuple of float, optional
        Extra start (D, t) [m].
    rtol_active : float
        A margin is reported active when |MS| ≤ 10·rtol_active.

    Returns
    -------
    dict
        ``D``, ``t`` [m], ``D_t``, ``A`` [m²], ``mass_length`` [kg/m], ``MS`` (see :func:`tube_margins`),
        ``active`` (margins plus ``t_min``, ``D_max``, ``D_min``), ``MS_min``.

    Raises
    ------
    ValueError
        If ``sigma_y`` is missing, ``L`` is missing under compression, or no feasible tube is found.

    Notes
    -----
    Constraints: tube margins ≥ 0 (von Mises, Euler/Johnson column, local buckling), t ≥ t_min, D in
    ``D_interval``, D/t ≥ 2.2 (tube_check requires 2t ≤ D) and r/t < 1500 (SP-8007 validity).
    Starts: 5 diameters × D/t ∈ {10, 40, 150}; the best feasible SLSQP result is kept.
    """
    if sigma_y is None or sigma_y <= 0:
        raise ValueError("sigma_y must be given")
    if P_start > 0 and L is None:
        raise ValueError("L must be given for a compressive load")

    def area(D, t):
        """Annulus area [m²]."""
        return math.pi / 4 * (D ** 2 - (D - 2 * t) ** 2)

    def ms_vec(x):
        """Margins at x = (ln D, ln t); −1 outside the geometric validity range."""
        D, t = np.exp(x)
        if not (2.2 * t <= D and (D - t) / (2 * t) < 1490):
            return np.array([-1.0])
        return np.array(list(tube_margins(D, t, M, T, P_start, L, K, E, nu, sigma_y, FS, local, gamma).values()))

    constraints = [{"type": "ineq", "fun": lambda x: np.minimum(ms_vec(x), 5.0)},
                   {"type": "ineq", "fun": lambda x: x[0] - x[1] - math.log(2.2)},
                   {"type": "ineq", "fun": lambda x: math.log(1400.0) - (x[0] - x[1])}]
    var_bounds = [(math.log(D_interval[0]), math.log(D_interval[1])),
                  (math.log(t_min), math.log(D_interval[1] / 2.2))]
    A_ref = area(0.05, 1e-3)
    best = None
    starts = [initial] if initial is not None else []
    for D0 in np.geomspace(D_interval[0] * 2, D_interval[1] / 1.5, 5):
        for Dt in (10.0, 40.0, 150.0):
            starts.append((D0, max(D0 / Dt, t_min * 1.01)))
    for D0, t0 in starts:
        x0 = np.log([D0, t0])
        try:
            with warnings.catch_warnings():       # SLSQP bound-clipping warning (harmless)
                warnings.simplefilter("ignore", RuntimeWarning)
                r = optimize.minimize(lambda x: area(*np.exp(x)) / A_ref, x0, method="SLSQP", bounds=var_bounds,
                                      constraints=constraints, options={"ftol": 1e-14, "maxiter": 500})
        except (ValueError, ZeroDivisionError):
            continue
        if np.min(ms_vec(r.x)) < -1e-7:
            continue
        if best is None or r.fun < best.fun:
            best = r
    if best is None:
        raise ValueError("no feasible tube found (widen the D interval)")
    D, t = np.exp(best.x)
    ms = tube_margins(D, t, M, T, P_start, L, K, E, nu, sigma_y, FS, local, gamma)
    active = [k for k, v in ms.items() if abs(v) <= rtol_active * 10]
    if t <= t_min * (1 + 1e-6):
        active.append("t_min")
    if D_interval[1] * (1 - 1e-6) <= D:
        active.append("D_max")
    if D_interval[0] * (1 + 1e-6) >= D:
        active.append("D_min")
    A = area(D, t)
    return {"D": D, "t": t, "D_t": D / t, "A": A, "mass_length": rho * A, "MS": ms, "active": active,
            "MS_min": min(ms.values())}


@cite("timoshenko_gere_1961", note="Euler column load and classical axial buckling stress of a thin cylinder")
@cite("shanley_1960", note="optimum strut proportions; the closed form here is derived, Shanley not read")
def tube_euler_closed(P: float, L: float, E: float, nu: float, gamma: float, K: float = 1.0,
                      FS: float = 1.5) -> dict[str, float]:
    """Least-area thin tube under pure axial compression with Euler and local buckling simultaneously active.

    Parameters
    ----------
    P : float
        Axial compressive load [N].
    L : float
        Length [m].
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    gamma : float
        Local-buckling knock-down factor [-].
    K : float
        Effective-length factor [-].
    FS : float
        Factor of safety [-].

    Returns
    -------
    dict
        ``t`` [m], mid-surface radius ``r`` [m], outer diameter ``D`` = 2r + t [m], ``D_t`` (outer diameter / t),
        ``A`` [m²].

    Notes
    -----
    Thin wall with mid-surface radius r: A = 2πrt, I = πr³t.
    Euler: FS·P = π²E·πr³t/(KL)²; local: FS·P = A·c·E·t/r = 2π·c·E·t², c = γ/√(3(1−ν²)).
    A = 2π·t·(FS·P·(KL)²/(π³Et))^(1/3) increases with t → the local constraint is active (smallest t);
    r then follows from Euler.
    """
    c = gamma / math.sqrt(3 * (1 - nu ** 2))
    Pd = FS * P
    t = math.sqrt(Pd / (2 * math.pi * c * E))
    r = (Pd * (K * L) ** 2 / (math.pi ** 3 * E * t)) ** (1 / 3)
    return {"t": t, "r": r, "D": 2 * r + t, "D_t": (2 * r + t) / t, "A": 2 * math.pi * r * t}


# ---------------------------------------------------------------------------
# (d) General tools
# ---------------------------------------------------------------------------
@cite("mckay_1979", note="Latin hypercube sampling (method='lhs', via scipy.stats.qmc)")
def parametric_scan(f: Callable[..., Any], variables: Mapping[str, Any], method: str = "grid", n: int = 5,
                    seed: int = 0) -> dict[str, Any]:
    """N-variable scan of a function on a full grid or a Latin hypercube.

    Parameters
    ----------
    f : callable
        ``f(**point)`` returning a scalar or {name: scalar}.
    variables : mapping
        {name: (lower, upper)} or, for the grid only, {name: [values]}.
    method : {"grid", "lhs"}
        ``"grid"``: n equally spaced points per variable (or the given list), full tensor product.
        ``"lhs"``: n-point Latin hypercube (``scipy.stats.qmc.LatinHypercube``, reproducible with ``seed``).
    n : int
        Points per variable (grid) or number of samples (lhs).
    seed : int
        Random seed of the Latin hypercube.

    Returns
    -------
    dict
        ``X`` (N×d points), ``names`` (variable order), ``Y`` (array, or {name: array} for dict outputs).

    Raises
    ------
    ValueError
        For an unknown ``method``.

    Examples
    --------
    >>> parametric_scan(lambda x: 2 * x, {"x": (0.0, 1.0)}, n=3)["Y"]
    array([0., 1., 2.])
    """
    names = list(variables)
    if method == "grid":
        axis = []
        for name in names:
            v = variables[name]
            axis.append(np.linspace(v[0], v[1], n) if isinstance(v, tuple) else np.asarray(v, float))
        X = np.array(np.meshgrid(*axis, indexing="ij")).reshape(len(names), -1).T
    elif method == "lhs":
        from scipy.stats import qmc
        sample = qmc.LatinHypercube(d=len(names), seed=seed).random(n)
        lower = np.array([variables[a][0] for a in names], float)
        upper = np.array([variables[a][1] for a in names], float)
        X = lower + sample * (upper - lower)
    else:
        raise ValueError("method must be 'grid' or 'lhs'")
    results = [f(**dict(zip(names, x, strict=True))) for x in X]
    Y: dict[str, np.ndarray] | np.ndarray
    if results and isinstance(results[0], dict):
        Y = {k: np.array([s[k] for s in results]) for k in results[0]}
    else:
        Y = np.array(results, float)
    return {"X": X, "names": names, "Y": Y}


def _oriented(F: ArrayLike, maximize: ArrayLike | None) -> np.ndarray:
    """Objective matrix with maximized columns negated (so that all are minimized)."""
    arr = np.atleast_2d(np.asarray(F, float))
    if maximize is not None:
        arr = arr * np.where(np.asarray(maximize, bool), -1.0, 1.0)
    return arr


def _dominance(F: np.ndarray) -> np.ndarray:
    """Matrix D[p, q] = point p dominates point q (≤ in every objective and < in at least one)."""
    weak = np.all(F[:, None, :] <= F[None, :, :], axis=2)
    strict = np.any(F[:, None, :] < F[None, :, :], axis=2)
    return weak & strict


def pareto_front(F: ArrayLike, maximize: ArrayLike | None = None) -> np.ndarray:
    """Indices of the non-dominated points.

    Parameters
    ----------
    F : array_like, shape (N, k)
        Objective values.
    maximize : array_like of bool, optional
        ``maximize[i] = True`` → objective i is maximized (default: all minimized).

    Returns
    -------
    ndarray of int
        Indices of the Pareto front.

    Notes
    -----
    p dominates q ⇔ p ≤ q in every objective and < in at least one. Identical points do not dominate each other.

    Examples
    --------
    >>> pareto_front([[1, 2], [2, 1], [2, 2]])
    array([0, 1])
    """
    dominates = _dominance(_oriented(F, maximize))           # [p, q]: p dominates q
    return np.nonzero(~dominates.any(axis=0))[0]


@cite("deb_2002", note="fast non-dominated sorting (NSGA-II); standard algorithm, paper not read")
def pareto_ranks(F: ArrayLike, maximize: ArrayLike | None = None) -> np.ndarray:
    """Front number of every point by fast non-dominated sorting (0 = Pareto front).

    Parameters
    ----------
    F : array_like, shape (N, k)
        Objective values.
    maximize : array_like of bool, optional
        As in :func:`pareto_front`.

    Returns
    -------
    ndarray of int, shape (N,)
        Rank (front index) of each point.

    Notes
    -----
    Count, for each point, how many points dominate it; points with count 0 form the current front; removing
    them decrements the counts of the points they dominate; repeat.
    """
    F = _oriented(F, maximize)
    n = len(F)
    B = _dominance(F)
    counter = B.sum(axis=0)                              # number of points dominating q
    order = np.full(n, -1)
    front = np.nonzero(counter == 0)[0]
    k = 0
    while len(front):
        order[front] = k
        for p in front:
            counter[B[p]] -= 1
        counter[front] = -1
        front = np.nonzero(counter == 0)[0]
        k += 1
    return order


def sensitivity(f: Callable[[np.ndarray], Any], x0: ArrayLike, h: float = 1e-5,
                keys: Sequence[str] | None = None) -> np.ndarray | dict[Any, np.ndarray]:
    """Elasticities e_i = ∂ln f/∂ln x_i by central differences with log-space step h.

    Parameters
    ----------
    f : callable
        ``f(x)`` returning a scalar or a dict of scalars.
    x0 : array_like
        Point of evaluation.
    h : float
        Step in ln x_i.
    keys : sequence of str, optional
        Dict keys to differentiate (default: all).

    Returns
    -------
    ndarray or dict
        Elasticities (scalar f) or {key: elasticities}.

    Notes
    -----
    If f ≤ 0 at a perturbed point the elasticity (x_i/f)·∂f/∂x_i is used instead (relative step); components
    with x_i = 0 are set to 0.

    Examples
    --------
    >>> float(round(sensitivity(lambda x: x[0] ** 3, [2.0])[0], 8))
    3.0
    """
    x0 = np.asarray(x0, float)
    f0 = f(x0)
    is_dict = isinstance(f0, dict)
    ks = (keys or list(f0)) if is_dict else [None]
    value = lambda r, k: r[k] if is_dict else r
    e = {k: np.zeros(len(x0)) for k in ks}
    for i in range(len(x0)):
        if x0[i] != 0:
            xp, xm = x0.copy(), x0.copy()
            xp[i] *= math.exp(h)
            xm[i] *= math.exp(-h)
            fp, fm = f(xp), f(xm)
            for k in ks:
                a, b_, c = value(fp, k), value(fm, k), value(f0, k)
                if a > 0 and b_ > 0:
                    e[k][i] = (math.log(a) - math.log(b_)) / (2 * h)
                else:
                    dx = x0[i] * (math.exp(h) - math.exp(-h))
                    e[k][i] = (a - b_) / dx * x0[i] / c
        else:
            for k in ks:
                e[k][i] = 0.0
    return e if is_dict else e[None]


# --- reliability ---
def distribution(kind: str, mean: float, std: float) -> dict[str, Any]:
    """Random-variable definition from its own mean and standard deviation.

    Parameters
    ----------
    kind : {"normal", "lognormal", "gumbel"}
        Distribution type (Gumbel = largest-value type I).
    mean : float
        Mean of the variable (> 0 for lognormal).
    std : float
        Standard deviation of the variable (> 0).

    Returns
    -------
    dict
        ``kind``, ``mean``, ``std`` and ``d`` (frozen ``scipy.stats`` distribution).

    Raises
    ------
    ValueError
        For ``std <= 0``, a non-positive lognormal mean or an unknown kind.

    Notes
    -----
    Lognormal: ζ² = ln(1 + (σ/μ)²), λ = ln μ − ζ²/2. Gumbel: scale β = σ√6/π, location μ − γ_E·β
    (γ_E = 0.5772…). (Moment relations derived; checked against scipy.)
    """
    if std <= 0:
        raise ValueError("std must be positive")
    if kind == "normal":
        d = stats.norm(loc=mean, scale=std)
    elif kind == "lognormal":
        if mean <= 0:
            raise ValueError("lognormal requires mean > 0")
        z = math.sqrt(math.log(1 + (std / mean) ** 2))
        lam = math.log(mean) - z * z / 2
        d = stats.lognorm(s=z, scale=math.exp(lam))
    elif kind == "gumbel":
        beta = std * math.sqrt(6) / math.pi
        d = stats.gumbel_r(loc=mean - np.euler_gamma * beta, scale=beta)
    else:
        raise ValueError("kind must be normal, lognormal or gumbel")
    return {"kind": kind, "mean": mean, "std": std, "d": d}


def _u_x(u: ArrayLike, distributions: Sequence[Mapping[str, Any]]) -> np.ndarray:
    """Standard normal u → physical x (independent variables, marginal iso-probabilistic transform)."""
    u = np.asarray(u, float)
    x = np.empty_like(u)
    for i, dg in enumerate(distributions):
        if dg["kind"] == "normal":
            x[..., i] = dg["mean"] + dg["std"] * u[..., i]
        elif dg["kind"] == "lognormal":            # x = exp(λ + ζu), without loss of accuracy in the tail
            x[..., i] = dg["d"].kwds["scale"] * np.exp(dg["d"].kwds["s"] * u[..., i])
        else:                                     # F_X(x) = Φ(u); right tail via sf
            x[..., i] = dg["d"].isf(stats.norm.sf(u[..., i]))
    return x


@cite("wilson_1927", note="Wilson score confidence interval of the binomial proportion P_f")
def monte_carlo_pf(g: Callable[[np.ndarray], Any], distributions: Sequence[Mapping[str, Any]], n: int = 100_000,
                   seed: int = 0, confidence: float = 0.95, vectorized: bool = True) -> dict[str, Any]:
    """Crude Monte Carlo failure probability P_f = P[g(X) ≤ 0] for independent variables.

    Parameters
    ----------
    g : callable
        Limit-state function; with ``vectorized=True`` it takes X (n×k) and returns (n,), otherwise one point.
    distributions : sequence of dict
        Outputs of :func:`distribution`.
    n : int
        Number of samples.
    seed : int
        Random seed.
    confidence : float
        Two-sided confidence level of the interval.
    vectorized : bool
        Call ``g`` once on all samples.

    Returns
    -------
    dict
        ``Pf``, ``std_error`` σ_MC = √(P_f(1 − P_f)/n), ``interval`` (Wilson score interval), ``n_failure``,
        ``n``, ``beta`` = −Φ⁻¹(P_f), ``cov`` = σ_MC/P_f.
    """
    rng = np.random.default_rng(seed)
    U = rng.standard_normal((n, len(distributions)))
    X = _u_x(U, distributions)
    G = np.asarray(g(X), float) if vectorized else np.array([g(x) for x in X])
    nf = int(np.count_nonzero(G <= 0))
    p = nf / n
    se = math.sqrt(p * (1 - p) / n)
    z = stats.norm.ppf(0.5 + confidence / 2)
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    beta = -stats.norm.ppf(p) if 0 < p < 1 else (math.inf if p == 0 else -math.inf)
    return {"Pf": p, "std_error": se, "interval": (max(0.0, center - half), min(1.0, center + half)),
            "n_failure": nf, "n": n, "beta": beta, "cov": se / p if p > 0 else math.inf}


@cite("hasofer_lind_1974", note="reliability index β = min ‖u‖ on G(u) = 0")
@cite("rackwitz_fiessler_1978", note="HL-RF iteration")
def form(g: Callable[[np.ndarray], Any], distributions: Sequence[Mapping[str, Any]], u0: ArrayLike | None = None,
         tol: float = 1e-9, maxit: int = 200, h: float = 1e-6) -> dict[str, Any]:
    """First-order reliability method (FORM) with the HL-RF iteration.

    Parameters
    ----------
    g : callable
        Limit-state function g(x) (failure for g ≤ 0); x has the variables in the last axis.
    distributions : sequence of dict
        Outputs of :func:`distribution` (independent variables).
    u0 : array_like, optional
        Start point in standard normal space (default origin).
    tol : float
        Convergence tolerance on the step ‖u_{k+1} − u_k‖.
    maxit : int
        Maximum number of iterations.
    h : float
        Central-difference step for ∇G in u-space.

    Returns
    -------
    dict
        ``beta`` (signed: negative if g(mean point) ≤ 0), ``Pf`` ≈ Φ(−β), ``u`` and ``x`` design point,
        ``alpha`` = −u*/β (sensitivities), ``iteration``, ``converged``.

    Raises
    ------
    ValueError
        If ∇G = 0.

    Notes
    -----
    β = min ‖u‖ s.t. G(u) = 0; u_{k+1} = [(∇G·u_k − G(u_k))/‖∇G‖²]·∇G. Non-normal variables are mapped to u-space
    by the marginal iso-probabilistic transform (identical at the design point to the Rackwitz–Fiessler
    equivalent-normal approximation). Converged when the step is below ``tol`` and |G| ≤ 1e-8·|G(0)|.
    """
    k = len(distributions)
    G = lambda u: float(g(_u_x(np.asarray(u, float), distributions)))
    u = np.zeros(k) if u0 is None else np.asarray(u0, float)
    G0 = G(np.zeros(k))
    scale = abs(G0) if G0 != 0 else 1.0
    converged = False
    iterations = 0
    for _ in range(maxit):
        iterations += 1
        Gu = G(u)
        gr = np.array([(G(u + h * e) - G(u - h * e)) / (2 * h) for e in np.eye(k)])
        nn = float(gr @ gr)
        if nn == 0:
            raise ValueError("∇G = 0: FORM cannot proceed")
        u_new = (gr @ u - Gu) / nn * gr
        if np.linalg.norm(u_new - u) <= tol * max(1.0, float(np.linalg.norm(u_new))) and abs(G(u_new)) <= 1e-8 * scale:
            u = u_new
            converged = True
            break
        u = u_new
    beta = float(np.linalg.norm(u)) * (1 if G0 > 0 else -1)
    alpha = -u / np.linalg.norm(u) if np.linalg.norm(u) > 0 else np.zeros(k)
    return {"beta": beta, "Pf": float(stats.norm.cdf(-beta)), "u": u, "x": _u_x(u, distributions), "alpha": alpha,
            "iteration": iterations, "converged": converged}


def pf_strength_load(R: Mapping[str, Any], S: Mapping[str, Any]) -> float:
    """Exact P_f = P[R ≤ S] = ∫ F_R(s)·f_S(s) ds for independent strength R and load S (numerical quadrature).

    Parameters
    ----------
    R, S : dict
        Outputs of :func:`distribution`.

    Returns
    -------
    float
        Failure probability.
    """
    dR, dS = R["d"], S["d"]
    lo, hi = dS.ppf(1e-14), dS.ppf(1 - 1e-14)
    v, _ = integrate.quad(lambda s: dR.cdf(s) * dS.pdf(s), lo, hi, limit=400, epsabs=0, epsrel=1e-11,
                          points=[R["mean"], S["mean"]] if lo < R["mean"] < hi else [S["mean"]])
    return v
