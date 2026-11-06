# EASA kit · 01 — Mentor answer → what we use (decision tree)

**5 Nov, official task received** (`02_EASA/official_2026-11-05/00_OFFICIAL_TASK_vs_KIT.md`). It already answers most rows:
- Q1 → **Q1-a**: the task is "reduce unlocked canopy events"; the bond/fatigue cause stays a one-line second barrier.
- Q2 → aircraft of our choosing, any canopy type: **Extra NG** (case-study aircraft) + kit `08` for "any aircraft".
- Q5 → **neither**: certification is to be disregarded. Design depth wins; the approval route is one real-world line.
- Q4 → engine shut-down is listed as an allowed feedback element: answered by kit `12` (ground-only take-off gate, in-flight
  shut-down rejected). Option C stays on the ladder.
- Still open: **Q6** (the "word list"), and whether a demo is wanted. Ask these two first.

Ask the mentor questions of `02_EASA/docs/23_easa_canopy_retrofit.md` §6 in this order: **1, 6, 2, 5, 4**. Each answer
below picks the kit pieces and the first 20 minutes. Numbers quoted here are the ones in doc 23; tags as there
([D] read at source, [K] computed by `canopy_day.py`, [Y] our assumption).

| # | If the mentor says … | Then the story is … | Use these pieces | First 20 min |
|---|---|---|---|---|
| Q1-a | "G-MIIL is only the motivation; design the latch alert" | Baseline story: *closed is not locked*, LOCK-SENSE (A3) | talk `02`, report `03`, figures C1–C6, K3/K4 figures | run `canopy_day.py`; open the report draft; split slides |
| Q1-b | "Address the structural cause (bond / fatigue) as well" | Two-layer answer: LOCK-SENSE for the lock hazard **plus** O5 bond NDT in the ICA (EASA is itself evaluating an NDT, SR 2024-004 response [D]) | report `03` §4 "second layer", ICA card `06` task T5, concept trade `11` (O5 row) | move O5 from "option" to "second deliverable"; one slide "two hazards, two barriers" |
| Q6-a | "The word list is a glossary we give you" | Map their words onto ours | `02_EASA/docs/glossary.md`, traceability `04` (requirement wording) | rename legends/requirements to their words; keep the CANOPY LOCKED / UNLOCKED / OPEN / SENS set |
| Q6-b | "The word list is the alert wording" | Alert wording is a design input | AFMS `05` §4–5, annunciator mock-up, requirement R-7/R-8 | replace legend strings in AFMS + mock-up; check one-word voice ("CANOPY") still fits |
| Q2-a | "Show a method for any aircraft" | The 12 steps are type-independent; the analysis scales with the number of latch points | other-aircraft piece `08`, process figure K3 | run `08` for the mentor's type (latch-point count, handle travel); swap the example in slide 1 |
| Q2-b | "Stay with Extra NG" | Baseline | — | — |
| Q5-a | "We want certification depth" | Approval route is the core | process figure K3, traceability `04` (regulation column), AFMS `05`, ICA `06` | slide 5 becomes two slides; drop the cry-wolf figure to backup |
| Q5-b | "We want design depth" | Sensor physics, rigging window, fault demo | C2, fault demo, BOM `07`, architecture figure K4 | slide 4 split into "sensing" + "logic"; the approval route goes to one line |
| Q4-a | "An interlock is acceptable" | Keep rejecting a *power* interlock (new hazard, major change) but offer option C, the **powered over-centre lock**: removes the omission itself, 7 100× / 6.1× [K] | concept trade `11`, doc 23 §3.3 | one backup slide "why not an interlock: C instead" |
| — | "No budget limit — be creative" (in the notes) | Show the ladder A3 → B → C → D with what each buys | concept trade `11`, doc 23 §3.3 | last slide = the ladder, A3 first because it can be approved as a minor change |
| — | "Build a demo / prototype" | The fault-injection demo is the prototype of the logic | `02_EASA/outputs/day/fault_demo.html`, annunciator mock-up | rehearse the 13-case demo; one person drives it during Q&A |

## Lines that do not change in any branch

1. **Never claim** the alert would have prevented G-MIIL. AAIB cause = bonding → fatigue [D]; BFU dissent = not
   completely locked [D]. A recorded lock state would have settled that dispute [Y].
2. The handle check stays the **primary** means; the green lamp is an independent second confirmation (AFMS `05`).
3. Every rate except the NUREG/CR-1278 omission base rate is [Y] and swept; say so before the jury asks (doc 23 §6b Q1).
