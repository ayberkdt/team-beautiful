# R7 — Vibrotactile (haptic) alerting for the canopy alert

Read by **subagent R7-haptic**, **2026-11-05**. Purpose: trade-off data for the throttle-knob vibration cue (kit item R-13).

**Tags.**
- **[D-ag]**: read at the source by R7 in this session. The URL and the page, section or table are given.
- **[D-ag abstract]**: only the abstract was read (Europe PMC record). Numbers inside the paper body were not seen.
- **[Y]**: secondary source, my calculation, or my interpretation.
- **[D (R0)]**: a fact the main session read (R0 files). R7 did not re-open that source, except where noted.

Downloads (untrusted data): `D:\tmp_ideathon\easa\dl\r7_haptic\`. Text was extracted with `python -I` scripts kept outside that folder.

## Sources

| # | Source | URL | What R7 read |
|---|---|---|---|
| S1 | Meng, Gray, Ho, Ahtamad, Spence (2015). Dynamic vibrotactile signals for forward collision avoidance warning systems. *Human Factors* 57(2):329–346 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4512524/fullTextXML (PMC4512524) | full text, Exp. 1–4 |
| S2 | Gray, Ho, Spence (2014). A comparison of different informative vibrotactile forward collision warnings. *PLoS ONE* 9(1):e87070 | Europe PMC PMC3903602 (same API) | full text, methods and results |
| S3 | Politis I. (2016). *Effects of modality, urgency and situation on responses to multimodal warnings for drivers*. PhD thesis, Univ. of Glasgow | https://theses.gla.ac.uk/7857/7/2016PolitisPhD.pdf | Exp. 1–3: pp. 4-80 to 4-97 and 5-114 to 5-115 (Fig. 4-10, Table 4-3, Fig. 5-5, Table 5-1) |
| S4 | Silva, Costa, Lisboa (2026). Vibration perception threshold assessments: Staircase vs von Békésy. *Atten. Percept. Psychophys.* 88(2):49 | Europe PMC PMC12795913 | full text, Tables 3–5 |
| S5 | Remache-Vinueza, Trujillo-León, Vidal-Verdú (2025). Vibrotactile stimulus duration threshold for perception of pulse to vibration transition. *Sci. Rep.* 15:5057 | Europe PMC PMC11814341 | abstract, introduction |
| S6 | Clemm et al. (2022). Hand-arm vibration exposure and vibrotactile thresholds among rock drill operators. *Occup. Environ. Med.* | Europe PMC PMC9606510 | discussion (dB conversion, diagnostic levels) |
| S7 | Scott & Gray (2008). *Human Factors* 50(2):264–275. PMID 18516837 | Europe PMC search API, core record | abstract only |
| S8 | Ho, Reed, Spence (2007). *Human Factors* 49(6):1107–1114. PMID 18074709 | same | abstract only |
| S9 | Mohebbi, Gray, Tan (2009). *Human Factors* 51(1):102–110. PMID 19634313 | same | abstract only |
| S10 | Lu, Wickens, Prinet, Hutchins, Sarter, Sebok (2013). Three meta-analyses... *Human Factors* 55(4):697–724. PMID 23964412 | same | abstract only |
| S11 | Sklar & Sarter (1999). Good vibrations. *Human Factors* 41(4):543–552. PMID 10774125 | same | abstract only |
| S12 | Rupert (2000). Tactile situation awareness system. *Aviat. Space Environ. Med.* 71(9 Suppl):A92–9. PMID 10993317 | same | abstract only |
| S13 | Kelley, Cheung, Lawson, ..., Rupert (2013). Tactile cues for orienting pilots during hover over moving targets. *ASEM* 84(12):1255–61. PMID 24459796 | same | abstract only |
| S14 | van Erp, Eriksson, Levin, Carlander, Veltman, Vos (2007). Tactile cueing effects on performance in simulated aerial combat with high acceleration. *ASEM* 78(12):1128–34. PMID 18064917 | same | abstract only |
| S15 | van Erp, Groen, Bos, van Veen (2006). A tactile cockpit instrument supports the control of self-motion during SD. *Human Factors* 48(2):219–228 | same | abstract only |
| S16 | Precision Microdrives datasheets: C10-100 LRA, C12-003 LRA, 307-103 ERM, 308-102 ERM, 312-107 ERM, 324-104 ERM; Haptic Feedback Evaluation Kit table | https://www.precisionmicrodrives.com/datasheets/C10-100%20-%20datasheet-006.pdf ; .../C12-003%20-%20datasheet-001.pdf ; https://precisionmicrodrives.com/cdn/catalog_product/4c94af6d-99d2-4677-8d91-1b217c8a69d5/307-103.pdf ; .../826d8a66-dc5c-493a-8740-b0e05c5115ff/308-102-datasheet.pdf ; .../3aee1d35-6a45-411f-8188-b85793c9c24e/312-107-datasheet.pdf ; .../ddb19c06-c7da-46fc-9003-b7d636d6e1e5/324-104.pdf ; https://www.precisionmicrodrives.com/wp-content/uploads/2021/11/Haptic-Feedback-Evaluation-Kit-Actuator-Table.pdf | spec tables (pp. 1, 3–4 of each) |
| S17 | Precision Microdrives web pages: AB-028 comparison guide; LRA page | https://www.precisionmicrodrives.com/ab-028 ; https://www.precisionmicrodrives.com/linear-resonant-actuators-lras | sections "Frequency", "Amplitude", "Lifetime"; "Extended lifetime" |
| S18 | Texas Instruments DRV2605L haptic driver datasheet | https://www.ti.com/lit/ds/symlink/drv2605l.pdf | §1 Features, §3 Description |
| S19 | EASA TCDS EASA.A.620 Extra NG, Issue 04 (2 Dec 2020) | local copy `D:\tmp_ideathon\easa\dl\cert\TCDS_EASA_A620_ExtraNG_AW.txt` (downloaded by R3) | §5.3 engine limits, §7 propellers, A.V Note 2 (pp. 6–7 of 12) |
| S20 | AAIB Bulletin 4/2024, G-MIIL | local copy `D:\tmp_ideathon\easa\dl\aaib\G-MIIL.txt` | passages on rpm, headset, parachute, throttle hand (page numbers lost in the text extraction; see `R0_AAIB_G-MIIL_report.md`) |
| S21 | 14 CFR 25.207 Stall warning (eCFR, version 2025-01-01) | https://www.ecfr.gov/api/versioner/v1/full/2025-01-01/title-14.xml?part=25&section=25.207 | (a), (b) |
| S22 | Safe Flight patents US 2,566,409 (1951) and US 5,986,582 (1999) | https://patents.google.com/patent/US2566409A/en ; https://patents.google.com/patent/US5986582A/en | description, claim 5 |
| S23 | Ouyang, Wu, Wu (2017). Vibrotactile display of flight attitude... *Appl. Sci.* 7:1291 | https://mdpi-res.com/d_attachment/applsci/applsci-07-01291/article_deploy/applsci-07-01291.pdf | §2.1 actuator |
| S24 | TB20 cockpit vibration spectra (private owner website, not peer-reviewed) | https://peter2000.co.uk/aviation/vibration/index.html | Figs. 1–9 descriptions |
| S25 | Clevenson (1982). NASA TM-84515, synthesized propeller vibration and passenger annoyance | https://ntrs.nasa.gov/api/citations/19820024068/downloads/19820024068.pdf | pp. 3–6 |

## Findings

### A. Aviation haptic cues

1. **Stick shakers are old and simple.** Safe Flight's 1951 patent puts a "high speed fractional horse power" motor with an eccentric weight on the control stick. The amplitude can be raised "to any desired magnitude" by the weight size. No frequency is given [D-ag, S22 US 2,566,409].
2. **Two-level shakers exist.** US 5,986,582 vibrates the helicopter collective "at a first frequency or amplitude", then at "a second, more violent" one for the critical level. The higher level uses a higher motor voltage. Claim 5: second-level frequency is greater [D-ag, S22].
3. **Regulators reject a visual-only stall warning.** 14 CFR 25.207(b): "a visual stall warning device that requires the attention of the crew within the cockpit is not acceptable by itself." The warning must be "clear and distinctive" [D-ag, S21]. This is a precedent for a non-visual cue on a hazard that needs action within seconds [Y].
4. **No stick-shaker frequency or amplitude number was found at a primary source.** A secondary snippet says ~10–30 Hz [Y, NOT VERIFIED].
5. **TSAS (US Navy/NASA).** Pilots flew complex manoeuvres blindfolded with < 20 min training. Recovery from unusual attitudes "solely by tactile cues was trivial" [D-ag abstract, S12]. No detection or RT numbers in the abstract.
6. **TSAS belt, UH-60 simulator, 16 aviators.** Mean distance from a moving hover target was 31.1 ft (SE 3.2) with the belt active vs 36.3 ft (SE 2.8) inactive [D-ag abstract, S13].
7. **TNO torso display, high G.** Nine pilots in a centrifuge reached > +8 Gz. Adding a 60-tactor torso display to Gripen visual displays cut mean RT to threat pop-up from **1458 ms (SE 54) to 1245 ms (SE 88)**, about −213 ms. The stimuli were "perceivable and useful" up to +9 Gz [D-ag abstract, S14]. Relevant to aerobatic g [Y].
8. **TNO tactile instrument in a rotating chair.** It improved recovery from disorientation but reduced tracking performance [D-ag abstract, S15].
9. **Cockpit automation (Sklar & Sarter 1999).** Tactile and visual+tactile cues gave higher detection rates and faster responses to uncommanded mode changes than visual cues. The tactile cue did not interfere with concurrent visual tasks [D-ag abstract, S11]. A university press release (not read at source) says "up to 40 % more" detected signals, and that vibrations were sometimes missed when the arm with the tactor was busy [Y, NOT VERIFIED].
10. **Throttle-lever shakers exist only as patents.** A web search returned Honeywell-style autothrottle patents that vibrate the throttle lever for out-of-bounds conditions. R7 read only the search summary [Y]. No study measuring a throttle-hand cue was found.

### B. Perception: thresholds, frequency, duration

11. **Fingertip threshold at 250 Hz (n = 30).** Mean vibration perception threshold (VPT), index finger: 110.25 dB re 10⁻⁶ m/s² (von Békésy) and 108.61 dB (staircase). The range was 76.5–128.2 dB [D-ag, S4 Table 3]. In SI units [Y]: median ≈ **0.27–0.33 m/s² rms (≈ 0.03 g rms)**. The least sensitive person needed ≈ **2.6 m/s² rms (0.26 g rms)**.
12. **Above 250 Hz, sensitivity falls.** VPT is +7.8 dB higher at 375 Hz and +13.8 dB higher at 500 Hz than at 250 Hz [D-ag, S4 Table 4]. Thresholds form a U-shaped curve with a minimum near **250 Hz** (Pacinian/RA-II channel) [D-ag, S5 Introduction].
13. **Clinical cut-offs.** At 125 Hz, a fingertip VPT of 0.7 m/s² is a "possible disorder" and 1 m/s² a "probable disorder" (UK criteria). Rock-drill exposure raised VPT by up to ~7.5 dB at 500 Hz [D-ag, S6 Discussion]. Pilots with years of hand-arm vibration exposure may need more amplitude [Y].
14. **Duration.** About **30 ms** is the minimum for a pulse to feel like vibration (35 participants, 40–590 Hz) [D-ag, S5 abstract]. Thresholds drop as duration grows up to ~1000 ms (temporal summation, RA-II channel only) [D-ag, S5 Introduction].
15. **The standard lab carrier is 250 Hz.** Many driving studies used it: VBW32 tactors driven at 250 Hz [D-ag, S1 Apparatus; S2]; EAI C2 tactor at 250 Hz, "the nominal centre frequency of the C2" [D-ag, S3 p. 4-80]. A flight-attitude vest used coin ERMs at ~140 Hz, with two motors stacked "to increase the perceived intensity in flight condition" [D-ag, S23 §2.1].
16. **Masking and gloves are recognised risks, but no numbers were obtained.** Meng et al. list whole-body vibration masking (citing Ryu et al. 2010) and thick clothing or gloves (citing Spence & Ho 2008b) as factors that "might be expected to degrade" vibrotactile warnings [D-ag, S1 Introduction]. No dB values were read for gloves or masking (see NOT VERIFIED).

### C. Vibration environment of the Extra NG (frequencies only)

17. **Engine and propeller.** The engine is the Lycoming AEIO-580-B1A, 315 hp at 2700 rpm. The 3-blade MTV-9-B-C/C198-25 (1980 mm) is limited to **2600 rpm** for a standard CofA. 2700 rpm applies to the Aerobatic-only case and to the 4-blade MTV-14-B-C/C190-130 (1900 mm) [D-ag, S19 §5.3, §7, Note 2]. The G-MIIL canopy event happened at a stabilised **2,400 rpm** (2,380–2,410) [D-ag, S20].
18. **Expected spectral lines [Y, calculation].** Direct drive. Six cylinders, four-stroke, gives 3 firing pulses per revolution (the cylinder count is from secondary sources and was not read at a primary source).

| rpm | shaft 1P | 3-blade pass = firing (3P) | 4P (4-blade pass) | 6P (2× firing) |
|---|---|---|---|---|
| 2400 | 40 Hz | 120 Hz | 160 Hz | 240 Hz |
| 2600 | 43 Hz | 130 Hz | 173 Hz | 260 Hz |
| 2700 | 45 Hz | 135 Hz | 180 Hz | 270 Hz |

    For the 3-blade aircraft, the blade-pass line and the firing line **coincide at 3P (120–135 Hz)**. The 6P line (240–270 Hz) sits **on top of the 250 Hz skin optimum**.
19. **A real six-cylinder, 3-blade single shows the same lines.** On a TB20 (accelerometer on a rudder-pedal support), the 3rd harmonic of crank speed dominated at cruise (120 Hz at 2400 rpm). In one setting the 6th harmonic (~250 Hz) dominated. Another peak sat at 280 Hz. No amplitudes in g are given [Y, S24, private website].
20. **No amplitude data at a light-aircraft throttle or stick was found.** NASA TM-84515 used in-flight armrest spectra from a turboprop, but gives only the cabin level used in the simulator: 0.15 g rms at 30 Hz [D-ag, S25 pp. 3–6]. This does not transfer to a piston single [Y].

### D. Reaction time and detection: tactile vs auditory vs visual

21. **Tactile beat visual and no warning (Scott & Gray 2008).** 16 drivers; warnings at TTC 3 or 5 s. Tactile gave the **shortest mean RT**. It was significantly faster than no warning and than visual [D-ag abstract, S7]. Numbers in ms were not read.
22. **Tactile survives a talking load; auditory does not (Mohebbi et al. 2009).** Warning-onset-to-brake time grew with a simple conversation by **+148 ms for auditory** (significant) and **+53 ms for tactile** (not significant). With a complex conversation: +221 ms auditory, +146 ms tactile. Tactile was then still **141 ms faster than no warning** [D-ag abstract, S9]. A close analogue for "pilot busy on radio or aerobatics" [Y].
23. **Audio + tactile beats either alone (Ho et al. 2007).** Braking began significantly sooner after audiotactile warnings than after auditory-only or vibrotactile-only ones [D-ag abstract, S8]. Numbers not read.
24. **Simple braking response, all 7 modality combinations (Politis Exp. 3, 15 participants).** Mean response times: **AV 0.71 s, ATV 0.71, AT 0.72, TV 0.73, A 0.77, V 0.77, T 0.78 s**. All multimodal cues were significantly faster than every single-modality cue; A, V and T did not differ [D-ag, S3 Fig. 5-5, Table 5-1, p. 5-115]. So redundancy saves **~50–70 ms** [Y].
25. **Tactile is poor for coded messages (Politis Exp. 2, 19 participants).** When people had to recognise one of three urgency levels from the pulse rhythm, T was slowest: **T 1.47 s vs 0.94–1.21 s** for the others. T also had significantly more recognition errors than every other modality [D-ag, S3 Fig. 4-10, Table 4-3, p. 4-95; p. 4-96 text].
26. **Hand cue = waist cue, and warnings save ~130–290 ms.** Exp. 4 (18 participants): BRT with hand tactors 843 ms vs waist 841 ms (no difference). The no-warning BRT was 977 ms, so any warning was faster (p < .001). In Exp. 1, no-warning was 1134 ms vs 886–915 ms with a warning [D-ag, S1 Results, Exp. 1 and 4].
27. **Misses were rare when the cue was felt.** In Exp. 1, misses were < 1 % of trials that had a warning [D-ag, S1 Exp. 1 Results].
28. **A strong cue on the hands caused more wrong actions.** False-alarm braking (warning without a real event): **hands, low intensity 4.2 %; hands, high intensity 22.3 %**. Waist: 7.5 % low, 10.9 % high. A high intensity at the waist sped responses (820 vs 863 ms); at the hands it did not (836 vs 849 ms, n.s.) [D-ag, S1 Exp. 4 Results].
29. **Single-tactor "looming" ramps added nothing.** BRTs did not differ between looming, constant, pulsed or ramped single-tactor signals [D-ag, S2 Introduction, Exp. 1].
30. **Meta-analysis (Lu et al. 2013, 68 studies).** Response times were faster for tactile interrupting tasks "in case of low-urgency messages". Accuracy was higher with tactile for low-complexity signals, and with auditory for high-complexity ones. Redundant auditory-visual pairs were best for communication tasks under high workload [D-ag abstract, S10].
31. **Meta-analysis (Prewett et al. 2012, 45 studies).** Tactile alerts substitute well for visual alerts. Tactile direction cues do not. Adding tactile cues to a baseline or to visual cues improved performance [Y, search snippet of the abstract; NOT VERIFIED at source].

### E. Hardware

32. **Families compared by the vendor** [D-ag, S17 AB-028]:

| Type | Frequency | Normalised amplitude | MTTF |
|---|---|---|---|
| Brushed ERM | 30–500 Hz (1,800–30,000 rpm) | 0.25–150 G | 100–600 h |
| Brushless ERM | 200–208 Hz | 1–30 G | 1000+ h |
| LRA | 150–205 Hz, must be driven within ±5 Hz of resonance | 0.75–2 G | 1000+ h |

33. **In an ERM, frequency and amplitude are tied to motor speed.** In an LRA the only parts prone to failure are the springs. LRAs need an AC drive at resonance [D-ag, S17 LRA page].
34. **Datasheet values.** Amplitude is peak-to-peak on a test sled at rated voltage [D-ag, S16, each datasheet pp. 1, 3–4]:

| Model | Type | Size | Mass | Rated | Speed / freq. | Typ. amplitude (sled) | Current typ / max / start | Lag / rise / stop | Op. temp. |
|---|---|---|---|---|---|---|---|---|---|
| C10-100 | LRA coin | Ø10 × 3.7 mm | 2 g | 2 V rms | 175 Hz (174 ± 8) | 1.5 G (100 g); min 1 G | 67 / 90 mA rms | 11 / 37 / 177 ms | −25…70 °C |
| C12-003 | LRA block | 6 × 12 mm | 1.5 g | 2 V rms | 204 ± 10 Hz | 1.5 G (100 g); min 0.9 G | 111 / 149 mA | — | — |
| 307-103 | ERM, Ø9 mm cylinder | 8.7 × 25.1 mm | 4.6 g | 3 V | 13,800 ± 2,700 rpm (≈ 185–275 Hz) | 7 G (100 g); min 4.8 G | 100 / 220 / 650 mA | 8 / 28 / 49 ms | −20…60 °C; MTTF 1780 h (C.L. 50 %) |
| 308-102 | ERM, Ø8 mm | 8 × 14.5 mm | 3 g | 4.5 V | 19,000 rpm (≈ 317 Hz) | 5.5 G norm. | 145 / 200 / 640 mA | 9 / 21 / 49 ms | −20…65 °C |
| 312-107 | ERM, Ø12 mm | 12 × 15.1 mm | 9.1 g | 3 V | 6,400 rpm (≈ 107 Hz) | 14.3 G norm. (250 g sled) | 250 / 450 / 600 mA | 15.5 / 85.5 / 180 ms | −10…60 °C |
| 324-104 | ERM, Ø24 mm | 24.4 × 12.4 mm | 32.7 g | 5 V | 2,400 ± 500 rpm (≈ 40 Hz) | 6.4 G norm. (1000 g sled) | 62 / 92 / 200 mA | 58 / 100 / 130 ms | −10…50 °C |

    Rpm-to-Hz conversion is mine [Y].
35. **Driver IC.** TI DRV2605L drives ERM or LRA. It offers automatic overdrive and braking, LRA resonance tracking, automatic actuator diagnostic and level calibration. Supply 2–5.2 V. It falls back to open loop if the LRA gives no valid back-EMF [D-ag, S18 §1, §3]. The diagnostic gives a built-in self-test of the actuator [Y].

### F. Known downsides

36. **Wrong action on a strong hand cue.** 22 % false-alarm braking with high-intensity hand vibration (Finding 28). For a canopy alert, the matching risk is an abrupt power cut or rejected take-off on a nuisance alert [Y].
37. **Tactile cannot carry several meanings.** It is the slowest and least accurate modality for coded urgency levels (Finding 25). Use one meaning only [Y].
38. **Annoyance.** In Politis Exp. 1, TV warnings were rated more annoying than T alone, and A more annoying than V [D-ag, S3 pp. 4-82 ff., §4.3.6.2]. Repetitive vibration may annoy (Petermeijer et al. seat study, snippet only) [Y, NOT VERIFIED].
39. **Missed when the hand or arm is busy** (Sklar & Sarter press release) [Y, NOT VERIFIED]. A knob cue is lost when the left hand leaves the lever.
40. **Confusion with engine or airframe vibration.** In the SP-HMM event, the crew felt a real vibration precursor, suspected the engine, ran it up, found nothing and called it an illusion [D (R0), `R0_PKBWL_2022-1097_SP-HMM_first_event.md` line 12]. A steady alert vibration could be read as engine roughness the same way [Y].
41. **Adaptation.** Long or strong exposure raises thresholds: temporary threshold shift after 20 m/s² rms for 5 min (Harada & Griffin 1991, cited) [D-ag, S4 Discussion; primary not read]. Use pulses, not continuous vibration [Y].
42. **Hardware limits.** ERM operating ceilings are 50–65 °C; the LRA's is 70 °C (Finding 34). A sun-soaked canopy cockpit may exceed 60 °C [Y]. Brushed ERM MTTF is 100–600 h, but the cue runs only seconds per flight [Y].

## Design implications [Y]

All items in this section are my interpretation of the findings above. They need ground and flight checks.

**Location.**

| Site | For | Against | Verdict |
|---|---|---|---|
| **Throttle knob** | G-MIIL pilot "flew with his left hand permanently on the throttle" (S20). The hand is on the lever during the take-off roll and initial climb. The cue sits on the control that fixes the problem (power reduction or abort). Hands and waist give equal RT (Finding 26). | Lost if the hand leaves the lever. Engine vibration enters through the lever. A strong hand cue triggers more wrong actions (Finding 28). | **Primary** |
| Stick | Right hand is always on it. | "Stick shaker" means stall to every pilot. The Extra NG has its stall warning removed by ELOS (`R1_extra_ng_canopy_design.md`, not re-read). A shake could prompt a wrong push. Buffet masking. | Reject |
| Seat pan or lap belt | Always in contact. Works without hands (Finding 26: waist = hands). Survives +9 Gz (Finding 7). | Whole-body engine vibration masks it. The G-MIIL pilot sat on a back parachute (S20), which blocks a seat-back tactor. Extra wiring through the harness. | Optional second tactor (lap belt), same pattern |

**Actuator.** Two good choices:
- **First choice: cylinder ERM, 307-103 class.** 4.6 g, ~7 G on a 100 g sled, ~230 Hz (185–275 Hz), 0.3 W typical (100 mA at 3 V), start current 650 mA, rise 28 ms, stop 49 ms. Strong, cheap and fast to stop.
- **Alternative: LRA C10-100 with a DRV2605L driver.** Fixed 175 Hz, 0.13 W, no brushes, 70 °C rating, built-in diagnostic. Its 1.5 G is about 13 dB weaker than the 7 G ERM. The 177 ms free stop time needs active braking.
- **Avoid big pancake ERMs** like the 324-104. They run at ~40 Hz, which equals the prop 1P line at 2400 rpm and lies outside the Pacinian band.

**Acceleration target.** Scale the sled value by about 1/(effective moving mass). This is a crude estimate that ignores hand impedance.
- With the 307-103 in a knob plus hand of 150–500 g: **≈ 1.4–4.7 G p-p, ≈ 5–16 m/s² rms**.
- With the C10-100: **≈ 1.0–3.5 m/s² rms**.
- Compare the median fingertip threshold of ≈ 0.3 m/s² rms and the worst individual's 2.6 m/s² rms (Finding 11).
- Target **≥ 5 m/s² rms (≈ 0.5 g rms) at the knob surface**: about +24 dB over the median and +6 dB over the least sensitive subject, before gloves and masking. Also require **≥ 10 dB above the measured background** in the same one-third-octave band at 2600 rpm.

**Frequency.** For the 3-blade aircraft, avoid steady tones at **120–135 Hz (3P)** and **240–270 Hz (6P)**. A carrier of about **175–220 Hz** sits between those lines and is still in the Pacinian band. The 4P line (160–180 Hz) should be weak on a 3-blade six-cylinder engine (unverified).
- With an ERM, the speed spread (185–275 Hz) cannot be controlled tightly. Rely on the pulse rhythm instead.
- On the 4-blade aircraft, 4P = blade pass ≈ 180 Hz, so prefer ~210–220 Hz.

**Pulse pattern.** The engine vibration is steady, so **rhythm is the main discriminator**. Use bursts of **150 ms on / 100 ms off, in groups of 3, then 400 ms off**, repeated while the alert is red. Each pulse is well above the 30 ms minimum (Finding 14), and 150 ms matches Meng's pulse length (S1). The rhythm (~4 Hz bursts, ~1.1 s cycle) cannot look like 40–270 Hz engine orders. The 49 ms ERM stop time keeps the gaps crisp.
- Start the vibration at the **same instant as the voice "CANOPY"**. Redundancy saves ~50–70 ms (Finding 24) and removes the "engine roughness" misreading (Finding 40).
- **Medium, not maximum, intensity**, to limit wrong abrupt actions (Finding 28).
- **One meaning only**: canopy not locked at power or in flight (Finding 25).
- **Stop after 10 s, re-arm every 30 s** while still red, to limit adaptation and annoyance (Findings 38, 41).

**Mass and power.**
- Actuator 2–5 g. Knob insert, flex lead along the lever and driver board about **15–30 g in total**.
- Power during an alert: ≤ 0.3 W (ERM typical) with a 0.65 A start peak, or ≈ 0.15 W (LRA). Zero when no alert is active.
- This matches the kit line in `easa_kit.py` (5–20 g, 0.5 W).

**Self-test.** At power-up, give one short burst while the pilot holds the knob (a pre-flight "felt it" check). Check ERM current, or use the DRV2605L diagnostic for an LRA. Report a failed actuator as amber.

**Ground check (kit step 11 and the engine run).** Fit an accelerometer to the knob. Record the spectrum at idle, 2400 and 2600 rpm, then with the cue on. Repeat with the gloves the pilot uses.

### Monte Carlo inputs [Y]

| Quantity | Value or distribution | Basis |
|---|---|---|
| P(hand on throttle knob), take-off roll and initial climb | 0.95–0.99 (uniform) | G-MIIL testimony (S20); normal take-off technique [Y] |
| P(hand on knob), cruise or aerobatics | 0.6–0.9 | Hands move to the stick or switches; no data [Y] |
| P(feel cue \| hand on, ≥ 5 m/s² rms) | 0.95–0.99 | Misses < 1 % in the lab (S1, Finding 27); discounted for gloves and masking |
| P(feel cue \| hand off knob) | 0 (knob only); 0.85–0.95 with a lap-belt tactor | S1 Finding 26; masking discount [Y] |
| P(correct interpretation \| felt), vibration alone | 0.80–0.95 | Engine-roughness misreading (SP-HMM, Finding 40); single-meaning cue |
| P(correct interpretation \| felt), with voice "CANOPY" | 0.95–0.99 | Redundancy (S3, S8) |
| RT, cue onset to start of response (simple action) | lognormal, median 0.80 s, 5–95 % 0.55–1.4 s | T 0.78 s (S3 Fig. 5-5); 0.84 s (S1 Exp. 4); 1.25 s in a complex high-G task (S14) |
| Penalty under high workload | +50 to +150 ms | Mohebbi tactile +53 / +146 ms (S9) |
| Multimodal gain (vibration + voice) | −50 to −70 ms | S3 Fig. 5-5 |
| RT with no alert (baseline) | +130 to +290 ms over the warned case | S1 Exp. 1 and 4 |
| P(wrong abrupt action \| nuisance cue) | 0.04 (medium intensity) to 0.22 (high) | S1 Exp. 4 |

These are driving and laboratory numbers moved to a cockpit. Treat them as plausible ranges, not measurements of pilots.

## NOT VERIFIED (searched, not read at source)

- **Blocked:**
  - DTIC: ADA422198 (JSF TSAS UH-60), ADA492500 (NATO RTO-TR-HFM-122 tactile displays). HTTP 403, tried once each.
  - FAA-hosted TSAS papers (MP-086-31, Rupert & Lawson): 403.
  - PMC (ncbi): reCAPTCHA, so the open Europe PMC API was used instead.
  - Southampton eprints (Morioka, Whitehouse & Griffin 2008, thresholds at finger/forearm/toe/heel): 403.
  - ResearchGate (Lu et al. 2013 full text): 403.
  - HKU hub (Ho et al. 2007): 403.
  - Univ. Iowa (Scott & Gray 2007 conference paper): Anubis bot block.
  - TU Delft repository (Petermeijer et al. 2016 vibrotactile survey): connection refused.
  - core.ac.uk (1950s stick-shaker paper): 403.
  - VUT Brno (Malalan & Zikmund): Anubis block.
- **Read only as abstract or snippet:** exact ms values of Scott & Gray 2008 and Ho et al. 2007; Prewett et al. 2012 (IEEE, paywalled; snippet only); Sklar & Sarter's "40 %" and "arm busy" claims (press release); Petermeijer seat annoyance.
- **No number found:**
  - Stick-shaker frequency and amplitude (snippet "10–30 Hz" only).
  - Glove attenuation of vibrotactile thresholds (Carré et al. 2017 claims gloves *lowered* thresholds; not read).
  - Masking of a hand tactor by engine vibration (Ryu et al. 2010; Lisboa et al. 2024 motorcycle gloves, TRF 100:197–210; neither read).
- **Not checked:**
  - Vibration amplitude at the throttle or stick of a piston single (no dataset found; must be measured).
  - Six-cylinder count of the AEIO-580 (Wikipedia-type sources only; Lycoming TCDS E00004NY not read).
  - Whether the 4P line is weak on the 3-blade Extra.
  - EAI C2 tactor specifications (manufacturer page gave no data).
  - TSAS tactor specifications.
  - DO-160G vibration curve for the actuator.
  - ERM bearing and eccentric-mass behaviour under ±10 g aerobatic loads.
- **Extra NG specifics not re-read by R7:** stall-warning ELOS (`R1_extra_ng_canopy_design.md`); SP-HMM vibration precursor (`R0_PKBWL...`).
