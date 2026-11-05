"""Mechanically fastened (bolted / riveted) joints: shear, bearing, net section, edge tear-out,
eccentrically loaded bolt group, load distribution with flexible fasteners, preload and joint stiffness,
NASA-STD-5020B interaction and separation margins.

Sources (read in this session):

- NASA-STD-5020B (2021): Eqs. (8)-(13) p. 28, (19)-(22) pp. 32-33.
- Swift flexibility formula: de Sá Martins et al., ICAS 2018-0659, Eq. (2) (attributed to Swift).
- Huth constants a, b: Altair Inspire "Connection Stiffness" glossary page (table). The form of the Huth
  expression is inconsistent between sources (ICAS 2018 Eq. 4 does not show the exponent); the common form
  with the exponent is used here.
- Frustum member stiffness and the Wileman relation: Roymech "Joint Stiffness" page (numerical example);
  the Shigley form of the equations was not read from the book in this session.

All functions work in N, m, Pa.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.references import cite
from aerokit.structures.beam import safety_margin


# ---------------------------------------------------------------------------
# Single-fastener strengths
# ---------------------------------------------------------------------------
@cite("nasa_std5020b_2021", note="Eq. (12), per shear plane")
def shear_strength(d: float, Fsu: float, shear_plane: int = 1) -> float:
    """Fastener shear strength ``P_su = n π d² F_su / 4``.

    Parameters
    ----------
    d : float
        Shank diameter [m].
    Fsu : float
        Ultimate shear strength [Pa].
    shear_plane : int
        Number of shear planes (1 single shear, 2 double shear).

    Returns
    -------
    float
        Shear strength [N].

    Raises
    ------
    ValueError
        If d or Fsu is not positive or ``shear_plane < 1``.
    """
    if d <= 0 or Fsu <= 0 or shear_plane < 1:
        raise ValueError("d and F_su must be positive and the number of shear planes ≥ 1")
    return shear_plane * math.pi * d ** 2 / 4 * Fsu


@cite("bruhn_1973", note="bearing on projected area")
def bearing_strength(d: float, t: float, Fbru: float) -> float:
    """Hole bearing strength ``P_br = d t F_bru`` (projected area).

    Parameters
    ----------
    d : float
        Hole / fastener diameter [m].
    t : float
        Sheet thickness [m].
    Fbru : float
        Ultimate bearing strength [Pa].

    Returns
    -------
    float
        Bearing strength [N].

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    if min(d, t, Fbru) <= 0:
        raise ValueError("d, t and F_bru must be positive")
    return d * t * Fbru


def net_section_strength(w: float, t: float, d: float, n_holes: int, Ftu: float) -> float:
    """Net-section tension strength ``P = (w − n d) t F_tu`` across a row of holes (no Kt).

    Parameters
    ----------
    w : float
        Gross width [m].
    t : float
        Thickness [m].
    d : float
        Hole diameter [m].
    n_holes : int
        Number of holes in the row.
    Ftu : float
        Ultimate tensile strength [Pa].

    Returns
    -------
    float
        Net-section strength [N].

    Raises
    ------
    ValueError
        If the net width, t or Ftu is not positive.
    """
    net = w - n_holes * d
    if net <= 0 or t <= 0 or Ftu <= 0:
        raise ValueError("net width, t and F_tu must be positive")
    return net * t * Ftu


def edge_tearout(e: float, d: float, t: float, Fsu: float) -> float:
    """Shear-out (edge tear-out) strength ``P = 2 (e − d/2) t F_su``.

    Parameters
    ----------
    e : float
        Distance from the hole centre to the edge [m].
    d : float
        Hole diameter [m].
    t : float
        Thickness [m].
    Fsu : float
        Ultimate shear strength [Pa].

    Returns
    -------
    float
        Tear-out strength [N].

    Raises
    ------
    ValueError
        Unless ``e > d/2`` and t, Fsu are positive.

    Notes
    -----
    Two shear planes, each of length ``e − d/2`` (common simple model; not read from a primary source in
    this session).
    """
    if e <= d / 2 or t <= 0 or Fsu <= 0:
        raise ValueError("e > d/2 is required and t, F_su must be positive")
    return 2 * (e - d / 2) * t * Fsu


