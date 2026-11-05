"""Preliminary structural sizing loops: spar cap, skin / web thickness, rib spacing, multi-boom
idealised section (Megson method), tube (bending + torsion + column), wing mass.

Every sizing function returns a dict with the required size (``"required"``), the margin of safety for the
given size (``"MS"``; ≈ 0 at the required size when no size is given) and the governing mode (``"mod"``).
``MS = allowable/(FS·applied) − 1`` (same definition as :func:`aerokit.structures.beam.safety_margin`).

Sources:

- Boom idealisation B = t_D·b/6·(2 + σ2/σ1), unsymmetric bending and shear flow in an idealised section
  q = −(SxIxx − SyIxy)/(IxxIyy − Ixy²)·ΣBx − (SyIyy − SxIxy)/(IxxIyy − Ixy²)·ΣBy + q_s0:
  Megson, "Aircraft Structures for Engineering Students" (4th ed.) Ch. 20, Examples 20.1-20.3 and 21.2 --
  the book was NOT read; the FOSSEE "Textbook Companion" Python notebooks (Chapter20/21.ipynb,
  tbc-python.fossee.in) were read: comments on Eqs. 20.1/20.2, inputs and result values come from there.
- Bredt-Batho q = T/(2A): :func:`aerokit.structures.beam.bredt_shear_flow`.
- Compressive buckling of a simply supported plate σ_cr = k·π²E/(12(1−ν²))·(t/b)², k = (m·b/a + a/(m·b))²:
  classical result (Timoshenko & Gere 1961) -- NOT read from the source in this session; k = 4 at a = b is
  consistent with :func:`aerokit.structures.beam.plate_buckling`. Tested by derivation checks.
- Johnson parabola σ_cr = σ_y − σ_y²/(4π²E)·λ², transition λ_c = √(2π²E/σ_y): only from search summaries
  (AMESweb, MechaniCalc) -- primary source NOT read; continuity Euler = Johnson = σ_y/2 at the transition
  is tested.

SI units (N, m, Pa, kg) unless a function says otherwise (the Megson examples are run in N and mm).
"""
from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import brentq

from aerokit.aero import wing
from aerokit.aero.weight import raymer_wing
from aerokit.references import cite
from aerokit.structures import beam


def _ms(allowable: float, applied: float, FS: float) -> float:
    """Margin of safety, see :func:`aerokit.structures.beam.safety_margin`."""
    return beam.safety_margin(allowable, applied, FS)


# --- (a) spar cap ------------------------------------------------------------------------------
def spar_cap_area(M: float, h: float, sigma_tension: float, FS: float = 1.5, sigma_compression: float | None = None,
                  A_current: float | None = None) -> dict[str, Any]:
    """Two-flange idealisation: flange force ``P = M/h``, required area ``A = FS·|M|/(h·σ_allow)``.

    Parameters
    ----------
    M : float
        Bending moment [N·m].
    h : float
        Distance between the flange centroids [m].
    sigma_tension : float
        Allowable tensile stress [Pa].
    FS : float
        Factor of safety.
    sigma_compression : float, optional
        Allowable compressive stress magnitude [Pa] (including buckling); if given, the compression flange is
        checked too and the flange needing the larger area governs.
    A_current : float, optional
        Actual flange area [m²] for the margin (default: the required area).

    Returns
    -------
    dict
        ``required`` area of each flange [m²], ``MS`` [-], ``mod`` (governing mode) and flange force ``P`` [N].

    Raises
    ------
    ValueError
        If h or an allowable stress is not positive.
    """
    if h <= 0 or sigma_tension <= 0:
        raise ValueError("h and sigma_tension must be positive")
    P = abs(M) / h
    candidates = [("spar cap tension (two flanges)", sigma_tension)]
    if sigma_compression is not None:
        if sigma_compression <= 0:
            raise ValueError("sigma_compression must be positive (a magnitude)")
        candidates.append(("spar cap compression (two flanges)", sigma_compression))
    mode, s = min(candidates, key=lambda a: a[1])
    A_req = FS * P / s
    A = A_current if A_current is not None else A_req
    MS = _ms(s, P / A, FS) if A > 0 else -1.0
    return {"required": A_req, "MS": MS, "mod": mode, "P": P}


