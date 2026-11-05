"""Rotating components: constant-thickness disk (solid / with a central hole), thin ring, rotating
bar / blade, speed limits, burst-speed estimate and an optional thermal-gradient term.

Sources:

- Disk (plane stress, constant thickness): Timoshenko & Goodier, Theory of Elasticity, Sec. 32;
  Shigley 10th ed. Ch. 3 rotating rings/disks (read in the Hijazi CH3 notes, p. 23; same relation).
- Thermal stress (axisymmetric T(r), thin disk): Timoshenko & Goodier Sec. 150.
- Burst speed, average hoop stress method: Robinson, E., "Bursting tests of steam-turbine disk wheels",
  Trans. ASME 66 (1944) p. 373 -- read as described in the NAFEMS NBC08 (2017) benchmark solution: the disk
  bursts when the area-weighted average hoop stress equals the tensile strength of the material; the
  stress scales with ω². The "material utilisation factor" η (≤ 1) is an optional correction (its value
  depends on material/geometry; the default here is 1.0 -- not a verified design value).

NOTE: Timoshenko & Goodier / Timoshenko / Hill section numbers were not verified from the books in this
session (general knowledge); the relations are tested through equilibrium, boundary conditions and limits.

SI units: ρ [kg/m³], ω [rad/s], radius [m], stress [Pa].
"""
from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import integrate

from aerokit.references import cite


def _check(rho: float, omega: float) -> None:
    """Raise ``ValueError`` unless ``rho > 0`` and ``omega ≥ 0``."""
    if not (rho > 0):
        raise ValueError("rho must be positive")
    if not (omega >= 0):
        raise ValueError("omega must not be negative")


def _r_array(r: ArrayLike, a: float, b: float) -> NDArray[np.float64]:
    """Return ``r`` as a float array after checking that it lies in ``[a, b]``."""
    r_arr = np.asarray(r, dtype=float)
    if np.any(r_arr < a * (1 - 1e-12)) or np.any(r_arr > b * (1 + 1e-12)):
        raise ValueError("r must lie within the disk radii")
    return r_arr


def _scalar(d: dict[str, Any], r: ArrayLike) -> dict[str, Any]:
    """Convert the arrays of ``d`` to floats when ``r`` is a scalar."""
    return {k: float(v) for k, v in d.items()} if np.ndim(r) == 0 else d


# --- disks -------------------------------------------------------------------------------------
@cite("timoshenko_goodier_1970", note="rotating disk of uniform thickness")
@cite("budynas_nisbett_2015", note="rotating rings, Ch. 3 (Hijazi CH3 notes p. 23)")
def solid_disk(rho: float, omega: float, b: float, nu: float, r: ArrayLike = 0.0,
               E: float | None = None) -> dict[str, Any]:
    """Solid rotating disk with a free outer edge (σr(b) = 0).

    Parameters
    ----------
    rho : float
        Density [kg/m³].
    omega : float
        Angular speed [rad/s].
    b : float
        Outer radius [m].
    nu : float
        Poisson's ratio [-].
    r : float or array_like
        Evaluation radius/radii in ``[0, b]`` [m].
    E : float, optional
        Young's modulus [Pa]; if given the radial displacement ``u`` [m] is returned too.

    Returns
    -------
    dict
        ``sr``, ``st`` [Pa] and optional ``u`` [m].

    Raises
    ------
    ValueError
        For invalid density, speed, radius or r outside the disk.

    Notes
    -----
    ``σr = (3+ν)/8 ρω²(b² − r²)``; ``σθ = ρω²[(3+ν)b² − (1+3ν)r²]/8``.
    At the centre ``σr = σθ = (3+ν)ρω²b²/8`` (maximum).
    """
    _check(rho, omega)
    if not (b > 0):
        raise ValueError("b must be positive")
    r_arr = _r_array(r, 0.0, b)
    k = rho * omega ** 2 / 8
    sr = (3 + nu) * k * (b ** 2 - r_arr ** 2)
    st = k * ((3 + nu) * b ** 2 - (1 + 3 * nu) * r_arr ** 2)
    d: dict[str, Any] = {"sr": sr, "st": st}
    if E is not None:
        d["u"] = r_arr * (st - nu * sr) / E
    return _scalar(d, r)


