# R3 — Controller and pilot workload catalogue for an automatic PAR cue

Prepared 6 November 2026 for the Advionics challenge, case 10 (PAR hybrid cue). Educational concept only. Not approved or
ready for flight use.

**Tags.** `[D 6 Nov]` = read at source on 6 Nov 2026. `[A 6 Nov]` = search snippet only, source not opened. `[Y]` = my
inference. `[K]` = computed result taken from `cases/case_10_par_hybrid_cue/TECHNICAL.md`. Quotes are avoided; the words
in capitals are standard radio phrases.

**Limit of `[D]`.** PDFs (Doc 4444, JO 7110.65BB, RA 3291, MMATM, CAP 413, AIM 5-4-11, Sarter 2024, Burian 2013, Manning 2002,
Ellis 2009, Dehais 2012, ALAR 7.1, Episode 3, Helmke 2024) were read as extracted text, the relevant sections only. Web pages
(Wikipedia, FAS, SKYbrary, AeroSafety World, Flying, NTRS, DepositOnce, SlideShare) reached me through the fetch tool's
summary, so check any exact wording there before quoting it.

## Main findings

1. **The final controller does about 27 tasks, but only about 8 are the "radar to correction" chain.** The rest are checks,
   relays, limits and fault handling. Section 1 lists them. Our system can do 11 fully, 14 partly, and 2 not at all. [Y]
2. **The talk-down is a 5-second heartbeat, not only guidance.** ICAO says transmission should not stop for more than
   5 s on final `[D 6 Nov]` ([Doc 4444 8.9.7.2.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)). The FAA says about every 5 s, and it tells the pilot to treat 5 s of
   silence on a PAR final as lost communication `[D 6 Nov]` ([JO 7110.65BB 5-12-4, 5-10-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)). Case 10 has a median of 6 voice
   calls per approach [K]. So the pilot needs a live visual sign that guidance is alive, or silence means two things. [Y]
3. **Gear state, landing clearance and the decision at minimums do not exist in radar data.** For these the system can
   only prompt, relay, or stop. [Y]