# --- (b) skin and spar web ---------------------------------------------------------------------
@cite("bredt_1896")
def skin_web_thickness(V: float, T: float, b: float, h: float, tau_allowed: float, FS: float = 1.5,
                       t_min: float = 0.0, t_web: float | None = None, t_skin: float | None = None) -> dict[str, Any]:
    """Single-cell rectangular box (mid-line b × h): shear shared equally by the two spar webs, Bredt torsion.

    Parameters
    ----------
    V : float
        Shear force [N] (acting through the shear centre of the symmetric box).
    T : float
        Torque [N·m].
    b, h : float
        Box width and height [m].
    tau_allowed : float
        Allowable shear stress [Pa].
    FS : float
        Factor of safety.
    t_min : float
        Minimum gauge [m].
    t_web, t_skin : float, optional
        Actual thicknesses for the margins [m] (default: required values).

    Returns
    -------
    dict
        ``required_web``, ``required_skin``, ``required`` (the larger) [m]; ``MS`` (smaller of the two
        element margins), ``MS_web``, ``MS_skin`` [-]; ``mod``; shear flows ``q_web``, ``q_skin`` [N/m].

    Raises
    ------
    ValueError
        If b, h or tau_allowed is not positive.

    Notes
    -----
    ``q_V = V/(2h)``, ``q_T = T/(2bh)``; most loaded web ``q_web = q_V + |q_T|``, skin ``q_skin = |q_T|``;
    ``t = max(FS·q/τ_allow, t_min)``.
    """
    if min(b, h, tau_allowed) <= 0:
        raise ValueError("b, h and tau_allowed must be positive")
    qT = abs(beam.bredt_shear_flow(T, b * h))
    q_w = abs(V) / (2 * h) + qT
    q_s = qT
    tw = max(FS * q_w / tau_allowed, t_min)
    ts = max(FS * q_s / tau_allowed, t_min)
    tw_actual = t_web if t_web is not None else tw
    ts_actual = t_skin if t_skin is not None else ts
    ms_w = _ms(tau_allowed, q_w / tw_actual, FS)
    ms_s = _ms(tau_allowed, q_s / ts_actual, FS)
    if tw == t_min and ts == t_min:
        mode = "minimum thickness (t_min)"
    elif ms_w <= ms_s:
        mode = "spar web shear + torsion"
    else:
        mode = "skin torsion (Bredt)"
    return {"required_web": tw, "required_skin": ts, "required": max(tw, ts), "MS": min(ms_w, ms_s),
            "MS_web": ms_w, "MS_skin": ms_s, "mod": mode, "q_web": q_w, "q_skin": q_s}


# --- (c) rib spacing ---------------------------------------------------------------------------
@cite("timoshenko_gere_1961", note="simply supported plate in compression; not read in this session")
def plate_k(a: float, b: float) -> float:
    """Compression buckling coefficient of a simply supported a × b plate, ``k = min_m (m b/a + a/(m b))²``.

    Parameters
    ----------
    a : float
        Length in the load direction (rib spacing) [m].
    b : float
        Loaded-edge width [m].

    Returns
    -------
    float
        k [-].

    Raises
    ------
    ValueError
        If a or b is not positive.

    Notes
    -----
    ``f(m) = m/r + r/m`` (r = a/b) is unimodal with its minimum at m* = r, so the best integer is ⌊r⌋ or ⌈r⌉.
    """
    if a <= 0 or b <= 0:
        raise ValueError("a and b must be positive")
    r = a / b
    candidates = {max(1, math.floor(r)), max(1, math.ceil(r))}
    return min((m / r + r / m) ** 2 for m in candidates)


