# Case 2 — "If communication with the tower is lost": what reaches the display

**Task wording that triggers it:** "communication with the tower is lost", "radio failure", "degraded / interrupted
link", "7600", "backup channel", "fallback". Spoiler fit: "İletişim kesilirse", "Kule ile iletişim kesilirse".

**Concept (5 lines)**
1. Explicit comm-state machine NORMAL / DEGRADED / RX_LOST / TX_LOST / ALTERNATE_AVAILABLE / ALL_COMMS_LOST, each
   state only on evidence (silence alone is never a loss: no carrier ≥ 30 s **and** ≥ 2 unanswered calls).
2. TX_LOST evidence: ATC asks "if you read, squawk ident" twice while we hear the frequency (SERA.14083(b)(1)).
3. Alternates count only if independent (other bus, other antenna); CPDLC items shown with their source.
4. In loss states every item is STALE with its age; **nothing new appears without a received message; a lost message
   is never reconstructed** (not by ASR, not by AI) — `lostcomm.DISPLAY_POLICY` per state.
5. Reminder timeline from the applicable rule set (EU SERA.14083 2025 / ICAO-EUR legacy / US 91.185), the crew decides.

**Three numbers** (`outputs/result.md`)
- Carrier stops at 100 s → amber **"VHF: NO SIGNAL n s - CHECKING"** from that first second (old items tagged
  "NO SIGNAL - LAST RX n s"); loss declared **29 s** later (`silence_for_loss_s` 30 s, 2 unanswered calls [Y]);
  "VHF VOICE OK" shown without carrier: **0 s** (was 29 s before the NO_SIGNAL state; `--set no_signal_after_s=null`
  reproduces the old behaviour).
- **0** items shown that were not received; **0** non-STALE items in loss states (300 s scripted approach, all 6 states).
- EU SERA.14083 (from 1 May 2025): hold last speed/level **20 min**, land within **30 min** after ETA/EAT, squawk
  **7600 / 7601** (C_EASA_SERA_EAR, C_BCAA_ASIL_2025_02 [D-ag]); old ICAO-EUR text 7 min (C_AIP_Georgia_ENR18).

**What the jury wants to hear:** the ground side too — SMS-type monitoring already counts 7600 codes
(S_intersoft_sms_brochure); ATC checks the receiver with code change / IDENT; surveillance keeps the aircraft visible
when voice is gone (radar does not bring the voice back). Common-cause failures (same bus/antenna) are not redundancy.

**Risks / limits:** thresholds are [Y]; on a real radio the squelch is closed between transmissions, so "no
carrier" should come from receiver health (noise floor, AGC, self-test), not from squelch alone — otherwise NO SIGNAL
shows on every quiet frequency; rule sets differ by State (CH 7600 only, UK
unchanged); SERA text read through a summarising tool (check the EASA PDF before quoting).

**Mentor questions:** Total loss, one-way (RX/TX) or degraded but audible? Which alternates may we assume (VHF2,
CPDLC, SATCOM, phone)? Pilot display, controller display, or both? Which State's rules?

**Run:** `python 03_Advionics/cases/case_2_lost_comms/run.py [--set rule_set=ICAO_EUR_LEGACY] [--set silence_for_loss_s=20]`
· demo: `outputs/cockpit_demo.html` 88–252 s. Reuses `atc.commhealth`, `atc.lostcomm`, `atc.datalink`, `clearance`.
