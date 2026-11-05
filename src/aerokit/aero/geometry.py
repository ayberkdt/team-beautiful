"""Geometry helpers: NACA 4-digit airfoil, trapezoidal wing planform, point-file export.

The last coefficient of the NACA 4-digit thickness equation (Abbott & von Doenhoff) selects the
trailing edge: -0.1015 gives an open (finite-thickness) trailing edge, -0.1036 a closed (sharp) one.
"""
from __future__ import annotations

import math
import os
from collections.abc import Sequence

import numpy as np

from aerokit.references import cite


@cite("abbott_vondoenhoff_1959", note="NACA 4-digit thickness distribution and mean line")
def naca4(code: str, n: int = 121, closed_trailing_edge: bool = False,
          chord: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Coordinates of a NACA 4-digit airfoil with cosine spacing.

    Parameters
    ----------
    code : str
        Four-digit designation, e.g. ``"0012"`` or ``"2412"``.
    n : int, optional
        Number of points per surface (the leading-edge point is shared).
    closed_trailing_edge : bool, optional
        Use the -0.1036 coefficient (sharp trailing edge) instead of -0.1015.
    chord : float, optional
        Chord length [m]; the coordinates are scaled by it.

    Returns
    -------
    x, y : numpy.ndarray
        Coordinates [m], ordered upper trailing edge -> leading edge -> lower trailing edge
        (``2 n - 1`` points).

    Raises
    ------
    ValueError
        If ``code`` is not a four-digit string.

    Notes
    -----
    Thickness: y_t = 5 t (0.2969 sqrt(x) - 0.1260 x - 0.3516 x^2 + 0.2843 x^3 + a4 x^4).
    Mean line (max camber m at p): y_c = m/p^2 (2 p x - x^2) for x < p,
    y_c = m/(1 - p)^2 ((1 - 2 p) + 2 p x - x^2) otherwise; the thickness is applied normal to the
    mean line. Cosine spacing x = (1 - cos beta)/2 clusters points at both edges.

    Examples
    --------
    >>> x, y = naca4("0012", n=101)
    >>> len(x)
    201
    """
    if len(code) != 4 or not code.isdigit():
        raise ValueError("expected a NACA 4-digit code, e.g. 0012 or 2412")
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    beta = np.linspace(0, math.pi, n)
    x = 0.5 * (1 - np.cos(beta))
    a4 = -0.1036 if closed_trailing_edge else -0.1015
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2
                  + 0.2843 * x ** 3 + a4 * x ** 4)
    if m == 0 or p == 0:
        yc = np.zeros_like(x)
        dyc = np.zeros_like(x)
    else:
        fore = x < p
        yc = np.where(fore, m / p ** 2 * (2 * p * x - x ** 2),
                      m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x ** 2))
        dyc = np.where(fore, 2 * m / p ** 2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    X = np.concatenate([xu[::-1], xl[1:]]) * chord
    Y = np.concatenate([yu[::-1], yl[1:]]) * chord
    return X, Y


def trailing_edge_thickness(x: Sequence[float] | np.ndarray, y: Sequence[float] | np.ndarray) -> float:
    """Trailing-edge thickness of an airfoil given as a closed point loop.

    Parameters
    ----------
    x, y : array_like
        Airfoil coordinates [m] starting and ending at the trailing edge (as from :func:`naca4`).

    Returns
    -------
    float
        Distance between the first and the last point [m].
    """
    return math.hypot(x[0] - x[-1], y[0] - y[-1])


def planform(S: float, AR: float, taper: float) -> dict[str, float]:
    """Dimensions of a straight-tapered (trapezoidal) wing.

    Parameters
    ----------
    S : float
        Reference wing area [m^2].
    AR : float
        Aspect ratio b^2/S [-].
    taper : float
        Taper ratio c_tip/c_root [-].

    Returns
    -------
    dict[str, float]
        ``b`` span [m], ``c_root`` root chord [m], ``c_tip`` tip chord [m], ``MAC`` mean
        aerodynamic chord [m], ``y_MAC`` spanwise station of the MAC from the root [m].

    Notes
    -----
    b = sqrt(AR S), c_root = 2 S / (b (1 + lambda)), MAC = 2/3 c_root (1 + lambda + lambda^2)/(1 + lambda),
    y_MAC = b/6 (1 + 2 lambda)/(1 + lambda).

    Examples
    --------
    >>> planform(10.0, 10.0, 1.0)["MAC"]
    1.0
    """
    b = math.sqrt(AR * S)
    c_root = 2 * S / (b * (1 + taper))
    c_tip = taper * c_root
    mac = 2 / 3 * c_root * (1 + taper + taper ** 2) / (1 + taper)
    y_mac = b / 6 * (1 + 2 * taper) / (1 + taper)
    return {"b": b, "c_root": c_root, "c_tip": c_tip, "MAC": mac, "y_MAC": y_mac}


def write_point_file(path: str | os.PathLike[str], x: Sequence[float] | np.ndarray, y: Sequence[float] | np.ndarray,
                     z: float = 0.0, format: str = "xyz") -> None:
    """Write airfoil points to a text file.

    Parameters
    ----------
    path : str or path-like
        Output file.
    x, y : array_like
        Point coordinates [m]; must have the same length.
    z : float, optional
        Constant z coordinate [m].
    format : {"xyz", "dm"}, optional
        ``"xyz"``: space-separated ``x y z`` lines (general purpose).
        ``"dm"``: DesignModeler 3D Curve format ``group point x y z`` (NOT VERIFIED: the format
        was written from memory; test the import on first use).

    Raises
    ------
    ValueError
        If ``x`` and ``y`` differ in length.
    """
    with open(path, "w", encoding="ascii") as f:
        for i, (xi, yi) in enumerate(zip(x, y, strict=True), start=1):
            if format == "dm":
                f.write(f"1 {i} {xi:.7f} {yi:.7f} {z:.7f}\n")
            else:
                f.write(f"{xi:.7f} {yi:.7f} {z:.7f}\n")
