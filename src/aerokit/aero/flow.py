"""CFD set-up sizing: Reynolds and Mach numbers, first-cell height for a target y+, boundary-layer
thickness, prism-layer count, cell budget, grid-refinement sequence and GCI.

All flow properties are taken from the ISA model (:func:`aerokit.aero.atmosphere.isa`).
"""
from __future__ import annotations

import math
from typing import Any

from aerokit.aero.atmosphere import isa
from aerokit.references import cite


def reynolds(U: float, L: float, h: float = 0.0) -> float:
    """Reynolds number based on length ``L``.

    Parameters
    ----------
    U : float
        Free-stream speed [m/s].
    L : float
        Reference length [m].
    h : float, optional
        ISA altitude [m] (default sea level).

    Returns
    -------
    float
        Re = U L / nu [-].

    Raises
    ------
    ValueError
        If ``h`` is outside the ISA range 0-20 000 m.
    """
    a = isa(h)
    return U * L / a["nu"]


def mach(U: float, h: float = 0.0) -> float:
    """Mach number of speed ``U`` at ISA altitude ``h``.

    Parameters
    ----------
    U : float
        Speed [m/s].
    h : float, optional
        ISA altitude [m] (default sea level).

    Returns
    -------
    float
        M = U / a [-].

    Raises
    ------
    ValueError
        If ``h`` is outside the ISA range 0-20 000 m.
    """
    return U / isa(h)["a"]


def first_cell(U: float, L: float, yplus: float = 1.0, h: float = 0.0) -> tuple[float, float, float, float]:
    """First-cell height for a target y+ from the turbulent flat-plate skin friction.

    Parameters
    ----------
    U : float
        Free-stream speed [m/s].
    L : float
        Reference length used for the Reynolds number [m].
    yplus : float, optional
        Target y+ at the first cell centre [-].
    h : float, optional
        ISA altitude [m].

    Returns
    -------
    cell_height : float
        First-cell height [m] (= 2 y_p).
    y_p : float
        Wall distance of the first cell centre [m].
    Re : float
        Reynolds number based on ``L`` [-].
    u_tau : float
        Friction velocity [m/s].

    Raises
    ------
    ValueError
        If ``h`` is outside the ISA range 0-20 000 m.

    Notes
    -----
    Cf = 0.026 Re^(-1/7) (turbulent flat plate; no source recorded in the code),
    u_tau = sqrt(Cf U^2 / 2), y_p = y+ nu / u_tau. Fluent reports y+ at the cell centre, so the
    cell height is 2 y_p.
    """
    a = isa(h)
    Re = U * L / a["nu"]
    Cf = 0.026 * Re ** (-1 / 7)
    u_tau = math.sqrt(0.5 * Cf * U ** 2)
    y_p = yplus * a["nu"] / u_tau
    return 2 * y_p, y_p, Re, u_tau


def boundary_layer(U: float, x: float, h: float = 0.0) -> float:
    """Turbulent flat-plate boundary-layer thickness at distance ``x``.

    Parameters
    ----------
    U : float
        Free-stream speed [m/s].
    x : float
        Distance from the leading edge [m].
    h : float, optional
        ISA altitude [m].

    Returns
    -------
    float
        delta = 0.37 x / Re_x^0.2 [m] (1/7-power-law estimate).

    Raises
    ------
    ValueError
        If ``h`` is outside the ISA range 0-20 000 m.
    """
    Re_x = reynolds(U, x, h)
    return 0.37 * x / Re_x ** 0.2


def layer_count(first: float, total: float, growth: float) -> int:
    """Smallest number of geometrically growing prism layers that covers a thickness.

    Parameters
    ----------
    first : float
        First-layer height [m].
    total : float
        Thickness to cover, e.g. the boundary-layer thickness [m].
    growth : float
        Layer growth ratio G > 1 [-].

    Returns
    -------
    int
        Smallest n with first (G^n - 1)/(G - 1) >= total.

    Raises
    ------
    ValueError
        If ``growth <= 1``.

    Examples
    --------
    >>> layer_count(1.0, 7.0, 2.0)
    3
    """
    if growth <= 1:
        raise ValueError("growth ratio must be > 1")
    return math.ceil(math.log(1 + total * (growth - 1) / first) / math.log(growth))


