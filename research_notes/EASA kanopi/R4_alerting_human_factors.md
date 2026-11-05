# R4 — Alerting human factors and regulatory alert conventions (canopy "not locked" alert)

- read by: subagent R4
- date read: 2026-11-04
- Tags: **[D-ag]** = read directly from the source (or its full official abstract) in this session. **[Y]** = secondary source, or R4's design interpretation.
- Local copies: `D:\tmp_ideathon\easa\dl\hf\`. Abstracts: `pubmed_hf1.txt`, `pubmed_hf2.txt`, `pubmed_hf3.txt`, `openalex_hf.txt`.
- **Limitation:** none of the empirical HF papers were open-access full texts. Every empirical number below comes from the **published abstract** (PubMed or OpenAlex, which reproduce the publisher's abstract), so page numbers are the article page ranges. Table- and figure-level numbers (e.g. response rate at each reliability level) are **not verified**.

## Sources

| ID | Document | Edition / date | URL |
|---|---|---|---|
| A1 | FAA AC 25.1322-1, Flightcrew Alerting | 12/13/2010 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.1322-1.pdf |
| A2 | 14 CFR 25.1322 (Amdt 25-131, 75 FR 67209, 2 Nov 2010) | current text on LII, read 2026-11-04 | https://www.law.cornell.edu/cfr/text/14/25.1322 |
| A3 | FAA AC 23.1311-1C, Installation of Electronic Display in Part 23 Airplanes | 11/17/2011 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC%2023.1311-1C.pdf |
| A4 | EASA CS-23 Amendment 4 (Annex to ED Decision 2015/018/R) | Amdt 4 (the Extra NG certification basis) | https://www.easa.europa.eu/sites/default/files/dfu/CS-23%20Amendment%204.pdf |
| A5 | EASA TCDS EASA.A.620 EXTRA NG | Issue 04, 02 Dec 2020 | https://www.easa.europa.eu/en/downloads/104842/en |
| A6 | FAA AC 23.1309-1E, System Safety Analysis and Assessment for Part 23 Airplanes | 11/17/2011 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC%2023.1309-1E.pdf |
| A7 | 14 CFR 25.703 Takeoff warning system (Amdt 25-42) | LII page, read 2026-11-04 | https://www.law.cornell.edu/cfr/text/14/25.703 |
| H1 | Wickens & Dixon (2007), The benefits of imperfect diagnostic automation: a synthesis of the literature. *Theor. Issues Ergon. Sci.* 8(3), 201–212. doi:10.1080/14639220500370105 | abstract via OpenAlex | https://api.openalex.org/works/doi:10.1080/14639220500370105 |
| H2 | Dixon, Wickens & McCarley (2007), On the independence of compliance and reliance: are automation false alarms worse than misses? *Hum. Factors* 49(4), 564–572. PMID 17702209 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/17702209/ |
| H3 | Dixon & Wickens (2006), Automation reliability in UAV control: a reliance-compliance model. *Hum. Factors* 48(3), 474–486. PMID 17063963 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/17063963/ |
| H4 | Bliss, Gilson & Deaton (1995), Human probability matching behaviour in response to alarms of varying reliability. *Ergonomics* 38(11), 2300–2312. doi:10.1080/00140139508925269 | abstract via OpenAlex and UCF STARS. Bliss's 1993 UCF dissertation abstract (stars.library.ucf.edu/rtd/3614) is identical in design. | https://stars.library.ucf.edu/scopus1990/1980 |
| H5 | Bliss & Dunn (2000), Behavioural implications of alarm mistrust as a function of task workload. *Ergonomics* 43(9), 1283–1300. PMID 11014752 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/11014752/ |
| H6 | Bliss (2003), Investigation of alarm-related accidents and incidents in aviation. *Int. J. Aviat. Psychol.* 13(3), 249–268 | abstract via OpenAlex | doi:10.1207/S15327108IJAP1303_04 |
| H7 | Parasuraman & Riley (1997), Humans and automation: use, misuse, disuse, abuse. *Hum. Factors* 39(2), 230–253 | abstract via OpenAlex | doi:10.1518/001872097778543886 |
| H8 | Parasuraman, Hancock & Olofinboba (1997), Alarm effectiveness in driver-centred collision-warning systems. *Ergonomics* 40(3), 390–399 | abstract via OpenAlex | doi:10.1080/001401397188224 |
| H9 | Meyer (2004), Conceptual issues in the study of dynamic hazard warnings. *Hum. Factors* 46(2), 196–204 | abstract via OpenAlex | doi:10.1518/hfes.46.2.196.37335 |
| H10 | Dehais et al. (2014), Failure to detect critical auditory alerts in the cockpit: evidence for inattentional deafness. *Hum. Factors* 56(4), 631–644. PMID 25029890 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/25029890/ |
| H11 | Scannella et al. (2013), Effects of the audiovisual conflict on auditory early processes. *Int. J. Psychophysiol.* 89(1), 115–122. PMID 23774001 | PubMed abstract | — |
| H12 | Riedinger, Suied, Keane, Sciabica & Dehais (2026), Rough auditory alarms mitigate inattentional deafness during piloting-like task. *Hum. Factors* 68(8), 1078–1097. PMID 41823247 | PubMed abstract | — |
| H13 | Wickens et al. (2009), False alerts in air traffic control conflict alerting system: is there a "cry wolf" effect? *Hum. Factors* 51(4), 446–462. PMID 19899356 | PubMed abstract | — |
| H14 | Breznitz, S. (1984), *Cry Wolf: The Psychology of False Alarms*. Hillsdale NJ: Lawrence Erlbaum. ISBN 0898592968 | bibliographic record only (OpenLibrary) | — |

## 1. Regulatory alert conventions

### 1.1 Alert levels and colours
- **14 CFR 25.1322(b)** [D-ag, A2]:
  - Warning: "immediate flightcrew awareness and immediate flightcrew response".
  - Caution: immediate awareness and *subsequent* response.
  - Advisory: awareness, and may require a subsequent response.
- **25.1322(c)(2)** [D-ag, A2]: warning and caution cues must use at least two different senses (aural, visual or tactile).
- **25.1322(e)** [D-ag, A2]: red for warning; amber or yellow for caution; any colour except red or green for advisory. A1 §11 (p.12) repeats this.
- **CS 23.1322 (CS-23 Amdt 4, A4 p.1-F-6)** [D-ag]: if warning, caution or advisory lights are installed in the cockpit, they must be:
  - (a) **red** for warning lights, i.e. a hazard which "may require immediate corrective action";
  - (b) **amber** for caution lights, i.e. the possible need for future corrective action;
  - (c) green for safe operation;
  - (d) any other colour, including white, for other lights, if it differs enough from (a)–(c);
  - (e) effective under all probable cockpit lighting conditions.
- **Applicability** [D-ag, A5 §A.II]: the Extra NG certification basis is **CS-23 incl. Amdt 4** (reference date 11 Oct 2016; TC 11 Oct 2019). So the prescriptive CS 23.1322 above is the colour rule that applies to an Extra NG retrofit. Whether a minor change would be assessed against a later CS-23 amendment is **not verified**.
- **AC 23.1311-1C §22.7 (A3 p.47–48)** [D-ag]: use red for emergency conditions that need immediate pilot recognition; amber for abnormal conditions that need immediate awareness and possibly later action; white or another unique colour for advisories; green for safe conditions. §22.6 (p.47): colour "should not be the sole means of discrimination"; pair it with text or a symbol.
- **AC 23.1311-1C §18.5 (p.44)** [D-ag]: visual alerts for warnings that require immediate pilot action "should be annunciated with an aural warning".

### 1.2 Door-warning requirement (closest CS-23 analogue)
- **CS 23.783(e)(3)** (A4 p.1-D-16) [D-ag]: requires a visual warning to the flight crew if an external door is "not fully closed and locked". Any failure, or combination of failures, that would give an erroneous closed-and-locked indication must be **improbable** (for doors whose initial opening movement is not inward).
- **CS 23.783(e)** scope [D-ag]: (e) applies to commuter-category doors, to each external door **forward of any engine or propeller** on normal, utility or aerobatic aeroplanes, and to pressure-vessel doors.
- **CS 23.783(e)(2)** [D-ag]: also requires direct visual inspection of the locking mechanism.
- R4 interpretation [Y]: the Extra NG canopy is aft of the propeller, so (e) may not formally apply. It is still the most direct numerical benchmark for a "not locked" indicator.
- **AC 23.1309-1E §11.b (A6 p.18)** [D-ag]: "No probable failure should result in a 'safe' indication of an 'unsafe' condition". **For our design, this is the governing rule for missed alerts.**
- **AC 23.1309-1E Figure 2 (A6 p.23)** [D-ag], allowable probabilities per flight hour, **Class I** (typically SRE ≤ 6,000 lb):
  - Minor (probable) < 10^-3
  - Major (remote) < 10^-4
  - Hazardous (extremely remote) < 10^-5
  - Catastrophic (extremely improbable) < 10^-6
- **AC 23.1309-1E §bb (A6 p.14)** [D-ag]: "improbable" maps to the major/hazardous values in Figure 2. Class I is therefore **10^-4 to 10^-5 per FH** for the erroneous-locked indication [Y: R4's mapping].
- Note [D-ag, A6 p.22]: these targets derive from a fatal-accident rate of about 10^-4/FH for single-engine aeroplanes under 6,000 lb, of which about 10 % is attributed to systems.

### 1.3 Alert inhibits, take-off phase and false-alert minimisation (AC 25.1322-1)
- **§7e (p.9)** [D-ag]: frequent false or nuisance alerts increase workload and reduce confidence in the alerting system. The crew "may ignore a real alert".
- **§8d (p.11)**: inhibits must prevent alerts that are inappropriate or unnecessary for a phase of operation. They should be used when (a) the alert could cause a hazard if the crew were distracted by it or responded to it, (b) it gives unnecessary information, or (c) several consequential alerts can be merged into one. Documentation must show that delayed or inhibited alerts do not hurt safety (§8a(5), p.10). [D-ag]
- **§12 (p.14)** [D-ag]: the design must:
  - (a) prevent inappropriate alerts;
  - (b) give a protected means to suppress the attention-getting part of an alert caused by an alerting-system failure;
  - (c) let warning and caution cues be acknowledged and then suppressed;
  - (d) remove the alert when the condition clears;
  - (e) not rely on pulling circuit breakers as the primary means to suppress a false alert.
- **Appendix 5 (p.A5-3)** [D-ag]:
  - "False alert": an incorrect or spurious alert caused by a failure of the alerting system **including the sensor**.
  - "Nuisance alert": an alert from a system working as designed that is inappropriate or unnecessary for the condition.
  - R4 note [Y]: **these two need separate rates in the Monte Carlo.**
- **§13 (p.15)** [D-ag]: compliance evaluation includes "inhibiting alerts for specific phases of flight (for example, takeoff and landing)".
- **14 CFR 25.703 (A7)** [D-ag, LII summary]:
  - (a) an aural warning is required during the initial take-off roll if flaps, slats, spoilers, speed brakes or trim are in an unsafe take-off position;
  - (b) it continues until the configuration is corrected, the take-off is rejected, the aircraft rotates, or the pilot silences it.
  - R4 interpretation [Y]: this is the closest analogy for a canopy "not locked" alert triggered by throttle advance or the take-off roll.
- Airbus ECAM "T.O. INHIBIT" (many warnings inhibited from 80 kt to 1,500 ft or 2 min): **only forum and flashcard sources found, NOT VERIFIED.** Do not cite.

### 1.4 Aural alerts (AC 25.1322-1 Appendix 2, p.A2-1 to A2-5) [D-ag]
- Frequencies 200–4,500 Hz. Use at least two frequencies, or one with distinct spacing, and avoid frequencies that dominate cockpit noise (A2-1).
- Audible in the worst-case noise with or without headsets. Automatic volume control is recommended (A2-1/A2-2).
- Number of unique tones: fewer than 10. One master warning tone and one master caution tone. No master aural for advisories (A2-2).
- Onset/offset ramps of 20–30 ms; onset 20–30 dB above ambient "is acceptable" (A2-2).
- Warning and caution tones repeat until acknowledged or the condition clears. Caution: one presentation, then auto-cancel if continuous awareness is not needed (A2-3).
- Voice: an "alarming tone indicating tension or panic" is not recommended (A2-4). Voice starts at the same time as its visual alert (A2-4).
- AC 25.1322-1 §6 (p.7) [D-ag]: warning and caution use two senses (master visual + aural, or visual + voice). Advisories do not need two senses (p.8).

## 2. Empirical HF findings: cry-wolf, reliability thresholds, attention

| # | Finding | Number | Source | Tag |
|---|---|---|---|---|
| 1 | Below this reliability, diagnostic automation is worse than no automation (crossover point) | **0.70** reliability; 20 studies, 35 data points; the effect is stronger under high workload | H1 abstract, pp.201–212 | D-ag |
| 2 | False-alarm-prone automation hurt overall performance more than miss-prone automation. False alarms reduced both compliance and reliance; misses reduced only reliance | 32 participants | H2 abstract, pp.564–572 | D-ag |
| 3 | With low-reliability aids, false alarms correlated with poorer performance on the failure task, and misses with poorer performance on concurrent tasks. "Aids must be fairly reliable" | 32 + 24 participants (incl. some pilots) | H3 abstract, pp.474–486 | D-ag |
| 4 | Probability matching: about 90 % of participants match their response rate to the true-alarm probability; about 10 % respond all-or-none | 138 students; alarm reliability 25 / 50 / 75 % true alarms | H4 abstract, pp.2300–2312 | D-ag |
| 5 | Higher primary-task and alarm workload degrade alarm response. Probability matching was replicated | 126 students | H5 abstract, pp.1283–1300 | D-ag |
| 6 | In ASRS, NTSB and US Army data, alarm problems are frequent and "false alarms remain a significant concern" | counts not in the abstract | H6 abstract | D-ag |
| 7 | Disuse of automation is "commonly caused by alarms that activate falsely", often because the **base rate** is ignored when setting the false-alarm/miss trade-off | — | H7 abstract, pp.230–253 | D-ag |
| 8 | Even a sensitive alarm can have a low posterior probability (PPV) when the event base rate is low, so "only a small proportion of alarms" are true | analytical | H8 abstract, pp.390–399 | D-ag |
| 9 | Compliance (acting on an alarm) and reliance (trusting silence) are distinct responses | conceptual | H9 abstract | D-ag |
| 10 | Inattentional deafness: during a windshear, **11 of 28 GA pilots (39.3 %)** did not react to an auditory alarm; with no windshear, all 28 perceived it | 28 GA pilots, simulator landings | H10 abstract, pp.631–644 | D-ag |
| 11 | A rare alarm that conflicts with the visual scene gives a smaller auditory N100, i.e. the alarm is gated out early | 13 participants (ERP) | H11 abstract | D-ag |
| 12 | Rough alarms (amplitude modulation in the 30–150 Hz range) gave higher hit rates with no cost in false alarms, RT or primary task | 27 participants | H12 abstract | D-ag |
| 13 | Counter-example: ATC conflict alerts were 45 % false (0.28–0.58 by centre), yet there was **no cry-wolf effect**, because controllers could verify and anticipate the conflicts | 495 alerts | H13 abstract, pp.446–462 | D-ag |
| 14 | Breznitz (1984) is the source monograph on the cry-wolf effect | book; content not read | H14 | Y (bibliographic only) |

### Design implications for the Monte Carlo and the design (R4 interpretation, all [Y])
1. **Use reliability, measured as PPV, as a hard gate.** Wickens & Dixon's 0.70 is a lower bound for automation to be net-beneficial (H1). Bliss's probability matching (H4) suggests the pilot's response probability ≈ the perceived PPV. In the MC, model P(pilot acts | alert) ≈ PPV(alert) as a first-order assumption, citing H4. The ~10 % of all-or-none responders can form a separate population.
2. **Compute PPV from the base rate.** The canopy is rarely unlocked at take-off, so even a low per-flight false-alarm probability gives a poor PPV (H7, H8). The MC should report PPV, not only P(FA).
3. **False alarms cost more than misses in trust** (H2, H3). This is in tension with AC 23.1309-1E §11.b (no probable failure may give a safe indication of an unsafe condition, i.e. misses must be improbable). The architecture must meet both at once. This argues for 2-out-of-2 sensing for "LOCKED" (fail toward alert) plus a check of sensor disagreement or plausibility, so that a sensor fault shows as a *caution* "CANOPY SENS" rather than as a false red warning.
4. **Arm the alert on throttle advance or the take-off roll**, like the 25.703 take-off configuration warning (A7). Do not alert continuously on the ground with the canopy open, which is a nuisance per A1 App. 5. Inhibit the aural (not the visual) at high-workload moments only if the analysis shows no safety loss (A1 §8a(5)).
5. **Aural is not guaranteed under workload** (39.3 % miss under windshear, H10). The take-off roll is high-workload, so pair the aural with a red light in the primary field of view and keep the visual on until the condition clears (A1 §12d). A rough or modulated tone may improve detection (H12; one lab study).
6. **Verifiability lowers the cry-wolf cost** (H13). If the pilot can verify the canopy state quickly (a visible latch-pin window, cf. CS 23.783(e)(2)), false alerts are less corrosive.

## NOT VERIFIED

1. Full texts of H1–H13: not read (paywalled). No per-condition response rates, effect sizes or page-level citations are available. Bliss's dissertation PDF is behind a Cloudflare bot check and was not bypassed.
2. Getty, Swets, Pickett & Gonthier (1995), *J. Exp. Psychol. Appl.* 1(1), 19–33, response time vs warning predictive value: bibliographic data only (OpenAlex). No abstract and no numbers.
3. CS-25 / AMC 25.1322 (EASA): not downloaded. FAA text was used instead. EASA CS-25 Amdt 11+ is believed to be harmonised, but that is not checked.
4. ASTM F3117 (Crew Interface in Aircraft), SAE ARP4102-4, SAE ARP5364: paywalled, not read.
5. Airbus and Boeing take-off inhibit logic: no primary source.
6. Whether a canopy counts as an "external door" under CS 23.783: not verified (no AMC 23.783 text read).
7. Full current text of 14 CFR 25.703 (any paragraph added after Amdt 25-42): only the LII summary was read.
