"""Material catalogue (SI) with typical values, plus design allowables from MIL-HDBK-5J.

Two layers:

* :data:`MATERIALS` — compact records used by the conceptual-design commands. The aluminium
  values are Aluminum Association **typical** values (ASM/MatWeb print-outs): they are *not*
  design allowables (A/B-basis); state "typical" when they are used in a report. Every record
  carries its ``source`` and the list of fields that could not be verified (``unverified``).
* :func:`design_values` — the same record with strengths, moduli and density replaced by
  MIL-HDBK-5J design allowables for a chosen basis, grain direction and thickness, read from the
  Markdown tables in ``aerokit/materials/data`` by :mod:`aerokit.materials.handbook`.

Known discrepancy (verified 2026-10-25 by ``scripts/materials/verify_tables.py``): the AA typical
Fty of 2024-T351 (324 MPa = 47 ksi) is *below* the MIL-HDBK-5J plate A-basis allowables
(48–50 ksi, Table 3.2.3.0(b1), PDF p. 373), so it is not an upper bound for 2024-T351 plate; the Ti-6Al-4V
record holds supplier *minimum* values, which the A/B allowables may exceed.
"""
from __future__ import annotations

from typing import Any

from aerokit.materials import handbook
from aerokit.references import cite

__all__ = ["MATERIALS", "HANDBOOK_SLUG", "handbook_slug", "find", "print_catalogue", "design_values"]

MATERIALS: dict[str, dict[str, Any]] = {
    "7075-T6": {
        "name": "Al 7075-T6/T651", "E": 71.7e9, "nu": 0.33, "G": 26.9e9, "rho": 2810,
        "Fty": 503e6, "Ftu": 572e6, "Fsu": 331e6, "fatigue_5e8": 159e6,
        "source": "ASM/MatWeb print-out, quickparts.com/wp-content/uploads/2024/05/Aluminum-7075.pdf (AA typical)",
        "unverified": [],
    },
    "6061-T6": {
        "name": "Al 6061-T6/T651", "E": 68.9e9, "nu": 0.33, "G": 26e9, "rho": 2700,
        "Fty": 276e6, "Ftu": 310e6, "Fsu": 207e6, "fatigue_5e8": 96.5e6,
        "source": "ASM/MatWeb print-out, quickparts.com/wp-content/uploads/2024/05/Aluminum-6061.pdf (AA typical)",
        "unverified": ["nu and G are 'estimated from similar alloys' in the source"],
    },
    "2024-T351": {
        "name": "Al 2024-T4/T351", "E": 73.1e9, "nu": 0.33, "G": 28e9, "rho": 2780,
        "Fty": 324e6, "Ftu": 469e6, "Fsu": 283e6, "fatigue_5e8": 138e6,
        "source": "ASM/MatWeb print-out, quickparts.com/wp-content/uploads/2024/05/Aluminium-2024.pdf (AA typical)",
        "unverified": [],
    },
    "Ti-6Al-4V": {
        "name": "Ti-6Al-4V annealed", "E": 110e9, "nu": 0.34, "G": 45e9, "rho": 4430,
        "Fty": 827e6, "Ftu": 896e6,
        "source": "Aubert & Duval TA6V data sheet (Rp0.2 > 827, Rm > 896 MPa; minimum values)",
        "unverified": ["nu = 0.34 (middle of the Wikipedia/ASM range 0.31-0.37; not in the supplier source)"],
    },
    "PLA-baski": {
        "name": "Prusament PLA, 3-D printed (horizontal)", "E": 2.3e9, "nu": 0.35, "rho": 1240,
        "Fty": 51e6, "Ftu": 51e6, "layers_between": 17e6,
        "source": "Prusa Prusament PLA TDS v1.1 (2022-07-27); read by a sub-agent",
        "unverified": ["nu = 0.35 assumed", "Ftu = Fty taken (brittle)", "Z direction limited to 17 MPa"],
    },
    "IM7-8552": {
        "name": "Hexcel IM7/8552 UD, 25 °C dry", "E1": 164e9, "E2": 12e9, "nu12": 0.32, "G12": 5.29e9,
        "rho": 1570, "Xt": 2724e6, "Xc": 1690e6, "Yt": 64e6, "Yc": 200e6, "S12": 120e6, "t_layer": 0.131e-3,
        "source": "Hexcel HexPly 8552 EU data sheet (E1, E2, Xt, Xc, Yt, S12, ply thickness, density)",
        "unverified": ["nu12 = 0.32", "G12 = 5.29 GPa (model card, search summary)",
                       "Yc = 200 MPa (not in the data sheet)"],
    },
    "AS4-8552": {
        "name": "Hexcel AS4/8552 UD, 25 °C dry", "E1": 141e9, "E2": 10e9, "nu12": 0.30, "G12": 5.0e9,
        "rho": 1580, "Xt": 2207e6, "Xc": 1531e6, "Yt": 81e6, "Yc": 200e6, "S12": 114e6, "t_layer": 0.130e-3,
        "source": "Hexcel HexPly 8552 EU data sheet (E1, E2, Xt, Xc, Yt, S12, ply thickness, density)",
        "unverified": ["nu12 = 0.30 assumed", "G12 = 5.0 GPa assumed", "Yc = 200 MPa assumed"],
    },
}

