# R2 – Canopy / door open-in-flight occurrence dataset: sources and method

- **Date read:** 2026-11-04
- **Read by:** subagent R2
- **Data file:** `R2_occurrences.csv` (UTF-8, comma separated, 146 rows, 18 columns)
- **Downloads:** `D:\tmp_ideathon\easa\dl\occ\` (PDFs plus extracted text in `txt\`, NTSB PDFs in `ntsb\`). Scripts: `D:\tmp_ideathon\easa\r2_scripts\` (`extract.py`, `ntsb_summ.py`, `build_csv.py`). You can rebuild the CSV with `python -I build_csv.py D:/tmp_ideathon/easa/dl/occ <out.csv>`.
- **Scope:** G-MIIL (Extra NG, 2 Apr 2022) is **not** a row. The main session covers it. Its AAIB report was used only for the SP-HMM paragraph.

## Tag legend (column `tag`)

| tag | meaning |
|---|---|
| `D-ag` | Verified. R2 read the cited primary report itself in this session (downloaded PDF or text). |
| `D-ag-ikincil` | Verified, but from a secondary summary in another official report. Examples: rows from AAIB G-FLOR Table 1 and from BEA2024-0375 §2.6. R2 did not read the event's own report. |

No row comes from a search-engine snippet, forum, ASN or news item. Those leads are listed under "NOT VERIFIED / gaps" below.

## Classification rules R2 applied (so you can challenge them)

- **cause_class**
  - `not_locked`: the report says the canopy/door was not latched or locked, or that the pilot forgot, or that the pilot "failed to secure" it.
  - `partially_latched`: the report says it was latched but "not fully", "intermediate/half-latch position", one latch or bolt not engaged, the lever was short of over-centre, or something obstructed seating.
  - `mechanism_failure`: a failed, worn, repaired, modified or mis-rigged latch.
  - `structural`: a transparency, hinge or attachment failure.
  - `handle_knocked`: an occupant, object or animal moved the handle.
  - `unknown`: the investigator could not determine the cause. This includes "probably inadequate closure" findings that were not stated firmly.
- **outcome** is the highest injury on board. AAIB "Injuries" field; NTSB `HighestInjuryLevel`.
- **aircraft_damage**
  - NTSB rows use the report's "Aircraft Damage" field.
  - AAIB, BEA and SUST rows are R2's mapping of the free-text "Nature of damage". "Damaged beyond economic repair" is mapped to `substantial`, and the notes say so.
  - Canopy or door lost with no other damage is mapped to `minor`.
- **phase**
  - `initial_climb` includes the first climb after liftoff, glider aerotow and winch climb, and the circuit up to downwind.
  - `takeoff_roll` means the opening began on the ground.
- **warning_fitted** is `yes` or `no` only when the report says so. A purely visual indicator (button, painted line) is not counted as a warning; the note says so.
- **date**
  - NTSB: the local date from the report's "Date & Time" field. The CAROL `EventDate` is UTC and can be one day off.
  - Europa table rows: year-month only.

## Sources searched (query → result)

### UK AAIB (gov.uk)
1. **WebSearch**
   - Queries: "AAIB bulletin canopy opened in flight not locked"; "AAIB report Extra 300 canopy opened takeoff not locked"; "AAIB glider canopy opened launch not locked bulletin"; "AAIB DA42 canopy opened in flight unlatched"; "AAIB Robin DR400 canopy opened in flight"; "AAIB bulletin canopy detached in flight aerobatic aircraft unlatched"; "AAIB canopy opened takeoff Cap 10 OR Bulldog OR Yak-52 OR Tucano"; "AAIB RV-8 OR RV-7 OR RV-6 canopy opened in flight".
   - Found about 25 bulletin PDFs.
2. **gov.uk search API** (systematic)
   - Queries: `https://www.gov.uk/api/search.json?filter_format=aaib_report&q=<q>&count=500`, with `q` = canopy, "canopy opened", "canopy detached", "canopy unlocked", "canopy departed", "canopy open", "door opened in flight". JSON saved as `govuk_q_*.json`.
   - 30 reports had canopy or door in the title or description. After excluding baggage doors, window losses and airliner cowl/airstair items, 20 were added.
   - Limitation: pre-2014 reports have empty descriptions, so the API under-finds older bulletins. Older ones came from WebSearch.