@cite("timoshenko_gere_1961", note="simply supported plate in compression; not read in this session")
def rib_spacing(sigma: float, t: float, b: float, E: float, nu: float, FS: float = 1.5, Fcy: float | None = None,
                a_current: float | None = None) -> dict[str, Any]:
    """Largest rib spacing a for a skin panel in compression (``σ_cr(a) ≥ FS·σ``).

    Parameters
    ----------
    sigma : float
        Applied compressive stress [Pa].
    t : float
        Skin thickness [m].
    b : float
        Loaded-edge width of the panel (stringer or spar pitch) [m].
    E, nu : float
        Young's modulus [Pa] and Poisson's ratio [-].
    FS : float
        Factor of safety.
    Fcy : float, optional
        Compressive yield stress [Pa]; if ``FS·σ > Fcy`` the mode is material yield.
    a_current : float, optional
        Actual rib spacing for the margin [m].

    Returns
    -------
    dict
        ``required`` spacing [m] (``inf`` when unconstrained, 0 when yield governs), ``MS`` [-], ``mod``,
        ``sigma_kr`` (critical stress at the evaluated spacing) [Pa], ``k_required`` [-].

    Raises
    ------
    ValueError
        If sigma, t, b or E is not positive.

    Notes
    -----
    For a ≥ b, k → 4 (lower bound); if ``4 D (t/b)²`` suffices the spacing is unconstrained. Otherwise the
    m = 1 branch gives ``a/b = (s − √(s² − 4))/2`` with ``s = √k_required``.
    """
    if min(sigma, t, b, E) <= 0:
        raise ValueError("sigma, t, b and E must be positive")
    D = math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t / b) ** 2
    k_req = FS * sigma / D
    if Fcy is not None and FS * sigma > Fcy:
        a_req, mode = 0.0, "material yield (before buckling)"
    elif k_req <= 4.0:
        a_req, mode = math.inf, "plate does not buckle (k ≥ 4 at any spacing); spacing unconstrained"
    else:
        s = math.sqrt(k_req)
        a_req, mode = b * (s - math.sqrt(s * s - 4)) / 2, "skin panel compression buckling"
    a = a_current if a_current is not None else a_req
    if a == math.inf or a == 0.0:
        sig_cr = 4 * D if a == math.inf else math.inf
    else:
        sig_cr = plate_k(a, b) * D
    if Fcy is not None:
        sig_cr = min(sig_cr, Fcy)
    return {"required": a_req, "MS": _ms(sig_cr, sigma, FS), "mod": mode, "sigma_kr": sig_cr, "k_required": k_req}


# --- (d) Megson boom idealisation --------------------------------------------------------------
@cite("megson_2007", note="Eq. 20.1")
def boom_area(t_D: float, b: float, sigma_ratio: float) -> float:
    """Contribution of a panel of width b to boom 1, ``B1 = t_D b/6 · (2 + σ2/σ1)``.

    Parameters
    ----------
    t_D : float
        Panel (skin) thickness.
    b : float
        Panel width (same length unit as ``t_D``).
    sigma_ratio : float
        Direct-stress ratio σ2/σ1 between the far and near booms [-].

    Returns
    -------
    float
        Boom area contribution (length unit squared).

    Examples
    --------
    >>> boom_area(2.0, 600.0, 1.0)
    600.0
    """
    return t_D * b / 6 * (2 + sigma_ratio)