def joint_margins(P: float, d: float, t: float, Fsu: float, Fbru: float, Ftu: float, w: float, e: float,
                  n_holes: int = 1, shear_plane: int = 1, FS: float = 1.0,
                  n_fasteners: int = 1) -> dict[str, Any]:
    """Margins of safety of a single-row joint for every failure mode.

    Parameters
    ----------
    P : float
        Total joint load [N]; each fastener carries ``P/n_fasteners`` (equal sharing assumed).
    d, t : float
        Fastener diameter and sheet thickness [m].
    Fsu, Fbru, Ftu : float
        Ultimate shear, bearing and tensile strength [Pa].
    w : float
        Sheet width [m].
    e : float
        Edge distance [m].
    n_holes : int
        Holes in the net-section row.
    shear_plane : int
        Shear planes per fastener.
    FS : float
        Factor of safety.
    n_fasteners : int
        Number of fasteners sharing P.

    Returns
    -------
    dict
        ``shear``, ``bearing``, ``edge_tearout``, ``net_section`` margins (``MS = allowable/(FS·applied) − 1``,
        see :func:`~aerokit.structures.beam.safety_margin`) and ``critical`` (name of the smallest).
    """
    Pe = P / n_fasteners
    allowable = {"shear": shear_strength(d, Fsu, shear_plane),
                 "bearing": bearing_strength(d, t, Fbru),
                 "edge_tearout": edge_tearout(e, d, t, Fsu)}
    ms: dict[str, Any] = {k: safety_margin(v, Pe, FS) for k, v in allowable.items()}
    ms["net_section"] = safety_margin(net_section_strength(w, t, d, n_holes, Ftu), P, FS)
    ms["critical"] = min(ms, key=lambda k: ms[k])
    return ms


