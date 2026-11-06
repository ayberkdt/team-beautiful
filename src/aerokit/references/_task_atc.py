"""References for the 2026 final-challenge work on the atc task (owned by one parallel session; add entries here only).

Tags in ``note``: "read 2026-11-04" = read from the source by the ATC session itself; "read by agent" = a research
subagent read it (note in ``prev_guess/03_Advionics/comms_kit_2026-11-05/research/``); "snippet" = search-engine summary only.
"""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    # --- Mode S / ADS-B decoding ------------------------------------------------------------------------
    Reference("sun_2021_1090riddle", "J. Sun", 2021,
              "The 1090 Megahertz Riddle: A Guide to Decoding Mode S and ADS-B Signals",
              "TU Delft OPEN Publishing, ISBN 978-94-6366-402-8", "2nd ed.", doi="10.34641/mg.11",
              url="https://mode-s.org/1090mhz/",
              note="read 2026-11-04 (web edition, CC BY-NC-SA 4.0): identification 8D4840D6202CC371C32CE0576098 -> "
                   "KLM1023 TC 4; position pair 8D40621D58C382D690C8AC2863A7 (even) / 8D40621D58C386435CC412692AD6 "
                   "(odd) -> 52.25720214843750, 3.91937255859375, 38000 ft, NZ = 15, NL formula; local decode with "
                   "reference 52.258, 3.918; velocity 8D485020994409940838175B284F -> 159.20 kt, 182.88 deg, -832 fpm "
                   "and 8DA05F219B06B6AF189400CBC33F -> TAS 375 kt, heading 243.98 deg, -2304 fpm; DF4 2000171806A983 "
                   "-> 36000 ft, DF5 2A00516D492B80 -> squawk 0356; identity bit order C1 A1 C2 A2 C4 A4 X B1 D1 B2 "
                   "D2 B4 D4; Gillham re-ordering D2 D4 A1 A2 A4 B1 B2 B4 C1 C2 C4, alt = 500 N500 + 100 N100 - 1300"),
    Reference("sun_2020_pymodes", "J. Sun, H. Vu, J. Ellerbroek, J. M. Hoekstra", 2020,
              "pyModeS: Decoding Mode-S Surveillance Data for Open Air Transportation Research",
              "IEEE Transactions on Intelligent Transportation Systems 21(7), 2777-2786",
              doi="10.1109/TITS.2019.2914770", url="https://github.com/junzis/pyModeS",
              note="paper: snippet only (search summary 2026-11-04). The library itself (pyModeS 3.6.1, installed to "
                   "D:\\tmp_ideathon\\pylib) was read 2026-11-04: _altcode.py (AC layout C1 A1 C2 A2 C4 A4 M B1 Q B2 "
                   "D2 B4 D4, Gray-to-binary fold, N100 in {0,5,6} invalid, 7 -> 5, odd N500 -> 6 - N100) and "
                   "_bits.py (generator 0xFFF409 / 0x1FFF409). Used only as an independent cross-check in tests"),
    # --- comms rules and VHF ------------------------------------------------------------------------------
    Reference("easa_sera_14083_2025", "EASA", 2025,
              "Easy Access Rules for Standardised European Rules of the Air (SERA), SERA.14083 Air-ground "
              "communication failure (as amended by Regulation (EU) 2024/404)", "EASA eRules, revision August 2025",
              url="https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/"
                  "easy-access-rules-standardised-european?erules-id=ERULES-1963177438-22770",
              note="read 2026-11-04 through a summarising fetch tool (short quotes only): (a) try previous/other "
                   "channels, other ATS units and aircraft, 'all available means, including ... data link, satellite "
                   "voice and mobile phones'; (b)(1) ATC checks the receiver using SSR code changes or IDENT; (b)(3) "
                   "no blind transmission of clearances unless the originator requests it; (c)(2) Mode A 7600; "
                   "(c)(4)(i) IFR keep last assigned speed and level 'for a period of 20 minutes'; (iv) descend at "
                   "EAT/ETA; (vi) land within 30 min; (c)(6) 7601 for an IFR flight that meets VMC and whose pilot-in-command decides to continue in VMC (land at the nearest suitable aerodrome, report arrival; the word VFR is not in (c)(6) -- audit 2026-11-04). Applicability 1 May "
                   "2025 per the research agent (C_BCAA_ASIL_2025_02.md), not read by us"),
    Reference("icom_ica24_channels", "Icom Inc.", 2026, "IC-A24 instruction manual, channel ID list (8.33 kHz)",
              "manualslib.com copy of the manual, page 35",
              url="https://www.manualslib.com/manual/514344/Icom-Ic-A24.html?page=35",
              note="read 2026-11-04: 118.000 = 118.0000 (25 kHz); 118.005/118.010/118.015 = 118.0000/118.0083/118.0167 "
                   "(8.33 kHz); 118.025 (25 kHz); 118.030/.035/.040 = 118.0250/.0333/.0417 ... (secondary source; "
                   "manufacturer manual year not printed in the extract)"),
    Reference("etsi_en300676_1", "ETSI", 2011, "EN 300 676-1 V1.5.2: VHF air-ground radio transmitters, receivers "
              "and transceivers for the aeronautical mobile service using amplitude modulation",
              "ETSI, Sophia Antipolis", url="https://www.etsi.org/deliver/etsi_en/300600_300699/30067601/"
                                            "01.05.02_60/en_30067601v010502p.pdf",
              note="read by agent (C_ETSI_EN300676_1.md): 118-136.975 MHz AM, 6K80A3EJN (25 kHz) / 5K00A3EJN (8.33 "
                   "kHz), audio 300-3400 Hz (25 kHz) or 350-2500 Hz (8.33 kHz), receiver sensitivity -101 dBm, "
                   "offset carrier 2-5 carriers (edition year from the version number, not verified)"),
    Reference("eurocontrol_cpdlc_practices_2026", "EUROCONTROL", 2026, "Recommended Practices for CPDLC in Europe",
              "EUROCONTROL WikiLink", url="https://ext.eurocontrol.int/WikiLink/images/9/97/"
                                          "Recommended_Practices_for_CPDLC_in_Europe_2026.pdf",
              note="read by agent (C_EUROCONTROL_CPDLC_RecPractices_2026.md): voice for time-critical situations, "
                   "ground timeout 120 s, revert to voice on error; SERA.8035 voice watch remains with CPDLC"),
    Reference("eurocontrol_evair_25", "EUROCONTROL", 2024, "EVAIR Safety Bulletin No 25 (2018-2022)",
              "EUROCONTROL, Brussels", url="https://www.eurocontrol.int/sites/default/files/2024-05/"
                                           "eurocontrol-evair-bulletin-25.pdf",
              note="read by agent (C_EVAIR_Bulletin25.md): loss of communication 4 % of reports; causes radio "
                   "availability 42 %, frequency change 32 %; go-around associated in 48 %"),
    # --- surveillance standards and products ---------------------------------------------------------------
    Reference("eurocontrol_radar_std_1997", "EUROCONTROL", 1997, "Standard Document for Radar Surveillance in "
              "En-Route Airspace and Major Terminal Areas", "EUROCONTROL, Brussels",
              url="https://www.eurocontrol.int/sites/default/files/publication/files/surveillance-standard-"
                  "document-for-radar-surveillance-in-en-route-airspace-and-major-terminal-areas199703.pdf",
              note="SUR.ET1.ST01.1000-STD-01-01 Ed. 1.0, read 2026-11-04 (PDF text) -- recommended figures: SSR "
                   "6.3.2.1 Pd > 97 %, 6.3.2.4 Mode A code detection > 98 %, Mode C > 96 %, 6.3.3.1 bias < 100 m / "
                   "0.1 deg, random < 70 m / 0.08 deg, 6.3.3.2 validated false Mode A < 0.1 %; PSR 6.4.2.1 Pd > 90 %, "
                   "6.4.2.2 < 20 false reports per scan, 6.4.3.1 random < 120 m / 0.15 deg. Rotation periods from the "
                   "research agent (R_eurocontrol_radar_std_1997.md), not re-read"),
    Reference("eurocontrol_esassp_2024", "EUROCONTROL", 2024, "EUROCONTROL Specification for ATM Surveillance "
              "System Performance (ESASSP), Vol 1, Ed 1.3", "EUROCONTROL, Brussels",
              url="https://www.eurocontrol.int/sites/default/files/2024-03/Released%20Issue%20ESASSP%20%20Vol%201%20Ed%201.3.pdf",
              note="read by agent (R_esassp.md): 3 NM separation update <= 5 s, RMS <= 300 m, probability of update "
                   ">= 97 %; 2.5 NM on final approach <= 5 s, <= 200 m, >= 99 %"),
    Reference("blom_yang_barshalom_imm", "H. A. P. Blom, K. Yang, Y. Bar-Shalom", 2020,
              "IMM Estimator in Multisensor Multitarget Tracking for Air Traffic Control and Autonomous Driving",
              "short paper (IEEE AESM, as named by the file), TU Delft file list",
              url="https://filelist.tudelft.nl/LR/Organisatie/Afdelingen/Department_of_Control_and_Operations/ATO/"
                  "News/IEEE_AESM_IMM%20%283%29.pdf",
              note="read by agent (R_blom_imm_atc.md): IMM = N Kalman filters with mixing and mode probabilities; "
                   "ARTAS architecture 'largely based on the IMM inspired design' (the uniform-motion / speed-change / turn modes belong to the earlier NLR IMM research), PDA later JPDA (wording corrected after the 4 Nov audit). Year is the "
                   "latest reference cited, not printed"),
    Reference("intersoft_rass_catalogue_2025", "Intersoft Electronics", 2025, "RASS product catalogue",
              "Intersoft Electronics, Olen, Belgium",
              url="https://intersoft-electronics.com/wp-content/uploads/2025/07/IE-CD-00107-012-RASS-spread-HR-2.pdf",
              note="read by agent (S_intersoft_rass_catalogue.md): radar comparator Pd, false plots, code "
                   "probabilities, range/azimuth/time bias and random error vs ADS-B; RES SSR/Mode S/ADS-B target "
                   "simulator up to 2048 targets incl. FRUIT and reflections"),
    # --- speech recognition in ATC -------------------------------------------------------------------------
    Reference("zuluagagomez_2022_wav2vec", "J. Zuluaga-Gomez et al.", 2022,
              "How Does Pre-trained Wav2Vec 2.0 Perform on Domain Shifted ASR? An Extensive Benchmark on Air "
              "Traffic Control Communications", "IEEE SLT 2022 (arXiv 2203.16822)",
              url="https://arxiv.org/abs/2203.16822",
              note="read 2026-11-04 (arXiv abstract page + PDF text): baseline hybrid ASR WER per test set, each with "
                   "its SNR range -- NATS >= 20 dB 7.7 %, ISAVIA 15-20 dB 12.5 %, ATCO2-Test 10-15 dB 24.7 %, "
                   "LiveATC-Test 5-15 dB 35.8 % (dataset-level, not a controlled SNR sweep); ATC audio 'usually below "
                   "15 dB SNR'; wav2vec 2.0 fine-tuning gives 20-40 % relative WER reduction. Authors: Zuluaga-Gomez, "
                   "Prasad, Nigmatulina, Sarfjoo, Motlicek, Kleinert, Helmke, Ohneiser, Zhan; SLT 2022"),
    Reference("nigmatulina_2021_callsign", "I. Nigmatulina, R. Braun, J. Zuluaga-Gomez, P. Motlicek", 2021,
              "Improving callsign recognition with air-surveillance data in air-traffic communication",
              "arXiv:2108.12156 (submitted to Interspeech 2021)", url="https://arxiv.org/abs/2108.12156",
              note="abstract read 2026-11-04: +28.4 % absolute callsign recognition accuracy, up to 74.2 % relative "
                   "WER improvement of callsign recognition using surveillance callsigns; baseline 41.3 % -> 69.7 % "
                   "on VHF data read by the agent (A_Nigmatulina2021_callsign_surveillance.md)"),
    Reference("haawaii_readback_2022", "HAAWAII consortium (Helmke, Ohneiser, Kleinert et al.)", 2022,
              "Readback error detection by automatic speech recognition (HAAWAII)", "SESAR Innovation Days 2022",
              note="read by agent (A_HAAWAII_readback_SID2022.md): ATCo WER 2.8-2.9 %, pilot 7.1-10.4 %; command "
                   "extraction ATCo 92-93 %, pilot 71-80 %; readback errors in 1.3 % of utterances; detection 81-82 % "
                   "at 67 % false alarms in ops (exact title not checked)"),
    Reference("cardosi_1994_readback", "K. Cardosi", 1994, "An analysis of tower (local) controller-pilot voice "
              "communications", "FAA report DOT/FAA/RD-94/15", url="https://rosap.ntl.bts.gov/view/dot/8652",
              note="read by agent (C_Cardosi_1994_FAA_RD94_15.md): 8444 messages, < 1 % readback errors, controllers "
                   "missed 7 of 19 (title as recorded by the agent, not checked)"),
    Reference("eurocontrol_asterix_cat048_2007", "EUROCONTROL", 2007,
              "EUROCONTROL Standard Document for Surveillance Data Exchange, Part 4: Transmission of Monoradar Target "
              "Reports (ASTERIX Category 048), SUR.ET1.ST05.2000-STD-04-01", "EUROCONTROL, Brussels", "Ed. 1.15",
              url="https://www.icao.int/sites/default/files/sp-files/SAM/Documents/2010/ASTERIX/04%20%20ASTERIX_CAT_48.pdf",
              note="read 2026-11-04 (PDF text via PyMuPDF): data block CAT=048 one octet, LEN two octets incl. CAT and "
                   "LEN, records with FSPEC (s. 4.6.2.2, 4.7); standard UAP FRN 1-28; I048/020 TYP/SIM/RDP/SPI/RAB/FX; "
                   "I048/040 RHO LSB 1/256 NM, THETA 360/2^16; I048/070 V G L spare + 12-bit octal; I048/090 V G + "
                   "14 bits LSB 1/4 FL; I048/140 LSB 1/128 s; I048/200 GSP 2^-14 NM/s, HDG 360/2^16; I048/240 8x6 bit. "
                   "Newer editions exist (1.32 listed by EUROCONTROL); not compared"),
    Reference("code7700_par", "J. Haskel (code7700.com)", 2026, "Precision Approach Radar (PAR)",
              "code7700.com pilot reference pages", url="https://code7700.com/par.htm",
              note="read 2026-11-04 (secondary, quotes AIM 5-4-11 and AFM 51-37 6-17): slightly/well above/below glide "
                   "path, slightly/well left/right of course, trend modified by rapidly/slowly ('coming down "
                   "rapidly'), range at least once each mile, guidance to DH, missed approach outside safety limits. "
                   "Not on the page: the 5 s transmission interval and the 5 s PAR lost-communication rule (FAA JO "
                   "7110.65 5-12, search summary only; the FAA site refused automated reading)"),
    Reference("enri_par_annex10", "ENRI / MIC Japan (summary of ICAO Annex 10 PAR figures)", 2016,
              "Precision approach radar technical conditions (Japanese government document)", "soumu.go.jp",
              url="https://www.soumu.go.jp/main_content/000376472.pdf",
              note="read by agent (R_par_enri_soumu.md): coverage >= 9 NM, 20 deg az x 7 deg el, accuracy elevation "
                   "0.4 % of range + 10 % of offset (fixed term 6 m), azimuth 0.6 % + 10 % (9 m), range 3 % (30 m), display update <= 1 s, ~9080 MHz (fixed terms added after the audit; year as "
                   "recorded by the agent, not checked)"),
    Reference("wikipedia_mti_2026", "Wikipedia contributors", 2026, "Moving target indication",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Moving_target_indication",
              note="read 2026-11-04 (summarising fetch): successive pulses compared, stationary returns cancel; "
                   "phase rotation 720 v f / c deg/s -> blind when it reaches 360 deg per pulse interval; 3-4 pulses "
                   "and staggered PRF reduce blind speeds; sub-clutter visibility limited to about 25 dB"),
    Reference("wikipedia_cfar_2026", "Wikipedia contributors", 2026, "Constant false alarm rate",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Constant_false_alarm_rate",
              note="read 2026-11-04 (summarising fetch): cell-averaging CFAR estimates the noise floor from cells around "
                   "the cell under test, guard cells excluded. The multiplier formula is not on the page; ours is "
                   "derived and Monte-Carlo checked"),
    Reference("zoranbosnjak_asterix_specs_2026", "Z. Bosnjak et al. (asterix-specs project)", 2026,
              "ASTERIX specifications in structured form: CAT048 ed. 1.32 (2024-07-01), CAT021 ed. 2.7 (2025-07-02)",
              "github.com/zoranbosnjak/asterix-specs, git revision 5cf64b6 (2026-10-27)",
              url="https://zoranbosnjak.github.io/asterix-specs/specs.html",
              note="read 2026-11-04 (definition.txt through a summarising fetch): CAT048 1.32 UAP FRN 1-14 and the "
                   "items we use identical to the EUROCONTROL Ed. 1.15 PDF; I048/090 FL a signed quantity; I048/140 "
                   "below 86400 s. CAT021 2.7: UAP FRN 1-30; I021/130 lat/lon 24-bit two's complement, LSB 180/2^23 "
                   "deg; I021/145 16-bit signed, LSB 1/4 FL; I021/160 RE + 15-bit GS LSB 2^-14 NM/s, TA 360/2^16; "
                   "I021/040 first octet ATP(3) ARC(2) RC RAB FX. Third-party rendering, not the EUROCONTROL PDF"),
    # --- radar ---------------------------------------------------------------------------------------
    Reference("mathworks_albersheim", "The MathWorks", 2026, "albersheim - Required SNR using Albersheim's equation",
              "Phased Array System Toolbox documentation", url="https://www.mathworks.com/help/phased/ref/albersheim.html",
              note="read 2026-11-04: A = ln(0.62/Pfa), B = ln(Pd/(1-Pd)), SNR_dB = -5 log10 N + (6.2 + 4.54/sqrt(N + "
                   "0.44)) log10(A + 0.12 A B + 1.7 B); linear detector, nonfluctuating target, N noncoherent samples. "
                   "The extracted page text lost the square root; the sqrt form is the one that reproduces the "
                   "exact Marcum-Q result in tests/test_atc_radar.py. Cites Richards (2005) and Skolnik (2001)"),
    Reference("richards_2005_radar", "M. A. Richards", 2005, "Fundamentals of Radar Signal Processing",
              "McGraw-Hill, New York",
              note="not read in this session; cited by mathworks_albersheim. Swerling-1 single-pulse "
                   "Pd = Pfa^(1/(1+SNR)) is derived in aerokit.atc.radar and checked by Monte Carlo"),
    Reference("wikipedia_radar_2026", "Wikipedia contributors", 2026, "Radar (section Radar range equation)",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Radar#Radar_range_equation",
              note="read 2026-11-04 (first 100 000 characters): Pr = Pt Gt Ar sigma F^4 / ((4 pi)^2 Rt^2 Rr^2), "
                   "Ar = Gr lambda^2 / (4 pi), monostatic Rt = Rr = R, F = 1 is free space"),
    Reference("wikipedia_ssr_2026", "Wikipedia contributors", 2026, "Secondary surveillance radar",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Secondary_surveillance_radar",
              note="read 2026-11-04: 1030 MHz up / 1090 MHz down; P1-P3 8 us (A), 17 us (B), 21 us (C), 25 us (D), "
                   "Mode S 3.5 us; P2 2 us after P1 from the omni beam (side-lobe suppression); Mode C 11 pulses, "
                   "D1 unused, 100 ft; FRUIT and garble; PRF <= 450 Hz; replies per scan 20-30 conventional, 4-8 "
                   "monopulse, 1 Mode S; Mode S reply PPM 0.5 us chips in 1 us bit periods"),
    Reference("ssr_reply_format_patents", "US patents 5387915, 4782450, 5406288, 5077673 (via search summary)", 2026,
              "Mode A/C reply format: F1-F2 20.3 us, 1.45 us grid, SPI 4.35 us after F2",
              "USPTO full texts not read; search-engine summary 2026-11-04",
              note="snippet only: order C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4, pulse width ~0.45 us. The same order "
                   "is printed for the Mode S identity field in sun_2021_1090riddle (read)"),
    Reference("wikipedia_radar_horizon", "Wikipedia contributors", 2026, "Radar horizon",
              "Wikipedia, The Free Encyclopedia", url="https://en.wikipedia.org/wiki/Radar_horizon",
              note="read 2026-11-04: D = sqrt(2 H R_e) for H << R_e; 4/3 effective radius ~8.5e3 km models standard "
                   "refraction; ducting can change this"),
)