@cite("megson_2007", note="Ch. 20 (via the FOSSEE notebooks)")
def multi_boom_section(x: ArrayLike, y: ArrayLike, B: ArrayLike, Mx: float = 0.0, My: float = 0.0, Sx: float = 0.0,
                       Sy: float = 0.0, x_s: float = 0.0, y_s: float = 0.0, T: float = 0.0, closed: bool = True,
                       t: ArrayLike | None = None, G: float | None = None, extra_area: ArrayLike | None = None,
                       center: tuple[float, float] | None = None, sigma_allowed: float | None = None,
                       tau_allowed: float | None = None, FS: float = 1.0) -> dict[str, Any]:
    """Idealised section: booms carry direct stress, panels carry shear only (Megson).

    Parameters
    ----------
    x, y : array_like
        Boom coordinates, in order around the section. Panel i runs from boom i to boom i+1; with
        ``closed=True`` the last panel returns from the last boom to the first. q > 0 means i → i+1.
    B : array_like
        Boom areas (all positive).
    Mx, My : float
        Bending moments.
    Sx, Sy : float
        Shear forces.
    x_s, y_s : float
        Line of action of (Sx, Sy).
    T : float
        Applied torque (closed sections only).
    closed : bool
        Single closed cell (True) or open section (False).
    t : float or array_like, optional
        Panel thickness(es); gives the shear stress ``tau`` (and ``dtheta_dz`` with G).
    G : float, optional
        Shear modulus.
    extra_area : array_like, optional
        Signed extra area swept by curved panels relative to the straight chord between booms.
    center : (float, float), optional
        Reference axis (default: boom-area centroid), e.g. for one-to-one comparison with worked examples.
    sigma_allowed, tau_allowed : float, optional
        Allowable boom direct stress and panel shear stress for the margins.
    FS : float
        Factor of safety.

    Returns
    -------
    dict
        ``Ixx``, ``Iyy``, ``Ixy``, ``center``, boom ``sigma`` and loads ``P``, open-section flows ``q_b``,
        panel lengths ``L``, ``q_s0``, total ``q``, resultants ``Fx``, ``Fy``, ``Mz``; for closed sections
        ``A_closed``; optional ``tau``, ``dtheta_dz``, ``MS``, ``mod``.

    Raises
    ------
    ValueError
        For mismatched lengths, too few booms, non-positive boom areas, a singular (collinear) section,
        a zero enclosed area, or torque on an open section.

    Notes
    -----
    Units are those of the inputs (consistent units required; the Megson examples use N and mm).
    Direct stress ``σ = [(My Ixx − Mx Ixy)x + (Mx Iyy − My Ixy)y]/(Ixx Iyy − Ixy²)`` about the centroid.
    Open-section flow ``q_b,i = q_b,i−1 − kx B_i x_i − ky B_i y_i`` (cut in the last panel).
    Closed-cell ``q_s0`` from moment equilibrium about the origin (z axis): ``Σ q·2A_i = x_s Sy − y_s Sx + T``.
    """
    x, y, B = (np.asarray(v, dtype=float) for v in (x, y, B))
    n = len(B)
    if not (len(x) == len(y) == n) or n < (3 if closed else 2):
        raise ValueError("x, y and B must have the same length (a closed cell needs ≥ 3 booms)")
    if np.any(B <= 0):
        raise ValueError("boom areas must be positive")
    x0, y0 = center if center is not None else (np.sum(B * x) / B.sum(), np.sum(B * y) / B.sum())
    xr, yr = x - x0, y - y0
    Ixx, Iyy, Ixy = np.sum(B * yr ** 2), np.sum(B * xr ** 2), np.sum(B * xr * yr)
    det = Ixx * Iyy - Ixy ** 2
    if det <= 0:
        raise ValueError("singular section (collinear booms)")
    sigma = ((My * Ixx - Mx * Ixy) * xr + (Mx * Iyy - My * Ixy) * yr) / det
    kx = (Sx * Ixx - Sy * Ixy) / det
    ky = (Sy * Iyy - Sx * Ixy) / det
    qb = np.cumsum(-kx * B * xr - ky * B * yr)       # panel i: after boom i
    n_panel = n if closed else n - 1
    qb = qb[:n_panel]
    j = (np.arange(n_panel) + 1) % n
    dx, dy = x[j] - x[:n_panel], y[j] - y[:n_panel]
    two_A = x[:n_panel] * y[j] - y[:n_panel] * x[j]          # r_i × r_{i+1} (about the origin)
    if extra_area is not None:
        two_A = two_A + 2 * np.asarray(extra_area, dtype=float)[:n_panel]
    L = np.hypot(dx, dy)
    result: dict[str, Any] = {"Ixx": Ixx, "Iyy": Iyy, "Ixy": Ixy, "center": (x0, y0), "sigma": sigma,
                              "P": sigma * B, "q_b": qb, "L": L}
    if closed:
        A_k = 0.5 * two_A.sum()
        if abs(A_k) < 1e-15:
            raise ValueError("the enclosed area is zero")
        qs0 = (x_s * Sy - y_s * Sx + T - np.sum(qb * two_A)) / (2 * A_k)
        q = qb + qs0
        result.update({"q_s0": qs0, "A_closed": A_k})
    else:
        if T != 0:
            raise ValueError("torsion of an open section is not modelled (Bredt applies to closed cells only)")
        q = qb
        result["q_s0"] = 0.0
    result["q"] = q
    result["Fx"], result["Fy"] = float(np.sum(q * dx)), float(np.sum(q * dy))
    result["Mz"] = float(np.sum(q * two_A))
    ms: list[float] = []
    modes: list[str] = []
    if t is not None:
        t_arr = np.broadcast_to(np.asarray(t, dtype=float), (n_panel,))
        tau = q / t_arr
        result["tau"] = tau
        if closed and G is not None:
            result["dtheta_dz"] = float(np.sum(q * L / t_arr) / (2 * result["A_closed"] * G))
        if tau_allowed is not None:
            ms.append(_ms(tau_allowed, np.max(np.abs(tau)), FS))
            modes.append("panel shear")
    if sigma_allowed is not None:
        ms.append(_ms(sigma_allowed, np.max(np.abs(sigma)), FS))
        modes.append("boom direct stress")
    if ms:
        i = int(np.argmin(ms))
        result["MS"], result["mod"] = ms[i], modes[i]
    return result


