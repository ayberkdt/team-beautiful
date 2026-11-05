"""CPDLC uplinks as an alternate source for the advisory display.

A CPDLC uplink is already digital and structured, so it needs no speech recognition -- but it is still a clearance
the crew must accept (WILCO/UNABLE), it is for non-time-critical messages, and voice watch remains (SERA.8035; EUROCONTROL
2026 CPDLC practice, research notes C_EASA_SERA_EAR.md, C_EUROCONTROL_CPDLC_RecPractices_2026.md [D-ag]).

Only message elements whose identifiers the research agent read in the EUROCONTROL list of message sets supported by
European ANSPs are mapped (C_EUROCONTROL_WikiLink_MessageSets.md [D-ag]): UM20 CLIMB TO, UM74 PROCEED DIRECT TO,
UM117 CONTACT, UM190 FLY HEADING (UM157 CHECK STUCK MICROPHONE is a service message, not a clearance).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from aerokit.atc.clearance import Clearance, Instruction, frequency_is_valid

__all__ = ["Uplink", "UM", "uplink_to_clearance"]

UM = {20: "CLIMB TO", 74: "PROCEED DIRECT TO", 117: "CONTACT", 157: "CHECK STUCK MICROPHONE", 190: "FLY HEADING"}


@dataclass(frozen=True)
class Uplink:
    """One CPDLC uplink message element as received (already decoded from the datalink)."""

    um: int
    value: object                 # FL (int) for UM20, fix name for UM74, (unit, "MHz text") for UM117, deg for UM190
    callsign: str
    t_received: float
    msg_id: int


def uplink_to_clearance(u: Uplink, own_callsign: str) -> Clearance:
    """Map an uplink to the display's :class:`Clearance` (source 'CPDLC'). Values are checked like voice values;
    an unsupported element is kept as INFO text, never guessed."""
    if u.um not in UM:
        ins = Instruction("cpdlc", None, f"UM{u.um} (not mapped)", 1.0, "INFO", detail="element not in our table")
    elif u.um == 20:
        fl = int(cast(int, u.value))
        ok = 10 <= fl <= 660
        ins = Instruction("flight_level", fl if ok else None, f"CLIMB FL {fl:03d}", 1.0,
                          "CONFIRMED" if ok else "INVALID", qualifier="climb", detail="" if ok else "FL out of range")
    elif u.um == 74:
        ins = Instruction("direct", str(u.value).upper(), f"DCT {str(u.value).upper()}", 1.0, "CONFIRMED")
    elif u.um == 117:
        unit, mhz = cast("tuple[str, str]", u.value)
        ok, why = frequency_is_valid(mhz)
        ins = Instruction("frequency", mhz if ok else None, f"CONTACT {unit.upper()} {mhz}", 1.0,
                          "CONFIRMED" if ok else "INVALID", qualifier=unit.upper(), detail=why)
    elif u.um == 190:
        h = int(cast(int, u.value))
        ok = 1 <= h <= 360
        ins = Instruction("heading", h if ok else None, f"HDG {h:03d}", 1.0, "CONFIRMED" if ok else "INVALID",
                          detail="" if ok else "heading 001-360")
    else:
        ins = Instruction("service", u.um, UM[u.um], 1.0, "INFO")
    return Clearance(u.callsign, 1.0, u.callsign == own_callsign, (ins,), f"UM{u.um} {UM.get(u.um, '')} {u.value}",
                     source="CPDLC (datalink)", t_received=u.t_received, msg_id=u.msg_id)
