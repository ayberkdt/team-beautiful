# R7 — Auditory alerting in depth: noise at the ear, audibility rules, voice vs tone, Garmin audio paths, disabling

- read by: subagent R7-aural
- date read: 2026-11-05 (16:49–17:10 laptop time, UTC+3)
- Tags: **[D-ag]** = read at the source in this session (URL + page/section given). **[Y]** = secondary source, or R7's own arithmetic or design interpretation.
- Scope: this file does **not** repeat R4 (AC 25.1322-1 App. 2 aural specs, cry-wolf abstracts, Riedinger 2026 abstract) or R6 (Dehais 2019 57.7 % missed; Callan 2018 DR400 38 % missed). It adds to them.
- Local copies (untrusted data): `D:\tmp_ideathon\easa\dl\r7_aural\` (PDFs + `.txt` extracts made with pdftotext; NTSB reports in `ntsb\`). Python that touched them ran with `python -I` from the scratchpad.
- No paywall, login, Cloudflare/Anubis bot check or 403 was bypassed. Each was tried once and recorded below.

## Sources

| ID | Document | Edition / what was read | URL |
|---|---|---|---|
| P1 | Patterson, R.D., *Guidelines for auditory warning systems on civil aircraft* (prepared for the CAA Airworthiness Division; published as CAA Paper 82017) | Typed manuscript no. 413/II, dated 02.02.1982, 97 PDF pp., hosted by Cambridge (the author's own upload). Read: Summary, §0.2–0.3 (pp.3–10), §1.1 (pp.12–13), §3.1 (pp.28–30), §3.4 (p.37), §4.1–4.2 (pp.38–40), §5.1, §5.3.2 (pp.41–47), App. A §1.1–1.2 (pp.2–4), App. C (pp.30–32) | https://www.pdn.cam.ac.uk/system/files/documents/AuditoryWarningSystems_CAA82017.pdf |
| P2 | Lower, Wheeler, Patterson, Edworthy, Shailer, Milroy, Rood & Chillery, *The design and production of auditory warnings for helicopters. 1: The Sea King*, ISVR Report AC527A, Oct 1986 | Summary (p.1), §4.3.1–4.3.2 (pp.14–15), §5.2.2–5.2.3 (pp.23–24), priority grouping (p.16) | https://generic.wordpress.soton.ac.uk/isvr-new/wp-content/uploads/sites/422/2024/02/AC527A_helicopter_auditory_warnings_ocrscan.pdf |
| I1 | ISO 7731:2003, *Ergonomics — Danger signals for public and work areas — Auditory danger signals* | Official free preview (iTeh sample), pp.1–5: §4.2.2, §4.4, §6.2. Annex B (masked-threshold method) **not** in the preview | https://cdn.standards.iteh.ai/samples/33590/23420e332c4c49c781f090ab4d915518/ISO-7731-2003.pdf |
| F1 | FAA CAMI, *Hearing and Noise in Aviation*, pilot safety brochure AM-400-98/3 | pp.1–3 (table checked on a rendered image of p.2) | https://www.faa.gov/pilots/safety/pilotsafetybrochures/media/hearing.pdf |
| F2 | FAA AC 20-133, *Cockpit noise and speech interference between crewmembers*, 22 Mar 1989 | §2b–c, §3, App. 5 (OCR text; the App. 4 example table is too garbled to use) | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-133.pdf |
| F3 | FAA InFO 07001, *Noise attenuation properties of noise-canceling headsets*, 5 Jan 2007 | full (1 p.) | https://www.faa.gov/sites/faa.gov/files/other_visit/aviation_industry/airline_operators/airline_safety/inFO07001.pdf |
| N1 | Unruh & Till, *General Aviation Interior Noise: Part III — Noise Control Measure Evaluation*, NASA/CR-2002-211667, May 2002 | §3.1 Fig. 3.2, §3.1.2, §3.2, §5 Table 5.8 (p.5-11); other page numbers unclear in the text extract, so sections are cited | https://ntrs.nasa.gov/api/citations/20020059662/downloads/20020059662.pdf |
| O1 | Lamm & Lawrence, "Interior sound levels in general aviation aircraft", *Occupational Health & Safety*, 12 Jul 2010 (Embry-Riddle field study; magazine article) | full web article | https://ohsonline.com/Articles/2010/07/12/Interior-Sound-Levels-in-General-Aviation-Aircraft.aspx |
| M1 | Müller & Schneider, "Noise exposure and auditory thresholds of German airline pilots", *BMJ Open* 7(5):e012913 | Abstract, Methods, Results (web page) | https://bmjopen.bmj.com/content/7/5/e012913 |
| DC1 | David Clark Co., helicopter passive headsets page (H10-13H octave attenuation table) and H10-13H data sheet 19601P-82 (07-16) | full page; data sheet p.1 | https://www.davidclarkcompany.com/aviation/helicopter-passive.php ; https://www.davidclarkcompany.com/files/literature/H10-13H.pdf |
| DC2 | David Clark DC ONE-X data sheet 19549P-14 (02-16); ENC Hearing Protector bulletin 19537P-44 | p.1 each | https://www.DavidClarkCompany.com/files/literature/DC%20ONE-X%20Data%20Sheet.pdf ; https://www.davidclarkcompany.com/files/literature/ENC%20Hearing%20Protector.pdf |
| G1 | Garmin GMA 245/245R Installation Manual 190-01879-11 **Rev. 14** (Jul 2023) | §1.2–1.3 (pp.1-1 to 1-5), §2.9 (pp.2-9/2-10), §3.7.6, §4.6.3, §4.6.5, §4.6.9 (pp.4-8 to 4-12) | https://static.garmin.com/pumac/190-01879-11_14.pdf |
| G2 | Garmin G3X/G3X Touch Avionics Installation Manual 190-01115-01 **Rev. AZ** (Sep 2025) | §2.1.1.19 (p.2-14), §23.3.10–23.3.11 (p.23-22), Sound config (p.30-150), discrete-input functions (pp.30-213/214), sensor-wiring note 13 (Fig. 26-1, p.26-1) | https://static.garmin.com/pumac/190-01115-01_az.pdf |
| G3 | Garmin G1000 Audio Panel (GMA 1347) Pilot's Guide 190-00378-02 Rev. A, §6A, p.6A-4 | **third-party copy on ManualsLib** (Garmin original not opened) | https://www.manualslib.com/manual/1587779/Garmin-G1000.html?page=6 |
| B1 | Begault & Pittman, *3-D audio versus head-down TCAS displays*, NASA CR-177636, Mar 1994 | stimulus (pp.5–6), Results and Conclusions (pp.8–9) | https://ntrs.nasa.gov/api/citations/19940028557/downloads/19940028557.pdf |
| B2 | Begault (1993), *Head-up auditory displays for TCAS advisories: a preliminary investigation*, Human Factors 35(4) | NTRS abstract 20000023210 only | https://ntrs.nasa.gov/citations/20000023210 |
| A1 | Arnal et al. (2019), "The rough sound of salience enhances aversion through neural synchronisation", *Nat. Commun.* 10:3671 | full text via Europe PMC PMC6694125 (abstract, Introduction, Results §1, Discussion) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6694125/fullTextXML |
| S1 | Simpson & Williams (1980), "Response time effects of alerting tone and semantic context for synthesized voice cockpit warnings", *Hum. Factors* 22(3):319–330 | NTRS abstract 19800064780 | https://ntrs.nasa.gov/citations/19800064780 |
| S2 | Simpson & Marchionda-Frost (1984), "Synthesized speech rate and pitch effects on intelligibility of warning messages for pilots", *Hum. Factors* 26(5) | NTRS abstract 19850039460 | https://ntrs.nasa.gov/citations/19850039460 |
| V1 | Arrabito (2009), "Effects of talker sex and voice style of verbal cockpit warnings on performance", *Hum. Factors* 51(1):3–20. PMID 19634305 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/19634305/ |
| V2 | Arrabito (2001), "The relation of vocal emotions and gender to convey urgency of verbal auditory warnings", *Canadian Acoustics* 29(3):68 | full (1 p., preliminary results) | https://jcaa.caa-aca.ca/index.php/jcaa/article/download/1387/1130 |
| E1 | Edworthy, Loxley & Dennis (1991), *Hum. Factors* 33(2):205–231. PMID 1860703 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/1860703/ |
| E2 | Hellier, Edworthy & Dennis (1993), *Hum. Factors* 35(4):693–706. PMID 8163282 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/8163282/ |
| E3 | Haas & Casali (1995), *Ergonomics* 38(11):2313–2326. PMID 7498190 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/7498190/ |
| E4 | Graham (1999), "Use of auditory icons as emergency warnings", *Ergonomics* 42(9):1233–1248. PMID 10503056 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/10503056/ |
| E5 | McNeer et al. (2018), "Auditory icon alarms are more accurately and quickly identified…", *Anesthesiology* 129(1):58–66. PMID 29698253 | PubMed abstract | https://pubmed.ncbi.nlm.nih.gov/29698253/ |
| H10 | Dehais et al. (2014), *Hum. Factors* 56(4):631–644. PMID 25029890 (already R4 #10) | PubMed abstract, re-read only for the **pre-exposure** sentence not in R4 | https://pubmed.ncbi.nlm.nih.gov/25029890/ |
| T1 | NTSB ATL87LA129 (gear horn breaker pulled as nuisance) | final report p.1 | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/7421/pdf |
| T2 | NTSB ATL86LA191 (horn silenced by holding the test button, then paper under it) | p.1 | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/7144/pdf |
| T3 | NTSB LAX01LA148 (new noise-attenuating headset; horn not recognised) | p.1 | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/52105/pdf |
| T4 | NTSB GAA17CA023 (horn not routed to headset; quotes FAA SAIB CE-16-08) | p.1 | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/94219/pdf |
| T5 | NTSB CEN16LA189 (gear horn mistaken for stall horn) | p.1 | https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/93196/pdf |
| T6 | NASA ASRS *CALLBACK* No. 247, Jan 2000 ("Unhappy Landings") | web page | https://asrs.arc.nasa.gov/publications/callback/cb_247.htm |

---

## 1. Noise at the pilot's head

1. **Light single cockpit, unprotected:** "Small Single Plane (Cockpit)" **70–90 dB** [D-ag, F1 p.2 table, checked on the rendered page]. The brochure gives no weighting or phase.
2. **Spectrum shape:** in fixed-wing cockpits the primary energy lies at **100–300 Hz** and falls rapidly above. Overall levels range from **~70 dB(A) to >100 dB(A)**. **The noisiest cockpits are open-cockpit aeroplanes** (e.g. agricultural) [D-ag, F2 §2b]. Within one light-single class, the spread between airframes of one type can be as large as the spread across types [D-ag, F2 §2c].
3. **Speech interference:** above **88 dB(A) (PSIL 78)** the FAA expects interference with normal cockpit speech [D-ag, F2 §3]. Better circumaural headset muffs "may attenuate cockpit noise more than 20 dB" [D-ag, F2 App. 5]. F2 also says a test should cover windows open in flight if that is possible [D-ag, F2 measurement section].
4. **Measured piston single (Cessna 182E test bed, "Baseline Aircraft @ 2,400 rpm, 75% Power Cruise", interior microphone spectra to 1 kHz):** **91.3 dB(A)** with a 2-blade and **90.7 dB(A)** with a 3-blade propeller [D-ag, N1 §3.1 Fig. 3.2]. Main tones: 80 Hz blade passage, 120 Hz firing, 160 Hz and 240 Hz harmonics [D-ag, N1 §3.1.2]. Power matrix flown at 5,000 ft: noise **rises with power**; 2,400→2,600 rpm changed the forward cabin by ~2 dB [D-ag, N1 §3.2]. Cessna 206, pilot position: **96.0 dB(A)** bare cabin, **93.2 dB(A)** standard interior [D-ag, N1 Table 5.8, p.5-11].
5. **Under-headset reduction in real use (passive):** Cessna 172S and PA-44, two dosimeters (one in the cabin ~6 in behind the ears, one inside a David Clark H10-13.4): the headset lowered the projected 8-h level by **13 dB(A) on average**; mean of 8 maximum cabin readings **101.3 dB(A)**; projected 8-h TWA in the cabin **86.3 dB(A)** [D-ag, O1; a magazine report of an ERAU study, so treat as secondary-quality data].
6. **Headset lab attenuation (passive), H10-13H (same design base as H10-13.4):** 125 Hz **16.6**, 250 **20.7**, 500 **27.4**, 1 k **33.0**, 2 k **30.5**, 3 k **36.2**, 4 k **38.1**, 6–8 k **36.6** dB; NRR 23 dB [D-ag, DC1 web table]. Ear-cup speaker response **200–5,500 Hz**; characteristic SPL **~95 dB SPL (1 kHz, 1 mW)** at maximum volume [D-ag, DC1 data sheet].
7. **ANR adds attenuation only at low frequency:** DC ONE-X "ENC peak attenuation **30 dB @ 150 Hz**", ENC range **20 Hz–1 kHz** [D-ag, DC2]. David Clark ENC protector: passive 27 dB plus **17–22 dB more "at lower frequencies"** [D-ag, DC2 bulletin]. So above ~1 kHz, where alert energy sits, ANR and passive headsets give about the same attenuation [Y].
8. **Comm audio is louder than the cockpit:** in 9 airline jet types, cockpit ambient was **74–80 dB(A)**, but the level **under the headset was 84–88 dB(A)**, driven by ATC audio (manikin measurement, passive supra-aural headset) [D-ag, M1 Abstract, Methods]. [Y] Pilots set radio audio about 8–10 dB above what leaks through. **The alert therefore competes mainly with radio and intercom speech, not engine noise.**
9. **Hot microphone raises the noise at the ear:** "A single active microphone can add up to **30 dB** to the residual noise at the ear"; a warning set for mics-off "may be inaudible when a microphone is switched on" [D-ag, P2 §4.3.1, p.14]. P2 therefore set the floor at **masked threshold +15 dB or 70 dB SPL, whichever is higher** [D-ag, P2 §4.3.1, p.15].
10. **Extra NG (AEIO-580, 3-blade, bubble canopy), open or broken canopy:** **no measured data found.** The only open-cockpit figures were a forum post (Pitts S-2A, "126 dB" in climb, no weighting) seen in a search snippet: **not read, NOT VERIFIED, do not cite**.

**Worked estimate for our aircraft [Y, R7 arithmetic, illustrative only].** Assume a cabin spectrum with the shape of finding 2 (flat 125–250 Hz, then −5 dB/octave) scaled to 90 / 96 / 102 dB(A) at the rear-seat head at take-off power, canopy closed. Subtract the H10-13H lab attenuation (finding 6):

| Cabin, dB(A) | Under headset, lab fit, dB(A) | Under headset, "−13 dB(A) real fit" (O1) | Octave levels under headset at 1 / 2 / 4 kHz, dB |
|---|---|---|---|
| 90 | 66.5 | 77 | 50 / 48 / 35 |
| 96 | 72.5 | 83 | 56 / 54 / 41 |
| 102 | 78.5 | 89 | 62 / 60 / 47 |

Add radio speech at about +8 dB over leakage (M1 analogy) and a possible hot mic (+up to 30 dB, P2). **Design level range under the headset: ~85–100 dB(A) for the in-flight warning**, ~10–15 dB less for the taxi chime. Headset headroom: 65 mW (G1 Table 1-3) ≈ +18 dB over 1 mW, so ≈ **113 dB SPL** maximum at 1 kHz [Y: 95 + 10·log10(65)]. Headroom is not the limit; annoyance is (finding 13).

## 2. Audibility rules (how far above the masker)

11. **ISO 7731:2003** [D-ag, I1]:
    - §4.2.2.1: signal ≥ **65 dB(A)** everywhere in the reception area. If hearing protectors are worn, "their levels of attenuation shall be known and introduced into the assessment".
    - §4.2.2.2: A-weighted method: **L_S,A − L_N,A > 15 dB**.
    - §4.2.2.3: octave method: signal > effective masked threshold by **≥ 10 dB** in one or more octave bands.
    - §4.2.2.4: 1/3-octave method: > masked threshold by **13 dB** in one or more 1/3-octave bands.
    - §4.4: if ambient > **100 dB(A)**, add visual signals rather than rely on sound alone; never exceed **118 dB(A)**.
    - §6.2: the 15 dB + 65 dB(A) pair is "sufficient but not always necessary"; a lower level may do if spectrum or timing clearly differ from the noise. Fright reactions: e.g. **> 30 dB rise in 0.5 s**.
12. **Patterson's psychometric basis** [D-ag, P1 App. A §1.1, pp.2–3; §1.1.1, p.12]: detection rises from chance to near-certain over **~20 dB**; about **5 % per dB** in the middle; "**10 dB above threshold it is easy to detect … 15 dB … difficult to miss**". Listener thresholds in broadband noise fall within **~3 dB** for most people [D-ag, App. A p.4].
13. **Upper limit and ceiling effect** [D-ag, P1 §1.1.2 p.13; App. A §1.2 pp.3–4]: upper limit **threshold +25 dB** (main text; §1.1 heading text says "not more than 30 dB"). Sounds **> 90 dB(A)** annoy "virtually everyone". In vigilance tests with sirens, more level above the asymptote did **not** improve detection; engrossed observers "occasionally fail to recognise a signal no matter what its level". **[Y] This is the psychoacoustic reason why inattentional deafness (R4 #10, R6 S6/S7) cannot be fixed by volume.**
14. **AC 25.1322-1 (R4 §1.4)** allows onset 20–30 dB above ambient. With findings 11–13, all three sources agree on **+15 dB minimum over the masked threshold**, with **+25 dB** as a sensible ceiling [Y].

## 3. Frequencies, timing and modulation

15. **Frequency band** [D-ag, P1 App. C §3, p.31]: components in **0.5–5.0 kHz**; at least **4** harmonically related components; fundamental **150–1,000 Hz**; at least four prominent components in **1.0–4.0 kHz**.
16. **Propeller aircraft: components below 1 kHz are "essentially useless"** because low-frequency noise is so strong; standardising across types needs a lower bound near **1.0 kHz** [D-ag, P1 §3.1.1, pp.29–30]. Low-frequency components would need **> 85 dB SPL** even on a jet and risk clipping and harsh distortion [D-ag, same].
17. **Upper bound:** keep dominant components **< 5 kHz** (presbycusis); noise-induced loss peaks at **4–6 kHz** [D-ag, P1 §3.1.2, p.30]. Through military helmet telephones the usable top was only **3–3.2 kHz** [D-ag, P2 §4.3.2, p.15]. Our audio path: GMA 245 alert bandwidth **100 Hz–6.5 kHz** (−3 dB band for alerts **350 Hz–6.5 kHz**) [D-ag, G1 Table 1-3, pp.1-3/1-4]; H10-13H ear cup **200–5,500 Hz** (finding 6).
18. **Pulse timing** [D-ag, P1 App. C §2, pp.30–31]: onset/offset **20–30 ms**, rounded; pulse **100–150 ms**; inter-pulse **< 150 ms for urgent**, **> 300 ms for non-urgent**; **≥ 5 pulses** in a distinctive rhythm. Haas & Casali: shorter inter-pulse interval and higher level → higher urgency and shorter RT [D-ag, E3 abstract].
19. **On-time:** short bursts with **5–10 s** silent gaps convey the information while leaving room for crew talk [D-ag, P1 §0.2.2, pp.3–4]. Patterson's prototype: moderate start, voice once, then background level, then return at maximum urgency if not corrected (32-s cycle); on-time < 25 % [D-ag, P1 §0.3.1–0.3.2, pp.6–7].
20. **Volume control** [D-ag, P1 §4.1, pp.38–39; App. C §4]: avoid a manual knob (crews set it on the quiet ground and it is then too low in flight). If automatic, limit it to **10–15 dB**, keyed to the noise in the octave around **2 kHz**, used mainly to turn warnings **down on the ground**.
21. **Frequency glide:** a rapid one-way sweep inside a 100-ms pulse "imparts a sense of urgency", reserved for high-priority warnings [D-ag, P1 §3.4, p.37].
22. **Roughness (amplitude modulation 30–150 Hz):** alarm signals exploit fast AM in this range. The rough-to-continuous transition was at **130 ± 6.5 Hz** (16 listeners); aversion peaks in the **lower roughness range, 40–80 Hz**; rough sounds synchronise salience and aversion networks [D-ag, A1 Abstract, Results §1, Discussion]. **Caveat [Y]:** A1 measures aversion, not detection in a cockpit. The detection benefit comes from the Riedinger 2026 abstract (R4 #12). Aversion is the very property that makes pilots silence or disable an alert (§6).
23. **Spatial (3-D) audio:** crews with a 3-D TCAS alert acquired targets **2.13 s vs 2.63 s** (−0.5 s, p < 0.0001; 24 targets) vs standard TCAS, with no difference in number acquired [D-ag, B1 Results pp.8–9]. Without a head-down display, the 3-D advantage was **~2.2 s** [D-ag, B2 abstract]. B1's alert: two 66-ms complex "BIP" tones, then "TRAFFIC" **462 ms**, 180 ms gap, "TRAFFIC" 462 ms; total **1.36 s**; the harmonically rich pre-tone was noticeable **~10 dB below** the speech [D-ag, B1 pp.5–6]. **[Y] For a canopy alert the benefit is small:** the pilot does not need to search for the hazard. A stereo cue "behind and above" is cheap with a stereo headset but is optional.

## 4. Voice vs tone vs auditory icon

24. **Voice: easy to learn, hard to confuse, but slow and competes with speech.** Patterson: voice warnings "are easy to learn and difficult to forget or confuse", but take longer and add to the speech already on the flight deck; for immediate-action warnings use a **brief key-word** voice to support a warning sound, not repeated in the background phase; full phrases for lower-priority messages, repeated after a pause [D-ag, P1 §0.2.5 p.5; §0.3.5 pp.9–10; §5.1 pp.41–42; App. C §5 pp.31–32]. Vowels are ~**30 dB** stronger than consonants, so voice cannot be played as a quiet background version [D-ag, P1 §0.3.5 p.10]. Place the first-formant peak near the top of the +15…+25 dB range; **~3 dB/octave whitening** over 0.5–4 kHz helps intelligibility [D-ag, P1 §5.3.2, pp.45–47].
25. **A tone before the voice slowed responses.** Airline pilots, fixed-base simulator with ATC radio, engine noise and talk: "responses were slower with an alerting tone"; adding a word to the voice message did **not** lengthen response time [D-ag, S1 NTRS abstract; size of the effect not in the abstract].
26. **Speech rate** affected response time and pilot ratings, not intelligibility; pilots who forgot to respond still recalled **90 %** of messages 8–10 s later [D-ag, S2 NTRS abstract].
27. **Which voice:** in speech babble (simulated radio traffic), a **male** talker in a **monotone or urgent** style gave the highest proportion correct and fastest identification; in quiet, talker sex did not matter [D-ag, V1 abstract]. A preliminary study: one-word warnings ("Bingo, Caution, Climb, Gear, Lock, Warning") identified correctly in **97.3 % of 1,872 trials** during visual tracking; female talker −45 ms RT in quiet [D-ag, V2].
28. **Abstract tones get confused.** NTSB CEN16LA189: the pilot "mistaken the gear-up warning horn for the stall warning horn" and landed gear-up [D-ag, T5 p.1]. Patterson: naive listeners learn ~**7** arbitrary warnings quickly; more need much more training [D-ag, P1 §4.2, pp.39–40].
29. **Auditory icons:** in a car, a horn/skid icon gave **faster braking RT** than a tone or the voice "ahead", but **more inappropriate responses** [D-ag, E4 abstract]. Anaesthetists identified icon alarms correctly **88 %** vs **43 %** for standard melodic alarms; RT **12 vs 15 s** [D-ag, E5 abstract]. [Y] There is no natural icon for "canopy unlocked"; a wind-rush icon would be confused with real wind noise. Not recommended.
30. **Urgency can be engineered:** fundamental frequency, harmonic series, envelope, speed, rhythm and pitch range all shift perceived urgency predictably [D-ag, E1 abstract]; the effects follow Stevens power laws, and some parameters weigh more than others [D-ag, E2 abstract].
31. **Pre-exposure helps detection.** In Dehais 2014, of the pilots who first met the alarm without the windshear and detected it, **only 3** then missed it in the windshear run; the authors propose case-based learning [D-ag, H10 abstract; this detail is not in R4].

## 5. Garmin practice: how a canopy alert reaches the ear

32. **G3X Touch has a built-in "Canopy Closed" discrete function** [D-ag, G2 p.30-214]: with the input inactive a **solid yellow CANOPY OPEN** message shows on the PFD; "**If engine power is increased or the aircraft is airborne, the CANOPY OPEN message will flash red and an alert tone will sound**". A Logic Signal can replace the power/airborne trigger. A "User-Defined Alert" in red also "will generate an audible warning tone" [D-ag, same]. **[Y] This is almost exactly our phase logic (amber on the ground, red + aural at power or airborne). Garmin uses a tone here, not a voice.**
33. **Fail-safe wiring advice:** use the **grounded state as the normal position (canopy closed)** "to avoid the possibility of a latent failure such as a broken wire or microswitch" [D-ag, G2 §26.1 Fig. 26-1 note 13, p.26-1].
34. **Audio path in G3X:** alert audio is generated by the GDU displays; typically PFD1 alert audio is wired to the audio panel or intercom [D-ag, G2 §2.1.1.19, p.2-14]. The GDU **mono audio output** is for "an **unswitched** input on an intercom or audio panel" [D-ag, G2 §23.3.10.1, p.23-22]. Alert audio can go to mono, stereo or both; a **Master Alert Volume 0–100 %** is set in configuration [D-ag, G2 p.30-150].
35. **GMA 245 audio panel** [D-ag, G1]:
    - **4 unswitched alert inputs**, each with a configurable volume set at installation; 600 Ω; 5 Vrms max (§1.2.1, Table 1-3, pp.1-2/1-3).
    - **"Alerts Mute Music"** option, **enabled by default** (§2.9.4, p.2-10).
    - Headset amplifier **65 mW into 150 Ω** (Table 1-3, p.1-4).
    - **Speaker output 3 W** (14 V, 4 Ω); 10 W/7 W at 28 V; **speaker disabled below 11 V** (Table 1-4 and §1.3.3, p.1-5).
    - **Fail-safe:** with power off or unit failure, the pilot headset is wired straight to COM 1, plus an optional **FAILSAFE WARN AUDIO** input heard in the **pilot's left ear**; summing resistors may be needed (§4.6.5, p.4-9).
    - Speaker check text covers selected receivers (COM/NAV/AUX) only; the manual does **not** say whether alert inputs are also sent to the speaker (§3.7.6) → **NOT VERIFIED**.
36. **G1000 GMA 1347:** "four (4) unmuted/unswitched inputs that are always present on the headsets **or speaker**" (Altitude warning, Unswitched 1–3) [D-ag, G3 p.6A-4, ManualsLib copy]. A search snippet (not opened) says that in fail-safe mode audio is not available on the speaker → NOT VERIFIED.
37. **DC ONE-X headset** has its own Bluetooth; "Audio Mute — reduces auxiliary audio volume and prevents missed communications"; fail-safe passive operation if the battery dies [D-ag, DC2]. [Y] Music fed **inside the headset** by Bluetooth is not muted by the audio panel's "Alerts Mute Music"; whether the headset's own mute reacts to panel alerts is not stated.

## 6. Annoyance, disabling and masking in GA (field evidence)

38. **Nuisance → breaker pulled:** "He had disarmed the landing gear warning system by pulling the system circuit breaker **because it was activating at normal power settings**"; he forgot to reset it and landed gear-up [D-ag, T1 p.1].
39. **Silenced by hand, then with paper:** pilot and passenger "took turns holding the test button in to keep the horn silent. Finally they put a piece of paper under the button" [D-ag, T2 p.1].
40. **Speaker-only horn + headset = unheard:** LAX01LA148: new noise-attenuating headset; pilot "did not recognize the gear warning horn"; it "was still sounding as he removed his headset" [D-ag, T3 p.1]. GAA17CA023: the horn "was not designed to sound through the headset/intercom system"; NTSB quotes FAA **SAIB CE-16-08** (pilots "may be unaware of … audible warning annunciations in the cockpit that do not come through the intercom system") [D-ag, T4 p.1]. ASRS: "unable to hear gear warning horn because of new noise canceling headsets … completely masked" [D-ag, T6]. FAA InFO 07001 asks operators to test on the ground and in flight whether alarms are audible with ANR on, or find other solutions [D-ag, F3].
41. **Crew dislike of loud warnings:** IATA survey of 46 airlines: "Most aural alerts … are too loud"; crews were seen with "a finger poised over the cancel button" [D-ag, P1 §1.0.1 p.11; §0.2.4 p.5 — Patterson quoting surveys]. Patterson's design aim is warnings that crews do **not** immediately cancel [D-ag, P1 §0.3.4, p.8].
42. Earlier project evidence: DA40 shared canopy/door light ignored during open-canopy taxi (R0 FAA AD 2010-25-01); AC 25.1322-1 §12(e): do not rely on pulling breakers to silence false alerts (R4 §1.3).

---

## Design implications [Y]

All points below are R7's interpretation of the findings above.

**A. Where the sound goes (audio path).**
1. Feed the alert into an **unswitched alert input** of the audio panel (GMA 1347 "Unswitched 1–3", or GMA 245 Alert 1–4, or the G3X GDU mono alert output). Never a speaker-only horn: findings 40 show headsets mask such horns.
2. Also wire the alert unit to the audio panel's **fail-safe warning input** (GMA 245 J2402-29, with summing resistors, finding 35), so the voice survives an audio-panel failure.
3. Keep the **"Alerts Mute Music"** option on (default). Add one POH line: no Bluetooth music in the headset during take-off (finding 37).
4. Set the alert level at installation; **no pilot volume knob** for it (finding 20). A ground/airborne step of **−10 to −15 dB on the ground** is allowed (taxi chime quieter).

**B. How loud.**
5. Target: each prominent component **15–25 dB above the masked threshold under the headset**, measured or computed at the **take-off power** condition, with the intercom open (findings 9, 11–14). In practice: **~90–95 dB(A) at the ear for the red warning, ~78–85 dB(A) for the taxi chime** (worked estimate in §1). Check that the voice is ≥ **10 dB above typical COM audio** (finding 8).
6. Verify with a **ground run + flight test** under the pilot's own headset, passive and ANR, as FAA InFO 07001 asks (finding 40). If a dummy-head or MIRE measurement is possible, apply ISO 7731 §4.2.2.3: ≥ 10 dB over masked threshold in at least one octave band (1, 2 or 4 kHz).
7. Do not go above ~**100 dB(A)** at the ear: no detection gain (finding 13), more annoyance and disabling (findings 38–41).

**C. Spectrum.**
8. All alert energy in **1–4 kHz** (finding 16; prop noise makes < 1 kHz useless). Tone: fundamental **500–800 Hz** with ≥ 4 harmonics in 1–4 kHz; nothing important above 5 kHz (findings 15, 17).
9. Voice: male, **monotone-firm** style (finding 27), band-limited **350 Hz–5 kHz**, with **+3 dB/octave** tilt over 0.5–4 kHz (finding 24).

**D. Tone vs voice, wording, length, repetition.**
10. **In-flight / take-off-power warning: voice first, no attention tone in front of it** (finding 25). Word: **"CANOPY"** (3 syllables, ~0.45–0.5 s by analogy with "TRAFFIC" 462 ms, finding 23). Say it **twice** ("CANOPY, CANOPY", ~1.2 s), the TCAS pattern. Do not add "UNLOCKED": the light gives the detail, and S1 shows a longer message does not slow the response, but every extra word blocks the radio channel longer (findings 24–25).
11. Between voice bursts, use a **short rough tone burst** (5 pulses of 100–150 ms, < 150 ms gaps, AM at **~50–70 Hz**, findings 18, 22) **only for the red warning**. Never for the taxi chime: roughness is aversive, and aversion drives disabling (findings 22, 38–39).
12. **Repetition:** voice pair at onset; then the rough tone burst every **~5 s**; voice pair again at **~15 s** and every 15 s until the condition clears or the pilot acknowledges (findings 19, R4 §1.4). After acknowledgement: aural off, **red light stays on** until locked (R4 §1.3, AC 25.1322-1 §12d). Re-arm the aural if the state changes (e.g. lift-off).
13. **Taxi chime:** one soft two-tone chime (harmonic, "attenson" style, finding 15 / P1 §0.3.3), **once per state change**, no repeat. Must sound different from the Garmin stall and gear tones (finding 28).
14. **Keep the 40 kt → lift-off + 10 s deferral** of a *new* voice alert: Patterson says no warning needs an instantaneous response (P1 §0.2.2), and Dehais 2014 shows misses at peak load (R4 #10). The red light is **not** deferred.
15. **Pre-exposure:** a 2-s self-test ("CANOPY" + chime) at avionics power-on, and the alert demonstrated in the type briefing. This checks the audio path every flight and gives the pre-exposure benefit (finding 31).

**E. When the headset is lost or not plugged in.**
16. **Most of the value of the aural cue is before the canopy opens** (taxi, run-up, take-off roll, first climb). The headset is on then. Once the canopy has opened or broken up, the alert brings no new information: the pilot already knows.
17. **A cockpit speaker is not worth it** for the headset-lost case. With the canopy gone the noise is far above **100 dB(A)**, where ISO 7731 §4.4 says to rely on visual signals; a 3–10 W panel speaker (finding 35) cannot reach +15 dB over that. It is also disabled below 11 V. In a closed cockpit, a speaker only helps when the headset is unplugged.
18. **Cheaper cover for "headset unplugged":** sense the headset plug (jack contact or audio-panel current) and show "NO AUDIO" on the alert unit at power-on (R7 idea, not a Garmin feature). Rely on **vibration and the red light** as the cues that do not need the ear. Bone conduction: only abstract-level evidence, and the transducer sits on the headset that is lost, so **not recommended**.

**F. P(detect) per presentation for the Monte Carlo** (aural only, headset on and working; combine with the visual and vibration cues separately).

| Phase | Workload | P(detect aural), range | Central | Basis |
|---|---|---|---|---|
| Taxi chime (advisory, once) | low | 0.90–0.99 | 0.96 | Dehais 2014 no-windshear 28/28 detected (R4 #10; rule-of-three lower bound ≈ 0.89); Dehais 2019 low-load miss 0.33 % (R6 S6); minus radio overlap and habituation [Y] |
| Run-up / take-off power on ground (voice) | moderate | 0.85–0.98 | 0.93 | Arrabito 2001: 97.3 % correct for one-word warnings under tracking (V2); Patterson +15 dB "difficult to miss" (finding 12); minus hot-mic/radio masking (finding 9) [Y] |
| Take-off roll, ≥ 40 kt (if voice **not** deferred) | high | 0.40–0.85 | 0.62 | Callan 2018 real DR400 hit rate 61.9 % (R6 S7); Dehais 2014 60.7 % under windshear (R4 #10); Dehais 2019 42.3 % hit at very high load (R6 S6, upper-end miss) |
| Lift-off + 10 s (deferred voice) | moderate–high | 0.60–0.95 | 0.80 | between the two rows above; climb with no emergency yet [Y] |
| In flight, cruise / transit | low–moderate | 0.88–0.99 | 0.95 | as run-up row [Y] |
| In flight, during an aerobatic sequence | high | 0.40–0.85 | 0.60 | as take-off-roll row [Y] |
| Headset lost or unplugged | — | 0.00–0.10 | 0.02 | ISO 7731 §4.4; findings 10, 17; only a speaker could help, and only with the canopy closed [Y] |

Repeated presentations [Y]: misses under load are **correlated** (the same attention bottleneck). Do not use 1−(1−p)^k. A simple choice: **P(detect within k bursts) = 1 − (1−p)^(1+(k−1)(1−ρ))**, with **ρ ≈ 0.5 (range 0.3–0.8)**. Example: p = 0.62, k = 3, ρ = 0.5 → 1 − 0.38² ≈ **0.86**. This formula is our modelling assumption, not a published result.

Also model [Y]:
- A **disable / silence probability** per flight that rises with the nuisance-alert rate (findings 38–41). This is the cost of an annoying chime.
- **P(audio path failed)**: wiring, panel, headset unplugged. The power-on self-test (D15) makes this failure visible, so treat it as revealed, not latent.

---

## NOT VERIFIED

1. **CAA-published CAA Paper 82017** (caa.co.uk Download/10717): **HTTP 404**, tried once. The Cambridge manuscript (dated 02.02.1982) was read instead. Page numbers above are the manuscript's printed pages. The printed CAA edition may paginate differently.
2. **Patterson's IOA guidelines paper** (ioa.org.uk): HTTP 404, tried once.
3. **ISO 7731 Annex B** (effective masked threshold method) and §6.3–6.4 (spectral and temporal design): not in the free preview. The standard is paywalled. ANSI preview: 403.
4. **IEC 60601-1-8** (medical alarm sound design): not read. Search snippets only: fundamental 150–1,000 Hz, ≥ 4 (or ≥ 5 in AMD2:2020) harmonics up to 4 kHz, high-priority burst of 10 pulses. **Do not cite** these.
5. **FAA SAIB CE-16-08** itself: not opened. Its text is known only as quoted in NTSB GAA17CA023 [D-ag, T4].
6. **Aircraft Alerting Systems Standardization Study, Vol. II** (DTIC ADA106732, FAA-RD-81-38, voice guidelines §1.3.6): **DTIC 403**, tried once.
7. **HAL** (hal.science) served an **Anubis bot-check page** today for Arnal 2015, Arnal 2019, the Elisabeth 2022 thesis on inattentional-deafness countermeasures, and an ATC multimodal-alarm paper (hal-05162059). Not bypassed. Arnal 2019 was read via Europe PMC instead. **The Elisabeth thesis may contain pilot data on alarm countermeasures and is worth a retry.**
8. **Riedinger et al. 2026** full text: still closed (R4 #12, abstract only).
9. **Simpson & Williams 1980** and **Simpson & Marchionda-Frost 1984**: NTRS abstracts only. The size of the tone-before-voice RT penalty is not known.
10. **Arrabito 2009**: abstract only. No per-condition numbers.
11. **Belz, Robinson & Casali 1999** (auditory icons in trucks): no PubMed record found; not read.
12. **NASA/CR-2002-211666** (GA interior noise Part II, in-flight): the NTRS archive link returned an HTML page, not a PDF. Not read. Part III (N1) was read.
13. **DTIC ADA460838** (GA noise / headset report from the first search): **403**. ROSA P dot_85646: **403**. LightSPEED "ANR 101 §3 Airplane issues": **403**. Not bypassed.
14. **Noise inside an Extra NG** (or any aerobatic type), canopy closed or open: **no measurement found**. The §1 worked table is an assumption-driven illustration. A Pitts "126 dB" forum claim was seen in a snippet only.
15. **Extra NG avionics:** the project files say **G1000** (AAIB G-MIIL report fn 1, p.3, read by the main session). A search snippet of a 2025 Extra NG sales listing mentions **G3X Touch + GMA 245R**. The listing pages (controller.com, aircraft.com) returned **403**, so this is **not verified**. Whether the Extra NG has a cockpit speaker at all is **not verified**.
16. Whether **GMA 245 alert inputs are routed to the speaker**, and whether **G1000 unswitched alerts reach the speaker in fail-safe mode**: not stated in the parts read.
17. **ANR headsets cancelling in-ear alert audio:** none of the sources says that ANR attenuates electrically fed audio; the documented problem is speaker-only horns (findings 40). That ANR leaves electrically fed alerts untouched is R7's inference [Y].
18. **Bone-conduction alerting in high noise:** only search-snippet abstracts (Manning et al. 2016; McBride et al. 2007). Not read.
19. The P(detect) table, the correlated-repetition formula and every level target in "Design implications" are **R7 estimates [Y]**. They are built on the [D-ag] findings cited, but none of them is a published value for this aircraft.
