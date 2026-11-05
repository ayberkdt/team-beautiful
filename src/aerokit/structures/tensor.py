"""Stress and strain tensors: principal values, invariants, yield criteria, transformation, Hooke's law.

Sign convention: tension positive. Shear components are tensor components (τxy = σxy).
For strain, the engineering shear strain is γ = 2·εxy; every function states which one it uses.
Stresses in Pa (any consistent unit works).
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.references import cite


class Stress:
    """Symmetric 3×3 Cauchy stress tensor [Pa].

    Parameters
    ----------
    sxx, syy, szz : float
        Normal components [Pa].
    txy, tyz, txz : float
        Shear components [Pa].

    Attributes
    ----------
    s : ndarray, shape (3, 3)
        Tensor components.

    Examples
    --------
    >>> round(Stress(sxx=100.0).von_mises(), 9)
    100.0
    """

    def __init__(self, sxx: float = 0.0, syy: float = 0.0, szz: float = 0.0, txy: float = 0.0, tyz: float = 0.0,
                 txz: float = 0.0) -> None:
        self.s = np.array([[sxx, txy, txz],
                           [txy, syy, tyz],
                           [txz, tyz, szz]], dtype=float)

    @classmethod
    def from_matrix(cls, m: ArrayLike) -> Stress:
        """Create a tensor from a symmetric 3×3 matrix.

        Parameters
        ----------
        m : array_like, shape (3, 3)
            Stress matrix [Pa].

        Returns
        -------
        Stress

        Raises
        ------
        ValueError
            If ``m`` is not 3×3 and symmetric.
        """
        m = np.asarray(m, dtype=float)
        if m.shape != (3, 3) or not np.allclose(m, m.T):
            raise ValueError("the stress tensor must be 3×3 and symmetric")
        g = cls()
        g.s = m.copy()
        return g

    # --- invariants and decomposition ---
    def invariants(self) -> tuple[float, float, float]:
        """Stress invariants.

        Returns
        -------
        tuple of float
            ``I1 = tr σ`` [Pa], ``I2 = ½[(tr σ)² − tr(σ²)]`` [Pa²], ``I3 = det σ`` [Pa³].
        """
        s = self.s
        I1 = np.trace(s)
        I2 = 0.5 * (I1 ** 2 - np.trace(s @ s))
        I3 = np.linalg.det(s)
        return I1, I2, I3

    def hydrostatic(self) -> float:
        """Mean (hydrostatic) stress ``tr σ / 3`` [Pa]."""
        return np.trace(self.s) / 3.0

    def deviatoric(self) -> NDArray[np.float64]:
        """Deviatoric stress matrix ``σ − (tr σ/3) I`` [Pa]."""
        return self.s - self.hydrostatic() * np.eye(3)

    # --- principal stresses ---
    def principal(self) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Principal stresses and directions.

        Returns
        -------
        tuple of ndarray
            ``(σ1 ≥ σ2 ≥ σ3)`` [Pa] and the unit direction vectors as columns in the same order.
        """
        w, v = np.linalg.eigh(self.s)
        order = np.argsort(w)[::-1]
        return w[order], v[:, order]

    # --- criteria ---
    def von_mises(self) -> float:
        """Von Mises equivalent stress ``√(3/2 s:s)`` [Pa]."""
        d = self.deviatoric()
        return math.sqrt(1.5 * np.sum(d * d))

    def max_shear(self) -> float:
        """Maximum shear stress ``(σ1 − σ3)/2`` [Pa]."""
        s1, _, s3 = self.principal()[0]
        return 0.5 * (s1 - s3)

    def tresca(self) -> float:
        """Tresca equivalent stress ``σ1 − σ3`` [Pa]."""
        return 2.0 * self.max_shear()

    def octahedral_shear(self) -> float:
        """Octahedral shear stress ``√2/3 · σ_vM`` [Pa]."""
        return math.sqrt(2.0) / 3.0 * self.von_mises()

    def safety_coefficient(self, yield_: float, criterion: str = "von_mises") -> float:
        """Factor of safety against yield.

        Parameters
        ----------
        yield_ : float
            Yield stress [Pa].
        criterion : {"von_mises", "tresca"}
            Yield criterion; anything other than ``"von_mises"`` uses Tresca.

        Returns
        -------
        float
            ``yield_ / σ_eq`` [-]; ``inf`` for a zero equivalent stress.
        """
        equivalent = self.von_mises() if criterion == "von_mises" else self.tresca()
        return math.inf if equivalent == 0 else yield_ / equivalent

    # --- traction on a plane ---
    def traction(self, n: ArrayLike) -> tuple[NDArray[np.float64], float, float]:
        """Traction on the plane with normal n.

        Parameters
        ----------
        n : array_like, shape (3,)
            Plane normal (normalised internally).

        Returns
        -------
        tuple
            Traction vector t [Pa], normal stress σn [Pa], shear stress τ [Pa].
        """
        nv = np.asarray(n, dtype=float)
        nv = nv / np.linalg.norm(nv)
        t = self.s @ nv
        sn = float(t @ nv)
        tau = float(math.sqrt(max(t @ t - sn ** 2, 0.0)))
        return t, sn, tau

    # --- coordinate transformation ---
    def rotate(self, R: ArrayLike) -> Stress:
        """Transform to new axes, ``σ' = R σ Rᵀ``.

        Parameters
        ----------
        R : array_like, shape (3, 3)
            Orthonormal matrix whose rows are the new axes' unit vectors in the old system.

        Returns
        -------
        Stress

        Raises
        ------
        ValueError
            If R is not orthonormal.
        """
        R = np.asarray(R, dtype=float)
        if not np.allclose(R @ R.T, np.eye(3), atol=1e-9):
            raise ValueError("R must be orthonormal")
        return Stress.from_matrix(R @ self.s @ R.T)

    def rotate_z(self, theta_deg: float) -> Stress:
        """Stress in axes rotated by θ about z.

        Parameters
        ----------
        theta_deg : float
            Rotation angle [deg].

        Returns
        -------
        Stress
        """
        t = math.radians(theta_deg)
        c, s = math.cos(t), math.sin(t)
        return self.rotate([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])

    def __repr__(self) -> str:
        return "Stress(\n" + np.array2string(self.s, precision=4) + ")"