# --- (e) tube: bending + torsion + column ------------------------------------------------------
@cite("bruhn_1973", note="Johnson-Euler column curve; primary source not read in this session")
def column_stress(E: float, sigma_y: float, lam: float) -> tuple[float, str]:
    """Euler / Johnson critical column stress.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    sigma_y : float
        Yield stress [Pa].
    lam : float
        Slenderness ``K L/ρ`` [-].

    Returns
    -------
    tuple
        ``(σ_cr [Pa], mode)`` with mode ``"Euler buckling"`` or ``"Johnson buckling"``.

    Notes
    -----
    Transition ``λ_c = √(2π²E/σ_y)``; Johnson ``σ_cr = σ_y − σ_y² λ²/(4π²E)``; Euler ``π²E/λ²``.
    """
    lam_c = math.sqrt(2 * math.pi ** 2 * E / sigma_y)
    if lam >= lam_c:
        return math.pi ** 2 * E / lam ** 2, "Euler buckling"
    return sigma_y - sigma_y ** 2 * lam ** 2 / (4 * math.pi ** 2 * E), "Johnson buckling"


def tube_check(D: float, t: float, M: float = 0.0, T: float = 0.0, P_start: float = 0.0, L: float | None = None,
               K: float = 1.0, E: float | None = None, sigma_y: float | None = None,
               FS: float = 1.5) -> dict[str, Any]:
    """Von Mises and column margins of a tube.

    Parameters
    ----------
    D, t : float
        Outer diameter and wall thickness [m], ``0 < 2t ≤ D``.
    M : float
        Bending moment [N·m].
    T : float
        Torque [N·m].
    P_start : float
        Axial load [N]; positive is COMPRESSION (the column check runs only for ``P_start > 0``).
    L : float, optional
        Column length [m] (enables the column check).
    K : float
        Effective-length factor.
    E : float, optional
        Young's modulus [Pa] (required for the column check).
    sigma_y : float, optional
        Yield stress [Pa].
    FS : float
        Factor of safety.

    Returns
    -------
    dict
        ``sigma = Mc/I + P/A``, ``tau = T r/J``, ``von_mises`` [Pa], ``MS_vm`` [-]; with the column check
        ``MS_column`` [-] and ``sigma_kr`` [Pa]; overall ``MS`` and governing ``mod``.

    Raises
    ------
    ValueError
        Unless ``0 < 2t ≤ D``.
    """
    if not 0 < 2 * t <= D:
        raise ValueError("0 < 2t ≤ D is required")
    k = beam.tube(D, t)
    s = abs(M) * k["c"] / k["I"] + abs(P_start) / k["A"]
    tau = abs(T) * (D / 2) / k["J"]
    vm = math.sqrt(s ** 2 + 3 * tau ** 2)
    result: dict[str, Any] = {"sigma": s, "tau": tau, "von_mises": vm, "MS_vm": _ms(sigma_y, vm, FS)}  # type: ignore[arg-type]
    modes = [("von Mises (bending + torsion + axial)", result["MS_vm"])]
    if P_start > 0 and L is not None:
        rho = math.sqrt(k["I"] / k["A"])
        s_cr, kmod = column_stress(E, sigma_y, K * L / rho)  # type: ignore[arg-type]
        result["MS_column"] = _ms(s_cr * k["A"], P_start, FS)
        result["sigma_kr"] = s_cr
        modes.append((kmod, result["MS_column"]))
    mode, ms = min(modes, key=lambda m: m[1])
    result.update({"MS": ms, "mod": mode})
    return result


