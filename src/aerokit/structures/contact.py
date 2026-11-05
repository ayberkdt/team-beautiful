"""Hertz contact stresses: sphere-sphere, sphere-plane, parallel cylinders, crossed cylinders
(elliptical contact), subsurface stresses and the depth of the maximum shear stress.

Sources:

- Johnson, K. L., Contact Mechanics (1985), Ch. 4 (Hertz) and Sec. 3.4 (elliptical contact) -- the book
  was not read in this session; the relations were checked against the Shigley/Budynas form and limits.
- Shigley 8th ed. (Budynas & Nisbett) Sec. 3-19 (Eqs. 3-68 to 3-77, tutorial numbering); Budynas & Nisbett
  "Tutorial 3-19: Hertz Contact Stresses" (McGraw-Hill online supplement) was read: stresses on the load axis
  for the sphere, critical depth ≈ 0.48a (ν = 0.3); for the cylinder, τmax ≈ 0.3 pmax at z = 0.786b;
  numerical values of Example T3.19.1 (cast-iron wheel on a steel plane).

NOTE: Timoshenko & Goodier / Timoshenko / Hill section numbers were not verified from the books in this
session (general knowledge); the relations are tested through equilibrium, boundary conditions and limits.

Radii of curvature: convex positive; ``math.inf`` for a plane; negative for a concave seat.
Effective modulus: ``1/E* = (1 − ν1²)/E1 + (1 − ν2²)/E2``. Compressive stresses are negative.
SI units (N, m, Pa); the functions are unit-agnostic as long as units are consistent.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy import optimize, special

from aerokit.references import cite


@cite("johnson_1985")
def e_star(E1: float, nu1: float, E2: float, nu2: float) -> float:
    """Effective (contact) modulus ``E* = 1 / [(1 − ν1²)/E1 + (1 − ν2²)/E2]``.

    Parameters
    ----------
    E1, E2 : float
        Young's moduli of the two bodies [Pa].
    nu1, nu2 : float
        Poisson's ratios [-].

    Returns
    -------
    float
        E* [Pa].

    Raises
    ------
    ValueError
        If E1 or E2 is not positive.
    """
    if not (E1 > 0 and E2 > 0):
        raise ValueError("E1 and E2 must be positive")
    return 1.0 / ((1 - nu1 ** 2) / E1 + (1 - nu2 ** 2) / E2)


def equivalent_radius(R1: float, R2: float = math.inf) -> float:
    """Equivalent radius ``1/R = 1/R1 + 1/R2``.

    Parameters
    ----------
    R1 : float
        Radius of the first (convex) body [m].
    R2 : float
        Radius of the second body [m]; ``inf`` for a plane, negative for a concave seat.

    Returns
    -------
    float
        R [m].

    Raises
    ------
    ValueError
        If ``R1 ≤ 0`` or the total curvature is not positive (seat smaller than the sphere).
    """
    if not (R1 > 0):
        raise ValueError("R1 must be positive")
    curvature = 1.0 / R1 + (0.0 if math.isinf(R2) else 1.0 / R2)
    if not (curvature > 0):
        raise ValueError("total curvature must be positive (the seat must be larger than the sphere)")
    return 1.0 / curvature


# --- sphere (circular contact) -----------------------------------------------------------------
@cite("budynas_nisbett_2015", note="Sec. 3-19, Eqs. 3-70/3-71 (tutorial 3-19 numbering)")
def sphere_stresses(p0: float, a: float, z: ArrayLike, nu: float) -> dict[str, Any]:
    """Principal stresses on the load axis at depth z below a circular Hertz contact.

    Parameters
    ----------
    p0 : float
        Peak contact pressure [Pa].
    a : float
        Contact radius [m].
    z : float or array_like
        Depth(s) below the surface [m] (sign ignored).
    nu : float
        Poisson's ratio of the body [-].

    Returns
    -------
    dict
        ``sr``, ``st`` (radial = hoop), ``sz`` (axial) [Pa] and ``tau = |σr − σz|/2`` [Pa]; floats for
        scalar ``z``, arrays otherwise.

    Notes
    -----
    ``σr = σθ = −p0[(1 + ν)(1 − ζ atan(1/ζ)) − 1/(2(1 + ζ²))]``, ``σz = −p0/(1 + ζ²)``, ``ζ = z/a``.
    """
    z_arr = np.asarray(z, dtype=float)
    zeta = np.abs(z_arr) / a
    with np.errstate(divide="ignore"):
        atn = np.where(zeta > 0, np.arctan(1.0 / np.where(zeta > 0, zeta, 1.0)), math.pi / 2)
    sr = -p0 * ((1 + nu) * (1 - zeta * atn) - 1.0 / (2 * (1 + zeta ** 2)))
    sz = -p0 / (1 + zeta ** 2)
    tau = 0.5 * np.abs(sr - sz)
    d = {"sr": sr, "st": sr, "sz": sz, "tau": tau}
    return {k: float(v) for k, v in d.items()} if np.ndim(z) == 0 else d


def _max_shear(func: Callable[[float], float], upper: float = 3.0) -> tuple[float, float]:
    """Maximise ``func`` over the normalised depth; returns ``(tau_max, zeta)``.

    The envelope (largest of the three principal differences) has kinks and a very flat top, so the best
    point of a fine grid is located first and then refined by a bounded search in the neighbouring interval.
    """
    grid = np.linspace(1e-6, upper, 3001)
    values = np.array([func(z) for z in grid])
    i = int(np.argmax(values))
    lower, upper_b = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    r = optimize.minimize_scalar(lambda zt: -func(zt), bounds=(lower, upper_b), method="bounded",
                                 options={"xatol": 1e-12})
    return (-r.fun, r.x) if -r.fun >= values[i] else (values[i], grid[i])


@cite("hertz_1882")
@cite("johnson_1985", note="Sec. 4.2")
def hertz_sphere(F: float, R1: float, R2: float, E1: float, nu1: float, E2: float, nu2: float,
                 nu_body: float | None = None) -> dict[str, float]:
    """Hertz contact of sphere-sphere, sphere-plane or sphere-in-seat.

    Parameters
    ----------
    F : float
        Normal load [N].
    R1, R2 : float
        Radii of the two bodies [m] (``inf`` plane, negative concave seat).
    E1, nu1, E2, nu2 : float
        Elastic constants of the two bodies [Pa, -].
    nu_body : float, optional
        Poisson's ratio of the body whose subsurface stress is wanted (default ``nu1``).

    Returns
    -------
    dict
        ``a`` contact radius [m], ``p0`` peak pressure [Pa], ``p_avg`` mean pressure [Pa], ``delta``
        approach [m], ``R`` equivalent radius [m], ``E_star`` [Pa], ``tau_max`` peak subsurface shear [Pa]
        and its depth ``z_tau_max`` [m].

    Raises
    ------
    ValueError
        If ``F ≤ 0`` or the geometry is invalid.

    Notes
    -----
    ``a = (3FR/(4E*))^(1/3)``, ``p0 = 3F/(2πa²)``, ``δ = a²/R``.
    """
    if not (F > 0):
        raise ValueError("F must be positive")
    R = equivalent_radius(R1, R2)
    Es = e_star(E1, nu1, E2, nu2)
    a = (3 * F * R / (4 * Es)) ** (1 / 3)
    p0 = 3 * F / (2 * math.pi * a ** 2)
    nu = nu1 if nu_body is None else nu_body
    tmax, zeta = _max_shear(lambda zt: sphere_stresses(1.0, 1.0, zt, nu)["tau"])
    return {"a": a, "p0": p0, "p_avg": F / (math.pi * a ** 2), "delta": a ** 2 / R,
            "R": R, "E_star": Es, "tau_max": tmax * p0, "z_tau_max": zeta * a}


# --- parallel cylinders (line contact) ---------------------------------------------------------
@cite("budynas_nisbett_2015", note="Sec. 3-19, Eqs. 3-75 to 3-77 (tutorial 3-19 numbering)")
def cylinder_stresses(p0: float, b: float, z: ArrayLike, nu: float) -> dict[str, Any]:
    """Principal stresses on the load axis at depth z below a line (cylinder) contact.

    Parameters
    ----------
    p0 : float
        Peak contact pressure [Pa].
    b : float
        Contact half-width [m].
    z : float or array_like
        Depth(s) below the surface [m] (sign ignored).
    nu : float
        Poisson's ratio [-].

    Returns
    -------
    dict
        ``sx`` (along the cylinder axis), ``sy`` (across the contact width), ``sz`` (depth) [Pa] and
        ``tau = (σmax − σmin)/2`` over the three principal stresses [Pa].

    Notes
    -----
    ``σx = −2νp0(√(1+ζ²) − ζ)``, ``σy = −p0[(1+2ζ²)/√(1+ζ²) − 2ζ]``, ``σz = −p0/√(1+ζ²)``, ``ζ = z/b``.
    """
    zeta = np.abs(np.asarray(z, dtype=float)) / b
    root = np.sqrt(1 + zeta ** 2)
    sx = -2 * nu * p0 * (root - zeta)
    sy = -p0 * ((1 + 2 * zeta ** 2) / root - 2 * zeta)
    sz = -p0 / root
    st = np.stack([sx, sy, sz])
    tau = 0.5 * (st.max(axis=0) - st.min(axis=0))
    d = {"sx": sx, "sy": sy, "sz": sz, "tau": tau}
    return {k: float(v) for k, v in d.items()} if np.ndim(z) == 0 else d


@cite("hertz_1882")
@cite("budynas_nisbett_2015", note="Sec. 3-19, Eqs. 3-73 and 3-74")
def hertz_cylinder(F: float, L: float, R1: float, R2: float, E1: float, nu1: float, E2: float, nu2: float,
                   nu_body: float | None = None) -> dict[str, float]:
    """Hertz contact of two parallel cylinders (or a cylinder on a plane).

    Parameters
    ----------
    F : float
        Total normal load [N].
    L : float
        Contact length [m].
    R1, R2 : float
        Radii [m] (``inf`` for a plane).
    E1, nu1, E2, nu2 : float
        Elastic constants [Pa, -].
    nu_body : float, optional
        Poisson's ratio for the subsurface stresses (default ``nu1``).

    Returns
    -------
    dict
        ``b`` half-width [m], ``p0`` [Pa], ``R`` [m], ``E_star`` [Pa], ``tau_max`` [Pa], ``z_tau_max`` [m].

    Raises
    ------
    ValueError
        If F or L is not positive.

    Notes
    -----
    ``b = √(4F'R/(πE*))`` with ``F' = F/L`` (identical to Shigley Eq. 3-73 with d = 2R) and
    ``p0 = 2F'/(πb)`` (Eq. 3-74). In line contact the approach depends logarithmically on the body size
    (Johnson Sec. 4.3) and is not computed here.
    """
    if not (F > 0 and L > 0):
        raise ValueError("F and L must be positive")
    R = equivalent_radius(R1, R2)
    Es = e_star(E1, nu1, E2, nu2)
    Fp = F / L
    b = math.sqrt(4 * Fp * R / (math.pi * Es))
    p0 = 2 * Fp / (math.pi * b)
    nu = nu1 if nu_body is None else nu_body
    tmax, zeta = _max_shear(lambda zt: cylinder_stresses(1.0, 1.0, zt, nu)["tau"])
    return {"b": b, "p0": p0, "R": R, "E_star": Es, "tau_max": tmax * p0, "z_tau_max": zeta * b}


# --- elliptical contact (general) and crossed cylinders ----------------------------------------
@cite("johnson_1985", note="Sec. 3.4; not read in this session, checked through the circular limit")
@cite("timoshenko_goodier_1970", note="elliptical Hertz contact")
def hertz_elliptic(F: float, A: float, B: float, Es: float) -> dict[str, float]:
    """General elliptical Hertz contact for the gap ``h = A x² + B y²``.

    Parameters
    ----------
    F : float
        Normal load [N].
    A, B : float
        Relative-curvature coefficients [1/m] (swapped if ``B < A`` so that A ≤ B).
    Es : float
        Effective modulus E* [Pa].

    Returns
    -------
    dict
        ``a`` semi-major axis (x direction) [m], ``b`` semi-minor axis [m], ``p0`` [Pa],
        ``delta`` approach [m], ``e`` eccentricity [-].

    Raises
    ------
    ValueError
        If any input is not positive.

    Notes
    -----
    With ``e² = 1 − (b/a)²``:
    ``A = (p0/E*)(b/(a²e²))[K(e) − E(e)]``, ``B = (p0/E*)(b/(a²e²))[(a²/b²)E(e) − K(e)]``,
    ``δ = (p0/E*) b K(e)`` and ``F = (2/3)π a b p0``.
    """
    if not (F > 0 and A > 0 and B > 0 and Es > 0):
        raise ValueError("F, A, B and E* must be positive")
    if B < A:
        A, B = B, A
    if math.isclose(A, B, rel_tol=1e-12):
        R = 1 / (2 * A)
        a = (3 * F * R / (4 * Es)) ** (1 / 3)
        p0 = 3 * F / (2 * math.pi * a ** 2)
        return {"a": a, "b": a, "p0": p0, "delta": a ** 2 / R, "e": 0.0}
    target = B / A

    def ratio(k: float) -> float:       # k = b/a ∈ (0, 1)
        m = 1 - k ** 2
        K, E = special.ellipk(m), special.ellipe(m)
        return (E / k ** 2 - K) / (K - E) - target

    k = optimize.brentq(ratio, 1e-8, 1 - 1e-12, xtol=1e-15, rtol=1e-14, maxiter=500)
    m = 1 - k ** 2
    K, E = special.ellipk(m), special.ellipe(m)
    # with p0 = 3F/(2πab) in the A equation: A = 3F(K − E)/(2π a³ e² E*) → a³ = 3F(K − E)/(2π e² A E*)
    a = (3 * F * (K - E) / (2 * math.pi * m * A * Es)) ** (1 / 3)
    b = k * a
    p0 = 3 * F / (2 * math.pi * a * b)
    return {"a": a, "b": b, "p0": p0, "delta": p0 / Es * b * K, "e": math.sqrt(m)}


@cite("johnson_1985", note="crossed cylinders")
def cross_cylinder(F: float, R1: float, R2: float, E1: float, nu1: float, E2: float, nu2: float) -> dict[str, float]:
    """Two cylinders with perpendicular axes: ``A = 1/(2R_large)``, ``B = 1/(2R_small)``.

    Parameters
    ----------
    F : float
        Normal load [N].
    R1, R2 : float
        Cylinder radii [m].
    E1, nu1, E2, nu2 : float
        Elastic constants [Pa, -].

    Returns
    -------
    dict
        As :func:`hertz_elliptic`. With equal radii the contact is circular and identical to a sphere of
        radius R on a plane.

    Raises
    ------
    ValueError
        If a radius is not positive.
    """
    if not (R1 > 0 and R2 > 0):
        raise ValueError("radii must be positive")
    return hertz_elliptic(F, 1 / (2 * max(R1, R2)), 1 / (2 * min(R1, R2)), e_star(E1, nu1, E2, nu2))
