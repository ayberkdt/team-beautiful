# R5 – Additional canopy / door open-in-flight occurrences: sources and method

- **Date read:** 2026-11-04 (21:06–22:00 laptop time, UTC+3)
- **Read by:** subagent R5
- **Data file:** `R5_occurrences_add.csv` (UTF-8, 95 rows, R2 header, ids R5-001…R5-095, tag `D-ag` on every row). Each row's `notes` field starts with `[family: …]`.
- **Relation to R2:** this file adds rows only. Before writing, `build.py` checks every row against `R2_occurrences.csv` for the same registration + date. It found 0 duplicates. All 105 NTSB Mkeys from R2's CAROL query were removed from the candidate set before triage.
- **Vocabularies and classification rules:** the same as R2. See `R2_occurrences_sources.md`, "Classification rules". Two rules matter most here:
  - A *probable* lock finding ("probably / most probably inadequate locking") is coded `unknown`, with the wording in the notes.
  - Several cases involved an intermediate or "ajar" lock position (F-HKAP, N9261L). These are coded `partially_latched`, the same as R2 coded G-GODV.
- **Downloads:** `D:\tmp_ideathon\easa\dl\occ2\`
  - `ntsb\` (352 PDFs)
  - `ntsb_door\`
  - `for\` (BFU, BEA, AAIB PDFs, BFU open-data CSV and extracted text in `for\txt\`)
  - `pl\` (PKBWL PDFs and text)
  - CAROL query JSONs: `q_*.json`, `d_*.json`
- **Scripts:** `D:\tmp_ideathon\easa\r5_scripts\`
  - `carol_q.py` (paged CAROL query; needs a random SessionId, because `SessionId: 1` now returns HTTP 500)
  - `union.py`, `ntsb_triage.py`, `show.py`, `full.py`, `csent.py`, `scan.py`, `pdftxt.py`
  - `rows_ntsb.py`, `rows_other.py`, `build.py`
  - Rebuild the CSV with: `python -I build.py <triage.json> <R2.csv> <out.csv>`

## Rows added (by investigator)

| Investigator | Rows | Notes |
|---|---|---|
| NTSB | 62 | 61 from the canopy queries, plus 1 Cirrus SR22 door row from a door query |
| BFU (Germany) | 14 | 13 open-data table entries, plus 1 full report (BFU21-0469-3X) |
| BEA | 10 | 4 read as PDFs, 6 read as notified-event web pages |
| PKBWL (Poland) | 8 | |
| AAIB (UK) | 1 | G-DBZZ |

**By cause_class:**
- unknown 35
- not_locked 32
- partially_latched 16
- mechanism_failure 6
- structural 5
- handle_knocked 1

**Lock-related rows (not_locked + partially_latched):** 48 of 95. Of these, 6 were fatal. Phase: initial_climb 27, takeoff_roll 9, cruise 8, approach 3, aerobatics 1.

**By category:** aeroplane 52, glider 34, motorglider 5, microlight 4.

**By outcome:** no_injury 52, fatal 15, serious 14, minor 13, unknown 1.

**warning_fitted = yes (2 rows), and in both the warning gave a false "closed":**
- **N2BD Bede BD-10, CHI94LA288.** The lock pins extended fully and put out the CANOPY OPEN light without engaging the lugs. The NTSB probable cause names the lock-pin design.
- **F-HSAB PS-28 Cruiser, BEA2016-0281.** The switch senses the lever, not the latches, so the partial lock gave no alarm (§2.1 and §3).

These two join R2's N6161 and G-IIDY pattern: a warning that confirms the handle position, not the latch engagement.

**Priority-type families present:**
- Extra (N330SB EA 300/LT 2026; SP-HMM Extra NG 2023)
- Cap 10/20/232 (F-OGXN, F-AZNZ, F-HKAP)
- Vans RV (5)
- Grob G102/G103/G109 (17)
- Robin (F-BRZM)
- Cirrus (N213CP door)
- Aero L-39 (N602MC)
- Schleicher ASK/ASW (4)
- Schempp-Hirth Discus/Ventus/Cirrus/Nimbus (5)
- SZD Bocian/Perkoz/Foka (5)
- Evektor/Czech Sportcruiser (6)
- Pipistrel, Ikarus C42 (microlights)

No new rows were found for Zlin, Yak-52/18T, Sukhoi, Pitts, Slingsby T67, Diamond DA20/40/42/62, Bulldog, Chipmunk, Tucano/Tutor or Jet Provost (see Gaps).

## Sources, queries, counts

### NTSB CAROL (systematic)

**Queries.** POST `https://data.ntsb.gov/carol-main-public/api/Query/Main`, with every term AND-ed and each term "contains". Hit counts are `ResultListCount`; "capped" means the API set `MaxResultCountReached=true`.

