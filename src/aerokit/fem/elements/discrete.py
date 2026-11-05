"""Discrete (lumped) elements: linear springs, point masses and viscous dashpots.

All three follow the element protocol of :mod:`aerokit.fem.model` (``nodes``, ``ndof``, ``k``,
``m``, ``kg``, ``stress``) so they can be mixed freely with bars, frames and continuum elements.

* :class:`Spring` — linear spring along one local DOF or along a direction vector, either between
  two nodes or from a node to the (fixed) ground. A grounded spring is a single-node element, so it
  adds no ground node to the model.
* :class:`PointMass` — translational mass and optional rotary inertia at one node.
* :class:`Dashpot` — linear viscous damper; it has zero stiffness and mass and provides the damping
  matrix ``c(X)`` that :func:`aerokit.fem.dynamics.damping_matrix` assembles into ``C``.

The two-node spring matrix is the bar matrix with the axial stiffness ``EA/L`` replaced by ``k``
[cook_2002]_: ``k_e = k [[e eᵀ, −e eᵀ], [−e eᵀ, e eᵀ]]`` with ``e`` the unit direction in the
nodal DOF space; the grounded spring keeps only the ``k e eᵀ`` block.

Units SI: ``k`` [N/m] or [N·m/rad], ``c`` [N·s/m] or [N·m·s/rad], mass [kg], inertia [kg·m²].
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from aerokit.references import cite

__all__ = ["Spring", "PointMass", "Dashpot"]


def _unit(ndof: int, dof: int | None, direction: Sequence[float] | np.ndarray | None) -> np.ndarray:
    """Unit vector in the nodal DOF space selected by ``dof`` or ``direction``."""
    if int(ndof) < 1:
        raise ValueError("ndof must be a positive integer")
    if (dof is None) == (direction is None):
        raise ValueError("give exactly one of dof= or direction=")
    e = np.zeros(int(ndof))
    if dof is not None:
        if not 0 <= int(dof) < ndof:
            raise ValueError(f"dof {dof} out of range for ndof = {ndof}")
        e[int(dof)] = 1.0
        return e
    d = np.asarray(direction, dtype=float).ravel()
    if d.size == 0 or d.size > ndof:
        raise ValueError(f"direction must have 1..{ndof} components")
    n = float(np.linalg.norm(d))
    if not np.isfinite(n) or n == 0.0:
        raise ValueError("direction vector must be finite and non-zero")
    e[:d.size] = d / n
    return e


class _LinearLink:
    """Common part of :class:`Spring` and :class:`Dashpot`: ``value · B`` with ``B = [±e][±e]ᵀ``."""

    def __init__(self, i: int, j: int | None, value: float, ndof: int, dof: int | None,
                 direction: Sequence[float] | np.ndarray | None, name: str) -> None:
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")
        self.nodes: list[int] = [int(i)] if j is None else [int(i), int(j)]
        self.grounded = j is None
        self.ndof = int(ndof)
        self.e = _unit(self.ndof, dof, direction)

    def _b(self) -> np.ndarray:
        """Row vector mapping element DOFs to the link elongation (``j − i`` along ``e``)."""
        return self.e.copy() if self.grounded else np.concatenate([-self.e, self.e])

    def _matrix(self, value: float) -> np.ndarray:
        b = self._b()
        return value * np.outer(b, b)

    def elongation(self, ue: np.ndarray) -> float:
        """Relative displacement along ``e`` (positive = extension)."""
        return float(self._b() @ np.asarray(ue, dtype=float))

    def _zeros(self) -> np.ndarray:
        n = self.ndof * len(self.nodes)
        return np.zeros((n, n))


@cite("cook_2002", note="two-node bar/spring stiffness matrix")
class Spring(_LinearLink):
    """Linear spring between two nodes (``j`` given) or from node ``i`` to ground (``j=None``).

    Parameters
    ----------
    i : int
        First node.
    j : int or None
        Second node; ``None`` makes a grounded (single-node) spring.
    k : float
        Stiffness [N/m] (translational DOF) or [N·m/rad] (rotational DOF), ``k ≥ 0``.
    ndof : int
        DOFs per node of the model.
    dof : int, optional
        Local DOF the spring acts along (e.g. ``2`` = rotation of a 2-D frame node).
    direction : array_like, optional
        Direction vector in the nodal DOF space (padded with zeros up to ``ndof``; normalised).
        Exactly one of ``dof`` and ``direction`` must be given.

    Examples
    --------
    >>> import numpy as np
    >>> s = Spring(0, 1, k=2.0, ndof=2, dof=0)
    >>> s.k(np.zeros((2, 2)))[0]
    array([ 2.,  0., -2.,  0.])
    """

    def __init__(self, i: int, j: int | None, k: float, ndof: int, dof: int | None = None,
                 direction: Sequence[float] | np.ndarray | None = None) -> None:
        super().__init__(i, j, k, ndof, dof, direction, "spring stiffness")
        self.stiffness = float(k)

    def k(self, X: np.ndarray) -> np.ndarray:
        """Element stiffness matrix (global axes)."""
        return self._matrix(self.stiffness)

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Zero mass matrix (a spring is massless)."""
        return self._zeros()

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Zero geometric stiffness (the spring direction is fixed)."""
        return self._zeros()

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Spring force (tension positive) and elongation."""
        d = self.elongation(ue)
        return {"force": self.stiffness * d, "elongation": d}


