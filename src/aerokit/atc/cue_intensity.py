"""How intrusive the cue may be. The pilot flies; on the path the system is silent.

One table, anchored on real systems (evidence in ``03_Advionics/research/R4_cue_intensity_human_factors.md``):

    below 1 dot       quiet     needles only (real voice systems are silent on the path)
    1 dot             advise    "slightly ..."   FSF ALAR stabilised limit
    1.3 dots          caution   "well ..."       EGPWS Mode 5 soft alert
    missed approach   warning   reason + condition, JO 7110.65 5-10-14

Rules: raise after 2 frames, lower after 5 s. Repeat only for 20 % more deviation (EGPWS Mode 5). No "advise" voice below
300 ft. What the radar cannot resolve is not alerted. Voice is 10 dB above cockpit noise, never above 90 dB(A).

The formula with height weight, trend term and sound ladder is in ``03_Advionics/complex/``. Thresholds not named above are
design values [Y]; no pilot has tested them.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = ["IntensityConfig", "CueIntensity", "level_for", "voice_level_dba", "VOICE_TEXT"]

_IF_NOT_VISUAL = "If runway or approach lights not in sight, execute missed approach."

#: position words are JO 7110.65 5-12-4; the missed approach pattern is 5-10-14; elevation is 5-12-10; tower is 5-10-13
VOICE_TEXT = {"slightly_below": "Slightly below glidepath", "well_below": "Well below glidepath",
              "slightly_above": "Slightly above glidepath", "well_above": "Well above glidepath",
              "slightly_left": "Slightly left of course", "well_left": "Well left of course",
              "slightly_right": "Slightly right of course", "well_right": "Well right of course",
              "coming_down": "Coming down rapidly", "delayed": "Radar data delayed", "invalid": "Radar data invalid",
              "at_dh": "At decision height",
              "too_low": f"Too low for safe approach. {_IF_NOT_VISUAL}",
              "too_high": f"Too high for safe approach. {_IF_NOT_VISUAL}",
              "too_left": f"Too far left for safe approach. {_IF_NOT_VISUAL}",
              "too_right": f"Too far right for safe approach. {_IF_NOT_VISUAL}",
              "radar_lost": f"Radar contact lost. {_IF_NOT_VISUAL}",
              "radar_suspect": f"Radar malfunction suspected. {_IF_NOT_VISUAL}",
              "no_glidepath": f"No glidepath information available. {_IF_NOT_VISUAL}",
              "link_lost": "Guidance link lost. Apply lost communications procedure."}

_DATA_LEVEL = {"DELAYED": 2, "INVALID": 3}
_DATA_CALL = {"DELAYED": "delayed", "INVALID": "invalid"}
_VISUAL = {0: "none", 2: "advise", 3: "caution", 4: "warning"}


@dataclass(frozen=True)
class IntensityConfig:
    advise_dots: float = 1.0          # FSF ALAR 7.1
    caution_dots: float = 1.3         # EGPWS Mode 5 soft alert
    floor_vert_m: float = 18.0        # [Y] 1 alert dot is at least this, so normal error near the ground stays quiet
    floor_lat_m: float = 50.0         # [Y]
    vert_deg_per_dot: float = 0.35
    lat_deg_per_dot: float = 1.25
    raise_frames: int = 2             # [Y] time filter, HFDS 7.1.3.6
    drop_after_s: float = 5.0         # [Y]
    growth: float = 1.2               # EGPWS Mode 5: repeat only for 20 % more deviation
    gap_s: float = 5.0                # ACAS first response and PAR interval, by analogy
    warning_gap_s: float = 8.0        # [Y] the call takes about 5 s, then the Mode 5 3 s period
    warning_repeats: int = 2          # [Y]
    no_advise_voice_below_ft: float = 300.0   # [Y] the pilot is looking for lights
    noise_dba: float = 78.0           # jet cockpit 74-80 dB(A); measure in a real aircraft
    over_noise_db: float = 10.0       # MIL-STD-1472 via HFDS 7.2.8.3
    ceiling_dba: float = 90.0         # non-emergency limit, HFDS 7.2.8.4
    blink_max_s: float = 10.0         # AC 25-11A


def level_for(e_dots: float, c: IntensityConfig) -> int:
    return 3 if e_dots >= c.caution_dots else 2 if e_dots >= c.advise_dots else 0


def voice_level_dba(level: int, c: IntensityConfig) -> float | None:
    """Voice level at the ear, capped. ``None`` when the level has no voice."""
    return min(c.noise_dba + c.over_noise_db, c.ceiling_dba) if level >= 2 else None


@dataclass
class CueIntensity:
    """Call :meth:`step` once a second."""

    cfg: IntensityConfig = field(default_factory=IntensityConfig)
    level: int = 0

    def __post_init__(self) -> None:
        self._up = 0
        self._below_since: float | None = None
        self._last_voice = -1e9
        self._last_e = 0.0
        self._called = 0
        self._warnings = 0
        self._warning_since: float | None = None
        self._old_state = ""
        self._fast_said = False

    def alert_dots(self, lat_m: float, vert_m: float, range_m: float) -> tuple[float, str]:
        """Largest deviation in alert dots, and its word. Needles stay true; only the alert uses the floor."""
        c = self.cfg
        per_v = max(range_m * math.tan(math.radians(c.vert_deg_per_dot)), c.floor_vert_m)
        per_l = max(range_m * math.tan(math.radians(c.lat_deg_per_dot)), c.floor_lat_m)
        ev, el = abs(vert_m) / per_v, abs(lat_m) / per_l
        if ev >= el:
            return ev, "above" if vert_m > 0 else "below"
        return el, "right" if lat_m > 0 else "left"

    def _raise_or_drop(self, t: float, want: int) -> None:
        c = self.cfg
        if want > self.level:
            self._up += 1
            self._below_since = None
            if self._up >= c.raise_frames:
                self.level, self._up = want, 0
        elif want < self.level:
            self._up = 0
            self._below_since = t if self._below_since is None else self._below_since
            if t - self._below_since >= c.drop_after_s:
                self.level, self._below_since = want, None
        else:
            self._up, self._below_since = 0, None

    def _result(self, level: int, e: float, voice: str | None, t: float) -> dict:
        c = self.cfg
        if level == 4 and self._warning_since is None:
            self._warning_since = t
        blink = level == 4 and self._warning_since is not None and t - self._warning_since < c.blink_max_s
        return {"level": level, "intensity": round(e, 2), "voice": voice, "tone_first": bool(voice) and level == 4,
                "voice_dba": voice_level_dba(level, c) if voice else None, "visual": _VISUAL[level], "blink": blink}

    def step(self, t: float, state: str, lat_m: float | None, vert_m: float | None, range_m: float | None,
             height_ft: float | None, closing_fast: bool = False, call: str | None = None,
             resolve_m: tuple[float, float] = (0.0, 0.0)) -> dict:
        """One frame. ``call``: the warning call of an end state. ``closing_fast``: heading below the limit in the
        look-ahead, the case position alone misses. ``resolve_m``: radar 1 sigma (lateral, vertical)."""
        c = self.cfg
        changed = state != self._old_state
        self._old_state = state
        if call:
            if changed:
                self._warnings, self._last_voice = 0, -1e9
            voice = None
            if self._warnings < c.warning_repeats and t - self._last_voice >= c.warning_gap_s:
                voice, self._last_voice = call, t
                self._warnings += 1
            return self._result(4, 0.0, voice, t)
        if state == "ADVISORY":                        # below DH: one call, then quiet
            return self._result(0, 0.0, "at_dh" if changed else None, t)
        if state in _DATA_LEVEL:
            voice = _DATA_CALL[state] if changed else None
            self._last_voice = t if voice else self._last_voice
            return self._result(_DATA_LEVEL[state], 0.0, voice, t)
        if state != "VALID" or lat_m is None or vert_m is None or range_m is None or height_ft is None:
            return self._result(0, 0.0, None, t)
        sure_lat = math.copysign(max(abs(lat_m) - resolve_m[0], 0.0), lat_m)
        sure_vert = math.copysign(max(abs(vert_m) - resolve_m[1], 0.0), vert_m)
        e, word = self.alert_dots(sure_lat, sure_vert, range_m)
        self._raise_or_drop(t, 3 if closing_fast else level_for(e, c))
        lvl = self.level
        if lvl < 2:
            self._called = 0
        if closing_fast and lvl >= 3 and not self._fast_said and t - self._last_voice >= c.gap_s:
            self._fast_said = True
            self._last_voice, self._last_e, self._called = t, e, lvl
            return self._result(lvl, e, "coming_down", t)
        quiet = (lvl < 2 or self._up or (lvl == 2 and height_ft < c.no_advise_voice_below_ft)
                 or t - self._last_voice < c.gap_s or (lvl <= self._called and e < c.growth * self._last_e))
        if quiet:
            return self._result(lvl, e, None, t)
        self._last_voice, self._last_e, self._called = t, e, lvl
        return self._result(lvl, e, f"{'slightly' if lvl == 2 else 'well'}_{word}", t)
