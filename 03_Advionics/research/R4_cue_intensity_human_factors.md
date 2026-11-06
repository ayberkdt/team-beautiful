# R4 — How intrusive may a pilot cue be? Sourced rules and a proposed intensity rule

Written 2026-11-06 for case 10 (PAR hybrid cue). All sources were read on 2026-11-06 unless stated.
Educational concept only. Not approved or ready for flight use.

## Tags

| Tag | Meaning |
|---|---|
| [D] | I read the source text itself in this session (PDF text extracted and read, or page read). |
| [D-f] | Page fetched in this session, but the text reached me through the fetch tool's extraction, not as raw text. Check before quoting. |
| [D-via] | I read a document that quotes or cites the named source. I did not read the named source. |
| [A] | Search snippet only. Not read. Do not cite as read. |
| [Y] | My inference or proposal. |
| [K] | Computed from `outputs/replay_data.json` or stated in `TECHNICAL.md` / `outputs/result.md`. Simulated data only. |

## Short answer

1. Real systems stay silent on the path. The closest real voice alert, EGPWS Mode 5, starts at 1.3 dots below
   the beam, below 1000 ft, at half volume. It says one noun, not a command [D].
2. Pilots already hear deviation calls from a colleague, but at and below the stabilisation gate, against limits
   the crew agreed in advance [D]. This is the model for our voice: a good pilot monitoring, not an instructor.
3. Loudness cannot carry the intensity. Pilots set radio voice at about 84–88 dB(A) at the ear, and the limit for
   non-emergency signals is 90 dB(A) [D-f, D-via]. That leaves about 2–6 dB. Intensity must come from fewer words,
   repetition, colour and position, as well as level [Y].
4. The most reported alert problem in an ASRS review was an alert that was too loud. The second was an alert that
   was missed [D-via]. Both limits are real.
5. A nuisance alert for an expert is often a correct alert about a problem already being fixed [D-via]. So the
   rule must stay quiet while the deviation is closing.
6. The proposed rule cuts guidance voice calls in scenario A from 6 to 1 [K], with the same needles and targets.

---

## 1. Alert levels and rules

### 1.1 14 CFR 25.1322 [D-f]

Source: https://www.law.cornell.edu/cfr/text/14/25.1322

- Three levels. Warning: immediate awareness and immediate response. Caution: immediate awareness, later response.
  Advisory: awareness, may need a later response.
- Warnings and cautions use at least two senses. Each cue can be acknowledged and silenced, unless it must stay on.
- Alerts must clear when the condition ends.
- Alerts must be designed to minimise false and nuisance alerts, and to prevent inappropriate or unnecessary ones.
- Colour: red for warnings, amber or yellow for cautions, any colour except red or green for advisories.
- Red, amber and yellow use outside alerting must be limited.

### 1.2 FAA AC 25.1322-1 (2010)

faa.gov refused the fetch (HTTP 403), and the browser only offered a file download. I did not read the AC itself.
I read the FAA Human Factors General Guidance Document, sections 4.1 and 4.3 (Nov 2013, Chg 1), which quotes the AC
paragraph by paragraph. All items below are [D-via] from these two PDFs:
https://hfcc.dot.gov/publications/docs/GeneralGuidance/zz_FAA_GeneralGuidanceDoc_Chapter_04_Section_03.pdf and
https://hfcc.dot.gov/publications/docs/GeneralGuidance/zz_FAA_GeneralGuidanceDoc_Chapter_04_Section_01.pdf

- Alert only on non-normal conditions and events that need crew awareness (AC 5.a, 5.c(1)).
- Advisory: normally one sense, placed where the crew scans periodically, no master alert, any tone once then
  automatic cancel (AC 6.e, App. 2 2.e(2)).
- A master aural alert is not recommended for advisories, because immediate attention is not needed (App. 2 2.c(3)).
- Caution: if continuous aural is not needed, play once and cancel automatically (App. 2 2.e(1)).
- One aural alert at a time. An active alert finishes first, unless a delay to a higher alert would harm response.
  An interrupted alert may repeat after (AC 8.b).
- Aural must be audible in the worst noise, but not so loud that it interferes with the action. Automatic volume
  control is recommended. Minimum volume must stay audible if noise rises (App. 2 2.b).
- Ramp onset and offset to avoid startle: 20–30 ms duration, onset 20–30 dB above ambient are "acceptable"
  (App. 2 2.d(2)).
- Frequencies 200–4500 Hz; avoid the dominant noise bands (App. 2 2.a).
- Fewer than 10 unique tones (App. 2 2.c(1)).
- Silenced aural alerts re-arm automatically. Manual re-arm needs a clear annunciation in the forward view
  (App. 2 2.e(4)).
- Time-critical warning: unique voice or tone, visual in each pilot's primary field of view, red, at least
  2 square degrees (App. 1 3.c). Master visual alert at least 1 degree (App. 1 1.e(2)).
- Green should not be used for advisory alerts (AC 11.a).
- Primary field of view about ±15° from the normal line of sight (section 4.1 background).
- Blink: use little. 0.8–4.0 Hz. Blinking that can last longer than about 10 s needs a cancel (AC 25-11A 31.f(4)).
  A blinking signal is more distracting than a steady one, and overuse reduces its effect.
- Alert text and voice should agree (App. 1 3.b(1)).

Note on the search snippet: a search summary said voice for time-critical warnings "should not be repeated if…"
with the sentence cut off [A]. The NPA text in 1.3 gives the full sense [D]: no repeat when it interferes with the
response.

### 1.3 CS-25 equivalent

- CS 25.1322 (Amdt 25/11, ED Decision 2011/004/R): same three levels, same "minimise false and nuisance alerts" [D-f].
  https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-large-aeroplanes-cs-25?page=42
  This Easy Access edition is dated January 2023. I did not check for later amendments.
- EASA NPA 2009-12 contains the draft AMC 25.1322 [D]. This is a draft from 30 Nov 2009, not the final AMC. It says:
  https://www.easa.europa.eu/sites/default/files/dfu/NPA%202009-12.pdf
  - Nuisance alert: alert from a working system that is inappropriate or unnecessary for the condition.
  - Frequent false or nuisance alerts raise workload, reduce confidence and affect reaction to a real alert (7.c).
  - Inhibit an alert when it could cause a hazard through distraction, adds clutter, or gives unnecessary
    information (8.b).
  - Manual inhibit needs a clear indication for as long as it exists (8.b).
  - Voice use should be limited, to keep it effective (section 6).
  - An alarming, tense voice tone is not recommended. The content of the message should be enough (B.2(2)).
  - Time-critical voice is not repeated if it interferes with the response, for example windshear or TCAS RA (B.2(4)).
  - Voice purpose: transfer load from visual to auditory, and reach the pilot wherever the eyes are (B.2).