- **`Narrative.Analysis` contains "canopy" AND:**

| Second term | Hits |
|---|---|
| unlatched | 26 |
| "not latched" | 4 |
| unlocked | 6 |
| "not locked" | 1 |
| opened | 107 |
| "came open" | 16 |
| open | 190 |
| separated | 86 |
| departed | 64 |
| lock | 77 |
| locked | 36 |

- **`Narrative.Factual` contains "canopy" AND:**

| Second term | Hits | Used? |
|---|---|---|
| latch | 170 | yes |
| latched | 89 | yes |
| unlatched | 43 | yes |
| unlocked | 19 | yes |
| locked | 117 | yes |
| opened | 174 | yes |
| open | 418 (capped) | no |
| separated | 509 (capped) | no |
| departed | 476 (capped) | no |
| lock | 324 (capped) | no |

- **Door / type queries (Analysis):**

| Terms | Hits |
|---|---|
| door + opened + DA40 | 0 |
| door + opened + Cirrus | 2 |
| door + unlatched | 33 |
| canopy + Extra | 4 |
| Factual "Extra NG" | 2 |

**Funnel.**
- **Candidate set.** The union of the uncapped canopy queries, minus R2's 105 Mkeys, gave **392 new cases** (`cand.csv`).
- **Filtered by make without download:** 39 helicopter and jet makes (Bell, Robinson, Hughes, Hiller, MD, Eurocopter, Sikorsky, Lear, Boeing and others).
- **Downloaded:** 352 of the remaining 353 PDFs. Mkey 84014 (CEN12FA378, IAR IS-28B2 glider, fatal) returned 403 twice; this is a gap.
- **Triage.** A script pulled every Analysis sentence that mentions canopy, door or hatch together with a latch, lock, open, separate or depart word, plus the Probable Cause.
  - **137 cases had such a sentence.** R5 read each of these. Where needed, R5 read the full Analysis and Findings with `full.py`.
  - **215 cases had no such sentence.** A second regex scan looked for "came open", "unlatched", "opened in flight" and similar wording in the full text of the 59 priority-type cases among them. It found only one lead (Extra NG, below). The remaining zero-hit cases were not opened individually.
- **Kept 61 + 1 = 62.**

**Excluded after reading (about 76), by reason:**
- **Parachute canopies:** BRS, CAPS, skydiver and powered-parachute wings (for example 6089, 33339, 84828, 49151, 87837).
- **Canopy opened deliberately** for smoke, fire, egress, ditching or bailout (for example 61899, 42230, 59028, 98148, 103581, 103700, 67652, 102696).
- **Canopy separated or broke in a breakup or impact** (for example 35106, 3658, 88095, 96636, 100861, 104670, 15205*, 59106, 82381).
  - *15205 KR-2 is kept: the NTSB names "total failure of the canopy" as a factor.
