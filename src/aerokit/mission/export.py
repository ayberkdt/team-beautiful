"""STK hand-off (P0-5): waypoint files and an Aviator performance parameter sheet.

**STK's own file formats are NOT verified here.** No STK installation or STK documentation was
used to write this module, so it writes no ``.mis``/``.aircraft``/``.pa`` files. It writes formats
whose specifications are public and which STK and most GIS tools import:

* CSV waypoints (``name, lat_deg, lon_deg, alt_m``);
* KML 2.2 (``http://www.opengis.net/kml/2.2``): one ``LineString`` for the route and one
  ``Placemark``/``Point`` per waypoint, coordinates ``lon,lat,alt``, ``altitudeMode`` absolute;
* GeoJSON (RFC 7946): a ``FeatureCollection`` with the ``LineString`` and the points,
  coordinates ``[lon, lat, alt]``.

The **Aviator parameter sheet** (Markdown + CSV) lists the values a user types by hand into
Aviator's performance models, computed from the aircraft with the P0-2 performance functions:
climb speed, rate and fuel flow versus altitude; cruise (best range) and loiter (best endurance)
speed and fuel flow at three weights; descent assumptions; absolute and service ceilings;
take-off and landing speeds; maximum and minimum level-flight speeds. The names of Aviator's
input fields are not verified against STK; confirm them on the event licence. Every file is
written atomically (:func:`aerokit.output.writers.write_text_atomic`).
"""
from __future__ import annotations

import json
import math
import os
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import brentq

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.performance import (best_climb_speed, best_endurance_speed, best_range_speed, max_rate_of_climb,
                                      rate_of_climb)
from aerokit.output.tables import Table
from aerokit.output.writers import write_text_atomic
from aerokit.references import cite

__all__ = ["KML_NS", "waypoints_csv", "waypoints_kml", "waypoints_geojson", "write_waypoints",
           "SheetValue", "AviatorSheet", "aviator_sheet", "write_aviator_sheet", "absolute_ceiling",
           "service_ceiling", "max_level_speed", "min_level_speed", "STK_DISCLAIMER"]

KML_NS = "http://www.opengis.net/kml/2.2"
STK_DISCLAIMER = ("STK file formats and Aviator field names are NOT verified by aerokit (no STK installation or "
                  "documentation was used); confirm on the event licence. KML/CSV are the safe hand-off.")
_KT = 1852.0 / 3600.0
_FT = 0.3048
_LB = 0.45359237
_H_MAX = 20000.0            # top of the ISA model in aerokit.aero.atmosphere


def _waypoints(lat: ArrayLike, lon: ArrayLike, alt: ArrayLike | float,
               names: Sequence[str] | None) -> tuple[list[float], list[float], list[float], list[str]]:
    la = np.asarray(lat, float).ravel()
    lo = np.asarray(lon, float).ravel()
    al = np.broadcast_to(np.asarray(alt, float), la.shape).astype(float)
    if la.shape != lo.shape or la.size == 0:
        raise ValueError("lat and lon must be non-empty arrays of equal length")
    if not (np.all(np.isfinite(la)) and np.all(np.isfinite(lo)) and np.all(np.isfinite(al))):
        raise ValueError("waypoints must be finite")
    if np.any(np.abs(la) > 90.0) or np.any(np.abs(lo) > 180.0):
        raise ValueError("latitude must be in [-90, 90] and longitude in [-180, 180] deg")
    nm = [f"WP{i + 1:03d}" for i in range(la.size)] if names is None else [str(n) for n in names]
    if len(nm) != la.size:
        raise ValueError("one name per waypoint")
    return la.tolist(), lo.tolist(), al.tolist(), nm


def waypoints_csv(lat: ArrayLike, lon: ArrayLike, alt: ArrayLike | float = 0.0,
                  names: Sequence[str] | None = None) -> str:
    """CSV text ``name,lat_deg,lon_deg,alt_m`` (9 decimals ≈ 0.1 mm in latitude)."""
    la, lo, al, nm = _waypoints(lat, lon, alt, names)
    rows = [[n, f"{a:.9f}", f"{b:.9f}", f"{h:.2f}"] for n, a, b, h in zip(nm, la, lo, al, strict=True)]
    return Table(["name", "lat_deg", "lon_deg", "alt_m"], rows).to_csv()


