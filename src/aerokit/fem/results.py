"""Typed analysis results.

Each result is a frozen dataclass. For backward compatibility (and convenient printing) the
classes also implement the read-only :class:`~collections.abc.Mapping` protocol, so
``result["u"]`` and ``result.u`` are equivalent and ``dict(result)`` gives a plain dictionary.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field, fields
from typing import Any

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]

__all__ = ["Result", "StaticResult", "ModalResult", "BucklingResult", "TransientResult", "HarmonicResult",
           "NonlinearResult", "SolverInfo"]


class Result(Mapping[str, Any]):
    """Mixin giving dataclass results a read-only mapping interface."""

    # Mapping.__eq__ would compare NumPy arrays element-wise; results compare by identity.
    __eq__ = object.__eq__
    __hash__ = object.__hash__

    def _names(self) -> list[str]:
        return [f.name for f in fields(self)]  # type: ignore[arg-type]

    def __getitem__(self, key: str) -> Any:
        if key not in self._names():
            raise KeyError(key)
        return getattr(self, key)

    def __iter__(self) -> Iterator[str]:
        return iter(self._names())

    def __len__(self) -> int:
        return len(self._names())

    def to_dict(self) -> dict[str, Any]:
        """Plain ``dict`` with NumPy arrays converted to lists (JSON friendly)."""
        def conv(v: Any) -> Any:
            if isinstance(v, np.ndarray):
                return v.tolist()
            if isinstance(v, np.generic):
                return v.item()
            if isinstance(v, Result):
                return v.to_dict()
            if isinstance(v, list | tuple):
                return [conv(x) for x in v]
            if isinstance(v, dict):
                return {k: conv(x) for k, x in v.items()}
            return v
        return {k: conv(getattr(self, k)) for k in self._names()}


@dataclass(frozen=True)
class SolverInfo(Result):
    """How a linear system was solved."""

    method: str
    n: int
    nnz: int
    iterations: int = 0
    residual: float = 0.0
    condition_estimate: float | None = None
    seconds: float = 0.0


@dataclass(frozen=True, eq=False)
class StaticResult(Result):
    """Linear static solution ``K u = F``.

    Attributes
    ----------
    u : ndarray, shape (n_dof,) or (n_dof, n_cases)
        Nodal displacements (global DOF order ``node * ndof + local``).
    reaction : ndarray
        ``K u − F`` for every DOF (non-zero only at constrained DOFs).
    energy : float or ndarray
        Strain energy ``½ uᵀ K u`` [J] (one value per load case).
    residual : float
        Relative residual ``‖K_r u_r − f_r‖ / ‖f_r‖`` of the reduced system.
    solver : SolverInfo
        Solver details.
    """

    u: Array
    reaction: Array
    energy: Any
    residual: float
    solver: SolverInfo | None = None


@dataclass(frozen=True, eq=False)
class ModalResult(Result):
    """Generalised eigenproblem ``K φ = ω² M φ`` (mass-normalised modes)."""

    omega: Array
    f: Array
    modes: Array
    participation: Array | None = None
    effective_mass: Array | None = None


@dataclass(frozen=True, eq=False)
class BucklingResult(Result):
    """Linear buckling ``(K + λ K_G) φ = 0``; ``lambda_`` are positive load factors (ascending)."""

    lambda_: Array
    modes: Array


@dataclass(frozen=True, eq=False)
class TransientResult(Result):
    """Time history from direct integration or modal superposition."""

    t: Array
    u: Array
    v: Array
    a: Array
    method: str = ""
    energy: Array | None = None


@dataclass(frozen=True, eq=False)
class HarmonicResult(Result):
    """Steady-state harmonic response ``u(t) = Re(U e^{iωt})``."""

    f: Array
    U: Array
    method: str = ""


@dataclass(frozen=True, eq=False)
class NonlinearResult(Result):
    """Load-displacement path of a geometrically non-linear analysis."""

    load_factor: Array
    u: Array
    iterations: Array
    converged: bool
    method: str = ""
    history: list[dict[str, float]] = field(default_factory=list)
