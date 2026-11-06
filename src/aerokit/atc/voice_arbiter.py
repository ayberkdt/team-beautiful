"""One voice at a time: the PAR cue gives way to the aircraft's own alerts and to the radio.

Three rules [Y], from one aural alert at a time and "must not interfere with the alerting function" (AC 25.1322-1 8.b, 6.e(3)):

1. An aircraft alert is sounding: the cue is silent. A routine call is dropped. A level 4 call waits for the end of the alert.
2. A radio transmission is on: a routine call is dropped. A level 4 call does not wait.
3. The display is never held. Only the voice waits.

The cue ranks below every line of TSO-C151c Table 4-2, read in the FAA Human Factors General Guidance, Table 4.3.1. Same-meaning
filtering and hold timers are in ``03_Advionics/complex/``.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["AIRCRAFT_ALERTS", "VoiceArbiter"]

#: TSO-C151c Table 4-2: name -> (priority, level). W warning, C caution, I information.
AIRCRAFT_ALERTS: dict[str, tuple[int, str]] = {
    "REACTIVE WINDSHEAR": (1, "W"), "SINK RATE PULL UP": (2, "W"), "CLOSURE PULL UP": (3, "W"), "TERRAIN": (4, "W"),
    "V1": (5, "I"), "ENGINE FAIL": (6, "W"), "FLTA PULL UP": (7, "W"), "PWS WARNING": (8, "W"),
    "TERRAIN CAUTION": (9, "C"), "MINIMUMS": (10, "I"), "FLTA CAUTION": (11, "C"), "TOO LOW TERRAIN": (12, "C"),
    "PDA TOO LOW TERRAIN": (13, "C"), "ALTITUDE CALLOUT": (14, "I"), "TOO LOW GEAR": (15, "C"),
    "TOO LOW FLAPS": (16, "C"), "SINK RATE": (17, "C"), "DONT SINK": (18, "C"), "GLIDESLOPE": (19, "C"),
    "PWS CAUTION": (20, "C"), "APPROACHING MINIMUMS": (21, "I"), "BANK ANGLE": (22, "C"), "WINDSHEAR CAUTION": (23, "C"),
    "TCAS RA": (24, "W"), "TCAS TA": (25, "C")}


@dataclass
class VoiceArbiter:
    held: str | None = None           # a level 4 call waiting for an aircraft alert to end

    def step(self, request: str | None, level: int, aircraft: Sequence[str] = (), radio: bool = False) -> dict:
        """One frame. ``aircraft``: alerts sounding now. Returns the call to play now, if any."""
        unknown = [a for a in aircraft if a not in AIRCRAFT_ALERTS]
        if unknown:
            raise ValueError(f"unknown aircraft alert: {unknown}")
        if request and level >= 4:
            self.held = request
        if self.held:
            if aircraft:
                return {"voice": None, "voice_level": 0, "held": True, "dropped": ""}
            voice, self.held = self.held, None
            return {"voice": voice, "voice_level": 4, "held": False, "dropped": ""}
        if request and (aircraft or radio):
            return {"voice": None, "voice_level": 0, "held": False, "dropped": request}
        return {"voice": request, "voice_level": level if request else 0, "held": False, "dropped": ""}
