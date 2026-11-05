"""Fault-injection demonstration: what the pilot sees for each latch state × injected sensor fault.

Each case gives the *physical* truth (canopy seated?, handle-equivalent position of each shoot bolt in mm) and the injected
faults (per-channel failure mode from :data:`aerokit.canopy.sensors.FAILURE_MODES`, a mis-rigged trip point, or lost
power). The case is run through the real :class:`aerokit.canopy.logic.CanopyAlertUnit` over a standard ground sequence
(power-up → parked → taxi → take-off power). The result records the annunciation at taxi and at take-off power, and
classifies it:

* ``correct``         — LOCKED shown only when truly locked, alert when not;
* ``fault shown``     — a sensor fault is annunciated (amber CANOPY SENS, green off), no false "locked";
* ``nuisance``        — a false "unlocked" alert on a correctly locked canopy;
* ``dark``            — the unit is off; green off, so the checklist item "green ON" fails (positive indication);
* ``MISSED``          — the canopy is not locked but the unit shows LOCKED. These are the residual cases; the "found by"
  column says which barrier is left.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from aerokit.canopy.logic import AlertLevel, CanopyAlertUnit, FlightInputs
from aerokit.canopy.mechanism import EXTRA_NG
from aerokit.canopy.sensors import Channel

__all__ = ["FaultCase", "CASES", "run_case", "run_all"]

BOLTS = ("bolt_front", "bolt_centre", "bolt_rear")
FULL, PARTIAL = EXTRA_NG.gap_locked_mm, EXTRA_NG.gap_partial_mm


@dataclass(frozen=True)
class FaultCase:
    key: str
    title: str
    seated: bool
    bolt_mm: tuple[float, float, float]
    failures: Mapping[str, str] = field(default_factory=dict)
    trip_mm: Mapping[str, float] = field(default_factory=dict)
    powered: bool = True
    found_by: str = ""

    @property
    def locked(self) -> bool:
        return self.seated and all(x >= 68.0 for x in self.bolt_mm)


NOM_TRIP = 68.0
OPEN = (0.0, 0.0, 0.0)
LOCK = (FULL, FULL, FULL)
PART = (62.0, 62.0, 62.0)

CASES: tuple[FaultCase, ...] = (
    FaultCase("ok_locked", "Locked, no fault", True, LOCK, found_by="—"),
    FaultCase("ok_partial", "Partial lock (handle released, not pulled aft)", True, PART, found_by="the alert"),
    FaultCase("rear_out", "Rear bolt not engaged (loose fitting)", True, (FULL, FULL, 62.0), found_by="the alert"),
    FaultCase("stuck_one", "Partial lock + front bolt sensor stuck ACTIVE", True, PART,
              failures={"bolt_front": "stuck_active"}, found_by="the alert (two other bolts); stuck sensor found at the next "
                                                                  "powered opening"),
    FaultCase("stuck_seat", "Partial lock + seated sensor stuck ACTIVE", True, PART, failures={"seated": "stuck_active"},
              found_by="the alert (bolt sensors)"),
    FaultCase("wire_break", "Locked + wire break on the centre bolt sensor", True, LOCK,
              failures={"bolt_centre": "open_circuit"}, found_by="self-check: amber SENS, defer INOP (ML.A.403)"),
    FaultCase("short", "Locked + short circuit on the seated sensor", True, LOCK, failures={"seated": "short_circuit"},
              found_by="self-check: amber SENS"),
    FaultCase("stuck_inactive", "Locked + rear bolt sensor stuck INACTIVE", True, LOCK,
              failures={"bolt_rear": "stuck_inactive"}, found_by="pilot sees handle at LOCK legend; maintenance"),
    FaultCase("late_rig", "Locked + rear bolt sensor rigged 3 mm too late", True, LOCK, trip_mm={"bolt_rear": 71.0},
              found_by="nuisance → ICA gauge test"),
    FaultCase("open_stuck", "Canopy open + centre bolt sensor stuck ACTIVE", False, OPEN,
              failures={"bolt_centre": "stuck_active"}, found_by="open-canopy plausibility check: SENS"),
    FaultCase("power_lost", "Locked + alert unit unpowered (CB out)", True, LOCK, powered=False,
              found_by="checklist 'green ON' fails"),
    FaultCase("misrig_all", "Partial lock + all three bolt sensors rigged 6 mm early (one wrong gauge)", True, PART,
              trip_mm={b: 62.0 for b in BOLTS}, found_by="only the pilot's handle check and the ICA gauge test"),
    FaultCase("one_bolt_stuck", "Rear bolt not engaged + rear bolt sensor stuck ACTIVE", True, (FULL, FULL, 62.0),
              failures={"bolt_rear": "stuck_active"}, found_by="only the pilot's handle check; ICA functional test"),
)
"""The demonstration set. Bolt positions in handle-equivalent mm (70 = full lock, 60 = spring-only partial lock)."""


def _readings(case: FaultCase) -> dict:
    chans = {n: Channel(n, case.failures.get(n)) for n in ("seated",) + BOLTS}
    out = {"seated": chans["seated"].read(case.seated)}
    for b, x in zip(BOLTS, case.bolt_mm):
        engaged = case.seated and x >= case.trip_mm.get(b, NOM_TRIP)
        out[b] = chans[b].read(engaged)
    return out


def _view(o) -> dict:
    return {"phase": o.phase.value, "level": o.level.name, "message": o.message, "green": o.green_locked,
            "voice": o.aural, "flashing": o.flashing}


def run_case(case: FaultCase) -> dict:
    """Run one case through the standard ground sequence; return taxi and take-off annunciation and the verdict."""
    u = CanopyAlertUnit()
    r = _readings(case)
    seq: Sequence[tuple[float, dict]] = ((0.0, {}), (4.0, {}), (10.0, {"engine_running": True, "throttle": 0.2}),
                                         (11.0, {"engine_running": True, "throttle": 0.2}),
                                         (20.0, {"engine_running": True, "throttle": 1.0}))
    outs = [u.step(FlightInputs(t=t, powered=case.powered, **kw), r) for t, kw in seq]
    taxi, to = _view(outs[3]), _view(outs[4])
    if not case.powered:
        verdict = "dark"
    elif to["green"] and not case.locked:
        verdict = "MISSED"
    elif to["message"] == "CANOPY SENS":
        verdict = "fault shown"
    elif case.locked and to["level"] != AlertLevel.NONE.name:
        verdict = "nuisance"
    else:
        verdict = "correct"
    return {"key": case.key, "title": case.title, "locked": case.locked, "taxi": taxi, "takeoff": to,
            "verdict": verdict, "found_by": case.found_by, "events": list(u.events)}


def run_all(cases: Sequence[FaultCase] = CASES) -> list[dict]:
    return [run_case(c) for c in cases]
