"""How intrusive the cue may be: alert level, voice, sound level and visual class from deviation, trend, height, data.

Design rule: the pilot flies. On the path the system is silent; it never tells an experienced pilot what they can
already see. Evidence and tags are in ``03_Advionics/research/R4_cue_intensity_human_factors.md``. In short:

* Real voice systems are silent on the path. EGPWS Mode 5 starts at 1.3 dots below 1000 ft at about -6 dB, says one word
  and repeats only for each 20 % more deviation (Honeywell guide; CAA 2017). Normal conditions get no alarm (HFDS 7.2.1.6).
* A correct alert about a problem already being fixed is still a nuisance (Wickens et al. 2009, via Ruskin et al.), so a
  closing deviation lowers the level. The trend uses position over 5 s, not a radar rate, which is too noisy.
* Voice has an attention cost whatever its content (Helleberg and Wickens 2003), so the goal is few calls.
* Status words state position, as a PAR controller does (JO 7110.65 5-12-4). The only imperative is GO AROUND.
* Radio voice sits at 84-88 dB(A) at the ear and the non-emergency limit is 90 dB(A): loudness has only a few dB to use.

Sourced anchors and our own weights are marked in :class:`IntensityConfig`. The weights have not been tested by a pilot.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

__all__ = ["IntensityConfig", "CueIntensity", "intensity_score", "voice_level_dba", "VOICE_TEXT", "LEVELS"]

LEVELS = ("L0 QUIET", "L1 NOTE", "L2 ADVISE", "L3 CAUTION", "L4 WARNING")

VOICE_TEXT = {"slightly_below": "Slightly below path", "well_below": "Well below path",
              "slightly_above": "Slightly above path", "well_above": "Well above path",
              "slightly_left": "Slightly left", "well_left": "Well left",
              "slightly_right": "Slightly right", "well_right": "Well right",
              "coming_down": "Coming down rapidly", "no_clearance": "No clearance",
              "delayed": "Radar delayed", "invalid": "Data invalid",
              "lost": "Radar lost. If not visual, go around.",
              "limits": "Limits. If not visual, go around.", "minimums": "Minimums"}

_DATA_LEVEL = {"DELAYED": 2, "INVALID": 3, "LOST": 4, "OUTSIDE LIMITS": 4}
_DATA_CALL = {"DELAYED": "delayed", "INVALID": "invalid", "LOST": "lost", "OUTSIDE LIMITS": "limits"}


@dataclass(frozen=True)
class IntensityConfig:
    quiet_dots: float = 0.5           # [Y] nothing below this
    full_dots: float = 2.0            # EGPWS Mode 5 hard alert [D]
    above_path_factor: float = 0.75   # [Y] Mode 5 has no above-beam alert [D]: high weighs less than low
    floor_vert_m: float = 18.0        # [Y] 1 alert dot is at least this, so normal error near the ground stays quiet
    floor_lat_m: float = 50.0         # [Y] same. EGPWS also desensitises low down [D]
    vert_m_per_deg_dot: float = 0.35  # degrees per dot (needle scale)
    lat_m_per_deg_dot: float = 1.25
    gate_ft: float = 1000.0           # stabilisation gate in IMC, FSF ALAR 7.1 [D]
    far_ft: float = 1500.0            # [Y]
    far_weight: float = 0.7           # [Y] above the gate a deviation matters less
    trend_window_s: float = 5.0       # [Y] one PAR call interval [D]
    trend_step_dots: float = 0.1      # [Y]
    trend_term: float = 0.10          # [Y]
    l1: float = 0.0                   # level limits in I; [Y] set so that 1.0 and 1.3 dots land on L2 and L3
    l2: float = 0.25
    l3: float = 0.50
    raise_frames: int = 2             # [Y] time filter, HFDS 7.1.3.6 [D]
    drop_after_s: float = 5.0         # [Y]
    growth: float = 1.2               # repeat only for 20 % more deviation, EGPWS Mode 5 [D]
    gap_l2_s: float = 10.0            # [Y] two PAR intervals
    gap_l3_s: float = 5.0             # ACAS first response and PAR interval [D], used by analogy
    gap_l4_s: float = 3.0             # Mode 5 hard alert period [D]
    l4_repeats: int = 3               # [Y] Patterson 1990: further urgent repetition irritates [D]
    no_l2_voice_below_ft: float = 300.0   # [Y] the pilot is looking for lights; Mode 5 hard starts here [D]
    noise_dba: float = 78.0           # jet cockpit ambient 74-80 dB(A) [D-f]; measure it in a real aircraft
    delta_db: tuple[float, float, float] = (5.0, 11.0, 15.0)  # L2, L3, L4 above ambient [Y] on sourced anchors
    ceiling_dba: float = 90.0         # non-emergency limit, HFDS 7.2.8.4 citing MIL-STD-1472F [D]
    blink_hz: float = 2.0             # inside 0.8-4 Hz, AC 25-11A [D-via]
    blink_max_s: float = 10.0         # [D-via]


def height_weight(height_ft: float, c: IntensityConfig) -> float:
    """1.0 at and below the gate, ``far_weight`` above ``far_ft``, a line between."""
    if height_ft <= c.gate_ft:
        return 1.0
    if height_ft >= c.far_ft:
        return c.far_weight
    return 1.0 - (1.0 - c.far_weight) * (height_ft - c.gate_ft) / (c.far_ft - c.gate_ft)


def intensity_score(e_dots: float, height_ft: float, trend: float, c: IntensityConfig) -> float:
    """I = clip(H (e - 0.5) / 1.5 + G, 0, 1), and 0 at or below the quiet limit."""
    if e_dots <= c.quiet_dots:
        return 0.0
    d = min(max((e_dots - c.quiet_dots) / (c.full_dots - c.quiet_dots), 0.0), 1.0)
    return min(max(height_weight(height_ft, c) * d + trend, 0.0), 1.0)


def voice_level_dba(level: int, c: IntensityConfig) -> float | None:
    """Voice level at the ear for a level, capped. ``None`` below L2: those levels have no voice."""
    if level < 2:
        return None
    return min(c.noise_dba + c.delta_db[level - 2], c.ceiling_dba)


@dataclass
class CueIntensity:
    """Call :meth:`step` once a second. Set ``quiet`` for the pilot's CUE QUIET: no L2 or L3 voice, L4 stays."""

    cfg: IntensityConfig = field(default_factory=IntensityConfig)
    quiet: bool = False
    level: int = 0

    def __post_init__(self) -> None:
        self._hist: deque[tuple[float, float]] = deque()
        self._up = 0
        self._below_since: float | None = None
        self._last_voice = -1e9
        self._last_e = 0.0
        self._last_key = ""
        self._called_level = 0
        self._l4_calls = 0
        self._l4_since: float | None = None
        self._done = False
        self._old_state = ""
        self._fast_said = False

    def alert_dots(self, lat_m: float, vert_m: float, range_m: float) -> tuple[float, str]:
        """Largest deviation in alert dots, and the axis word. Needles stay true; only the alert uses the floor."""
        c = self.cfg
        per_v = max(range_m * math.tan(math.radians(c.vert_m_per_deg_dot)), c.floor_vert_m)
        per_l = max(range_m * math.tan(math.radians(c.lat_m_per_deg_dot)), c.floor_lat_m)
        ev = abs(vert_m) / per_v * (c.above_path_factor if vert_m > 0 else 1.0)
        el = abs(lat_m) / per_l
        if ev >= el:
            return ev, "above" if vert_m > 0 else "below"
        return el, "right" if lat_m > 0 else "left"

    def _trend(self, t: float, e: float) -> float:
        c = self.cfg
        self._hist.append((t, e))
        while self._hist and self._hist[0][0] < t - c.trend_window_s:
            self._hist.popleft()
        if t - self._hist[0][0] < c.trend_window_s - 1.0:
            return 0.0
        change = e - self._hist[0][1]
        if change > c.trend_step_dots:
            return c.trend_term
        return -c.trend_term if change < -c.trend_step_dots else 0.0

    def _guidance_level(self, t: float, score: float) -> int:
        """Raise only after ``raise_frames`` frames; lower only after ``drop_after_s`` below."""
        c = self.cfg
        want = 0 if score <= c.l1 else 1 if score < c.l2 else 2 if score < c.l3 else 3
        if want > self.level:
            self._up += 1
            self._below_since = None
            if self._up >= c.raise_frames:
                self.level, self._up = want, 0
        elif want < self.level:
            self._up = 0
            if self._below_since is None:
                self._below_since = t
            if t - self._below_since >= c.drop_after_s:
                self.level, self._below_since = want, None
        else:
            self._up, self._below_since = 0, None
        return self.level

    def _guidance_voice(self, t: float, e: float, word: str, height_ft: float) -> str | None:
        c = self.cfg
        lvl = self.level
        if lvl < 2 or self.quiet or (lvl == 2 and height_ft < c.no_l2_voice_below_ft):
            return None
        if self._up:                  # a higher level is one frame away: one call for one event
            return None
        gap = c.gap_l2_s if lvl == 2 else c.gap_l3_s
        if t - self._last_voice < gap:
            return None
        if lvl <= self._called_level and e < c.growth * self._last_e:
            return None
        self._last_voice, self._last_e, self._called_level = t, e, lvl
        return f"{'slightly' if lvl == 2 else 'well'}_{word}"

    def _result(self, level: int, score: float, trend: float, voice: str | None, t: float) -> dict:
        c = self.cfg
        if level == 4 and self._l4_since is None:
            self._l4_since = t
        blink = level == 4 and self._l4_since is not None and t - self._l4_since < c.blink_max_s
        return {"level": level, "intensity": round(score, 3), "trend": "going" if trend > 0 else
                "correcting" if trend < 0 else "holding", "voice": voice,
                "tone_first": bool(voice) and level == 4,
                "voice_dba": voice_level_dba(level, c) if voice else None,
                "visual": ("none", "note", "advise", "caution", "warning")[level], "blink": blink}

    def step(self, t: float, state: str, lat_m: float | None, vert_m: float | None, range_m: float | None,
             height_ft: float | None, closing_fast: bool = False, notice: str | None = None,
             resolve_m: tuple[float, float] = (0.0, 0.0)) -> dict:
        """One frame. ``state`` is the validity state of :class:`aerokit.atc.parcue.CueLogic`. ``closing_fast``: heading
        below the limit in the look-ahead, the case position alone misses. ``notice``: a one-off status call.
        ``resolve_m``: radar 1 sigma (lateral, vertical). What the radar cannot resolve is not alerted: ICAO also allows
        tolerance before 2 NM (Doc 4444 8.9.7.2.5.3)."""
        c = self.cfg
        changed = state != self._old_state
        self._old_state = state
        if self._done or state == "MINIMUMS":          # guidance ends; nothing after the one call
            voice = None if self._done else "minimums"
            self._done = True
            return self._result(0, 0.0, 0.0, voice, t)
        if state in _DATA_LEVEL:                       # bad data replaces guidance intensity, it never raises it
            lvl = _DATA_LEVEL[state]
            voice = None
            if lvl == 4:
                if changed:
                    self._l4_calls = 0
                if self._l4_calls < c.l4_repeats and t - self._last_voice >= c.gap_l4_s:
                    voice = _DATA_CALL[state]
                    self._l4_calls += 1
                    self._last_voice = t
            elif changed and not self.quiet:
                voice = _DATA_CALL[state]
                self._last_voice = t
            return self._result(lvl, 0.0, 0.0, voice, t)
        if state != "VALID" or lat_m is None or vert_m is None or range_m is None or height_ft is None:
            return self._result(0, 0.0, 0.0, None, t)
        sure_lat = math.copysign(max(abs(lat_m) - resolve_m[0], 0.0), lat_m)
        sure_vert = math.copysign(max(abs(vert_m) - resolve_m[1], 0.0), vert_m)
        e, word = self.alert_dots(sure_lat, sure_vert, range_m)
        trend = self._trend(t, e)
        score = intensity_score(e, height_ft, trend, c)
        if closing_fast:              # a raised floor, not a new level: same caution rules
            score = max(score, c.l3)
        lvl = self._guidance_level(t, score)
        if lvl < 2:
            self._called_level = 0
        if closing_fast and lvl >= 3 and t - self._last_voice >= c.gap_l3_s and not self.quiet and not self._fast_said:
            self._fast_said = True
            self._last_voice, self._last_e, self._called_level = t, e, lvl
            return self._result(lvl, score, trend, "coming_down", t)
        if notice and not self.quiet:
            self._last_voice = t
            return self._result(max(lvl, 2), score, trend, notice, t)
        voice = self._guidance_voice(t, e, word, height_ft)
        return self._result(lvl, score, trend, voice, t)
