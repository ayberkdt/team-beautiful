"""Section properties: arbitrary polygons (Green's theorem), sections with holes and multi-material
sections, thin-walled open sections (shear flow, shear centre, sectorial properties, Cw),
unsymmetric bending and multi-cell closed-section torsion.

Axis and sign conventions (the same throughout the module):

- Ix = ∫(y − yc)² dA, Iy = ∫(x − xc)² dA, Ixy = ∫(x − xc)(y − yc) dA (about the centroid).
- Principal angle θ: the axes are rotated counter-clockwise by θ; Ix' = (Ix+Iy)/2 + (Ix−Iy)/2·cos2θ − Ixy·sin2θ.
- Bending: positive Mx puts +y fibres in tension, positive My puts +x fibres in tension
  (with Ixy = 0, σ = Mx·y/Ix + My·x/Iy). The general case has Megson's form:
  σ = [(My·Ix − Mx·Ixy)·x + (Mx·Iy − My·Ixy)·y] / (Ix·Iy − Ixy²).
- Polygon vertices may be given counter-clockwise or clockwise; the orientation is corrected automatically.

SI units: lengths [m], areas [m²], second moments [m⁴], warping constant [m⁶], moments [N·m].
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.references import cite

Point = tuple[float, float]


# ---------------------------------------------------------------------------
# Polygon helpers
# ---------------------------------------------------------------------------
def _ring_integrals(points: ArrayLike) -> NDArray[np.float64]:
    """Signed ring integrals A, ∫x, ∫y, ∫x², ∫y², ∫xy about the origin (Green's theorem)."""
    p = np.asarray(points, dtype=float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 3:
        raise ValueError("a polygon must be an (N×2) array with at least 3 vertices")
    x0, y0 = p[:, 0], p[:, 1]
    x1, y1 = np.roll(x0, -1), np.roll(y0, -1)
    c = x0 * y1 - x1 * y0
    A = c.sum() / 2
    Sx = ((x0 + x1) * c).sum() / 6
    Sy = ((y0 + y1) * c).sum() / 6
    Ixx_o = ((x0 ** 2 + x0 * x1 + x1 ** 2) * c).sum() / 12          # ∫x² dA
    Iyy_o = ((y0 ** 2 + y0 * y1 + y1 ** 2) * c).sum() / 12          # ∫y² dA
    Ixy_o = ((x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0) * c).sum() / 24
    return np.array([A, Sx, Sy, Ixx_o, Iyy_o, Ixy_o])


def _oriented(points: ArrayLike, sign: float) -> NDArray[np.float64]:
    """Ring integrals with a fixed orientation (outer boundary +, hole −)."""
    v = _ring_integrals(points)
    return v * (sign * np.sign(v[0]) if v[0] != 0 else 0.0)


def principal(Ix: float, Iy: float, Ixy: float) -> tuple[float, float, float]:
    """Principal second moments of area and angle.

    Parameters
    ----------
    Ix, Iy, Ixy : float
        Centroidal second moments and product of area [m⁴].

    Returns
    -------
    tuple of float
        ``(I1, I2, theta)`` with ``I1 ≥ I2`` [m⁴] and θ [rad], measured counter-clockwise from x to the
        I1 axis.
    """
    avg, half_diff = (Ix + Iy) / 2, math.hypot((Ix - Iy) / 2, Ixy)
    theta = 0.5 * math.atan2(-2 * Ixy, Ix - Iy)
    return avg + half_diff, avg - half_diff, theta


def rotate_axis(Ix: float, Iy: float, Ixy: float, theta: float) -> tuple[float, float, float]:
    """Second moments about axes rotated counter-clockwise by θ.

    Parameters
    ----------
    Ix, Iy, Ixy : float
        Second moments and product of area [m⁴].
    theta : float
        Rotation angle [rad].

    Returns
    -------
    tuple of float
        ``(Ix', Iy', Ixy')`` [m⁴].
    """
    c2, s2 = math.cos(2 * theta), math.sin(2 * theta)
    avg, difference = (Ix + Iy) / 2, (Ix - Iy) / 2
    return avg + difference * c2 - Ixy * s2, avg - difference * c2 + Ixy * s2, difference * s2 + Ixy * c2


def _property_dict(v: NDArray[np.float64], xs: ArrayLike, ys: ArrayLike) -> dict[str, float]:
    """Centroidal properties from origin integrals ``v``; xs, ys are vertex coordinates (for fibre distances)."""
    A, Sx, Sy, Ixx_o, Iyy_o, Ixy_o = v
    if A <= 0:
        raise ValueError("the net area must be positive")
    xc, yc = Sx / A, Sy / A
    Iy = Ixx_o - A * xc ** 2           # ∫(x−xc)²
    Ix = Iyy_o - A * yc ** 2           # ∫(y−yc)²
    Ixy = Ixy_o - A * xc * yc
    I1, I2, th = principal(Ix, Iy, Ixy)
    cy_upper, cy_lower = np.max(ys) - yc, yc - np.min(ys)
    cx_right, cx_left = np.max(xs) - xc, xc - np.min(xs)
    return {"A": A, "xc": xc, "yc": yc, "Ix": Ix, "Iy": Iy, "Ixy": Ixy,
            "I1": I1, "I2": I2, "theta_p": th, "J_polar": Ix + Iy,
            "rx": math.sqrt(Ix / A), "ry": math.sqrt(Iy / A),
            "Sx_upper": Ix / cy_upper, "Sx_lower": Ix / cy_lower,
            "Sy_right": Iy / cx_right, "Sy_left": Iy / cx_left}


def polygon_properties(outer: ArrayLike, holes: Iterable[ArrayLike] = ()) -> dict[str, float]:
    """Properties of an arbitrary simple polygon (optionally with holes), in closed form via Green's theorem.

    Parameters
    ----------
    outer : array_like, shape (N, 2)
        Outer boundary vertices (x, y) [m].
    holes : iterable of array_like
        Inner boundaries in the same format.

    Returns
    -------
    dict
        ``A`` [m²]; ``xc``, ``yc`` [m]; centroidal ``Ix``, ``Iy``, ``Ixy`` [m⁴]; ``I1``, ``I2`` [m⁴];
        ``theta_p`` [rad]; ``rx``, ``ry`` [m]; section moduli ``Sx_upper``/``Sx_lower`` (Ix/c) and
        ``Sy_right``/``Sy_left`` [m³]; ``J_polar = Ix + Iy`` [m⁴] (polar moment, NOT the torsion constant).

    Raises
    ------
    ValueError
        If a ring has fewer than 3 vertices or the net area is not positive.

    Examples
    --------
    >>> s = polygon_properties(rectangle_polygon(0.02, 0.04))
    >>> round(s["Ix"] / (0.02 * 0.04 ** 3 / 12), 12)
    1.0
    """
    total = _oriented(outer, +1)
    all_items = [np.asarray(outer, float)]
    for d in holes:
        total = total + _oriented(d, -1)
        all_items.append(np.asarray(d, float))
    xs = np.concatenate([p[:, 0] for p in all_items])
    ys = np.concatenate([p[:, 1] for p in all_items])
    return _property_dict(total, xs, ys)


def rectangle_polygon(b: float, h: float, x0: float = 0.0, y0: float = 0.0) -> list[Point]:
    """Counter-clockwise b × h rectangle with its lower-left corner at (x0, y0).

    Parameters
    ----------
    b, h : float
        Width and height [m].
    x0, y0 : float
        Lower-left corner [m].

    Returns
    -------
    list of (float, float)
        Four vertices.
    """
    return [(x0, y0), (x0 + b, y0), (x0 + b, y0 + h), (x0, y0 + h)]


def circle_polygon(r: float, n: int = 360, xc: float = 0.0, yc: float = 0.0) -> list[Point]:
    """Regular n-gon inscribed in a circle.

    Parameters
    ----------
    r : float
        Circle radius [m].
    n : int
        Number of vertices.
    xc, yc : float
        Centre [m].

    Returns
    -------
    list of (float, float)
        Counter-clockwise vertices.
    """
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return list(zip(xc + r * np.cos(t), yc + r * np.sin(t), strict=True))


def i_section_polygon(b_flange: float, t_flange: float, h: float, t_web: float) -> list[Point]:
    """Polygon of a doubly symmetric I-section (same dimensions as :func:`aerokit.structures.beam.i_section`).

    Parameters
    ----------
    b_flange, t_flange : float
        Flange width and thickness [m].
    h : float
        Overall height [m].
    t_web : float
        Web thickness [m].

    Returns
    -------
    list of (float, float)
        Twelve vertices, bottom mid-point at the origin.
    """
    bf, tf, tw = b_flange, t_flange, t_web
    return [(-bf / 2, 0), (bf / 2, 0), (bf / 2, tf), (tw / 2, tf), (tw / 2, h - tf), (bf / 2, h - tf),
            (bf / 2, h), (-bf / 2, h), (-bf / 2, h - tf), (-tw / 2, h - tf), (-tw / 2, tf), (-bf / 2, tf)]


# ---------------------------------------------------------------------------
# Plastic section modulus
# ---------------------------------------------------------------------------
@cite("sutherland_hodgman_1974")
def _clip_half_plane(points: ArrayLike, cut_y: float, upper: bool = True) -> list[Point]:
    """Sutherland-Hodgman: clip the polygon to the half plane y ≥ cut_y (upper) or y ≤ cut_y."""
    p = [tuple(q) for q in np.asarray(points, float)]
    inside: Callable[[Sequence[float]], bool] = ((lambda q: q[1] >= cut_y) if upper
                                                 else (lambda q: q[1] <= cut_y))
    output: list[Point] = []
    for i in range(len(p)):
        a, b = p[i], p[(i + 1) % len(p)]
        if inside(b):
            if not inside(a):
                output.append(_intersection(a, b, cut_y))
            output.append((b[0], b[1]))
        elif inside(a):
            output.append(_intersection(a, b, cut_y))
    return output


def _intersection(a: Sequence[float], b: Sequence[float], y: float) -> Point:
    """Intersection of segment a-b with the horizontal line at ``y``."""
    t = (y - a[1]) / (b[1] - a[1])
    return (a[0] + t * (b[0] - a[0]), y)


def _part_A_Sy(rings: list[tuple[NDArray[np.float64], int]], cut_y: float, upper: bool) -> tuple[float, float]:
    """Area and first moment ∫y dA of the part of the section above (or below) ``cut_y``."""
    A = Sy = 0.0
    for points, sign in rings:
        k = _clip_half_plane(points, cut_y, upper)
        if len(k) >= 3:
            v = _ring_integrals(k)
            direction = sign * (np.sign(_ring_integrals(points)[0]))
            A += direction * v[0]
            Sy += direction * v[2]
    return A, Sy


def plastic_modulus(outer: ArrayLike, holes: Iterable[ArrayLike] = (), axis: str = "x") -> tuple[float, float]:
    """Plastic section modulus ``Z = ∫|y − y_p| dA`` about the equal-area axis y_p.

    Parameters
    ----------
    outer : array_like, shape (N, 2)
        Outer boundary [m].
    holes : iterable of array_like
        Hole boundaries [m].
    axis : {"x", "y"}
        ``"x"``: bending about a horizontal axis; ``"y"``: coordinates are swapped first.

    Returns
    -------
    tuple of float
        ``(Z, y_p)`` -- plastic modulus [m³] and equal-area axis position [m].

    Examples
    --------
    >>> Z, _ = plastic_modulus(rectangle_polygon(0.02, 0.04))
    >>> round(float(Z) / (0.02 * 0.04 ** 2 / 4), 9)
    1.0
    """
    def convert(p: ArrayLike) -> NDArray[np.float64]:
        p = np.asarray(p, float)
        return p if axis == "x" else p[:, ::-1]
    rings = [(convert(outer), +1)] + [(convert(d), -1) for d in holes]
    ymin = min(h[0][:, 1].min() for h in rings)
    ymax = max(h[0][:, 1].max() for h in rings)
    A_top = _part_A_Sy(rings, ymin - 1, True)[0]
    lo, hi = ymin, ymax
    for _ in range(200):                     # bisection: upper area = A/2
        middle = 0.5 * (lo + hi)
        if _part_A_Sy(rings, middle, True)[0] > A_top / 2:
            lo = middle
        else:
            hi = middle
    yp = 0.5 * (lo + hi)
    Au, Su = _part_A_Sy(rings, yp, True)
    Al, Sl = _part_A_Sy(rings, yp, False)
    return (Su - yp * Au) + (yp * Al - Sl), yp


# ---------------------------------------------------------------------------
# Multi-material (modulus-weighted) section
# ---------------------------------------------------------------------------
def compound_section(parts: Sequence[dict[str, Any]], E_ref: float | None = None) -> dict[str, float]:
    """Multi-material section (transformed-section method).

    Parameters
    ----------
    parts : sequence of dict
        ``[{"outer": [...], "E": E, "holes": [...]}, ...]``; ``"holes"`` is optional (the legacy key
        ``"delikler"`` is still accepted). Parts must not overlap.
    E_ref : float, optional
        Reference modulus [Pa] (default: E of the first part).

    Returns
    -------
    dict
        All keys of :func:`polygon_properties`, as transformed quantities (divided by E_ref), plus
        ``E_ref`` [Pa], ``EA`` [N], ``EIx``, ``EIy``, ``EIxy`` [N·m²].

    Raises
    ------
    ValueError
        If ``parts`` is empty or a modulus is not positive.

    Notes
    -----
    ``EA = Σ E·A``; the centroid is E·A weighted; the EI values are about the common modulus-weighted centroid.
    """
    if not parts:
        raise ValueError("at least one part is required")
    E_ref = parts[0]["E"] if E_ref is None else E_ref
    total = np.zeros(6)
    xs: list[float] = []
    ys: list[float] = []
    for p in parts:
        if p["E"] <= 0:
            raise ValueError("E must be positive")
        holes = p.get("holes", p.get("delikler", ()))
        v = _oriented(p["outer"], +1) + sum((_oriented(d, -1) for d in holes), np.zeros(6))
        total += p["E"] / E_ref * v
        q = np.asarray(p["outer"], float)
        xs.extend(q[:, 0])
        ys.extend(q[:, 1])
    s = _property_dict(total, xs, ys)
    s.update({"E_ref": E_ref, "EA": E_ref * s["A"], "EIx": E_ref * s["Ix"], "EIy": E_ref * s["Iy"],
              "EIxy": E_ref * s["Ixy"]})
    return s


# ---------------------------------------------------------------------------
# Unsymmetric bending
# ---------------------------------------------------------------------------
@cite("megson_2017", note="unsymmetrical bending, direct stress distribution")
def bending_stress(Mx: float, My: float, Ix: float, Iy: float, Ixy: float, x: Any, y: Any) -> Any:
    """Direct stress σ(x, y) under unsymmetric bending (x, y about the centroid).

    Parameters
    ----------
    Mx, My : float
        Bending moments [N·m]; Mx > 0 puts +y in tension, My > 0 puts +x in tension.
    Ix, Iy, Ixy : float
        Centroidal second moments and product of area [m⁴].
    x, y : float or ndarray
        Fibre coordinates relative to the centroid [m].

    Returns
    -------
    float or ndarray
        Stress [Pa].

    Raises
    ------
    ValueError
        If ``Ix·Iy − Ixy² ≤ 0``.

    Notes
    -----
    ``σ = [(My Ix − Mx Ixy) x + (Mx Iy − My Ixy) y] / (Ix Iy − Ixy²)``.
    """
    D = Ix * Iy - Ixy ** 2
    if D <= 0:
        raise ValueError("Ix·Iy − Ixy² must be positive")
    return ((My * Ix - Mx * Ixy) * x + (Mx * Iy - My * Ixy) * y) / D


@cite("megson_2017", note="position of the neutral axis")
def neutral_axis_angle(Mx: float, My: float, Ix: float, Iy: float, Ixy: float) -> float:
    """Angle α of the neutral axis with the x axis.

    Parameters
    ----------
    Mx, My : float
        Bending moments [N·m].
    Ix, Iy, Ixy : float
        Centroidal second moments and product of area [m⁴].

    Returns
    -------
    float
        α [rad], counter-clockwise, in (−π/2, π/2].

    Raises
    ------
    ValueError
        If both moment terms vanish (neutral axis undefined).
    """
    a = My * Ix - Mx * Ixy
    b = Mx * Iy - My * Ixy
    if a == 0 and b == 0:
        raise ValueError("zero moment: the neutral axis is undefined")
    alpha = math.atan2(-a, b)                 # direction (b, −a) of σ = a·x + b·y = 0
    if alpha <= -math.pi / 2:
        alpha += math.pi
    elif alpha > math.pi / 2:
        alpha -= math.pi
    return alpha


# ---------------------------------------------------------------------------
# Thin-walled open section (mid-line + thickness)
# ---------------------------------------------------------------------------
@cite("vlasov_1961", note="sectorial coordinates, shear centre and warping constant")
@cite("megson_2017", note="shear flow in open sections")
class ThinOpenSection:
    """Thin-walled open section defined by nodes [(x, y)] and straight wall elements [(i, j, t)].

    The elements must form a tree (branches allowed, no closed cell). Thin-wall assumption: properties are
    integrated along the mid-line as ∫(.) t ds; with ``thickness_term=True`` each element's own t³ term is
    added to Ix, Iy, Ixy. Shear flow and sectorial quantities always use the thin-wall assumption.

    Parameters
    ----------
    nodes : array_like, shape (N, 2)
        Mid-line node coordinates [m].
    elements : iterable of (int, int, float)
        Wall elements ``(i, j, t)``: node indices and thickness [m].
    thickness_term : bool
        Include the t³/12 self-terms of the walls in the second moments.

    Attributes
    ----------
    A : float
        Wall area [m²].
    xc, yc : float
        Centroid [m].
    Ix, Iy, Ixy : float
        Centroidal second moments and product of area [m⁴].
    J : float
        St Venant torsion constant ``Σ L t³/3`` [m⁴].

    Raises
    ------
    ValueError
        For invalid or zero-length elements, or elements that do not form a connected tree
        (use :func:`multi_cell_torsion` for closed cells).
    """

    def __init__(self, nodes: ArrayLike, elements: Iterable[tuple[int, int, float]],
                 thickness_term: bool = False) -> None:
        self.P = np.asarray(nodes, dtype=float)
        self.E = [(int(i), int(j), float(t)) for i, j, t in elements]
        n = len(self.P)
        if not self.E:
            raise ValueError("at least one element is required")
        for i, j, t in self.E:
            if t <= 0 or i == j or not (0 <= i < n and 0 <= j < n):
                raise ValueError(f"invalid element ({i}, {j}, {t})")
            if np.allclose(self.P[i], self.P[j]):
                raise ValueError("zero-length element")
        if len(self.E) != n - 1 or not self._connected():
            raise ValueError("open-section elements must form a connected tree (use multi_cell_torsion for "
                             "closed cells)")
        self.thickness_term = thickness_term
        self._compute_properties()

    def _connected(self) -> bool:
        """Build the adjacency list ``self.neighbor`` and check that every node is reachable from node 0."""
        adjacency: dict[int, list[tuple[int, int]]] = {k: [] for k in range(len(self.P))}
        for e, (i, j, _) in enumerate(self.E):
            adjacency[i].append((j, e))
            adjacency[j].append((i, e))
        self.neighbor = adjacency
        seen, stack = {0}, [0]
        while stack:
            u = stack.pop()
            for v, _ in adjacency[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == len(self.P)

    @staticmethod
    def _lin(fa: float, fb: float, ga: float, gb: float) -> float:
        """∫₀¹ f g dξ for linear f and g."""
        return fa * ga / 3 + (fa * gb + fb * ga) / 6 + fb * gb / 3

    def _compute_properties(self) -> None:
        """Compute A, centroid, Ix, Iy, Ixy and J."""
        A = Sx = Sy = 0.0
        for i, j, t in self.E:
            (xa, ya), (xb, yb) = self.P[i], self.P[j]
            L = math.hypot(xb - xa, yb - ya)
            A += t * L
            Sx += t * L * (xa + xb) / 2
            Sy += t * L * (ya + yb) / 2
        self.A, self.xc, self.yc = A, Sx / A, Sy / A
        self.Pc = self.P - [self.xc, self.yc]          # centroidal coordinates
        Ix = Iy = Ixy = J = 0.0
        for i, j, t in self.E:
            (xa, ya), (xb, yb) = self.Pc[i], self.Pc[j]
            L = math.hypot(xb - xa, yb - ya)
            Ix += t * L * self._lin(ya, yb, ya, yb)
            Iy += t * L * self._lin(xa, xb, xa, xb)
            Ixy += t * L * self._lin(xa, xb, ya, yb)
            J += L * t ** 3 / 3
            if self.thickness_term:
                c, s = (xb - xa) / L, (yb - ya) / L
                Ix += L * t ** 3 / 12 * c ** 2
                Iy += L * t ** 3 / 12 * s ** 2
                Ixy -= L * t ** 3 / 12 * s * c
        self.Ix, self.Iy, self.Ixy, self.J = Ix, Iy, Ixy, J

    def properties(self) -> dict[str, float]:
        """Section properties.

        Returns
        -------
        dict
            ``A`` [m²], ``xc``, ``yc`` [m], ``Ix``, ``Iy``, ``Ixy``, ``I1``, ``I2`` [m⁴], ``theta_p`` [rad],
            ``J`` [m⁴].
        """
        I1, I2, th = principal(self.Ix, self.Iy, self.Ixy)
        return {"A": self.A, "xc": self.xc, "yc": self.yc, "Ix": self.Ix, "Iy": self.Iy, "Ixy": self.Ixy,
                "I1": I1, "I2": I2, "theta_p": th, "J": self.J}

    # --- tree traversal ---
    def _order(self, root: int = 0) -> list[tuple[int, int, int]]:
        """(parent, child, element) triples ordered from the root to the leaves."""
        order: list[tuple[int, int, int]] = []
        seen, stack = {root}, [root]
        while stack:
            u = stack.pop()
            for v, e in self.neighbor[u]:
                if v not in seen:
                    seen.add(v)
                    order.append((u, v, e))
                    stack.append(v)
        return order

    # --- shear flow ---
    def shear_flow(self, Sx: float, Sy: float) -> dict[str, Any]:
        """Open-section shear flow for shear forces (Sx, Sy) acting through the shear centre (no twist).

        Parameters
        ----------
        Sx, Sy : float
            Shear forces [N].

        Returns
        -------
        dict
            ``elements``: one dict per element (direction i→j) with ``i``, ``j``, ``q_i``, ``q_mid``,
            ``q_j``, ``q_max`` [N/m] and ``F = ∫q ds`` [N]; resultants ``Fx``, ``Fy`` [N]; moment about the
            centroid ``M_center`` [N·m]; ``balance_residual`` (flow left at the root) [N/m].

        Notes
        -----
        ``q_s = −(Sx Ixx − Sy Ixy)/Δ ∫t x ds − (Sy Iyy − Sx Ixy)/Δ ∫t y ds`` (Megson form; here
        Ixx = ∫y², Iyy = ∫x², Δ = Ixx Iyy − Ixy²). q = 0 at free ends.
        """
        Ixx, Iyy, Ixy = self.Ix, self.Iy, self.Ixy
        D = Ixx * Iyy - Ixy ** 2
        kx = (Sx * Ixx - Sy * Ixy) / D
        ky = (Sy * Iyy - Sx * Ixy) / D
        order = self._order()
        q_end: dict[int, tuple[int, int, float, float, float, float]] = {}   # element → child→parent data
        incoming = {k: 0.0 for k in range(len(self.P))}
        for u, v, e in reversed(order):           # leaf to root: v child, u parent
            (xa, ya), (xb, yb) = self.Pc[v], self.Pc[u]
            t = self.E[e][2]
            L = math.hypot(xb - xa, yb - ya)
            qa = incoming[v]
            a1 = -t * (kx * xa + ky * ya)                     # dq/ds (s=0)
            a2 = -t * (kx * (xb - xa) + ky * (yb - ya)) / (2 * L)   # coefficient of s²
            qb = qa + a1 * L + a2 * L ** 2
            q_end[e] = (v, u, qa, a1, a2, L)
            incoming[u] += qb
        result, Fx, Fy, M = [], 0.0, 0.0, 0.0
        for e, (i, j, _t) in enumerate(self.E):
            v, u, qa, a1, a2, L = q_end[e]
            s = np.linspace(0, L, 41)
            q = qa + a1 * s + a2 * s ** 2
            F = qa * L + a1 * L ** 2 / 2 + a2 * L ** 3 / 3
            (xa, ya), (xb, yb) = self.Pc[v], self.Pc[u]
            Fx += F * (xb - xa) / L
            Fy += F * (yb - ya) / L
            M += F * (xa * (yb - ya) - ya * (xb - xa)) / L
            if (v, u) != (i, j):                       # flip to the i→j direction
                q, F = -q[::-1], -F
            result.append({"i": i, "j": j, "q_i": q[0], "q_mid": q[len(q) // 2], "q_j": q[-1],
                           "q_max": float(q[np.argmax(np.abs(q))]), "F": F})
        return {"elements": result, "Fx": Fx, "Fy": Fy, "M_center": M,
                "balance_residual": abs(incoming[0])}

    def shear_center_flow(self) -> tuple[float, float]:
        """Shear centre (x, y) [m, global] from the shear-flow moment: Sy = 1 gives x_s, Sx = 1 gives y_s."""
        m_y = self.shear_flow(0.0, 1.0)["M_center"]
        m_x = self.shear_flow(1.0, 0.0)["M_center"]
        return self.xc + m_y, self.yc - m_x

    # --- sectorial properties ---
    def _sectorial(self, xP: float, yP: float) -> NDArray[np.float64]:
        """Nodal sectorial coordinates ω for the pole (xP, yP) in centroidal coordinates (root = 0)."""
        w = np.zeros(len(self.P))
        for u, v, _e in self._order():
            (xa, ya), (xb, yb) = self.Pc[u], self.Pc[v]
            w[v] = w[u] + (xa - xP) * (yb - ya) - (ya - yP) * (xb - xa)
        return w

    def _sectorial_integrals(self, w: NDArray[np.float64]) -> tuple[float, float, float, float]:
        """∫ω dA, ∫ωx dA, ∫ωy dA, ∫ω² dA for nodal sectorial coordinates ``w``."""
        Iw = Iwx = Iwy = Iww = 0.0
        for i, j, t in self.E:
            (xa, ya), (xb, yb) = self.Pc[i], self.Pc[j]
            L = math.hypot(xb - xa, yb - ya)
            Iw += t * L * (w[i] + w[j]) / 2
            Iwx += t * L * self._lin(w[i], w[j], xa, xb)
            Iwy += t * L * self._lin(w[i], w[j], ya, yb)
            Iww += t * L * self._lin(w[i], w[j], w[i], w[j])
        return Iw, Iwx, Iwy, Iww

    def shear_center(self) -> tuple[float, float]:
        """Shear centre (x, y) [m, global]: the pole for which ∫ω x dA = ∫ω y dA = 0 (Vlasov)."""
        w = self._sectorial(0.0, 0.0)
        _, Iwx, Iwy, _ = self._sectorial_integrals(w)
        # ω_S = ω_P − Δx·y + Δy·x + const; orthogonality: Iwx − Δx·Ixy + Δy·Iyy = 0, Iwy − Δx·Ixx + Δy·Ixy = 0
        M = np.array([[-self.Ixy, self.Iy], [-self.Ix, self.Ixy]])
        dx, dy = np.linalg.solve(M, [-Iwx, -Iwy])
        return self.xc + dx, self.yc + dy

    def sectorial(self) -> dict[str, Any]:
        """Normalised sectorial coordinate about the shear centre and the warping constant.

        Returns
        -------
        dict
            ``omega`` (nodal ω_n) [m²], ``Cw = ∫ω_n² dA`` [m⁶], shear centre ``x_s``, ``y_s`` [m].
        """
        xs, ys = self.shear_center()
        w = self._sectorial(xs - self.xc, ys - self.yc)
        Iw = self._sectorial_integrals(w)[0]
        w = w - Iw / self.A
        Cw = self._sectorial_integrals(w)[3]
        return {"omega": w, "Cw": Cw, "x_s": xs, "y_s": ys}


def i_section_thin(b: float, h: float, t_f: float, t_w: float) -> ThinOpenSection:
    """Thin-walled I-section (mid-line model).

    Parameters
    ----------
    b : float
        Flange width [m].
    h : float
        Distance between the flange mid-lines [m].
    t_f, t_w : float
        Flange and web thickness [m].

    Returns
    -------
    ThinOpenSection
    """
    d = [(-b / 2, h / 2), (0, h / 2), (b / 2, h / 2), (-b / 2, -h / 2), (0, -h / 2), (b / 2, -h / 2)]
    e = [(0, 1, t_f), (1, 2, t_f), (3, 4, t_f), (4, 5, t_f), (1, 4, t_w)]
    return ThinOpenSection(d, e)


def u_section_thin(b: float, h: float, t_f: float, t_w: float) -> ThinOpenSection:
    """Thin-walled channel: web on x = 0 (height h), flanges of length b towards +x.

    Parameters
    ----------
    b : float
        Flange length [m].
    h : float
        Web height (between flange mid-lines) [m].
    t_f, t_w : float
        Flange and web thickness [m].

    Returns
    -------
    ThinOpenSection
    """
    d = [(b, h / 2), (0, h / 2), (0, -h / 2), (b, -h / 2)]
    e = [(0, 1, t_f), (1, 2, t_w), (2, 3, t_f)]
    return ThinOpenSection(d, e)


def z_section_thin(b: float, h: float, t: float) -> ThinOpenSection:
    """Thin-walled Z-section: web on x = 0, upper flange towards +x and lower flange towards −x.

    Parameters
    ----------
    b : float
        Flange length [m].
    h : float
        Web height [m].
    t : float
        Wall thickness [m].

    Returns
    -------
    ThinOpenSection
    """
    d = [(b, h / 2), (0, h / 2), (0, -h / 2), (-b, -h / 2)]
    e = [(0, 1, t), (1, 2, t), (2, 3, t)]
    return ThinOpenSection(d, e)


# ---------------------------------------------------------------------------
# Multi-cell closed-section torsion (generalised Bredt-Batho)
# ---------------------------------------------------------------------------
@cite("bredt_1896")
@cite("megson_2017", note="torsion of multicell sections")
def multi_cell_torsion(A: ArrayLike, delta: ArrayLike, T: float = 1.0, G: float = 1.0) -> dict[str, Any]:
    """Pure torsion of an n-cell thin-walled closed section.

    Parameters
    ----------
    A : array_like, shape (n,)
        Cell areas [m²].
    delta : array_like, shape (n, n)
        Symmetric matrix: ``delta[i][i] = ∮(cell i) ds/t``, ``delta[i][j] = ∫ds/t`` of the wall shared by
        cells i and j (0 if none) [-].
    T : float
        Torque [N·m].
    G : float
        Shear modulus [Pa].

    Returns
    -------
    dict
        ``q`` cell shear flows (counter-clockwise positive) [N/m], ``twist_rate`` dθ/dz [rad/m] and
        torsion constant ``J = T/(G θ')`` [m⁴].

    Raises
    ------
    ValueError
        For non-positive areas, a wrongly sized or non-symmetric ``delta``, or a non-positive diagonal.

    Notes
    -----
    For each cell ``θ' = (q_i δ_ii − Σ_j q_j δ_ij)/(2 A_i G)``, and ``T = Σ 2 A_i q_i``.
    """
    A = np.asarray(A, float)
    d = np.asarray(delta, float)
    n = len(A)
    if d.shape != (n, n) or np.any(A <= 0) or np.any(np.diag(d) <= 0):
        raise ValueError("A must be positive and delta n×n with a positive diagonal")
    if not np.allclose(d, d.T):
        raise ValueError("delta must be symmetric")
    M = np.zeros((n + 1, n + 1))
    rhs = np.zeros(n + 1)
    for i in range(n):
        M[i, :n] = -d[i] / (2 * A[i] * G)
        M[i, i] = d[i, i] / (2 * A[i] * G)
        M[i, n] = -1.0
    M[n, :n] = 2 * A
    rhs[n] = T
    x = np.linalg.solve(M, rhs)
    q, th = x[:n], x[n]
    return {"q": q, "twist_rate": th, "J": T / (G * th)}
