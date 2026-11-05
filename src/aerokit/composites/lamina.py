"""Classical lamination theory (CLT) for a single material.

Ply stiffness Q, transformed stiffness Q̄, ABD matrices, mid-ply stresses and two
simple failure criteria (Tsai-Wu and maximum stress).

Conventions
-----------
* Stacking sequence from bottom to top: ``[(angle_deg, thickness_m), ...]``.
* Voigt order ``[x, y, xy]`` (global) and ``[1, 2, 12]`` (material axes).
* Shear strain is the engineering strain γxy = 2εxy.
* z is measured from the mid-plane, z = −h/2 at the bottom face.

The multi-material, hygrothermal and failure-mode-aware implementation lives in
:mod:`aerokit.composites.laminate`; this module is the minimal single-material core.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.references import cite

__all__ = ["Q_matrix", "T_stress", "T_strain", "Qbar", "abd", "layer_stresses", "tsai_wu", "max_stress"]


@cite("kaw_2006", "jones_1999", note="Kaw §2.4: reduced stiffness of an orthotropic lamina in plane stress")
def Q_matrix(E1: float, E2: float, nu12: float, G12: float) -> NDArray[np.float64]:
    """Reduced (plane-stress) stiffness matrix of an orthotropic ply in material axes.

    Parameters
    ----------
    E1, E2 : float
        Longitudinal and transverse Young's moduli [Pa].
    nu12 : float
        Major Poisson's ratio [-].
    G12 : float
        In-plane shear modulus [Pa].

    Returns
    -------
    ndarray, shape (3, 3)
        Q such that σ_12 = Q ε_12 (Voigt [1, 2, 12], engineering shear strain) [Pa].

    Notes
    -----
    ν21 = ν12 E2/E1, Δ = 1 − ν12 ν21::

        Q11 = E1/Δ,  Q12 = ν12 E2/Δ,  Q22 = E2/Δ,  Q66 = G12.

    Examples
    --------
    >>> Q = Q_matrix(140e9, 10e9, 0.3, 5e9)
    >>> round(Q[2, 2] / 1e9, 3)
    5.0
    """
    nu21 = nu12 * E2 / E1
    d = 1 - nu12 * nu21
    return np.array([[E1 / d, nu12 * E2 / d, 0],
                     [nu12 * E2 / d, E2 / d, 0],
                     [0, 0, G12]])


@cite("kaw_2006", note="§2.5 (stress transformation)")
def T_stress(theta_degree: float) -> NDArray[np.float64]:
    """Stress transformation matrix from global to material axes, σ_12 = T σ_xy.

    Parameters
    ----------
    theta_degree : float
        Ply angle θ measured from the global x axis to the fibre direction [deg].

    Returns
    -------
    ndarray, shape (3, 3)
        T with rows ``[c², s², 2sc], [s², c², −2sc], [−sc, sc, c² − s²]``.
    """
    t = math.radians(theta_degree)
    c, s = math.cos(t), math.sin(t)
    return np.array([[c * c, s * s, 2 * s * c],
                     [s * s, c * c, -2 * s * c],
                     [-s * c, s * c, c * c - s * s]])


@cite("kaw_2006", note="§2.5 (strain transformation with engineering shear strain)")
def T_strain(theta_degree: float) -> NDArray[np.float64]:
    """Strain transformation from global to material axes, ε_12 = T_ε ε_xy (engineering γ).

    Parameters
    ----------
    theta_degree : float
        Ply angle θ [deg].

    Returns
    -------
    ndarray, shape (3, 3)
        T_ε with rows ``[c², s², sc], [s², c², −sc], [−2sc, 2sc, c² − s²]``.
    """
    t = math.radians(theta_degree)
    c, s = math.cos(t), math.sin(t)
    return np.array([[c * c, s * s, s * c],
                     [s * s, c * c, -s * c],
                     [-2 * s * c, 2 * s * c, c * c - s * s]])


@cite("kaw_2006", note="§2.5 (transformed reduced stiffness)")
def Qbar(Q: ArrayLike, theta_degree: float) -> NDArray[np.float64]:
    """Transformed reduced stiffness of a ply rotated by θ, Q̄ = T⁻¹ Q T_ε.

    Parameters
    ----------
    Q : array_like, shape (3, 3)
        Ply stiffness in material axes [Pa] (see :func:`Q_matrix`).
    theta_degree : float
        Ply angle θ [deg].

    Returns
    -------
    ndarray, shape (3, 3)
        Q̄ such that σ_xy = Q̄ ε_xy [Pa].
    """
    return np.linalg.inv(T_stress(theta_degree)) @ np.asarray(Q, dtype=float) @ T_strain(theta_degree)


@cite("kaw_2006", "reddy_2004", note="Kaw §4.3 (ABD matrices)")
def abd(Q: ArrayLike, sequence: Sequence[tuple[float, float]]
        ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], list[float]]:
    """Extensional (A), coupling (B) and bending (D) stiffness matrices of a laminate.

    Parameters
    ----------
    Q : array_like, shape (3, 3)
        Ply stiffness in material axes [Pa]; the same material is used for every ply.
    sequence : sequence of (float, float)
        ``[(angle_deg, thickness_m), ...]`` from bottom to top.

    Returns
    -------
    A : ndarray, shape (3, 3)
        Extensional stiffness [N/m].
    B : ndarray, shape (3, 3)
        Bending-extension coupling stiffness [N].
    D : ndarray, shape (3, 3)
        Bending stiffness [N·m].
    z : list of float
        Ply interface coordinates from −h/2 to +h/2 [m] (length n_ply + 1).

    Notes
    -----
    A = Σ Q̄_k (z_k − z_{k−1}),  B = ½ Σ Q̄_k (z_k² − z_{k−1}²),  D = ⅓ Σ Q̄_k (z_k³ − z_{k−1}³).
    """
    h = sum(t for _, t in sequence)
    z = [-h / 2]
    for _, t in sequence:
        z.append(z[-1] + t)
    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    D = np.zeros((3, 3))
    for k, (angle, _) in enumerate(sequence):
        Qb = Qbar(Q, angle)
        A += Qb * (z[k + 1] - z[k])
        B += Qb * (z[k + 1] ** 2 - z[k] ** 2) / 2
        D += Qb * (z[k + 1] ** 3 - z[k] ** 3) / 3
    return A, B, D, z


@cite("kaw_2006", note="§4.3: mid-plane strains, curvatures and ply stresses")
def layer_stresses(Q: ArrayLike, sequence: Sequence[tuple[float, float]], N: ArrayLike,
                   M: ArrayLike = (0, 0, 0)) -> dict[str, Any]:
    """Material-axis stresses at the mid-plane of every ply under running loads.

    Parameters
    ----------
    Q : array_like, shape (3, 3)
        Ply stiffness in material axes [Pa].
    sequence : sequence of (float, float)
        ``[(angle_deg, thickness_m), ...]`` from bottom to top.
    N : array_like, shape (3,)
        In-plane force resultants [Nx, Ny, Nxy] [N/m].
    M : array_like, shape (3,), optional
        Moment resultants [Mx, My, Mxy] [N·m/m].

    Returns
    -------
    dict
        ``eps0`` mid-plane strains (3,) [-]; ``kappa`` curvatures (3,) [1/m];
        ``layers`` list of dicts with ``angle`` [deg], ``z`` ply mid-plane coordinate [m] and
        ``sig12`` material-axis stresses [σ1, σ2, τ12] [Pa].

    Notes
    -----
    [N; M] = [A B; B D] [ε0; κ],  σ_xy(z) = Q̄ (ε0 + z κ),  σ_12 = T σ_xy.
    """
    A, B, D, z = abd(Q, sequence)
    ABD = np.block([[A, B], [B, D]])
    result = np.linalg.solve(ABD, np.concatenate([np.asarray(N, dtype=float), np.asarray(M, dtype=float)]))
    eps0, kappa = result[:3], result[3:]
    layers = []
    for k, (angle, _) in enumerate(sequence):
        zm = 0.5 * (z[k] + z[k + 1])
        eps_xy = eps0 + zm * kappa
        sig_xy = Qbar(Q, angle) @ eps_xy
        layers.append({"angle": angle, "z": zm, "sig12": T_stress(angle) @ sig_xy})
    return {"eps0": eps0, "kappa": kappa, "layers": layers}


@cite("tsai_wu_1971", "kaw_2006", note="Kaw §2.8.4")
def tsai_wu(sig12: ArrayLike, Xt: float, Xc: float, Yt: float, Yc: float, S: float,
            F12_ply: float = -0.5) -> dict[str, float]:
    """Tsai-Wu failure index and strength ratio of a ply.

    Parameters
    ----------
    sig12 : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    Xt, Xc : float
        Longitudinal tensile and compressive strengths [Pa] (Xc as a positive magnitude).
    Yt, Yc : float
        Transverse tensile and compressive strengths [Pa] (Yc as a positive magnitude).
    S : float
        In-plane shear strength [Pa].
    F12_ply : float, optional
        Normalised interaction coefficient, F12 = F12_ply·√(F11 F22). −0.5 is a common
        assumption, not an experimental value.

    Returns
    -------
    dict
        ``index`` Tsai-Wu index (≥ 1 means failure) [-]; ``safety`` load multiplier R that
        brings the stress state to the failure surface [-] (``inf`` if none);
        ``irf`` inverse reserve factor 1/R [-] (0 if R is infinite).

    Notes
    -----
    F1 = 1/Xt − 1/Xc, F2 = 1/Yt − 1/Yc, F11 = 1/(Xt Xc), F22 = 1/(Yt Yc), F66 = 1/S²::

        index = F1σ1 + F2σ2 + F11σ1² + F22σ2² + F66τ12² + 2F12σ1σ2.

    The load multiplier R solves a R² + b R − 1 = 0 with a the quadratic and b the linear part.
    """
    s1, s2, t12 = (float(v) for v in np.asarray(sig12, dtype=float))
    F1, F2 = 1 / Xt - 1 / Xc, 1 / Yt - 1 / Yc
    F11, F22, F66 = 1 / (Xt * Xc), 1 / (Yt * Yc), 1 / S ** 2
    F12 = F12_ply * math.sqrt(F11 * F22)
    a = F11 * s1 ** 2 + F22 * s2 ** 2 + F66 * t12 ** 2 + 2 * F12 * s1 * s2
    b = F1 * s1 + F2 * s2
    index = a + b
    # load multiplier R: a R² + b R − 1 = 0 → safety factor
    if a > 0:
        R = (-b + math.sqrt(b * b + 4 * a)) / (2 * a)
    elif b > 0:
        R = 1 / b
    else:
        R = math.inf
    return {"index": index, "safety": R, "irf": 0 if math.isinf(R) else 1 / R}


@cite("kaw_2006", note="§2.8.1")
def max_stress(sig12: ArrayLike, Xt: float, Xc: float, Yt: float, Yc: float, S: float
               ) -> tuple[float, dict[str, float]]:
    """Maximum-stress criterion: ratio of each stress component to its strength.

    Parameters
    ----------
    sig12 : array_like, shape (3,)
        Material-axis stresses [σ1, σ2, τ12] [Pa].
    Xt, Xc, Yt, Yc, S : float
        Ply strengths [Pa]; compressive strengths as positive magnitudes.

    Returns
    -------
    index : float
        Largest ratio (≥ 1 means failure) [-].
    ratios : dict
        ``fiber``, ``matrix`` and ``shear`` ratios [-].
    """
    s1, s2, t12 = (float(v) for v in np.asarray(sig12, dtype=float))
    ratios = {"fiber": s1 / Xt if s1 >= 0 else -s1 / Xc,
              "matrix": s2 / Yt if s2 >= 0 else -s2 / Yc,
              "shear": abs(t12) / S}
    return max(ratios.values()), ratios
