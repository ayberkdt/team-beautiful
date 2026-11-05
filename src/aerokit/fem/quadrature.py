"""Numerical integration rules for the reference elements.

* :func:`gauss1d` / :func:`gauss2d` - Gauss-Legendre points on ``[-1, 1]`` and their tensor product
  on ``[-1, 1]²`` (quadrilaterals);
* :func:`triangle` - rules on the reference triangle ``{ξ ≥ 0, η ≥ 0, ξ + η ≤ 1}`` (area 1/2).

Tetrahedron and hexahedron rules live next to the solid elements
(:func:`aerokit.fem.elements.solid.rule_tet`, :func:`~aerokit.fem.elements.solid.rule_tet_duffy`,
:func:`~aerokit.fem.elements.solid.rule_hex`).
"""
from __future__ import annotations

import numpy as np

from aerokit.references import cite

__all__ = ["gauss1d", "gauss2d", "triangle"]


@cite("zienkiewicz_taylor_2013", note="Gauss-Legendre quadrature")
def gauss1d(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Gauss-Legendre rule with ``n`` points on ``[-1, 1]``.

    Parameters
    ----------
    n : int
        Number of points (``n ≥ 1``); exact for polynomials of degree ``2n − 1``.

    Returns
    -------
    x, w : ndarray, shape (n,)
        Abscissae and weights (``Σ w = 2``).
    """
    x, w = np.polynomial.legendre.leggauss(n)
    return x, w


def gauss2d(n: int) -> list[tuple[float, float, float]]:
    """``n × n`` tensor-product Gauss rule on ``[-1, 1]²``.

    Parameters
    ----------
    n : int
        Points per direction.

    Returns
    -------
    list of (ξ, η, w)
        Points and weights (``Σ w = 4``).
    """
    x, w = gauss1d(n)
    return [(float(x[i]), float(x[j]), float(w[i] * w[j])) for i in range(n) for j in range(n)]


@cite("strang_fix_1973", note="one- and three-point interior rules")
def triangle(n: int) -> list[tuple[float, float, float]]:
    """Quadrature rule on the reference triangle (weights sum to 1/2, the reference area).

    Parameters
    ----------
    n : {1, 3}
        ``1``: centroid rule (exact for linear integrands);
        ``3``: interior points ``(1/6, 1/6), (2/3, 1/6), (1/6, 2/3)`` (exact for quadratics).

    Returns
    -------
    list of (ξ, η, w)

    Raises
    ------
    ValueError
        For any other ``n``.
    """
    if n == 1:
        return [(1 / 3, 1 / 3, 0.5)]
    if n == 3:
        return [(1 / 6, 1 / 6, 1 / 6), (2 / 3, 1 / 6, 1 / 6), (1 / 6, 2 / 3, 1 / 6)]
    raise ValueError("triangle rule needs n ∈ {1, 3}")
