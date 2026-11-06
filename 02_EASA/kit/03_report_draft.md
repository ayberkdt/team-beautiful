# EASA kit · 03 — Report draft (5 pages, template `Ideathon_Template_2026.docx`)

**Structure (5 Nov, user: "pull from the draft section and the rules").** The sections follow the EASA task sheet
(`official_2026-11-05/EASA retrofit challenge.docx`: "State your Assumptions and Goal", "Outline a Step-by-Step
process": mount, wire, program) and the scoring sheet (`Rules and Criteria.xlsx`): R1 10 → §1 (problem in our own words,
assumptions explicit); R2 20 → §2–§4 (method, and "justifies choice over alternatives" → Table 1); R3 15 → §5
(order-of-magnitude numbers, limits); R4 10 + R5 10 → §6 (new angle, benefit, next step); R6 10 → whole document
(figures labelled, sources cited, body ≤ 5 pages).
**Restructure (5 Nov, user):** the architecture figure is gone and its content is the first paragraph of §3; the phase
table is now the block diagram of Figure 2 (`scripts/easa_phase_diagram.py`); Table 1 has three columns; §5 shows its
numbers in Tables 4 and 5 (generated) and Figure 4, and the text states only what they do not show; citations are
numbered [n], blue, and linked to the reference list. Barriers (engine shut-down, gate, pawl) appear only in Table 1,
removed for safety; the vibration cue is a lap-belt tactor.
**Citations:** write `[@key]`, `[@key, p. 9]` or `[@a; @b]`. The build numbers keys in order of first use and takes the
reference text from the `- @key:` lines under "## References". Unused references are dropped and printed.
**Generated tables:** a line `{{table:cues}}` or `{{table:sensors}}` is filled from `outputs/tradeoffs/tradeoffs.json`
by `easa_report_docx.py`, so §5 numbers cannot go stale.
**Style:** humanizer (`D:\Masaustu\Makale\.agents\skills\humanizer\SKILL.md` v2.8.2) plus STE-like clarity: no em or en
dashes in the report text (ranges written "a to b"), no "not X but Y" or tailing negations, no bold inline-header lists,
one term for one concept, active voice, each fact stated once. Check: `article_lint.py` (articlecraft) and a dash scan.
**Numbers:** §5 from `outputs/tradeoffs/tradeoffs.md` (checked by `easa_report_docx.py`); §3 response time from
`research/R8_reaction_time_design.md` §B; §4 from `docs/28_retrofit_installation.md`; mass and power from kit `07`.

---

## Title: LOCK-SENSE, a retrofit canopy-lock alert for the Extra NG

Team Beetiful · EUROAVIA Ideathon 2026 · EASA challenge

## 1. Problem, assumptions and goal  *(R1)*

On 2 April 2022 the canopy of Extra NG G-MIIL broke up in level flight at 184 KIAS, and the pilot bailed out
[@aaib_gmiil]. The AAIB traced the failure to poor bonding of the canopy frame, which let fatigue cracks grow in the
acrylic. The BFU, as State of Design, thought a canopy that was not fully locked more probable [@aaib_gmiil, App. A].
Nobody can settle the question, because the aircraft did not record the lock state.

EASA AD 2025-0156 names a partly locked canopy as the main cause of in-flight openings on this type [@easa_ad], and on SP-HMM the BFU and the manufacturer judged that the pawls were "engaged only partially"
[@pkbwl_hmm, §3.1]. The type now has a new placard [@extra_sb124] and new
flight-manual text. It still has no electrical canopy warning. We assume that:

- the aircraft is an Extra NG with three shoot bolts on one linkage [@aaib_gmiil, p. 9] and a Garmin G3X Touch [@extra_sl122];
- certification and cost are outside the task [@task_sheet];
- the latch does not change; we add sensors and alerts only;
- jettison does not change, and the pilot's handle check stays the primary check;
- a single electrical fault must not show a false "locked"; latent sensor faults, one rigging error on all sensors and
  combined faults stay as residual hazards (§5).

Our goal is fewer take-offs with an unlocked canopy that the pilot has not noticed, and a lock-state record for the next
investigation.

## 2. Evidence from 241 investigated events  *(R2)*

*Figure 1 caption:* "Lock-related openings cluster in the initial climb and occur on many aircraft types (126 of 241
investigated events)."

We built a catalogue of 241 investigated canopy and door events from public NTSB, AAIB, BEA, BFU, PKBWL, SUST and DSB
reports, each with its source URL [@catalogue]. A check of random rows found a 1.5 % field error, which we corrected.
Of the 241 events, 126 were lock-related, 76 of these happened in the initial climb, and 16 were fatal (Figure 1).
Fleet hours are not published, so the catalogue shows where openings happen but cannot give a rate.