@cite("timoshenko_goodier_1970", note="rotating disk with a central hole")
@cite("budynas_nisbett_2015", note="rotating rings, Ch. 3 (Hijazi CH3 notes p. 23)")
def annular_disk(rho: float, omega: float, a: float, b: float, nu: float, r: ArrayLike | None = None,
                 E: float | None = None) -> dict[str, Any]:
    """Rotating disk with a central hole, both edges free (σr(a) = σr(b) = 0).

    Parameters
    ----------
    rho : float
        Density [kg/m³].
    omega : float
        Angular speed [rad/s].
    a, b : float
        Inner and outer radius [m], ``0 < a < b``.
    nu : float
        Poisson's ratio [-].
    r : float or array_like, optional
        Evaluation radius/radii in ``[a, b]`` (default: hole edge) [m].
    E : float, optional
        Young's modulus [Pa]; if given the radial displacement ``u`` [m] is returned too.

    Returns
    -------
    dict
        ``sr``, ``st`` [Pa] and optional ``u`` [m].

    Raises
    ------
    ValueError
        Unless ``0 < a < b`` and r lies in ``[a, b]``.

    Notes
    -----
    ``σr = (3+ν)/8 ρω²(a² + b² − a²b²/r² − r²)``,
    ``σθ = (3+ν)/8 ρω²(a² + b² + a²b²/r² − (1+3ν)/(3+ν) r²)``.
    The maximum σθ is at the hole edge: ``ρω²[(3+ν)b² + (1−ν)a²]/4``.
    """
    _check(rho, omega)
    if not (0 < a < b):
        raise ValueError("0 < a < b is required")
    r = a if r is None else r
    r_arr = _r_array(r, a, b)
    k = (3 + nu) * rho * omega ** 2 / 8
    sr = k * (a ** 2 + b ** 2 - a ** 2 * b ** 2 / r_arr ** 2 - r_arr ** 2)
    st = k * (a ** 2 + b ** 2 + a ** 2 * b ** 2 / r_arr ** 2 - (1 + 3 * nu) / (3 + nu) * r_arr ** 2)
    d: dict[str, Any] = {"sr": sr, "st": st}
    if E is not None:
        d["u"] = r_arr * (st - nu * sr) / E
    return _scalar(d, r)


def disk_max_stress(rho: float, omega: float, b: float, nu: float, a: float = 0.0) -> float:
    """Largest stress in a rotating disk (the hoop stress, at the centre or at the hole edge).

    Parameters
    ----------
    rho, omega, b, nu
        As in :func:`solid_disk`.
    a : float
        Hole radius [m]; 0 for a solid disk.

    Returns
    -------
    float
        Maximum hoop stress [Pa].
    """
    if a == 0:
        return solid_disk(rho, omega, b, nu, 0.0)["st"]
    return annular_disk(rho, omega, a, b, nu, a)["st"]


def mean_hoop_stress(rho: float, omega: float, b: float, a: float = 0.0, nu: float = 0.3,
                     numeric: bool = False) -> float:
    """Area-weighted (r-z section) average hoop stress of a constant-thickness disk.

    Parameters
    ----------
    rho, omega : float
        Density [kg/m³] and angular speed [rad/s].
    b, a : float
        Outer and hole radius [m] (``a = 0`` for a solid disk).
    nu : float
        Poisson's ratio [-] (used only when ``numeric=True``).
    numeric : bool
        If True, integrate the elastic solution numerically instead (independent check).

    Returns
    -------
    float
        Average hoop stress [Pa].

    Raises
    ------
    ValueError
        Unless ``0 ≤ a < b``.

    Notes
    -----
    From statics (half-disk equilibrium, σr zero at the edges): ``∫σθ dr = ρω²(b³ − a³)/3``, i.e.
    ``σθ_avg = ρω²(b³ − a³)/[3(b − a)]``, independent of ν.
    """
    _check(rho, omega)
    if not (0 <= a < b):
        raise ValueError("0 ≤ a < b is required")
    if not numeric:
        return rho * omega ** 2 * (b ** 3 - a ** 3) / (3 * (b - a))
    if a == 0:
        f = lambda r: solid_disk(rho, omega, b, nu, r)["st"]
    else:
        f = lambda r: annular_disk(rho, omega, a, b, nu, r)["st"]
    value, _ = integrate.quad(f, a, b, epsabs=0, epsrel=1e-12)
    return value / (b - a)