@cite("chopra_2012", note="linear viscous damper, force = c x relative velocity")
class Dashpot(_LinearLink):
    """Linear viscous damper between two nodes or from a node to ground.

    Parameters
    ----------
    i, j, ndof, dof, direction
        As for :class:`Spring`.
    c : float
        Damping coefficient [N·s/m] or [N·m·s/rad], ``c ≥ 0``.

    Notes
    -----
    ``k`` and ``m`` are zero; :meth:`c` returns the damping matrix, collected by
    :func:`aerokit.fem.dynamics.damping_matrix`.
    """

    def __init__(self, i: int, j: int | None, c: float, ndof: int, dof: int | None = None,
                 direction: Sequence[float] | np.ndarray | None = None) -> None:
        super().__init__(i, j, c, ndof, dof, direction, "damping coefficient")
        self.coefficient = float(c)

    def c(self, X: np.ndarray) -> np.ndarray:
        """Element damping matrix (global axes)."""
        return self._matrix(self.coefficient)

    def k(self, X: np.ndarray) -> np.ndarray:
        """Zero stiffness matrix."""
        return self._zeros()

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Zero mass matrix."""
        return self._zeros()

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Zero geometric stiffness."""
        return self._zeros()

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Relative displacement along the dashpot axis (forces need velocities)."""
        return {"elongation": self.elongation(ue)}

    def force(self, ve: np.ndarray) -> float:
        """Damper force ``c · (relative velocity)`` for element nodal velocities ``ve``."""
        return self.coefficient * self.elongation(ve)


@cite("cook_2002", note="concentrated (diagonal) nodal mass")
class PointMass:
    """Concentrated mass (and rotary inertia) at one node.

    Parameters
    ----------
    node : int
        Node index.
    mass : float
        Translational mass [kg], applied to every translational DOF.
    ndof : int
        DOFs per node of the model.
    inertia : float or sequence of float
        Rotary inertia [kg·m²] of the rotational DOFs (scalar: the same for all of them).
    translational : sequence of int, optional
        Local DOFs that are translations. Default: the first ``min(ndof, dim)`` DOFs, with ``dim``
        the number of coordinates of the model (true for trusses, frames, plane and solid elements;
        give it explicitly for the Mindlin plate, whose translation is DOF 0 only). All other DOFs
        are rotational.
    """

    def __init__(self, node: int, mass: float, ndof: int, inertia: float | Sequence[float] = 0.0,
                 translational: Sequence[int] | None = None) -> None:
        if not np.isfinite(mass) or mass < 0:
            raise ValueError("mass must be finite and non-negative")
        if int(ndof) < 1:
            raise ValueError("ndof must be a positive integer")
        J = np.atleast_1d(np.asarray(inertia, dtype=float))
        if not np.all(np.isfinite(J)) or np.any(J < 0):
            raise ValueError("rotary inertia must be finite and non-negative")
        if translational is not None:
            tr = sorted({int(t) for t in translational})
            if any(not 0 <= t < ndof for t in tr):
                raise ValueError(f"translational DOFs must lie in 0..{ndof - 1}")
            self.translational: list[int] | None = tr
        else:
            self.translational = None
        self.nodes = [int(node)]
        self.ndof = int(ndof)
        self.mass = float(mass)
        self.inertia = J

    def _diagonal(self, dim: int) -> np.ndarray:
        tr = self.translational if self.translational is not None else list(range(min(self.ndof, dim)))
        rot = [d for d in range(self.ndof) if d not in tr]
        if self.inertia.size not in (1, len(rot)):
            raise ValueError(f"inertia needs 1 or {len(rot)} values (rotational DOFs {rot})")
        diag = np.zeros(self.ndof)
        diag[tr] = self.mass
        if rot:
            diag[rot] = self.inertia if self.inertia.size == len(rot) else self.inertia[0]
        return diag

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Diagonal mass matrix (consistent and lumped forms coincide)."""
        return np.diag(self._diagonal(int(np.shape(X)[1])))

    def k(self, X: np.ndarray) -> np.ndarray:
        """Zero stiffness matrix."""
        return np.zeros((self.ndof, self.ndof))

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Zero geometric stiffness."""
        return np.zeros((self.ndof, self.ndof))

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """No stresses; returns the nodal displacement for convenience."""
        return {"u": np.asarray(ue, dtype=float).copy()}