On the Extra NG one spring-loaded linkage moves all three bolts. The handles sit at the same 70 mm gap when the canopy
is locked and when it is open with the handles released, and at the frame edge a partly locked canopy looks the same as a locked one
[@aaib_gmiil, pp. 9, 20].  On
other types, every false "closed" or "locked" indication we found came from a switch on the handle, the drive or one
pin: DA40 PH-TIN [@dsb_phtin], Pitts G-IIDY [@aaib_giidy] and a fatal RV-14A [@rv14]. For transport-aircraft doors, AC 25.783-1A asks for an indication that directly monitors the closed, latched and
locked condition, with an erroneous "locked" indication no more likely than 10⁻⁵ [@ac25783, §12].

## 3. Design  *(R2)*

LOCK-SENSE adds four inductive sensors and one alert unit. Three sensors watch the bolt tips and the fourth watches
the seated frame (Figure 2). All four sit on the fuselage side, so the jettison path does not change. A hardware AND
lights the green CANOPY LOCKED lamp only when all four agree. Line monitoring turns an open or a short circuit in a
sensor loop into a fault, and the unit then shows "not locked". The unit drives a red lamp, the voice "CANOPY,
CANOPY", a pulsed vibration pad in the lap belt, the G3X "Canopy Closed" input and a lock-state log.

The pilot takes off only with the green lamp on and no G3X canopy alert. If the two disagree, the canopy counts as not
locked. At power-up the unit sends "not locked" to the G3X, so a shorted G3X line shows as a missing G3X alert.

*Figure 2 caption:* "Each sensor sees the steel bolt tip only at full lock; a partly locked bolt leaves it off, and the
unit shows red."

*Figure 3 caption:* "The phase of flight sets the alerts. A wrong speed reading can only move the unit between
Take-off roll and Airborne, and both show red."

*Table 1 (title above the table):* "For each element we kept the option that reaches a busy pilot and never takes
away engine power."

| Element | Choice | Why not the others |
|:---|:---|:---|
| Sensing point | Each bolt and the seat | One pin (the task-sheet example), the handle or the linkage cannot see one bolt out (Table 4) |
| Sensor type | Line-monitored inductive sensor | Snap switches, Hall sensors and bare contacts give more false alerts (Table 4); a worn or wet bare contact, our first idea, can read "locked" |
| Aural | Voice without a lead tone | A lead tone slowed responses [@simpson1980] |
| Vibration | Lap-belt pad | A stick shaker means "stall"; a knob shaker vibrates an engine control, which must not creep under vibration [@cs23]. The waist matched the hand's response time and, with a strong vibration, half the wrong actions (10.9 % against 22.3 %) [@meng2015] |
| Barrier | None; alerts only | Removed for safety: engine shut-down, a take-off gate and a throttle pawl act on the engine or throttle, so a fault could take away power in flight |
| G3X link | Unit output into the G3X | A raw switch on the two-state G3X input [@g3x_im] would read a short to ground as "closed" |

Pilots in real flight answered a headset tone in 0.79 s, but under high workload they missed 38 % of tones
[@callan2018]; in a simulator the misses rose to 58 % [@dehais2019]. Two or three cues together gave faster responses than one cue alone [@politis2016]. Most of this work comes from
driving and laboratory studies, so we design for 1.5 s, an estimate for a surprised driver [@green_rt], and take
3.0 s as our own 95th-percentile margin [@scrivens2024]; transport certification allows only 1 s, for a test pilot
who expects the failure [@ac257d].

Extra NG roll data is not published. With an assumed 5.0 m/s², a brisk roll reaches 30 kt 3.1 s after the throttle
moves, and lift-off is at 80 KIAS [@aopa2020]. An rpm trigger with 0.5 s persistence starts 1.3 s later than the lever
switch (Figure 4), and even with the lever switch a slow pilot acts after 30 kt. So the red alert starts at
line-up, before the roll, in line with AC 25.783-1A, which asks for an aural warning before or early in the take-off roll [@ac25783]. If a new voice alert first appears
above 40 kt, it waits until 10 s after lift-off, so it does not prompt a high-speed reject. The red lamp never waits.

*Figure 4 caption:* "With the lever switch the median pilot acts at 18 kt on a brisk roll; with an rpm trigger the
action comes after 30 kt."

## 4. Step-by-step retrofit  *(R2)*

