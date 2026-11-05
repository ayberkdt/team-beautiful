# R6: Human-factors full texts (OA search for the R4 papers H1–H13, plus checklist-omission data)

- Read by: subagent R6
- Date read: 2026-11-04 (21:06–21:30 laptop time, UTC+3)
- Tags:
  - **[D-ag]**: read directly from the full text in this session. Page numbers are given as printed page (PDF page) where they differ.
  - **[Y]**: R6's own arithmetic or interpretation, or a secondary source.
- Local copies: `D:\tmp_ideathon\easa\dl\hf2\` (PDFs, plus `.txt` extracts made with pdftotext).
- Method: for every DOI in R4, I queried the Unpaywall API (generic email), the OpenAlex locations, Europe PMC and the HAL API. I also searched NASA NTRS, OSTI, ROSA P and the web.
- No paywall, login, Cloudflare/"Just a moment" page, firewall or 403 was bypassed. Each one was tried at most once and then left alone.

## Bottom line
**None of the core cry-wolf and reliability papers (H1–H9, H13) had a legal OA full text that I could reach.**
- H4 (Bliss 1995): the UCF STARS repository records Unpaywall points to contain only metadata (bibliographic pages, no PDF). The PDF of Bliss's dissertation is behind a Cloudflare check.
- H10 (Dehais 2014): the only OA copy is on OATAO (Toulouse), and that server refused connections all evening.
- H13 (Wickens 2009): this is publisher "bronze" OA on Sage, but Sage returned a Cloudflare challenge.

So **the per-condition numbers asked for in H1, H2, H4, H8, H6 and H13 are still unverified.** The R4 abstract-level values remain the only values available. To make up for this, I read in full open primary sources on checklist omission, ATC nuisance alerts and inattentional deafness in a light aircraft.

---

## S1. Degani & Wiener (1990), *Human Factors of Flight-Deck Checklists: The Normal Checklist*, NASA CR-177549 (May 1990; contract NCC2-377)
- **OA copy:** NASA NTRS 19910017830, https://ntrs.nasa.gov/api/citations/19910017830/downloads/19910017830.pdf. Public NASA contractor report, free on NTRS. Local file: `degani_wiener_1990_CR177549.pdf` (71 pp.).
- **What I read:** the whole text was extracted and searched. Front matter, §1.3 Methods (p.5–6), §3.1.7 (p.21), §5.4 (p.31–32), §5.4.4 (p.36), §7.2.3–7.2.5 (p.50–52) and §8 (p.56) were read in context.
- **Key finding: there is no measured omission rate.** The authors deliberately did **no statistical analysis** of the NTSB (1983–88), ICAO (12,000 reports) or ASRS (1981–89) data [D-ag, p.6 (PDF 9)]. Their reasons: reports describe outcomes rather than the checklist error type, and ASRS has reporting bias. The ASRS narratives they quote "are not representative" [D-ag, p.6].
- **Only quantitative per-item omission figure, quoted from Swain & Guttman 1983** [D-ag, p.36 (PDF 39)]:
  - checklist with no check-off provision: about **1 in 100 per item**;
  - checklist with a check-off provision: **3 in 1,000**.
  - S2 below checks this against the original.
- **Monan (1979), reproduced as Table B** [D-ag, p.32 (PDF 35)]: of **169** air-carrier ASRS distraction reports, **22** were distractions caused by checklist procedures. The other leading categories were malfunctions (19), company radio (16) and traffic watch (16).
- **Item order** [D-ag, p.51]:
  - the probability of completing items "slowly diminishes" along a checklist as interruptions accumulate;
  - the authors recommend that very critical items come **first**, not last;
  - duplicating one or two "killer items" (flaps/slats, trim) in a ground checklist and again before take-off is recommended as a safeguard (p.51–52).
- **Deferred items** [D-ag, p.51 (PDF 54)]: an item deferred because it cannot be done in sequence is held in short-term memory, and its omission likelihood is "relatively high". Example: ASRS #2855, a crew that deferred fuel and departed unfuelled.
- **Warning systems can also fail** [D-ag, p.21 (PDF 24)]: the take-off configuration warning failed in both NW255 (MD-80, CAWS) and DL1141 (B-727). This argues against treating an alert as a replacement for the checklist item.
- **Our design** [Y]: put the canopy check as the **first** item of the before-take-off checklist and **also** back it with the automatic alert. An alert does not remove the checklist item (Boeing B-757 philosophy, p.21, is the opposite view).

## S2. Swain & Guttmann (1983), *Handbook of Human Reliability Analysis…*, NUREG/CR-1278 (SAND80-0200), Aug 1983
- **OA copy:** OSTI 5752058, https://www.osti.gov/servlets/purl/5752058. US-government report with full text on OSTI. Local file: `nureg_cr1278.pdf` (35 MB).
- **What I read:** Ch. 15, pp.15-13 to 15-14 (PDF 407–408) and Table 16-1, p.16-5 (PDF 418). Table 20-7 (PDF 502) repeats Table 15-3.
- **Table 15-3: errors of omission per item, when use of written procedures is specified** [D-ag, p.15-14]. HEP = human error probability; EF = error factor.

  | Case | HEP | EF |
  |---|---|---|
  | Check-off used correctly, short list (≤10 items) | **.001** | 3 |
  | Check-off used correctly, long list (>10 items) | **.003** | 3 |
  | No check-off, or check-off used incorrectly, short list | **.003** | 3 |
  | No check-off, or check-off used incorrectly, long list | **.01** | 3 |
  | Written procedure available but not used | **.05** | 5 |

  - If the task is "second nature", use .01 for the last case.
  - The estimates assume zero dependence between items.
- **Table 16-1** [D-ag, p.16-5]:
  - "Use a checklist properly" (read item, do it, check it off) fails with **HEP .5 (EF 5)**;
  - "Use written operations procedures under normal operating conditions" fails with **.01 (EF 3)**.
- **Caveat** [Y]:
  - these are judgement-based nuclear-plant values (p.15-13 says the long/short split is "arbitrary");
  - a single-pilot GA "canopy closed and locked" item done from a card or from memory is closest to "no check-off, short list" (.003) or "procedure not used" (.01–.05).
- **Suggested Monte Carlo range for P(pilot omits canopy lock check)** [Y]: **10^-3 to 5×10^-2 per flight**, with about 3×10^-3 to 10^-2 as the central value.

## S3. Dismukes & Berman (2010), *Checklists and Monitoring in the Cockpit: Why Crucial Defenses Sometimes Fail*, NASA/TM-2010-216396 (July 2010)
- **OA copy:** NTRS 20110011145, https://ntrs.nasa.gov/api/citations/20110011145/downloads/20110011145.pdf. Public NASA TM. Local file: `dismukes_berman_2010_TM216396.pdf`.
- **What I read:** Executive summary (pp.2–4, PDF 8–10), §4 opening (p.12, PDF 18), and Tables 1–5 (pp.41–45, PDF 47–51).
- **Sample** [D-ag, p.2]: **60** normal line flights, observed from the jumpseat at 3 airlines.
- **Deviations observed** [D-ag, p.2]:
  - **899** in total: 194 in checklist use, 391 in monitoring, 314 in primary procedures;
  - **Table 2** (p.42), checklist deviations per flight: mean **3.2**, median 2.0, SD 2.9, range 0–13;
  - all deviations per flight: mean **15.0**.
- **Skew** [D-ag, p.2]: 31 flights had 0–2 checklist deviations, the other 29 had 3–13. A subset of flights produces most of the deviations.
- **Table 5, types of checklist deviation** [D-ag, p.45]:

  | Type | Count | Share |
  |---|---|---|
  | Flow-check performed as read-do | 48 | 25 % |
  | Responded without looking | 43 | 22 % |
  | **Item omitted, performed incompletely or incorrectly** | **42** | **22 %** |
  | Checklist initiated at a poor time | 31 | 16 % |
  | Performed from memory | 17 | 9 % |
  | Checklist not initiated | 13 | 7 % |
  | **Total** | **194** | |

  - "Responded without looking" includes answering that an item was correctly set when it was not (p.12).
- **Rate per opportunity** [D-ag, p.2]: one airline had 10 checklists with 197 challenge and response items. The authors judge errors per opportunity to be "probably well under one percent".
- **Trapping** [D-ag, p.3]:
  - only **18 %** of all deviations were caught or corrected;
  - **14 %** of checklist deviations were caught, versus 35 % of primary-procedure and 6 % of monitoring deviations.
- **Outcomes** [D-ag, p.4]: 89 % of deviations had no discernible outcome; 9 % led to an undesired aircraft state.
- **Phase** [D-ag, Table 3 p.43]: **83 of 194** checklist deviations (43 %) occurred **pre-taxi/preflight**, and 20 during taxi-out.
- **Per-item estimate** [Y]: 42 omitted, incomplete or incorrect items in 60 flights is 0.7 per flight. With about 200 items per flight, that is roughly **3–4×10^-3 per item**, consistent with Swain's .003. This applies to two-pilot crews with cross-checking. A single-pilot Extra has no second pilot to trap the error, so 14 % trapping is an upper bound on mitigation.

## S4. NTSB final reports on canopies left unlatched (GA)
- **OA copies:** data.ntsb.gov CAROL report generator (public US-government records). Local files: `ntsb_75712.pdf` and `ntsb_51859.pdf`.
- **What I read:** both reports in full (6 pp. each).
- **ERA10LA221** (SportCruiser, 11 Apr 2010; aircraft destroyed, 1 serious injury) [D-ag, pp.1–4]:
  - Probable cause: failure to keep control while distracted by holding shut the **unlocked canopy**. Contributing: failure to lock it, and inadequate POH guidance.
  - Two earlier cases (WPR09LA075, WPR10LA276): the **unlatched canopy rests fully closed** on the ground and lifts after take-off.
  - Afterwards the manufacturer added a pre-take-off "closed-and-locked" checklist item.
  - [Y]: this is direct evidence that a closed-but-unlatched canopy looks locked, which defeats the visual check.
- **SEA01LA058** (AC-5m motor glider, 4 Mar 2001) [D-ag, pp.1–3]:
  - The pilot opened and closed the canopy **several times** before departure to talk to the ground crew. The last closure was not fully latched.
  - The canopy opened at about 30 ft after lift-off. Attention was diverted and the aircraft hit the runway.
  - Findings: checklist not used; canopy not secured.
  - [Y]: the alert must be evaluated at the **last** closure before take-off. Arming on throttle advance or the take-off roll (R4 §1.3) covers this case.
- No aggregate GA canopy or door statistics were found. A CAROL query on findings "Window, canopy – unlatched/open" would give counts; it was **not run**.

## S5. Allendoerfer, Friedman-Berg & Pai (2007), *Human Factors Analysis of Safety Alerts in Air Traffic Control*, DOT/FAA/TC-07/22 (Nov 2007)
- **OA copy:** ROSA P, https://rosap.ntl.bts.gov/view/dot/71701/dot_71701_DS1.pdf (FAA technical report, available to the public). Local file: `faa_tc07_22.pdf`.
- **What I read:** Executive summary (p.ix) and §1.4 on posterior probability (p.24–25, p.54).
- **Sample** [D-ag, p.ix]: **607** conflict alerts (CAs) and **178** minimum safe altitude warnings (MSAWs), from 5 en-route and 17 terminal facilities.
- **No-response rates** [D-ag, p.ix]:
  - en route: **62 %** of CAs and **91 %** of MSAWs got no controller response;
  - terminal: **44 %** of CAs and **61 %** of MSAWs got no response;
  - none of these cases involved an operational error.
- **Responses that came before the alert** [D-ag, p.ix]: 67 % for CAs and 68 % for MSAWs.
- **Nuisance estimate** [D-ag, p.ix]: **81–87 %** of CAs and **87–97 %** of MSAWs are nuisance or unnecessary alerts ("valid according to the algorithms" but not useful).
- **Posterior probability** [D-ag, p.24 and p.54]: when the base rate is low, even an accurate alert system has a low posterior probability that an alert is real. This is the FAA's restatement of Parasuraman & Hancock. It is **secondary for H8**.
- **Our design** [Y]: if the operator can anticipate the hazard, a valid-by-algorithm alert becomes a nuisance alert. That is why the canopy alert must be armed only when it carries new information (take-off roll), not continuously on the ground.

## S6. Dehais, Roy & Scannella (2019), Inattentional deafness to auditory alarms… *Behav. Brain Res.* 360, 51–59. doi:10.1016/j.bbr.2018.11.045
- **OA copy:** HAL hal-01991825, https://hal.science/hal-01991825/document. Author manuscript deposited in HAL; no licence statement seen on the cover page. Local file: `hal-01991825.pdf`.
- **What I read:** methods and results (PDF pp.6–15) and discussion (PDF pp.17–22).
- **Setup** [D-ag, PDF p.7–10]:
  - 13 male pilots, 81.1 ± 43.8 flight hours, in the ISAE-SUPAERO motion simulator;
  - oddball paradigm: 1000/1100 Hz pure tones at **90 dB SPL**, 20 % of tones were targets;
  - high-load scenario: night landing in poor visibility with simulated cabin smoke and a go-around, with an observing expert pilot as stressor.
- **Result** [D-ag, PDF p.14]: missed targets were **0.33 % (±0.47)** under low load versus **57.73 % (±12.63)** under high load (t = 15.73, p < 0.001).
- **Discussion** [D-ag, PDF p.18]: every pilot missed at least 20 % of alerts while all of them landed, i.e. they prioritised flying ("aviate first").
- **Limitations stated by the authors** [D-ag, PDF p.22]: the tones were not real cockpit alarms, were frequent, and had no flight consequence. So 57.7 % is an upper-end figure.
- **Dehais et al. 2014 (H10)** is cited (PDF p.4, p.17) but its numbers are not repeated. The 11/28 figure is still abstract-only (R4).

## S7. Callan, Gateau, Durantin, Gonthier & Dehais (2018), Disruption in neural phase synchrony… in real-world setting, *Hum. Brain Mapp.* doi:10.1002/hbm.24026
- **OA copy:** HAL hal-01738660, https://hal.science/hal-01738660/document. Author version on HAL. Local file: `hal-01738660.pdf`.
- **What I read:** §2.1–2.2 (PDF p.5–6) and §3.1 (PDF p.8).
- **Setup** [D-ag, PDF p.5–6]:
  - **real flight in a DR400 Robin** (a light GA aircraft) with 13 pilots and student pilots;
  - the audio task ran from **take-off** to landing, with instructor-induced high workload (diversion, simulated engine failure, low circuits);
  - 180 target tones (20 %) and 720 standard tones, delivered through the aviation headset.
- **Results** [D-ag, PDF p.8]:
  - mean hit rate **61.9 %** (SE 4.5; range 34.8–84.3 %), i.e. **about 38 % missed**;
  - false-alarm rate 1.2 %;
  - mean hit RT **792 ms** (SE 24; range 661–945 ms);
  - subjective workload median 5 on a 1–7 scale.
- **Our design** [Y]: this is the best open, GA-specific evidence that an aural-only alert is missed about 4 times in 10 under high workload. Make the visual red warning primary and keep it latched, and treat the aural as a supplement.

---

## Papers that stayed unreadable (full text)
| ID | Paper | Why |
|---|---|---|
| H1 | Wickens & Dixon 2007, TIES 8(3) | Unpaywall/OpenAlex: closed. The tech-report version (AHFD-05-01/MAAD-05-1) is not online; UIUC IDEALS returned 403 to the API and to WebFetch. **How the 0.70 crossover was derived is not verified.** The OpenAlex abstract only says a regression of benefit vs reliability was "strongly linear". |
| H2 | Dixon, Wickens & McCarley 2007, HF 49(4) | Closed. The DTIC tech-report version ADA496817 returned HTTP 403 (curl and WebFetch). Not bypassed. |
| H3 | Dixon & Wickens 2006, HF 48(3) | Closed. DTIC ADA462195 returned 403. |
| H4 | Bliss, Gilson & Deaton 1995, Ergonomics 38(11) | Unpaywall lists STARS "green" copies, but both pages are metadata only, with no PDF. The dissertation PDF (STARS rtd/3614) is behind Cloudflare. **Per-reliability response rates remain unverified.** |
| H5 | Bliss & Dunn 2000 (doi 10.1080/001401300421743) | Closed. |
| H6 | Bliss 2003, IJAP 13(3) | Closed. TRID abstract read (https://trid.trb.org/View/662432) [D-ag, abstract]: about **1–3 %** of NTSB and Army events were alarm-related versus **27 %** in ASRS; the share of false alarms was "significantly greater" in the Army database; most problems occurred in high-workload flight segments. **Event counts not available.** |
| H7 | Parasuraman & Riley 1997 | Closed. |
| H8 | Parasuraman, Hancock & Olofinboba 1997 | Closed. **The paper's formula and worked example are not verified.** For the MC use plain Bayes [Y]: PPV = P(H)·p_hit / [P(H)·p_hit + (1−P(H))·p_FA]. |
| H9 | Meyer 2004 | Closed. |
| H10 | Dehais et al. 2014 | OA accepted version on OATAO (oatao.univ-toulouse.fr/11613/1/Dehais_11613.pdf), but the server refused TCP connections (3 attempts plus WebFetch: ECONNREFUSED). **Not read.** It is legally OA, so a later retry should work. |
| H11 | Scannella et al. 2013 | OA version is also on OATAO (10736), which was unreachable. |
| H12 | Riedinger et al. 2026, doi 10.1177/00187208261431654 | Closed (Unpaywall). |
| H13 | Wickens et al. 2009, HF 51(4) | "Bronze" OA on Sage, which served a Cloudflare challenge. The ISAP 2009 conference version (Wright State CoreScholar) and CORE mirrors are also behind Cloudflare. Not bypassed. |
| — | Cafarelli 1998, MIT thesis (F-16 missile warning false-alarm rate vs trust), dspace.mit.edu 1721.1/59842 | The DSpace firewall returned 429 twice. Abstract only: RT rose and trust fell as FA rate increased. No numbers. |
| — | ODU theses by Bliss's students (psychology_etds 453/506/560) | Behind Cloudflare. |