def waypoints_kml(lat: ArrayLike, lon: ArrayLike, alt: ArrayLike | float = 0.0, names: Sequence[str] | None = None,
                  title: str = "aerokit search route") -> str:
    """KML 2.2 document: a route ``LineString`` and one point placemark per waypoint."""
    la, lo, al, nm = _waypoints(lat, lon, alt, names)
    ET.register_namespace("", KML_NS)
    q = f"{{{KML_NS}}}"
    root = ET.Element(q + "kml")
    doc = ET.SubElement(root, q + "Document")
    ET.SubElement(doc, q + "name").text = title
    ET.SubElement(doc, q + "description").text = STK_DISCLAIMER
    route = ET.SubElement(doc, q + "Placemark")
    ET.SubElement(route, q + "name").text = "route"
    ls = ET.SubElement(route, q + "LineString")
    ET.SubElement(ls, q + "altitudeMode").text = "absolute"
    ET.SubElement(ls, q + "coordinates").text = " ".join(f"{b:.9f},{a:.9f},{h:.2f}"
                                                         for a, b, h in zip(la, lo, al, strict=True))
    for n, a, b, h in zip(nm, la, lo, al, strict=True):
        pm = ET.SubElement(doc, q + "Placemark")
        ET.SubElement(pm, q + "name").text = n
        pt = ET.SubElement(pm, q + "Point")
        ET.SubElement(pt, q + "altitudeMode").text = "absolute"
        ET.SubElement(pt, q + "coordinates").text = f"{b:.9f},{a:.9f},{h:.2f}"
    ET.indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def waypoints_geojson(lat: ArrayLike, lon: ArrayLike, alt: ArrayLike | float = 0.0,
                      names: Sequence[str] | None = None) -> str:
    """GeoJSON (RFC 7946) FeatureCollection: the route line and the waypoints."""
    la, lo, al, nm = _waypoints(lat, lon, alt, names)
    coords = [[b, a, h] for a, b, h in zip(la, lo, al, strict=True)]
    feats: list[dict[str, object]] = [{"type": "Feature", "properties": {"name": "route"},
                                       "geometry": {"type": "LineString", "coordinates": coords}}]
    feats += [{"type": "Feature", "properties": {"name": n, "index": i},
               "geometry": {"type": "Point", "coordinates": c}} for i, (n, c) in enumerate(zip(nm, coords,
                                                                                               strict=True))]
    return json.dumps({"type": "FeatureCollection", "features": feats}, indent=1) + "\n"


def write_waypoints(stem: str | os.PathLike[str], lat: ArrayLike, lon: ArrayLike, alt: ArrayLike | float = 0.0,
                    names: Sequence[str] | None = None, base_dir: str | os.PathLike[str] | None = None) -> list[str]:
    """Write ``<stem>.csv``, ``<stem>.kml`` and ``<stem>.geojson`` atomically; returns the paths."""
    s = os.fspath(stem)
    out = []
    for suffix, text in ((".csv", waypoints_csv(lat, lon, alt, names)), (".kml", waypoints_kml(lat, lon, alt, names)),
                         (".geojson", waypoints_geojson(lat, lon, alt, names))):
        out.append(str(write_text_atomic(s + suffix, text, suffixes=[suffix], base_dir=base_dir)))
    return out


# ----------------------------------------------------------------------------- envelope
def _roc_max(ac: Aircraft, h: float, W: float) -> float:
    return max_rate_of_climb(ac, h, W)


def _ceiling(ac: Aircraft, W: float, roc: float) -> float:
    def f(h: float) -> float:
        return _roc_max(ac, h, W) - roc
    if f(0.0) <= 0.0:
        return 0.0
    if f(_H_MAX) > 0.0:
        return math.inf
    return float(brentq(f, 0.0, _H_MAX, xtol=0.5))


