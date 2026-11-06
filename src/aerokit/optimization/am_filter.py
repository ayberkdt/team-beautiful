"""Layer-by-layer additive-manufacturing filter for 2-D density topology optimisation (overhang ≤ 45°).

Langelaar (2017, *Struct. Multidisc. Optim.* 55:871–883, doi 10.1007/s00158-016-1522-2), open-access PDF read on
2026-11-03: the design is "printed" layer by layer from the base plate; an element can only be as dense as the
densest of the three elements below it (left, centre, right), a 45° rule on a square grid; two at the domain edge.

* ``smax(v) = (Σ vⱼ^P)^(1/Q)`` with ``Q = P + ln N / ln ξ₀`` (Eq. 5–6);
* ``smin(x, Ξ) = ½ (x + Ξ − √((x − Ξ)² + ε) + √ε)`` (Eq. 3);
* printed density ``ξ = smin(x, smax(ξ_below))``, the base layer printed as designed (Eq. 7–8).

Defaults are the paper's (p. 875): ε = 1e-4, P = 40, ξ₀ = 0.5; the paper's top88 recipe also lowers the OC move
limit to 0.05. An earlier version of this module used P = 80, ε = 1e-3 (a CILAMCE 2024 study); pass them explicitly
to reproduce ``prev_guess/01_Ansys/scenarios/am_filter_demo.json``. Because Q < P, a fully dense support row gives
Ξ = N^(1/Q) > 1, so printed densities can exceed 1 by a fraction of a per cent; that is the paper's operator.

The backward pass is the exact adjoint (Eq. 10–14), checked against finite differences in the tests.
"""
from __future__ import annotations

import math

import numpy as np

from aerokit.references import cite

__all__ = ["AMFilter2D", "overhang_violations"]

_ROT = {"S": 0, "E": 1, "N": 2, "W": 3}       # base plate side → quarter-turns that bring it to the bottom


class AMFilter2D:
    """Filter for a 2-D density array ``(nely, nelx)`` (row 0 at the top), base plate on side ``base``."""

    def __init__(self, base: str = "S", P: float = 40.0, eps: float = 1e-4, xi0: float = 0.5) -> None:
        if base not in _ROT:
            raise ValueError("base must be 'S', 'N', 'E' or 'W'")
        self.k, self.P, self.eps, self.xi0 = _ROT[base], float(P), float(eps), float(xi0)
        self._cache: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def _q(self, n: int) -> float:
        return self.P + math.log(n) / math.log(self.xi0)

    @cite("langelaar_2017", note="Eq. (3)-(8)")
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Printed density of the array ``x`` (same shape)."""
        a = np.rot90(np.asarray(x, float), self.k)          # base now at the bottom row
        ny, nx = a.shape
        xi = np.empty_like(a)
        xi[-1] = a[-1]
        self._cache = []
        cols = np.arange(nx)
        lo, hi = np.maximum(cols - 1, 0), np.minimum(cols + 1, nx - 1)
        n = (hi - lo + 1)
        for r in range(ny - 2, -1, -1):
            below = xi[r + 1]
            s = np.array([np.sum(below[lo[c]:hi[c] + 1] ** self.P) for c in range(nx)])
            q = np.array([self._q(int(k)) for k in n])
            Xi = np.power(np.maximum(s, 1e-300), 1.0 / q)
            d = a[r] - Xi
            root = np.sqrt(d * d + self.eps)
            xi[r] = 0.5 * (a[r] + Xi - root + math.sqrt(self.eps))
            self._cache.append((s, q, d / root))
        return np.rot90(xi, -self.k)

    def backward(self, x: np.ndarray, dxi: np.ndarray) -> np.ndarray:
        """∂f/∂x from ∂f/∂ξ (call :meth:`forward` on the same ``x`` first)."""
        a = np.rot90(np.asarray(x, float), self.k)
        lam = np.rot90(np.asarray(dxi, float), self.k).copy()
        xi = np.rot90(self.forward(x), self.k)
        ny, nx = a.shape
        cols = np.arange(nx)
        lo, hi = np.maximum(cols - 1, 0), np.minimum(cols + 1, nx - 1)
        dx = np.zeros_like(a)
        # walk from the top layer down: lam[r] is complete once every layer above has passed its share down
        for r in range(ny - 1):
            s, q, t = self._cache[ny - 2 - r]
            dsmin_dx = 0.5 * (1 - t)
            dsmin_dXi = 0.5 * (1 + t)
            dx[r] = lam[r] * dsmin_dx
            g = lam[r] * dsmin_dXi * (1.0 / q) * np.power(np.maximum(s, 1e-300), 1.0 / q - 1.0) * self.P
            below = xi[r + 1]
            for c in range(nx):
                seg = slice(lo[c], hi[c] + 1)
                lam[r + 1, seg] += g[c] * below[seg] ** (self.P - 1)
        dx[-1] = lam[-1]
        return np.rot90(dx, -self.k)


def overhang_violations(x: np.ndarray, base: str = "S", threshold: float = 0.5) -> int:
    """Solid elements (above the base layer) with no solid element among the three below."""
    a = np.rot90(np.asarray(x, float) > threshold, _ROT[base])
    sup = a[1:].copy()
    sup[:, 1:] |= a[1:, :-1]
    sup[:, :-1] |= a[1:, 1:]
    return int((a[:-1] & ~sup).sum())