*Table 2 (title above the table):* "Twelve retrofit steps in the order of the task sheet (1 to 4 mount, 5 to 8 wire and
program, 9 to 12 test); each step ends with a check that can fail."

| No. | Action | Pass check |
|:---|:---|:---|
| 1 | Measure bolt travel per millimetre of handle travel (ratio r) at gaps of 60 to 70 mm, and the space and metal in the sensor keep-out zone (Ø40.6 mm) at each lug [@gaps] | r and the trip window known before any part is made |
| 2 | Fit an aluminium bracket under the lug fasteners (one grip length longer); drill no new holes | Clamp-up and thread engagement agreed with the manufacturer |
| 3 | Set the sensor gap of Figure 2 at full lock | Gap within 0.3 mm and inside the 3.5 mm range for a 17-4 PH target [@gaps]; lug alone, bolt withdrawn: sensor off |
| 4 | Fit the seated sensor opposite a steel target on the frame | Brackets torque-striped and lock-wired; jettison forces unchanged |
| 5 | Supply the unit from its own breaker | Breaker sized for 22 AWG; peak load 2.8 W |
| 6 | Run one shielded loop per sensor to a sealed, keyed connector; fit the pad in the pilot's lap belt | Shields grounded at the unit end only |
| 7 | Connect lever switch, manifold pressure, rpm, IAS and GPS speed; drive lamps, voice (a GMA 245R alert input other than ALERT 1, which the GNX 375 uses [@gma245_im; @extra_sl322]), belt pad and G3X line | Lamp, voice and pad start within 0.5 s of lever-switch closure |
| 8 | Load the phase logic of Figure 3 and the self-checks | Bench run matches Figure 3 |
| 9 | Gauge each bolt at the trip window from step 1 (design values 67.5 and 68.7 mm) | Not locked and locked read right 10 times of 10 |
| 10 | Inject opens, shorts, a sensor stuck ON (canopy open; bolt out), a G3X line short and an output stuck at LOCKED | Each fault logged as caught or missed; only stuck ON with the bolt out is missed (§5) |
| 11 | Run the engine at take-off power, then fly an aerobatic check flight | Belt pad felt at take-off power; no nuisance alert |
| 12 | Add "handle check, green ON, no G3X canopy alert" to the checklist | Gauge check and log download at each annual |

## 5. Results, rigour and limits  *(R3)*

A Monte Carlo model runs 200 000 simulated take-offs per case (seed 2026). The task-sheet example, one microswitch at
one pin, missed a single bolt out in 133 345 trials (0.67). LOCK-SENSE missed a partial lock 87 times and one bolt out
103 times, and it never missed an unseated canopy (95 % upper bound 2e-5). A second model adds whether the pilot
notices the alert in time and acts on it. Its output, the risk reduction factor (RF), is how many times less likely a
take-off with an unnoticed unsafe lock becomes, against no system. It is a model estimate, and it does not count
canopy losses or fatal accidents.

*Table 3 (title above the table):* "The chosen alert set gives 71× when the pilot always acts and about 3× when the
pilot distrusts the alert."

{{table:cues}}

*Table 3 note:* "Always acts": the pilot acts on every alert noticed. "Distrusts": the pilot acts as often as alerts
have been right (0.66). Generic false-alert rate 0.31 per 1 000 flights; Table 4 uses each sensor's own rate, 0.14
for the inductive sensor, so the chosen set gives 5.0× there.

*Table 4 (title above the table):* "Only per-bolt sensors see one bolt out, so only they keep a large benefit when
the pilot acts."

{{table:sensors}}

*Figure 5 caption:* "An alert helps much only when the pilot nearly always acts on it."

With alerts only, the pilot sets the benefit: if the pilot acts on half of the alerts (c = 0.5), the alert sets give
1.6× to 2.0× (Figure 5). If each millimetre of handle travel moves the bolt only 0.5 mm, scatter
gives the inductive sensors about 51 false alerts per 1 000 flights, and a distrusting pilot then gains nothing
(1.0×). Step 1 measures this ratio first.

We ran thirteen fault cases through the alert logic. No single electrical fault gave a false green, but two
cases did: a bolt out with its own sensor stuck ON, and all three sensors rigged early with one wrong gauge. The stuck
sensor shows as a fault at the next powered opening; the step 9 gauge check and the handle check cover the rest.

Only the partial-lock base rate comes from a published source, an expert-judgment omission rate [@nureg1278]. The other rates are assumed ranges, and the sensor
failure rates come from an industrial sensor analysis [@exida]; a tenfold change in them moves the RF by less than
2 %. Step 11 checks that engine vibration does not mask the belt pad.
The system cannot detect a frame failure while the bolts stay locked, which is the failure the AAIB found on G-MIIL.