3. **Rows:** 34 AAIB event reports read, plus 6 Europa rows from the G-FLOR Table 1 summary. SP-HMM is counted under PKBWL.
4. **Excluded after reading:**
   - G-BCVF (pilot deliberately opened the canopy for CO ventilation and it detached)
   - G-BLWY (bonded rear transparency dis-bonded; not a canopy or latch)
   - G-CZAW (wing locker)
   - G-CJSK (aileron connection)
   - G-MIIL (main session)

### France BEA
- **Queries:** "BEA rapport verrière non verrouillée ouverture en vol décollage"; "bea.aero verrière ouverture intempestive décollage rapport ULM perte de contrôle".
- **Reports read:** BEA2015-0439 (59CVF), BEA2016-0092 (D-EFBY), BEA2024-0375 (77AUM, published March 2026), BEA2018-0375 (86QF), BEA2019-0694 (83ARU), f-do120807/f-uf120820 (APM30 ×2), n-cv100719 (N58CV), f-jp020707 (F-WGJP), REC info 7/2008.
- **Opened and excluded:**
  - BEA2015-0370, BEA2017-0311, BEA2017-0118, BEA2021-0364: not canopy events.
  - 31-t030523: door hinge torn, cause "inadequate modification", opening sequence not established.
- **BEA notified-event page** for D-EWLA (Lienz, 2023, Austrian investigation), read through WebFetch.
- **REC info 7/2008** gives anonymous pilot narratives only, so no rows. Design-relevant narrative 3: a canopy lock indication on the panel showed LOCKED while the canopy was not locked, because a key barrel was turned while the handle was open (p2).

### Switzerland SUST
- **Query:** "BFU Untersuchungsbericht Haube nicht verriegelt geöffnet Start". The search returned SUST hits, not German BFU hits.
- **Read:** 1951 (HB-2002 ASK 16), 2087 (OE-AKG DA20-A1), HB-3214 (Duo Discus), HB-3099 (ASK 21).

### USA NTSB (CAROL)
- **WebSearch:** "NTSB canopy opened during takeoff not latched loss of control fatal"; "NTSB final report canopy not latched Extra OR Pitts OR Diamond DA20".
- **CAROL API** (systematic): POST `https://data.ntsb.gov/carol-main-public/api/Query/Main` with `Narrative.Analysis contains "canopy" AND contains "latch"`.
  - Returned **105 cases** (`ResultListCount=105`, not capped), saved as `carol_canopy_latch.json`.
  - "canopy" alone returned 490 with `MaxResultCountReached=true`, so that list is capped and was not used.
- **Report PDFs** downloaded from `GenerateNewestReport/<Mkey>/pdf`: 103 of 105. Mkeys 199398 (ERA25LA070) and 15439 (CHI92LA143) returned HTTP 403 twice; these are gaps.
- **88 rows included.** The remaining 15 were excluded after reading the Analysis and Probable Cause:

| Mkey | Report / aircraft | Reason for exclusion |
|---|---|---|
| 200381 | — | Canopy unlatched from propeller-failure vibration; secondary |
| 106995 | DA42 | Canopy unlatched during porpoising hard landing; not causal |
| 105676 | DA40 | Passenger walked into propeller |
| 99294 | N9M | — |
| 96223 | EA300L | Aerobatic loss of control; canopy appears only in debris description |
| 92789 | RV-6A | Witness marks show canopy was latched |
| 89159 | Stearman | — |
| 89037 | Sonex | Undetermined |
| 82857 | Varga | Ditching |
| 81758 | RV-7A | Pilot fell through open canopy after inversion; opening not established as the initiator |
| 77104 | PA-28 | Instructor stepped out |
| 64929 | Interavia | Undetermined |
| 8932 | Mustang II | Overstress breakup |
| 24959 | KR-1 | Canopy and latch found before impact point; no cause stated |
| 103795 | KR-2S | Pilot reported an "unspecified canopy problem", fatal, cause undetermined. **Borderline.** Could be added as a cause-unknown row. |

