# Case 7 — Voice + surveillance correlation: readback/hearback check, callsign ↔ track

**Task wording that triggers it:** "readback / hearback", "callsign confusion", "wrong aircraft took the clearance",
"correlate the voice message with the radar track", "miscommunication". Sponsor angle: anchor speech in surveillance
(match the spoken callsign to a Mode S / ADS-B identity) — S_00_summary §3.

**Concept (5 lines)**
1. Both transmissions (clearance and readback) go through the recogniser; fields compared only where both are
   CONFIRMED — otherwise "unverifiable, check by ear", never an alarm.
2. A readback value heard confidently but invalid (squawk with an 8) also alerts.
3. Spoken callsign is matched against the callsigns surveillance says are present: exact, one near match, or
   AMBIGUOUS (several similar) — the system may confirm one candidate, never choose among several.
4. Similar callsigns in the picture are shown as a warning line on the panel.
5. Message to the jury: a low base rate makes false alarms dominate; that is a design input, not a footnote.

**Three numbers** (`outputs/result.md`, base rate 4 % of exchanges, A_HAAWAII_readback_SID2022)
- At 30 dB: **81 %** of real readback errors caught (n = 54), false alarms **6.1 %** of correct readbacks → only
  **33 %** of alerts are real.
- At 6 dB: **97 %** of exchanges unverifiable — the checker stays silent instead of guessing.
- Callsigns: BTL128 → BTL123 (one near match), BTL133 → **ambiguous** (BTL123 and BTL132 both near), XYZ999 unknown.

**What the jury wants to hear:** Pd/Pfa language for alerts; literature: HAAWAII 82 % detection at 67 % false alarms
in operations; controllers miss 7 of 19 readback errors (Cardosi 1994, C_Cardosi_1994_FAA_RD94_15); callsign boost
from surveillance 41.3 → 69.7 % (A_Nigmatulina2021).

**Risks / limits:** word-error model [Y]; errors injected as one wrong digit only; no timing/threading of real
dialogues; similarity measure is character-based (not phonetic).

**Mentor questions:** Ground (controller hearback) or cockpit (pilot)? Is surveillance identity available? What false
alarm rate is acceptable?

**Run:** `python 03_Advionics/cases/case_7_readback_correlation/run.py [--quick] [--set p_readback_error=0.013]`.
Reuses `clearance.readback_check / resolve_callsign / similar_callsigns`, `channel.degrade_words`.