# --- ring and bar ------------------------------------------------------------------------------
@cite("timoshenko_1956", note="rotating ring")
def thin_ring(rho: float, omega: float, R: float) -> float:
    """Hoop stress of a thin rotating ring, ``σθ = ρω²R² = ρv²``.

    Parameters
    ----------
    rho : float
        Density [kg/m³].
    omega : float
        Angular speed [rad/s].
    R : float
        Mean radius [m].

    Returns
    -------
    float
        Hoop stress [Pa].
    """
    _check(rho, omega)
    return rho * (omega * R) ** 2


def rotating_bar(rho: float, omega: float, r_root: float, r_tip: float, r: ArrayLike | None = None,
                 tip_mass: float = 0.0, A: float | None = None) -> float | NDArray[np.float64]:
    """Axial centrifugal stress in a rotating bar / blade of constant cross-section.

    Parameters
    ----------
    rho : float
        Density [kg/m³].
    omega : float
        Angular speed [rad/s].
    r_root, r_tip : float
        Root and tip radius [m], ``0 ≤ r_root < r_tip``.
    r : float or array_like, optional
        Evaluation radius/radii (default: root, where the stress is maximum) [m].
    tip_mass : float
        Optional concentrated tip mass [kg].
    A : float, optional
        Cross-section area [m²]; required with a tip mass.

    Returns
    -------
    float or ndarray
        Stress [Pa].

    Raises
    ------
    ValueError
        For invalid radii, or a tip mass without area.

    Notes
    -----
    ``σ(r) = ρω²(r_tip² − r²)/2 + m_tip ω² r_tip / A``.
    """
    _check(rho, omega)
    if not (0 <= r_root < r_tip):
        raise ValueError("0 ≤ r_root < r_tip is required")
    r = r_root if r is None else r
    r_arr = _r_array(r, r_root, r_tip)
    s = rho * omega ** 2 * (r_tip ** 2 - r_arr ** 2) / 2
    if tip_mass:
        if not A:
            raise ValueError("a tip mass requires the cross-section area A")
        s = s + tip_mass * omega ** 2 * r_tip / A
    return float(s) if np.ndim(r) == 0 else s


# --- speed limits ------------------------------------------------------------------------------
def hoop_speed_limit(sigma_allowed: float, rho: float) -> float:
    """Allowable rim speed of a thin ring, ``v = √(σ/ρ)``.

    Parameters
    ----------
    sigma_allowed : float
        Allowable hoop stress [Pa].
    rho : float
        Density [kg/m³].

    Returns
    -------
    float
        Rim speed [m/s].

    Raises
    ------
    ValueError
        If an input is not positive.
    """
    if not (sigma_allowed > 0 and rho > 0):
        raise ValueError("positive values are required")
    return math.sqrt(sigma_allowed / rho)


def ring_speed_limit(sigma_allowed: float, rho: float, R: float) -> float:
    """Allowable angular speed of a thin ring.

    Parameters
    ----------
    sigma_allowed : float
        Allowable hoop stress [Pa].
    rho : float
        Density [kg/m³].
    R : float
        Ring radius [m].

    Returns
    -------
    float
        Angular speed [rad/s].
    """
    return hoop_speed_limit(sigma_allowed, rho) / R


def disk_speed_limit(sigma_allowed: float, rho: float, b: float, nu: float, a: float = 0.0) -> float:
    """Angular speed at which the largest (hoop) stress reaches ``sigma_allowed`` (elastic limit).

    Parameters
    ----------
    sigma_allowed : float
        Allowable stress [Pa].
    rho, b, nu, a
        As in :func:`disk_max_stress`.

    Returns
    -------
    float
        Angular speed [rad/s].
    """
    s1 = disk_max_stress(rho, 1.0, b, nu, a)      # ω = 1 rad/s
    return math.sqrt(sigma_allowed / s1)