### Australia ATSB, Canada TSB, BGA, CASA
- **Queries:** "ATSB research report doors canopies opening in flight light aircraft"; "TSB Canada canopy opened in flight unlatched report"; "British Gliding Association canopy opening on launch statistics accidents"; "gliding.co.uk accident review canopies opening in flight 213 reports"; "Transport Canada study doors opening in flight 33 accidents".
- **All primary documents were unreachable from this machine:**
  - atsb.gov.au: curl connect failure, WebFetch timeout ×3.
  - bst-tsb.gc.ca: HTTP 403.
  - gliding.co.uk: 404 at old upload paths; members site 403.
  - casa.gov.au: no response.
  - Wayback `id_` retrieval also failed.
- **No rows from these sources.** See gaps.
- **Read instead:**
  - Scottish Gliding Centre "Topic of the month June 2026 – Canopies" (qualitative: "Aviate first"; Vega needs a helper to check the lock).
  - Van's Service Letter 16-11-04 "Tip-up canopies".

### EASA / FAA ADs (Diamond)
- **Query:** "EASA AD Diamond DA40 canopy locking unlocked in flight"; "Diamond DA20 DA40 canopy opened in flight airworthiness directive front canopy latch".
- **Read FAA AD 2010-25-01** (Federal Register 2010-30199, 7 Dec 2010):
  - Prompted by "several reports of the rear passenger door departing the airplane in flight" (DA 40/40F).
  - A comment section (p1-2) is directly relevant to alert design. Front canopy and rear door share one "door open" annunciator, and pilots taxi with the canopy in the partly open (cooling) position. So "the pilot ignores the annunciation and is unaware that the rear door might not be properly latched".
  - The commenter asked to separate the sensors. The FAA neither agreed nor disagreed and referred it to ACG/EASA/Diamond.
- **Read FAA NPRM 2026-09574** (Docket FAA-2026-4633, scheduled for publication 13 May 2026), based on Transport Canada AD CF-2025-30 (23 Jun 2025):
  - Covers DA 40/40F/40NG passenger door separations, "several reports".
  - DAI attributed some of them to "the passenger door not being properly latched and subsequent attempts to latch the passenger door in flight". The rest have no definitive root cause (p3).
  - Required actions include inspecting the "canopy and passenger door warning light".
- **EASA AD 2010-0235** and EASA AD numbers for Diamond canopy: **not read** (gap).

## Aggregate statistics found

### Verified (read in this session)

| # | Statistic | Source (page/section) |
|---|---|---|
| S1 | Since 2003 there were **8 UK occurrences** of inadvertent Europa cockpit-door opening (2003–2021). **At least 6 of 8 were the pilot's left door**, which is the hardest to check from the seat. LAA mod SM 15833 (1 Nov 2021) prevents the latch lever closing when the door is not latched. | AAIB Bulletin 1/2022 G-FLOR, p1 synopsis, p7-8 Table 1, Analysis |
| S2 | Pitts S-2B/S-2C: pilots reported an "apparently high number" of canopy detachments, but the **CAA MOR database held only 1 detachment in the previous 10 years**. This is an under-reporting signal. | AAIB Bulletin 3/2011 G-IIDY, p2 |
| S3 | Dynamic WT9: the DSB found **at least 12 previous canopy openings** on the type. Aerospool issued a 2008 mandatory SB (AFM procedure) and in 2012 recommended a new lock with a safety catch plus an **incomplete-closure warning system**. | BEA2024-0375 (77AUM) §2.6, p10 |
| S4 | BEA: "a significant number" of accidental canopy openings on similar microlights; **in the majority of cases linked to incorrect closing/locking before takeoff**, and they **often led to loss of control**. | BEA2024-0375 §2.6 p10 and "Messages de sécurité" |
| S5 | Diamond reported **3 other DA20-A1 accidents** from inadvertent canopy opening with the same lock system, **all at or just after takeoff**. | SUST report 2087 (OE-AKG) §1.8 |
| S6 | King Air 90 series: the manufacturer knows of **only 2 other** in-flight cabin-door openings. | AAIB 11/2024 D-IMEP, p1 |
| S7 | Sling 4: **no other** reported canopy losses on type (2017). | AAIB 12/2017 G-LDSA, p1/p3 |
| S8 | Slingsby T67:<br>• **Two earlier UK canopy openings** (Bulletin 12/96), plus non-UK reports and "persistent reports" of latches failing to engage while appearing engaged. Mod M810 placard made mandatory by the CAA (AAIB 12/1997 G-BIZN, p2).<br>• On the T67M, ≥1 opening near Vne and ≥1 at >1500 RPM led to SB 68 (AAIB 12/1996 G-BWXB, p2). | AAIB 12/1997 G-BIZN p2; AAIB 12/1996 G-BWXB p2 |
| S9 | NTSB CAROL: **105** US cases whose Analysis narrative contains both "canopy" and "latch" (1982–2026, query run 2026-11-04). R2 kept 88 as canopy/door opening events after reading them. | CAROL query JSON `carol_canopy_latch.json` |
| S10 | Van's: in-flight canopy and door openings "reported in all models of RVs". The most pronounced effects are on tip-up canopies (RV-6/7/9/12/14), with an abrupt nose-down pitch. "Most in-flight openings occur due to the pilot simply forgetting to latch the canopy properly prior to take-off." | Van's SL 16-11-04, p1 |
| S11 | Van's Notification 14-05-22 recommended that **RV-12s with SkyView/G3X add a canopy latch warning**: a switch that alerts if the canopy is unlatched when rpm exceeds 3,700. Issued after CEN13LA340. | NTSB CEN13LA340 (N666BE) Analysis |
| S12 | Sportcruiser: after 3 investigations (WPR09LA075, WPR10LA276, ERA10LA221), flight tests showed an unlocked canopy rides slightly ajar and the aircraft stays controllable. The manufacturer added a pre-takeoff "closed and locked" checklist item and a POH procedure. | NTSB ERA10LA221 Analysis |

