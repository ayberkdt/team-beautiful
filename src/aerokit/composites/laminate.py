"""Composite mechanics: micromechanics, lamina, laminate, hygrothermal effects, plane-stress
failure criteria, progressive failure, orthotropic plate buckling and sandwich basics.

Conventions
-----------
* SI units throughout (Pa, m, N/m, N·m/m, 1/°C).
* Voigt order [1, 2, 12] in material axes and [x, y, xy] in global axes; shear strain is the
  engineering strain γ.
* Compressive strengths (Xc, Yc) are entered as POSITIVE magnitudes.
* Stacking sequence from bottom to top ``[(angle_deg, thickness_m), ...]`` (same z rule as
  :func:`aerokit.composites.lamina.abd`: z = −h/2 is the bottom face).

Material dictionaries use the keys ``E1, E2, nu12, G12``; strengths ``Xt, Xc, Yt, Yc, S12``
(or ``S``); optional ``alpha1, alpha2, beta1, beta2``. Records of
:mod:`aerokit.materials.library` work directly.

Sources read for this module (labels used in the comments below):

* [Kaw]  A. K. Kaw, Mechanics of Composite Materials, 2nd ed., CRC 2006 — the author's worked
  examples (kaw.eng.usf.edu/compositesOCW, Sections 2.4-5.3).
* [DC03] C. G. Dávila, P. P. Camanho, "Failure Criteria for FRP Laminates in Plane Stress",
  NASA/TM-2003-212663 (LaRC03; Table 1 gives the plane-stress forms of Hashin 1980).
* [GC19] J. Gu, P. Chen, Materials 12 (2019) 3292 — Puck parameter recommendations (citing
  Puck, Kopp & Knops 2002) and the p⊥⊥ relation.
* [ALT]  Altair HyperView Result Math documentation, "Puck Criteria (2D)" and "Hoffman".
* [MIL]  MIL-HDBK-17-3F, Volume 3, §5.7.1 (2002) — orthotropic plate buckling.
* [LEY]  R. P. Ley, W. Lin, U. Mbanefo, NASA/CR-1999-208994 — face-sheet wrinkling.

Primary sources that are cited but were not read are marked as such in each function.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.composites.lamina import Q_matrix, Qbar, T_strain, T_stress
from aerokit.references import cite

Material = Mapping[str, Any]
"""Material record: ``E1, E2, nu12, G12`` [Pa, -], strengths ``Xt, Xc, Yt, Yc, S12`` [Pa], optional
``alpha1, alpha2`` [1/°C] and ``beta1, beta2`` [-]."""
Ply = dict[str, Any]
"""Ply record produced by :func:`layers`: ``angle`` [deg], ``t`` [m], ``m`` (material)."""
Array = NDArray[Any]

MSI = 6.894757293168e9  # 1 Msi → Pa

# ---------------------------------------------------------------- reference materials
KAW_GLASS_EPOXY = {
    "name": "Kaw Table 2.1 glass/epoxy UD", "E1": 38.6e9, "E2": 8.27e9, "nu12": 0.26, "G12": 4.14e9,
    "Xt": 1062e6, "Xc": 610e6, "Yt": 31e6, "Yc": 118e6, "S12": 72e6,
    "alpha1": 8.6e-6, "alpha2": 22.1e-6, "beta1": 0.0, "beta2": 0.6,
    "source": "[Kaw] Table 2.1, worked examples 2.4-2.8, 4.5, 5.3 and the 'beta angle ply' example",
}
KAW_BORON_EPOXY = {
    "name": "Kaw Table 2.2 boron/epoxy UD", "E1": 29.59 * MSI, "E2": 2.683 * MSI, "nu12": 0.23,
    "G12": 0.811 * MSI, "source": "[Kaw] solution of Problem 2.29 (Table 2.2 values, Msi)",
}
KAW_GLASS_FIBER = {"E": 85e9, "nu": 0.2, "G": 35.42e9, "alpha": 5e-6, "rho": 2500.0, "beta": 0.0,
                   "source": "[Kaw] Table 3.1 (worked examples 3.3, 3.5, 3.6)"}
KAW_EPOXY = {"E": 3.4e9, "nu": 0.3, "G": 1.308e9, "alpha": 63e-6, "rho": 1200.0, "beta": 0.33,
             "source": "[Kaw] Table 3.2 (worked examples 3.3, 3.5, 3.6)"}

# Puck inclination parameters (p⊥∥(+), p⊥∥(−)). CFRP: [GC19] (citing Puck, Kopp & Knops 2002) — read.
# GFRP: [ALT] table (0.30/0.25); the row labels of that table are ambiguous in the text and were assumed
# to follow the CFRP ordering → partially verified. The primary source (Puck et al. 2002, VDI 2014) was
# not read.
PUCK_SLOPE = {"CFRP": (0.35, 0.30), "GFRP": (0.30, 0.25)}


def _positive(name: str, value: Any) -> float:
    """Return ``value`` as float after checking that it is a positive finite number."""
    if not (isinstance(value, int | float | np.floating) and math.isfinite(value) and value > 0):
        raise ValueError(f"{name} must be positive and finite (got {value})")
    return float(value)


def _elastic(m: Material) -> tuple[float, float, float, float]:
    """Validated (E1, E2, nu12, G12); thermodynamic condition |ν12| < √(E1/E2)."""
    E1, E2, G12 = _positive("E1", m["E1"]), _positive("E2", m["E2"]), _positive("G12", m["G12"])
    nu12 = float(m["nu12"])
    if not abs(nu12) < math.sqrt(E1 / E2):
        raise ValueError(f"|ν12| = {abs(nu12)} ≥ √(E1/E2): Q is not positive definite")
    return E1, E2, nu12, G12


def _strengths(m: Material) -> tuple[float, float, float, float, float]:
    """Validated (Xt, Xc, Yt, Yc, S), all positive magnitudes."""
    S = m.get("S12", m.get("S"))
    return (_positive("Xt", m["Xt"]), _positive("Xc", m["Xc"]), _positive("Yt", m["Yt"]),
            _positive("Yc", m["Yc"]), _positive("S12", S))


def Q_material(m: Material) -> Array:
    """Reduced stiffness matrix Q of a material record (see :func:`aerokit.composites.lamina.Q_matrix`).

    Parameters
    ----------
    m : mapping
        Material record with ``E1, E2, nu12, G12`` [Pa, Pa, -, Pa].

    Returns
    -------
    ndarray, shape (3, 3)
        Q in material axes [Pa].

    Raises
    ------
    ValueError
        If a modulus is not positive or |ν12| ≥ √(E1/E2).
    """
    return Q_matrix(*_elastic(m))


# ---------------------------------------------------------------- 1. micromechanics
def _vf(Vf: float) -> float:
    """Validated fibre volume fraction in [0, 1]."""
    if not 0.0 <= Vf <= 1.0:
        raise ValueError(f"fibre volume fraction must be in 0-1 (got {Vf})")
    return float(Vf)


@cite("kaw_2006", note="§3.3, mechanics-of-materials approach")
def rom_E1(Ef: float, Em: float, Vf: float) -> float:
    """Longitudinal modulus by the rule of mixtures (Voigt bound), E1 = Ef·Vf + Em·Vm.

    Parameters
    ----------
    Ef, Em : float
        Fibre and matrix Young's moduli [Pa].
    Vf : float
        Fibre volume fraction [-], Vm = 1 − Vf.

    Returns
    -------
    float
        E1 [Pa].

    Raises
    ------
    ValueError
        If Vf is outside [0, 1].

    Examples
    --------
    >>> round(rom_E1(85e9, 3.4e9, 0.6) / 1e9, 2)
    52.36
    """
    Vf = _vf(Vf)
    return Ef * Vf + Em * (1 - Vf)


@cite("kaw_2006", note="§3.3")
def rom_nu12(nuf: float, num: float, Vf: float) -> float:
    """Major Poisson's ratio by the rule of mixtures, ν12 = νf·Vf + νm·Vm.

    Parameters
    ----------
    nuf, num : float
        Fibre and matrix Poisson's ratios [-].
    Vf : float
        Fibre volume fraction [-].

    Returns
    -------
    float
        ν12 [-].

    Raises
    ------
    ValueError
        If Vf is outside [0, 1].
    """
    Vf = _vf(Vf)
    return nuf * Vf + num * (1 - Vf)


@cite("kaw_2006", note="§3.3")
def inverse_rom(Mf: float, Mm: float, Vf: float) -> float:
    """Inverse rule of mixtures (Reuss bound), 1/M = Vf/Mf + Vm/Mm, for E2 or G12.

    Parameters
    ----------
    Mf, Mm : float
        Fibre and matrix modulus (Young's or shear) [Pa].
    Vf : float
        Fibre volume fraction [-].

    Returns
    -------
    float
        Composite modulus M [Pa].

    Raises
    ------
    ValueError
        If Vf is outside [0, 1] or a modulus is not positive.
    """
    Vf = _vf(Vf)
    return 1.0 / (Vf / _positive("Mf", Mf) + (1 - Vf) / _positive("Mm", Mm))


@cite("halpin_kardos_1976", "kaw_2006", note="Kaw §3.3: ξ values for circular and rectangular fibres")
def halpin_tsai(Mf: float, Mm: float, Vf: float, xi: float) -> float:
    """Halpin-Tsai estimate of a transverse or shear modulus.

    Parameters
    ----------
    Mf, Mm : float
        Fibre and matrix modulus [Pa].
    Vf : float
        Fibre volume fraction [-].
    xi : float
        Reinforcing factor ξ ≥ 0 [-].

    Returns
    -------
    float
        Composite modulus M [Pa].

    Raises
    ------
    ValueError
        If Vf is outside [0, 1], ξ < 0 or a modulus is not positive.

    Notes
    -----
    M/Mm = (1 + ξηVf)/(1 − ηVf),  η = (Mf/Mm − 1)/(Mf/Mm + ξ).

    [Kaw] §3.3: circular fibres in a square array → ξ = 2 for E2 and ξ = 1 for G12; rectangular
    fibre cross-section a×b → ξ = 2a/b for E2 and ξ = √3·ln(a/b) for G12.
    ξ → ∞ gives the rule of mixtures and ξ → 0 the inverse rule of mixtures.
    """
    Vf = _vf(Vf)
    if xi < 0:
        raise ValueError("ξ must not be negative")
    r = _positive("Mf", Mf) / _positive("Mm", Mm)
    eta = (r - 1) / (r + xi)
    return Mm * (1 + xi * eta * Vf) / (1 - eta * Vf)


@cite("kaw_2006", note="§3.3-3.6")
def micromechanics(fiber: Mapping[str, Any], matrix: Mapping[str, Any], Vf: float, method: str = "halpin_tsai",
                   xi_E2: float = 2.0, xi_G12: float = 1.0) -> dict[str, float]:
    """Unidirectional ply constants from fibre and matrix properties.

    Parameters
    ----------
    fiber, matrix : mapping
        Constituent records with ``E`` [Pa] and ``nu`` [-]; optional ``G`` [Pa] (default
        E/(2(1+ν))), ``rho`` [kg/m³], ``alpha`` [1/°C] and ``beta`` [-].
    Vf : float
        Fibre volume fraction [-].
    method : {"halpin_tsai", "inverse_rom"}, optional
        Model for E2 and G12 (E1 and ν12 always use the rule of mixtures).
    xi_E2, xi_G12 : float, optional
        Halpin-Tsai reinforcing factors for E2 and G12 [-].

    Returns
    -------
    dict
        ``E1, E2, G12`` [Pa], ``nu12`` [-], ``Vf`` [-]; if both constituents have ``rho``:
        ``rho`` [kg/m³]; if both have ``alpha``: ``alpha1, alpha2`` [1/°C]; if the matrix has
        ``beta``, the fibre absorbs no moisture and ``rho`` is known: ``beta1, beta2`` [-].

    Raises
    ------
    ValueError
        For an unknown ``method`` or Vf outside [0, 1].
    """
    Ef, Em = fiber["E"], matrix["E"]
    Gf = fiber.get("G", Ef / (2 * (1 + fiber["nu"])))
    Gm = matrix.get("G", Em / (2 * (1 + matrix["nu"])))
    E1 = rom_E1(Ef, Em, Vf)
    nu12 = rom_nu12(fiber["nu"], matrix["nu"], Vf)
    if method == "halpin_tsai":
        E2, G12 = halpin_tsai(Ef, Em, Vf, xi_E2), halpin_tsai(Gf, Gm, Vf, xi_G12)
    elif method == "inverse_rom":
        E2, G12 = inverse_rom(Ef, Em, Vf), inverse_rom(Gf, Gm, Vf)
    else:
        raise ValueError("method must be 'halpin_tsai' or 'inverse_rom'")
    m = {"E1": E1, "E2": E2, "nu12": nu12, "G12": G12, "Vf": Vf}
    if "rho" in fiber and "rho" in matrix:
        m["rho"] = density([(fiber["rho"], Vf), (matrix["rho"], 1 - Vf)])
    if "alpha" in fiber and "alpha" in matrix:
        m["alpha1"] = alpha1_micro(Ef, Em, fiber["alpha"], matrix["alpha"], Vf)
        m["alpha2"] = alpha2_micro(fiber["nu"], matrix["nu"], fiber["alpha"], matrix["alpha"], Vf,
                                   m["alpha1"], nu12)
    if matrix.get("beta") is not None and "rho" in m and fiber.get("beta", 0.0) == 0.0:
        m["beta1"] = beta1_micro(Em, E1, m["rho"], matrix["rho"], matrix["beta"])
        m["beta2"] = beta2_micro(matrix["nu"], m["rho"], matrix["rho"], matrix["beta"], m["beta1"], nu12)
    return m


@cite("schapery_1968", "kaw_2006", note="Kaw §3.5 (Schapery form)")
def alpha1_micro(Ef: float, Em: float, af: float, am: float, Vf: float) -> float:
    """Longitudinal coefficient of thermal expansion, α1 = (αf Ef Vf + αm Em Vm)/E1.

    Parameters
    ----------
    Ef, Em : float
        Fibre and matrix Young's moduli [Pa].
    af, am : float
        Fibre and matrix CTE [1/°C].
    Vf : float
        Fibre volume fraction [-].

    Returns
    -------
    float
        α1 [1/°C].
    """
    Vf = _vf(Vf)
    return (af * Ef * Vf + am * Em * (1 - Vf)) / rom_E1(Ef, Em, Vf)


@cite("schapery_1968", "kaw_2006", note="Kaw §3.5")
def alpha2_micro(nuf: float, num: float, af: float, am: float, Vf: float, alpha1: float, nu12: float) -> float:
    """Transverse coefficient of thermal expansion, α2 = (1+νf)αf Vf + (1+νm)αm Vm − α1 ν12.

    Parameters
    ----------
    nuf, num : float
        Fibre and matrix Poisson's ratios [-].
    af, am : float
        Fibre and matrix CTE [1/°C].
    Vf : float
        Fibre volume fraction [-].
    alpha1 : float
        Longitudinal CTE of the ply [1/°C] (see :func:`alpha1_micro`).
    nu12 : float
        Major Poisson's ratio of the ply [-].

    Returns
    -------
    float
        α2 [1/°C].
    """
    Vf = _vf(Vf)
    return (1 + nuf) * af * Vf + (1 + num) * am * (1 - Vf) - alpha1 * nu12


@cite("kaw_2006", note="§3.6")
def beta1_micro(Em: float, E1: float, rho_c: float, rho_m: float, beta_m: float) -> float:
    """Longitudinal coefficient of moisture expansion, β1 = (Em/E1)(ρc/ρm) βm.

    Assumes the fibre absorbs no moisture.

    Parameters
    ----------
    Em, E1 : float
        Matrix and ply longitudinal moduli [Pa].
    rho_c, rho_m : float
        Composite and matrix densities [kg/m³].
    beta_m : float
        Matrix coefficient of moisture expansion [-].

    Returns
    -------
    float
        β1 [-].
    """
    return Em / E1 * rho_c / rho_m * beta_m


@cite("kaw_2006", note="§3.6")
def beta2_micro(num: float, rho_c: float, rho_m: float, beta_m: float, beta1: float, nu12: float) -> float:
    """Transverse coefficient of moisture expansion, β2 = (1+νm)(ρc/ρm) βm − β1 ν12.

    Parameters
    ----------
    num : float
        Matrix Poisson's ratio [-].
    rho_c, rho_m : float
        Composite and matrix densities [kg/m³].
    beta_m : float
        Matrix coefficient of moisture expansion [-].
    beta1 : float
        Longitudinal coefficient of the ply [-] (see :func:`beta1_micro`).
    nu12 : float
        Major Poisson's ratio of the ply [-].

    Returns
    -------
    float
        β2 [-].
    """
    return (1 + num) * rho_c / rho_m * beta_m - beta1 * nu12


@cite("kaw_2006", note="§3.2")
def density(components: Sequence[tuple[float, float]]) -> float:
    """Composite density from volume fractions, ρc = Σ ρi Vi.

    Parameters
    ----------
    components : sequence of (float, float)
        ``[(rho_i [kg/m³], V_i [-]), ...]`` with ΣV = 1.

    Returns
    -------
    float
        ρc [kg/m³].

    Raises
    ------
    ValueError
        If the volume fractions do not sum to 1.

    Examples
    --------
    >>> density([(2600, 0.4), (1800, 0.2), (1200, 0.4)])
    1880.0
    """
    if abs(sum(V for _, V in components) - 1) > 1e-9:
        raise ValueError("volume fractions must sum to 1")
    return sum(r * V for r, V in components)


@cite("kaw_2006", note="§3.2")
def mass_fractions(components: Sequence[tuple[float, float]]) -> list[float]:
    """Mass fractions from volume fractions, Mi = ρi Vi / ρc.

    Parameters
    ----------
    components : sequence of (float, float)
        ``[(rho_i [kg/m³], V_i [-]), ...]`` with ΣV = 1.

    Returns
    -------
    list of float
        Mass fractions Mi [-] in input order.

    Raises
    ------
    ValueError
        If the volume fractions do not sum to 1.
    """
    rc = density(components)
    return [r * V / rc for r, V in components]


@cite("kaw_2006", note="§3.2")
def volume_fractions(components: Sequence[tuple[float, float]]) -> list[float]:
    """Volume fractions from mass fractions, Vi = (Mi/ρi) / Σ(Mj/ρj).

    Parameters
    ----------
    components : sequence of (float, float)
        ``[(rho_i [kg/m³], M_i [-]), ...]`` with ΣM = 1.

    Returns
    -------
    list of float
        Volume fractions Vi [-] in input order.

    Raises
    ------
    ValueError
        If the mass fractions do not sum to 1.
    """
    if abs(sum(M for _, M in components) - 1) > 1e-9:
        raise ValueError("mass fractions must sum to 1")
    s = sum(M / r for r, M in components)
    return [(M / r) / s for r, M in components]


@cite("kaw_2006", note="§3.2")
def theoretical_density_from_mass(components: Sequence[tuple[float, float]]) -> float:
    """Theoretical (void-free) density from mass fractions, 1/ρc = Σ Mi/ρi.

    Parameters
    ----------
    components : sequence of (float, float)
        ``[(rho_i [kg/m³], M_i [-]), ...]`` with ΣM = 1.

    Returns
    -------
    float
        ρc [kg/m³].

    Raises
    ------
    ValueError
        If the mass fractions do not sum to 1.
    """
    if abs(sum(M for _, M in components) - 1) > 1e-9:
        raise ValueError("mass fractions must sum to 1")
    return 1.0 / sum(M / r for r, M in components)


@cite("kaw_2006", note="§3.2, Problem 3.3")
def void_ratio(rho_theoretical: float, rho_experimental: float) -> float:
    """Void volume fraction, Vv = (ρ_theoretical − ρ_experimental)/ρ_theoretical.

    Parameters
    ----------
    rho_theoretical, rho_experimental : float
        Theoretical and measured densities [kg/m³].

    Returns
    -------
    float
        Vv [-].
    """
    return (rho_theoretical - rho_experimental) / rho_theoretical


# ---------------------------------------------------------------- 2. lamina
@cite("kaw_2006", note="§2.4")
def S_matrix(E1: float, E2: float, nu12: float, G12: float) -> Array:
    """Reduced compliance matrix S = Q⁻¹ of a ply in plane stress (material axes).

    Parameters
    ----------
    E1, E2 : float
        Longitudinal and transverse moduli [Pa].
    nu12 : float
        Major Poisson's ratio [-].
    G12 : float
        In-plane shear modulus [Pa].

    Returns
    -------
    ndarray, shape (3, 3)
        S with ε_12 = S σ_12 [1/Pa].

    Raises
    ------
    ValueError
        If a modulus is not positive or |ν12| ≥ √(E1/E2).
    """
    _elastic({"E1": E1, "E2": E2, "nu12": nu12, "G12": G12})
    return np.array([[1 / E1, -nu12 / E1, 0],
                     [-nu12 / E1, 1 / E2, 0],
                     [0, 0, 1 / G12]])


@cite("kaw_2006", note="§2.5, Eq. 2.106")
def Sbar(S: ArrayLike, theta: float) -> Array:
    """Transformed compliance S̄ = T_ε⁻¹ S T_σ, so that ε_xy = S̄ σ_xy.

    Parameters
    ----------
    S : array_like, shape (3, 3)
        Compliance in material axes [1/Pa].
    theta : float
        Ply angle [deg].

    Returns
    -------
    ndarray, shape (3, 3)
        S̄ in global axes [1/Pa].
    """
    return np.linalg.solve(T_strain(theta), np.asarray(S, dtype=float) @ T_stress(theta))


@cite("kaw_2006", "jones_1999", note="Kaw §2.6; mutual-influence coefficients per the Lekhnitskii/Jones "
      "definition (not read from the source in this repository)")
def axis_off_constants(E1: float, E2: float, nu12: float, G12: float, theta: float) -> dict[str, Any]:
    """Engineering constants of an off-axis (angle) ply.

    Parameters
    ----------
    E1, E2, G12 : float
        Ply moduli [Pa].
    nu12 : float
        Major Poisson's ratio [-].
    theta : float
        Ply angle [deg].

    Returns
    -------
    dict
        ``Ex, Ey, Gxy`` [Pa]; ``nuxy, nuyx`` [-]; Kaw's shear coupling coefficients ``mx, my`` [-];
        mutual-influence coefficients ``eta_xy_x, eta_xy_y, eta_x_xy, eta_y_xy`` [-];
        ``Sbar`` (3, 3) [1/Pa].

    Notes
    -----
    Ex = 1/S̄11, Ey = 1/S̄22, Gxy = 1/S̄66, νxy = −S̄12/S̄11, νyx = −S̄12/S̄22;
    Kaw shear coupling coefficients mx = −S̄16·E1, my = −S̄26·E1;
    mutual-influence coefficients η_xy,x = S̄16/S̄11 (γxy/εx under σx), η_xy,y = S̄26/S̄22,
    η_x,xy = S̄16/S̄66 (εx/γxy under τxy), η_y,xy = S̄26/S̄66.
    """
    Sb = Sbar(S_matrix(E1, E2, nu12, G12), theta)
    return {"Ex": 1 / Sb[0, 0], "Ey": 1 / Sb[1, 1], "Gxy": 1 / Sb[2, 2],
            "nuxy": -Sb[0, 1] / Sb[0, 0], "nuyx": -Sb[0, 1] / Sb[1, 1],
            "mx": -Sb[0, 2] * E1, "my": -Sb[1, 2] * E1,
            "eta_xy_x": Sb[0, 2] / Sb[0, 0], "eta_xy_y": Sb[1, 2] / Sb[1, 1],
            "eta_x_xy": Sb[0, 2] / Sb[2, 2], "eta_y_xy": Sb[1, 2] / Sb[2, 2], "Sbar": Sb}


@cite("kaw_2006", note="§2.9")
def alpha_global(a1: float, a2: float, theta: float, a12: float = 0.0) -> Array:
    """Expansion coefficients of a ply in global axes.

    Parameters
    ----------
    a1, a2 : float
        Coefficients in material axes [1/°C] (or [-] for moisture β).
    theta : float
        Ply angle [deg].
    a12 : float, optional
        Engineering shear coefficient in material axes (normally 0).

    Returns
    -------
    ndarray, shape (3,)
        [αx, αy, αxy] with αxy the engineering shear coefficient.

    Notes
    -----
    [αx, αy, αxy/2] = T⁻¹ [α1, α2, α12/2]. The same transformation is used for the moisture
    coefficients β.
    """
    v = np.linalg.solve(T_stress(theta), np.array([a1, a2, a12 / 2]))
    return np.array([v[0], v[1], 2 * v[2]])


# ---------------------------------------------------------------- 3. laminate
def layers(material: Material | None, sequence: Sequence[Sequence[Any]]) -> list[Ply]:
    """Build validated ply records from a stacking sequence.

    Parameters
    ----------
    material : mapping or None
        Default material for plies that do not name their own.
    sequence : sequence
        ``[(angle_deg, t_m), ...]`` or ``[(angle_deg, t_m, material), ...]`` from bottom to top.

    Returns
    -------
    list of dict
        ``[{"angle": float [deg], "t": float [m], "m": material}, ...]`` from bottom to top.

    Raises
    ------
    ValueError
        If the sequence is empty, a thickness is not positive, a ply has no material or the
        material elastic constants are invalid.
    """
    if not sequence:
        raise ValueError("ply sequence is empty")
    ply = []
    for k in sequence:
        angle, t = float(k[0]), _positive("ply thickness", k[1])
        m = k[2] if len(k) > 2 else material
        if m is None:
            raise ValueError("no ply material given")
        _elastic(m)
        ply.append({"angle": angle, "t": t, "m": m})
    return ply


def _z_bounds(ply: Sequence[Ply]) -> tuple[float, list[float]]:
    """Total thickness h and ply interface coordinates z (−h/2 … +h/2)."""
    h = sum(k["t"] for k in ply)
    z = [-h / 2]
    for k in ply:
        z.append(z[-1] + k["t"])
    return h, z


@cite("kaw_2006", "reddy_2004", note="Kaw §4.3")
def abd_matrix(ply: Sequence[Ply]) -> tuple[Array, Array, Array, list[float]]:
    """A, B, D matrices using each ply's own stiffness.

    Parameters
    ----------
    ply : sequence of dict
        Ply records from :func:`layers` (an optional ``Q`` entry overrides the material).

    Returns
    -------
    A : ndarray, shape (3, 3)
        Extensional stiffness [N/m].
    B : ndarray, shape (3, 3)
        Coupling stiffness [N].
    D : ndarray, shape (3, 3)
        Bending stiffness [N·m].
    z : list of float
        Ply interface coordinates [m].

    Notes
    -----
    For a single material the result is identical to :func:`aerokit.composites.lamina.abd`.
    """
    h, z = _z_bounds(ply)
    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    D = np.zeros((3, 3))
    for i, k in enumerate(ply):
        Qb = Qbar(k.get("Q", Q_material(k["m"])), k["angle"])
        A += Qb * (z[i + 1] - z[i])
        B += Qb * (z[i + 1] ** 2 - z[i] ** 2) / 2
        D += Qb * (z[i + 1] ** 3 - z[i] ** 3) / 3
    return A, B, D, z


@cite("kaw_2006", note="§4.4")
def abd_inverse(A: ArrayLike, B: ArrayLike, D: ArrayLike) -> dict[str, Array]:
    """Inverse of the 6×6 laminate stiffness, [A B; B D]⁻¹ = [a b; c d] (the abd′ matrix).

    Parameters
    ----------
    A, B, D : array_like, shape (3, 3)
        Laminate stiffness blocks [N/m, N, N·m].

    Returns
    -------
    dict
        Blocks ``a`` [m/N], ``b`` [1/N], ``c`` (= bᵀ) [1/N], ``d`` [1/(N·m)] and the
        ``full`` 6×6 inverse.
    """
    T = np.linalg.inv(np.block([[A, B], [B, D]]))
    return {"a": T[:3, :3], "b": T[:3, 3:], "c": T[3:, :3], "d": T[3:, 3:], "full": T}


@cite("kaw_2006", note="§4.4")
def laminate_constants(ply: Sequence[Ply], bending_free: bool = False) -> dict[str, Any]:
    """Effective in-plane and flexural engineering constants of a laminate.

    Parameters
    ----------
    ply : sequence of dict
        Ply records from :func:`layers`.
    bending_free : bool, optional
        False (Kaw): a* = A⁻¹ and d* = D⁻¹ (B = 0 assumption). True: a* and d* are taken from the
        full ABD inverse (an unsymmetric laminate free to bend).

    Returns
    -------
    dict
        In-plane ``Ex, Ey, Gxy`` [Pa], ``nuxy, nuyx`` [-]; flexural ``Efx, Efy, Gfxy`` [Pa],
        ``nufxy, nufyx`` [-]; thickness ``h`` [m]; ``A, B, D`` and the used compliances ``a, d``.

    Notes
    -----
    In-plane: Ex = 1/(h a*11), Ey = 1/(h a*22), Gxy = 1/(h a*66), νxy = −a*12/a*11.
    Flexural: Ef_x = 12/(h³ d*11), Ef_y = 12/(h³ d*22), Gf_xy = 12/(h³ d*66), νf_xy = −d*12/d*11.
    """
    A, B, D, z = abd_matrix(ply)
    h = z[-1] - z[0]
    if bending_free:
        inverse = abd_inverse(A, B, D)
        a, d = inverse["a"], inverse["d"]
    else:
        a, d = np.linalg.inv(A), np.linalg.inv(D)
    return {"Ex": 1 / (h * a[0, 0]), "Ey": 1 / (h * a[1, 1]), "Gxy": 1 / (h * a[2, 2]),
            "nuxy": -a[0, 1] / a[0, 0], "nuyx": -a[0, 1] / a[1, 1],
            "Efx": 12 / (h ** 3 * d[0, 0]), "Efy": 12 / (h ** 3 * d[1, 1]),
            "Gfxy": 12 / (h ** 3 * d[2, 2]), "nufxy": -d[0, 1] / d[0, 0], "nufyx": -d[0, 1] / d[1, 1],
            "h": h, "A": A, "B": B, "D": D, "a": a, "d": d}


def symmetry_balance(ply: Sequence[Ply], tol: float = 1e-9) -> dict[str, bool]:
    """Symmetry and balance checks from the stacking sequence and from the stiffness.

    Parameters
    ----------
    ply : sequence of dict
        Ply records from :func:`layers`.
    tol : float, optional
        Relative tolerance for the zero tests on B, A16/A26 and D16/D26.

    Returns
    -------
    dict
        ``symmetric``: mirror plies about the mid-plane have the same (angle, t, material) → B = 0;
        ``balanced``: every +θ ply other than 0°/90° has a −θ counterpart of the same total
        thickness and material → A16 = A26 = 0;
        ``B_zero``, ``A16_A26_zero``: the corresponding stiffness terms vanish numerically;
        ``specially_orthotropic``: D16 = D26 = 0 (condition of the plate-buckling formula).
    """
    n = len(ply)
    sim = all(abs(ply[i]["angle"] - ply[n - 1 - i]["angle"]) < 1e-9
              and abs(ply[i]["t"] - ply[n - 1 - i]["t"]) < 1e-15
              and ply[i]["m"] is ply[n - 1 - i]["m"] for i in range(n // 2))
    total: dict[tuple[float, int], float] = {}
    for k in ply:
        a = ((k["angle"] + 90) % 180) - 90  # (−90, 90]
        if abs(a) < 1e-9 or abs(abs(a) - 90) < 1e-9:
            continue
        key = (abs(a), id(k["m"]))
        total[key] = total.get(key, 0.0) + math.copysign(k["t"], a)
    balanced = all(abs(v) < 1e-15 for v in total.values())
    A, B, D, _ = abd_matrix(ply)
    scale_A = abs(A[0, 0]) + abs(A[1, 1])
    scale_B = abs(A[0, 0]) * (_z_bounds(ply)[0])
    scale_D = abs(D[0, 0]) + abs(D[1, 1])
    return {"symmetric": sim, "balanced": balanced,
            "B_zero": float(np.max(np.abs(B))) <= tol * scale_B,
            "A16_A26_zero": max(abs(A[0, 2]), abs(A[1, 2])) <= tol * scale_A,
            "specially_orthotropic": max(abs(D[0, 2]), abs(D[1, 2])) <= tol * scale_D}


# ---------------------------------------------------------------- 4. hygrothermal
@cite("kaw_2006", note="§4.5")
def hygrothermal_loads(ply: Sequence[Ply], dT: float = 0.0, dC: float = 0.0) -> tuple[Array, Array]:
    """Fictitious thermal and moisture force and moment resultants.

    Parameters
    ----------
    ply : sequence of dict
        Ply records; materials need ``alpha1, alpha2`` if dT ≠ 0 and ``beta1, beta2`` if dC ≠ 0.
    dT : float, optional
        Temperature change ΔT [°C].
    dC : float, optional
        Moisture concentration change ΔC [-].

    Returns
    -------
    N : ndarray, shape (3,)
        N^T + N^C [N/m].
    M : ndarray, shape (3,)
        M^T + M^C [N·m/m].

    Raises
    ------
    KeyError
        If a required expansion coefficient is missing.

    Notes
    -----
    N = Σ Q̄ (αΔT + βΔC)(z_k − z_{k−1}),  M = ½ Σ Q̄ (αΔT + βΔC)(z_k² − z_{k−1}²).
    """
    h, z = _z_bounds(ply)
    N = np.zeros(3)
    M = np.zeros(3)
    for i, k in enumerate(ply):
        Qb = Qbar(k.get("Q", Q_material(k["m"])), k["angle"])
        e = _free_strain(k, dT, dC)
        N += Qb @ e * (z[i + 1] - z[i])
        M += Qb @ e * (z[i + 1] ** 2 - z[i] ** 2) / 2
    return N, M


def _free_strain(k: Ply, dT: float, dC: float) -> Array:
    """Unconstrained hygrothermal strain αΔT + βΔC of a ply in global axes."""
    m = k["m"]
    e = np.zeros(3)
    if dT:
        e += alpha_global(m["alpha1"], m["alpha2"], k["angle"]) * dT
    if dC:
        e += alpha_global(m["beta1"], m["beta2"], k["angle"]) * dC
    return e


@cite("kaw_2006", "reddy_2004", note="Kaw §4.3, §4.5")
def laminate_analysis(ply: Sequence[Ply], N: ArrayLike = (0, 0, 0), M: ArrayLike = (0, 0, 0),
                      dT: float = 0.0, dC: float = 0.0) -> dict[str, Any]:
    """Mechanical plus hygrothermal CLT solution with ply strains and stresses.

    Parameters
    ----------
    ply : sequence of dict
        Ply records from :func:`layers`.
    N : array_like, shape (3,), optional
        Force resultants [Nx, Ny, Nxy] [N/m].
    M : array_like, shape (3,), optional
        Moment resultants [Mx, My, Mxy] [N·m/m].
    dT, dC : float, optional
        Temperature change [°C] and moisture change [-].

    Returns
    -------
    dict
        ``eps0`` (3,) [-], ``kappa`` (3,) [1/m], ``NT``, ``MT`` hygrothermal resultants,
        ``A, B, D, z`` and ``layers``: one dict per ply with ``angle`` [deg] and ``points``,
        a dict with keys ``lower``, ``middle``, ``upper``, each holding ``z`` [m], ``eps_xy`` total
        global strain, ``eps_mech_xy`` mechanical global strain (total − free), ``sig_xy`` global
        stress [Pa], ``sig12`` material-axis stress [Pa] and ``eps12`` material-axis mechanical
        strain.

    Notes
    -----
    [N + N^T; M + M^T] = [A B; B D][ε0; κ];  ply stress σ_xy = Q̄(ε0 + zκ − αΔT − βΔC).
    """
    A, B, D, z = abd_matrix(ply)
    NT, MT = hygrothermal_loads(ply, dT, dC)
    load = np.concatenate([np.asarray(N, float) + NT, np.asarray(M, float) + MT])
    result = np.linalg.solve(np.block([[A, B], [B, D]]), load)
    eps0, kappa = result[:3], result[3:]
    entries = []
    for i, k in enumerate(ply):
        Qb = Qbar(k.get("Q", Q_material(k["m"])), k["angle"])
        eS = _free_strain(k, dT, dC)
        points = {}
        for name, zz in (("lower", z[i]), ("middle", 0.5 * (z[i] + z[i + 1])), ("upper", z[i + 1])):
            e = eps0 + zz * kappa
            s = Qb @ (e - eS)
            points[name] = {"z": zz, "eps_xy": e, "eps_mech_xy": e - eS, "sig_xy": s,
                            "sig12": T_stress(k["angle"]) @ s,
                            "eps12": _strain_xy_to_12(e - eS, k["angle"])}
        entries.append({"angle": k["angle"], "points": points})
    return {"eps0": eps0, "kappa": kappa, "NT": NT, "MT": MT, "A": A, "B": B, "D": D, "z": z,
            "layers": entries}


def _strain_xy_to_12(e: Array, theta: float) -> Array:
    """Transform an engineering strain vector from global to material axes."""
    return T_strain(theta) @ e


# ---------------------------------------------------------------- 5. failure criteria
def _second_degree_R(a: float, b: float) -> float:
    """Positive root of a R² + b R − 1 = 0 (numerically stable form); ``inf`` if there is none."""
    if a > 0:
        return 2.0 / (b + math.sqrt(b * b + 4 * a))
    if b > 0:
        return 1.0 / b
    return math.inf


def _dominant_kind(sig: ArrayLike, m: Material) -> str:
    """Heuristic failure kind for interactive criteria: the larger of the maximum-stress ratios."""
    s1, s2, t = (float(v) for v in np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, S = _strengths(m)
    fiber = s1 / Xt if s1 >= 0 else -s1 / Xc
    mat = max(s2 / Yt if s2 >= 0 else -s2 / Yc, abs(t) / S)
    return "fiber" if fiber >= mat else "matrix"



@cite("kaw_2006", note="§2.8.1")
def max_stress(sig: ArrayLike, m: Material) -> dict[str, Any]:
    """Maximum-stress criterion.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with strengths ``Xt, Xc, Yt, Yc, S12`` [Pa].

    Returns
    -------
    dict
        ``index`` largest ratio [-]; ``R`` = 1/index [-]; ``mode`` one of ``fiber``, ``matrix``,
        ``shear``; ``kind`` ``"fiber"`` or ``"matrix"``; ``ratios`` all three ratios.

    Raises
    ------
    ValueError
        If a strength is not positive.
    """
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, S = _strengths(m)
    ratio = {"fiber": s1 / Xt if s1 >= 0 else -s1 / Xc,
             "matrix": s2 / Yt if s2 >= 0 else -s2 / Yc,
             "shear": abs(t) / S}
    mode = max(ratio, key=lambda key: ratio[key])
    ind = ratio[mode]
    return {"index": ind, "R": 1 / ind if ind > 0 else math.inf, "mode": mode,
            "kind": "fiber" if mode == "fiber" else "matrix", "ratios": ratio}


@cite("kaw_2006", note="§2.8.2")
def max_strain(sig: ArrayLike, m: Material) -> dict[str, Any]:
    """Maximum-strain criterion; limit strains are strength/modulus (linear-elastic assumption).

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with elastic constants and strengths.

    Returns
    -------
    dict
        ``index``, ``R``, ``mode`` (``fiber``/``matrix``/``shear``), ``kind``, ``ratios`` and the
        material-axis strains ``eps12`` = (ε1, ε2, γ12).

    Raises
    ------
    ValueError
        If an elastic constant or strength is invalid.
    """
    E1, E2, nu12, G12 = _elastic(m)
    Xt, Xc, Yt, Yc, S = _strengths(m)
    e1, e2, g = S_matrix(E1, E2, nu12, G12) @ np.asarray(sig, float)
    ratio = {"fiber": e1 / (Xt / E1) if e1 >= 0 else -e1 / (Xc / E1),
             "matrix": e2 / (Yt / E2) if e2 >= 0 else -e2 / (Yc / E2),
             "shear": abs(g) / (S / G12)}
    mode = max(ratio, key=lambda key: ratio[key])
    ind = ratio[mode]
    return {"index": ind, "R": 1 / ind if ind > 0 else math.inf, "mode": mode,
            "kind": "fiber" if mode == "fiber" else "matrix", "ratios": ratio, "eps12": (e1, e2, g)}


@cite("azzi_tsai_1965", "hill_1948", "kaw_2006", note="Kaw §2.8.3 (Tsai-Hill and modified Tsai-Hill)")
def tsai_hill(sig: ArrayLike, m: Material, signed: bool = True) -> dict[str, Any]:
    """Tsai-Hill criterion.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with strengths [Pa].
    signed : bool, optional
        True: Kaw's "modified Tsai-Hill" — X1 follows the sign of σ1, X2 and Y the sign of σ2.
        False: tensile strengths only (X = Xt, Y = Yt), as in Kaw's "Tsai-Hill" example.

    Returns
    -------
    dict
        ``index`` [-], ``R`` = 1/√index [-], ``mode`` = ``"interactive"``, ``kind`` (heuristic,
        from the dominant maximum-stress ratio).

    Notes
    -----
    signed=False: (σ1/X)² − σ1σ2/X² + (σ2/Y)² + (τ12/S)².
    signed=True:  (σ1/X1)² − (σ1/X2)(σ2/X2) + (σ2/Y)² + (τ12/S)².
    The index is homogeneous of degree two, hence R = 1/√index.
    """
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, S = _strengths(m)
    if signed:
        X1 = Xt if s1 >= 0 else Xc
        X2 = Xt if s2 >= 0 else Xc
        Y = Yt if s2 >= 0 else Yc
    else:
        X1 = X2 = Xt
        Y = Yt
    ind = (s1 / X1) ** 2 - s1 * s2 / X2 ** 2 + (s2 / Y) ** 2 + (t / S) ** 2
    return {"index": ind, "R": 1 / math.sqrt(ind) if ind > 0 else math.inf,
            "mode": "interactive", "kind": _dominant_kind(sig, m)}


@cite("tsai_wu_1971", "kaw_2006", note="Kaw §2.8.4")
def tsai_wu(sig: ArrayLike, m: Material, F12: float | None = None, F12_ply: float = -0.5) -> dict[str, Any]:
    """Tsai-Wu criterion.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with strengths [Pa].
    F12 : float, optional
        Interaction coefficient [1/Pa²]. Default F12 = F12_ply·√(F11 F22).
    F12_ply : float, optional
        Normalised interaction coefficient [-]; −½ (Kaw: Mises-Hencky analogy).

    Returns
    -------
    dict
        ``index`` [-], ``R`` [-], ``mode`` = ``"interactive"``, ``kind`` (heuristic) and the used
        ``F12`` [1/Pa²].

    Raises
    ------
    ValueError
        If F12² ≥ F11·F22 (open failure surface) or a strength is not positive.

    Notes
    -----
    index = F1σ1 + F2σ2 + F11σ1² + F22σ2² + F66τ² + 2F12σ1σ2 (≥ 1 failure) with
    F1 = 1/Xt − 1/Xc, F2 = 1/Yt − 1/Yc, F11 = 1/(XtXc), F22 = 1/(YtYc), F66 = 1/S².
    R is the positive root of aR² + bR − 1 = 0 (a quadratic, b linear part).
    """
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, S = _strengths(m)
    F1, F2 = 1 / Xt - 1 / Xc, 1 / Yt - 1 / Yc
    F11, F22, F66 = 1 / (Xt * Xc), 1 / (Yt * Yc), 1 / S ** 2
    if F12 is None:
        F12 = F12_ply * math.sqrt(F11 * F22)
    if F12 * F12 >= F11 * F22:
        raise ValueError("F12² < F11·F22 is required (closed ellipsoid)")
    a = F11 * s1 ** 2 + F22 * s2 ** 2 + F66 * t ** 2 + 2 * F12 * s1 * s2
    b = F1 * s1 + F2 * s2
    return {"index": a + b, "R": _second_degree_R(a, b), "mode": "interactive",
            "kind": _dominant_kind(sig, m), "F12": F12}


@cite("hoffman_1967", note="formula as given in the Altair HyperView Result Math documentation, 'Hoffman'")
def hoffman(sig: ArrayLike, m: Material) -> dict[str, Any]:
    """Hoffman (1967) criterion, the special case F12 = −1/(2XtXc) of Tsai-Wu.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with strengths [Pa].

    Returns
    -------
    dict
        As :func:`tsai_wu` (``index``, ``R``, ``mode`` = ``"interactive"``, ``kind``, ``F12``).

    Notes
    -----
    (1/Xt − 1/Xc)σ1 + (1/Yt − 1/Yc)σ2 + σ1²/(XtXc) + σ2²/(YtYc) − σ1σ2/(XtXc) + τ²/S².
    """
    Xt, Xc, _, _, _ = _strengths(m)
    r = tsai_wu(sig, m, F12=-1 / (2 * Xt * Xc))
    r["mode"] = "interactive"
    return r


@cite("hashin_1980", "davila_camanho_2003", "hashin_rotem_1973",
      note="plane-stress forms from Dávila & Camanho 2003, Table 1; Hashin 1980 (J. Appl. Mech. 47:329) "
           "itself was not read in this repository")
def hashin(sig: ArrayLike, m: Material, ST: float | None = None, alpha: float = 1.0) -> dict[str, Any]:
    """Hashin (1980) plane-stress failure criteria.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    m : mapping
        Material record with strengths; ``S12`` is the longitudinal shear strength S_L [Pa].
    ST : float, optional
        Transverse shear strength S_T [Pa]; default Yc/2 (the criterion then reduces to the 1973
        form, [DC03] p. 7).
    alpha : float, optional
        Shear contribution factor in fibre tension (α = 1 in Hashin 1980).

    Returns
    -------
    dict
        ``index`` max of fibre and matrix indices [-]; ``R`` governing strength ratio [-];
        ``mode`` one of ``fiber_tension``, ``fiber_compression``, ``matrix_tension``,
        ``matrix_compression``; ``kind``; and the sub-results ``fiber`` and ``matrix``
        (each with ``mode``, ``index``, ``R``).

    Notes
    -----
    Fibre tension (σ1 ≥ 0):     (σ1/Xt)² + α(τ12/S_L)²
    Fibre compression (σ1 < 0): −σ1/Xc
    Matrix tension (σ2 ≥ 0):    (σ2/Yt)² + (τ12/S_L)²
    Matrix compression (σ2 < 0): (σ2/(2S_T))² + [(Yc/(2S_T))² − 1]σ2/Yc + (τ12/S_L)²
    """
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, SL = _strengths(m)
    ST = Yc / 2 if ST is None else _positive("S_T", ST)
    fiber: dict[str, Any]
    mat: dict[str, Any]
    if s1 >= 0:
        a = (s1 / Xt) ** 2 + alpha * (t / SL) ** 2
        fiber = {"mode": "fiber_tension", "index": a, "R": 1 / math.sqrt(a) if a > 0 else math.inf}
    else:
        fiber = {"mode": "fiber_compression", "index": -s1 / Xc, "R": Xc / -s1}
    if s2 >= 0:
        a = (s2 / Yt) ** 2 + (t / SL) ** 2
        mat = {"mode": "matrix_tension", "index": a, "R": 1 / math.sqrt(a) if a > 0 else math.inf}
    else:
        a = (s2 / (2 * ST)) ** 2 + (t / SL) ** 2
        b = ((Yc / (2 * ST)) ** 2 - 1) * s2 / Yc
        mat = {"mode": "matrix_compression", "index": a + b, "R": _second_degree_R(a, b)}
    governing = fiber if fiber["R"] <= mat["R"] else mat
    return {"index": max(fiber["index"], mat["index"]), "R": governing["R"], "mode": governing["mode"],
            "kind": "fiber" if governing is fiber else "matrix", "fiber": fiber, "matrix": mat}


@cite("puck_schurmann_2002", "puck_kopp_2002", "gu_chen_2019",
      note="Gu & Chen 2019 Eqs. 26 and 28; the τ21c relation and the GFRP slopes from the Altair HyperView "
           "Result Math documentation, 'Puck Criteria (2D)'; Puck's original papers not read")
def puck_parameters(m: Material, kind: str = "CFRP", p_plus: float | None = None,
                    p_minus: float | None = None) -> dict[str, float]:
    """Derived parameters of the 2-D Puck criterion.

    Parameters
    ----------
    m : mapping
        Material record with strengths [Pa].
    kind : {"CFRP", "GFRP"}, optional
        Material class selecting the default inclination parameters from :data:`PUCK_SLOPE`.
    p_plus, p_minus : float, optional
        Inclination parameters p⊥∥(+) and p⊥∥(−) [-] overriding the defaults.

    Returns
    -------
    dict
        ``p_plus`` p⊥∥(+), ``p_minus`` p⊥∥(−), ``p_dd`` p⊥⊥(−) [-]; ``R_AA`` fracture resistance of
        the action plane against transverse shear R⊥⊥A [Pa]; ``tau21c`` shear stress at the mode B/C
        turning point [Pa].

    Raises
    ------
    ValueError
        For an unknown ``kind`` or non-positive inclination parameters.

    Notes
    -----
    R⊥⊥A = S/(2p⊥∥(−))·[√(1 + 2p⊥∥(−)Yc/S) − 1] = Yc/(2(1+p⊥⊥(−)))
    p⊥⊥(−) = p⊥∥(−)·R⊥⊥A/S = ½[√(1 + 2p⊥∥(−)Yc/S) − 1]
    τ21c = S·√(1 + 2p⊥⊥(−))
    """
    if kind not in PUCK_SLOPE:
        raise ValueError(f"kind must be one of {list(PUCK_SLOPE)}")
    Xt, Xc, Yt, Yc, S = _strengths(m)
    pa = PUCK_SLOPE[kind][0] if p_plus is None else float(p_plus)
    pe = PUCK_SLOPE[kind][1] if p_minus is None else float(p_minus)
    if not (pa >= 0 and pe > 0):
        raise ValueError("inclination parameters must be positive")
    root = math.sqrt(1 + 2 * pe * Yc / S)
    R_AA = S / (2 * pe) * (root - 1)
    p_dd = pe * R_AA / S
    return {"p_plus": pa, "p_minus": pe, "p_dd": p_dd, "R_AA": R_AA, "tau21c": S * math.sqrt(1 + 2 * p_dd)}


@cite("puck_schurmann_2002", note="forms as in the Altair HyperView 'Puck2D' documentation; parameters from "
      "puck_parameters()")
def puck(sig: ArrayLike, m: Material, kind: str = "CFRP", p_plus: float | None = None,
         p_minus: float | None = None) -> dict[str, Any]:
    """Puck 2-D (plane-stress) criterion based on the stress exposure fE.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ21] [Pa].
    m : mapping
        Material record with strengths [Pa].
    kind : {"CFRP", "GFRP"}, optional
        Material class for the default inclination parameters.
    p_plus, p_minus : float, optional
        Inclination parameters p⊥∥(+), p⊥∥(−) [-].

    Returns
    -------
    dict
        ``index`` = max(fE_FF, fE_IFF) [-]; ``R`` = 1/index [-]; ``mode`` one of ``FF``, ``IFF-A``,
        ``IFF-B``, ``IFF-C``; ``kind``; ``fE_FF``, ``fE_IFF`` [-] and ``parameters``
        (see :func:`puck_parameters`).

    Notes
    -----
    fE is homogeneous of degree one in the stresses, so R = 1/fE.

    FF:               fE = σ1/Xt (σ1 ≥ 0), −σ1/Xc (σ1 < 0)  (simple fibre-fracture form)
    Mode A (σ2 ≥ 0):  fE = √[(τ21/S)² + (1 − p⊥∥(+)Yt/S)²(σ2/Yt)²] + p⊥∥(+)σ2/S
    Mode B (σ2 < 0, |σ2/τ21| ≤ R⊥⊥A/τ21c): fE = [√(τ21² + (p⊥∥(−)σ2)²) + p⊥∥(−)σ2]/S
    Mode C (other σ2 < 0): fE = [(τ21/(2(1+p⊥⊥(−))S))² + (σ2/Yc)²]·Yc/(−σ2)
    """
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    Xt, Xc, Yt, Yc, S = _strengths(m)
    p = puck_parameters(m, kind, p_plus, p_minus)
    fFF = s1 / Xt if s1 >= 0 else -s1 / Xc
    if s2 >= 0:
        fIFF = math.sqrt((t / S) ** 2 + (1 - p["p_plus"] * Yt / S) ** 2 * (s2 / Yt) ** 2) + p["p_plus"] * s2 / S
        mode = "IFF-A"
    elif t != 0 and abs(s2 / t) <= p["R_AA"] / p["tau21c"]:
        fIFF = (math.sqrt(t * t + (p["p_minus"] * s2) ** 2) + p["p_minus"] * s2) / S
        mode = "IFF-B"
    else:
        fIFF = ((t / (2 * (1 + p["p_dd"]) * S)) ** 2 + (s2 / Yc) ** 2) * Yc / (-s2)
        mode = "IFF-C"
    if fFF >= fIFF:
        mode, ind, failure_kind = "FF", fFF, "fiber"
    else:
        ind, failure_kind = fIFF, "matrix"
    return {"index": ind, "R": 1 / ind if ind > 0 else math.inf, "mode": mode, "kind": failure_kind,
            "fE_FF": fFF, "fE_IFF": fIFF, "parameters": p}


@cite("davila_camanho_2003", "davila_camanho_2005", note="Dávila & Camanho 2003, Appendix and Eqs. 9-11, 13, "
      "23-27, 32")
def larc03_parameters(m: Material, alpha0: float = 53.0, thickness: str = "ud", G_Ic: float | None = None,
                      G_IIc: float | None = None, t_layer: float | None = None) -> dict[str, float]:
    """Derived quantities of the LaRC03 criteria.

    Parameters
    ----------
    m : mapping
        Material record with elastic constants and strengths [Pa]; ``S12`` is S_L.
    alpha0 : float, optional
        Fracture plane angle under pure transverse compression α0 [deg], 45 < α0 < 90.
    thickness : {"ud", "thick", "thin"}, optional
        In-situ strength model: ``"ud"`` unidirectional specimen (Yis = Yt, Sis = S_L);
        ``"thick"`` embedded thick ply (Yis = 1.12√2·Yt, Sis = √2·S_L); ``"thin"`` embedded thin
        ply (fracture-mechanics in-situ strengths, needs G_Ic, G_IIc and t_layer).
    G_Ic, G_IIc : float, optional
        Mode I and mode II fracture toughness [J/m²] (``thickness="thin"`` only).
    t_layer : float, optional
        Thickness of the embedded thin ply [m] (``thickness="thin"`` only).

    Returns
    -------
    dict
        ``etaT``, ``etaL`` friction coefficients [-]; ``ST`` transverse shear strength [Pa];
        ``phiC`` misalignment angle under pure compression [rad]; in-situ strengths ``Yis``, ``Sis``
        [Pa]; ``g`` toughness ratio [-]; ``alpha0`` [rad]; ``L22``, ``L44`` [1/Pa].

    Raises
    ------
    ValueError
        If α0 is outside (45°, 90°), ``thickness`` is unknown, thin-ply inputs are missing or the
        discriminant for φC is negative.

    Notes
    -----
    "ud" and "thick": g = 1.12²(Λ22/Λ44)(Yt/S_L)²; "thin": Yis = √(8G_Ic/(π t Λ22)),
    Sis = √(8G_IIc/(π t Λ44)), g = G_Ic/G_IIc; Λ22 = 2(1/E2 − ν21²/E1), Λ44 = 1/G12.
    ηT = −1/tan(2α0), S_T = Yc cos α0 (sin α0 + cos α0/tan 2α0), ηL = −Sis cos 2α0/(Yc cos² α0),
    φC = atan{[1 − √(1 − 4(Sis/Xc + ηL)(Sis/Xc))]/[2(Sis/Xc + ηL)]}.
    """
    E1, E2, nu12, G12 = _elastic(m)
    Xt, Xc, Yt, Yc, SL = _strengths(m)
    if not 45.0 < alpha0 < 90.0:
        raise ValueError("α0 must lie between 45° and 90°")
    a0 = math.radians(alpha0)
    nu21 = nu12 * E2 / E1
    L22, L44 = 2 * (1 / E2 - nu21 ** 2 / E1), 1 / G12
    if thickness == "ud":
        Yis, Sis = Yt, SL
        g = 1.12 ** 2 * L22 / L44 * (Yt / SL) ** 2
    elif thickness == "thick":
        Yis, Sis = 1.12 * math.sqrt(2) * Yt, math.sqrt(2) * SL
        g = 1.12 ** 2 * L22 / L44 * (Yt / SL) ** 2
    elif thickness == "thin":
        GIc, GIIc, tl = _positive("G_Ic", G_Ic), _positive("G_IIc", G_IIc), _positive("t_layer", t_layer)
        Yis = math.sqrt(8 * GIc / (math.pi * tl * L22))
        Sis = math.sqrt(8 * GIIc / (math.pi * tl * L44))
        g = GIc / GIIc
    else:
        raise ValueError("thickness must be 'ud', 'thick' or 'thin'")
    etaT = -1 / math.tan(2 * a0)
    ST = Yc * math.cos(a0) * (math.sin(a0) + math.cos(a0) / math.tan(2 * a0))
    etaL = -Sis * math.cos(2 * a0) / (Yc * math.cos(a0) ** 2)
    q = Sis / Xc + etaL
    disc = 1 - 4 * q * (Sis / Xc)
    if disc < 0:
        raise ValueError("negative discriminant for φC (Sis/Xc too large)")
    phiC = math.atan((1 - math.sqrt(disc)) / (2 * q))
    return {"etaT": etaT, "etaL": etaL, "ST": ST, "phiC": phiC, "Yis": Yis, "Sis": Sis, "g": g,
            "alpha0": a0, "L22": L22, "L44": L44}


def _macaulay(x: float) -> float:
    """Macaulay bracket ⟨x⟩ = max(x, 0)."""
    return x if x > 0 else 0.0


def _larc_matrix_compression(s22: float, t12: float, p: Mapping[str, float]) -> tuple[float, float]:
    """LaRC03 matrix-compression index maximised over the fracture angle α ∈ [0, α0] ([DC03] Eqs. 4, 6).

    Returns ``(FI_M, alpha_rad)`` with FI_M = (τeffT/S_T)² + (τeffL/Sis)².
    """
    def fi(a: float) -> float:
        c, s = math.cos(a), math.sin(a)
        tT = _macaulay(-s22 * c * (s - p["etaT"] * c))
        tL = _macaulay(c * (abs(t12) + p["etaL"] * s22 * c))
        return (tT / p["ST"]) ** 2 + (tL / p["Sis"]) ** 2
    a0 = p["alpha0"]
    grid = np.linspace(0.0, a0, 91)
    values = [fi(a) for a in grid]
    i = int(np.argmax(values))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    for _ in range(60):  # golden-section refinement
        x1, x2 = hi - 0.618033988749895 * (hi - lo), lo + 0.618033988749895 * (hi - lo)
        if fi(x1) < fi(x2):
            lo = x1
        else:
            hi = x2
    a_best = 0.5 * (lo + hi)
    if fi(a_best) >= values[i]:
        return fi(a_best), a_best
    return values[i], grid[i]


def _larc_index(sig: ArrayLike, m: Material, p: Mapping[str, float]) -> dict[str, float]:
    """Failure indices of the active LaRC03 modes for one stress state (keys are mode labels)."""
    s1, s2, t = map(float, np.asarray(sig, dtype=float))
    E1, E2, nu12, G12 = _elastic(m)
    Xt, Xc, Yt, Yc, SL = _strengths(m)
    modes = {}
    # fibre modes
    if s1 >= 0:
        e11 = (s1 - nu12 * s2) / E1
        modes["LaRC03#3 fiber tension"] = e11 / (Xt / E1)
    else:
        denominator = G12 + s1 - s2
        if denominator <= 0:
            raise ValueError("LaRC03: G12 + σ11 − σ22 ≤ 0 (stress comparable to the shear modulus)")
        phi = (abs(t) + (G12 - Xc) * p["phiC"]) / denominator
        c, s = math.cos(phi), math.sin(phi)
        # |τ12| is used: the sign of φ is thereby taken equal to the sign of the shear (see [DC03] p. 15)
        s22m = s * s * s1 + c * c * s2 - 2 * s * c * abs(t)
        t12m = -s * c * s1 + s * c * s2 + (c * c - s * s) * abs(t)
        if s22m < 0:
            modes["LaRC03#4 fiber compression (kink)"] = _macaulay(abs(t12m) + p["etaL"] * s22m) / p["Sis"]
        else:
            modes["LaRC03#5 fiber compression (kink, matrix tension)"] = (
                (1 - p["g"]) * s22m / p["Yis"] + p["g"] * (s22m / p["Yis"]) ** 2 + (t12m / p["Sis"]) ** 2)
        if s1 < -Yc and s2 < 0:
            modes["LaRC03#6 matrix (biaxial compression)"] = _larc_matrix_compression(s22m, t12m, p)[0]
    # matrix modes
    if s2 >= 0:
        modes["LaRC03#2 matrix tension"] = (
            (1 - p["g"]) * s2 / p["Yis"] + p["g"] * (s2 / p["Yis"]) ** 2 + (t / p["Sis"]) ** 2)
    elif not (s1 < -Yc):
        modes["LaRC03#1 matrix compression"] = _larc_matrix_compression(s2, t, p)[0]
    return modes


@cite("davila_camanho_2003", "davila_camanho_2005", note="Dávila & Camanho 2003, Appendix (criteria #1-#6)")
def larc03(sig: ArrayLike, m: Material, alpha0: float = 53.0, thickness: str = "ud", G_Ic: float | None = None,
           G_IIc: float | None = None, t_layer: float | None = None) -> dict[str, Any]:
    """LaRC03 plane-stress failure criteria #1-#6.

    Parameters
    ----------
    sig : array_like, shape (3,)
        Material-axis stresses [σ11, σ22, τ12] [Pa].
    m : mapping
        Material record with elastic constants and strengths.
    alpha0, thickness, G_Ic, G_IIc, t_layer
        See :func:`larc03_parameters`.

    Returns
    -------
    dict
        ``index`` largest mode index at the given stress [-]; ``R`` strength ratio [-] found by
        root finding (the indices are not homogeneous); ``mode`` label of the governing mode at
        failure (R·σ), e.g. ``"LaRC03#1 matrix compression"``; ``kind`` ``"fiber"`` or
        ``"matrix"``; ``modes`` all active mode indices; ``parameters``.

    Raises
    ------
    ValueError
        For invalid material data or parameters.
    """
    p = larc03_parameters(m, alpha0, thickness, G_Ic, G_IIc, t_layer)
    sig = np.asarray(sig, float)
    modes = _larc_index(sig, m, p)

    def fi(s: Array) -> float:
        return max(_larc_index(s, m, p).values())
    R = _general_R(fi, sig, np.zeros(3))
    # the mode is the one with the largest index at the failure stress R·σ (indices differ in degree)
    failure_modes = _larc_index(sig * R, m, p) if math.isfinite(R) and R > 0 else modes
    mode = max(failure_modes, key=lambda key: failure_modes[key])
    return {"index": max(modes.values()), "R": R, "mode": mode, "kind": "fiber" if "fiber" in mode else "matrix",
            "modes": modes, "parameters": p}


def _general_R(fi: Callable[[Array], float], sig: Array, sig0: Array, upper: float = 1e30) -> float:
    """Smallest λ > 0 with fi(σ0 + λσ) ≥ 1 (geometric search + bisection; index assumed monotonic in λ)."""
    def failure(lam: float) -> bool:
        try:
            return fi(sig0 + lam * sig) >= 1.0
        except ValueError:
            return True  # model left its range of validity → treated as failure
    if failure(0.0):
        return 0.0
    lam = 1.0
    if failure(lam):
        while lam > 1e-30 and failure(lam / 2):
            lam /= 2
        lo, hi = lam / 2, lam
    else:
        while not failure(lam):
            lam *= 2
            if lam > upper:
                return math.inf
        lo, hi = lam / 2, lam
    for _ in range(200):
        middle = 0.5 * (lo + hi)
        if failure(middle):
            hi = middle
        else:
            lo = middle
        if hi - lo <= 1e-14 * hi:
            break
    return 0.5 * (lo + hi)


CRITERIA: dict[str, Callable[..., dict[str, Any]]] = {
    "max_stress": max_stress, "max_strain": max_strain, "tsai_hill": tsai_hill, "hoffman": hoffman,
    "tsai_wu": tsai_wu, "hashin": hashin, "puck": puck, "larc03": larc03}
"""Failure criteria by name; each takes ``(sig12, material, **kw)`` and returns a dict with ``index``,
``R``, ``mode`` and ``kind``."""


def strength_ratio(criterion: str | Callable[..., dict[str, Any]], sig_mech: ArrayLike, m: Material,
                   sig_fixed: ArrayLike | None = None, **kw: Any) -> float:
    """Load multiplier R such that criterion(σ_fixed + R·σ_mech) lies on the failure surface.

    Parameters
    ----------
    criterion : str or callable
        Name in :data:`CRITERIA` or a function with the same signature.
    sig_mech : array_like, shape (3,)
        Material-axis stresses of the scalable (mechanical) load [Pa].
    m : mapping
        Material record.
    sig_fixed : array_like, shape (3,), optional
        Non-scaled stresses, e.g. residual curing stresses [Pa].
    **kw
        Extra keyword arguments of the criterion.

    Returns
    -------
    float
        R [-] (``inf`` if the load direction never fails).

    Notes
    -----
    Without ``sig_fixed`` the criterion's closed-form R is returned; otherwise R is found by a
    general root search on the failure index.
    """
    f = CRITERIA[criterion] if isinstance(criterion, str) else criterion
    sig_mech = np.asarray(sig_mech, float)
    if sig_fixed is None or not np.any(sig_fixed):
        return f(sig_mech, m, **kw)["R"]
    return _general_R(lambda s: f(s, m, **kw)["index"], sig_mech, np.asarray(sig_fixed, float))


# ---------------------------------------------------------------- 6. progressive failure
@cite("kaw_2006", note="§5.3 (ply-discount example)")
def progressive_failure(ply: Sequence[Ply], load: ArrayLike, criterion: str | Callable[..., dict[str, Any]] = "tsai_wu",
                        reduction: str = "mode", d: float = 1e-6, dT: float = 0.0,
                        criterion_kw: Mapping[str, Any] | None = None, max_event: int = 200,
                        collapse_threshold: float = 1e-3) -> dict[str, Any]:
    """Ply-by-ply (ply discount) failure analysis from first-ply (FPF) to last-ply failure (LPF).

    Parameters
    ----------
    ply : sequence of dict
        Ply records from :func:`layers`.
    load : array_like, shape (6,)
        Unit load direction [Nx, Ny, Nxy, Mx, My, Mxy] [N/m, N·m/m]; results are multipliers of it.
    criterion : str or callable, optional
        Failure criterion (see :data:`CRITERIA`).
    reduction : {"mode", "full"}, optional
        ``"full"``: E1, E2 and G12 of a failed ply are multiplied by ``d`` (Kaw's §5.3 example sets
        Q = 0; d = 1e-6 avoids singularity). ``"mode"``: full reduction on fibre failure, only E2
        and G12 on matrix failure (common practice; not taken from a specific source).
    d : float, optional
        Stiffness reduction factor [-].
    dT : float, optional
        Curing temperature change ΔT [°C]; the residual stresses are added as a fixed part.
    criterion_kw : mapping, optional
        Extra keyword arguments of the criterion.
    max_event : int, optional
        Maximum number of failure events.
    collapse_threshold : float, optional
        LPF when the stiffness in the load direction falls below this fraction of its initial value.

    Returns
    -------
    dict
        ``fpf``, ``lpf`` load multipliers [-]; ``collapse`` bool; ``history`` list of events with
        ``load_factor`` [-], ``layers`` failed ply indices, ``kinds`` (``"fiber"``/``"matrix"``),
        ``eps0`` [-], ``kappa`` [1/m] and ``stiffness_ratio`` [-].

    Raises
    ------
    ValueError
        For an invalid ``reduction`` or ``load``, or if no failure is found.

    Notes
    -----
    A matrix-failed ply is checked only along the fibres (σ1, 0, 0). Stresses are evaluated at the
    lower, middle and upper point of every ply. The load history is kept monotonic: if load
    redistribution immediately causes another failure, the event is recorded at the same load.
    Last-ply failure is the event at which the stiffness in the load direction (yᵀ[ABD]⁻¹y)⁻¹ drops
    below ``collapse_threshold`` times its initial value, or fibre failure of all plies.
    """
    if reduction not in ("full", "mode"):
        raise ValueError("reduction must be 'full' or 'mode'")
    load = np.asarray(load, float)
    if load.shape != (6,) or not np.any(load):
        raise ValueError("load must be a non-zero vector with 6 components")
    kw = dict(criterion_kw or {})
    plies = [{"angle": k["angle"], "t": k["t"], "m": k["m"], "m0": k["m"], "failure": None} for k in ply]
    history: list[dict[str, Any]] = []
    lam_before, collapse = 0.0, False
    f = CRITERIA[criterion] if isinstance(criterion, str) else criterion

    def compliance(stack: Sequence[Ply]) -> float:
        """Compliance in the load direction yᵀ[ABD]⁻¹y."""
        A, B, D, _ = abd_matrix(stack)
        return float(load @ np.linalg.solve(np.block([[A, B], [B, D]]), load))
    c0 = compliance(plies)
    for _ in range(max_event):
        effective = [k for k in plies if k["failure"] != "fiber"]
        if not effective:
            break
        unit = laminate_analysis(plies, N=load[:3], M=load[3:])
        fixed = laminate_analysis(plies, dT=dT) if dT else None
        ratios = []
        for i, k in enumerate(plies):
            if k["failure"] == "fiber":
                continue
            R_k, kind_k = math.inf, None
            for point in ("lower", "middle", "upper"):
                s = unit["layers"][i]["points"][point]["sig12"]
                s0 = fixed["layers"][i]["points"][point]["sig12"] if fixed else None
                if k["failure"] == "matrix":
                    s = np.array([s[0], 0.0, 0.0])
                    s0 = None if s0 is None else np.array([s0[0], 0.0, 0.0])
                r = strength_ratio(criterion, s, k["m0"], s0, **kw)
                if r < R_k:
                    final = f(s if s0 is None else s0 + r * s, k["m0"], **kw)
                    R_k, kind_k = r, ("fiber" if k["failure"] == "matrix" else final["kind"])
            ratios.append((R_k, i, kind_k))
        R_min = min(r for r, _, _ in ratios)
        if not math.isfinite(R_min):
            break
        lam = max(R_min, lam_before)
        event = [(i, kind) for r, i, kind in ratios if r <= R_min * (1 + 1e-9)]
        for i, kind in event:
            k = plies[i]
            new = dict(k["m"])
            if reduction == "full" or kind == "fiber":
                new.update(E1=k["m0"]["E1"] * d, E2=k["m0"]["E2"] * d, G12=k["m0"]["G12"] * d)
                k["failure"] = "fiber"
            else:
                new.update(E2=k["m0"]["E2"] * d, G12=k["m0"]["G12"] * d)
                k["failure"] = "matrix"
            k["m"] = new
        ratio = c0 / compliance(plies)
        history.append({"load_factor": lam, "layers": [i for i, _ in event],
                        "kinds": [t for _, t in event], "eps0": unit["eps0"] * lam,
                        "kappa": unit["kappa"] * lam, "stiffness_ratio": ratio})
        lam_before = lam
        if ratio < collapse_threshold:  # no load-carrying capacity left in the load direction → LPF
            collapse = True
            break
    if not history:
        raise ValueError("no failure found (the load direction does not trigger the criterion)")
    return {"fpf": history[0]["load_factor"], "lpf": history[-1]["load_factor"], "history": history,
            "collapse": collapse}


# ---------------------------------------------------------------- 7. plate buckling
@cite("mil_hdbk_17_3f_2002", note="Eq. 5.7.1.6(a)")
def plate_buckling(D: ArrayLike, a: float, b: float, phi: float = 0.0, m_max: int = 30, n_max: int = 30,
                   tol: float = 0.02) -> dict[str, Any]:
    """Buckling of a simply supported, specially orthotropic plate under biaxial compression.

    Parameters
    ----------
    D : array_like, shape (3, 3)
        Bending stiffness matrix [N·m]; D16 = D26 = 0 is assumed.
    a : float
        Edge length in the x (Nx) direction [m].
    b : float
        Edge length in the y direction [m].
    phi : float, optional
        Load ratio φ = Ny/Nx [-]; φ < 0 means tension in y.
    m_max, n_max : int, optional
        Number of half-waves scanned in x and y.
    tol : float, optional
        A warning is issued if max(|D16|, |D26|) > tol·√(D11 D22).

    Returns
    -------
    dict
        ``Nx_cr`` critical compressive running load (positive = compression) [N/m]; ``Ny_cr`` = φ·Nx_cr
        [N/m]; ``m``, ``n`` half-wave numbers; ``warning`` text ("" if none).

    Raises
    ------
    ValueError
        If a or b is not positive, D11, D22 or D66 is not positive, or no (m, n) gives compressive
        buckling.

    Notes
    -----
    [MIL] Eq. 5.7.1.6(a)::

        Nx_cr = (π²/b²)·min_{m,n} [D11 m⁴(b/a)⁴ + 2(D12+2D66) m²n²(b/a)² + D22 n⁴] / [m²(b/a)² + φ n²]

    (identical to π²[D11m⁴ + 2(D12+2D66)m²n²(a/b)² + D22n⁴(a/b)⁴]/(a²[m² + φn²(a/b)²])).
    For φ < 0 only (m, n) pairs with a positive denominator are scanned.
    """
    a, b = _positive("a", a), _positive("b", b)
    D = np.asarray(D, float)
    D11, D12, D22, D66 = D[0, 0], D[0, 1], D[1, 1], D[2, 2]
    if min(D11, D22, D66) <= 0:
        raise ValueError("D11, D22 and D66 must be positive")
    r = b / a
    best: tuple[float, int | None, int | None] = (math.inf, None, None)
    for mm in range(1, m_max + 1):
        for nn in range(1, n_max + 1):
            denominator = mm * mm * r * r + phi * nn * nn
            if denominator <= 0:
                continue
            n_cr = math.pi ** 2 / b ** 2 * (D11 * mm ** 4 * r ** 4 + 2 * (D12 + 2 * D66) * mm ** 2 * nn ** 2 * r ** 2
                                            + D22 * nn ** 4) / denominator
            if n_cr < best[0]:
                best = (n_cr, mm, nn)
    if best[1] is None:
        raise ValueError("no compressive buckling for any (m, n)")
    warning = ""
    if max(abs(D[0, 2]), abs(D[1, 2])) > tol * math.sqrt(D11 * D22):
        warning = ("D16/D26 not negligible: the specially orthotropic formula is approximate "
                   "(generally not conservative)")
    if best[1] == m_max or best[2] == n_max:
        warning += (" · " if warning else "") + "minimum found at the scan limit: increase m_max/n_max"
    return {"Nx_cr": best[0], "Ny_cr": phi * best[0], "m": best[1], "n": best[2], "warning": warning}


@cite("mil_hdbk_17_3f_2002", note="Eq. 5.7.1.3")
def long_plate_buckling(D: ArrayLike, b: float) -> float:
    """Uniaxial buckling load of a long (a/b > 4) simply supported, specially orthotropic plate.

    Parameters
    ----------
    D : array_like, shape (3, 3)
        Bending stiffness matrix [N·m].
    b : float
        Loaded-edge width [m].

    Returns
    -------
    float
        Nx_cr = 2π²/b²[√(D11D22) + D12 + 2D66] [N/m].
    """
    D = np.asarray(D, float)
    return 2 * math.pi ** 2 / _positive("b", b) ** 2 * (math.sqrt(D[0, 0] * D[1, 1]) + D[0, 1] + 2 * D[2, 2])


# ---------------------------------------------------------------- 8. sandwich basics
@cite("zenkert_1995", "allen_1969", note="exact composite-section relations derived here; thin-face "
      "approximations in the form of Allen 1969 (not read in this repository)")
def sandwich_beam(Ef: float, tf: float, tc: float, Ec: float = 0.0, M: float = 0.0, Q: float = 0.0
                  ) -> dict[str, float]:
    """Symmetric sandwich beam per unit width (Poisson effect neglected).

    Parameters
    ----------
    Ef : float
        Face modulus [Pa] (for a plate use Ef/(1−ν²)).
    tf : float
        Face thickness [m].
    tc : float
        Core thickness [m].
    Ec : float, optional
        Core modulus [Pa].
    M : float, optional
        Bending moment per unit width [N·m/m].
    Q : float, optional
        Shear force per unit width [N/m].

    Returns
    -------
    dict
        ``D`` exact flexural rigidity [N·m]; ``D_thin`` thin-face approximation [N·m]; ``d`` distance
        between face centroids [m]; ``h`` total thickness [m]; ``sig_face`` and ``sig_face_thin``
        maximum face stress [Pa]; ``tau_core`` and ``tau_core_thin`` maximum core shear stress [Pa].

    Raises
    ------
    ValueError
        If Ef, tf or tc is not positive or Ec is negative.

    Notes
    -----
    Exact (composite section): D = Ef(h³ − tc³)/12 + Ec tc³/12, h = tc + 2tf, d = tc + tf;
    σf = M·Ef·(h/2)/D;  τc = Q[Ef tf d/2 + Ec tc²/8]/D.
    Thin-face approximation (limit Ec → 0, tf ≪ d): D ≈ Ef tf d²/2, σf ≈ M/(tf d), τc ≈ Q/d.
    """
    Ef, tf, tc = _positive("Ef", Ef), _positive("tf", tf), _positive("tc", tc)
    if Ec < 0:
        raise ValueError("Ec must not be negative")
    h, d = tc + 2 * tf, tc + tf
    D = Ef * (h ** 3 - tc ** 3) / 12 + Ec * tc ** 3 / 12
    return {"D": D, "D_thin": Ef * tf * d ** 2 / 2, "d": d, "h": h,
            "sig_face": M * Ef * (h / 2) / D, "sig_face_thin": M / (tf * d),
            "tau_core": Q * (Ef * tf * d / 2 + Ec * tc ** 2 / 8) / D, "tau_core_thin": Q / d}


@cite("ley_lin_1999", "hoff_mautner_1945", note="Ley et al. 1999, Table 3 and Eqs. 7-8")
def face_crippling(Ef: float, Ec: float, Gc: float, k1: float = 0.5) -> float:
    """Symmetric face-sheet wrinkling stress for a continuous (isotropic) core.

    Parameters
    ----------
    Ef : float
        Face modulus [Pa].
    Ec, Gc : float
        Core through-thickness modulus and shear modulus [Pa].
    k1 : float, optional
        Wrinkling coefficient [-]: 0.50 Hoff & Mautner design recommendation; 0.76 theory (upper
        bound), 0.63 lower bound; 0.91 Hoff & Mautner theoretical value for a thick core.

    Returns
    -------
    float
        σ_wr = k1 (Ef Ec Gc)^(1/3) [Pa].
    """
    return _positive("k1", k1) * (_positive("Ef", Ef) * _positive("Ec", Ec) * _positive("Gc", Gc)) ** (1 / 3)


@cite("ley_lin_1999", note="Table 3")
def face_crippling_honeycomb(Ef: float, Ec: float, tf: float, tc: float, k2: float = 0.82) -> float:
    """Face-sheet wrinkling stress on an antiplane (honeycomb) core.

    Parameters
    ----------
    Ef : float
        Face modulus [Pa].
    Ec : float
        Core through-thickness modulus [Pa].
    tf, tc : float
        Face and core thicknesses [m].
    k2 : float, optional
        Coefficient [-]: 0.82 theory / Norris-Boller-Voss honeycomb; 0.60 imperfect face.

    Returns
    -------
    float
        σ_wr = k2·Ef·√(Ec tf/(Ef tc)) [Pa].
    """
    Ef = _positive("Ef", Ef)
    return _positive("k2", k2) * Ef * math.sqrt(_positive("Ec", Ec) * _positive("tf", tf) / (Ef * _positive("tc", tc)))