4. **Rule and evidence gaps in case 10.** LOST at 5 s now has primary numbers (UK: tell the pilot after 3 s, `[D 6 Nov]` [RA 3291
   para 5](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). Guidance stops at minimums, but the rules continue advisory information to the threshold `[D 6 Nov]` ([Doc 4444
   8.9.7.2.7](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)). The limit is 2 dots each way, but the UK safety cursor is a lower limit from obstacle surfaces `[D 6 Nov]`
   ([RA 3291 para 26](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). See "Design consequences".
5. **The closest existing system is carrier ACLS Mode II.** Ship radar sends errors by data link to cockpit needles, and
   the pilot flies them `[D 6 Nov]` ([Wikipedia, carrier operations](https://en.wikipedia.org/wiki/Modern_United_States_Navy_carrier_air_operations)), `[A 6 Nov]` ([USNI Proceedings 1965](https://www.usni.org/magazines/proceedings/1965/july/all-weather-carrier-landing-system)). Do not claim that radar-to-needle is new. The voice
   and fault logic may be the contribution. [Y]
6. **I found no study that measures controller workload on a PAR final, no study comparing pilot workload on a talk-down
   and an ILS, and no automated talk-down experiment.** Sections 2, 3 and 5 say what stands in for them.

## 1. Task catalogue of the final controller

Sequence follows the approach. **Who now:** F = final (talkdown) controller; D = director or approach controller; T = tower.
**Class:** P = perception, J = judgement, C = communication. **Our system:** yes, partly, no, for an uplinked cue with no
tower link and no gear data. These calls are mine [Y], built on the sources in the last column. Rates at 140 kt groundspeed
are my assumption.

**Only 11 of 27 tasks can be fully automated from radar data; the rest need pilot input, tower input or pilot judgement.**
Source tags in this table mean read on 6 Nov 2026.

| Task | Who now | Input | Output | Rate | Class | Our system | Stays with pilot | Source |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| T1 Accept handover, identify | F, from D | Correlated track in azimuth and elevation, data block | Takes control | Once, at least 1 NM before glidepath intercept; UK figure shows 7 to 8 NM | P | partly | Confirm the cue is for own aircraft | [Doc 4444 8.9.7.2.2](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [RA 3291 para 16](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [MMATM fig. 2](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/835083/MMATM_Issue_12.pdf) |
| T2 Radio check, no-reply instruction | F | Pilot's voice | HOW DO YOU HEAR ME, DO NOT ACKNOWLEDGE | Once | C | partly | Confirm cue is live; link handshake replaces voice | [7110.65BB 5-10-9, 5-10-10](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [Doc 4444 8.9.7.2.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T3 Approach data | D or F | Runway, OCA/H, glidepath angle, altimeter, DH, lost-comm and missed approach procedure | Briefing, altimeter readback | Once; about 1 call per min in this phase (FAA) | C | partly | Set altimeter, enter DH, judge minima | [Doc 4444 8.9.6.1.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-10-1, 5-10-2, 5-10-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 para 1b, 1c](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T4 Monitor lateral deviation | F | Azimuth display, 2 and 5 degree lines, track trail | Position word: on, slightly, left/right, well | Continuous; spoken inside the 5 s stream | P | yes | Cross-check own heading | [RA 3291 para 24](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [Doc 4444 8.9.7.2.4.1](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T5 Monitor vertical deviation | F | Elevation display, data block height, glidepath cursor | Slightly within 60 ft; above/below 61 to 100 ft; well over 100 ft | Continuous | P | yes | Cross-check altimeter against range | [RA 3291 para 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [Doc 4444 8.9.7.2.5.1](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T6 Predict drift, give trend | F | Track history trail over time | RAPIDLY, SLOWLY; UK adds nicely, not correcting | As required | J | partly | Own vertical speed and heading trend | [7110.65BB 5-12-4b](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 paras 24, 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [TECHNICAL s.2](../cases/case_10_par_hybrid_cue/TECHNICAL.md) |
| T7 Choose heading | F | Position, trail, range, drift (wind is inferred, radar shows none) | HEADING (number) or turn | As needed; pilot turns only when told | J | yes | Fly it, or refuse it | [Doc 4444 8.9.7.2.4](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [RA 3291 paras 22, 24](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T8 Call glidepath | F | Elevation trend, range | Position, trend, ADJUST RATE OF DESCENT if pilot's action seems too small | Regular, also when on path; feet above/below inside 2 NM | J, C | yes | Choose pitch and power; pilot corrects from information alone | [Doc 4444 8.9.7.2.5.1 to .3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [Doc 4444 12.4.2.5.4](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T9 Glidepath intercept, start descent | F | Range, height, aircraft type | APPROACHING GLIDEPATH, BEGIN DESCENT | Once; 10 to 30 s before descent; UK 200 ft below path | J, C | yes | Start descent, check DH | [7110.65BB 5-12-1, 5-12-3](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 para 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T10 Range calls | F | Range lines or data block | (Number) MILES FROM TOUCHDOWN | ICAO every 1 NM to 4 NM, then more often. FAA each mile. UK each 1/2 NM inside 15 NM | C | yes | Cross-check height for range | [Doc 4444 8.9.7.2.6](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-12-5](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 para 19](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T11 Keep the 5 s stream | F | Clock, own speech | Unbroken guidance; transmitter unkeyed at times | Gap under 5 s (ICAO); about every 5 s (FAA) | C | partly | Treat lost cue as lost guidance | [Doc 4444 8.9.7.2.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-12-4, 5-10-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T12 Gear check | F (D: landing check in USA/USN) | Pilot's reply; radar cannot show gear [Y] | CHECK GEAR DOWN, acknowledge | Once, before clearance | C | partly | Check and confirm gear | [Doc 4444 8.9.6.1.5](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [RA 3291 para 1d](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [CAP 413 ch. 10](https://www.caa.co.uk/publication/download/18165) |
| T13 Coordinate with tower | F with T | Clearance line, range | Notify at about 8 NM, again at 4 NM; get clearance | 1 to 2 times | C | no | Know clearance state | [Doc 4444 8.9.6.1.6](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [RA 3291 para 1e](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T14 Relay clearance and wind | F | Tower's words | Clearance verbatim, surface wind; pilot acknowledges | Once, before 2 NM | C | partly | Acknowledge; needs tower input | [Doc 4444 8.9.6.1.7](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-10-13](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 para 1e](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T15 No clearance by 2 NM | F | Range, clearance state | Break off approach | Event | J | partly | Execute missed approach | [Doc 4444 8.9.6.1.8a](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [RA 3291 para 1e(4)](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T16 Safety limits | F | Lower safe limit cursor set by engineers from obstacle surface | DANGEROUSLY BELOW GLIDEPATH, acknowledge | Event; priority over other deviation calls | P, J | yes | Correct at once | [RA 3291 paras 25 to 27](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [7110.65BB 5-10-14a](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T17 Wave-off, missed approach | F or T | Position, doubt, traffic, tower order | Directed: dangerous position, traffic, no clearance, tower order. Advised: bad outcome likely, target lost, doubt. Reason given | Event | J, C | partly | Go-around decision and flying; runway in sight exception | [Doc 4444 8.9.6.1.8, .9](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-10-14](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T18 Spot pilot going around | F | Elevation trend | Over 2 NM: ask. Inside: keep calling, then missed approach instructions | Event | J | partly | Say what you are doing | [Doc 4444 8.9.7.2.8](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T19 Decision height call | F | DH cursor, target | Approaching, then at or passing DH | Twice at most | P, C | yes | Land or go around | [7110.65BB 5-12-6](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 para 1f](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T20 Advisory to threshold | F | Displays below DH | Direction and degrees only; OVER APPROACH LIGHTS, OVER THRESHOLD | To threshold; UK glidepath to 50 ft below minimum | C | partly | Land visually; advisory only | [Doc 4444 8.9.7.2.7](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-12-7](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf); [RA 3291 paras 24, 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T21 Radar check | F | Built-in test alerts, audio alarm, range scale, rain mode | Decide if radar is fit; report | Continuous; each alert | P, J | yes | None; sees validity state | [RA 3291 paras 1a, 3, 13, 33](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| T22 Contact lost or radar fault | F | Lost track, alert | Tell pilot after 3 s. Inside 4 NM treat as failure. Elevation failure: tell at once, azimuth-only or missed | Event | J, C | yes | Continue visually or go around | [RA 3291 paras 4 to 7](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [Doc 4444 8.9.7.2.5.4](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [7110.65BB 5-12-10](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T23 Identity in doubt | F | Track merge, data block jump, formation split | Continue if trail matches; else terminate | Event | P, J | partly | Report anything odd | [RA 3291 paras 10, 21, 23, 31](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [7110.65BB 5-10-14b](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T24 Traffic | F, D | Other contacts in both pictures | Information or avoiding advice; stop descent or climb | Event | J | no | See and avoid, own traffic systems | [RA 3291 paras 11, 32](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [Doc 4444 8.9.6.1.8a](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T25 Manage pilot's load | F | Pilot's response, late handover | Stagger corrections, set priorities, use emphasis | Continuous | J | partly | Say if unable | [RA 3291 paras 28, 30](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [Doc 4444 8.9.7.2.5.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| T26 End guidance on pilot's request | F | Pilot's call, controller's opinion | PROCEED VISUALLY | Event | J, C | partly | Decide to go visual; a button replaces the call, no controller opinion | [7110.65BB 5-12-8](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| T27 Close out | F | Landing, or end of approach | Tell D talkdown free; transfer after rollout | Once per aircraft | C | yes | Change frequency | [RA 3291 para 8](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [7110.65BB 5-12-9](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |

### Numbers that follow from the rates [Y]

- At 140 kt, 5 NM takes 129 s and 8 NM takes 206 s. At one transmission per 5 s, this gives about 26 and about 41
  transmissions. Case 10 has a median of 6 voice calls [K].
- Range calls over the last 8 NM: 8 under the FAA rule, 16 under the UK half-mile rule.
- Rates differ between authorities. Use "every mile" as the floor and do not call it universal.
- The FAA 5 s lost-communication instruction need not be sent to military aircraft at US Army and USAF sites `[D 6 Nov]`
  ([5-10-4 note](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)). The 5 s rate of transmission still applies.

### What the task list leaves out

- Exact USAF and US Navy text. AFMAN 13-204 V3 and NAVAIR 00-80T-114 were not readable. The US Navy manual has a section
  on PAR approach tolerances `[A 6 Nov]` ([search result, mirror](https://dokumen.tips/documents/navair-00-80t-114-natops-air-traffic.html)). I therefore have no number for FAA or Navy
  safety limits. JO 7110.65BB names safety limits but gives no value in the sections I read `[D 6 Nov]` ([5-10-14](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)).
- Local orders. RA 3291 leaves the clearance range and more to unit orders `[D 6 Nov]` ([para 1e](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)).
- RA 3291 describes one UK radar type: its range scales and alerts are equipment rules, not general PAR rules. [Y]

## 2. Controller workload evidence

### No direct measurement found

I found no ISA, NASA-TLX or communications-load study of a PAR final controller. Three searches returned none. The
evidence below is indirect.

| Evidence | Finding | Tag |
|---|---|---|
| Duty rule | During a precision approach the controller should have no other duty | `[D 6 Nov]` [Doc 4444 8.9.7.2.1, 8.9.6.1.1](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| Traffic flow protects the final controller | Director may stretch the pattern to keep spacing and stop the Talkdown Controller being overloaded | `[D 6 Nov]` [MMATM ch. 3 para 6](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/835083/MMATM_Issue_12.pdf) |
| One-at-a-time signal | Controller tells Director "Talkdown free" when the PAR ends | `[D 6 Nov]` [RA 3291 para 8](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Late handover | Both workloads rise; control comes first, administration after | `[D 6 Nov]` [RA 3291 para 30](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Staffing claim | Wikipedia says one GCA controller per aircraft on final, and this cost ended civil use. No citation given. "Max 2" is tagged citation needed | `[D 6 Nov]` [Wikipedia GCA](https://en.wikipedia.org/wiki/Ground-controlled_approach) |
| Carrier radar | Two antennas allow two aircraft in a leapfrog pattern | `[D 6 Nov]` [FAS AN/SPN-46](https://man.fas.org/dod-101/sys/ship/weaps/an-spn-46.htm) |

### Why the talk-down needs one controller per aircraft

No rule I read states the number. This reasoning is mine [Y], from the facts above:

- The FAA rate is one transmission about every 5 s `[D 6 Nov]` ([5-12-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)). An en route study measured a mean controller
  transmission of 3.38 s `[D 6 Nov]` ([Manning et al. 2002](https://rosap.ntl.bts.gov/view/dot/57932/dot_57932_DS1.pdf)). En route is not PAR, so treat the figure as a rough value.
- 3.38 s in every 5 s is about 68 % talk time, against 16 % measured en route (38.3 s in 240 s) `[D 6 Nov]`.
- Two aircraft would need one call every 2.5 s, shorter than the mean call. Two aircraft on one frequency cannot fit.
- The display task also has no slack: the controller reads two pictures and a trail, and speaks the result at once.

This one-to-one limit is the strongest case for automation: capacity, not only accuracy. The task text does not ask for
this, so use it as a supporting point only. [Y]

### Workload measures used in ATC

| Measure | What it is | Use for this team | Tag |
|---|---|---|---|
| ISA | 1 to 5 rating given during the task | Quick, low intrusion | `[A 6 Nov]` [Eurocontrol Dublin TMA simulation](https://www.eurocontrol.int/sites/default/files/library/020_Dublin_TMA_real_time_simulation.pdf); [NASA primer](https://matb-files.larc.nasa.gov/Workload_Primer_TM_Final.pdf) |
| NASA-TLX | Six-part rating after the task | Used with ISA in Eurocontrol trials | `[A 6 Nov]` [EATCHIP evaluation](https://www.eurocontrol.int/sites/default/files/library/027_EATCHIP_III_Evaluation_and_Demonstration_Phase_3A.pdf) |
| ATWIT | One of seven buttons, prompted every 4 min | Predicted well by traffic activity | `[D 6 Nov]` [Manning et al. 2002](https://rosap.ntl.bts.gov/view/dot/57932/dot_57932_DS1.pdf) |
| Communications load | Count and duration of calls | 25 events and 69 s per 4 min, or 29 % of time, en route | `[D 6 Nov]` [Manning et al. 2002](https://rosap.ntl.bts.gov/view/dot/57932/dot_57932_DS1.pdf) |

Manning et al. found the activity component alone gave R² = .65 against .77 for the full model. Removing it left R² = .02.
Communications added little beyond activity `[D 6 Nov]`. The study used 16 experts rating 8 en route samples, so it is not
approach data.

### Job task analyses

- Episode 3 D2.4.4-05 covers en route, TMA and tower tasks in nominal conditions `[D 6 Nov]` ([Eurocontrol 2007](https://www.eurocontrol.int/sites/default/files/library/E3-WP2-D2.4.4-05-REP-V1.01-today-analysis.pdf)). It has no
  PAR position. Its tower arrivals tasks include monitoring the approach radar, checking final separation and landing
  clearance.
- Eurocontrol's literature review lists the general tasks: observing aircraft, operating displays, data entry, updating
  flight data, communicating `[D 6 Nov]` ([Cognitive complexity review](https://www.eurocontrol.int/sites/default/files/library/007_Cognitive_Complexity_in_ATC.pdf)).
- FAA en route task list (Ammerman, AM-93-1) and the 1988 CTA study: citation only `[A 6 Nov]` ([FAA AM-93-1](https://www.faa.gov/sites/faa.gov/files/data_research/research/med_humanfacs/oamtechreports/AM93-01.pdf)).
- Eurocontrol Integrated Task and Job Analysis, phase 3: citation only `[A 6 Nov]` ([2020 review](https://econtent.hogrefe.com/doi/10.1027/2192-0923/a000218)).
- None of these covers PAR. RA 3291, Doc 4444 and JO 7110.65 are therefore the task source in Section 1. [Y]

## 3. Pilot workload on a low-visibility approach

### Phase by phase

| Phase | Pilot's work | Evidence | Tag |
|---|---|---|---|
| Before final | Set altimeter, read back, give DH, run checks; controller starts checks on a radar approach | Military procedure | `[D 6 Nov]` [RA 3291 para 1](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf); [MMATM ch. 3 para 5](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/835083/MMATM_Issue_12.pdf) |
| Final, in cloud, manual | Fly attitude. PF spends over 50 % of dwell time on the attitude indicator | 17 B737 crews, Jarvis 2017, read through Sarter | `[D 6 Nov]` [Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf) |
| Final, coupled | Attitude dwell falls, HSI dwell more than doubles; mode annunciators get more looks | Same | `[D 6 Nov]` [Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf) |
| 1000 ft in IMC | Must be stabilised, or go around | ALAR 7.1 | `[D 6 Nov]` [FSF ALAR 7.1](https://flightsafety.org/wp-content/uploads/2016/09/alar_bn7-1stablizedappr.pdf) |
| Near minimums | Outside view rises. In one study, PM reached 35 % outside below 500 ft, away from flight parameters | Reynal 2016, 8 crews | `[D 6 Nov]` [Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf) |
| Decision height | Land or go around, on what the pilot sees | Pilot's own duty; guidance below DH is advisory | `[D 6 Nov]` [JO 7110.65BB 5-12-7](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| Landing | Heart rate peak 88.6 bpm at landing, 83.2 at take-off | In-flight study, snippet only | `[A 6 Nov]` [PubMed 14556571](https://pubmed.ncbi.nlm.nih.gov/14556571/) |
| Go-around at 200 ft | Outside view under 5 % against 40 % on final. PF 70 % on three PFD areas. Only 3 of 12 crews read back the full ATC instruction. PMs felt overwhelmed | Dehais 2017, read through Sarter | `[D 6 Nov]` [Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf) |

### Comparison: talk-down, raw data, flight director, autopilot

- **Talk-down against ILS: no study found.** One search for this comparison returned background only. Any workload
  claim for a talk-down is inference. [Y]
- **Flight director against manual:** in a 737 simulator, 12 pilots rated Bedford workload at each waypoint. Workload
  rose with less automation (F(2,136) about 16.3, p < .001). Full automation differed from both other conditions. Flight
  director and manual did not differ significantly (t = 1.006) `[D 6 Nov]` ([Ellis and Schnell 2009](https://ntrs.nasa.gov/api/citations/20100012851/downloads/20100012851.pdf)). The paper's "manual"
  condition had raw deviation indicators. Only the coupled condition reduced rated workload there. The scanned copy
  gives no readable condition means.
- **Scan:** mean saccade length was longer with full automation, so eyes roamed more `[D 6 Nov]` ([Ellis and Schnell 2009](https://ntrs.nasa.gov/api/citations/20100012851/downloads/20100012851.pdf)).
  In Spady's 1978 study of 7 pilots, looks at the flight director were 73 % manual and 52 % coupled, with mean dwell 1.6 s
  and 0.8 s `[D 6 Nov]` ([Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf)).
- **Head-down time:** no figure for a talk-down. In Sarter et al. 2007, 20 B747-400 pilots on automated flight looked outside
  3 % of the time until final approach, then 12 %; the PFD took 31 % and the navigation display 25 % `[D 6 Nov]` ([Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf)).
- **Scales seen:** Bedford (1 to 10) `[D 6 Nov]` ([Ellis and Schnell 2009](https://ntrs.nasa.gov/api/citations/20100012851/downloads/20100012851.pdf)); ISA and NASA-TLX for single-pilot jets `[D 6 Nov]` ([Burian
  et al. 2013](https://libraryonline.erau.edu/online-full-text/faa-aviation-medicine-reports/AM13-17.pdf)); a Modified Bedford for instrument approaches `[A 6 Nov]` ([NASA primer](https://matb-files.larc.nasa.gov/Workload_Primer_TM_Final.pdf)).
- **What this means for us [Y]:** a cue does not remove the pilot's flying task. A better display alone may not lower rated
  workload. Claim "less interpretation and more warning", not "lower workload", until a pilot trial shows it.
- **Talk-down in principle [Y]:** the pilot does no deviation estimate, because the controller does it. The pilot holds
  headings and adjusts sink, and scans attitude, heading and vertical speed. The cost is a constant audio stream and
  no picture of what comes next. A hybrid should keep the first and remove the second.

### Under high workload

- **Auditory alerts are missed.** 8 of 14 pilots (57.1 %) reported no critical landing gear alarm during a landing with
  windshear; all but one of those 8 failed to go around correctly `[D 6 Nov]` ([Dehais et al. 2012](https://openscience.isae-supaero.fr/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?parentDocumentId=8060&documentId=12857&skipWatermark=true&skipCopyright=true)). 11 of 28 (39.3 %)
  in a later study `[A 6 Nov]` ([Dehais et al. 2014](https://journals.sagepub.com/doi/abs/10.1177/0018720813510735)). So voice alone is not safe for a critical warning. [Y]
- **Working memory drops.** The 3 of 12 readback result above.
- **Scan narrows.** Pilots with large deviations showed a mostly attitude-based scan `[A 6 Nov]` ([search summary, eye-tracking
  studies](https://www.researchgate.net/publication/316078684_I_spy_with_my_little_eye_Analysis_of_airline_pilots'_gaze_patterns_in_a_manual_instrument_flight_scenario)).
- **Tasks get front-loaded or delayed.** Single-pilot jet participants did tasks early and asked for vectors to buy time;
  errors included readback errors `[D 6 Nov]` ([Burian et al. 2013](https://libraryonline.erau.edu/online-full-text/faa-aviation-medicine-reports/AM13-17.pdf)).
- **Continuation.** Crews go around in only about 3 % of unstable approaches. Unstable approaches were a causal factor in
  66 % of 76 accidents and serious incidents `[D 6 Nov]` ([AeroSafety World 2019](https://flightsafety.org/asw-article/unstable-2/)). The cue must not depend on a pilot's
  self-initiated go-around being automatic. [Y]

### How pilots use radio calls on approach

- On a PAR final the pilot does not reply. The controller checks the channel, then says no acknowledgement is needed
  `[D 6 Nov]` ([Doc 4444 8.9.7.2.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); [JO 7110.65BB 5-10-10](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)). ICAO notes replies may be impracticable late on final
  `[D 6 Nov]` ([Doc 4444 ch. 9 note](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)).
- Exceptions need a reply: gear, clearance, and "dangerously below" `[D 6 Nov]` ([CAP 413 ch. 10](https://www.caa.co.uk/publication/download/18165); [RA 3291 para 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)).
- Azimuth and elevation work differently. The pilot corrects heading only when told, and corrects glidepath from the
  information alone `[D 6 Nov]` ([Doc 4444 8.9.7.2.4.2, 8.9.7.2.5.2](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)).
- Controllers delay non-urgent calls near touchdown so the pilot is not distracted `[D 6 Nov]` ([JO 7110.65BB 5-12-9 note](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)).
- Message length matters. Miscommunication was 1 to 3 % for 1 to 4 items and 8 % for 5 or more, en route `[A 6 Nov]` ([search
  summary, FAA reports](https://apps.dtic.mil/sti/tr/pdf/ADA494551.pdf)). Faster speech more than doubled errors in a lab study `[A 6 Nov]` (same search).

### Sterile cockpit, crew roles, and who receives the call

- **Sterile flight deck.** Only essential activity in critical phases. FAA: all flight below 10,000 ft except cruise.
  EU-OPS covers take-off, initial climb, final approach and landing. Military transport uses a similar rule `[D 6 Nov]` ([SKYbrary
  sterile flight deck](https://skybrary.aero/articles/sterile-flight-deck)). I read SKYbrary, not the 14 CFR 121.542 text. Guidance calls are essential, so the rule
  does not ban them. Non-essential system chatter would break its intent. [Y]
- **Two crew.** PF flies, PM monitors and backs up. PM makes a call if a parameter exceeds limits `[D 6 Nov]` ([FSF ALAR 7.1](https://flightsafety.org/wp-content/uploads/2016/09/alar_bn7-1stablizedappr.pdf)).
  ALAR also warns of PF and PM relying on each other too much `[D 6 Nov]`. PF and PM spread attention over different instruments in
  a go-around `[D 6 Nov]` ([Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf)).
- **Who takes a talk-down call in two crew:** no source found. Both hear it on the same audio, the PF acts, the PM
  cross-checks. This is my reading, not a procedure. [Y]
- **Single seat.** One person flies, monitors, listens and decides. Single-pilot scans become more dispersed, primary
  instruments get less time, and looks outside are shorter `[D 6 Nov]` ([Sarter 2024](https://rosap.ntl.bts.gov/view/dot/77748/dot_77748_DS1.pdf)). No single-seat talk-down study found.
  The case for the hybrid is stronger here, because there is no PM to catch a missed call. [Y]

## 4. What controllers add that is hard to automate

| What the controller adds | Evidence | Our route | Tag |
|---|---|---|---|
| Reads overall trend, not single height snapshots | Data block height fluctuates | Filtered position, words at low rate | `[D 6 Nov]` [RA 3291 para 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Resists over-correcting | Display makes small errors look large | Hold-off rule, step targets | `[D 6 Nov]` [RA 3291 para 22](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Scales corrections with range | Heading changes shrink as range falls; avoid small changes far out | T shortens near runway | `[D 6 Nov]` [RA 3291 para 24](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Avoids capturing centreline and glidepath together | Reduces pilot workload | Not in case 10: stagger corrections | `[D 6 Nov]` [RA 3291 para 28](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Uses emphasis | Voice stress speeds pilot action | Fixed urgent voice, tone, colour | `[D 6 Nov]` [Doc 4444 8.9.7.2.5.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| Adapts to aircraft type and speed | Gives warnings and clearances earlier for fast types | Type table at setup | `[D 6 Nov]` [RA 3291 paras 25, 29](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Tests that the pilot is receiving | With no radio reply, orders a manoeuvre and watches the radar | Compliance check on track response | `[D 6 Nov]` [RA 3291 para 17](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf) |
| Detects a wrong or surprising response | Climb on the elevation display: ask if more than 2 NM out, keep calling if closer | Partly: detect, display, no question | `[D 6 Nov]` [Doc 4444 8.9.7.2.8](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |
| Forms an opinion that the approach is unsafe | FAA stops guidance on the controller's opinion | Only coded rules; no opinion | `[D 6 Nov]` [JO 7110.65BB 5-12-8](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| Handles the case not in the book | Order tells controllers to use best judgement | Cannot; stop guidance, hand to pilot | `[D 6 Nov]` [JO 7110.65BB title page](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| Reassures | Pilot on one-chance fuel called the controller steady and calm, and said it helped. One account, not data | Calm fixed voice; do not claim this | `[D 6 Nov]` [Flying, 2009](https://www.flyingmag.com/green-light-at-bitburg/) and `[A 6 Nov]` [Air & Space, Radar Love](https://www.smithsonianmag.com/air-space-magazine/radar-love-121076372/) |
| Phrases and gives a reason | Reason should go with a missed approach instruction | Short reason word in the call | `[D 6 Nov]` [Doc 4444 8.9.6.1.8](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf) |

### Function allocation

**Parasuraman, Sheridan and Wickens (2000)** `[D 6 Nov]` ([copy on SlideShare](https://www.slideshare.net/slideshow/psw-67316430/67316430), full text except Table I and figures).
Original not opened. Four stages, each with its own level. My allocation [Y]:

| Stage | Level for our system | Why |
|---|---|---|
| Information acquisition | High | Radar and filter do this better; keep raw deviation visible |
| Information analysis | High | Allowed if the operator can reach raw data and knows its limits |
| Decision and action selection | Moderate: suggest one option, pilot may refuse (level 4 in the paper) | Paper advises no more than moderate in high-risk cases where a human may need to take over |
| Action implementation | None | Pilot flies; no autopilot coupling in scope |

The paper also says high automation suits time-critical cases where humans cannot respond in time `[D 6 Nov]`. Removing bad
needles at once fits this: it is an information action, not a flight action. [Y] It sets reliability as a critical criterion
and asks for a near-zero miss rate with few false alerts `[D 6 Nov]`. Case 10's 26 % catch of a 100 m jump at 4 NM [K] is the
weak point against that criterion. [Y]

**Fitts list.** The list has 11 statements on what humans and machines each do better. It is criticised but still
widely used, as a starting point `[A 6 Nov]` ([de Winter and Dodou 2014](https://link.springer.com/doi/10.1007/s10111-011-0188-1)). The full paper refused connection. Applied here
[Y]: machine takes steady monitoring, fast arithmetic and fixed timing; the human keeps judgement, the unexpected and
final responsibility.

**Known automation problems:**

| Problem | Meaning | Risk in this concept [Y] | Control [Y] | Tag |
|---|---|---|---|---|
| Automation surprise | System acts other than expected | Cue changes with no visible reason | Show state and reason in one word | `[A 6 Nov]` [Sarter, Woods, Billings 1997, citation only](https://floss.syr.edu/bibcite/reference/6865) |
| Mode confusion | Operator misreads the current mode | Pilot flies an old target in HOLD or DELAYED | Few states, each with a unique look | `[A 6 Nov]` [review of mode awareness](https://hal.archives-ouvertes.fr/hal-03114205) |
| Complacency | Attention leaves the automated task when others compete | Pilot stops cross-checking height and range | Require altimeter/range cross-check at fixed points | `[D 6 Nov]` abstract only [Parasuraman and Manzey 2010](https://depositonce.tu-berlin.de/handle/11303/8923) |
| Automation bias | Omission and commission errors with imperfect aids; training does not cure it | Pilot follows a wrong cue | Show validity with the cue; no cue if not valid | `[D 6 Nov]` abstract only [Parasuraman and Manzey 2010](https://depositonce.tu-berlin.de/handle/11303/8923) |
| Out of the loop | Operator cannot intervene well after automation fails | LOST at 1 NM with no mental picture | Keep pilot hand-flying; needles show position, not only commands | `[D 6 Nov]` [PSW 2000](https://www.slideshare.net/slideshow/psw-67316430/67316430); `[A 6 Nov]` [Endsley and Kiris 1995, citation only](https://informahealthcare.com/doi/abs/10.1080/00140139.2023.2243404) |
| Ironies | Rare manual takeover is the hardest task | Go-around after cue loss | Rehearsed single action; no restart | `[A 6 Nov]` [Bainbridge, Automatica 19(6), citation only](https://informahealthcare.com/doi/abs/10.1080/00140139.2023.2243404) |

## 5. Existing automation of this kind

| System | Chain | Who flies | Human role | Lesson | Tag |
|---|---|---|---|---|---|
| ACLS Mode I | Ship radar, data link, autopilot, to touchdown | Autopilot | Pilot monitors | Needs an aircraft coupler. Out of our scope | `[D 6 Nov]` [Wikipedia, carrier operations](https://en.wikipedia.org/wiki/Modern_United_States_Navy_carrier_air_operations); [FAS](https://man.fas.org/dod-101/sys/ship/weaps/an-spn-46.htm) |
| ACLS Mode IA | Same, uncoupled at about 3/4 NM | Autopilot, then pilot | Pilot takes the last part | Shows handback before touchdown | `[D 6 Nov]` [Wikipedia, carrier operations](https://en.wikipedia.org/wiki/Modern_United_States_Navy_carrier_air_operations) |
| ACLS Mode II | Radar errors to cockpit needles | Pilot | Pilot checks readings with the ship's control centre | **Nearest match to our visual cue** | `[D 6 Nov]` [Wikipedia, carrier operations](https://en.wikipedia.org/wiki/Modern_United_States_Navy_carrier_air_operations); [FAS](https://man.fas.org/dod-101/sys/ship/weaps/an-spn-46.htm) |
| ACLS Mode III | Controller talk-down | Pilot | Controller | Voice stays as backup | `[D 6 Nov]` [FAS](https://man.fas.org/dod-101/sys/ship/weaps/an-spn-46.htm) |
| ACLS loss of link | FAA phrase: no transmission for 5 s after data link loss, then alternative | Pilot | Pilot acts | Published 5 s precedent for a data-link cue | `[D 6 Nov]` [JO 7110.65BB 5-10-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf) |
| TALS | Ground mm-wave radar plus aircraft transponder, for RQ-7 Shadow | Autopilot | Operator | Radar landing guidance works with a cooperative transponder | `[A 6 Nov]` [Wikipedia RQ-7](https://en.wikipedia.org/wiki/AAI_RQ-7_Shadow) |
| UCARS-V2 | Ground radar, transponder, encrypted link; ship motion added | Autopilot of MQ-8 | Operator | Same; a blog reports one aircraft lost after failed acquisition, unverified | `[A 6 Nov]` [NAVAIR](https://www.navair.navy.mil/node/4586); [blog](https://vmasecaviation.wordpress.com/2017/03/13/automated-manned-and-unmanned-aircraft-landing-systems/) |
| PAPI | Four lights, 2 white 2 red on path | Pilot | None | Passive and independent, but useless before visual contact. Range figures in search results conflict | `[A 6 Nov]` [AOPA](https://www.aopa.org/news-and-media/all-news/2015/february/flight-training-magazine/how-it-works) |
| CPDLC | Text data link | Pilot | Controller | Long messages should be avoided. Reply-based, for non-urgent strategic use, so wrong for a 1 Hz cue | `[D 6 Nov]` [Doc 4444 14.3.1.1](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf); `[D 6 Nov]` [Prasad et al. 2022 footnote](https://arxiv.org/pdf/2212.07164) |
| Simulator voice agents | Controller speech to text to pilot agent to synthetic voice | Simulator | Trainee controller | Direction is opposite to ours. WER 3.1 % average, 0.7 to 8.2 % per controller, Vienna | `[D 6 Nov]` [Helmke et al. 2024](https://www.sesarju.eu/sites/default/files/documents/sid/2024/papers/SIDs_2024_paper_004%20final.pdf); `[A 6 Nov]` command rate over 96 % [Prasad et al. 2022](https://arxiv.org/pdf/2212.07164) |
| SYNCALL | Synthetic voice callouts against pilot-not-flying calls, simulator | Pilot | Crew | Better airspeed and sink rate on non-precision approaches; on one-engine approach, inappropriate callouts and worse airspeed | `[D 6 Nov]` abstract [Simpson 1980, NASA CR-3300](https://ntrs.nasa.gov/search.jsp?R=19800025590) |

**Automated talk-down experiment:** not found. Two targeted searches gave none. SYNCALL is the closest. The term "Autonomous
GCA" gave no result; I cannot confirm that a system of that name exists. A synthetic-ILS patent shows the idea of ILS-like
needles from another source `[A 6 Nov]` ([US 9159241](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9159241)).

Voice recognition is not needed for us: the cue only speaks fixed phrases, so no recognition error can enter the loop. [Y]

## What we could not read

| Source | Why | What is missing |
|---|---|---|
| FAA site for JO 7110.65, AIM | HTTP 403 on fetch; browser page text failed ("policy check temporarily unavailable") | Read instead: full JO 7110.65BB PDF from the [Sprinkle copy](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf), a third-party host. Its Section 12 pages are dated 2/20/25. Sprinkle says the copy includes Change 2; I did not check this. The "every 5 seconds" rule also appears in the 2017 edition (7110.65X, [SKYbrary copy](https://skybrary.aero/sites/default/files/bookshelf/4141.pdf)) |
| AFMAN 13-204 V3, DAFMAN 13-204 V3 | 403, then 404 in the browser | All USAF final-control text |
| NAVAIR 00-80T-114 | Mirrors refused or gone | Navy duties and PAR tolerances (para 7.2.5.7) |
| CV NATOPS, NAVEDTRA 14342A, Navy ACLS chapter, DTIC ACLS report | Failed or 403 | Primary ACLS mode definitions. Modes above rest on Wikipedia and FAS |
| Doc 4444 edition | Read Swiss FOCA consolidated copy, 16th edition, footers show amendment No. 11 | Later amendments not checked |
| MMATM | File name says Issue 12, page footers say Issue 14 | Treat as Issue 14; PAR rules sit in RA 3291 |
| Annex 10, Doc 9426, GOLD Doc 10037 | Not fetched or not reached | PAR specification, planning guidance, data-link latency |
| 14 CFR 121.542 | eCFR redirected | Rule text; SKYbrary used |
| Original Parasuraman 2000, Sarter 1997, Endsley 1995, Bainbridge, Fitts, de Winter 2014 | Paywall or refused | PSW read on an unverified SlideShare copy; rest are citation only |
| Studies seen through Sarter 2024 | Report summarises them | Jarvis 2017, Reynal 2016, Dehais 2017, Spady 1978 originals not read. Sarter's Tables 5 and 6 are images and I did not extract them |
| NASA workload primer, Eurocontrol Dublin report, PubMed abstract, Radar Love, USNI 1952, SKYbrary PAR and CPDLC pages | DNS, not opened, cookie wall, 403, 429 | Used as [A] only, or left out |
| FAA and DTIC message-complexity reports | Not opened | Readback numbers are [A] |

## Design consequences

Everything here is my inference [Y] from the sources cited. Case 10 facts come from `TECHNICAL.md`.

### Must do

1. **Show guidance is alive at all times.** A visible heartbeat at the radar rate replaces the 5 s voice stream (`[D 6 Nov]` [5-12-4,
   5-10-4](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)). Silence must mean "no correction needed" only while the heartbeat runs.
2. **Tell the pilot about radar loss early.** Show loss at 3 s (`[D 6 Nov]` [RA 3291 para 5](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). Case 10 goes to LOST at about
   5 s. The team can keep 5 s as the go-around point. The FAA 5 s is radio silence, not radar loss, so it is the nearest
   published time on the pilot's side and not a direct source. Re-run the fault tests if the timing changes.
3. **Give position and trend as well as a target.** Rules give both. Add a trend word such as NOT CORRECTING (`[D 6 Nov]` [RA 3291
   para 25](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). This also serves as the "wrong response" check: if the track does not respond after a set time, say so.
4. **Treat azimuth and elevation failure apart.** Elevation loss has its own rule: tell the pilot at once, then azimuth-only
   or missed approach (`[D 6 Nov]` [Doc 4444 8.9.7.2.5.4](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)). Case 10 has one valid flag.
5. **Take DH from the pilot.** Case 10 fixes 200 ft. The rule sets it from the pilot (`[D 6 Nov]` [RA 3291 para 1b](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)).
6. **Keep advisory information below DH, marked advisory, or state why not.** (`[D 6 Nov]` [Doc 4444 8.9.7.2.7](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)). Stopping at
   minimums is defensible for a demo, but say it is a deliberate cut.
7. **Add a gear prompt and a clearance gate.** Prompt gear before 2 NM and ask for a pilot press. Show CLEARANCE NOT
   CONFIRMED at 2 NM (`[D 6 Nov]` [RA 3291 para 1d, 1e](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). Neither is in case 10.
8. **Say the reason and the condition in a go-around call.** Pattern: RADAR LOST, IF RUNWAY NOT IN SIGHT, GO AROUND (`[D 6 Nov]`
   [JO 7110.65BB 5-10-14](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)).
9. **Back every critical voice call with a visual flag.** 8 of 14 pilots in one study did not report an alarm (`[D 6 Nov]` [Dehais 2012](https://openscience.isae-supaero.fr/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?parentDocumentId=8060&documentId=12857&skipWatermark=true&skipCopyright=true)).
10. **Keep voice short and scarce.** Fixed phrases, one topic per call, no call near touchdown except warnings.
11. **Use a lower limit from obstacle data.** Warn on low deviation earlier than high deviation (`[D 6 Nov]` [RA 3291 paras 26, 27](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)).
    Case 10's symmetric 2 dots is a simplification; state it.
12. **Stagger corrections.** Avoid capturing both axes at once (`[D 6 Nov]` [RA 3291 para 28](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). The brief's test scenario starts off
    both axes, so show this.
13. **Show raw position beside any command**, so the pilot can judge the command (`[D 6 Nov]` [PSW 2000](https://www.slideshare.net/slideshow/psw-67316430/67316430)).

### Must not do

1. **Must not fly the aircraft.** No coupling, no control output.
2. **Must not decide land or go around at DH.** The pilot decides; below DH, guidance is advisory (`[D 6 Nov]` [5-12-7](https://cdn.sprinkle.com/library/pdfs/4dc0aa14-617e-413e-8f42-2642e94301d5.pdf)).
3. **Must not claim gear state, clearance or traffic separation.** The PAR controller has no separation duty either (`[D 6 Nov]` [RA 3291
   para 32](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)), and case 10 tracks one target.
4. **Must not guess when data is bad.** No extrapolation. Inside 4 NM, a returned contact does not restart the approach (`[D 6 Nov]` [RA
   3291 para 7b](https://assets.publishing.service.gov.uk/media/68db8f9ac487360cc70c9eea/RA3291_Issue_4.pdf)). Case 10's latch agrees. Outside 4 NM the UK allows re-identification; ours is stricter, and that is fine.
5. **Must not require readback or voice input on final.** Pilot must stay free of the radio (`[D 6 Nov]` [Doc 4444 8.9.7.2.3](https://www.bazl.admin.ch/dam/it/sd-web/jMIWMg9YgaoW/4444_cons_en.pdf)).
6. **Must not add non-essential messages below the sterile boundary.** No status or advisory chatter.
7. **Must not rely on voice alone for a critical warning.**
8. **Must not imitate reassurance or claim judgement.** Say what the system cannot do: it holds no opinion that an approach
   is unsafe, and it cannot handle the case outside its rules.
9. **Must not claim lower pilot workload without a pilot trial.** Evidence here does not support it. No real pilot has flown
   the cue [K]. Flight director and raw data did not differ in one study (`[D 6 Nov]` [Ellis and Schnell 2009](https://ntrs.nasa.gov/api/citations/20100012851/downloads/20100012851.pdf)).
10. **Must not present the concept as new radar-to-needle technology, or as approved or ready for flight.**
