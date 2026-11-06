"""Family-level embodied energy and CO₂ of materials and shaping processes (Ashby 2013, via a reproduction).

Values are ``(low, high)`` ranges as printed; a single printed value gives ``low == high``. They are **family**
values (all aluminium alloys, all titanium alloys…), primary production, cradle to gate; the alloy-specific
numbers of Granta EduPack supersede them on the day. Read on 2026-11-01 from the PDF text of
"Useful numbers for environmental studies" (pp. 1-11), which cites Ashby, *Materials and the Environment*, 2nd ed.
(2013) by page; Ashby's book itself was not read.

Not here, on purpose: alloy-level values (2024 vs 7075 vs Al-Li), regional smelting mixes (the aluminium figure
moves by a factor of ~2-3 with the electricity mix), AM powder and post-processing — see the decision catalogue
in ``prev_guess/01_Ansys/reports/`` for those sources and their verification tags.
"""
from __future__ import annotations

from dataclasses import dataclass

from aerokit.references import cite

__all__ = ["EcoFamily", "FAMILIES", "SHAPING", "CATALOGUE_FAMILY", "family_of", "co2_per_kg", "composite_co2_per_kg"]

Range = tuple[float, float]


@dataclass(frozen=True)
class EcoFamily:
    """Primary and recycled embodied energy [MJ/kg] and CO₂ [kg/kg]; recycle fraction in current supply [-]."""

    energy: Range
    co2: Range
    recycled_energy: Range | None
    recycled_co2: Range | None
    recycle_fraction: Range | None
    page: str                       # page in the reproduction, Ashby page in brackets


FAMILIES: dict[str, EcoFamily] = {
    "aluminium": EcoFamily((200, 220), (12, 12), (26, 26.7), (2.1, 2.1), (0.41, 0.45), "p. 1 [Ashby p. 471]"),
    "magnesium_alloy": EcoFamily((300, 330), (36, 36), (23, 26), (2.9, 2.9), (0.36, 0.41), "p. 3 [Ashby p. 473]"),
    "titanium_alloy": EcoFamily((650, 720), (46.5, 46.5), (78, 96), (5.2, 5.2), (0.23, 0.23),
                                "p. 4 [Ashby pp. 127, 474, 487, 488]"),
    "stainless_steel": EcoFamily((81, 88), (5.0, 5.0), (11, 13), (0.73, 0.73), (0.35, 0.40),
                                 "p. 3 [Ashby pp. 463-469]"),
    # added 2026-11-04 (bracket task): values read from the same reproduction by a research sub-agent [D-ag];
    # recycled-route values for plain/low-alloy steel were not reported, so they are None here
    "carbon_steel": EcoFamily((25, 28), (1.8, 1.8), None, None, None, "p. 3 [Ashby pp. 463-469], sub-agent read"),
    "low_alloy_steel": EcoFamily((31, 34), (2.0, 2.0), None, None, None, "p. 3 [Ashby pp. 463-469], sub-agent read"),
    "nickel_superalloy": EcoFamily((221, 244), (11.6, 11.6), (33.8, 37.5), (2.14, 2.14), (0.22, 0.26),
                                   "p. 4 [Ashby pp. 483, 485]"),
    "carbon_fibre": EcoFamily((450, 500), (33, 36), None, None, None, "p. 10"),
    "gfrp": EcoFamily((107, 118), (7.47, 8.26), None, None, None, "p. 11"),
    "epoxy": EcoFamily((127, 140), (6.8, 7.5), None, None, None, "p. 5"),
}
"""Primary production (bauxite → ingot for aluminium, *excluding* fabrication)."""

# shaping process → (energy MJ/kg, CO₂ kg/kg) ranges, Ashby p. 133 (reproduction p. 9)
SHAPING: dict[str, tuple[Range, Range]] = {
    "casting": ((8, 12), (0.4, 0.6)),
    "rolling": ((3, 5), (0.15, 0.25)),
    "extrusion": ((10, 20), (0.5, 1.0)),
    "wire_drawing": ((20, 40), (1.0, 2.0)),
    "metal_powder_forming": ((20, 30), (1.0, 1.5)),
    "polymer_molding": ((11, 27), (0.55, 1.4)),
    "compression_molding": ((11, 16), (0.5, 1.6)),     # printed "1.6-0.5"
    "layup": ((14, 18), (0.7, 0.9)),
    "filament_winding": ((2.7, 4.0), (0.14, 0.2)),
    "autoclave_molding": ((100, 300), (5, 15)),
}

CATALOGUE_FAMILY: dict[str, str] = {"7075-T6": "aluminium", "6061-T6": "aluminium", "2024-T351": "aluminium",
                                    "Ti-6Al-4V": "titanium_alloy"}
"""Catalogue name (:data:`aerokit.materials.library.MATERIALS`) → family."""


def family_of(name: str) -> EcoFamily:
    """Family record of a catalogue name or of a family key."""
    key = CATALOGUE_FAMILY.get(name, name)
    if key not in FAMILIES:
        raise KeyError(f"no eco family for {name!r}; families: {', '.join(FAMILIES)}; "
                       f"catalogue names: {', '.join(CATALOGUE_FAMILY)}")
    return FAMILIES[key]


@cite("useful_numbers_env", note="Ashby 2013 family values via the reproduction, pp. 1-11")
def co2_per_kg(name: str, which: str = "mid", recycled_content: float = 0.0) -> float:
    """CO₂ [kg/kg] of a family: ``which`` = "low", "mid" or "high"; ``recycled_content`` (0-1) mixes in the
    recycled route (recycled-content method, as in the Granta EduPack Eco Audit)."""
    f = family_of(name)
    if not 0 <= recycled_content <= 1:
        raise ValueError("recycled_content must be in [0, 1]")
    if recycled_content and f.recycled_co2 is None:
        raise ValueError(f"no recycled route for {name!r}")
    pick = {"low": lambda r: r[0], "high": lambda r: r[1], "mid": lambda r: 0.5 * (r[0] + r[1])}
    if which not in pick:
        raise ValueError("which must be 'low', 'mid' or 'high'")
    primary = pick[which](f.co2)
    recycled = pick[which](f.recycled_co2) if f.recycled_co2 else 0.0
    return (1 - recycled_content) * primary + recycled_content * recycled


def composite_co2_per_kg(fibre_mass_fraction: float, process: str = "autoclave_molding",
                         which: str = "mid") -> float:
    """Cradle-to-part CO₂ [kg/kg] of a carbon/epoxy laminate: fibre + epoxy by mass fraction + shaping process.

    A rule-of-mixtures estimate from the family values; it ignores prepreg conversion and scrap.
    """
    if not 0 < fibre_mass_fraction < 1:
        raise ValueError("fibre_mass_fraction must be in (0, 1)")
    if process not in SHAPING:
        raise KeyError(f"unknown process {process!r}; choose one of: {', '.join(SHAPING)}")
    w = fibre_mass_fraction
    proc = SHAPING[process][1]
    p = {"low": proc[0], "high": proc[1], "mid": 0.5 * (proc[0] + proc[1])}[which]
    return w * co2_per_kg("carbon_fibre", which) + (1 - w) * co2_per_kg("epoxy", which) + p