- **Jettison or bailout:** 29615 DG-300, 53740 Pitts S-1S, 19632 Su-29, 67990 EA-300/L, 89616 Raven.
- **Taxi or ground event:** 34442 Varieze (canopy fell while back-taxiing), 30721 SGS 1-34.
- **Opening was secondary to another failure:**
  - 24082 HP-18 (canopy loosened after a bounce)
  - 20599 BD-5B (prop-induced vibration; R2 excluded a similar case)
  - 70584 is kept
  - 61876 Atlantis (wing struck runway first)
- **Ercoupe** (designed to fly with the canopy open): 30915, 68828.
- **100408 RV-4 2019.** The canopy separated after takeoff on an earlier flight. The fatal accident happened two days later, flown deliberately without a canopy. The canopy-loss date is not given, so there is no row.
- **65683 Zodiac 601XL 2007.** The lock was found unlocked, but the NTSB found an in-flight breakup in weather.
- **90592 RV-9A.** The lock was found open, but the canopy was ejected on impact. The NTSB found a stall on climb; canopy opening is not stated.
- **24472 Ganador.** Landed with the canopy open after a propeller counterweight failure.
- **98276 Lockheed.** Canopy deliberately cracked open on landing.
- **Door query (`d_unlatched`, 33 hits).** Only priority types were opened: 73493 Cirrus SR22 was kept; 52469 Yak-52 was a fuel door; 93486 Decathlon was a cowl door. The Piper, Beech, Cessna and Mooney door hits were not reviewed (gap).

### BFU Germany

**Sources.**
- **WebSearch** (bfu-web.de):
  - "BFU Untersuchungsbericht Kabinenhaube nicht verriegelt Start geöffnet"
  - "bfu-web.de Bulletin Haube öffnete sich Start Segelflugzeug Windenstart nicht verriegelt"
  - "BFU Untersuchungsbericht Extra 300 OR Pitts OR Yak-52 OR Cap 10 Haube geöffnet Flug"
- **BFU open data** `Tabelle_GA_B1-download.csv` (GA events under 5.7 t, 1998–2010, 3,553 lines, with a `Kurzdarstellung` column). Grepped for Haube, Kanzel, Kabinentür, Cockpittür and Tür.
- **`Tabelle_GA_B2`** (2011 onward) has almost no descriptions (3 non-empty), so it could not be used.

**Kept 14.**
- 13 table entries. Investigator: "BFU (Germany) - open-data table entry". The URL is the CSV; the section is the Aktenzeichen.
- 1 full report: **BFU21-0469-3X**, G 103 C, 23 Jun 2021, fatal. The front-canopy lock lever was vertical (unlocked) on video during the winch launch; the canopy opened on final.

**Method caveats for the table rows.**
- Per-case BFU PDFs were not located. Guessed `Bericht_3X…-0.YY.pdf` URLs returned 404.
- The row content is only the BFU's own short summary, so the cause is mostly `unknown`.
- BFU does not publish registrations, so these rows have `registration = unknown (not published)`. Duplicate checking against other sources therefore relies on date + type + place in the notes.

**Excluded.** Rows that mention a canopy but describe something else:
- canopy damaged on landing or outlanding (for example 3X225-98, 3X081-00, 3X118-01)
- 3X017-99 CAP10: canopy broken in aerobatics by a bird strike
- 3X284-99: not a canopy event
- Aquila AT01 Plön 2006 and Smaragd 2005 reports: canopy destroyed at impact only

### BEA France

**Queries:**
- "BEA rapport verrière ouverte en vol décollage non verrouillée planeur OR CAP 10 OR Robin"
- "bea.aero evenements-notifies verrière ouverture en vol mal verrouillée"
- "bea.aero ouverture de la verrière au décollage perte de contrôle planeur verrière non verrouillée"
- "bea.aero verrière en vol Extra OR Pitts OR CAP 232 OR Yak OR DR400 OR DA40 incident ouverture"

**Kept 10.**
- **PDFs read directly:**
  - F-HKAP (BEA2025-0235)
  - F-HSAB (BEA2016-0281)
  - F-CLBG (BEA2019-0656)
  - F-CFKD (f-kd040702)