# catalogue name → MIL-HDBK-5J sheet in aerokit/materials/data
HANDBOOK_SLUG: dict[str, str] = {"7075-T6": "al-7075-t6", "6061-T6": "al-6061-t6", "2024-T351": "al-2024-t351",
                                 "Ti-6Al-4V": "ti-6al-4v-annealed"}


def _key(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("_", "-")


def handbook_slug(name: str) -> str:
    """MIL-HDBK-5J sheet id of a catalogue name (``"7075-t6"`` → ``"al-7075-t6"``) or of a sheet id."""
    catalogue = next((k for k in MATERIALS if _key(k) == _key(name)), "")
    return HANDBOOK_SLUG.get(catalogue, _key(name))


def find(name: str) -> dict[str, Any]:
    """Return the catalogue record of ``name`` (case, space, dash and underscore insensitive).

    Raises
    ------
    KeyError
        Unknown material; the message lists the valid names.
    """
    if not isinstance(name, str) or not name.strip():
        raise KeyError("material name must be a non-empty string")
    key = _key(name)
    for k, v in MATERIALS.items():
        if k.lower() == key or k.lower().replace("-", "") == key.replace("-", ""):
            return v
    raise KeyError(f"material {name!r} not found; choose one of: {', '.join(MATERIALS)} "
                   f"(MIL-HDBK-5J sheets: python -m aerokit materials list)")


def print_catalogue() -> None:
    """Print the catalogue (name, kind, description, unverified fields)."""
    from aerokit.output.console import result, table
    rows = []
    for k, v in MATERIALS.items():
        kind = "composite ply" if "E1" in v else "isotropic"
        rows.append([k, kind, v["name"], "; ".join(v["unverified"]) or "—"])
    table(["Material", "Kind", "Description", "Unverified"], rows)
    result("Aluminium values are AA typical values, not design (A/B-basis) allowables.",
           "Pass --material <name>, or use 'materials allowable' for MIL-HDBK-5J design values.")


@cite("mil_hdbk_5j_2003", note="Ch. 1.4 basis definitions; alloy tables per aerokit/materials/data")
def design_values(name: str, basis: str = "A", direction: str = "L", thickness: float | None = None,
                  thickness_units: handbook.LengthUnit = "m", **filters: Any) -> dict[str, Any]:
    """Catalogue record with MIL-HDBK-5J allowables substituted.

    Parameters
    ----------
    name : str
        Catalogue name (``"7075-T6"``) or any MIL-HDBK-5J sheet id (``"al-7050-t7451"``).
    basis : {"A", "B", "S"}
        Statistical basis of the strengths.
    direction : {"L", "LT", "ST", "T"}
        Grain direction of Ftu/Fty/Fcy.
    thickness : float, optional
        Product thickness (selects the thickness row of the table).
    thickness_units : {"m", "mm", "in"}
    **filters
        ``form``, ``specification`` or ``temper`` passed to :func:`handbook.lookup_allowable`
        when a sheet holds several products.

    Returns
    -------
    dict
        Keys ``E, nu, G, rho, Ftu, Fty, Fcy, Fsu`` [SI] (missing ones omitted), ``name``,
        ``basis``, ``direction``, ``source`` (table and PDF page of every value) and
        ``unverified`` (properties not printed for this product).

    Raises
    ------
    KeyError
        Unknown material.
    ValueError
        Thickness outside the tabulated ranges, or an ambiguous selection.
    """
    slug = handbook_slug(name)
    if slug not in handbook.list_materials():
        raise KeyError(f"no MIL-HDBK-5J sheet for {name!r}; available: {', '.join(handbook.list_materials())}")
    base = dict(find(name)) if any(_key(k) == _key(name) for k in MATERIALS) else {"name": slug}
    out: dict[str, Any] = {k: v for k, v in base.items() if k not in ("source", "unverified")}
    sources: dict[str, list[str]] = {}
    missing: list[str] = []
    for prop in ("Ftu", "Fty", "Fcy", "Fsu", "E", "G", "nu", "rho"):
        try:
            a = handbook.lookup_allowable(slug, prop, basis, direction, thickness, "SI",
                                          thickness_units=thickness_units, **filters)
        except (KeyError, LookupError):
            missing.append(prop)
            continue
        out[prop] = a.value
        sources.setdefault(f"MIL-HDBK-5J Table {a.table_id}, PDF p. {a.pdf_page}", []).append(prop)
    if not any(p in out for p in ("Ftu", "Fty")):
        raise ValueError(f"no strength allowables for {name!r} with basis={basis}, direction={direction}, "
                         f"thickness={thickness}")
    source = "; ".join(f"{where} ({', '.join(props)})" for where, props in sources.items())
    out.update(basis=basis, direction=direction, thickness=thickness, source=source,
               unverified=[f"{p} not printed for this product" for p in missing])
    return out