# ---------------------------------------------------------------------------
# Eccentrically loaded bolt group (elastic method)
# ---------------------------------------------------------------------------
@cite("bruhn_1973", note="elastic analysis of eccentrically loaded fastener groups")
def bolt_group(positions: ArrayLike, Px: float, Py: float, M: float = 0.0,
               point: Sequence[float] | None = None, areas: ArrayLike | None = None) -> dict[str, Any]:
    """In-plane loaded fastener group, elastic method (rigid plate, stiffness proportional to area).

    Parameters
    ----------
    positions : array_like, shape (N, 2)
        Fastener coordinates (x, y) [m].
    Px, Py : float
        Force components [N].
    M : float
        Additional moment (counter-clockwise positive) [N·m].
    point : (float, float), optional
        Point of application of (Px, Py) [m]; if given its moment about the centroid is added.
    areas : array_like, optional
        Fastener areas (default all equal) [m²].

    Returns
    -------
    dict
        Per-fastener ``Fx``, ``Fy``, ``F`` (magnitude) arrays [N], ``center`` (centroid) [m],
        ``M_center`` (total moment about the centroid) [N·m], ``J_polar = Σ A r²`` [m⁴].

    Raises
    ------
    ValueError
        If positions are not N×2, an area is not positive, or a moment acts on a group concentrated at a
        single point.

    Notes
    -----
    Direct share ``F_i = P A_i/ΣA``; moment share ``F_i = M A_i r_i / Σ A_j r_j²`` perpendicular to r.
    """
    p = np.asarray(positions, float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 1:
        raise ValueError("positions must be an N×2 array")
    a = np.ones(len(p)) if areas is None else np.asarray(areas, float)
    if np.any(a <= 0):
        raise ValueError("areas must be positive")
    c = (a[:, None] * p).sum(0) / a.sum()
    Mc = M
    if point is not None:
        dx, dy = point[0] - c[0], point[1] - c[1]
        Mc += dx * Py - dy * Px
    r = p - c
    Jp = (a * (r ** 2).sum(1)).sum()
    if Mc != 0 and Jp == 0:
        raise ValueError("a group concentrated at a single point cannot carry a moment")
    Fx = Px * a / a.sum() - (Mc * a * r[:, 1] / Jp if Jp else 0)
    Fy = Py * a / a.sum() + (Mc * a * r[:, 0] / Jp if Jp else 0)
    return {"Fx": Fx, "Fy": Fy, "F": np.hypot(Fx, Fy), "center": tuple(c), "M_center": Mc, "J_polar": Jp}


# ---------------------------------------------------------------------------
# Fastener flexibility and load distribution in a single-row lap joint
# ---------------------------------------------------------------------------
@cite("swift_1971", note="via de Sá Martins et al., ICAS 2018-0659, Eq. (2)")
def swift_flexibility(d: float, Ef: float, t1: float, E1: float, t2: float, E2: float) -> float:
    """Swift (Douglas) fastener flexibility ``f = 5/(E_f d) + 0.8/(t1 E1) + 0.8/(t2 E2)``.

    Parameters
    ----------
    d : float
        Fastener diameter [m].
    Ef : float
        Fastener modulus [Pa].
    t1, E1, t2, E2 : float
        Thickness [m] and modulus [Pa] of the two sheets.

    Returns
    -------
    float
        Flexibility [m/N].

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    if min(d, Ef, t1, E1, t2, E2) <= 0:
        raise ValueError("all inputs must be positive")
    return 5 / (Ef * d) + 0.8 / (t1 * E1) + 0.8 / (t2 * E2)


HUTH_CONSTANTS = {  # (a, b) -- Altair Inspire glossary table
    "bolt_metal": (2 / 3, 3.0),
    "rivet_metal": (2 / 5, 2.2),
    "bolt_graphite": (2 / 3, 4.2),
}


@cite("huth_1986", note="constants from the Altair Inspire glossary; form NOT VERIFIED (sources disagree)")
def huth_flexibility(d: float, Ef: float, t1: float, E1: float, t2: float, E2: float, kind: str = "bolt_metal",
                     n: int = 1) -> float:
    """Huth fastener flexibility (common form).

    Parameters
    ----------
    d : float
        Fastener diameter [m].
    Ef : float
        Fastener modulus [Pa].
    t1, E1, t2, E2 : float
        Thickness [m] and modulus [Pa] of the two sheets.
    kind : {"bolt_metal", "rivet_metal", "bolt_graphite"}
        Joint type selecting (a, b) from :data:`HUTH_CONSTANTS`.
    n : {1, 2}
        1 single shear, 2 double shear.

    Returns
    -------
    float
        Flexibility C [m/N].

    Raises
    ------
    ValueError
        If an input is not positive or n is not 1 or 2.
    KeyError
        If ``kind`` is unknown.

    Notes
    -----
    ``C = ((t1 + t2)/(2d))^a · (b/n) · [1/(t1E1) + 1/(n t2E2) + 1/(2 t1 E_f) + 1/(2 n t2 E_f)]``.
    """
    if min(d, Ef, t1, E1, t2, E2) <= 0 or n not in (1, 2):
        raise ValueError("inputs must be positive and n must be 1 or 2")
    a, b = HUTH_CONSTANTS[kind]
    return ((t1 + t2) / (2 * d)) ** a * b / n * (1 / (t1 * E1) + 1 / (n * t2 * E2)
                                                 + 1 / (2 * t1 * Ef) + 1 / (2 * n * t2 * Ef))


def load_distribution(P: float, n: int, step: float, E1A1: float, E2A2: float,
                      C: float | ArrayLike) -> NDArray[Any]:
    """Fastener loads in a single-row lap joint with n fasteners (spring model).

    Parameters
    ----------
    P : float
        Joint load [N].
    n : int
        Number of fasteners.
    step : float
        Fastener pitch [m].
    E1A1, E2A2 : float
        Axial stiffness of sheets 1 and 2 [N].
    C : float or array_like
        Fastener flexibility [m/N], scalar or length n.

    Returns
    -------
    ndarray
        Fastener loads F_i [N] (ΣF = P).

    Raises
    ------
    ValueError
        For invalid sizes or a negative flexibility.

    Notes
    -----
    Sheet 1 carries P before fastener 1, sheet 2 reacts after fastener n. The relative slip at fastener i is
    ``u2_i − u1_i = C_i F_i``; compatibility:
    ``C_{i+1}F_{i+1} − C_i F_i = step·(P2_i/E2A2 − P1_i/E1A1)`` with ``P1_i = P − ΣF_≤i``, ``P2_i = ΣF_≤i``
    and ``ΣF = P``.
    """
    if n < 1 or step <= 0 or E1A1 <= 0 or E2A2 <= 0:
        raise ValueError("invalid input")
    Cv = np.full(n, float(C)) if np.isscalar(C) else np.asarray(C, float)  # type: ignore[arg-type]
    if len(Cv) != n or np.any(Cv < 0):
        raise ValueError("C must not be negative and must have length n")
    M = np.zeros((n, n))
    rhs = np.zeros(n)
    s1, s2 = step / E1A1, step / E2A2
    for i in range(n - 1):
        M[i, i + 1] += Cv[i + 1]
        M[i, i] -= Cv[i]
        M[i, : i + 1] -= s1 + s2          # s2·ΣF + s1·ΣF moved from the right-hand side
        rhs[i] = -s1 * P
    M[n - 1, :] = 1.0
    rhs[n - 1] = P
    return np.linalg.solve(M, rhs)


# ---------------------------------------------------------------------------
# Preload and joint stiffness
# ---------------------------------------------------------------------------
@cite("budynas_nisbett_2015", note="bolt stiffness; not read from the book in this session")
def bolt_stiffness(E: float, Ad: float, At: float, ld: float, lt: float) -> float:
    """Bolt axial stiffness ``k_b = Ad At E / (Ad lt + At ld)`` (shank and thread as springs in series).

    Parameters
    ----------
    E : float
        Bolt modulus [Pa].
    Ad : float
        Major-diameter (shank) area [m²].
    At : float
        Tensile-stress area [m²].
    ld, lt : float
        Unthreaded and threaded grip lengths [m].

    Returns
    -------
    float
        Stiffness [N/m].

    Raises
    ------
    ValueError
        For non-positive E/areas, negative lengths or zero grip.
    """
    if min(E, Ad, At) <= 0 or ld < 0 or lt < 0 or ld + lt == 0:
        raise ValueError("invalid input")
    return Ad * At * E / (Ad * lt + At * ld)


@cite("budynas_nisbett_2015",
      note="frustum member stiffness (book not read in this session); checked against the Roymech example")
def frustum_stiffness(E: float, d: float, t: float, D: float, angle_deg: float = 30.0) -> float:
    """Stiffness of a conical (frustum) compression zone.

    Parameters
    ----------
    E : float
        Member modulus [Pa].
    d : float
        Hole diameter [m].
    t : float
        Frustum height [m].
    D : float
        Small base diameter of the cone (washer / head diameter) [m], ``D > d``.
    angle_deg : float
        Cone half-angle [deg] (30° gives tan α = 0.5774).

    Returns
    -------
    float
        Stiffness [N/m].

    Raises
    ------
    ValueError
        Unless E, d, t are positive and ``D > d``.

    Notes
    -----
    ``k = π E d tanα / ln[(2t tanα + D − d)(D + d) / ((2t tanα + D + d)(D − d))]``.
    """
    if min(E, d, t) <= 0 or d >= D:
        raise ValueError("E, d, t must be positive and D > d")
    ta = math.tan(math.radians(angle_deg))
    numerator = (2 * t * ta + D - d) * (D + d)
    denominator = (2 * t * ta + D + d) * (D - d)
    return math.pi * E * d * ta / math.log(numerator / denominator)


@cite("budynas_nisbett_2015", note="member stiffness of a layered joint (book not read in this session)")
def member_stiffness(layers: Sequence[tuple[float, float]], d: float, D: float | None = None,
                     angle_deg: float = 30.0) -> float:
    """Stiffness of layered clamped members; cones from both ends meet at mid-grip (l/2).

    Parameters
    ----------
    layers : sequence of (t, E)
        Layer thickness [m] and modulus [Pa], from the head to the nut.
    d : float
        Hole diameter [m].
    D : float, optional
        Cone base diameter (default 1.5 d) [m].
    angle_deg : float
        Cone half-angle [deg].

    Returns
    -------
    float
        Member stiffness k_m [N/m]; each layer / half is a separate frustum, all in series
        (``1/k_m = Σ 1/k_i``).
    """
    D = 1.5 * d if D is None else D
    l = sum(t for t, _ in layers)
    ta = math.tan(math.radians(angle_deg))
    flexibility, z = 0.0, 0.0
    for t, E in layers:
        start, end = z, z + t
        parts = [(start, min(end, l / 2)), (max(start, l / 2), end)]
        for z0, z1 in parts:
            if z1 - z0 <= 1e-15 * l:
                continue
            near = z0 if z1 <= l / 2 + 1e-15 * l else l - z1      # distance to the nearest outer face
            Dk = D + 2 * near * ta
            flexibility += 1 / frustum_stiffness(E, d, z1 - z0, Dk, angle_deg)
        z = end
    return 1 / flexibility


@cite("wileman_choudhury_1991", note="constants for steel as given on the Roymech page")
def wileman_stiffness(E: float, d: float, l: float, A: float = 0.78715, B: float = 0.62873) -> float:
    """Wileman exponential member stiffness ``k_m = E d A exp(B d/l)``.

    Parameters
    ----------
    E : float
        Member modulus [Pa].
    d : float
        Bolt diameter [m].
    l : float
        Grip length [m].
    A, B : float
        Material constants (defaults for steel) [-].

    Returns
    -------
    float
        Stiffness [N/m].

    Raises
    ------
    ValueError
        If E, d or l is not positive.
    """
    if min(E, d, l) <= 0:
        raise ValueError("E, d and l must be positive")
    return E * d * A * math.exp(B * d / l)


@cite("nasa_std5020b_2021", note="Eq. (9)")
def stiffness_coefficient(kb: float, kc: float) -> float:
    """Joint stiffness factor ``φ = k_b/(k_b + k_c)``.

    Parameters
    ----------
    kb, kc : float
        Bolt and clamped-member stiffness [N/m].

    Returns
    -------
    float
        φ [-].
    """
    return kb / (kb + kc)


@cite("nasa_std5020b_2021", note="Eqs. (8) and (11)")
def bolt_load(Pp: float, Pt: float, phi: float, n: float = 1.0) -> dict[str, float]:
    """Bolt load under external tension and the separation load.

    Parameters
    ----------
    Pp : float
        Preload [N].
    Pt : float
        External tensile load [N].
    phi : float
        Stiffness factor φ [-].
    n : float
        Loading-plane factor [-], ``0 ≤ nφ < 1``.

    Returns
    -------
    dict
        ``P_bolt = P_p + nφP_t`` (Eq. 8), ``P_separation = P_p/(1 − nφ)`` (Eq. 11) and the member
        compression ``P_member = P_p − (1 − nφ)P_t`` [N].

    Raises
    ------
    ValueError
        Unless ``0 ≤ nφ < 1``.
    """
    if not 0 <= n * phi < 1:
        raise ValueError("0 ≤ nφ < 1 is required")
    return {"P_bolt": Pp + n * phi * Pt, "P_separation": Pp / (1 - n * phi),
            "P_member": Pp - (1 - n * phi) * Pt}


@cite("nasa_std5020b_2021", note="Eq. (19)")
def ms_separation(Pp_min: float, PtL: float, FS_sep: float = 1.0, FF: float = 1.0) -> float:
    """Separation margin ``MS_sep = P_p,min/(FF · FS_sep · P_tL) − 1`` (axial load only).

    Parameters
    ----------
    Pp_min : float
        Minimum preload [N].
    PtL : float
        Limit external tensile load [N].
    FS_sep : float
        Separation factor of safety.
    FF : float
        Fitting factor.

    Returns
    -------
    float
        Margin of safety [-].
    """
    return Pp_min / (FF * FS_sep * PtL) - 1


@cite("nasa_std5020b_2021", note="Eqs. (20) and (22); load-factor MS derived here")
def ms_tension_shear(Pt: float, Pt_allowed: float, Ps: float, Ps_allowed: float,
                     thread_in_shear: bool = False) -> float:
    """NASA-STD-5020B ultimate tension-shear interaction (no bending term), as a load-factor margin.

    Parameters
    ----------
    Pt, Pt_allowed : float
        Applied and allowable tensile load [N].
    Ps, Ps_allowed : float
        Applied and allowable shear load [N].
    thread_in_shear : bool
        True if the threads lie in the shear plane.

    Returns
    -------
    float
        ``MS = λ − 1`` with ``(λR_s)^a + (λR_t)^b = 1`` (loads grow proportionally; this MS definition
        is derived here, not taken from the standard).

    Notes
    -----
    Shank in the shear plane: ``R_s^2.5 + R_t^1.5 ≤ 1`` (Eq. 20); threads in the shear plane:
    ``R_s^1.2 + R_t^2 ≤ 1`` (Eq. 22).
    """
    from aerokit.structures.buckling import interaction_load_factor
    Rs, Rt = Ps / Ps_allowed, Pt / Pt_allowed
    exponents = (1.2, 2.0) if thread_in_shear else (2.5, 1.5)
    return interaction_load_factor([Rs, Rt], exponents) - 1