### 1.4 FAA HF-STD-001 and DOT/FAA/CT-96/1

The FAA hosts chapter 7 of the Human Factors Design Standard (HFDS 2003). HF-STD-001 replaced the 1996 Human Factors
Design Guide, DOT/FAA/CT-96/1 [A: https://hf.tc.faa.gov/publications/2003-human-factors-design-standard/]. I read the
2003 chapter, not the 1996 guide, and not revision 001B (2016) [A].
All items below are [D]: https://hf.tc.faa.gov/hfds/download-hfds/hfds_pdfs/Ch7_Alarms_audio_and_voice.pdf
The chapter cites MIL-STD-1472F for most numbers, so these are also the MIL-STD-1472 values as [D-via].

| Rule | Value | Section |
|---|---|---|
| Priority levels for alarm messages | at most 4 | 7.1.2.4 |
| Alarm must give better detection than normal observation | required | 7.1.1.8 |
| Audio alongside a visual display is supportive, it directs attention to the display | required | 7.1.1.12 |
| Auditory alarms for normal conditions | should not be used | 7.2.1.6 |
| Signals so startling they prevent the right response | should not be used | 7.2.1.12 |
| Time filtering against brief threshold crossings | should be used | 7.1.3.6 |
| Test with representative users before adoption | required | 7.2.1.8 |
| Above ambient | at least 10 dB(A), or 5 dB(A) above any 30 s maximum | 7.2.8.3 |
| Alternative form | 10 dBA above ambient or 20 dBA above masked threshold, in one octave band, 200–5000 Hz | 7.2.7.1 |
| Upper limit, emergency | 115 dB(A) | 7.2.8.4 |
| Upper limit, all other signals | 90 dB(A) | 7.2.8.4 |
| Critical voice | at least 20 dB above speech interference level, at most 90 dB(A) | 7.3.2.1 |
| Speech signal to noise | at least 5:1 | 7.3.2.2 |
| Warning frequency | 200–5000 Hz, preferably 500–3000 Hz | 7.2.7.2 |
| Two-element signal | 0.5 s alert, then all key information in the first 2 s | 7.2.6.1 |
| Minimum warning signal duration | 0.5 s | 7.2.6.4 |
| Absolute identification | at most 4 signals | 7.2.2.1 |
| Critical voice repeat | pause at most 3 s until corrected or overridden | 7.3.4.6 |
| Voice style | formal, impersonal, not confusable with radio | 7.3.4.4, 7.3.4.5 |
| Non-critical alarm | simple way to turn off, displayed message stays | 7.2.9.2 |
| Volume control | must not reach inaudible or too loud | 7.2.8.6 |
| User-set thresholds | not allowed where safety is affected | 7.2.1.10 |

Exhibit 7.2.1.7 rates speech as poor for tracking. Tones or a display are better for continuous tracking. This
supports needles for tracking and voice for discrete changes.

### 1.5 SAE ARP4033, ARP4102

Paid documents. I could not read them. Abstract level only [A]:
https://saemobilus.sae.org/content/ARP4102/4, https://saemobilus.sae.org/content/ARP4033
ARP4102/4 gives design criteria for flight deck alerting. ARP4033 gives a top-down pilot-system integration method.
No numbers obtained.

---

## 2. Closest real analogue: EGPWS Mode 5 and the priority tables

### 2.1 Mode 5 "GLIDESLOPE"

Source: Honeywell MK V & MK VII EGPWS Pilot Guide, 060-4241-000 Rev. D, March 2000, printed pp. 19–20 [D].
https://lso.fe.uni-lj.si/literatura/Razno/Avionika/radar/EGPWS.pdf. This is an unofficial host and an old revision.

| Item | Soft alert | Hard alert |
|---|---|---|
| Height | below 1000 ft radio altitude | below 300 ft radio altitude |
| Deviation below the beam | 1.3 dots or more | 2 dots or more |
| Voice | "GLIDESLOPE" at half volume | louder "GLIDESLOPE, GLIDESLOPE" |
| Repetition | a further call for each 20 % increase in deviation, progressively faster | every 3 s until the hard envelope is exited |
| Visual | caution lights | caution lights stay on until deviation is below 1.3 dots |

- **Half volume in dB.** About −6 dB against the other alerts: UK CAA report, Clapp and Howson, April 2017, section 4.5
  [D]. https://www.caa.co.uk/publication/download/16084. That report is about helicopters (MK XXII).
- **Enable logic [D].** Localizer within 2 dots, gear and flaps selected, Glideslope Cancel not active, front course.
- **Upper limit [D].** 1000 ft for descent rates above 500 ft/min, reduced to as low as 500 ft below that rate. This
  avoids alerts during late intercepts.
- **Low limit [D].** Both levels desensitised below 150 ft to allow for normal beam variation and to reduce nuisance
  alerts.
- **Cancel [D].** Pilot switch cancels Mode 5 below 2000 ft AGL. It resets below 30 ft or above 2000 ft. The alternate
  switch needs a cockpit annunciation that cancel is active.
- **Only below the beam.** No above-beam alert exists in this mode [D]. Being high is not called. [Y] Our "above path"
  should weigh less than "below path".
- **Period.** TSO-C151c table gives "Glideslope" a 3 s period [D-via, FAA section 4.3 Table 4.3.1].
- **Field data.** 34 % of Mode 5 alerts occurred below 100 ft, many from pilots ducking under the path. Higher alerts
  often came during localizer intercept below 1000 ft [D]. IATA/Honeywell Performance Assessment, 2019:
  https://www.iata.org/contentassets/06377898f60c46028a4dd38f13f979ad/iata_guidance_performance_assessment_of_pilot_response_to_egpws.pdf
  The data is Honeywell's, not independently verified by IATA [D].

### 2.2 Callouts and "MINIMUMS"

Same pilot guide, pp. 21–22 and 43–44 [D].

- Mode 6 callouts have no visual alert. Each callout is said once per approach.
- "MINIMUMS" takes priority over altitude callouts when they overlap.
- Installation options reduce Mode 6 volume by 3 dB or 6 dB, plus a further 6 dB low-volume option. So routine
  callouts are built to be quieter than alerts.
- Approach options include "PLUS HUNDRED" at DH+100 ft, "APPROACHING MINIMUMS" at DH+80 ft.

### 2.3 Ranking: one voice at a time

- EGPWS: a higher message starts before, or immediately overrides, a lower one, even mid-word. Pilot guide pp. 39–40
  [D].
- TSO-C151c Table 4-2 order [D-via, FAA section 4.3]: reactive windshear (1), pull-up warnings (2–3), …, Minimums (10),
  Altitude callouts (14), Sink rate (17), Don't sink (18), Glideslope (19), Approaching minimums (21), Bank angle (22),
  reactive windshear caution (23). "Minimums" ranks far above "Glideslope".
- TCAS: windshear and GPWS have higher priority. TCAS aural alerts are inhibited while those are active [D].
  Introduction to TCAS II Version 7.1, Feb 2011: https://skybrary.aero/sites/default/files/bookshelf/3340.pdf
- TCAS inhibits near the ground [D, same booklet]: Increase Descent RA below 1450 ft AGL, Descend RA below 1100 ft AGL,
  all RAs below 1000 ± 100 ft AGL, all aural annunciations below 500 ± 100 ft AGL. Even a collision system goes quiet
  on short final.
- Flight director. I found no source that ranks it. [Y] It is silent, shown continuously, and carries no alert logic.
  This is the role of our needles and target.

### 2.4 The real baseline for this task: a human PAR controller

FAA JO 7110.65, section 5-12, read from an unofficial mirror because faa.gov refused the fetch [D-f]:
https://pointsixtyfive.com/xenforo/wiki/05-12. The official text confirms the 5 s line as a snippet [A]:
https://www.faa.gov/air_traffic/publications/atpubs/atc/atc0512.html. Revision of the mirror not checked.

- Transmissions on precision final about every 5 s (5-12-4.a).
- Position words: ON GLIDEPATH, ON COURSE; SLIGHTLY or WELL above, below, left, right.
- Trend words: GOING above; HOLDING; CORRECTING; COMING DOWN; modified by RAPIDLY or SLOWLY (5-12-4.b).
- Heading is given as a value. Range at least once per mile. "AT DECISION HEIGHT" at DH.
- The controller tells the pilot not to acknowledge further transmissions (5-10-10) [D-f]:
  https://pointsixtyfive.com/xenforo/wiki/05-10
- Lost communications interval on PAR final: 5 s (5-10-4) [D-f]. Pilot then tries another frequency, goes VFR if able,
  or flies a nonradar approach or the published lost communications procedure.

[Y] Two results follow. First, the words of a PAR controller are mostly status words, so status wording is true to
the task. Second, a PAR pilot treats 5 s of silence as a failure, so a silent cue needs a visible sign of life.

---

## 3. Sound level numbers

### 3.1 Patterson

Read: Patterson, Phil. Trans. R. Soc. Lond. B 327 (1990) 485–492 [D].
https://www.pdn.cam.ac.uk/system/files/documents/AuditoryWarningsAtWork_RSoc1990.pdf
The 1982 CAA Paper itself was not readable. Its content below is [D-via].

- Spectral components must be 15 dB above the threshold set by the noise. Four or more components at that level.
- Upper bound about 10 dB above the lower bound. So the band is 15–25 dB above masked threshold.
- On a Boeing 727 at 240 kt the 1–2 kHz band needs components above 85 dB SPL.
- Sounds above 85 dB SPL are aversive for most people.
- Some warnings went from off to over 100 dB SPL in under 10 ms. Instantaneous responses often prove incorrect.
- Rise time 20 ms suggested.
- Start low and raise successive pulses: an arresting warning without startle.
- After two bursts further urgent repetition is "needlessly irritating"; then lower pitch, level and speed, every 4 s or so.
- Two test pilots chose the same level the model predicted.
- Immediate-action sounds should not exceed about six.

Conflict: one survey paper reports a 30 dB limit for Patterson's model [A, Peryer et al.,
https://www.researchgate.net/publication/250158978_Auditory_Alert_Characteristics_A_Survey_of_Pilot_Views]. The 1990
paper gives about 25 dB. Use 25 dB.

Pulse details from CAA Paper 82017 [D-via, FAA section 4.1]: pulses 100–150 ms, 20–30 ms onset and offset; inter-pulse
gap under 150 ms for urgency, over 300 ms otherwise; 5 or more pulses; more than 4 harmonics.

### 3.2 Why "15 dB" must not be applied to dB(A)

Patterson's figure is above masked threshold per spectral component. It is not above overall dB(A).
MIL-STD-1472F as cited in HFDS 7.2.7.1 treats "10 above ambient" and "20 above masked threshold" as alternatives.
[Y] This implies masked threshold ≈ ambient dB(A) − 10 dB. It is a rough proxy, not a measurement. On that proxy,
Patterson's band becomes ambient +5 to +15 dB. Three independent numbers agree with this:

- Speech at least 5 dB above ambient (McAnulty 1995) [D-via, FAA section 4.3].
- MIL-STD-1472F 10 dB above ambient [D-via, HFDS].
- Pilots' own radio level sits 7–11 dB above ambient (table below) [D-f].

The AC's "20–30 dB above ambient" for onset is higher than this band. I read it as an accepted upper case, not a target.

### 3.3 Cockpit noise

Radio at the ear sits 7–11 dB above ambient on all nine types. Table 2 of "Noise exposure and auditory thresholds of
German airline pilots" (Hoffmann data), one airline [D-f].
https://pmc.ncbi.nlm.nih.gov/articles/PMC5777454/. No breakdown by flight phase. Older types.

| Aircraft | Ambient dB(A) | At ear in ATC time dB(A) | Difference dB |
|---|---|---|---|
| A310-200 | 74.9 | 83.5 | 8.6 |
| B767 | 74.4 | 83.8 | 9.4 |
| B737-200 | 76.8 | 83.8 | 7.0 |
| MD11 | 75.0 | 85.8 | 10.8 |
| B737-300 | 77.3 | 85.8 | 8.5 |
| B757 | 75.1 | 86.0 | 10.9 |
| DC10 | 76.8 | 87.6 | 10.8 |
| B747 | 79.9 | 88.0 | 8.1 |
| A310-300 | 76.7 | 88.1 | 11.4 |

Same paper, earlier work: 71–76, 71–79, 75 (A310) to 84 (B727) dB(A). Propeller cockpits average 95 dB(A) (Gassaway).
C-130: 111.9 dB near the co-pilot, weighting not stated, undated trade article [A, flightglobal.com]. Do not use.
Speech begins to suffer above 88 dB(A), SIL 78 (FAA AC 20-133, 1989) [A].

### 3.4 Speech

- Rate about 156 words per minute, not above 178 or below 123 (McAnulty 1995) [D-via, FAA section 4.3].
  So 3 words take about 1.15 s, between 1.0 s and 1.5 s across the range [Y].
- Rate affected response time and pilot ratings, in helicopter pilots in noise. Pitch had no significant effect
  (Simpson and Marchionda-Frost 1984) [D-f abstract, https://ntrs.nasa.gov/citations/19850039460]. The rates tested
  were not in the abstract.
- Monotone inflection avoids the distraction of urgent-sounding speech (Boucek 1980) [D-via].
- If voice has several functions, put a tone before warnings (Stokes, Wickens and Kite 1990) [D-via].
- Pilots preferred a short non-speech sound, then voice, and said loud continuous alerts distract (Peryer et al. 2005)
  [D-via, Ruskin et al. review, https://rosap.ntl.bts.gov/view/dot/59041/dot_59041_DS1.pdf].
- Voice is best when the eyes are elsewhere; messages should be brief (HFDS 7.3.4.3, CAA Paper 82017) [D, D-via].
- Word priority: intelligibility, then descriptiveness, then brevity (HFDS 7.3.3.2) [D].

### 3.5 Startle

- Fast rise is what triggers startle: traditionally less than 15–25 ms [A, ScienceDirect review, Carlsen et al.,
  https://www.sciencedirect.com/science/article/abs/pii/S014976341000093X].
- Startle magnitude starts to rise around 80 dB SPL in a mammal review [A,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7075047/]. Probe stimuli in humans are 95–105 dB with instant rise [A].
- I found no study of a startle threshold for pilots in cockpit noise. So no pilot number exists here.
- [Y] The AC's 20–30 ms ramp sits at the edge of the startle range. Use 30 ms, not 20 ms.

---

## 4. Reaction times, eyes and scan

| Measure | Value | Tag and source |
|---|---|---|
| ACAS first RA | begins within 5 s, 0.25 g, to 1500 ft/min | [D] TCAS II v7.1 booklet |
| ACAS later RA | within 2.5 s, 0.35 g, to 2500 ft/min | [D] same |
| EGPWS pilot response, pitch rise above 1.4° | histograms peak at about 2 s | [D-f] FSF, https://flightsafety.org/asw-article/a-la-mode/; [D] method in IATA 2019 |
| EGPWS caution against warning | response time very similar | [D] IATA 2019 |
| Alert in the final 5 s of flight | not enough time to respond | [D] IATA 2019, citing studies |
| Aural against visual ATC message, acknowledge | about 1.5 s faster, not significant, 14 airline pilots | [D] Latorella 1998 |
| Data link acknowledge | average about 10 s (Kerns 1990) | [D-via] Latorella 1998 |
| Simple RT auditory, visual | about 284 ms, 331 ms, 14 subjects | [D-f] Shelton and Kumar 2010, https://www.scirp.org/html/4-2400003_2689.htm |
| Visual attention on panel, GA flight, 15 instructors | about 60 % | [D] Helleberg and Wickens 2003 |
| Mean dwell, airline pilots against novices | 1.1 against 1.51 (units not stated in the extract; seconds assumed) | [D-f] Lounis et al. 2021, https://pmc.ncbi.nlm.nih.gov/articles/PMC7891757/ |
| Dwells per landing, pilots against novices | 188 against 137.5 | [D-f] same |
| Our model, reaction 3 s | 97 of 100 reach minimums | [K] TECHNICAL.md |

Note on the 2.5 s line: the request said 0.25 g for later RAs. The booklet says 0.35 g. An ICAO document says 0.25 g
for later RAs except reversals and increase-rate RAs, which take 0.35 g [A,
https://www2023.icao.int/NACC/Documents/Meetings/2024/GTE24/GTE24-P03.pdf]. The ICAO URL gave 404 on fetch.

Other findings:

- Experts dwell for shorter times, visit instruments more often, and adapt the scan to the task (Bellenkes, Wickens,
  Kramer 1997; 12 experts, 12 novices) [A, https://pesquisa.bvsalud.org/portal/resource/pt/mdl-9215461]. Lounis agrees
  [D-f]. [Y] An expert scan is fast and regular. A cue must fit into one short dwell.
- HUD: identical symbology head-up cost about 2.5 s more to detect an unexpected runway incursion (Wickens and Long)
  [A, McCann SAE 94 snippet; the PDF failed to fetch twice]. The meta-analysis says the cost appears only for unexpected
  events [A, https://saemobilus.sae.org/content/2000-01-5542]. [Y] Compelling symbology can tunnel attention, so a cue
  must not pull the eyes from the search for runway lights.
- Head-down time limit for pilots: I found none. The car rule is 2 s per glance, 12 s total (NHTSA 2013, voluntary) [A].
  This is an analogy only.
- ALAR 7.1 and related notes: at transition to visual the PF must concentrate on visual references; the PNF stays on
  instruments and calls excessive deviation [D, https://flightsafety.org/wp-content/uploads/2019/05/fsd_aug-nov00.pdf].
- [Y] Voice is only about 50 ms faster than vision in the laboratory, against a 2–5 s pilot response. The case for voice
  is that it works when eyes are elsewhere, not that it is quicker.
- [Y] Caution and warning give the same EGPWS response time. So a louder call does not buy a faster pilot.

---

## 5. Nuisance and intrusion

### 5.1 Cry wolf and false alarms

- Cry wolf: operators disable or ignore unreliable alarms, more so at high workload (Breznitz 1984; Bliss 2000)
  [D-via, Ruskin et al.].
- About 90 % of participants did not respond to every alarm (Bliss et al. 1995) [D-via]. Their response rate tends to
  match alarm reliability [A]. Telling operators the reliability, or raising urgency, improved response [A].
- 24 pilots, 75 % true alarms: slower, less frequent responses [A, Bliss, snippet only].
- Automation below about 70 % reliability is worse than none (Wickens and Dixon 2007) [D-via, plus A].
- False alarms can hurt trust more than misses [D-via].
- Low base rate makes most alarms false, even with a good detector (Parasuraman et al. 1997) [A].
- Graded alarms: likelihood displays (Sorkin et al. 1988) [A]. The FAA nuisance study recommended prototypes with
  gradations of urgency or likelihood [D-via]. Results are mixed; one study found they can amplify cry wolf [A].
- Counter-evidence: Wickens et al. 2009 found no strong cry-wolf effect in controllers, who often acted before the alert
  [D-via]. I did not read Breznitz, Sorkin or Bliss.

### 5.2 Real rates

| System | Figure | Tag |
|---|---|---|
| Helicopter TAWS design target | nuisance alerts below 1 in 100 flights | [D] CAA 2017 |
| EGPWS Mode 4 | 57 % false, from faulty inputs | [D] IATA 2019 |
| ATC conflict alerts | 81–87 % nuisance or unnecessary | [D-via] Ruskin et al. |
| ATC low altitude alerts | 87–97 % nuisance or unnecessary | [D-via] same |
| Our DELAYED or INVALID in clean runs | 0 of 100 runs | [K] TECHNICAL.md |

[Y] 0 of 100 only shows the true rate is below about 3 % at 95 % confidence. This does not yet prove the 1 in 100 target.

The CAA report also says a higher nuisance rate may be acceptable for soft alerts than for hard alerts [D].

### 5.3 The key definition for the 20-year pilot

Nuisance alarms can occur when the person is already aware of the problem and acting on it (Wickens et al. 2009)
[D-via, Ruskin et al.]. In the FAA data most controllers who responded did so before the alert [D-via].

[Y] This is the closest evidence to the user's concern. The cue is patronising when it is correct but late: the pilot
has seen it and is already correcting. So "closing" must lower intensity.

### 5.4 Attention and modality

- Multiple resource theory: resources separate by stage, code and modality, plus focal and ambient vision (Wickens 2008)
  [A]. It predicts voice should help a visual task.
- Auditory preemption says the opposite. A discrete voice message pulls attention from the ongoing visual task. In
  Helleberg and Wickens 2003, voice-only was most disruptive to traffic monitoring and flight path tracking, and adding
  voice to text gave no gain over text alone [D, https://www.interruptions.net/literature/Helleberg-IJAP03.pdf].
  Caution: pilots there took notes and read back. Ours do neither.
- Same finding for digit tasks; the preemption cost did not grow with message length (Wickens, Dixon, Seppelt 2005)
  [A]. The auditory advantage appeared at eccentricity above 15° [A].
- Latorella 1998: aural interruptions are more compelling; same-modality conditions produced more errors [D,
  https://www.interruptions.net/literature/Latorella-NASA-98-42hfes-kal.pdf].
- Too loud was the most common cause of alert-related ASRS incidents, missed alerts the second (Mitman et al. 1994)
  [D-via, FAA section 4.1].

[Y] Each voice call has an attention cost on the flying task, whatever its content. The design goal is few calls, not
gentler calls.

### 5.5 Command or status

- Status against command display, 27 pilots, in-flight icing: both helped when accurate. Wrong advice cost most with
  command displays. Authors favour status displays unless reliability is perfect (Sarter and Schroeder 2001) [A].
- Status 95 %, status plus recommendation 86 %, recommendation only 80 % correct (Crocoll and Coury 1990) [A, garbled
  snippet. Do not quote].
- Automation bias: pilots follow wrong automated advice (Mosier et al. 1998) [A]. I found no support for "experts are
  worse".
- Direct study of experienced pilots and intrusive advice: none found. This is a real gap, not an omission.

[Y] Status words respect the pilot's authority. They also fail safer, because our main blind spot is an uncaught small
radar jump (TECHNICAL section 5), and a status word invites a cross-check where a command word does not.

### 5.6 Stable approach gates and deviation callouts

FSF ALAR Briefing Note 7.1 [D, https://skybrary.aero/sites/default/files/bookshelf/864.pdf]:

- Stable by 1000 ft in IMC, 500 ft in VMC.
- ILS within one dot of glideslope and localizer.
- Sink rate at most 1000 ft/min. Speed VREF to VREF+20 kt.
- Only small heading and pitch changes needed.
- At and below the gate, the PM calls if a parameter exceeds the criteria.
- Unstable below the gate: immediate go-around.

FSF Note 1.4 [D, ALAR tool kit]: standard calls should be concise, distinct from cockpit and radio talk, and should be
defined for excessive deviation. Note 7.1 says limits give both pilots a common reference.

Airbus A320 FCOM as quoted by BEA [D, https://bea.aero/fileadmin/user_upload/BEA2020-0417_1.en.pdf, pp. 10–11]: PM calls if
speed is below VAPP−5 kt or above VAPP+10 kt, pitch below −2.5° or above +10°, bank above 7°, vertical speed beyond
−1000 ft/min. PF acknowledges and corrects. One operator's table there uses ±0.5 dot glideslope at its gates [D].

Localizer and glideslope call thresholds differ between sources: ½ dot, or ¼ dot LOC and 1 dot GS [A, non-official
copies]. Use with care. FAA AC 120-71B: not read, faa.gov refused.

Behaviour: unstable approaches are 3.5–4 % of approaches, and only about 3 % lead to a go-around [D, FSF Go-Around
Decision-Making report, March 2017, https://flightsafety.org/wp-content/uploads/2017/03/Go-around-study_final.pdf].
[Y] Experienced crews often press on. A nagging voice will not change this. A clear limit might.

---

## 6. What this says about the present design

1. **On-path voice.** `TECHNICAL.md` section 1.7 says voice only above 0.5 dot, but scenario A plays `on_path` at
   t = 24 s and t = 83 s [K]. HFDS 7.2.1.6 says no alarms for normal conditions [D].
2. **Voice threshold 0.5 dot.** No real voice system I read starts there. PM calls start near 1 dot or at the crew's
   limit, and EGPWS at 1.3 dots. One operator uses 0.5 dot at its gates [D].
3. **4 s spacing.** This is shorter than the 5 s first-response allowance in ACAS and the human PAR interval.
4. **Imperative words.** TURN, DESCEND MORE are commands. Real soft alerts and PAR position calls are status words.
5. **Fault calls without a limit.** The AC and Patterson both warn against this.
6. **"RESTORED" voice.** A return to normal. Visual only is enough.
7. **LOST at 5 s.** This now has a source: 7110.65 5-10-4 [D-f]. But the procedure is a lost communications procedure,
   not simply a go-around. `TECHNICAL.md` section 6 can be updated once the official text is checked.
8. **2-dot limit against the 1-dot gate.** ALAR calls for a go-around outside 1 dot below the gate. We continue to
   2 dots. Say why, or lower the limit.
9. **Dot size near the ground.** From replay and the 2.5° note, I infer 1.25° and 0.35° per dot, as for ILS [Y]. I did
   not open `parcue.py`. Then at 200 ft 1 dot is about 7 m vertical and 25 m lateral. Our 95 % error at minimums, 9 m
   and 25 m [K], is about 1.3 and 1.0 dot. So a normal approach would trigger dot-based alerts near minimums [Y]. EGPWS
   solves the same problem by desensitising low down [D].

---

## 7. Proposed intensity rule

Everything in this section is [Y] unless a source is named. Sources supply the anchors. The weights are mine, tuned to
hit those anchors, and no pilot has tested them.

### 7.1 Inputs, each frame at 1 Hz

| Input | Symbol | Note |
|---|---|---|
| Deviation per axis, dots | v, l | Filtered needle values |
| Height above runway, ft | h | From range and path |
| Data state | q | VALID, DELAYED, INVALID, LOST, OUTSIDE LIMITS (existing) |
| Trend | G | From position only, see below |

**Trend uses position, not rate.** `TECHNICAL.md` section 2 shows the radar rate is too noisy. Compare e now with e 5 s ago:

- Diverging: e rose more than 0.1 dot, G = +0.10.
- Closing: e fell more than 0.1 dot, G = −0.10.
- Holding: G = 0.

This gives the same three words a PAR controller uses: going, correcting, holding.

### 7.2 Calculation

1. **Alert dots.** Needles stay true. Alert logic uses a floor on dot size, so normal error near the ground stays quiet:
   1 alert dot is at least 18 m vertical and 50 m lateral. These are the 95 % errors at minimums doubled, so that
   0.5 dot covers the normal error [K, Y]. The vertical floor acts below about 500 ft, the lateral inside about 1.2 NM.
2. **Asymmetry.** Above the path multiply by 0.75. Below the path 1.0. Reason: Mode 5 has no above-beam alert [D].
3. **Effective deviation.** e = the larger of the two axes.
4. **Deviation score.** D = clip((e − 0.5) / 1.5, 0, 1). Zero at the 0.5 dot edge, 1 at the 2 dot limit.
5. **Height weight.** H = 0.7 at 1500 ft and above, rising in a line to 1.0 at 1000 ft, then 1.0. Reason: PM deviation
   calls apply at and below the stabilisation height [D].
6. **Intensity.** I = 0 if e ≤ 0.5, otherwise I = clip(H·D + G, 0, 1).
7. **Validity override.** Bad data never raises guidance intensity. It replaces it, see 7.4.

### 7.3 Levels

Four levels only (HFDS 7.1.2.4).

| Level | Condition | Anchor at H = 1, G = 0 | Voice | Visual |
|---|---|---|---|---|
| L0 Quiet | I = 0 | e ≤ 0.5 dot | None | Needles only, white. Plot age tick moves. No text |
| L1 Note | 0 < I < 0.25 | up to 0.875 dot | None | Target value steady, small trend arrow |
| L2 Advise | 0.25 ≤ I < 0.50 | 1.0 dot is I = 0.33: the ALAR limit [D] | Once, status words, N + 5 dB | Cyan text, in scan area |
| L3 Caution | 0.50 ≤ I < 1 | 1.3 dots is I = 0.53: Mode 5 soft [D] | Once, N + 11 dB | Amber text, within ±15°, at least 1° high, steady |
| L4 Warning | Raw 2 dots, or LOST | Mode 5 hard, our OUTSIDE LIMITS | Tone then voice, N + 15 dB | Red, at least 2 sq deg, within ±15°, blink 2 Hz for at most 10 s, then steady |

Effect of trend: closing delays L2 to about 1.03 dots and L3 to about 1.40. Diverging brings L2 to about 0.73 dot and L3
to about 1.10.

**Change rules.**

- Raise a level only after 2 frames in a row (HFDS 7.1.3.6 time filter).
- Lower a level only after 5 s below it.
- Visual text changes at most every 5 s, as the targets do now.
- No blink below L4. Blink rates from AC 25-11A [D-via]. At most two blink levels (MIL-STD-1472G) [D-via].
- Red and amber appear only at L3 and L4, and never as decoration (25.1322(f)).
- All L2 text readable in one dwell, about 1 s [Y from Lounis].

### 7.4 Data validity

| State | Level | Voice | Visual |
|---|---|---|---|
| VALID | From I | From level | From level |
| DELAYED | L2, cap on guidance | "DATA DELAYED" once | Needle marked old, target frozen |
| INVALID | L3 | "DATA INVALID" once | Needles removed, flags |
| LOST | L4 | "LOST, GO AROUND" | Needles removed, latched |
| OUTSIDE LIMITS | L4 | "LIMITS, GO AROUND" | Latched |
| Restored | Back to I | None. Normal state | Flags clear |

The go-around wording on LOST is our own rule (see section 6, item 7).

### 7.5 Sound

N = noise at the ear in dB(A), by microphone or preset. Automatic volume control is what the AC recommends [D-via].

    L_voice = min(N + delta, 90 dB(A))
    delta:  L2 +5 dB    L3 +11 dB    L4 +15 dB

| Value | Reason | Tag |
|---|---|---|
| +5 dB | Speech floor; Patterson lower bound on the proxy | [D-via], [Y] |
| +11 dB | L2 + 6 dB, the Mode 5 soft to hard step; top of pilots' own radio margin | [D], [D-f] |
| +15 dB | Patterson upper bound on the proxy | [D], [Y] |
| 90 dB(A) | Non-emergency ceiling. The 115 dB(A) emergency limit is not used | [D] |
| 30 ms | Onset and offset ramp, all levels | [D-via], [Y] |

Worked example, jet at N = 75–80 dB(A): L2 80–85, L3 86–90, L4 90 dB(A). Above N = 79 the cap merges L3 and L4, so the
L4 tone and repetition must carry the difference. In a propeller cockpit near 95 dB(A), N must be the level under the
headset. This is unknown. Measure it.

L4 tone: one 0.5 s tone at 500–3000 Hz, level rising over the first pulses (Patterson; MIL-STD-1472F). No tone at L2 or
L3: the AC does not recommend a master aural for advisories, and caution is one presentation.

### 7.6 Voice rate and repetition

| Level | First call | Repeat needs both | Minimum gap |
|---|---|---|---|
| L2 | On entry | e at least 1.2 × e at last call | 10 s |
| L3 | On entry | e at least 1.2 × e at last call | 5 s |
| L4 | On entry | Every 3 s, at most 3 times, or until acknowledged | 3 s |

- The 1.2 factor is the Mode 5 rule [D]. It needs no rate signal, so it suits noisy radar.
- 5 s: the ACAS first response and the PAR interval [D]. 10 s is two PAR intervals [Y]. 3 s is the Mode 5 period,
  TSO table and MIL repeat rule [D, D-via]. Stopping at 3 repeats is mine, from Patterson's "needlessly irritating".
- Message at most 3 words, about 1.15 s, at 156 words per minute.
- Flat, impersonal voice, different from the radio voice.
- One voice at a time, in this order: aircraft TAWS, windshear and TCAS first (ours is silent during them), then L4,
  MINIMUMS, L3, L2. Wait for radio transmissions to end, except L4.
- Worst-case voice occupancy about 12 % at L2 and 23 % at L3.

### 7.7 Words

| Situation | L2 | L3 |
|---|---|---|
| Below path | "SLIGHTLY BELOW PATH" | "WELL BELOW PATH" |
| Above path | "SLIGHTLY ABOVE PATH" | "WELL ABOVE PATH" |
| Lateral | "SLIGHTLY LEFT" | "WELL RIGHT" |

Terms are 7110.65 words [D-f], shortened on the lateral axis to keep to 3 words. They state position. The heading and
descent targets on the display carry the correction.

### 7.8 Forbidden on the path, and when it is quiet

Forbidden always at L0 and L1, with valid data:

1. Any voice.
2. "ON PATH", "ON COURSE", "GOOD", "CORRECT", "MAINTAIN" or any praise. Normal state, HFDS 7.2.1.6. Show it on the
   display. Remove `on_path` from voice use.
3. Tones, chimes or a heartbeat sound.
4. Any blink, red or amber.
5. Text that demands reading.

Forbidden at every level:

6. Imperative verbs, except GO AROUND. TURN and DESCEND stay as display words only, if at all.
7. Voice at L2 below 300 ft. Below that height the pilot is looking for lights, callouts fill the channel, and Mode 5
   hard starts there [D]. L3 and L4 stay.
8. Any deviation voice after MINIMUMS. Pilot decides, guidance ends.
9. A repeat with no growth in deviation.
10. Duplicate MINIMUMS if the aircraft already calls it.
11. Tense or urgent voice acting.

**Pilot control.** One button, CUE QUIET. It silences L2 and L3 voice for this approach. Display stays. L4 cannot be
silenced. "VOICE OFF" stays in view. Reset on go-around or next approach. Model: Glideslope Cancel [D], 25.1322(c)(3),
NPA 8.b [D]. This is the strongest answer to the 20-year pilot: it is their approach and they can quiet us.

**Sign of life when silent.** A small plot-age tick on the display, updated each second. Brief: silence means on path,
never a fault. Fault is always announced.

**Do not set the thresholds by pilot experience.** HFDS 7.2.1.10 bars user-set limits where safety is affected [D].

### 7.9 Check on the replay [K]

Script applied to `outputs/replay_data.json` offline, after the fact, seed 1 only. Guidance voice means deviation calls,
without MINIMUMS or fault calls.

| Scenario | Valid frames | Present guidance voice | Proposed guidance voice | Proposed call |
|---|---|---|---|---|
| A return to path | 114 | 6 | 1 | L2 at t = 99 s, 0.82 dot lateral, 447 ft |
| B bad data | 98 | 5 | 1 | L2 at t = 100 s, 0.91 dot lateral, 426 ft |
| C guidance lost | 70 | 2 | 0 | none |

- Present counts include `on_path`. The table leaves out MINIMUMS and fault calls: 4 in B (delayed, invalid, 2 restored),
  2 in C (delayed, lost).
- A human controller at one call each 5 s would make about 23 calls in 116 s [Y].
- Without the dot floor, B also gives an L3 at t = 104 s, 1.15 dots, 377 ft. So the floor removes one amber alert from
  a normal approach. Whether this is safe is unproven.
- L3 and L4 never fired from deviation in these replays. The levels are not exercised by them. Add a demo case.
- Demo cost: the first 98 s of A is now silent. The jury may want to hear a voice. Show a larger offset case, or say
  "silence is the feature" and point at the needles.

Not done: 100-seed Monte Carlo. Not done: closed-loop run. I assume voice does not feed the pilot model, because
`TECHNICAL.md` says the pilot follows targets. I did not open `src/`. Verify this before quoting.

---

## 8. Which thresholds are sourced and which are mine

| Threshold | Status |
|---|---|
| 1 dot gate; 1000 ft IMC gate | Source [D] ALAR 7.1 |
| 1.3 dots, 2 dots, 1000 ft, 300 ft, 150 ft, +20 %, 3 s, −6 dB | Source [D] Honeywell, CAA |
| 5 s and 2.5 s response | Source [D] TCAS booklet. Used by analogy |
| 5 s PAR interval | Source [D-f] mirror, [A] official |
| 15–25 dB above masked threshold; 20 ms | Source [D] Patterson 1990 |
| 10 dB(A), 90 dB(A), 0.5 s, 2 s | Source [D] HFDS citing MIL-STD-1472F |
| 20–30 ms; ±15°; 1°; 2 sq deg; 0.8–4 Hz; 10 s | Source [D-via] FAA guidance quoting AC |
| 156 words per minute | Source [D-via] McAnulty 1995 |
| Below 1 in 100 flights nuisance | Source [D] CAA, helicopter TAWS. Borrowed |
| 0.5 dot deadband | Mine. Existing value, one operator matches at its gates |
| 0.75 above-path factor; H weights; ±0.10 trend; 0.1 dot in 5 s | Mine |
| I cut points 0.25 and 0.50 | Mine, set to land on 1.0 and 1.3 dots |
| 18 m and 50 m dot floor | Mine, from our simulated errors |
| Masked threshold ≈ ambient − 10 dB | Mine, inferred from MIL-STD-1472F wording |
| +5, +11, +15 dB ladder | Mine, built on sourced anchors |
| 10 s L2 gap; 2-frame raise; 5 s drop; 300 ft L2 inhibit; 3-repeat stop | Mine |

---

## 9. What we could not read

| Source | Reason | Effect |
|---|---|---|
| FAA AC 25.1322-1 | faa.gov 403; the browser pane answered with a file download, not a page | Read through FAA guidance quoting it |
| JO 7110.65 official; AC 120-71B; AC 20-133 | faa.gov 403 | Mirror for 7110.65; others snippet or unread |
| Final AMC 25.1322 wording | Only first part of the EASA page read | Draft NPA 2009-12 read instead |
| Patterson 1982 CAA Paper; Patterson and Milroy 1980 | Full text not found | 1990 paper read |
| Noise and Health 2000; DTIC ADA145469 | 402, 403 | Snippets only |
| SAE ARP4033, ARP4102 | Paid | Abstract snippets |
| DOT/FAA/CT-96/1; HF-STD-001B; MIL-STD-1472 itself | Not fetched | 2003 HFDS chapter read |
| Breznitz; Sorkin; Bliss papers | 403 or book only | Snippets and Ruskin review |
| Wickens 2008; Wickens and Dixon 2007; Wickens, Dixon, Seppelt 2005 | 404 or not tried | Snippets, one via review |
| Sarter and Schroeder 2001; Crocoll and Coury 1990 | 403 | Snippets |
| Peryer et al. 2005 | 403 | Snippet and Ruskin review |
| Wickens and Long; McCann SAE 94 | Fetch failed twice | Snippet |
| ICAO Doc 9863; ICAO GTE24 paper | Not tried; 404 | TCAS booklet read instead |
| Later Honeywell guide revisions | Not opened; other copies exist (NTSB docket, manualslib) [A] | March 2000 guide, unofficial host |

Numbers I looked for and did not find: a dB value for the Mode 5 hard alert; a pilot startle threshold; a head-down
time limit for pilots; noise at approach power by type; noise under a headset in a military PAR aircraft; luminance or
contrast rules for cue prominence; a direct study of experienced pilots and intrusive advice.

---

## 10. Numbers to use

Limits and rule values, grouped by use.

| Item | Value | Unit | Tag |
|---|---|---|---|
| Stable gate, IMC | 1000 | ft | [D] ALAR 7.1 |
| Stable limit, glideslope and localizer | 1.0 | dot | [D] ALAR 7.1 |
| Soft alert, Mode 5 | 1.3 | dot | [D] Honeywell |
| Soft alert ceiling | 1000 | ft | [D] Honeywell |
| Hard alert, Mode 5 | 2.0 | dot | [D] Honeywell |
| Hard alert ceiling | 300 | ft | [D] Honeywell |
| Soft alert volume | −6 | dB | [D] CAA 2017 |
| Growth for repeat | 20 | % | [D] Honeywell |
| Hard alert period | 3 | s | [D] Honeywell |
| Desensitise below | 150 | ft | [D] Honeywell |
| TCAS aural inhibit | 500 | ft | [D] TCAS booklet |
| ACAS first response | 5 | s | [D] TCAS booklet |
| ACAS later response | 2.5 | s | [D] TCAS booklet |
| EGPWS response peak | 2 | s | [D-f] FSF |
| PAR call interval | 5 | s | [D-f] 7110.65 mirror |
| PAR lost interval | 5 | s | [D-f] 7110.65 mirror |
| Masked threshold margin, low | 15 | dB | [D] Patterson 1990 |
| Masked threshold margin, high | 25 | dB | [D] Patterson 1990 |
| Above ambient, minimum | 10 | dB(A) | [D] HFDS, MIL-STD-1472F |
| Speech above ambient, minimum | 5 | dB | [D-via] McAnulty 1995 |
| Ceiling, non-emergency | 90 | dB(A) | [D] HFDS, MIL-STD-1472F |
| Aversive above | 85 | dB SPL | [D] Patterson 1990 |
| Jet ambient, low | 74 | dB(A) | [D-f] PMC5777454 |
| Jet ambient, high | 80 | dB(A) | [D-f] PMC5777454 |
| Radio at ear, low | 84 | dB(A) | [D-f] PMC5777454 |
| Radio at ear, high | 88 | dB(A) | [D-f] PMC5777454 |
| Propeller cockpit average | 95 | dB(A) | [D-f] PMC5777454, citing Gassaway |
| Onset ramp | 30 | ms | [D-via] AC range 20–30, [Y] choice |
| Speech rate | 156 | words/min | [D-via] McAnulty 1995 |
| Primary field of view | 15 | ± deg | [D-via] FAA guidance |
| Caution visual size | 1 | deg | [D-via] AC 25.1322-1 |
| Warning visual size | 2 | sq deg | [D-via] AC 25.1322-1 |
| Blink, low | 0.8 | Hz | [D-via] AC 25-11A |
| Blink, high | 4 | Hz | [D-via] AC 25-11A |
| Blink cancel after | 10 | s | [D-via] AC 25-11A |
| Priority levels, maximum | 4 | levels | [D] HFDS 7.1.2.4 |
| Nuisance target | 1 | per 100 flights | [D] CAA 2017, borrowed |
| Reliability floor | 70 | % | [D-via] Wickens and Dixon 2007 |
| Voice deadband | 0.5 | dot | [Y] |
| L2 entry, holding | 0.875 | dot | [Y] anchored on 1.0 dot |
| L3 entry, holding | 1.25 | dot | [Y] anchored on 1.3 dot |
| L4 entry | 2.0 | dot | [Y] existing, matches Mode 5 hard |
| Above-path factor | 0.75 | ratio | [Y] |
| Trend window | 5 | s | [Y] |
| Trend step | 0.1 | dot | [Y] |
| Trend term | 0.10 | I units | [Y] |
| Height weight at 1500 ft | 0.7 | ratio | [Y] |
| Alert dot floor, vertical | 18 | m/dot | [Y] from [K] |
| Alert dot floor, lateral | 50 | m/dot | [Y] from [K] |
| L2 voice level | N + 5 | dB(A) | [Y] |
| L3 voice level | N + 11 | dB(A) | [Y] |
| L4 voice level | N + 15 | dB(A) | [Y] |
| L2 repeat gap | 10 | s | [Y] |
| L3 repeat gap | 5 | s | [Y] |
| L4 repeat period | 3 | s | [D] |
| L2 voice inhibit below | 300 | ft | [Y] |
| Message length | 3 | words | [Y] |
| Level raise | 2 | frames | [Y] |
| Level drop | 5 | s | [Y] |
