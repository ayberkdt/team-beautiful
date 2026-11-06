"""The canopy alert unit: sensor fusion, flight-phase state machine, annunciation and event log.

Design rules implemented (the reasons and sources are in ``02_EASA/docs/23_easa_canopy_retrofit.md``):

* **Closed is not locked.** The canopy state is LOCKED only if every *seated* sensor and every *bolt-engagement*
  sensor is ACTIVE. A handle-position sensor alone cannot be trusted: on the Extra NG the handle sits at 70 mm both
  when locked and when the canopy is open with the handles released (AAIB-28120 p. 9).
* **Never a false "locked".** Any invalid code or physically impossible combination (a bolt sensed in its fuselage
  lug while the canopy is not seated) gives UNKNOWN → amber "CANOPY SENS"; the green LOCKED light is off. At take-off
  power UNKNOWN is treated as not locked (red "CANOPY SENS"): found by the fault-injection demo (``faults.py``), where an
  open canopy with a stuck bolt sensor otherwise got only an amber caution at take-off.
* **Positive indication.** A green "CANOPY LOCKED" light is lit only in the LOCKED state, so loss of power or a dead
  unit (dark panel) can never look like "all is well" to a pilot whose checklist says "green light ON".
* **Alert by phase.** Parked: no nuisance for an open canopy. Taxi: amber caution if closed-but-unlocked. Take-off
  (throttle advanced or IAS rising on the ground) and airborne: red warning, flashing, repeating voice until acknowledged.
* **Persistence filter.** A state change must last ``persistence_s`` before it is believed (contact bounce / vibration).
* **Aural inhibit near rotation** for a *new* alert only: between ``aural_inhibit_low_kt`` on the take-off roll and
  ``aural_inhibit_after_airborne_s`` after lift-off the voice is deferred (the red light still shows); an alert that
  was already active before the roll keeps its voice — that is the alert meant to stop the take-off.
* **Event log** with time stamps (for maintenance and investigators): every state change, every in-flight unlock.

All thresholds are design choices [Y] and live in :class:`LogicConfig`.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum, IntEnum

from aerokit.canopy.sensors import Reading
from aerokit.references import cite

__all__ = ["Phase", "CanopyState", "AlertLevel", "FlightInputs", "LogicConfig", "AlertOutput", "canopy_state",
           "CanopyAlertUnit"]


class Phase(Enum):
    OFF = "off"
    SELF_TEST = "self-test"
    PARKED = "parked"          # powered, engine not running
    TAXI = "taxi"
    TAKEOFF = "take-off"       # on the ground with take-off power or accelerating
    AIRBORNE = "airborne"


class CanopyState(Enum):
    LOCKED = "locked"
    CLOSED_UNLOCKED = "closed, not locked"
    OPEN = "open"
    UNKNOWN = "unknown (sensor fault)"


class AlertLevel(IntEnum):
    NONE = 0
    ADVISORY = 1     # white/cyan text, no sound
    CAUTION = 2      # amber, single chime
    WARNING = 3      # red, flashing, repeating voice


@dataclass(frozen=True)
class FlightInputs:
    """What the unit reads from the aircraft each cycle (from the EFIS / engine monitor or own discrete inputs)."""

    t: float
    powered: bool = True
    engine_running: bool = False
    throttle: float = 0.0          # lever position 0..1 (a throttle micro-switch would do)
    ias_kt: float = 0.0
    ack: bool = False              # master warning / caution push-button


@dataclass(frozen=True)
class LogicConfig:
    self_test_s: float = 3.0
    takeoff_throttle: float = 0.6
    takeoff_ias_kt: float = 30.0
    airborne_ias_kt: float = 55.0
    airborne_confirm_s: float = 3.0
    landed_ias_kt: float = 30.0
    persistence_s: float = 0.5
    caution_chime_s: float = 1.0
    aural_inhibit_low_kt: float = 40.0
    aural_inhibit_after_airborne_s: float = 10.0
    taxi_open_allowed: bool = True


@dataclass(frozen=True)
class AlertOutput:
    t: float
    phase: Phase
    state: CanopyState
    level: AlertLevel
    message: str
    aural: bool
    flashing: bool
    green_locked: bool
    lamp_test: bool = False
    fault: str | None = None

    @property
    def recorder_locked(self) -> bool:
        """The discrete sent to the EFIS data recorder: True only when LOCKED was positively sensed."""
        return self.state is CanopyState.LOCKED and not self.lamp_test


@cite("aaib_2024_g_miil", "faa_2011_ac23_1309_1e",
      note="AAIB p. 9: handle at 70 mm both locked and open-released; AC 23.1309-1E 11.b: no misleading safe indication")
def canopy_state(readings: Mapping[str, Reading], seated: Sequence[str], bolts: Sequence[str]) \
        -> tuple[CanopyState, str | None]:
    """Fuse the channel readings into one canopy state (with the reason when UNKNOWN)."""
    names = list(seated) + list(bolts)
    missing = [n for n in names if n not in readings]
    if missing:
        return CanopyState.UNKNOWN, f"no reading from {', '.join(missing)}"
    bad = [n for n in names if readings[n] is Reading.FAULT]
    if bad:
        return CanopyState.UNKNOWN, f"invalid code on {', '.join(bad)}"
    s = [readings[n] is Reading.ACTIVE for n in seated]
    b = [readings[n] is Reading.ACTIVE for n in bolts]
    if s and any(s) and not all(s):
        return CanopyState.UNKNOWN, "seated sensors disagree"
    is_seated = all(s) if s else None
    if is_seated is False and any(b):
        return CanopyState.UNKNOWN, "bolt sensed in lug while canopy not seated"
    if is_seated is False:
        return CanopyState.OPEN, None
    if b and not all(b):
        return CanopyState.CLOSED_UNLOCKED, None
    if not b and not s:
        return CanopyState.UNKNOWN, "no sensors configured"
    return CanopyState.LOCKED, None          # NB: with no bolt sensors, "seated" is (wrongly) taken as locked


@dataclass
class CanopyAlertUnit:
    """Stateful alert unit; call :meth:`step` once per sample with the inputs and the channel readings."""

    seated: Sequence[str] = ("seated",)
    bolts: Sequence[str] = ("bolt_front", "bolt_centre", "bolt_rear")
    config: LogicConfig = field(default_factory=LogicConfig)
    events: list[tuple[float, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._t_power: float | None = None
        self._phase = Phase.OFF
        self._raw: CanopyState | None = None
        self._raw_since = 0.0
        self._filtered: CanopyState | None = None
        self._fault: str | None = None
        self._fast_since: float | None = None
        self._t_airborne: float | None = None
        self._alert: tuple[AlertLevel, str] | None = None
        self._alert_since = 0.0
        self._acked = False
        self._window_open: float | None = None

    def _log(self, t: float, text: str) -> None:
        self.events.append((t, text))

    def _update_phase(self, x: FlightInputs) -> Phase:
        c, prev = self.config, self._phase
        if self._t_power is None:                       # step() sets it before calling here
            raise RuntimeError("phase update before power-on")
        if x.t - self._t_power < c.self_test_s:
            return Phase.SELF_TEST
        if prev is Phase.SELF_TEST and x.ias_kt >= c.airborne_ias_kt:      # power restored in flight
            self._t_airborne = x.t
            return Phase.AIRBORNE
        if prev in (Phase.SELF_TEST, Phase.PARKED, Phase.TAXI):
            if x.engine_running and (x.throttle >= c.takeoff_throttle or x.ias_kt >= c.takeoff_ias_kt):
                self._fast_since = None
                return Phase.TAKEOFF
            return Phase.TAXI if x.engine_running else Phase.PARKED
        if prev is Phase.TAKEOFF:
            if x.ias_kt >= c.airborne_ias_kt:
                self._fast_since = x.t if self._fast_since is None else self._fast_since
                if x.t - self._fast_since >= c.airborne_confirm_s:
                    self._t_airborne = x.t
                    return Phase.AIRBORNE
                return Phase.TAKEOFF
            self._fast_since = None
            if x.throttle < c.takeoff_throttle and x.ias_kt < c.takeoff_ias_kt:
                return Phase.TAXI if x.engine_running else Phase.PARKED            # rejected take-off
            return Phase.TAKEOFF
        if prev is Phase.AIRBORNE and x.ias_kt < c.landed_ias_kt:
            return Phase.TAXI if x.engine_running else Phase.PARKED
        return prev

    def _classify(self, phase: Phase, state: CanopyState) -> tuple[AlertLevel, str]:
        c = self.config
        if state is CanopyState.LOCKED:
            return AlertLevel.NONE, ""
        if state is CanopyState.UNKNOWN:
            # unconfirmed is not locked: at take-off power a sensor fault is treated like "not locked" (red); in flight a
            # newly appearing fault on a canopy that was locked is most likely the sensor, so amber. A system deferred INOP
            # is switched off (CB pulled, panel dark) and the pilot relies on the handle check.
            if phase is Phase.TAKEOFF:
                return AlertLevel.WARNING, "CANOPY SENS"
            return AlertLevel.CAUTION, "CANOPY SENS"
        word = "CANOPY OPEN" if state is CanopyState.OPEN else "CANOPY UNLOCKED"
        if phase in (Phase.TAKEOFF, Phase.AIRBORNE):
            return AlertLevel.WARNING, word
        if phase is Phase.TAXI:
            if state is CanopyState.OPEN and c.taxi_open_allowed:
                return AlertLevel.ADVISORY, word
            return AlertLevel.CAUTION, word
        if phase is Phase.PARKED and state is CanopyState.CLOSED_UNLOCKED:
            return AlertLevel.ADVISORY, word
        return AlertLevel.NONE, ""

    def _inhibit_window(self, phase: Phase, x: FlightInputs) -> bool:
        c = self.config
        if phase is Phase.TAKEOFF and x.ias_kt >= c.aural_inhibit_low_kt:
            return True
        return phase is Phase.AIRBORNE and self._t_airborne is not None \
            and x.t - self._t_airborne < c.aural_inhibit_after_airborne_s

    def step(self, x: FlightInputs, readings: Mapping[str, Reading]) -> AlertOutput:
        c = self.config
        if not x.powered:
            if self._phase is not Phase.OFF:
                self._log(x.t, "power lost: unit off, panel dark (green LOCKED light off)")
            self._reset()
            return AlertOutput(x.t, Phase.OFF, CanopyState.UNKNOWN, AlertLevel.NONE, "", False, False, False)
        if self._t_power is None:
            self._t_power = x.t
            self._log(x.t, "power on: lamp and voice test")

        raw, fault = canopy_state(readings, self.seated, self.bolts)
        if raw is not self._raw:
            self._raw, self._raw_since = raw, x.t
        if self._filtered is None or (raw is not self._filtered and x.t - self._raw_since >= c.persistence_s):
            old = self._filtered
            self._filtered, self._fault = raw, fault
            if old is not None:
                self._log(x.t, f"canopy {old.value} -> {raw.value}" + (f" ({fault})" if fault else ""))
                if self._phase is Phase.AIRBORNE and old is CanopyState.LOCKED:
                    self._log(x.t, "IN-FLIGHT LOSS OF LOCK recorded")
        state = self._filtered

        phase = self._update_phase(x)
        if phase is not self._phase:
            self._log(x.t, f"phase {self._phase.value} -> {phase.value}")
            self._phase = phase
        if phase is Phase.SELF_TEST:
            return AlertOutput(x.t, phase, state, AlertLevel.WARNING, "TEST", True, False, True, lamp_test=True,
                               fault=self._fault)

        level, msg = self._classify(phase, state)
        alert = (level, msg) if level > AlertLevel.NONE else None
        if alert != self._alert:
            self._alert, self._alert_since, self._acked = alert, x.t, False
            if alert and level >= AlertLevel.CAUTION:
                self._log(x.t, f"{level.name} {msg} ({phase.value})")
        if alert and x.ack and level >= AlertLevel.CAUTION:
            if not self._acked:
                self._log(x.t, f"{msg} acknowledged")
            self._acked = True

        in_window = self._inhibit_window(phase, x)
        if not in_window:
            self._window_open = None
        elif self._window_open is None:
            self._window_open = x.t
        deferred = in_window and self._window_open is not None and self._alert_since >= self._window_open
        aural = flashing = False
        if level is AlertLevel.WARNING and not self._acked:
            flashing, aural = True, not deferred
        elif level is AlertLevel.CAUTION and not self._acked:
            aural = x.t - self._alert_since < c.caution_chime_s and not deferred
        return AlertOutput(x.t, phase, state, level, msg, aural, flashing, state is CanopyState.LOCKED,
                           fault=self._fault if state is CanopyState.UNKNOWN else None)