def cell_budget(surface_face: float, layer: float, core_share: float = 0.45) -> dict[str, float]:
    """Rough cell-count budget of a prism-layer mesh.

    Parameters
    ----------
    surface_face : float
        Number of surface faces [-].
    layer : float
        Number of prism layers [-].
    core_share : float, optional
        Share of the total cell count taken by the core (tetra/poly) mesh, 0 <= share < 1.

    Returns
    -------
    dict[str, float]
        ``prism`` prism cells (= faces x layers), ``core`` core cells, ``total`` total cells.
    """
    prism = surface_face * layer
    total = prism / (1 - core_share)
    return {"prism": prism, "core": total - prism, "total": total}


@cite("celik_2008", note="grid refinement ratio r = h_coarse/h_fine > 1.3")
def grid_sequence(n_fine: float, r: float = 1.3, size: int = 3, level: int = 3) -> list[int]:
    """Cell counts of a systematic grid-refinement sequence.

    Parameters
    ----------
    n_fine : float
        Cell count of the finest grid [-].
    r : float, optional
        Grid refinement ratio h_coarse/h_fine (> 1.3 recommended) [-].
    size : int, optional
        Spatial dimension of the mesh (2 or 3); the cell-count ratio is r^size.
    level : int, optional
        Number of grid levels.

    Returns
    -------
    list[int]
        Cell counts from the coarsest to the finest grid.

    Examples
    --------
    >>> grid_sequence(1000, r=2.0, size=3, level=2)
    [125, 1000]
    """
    return [round(n_fine / r ** (size * i)) for i in reversed(range(level))]


@cite("celik_2008", note="apparent order, Richardson extrapolation and fine-grid GCI")
def gci(f1: float, f2: float, f3: float, r21: float, r32: float, Fs: float = 1.25, tol: float = 1e-10,
        maxit: int = 200) -> dict[str, Any]:
    """Grid Convergence Index of a three-grid study.

    Parameters
    ----------
    f1, f2, f3 : float
        Solution on the fine, medium and coarse grids.
    r21, r32 : float
        Refinement ratios h2/h1 and h3/h2 [-].
    Fs : float, optional
        Safety factor (1.25 for three grids).
    tol : float, optional
        Convergence tolerance of the fixed-point iteration for the apparent order.
    maxit : int, optional
        Maximum number of iterations.

    Returns
    -------
    dict[str, Any]
        ``p`` apparent order, ``f_ext`` Richardson-extrapolated value, ``e_a`` approximate relative
        error |(f1 - f2)/f1|, ``e_ext`` extrapolated relative error |(f_ext - f1)/f_ext|,
        ``gci_fine`` fine-grid GCI = Fs e_a / (r21^p - 1), ``oscillatory`` True if the convergence is
        oscillatory (sign of e32/e21 negative).

    Raises
    ------
    ZeroDivisionError
        If ``f1 == f2`` (zero difference between the fine and medium grids).

    Notes
    -----
    p = |ln|e32/e21| + q(p)| / ln r21, q(p) = ln((r21^p - s)/(r32^p - s)), s = sign(e32/e21),
    solved by fixed-point iteration from p = 2.
    f_ext = (r21^p f1 - f2)/(r21^p - 1).
    """
    e32, e21 = f3 - f2, f2 - f1
    s = math.copysign(1, e32 / e21)
    p = 2.0
    for _ in range(maxit):
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < tol:
            p = p_new
            break
        p = p_new
    f_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    e_a = abs((f1 - f2) / f1)
    e_ext = abs((f_ext - f1) / f_ext)
    return {"p": p, "f_ext": f_ext, "e_a": e_a, "e_ext": e_ext,
            "gci_fine": Fs * e_a / (r21 ** p - 1), "oscillatory": s < 0}


def speed_components(U: float, alpha_degree: float) -> dict[str, Any]:
    """Velocity-inlet components and force directions for a 2-D case (x downstream, y up).

    Parameters
    ----------
    U : float
        Free-stream speed [m/s].
    alpha_degree : float
        Angle of attack [deg].

    Returns
    -------
    dict
        ``Ux``, ``Uy`` velocity components [m/s]; ``drag_direction`` and ``lift_direction``
        unit vectors (x, y) [-].

    Examples
    --------
    >>> round(speed_components(1.0, 6.0)["Ux"], 4)
    0.9945
    """
    a = math.radians(alpha_degree)
    return {"Ux": U * math.cos(a), "Uy": U * math.sin(a),
            "drag_direction": (math.cos(a), math.sin(a)),
            "lift_direction": (-math.sin(a), math.cos(a))}
