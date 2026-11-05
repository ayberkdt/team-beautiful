"""Wing span loading: Schrenk distribution, shear force and bending moment, root loads.

Assumptions: the air load is not relieved by the wing weight (conservative), no sweep and no
twist, the load factor n is the same along the whole span. One half-wing is computed.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from aerokit.references import cite


def trapezoid_chord(y: float | np.ndarray, b: float, c_root: float, c_tip: float) -> float | np.ndarray:
    """Chord of a straight-tapered wing at spanwise station ``y``.

    Parameters
    ----------
    y : float or numpy.ndarray
        Spanwise station(s) from the root [m]; |y| <= b/2.
    b : float
        Span [m].
    c_root, c_tip : float
        Root and tip chords [m].

    Returns
    -------
    float or numpy.ndarray
        c(y) = c_root + (c_tip - c_root) 2|y|/b [m].
    """
    return c_root + (c_tip - c_root) * (2 * np.abs(y) / b)


@cite("schrenk_1940", note="Schrenk chord: mean of the trapezoidal and elliptic chords of equal area")
def schrenk(b: float, c_root: float, c_tip: float, n_point: int = 401) -> tuple[np.ndarray, np.ndarray, float]:
    """Schrenk effective chord along the half-span.

    Parameters
    ----------
    b : float
        Span [m].
    c_root, c_tip : float
        Root and tip chords [m].
    n_point : int, optional
        Number of equally spaced stations from root to tip.

    Returns
    -------
    y : numpy.ndarray
        Stations 0 ... b/2 [m].
    c_schrenk : numpy.ndarray
        Schrenk effective chord at ``y`` [m].
    S : float
        Wing reference area (c_root + c_tip) b / 2 [m^2].

    Notes
    -----
    c_ellipse(y) = 4 S / (pi b) sqrt(1 - (2 y / b)^2), c_schrenk = (c_trapezoid + c_ellipse)/2.
    """
    y = np.linspace(0.0, b / 2, n_point)
    S = 0.5 * (c_root + c_tip) * b
    c_trap = trapezoid_chord(y, b, c_root, c_tip)
    c_ellipse = 4 * S / (math.pi * b) * np.sqrt(np.clip(1 - (2 * y / b) ** 2, 0, None))
    return y, 0.5 * (c_trap + c_ellipse), S


def _inverse_cumulative(y: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Integral of ``f`` from each station ``y`` to the tip (trapezoidal rule)."""
    part = 0.5 * (f[1:] + f[:-1]) * np.diff(y)
    return np.concatenate([np.cumsum(part[::-1])[::-1], [0.0]])


@cite("schrenk_1940", note="default 'schrenk' distribution")
def span_loads(W: float, n: float, b: float, c_root: float, c_tip: float, distribution: str = "schrenk",
               n_point: int = 401) -> dict[str, Any]:
    """Running air load, shear force and bending moment along the half-wing.

    Parameters
    ----------
    W : float
        Aircraft weight [N].
    n : float
        Load factor [-]; the whole wing carries n W, one half-wing n W / 2.
    b : float
        Span [m].
    c_root, c_tip : float
        Root and tip chords [m].
    distribution : {"schrenk", "ellipse", "trapezoid"}, optional
        Spanwise lift distribution; any other value falls back to ``"schrenk"``.
    n_point : int, optional
        Number of stations from root to tip.

    Returns
    -------
    dict[str, Any]
        ``y`` stations [m], ``load`` running load [N/m], ``V`` shear force [N], ``M`` bending
        moment [N m] (arrays, root first; ``V[0]``, ``M[0]`` are the root values), ``S`` wing area [m^2].

    Notes
    -----
    load(y) = n W c(y) / S, so that the integral over the full span is n W.
    V(y) = int_y^{b/2} load dy, M(y) = int_y^{b/2} V dy (trapezoidal rule).

    Examples
    --------
    >>> r = span_loads(1000.0, 1.0, 10.0, 1.0, 1.0, distribution="trapezoid")
    >>> round(float(r["V"][0]), 6)
    500.0
    """
    y, c_s, S = schrenk(b, c_root, c_tip, n_point)
    c: np.ndarray
    if distribution == "ellipse":
        c = 4 * S / (math.pi * b) * np.sqrt(np.clip(1 - (2 * y / b) ** 2, 0, None))
    elif distribution == "trapezoid":
        c = np.asarray(trapezoid_chord(y, b, c_root, c_tip))
    else:
        c = c_s
    load = n * W * c / S                              # N/m; integral over -b/2..b/2 = nW
    V = _inverse_cumulative(y, load)
    M = _inverse_cumulative(y, V)
    return {"y": y, "load": load, "V": V, "M": M, "S": S}


@cite("cfr14_part23", note="§23.337(a)(1) and (b)(1), 2011 edition text")
def n_limit_far23_normal(W: float) -> tuple[float, float]:
    """FAR 23 normal/commuter category limit maneuver load factors.

    Parameters
    ----------
    W : float
        Design maximum takeoff weight [N].

    Returns
    -------
    n_pos : float
        Positive limit load factor, 2.1 + 24 000/(W_lb + 10 000), capped at 3.8 [-].
    n_neg : float
        Negative limit load factor, -0.4 n_pos [-].

    Notes
    -----
    14 CFR 23.337 (2011 edition). The current Part 23 is performance-based; this older formula is
    kept as a reference for conceptual work. See :func:`aerokit.aero.loads.n_maneuver` for all
    categories.

    Examples
    --------
    >>> n_limit_far23_normal(2000 * 4.4482216152605)[0]
    3.8
    """
    W_lb = W / 4.4482216152605
    n = min(2.1 + 24000 / (W_lb + 10000), 3.8)
    return n, -0.4 * n


def ellipse_root_moment(W: float, n: float, b: float) -> float:
    """Analytical half-wing root bending moment for an elliptic lift distribution.

    Parameters
    ----------
    W : float
        Aircraft weight [N].
    n : float
        Load factor [-].
    b : float
        Span [m].

    Returns
    -------
    float
        M_root = n W b / (3 pi) [N m].
    """
    return n * W * b / (3 * math.pi)