## 6. Innovation, value and next step  *(R4, R5)*

LOCK-SENSE senses each bolt where it enters its lug, and we chose the trigger and the alerts from measured pilot
response times and compliance. Its log keeps the sensed lock state for investigators, though it cannot prove that the
frame was sound. For EASA it adds an electrical warning against the hazard named
in AD 2025-0156, for about 0.45 to 0.85 kg and 1.8 W of continuous power. A one-off NDT of the frame bond, which EASA said in April 2024 it was considering [@aaib_sr], stays the defence
against the AAIB cause. Next we will measure bolt travel on an aircraft and bench-test 30 sensors over 10 cycles.
As 300 clean cycles bound the failure rate only below about 1 %, vibration, temperature, endurance and pilot-response
tests follow.

## References (page 8, not counted)

Sources and checks: `research/00_INDEX.md`; reference details verified against the research notes on 5 Nov 2026
(scratchpad `refs_verified.md`), journal metadata against Crossref. Titles without quotation marks are descriptions.

- @aaib_gmiil: Air Accidents Investigation Branch, "Extra NG, G-MIIL," AAIB Bulletin 4/2024, report AAIB-28120, 22 Feb. 2024. https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf
- @easa_ad: European Union Aviation Safety Agency, Airworthiness Directive AD 2025-0156, EXTRA NG, placards and markings, flight manual amendment, 21 Jul. 2025. https://www.easa.europa.eu/download/AD-tmp-storage/EASA_AD_2025_0156.pdf
- @pkbwl_hmm: PKBWL (State Commission on Aircraft Accidents Investigation, Poland), final report 2023-0061, Extra NG SP-HMM, canopy opened in flight, 11 Jun. 2024. https://pkbwl.gov.pl/wp-content/uploads/2023/08/2023_0061_RK_ENG.pdf
- @extra_sb124: EXTRA Aerobatic Aircraft GmbH, "Canopy-Placard," Service Bulletin SB-NG-1-24, Issue A, 19 Dec. 2024. https://extraaircraft.com/download-pdf/3470/
- @extra_sl122: EXTRA Aerobatic Aircraft GmbH, "EXTRA Statement to FAA AD 2022-03-15," Service Letter SL-NG-1-22, Issue A, 21 Mar. 2022. https://extraaircraft.com/download-pdf/2773/
- @task_sheet: European Union Aviation Safety Agency, "Team challenge": retrofit a canopy alert system, task sheet for the EUROAVIA Ideathon, received 5 Nov. 2026.
- @catalogue: Team Beetiful, catalogue of 241 investigated canopy and door events (NTSB, AAIB, BEA, BFU, PKBWL, SUST, DSB), one source URL per row, compiled 4 Nov. 2026, unpublished dataset.
- @dsb_phtin: Dutch Safety Board, report 2011051, Diamond DA 40 D PH-TIN, rear door separated in flight on 29 Jun. 2011. https://onderzoeksraad.nl/wp-content/uploads/2023/11/2011051_ph_tin_eng.pdf
- @aaib_giidy: Air Accidents Investigation Branch, Pitts S-2B Special G-IIDY, canopy opened on the take-off roll, AAIB Bulletin 3/2011, EW/G2010/11/04, pp. 36 to 37. https://assets.publishing.service.gov.uk/media/5422eb2440f0b61346000055/Pitts_S-2B_Special__G-IIDY_03-11.pdf
- @rv14: National Transportation Safety Board, final report CEN23FA359, Van's RV-14A N6161, fatal accident on 12 Aug. 2023. https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/192848/pdf
- @ac25783: Federal Aviation Administration, "Fuselage Doors and Hatches," Advisory Circular AC 25.783-1A, 25 Apr. 2005. https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25_783-1A.pdf
- @faa_memo: Federal Aviation Administration, Transport Airplane Directorate, "Modification of outward opening doors on existing transport airplanes," memorandum, n.d. https://www.faa.gov/sites/faa.gov/files/2022-10/Transport_Airplane_Directorate_Memorandum.pdf
- @g3x_im: Garmin, "G3X/G3X Touch Avionics Installation Manual," 190-01115-01, Rev. AZ, Sep. 2025, §23.4.9 and Fig. 26-1 note 13. https://static.garmin.com/pumac/190-01115-01_az.pdf
- @gma245_im: Garmin, "GMA 245/245R Installation Manual," 190-01879-11, Rev. 14, Mar. 2026, §1.2.1. https://static.garmin.com/pumac/190-01879-11_14.pdf
- @extra_sl322: EXTRA Aerobatic Aircraft GmbH, "Garmin GNX 375 Transponder Audio OUT," Service Letter SL-NG-3-22, Issue A, 23 Dec. 2022. https://extraaircraft.com/download-pdf/2788/
- @simpson1980: C. A. Simpson and D. H. Williams, "Response time effects of alerting tone and semantic context for synthesized voice cockpit warnings," Human Factors, vol. 22, no. 3, pp. 319 to 330, 1980. https://doi.org/10.1177/001872088002200306
- @callan2018: D. E. Callan, T. Gateau, G. Durantin, N. Gonthier and F. Dehais, "Disruption in neural phase synchrony is related to identification of inattentional deafness in real-world setting," Human Brain Mapping, vol. 39, no. 6, pp. 2596 to 2608, 2018. https://doi.org/10.1002/hbm.24026
- @dehais2019: F. Dehais, R. N. Roy and S. Scannella, "Inattentional deafness to auditory alarms: inter-individual differences, electrophysiological signature and single trial classification," Behavioural Brain Research, vol. 360, pp. 51 to 59, 2019. https://doi.org/10.1016/j.bbr.2018.11.045
- @politis2016: I. Politis, "Effects of modality, urgency and situation on responses to multimodal warnings for drivers," PhD thesis, University of Glasgow, 2016. https://theses.gla.ac.uk/7857/7/2016PolitisPhD.pdf
- @vanerp2007: J. B. F. van Erp, L. Eriksson, B. Levin, O. Carlander, J. A. Veltman and W. K. Vos, "Tactile cueing effects on performance in simulated aerial combat with high acceleration," Aviation, Space, and Environmental Medicine, vol. 78, no. 12, pp. 1128 to 1134, 2007. https://doi.org/10.3357/asem.2133.2007
- @meng2015: F. Meng, R. Gray, C. Ho, M. Ahtamad and C. Spence, "Dynamic vibrotactile signals for forward collision avoidance warning systems," Human Factors, vol. 57, no. 2, pp. 329 to 346, 2015. https://doi.org/10.1177/0018720814542651
- @green_rt: M. Green, "Driver reaction time," Visual Expert, accessed 5 Nov. 2026. https://www.visualexpert.com/Resources/reactiontime.html
- @ac257d: Federal Aviation Administration, "Flight Test Guide for Certification of Transport Category Airplanes," Advisory Circular AC 25-7D, 2018, §4.3.6. https://www.faa.gov/documentLibrary/media/Advisory_Circular/25-7D.pdf
- @scrivens2024: L. S. Scrivens, "Study on pilot response time to reject takeoff with one engine inoperative," MS thesis, Florida Institute of Technology, 2024. https://repository.fit.edu/etd/1482
- @aopa2020: D. Hirschman, "Extra NG: mild to wild," AOPA Pilot, Dec. 2020. https://aopa.org/news-and-media/all-news/2020/december/pilot/extra-ng-mild-to-wild
- @gaps: Honeywell, "GAPS and HAPS Series Aerospace Proximity Sensors," datasheet 000843, Issue 2, Apr. 2021. https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/en-us/products/sensors/motion-position-sensors/common/documents/sps-siot-haps-gaps-combined-datasheet-000843-1-en-ciid-180941.pdf
- @nureg1278: A. D. Swain and H. E. Guttmann, "Handbook of Human Reliability Analysis with Emphasis on Nuclear Power Plant Applications," U.S. Nuclear Regulatory Commission, NUREG/CR-1278, Aug. 1983. https://www.osti.gov/servlets/purl/5752058
- @exida: exida, FMEDA and proven-in-use assessment of Pepperl+Fuchs inductive NAMUR sensors, report P+F 03/11-10 R015, V1 R1.1, Jul. 2004. https://files.pepperl-fuchs.com/webcat/navi/productInfo/cert/cert0707.pdf
- @cs23: European Union Aviation Safety Agency, Easy Access Rules for Normal, Utility, Aerobatic and Commuter Category Aeroplanes (CS-23), Amendment 4, CS 23.1141(c), Jun. 2018. https://www.easa.europa.eu/en/downloads/47182/en
- @aaib_sr: Air Accidents Investigation Branch, "G-MIIL Safety Recommendation Document," SR 2024-004 and 2024-005 with EASA responses, updated 29 Jan. 2025. https://assets.publishing.service.gov.uk/media/67a2193fad556423b636ca0d/G-MIIL_Safety_Recommendation_Document.pdf
