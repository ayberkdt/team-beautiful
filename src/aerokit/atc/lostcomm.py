"""Radio-communication-failure (RCF) rule sets and the reminder timeline a cockpit aid may show.

The aid **reminds**, it never decides or flies: it lists the published steps of the rule set that applies to the
airspace, with the times they refer to, and marks every pilot decision as the pilot's (7600 vs 7601, VMC branch).
It never creates a clearance (SERA.14083(b)(3): no blind clearances unless the originator asks).

Rule sets are data with a source note for each value, because the rules differ by state (EU SERA 2025, the older
ICAO/EUR "7 minutes" text still in many AIPs, the US 14 CFR 91.185 which has no hold timer) — research note
``C_00_summary.md`` item 10: "must not hard-code one rule set". The applicable set must come from the AIP/NOTAMs.

Sources (research notes in ``prev_guess/03_Advionics/comms_kit_2026-11-05/research/``, read by the research agent [D-ag]):

* EU: ``C_EASA_SERA_EAR.md`` (SERA.14083(c)(2), (c)(4)(i), (iv), (vi), (c)(6)); applicable from 1 May 2025
  (``C_BCAA_ASIL_2025_02.md``).
* ICAO/EUR legacy: ``C_AIP_Georgia_ENR18.md`` (ENR 1.8 §3.3 b, f, h).
* US: ``C_14CFR_91_185.md`` (no fixed hold, highest of assigned / minimum IFR / expected altitude, EFC/ETA).
"""
from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["RuleSet", "RULE_SETS", "Milestone", "timeline", "squawk_guidance", "DISPLAY_POLICY", "display_policy"]


@dataclass(frozen=True)
class RuleSet:
    key: str
    title: str
    hold_min: float | None          # keep last assigned speed and level for this long (None: no fixed timer)
    hold_start: str                 # what starts the hold timer
    land_within_min: float | None   # land, if possible, within this many minutes after ETA / EAT
    descent_ref: str                # when descent begins
    squawks: tuple[str, ...]
    altitude_rule: str
    sources: dict[str, str] = field(default_factory=dict)


RULE_SETS: dict[str, RuleSet] = {
    "EU_SERA_2025": RuleSet(
        "EU_SERA_2025", "EU SERA.14083 (Reg. (EU) 2024/404, from 1 May 2025)", 20.0,
        "failing to make a required report, or setting 7600 / ADS-B emergency where a surveillance service is "
        "provided (SERA.14083(c)(4)(i))", 30.0,
        "the last received and acknowledged EAT; if none, the ETA (SERA.14083(c)(4)(iv))",
        ("7600", "7601"),
        "last assigned speed and level, or the minimum flight altitude if higher; then the filed flight plan",
        {"hold_min": "C_EASA_SERA_EAR (SERA.14083(c)(4)(i)) [D-ag]",
         "land_within_min": "C_EASA_SERA_EAR (SERA.14083(c)(4)(vi)) [D-ag]",
         "squawks": "C_EASA_SERA_EAR ((c)(2) 7600, (c)(6) 7601) [D-ag]",
         "applicability": "C_BCAA_ASIL_2025_02 [D-ag]"}),
    "ICAO_EUR_LEGACY": RuleSet(
        "ICAO_EUR_LEGACY", "ICAO EUR regional text as in AIP ENR 1.8 (pre-2025, '7 minutes')", 7.0,
        "the later of reaching the assigned level / minimum flight altitude and setting 7600 (route without "
        "compulsory reporting points)", 30.0, "the last acknowledged EAT, otherwise the ETA", ("7600",),
        "last assigned speed and level, or the minimum flight altitude if higher; then the filed flight plan",
        {"hold_min": "C_AIP_Georgia_ENR18 (§3.3 b) [D-ag]", "land_within_min": "C_AIP_Georgia_ENR18 (§3.3 h) [D-ag]"}),
    "US_14CFR_91_185": RuleSet(
        "US_14CFR_91_185", "US 14 CFR 91.185", None, "no fixed hold timer", None,
        "the EFC time; if none, the ETA (91.185(c)(3))", ("7600",),
        "highest of: last assigned, minimum IFR altitude for the segment, altitude ATC said to expect",
        {"hold_min": "C_14CFR_91_185: no fixed 7- or 20-minute hold [D-ag]",
         "squawks": "7600 is the general RCF code; 91.185 itself not checked for the code [Y]"}),
}


@dataclass(frozen=True)
class Milestone:
    t_min: float | None      # minutes after the trigger; None = not a fixed time
    text: str
    who: str                 # "crew decides", "reminder", "ATC"
    source: str


