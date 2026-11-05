"""Material selection by performance index (Ashby method) for a light, stiff or strong part.

For a part of fixed load and length whose cross-section is free, the mass is ``m ∝ ρ / P**n`` where ``P`` is
the limiting property (``E`` or the yield strength ``Fty``) and ``n`` depends on the loading. The best material
maximises the index ``M = P**n / ρ``; the mass of material *i* relative to the best is ``M_best / M_i``.

Cases (constants: load, length; free variable in brackets):

====================  =========  ======  =====================================================
case                  property   n       mass scaling (derivation)
====================  =========  ======  =====================================================
``tie_stiff``         E          1       m = S F L² ρ / (δ E)            [area]   (source p. 22)
``tie_strong``        Fty        1       m = S L F ρ / σ_y                [area]   (source p. 16)
``beam_stiff``        E          1/2     k ∝ E I/L³, I ∝ A² → m ∝ ρ/E^½   [size of a self-similar section]
``beam_strong``       Fty        2/3     σ ∝ M/Z, Z ∝ A^{3/2} → m ∝ ρ/σ^⅔ [size]   (source p. 26)
``panel_stiff``       E          1/3     D ∝ E t³ → t ∝ E^-⅓              [thickness]
``panel_strong``      Fty        1/2     σ ∝ M/t² → t ∝ σ^-½              [thickness]
``column_buckling``   E          1/2     F_cr = π² E I/L², I ∝ A²         [size]
====================  =========  ======  =====================================================

Rows without a "source" page were derived in this module's docstring from the scaling shown; the tests check
each row against the explicit mass formula. ``co2_per_kg`` replaces ρ by ρ·c (c in kg CO₂ per kg material),
giving the index for the *least embodied CO₂* part instead of the lightest one. Embodied CO₂ values are
**parameters**: take them from Granta EduPack (or another stated source); none are stored here.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from aerokit.materials.library import MATERIALS
from aerokit.references import cite

__all__ = ["CASES", "Ranked", "performance_index", "rank", "plate_for_stiffness", "sandwich_for_stiffness"]

# case → (property key in the material record, exponent n, wording)
CASES: dict[str, tuple[str, float, str]] = {
    "tie_stiff": ("E", 1.0, "light, stiff tie (axial, area free)"),
    "tie_strong": ("Fty", 1.0, "light, strong tie (axial, area free)"),
    "beam_stiff": ("E", 0.5, "light, stiff beam (bending, section size free)"),
    "beam_strong": ("Fty", 2.0 / 3.0, "light, strong beam (bending, section size free)"),
    "panel_stiff": ("E", 1.0 / 3.0, "light, stiff panel (bending, thickness free)"),
    "panel_strong": ("Fty", 0.5, "light, strong panel (bending, thickness free)"),
    "column_buckling": ("E", 0.5, "light column against Euler buckling (section size free)"),
}


@dataclass(frozen=True)
class Ranked:
    """One material in a ranking."""

    name: str
    index: float
    relative_mass: float          # mass / mass of the best material (1.0 = best); CO₂ ratio if co2_per_kg given
    property_value: float
    rho: float


def _case(case: str) -> tuple[str, float, str]:
    if case not in CASES:
        raise KeyError(f"unknown case {case!r}; choose one of: {', '.join(CASES)}")
    return CASES[case]


@cite("uiuc_me598_2020_selection", note="tie and cantilever indices; panel/column rows derived in the module")
def performance_index(record: Mapping[str, Any], case: str, co2_per_kg: float | None = None) -> float:
    """Index ``P**n / ρ`` (or ``P**n / (ρ c)`` with ``co2_per_kg``) of a material record in SI units.

    Raises
    ------
    KeyError
        Unknown case, or the record lacks the property (composite ply records hold ``E1``/``Xt``, not ``E``/``Fty``:
        pass a laminate-equivalent record instead).
    ValueError
        Non-positive property, density or CO₂ factor.
    """
    prop, n, _ = _case(case)
    if prop not in record or "rho" not in record:
        raise KeyError(f"record needs {prop!r} and 'rho' for case {case!r} (has: {', '.join(sorted(record))})")
    p, rho = float(record[prop]), float(record["rho"])
    if not (p > 0 and rho > 0):
        raise ValueError(f"{prop} and rho must be > 0")
    if co2_per_kg is not None and not co2_per_kg > 0:
        raise ValueError("co2_per_kg must be > 0")
    return p ** n / (rho * (co2_per_kg if co2_per_kg is not None else 1.0))


def rank(case: str, materials: Mapping[str, Mapping[str, Any]] | Iterable[str] | None = None,
         co2_per_kg: Mapping[str, float] | None = None) -> list[Ranked]:
    """Rank materials for ``case``, best first.

    Parameters
    ----------
    case : str
        A key of :data:`CASES`.
    materials : mapping or iterable of names, optional
        ``{name: record}`` with SI fields (``E`` [Pa], ``Fty`` [Pa], ``rho`` [kg/m³]) — e.g. values read from
        Granta EduPack — or names from :data:`aerokit.materials.library.MATERIALS`. Default: every isotropic
        catalogue record that has the property.
    co2_per_kg : mapping, optional
        ``{name: kg CO₂ per kg}`` for every ranked material; the ranking then minimises embodied CO₂ of the part
        and ``relative_mass`` is the CO₂ ratio.
    """
    prop, _, _ = _case(case)
    pool: dict[str, Mapping[str, Any]]
    if materials is None:
        pool = {k: v for k, v in MATERIALS.items() if prop in v}
    elif isinstance(materials, Mapping):
        pool = dict(materials)
    else:
        pool = {k: MATERIALS[k] for k in materials}
    if not pool:
        raise ValueError("no material to rank")
    if co2_per_kg is not None:
        missing = [k for k in pool if k not in co2_per_kg]
        if missing:
            raise KeyError(f"co2_per_kg missing for: {', '.join(missing)}")
    idx = {k: performance_index(v, case, None if co2_per_kg is None else co2_per_kg[k]) for k, v in pool.items()}
    best = max(idx.values())
    out = [Ranked(k, m, best / m, float(pool[k][prop]), float(pool[k]["rho"])) for k, m in idx.items()]
    return sorted(out, key=lambda r: r.relative_mass)


def plate_for_stiffness(D: float, E: float, rho: float, nu: float = 0.0) -> dict[str, float]:
    """Monolithic plate of bending stiffness ``D`` [N·m] per unit width: thickness and areal mass.

    ``D = E h³ / (12 (1 − ν²))``; with the default ``ν = 0`` it is the beam-strip value ``E h³ / 12``.
    """
    h = (12 * D * (1 - nu ** 2) / E) ** (1 / 3)
    return {"thickness_m": h, "areal_mass_kg_m2": rho * h}


def sandwich_for_stiffness(D: float, E_face: float, rho_face: float, t_face: float,
                           rho_core: float) -> dict[str, float]:
    """Symmetric thin-face sandwich of bending stiffness ``D`` [N·m] per unit width: core depth and areal mass.

    Thin faces on a weak core give ``D ≈ E_f t d² / 2`` with ``d = c + t`` the distance between face centroids
    (Zeleniakiene et al. 2012, Eq. 4, citing Zenkert 1997; the face-own and core terms are dropped). Core shear
    deflection and adhesive mass are not included: check them separately (``δ_shear = F L / (4 b d G_c)`` for
    three-point bending).
    """
    d = (2 * D / (E_face * t_face)) ** 0.5
    c = d - t_face
    if c <= 0:
        raise ValueError("faces alone already exceed D: use a thinner face or a monolithic plate")
    return {"core_m": c, "depth_m": c + 2 * t_face, "areal_mass_kg_m2": 2 * t_face * rho_face + c * rho_core}
