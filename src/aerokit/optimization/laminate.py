"""Laminate stacking-sequence optimization and lamination parameters.

Contents:

* Tsai-Pagano material invariants U1..U5, lamination parameters V1..V4 (in-plane) and W1..W4
  (bending), A and D from the parameters, feasibility bounds (Miki diagram, four-parameter region,
  one-parameter V-W bound).
* Discrete stacking: two-ply stacks {0₂, ±45, 90₂}; the half laminate is encoded (symmetry and
  balance are guaranteed by the data structure); contiguity constraint (at most 4 consecutive plies
  of the same angle). Objectives: stiffness (effective modulus in the load direction), first-ply
  failure (FPF) load factor, simply supported plate buckling load factor
  (:func:`aerokit.composites.laminate.plate_buckling`), strain load factor, buckling + strain.
* Search: exhaustive (small numbers of stacks; vectorized), genetic algorithm (with a stack-swap
  operator), permutation search (fixed ply counts, order varies), continuous angle optimization
  (SciPy).

Naming (in this module): V1 = ∫cos2θ, V2 = ∫cos4θ, V3 = ∫sin2θ, V4 = ∫sin4θ (averages over z/h);
W_i are the same functions averaged with the weight 12z²/h³. The ordering varies between authors
in the literature (in Miki 1982 the cos4θ term is called V3); the primary sources were NOT read in
this repository. The invariants and the relations A = h[U1 + U2V1 + U3V2, ...] are checked
numerically against :func:`aerokit.composites.laminate.abd_matrix` (derivation: trigonometric
expansion of Q̄).

Sources:

[LR94]
    R. Le Riche, "Optimization of Composite Laminated Structures by Genetic Algorithms", PhD thesis,
    Virginia Tech 1994 (advisor R. T. Haftka) — Chapter 3 READ (vtechworks PDF): problem statement
    Eqs. (3.1)-(3.5), material (E1 = 18.5 Msi, E2 = 1.89 Msi, G12 = 0.93 Msi, ν12 = 0.3,
    t = 0.005 in), strain allowables (ε1 = 0.008, ε2 = 0.029, γ12 = 0.015, FS = 1.5), Tables 3.1-3.3.
    The same problem is used in Le Riche & Haftka, AIAA J. 31(5) 951-956 (1993) and in the book of
    Gürdal, Haftka & Hajela (1999) — those two were NOT read.

The contiguity rule and the two-ply stack encoding are from [LR94] §3.1.2.
"""
from __future__ import annotations

import math
import warnings
from collections.abc import Iterator, Sequence
from typing import Any

import numpy as np
from scipy import optimize

from aerokit.composites import laminate
from aerokit.composites.lamina import Qbar, T_strain
from aerokit.references import cite

STACK = {0: (0.0, 0.0), 1: (45.0, -45.0), 2: (90.0, 90.0)}       # code → (outer ply, inner ply)
STACK_NAME = {0: "0₂", 1: "±45", 2: "90₂"}

# [LR94] §3.1: graphite/epoxy, US customary units → SI
PSI = 6894.757293168
INCH = 0.0254
LBF_PER_INCH = 4.4482216152605 / 0.0254           # 1 lbf/in → N/m
LR94_MATERIAL = {"name": "[LR94] graphite/epoxy", "E1": 18.5e6 * PSI, "E2": 1.89e6 * PSI, "G12": 0.93e6 * PSI,
                 "nu12": 0.3, "source": "Le Riche 1994 thesis §3.1 (127.59/13.03/6.41 GPa)"}
LR94_T = 0.005 * INCH
LR94_STRAIN = (0.008, 0.029, 0.015)


# ---------------------------------------------------------------------------
# Lamination parameters
# ---------------------------------------------------------------------------
@cite("tsai_pagano_1968")
def U_invariants(m: dict[str, Any]) -> np.ndarray:
    """Tsai-Pagano material invariants of a ply.

    Parameters
    ----------
    m : dict
        Ply material (keys E1, E2, nu12, G12 [Pa]).

    Returns
    -------
    numpy.ndarray
        [U1, U2, U3, U4, U5] [Pa].

    Notes
    -----
    From the reduced stiffness Q::

        U1 = (3Q11 + 3Q22 + 2Q12 + 4Q66)/8,   U2 = (Q11 − Q22)/2,
        U3 = (Q11 + Q22 − 2Q12 − 4Q66)/8,     U4 = (Q11 + Q22 + 6Q12 − 4Q66)/8,
        U5 = (Q11 + Q22 − 2Q12 + 4Q66)/8.
    """
    Q = laminate.Q_material(m)
    Q11, Q22, Q12, Q66 = Q[0, 0], Q[1, 1], Q[0, 1], Q[2, 2]
    return np.array([(3 * Q11 + 3 * Q22 + 2 * Q12 + 4 * Q66) / 8, (Q11 - Q22) / 2,
                     (Q11 + Q22 - 2 * Q12 - 4 * Q66) / 8, (Q11 + Q22 + 6 * Q12 - 4 * Q66) / 8,
                     (Q11 + Q22 - 2 * Q12 + 4 * Q66) / 8])


def _trig(angle: Any) -> np.ndarray:
    """Stack [cos2θ, cos4θ, sin2θ, sin4θ] along the last axis (θ in degrees)."""
    r = np.radians(np.asarray(angle, float))
    return np.stack([np.cos(2 * r), np.cos(4 * r), np.sin(2 * r), np.sin(4 * r)], axis=-1)


