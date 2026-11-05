"""Material cards: Ansys Engineering Data XML (MatML) and a human-readable Markdown card per material.

The XML mirrors an Engineering Data 23.1 export (``EngineeringData`` → ``Materials`` → ``MatML_Doc`` with
``Material/BulkDetails/PropertyData`` that point to ``Metadata`` ``PropertyDetails`` (pr…) and
``ParameterDetails`` (pa…)), as read in the ``Structural Steel`` export of the pymaterials-manager test data
(local copy of ``tests/data/steel_eglass_air.xml``, read 2026-11-04). Property and parameter names, unit spelling
(``<Unit power="-3"><Name>m</Name></Unit>``), the "Variable Type" qualifiers and the placeholder temperature
``7.88860905221012e-31`` of temperature-independent data are copied from that file. Temperature tables use
comma-separated ``<Data>`` lists with a matching ``Variable Type`` list (pymaterials-manager
``matml_unittest_density.xml``).

Written per material:

* Elasticity (Young's modulus, Poisson's ratio, bulk and shear modulus) as a table over temperature (20 °C and the
  working temperature);
* Density; Tensile/Compressive Yield and Tensile Ultimate Strength at the working temperature (Mechanical's
  stress tool reads one value; the room-temperature values are in the Description);
* Coefficient of Thermal Expansion, Thermal Conductivity, Specific Heat when the record has them.

Import in Workbench: Engineering Data → File → Import Engineering Data → the ``.xml``. This import was NOT tested
here (no Ansys on this laptop): the file is validated by parsing it back (:func:`read_matml`).
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from aerokit.bracket.matdata import Material

__all__ = ["matml", "write_matml", "read_matml", "markdown_card"]

ZERO_T = "7.88860905221012e-31"

_PARAMS: dict[str, tuple[str, list[tuple[str, str | None]], str | None]] = {   # id → (name, units, units-name)
    "pa0": ("Options Variable", [], None),
    "pa1": ("Density", [("kg", None), ("m", "-3")], "Density"),
    "pa2": ("Temperature", [("C", None)], "Temperature"),
    "pa41": ("Tensile Yield Strength", [("Pa", None)], "Stress"),
    "pa31": ("Compressive Yield Strength", [("Pa", None)], "Stress"),
    "pa53": ("Tensile Ultimate Strength", [("Pa", None)], "Stress"),
    "pa63": ("Coefficient of Thermal Expansion", [("C", "-1")], "InvTemp1"),
    "pa69": ("Zero-Thermal-Strain Reference Temperature", [("C", None)], "Temperature"),
    "pa72": ("Specific Heat", [("J", None), ("kg", "-1"), ("C", "-1")], "Specific Heat Capacity"),
    "pa74": ("Thermal Conductivity", [("W", None), ("m", "-1"), ("C", "-1")], "Thermal Conductivity"),
    "pa88": ("Young's Modulus", [("Pa", None)], "Stress"),
    "pa89": ("Poisson's Ratio", [], None),
    "pa90": ("Bulk Modulus", [("Pa", None)], "Stress"),
    "pa91": ("Shear Modulus", [("Pa", None)], "Stress"),
}
_PROPS = {"pr0": "Density", "pr1": "Specific Heat", "pr2": "Thermal Conductivity", "pr4": "Elasticity",
          "pr12": "Compressive Yield Strength", "pr13": "Tensile Yield Strength", "pr20": "Tensile Ultimate Strength",
          "pr23": "Coefficient of Thermal Expansion", "pr29": "Zero-Thermal-Strain Reference Temperature"}


def _fmt(v: float) -> str:
    return f"{v:.10g}"


def _interp_opts(pd: ET.Element) -> None:
    pv = ET.SubElement(pd, "ParameterValue", parameter="pa0", format="string")
    ET.SubElement(pv, "Data").text = "Interpolation Options"
    for k, v in (("AlgorithmType", "Linear Multivariate (Qhull)"), ("Normalized", "True"), ("Cached", "True"),
                 ("ExtrapolationType", "Projection to the Bounding Box")):
        ET.SubElement(pv, "Qualifier", name=k).text = v


def _value(pd: ET.Element, pa: str, values: list[float]) -> None:
    pv = ET.SubElement(pd, "ParameterValue", parameter=pa, format="float")
    ET.SubElement(pv, "Data").text = ",".join(_fmt(v) for v in values)
    ET.SubElement(pv, "Qualifier", name="Variable Type").text = ",".join(["Dependent"] * len(values))


def _temperature(pd: ET.Element, temps: list[float] | None) -> None:
    pv = ET.SubElement(pd, "ParameterValue", parameter="pa2", format="float")
    if temps is None:
        ET.SubElement(pv, "Data").text = ZERO_T
        ET.SubElement(pv, "Qualifier", name="Variable Type").text = "Independent"
    else:
        ET.SubElement(pv, "Data").text = ",".join(_fmt(t) for t in temps)
        ET.SubElement(pv, "Qualifier", name="Variable Type").text = ",".join(["Independent"] * len(temps))
    for k, v in (("Field Variable", "Temperature"), ("Default Data", "22"), ("Field Units", "C"),
                 ("Upper Limit", "Program Controlled"), ("Lower Limit", "Program Controlled")):
        ET.SubElement(pv, "Qualifier", name=k).text = v


def _material(root: ET.Element, m: Material, T_work: float) -> None:
    mat = ET.SubElement(root, "Material")
    bd = ET.SubElement(mat, "BulkDetails")
    ET.SubElement(bd, "Name").text = f"{m.name} @ {T_work:g} C (aerokit)"
    desc = (f"aerokit card for the Ideathon 2026 bracket. Room temperature: E {m.E.value / 1e9:.1f} GPa, "
            f"Fty {m.Fty.value / 1e6:.0f} MPa, Ftu {m.Ftu.value / 1e6:.0f} MPa. Strengths below are at {T_work:g} C. "
            f"Temperature factors: {m.k_source} [{m.k_tag}]. Room-temperature sources: E {m.E.source} [{m.E.tag}]; "
            f"Fty {m.Fty.source} [{m.Fty.tag}].")
    ET.SubElement(bd, "Description").text = desc
    cl = ET.SubElement(bd, "Class")
    ET.SubElement(cl, "Name").text = "Alloy"
    temps = sorted({float(m.T[0]), float(T_work)})
    # density (temperature independent)
    pd = ET.SubElement(bd, "PropertyData", property="pr0")
    ET.SubElement(pd, "Data", format="string").text = "-"
    ET.SubElement(pd, "Qualifier", name="Field Variable Compatible").text = "Temperature"
    _interp_opts(pd)
    _value(pd, "pa1", [m.rho.value])
    _temperature(pd, None)
    # elasticity table
    pd = ET.SubElement(bd, "PropertyData", property="pr4")
    ET.SubElement(pd, "Data", format="string").text = "-"
    ET.SubElement(pd, "Qualifier", name="Behavior").text = "Isotropic"
    ET.SubElement(pd, "Qualifier", name="Derive from").text = "Young's Modulus and Poisson's Ratio"
    ET.SubElement(pd, "Qualifier", name="Field Variable Compatible").text = "Temperature"
    _interp_opts(pd)
    nu = m.nu.value
    Es = [m.E_at(t) for t in temps]
    _value(pd, "pa88", Es)
    _value(pd, "pa89", [nu] * len(temps))
    _value(pd, "pa90", [E / (3 * (1 - 2 * nu)) for E in Es])
    _value(pd, "pa91", [E / (2 * (1 + nu)) for E in Es])
    _temperature(pd, temps)
    # strengths at the working temperature
    for pr, pa, val in (("pr13", "pa41", m.Fty_at(T_work)), ("pr12", "pa31", m.Fty_at(T_work)),
                        ("pr20", "pa53", m.Ftu_at(T_work))):
        pd = ET.SubElement(bd, "PropertyData", property=pr)
        ET.SubElement(pd, "Data", format="string").text = "-"
        _value(pd, pa, [val])
    if m.cte is not None:
        pd = ET.SubElement(bd, "PropertyData", property="pr23")
        ET.SubElement(pd, "Data", format="string").text = "-"
        ET.SubElement(pd, "Qualifier", name="Definition").text = "Secant"
        ET.SubElement(pd, "Qualifier", name="Behavior").text = "Isotropic"
        ET.SubElement(pd, "Qualifier", name="Field Variable Compatible").text = "Temperature"
        _interp_opts(pd)
        _value(pd, "pa63", [m.cte.value])
        _temperature(pd, None)
        pd = ET.SubElement(bd, "PropertyData", property="pr29")
        ET.SubElement(pd, "Data", format="string").text = "-"
        ET.SubElement(pd, "Qualifier", name="Definition").text = "Secant"
        ET.SubElement(pd, "Qualifier", name="Behavior").text = "Isotropic"
        _value(pd, "pa69", [22.0])
    for prop, pr, pa in ((m.cp, "pr1", "pa72"), (m.k, "pr2", "pa74")):
        if prop is None:
            continue
        pd = ET.SubElement(bd, "PropertyData", property=pr)
        ET.SubElement(pd, "Data", format="string").text = "-"
        if pr == "pr1":
            ET.SubElement(pd, "Qualifier", name="Definition").text = "Constant Pressure"
        else:
            ET.SubElement(pd, "Qualifier", name="Behavior").text = "Isotropic"
        ET.SubElement(pd, "Qualifier", name="Field Variable Compatible").text = "Temperature"
        _interp_opts(pd)
        _value(pd, pa, [prop.value])
        _temperature(pd, None)


def matml(materials: list[Material], T_work: float = 300.0) -> ET.ElementTree:
    """Engineering Data XML tree holding ``materials``."""
    ed = ET.Element("EngineeringData", version="23.1.0.209", versiondate="11/4/2026 12:00:00 PM")
    ET.SubElement(ed, "Notes").text = ("Written by aerokit.bracket.cards (Team Beetiful, Ideathon 2026); "
                                       "values and sources in the Markdown cards beside this file.")
    mats = ET.SubElement(ed, "Materials")
    doc = ET.SubElement(mats, "MatML_Doc")
    for m in materials:
        _material(doc, m, T_work)
    meta = ET.SubElement(doc, "Metadata")
    for pid, (name, units, uname) in _PARAMS.items():
        pdt = ET.SubElement(meta, "ParameterDetails", id=pid)
        ET.SubElement(pdt, "Name").text = name
        if units:
            us = ET.SubElement(pdt, "Units")
            if uname:
                us.set("name", uname)
            for un, pw in units:
                u = ET.SubElement(us, "Unit")
                if pw:
                    u.set("power", pw)
                ET.SubElement(u, "Name").text = un
        else:
            ET.SubElement(pdt, "Unitless")
    for pid, name in _PROPS.items():
        pdt = ET.SubElement(meta, "PropertyDetails", id=pid)
        ET.SubElement(pdt, "Unitless")
        ET.SubElement(pdt, "Name").text = name
    tree = ET.ElementTree(ed)
    ET.indent(tree, space="  ")
    return tree


def write_matml(path: str | Path, materials: list[Material], T_work: float = 300.0) -> Path:
    p = Path(path)
    matml(materials, T_work).write(p, encoding="UTF-8", xml_declaration=True)
    return p


def read_matml(path: str | Path) -> dict[str, dict[str, Any]]:
    """Parse an Engineering Data XML back to ``{material: {parameter name: [values] or value}}`` (round-trip check;
    also reads a real Workbench export)."""
    root = ET.parse(path).getroot()  # noqa: S314 - local Engineering Data files chosen by the user
    doc = root.find("Materials/MatML_Doc")
    if doc is None:
        raise ValueError("no Materials/MatML_Doc")
    names = {p.get("id"): p.findtext("Name") for p in doc.iter("ParameterDetails")}
    out: dict[str, dict[str, Any]] = {}
    for mat in doc.findall("Material"):
        bd = mat.find("BulkDetails")
        if bd is None:
            continue
        rec: dict[str, Any] = {}
        props = {p.get("id"): p.findtext("Name") for p in doc.iter("PropertyDetails")}
        for pd in bd.findall("PropertyData"):
            for pv in pd.findall("ParameterValue"):
                if pv.get("format") != "float":
                    continue
                vals = [float(v) for v in (pv.findtext("Data") or "").split(",") if v.strip()]
                key = str(names.get(pv.get("parameter")) or pv.get("parameter"))
                if key == "Temperature":                  # one temperature list per property
                    key = f"Temperature [{props.get(pd.get('property'), pd.get('property'))}]"
                rec[key] = vals[0] if len(vals) == 1 else vals
        out[bd.findtext("Name") or "?"] = rec
    return out


def markdown_card(m: Material, T_work: float = 300.0) -> str:
    """Human-readable card: every value with unit, source and tag, at 20 °C and ``T_work``."""
    def row(label: str, p: Any, scale: float, unit: str, at: float | None = None) -> str:
        if p is None:
            return f"| {label} | NOT FOUND | | | |\n"
        v = p.value * scale
        hot = "" if at is None else f"{at * scale:.4g}"
        return f"| {label} | {v:.4g} {unit} | {hot} | {p.source} | {p.tag} |\n"

    s = f"# Material card — {m.name}\n\n"
    s += (f"Route assumed: **{m.route}** · 3-D printable: **{'yes' if m.am else 'no'}** · working temperature "
          f"**{T_work:g} °C**.\n\nTags: D = read from the primary source (values whose source starts with \"pool\" "
          f"carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), "
          f"D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), "
          f"S = secondary, Y = assumption or proxy.\n\n")
    s += f"| Property | 20 °C | {T_work:g} °C | Source | Tag |\n|---|---|---|---|---|\n"
    s += row("Density", m.rho, 1, "kg/m³")
    s += row("Young's modulus E", m.E, 1e-9, "GPa", m.E_at(T_work))
    s += row("Poisson's ratio", m.nu, 1, "")
    s += row("Tensile yield Fty (0.2 %)", m.Fty, 1e-6, "MPa", m.Fty_at(T_work))
    s += row("Tensile ultimate Ftu", m.Ftu, 1e-6, "MPa", m.Ftu_at(T_work))
    s += row("Max service temperature", m.Tmax, 1, "°C")
    s += row("Fatigue (endurance / 1e6-1e7)", m.fatigue, 1e-6, "MPa")
    s += row("CTE", m.cte, 1e6, "µm/(m K)")
    s += row("Thermal conductivity", m.k, 1, "W/(m K)")
    s += row("Specific heat", m.cp, 1, "J/(kg K)")
    s += row("Embodied CO₂ (primary)", m.co2, 1, "kg CO₂e/kg")
    s += row("Embodied energy (primary)", m.energy, 1, "MJ/kg")
    s += row("Embodied CO₂ (recycled)", m.co2_recycled, 1, "kg CO₂e/kg")
    s += row("Price (stock / powder)", m.price, 1, "EUR/kg")
    s += f"\nTemperature factors E, Fty, Ftu at {T_work:g} °C: {m.E_at(T_work) / m.E.value:.3f}, " \
         f"{m.Fty_at(T_work) / m.Fty.value:.3f}, {m.Ftu_at(T_work) / m.Ftu.value:.3f} — {m.k_source} [{m.k_tag}].\n"
    if m.notes:
        s += "\nNotes:\n" + "".join(f"- {n}\n" for n in m.notes)
    s += ("\nAnsys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` "
          "(not tested on this laptop; the XML is checked by parsing it back).\n")
    return s