- **Notified-event pages read through WebFetch.** WebFetch passes the page through a summarising model, so wording may be paraphrased; key French quotes were requested and are reflected in the notes.
  - 27-YR
  - F-OGXN
  - F-AZNZ
  - F-BRZM
  - F-CNKI
  - D-KAPX (investigation in progress, 50 %)

**Excluded as R2 duplicates:**
- BEA2017-0269 = 68-US (17 May 2017; R2 secondary row)
- 73-OH
- F-WGJP
- D-EFBY
- 77AUM
- 59CVF

### PKBWL Poland

**Query:** "PKBWL raport owiewka kabiny otwarła się w locie start niezamknięta". The 11 PDFs from the results were downloaded and read.

**Kept 8:**
- SP-HMM 4 Aug 2023 (2023-0061 uchwała)
- XA-42 2016
- Bocian 2013, 2019 and 2024
- Perkoz 2018
- Sportstar 2015
- Virus SP-SWWW 2016

**Excluded:**
- **20162421RK** Extra 300SC, Mielec, 11 Sep 2016: the canopy opened in propwash *while taxiing*; cause improper closing.
- **20171667RK** Extra 300/L, EPPK, 18 Jul 2017: canopy destroyed during taxi; cause "imprecise closing"; contributing: no hand-lift check.
- Both are outside the "in flight / take-off" scope but relevant to a "not locked" alert that would sound at taxi.
- **2023_0061_RK** is the final-report file for the same SP-HMM event as the uchwała. One row only.
- **2022-1097** (SP-HMM, 2022) is already in R2.

### UK AAIB

**WebSearch queries** (assets.publishing.service.gov.uk / gov.uk):
- "Yak-52 canopy opened in flight"
- "Pitts canopy opened takeoff not locked"
- "glider canopy opened launch unlocked ASK 21 OR Discus OR DG OR K13"
- "Bulldog OR Chipmunk OR Grob 115 canopy opened in flight"
- "canopy opened takeoff Vans RV-7…RV-14"
- "Robin DR400 OR HR200 OR R2160 canopy came open"
- "glider canopy opened aerotow winch K-21…"
- "Diamond DA42 OR DA40 OR DA20 canopy opened takeoff"

**gov.uk API queries:** `filter_format=aaib_report` with `q` = "canopy came open", "canopy unlatched", "canopy not latched", "canopy separated", "canopy lost", "canopy opened in flight", "door came open", "door opened in flight", "canopy latch", "canopy lock". This gave 31 title/description hits, all already in R2 or out of scope.

**Kept 1:** G-DBZZ (5/2011). The canopy opened on final as the airbrakes were extended, on the first flight of the day. The later fatal flight that day was a rigging accident and is not this row's outcome.

**Opened and excluded:**
- **G-DDGX** (6/2020): canopy detached in the accident sequence; the tailplane was the issue.
- **G-CFWC** (2/2023) and **G-CHBB** (7/2024): canopy damage at impact only. In G-CHBB the release levers were found partly open, but damage indicated otherwise.
- **G-YAKW, G-BYXJ, G-BYXR:** read from search snippets only. G-BYXJ's canopy departed after a propeller blade separation (secondary). G-BYXR's handle was opened before impact for egress.

### ATSB, TSB Canada, SUST, ANSV, CIAIAC, DSB

- **ATSB:** WebFetch timed out (60 s) and curl returned code 000. **No rows.**
- **TSB:** curl returned 403. **No rows.**
- **SUST:** queries in German ("Kabinenhaube öffnete sich im Steigflug nicht verriegelt") and French ("verrière ouverte décollage non verrouillée") returned only cases R2 already has (2087 OE-AKG) or off-topic reports. **No rows.**
- **ANSV, CIAIAC, DSB:** queried once each. **No primary report read.** See leads.

