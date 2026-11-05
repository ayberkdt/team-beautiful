"""Zienkiewicz-Zhu recovery-based a-posteriori error estimation for 2-D continuum meshes.

The finite-element stress ``σh`` is discontinuous between elements. A smoother, more accurate
field ``σ*`` is *recovered* at the nodes and interpolated with the element shape functions; the
difference is used as an estimate of the true error [zienkiewicz_zhu_1987]_:

``‖e‖²_K ≈ ∫_K (σ* − σh)ᵀ D⁻¹ (σ* − σh) dV``,  ``‖u‖² = Σ ∫ σhᵀ D⁻¹ σh dV``,

``η = ‖e‖ / √(‖u‖² + ‖e‖²)``  (relative energy-norm error).

Recovery methods
    ``"average"``  simple nodal averaging of the element nodal stresses (ZZ 1987);
    ``"spr"``      superconvergent patch recovery (ZZ 1992) [zienkiewicz_zhu_1992]_: for every
                   interior vertex a polynomial (``1, x, y`` for T3/Q4/QM6; complete quadratic for Q8)
                   is least-squares fitted to the stresses at the elements' superconvergent sampling
                   points (centroid for linear elements, 2 × 2 Gauss points for Q8). Vertex nodes
                   take the value of their own patch; boundary and mid-side nodes the average of the
                   interior patches that contain them (falling back to boundary patches, then to
                   nodal averaging).

Elements whose indicator exceeds ``fraction × max`` are proposed for refinement. Supports the
plane elements T3, Q4, QM6 and Q8 in plane stress, plane strain or axisymmetry (other elements of
the model are ignored).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.elements.plane import Q8, T3, _Continuum
from aerokit.fem.quadrature import gauss2d, triangle
from aerokit.fem.results import Result
from aerokit.references import cite

__all__ = ["ErrorEstimate", "recover_stresses", "zz_error_estimate", "exact_energy_error", "effectivity_index"]


@dataclass(frozen=True, eq=False)
class ErrorEstimate(Result):
    """Result of :func:`zz_error_estimate`.

    Attributes
    ----------
    element_error : ndarray, shape (n_continuum_elements,)
        Element energy-norm error indicators ``‖e‖_K`` [√J].
    error_norm : float
        Global estimated error ``‖e‖ = √Σ ‖e‖²_K`` [√J].
    energy_norm : float
        ``‖u‖ = √(∫ σhᵀ D⁻¹ σh dV)`` [√J] (``‖u‖² = 2 × strain energy``).
    eta : float
        Relative error ``‖e‖ / √(‖u‖² + ‖e‖²)``.
    recovered : ndarray, shape (n_node, n_components)
        Recovered nodal stresses ``σ*`` [Pa] (NaN at nodes without continuum elements).
    refine : ndarray of int
        Model element indices with ``‖e‖_K ≥ fraction · max ‖e‖_K``.
    elements : ndarray of int
        Model indices of the continuum elements (order of ``element_error``).
    method : str
        Recovery method.
    fraction : float
        Refinement threshold.
    """

    element_error: np.ndarray
    error_norm: float
    energy_norm: float
    eta: float
    recovered: np.ndarray
    refine: np.ndarray
    elements: np.ndarray
    method: str = "spr"
    fraction: float = 0.5


def _continuum(model: Any) -> list[tuple[int, _Continuum]]:
    els = [(i, e) for i, e in enumerate(model.elements) if isinstance(e, _Continuum)]
    if not els:
        raise ValueError("model has no 2-D continuum elements (T3, Q4, QM6, Q8)")
    if len({e.D.shape[0] for _, e in els}) != 1:
        raise ValueError("all continuum elements must use the same formulation")
    return els


def _corners(e: _Continuum) -> list[int]:
    return e.nodes[:3] if isinstance(e, T3) else e.nodes[:4]


def _sampling_points(e: _Continuum) -> list[tuple[float, float]]:
    """Superconvergent stress sampling points (natural coordinates)."""
    if isinstance(e, Q8):
        return [(xi, eta) for xi, eta, _ in gauss2d(2)]
    return [(float(e.center[0]), float(e.center[1]))]


def _error_rule(e: _Continuum) -> list[tuple[float, float, float]]:
    """Integration rule for the error norms (one order above the stiffness rule)."""
    if isinstance(e, T3):
        return triangle(3)
    return gauss2d(4 if isinstance(e, Q8) else 3)


def _basis(e: _Continuum, x: np.ndarray) -> np.ndarray:
    """Polynomial basis for SPR at scaled local coordinates ``x`` (k, 2)."""
    one = np.ones(x.shape[0])
    if isinstance(e, Q8):
        return np.column_stack([one, x[:, 0], x[:, 1], x[:, 0] ** 2, x[:, 0] * x[:, 1], x[:, 1] ** 2])
    return np.column_stack([one, x[:, 0], x[:, 1]])


def _average(model: Any, u: np.ndarray, els: list[tuple[int, _Continuum]]) -> np.ndarray:
    """Nodal averaging of the element nodal stresses."""
    ncomp = els[0][1].D.shape[0]
    total = np.zeros((model.n_node, ncomp))
    count = np.zeros(model.n_node)
    for _, e in els:
        ue = u[model.equivalent_dof(e)]
        for d, (xi, eta) in zip(e.nodes, e.NATURAL, strict=True):
            total[d] += e.stress_at_point(model.X, ue, xi, eta)[0]
            count[d] += 1
    out = np.full((model.n_node, ncomp), np.nan)
    ok = count > 0
    out[ok] = total[ok] / count[ok, None]
    return out


def _boundary_corner_nodes(els: list[tuple[int, _Continuum]]) -> set[int]:
    edges: dict[tuple[int, int], int] = {}
    for _, e in els:
        c = _corners(e)
        for a, b in zip(c, c[1:] + c[:1], strict=True):
            k = (min(a, b), max(a, b))
            edges[k] = edges.get(k, 0) + 1
    return {n for k, v in edges.items() if v == 1 for n in k}


def _spr(model: Any, u: np.ndarray, els: list[tuple[int, _Continuum]]) -> np.ndarray:
    """Superconvergent patch recovery (ZZ 1992)."""
    X = model.X[:, :2]
    ncomp = els[0][1].D.shape[0]
    samples: list[tuple[np.ndarray, np.ndarray]] = []           # per element: (points (k,2), stresses (k,c))
    for _, e in els:
        ue = u[model.equivalent_dof(e)]
        pts, sig = [], []
        for xi, eta in _sampling_points(e):
            s, _, x = e.stress_at_point(model.X, ue, xi, eta)
            pts.append(x)
            sig.append(s)
        samples.append((np.array(pts), np.array(sig)))
    patches: dict[int, list[int]] = {}
    for k, (_, e) in enumerate(els):
        for n in _corners(e):
            patches.setdefault(n, []).append(k)
    boundary = _boundary_corner_nodes(els)
    own = np.full((model.n_node, ncomp), np.nan)
    total = {True: np.zeros((model.n_node, ncomp)), False: np.zeros((model.n_node, ncomp))}
    count = {True: np.zeros(model.n_node), False: np.zeros(model.n_node)}
    for node, ks in patches.items():
        P = np.vstack([samples[k][0] for k in ks])
        S = np.vstack([samples[k][1] for k in ks])
        e0 = els[ks[0]][1]
        scale = max(float(np.ptp(P, axis=0).max()), 1e-300)
        A = _basis(e0, (P - X[node]) / scale)
        if A.shape[0] < A.shape[1] or np.linalg.matrix_rank(A, tol=1e-10 * np.abs(A).max()) < A.shape[1]:
            continue
        coef = np.linalg.lstsq(A, S, rcond=None)[0]
        targets = sorted({n for k in ks for n in els[k][1].nodes})
        values = _basis(e0, (X[targets] - X[node]) / scale) @ coef
        interior = node not in boundary
        if interior:
            own[node] = values[targets.index(node)]
        total[interior][targets] += values
        count[interior][targets] += 1
    avg = _average(model, u, els)
    out = own.copy()
    for n in range(model.n_node):
        if np.all(np.isfinite(out[n])):
            continue
        if count[True][n] > 0:
            out[n] = total[True][n] / count[True][n]
        elif count[False][n] > 0:
            out[n] = total[False][n] / count[False][n]
        else:
            out[n] = avg[n]
    return out


@cite("zienkiewicz_zhu_1987", "zienkiewicz_zhu_1992", note="nodal averaging and SPR")
def recover_stresses(model: Any, u: ArrayLike, method: str = "spr") -> np.ndarray:
    """Recovered (continuous) nodal stresses of a 2-D continuum mesh.

    Parameters
    ----------
    model : Model
        Model with T3, Q4, QM6 or Q8 elements (one formulation).
    u : array_like, shape (n_dof,)
        Displacement solution [m].
    method : {"spr", "average"}
        Superconvergent patch recovery or simple nodal averaging.

    Returns
    -------
    ndarray, shape (n_node, n_components)
        ``σ*`` [Pa]; NaN at nodes without continuum elements.

    Raises
    ------
    ValueError
        No continuum elements, mixed formulations or unknown method.
    """
    U = np.asarray(u, dtype=float)
    els = _continuum(model)
    if method == "average":
        return _average(model, U, els)
    if method == "spr":
        return _spr(model, U, els)
    raise ValueError("method must be 'spr' or 'average'")


def _integrate(model: Any, U: np.ndarray, els: list[tuple[int, _Continuum]],
               reference: Callable[[_Continuum, np.ndarray, float, float], np.ndarray]
               ) -> tuple[np.ndarray, np.ndarray]:
    """Element ``∫ (σref − σh)ᵀ D⁻¹ (σref − σh) dV`` and ``∫ σhᵀ D⁻¹ σh dV``."""
    err = np.zeros(len(els))
    energy = np.zeros(len(els))
    for k, (_, e) in enumerate(els):
        ue = U[model.equivalent_dof(e)]
        Dinv = np.linalg.inv(e.D)
        Xe = e._Xe(model.X)
        for xi, eta, w in _error_rule(e):
            N, _, detJ = e._jacobian(Xe, xi, eta)
            c, _ = e._volume_factor(N, Xe)
            sh, _, x = e.stress_at_point(model.X, ue, xi, eta)
            d = reference(e, x, xi, eta)
            ds = d - sh
            err[k] += float(ds @ Dinv @ ds) * detJ * w * c
            energy[k] += float(sh @ Dinv @ sh) * detJ * w * c
    return err, energy


@cite("zienkiewicz_zhu_1987", "zienkiewicz_zhu_1992", note="ZZ estimator, relative error η and refinement")
def zz_error_estimate(model: Any, u: ArrayLike, method: str = "spr", fraction: float = 0.5) -> ErrorEstimate:
    """Zienkiewicz-Zhu energy-norm error estimate of a 2-D continuum solution.

    Parameters
    ----------
    model : Model
        Model with T3, Q4, QM6 or Q8 elements.
    u : array_like, shape (n_dof,)
        Displacement solution [m] (e.g. ``model.static().u``).
    method : {"spr", "average"}
        Stress recovery, see :func:`recover_stresses`.
    fraction : float
        Elements with indicator ``≥ fraction · max`` are listed in :attr:`ErrorEstimate.refine`.

    Returns
    -------
    ErrorEstimate

    Raises
    ------
    ValueError
        No continuum elements, unknown method or ``fraction`` outside ``[0, 1]``.

    Notes
    -----
    ``‖e‖²_K = ∫_K (σ* − σh)ᵀ D⁻¹ (σ* − σh) dV`` with ``σ* = Σ Nᵢ σ*ᵢ`` (element shape functions),
    integrated with a rule one order above the stiffness rule; ``η = ‖e‖ / √(‖u‖² + ‖e‖²)``.
    For a field the elements reproduce exactly (constant stress) ``η = 0`` to round-off.
    """
    if not 0 <= fraction <= 1:
        raise ValueError("fraction must lie in [0, 1]")
    U = np.asarray(u, dtype=float)
    els = _continuum(model)
    S = recover_stresses(model, U, method)

    def recovered(e: _Continuum, x: np.ndarray, xi: float, eta: float) -> np.ndarray:
        N = e.shape(xi, eta)[0]
        return N @ S[e.nodes]

    err2, energy2 = _integrate(model, U, els, recovered)
    err = np.sqrt(np.maximum(err2, 0.0))
    e_norm = math.sqrt(float(err2.sum()))
    u_norm = math.sqrt(float(energy2.sum()))
    denom = math.sqrt(u_norm ** 2 + e_norm ** 2)
    eta = e_norm / denom if denom > 0 else 0.0
    idx = np.array([i for i, _ in els], dtype=int)
    top = float(err.max())
    refine = idx[err >= fraction * top] if top > 0 else np.array([], dtype=int)
    return ErrorEstimate(element_error=err, error_norm=e_norm, energy_norm=u_norm, eta=eta, recovered=S,
                         refine=refine, elements=idx, method=method, fraction=fraction)


def exact_energy_error(model: Any, u: ArrayLike, exact_stress: Callable[[float, float], Sequence[float]]
                       ) -> tuple[float, np.ndarray]:
    """True energy-norm error ``‖σ − σh‖`` against a known stress field.

    Parameters
    ----------
    model : Model
    u : array_like
        Displacement solution [m].
    exact_stress : callable
        ``exact_stress(x, y)`` → Voigt stress vector [Pa] of the analytical solution.

    Returns
    -------
    error : float
        ``√Σ ∫ (σ − σh)ᵀ D⁻¹ (σ − σh) dV`` [√J].
    element_error : ndarray
        Element contributions (square roots).
    """
    U = np.asarray(u, dtype=float)
    els = _continuum(model)

    def exact(e: _Continuum, x: np.ndarray, xi: float, eta: float) -> np.ndarray:
        return np.asarray(exact_stress(float(x[0]), float(x[1])), dtype=float)

    err2, _ = _integrate(model, U, els, exact)
    return math.sqrt(float(err2.sum())), np.sqrt(np.maximum(err2, 0.0))


def effectivity_index(estimate: ErrorEstimate, exact_error: float) -> float:
    """Effectivity index ``θ = ‖e*‖ / ‖e‖`` (1 for a perfect estimator).

    Parameters
    ----------
    estimate : ErrorEstimate
    exact_error : float
        True error norm, e.g. from :func:`exact_energy_error`.
    """
    if exact_error <= 0:
        raise ValueError("exact error must be positive")
    return estimate.error_norm / exact_error