@cite("timoshenko_goodier_1970", note="plane stress, Mohr's circle")
def mohr_2d(sxx: float, syy: float, txy: float) -> dict[str, float]:
    """Mohr's circle for plane stress.

    Parameters
    ----------
    sxx, syy, txy : float
        In-plane stress components [Pa].

    Returns
    -------
    dict
        ``center``, ``radius``, ``s1``, ``s2``, ``tau_max_plane`` [Pa] and principal angle ``theta_p``
        [deg] (from x to σ1).
    """
    center = 0.5 * (sxx + syy)
    radius = math.hypot(0.5 * (sxx - syy), txy)
    theta_p = 0.5 * math.degrees(math.atan2(2 * txy, sxx - syy))
    return {"center": center, "radius": radius, "s1": center + radius,
            "s2": center - radius, "theta_p": theta_p, "tau_max_plane": radius}


def lame(E: float, nu: float) -> tuple[float, float]:
    """Lamé constants.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].

    Returns
    -------
    tuple of float
        ``(λ, μ)`` [Pa], ``λ = Eν/((1+ν)(1−2ν))``, ``μ = E/(2(1+ν))``.
    """
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))
    return lam, mu


@cite("timoshenko_goodier_1970", note="generalised Hooke's law")
def from_strain_stress(eps: ArrayLike, E: float, nu: float) -> Stress:
    """Stress from strain, isotropic Hooke's law ``σ = λ tr(ε) I + 2μ ε``.

    Parameters
    ----------
    eps : array_like, shape (3, 3)
        TENSOR strain (εxy = γxy/2) [-].
    E, nu : float
        Young's modulus [Pa] and Poisson's ratio [-].

    Returns
    -------
    Stress
    """
    eps = np.asarray(eps, dtype=float)
    lam, mu = lame(E, nu)
    return Stress.from_matrix(lam * np.trace(eps) * np.eye(3) + 2 * mu * eps)


@cite("timoshenko_goodier_1970", note="generalised Hooke's law")
def from_stress_strain(g: Stress, E: float, nu: float) -> NDArray[np.float64]:
    """Strain from stress, inverse isotropic Hooke's law ``ε = [(1+ν)σ − ν tr(σ) I]/E``.

    Parameters
    ----------
    g : Stress
        Stress tensor.
    E, nu : float
        Young's modulus [Pa] and Poisson's ratio [-].

    Returns
    -------
    ndarray, shape (3, 3)
        Tensor strain [-].
    """
    s = g.s
    return ((1 + nu) * s - nu * np.trace(s) * np.eye(3)) / E


def voigt_strain(eps: Any) -> NDArray[np.float64]:
    """Tensor strain → Voigt vector ``[εxx, εyy, εzz, γyz, γxz, γxy]`` (engineering shear).

    Parameters
    ----------
    eps : array_like, shape (3, 3)
        Tensor strain [-].

    Returns
    -------
    ndarray, shape (6,)
    """
    e = np.asarray(eps, dtype=float)
    return np.array([e[0, 0], e[1, 1], e[2, 2], 2 * e[1, 2], 2 * e[0, 2], 2 * e[0, 1]])