### R2-derived counts from this dataset

These are **not** population rates. The dataset is a convenience sample, biased towards events that became investigated accidents. NTSB generally investigates only accidents with substantial damage or serious injury.

| Measure | Result |
|---|---|
| Rows by investigator | NTSB 88; AAIB 40 (34 own reports + 6 Europa table rows); BEA 11; SUST 4; DSB 1, PKBWL 1, Austria 1 (via other reports) |
| Rows by cause_class | not_locked 43; partially_latched 34; unknown 50; mechanism_failure 11; structural 4; handle_knocked 4 |
| Lock-related (not_locked + partially_latched) | 77 of 146 rows (53 %). 10 of these 77 were fatal (13 %). |
| Lock-related by phase where the opening began | initial_climb 49 (64 %); cruise 16; takeoff_roll 7; approach 4; unknown 1 |
| Outcome, all 146 rows | fatal 24; serious 24; minor 25; no_injury 61; unknown 12 |
| warning_fitted | yes in only 12 rows (no 6; unknown 128). See the pattern below. |

**Pattern in the `warning_fitted = yes` rows:**
- **Warning present but ignored, missed or distrusted:** G-OALB (light disregarded as a faulty switch); N527SS (light not observed); N560SS (light still on after the accident); OE-AKG (pilot saw no lamp; no AFM procedure); N88VE (warning caused distraction).
- **Warning defeated or giving a false "closed":** N6161 (microswitch set to signal closed before pins seated); G-IIDY (horn silent, canopy not engaged); G-UKCS (door-ajar light out).

## Duplicates and how they were de-duplicated

- **G-BYCT:** gov.uk has an original page and a "Correction" page (flying hours only). Kept one row (AAIB-14).
- **G-FIZY:** appears as its own report and in G-FLOR Table 1. Kept the own-report row (AAIB-15) and did not create a table row.
- **G-CBAP:** two different events on the same airframe (17 Feb 2013 canopy detached; 1 Jul 2014 canopy shattered). Kept both; they are separate occurrences.
- **59CVF:** appears as its own BEA report and in BEA2024-0375 §2.6. Kept one row (own report).
- **N999NA:** appears as its own NTSB report (report_id ERA13LA183) and in BEA2024-0375 §2.6. Kept the NTSB row only.
- **APM30 F-HADO / F-HOUF:** one combined BEA report covering two events. Kept two rows with the same URL.
- **NTSB 75712 (ERA10LA221):** cites WPR09LA075 and WPR10LA276. Both are separate rows, and the rows are not duplicates.
- **Method:** registration plus date checked across all sources. No other cross-source duplicates found. Note that gov.uk search results overlap heavily between queries; the results were merged by report link.

