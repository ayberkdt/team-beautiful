"""Approach guidance panel: from a clearance and surveillance/navigation inputs to what the pilot sees -- and which
failures are *annunciated* instead of guessed.

One end-to-end path, all pieces existing elsewhere in aerokit:

* **clearance**: voice -> :func:`aerokit.atc.clearance.parse` -> :class:`aerokit.atc.commhealth.AdvisoryDisplay`;
  the panel needs an approach clearance for the selected runway ("cleared ILS approach runway two five right").
* **ground surveillance**: a PAR measurement of the aircraft (:func:`aerokit.atc.par.par_measure`) whose deviation
  is up-linked (data, not voice) with a time stamp;
* **on-board navigation**: the aircraft's own position estimate with a protection level
  (:func:`aerokit.approach.protection_level` style);
* geometry and needles: :func:`aerokit.approach.deviation`, :func:`aerokit.approach.to_dots`,
  :func:`aerokit.approach.glide_path_height` (read-only reuse).

The panel shows lateral and vertical deviation in dots, distance and height to the threshold, the glide-path height
and a MINIMUMS alert at the decision height. Rules (advisory concept, not certified):

=============================  ===================================================================================
condition                       panel behaviour
=============================  ===================================================================================
no approach clearance received  "NO APPROACH CLEARANCE" -- guidance still drawn, labelled advisory
clearance runway != selected    "RWY MISMATCH: cleared 25L, selected 25R"
ground uplink older than 5 s    that source is INVALID; if it was the one in use: "GND GUIDANCE LOST"
on-board PL > alert limit       on-board source INVALID: "NAV INTEGRITY" (no needle from it)
both sources valid, disagree    "SOURCES DISAGREE <d> m" -- the independent ground source drives the needles
no valid source                 both needles REMOVED + "V FLAG" / "L FLAG" -- never centred, never extrapolated
height <= decision height       "MINIMUMS" (the crew decides; the panel never commands)
comm state lost                 "COMM LOST - LAST CLEARANCE ONLY" (from the comm-health monitor)
=============================  ===================================================================================

Thresholds (5 s staleness, 35 m vertical alert limit, 30 m disagreement, needle full scale) are assumptions [Y];
35 m is the LPV-200 VAL quoted in doc 18 [D-ag].
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from aerokit.approach import Runway, deviation, glide_path_height, to_dots

__all__ = ["SourceReading", "GuidanceConfig", "GuidancePanel", "panel_frame"]


@dataclass(frozen=True)
class SourceReading:
    """One navigation/surveillance input at time ``t``: the aircraft position it implies (runway frame, m)."""

    name: str                   # "GND PAR uplink", "ON-BOARD"
    t: float
    x: float
    y: float
    z: float
    protection_level_m: float | None = None     # vertical PL if the source provides one


@dataclass(frozen=True)
class GuidanceConfig:
    stale_after_s: float = 5.0
    vertical_alert_limit_m: float = 35.0
    disagree_m: float = 30.0
    lateral_full_scale_deg: float = 2.5          # needle full scale (2 dots) [Y]
    vertical_full_scale_deg: float = 0.7
    decision_height_m: float = 60.96             # 200 ft


@dataclass
class GuidancePanel:
    """Holds the latest readings and produces the pilot's panel at time ``t``."""

    rwy: Runway
    selected_runway: str
    cfg: GuidanceConfig = field(default_factory=GuidanceConfig)
    latest: dict[str, SourceReading] = field(default_factory=dict)
    preferred: tuple[str, ...] = ("GND PAR uplink", "ON-BOARD")   # independent ground source first
    _disagree: bool = False          # hysteresis: set above disagree_m, released below 0.7 x disagree_m
    _minimums: bool = False          # latched once the decision height is reached

    def receive(self, r: SourceReading) -> None:
        self.latest[r.name] = r

    def _valid(self, t: float) -> dict[str, tuple[SourceReading, str]]:
        out = {}
        for name, r in self.latest.items():
            if t - r.t > self.cfg.stale_after_s:
                out[name] = (r, f"stale {t - r.t:.0f} s")
            elif r.protection_level_m is not None and r.protection_level_m > self.cfg.vertical_alert_limit_m:
                out[name] = (r, f"PL {r.protection_level_m:.0f} m > AL {self.cfg.vertical_alert_limit_m:.0f} m")
            else:
                out[name] = (r, "valid")
        return out

    def view(self, t: float, cleared_runway: str | None, clearance_tag: str | None = None,
             comm_state: str = "NORMAL") -> dict:
        ann: list[str] = []
        if cleared_runway is None:
            ann.append("NO APPROACH CLEARANCE")
        elif cleared_runway != self.selected_runway:
            ann.append(f"RWY MISMATCH: cleared {cleared_runway}, selected {self.selected_runway}")
        if comm_state in ("RX_LOST", "ALL_COMMS_LOST", "TX_LOST"):
            ann.append("COMM LOST - LAST CLEARANCE ONLY")
        status = self._valid(t)
        valid = [n for n in self.preferred if n in status and status[n][1] == "valid"]
        for n, (r, why) in status.items():
            if why != "valid":
                ann.append(("GND GUIDANCE LOST" if n.startswith("GND") else "NAV INTEGRITY" if "PL" in why
                            else f"{n} LOST") + f" ({why})")
        if len(valid) >= 2:
            a, b = status[valid[0]][0], status[valid[1]][0]
            d = math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))
            self._disagree = d > self.cfg.disagree_m or (self._disagree and d > 0.7 * self.cfg.disagree_m)
            if self._disagree:
                ann.append(f"SOURCES DISAGREE {d:.0f} m - using {valid[0]}")
        if not valid:
            return {"t": t, "source": None, "lat_dots": None, "vert_dots": None, "dist_nm": None, "height_m": None,
                    "gp_height_m": None, "annunciations": ann + ["V FLAG", "L FLAG"], "minimums": False,
                    "clearance": cleared_runway, "clearance_tag": clearance_tag, "advisory_only": True}
        r = status[valid[0]][0]
        dv = deviation(self.rwy, r.x, r.y, r.z)
        lat = float(to_dots(dv.lateral_angle_deg, self.cfg.lateral_full_scale_deg))
        vert = float(to_dots(dv.vertical_angle_deg, self.cfg.vertical_full_scale_deg))
        self._minimums = self._minimums or r.z <= self.cfg.decision_height_m
        minimums = self._minimums
        if minimums:
            ann.append("MINIMUMS")
        return {"t": t, "source": r.name, "lat_dots": lat, "vert_dots": vert, "dist_nm": float(r.x / 1852.0),
                "height_m": float(r.z), "gp_height_m": float(glide_path_height(self.rwy, max(r.x, self.rwy.gpip))),
                "annunciations": ann, "minimums": minimums, "clearance": cleared_runway,
                "clearance_tag": clearance_tag, "advisory_only": True}


def panel_frame(views: Sequence[dict]) -> dict:
    """Summary of a run: how often each annunciation appeared and how often the needles were removed."""
    counts: dict[str, int] = {}
    for v in views:
        for a in v["annunciations"]:
            key = a.split(" (")[0].split(":")[0]
            counts[key] = counts.get(key, 0) + 1
    removed = sum(1 for v in views if v["vert_dots"] is None)
    return {"n": len(views), "needles_removed": removed, "annunciation_counts": counts,
            "max_abs_vert_dots": float(np.nanmax([abs(v["vert_dots"]) for v in views if v["vert_dots"] is not None]
                                                 or [np.nan]))}