def size_tube(M: float = 0.0, T: float = 0.0, P_start: float = 0.0, L: float | None = None, K: float = 1.0,
              E: float = 70e9, sigma_y: float | None = None, FS: float = 1.5, D: float | None = None,
              t: float | None = None, D_t: float | None = None) -> dict[str, Any]:
    """Size a tube so that ``MS_min = 0`` (brentq), with exactly one of D, t or D/t fixed.

    Parameters
    ----------
    M, T, P_start, L, K, E, sigma_y, FS
        As in :func:`tube_check`.
    D : float, optional
        Fixed outer diameter → t is solved [m].
    t : float, optional
        Fixed wall thickness → D is solved [m].
    D_t : float, optional
        Fixed D/t ratio (≥ 2) → D is solved [-].

    Returns
    -------
    dict
        ``required`` (solved size) [m], ``sizing`` (``"t"`` or ``"D"``), ``D``, ``t`` [m], ``MS`` (≈ 0),
        ``mod`` and the full ``check`` dict of :func:`tube_check`.

    Raises
    ------
    ValueError
        If sigma_y is missing, not exactly one of D, t, D_t is given, ``D_t < 2``, or the margin is negative
        even at the upper end of the search range.

    Notes
    -----
    Beam-column interaction (amplification of bending by the axial load) is NEGLECTED; von Mises combines
    axial and bending stress.
    """
    if sigma_y is None or sigma_y <= 0:
        raise ValueError("sigma_y must be given")
    if sum(v is not None for v in (D, t, D_t)) != 1:
        raise ValueError("exactly one of D, t, D_t must be given")
    size: Callable[[float], tuple[float, float]]
    if D is not None:
        D_fixed = D

        def size(z: float) -> tuple[float, float]:
            return D_fixed, z
        lower, upper, name = D * 1e-7, D / 2, "t"
    elif t is not None:
        t_fixed = t

        def size(z: float) -> tuple[float, float]:
            return z, t_fixed
        lower, upper, name = 2 * t * (1 + 1e-9), 1e4 * t, "D"
    else:
        ratio = float(D_t)  # type: ignore[arg-type]  # exactly one of D, t, D_t is set (checked above)
        if ratio < 2:
            raise ValueError("D/t ≥ 2 is required")

        def size(z: float) -> tuple[float, float]:
            return z, z / ratio
        lower, upper, name = 1e-6, 10.0, "D"

    def f(z: float) -> float:
        Dz, tz = size(z)
        return tube_check(Dz, tz, M, T, P_start, L, K, E, sigma_y, FS)["MS"]
    if f(upper) < 0:
        raise ValueError(f"the margin is negative even at the top of the {name} search range (load too large)")
    if f(lower) >= 0:
        z = lower
    else:
        z = brentq(f, lower, upper, xtol=1e-14, rtol=1e-12, maxiter=500)
    Dz, tz = size(z)
    k = tube_check(Dz, tz, M, T, P_start, L, K, E, sigma_y, FS)
    return {"required": z, "sizing": name, "D": Dz, "t": tz, "MS": k["MS"], "mod": k["mod"], "check": k}


