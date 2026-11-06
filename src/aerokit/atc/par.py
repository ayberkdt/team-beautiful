"""Precision approach radar (PAR) talk-down: radar measurement -> voice guidance -> cockpit display, and what happens
when the voice stops.

PAR is "automated approach guidance from radar expertise" in its oldest form: a ground radar measures the aircraft
against the final approach path and a controller *talks* it down ("slightly below glidepath, on course, four miles
from touchdown") about every 5 seconds. Every word of the challenge notes fits: the guidance **signal** is radar, it
reaches the pilot as **voice**, and if **communication is lost** the guidance stops. This module

* measures an aircraft with PAR-like errors (accuracy model from the ICAO Annex 10 figures summarised by ENRI:
  elevation 6 m or 0.4 % of range + 10 % of the deviation, azimuth 9 m or 0.6 % of range + 10 % of the deviation,
  update <= 1 s; research note R_par_enri_soumu.md [D-ag], fixed terms checked by the 4 Nov audit; how fixed and
  percentage terms combine is not stated, so the larger one is used, as a 2-sigma bound [Y]);
* turns the deviation into talk-down phrases: "slightly/well above/below glide path", "slightly/well left/right of
  course", trend modified by "rapidly/slowly" (example "well above glide path, coming down rapidly"), range at
  least once each mile, guidance to the decision height -- AIM 5-4-11 / AFM 51-37 6-17 as quoted by code7700.com
  (read 2026-11-04, secondary); "on course / on glidepath" and the slightly/well thresholds are our assumption [Y];
* parses those phrases back into a display state (needle position class, trend, range) -- the "translate signal" for
  a cockpit that may also receive the same deviations by datalink;
* flags **guidance lost** when no talk-down transmission has arrived for ``lost_after_s`` (5 s by default: the PAR
  lost-communication interval in the search summary [A]); the display then says so and never extrapolates guidance.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from aerokit.approach import Runway, deviation
from aerokit.references import cite

__all__ = ["ParMeasurement", "par_measure", "TalkdownRules", "talkdown_phrase", "ParDisplayState",
           "parse_talkdown", "ParGuidanceMonitor", "talkdown_series"]

NM = 1852.0


@dataclass(frozen=True)
class ParMeasurement:
    t: float
    range_m: float                 # to touchdown (along-track x from the GPIP side)
    el_dev_deg: float              # + above the glidepath
    az_dev_deg: float              # + right of course
    el_dev_m: float
    az_dev_m: float


@cite("enri_par_annex10", note="el 6 m / 0.4 % of range + 10 % of offset, az 9 m / 0.6 % + 10 % (larger, 2-sigma [Y])")
def par_measure(rwy: Runway, t: float, x: float, y: float, z: float, rng: np.random.Generator | None = None,
                errors: bool = True) -> ParMeasurement:
    """One PAR measurement of an aircraft at runway coordinates (x before the threshold, y right, z up) [m].

    Error model [Y]: zero-mean Gaussian with 2 sigma = max(6 m, 0.4 % of range + 10 % of |deviation|) (elevation)
    and max(9 m, 0.6 % of range + 10 % of |deviation|) (azimuth), converted to angle at the aircraft's range.
    """
    d = deviation(rwy, x, y, z)
    rng_m = float(max(x - rwy.gpip, 1.0))
    ev, lv = float(d.vertical_m), float(d.lateral_m)
    if errors:
        r = rng or np.random.default_rng()
        ev += float(r.normal(0, 0.5 * max(6.0, 0.004 * rng_m + 0.1 * abs(ev))))
        lv += float(r.normal(0, 0.5 * max(9.0, 0.006 * rng_m + 0.1 * abs(lv))))
    return ParMeasurement(t, rng_m, math.degrees(math.atan2(ev, rng_m)), math.degrees(math.atan2(lv, rng_m)), ev, lv)


@dataclass(frozen=True)
class TalkdownRules:
    """Deviation classes [deg] and the heading correction law -- all our assumptions [Y]."""

    gp_slightly: float = 0.1       # |el| above this -> "slightly above/below"
    gp_well: float = 0.3           # above this -> "well above/below"
    crs_slightly: float = 0.2
    crs_well: float = 0.6
    trend_deg_per_s: float = 0.02  # |d(el)/dt| above this -> "going above/below"
    heading_gain_deg: float = 10.0  # heading correction per degree of azimuth deviation, capped
    heading_cap_deg: float = 15.0


def _num_words(n: int, digits: int) -> str:
    names = "zero one two three four five six seven eight niner".split()
    return " ".join(names[int(c)] for c in f"{n:0{digits}d}")


@cite("code7700_par", note="slightly/well above/below; slightly/well left/right of course; rapidly/slowly")
def talkdown_phrase(m: ParMeasurement, prev: ParMeasurement | None, course_deg: float,
                    rules: TalkdownRules = TalkdownRules(), callsign_words: str = "") -> str:
    """One talk-down transmission (ICAO-style spoken digits) from a measurement and the previous one."""
    parts = [callsign_words] if callsign_words else []
    a = m.az_dev_deg
    if abs(a) <= rules.crs_slightly:
        parts.append("on course")
    else:
        side = "right" if a > 0 else "left"
        size = "well" if abs(a) > rules.crs_well else "slightly"
        corr = -math.copysign(min(rules.heading_cap_deg, rules.heading_gain_deg * abs(a)), a)
        hdg = int(round((course_deg + corr) % 360)) or 360
        turn = "left" if corr < 0 else "right"
        parts.append(f"{size} {side} of course turn {turn} heading {_num_words(hdg, 3)}")
    e = m.el_dev_deg
    if abs(e) <= rules.gp_slightly:
        parts.append("on glidepath")
    else:
        parts.append(f"{'well' if abs(e) > rules.gp_well else 'slightly'} {'above' if e > 0 else 'below'} glidepath")
    if prev is not None and m.t > prev.t:
        rate = (m.el_dev_deg - prev.el_dev_deg) / (m.t - prev.t)
        if abs(rate) > rules.trend_deg_per_s and abs(e) > rules.gp_slightly:
            speed = "rapidly" if abs(rate) > 3 * rules.trend_deg_per_s else "slowly"
            parts.append(f"{'going up' if rate > 0 else 'coming down'} {speed}")
    if prev is not None:                          # a whole mile was crossed since the last call -> range call
        mile = math.floor(prev.range_m / NM)
        if 1 <= mile <= 9 and m.range_m / NM < mile:
            parts.append("one mile from touchdown" if mile == 1 else f"{_num_words(mile, 1)} miles from touchdown")
    return " ".join(parts)


@dataclass(frozen=True)
class ParDisplayState:
    """What a cockpit display can draw from one talk-down transmission (classes, not invented numbers)."""

    t: float
    glidepath: str                 # "ON", "SLIGHTLY ABOVE", "WELL BELOW", ... or "?" if not heard
    course: str                    # "ON", "SLIGHTLY LEFT", ...
    trend: str = ""                # "GOING ABOVE", "CORRECTING", ""
    heading: int | None = None
    miles: int | None = None
    source: str = "PAR voice"


def parse_talkdown(text: str, t: float) -> ParDisplayState:
    """Talk-down text -> display state. Anything not heard stays '?' -- the display never fills a gap."""
    w = text.lower().split()
    s = " ".join(w)
    gp = "?"
    for k in ("on glidepath", "slightly above glidepath", "slightly below glidepath", "well above glidepath",
              "well below glidepath"):
        if k in s:
            gp = k.replace(" glidepath", "").upper()
            break
    crs = "?"
    for k, lab in (("on course", "ON"), ("slightly left of course", "SLIGHTLY LEFT"),
                   ("slightly right of course", "SLIGHTLY RIGHT"), ("well left of course", "WELL LEFT"),
                   ("well right of course", "WELL RIGHT")):
        if k in s:
            crs = lab
            break
    trend = ""
    for k in ("coming down rapidly", "coming down slowly", "going up rapidly", "going up slowly"):
        if k in s:
            trend = k.upper()
            break
    from aerokit.atc.clearance import DIGITS
    heading = None
    if "heading" in w:
        i = w.index("heading")
        dig = [DIGITS.get(x) for x in w[i + 1:i + 4]]
        if len(dig) == 3 and all(d is not None for d in dig):
            heading = int("".join(dig))           # type: ignore[arg-type]
    miles = None
    if "touchdown" in w:
        i = w.index("touchdown")
        if i >= 3 and w[i - 1] == "from" and w[i - 2] in ("miles", "mile"):
            d = DIGITS.get(w[i - 3])
            miles = int(d) if d is not None else None
    return ParDisplayState(t, gp, crs, trend, heading, miles)


@dataclass
class ParGuidanceMonitor:
    """Declares PAR guidance lost when no talk-down has been received for ``lost_after_s``."""

    lost_after_s: float = 5.0
    #: optional: calls are expected this often; between (expected + grace) and lost_after_s the status is
    #: "PAR CALL OVERDUE" (amber) instead of plain guidance. None = old behaviour.
    expected_every_s: float | None = None
    grace_s: float = 0.5
    last: ParDisplayState | None = None

    def receive(self, st: ParDisplayState) -> None:
        self.last = st

    def view(self, t: float) -> dict:
        if self.last is None:
            return {"t": t, "status": "NO PAR GUIDANCE YET", "state": None, "display": "NO PAR GUIDANCE YET"}
        age = t - self.last.t
        if age > self.lost_after_s:
            return {"t": t, "status": f"PAR GUIDANCE LOST ({age:.0f} s) - apply the lost-communication instruction "
                                      "given before final", "state": None, "last": self.last, "age_s": age,
                    "display": f"PAR GUIDANCE LOST {age:.0f} s"}
        if self.expected_every_s is not None and age > self.expected_every_s + self.grace_s:
            return {"t": t, "status": f"PAR CALL OVERDUE ({age:.0f} s) - CHECKING", "state": self.last, "age_s": age,
                    "display": f"PAR CALL OVERDUE {age:.0f} s", "caution": True}
        # the age is always on the panel: the class shown is "as of the last call", never "now"
        return {"t": t, "status": "PAR GUIDANCE", "state": self.last, "age_s": age,
                "display": f"PAR GUIDANCE - last call {max(age, 0.0):.0f} s"}


def talkdown_series(rwy: Runway, t: Sequence[float], x: Sequence[float], y: Sequence[float], z: Sequence[float],
                    every_s: float = 5.0, update_s: float = 1.0, seed: int = 0,
                    callsign_words: str = "beetle one two three", rules: TalkdownRules = TalkdownRules(),
                    decision_height_m: float = 60.96) -> list[tuple[ParMeasurement, str]]:
    """Talk-down along a trajectory: PAR measurements every ``update_s`` (<= 1 s per the PAR figures), one phrase
    every ``every_s`` from the mean of the measurements since the last call (what a controller reads off a
    persistent display), ending with "at decision height" when the aircraft reaches ``decision_height_m``
    (200 ft default) -- below that the guidance angle errors grow without bound and PAR guidance ends [Y]."""
    rng = np.random.default_rng(seed)
    out: list[tuple[ParMeasurement, str]] = []
    prev: ParMeasurement | None = None
    buf: list[ParMeasurement] = []
    next_meas = next_call = float(t[0])
    for ti, xi, yi, zi in zip(t, x, y, z):
        if zi <= decision_height_m:
            if out:
                m = par_measure(rwy, float(ti), float(xi), float(yi), float(zi), rng)
                out.append((m, f"{callsign_words} at decision height".strip()))
            break
        if ti + 1e-9 >= next_meas:
            buf.append(par_measure(rwy, float(ti), float(xi), float(yi), float(zi), rng))
            next_meas = float(ti) + update_s
        if ti + 1e-9 >= next_call and buf:
            m = ParMeasurement(buf[-1].t, buf[-1].range_m, float(np.mean([b.el_dev_deg for b in buf])),
                               float(np.mean([b.az_dev_deg for b in buf])), float(np.mean([b.el_dev_m for b in buf])),
                               float(np.mean([b.az_dev_m for b in buf])))
            out.append((m, talkdown_phrase(m, prev, rwy.course_deg, rules, callsign_words)))
            prev, buf = m, []
            next_call = float(ti) + every_s
    return out