@cite("tsai_pagano_1968", "gurdal_haftka_1999", note="definitions; ordering V1..V4 as stated in the module notes")
def lamination_parameters(angles: Sequence[float], thicknesses: Sequence[float] | None = None) -> dict[str, Any]:
    """In-plane, coupling and bending lamination parameters of a stacking sequence.

    Parameters
    ----------
    angles : sequence of float
        Ply angles from bottom to top [deg].
    thicknesses : sequence of float, optional
        Ply thicknesses [m] (equal thicknesses if omitted).

    Returns
    -------
    dict
        ``V`` (4,) in-plane parameters, ``W`` (4,) bending parameters, ``B`` (4,) coupling
        parameters (4/h² ∫ z f dz), ``h`` total thickness (number of plies if thicknesses are not
        given).

    Notes
    -----
    With f = [cos2θ, cos4θ, sin2θ, sin4θ]: V = (1/h)∫f dz, B = (4/h²)∫z f dz, W = (12/h³)∫z² f dz.

    Examples
    --------
    >>> lamination_parameters([0.0])["V"][:2]
    array([1., 1.])
    """
    ang = np.asarray(angles, float)
    t = np.ones(len(ang)) if thicknesses is None else np.asarray(thicknesses, float)
    h = t.sum()
    z = np.concatenate([[-h / 2], -h / 2 + np.cumsum(t)])
    f = _trig(ang)
    V = (f * (z[1:] - z[:-1])[:, None]).sum(0) / h
    Bp = (f * ((z[1:] ** 2 - z[:-1] ** 2) / 2)[:, None]).sum(0) * 4 / h ** 2
    Wp = (f * ((z[1:] ** 3 - z[:-1] ** 3) / 3)[:, None]).sum(0) * 12 / h ** 3
    return {"V": V, "W": Wp, "B": Bp, "h": h}


def _lp_matrix(U: np.ndarray, L: np.ndarray) -> np.ndarray:
    """Averaged Q̄ from invariants and lamination parameters (11, 22, 12, 66, 16, 26 entries)."""
    U1, U2, U3, U4, U5 = U
    L1, L2, L3, L4 = L
    M = np.empty((3, 3))
    M[0, 0] = U1 + U2 * L1 + U3 * L2
    M[1, 1] = U1 - U2 * L1 + U3 * L2
    M[0, 1] = M[1, 0] = U4 - U3 * L2
    M[2, 2] = U5 - U3 * L2
    M[0, 2] = M[2, 0] = U2 * L3 / 2 + U3 * L4
    M[1, 2] = M[2, 1] = U2 * L3 / 2 - U3 * L4
    return M


