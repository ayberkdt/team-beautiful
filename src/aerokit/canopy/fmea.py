"""FMEA of the recommended installation (architecture A3: one seated sensor + one engagement sensor per shoot bolt,
self-checking outputs, fuselage-side mounting, green LOCKED + amber/red alert, voice).

Severity words follow the usual five failure-condition classes (no safety effect / minor / major / hazardous /
catastrophic); the class given to each row is our judgement [Y]. ``rate_key`` names the channel failure mode whose
per-flight probability the study script fills in from the cited rates (``None`` = not quantified).
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FmeaRow", "FMEA", "markdown_table"]


@dataclass(frozen=True)
class FmeaRow:
    item: str
    mode: str
    effect: str
    detection: str
    severity: str
    mitigation: str
    rate_key: str | None = None


FMEA: tuple[FmeaRow, ...] = (
    FmeaRow("Seated sensor", "stuck ACTIVE (reads seated)",
            "open canopy shown as CANOPY UNLOCKED instead of OPEN; lock protection unchanged (bolt sensors)",
            "functional test (ICA)", "no safety effect", "lock needs seated AND all bolts", "stuck_active"),
    FmeaRow("Seated sensor", "stuck INACTIVE",
            "bolts sensed while 'not seated' -> CANOPY SENS caution (nuisance)", "immediate (self-revealing)",
            "minor", "MEL/placard: system INOP, pilot handle check", "stuck_inactive"),
    FmeaRow("Any sensor", "open circuit / short", "invalid complementary code -> CANOPY SENS, green off",
            "immediate", "minor", "complementary outputs; fuselage-side harness only", "open"),
    FmeaRow("Bolt sensor", "stuck ACTIVE",
            "that bolt unmonitored: a single-bolt hazard there is missed; a partial lock is still caught by the "
            "other two bolts (common linkage tube)", "next powered opening (bolt sensed, canopy not seated) or "
            "functional test", "major (latent)", "three bolt sensors; plausibility check on every opening",
            "stuck_active"),
    FmeaRow("Bolt sensor", "stuck INACTIVE", "false CANOPY UNLOCKED (nuisance)", "immediate", "minor",
            "dispatch rule; fix before next flight", "stuck_inactive"),
    FmeaRow("Bolt sensor", "rigged to trip too early", "partial lock read as locked (missed alert)",
            "installation and annual go/no-go spacer test", "major (latent)",
            "rigging gauge in ICA; trip point set from tolerance study", None),
    FmeaRow("Bolt sensor", "rigged to trip too late", "full lock read as unlocked (false alarm)", "immediate",
            "minor", "tolerance study; re-rig", None),
    FmeaRow("Alert unit", "loss of power / CB open", "panel dark, green LOCKED off, no alert",
            "pilot checklist item 'CANOPY - LOCKED, green ON'", "minor", "positive-indication design", None),
    FmeaRow("Alert unit", "logic error shows LOCKED", "missed alert", "functional test (ICA)", "major (latent)",
            "simple hardware AND for the green lamp; no software needed", None),
    FmeaRow("Red lamp / LED", "fails dark", "warning not seen (voice still works)", "power-up lamp test",
            "minor", "two LEDs per legend; voice channel independent", None),
    FmeaRow("Voice / tone", "no audio (headset unplugged)", "warning only visual", "power-up tone test", "minor",
            "flashing red in primary field of view", None),
    FmeaRow("Installation", "part bridges canopy and fuselage", "could obstruct emergency opening / jettison",
            "ground test of emergency opening after installation", "catastrophic if it occurred",
            "nothing mounted across the split line; magnets passive in the frame", None),
    FmeaRow("Installation", "magnet near the standby compass", "compass deviation", "compass swing",
            "minor", "magnet position and size; DO-160 magnetic-effect test", None),
    FmeaRow("Pilot", "relies on the light, skips the handle check", "the old barrier weakens",
            "training / line checks", "major", "AFM supplement: handle check stays primary; system is "
                                                 "supplementary", None),
    FmeaRow("Pilot", "ignores alerts after nuisance alarms (cry wolf)", "true alert not acted on",
            "false-alarm monitoring in the event log", "major", "false-alarm budget; persistence filter", None),
)


def markdown_table(rows: tuple[FmeaRow, ...] = FMEA, probs: dict[str, float] | None = None) -> str:
    head = "| Item | Failure mode | Effect | Detection | Severity [Y] | Mitigation | P per flight |\n" \
           "|---|---|---|---|---|---|---|\n"
    body = []
    for r in rows:
        p = probs.get(r.rate_key) if probs and r.rate_key else None
        body.append(f"| {r.item} | {r.mode} | {r.effect} | {r.detection} | {r.severity} | {r.mitigation} | "
                    f"{'%.1e' % p if p is not None else '—'} |")
    return head + "\n".join(body) + "\n"