# --- (f) wing mass: sized primary structure vs. Raymer statistics -----------------------------
@cite("raymer_2018", note="statistical wing weight used only as a sanity comparison")
def wing_mass_estimated(W: float, n_limit: float, b: float, c_root: float, c_tip: float, t_c: float, rho: float,
                        sigma_allowed: float, tau_allowed: float, FS: float = 1.5, h_ratio: float = 0.85,
                        box_ratio: float = 0.5, t_min: float = 0.5e-3, distribution: str = "schrenk",
                        n_station: int = 401, secondary_factor: float = 1.0,
                        raymer: dict[str, float] | None = None) -> dict[str, Any]:
    """Box-beam sizing along the half span and mass integral.

    Parameters
    ----------
    W : float
        Aircraft weight [N].
    n_limit : float
        Limit load factor [-].
    b : float
        Wing span [m].
    c_root, c_tip : float
        Root and tip chord [m].
    t_c : float
        Thickness-to-chord ratio [-].
    rho : float
        Structural material density [kg/m³].
    sigma_allowed, tau_allowed : float
        ULTIMATE allowable direct and shear stress [Pa] (FS is applied to the load).
    FS : float
        Factor of safety; ``n_ult = FS·n_limit``.
    h_ratio : float
        Box height / section thickness [-]: ``h = h_ratio·(t/c)·c(y)``.
    box_ratio : float
        Box width / chord [-]: ``w = box_ratio·c(y)``.
    t_min : float
        Minimum skin and web gauge [m] (skins carry no torsion here).
    distribution : str
        Spanwise lift distribution passed to :func:`aerokit.aero.wing.span_loads`.
    n_station : int
        Number of spanwise stations.
    secondary_factor : float
        Allowance for ribs, leading/trailing edges and joints (ASSUMPTION; 1.0 = primary box only).
    raymer : dict, optional
        ``S, A, Lambda, taper, t_c, W_fw, q, W_dg`` [kg]; if given, the ratio to Raymer's general-aviation
        wing weight is reported (sanity check, not a validation).

    Returns
    -------
    dict
        ``masses`` (``"spar caps"``, ``"spar webs"`` (spar webs; key kept for compatibility with
        :mod:`aerokit.optimization.design`), ``"skin"``) [kg], ``primary`` and ``total`` [kg], ``n_ult``,
        station arrays ``y``, ``A_title`` (cap area per flange) [m²], ``t_web`` [m], ``h`` [m]; optional
        ``raymer`` [kg] and ``ratio_raymer`` [-].

    Raises
    ------
    ValueError
        If an input is not positive.

    Notes
    -----
    At each station the ultimate moment/shear come from :func:`aerokit.aero.wing.span_loads`. Cap area per
    flange ``M/(h σ_allow)``, web ``V/(2 h τ_allow)`` (two webs), skin ``t_min``.
    Mass per length ``ρ(2A + 2h·t_web + 2w·t_min)``; two half wings.
    """
    if min(W, n_limit, b, c_root, c_tip, t_c, rho, sigma_allowed, tau_allowed) <= 0:
        raise ValueError("inputs must be positive")
    n_ult = FS * n_limit
    loads = wing.span_loads(W, n_ult, b, c_root, c_tip, distribution=distribution, n_point=n_station)
    y = loads["y"]
    c = wing.trapezoid_chord(y, b, c_root, c_tip)
    h = h_ratio * t_c * c
    w = box_ratio * c
    A_cap = np.abs(loads["M"]) / (h * sigma_allowed)
    t_w = np.maximum(np.abs(loads["V"]) / (2 * h * tau_allowed), t_min)
    m_cap = rho * 2 * A_cap
    m_web = rho * 2 * h * t_w
    m_skin = rho * 2 * w * t_min

    def integral(f: Any) -> float:
        return 2 * float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(y)))
    masses = {"spar caps": integral(m_cap), "spar webs": integral(m_web), "skin": integral(m_skin)}
    primary = sum(masses.values())
    result: dict[str, Any] = {"masses": masses, "primary": primary, "total": primary * secondary_factor,
                              "n_ult": n_ult, "y": y, "A_title": A_cap, "t_web": t_w, "h": h}
    if raymer is not None:
        r = raymer
        m_r = raymer_wing(r["S"], r["W_fw"], r["A"], r["Lambda"], r["q"], r["taper"], r["t_c"], n_ult, r["W_dg"])
        result["raymer"] = m_r
        result["ratio_raymer"] = result["total"] / m_r
    return result
