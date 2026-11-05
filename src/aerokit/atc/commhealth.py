"""Communication-health monitor and the advisory display model that sits on top of it.

States (demo names, not a certified logic):

========================  =====================================================================================
NORMAL                    receiving ATC speech of good quality; our calls get answered
DEGRADED                  carrier present but SNR / recogniser confidence low, clipping or dropouts
RX_LOST                   we hear nobody (no carrier, no traffic) and our calls go unanswered
TX_LOST                   we hear ATC and others, but ATC does not hear us (repeated calls to us, "if you read",
                          our transmitter self-test fails)
ALTERNATE_AVAILABLE       primary VHF lost (RX or TX) but an *independent* authorised channel is up
ALL_COMMS_LOST            primary lost and no independent alternate
========================  =====================================================================================

Evidence, not guesses: silence alone never declares RX_LOST (a quiet frequency is normal); it needs unanswered
calls *and* no other traffic. Hysteresis: leaving a failure state needs ``recover_ticks`` good ticks.

The :class:`AdvisoryDisplay` enforces the central safety property of the whole concept: **the display can only show
clearances that were actually received** (each with its message id, source and time). In RX_LOST / ALL_COMMS_LOST
every item is marked STALE with its age; no new item can appear without a received message. The tests check this
with randomised input sequences.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from aerokit.atc.clearance import Clearance
from aerokit.references import cite

__all__ = ["States", "CommInputs", "AltLink", "CommHealthMonitor", "AdvisoryDisplay", "LOST_COMM_REMINDERS",
           "ALTERNATE_REMINDERS"]


class States:
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    RX_LOST = "RX_LOST"
    TX_LOST = "TX_LOST"
    ALTERNATE_AVAILABLE = "ALTERNATE_AVAILABLE"
    ALL_COMMS_LOST = "ALL_COMMS_LOST"
    ALL = (NORMAL, DEGRADED, RX_LOST, TX_LOST, ALTERNATE_AVAILABLE, ALL_COMMS_LOST)


@dataclass(frozen=True)
class AltLink:
    """An alternate channel: availability and the power bus / antenna it depends on (for common-cause checks)."""

    name: str                 # e.g. "VHF2", "CPDLC (VDL2)", "SATCOM voice"
    up: bool
    bus: str = "BUS2"
    antenna: str = "ANT2"
    authorised_for: str = "voice"   # "voice", "datalink (non-urgent)", ...


@dataclass(frozen=True)
class CommInputs:
    """One monitor tick (e.g. every second)."""

    t: float
    carrier: bool                         # squelch open on the ATC frequency
    snr_db: float | None = None           # estimated from audio (channel.measure_audio)
    asr_conf: float | None = None         # mean word confidence of the last transmission
    dropout_fraction: float = 0.0
    heard_traffic: bool = False           # any intelligible transmission (ATC or other aircraft) this tick
    atc_to_us: bool = False               # ATC transmission addressed to our callsign this tick
    atc_asks_if_read: bool = False        # "... if you read, squawk ident" / repeated calls
    we_transmitted: bool = False          # PTT used this tick
    tx_selftest_ok: bool = True           # sidetone / forward power / PTT discrete
    ptt_held_s: float = 0.0               # how long the push-to-talk has been keyed continuously
    primary_bus_ok: bool = True
    primary_bus: str = "BUS1"
    primary_antenna: str = "ANT1"
    alt_links: tuple[AltLink, ...] = ()


@cite("easa_sera_14083_2025", note="(b)(1): ATC checks the aircraft receiver with SSR code change / IDENT -> TX_LOST evidence")
@dataclass
class CommHealthMonitor:
    """Explicit state machine; :meth:`step` returns the new state and the reasons."""

    snr_degraded_db: float = 12.0
    conf_degraded: float = 0.6
    dropout_degraded: float = 0.15
    answer_timeout_s: float = 10.0
    unanswered_for_loss: int = 2
    silence_for_loss_s: float = 30.0
    recover_ticks: int = 3
    stuck_mic_s: float = 30.0             # [Y] PTT keyed longer than this = stuck microphone suspected
    state: str = States.NORMAL
    reasons: tuple[str, ...] = ()
    _pending_calls: list[float] = field(default_factory=list)
    _unanswered: int = 0
    _last_heard: float = 0.0
    _good: int = 0
    _if_read_count: int = 0
    history: list[tuple[float, str, tuple[str, ...]]] = field(default_factory=list)

    def step(self, x: CommInputs) -> str:
        why: list[str] = []
        # --- bookkeeping of our calls and ATC answers
        if x.we_transmitted:
            self._pending_calls.append(x.t)
        if x.atc_to_us and not x.atc_asks_if_read:
            self._pending_calls.clear()
            self._unanswered = 0
        expired = [c for c in self._pending_calls if x.t - c > self.answer_timeout_s]
        if expired:
            self._unanswered += len(expired)
            self._pending_calls = [c for c in self._pending_calls if x.t - c <= self.answer_timeout_s]
        if x.heard_traffic:
            self._last_heard = x.t
        if x.atc_asks_if_read:
            self._if_read_count += 1
        elif x.atc_to_us:
            self._if_read_count = 0          # ATC answered us normally: they hear us
        # --- primary channel assessment
        rx_lost = (not x.primary_bus_ok) or (
            not x.carrier and x.t - self._last_heard >= self.silence_for_loss_s
            and self._unanswered >= self.unanswered_for_loss)
        stuck = x.ptt_held_s > self.stuck_mic_s
        tx_lost = x.primary_bus_ok and (not x.tx_selftest_ok or stuck or (
            self._if_read_count >= 2 and x.t - self._last_heard < self.silence_for_loss_s))
        if stuck:
            why.append(f"PTT keyed {x.ptt_held_s:.0f} s: stuck microphone suspected -- it blocks the frequency "
                       "for everyone (CPDLC UM157 CHECK STUCK MICROPHONE exists for this)")
        degraded = x.carrier and (
            (x.snr_db is not None and x.snr_db < self.snr_degraded_db)
            or (x.asr_conf is not None and x.asr_conf < self.conf_degraded)
            or x.dropout_fraction > self.dropout_degraded)
        if not x.primary_bus_ok:
            why.append(f"primary radio bus {x.primary_bus} failed")
        if rx_lost and x.primary_bus_ok:
            why.append(f"no carrier/traffic for {x.t - self._last_heard:.0f} s and {self._unanswered} unanswered calls")
        if tx_lost and not stuck:
            why.append("transmitter self-test failed" if not x.tx_selftest_ok
                       else f"ATC asked 'if you read' {self._if_read_count} times while we hear the frequency")
        if degraded:
            why.append("low SNR / recogniser confidence / dropouts")
        # --- alternates must be independent of the failed primary
        alts_ok = [a for a in x.alt_links if a.up and (x.primary_bus_ok or a.bus != x.primary_bus)
                   and a.antenna != x.primary_antenna]
        common = [a.name for a in x.alt_links if a.up and not x.primary_bus_ok and a.bus == x.primary_bus]
        if common:
            why.append(f"not counted (shares failed bus {x.primary_bus}): {', '.join(common)}")
        if rx_lost or tx_lost:
            new = States.ALTERNATE_AVAILABLE if alts_ok else States.ALL_COMMS_LOST
            if alts_ok:
                why.append("alternate: " + ", ".join(a.name for a in alts_ok))
            if new == States.ALL_COMMS_LOST and not x.alt_links:
                new = States.RX_LOST if rx_lost and not tx_lost else (States.TX_LOST if tx_lost and not rx_lost
                                                                        else States.ALL_COMMS_LOST)
            self._good = 0
        elif degraded:
            new = States.DEGRADED
            self._good = 0
        else:
            self._good += 1
            failure = self.state in (States.RX_LOST, States.TX_LOST, States.ALL_COMMS_LOST,
                                     States.ALTERNATE_AVAILABLE, States.DEGRADED)
            new = self.state if failure and self._good < self.recover_ticks else States.NORMAL
            if new != States.NORMAL:
                why.append(f"recovering ({self._good}/{self.recover_ticks} good ticks)")
        self.state = new
        self.reasons = tuple(why)
        self.history.append((x.t, new, self.reasons))
        return new


#: reminders shown (as links to the official procedure, never as new instructions) when comms are lost
LOST_COMM_REMINDERS = (
    "Try the previous channel, another channel for the route, other ATS units/aircraft; data link, SATCOM voice",
    "Set Mode A 7600 (EU: 7601 if IFR, in VMC, and the commander decides to continue in VMC to the nearest aerodrome)",
    "Radio-failure procedure: SERA.14083(c) -- the crew applies it; this display does not choose a branch",
    "The last clearance shown is REFERENCE ONLY (see its age); nothing new appears without a received message",
)


def _t(c: Clearance) -> float:
    """Reception time of a displayed message (receive() guarantees it is set)."""
    return float(c.t_received if c.t_received is not None else 0.0)


#: shown when primary VHF is lost but an independent alternate is up
ALTERNATE_REMINDERS = (
    "Re-establish contact on the alternate; state that the assigned VHF channel failed (SERA.14083(a))",
    "CPDLC is for non-time-critical messages; time-critical instructions stay on voice (EUROCONTROL 2026 practice)",
    "Clearances arriving on the alternate are shown with that source; the old voice clearance stays STALE",
)


@cite("easa_sera_14083_2025", note="(b)(3) no blind clearances; (c)(2) 7600; the crew applies (c)")
@dataclass
class AdvisoryDisplay:
    """Display model: what the cockpit advisory panel may show, derived only from received messages."""

    stale_after_s: float = 120.0
    similar_callsigns: tuple[str, ...] = ()     # from the traffic picture (ADS-B In / TIS-B), see clearance.similar_callsigns
    received: list[Clearance] = field(default_factory=list)
    acknowledged: set[int] = field(default_factory=set)

    def receive(self, c: Clearance) -> None:
        if c.msg_id is None or c.t_received is None:
            raise ValueError("a displayable message needs msg_id and t_received")
        self.received.append(c)

    def acknowledge(self, msg_id: int) -> None:
        """Pilot confirms by ear / readback accepted -- the only way a value becomes 'PILOT CONFIRMED'."""
        if msg_id not in {c.msg_id for c in self.received}:
            raise KeyError(msg_id)
        self.acknowledged.add(msg_id)

    def view(self, t: float, state: str) -> dict:
        """Panel content at time ``t`` for comm state ``state``."""
        mine = [c for c in self.received if c.t_received is not None and c.t_received <= t
                and c.addressed_to_us is not False]
        others = [c for c in self.received if c.t_received is not None and c.t_received <= t
                  and c.addressed_to_us is False]
        last = mine[-1] if mine else None
        lost = state in (States.RX_LOST, States.ALL_COMMS_LOST, States.TX_LOST) or (
            state == States.ALTERNATE_AVAILABLE and last is not None and last.source.startswith("VHF"))
        items = []
        if last is not None:
            age = t - _t(last)
            for ins in last.instructions:
                if ins.status == "INFO":
                    continue
                shown = ins.display if ins.status in ("CONFIRMED", "NOT_RECEIVED") or "?" in ins.display \
                    else ins.display + " ?"
                tag = ins.status
                if ins.status == "CONFIRMED" and last.msg_id not in self.acknowledged and (
                        state == States.DEGRADED or last.partial):
                    tag = "UNCONFIRMED"
                if last.addressed_to_us is None and ins.status == "CONFIRMED":
                    tag = "CHECK CALLSIGN"
                if lost or age > self.stale_after_s:
                    tag = f"STALE {age:.0f} s"
                items.append({"msg_id": last.msg_id, "kind": ins.kind, "text": shown, "tag": tag,
                              "pilot_confirmed": last.msg_id in self.acknowledged,
                              "source": last.source, "t_received": last.t_received})
        banner = {States.NORMAL: "VHF VOICE OK", States.DEGRADED: "VHF DEGRADED - VERIFY BY EAR",
                  States.RX_LOST: "NO ATC RECEPTION - NO NEW CLEARANCES",
                  States.TX_LOST: "ATC NOT RECEIVING US", States.ALTERNATE_AVAILABLE: "PRIMARY VHF LOST - ALTERNATE UP",
                  States.ALL_COMMS_LOST: "ALL COMMS LOST"}[state]
        return {"t": t, "state": state, "banner": banner, "items": items,
                "last_rx_age_s": None if last is None else t - _t(last),
                "reminders": (list(LOST_COMM_REMINDERS) if state in (States.RX_LOST, States.ALL_COMMS_LOST)
                              else list(ALTERNATE_REMINDERS) if state == States.ALTERNATE_AVAILABLE else []),
                "partial": bool(last is not None and last.partial),
                "not_for_us": (None if not others else {"callsign": others[-1].callsign,
                                                        "age_s": t - _t(others[-1])}),
                "similar_callsigns": list(self.similar_callsigns),
                "advisory_only": True}

    def displayed_ids(self, t: float, state: str) -> set[int]:
        return {it["msg_id"] for it in self.view(t, state)["items"]}


def run_scenario(ticks: Sequence[CommInputs], messages: Mapping[float, Clearance] | None = None,
                 monitor: CommHealthMonitor | None = None) -> list[dict]:
    """Drive monitor + display through a scenario; ``messages`` maps tick time -> received clearance."""
    mon = monitor or CommHealthMonitor()
    disp = AdvisoryDisplay()
    out = []
    for x in ticks:
        st = mon.step(x)
        if messages and x.t in messages and x.carrier:     # no carrier -> nothing was received, nothing shown
            disp.receive(messages[x.t])
        v = disp.view(x.t, st)
        v["reasons"] = list(mon.reasons)
        out.append(v)
    return out


__all__ += ["run_scenario"]
