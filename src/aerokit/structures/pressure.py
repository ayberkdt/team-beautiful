"""Pressure vessels: thin- and thick-walled cylinders and spheres, interference fits, autofrettage.

Sources:

- Lamé thick cylinder, thin wall, interference fit: Shigley 10th ed. Ch. 3 (read in the Hijazi lecture
  notes CH3, pp. 22-23; equation numbers not verified). Timoshenko, Strength of Materials Part II,
  Ch. VI (same relations).
- Thick sphere: Timoshenko & Goodier, Theory of Elasticity, Sec. 137 (spherical shell).
- Autofrettage (elastic-perfectly plastic, Tresca, closed ends / plastic radius c):
  Hill, The Mathematical Theory of Plasticity (1950), Ch. V.

NOTE: Timoshenko & Goodier / Timoshenko / Hill section numbers were not verified from the books in this
session (general knowledge); the relations are tested through equilibrium, boundary conditions and limits.

Sign convention: tension positive; a pressure p > 0 pushes on the inner/outer surface (σr = −p).
SI units (Pa, m); the functions are unit-agnostic, consistent units suffice.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.references import cite
from aerokit.structures.tensor import Stress


def _positive(**kw: float) -> None:
    """Raise ``ValueError`` naming the first keyword argument that is not positive."""
    for name, v in kw.items():
        if not (v > 0):
            raise ValueError(f"{name} must be positive (got {v})")


def _radii(ri: float, ro: float) -> None:
    """Raise ``ValueError`` unless ``0 ≤ ri < ro``."""
    if not (0 <= ri < ro):
        raise ValueError(f"0 ≤ ri < ro is required (ri={ri}, ro={ro})")


# --- thin wall ---------------------------------------------------------------------------------
@cite("budynas_nisbett_2015", note="thin-walled vessels, Ch. 3 (Hijazi CH3 notes)")
def thin_cylinder(p: float, r: float, t: float) -> dict[str, float]:
    """Thin-walled cylinder with closed ends (suitable for t ≤ r/20).

    Parameters
    ----------
    p : float
        Internal pressure [Pa].
    r : float
        Mean (or inner) radius [m].
    t : float
        Wall thickness [m].

    Returns
    -------
    dict
        ``hoop = p r/t``, ``axial = p r/(2t)``, ``radial_inner = −p``, ``radial_outer = 0`` [Pa].

    Raises
    ------
    ValueError
        If r or t is not positive.
    """
    _positive(r=r, t=t)
    return {"hoop": p * r / t, "axial": p * r / (2 * t), "radial_inner": -p, "radial_outer": 0.0}


@cite("budynas_nisbett_2015", note="thin-walled vessels, Ch. 3")
def thin_sphere(p: float, r: float, t: float) -> dict[str, float]:
    """Thin-walled sphere: ``σ = p r/(2t)`` in both tangential directions.

    Parameters
    ----------
    p : float
        Internal pressure [Pa].
    r, t : float
        Radius and wall thickness [m].

    Returns
    -------
    dict
        ``hoop``, ``radial_inner = −p``, ``radial_outer = 0`` [Pa].

    Raises
    ------
    ValueError
        If r or t is not positive.
    """
    _positive(r=r, t=t)
    return {"hoop": p * r / (2 * t), "radial_inner": -p, "radial_outer": 0.0}


# --- Lamé thick cylinder -----------------------------------------------------------------------
@cite("timoshenko_goodier_1970", note="Lamé thick cylinder")
def lame_constants(ri: float, ro: float, pi: float = 0.0, po: float = 0.0) -> tuple[float, float]:
    """Lamé constants (A, B) for ``σr = A − B/r²``, ``σθ = A + B/r²``.

    Parameters
    ----------
    ri, ro : float
        Inner and outer radius [m].
    pi, po : float
        Internal and external pressure [Pa].

    Returns
    -------
    tuple of float
        ``A = (pi ri² − po ro²)/(ro² − ri²)`` [Pa], ``B = (pi − po) ri² ro²/(ro² − ri²)`` [Pa·m²].
    """
    _radii(ri, ro)
    d = ro ** 2 - ri ** 2
    A = (pi * ri ** 2 - po * ro ** 2) / d
    B = (pi - po) * ri ** 2 * ro ** 2 / d
    return A, B


@cite("timoshenko_goodier_1970", note="Lamé thick cylinder")
@cite("budynas_nisbett_2015", note="Ch. 3 (Hijazi CH3 notes pp. 22-23)")
def lame_cylinder(ri: float, ro: float, pi: float = 0.0, po: float = 0.0, r: ArrayLike | None = None,
                  ends: str = "closed", E: float | None = None, nu: float | None = None) -> dict[str, Any]:
    """Thick-walled (Lamé) cylinder.

    Parameters
    ----------
    ri, ro : float
        Inner and outer radius [m].
    pi, po : float
        Internal and external pressure [Pa].
    r : float or array_like, optional
        Evaluation radius/radii in ``[ri, ro]`` [m] (default: inner surface).
    ends : {"closed", "open", "plane_strain"}
        ``closed``: σz = A (pressure pushes the end caps); ``open``: σz = 0;
        ``plane_strain``: εz = 0 → σz = 2νA (needs ``nu``).
    E, nu : float, optional
        If ``E`` is given the radial displacement ``u = r[σθ − ν(σr + σz)]/E`` [m] is returned too.

    Returns
    -------
    dict
        ``sr``, ``st``, ``sz`` [Pa] (floats for scalar r, arrays otherwise), ``A`` [Pa], ``B`` [Pa·m²],
        optional ``u`` [m].

    Raises
    ------
    ValueError
        If r is outside ``[ri, ro]``, ``ends`` is unknown, or ``nu`` is missing where required.
    """
    A, B = lame_constants(ri, ro, pi, po)
    r = ri if r is None else r
    r_arr = np.asarray(r, dtype=float)
    if np.any(r_arr < ri - 1e-12 * ro) or np.any(r_arr > ro * (1 + 1e-12)):
        raise ValueError("r must lie in [ri, ro]")
    sr = A - B / r_arr ** 2
    st = A + B / r_arr ** 2
    if ends == "closed":
        sz = A * np.ones_like(r_arr)
    elif ends == "open":
        sz = np.zeros_like(r_arr)
    elif ends == "plane_strain":
        if nu is None:
            raise ValueError("plane strain requires nu")
        sz = 2 * nu * A * np.ones_like(r_arr)
    else:
        raise ValueError("ends must be 'closed', 'open' or 'plane_strain'")
    result: dict[str, Any] = {"sr": sr, "st": st, "sz": sz, "A": A, "B": B}
    if E is not None:
        if nu is None:
            raise ValueError("the displacement requires nu")
        result["u"] = r_arr * (st - nu * (sr + sz)) / E
    if np.ndim(r) == 0:
        result = {k: (float(v) if isinstance(v, np.ndarray) else v) for k, v in result.items()}
    return result


def lame_tensor(ri: float, ro: float, pi: float = 0.0, po: float = 0.0, r: float | None = None,
                ends: str = "closed", nu: float | None = None) -> Stress:
    """Stress tensor at radius r in cylindrical axes (r, θ, z) as a :class:`~aerokit.structures.tensor.Stress`.

    Parameters
    ----------
    ri, ro, pi, po, ends, nu
        As in :func:`lame_cylinder`.
    r : float, optional
        Radius [m] (default: inner surface).

    Returns
    -------
    Stress
        Diagonal tensor ``diag(σr, σθ, σz)`` [Pa].
    """
    s = lame_cylinder(ri, ro, pi, po, r=ri if r is None else float(r), ends=ends, nu=nu)
    return Stress(sxx=s["sr"], syy=s["st"], szz=s["sz"])


def lame_inner_surface(ri: float, ro: float, pi: float = 0.0, po: float = 0.0, ends: str = "closed",
                       nu: float | None = None, yield_: float | None = None) -> dict[str, Any]:
    """Bore (inner-surface) von Mises and Tresca stresses and, if a yield stress is given, safety factors.

    Parameters
    ----------
    ri, ro, pi, po, ends, nu
        As in :func:`lame_cylinder`.
    yield_ : float, optional
        Yield stress [Pa].

    Returns
    -------
    dict
        ``stress`` (:class:`Stress`), ``von_mises`` and ``tresca`` [Pa]; with ``yield_`` also
        ``n_von_mises`` and ``n_tresca`` [-].
    """
    g = lame_tensor(ri, ro, pi, po, ri, ends, nu)
    d: dict[str, Any] = {"stress": g, "von_mises": g.von_mises(), "tresca": g.tresca()}
    if yield_ is not None:
        d["n_von_mises"] = g.safety_coefficient(yield_, "von_mises")
        d["n_tresca"] = g.safety_coefficient(yield_, "tresca")
    return d


# --- thick sphere ------------------------------------------------------------------------------
@cite("timoshenko_goodier_1970", note="spherical shell (Sec. 137, not verified in this session)")
def thick_sphere(ri: float, ro: float, pi: float = 0.0, po: float = 0.0, r: ArrayLike | None = None,
                 E: float | None = None, nu: float | None = None) -> dict[str, Any]:
    """Thick-walled sphere.

    Parameters
    ----------
    ri, ro : float
        Inner and outer radius [m].
    pi, po : float
        Internal and external pressure [Pa].
    r : float or array_like, optional
        Evaluation radius/radii [m] (default: inner surface).
    E, nu : float, optional
        If ``E`` is given the radial displacement ``u`` [m] is returned too (``nu`` required).

    Returns
    -------
    dict
        ``sr``, ``st`` (= σφ) [Pa] and optional ``u`` [m].

    Notes
    -----
    ``σr = C1 − C2/r³``, ``σθ = σφ = C1 + C2/(2r³)`` with
    ``C1 = (pi ri³ − po ro³)/(ro³ − ri³)``, ``C2 = (pi − po) ri³ ro³/(ro³ − ri³)``.
    """
    _radii(ri, ro)
    r = ri if r is None else r
    r_arr = np.asarray(r, dtype=float)
    d = ro ** 3 - ri ** 3
    C1 = (pi * ri ** 3 - po * ro ** 3) / d
    C2 = (pi - po) * ri ** 3 * ro ** 3 / d
    sr = C1 - C2 / r_arr ** 3
    st = C1 + C2 / (2 * r_arr ** 3)
    result: dict[str, Any] = {"sr": sr, "st": st}
    if E is not None:
        result["u"] = r_arr * ((1 - nu) * st - nu * sr) / E  # type: ignore[operator]
    if np.ndim(r) == 0:
        result = {k: float(v) for k, v in result.items()}
    return result


# --- interference fit --------------------------------------------------------------------------
@cite("budynas_nisbett_2015", note="press and shrink fits, Ch. 3; general form not read in this session")
def interference_pressure(delta: float, R: float, ri: float, ro: float, E_inner: float, nu_inner: float,
                          E_outer: float | None = None, nu_outer: float | None = None) -> float:
    """Contact pressure of a press / shrink fit (open ends, plane stress).

    Parameters
    ----------
    delta : float
        RADIAL interference (half the diametral interference) [m].
    R : float
        Common (nominal) interface radius [m].
    ri : float
        Inner radius of the inner member (shaft); 0 for a solid shaft [m].
    ro : float
        Outer radius of the outer member (hub) [m].
    E_inner, nu_inner : float
        Shaft modulus [Pa] and Poisson's ratio [-].
    E_outer, nu_outer : float, optional
        Hub constants; if omitted both members are of the same material.

    Returns
    -------
    float
        Interface pressure p [Pa].

    Raises
    ------
    ValueError
        Unless ``0 ≤ ri < R < ro`` and R, E_inner are positive.

    Notes
    -----
    ``p = δ / {R/E_o [(ro² + R²)/(ro² − R²) + ν_o] + R/E_i [(R² + ri²)/(R² − ri²) − ν_i]}``; it reduces to
    :func:`interference_pressure_same` for one material (checked in the tests).
    """
    _positive(R=R, E_inner=E_inner)
    if not (0 <= ri < R < ro):
        raise ValueError("0 ≤ ri < R < ro is required")
    if E_outer is None:
        E_outer, nu_outer = E_inner, nu_inner
    outer = R / E_outer * ((ro ** 2 + R ** 2) / (ro ** 2 - R ** 2) + nu_outer)  # type: ignore[operator]
    inner = R / E_inner * ((R ** 2 + ri ** 2) / (R ** 2 - ri ** 2) - nu_inner)
    return delta / (outer + inner)


@cite("budynas_nisbett_2015", note="Ch. 3 (Hijazi CH3 notes p. 23)")
def interference_pressure_same(delta: float, R: float, ri: float, ro: float, E: float) -> float:
    """Closed-form interference pressure for members of the same material.

    Parameters
    ----------
    delta : float
        Radial interference [m].
    R, ri, ro : float
        Interface, shaft inner and hub outer radius [m].
    E : float
        Young's modulus [Pa].

    Returns
    -------
    float
        ``p = (Eδ/R) (ro² − R²)(R² − ri²) / [2R²(ro² − ri²)]`` [Pa].

    Raises
    ------
    ValueError
        Unless ``0 ≤ ri < R < ro``.
    """
    if not (0 <= ri < R < ro):
        raise ValueError("0 ≤ ri < R < ro is required")
    return E * delta / R * (ro ** 2 - R ** 2) * (R ** 2 - ri ** 2) / (2 * R ** 2 * (ro ** 2 - ri ** 2))


def interference_stresses(delta: float, R: float, ri: float, ro: float, E_inner: float, nu_inner: float,
                          E_outer: float | None = None, nu_outer: float | None = None) -> dict[str, float]:
    """Hub and shaft stresses at the interface of an interference fit (open ends).

    Parameters
    ----------
    delta, R, ri, ro, E_inner, nu_inner, E_outer, nu_outer
        As in :func:`interference_pressure`.

    Returns
    -------
    dict
        ``p`` [Pa], ``hub_hoop``, ``hub_radial``, ``shaft_hoop``, ``shaft_radial`` [Pa].
    """
    p = interference_pressure(delta, R, ri, ro, E_inner, nu_inner, E_outer, nu_outer)
    hub = lame_cylinder(R, ro, pi=p, r=R, ends="open")
    if ri > 0:
        shaft = lame_cylinder(ri, R, po=p, r=R, ends="open")
    else:   # solid shaft: σr = σθ = −p everywhere
        shaft = {"sr": -p, "st": -p, "sz": 0.0}
    return {"p": p, "hub_hoop": hub["st"], "hub_radial": hub["sr"],
            "shaft_hoop": shaft["st"], "shaft_radial": shaft["sr"]}


# --- autofrettage (optional) -------------------------------------------------------------------
@cite("hill_1950", note="Ch. V")
def autofrettage_pressure(ri: float, ro: float, yield_: float, c: float | None = None) -> float:
    """Internal pressure at which the plastic zone of an elastic-perfectly plastic cylinder reaches radius c.

    Parameters
    ----------
    ri, ro : float
        Inner and outer radius [m].
    yield_ : float
        Yield stress σy [Pa].
    c : float, optional
        Elastic-plastic boundary radius, ``ri ≤ c ≤ ro`` (default ``ri``, first yield) [m].

    Returns
    -------
    float
        Pressure [Pa].

    Raises
    ------
    ValueError
        For invalid radii or a non-positive yield stress.

    Notes
    -----
    Tresca with σz the intermediate principal stress (closed ends):
    ``p(c) = σy [ln(c/ri) + (ro² − c²)/(2 ro²)]``. ``c = ri`` gives the first-yield pressure
    ``σy(ro² − ri²)/(2ro²)``; ``c = ro`` the fully plastic ``σy ln(ro/ri)``.
    """
    _radii(ri, ro)
    _positive(ri=ri, yield_=yield_)
    c = ri if c is None else c
    if not (ri <= c <= ro):
        raise ValueError("ri ≤ c ≤ ro is required")
    return yield_ * (math.log(c / ri) + (ro ** 2 - c ** 2) / (2 * ro ** 2))