## Leads only (not in CSV)

These have no investigator report read, or were not investigated.

1. **ATSB AO-2013-158**, VH-ALP Lancair Legacy, Geraldton, 18 Sep 2013, fatal. Takeoff with canopy down but inadvertently unlatched (search summary). Site unreachable.
2. **ATSB AO-2014-164**, VH-JON RV-6A, Moorabbin, 14 Oct 2014, fatal. Canopy likely opened in flight; lock state not established. **ATSB AB-2018-007**, DA42, Parafield, 18 Jan 2018 ("aircraft preparation"; canopy). ATSB news item 2022, "Open canopy leads to fatal takeoff". All unreachable.
3. **DSB (Netherlands), Kornhorn fatal crash** (sport aircraft; canopy very probably not properly closed at takeoff). The manufacturer recommended a safety hook plus sensor in 2019, and the DSB recommended making it mandatory. Read from news summaries only (nos.nl, hartvannederland.nl). It may be the same airframe as R2's PH-4E7 (WT9) row; not verified.
4. **ANSV I-ISAM** (aerobatic aircraft). Canopy lock handle found unlocked; a partial opening during a manoeuvre was considered possible but unlikely. Search summary only.
5. **BFU15-0722-3X**, Schleicher ASK 16 motorglider, Wiefelstede, 14 Jun 2015. Canopy opened in initial climb; landed in a hedge (BFU Bulletin 06/2015, p14). The bulletin says "Keine Untersuchung durch BFU" (not investigated), so it was excluded under the primary-report rule.
6. **BFU17-0890-4X**, glider, Höfen (Austria), 8 Jul 2017. Canopy came loose after the winch launch; the pilot held it with his left hand; wing-tip ground contact on approach (BFU Bulletin 07/2017, p12). Investigated by the Austrian authority; that report was not read.
7. **BFU 3X185-02**, Dallach D4 microlight, 14 Aug 2002, fatal. Canopy fragments found several hundred metres from the wreck three minutes after takeoff. The sequence (canopy loss or breakup) is not stated in the table.
8. **Extra NG canopy opened during takeoff.** Mentioned in NTSB WPR24FA156 (N22MW EA 300/L, Factual: "the pilot recently had a mishap with his own airplane, an Extra NG, where it was damaged when the canopy opened during takeoff"). No separate investigator report was found (CAROL Factual "Extra NG" returned only WPR24FA156 and ERA22FA141, which is not a canopy case).
9. **AAIB G-BFJZ** DR400/140B, Headcorn, 14 Nov 2005 (Bulletin 3/2006). Canopy fully open in the wreckage, one latch lug missing; opening in flight not established. Snippet only; not opened.
10. **NTSB 84014** CEN12FA378 IAR IS-28B2 (fatal, Factual mentions latch). PDF returned 403.

## Aggregate statistics found (verified this session)

PDF page indices are from text extraction; the printed page may differ by the cover page.

