"""Beams and thin-walled sections: section properties, bending, torsion, buckling, margins.

Euler-Bernoulli beam, Bredt-Batho closed thin-walled section, Euler column and thin-plate buckling.
Everything is linear elastic with small strains. SI units throughout (N, m, Pa).

Section-property helpers return a dict with at least

* ``"A"`` -- cross-section area [m²],
* ``"I"`` -- second moment of area about the bending (horizontal) axis [m⁴],
* ``"c"`` -- distance from the neutral axis to the extreme fibre [m],

plus ``"J"`` (torsion constant [m⁴]) and ``"A_closed"`` (enclosed area [m²]) where defined.
"""
from __future__ import annotations

import math

from aerokit.references import cite


# --- section properties ------------------------------------------------------------------------
def rectangle(b: float, h: float) -> dict[str, float]:
    """Solid rectangle of width ``b`` and height ``h``.

    Parameters
    ----------
    b, h : float
        Width and height [m]; bending is about the axis parallel to ``b``.

    Returns
    -------
    dict
        ``A`` [m²], ``I = b h³/12`` [m⁴], ``c = h/2`` [m].

    Examples
    --------
    >>> rectangle(0.02, 0.04)["I"]  # doctest: +ELLIPSIS
    1.066...e-07
    """
    return {"A": b * h, "I": b * h ** 3 / 12, "c": h / 2}


def tube(D: float, t: float) -> dict[str, float]:
    """Circular tube of outer diameter ``D`` and wall thickness ``t``.

    Parameters
    ----------
    D, t : float
        Outer diameter and wall thickness [m] (``t = D/2`` gives a solid bar).

    Returns
    -------
    dict
        ``A`` [m²], ``I = π(D⁴ − d⁴)/64`` [m⁴], ``c = D/2`` [m] and polar moment
        ``J = π(D⁴ − d⁴)/32`` [m⁴], with ``d = D − 2t``.
    """
    d = D - 2 * t
    return {"A": math.pi / 4 * (D ** 2 - d ** 2), "I": math.pi / 64 * (D ** 4 - d ** 4),
            "c": D / 2, "J": math.pi / 32 * (D ** 4 - d ** 4)}


def i_section(b_flange: float, t_flange: float, h: float, t_web: float) -> dict[str, float]:
    """Doubly symmetric I-section.

    Parameters
    ----------
    b_flange, t_flange : float
        Flange width and thickness [m].
    h : float
        Overall height [m].
    t_web : float
        Web thickness [m].

    Returns
    -------
    dict
        ``A`` [m²], ``I`` about the strong axis [m⁴], ``c = h/2`` [m].

    Notes
    -----
    ``I = [b_f h³ − (b_f − t_w) h_w³]/12`` with clear web height ``h_w = h − 2 t_f``.
    """
    hw = h - 2 * t_flange
    A = 2 * b_flange * t_flange + hw * t_web
    I = (b_flange * h ** 3 - (b_flange - t_web) * hw ** 3) / 12
    return {"A": A, "I": I, "c": h / 2}


@cite("bredt_1896", note="J = 4A²/∮ds/t")
def box(b: float, h: float, t_upper: float, t_side: float) -> dict[str, float]:
    """Thin-walled rectangular box beam (wing-box idealisation), mid-line dimensions.

    Parameters
    ----------
    b : float
        Box width (chordwise) [m].
    h : float
        Box height [m].
    t_upper : float
        Skin / flange thickness of the upper and lower covers [m].
    t_side : float
        Spar web thickness of the two sides [m].

    Returns
    -------
    dict
        ``A`` (wall area) [m²], ``I`` (thin-wall approximation) [m⁴], ``c = h/2`` [m],
        ``A_closed = b h`` (enclosed area) [m²] and Bredt torsion constant ``J`` [m⁴].

    Notes
    -----
    ``I = 2 b t_u (h/2)² + 2 t_s h³/12`` and ``J = 4 A_closed² / ∮ ds/t`` with
    ``∮ ds/t = 2b/t_u + 2h/t_s``.
    """
    I = 2 * b * t_upper * (h / 2) ** 2 + 2 * t_side * h ** 3 / 12
    A_closed = b * h
    integral = 2 * b / t_upper + 2 * h / t_side          # ∮ ds/t
    J = 4 * A_closed ** 2 / integral
    return {"A": 2 * b * t_upper + 2 * h * t_side, "I": I, "c": h / 2,
            "A_closed": A_closed, "J": J}


# --- stresses ----------------------------------------------------------------------------------
def bending_stress(M: float, section: dict[str, float]) -> float:
    """Extreme-fibre bending stress ``σ = M c / I``.

    Parameters
    ----------
    M : float
        Bending moment [N·m].
    section : dict
        Section properties with keys ``"c"`` [m] and ``"I"`` [m⁴] (e.g. from :func:`box`).

    Returns
    -------
    float
        Bending stress [Pa].
    """
    return M * section["c"] / section["I"]


