"""Parameter study → quadratic response surface → lightest feasible design (Discovery "design variations", docs/13).

A Discovery or Mechanical parameter study gives a small table: input parameters (rib thickness, fillet radius,
retained volume …) and responses (mass, peak stress, deflection, f₁). This module plans the runs (3-level full
factorial), fits a full quadratic surface to each response by least squares, reports the leave-one-out error so
the fit's honesty is visible, and searches the box for the best point that meets every constraint.

A quadratic surface is only trusted inside the sampled box; ``optimise`` never extrapolates.
"""
from __future__ import annotations

import itertools
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

__all__ = ["plan", "Surface", "fit", "optimise"]


def plan(bounds: Mapping[str, tuple[float, float]], levels: int = 3) -> list[dict[str, float]]:
    """Full-factorial points (``levels`` per parameter, ends included)."""
    names = list(bounds)
    grids = [np.linspace(bounds[n][0], bounds[n][1], levels) for n in names]
    return [dict(zip(names, map(float, p), strict=True)) for p in itertools.product(*grids)]


def _terms(X: np.ndarray) -> np.ndarray:
    n, k = X.shape
    cols = [np.ones(n)] + [X[:, i] for i in range(k)]
    cols += [X[:, i] * X[:, j] for i in range(k) for j in range(i, k)]
    return np.column_stack(cols)


@dataclass
class Surface:
    names: list[str]
    lo: np.ndarray
    hi: np.ndarray
    coef: np.ndarray
    r2: float
    loo_rmse: float

    def _scale(self, X: np.ndarray) -> np.ndarray:
        return 2 * (X - self.lo) / (self.hi - self.lo) - 1

    def __call__(self, point: Mapping[str, float] | np.ndarray) -> np.ndarray:
        X = np.atleast_2d(np.array([point[n] for n in self.names], float) if isinstance(point, Mapping)
                          else np.asarray(point, float))
        return _terms(self._scale(X)) @ self.coef


def fit(points: Sequence[Mapping[str, float]], values: Sequence[float]) -> Surface:
    """Least-squares full quadratic in the parameters scaled to [-1, 1]; needs at least as many runs as terms."""
    names = list(points[0])
    X = np.array([[p[n] for n in names] for p in points], float)
    y = np.asarray(values, float)
    lo, hi = X.min(0), X.max(0)
    if np.any(hi <= lo):
        raise ValueError("every parameter must take at least two values")
    Z = _terms(2 * (X - lo) / (hi - lo) - 1)
    if len(y) < Z.shape[1]:
        raise ValueError(f"{len(y)} runs for {Z.shape[1]} quadratic terms: add runs or drop a parameter")
    coef, *_ = np.linalg.lstsq(Z, y, rcond=None)
    res = y - Z @ coef
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((res ** 2).sum()) / ss if ss > 0 else 1.0
    H = Z @ np.linalg.pinv(Z)
    lev = np.clip(np.diag(H), 0, 1 - 1e-12)
    loo = res / (1 - lev)
    return Surface(names, lo, hi, coef, r2, float(np.sqrt((loo ** 2).mean())))


def optimise(objective: Surface, constraints: Mapping[str, tuple[Surface, float]], n: int = 41,
             sense: str = "min") -> dict:
    """Best grid point inside the sampled box with every ``surface <= limit``; ``sense`` 'min' or 'max'."""
    names = objective.names
    for s, _ in constraints.values():
        if s.names != names:
            raise ValueError("all surfaces must share the same parameters")
    grids = [np.linspace(objective.lo[i], objective.hi[i], n) for i in range(len(names))]
    P = np.array(list(itertools.product(*grids)))
    ok = np.ones(len(P), bool)
    for s, limit in constraints.values():
        ok &= s(P) <= limit
    if not ok.any():
        return {"feasible": False}
    f = objective(P)
    f = np.where(ok, f, np.inf if sense == "min" else -np.inf)
    i = int(np.argmin(f) if sense == "min" else np.argmax(f))
    return {"feasible": True, "point": dict(zip(names, map(float, P[i]), strict=True)), "objective": float(f[i]),
            **{f"{k}_pred": float(s(P[i:i + 1])[0]) for k, (s, _) in constraints.items()}}