def absolute_ceiling(ac: Aircraft, W: float | None = None) -> float:
    """Altitude where the maximum rate of climb is zero [m] (inf if above the 20 km ISA model)."""
    return _ceiling(ac, ac.W0 if W is None else W, 0.0)


def service_ceiling(ac: Aircraft, W: float | None = None, roc: float = 100.0 * _FT / 60.0) -> float:
    """Altitude where the maximum rate of climb equals ``roc`` (default 100 ft/min) [m]."""
    return _ceiling(ac, ac.W0 if W is None else W, roc)


def _excess(ac: Aircraft, V: float, h: float, W: float) -> float:
    return ac.power_available(V, h) - ac.power_required(V, h, W)


def max_level_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Maximum steady level speed (high-speed root of P_A = P_R) [m/s]; nan above the ceiling."""
    w = ac.W0 if W is None else W
    v0 = best_climb_speed(ac, h, w)
    if _excess(ac, v0, h, w) <= 0.0:
        return math.nan
    hi = 2.0 * v0
    for _ in range(30):
        if _excess(ac, hi, h, w) < 0.0:
            break
        hi *= 1.5
    return float(brentq(lambda v: _excess(ac, v, h, w), v0, hi, xtol=1e-4))


def min_level_speed(ac: Aircraft, h: float, W: float | None = None) -> float:
    """Minimum steady level speed: the larger of V_stall and the low-speed power limit [m/s]."""
    w = ac.W0 if W is None else W
    vs = ac.stall_speed(h, w)
    v0 = best_climb_speed(ac, h, w)
    if _excess(ac, v0, h, w) <= 0.0:
        return math.nan
    if _excess(ac, vs, h, w) >= 0.0:
        return vs
    return float(brentq(lambda v: _excess(ac, v, h, w), vs, v0, xtol=1e-4))


# ----------------------------------------------------------------------------- sheet
@dataclass(frozen=True)
class SheetValue:
    """One sheet entry in SI with its Aviator-friendly display unit."""

    section: str
    parameter: str
    altitude: float
    mass: float
    value: float
    unit: str
    note: str = ""


@dataclass(frozen=True)
class AviatorSheet:
    """Parameter sheet: values (SI) plus rendered Markdown and CSV."""

    aircraft: str
    values: tuple[SheetValue, ...]
    markdown: str
    csv: str

    def get(self, section: str, parameter: str, altitude: float | None = None, mass: float | None = None) -> float:
        """Look up one SI value (first match)."""
        for v in self.values:
            if v.section == section and v.parameter == parameter and \
                    (altitude is None or abs(v.altitude - altitude) < 1e-6) and \
                    (mass is None or abs(v.mass - mass) < 1e-6):
                return v.value
        raise KeyError(f"no sheet value {section}/{parameter} at h={altitude}, m={mass}")


def _fmt(x: float, nd: int) -> str:
    return "—" if not math.isfinite(x) else f"{x:.{nd}f}"


@cite("anderson_1999", note="power available/required: climb rate, ceilings, level-flight speed limits")
@cite("raymer_2018", note="take-off and approach speed factors 1.1 V_stall,TO and 1.3 V_stall,L "
                          "(conventional values; not re-read in this session)")
def aviator_sheet(ac: Aircraft, altitudes: Sequence[float] | None = None, *, descent_rate: float = 5.0,
                  descent_speed: float | None = None, idle_throttle: float = 0.05,
                  liftoff_factor: float = 1.1, approach_factor: float = 1.3) -> AviatorSheet:
    """Build the Aviator parameter sheet for ``ac``.

    Parameters
    ----------
    ac : Aircraft
    altitudes : sequence of float, optional
        Climb-table altitudes [m] (default 0 to the service ceiling in 1000 m steps).
    descent_rate, descent_speed, idle_throttle : float
        Descent assumptions as in :class:`aerokit.mission.simulate.Descent` (speed default: best
        range at W0 and half the service ceiling).
    liftoff_factor, approach_factor : float
        V_LOF = factor × V_stall (take-off CLmax), V_app = factor × V_stall (landing CLmax).
    """
    W0, Wf = ac.W0, ac.W_fuel
    weights = [("W0", W0), ("W0 − ½ fuel", W0 - 0.5 * Wf), ("W0 − fuel", W0 - Wf)]
    h_srv, h_abs = service_ceiling(ac), absolute_ceiling(ac)
    top = min(h_srv, _H_MAX) if math.isfinite(h_srv) else _H_MAX
    hs = list(altitudes) if altitudes is not None else [float(h) for h in np.arange(0.0, top + 1e-9, 1000.0)]
    vals: list[SheetValue] = []

    def add(sec: str, par: str, h: float, W: float, v: float, unit: str, note: str = "") -> None:
        vals.append(SheetValue(sec, par, h, W / G0, v, unit, note))

    climb_rows = []
    for h in hs:
        V = best_climb_speed(ac, h, W0)
        roc = rate_of_climb(ac, V, h, W0)
        ff = ac.engine.fuel_flow(V, h, ac.power_available(V, h))
        add("climb", "speed", h, W0, V, "m/s", "TAS, best rate of climb")
        add("climb", "rate", h, W0, roc, "m/s")
        add("climb", "fuel_flow", h, W0, ff / G0, "kg/s", "full throttle")
        climb_rows.append([f"{h:.0f}", f"{h / _FT:.0f}", f"{V * 3.6:.1f}", f"{V / _KT:.1f}", f"{roc:.1f}",
                           f"{roc / _FT * 60:.0f}", f"{ff / G0 * 3600:.1f}"])

    level_rows = []
    h_ref = round(0.5 * (h_srv if math.isfinite(h_srv) else _H_MAX), -2)
    for label, fn, sec in (("cruise (best range)", best_range_speed, "cruise"),
                           ("loiter (best endurance)", best_endurance_speed, "loiter")):
        for wl, W in weights:
            for h in (0.0, h_ref):
                V = fn(ac, h, W)
                ff = ac.fuel_flow(V, h, W)
                add(sec, "speed", h, W, V, "m/s", f"TAS, {label}, {wl}")
                add(sec, "fuel_flow", h, W, ff / G0, "kg/s", f"{label}, {wl}")
                level_rows.append([label, wl, f"{h:.0f}", f"{W / G0:.0f}", f"{V * 3.6:.1f}", f"{V / _KT:.1f}",
                                   f"{ff / G0 * 3600:.1f}", f"{ff / G0 * 3600 / _LB:.1f}"])

    Vd = best_range_speed(ac, h_ref, W0) if descent_speed is None else descent_speed
    pd = max(ac.power_required(Vd, h_ref, W0) - W0 * descent_rate, idle_throttle * ac.power_available(Vd, h_ref))
    ffd = ac.engine.fuel_flow(Vd, h_ref, pd)
    add("descent", "speed", h_ref, W0, Vd, "m/s", "TAS, constant")
    add("descent", "rate", h_ref, W0, descent_rate, "m/s", "assumed")
    add("descent", "fuel_flow", h_ref, W0, ffd / G0, "kg/s", f"thrust power max(P_R − W·RD, {idle_throttle:g}·P_A)")

    vs_to = ac.stall_speed(0.0, W0, ac.CLmax_takeoff)
    vs_l = ac.stall_speed(0.0, W0 - Wf, ac.CLmax_landing)
    add("ceilings", "service_ceiling", 0.0, W0, h_srv, "m", "ROC = 100 ft/min")
    add("ceilings", "absolute_ceiling", 0.0, W0, h_abs, "m", "ROC = 0")
    add("takeoff_landing", "stall_speed_takeoff", 0.0, W0, vs_to, "m/s", "CLmax take-off, W0, sea level")
    add("takeoff_landing", "liftoff_speed", 0.0, W0, liftoff_factor * vs_to, "m/s", f"{liftoff_factor:g} V_stall,TO")
    add("takeoff_landing", "stall_speed_landing", 0.0, W0 - Wf, vs_l, "m/s", "CLmax landing, zero usable fuel")
    add("takeoff_landing", "approach_speed", 0.0, W0 - Wf, approach_factor * vs_l, "m/s",
        f"{approach_factor:g} V_stall,L")
    lim_rows = []
    for h in hs:
        vmax, vmin, vs = max_level_speed(ac, h, W0), min_level_speed(ac, h, W0), ac.stall_speed(h, W0)
        add("limits", "max_speed", h, W0, vmax, "m/s", "TAS, P_A = P_R")
        add("limits", "min_speed", h, W0, vmin, "m/s", "TAS, max(V_stall, power limit)")
        add("limits", "stall_speed", h, W0, vs, "m/s", "TAS, clean CLmax")
        lim_rows.append([f"{h:.0f}", f"{vs * 3.6:.1f}", f"{vmin * 3.6:.1f}", f"{vmax * 3.6:.1f}",
                         _fmt(vmax / _KT, 1)])

    md = [f"# STK Aviator parameter sheet: {ac.name}", "", f"> {STK_DISCLAIMER}", "",
          f"Values from aerokit P0-2 performance (ISA, no wind, true airspeeds). W0 = {W0 / G0:.0f} kg, "
          f"usable fuel {Wf / G0:.0f} kg. Climb and speed-limit tables at W0.", "",
          Table(["altitude (m)", "altitude (ft)", "TAS (km/h)", "TAS (kt)", "ROC (m/s)", "ROC (ft/min)",
                 "fuel flow (kg/h)"], climb_rows, title="Climb at best rate of climb, full throttle").to_markdown(),
          "",
          Table(["condition", "weight", "altitude (m)", "mass (kg)", "TAS (km/h)", "TAS (kt)", "fuel flow (kg/h)",
                 "fuel flow (lb/h)"], level_rows, title="Cruise and loiter").to_markdown(), "",
          Table(["quantity", "value", "unit"], [
              ["descent TAS", f"{Vd * 3.6:.0f}", "km/h"],
              ["descent rate", f"{descent_rate / _FT * 60:.0f}", "ft/min"],
              [f"descent fuel flow at {h_ref:.0f} m", f"{ffd / G0 * 3600:.0f}", "kg/h"],
              ["service ceiling (100 ft/min)", _fmt(h_srv, 0), "m"],
              ["absolute ceiling", _fmt(h_abs, 0), "m"],
              ["stall speed, take-off flaps (W0)", f"{vs_to * 3.6:.0f}", "km/h"],
              [f"lift-off speed ({liftoff_factor:g} V_stall,TO)", f"{liftoff_factor * vs_to * 3.6:.0f}", "km/h"],
              ["stall speed, landing flaps (zero fuel)", f"{vs_l * 3.6:.0f}", "km/h"],
              [f"approach speed ({approach_factor:g} V_stall,L)", f"{approach_factor * vs_l * 3.6:.0f}", "km/h"],
          ], title="Descent, ceilings, take-off and landing (sea level; whole units)").to_markdown(), "",
          Table(["altitude (m)", "stall TAS (km/h)", "min TAS (km/h)", "max TAS (km/h)", "max TAS (kt)"], lim_rows,
                title="Level-flight speed limits at W0").to_markdown(), ""]
    csv_rows = [[v.section, v.parameter, f"{v.altitude:.1f}", f"{v.mass:.1f}", repr(float(v.value)), v.unit, v.note]
                for v in vals]
    csv = Table(["section", "parameter", "altitude_m", "mass_kg", "value", "unit", "note"], csv_rows).to_csv()
    return AviatorSheet(ac.name, tuple(vals), "\n".join(md), csv)


def write_aviator_sheet(stem: str | os.PathLike[str], sheet: AviatorSheet,
                        base_dir: str | os.PathLike[str] | None = None) -> list[str]:
    """Write ``<stem>.md`` and ``<stem>.csv`` atomically; returns the paths."""
    s = os.fspath(stem)
    return [str(write_text_atomic(s + ".md", sheet.markdown, suffixes=[".md"], base_dir=base_dir)),
            str(write_text_atomic(s + ".csv", sheet.csv, suffixes=[".csv"], base_dir=base_dir))]