@cite("tsai_pagano_1968")
def abd_lp(m: dict[str, Any], h: float, V: np.ndarray, W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Laminate A and D matrices from lamination parameters (single material).

    Parameters
    ----------
    m : dict
        Ply material.
    h : float
        Laminate thickness [m].
    V, W : array_like
        In-plane and bending lamination parameters (4,).

    Returns
    -------
    A : numpy.ndarray
        (3, 3) in-plane stiffness h·Q̄(V) [N/m].
    D : numpy.ndarray
        (3, 3) bending stiffness h³/12·Q̄(W) [N·m].

    Notes
    -----
    Q̄(L) = [U1 + U2L1 + U3L2, U4 − U3L2, U1 − U2L1 + U3L2, U5 − U3L2, U2L3/2 + U3L4,
    U2L3/2 − U3L4] for the 11, 12, 22, 66, 16, 26 entries.
    """
    U = U_invariants(m)
    return h * _lp_matrix(U, V), h ** 3 / 12 * _lp_matrix(U, W)


@cite("hammer_1997", "miki_1982", note="four-parameter region as attributed to Hammer et al. 1997; not read")
def lp_feasible(V1: float, V2: float, V3: float = 0.0, V4: float = 0.0, tol: float = 1e-12) -> tuple[bool, float]:
    """Feasibility of in-plane (or bending) lamination parameters.

    Parameters
    ----------
    V1, V2, V3, V4 : float
        Lamination parameters (V3 = V4 = 0 for orthotropic laminates).
    tol : float
        Tolerance on the inequalities.

    Returns
    -------
    feasible : bool
        True if all conditions hold.
    value : float
        Value of the boundary function (feasible if ≤ 1).

    Notes
    -----
    Conditions: V1² + V3² ≤ 1, −1 ≤ V2 ≤ 1 and
    ``2V1²(1 − V2) + 2V3²(1 + V2) + V2² + V4² − 4V1V3V4 ≤ 1``
    (four-parameter region; form attributed to Hammer, Bendsøe, Lipton & Pedersen 1997 — NOT read;
    tested: a single-angle ply lies exactly on the boundary, random laminates lie inside).
    For orthotropic laminates (V3 = V4 = 0) this reduces to (1 − V2)(2V1² − 1 − V2) ≤ 0, i.e. the
    Miki bound V2 ≥ 2V1² − 1 (derivation).
    """
    f = 2 * V1 ** 2 * (1 - V2) + 2 * V3 ** 2 * (1 + V2) + V2 ** 2 + V4 ** 2 - 4 * V1 * V3 * V4
    ok = (V1 ** 2 + V3 ** 2 <= 1 + tol) and (-1 - tol <= V2 <= 1 + tol) and f <= 1 + tol  # noqa: SIM300
    return bool(ok), float(f)


@cite("miki_1982", note="Miki diagram; not read")
def miki_feasible(V1: float, V2: float, tol: float = 1e-12) -> bool:
    """Miki-diagram feasibility for balanced/orthotropic laminates: |V1| ≤ 1, 2V1² − 1 ≤ V2 ≤ 1.

    Examples
    --------
    >>> miki_feasible(0.0, -1.0), miki_feasible(0.9, 0.0)
    (True, False)
    """
    return bool(abs(V1) <= 1 + tol and 2 * V1 ** 2 - 1 - tol <= V2 <= 1 + tol)


def lp_vw_bounds(V: float) -> tuple[float, float]:
    """Range of W for a given V of the same function f ∈ [−1, 1] in a symmetric laminate.

    Parameters
    ----------
    V : float
        In-plane lamination parameter, |V| ≤ 1.

    Returns
    -------
    W_min, W_max : float
        Bounds −1 + (1 + V)³/4 and 1 − (1 − V)³/4.

    Raises
    ------
    ValueError
        If |V| > 1.

    Notes
    -----
    Derivation (ζ = 2z/h ∈ [0, 1], V = ∫f dζ, W = ∫3ζ²f dζ): W is maximal for f = +1 outside and −1
    inside (bang-bang), giving W_max = 1 − (1 − V)³/4 and W_min = −1 + (1 + V)³/4. Example: [0_k/90_l]s
    attains the bound exactly.
    """
    if abs(V) > 1 + 1e-12:
        raise ValueError("|V| ≤ 1 is required")
    return -1 + (1 + V) ** 3 / 4, 1 - (1 - V) ** 3 / 4


# ---------------------------------------------------------------------------
# Stack codes ↔ angles, constraints
# ---------------------------------------------------------------------------
@cite("leriche_1994", note="§3.1.2 stack encoding")
def stack_angles(codes: Sequence[int]) -> list[float]:
    """Full symmetric ply angles from half-laminate stack codes.

    Parameters
    ----------
    codes : sequence of int
        Stack codes (0 → 0₂, 1 → ±45, 2 → 90₂) from the outer surface to the mid-plane.

    Returns
    -------
    list of float
        Ply angles from one face to the other [deg]. Because of symmetry, reading the sequence
        bottom-to-top or top-to-bottom does not change the ABD matrix.

    Examples
    --------
    >>> stack_angles([0, 1])
    [0.0, 0.0, 45.0, -45.0, -45.0, 45.0, 0.0, 0.0]
    """
    half = [a for k in codes for a in STACK[int(k)]]
    return half + half[::-1]


def stack_text(codes: Sequence[int]) -> str:
    """Text form of a stack code list, e.g. ``[0, 1, 1, 2]`` → ``'[0₂/±45/±45/90₂]s'``."""
    return "[" + "/".join(STACK_NAME[int(k)] for k in codes) + "]s"


@cite("leriche_1994", note="Fig. 3.2: +45 and −45 count as different angles")
def adjacency_max(angles: Sequence[float]) -> int:
    """Length of the longest run of consecutive plies with the same angle.

    Examples
    --------
    >>> adjacency_max(stack_angles([0, 0]))
    8
    """
    longest, count = 1, 1
    for i in range(1, len(angles)):
        count = count + 1 if abs(angles[i] - angles[i - 1]) < 1e-9 else 1
        longest = max(longest, count)
    return longest


def balance_symmetry(angles: Sequence[float]) -> tuple[bool, bool]:
    """Check mirror symmetry and balance of a stacking sequence.

    Parameters
    ----------
    angles : sequence of float
        Ply angles [deg].

    Returns
    -------
    symmetric : bool
        Mirror symmetric about the mid-plane.
    balanced : bool
        Every +θ other than 0/90 has an equal number of −θ plies.
    """
    a = [((x + 90) % 180) - 90 for x in angles]
    sym = all(abs(a[i] - a[-1 - i]) < 1e-9 for i in range(len(a) // 2))
    count: dict[float, int] = {}
    for x in a:
        if abs(x) > 1e-9 and abs(abs(x) - 90) > 1e-9:
            count[round(abs(x), 9)] = count.get(round(abs(x), 9), 0) + (1 if x > 0 else -1)
    return sym, all(v == 0 for v in count.values())


# ---------------------------------------------------------------------------
# Single-design evaluation (with the aerokit.composites functions)
# ---------------------------------------------------------------------------
def _load_vec(load: Any, n: int) -> np.ndarray:
    """Zero-padded load vector of length n."""
    v = np.zeros(n)
    load = np.asarray(load, float)
    v[:len(load)] = load
    return v


@cite("leriche_1994", "mil_hdbk_17_3f_2002", note="Eqs. 3.1, 3.4, 3.5 (buckling, strain, combined)")
def evaluate_stack(angles: Sequence[float], m: dict[str, Any], t: float, objective: str = "buckling",
                   load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                   strain_allowed: Sequence[float] | None = None, FS: float = 1.0, criterion: str = "tsai_wu",
                   m_max: int = 5, n_max: int = 5) -> float:
    """Objective value (larger is better) of one laminate, computed with :mod:`aerokit.composites`.

    Parameters
    ----------
    angles : sequence of float
        Ply angles [deg].
    m : dict
        Ply material.
    t : float
        Ply thickness [m].
    objective : {"stiffness", "fpf", "buckling", "strain", "buckling_strain"}
        Objective (see Notes).
    load : sequence of float
        Load vector; meaning depends on ``objective`` [N/m, N·m/m].
    a, b : float, optional
        Plate dimensions in x and y [m] (buckling objectives).
    strain_allowed : sequence of float, optional
        Allowable strains (ε1, ε2, γ12) (strain objectives).
    FS : float
        Factor of safety on strains.
    criterion : str
        Failure criterion name for ``"fpf"`` (:data:`aerokit.composites.laminate.CRITERIA`).
    m_max, n_max : int
        Half-wave search limits for plate buckling.

    Returns
    -------
    float
        Objective value.

    Raises
    ------
    ValueError
        For an unknown objective, a buckling objective without ``a``/``b`` or a strain objective without
        ``strain_allowed``.

    Notes
    -----
    ``"stiffness"``: load = (Nx, Ny, Nxy) direction; E_eff = |N|²/(h·Nᵀ A⁻¹ N) (Ex for uniaxial load,
    Gxy for pure shear).
    ``"fpf"``: load = (Nx, Ny, Nxy[, Mx, My, Mxy]) with CLT signs (tension +); first-ply-failure load
    factor (smallest :func:`aerokit.composites.laminate.strength_ratio` over the bottom/middle/top
    points of all plies).
    ``"buckling"``: load = (Nx, Ny), COMPRESSION POSITIVE; λ = Nx_cr/Nx
    (:func:`aerokit.composites.laminate.plate_buckling`, φ = Ny/Nx, a × b plate; D16, D26 neglected,
    [LR94] Eq. 3.1).
    ``"strain"``: load = (Nx, Ny[, Nxy]) compression positive;
    λ = min over plies of min(ε_iu/(FS·|ε_i|)) [LR94] Eq. 3.4, ``strain_allowed`` = (ε1, ε2, γ12).
    ``"buckling_strain"``: min(buckling, strain) [LR94] Eq. 3.5, without the penalty.
    """
    ply = laminate.layers(m, [(x, t) for x in angles])
    if objective == "stiffness":
        A = laminate.abd_matrix(ply)[0]
        N = _load_vec(load, 3)
        h = t * len(angles)
        return float(N @ N / (h * N @ np.linalg.solve(A, N)))
    if objective == "fpf":
        y = _load_vec(load, 6)
        r = laminate.laminate_analysis(ply, N=y[:3], M=y[3:])
        R = math.inf
        for k, kr in zip(ply, r["layers"], strict=True):
            for point in kr["points"].values():
                R = min(R, laminate.strength_ratio(criterion, point["sig12"], k["m"]))
        return float(R)
    if objective in ("buckling", "buckling_strain"):
        if a is None or b is None:
            raise ValueError("a and b are required for buckling")
        y = _load_vec(load, 2)
        D = laminate.abd_matrix(ply)[2]
        lb = laminate.plate_buckling(D, a, b, phi=y[1] / y[0], m_max=m_max, n_max=n_max)["Nx_cr"] / y[0]
        if objective == "buckling":
            return float(lb)
    if objective in ("strain", "buckling_strain"):
        y = _load_vec(load, 3)
        r = laminate.laminate_analysis(ply, N=-y)
        if strain_allowed is None:
            raise ValueError("strain_allowed = (ε1, ε2, γ12) is required for strain")
        e1u, e2u, gu = strain_allowed
        lg = math.inf
        for kr in r["layers"]:
            e = kr["points"]["middle"]["eps12"]
            for value, allowed in zip(np.abs(e), (e1u, e2u, gu), strict=True):
                if value > 1e-300:
                    lg = min(lg, allowed / (FS * value))
        return float(lg if objective == "strain" else min(lb, lg))
    raise ValueError("objective: stiffness, fpf, buckling, strain, buckling_strain")


# ---------------------------------------------------------------------------
# Vectorized evaluator (many stack designs at once)
# ---------------------------------------------------------------------------
@cite("leriche_1994", note="D16/D26 neglected; buckling and strain objectives of Ch. 3")
class StackEvaluator:
    """Batch evaluation of symmetric balanced laminates built from {0₂, ±45, 90₂} stacks.

    Parameters
    ----------
    m : dict
        Ply material.
    t : float
        Ply thickness [m].
    n_stack : int
        Number of stacks in the half laminate (laminate has 4·n_stack plies).
    objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max
        As in :func:`evaluate_stack`.

    Attributes
    ----------
    h : float
        Laminate thickness 4·n_stack·t [m].
    n_evaluations : int
        Number of designs evaluated so far.

    Raises
    ------
    ValueError
        If a buckling objective lacks a, b or a strain objective lacks ``strain_allowed``.

    Notes
    -----
    D11, D12, D22, D66 and A11, A12, A22, A66 are sums of the contributions of the stack positions
    (in a ±45 stack Q̄11, Q̄12, Q̄22, Q̄66 are the same for both signs; A16 = 0, D16/D26 neglected
    [LR94]). The test checks that the result equals :func:`evaluate_stack`. Vectorized objectives:
    stiffness, buckling, strain, buckling_strain; the others (fpf) are evaluated one by one with
    :func:`evaluate_stack`.
    """

    VECTORIZED = ("stiffness", "buckling", "strain", "buckling_strain")

    def __init__(self, m: dict[str, Any], t: float, n_stack: int, objective: str = "buckling",
                 load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                 strain_allowed: Sequence[float] | None = None, FS: float = 1.0, criterion: str = "tsai_wu",
                 m_max: int = 5, n_max: int = 5) -> None:
        self.m, self.t, self.n = m, t, n_stack
        self.objective, self.load, self.a, self.b = objective, load, a, b
        self.strain_allowed, self.FS, self.criterion = strain_allowed, FS, criterion
        self.m_max, self.n_max = m_max, n_max
        if objective in ("buckling", "buckling_strain") and (a is None or b is None):
            raise ValueError("a and b are required for buckling")
        if objective in ("strain", "buckling_strain") and strain_allowed is None:
            raise ValueError("strain_allowed = (ε1, ε2, γ12) is required for strain")
        Q = laminate.Q_material(m)
        Qs = [Qbar(Q, 0.0), 0.5 * (Qbar(Q, 45.0) + Qbar(Q, -45.0)), Qbar(Q, 90.0)]
        self.Qc = np.array([[q[0, 0], q[0, 1], q[1, 1], q[2, 2]] for q in Qs])      # (3, 4)
        self.h = 4 * n_stack * t
        zo = self.h / 2 - 2 * t * np.arange(n_stack)
        zi = zo - 2 * t
        self.wD = 2 * (zo ** 3 - zi ** 3) / 3                                      # mirror included
        self.wA = 4 * t
        self.n_evaluations = 0

    def stiffnesses(self, codes: Any) -> tuple[np.ndarray, np.ndarray]:
        """A and D entries of many designs.

        Parameters
        ----------
        codes : array_like
            (n_design, n_stack) stack codes.

        Returns
        -------
        A, D : numpy.ndarray
            (n_design, 4) arrays; columns 11, 12, 22, 66 [N/m] and [N·m].
        """
        codes = np.atleast_2d(np.asarray(codes, int))
        D = np.einsum("k,nkj->nj", self.wD, self.Qc[codes])
        A = self.wA * self.Qc[codes].sum(axis=1)
        return A, D

    def _buckling(self, D: np.ndarray) -> np.ndarray:
        """Buckling load factors λ = Nx_cr/Nx of many designs (specially orthotropic plate)."""
        y = _load_vec(self.load, 2)
        phi = y[1] / y[0]
        if self.a is None or self.b is None:
            raise ValueError("buckling needs plate dimensions a and b")
        r = self.b / self.a
        D11, D12, D22, D66 = D.T
        lowest = np.full(len(D), np.inf)
        for mm in range(1, self.m_max + 1):
            for nn in range(1, self.n_max + 1):
                denominator = mm * mm * r * r + phi * nn * nn
                if denominator <= 0:
                    continue
                N = (math.pi ** 2 / self.b ** 2
                     * (D11 * mm ** 4 * r ** 4 + 2 * (D12 + 2 * D66) * mm ** 2 * nn ** 2 * r ** 2 + D22 * nn ** 4)
                     / denominator)
                lowest = np.minimum(lowest, N)
        return lowest / y[0]

    def _strain(self, A: np.ndarray, codes: np.ndarray) -> np.ndarray:
        """Strain load factors λ = min ε_allow/(FS·|ε|) over the ply orientations present."""
        y = _load_vec(self.load, 3)
        A11, A12, A22, A66 = A.T
        det = A11 * A22 - A12 ** 2
        Nx, Ny, Nxy = -y
        ex = (A22 * Nx - A12 * Ny) / det
        ey = (A11 * Ny - A12 * Nx) / det
        gxy = Nxy / A66
        if self.strain_allowed is None:
            raise ValueError("strain objective needs strain_allowed = (ε1, ε2, γ12)")
        e1u, e2u, gu = self.strain_allowed
        lam: np.ndarray = np.full(len(A), np.inf)
        for code, angles in ((0, (0.0,)), (1, (45.0, -45.0)), (2, (90.0,))):
            present = np.any(codes == code, axis=1)
            for th in angles:
                T = T_strain(th)
                for row, allowed in zip(T, (e1u, e2u, gu), strict=True):
                    e = np.abs(row[0] * ex + row[1] * ey + row[2] * gxy)
                    with np.errstate(divide="ignore"):
                        lam_k = np.where(e > 1e-300, allowed / (self.FS * np.where(e > 1e-300, e, 1.0)), np.inf)
                    lam = np.where(present, np.minimum(lam, lam_k), lam)
        return lam

    def values(self, codes: Any) -> np.ndarray:
        """Objective values of many designs.

        Parameters
        ----------
        codes : array_like
            (n_design, n_stack) stack codes.

        Returns
        -------
        numpy.ndarray
            (n_design,) objective values (larger is better). Increments :attr:`n_evaluations`.
        """
        codes = np.atleast_2d(np.asarray(codes, int))
        self.n_evaluations += len(codes)
        if self.objective not in self.VECTORIZED:
            return np.array([evaluate_stack(stack_angles(k), self.m, self.t, self.objective, self.load, self.a,
                                            self.b, self.strain_allowed, self.FS, self.criterion, self.m_max,
                                            self.n_max) for k in codes])
        A, D = self.stiffnesses(codes)
        if self.objective == "stiffness":
            N = _load_vec(self.load, 3)
            A11, A12, A22, A66 = A.T
            det = A11 * A22 - A12 ** 2
            compliance = (A22 * N[0] ** 2 - 2 * A12 * N[0] * N[1] + A11 * N[1] ** 2) / det + N[2] ** 2 / A66
            return (N @ N) / (self.h * compliance)
        if self.objective == "buckling":
            return self._buckling(D)
        if self.objective == "strain":
            return self._strain(A, codes)
        return np.minimum(self._buckling(D), self._strain(A, codes))

    @staticmethod
    def adjacency(codes: Any) -> np.ndarray:
        """Longest same-angle run in the full laminate of every design (vectorized :func:`adjacency_max`).

        Parameters
        ----------
        codes : array_like
            (n_design, n_stack) stack codes.

        Returns
        -------
        numpy.ndarray
            (n_design,) integer run lengths.
        """
        codes = np.atleast_2d(np.asarray(codes, int))
        # ply angle codes: 0 → 0°, 1 → +45, 2 → −45, 3 → 90
        outer = np.array([0, 1, 3])[codes]
        inner = np.array([0, 2, 3])[codes]
        half = np.stack([outer, inner], axis=2).reshape(len(codes), -1)
        full = np.concatenate([half, half[:, ::-1]], axis=1)
        run: np.ndarray = np.ones(len(codes), int)
        longest: np.ndarray = run.copy()
        for j in range(1, full.shape[1]):
            run = np.where(full[:, j] == full[:, j - 1], run + 1, 1)
            longest = np.maximum(longest, run)
        return longest


def _result(ev: StackEvaluator, codes: Any, value: float, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """Assemble the result dict of a discrete search (re-evaluating the best design directly)."""
    codes = [int(k) for k in codes]
    angles = stack_angles(codes)
    direct = evaluate_stack(angles, ev.m, ev.t, ev.objective, ev.load, ev.a, ev.b, ev.strain_allowed, ev.FS,
                            ev.criterion, ev.m_max, ev.n_max)
    s = {"codes": codes, "stack": stack_text(codes), "angles": angles, "value": float(value),
         "value_composite": direct, "adjacency": adjacency_max(angles), "n_evaluation": ev.n_evaluations}
    if extra:
        s.update(extra)
    return s


def exhaustive_search(m: dict[str, Any], t: float, n_stack: int, objective: str = "buckling",
                      load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                      max_contiguous: int | None = 4, strain_allowed: Sequence[float] | None = None, FS: float = 1.0,
                      criterion: str = "tsai_wu", m_max: int = 5, n_max: int = 5, top_k: int = 5,
                      chunk: int = 100_000) -> dict[str, Any]:
    """Evaluate all 3^n_stack designs and return the best one.

    Parameters
    ----------
    m, t, n_stack, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max
        As in :class:`StackEvaluator` (n_stack ≲ 13 is reasonable for vectorized objectives).
    max_contiguous : int or None
        Contiguity limit on same-angle plies (None: no constraint).
    top_k : int
        Number of best designs to keep.
    chunk : int
        Designs evaluated per vectorized batch.

    Returns
    -------
    dict
        ``codes``, ``stack`` (text), ``angles``, ``value``, ``value_composite`` (value recomputed with
        :func:`evaluate_stack`), ``adjacency``, ``n_evaluation``, ``top_designs`` (list of
        ``{value, codes, stack}``, best first), ``n_design`` (= 3^n_stack).

    Raises
    ------
    ValueError
        If no feasible design exists (contiguity constraint).
    """
    ev = StackEvaluator(m, t, n_stack, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max)
    N = 3 ** n_stack
    weights = 3 ** np.arange(n_stack)[::-1]
    best: list[tuple[float, int]] = []                       # (value, index)
    for start in range(0, N, chunk):
        idx = np.arange(start, min(N, start + chunk))
        code = (idx[:, None] // weights) % 3
        v = ev.values(code)
        if max_contiguous is not None:
            v = np.where(StackEvaluator.adjacency(code) <= max_contiguous, v, -np.inf)
        k = min(top_k, len(v))
        select = np.argpartition(-v, k - 1)[:k]
        best.extend((float(v[i]), int(idx[i])) for i in select)
        best = sorted(best, reverse=True)[:top_k]
    if not best or not math.isfinite(best[0][0]):
        raise ValueError("no feasible design (contiguity constraint?)")
    entries: list[dict[str, Any]] = []
    for value, i in best:
        best_code = [int(x) for x in (i // weights) % 3]
        entries.append({"value": value, "codes": best_code, "stack": stack_text(best_code)})
    return _result(ev, entries[0]["codes"], entries[0]["value"], {"top_designs": entries, "n_design": N})


@cite("leriche_1994", "leriche_haftka_1993", note="GA structure of thesis Ch. 3; penalty form of Eq. 3.5")
def genetic_algorithm(m: dict[str, Any], t: float, n_stack: int, objective: str = "buckling",
                      load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                      max_contiguous: int | None = 4, strain_allowed: Sequence[float] | None = None, FS: float = 1.0,
                      criterion: str = "tsai_wu", m_max: int = 5, n_max: int = 5, population: int = 30,
                      max_generations: int = 400, stagnation: int = 60, p_mutation: float = 0.05,
                      p_swap: float = 0.8, penalty: float = 0.5, seed: int = 0,
                      practical_tol: float = 1e-3) -> dict[str, Any]:
    """Stack-coded genetic algorithm for the stacking sequence.

    Parameters
    ----------
    m, t, n_stack, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max
        As in :class:`StackEvaluator`.
    max_contiguous : int or None
        Contiguity limit (None: no constraint).
    population : int
        Population size.
    max_generations : int
        Maximum number of generations.
    stagnation : int
        Stop after this many generations without improvement.
    p_mutation : float
        Per-gene mutation probability.
    p_swap : float
        Probability of the stack-swap operator.
    penalty : float
        Contiguity violations multiply the objective by (1 − penalty) (penalty value is an
        ASSUMPTION).
    seed : int
        Random seed.
    practical_tol : float
        Relative tolerance defining practical optima (‰1, [LR94] §3.3.1 definition).

    Returns
    -------
    dict
        Keys of :func:`exhaustive_search` (without ``top_designs``/``n_design``) plus ``generation``
        (generations run), ``history`` (best fitness per generation) and ``practical_optima``
        (``{value, codes, stack}`` of all feasible designs within ``practical_tol`` of the best).
        ``n_evaluation`` is the number of unique evaluations.

    Raises
    ------
    ValueError
        If no feasible design was found.

    Notes
    -----
    Structure of [LR94] Chapter 3: natural {0₂, ±45, 90₂} alphabet, one-point crossover, mutation,
    swap of two stacks, elitism; selection by binary tournament. Stops after ``stagnation``
    generations without improvement or at ``max_generations``. Repeated designs are read from a
    cache.
    """
    rng = np.random.default_rng(seed)
    ev = StackEvaluator(m, t, n_stack, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max)
    cache: dict[tuple[int, ...], tuple[float, bool, float]] = {}   # design → (fitness, feasible, raw value)

    def fitness(P: np.ndarray) -> np.ndarray:
        """Penalized fitness of a population, evaluating only unseen designs."""
        key = [tuple(int(x) for x in p) for p in P]
        new = [k for k in dict.fromkeys(key) if k not in cache]
        if new:
            v = ev.values(np.array(new))
            run = StackEvaluator.adjacency(np.array(new)) if max_contiguous is not None else np.zeros(len(new))
            for k, vv, rr in zip(new, v, run, strict=True):
                feasible = max_contiguous is None or rr <= max_contiguous
                cache[k] = (float(vv) if feasible else float(vv) * (1 - penalty), feasible, float(vv))
        return np.array([cache[k][0] for k in key])

    P = rng.integers(0, 3, size=(population, n_stack))
    f = fitness(P)
    best_f, counter, history = -np.inf, 0, []
    generation = 0
    for generation in range(max_generations):  # noqa: B007 - used after the loop
        i_best = int(np.argmax(f))
        if f[i_best] > best_f * (1 + 1e-12) or not math.isfinite(best_f):
            best_f, counter = f[i_best], 0
        else:
            counter += 1
        history.append(float(best_f))
        if counter >= stagnation:
            break
        new = [P[i_best].copy()]                                     # elitism
        while len(new) < population:
            parents = []
            for _ in range(2):
                i, j = rng.integers(0, population, 2)
                parents.append(P[i] if f[i] >= f[j] else P[j])
            cut = rng.integers(1, n_stack) if n_stack > 1 else 0
            c = np.concatenate([parents[0][:cut], parents[1][cut:]])
            mut = rng.random(n_stack) < p_mutation
            c[mut] = (c[mut] + rng.integers(1, 3, mut.sum())) % 3
            if rng.random() < p_swap and n_stack > 1:
                i, j = rng.choice(n_stack, 2, replace=False)
                c[i], c[j] = c[j], c[i]
            new.append(c)
        P = np.array(new)
        f = fitness(P)
    feasible = {k: v for k, v in cache.items() if v[1]}
    if not feasible:
        raise ValueError("GA found no feasible design")
    best_k = max(feasible, key=lambda k: feasible[k][2])
    best_v = feasible[best_k][2]
    practical = sorted(((v[2], list(k)) for k, v in feasible.items() if v[2] >= best_v * (1 - practical_tol)),
                       reverse=True)
    ev.n_evaluations = len(cache)
    return _result(ev, best_k, best_v, {"generation": generation + 1, "history": history,
                                        "practical_optima": [{"value": v, "codes": k, "stack": stack_text(k)}
                                                             for v, k in practical]})


def _unique_permutations(codes: Sequence[int]) -> Iterator[list[int]]:
    """Unique permutations of a multiset in lexicographic order (next-permutation algorithm)."""
    a = sorted(codes)
    while True:
        yield list(a)
        i = len(a) - 2
        while i >= 0 and a[i] >= a[i + 1]:
            i -= 1
        if i < 0:
            return
        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
        a[i + 1:] = reversed(a[i + 1:])


def permutation_search(m: dict[str, Any], t: float, codes: Sequence[int], objective: str = "buckling",
                       load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                       max_contiguous: int | None = 4, strain_allowed: Sequence[float] | None = None,
                       FS: float = 1.0, criterion: str = "tsai_wu", m_max: int = 5, n_max: int = 5,
                       limit: int = 50_000, seed: int = 0, n_restarts: int = 10) -> dict[str, Any]:
    """Optimize the stack order with fixed stack counts (the in-plane stiffness A is unchanged).

    Parameters
    ----------
    m, t, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max
        As in :class:`StackEvaluator`.
    codes : sequence of int
        Initial stack codes (defines the stack counts).
    max_contiguous : int or None
        Contiguity limit (None: no constraint).
    limit : int
        Enumerate all permutations if their number is ≤ ``limit``.
    seed : int
        Random seed for the restarts.
    n_restarts : int
        Number of random restarts of the hill climber.

    Returns
    -------
    dict
        Keys of :func:`exhaustive_search` (without ``top_designs``/``n_design``) plus ``exact``
        (True if all permutations were enumerated) and ``n_permutation``.

    Notes
    -----
    If the number of unique permutations n!/(n0!·n1!·n2!) ≤ ``limit`` all are evaluated (exact);
    otherwise pairwise-swap hill climbing (best improving swap) with random restarts (local
    optimum).
    """
    n = len(codes)
    count = [list(codes).count(k) for k in range(3)]
    n_perm = math.factorial(n) // math.prod(math.factorial(c) for c in count)
    ev = StackEvaluator(m, t, n, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max)

    def evaluate(P: Any) -> np.ndarray:
        """Objective values with infeasible (contiguity) designs set to −∞."""
        P = np.atleast_2d(P)
        v = ev.values(P)
        if max_contiguous is not None:
            v = np.where(StackEvaluator.adjacency(P) <= max_contiguous, v, -np.inf)
        return v
    if n_perm <= limit:
        P = np.array(list(_unique_permutations(list(codes))))
        v = evaluate(P)
        i = int(np.argmax(v))
        return _result(ev, P[i], v[i], {"exact": True, "n_permutation": n_perm})
    rng = np.random.default_rng(seed)
    best_v: float = -np.inf
    best_x = np.array(codes)
    starts = [np.array(codes)] + [rng.permutation(codes) for _ in range(n_restarts)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for x in starts:
        vx = float(evaluate(x)[0])
        while True:
            neighbor = []
            for i, j in pairs:
                if x[i] != x[j]:
                    y = x.copy()
                    y[i], y[j] = y[j], y[i]
                    neighbor.append(y)
            if not neighbor:
                break
            K = np.array(neighbor)
            vk = evaluate(K)
            i = int(np.argmax(vk))
            if vk[i] <= vx * (1 + 1e-12):
                break
            x, vx = K[i], float(vk[i])
        if vx > best_v:
            best_v, best_x = vx, x.copy()
    return _result(ev, best_x, best_v, {"exact": False, "n_permutation": n_perm})


def continuous_angle_optimize(m: dict[str, Any], t: float, n_pairs: int, objective: str = "buckling",
                              load: Sequence[float] = (1.0, 0.0), a: float | None = None, b: float | None = None,
                              strain_allowed: Sequence[float] | None = None, FS: float = 1.0,
                              criterion: str = "tsai_wu", m_max: int = 5, n_max: int = 5, n_random: int = 6,
                              seed: int = 0) -> dict[str, Any]:
    """Continuous ply-angle optimization of a balanced symmetric laminate.

    Parameters
    ----------
    m, t, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max
        As in :func:`evaluate_stack`.
    n_pairs : int
        Number of ±θ_i pairs in the half laminate (total 4·n_pairs plies).
    n_random : int
        Number of random starting points (in addition to uniform 5/30/45/60/85°).
    seed : int
        Random seed.

    Returns
    -------
    dict
        ``theta`` (n_pairs,) optimal angles θ_i ∈ [0°, 90°], ``angles`` (full laminate),
        ``value`` (objective), ``success`` (L-BFGS-B flag of the best start).

    Notes
    -----
    Objective :func:`evaluate_stack`; L-BFGS-B with multiple starts. For buckling D16/D26 are
    neglected (the :func:`aerokit.composites.laminate.plate_buckling` warning is suppressed, an
    [LR94] assumption).
    """
    rng = np.random.default_rng(seed)

    def angles(th: Any) -> list[float]:
        """Full symmetric laminate [±θ_1/±θ_2/...]s."""
        half = [s * x for x in th for s in (1, -1)]
        return half + half[::-1]

    def f(th: Any) -> float:
        """Objective of the angle vector θ."""
        return evaluate_stack(angles(th), m, t, objective, load, a, b, strain_allowed, FS, criterion, m_max, n_max)
    starts = [np.full(n_pairs, v) for v in (5.0, 30.0, 45.0, 60.0, 85.0)] + \
             [rng.uniform(0, 90, n_pairs) for _ in range(n_random)]
    scale = max(abs(f(x)) for x in starts[:3]) or 1.0
    best: Any = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for x0 in starts:
            r = optimize.minimize(lambda th: -f(th) / scale, x0, method="L-BFGS-B", bounds=[(0.0, 90.0)] * n_pairs,
                                  options={"ftol": 1e-14, "gtol": 1e-10, "maxiter": 500})
            if best is None or r.fun < best.fun:
                best = r
    th = np.clip(best.x, 0, 90)
    return {"theta": th, "angles": angles(th), "value": f(th), "success": bool(best.success)}