| # | Statistic | Source (page) |
|---|---|---|
| A1 | BFU study of microlight (Luftsportgeräte) events investigated by the BFU in **2000–2019**: of 24 SCF-NP (component failure) cases, **5 were canopy or cabin-door opened or lost**. The same study counts 42 component-failure cases in its HFACS breakdown. In **9 of these 42 (22 %)** the checklist check was inadequate, "e.g. proper closing of the canopy/door". Its phase example: a door opens in initial climb, then loss of control on final during the turn-back. | BFU22-803.1 "Studie zur Flugsicherheit von Luftsportgeräten" (2022): PDF p42 (5 of 24), p87 (9 cases, 22 %), p35 (example) |
| A2 | PKBWL commission comment: openings of light, flexible forward-hinged canopies (Zenair CH-601 / Evektor Sportstar type) are "fairly frequent". The open canopy settles at about 28° and vibrates; strong nose-down tendency; practically impossible to close in flight. The AFM had no procedure. Instructor and Commission "know analogous cases". | PKBWL 636/15 (Sportstar, 4 May 2015), p2 |
| A3 | PS-28 Cruiser: the canopy-warning switch detects the lever position, not the latches. The partial lock was not signalled. | BEA2016-0281 §2.1 (p1), §3 (p2) |
| A4 | BD-10: lock pins fully extended extinguished the CANOPY OPEN light without engaging the lugs. The probable cause is the lock-pin design. | NTSB CHI94LA288, Analysis and Probable Cause |
| A5 | CAP 232 operators sometimes leave the canopy locked in the ajar position for taxi cooling in summer, then close it before takeoff. The accident pilot forgot to close it. | BEA2025-0235 (F-HKAP) §2.5.2 |
| A6 | ASK 13 (Le Havre, 2019): no training item covers an inadvertent canopy opening, and cable-release practice is theory only. | BEA2019-0656 §2.4.1 (PDF p5) |
| A7 | Sportcruiser POH (2011): if the canopy opens on takeoff, do not try to close it; continue the climb at 65 kt, fly the pattern and land. | NTSB WPR12CA014, Analysis |
| A8 | CAROL hit counts for each query are in the NTSB section above (run 2026-11-04). For example, Analysis "canopy"+"opened" gives 107; Factual "canopy"+"latch" gives 170. | `q_*.json` |

**R5-derived counts** are in "Rows added". They are a convenience sample, not rates. NTSB rows are biased towards accidents with substantial damage or serious injury. BFU rows are biased towards glider launches.

## NOT VERIFIED / gaps

1. **BEA "18 accidents 2005–2018, 3 fatal"** after inadvertent canopy opening (microlights). This appears only in a search-engine summary that attributes it to "another ULM study". The BEA PDF was not identified or read. **Do not cite.**
2. **BEA notified-event pages** (6 rows) were read through WebFetch's summarising model, not as raw text. The PDF links on those pages were placeholders.
3. **BFU table rows** (13) come only from the BFU's one-paragraph summaries. Cause, warning and registration are unknown. The per-case PDFs (if any exist) were not found.
4. **The NTSB zero-hit set** (215 cases) was screened by regex, not read. The 39 helicopter and jet candidates were not downloaded. Mkey 84014 is missing.
5. **NTSB door events for non-priority types** (Piper, Beech, Cessna, Mooney) were not reviewed. Diamond DA40 rear-door separations (FAA AD 2010-25-01) did not surface with "door opened DA40". The narratives probably say "passenger door separated"; this query was not run.
6. **ATSB and TSB Canada:** unreachable (timeout / 403) from this machine, as for R2. No Australian or Canadian rows.
7. **AAIB coverage:** the gov.uk API matches only titles and descriptions. Pre-2014 bulletins have empty descriptions, and WebSearch found no new canopy-opening bulletins for Bulldog, Chipmunk, Yak-52, Tutor, Robin, DA40/42 or RV. The AAIB monthly compilations were not scanned.
8. **No rows** for Zlin, Yak, Sukhoi, Pitts, Slingsby T67, Diamond, Bulldog, Chipmunk, Tucano or Jet Provost. That reflects the search, not proof of absence.
9. **Classification judgements to challenge:**
   - 90015 SH-3R (handle vibrated open) coded mechanism_failure
   - 62754 Sonerai (friction pins, no lock) coded mechanism_failure
   - 103344 AA-1A and F-HKAP (ajar / intermediate position) coded partially_latched
   - 91880 One Easy kept unknown, although video suggests it was unlatched
   - F-CLBG and PKBWL 636/15 kept unknown because their lock findings are "probable"
10. **PKBWL 3586/19:** the header date is 14 Aug 2019 but the narrative says 16 Aug 2019. The row uses the header date.
11. **G-DBZZ:** the canopy event and a separate fatal flight happened on the same day. The row's outcome refers to the canopy flight only.