## NOT VERIFIED / gaps

1. **BGA statistics (not verified).**
   - A search-engine summary attributes these to the BGA Accident Review 2018: "BGA database has 213 reports of canopies opening in flight, 59 in the 10 years 2008-2017"; 7 unlocked canopies opened in flight in 2018; "unlocked canopies a chronic problem".
   - The 2022 Accident Review was summarised as one canopy opening on a winch launch, plus a case where a pilot distracted by the canopy crashed inverted.
   - **R2 could not open any BGA PDF** (404/403). Do not cite these numbers without reading the PDF.
2. **TSB Canada A95W0153 (not verified).** A snippet says "A review of TSB accident data from 1977 to 1993 showed 33 accidents involving small aircraft, resulting in 10 fatalities, in which a cabin, baggage, or other compartment door opened during flight", 6 of them baggage doors, plus TSB recommendations A93-06 to A93-10 (June 1993). The TSB site returned 403.
3. **ATSB (not verified, no rows).** Leads from snippets only:
   - AO-2014-164 VH-JON RV-6A (canopy probably opened in flight, fatal; safety issue AO-2014-164-SI-01 and SAN-012)
   - AO-2013-158 VH-ALP Lancair Legacy (canopy unlatched on takeoff)
   - DA42 Parafield 18 Jan 2018 (canopy likely opened)
   - AE-2008-029 CH601XL
   - AO-2012-151 Beech A36 door, which cites Transport Canada/TSB work: "all capable of controlled flight with a door open; distraction/panic in 17 accidents"
   - CASA Airworthiness Bulletin "Inadvertent door opening in flight"
   - All ATSB/CASA URLs timed out. Retry from another network or ask the user to download them.
4. **EASA ADs not read.**
   - EASA AD 2010-0235 (DA40 rear door) and any EASA AD on Diamond front-canopy locking were not opened. Only the FAA AD 2010-25-01 and FAA NPRM 2026-09574 were read.
   - No DA20/DA40/DA42 front-canopy AD was confirmed.
   - Snippets mention EASA AD CF-2025-30 on ad.easa.europa.eu; that is actually the Transport Canada AD number, mirrored.
5. **Primary reports read only as summaries:**
   - SP-HMM (PKBWL report; only the AAIB G-MIIL summary)
   - PH-4E7 (DSB report; date unknown)
   - 68-US and 73-OH (own BEA reports not downloaded)
   - G-PEGY / G-IIGI / G-CCUL / G-BYJI / G-OURO / G-BLVL (own AAIB bulletins not opened)
   - The FFVP/FFPLUM federation reports cited in BEA2024-0375 (WT9 13 Aug 2022, cruise 25 Oct 2018, WT9 20 Feb 2020) are not public. No rows.
6. **Missing NTSB PDFs:** Mkeys 199398 (ERA25LA070, Clapp Saberwing, serious) and 15439 (CHI92LA143, Grob G-103) returned 403.
7. **AAIB coverage gaps:**
   - The gov.uk API under-finds pre-2014 bulletins.
   - G-BLLS's file name "12-96a" implies a companion "12-96b". G-BIZN cites two T67 events in 12/96; the second was not found.
   - No AAIB DA40/DA42 front-canopy, Bulldog, Yak-52, Tucano, Cap 10 or RV canopy bulletin surfaced.
   - The ASN-listed Grob G109 G-BJZX (1998) and Ka 6 (May 2023) were not checked.
8. **No German BFU rows.** The searches returned only SUST hits; the bfu-web.de archive was not searched directly.
9. **No EASA Annual Safety Review or AOPA Nall Report figure for canopy openings** was found or read.
10. **Interpretation caveats:**
    - AAIB "Information source: pilot's report form" bulletins carry the pilot's own conclusion (e.g. G-CDAL, G-BYCT), not an AAIB finding. The notes say so where relevant.
    - cause_class and damage mapping are R2 judgements under the rules above.
    - `warning_fitted = unknown` (128 rows) means the report is silent. It does **not** mean no warning was fitted.
