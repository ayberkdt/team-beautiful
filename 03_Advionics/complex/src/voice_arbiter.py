"""One voice at a time: how the PAR cue gives way to the aircraft's own alerts and to the radio.

Rules from sources (``03_Advionics/research/R4_cue_intensity_human_factors.md``):

* one aural alert at a time; a higher alert may cut a lower one (AC 25.1322-1 8.b; EGPWS pilot guide pp. 39-40);
* the priority list is TSO-C151c Table 4-2, quoted in the FAA Human Factors General Guidance, Table 4.3.1, read 6 Nov;
* TCAS aural alerts are inhibited while windshear and GPWS alerts are active (TCAS II v7.1 booklet);
* a new system must not interfere with the alerting function (AC 25.1322-1 6.e(3)).

Our design [Y]: the cue is an add-on, so it ranks below every line of that table. It never interrupts an aircraft alert.
The visual cue is never held: it stays on the display whatever the voice does. A call that repeats what the aircraft
just said is dropped. Radio: routine calls wait for the end of a transmission, a level 4 call does not.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

__all__ = ["AIRCRAFT_ALERTS", "SAME_MEANING", "ArbiterConfig", "VoiceArbiter"]

#: TSO-C151c Table 4-2: name -> (priority, level). W warning, C caution, I information.
AIRCRAFT_ALERTS: dict[str, tuple[int, str]] = {
    "REACTIVE WINDSHEAR": (1, "W"), "SINK RATE PULL UP": (2, "W"), "CLOSURE PULL UP": (3, "W"), "TERRAIN": (4, "W"),
    "V1": (5, "I"), "ENGINE FAIL": (6, "W"), "FLTA PULL UP": (7, "W"), "PWS WARNING": (8, "W"),
    "TERRAIN CAUTION": (9, "C"), "MINIMUMS": (10, "I"), "FLTA CAUTION": (11, "C"), "TOO LOW TERRAIN": (12, "C"),
    "PDA TOO LOW TERRAIN": (13, "C"), "ALTITUDE CALLOUT": (14, "I"), "TOO LOW GEAR": (15, "C"),
    "TOO LOW FLAPS": (16, "C"),
    "SINK RATE": (17, "C"), "DONT SINK": (18, "C"), "GLIDESLOPE": (19, "C"), "PWS CAUTION": (20, "C"),
    "APPROACHING MINIMUMS": (21, "I"), "BANK ANGLE": (22, "C"), "WINDSHEAR CAUTION": (23, "C"),
    "TCAS RA": (24, "W"), "TCAS TA": (25, "C")}

#: aircraft alert -> our calls that would only repeat it
SAME_MEANING: dict[str, frozenset[str]] = {
    "GLIDESLOPE": frozenset({"slightly_below", "well_below"}),
    "TOO LOW TERRAIN": frozenset({"slightly_below", "well_below"}),
    "SINK RATE": frozenset({"coming_down"}), "SINK RATE PULL UP": frozenset({"coming_down"}),
    "MINIMUMS": frozenset({"at_dh"}), "APPROACHING MINIMUMS": frozenset({"at_dh"})}


@dataclass(frozen=True)
class ArbiterConfig:
    same_meaning_s: float = 15.0      # [Y] a repeat inside this time is dropped
    hold_routine_s: float = 3.0       # [Y] a held routine call is stale after this
    hold_warning_s: float = 10.0      # [Y] a held level 4 call is stale after this; the display still shows it


@dataclass
class VoiceArbiter:
    cfg: ArbiterConfig = field(default_factory=ArbiterConfig)

    def __post_init__(self) -> None:
        self._pending: tuple[str, int, float] | None = None
        self._heard: dict[str, float] = {}

    def _repeats(self, key: str, t: float) -> bool:
        window = self.cfg.same_meaning_s
        return any(t - at <= window and key in SAME_MEANING.get(name, ()) for name, at in self._heard.items())

    def step(self, t: float, request: str | None, level: int, aircraft: Sequence[str] = (),
             radio: bool = False) -> dict:
        """One frame. ``aircraft``: alerts sounding now. Returns the call to play, if any, and what happened to it."""
        unknown = [a for a in aircraft if a not in AIRCRAFT_ALERTS]
        if unknown:
            raise ValueError(f"unknown aircraft alert: {unknown}")
        for a in aircraft:
            self._heard[a] = t
        dropped = ""
        if request:
            if self._repeats(request, t):
                return {"voice": None, "voice_level": 0, "held": False, "dropped": f"same as aircraft: {request}"}
            if self._pending is None or level >= self._pending[1]:
                if self._pending is not None:
                    dropped = f"replaced: {self._pending[0]}"
                self._pending = (request, level, t)
        if self._pending is None:
            return {"voice": None, "voice_level": 0, "held": False, "dropped": dropped}
        key, lvl, t0 = self._pending
        limit = self.cfg.hold_warning_s if lvl >= 4 else self.cfg.hold_routine_s
        if t - t0 > limit:
            self._pending = None
            return {"voice": None, "voice_level": 0, "held": False, "dropped": f"stale: {key}"}
        levels = {AIRCRAFT_ALERTS[a][1] for a in aircraft}
        if self._repeats(key, t):
            self._pending = None
            return {"voice": None, "voice_level": 0, "held": False, "dropped": f"same as aircraft: {key}"}
        blocked = bool(levels) or (radio and lvl < 4)
        if blocked:
            if lvl < 4 and ("W" in levels or "C" in levels):
                self._pending = None          # a routine call is not worth keeping behind an alert
                return {"voice": None, "voice_level": 0, "held": False, "dropped": f"behind aircraft alert: {key}"}
            return {"voice": None, "voice_level": 0, "held": True, "dropped": dropped}
        self._pending = None
        return {"voice": key, "voice_level": lvl, "held": False, "dropped": dropped}