@cite("robinson_1944")
@cite("nafems_nbc08_2017")
def burst_speed(Ftu: float, sigma_avg: float, omega: float, eta: float = 1.0) -> float:
    """Average-hoop-stress burst speed ``ω_b = ω √(η Ftu / σθ_avg(ω))``.

    Parameters
    ----------
    Ftu : float
        Ultimate tensile strength [Pa].
    sigma_avg : float
        Area-weighted average hoop stress at speed ``omega`` [Pa].
    omega : float
        Reference speed [rad/s].
    eta : float
        Material utilisation factor, ``0 < η ≤ 1`` (default 1; not a verified value -- take it from a
        source for design).

    Returns
    -------
    float
        Burst speed [rad/s].

    Raises
    ------
    ValueError
        For non-positive inputs or η outside (0, 1].
    """
    if not (Ftu > 0 and sigma_avg > 0 and omega > 0 and 0 < eta <= 1):
        raise ValueError("Ftu, sigma_avg, omega > 0 and 0 < eta ≤ 1 are required")
    return omega * math.sqrt(eta * Ftu / sigma_avg)


@cite("robinson_1944")
def disk_burst_speed(Ftu: float, rho: float, b: float, a: float = 0.0, eta: float = 1.0) -> float:
    """Burst speed of a constant-thickness disk (average hoop stress from statics).

    Parameters
    ----------
    Ftu : float
        Ultimate tensile strength [Pa].
    rho : float
        Density [kg/m³].
    b, a : float
        Outer and hole radius [m].
    eta : float
        Material utilisation factor [-].

    Returns
    -------
    float
        Burst speed [rad/s].
    """
    return burst_speed(Ftu, mean_hoop_stress(rho, 1.0, b, a), 1.0, eta)


# --- thermal gradient (optional) ---------------------------------------------------------------
@cite("timoshenko_goodier_1970", note="thermal stresses in a thin disk (Sec. 150, not verified in this session)")
def thermal_disk(T: Callable[[float], float], alpha: float, E: float, b: float, a: float = 0.0,
                 r: ArrayLike | None = None) -> dict[str, Any]:
    """Stresses in a thin disk due to an axisymmetric temperature change T(r) (plane stress, free edges).

    Parameters
    ----------
    T : callable
        Temperature change ``T(r)`` [K].
    alpha : float
        Thermal expansion coefficient [1/K].
    E : float
        Young's modulus [Pa].
    b, a : float
        Outer and hole radius [m] (``a = 0``: solid disk).
    r : float or array_like, optional
        Evaluation radius/radii (default: centre or hole edge) [m].

    Returns
    -------
    dict
        ``sr``, ``st`` [Pa]; floats for scalar r. May be superposed with the centrifugal stresses
        (linear elasticity).

    Raises
    ------
    ValueError
        Unless ``0 ≤ a < b``.

    Notes
    -----
    Solid disk:  ``σr = αE[(1/b²)∫₀ᵇ T r dr − (1/r²)∫₀ʳ T r dr]``,
    ``σθ = αE[(1/b²)∫₀ᵇ T r dr + (1/r²)∫₀ʳ T r dr − T]``.
    With hole: ``σr = (αE/r²)[(r² − a²)/(b² − a²)∫ₐᵇ T r dr − ∫ₐʳ T r dr]``,
    ``σθ = (αE/r²)[(r² + a²)/(b² − a²)∫ₐᵇ T r dr + ∫ₐʳ T r dr − T r²]``.
    """
    if not (0 <= a < b):
        raise ValueError("0 ≤ a < b is required")
    r = (a if a > 0 else 0.0) if r is None else r
    r_arr = np.atleast_1d(_r_array(r, a, b))
    I = lambda x0, x1: integrate.quad(lambda x: T(x) * x, x0, x1, epsabs=0, epsrel=1e-12)[0]
    Ib = I(a, b)
    sr, st = [], []
    for ri in r_arr:
        if a == 0:
            if ri == 0:      # limit: (1/r²)∫₀ʳ T r dr → T(0)/2
                inner = T(0.0) / 2
            else:
                inner = I(0.0, ri) / ri ** 2
            sr.append(alpha * E * (Ib / b ** 2 - inner))
            st.append(alpha * E * (Ib / b ** 2 + inner - T(ri)))
        else:
            Ir = I(a, ri)
            sr.append(alpha * E / ri ** 2 * ((ri ** 2 - a ** 2) / (b ** 2 - a ** 2) * Ib - Ir))
            st.append(alpha * E / ri ** 2 * ((ri ** 2 + a ** 2) / (b ** 2 - a ** 2) * Ib + Ir - T(ri) * ri ** 2))
    d = {"sr": np.array(sr), "st": np.array(st)}
    return {k: float(v[0]) for k, v in d.items()} if np.ndim(r) == 0 else d