def timeline(rule: str | RuleSet, *, eat_min: float | None = None, eta_min: float | None = None) -> list[Milestone]:
    """Reminder milestones after the RCF trigger (t = 0). ``eat_min`` / ``eta_min`` are minutes after the trigger.

    Only times the rule set itself defines appear with a number; everything else is listed without a time.
    """
    r = RULE_SETS[rule] if isinstance(rule, str) else rule
    s = r.sources
    out = [Milestone(0.0, "Try the previous channel, another channel, other units, other aircraft; data link, "
                          "SATCOM voice, mobile phone", "crew", "C_EASA_SERA_EAR (SERA.14083(a)) [D-ag]"),
           Milestone(0.0, "Squawk " + " or ".join(r.squawks) + " — the pilot-in-command chooses", "crew decides",
                     s.get("squawks", "rule set")),
           Milestone(0.0, "Level/speed: " + r.altitude_rule, "reminder", s.get("hold_min", "rule set"))]
    if r.hold_min is not None:
        out.append(Milestone(r.hold_min, f"End of the {r.hold_min:g} min hold of last assigned speed and level "
                                         f"(timer starts at: {r.hold_start}); then the filed flight plan",
                             "reminder", s["hold_min"]))
    ref = eat_min if eat_min is not None else eta_min
    ref_name = "EAT" if eat_min is not None else "ETA" if eta_min is not None else None
    if ref is not None:
        out.append(Milestone(ref, f"Begin descent at the {ref_name} ({r.descent_ref})", "reminder", r.title))
        if r.land_within_min is not None:
            later = max(x for x in (eat_min, eta_min) if x is not None)
            out.append(Milestone(later + r.land_within_min,
                                 f"Land, if possible, within {r.land_within_min:g} min after the later of ETA/EAT",
                                 "reminder", s.get("land_within_min", r.title)))
    else:
        out.append(Milestone(None, f"Begin descent at {r.descent_ref} — no EAT/ETA entered", "reminder", r.title))
    return sorted(out, key=lambda m: (m.t_min is None, m.t_min or 0.0))


def squawk_guidance(rule: str, vmc: bool, ifr: bool, commander_continues_vmc: bool | None) -> dict:
    """What the aid may *suggest*. 7601 needs the commander's decision (C_BCAA_ASIL_2025_02); unknown -> ask."""
    r = RULE_SETS[rule]
    if "7601" not in r.squawks or not ifr or not vmc:
        return {"suggest": "7600", "decision": "none needed", "source": r.sources.get("squawks", r.title)}
    if commander_continues_vmc is None:
        return {"suggest": "7600 or 7601", "decision": "PILOT-IN-COMMAND: continue in VMC to the nearest suitable "
                                                         "aerodrome (7601) or not (7600)?",
                "source": r.sources["squawks"]}
    return {"suggest": "7601" if commander_continues_vmc else "7600", "decision": "taken by the pilot-in-command",
            "source": r.sources["squawks"]}


#: what may reach the cockpit display in each comm state (the "how does the signal reach the display" answer)
DISPLAY_POLICY: dict[str, dict[str, str]] = {
    "NORMAL": {"new_voice_items": "yes, with source, age and confidence tag", "old_items": "current",
               "never": "a value the recogniser was unsure of shown as a number"},
    "DEGRADED": {"new_voice_items": "yes, tagged UNCONFIRMED / LOW CONFIDENCE, unsure digits masked",
                 "old_items": "current", "never": "a masked digit completed from context"},
    "NO_SIGNAL": {"new_voice_items": "none (nothing heard for n s); banner 'VHF: NO SIGNAL n s - CHECKING' (amber)",
                  "old_items": "shown with 'NO SIGNAL - LAST RX n s' (newer calls may have been missed)",
                  "never": "'VHF VOICE OK' while nothing is heard; a declared loss before the evidence is in"},
    "RX_LOST": {"new_voice_items": "none (nothing is received)", "old_items": "STALE with age, reference only",
                "never": "a 'last' clearance presented as current; any reconstructed message"},
    "TX_LOST": {"new_voice_items": "yes (we still hear ATC), tagged; readback impossible -> crew uses IDENT/code "
                                   "change when ATC asks (SERA.14083(b)(1))",
                "old_items": "STALE (ATC cannot hear our readback)", "never": "an automatic transmission"},
    "ALTERNATE_AVAILABLE": {"new_voice_items": "none on the failed channel; items from the alternate shown with "
                                               "that source (e.g. CPDLC, non-time-critical)",
                            "old_items": "voice items STALE", "never": "an alternate on the failed bus/antenna "
                                                                      "counted as independent"},
    "ALL_COMMS_LOST": {"new_voice_items": "none", "old_items": "STALE + the rule-set reminders (timeline)",
                       "never": "a new instruction; a choice of the RCF branch for the crew"},
}


def display_policy(state: str) -> dict[str, str]:
    """Policy row for a comm state (KeyError for an unknown state)."""
    return DISPLAY_POLICY[state]
