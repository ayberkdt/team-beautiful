"""Modal and thermal checks of a black-and-white topology design on the card's unit-square Q4 grid.

The three ways the Ansys task may leave the static-strength path (docs/11) need two more physics on the same
grid that :mod:`aerokit.design.card` uses:

* **natural frequency** — ``K φ = ω² M φ`` with the solid elements only (void elements are dropped, so no
  spurious void modes), consistent Q4 mass, and optional lumped masses (an avionics box, a motor) on nodes;
* **thermal stress** — a uniform temperature change ``ΔT`` on a part whose supports stop it from growing.

Scaling. Elements are unit squares of physical size ``h``; the plane-stress stiffness of a square element does not
depend on its size, so ``K = E t K̂`` and ``M = ρ t h² M̂``. Thermal stresses are solved for ``E α ΔT = 1`` and
scale linearly: ``σ = E α ΔT σ̂``; displacements scale as ``u = α ΔT h û``.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.sparse import csgraph

from aerokit.optimization import topology as tp

__all__ = ["MASS_Q4", "centre_stress", "von_mises", "solid_dofs", "load_path", "modal", "thermal_unit"]

_N4 = np.array([[4, 2, 1, 2], [2, 4, 2, 1], [1, 2, 4, 2], [2, 1, 2, 4]], float) / 36.0
MASS_Q4 = np.zeros((8, 8))
for _d in (0, 1):
    MASS_Q4[_d::2, _d::2] = _N4
"""Consistent mass of a unit-square bilinear element, unit density and thickness (nodes counter-clockwise)."""

_DNDX = np.array([-0.5, 0.5, 0.5, -0.5])        # ∂N/∂x at the centre of a unit square, nodes LL, LR, UR, UL
_DNDY = np.array([-0.5, -0.5, 0.5, 0.5])
_BC = np.zeros((3, 8))
_BC[0, 0::2], _BC[1, 1::2], _BC[2, 0::2], _BC[2, 1::2] = _DNDX, _DNDY, _DNDY, _DNDX


def _d_plane_stress(nu: float) -> np.ndarray:
    return np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]]) / (1 - nu ** 2)


def centre_stress(grid: tp.Grid2D, U: np.ndarray, nu: float,
                  eps0: Sequence[float] | np.ndarray = (0.0, 0.0, 0.0)) -> np.ndarray:
    """(nel, 3) element-centre ``[σx, σy, τxy]`` for unit modulus, minus an initial strain ``eps0``."""
    u = np.asarray(U).reshape(grid.ndof, -1)[:, 0]
    strain = u[grid.edof] @ _BC.T - np.asarray(eps0, float)
    return strain @ _d_plane_stress(nu).T


def von_mises(s: np.ndarray) -> np.ndarray:
    """Plane-stress von Mises of ``[σx, σy, τxy]`` rows."""
    sx, sy, txy = s[..., 0], s[..., 1], s[..., 2]
    return np.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2)


def solid_dofs(grid: tp.Grid2D, solid: np.ndarray, fixed: Sequence[int]) -> np.ndarray:
    """DOFs carried by at least one solid element, minus the fixed ones."""
    used = np.unique(grid.edof[np.asarray(solid, bool)].ravel())
    return np.setdiff1d(used, np.asarray(fixed, int))


def load_path(grid: tp.Grid2D, solid: np.ndarray, fixed: Sequence[int]) -> np.ndarray:
    """Solid elements joined to the supports through shared element *edges*.

    A thresholded topology result can leave islands or parts held by a single corner node; both are mechanisms
    (zero-frequency modes) and carry no load, so the modal and thermal checks drop them.
    """
    solid = np.asarray(solid, float) > 0.5
    nodes = grid.edof[:, 0::2] // 2                                       # (nel, 4) nodes LL, LR, UR, UL
    idx = np.flatnonzero(solid)
    edge_owner: dict[tuple[int, int], list[int]] = {}
    for e in idx:
        n = nodes[e]
        for a, b in ((n[0], n[1]), (n[1], n[2]), (n[2], n[3]), (n[3], n[0])):
            edge_owner.setdefault((min(a, b), max(a, b)), []).append(int(e))
    rows, cols = [], []
    for owners in edge_owner.values():
        if len(owners) == 2:
            rows.append(owners[0])
            cols.append(owners[1])
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(grid.nel, grid.nel))
    _, label = csgraph.connected_components(A, directed=False)
    fixed_nodes = np.unique(np.asarray(fixed, int) // 2)
    seeds = idx[np.isin(nodes[idx], fixed_nodes).sum(axis=1) >= 2]       # held along an edge, not a corner
    keep = np.isin(label, np.unique(label[seeds])) & solid
    return keep


def _assemble(grid: tp.Grid2D, solid: np.ndarray, ke: np.ndarray) -> sp.csc_matrix:
    w = np.asarray(solid, float)
    data = (ke.ravel()[None, :] * w[:, None]).ravel()
    A = sp.coo_matrix((data, (grid.iK, grid.jK)), shape=(grid.ndof, grid.ndof)).tocsc()
    return (A + A.T) / 2


def modal(grid: tp.Grid2D, solid: np.ndarray, fixed: Sequence[int], E: float, rho: float, t: float, h: float,
          point_masses: Mapping[int, float] | None = None, n: int = 3) -> dict:
    """First ``n`` natural frequencies [Hz] of the solid part, with lumped masses ``{node: kg}`` on nodes.

    Returns ``{"frequencies_Hz", "structural_mass_kg", "added_mass_kg"}``.
    """
    solid = load_path(grid, solid, fixed)
    K = _assemble(grid, solid, grid.KE) * (E * t)
    M = _assemble(grid, solid, MASS_Q4) * (rho * t * h * h)
    M = M.tolil()
    act = solid_dofs(grid, solid, fixed)
    added = 0.0
    for node, kg in (point_masses or {}).items():
        if 2 * int(node) not in act:
            raise ValueError(f"added mass on node {node}, which no load-carrying solid element holds")
        for d in (0, 1):
            M[2 * int(node) + d, 2 * int(node) + d] += kg
        added += kg
    Ka, Ma = K[act][:, act].tocsc(), M.tocsc()[act][:, act].tocsc()
    k = min(n, len(act) - 2)
    w2 = spla.eigsh(Ka, k=k, M=Ma, sigma=0.0, which="LM", return_eigenvectors=False)
    f = np.sqrt(np.clip(np.sort(w2), 0, None)) / (2 * np.pi)
    return {"frequencies_Hz": f.tolist(), "structural_mass_kg": float(solid.sum() * rho * t * h * h),
            "added_mass_kg": added}


def thermal_unit(grid: tp.Grid2D, solid: np.ndarray, fixed: Sequence[int], nu: float | None = None) -> np.ndarray:
    """(nel, 3) centre stresses from a uniform temperature rise with ``E α ΔT = 1``; void rows are zero.

    The fixed DOFs are held at zero: they stand for a structure that does not grow. For a structure that grows
    too (a metal bracket on a CFRP frame), use ``α = α_part − α_structure`` when scaling.
    """
    nu = grid.nu if nu is None else nu
    solid = load_path(grid, solid, fixed)
    K = _assemble(grid, solid, grid.KE)
    eps0 = np.array([1.0, 1.0, 0.0])
    fe = _BC.T @ (_d_plane_stress(nu) @ eps0)                # ∫Bᵀ D ε0 dA; B is linear, so the centre value × area
    F = np.zeros(grid.ndof)
    np.add.at(F, grid.edof[solid].ravel(), np.tile(fe, int(solid.sum())))
    act = solid_dofs(grid, solid, fixed)
    U = np.zeros(grid.ndof)
    U[act] = spla.splu(K[act][:, act].tocsc()).solve(F[act])
    s = centre_stress(grid, U, nu, eps0)
    s[~solid] = 0.0
    return s