@cite("bredt_1896")
def bredt_shear_flow(T: float, A_closed: float) -> float:
    """Torsional shear flow in a closed thin-walled section, ``q = T/(2A)``.

    Parameters
    ----------
    T : float
        Torque [N·m].
    A_closed : float
        Area enclosed by the wall mid-line [m²].

    Returns
    -------
    float
        Shear flow [N/m].
    """
    return T / (2 * A_closed)


@cite("bredt_1896")
def bredt_shear_stress(T: float, A_closed: float, t: float) -> float:
    """Torsional shear stress ``τ = T/(2 A t)`` in a closed thin-walled section.

    Parameters
    ----------
    T : float
        Torque [N·m].
    A_closed : float
        Enclosed area [m²].
    t : float
        Local wall thickness [m].

    Returns
    -------
    float
        Shear stress [Pa].
    """
    return bredt_shear_flow(T, A_closed) / t


def mean_shear(V: float, A_web: float) -> float:
    """Approximate spar-web shear stress ``V / A_web`` (the web carries all of the shear force).

    Parameters
    ----------
    V : float
        Shear force [N].
    A_web : float
        Web area [m²].

    Returns
    -------
    float
        Mean shear stress [Pa].
    """
    return V / A_web


# --- buckling ----------------------------------------------------------------------------------
@cite("timoshenko_gere_1961", note="Euler column")
def euler_column(E: float, I: float, L: float, K: float = 1.0) -> float:
    """Euler critical load ``P_cr = π² E I / (K L)²``.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    I : float
        Second moment of area [m⁴].
    L : float
        Column length [m].
    K : float
        Effective-length factor: 1 pinned-pinned, 0.5 fixed-fixed, 2 fixed-free, 0.699 fixed-pinned.

    Returns
    -------
    float
        Critical load [N].

    Examples
    --------
    >>> round(euler_column(1.0, 1.0, 1.0), 6)
    9.869604
    """
    return math.pi ** 2 * E * I / (K * L) ** 2


@cite("timoshenko_gere_1961", note="buckling of simply supported rectangular plates")
def plate_buckling(E: float, nu: float, t: float, b: float, k: float = 4.0) -> float:
    """Compressive buckling stress of a thin plate, ``σ_cr = k π² E / (12(1 − ν²)) · (t/b)²``.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    t : float
        Plate thickness [m].
    b : float
        Loaded-edge width [m].
    k : float
        Buckling coefficient; 4.0 is the classical value for a long plate simply supported on all four
        edges under uniaxial compression.

    Returns
    -------
    float
        Critical stress [Pa].
    """
    return k * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t / b) ** 2


@cite("nasa_sp8007", note="Eqs. (5)-(6) axial, (9)-(10) bending")
def sp8007_reduction(r: float, t: float, loading: str = "axial") -> float:
    """NASA SP-8007 knock-down factor γ for isotropic cylinders (valid for r/t < 1500).

    Parameters
    ----------
    r : float
        Cylinder radius [m].
    t : float
        Wall thickness [m].
    loading : {"axial", "bending"}
        Load case; any value other than ``"axial"`` is treated as bending.

    Returns
    -------
    float
        Knock-down factor γ [-].

    Raises
    ------
    ValueError
        If ``r/t ≥ 1500``.

    Notes
    -----
    Axial: ``γ = 1 − 0.901(1 − e^−φ)``; bending: ``γ = 1 − 0.731(1 − e^−φ)``; ``φ = √(r/t)/16``.
    """
    if r / t >= 1500:
        raise ValueError("the SP-8007 relation is valid for r/t < 1500")
    phi = math.sqrt(r / t) / 16
    k = 0.901 if loading == "axial" else 0.731
    return 1 - k * (1 - math.exp(-phi))


# --- design margin -----------------------------------------------------------------------------
@cite("bruhn_1973", note="margin-of-safety definition")
def safety_margin(allowable: float, applied: float, FS: float = 1.0) -> float:
    """Margin of safety ``MS = allowable / (FS · |applied|) − 1``; ``MS ≥ 0`` is acceptable.

    Parameters
    ----------
    allowable : float
        Allowable load or stress (same unit as ``applied``).
    applied : float
        Applied load or stress; its sign is ignored.
    FS : float
        Factor of safety applied to ``applied``.

    Returns
    -------
    float
        Margin of safety [-]; ``math.inf`` when ``applied == 0``.

    Examples
    --------
    >>> round(safety_margin(400.0, 200.0, 1.5), 4)
    0.3333
    """
    return math.inf if applied == 0 else allowable / (FS * abs(applied)) - 1
