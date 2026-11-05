# Advionics: "Automated Approach Guidance" (research note)

**For:** EUROAVIA Ideathon 2026 team (Bruges, 3–8 Nov 2026; challenges are revealed on the morning of 4 Nov)
**Written:** 2026-11-03, from web research done in this session
**Language:** English, because the event is held in English

## How to read the tags

| Tag | Meaning |
|---|---|
| **[D]** | I read this on the source page (or in the PDF text I extracted) **during this session**. |
| **[A]** | I only saw it in a search snippet or a search-engine summary. I did **not** open the source. Treat it as a lead, not a fact. |
| **[Y]** | My own judgement, a calculation, or general domain knowledge that I did **not** re-read this session. |

When a number matters for the pitch, use only [D] numbers, or say "approximately/typically" out loud.

---

## 0. Summary (read this first)

1. **Who Advionics is.** Advionics NV is a Belgian company at **Siemenslaan 16, 8020 Oostkamp**, about 10 km from Bruges. It designs and manufactures **RF, radar and IFF electronics** for defence and aviation and belongs to the **Intersoft Electronics Group (IE Group)**. [D] https://advionics.be/
   - My confidence that this is the sponsor: **high (about 90%)** [Y]. It is the only "Advionics" I found anywhere, it sits next to the host city, and the host (EUROAVIA Oostende, a VIVES student group) is local.
   - **Advionics does not appear to sell any approach or landing guidance product.** Its sister company **Intersoft Electronics** does have approach-related products and services:
     - **SkyRF®**, a drone that measures ILS/VOR/DME/GBAS signals. Its "Mini-Approach" mode **flies the drone along the glidepath**. [D]
     - **GroundRF**, a handheld ILS/VOR/DME test receiver. [D]
     - ILS planning, installation and maintenance. [D]
     - The ASR-M surveillance radar with drone detection. [D]
     - MLAT surveillance. [D]
2. **What this probably means for the challenge [Y].** A radar/RF/IFF house writing "Automated Approach Guidance" is most likely to favour **ground-based or RF-based, GNSS-independent** guidance. Likely flavours:
   - radar or transponder tracking, PAR-style;
   - automated approach and landing for UAS/drones, possibly onto ships, since Advionics builds naval IFF for frigates;
   - drones that fly approach paths on their own for navaid flight inspection;
   - resilience against GNSS jamming.

   The generic "AI vision autoland" or "GA LPV" ideas remain possible, but I would expect the jury (Advionics RF and radar engineers) to reward **RF, sensor-physics and integrity reasoning** most.
3. **Top 3 framings to prepare** [Y]:
   - **(A)** GNSS-independent automated approach guidance from a ground sensor (radar or transponder), for UAS or military aircraft.
   - **(B)** Automated approach and landing of a UAS on a moving platform or a confined site.
   - **(C)** A multi-sensor resilient approach-guidance architecture (ILS/GBAS/SBAS + radar + vision + INS) with integrity monitoring, aimed at the Baltic-type jamming and spoofing threat.

---

## 1. Event context (what we know about the format)

| Item | Finding | Tag / source |
|---|---|---|
| Dates and place | 3–8 Nov 2026, Brugge (Bruges), Belgium; hosted by AS Oostende | [D] https://euroavia.eu/event/ideathon-2026/ |
| Challenge reveal | Details kept confidential "until the morning of November 4th" | [D] Regulations v1.1 (PDF text extracted), https://ideathon.euroavia.eu/wp-content/uploads/Ideathon-2026-Regulations-1.1.pdf |
| Number of challenges | Four challenges, one per competition slot; every team does all four and gives a "conceptual solution" for each | [D] same Regulations |
| Judging criteria | "technical feasibility, innovation/creativity, sustainability, and presentation quality" (no weights given) | [D] same Regulations §1.4 |
| Jury | "Technical experts from the sponsoring companies" plus academics if applicable | [D] same Regulations §1.4 |
| Software | BYOD; sponsors "may provide temporary licences or access to specialized engineering software" | [D] same Regulations §1.3 |
| IP / NDA | Teams keep IP unless the sponsor states otherwise; a sponsor may require an NDA | [D] same Regulations §1.6 |
| Venue | KU Leuven Brugge campus; accommodation at Lybeer Hostel | [D] local booklet `D:\Masaustu\Ideathon 2026\EUROAVIA Ideathon 2026.pdf` (text extracted) |
| Host group | EUROAVIA Oostende, students at VIVES University of Applied Sciences | [D] same booklet, p. 6 |
| Schedule | Competition on 4 and 5 Nov (morning and afternoon blocks); team presentations on 6–7 Nov (the booklet grid shows presentations on 7/11) | [D] same booklet p. 8 and Regulations §1.1. The two grids differ slightly, so check on site. |
| Sponsor names | **No public sponsor list found.** "Advionics: Automated Approach Guidance" comes from the user's brief, not from any page I could read. | Not found |

**[Y] Implication:** with roughly 5 hours per challenge, the jury will see a **concept**, not a design. To win, make visible:
- a clear **requirement → architecture → numbers → failure modes → certification path → sustainability** chain;
- 2–3 **quantified** claims;
- one memorable **diagram**.

---

## 2. Who is Advionics? (most important section)

### 2.1 Identity and location

| Fact | Detail | Tag / source |
|---|---|---|
| Legal name | Advionics NV | [D] https://advionics.be/ (header) |
| Address | Siemenslaan 16, 8020 Oostkamp, Belgium; +32 (0)50 831 811 | [D] https://advionics.be/ |
| Tagline | "Innovation for aviation AND defense" | [D] https://advionics.be/ |
| Group | "an Intersoft Electronics Group company" (IE Group); sister companies are Intersoft Electronics (Olen) and Intersoft Electronics Services | [D] https://advionics.be/about/ ; [A] group composition in https://evertiq.com/news/2025-06-12-idi-acquires-majority-stake-in-intersoft-electronics-group |
| Group owner | French PE firm **IDI** took a majority stake in June 2025 (seller: Waterland PE) | [D] Advionics news list, https://advionics.be/news/ (item 11 Jun 2025); [A] https://www.lincolninternational.com/transactions/waterland-private-equity-has-sold-intersoft-group-to-idi-groupe/ |
| Earlier ownership | Mergr lists Advionics as acquired by Waterland on 21 Aug 2019 | [A] https://mergr.com/company/advionics |
| Heritage | "+60 years of experience" / "track record of over 60 years in the RF electronics industry"; VRT says it has been in Oostkamp "since the 1960s" | [D] https://advionics.be/about/ ; [D] https://www.vrt.be/vrtnws/nl/2025/03/06/radarproducent-advionics-uit-oostkamp-breidt-uit-met-grote-hal/ |
| Brand age | The website has a "10 jaar Advionics & opening nieuwe hal" invitation (celebration on Thu 24 Sept). This suggests the *Advionics* name or entity dates from about 2016, while the site itself is older (1960s). **No predecessor company name was found.** | [D] https://advionics.be/10-jaar-advionics-opening-nieuwe-hal/ ; predecessor: not found |
| Founding-year conflicts | Directories give 1960, 1999 (company register) and 2002 | [A] https://www.twoinstitute.com/ent/advionics/ (1960, read [D]: "Founded in 1960"); [A] marketscreener/Kompass snippets |
| Belgian enterprise no. | BE 0477.143.394 | [A] search summary (trendstop.levif.be URL contains 477143394) |
| Size | About 200 staff (March 2025), growing to about 250; more than 60 hires in two years; at least 50 more needed in 2026 | [D] VRT 2025-03-06 (link above); [D] https://www.vrt.be/vrtnws/nl/2026/03/11/advionics-uitbreiding-oostkamp-radarsystemen/ |
| Revenue trend | 2023 revenue €8 M higher than 2022 (absolute value not given) | [D] VRT 2025-03-06 |
| Investment | Over €20 M in the new hall, machinery and engineering department; site growing from 12,000 to 18,000 m² | [D] VRT 2026-03-11 |
| New factory | 6,000 m² production facility opened 11 March 2026, "doubling production capacity" | [D] https://advionics.be/ and https://advionics.be/news/ |
| Certifications | ISO 9001, ISO 14001, **EN 9100**; AEO (customs) | [D] https://advionics.be/manufacturing/product-development/ ; [D] https://advionics.be/about/ |

### 2.2 People (as found)

| Person | Role | Tag / source |
|---|---|---|
| **Jan Bonte** | CEO; quoted saying customers can "secure airspace from airports and from ships"; expects orders to rise through 2030 | [D] VRT 2025-03-06 |
| **Thibaud Dauw** | CFO; quote: "we do everything ourselves: mechanics, electronics, cable assembly and testing" | [D] VRT 2026-03-11 |
| **Mathijs Degryse** | Commercial director (VRT); business development, Intersoft Electronics (b2match profile) | [D] VRT 2026-03-11; [D] https://www.b2match.com/e/feindef-2025/participants/2915895 |
| Guy Beyens, Jan van Gent | Appear in LinkedIn search results for Advionics; roles unknown | [A] search results only (be.linkedin.com/in/guy-beyens, be.linkedin.com/in/jan-van-gent-6a1952) |

**[Y]** The jury probably includes Advionics or Intersoft engineers with **RF, radar and IFF backgrounds** rather than flight-control or AI specialists. Speak their language: link budget, frequency band, antenna geometry, multipath, angular accuracy versus range, integrity, and testing and qualification (they run a DC–26 GHz test lab).

### 2.3 What Advionics actually does and makes

| Capability / product | Detail | Tag / source |
|---|---|---|
| Core services | Development (RF engineering for defence, aviation, aerospace), manufacturing, testing and qualification, lifecycle services | [D] https://advionics.be/ |
| RF range | Systems "from 5 MHz to 26 GHz"; testing "DC to 26 GHz" | [D] https://advionics.be/manufacturing/product-development/ |
| Engineering disciplines | RF, analog and digital, **FPGA/CPLD** ("high-speed, deterministic processing for real-time applications"), **embedded software/firmware**, PCB, mechanical CAD | [D] same page |
| **L-IESA® IFF** (flagship) | "L-band Integrated Electronic Scanning Array" for **ship-board IFF**: non-rotating, wraps around a frigate mast, "smart beam concepts for electronic levelling against ship roll"; co-developed within the IE Group | [D] https://advionics.be/ |
| Flagship description (about page) | "innovative flagship nonrotating secondary radar" | [D] https://advionics.be/about/ |
| Installations | "On-site IFF installations in more than 20 countries" | [D] https://advionics.be/about/ |
| Directory business lines | "operator, primary and secondary radar component, power amplifier, transponder" | [D] https://www.twoinstitute.com/ent/advionics/ |
| Other directory description | "RF design, avionic system installation, CNC-milling, electronic assembly" | [A] search summary |
| Customers (named) | Belgian Defence and other NATO countries (Germany and the US are named); a Walloon medical-equipment firm | [D] VRT 2025-03-06 |
| Recent product | "Recently developed its first radar antenna system"; before that it made only components for other firms' radars | [D] VRT 2026-03-11; [D] news list item 2 Jun 2025 ("radar antenna for frigates") |
| Partnerships | LoI with **Kongsberg Defence & Aerospace** (12 Mar 2026, BEDEX) on ground-based air defence in Belgium (the NASAMS context) | [D] https://advionics.be/news/ ; [D] Janes 13 Mar 2026 describes Advionics as providing "radio frequency engineering, radar and antenna systems, advanced avionics development" and "non-rotating identification friend-or-foe technology" — https://www.janes.com/osint-insights/defence-news/weapons/bedex-2026-kongsberg-signs-lois-with-belgian-companies-for-gbad-co-operation |
| EU defence funding | "We are open to cooperate on EDF proposals" | [D] b2match FEINDEF 2025 profile |
| Job ads (tech stack) | Openings for Hardware Development/Design Engineer (Altium, EMI/EMC, bachelor in electronics), Test engineer, Process engineer, many production roles. **No DO-178C, Kalman, computer vision or software roles found.** | [D] https://jobsopderadar.be/ ; [D] https://jobsopderadar.be/vacature/hardware-development-engineer?jobid=1360473931 |

**Not found:**
- any Advionics approach, landing or guidance product;
- any Advionics patents (I did not search patent databases in depth);
- any CORDIS project naming Advionics or Intersoft (one CORDIS search returned only unrelated projects [A]);
- any DO-178C or DO-254 mention on Advionics pages.

### 2.4 The sister company is where the approach guidance lives: Intersoft Electronics (IE Group)

| Product / service | Relevance to "approach guidance" | Tag / source |
|---|---|---|
| **SkyRF®** (drone-based CNS measurement) | Measures "ILS-DME and VOR-DME", **PAPI, GBAS**, localizer and glide path. Its **"Mini-Approach" scenario "flies the drone on the glidepath"**. Claims to cut flight checks "by up to 50%". | [D] https://intersoft-electronics.com/cns-test-equipment/navaids-test-equipment/ |
| SkyRF + Skyguide | Measurement-as-a-service MoU (21 Jun 2022). Swiss regulator FOCA accepted a reduction of aircraft flight checks "by more than 50%". Covers ILS, DME, TACAN, VOR, PSR, SSR. | [D] https://canso.org/skyguide-and-intersoft-electronics-services-to-deliver-cns-drone-measurements-as-a-service/ |
| SkyRF Generator | Drone-borne target and scenario simulation: SSR Modes 1/2/3A/C, optional Mode S and Mode 5, PSR Doppler targets, "sensor alignment (e.g., touchdown zones and runway intersections)" | [D] https://intersoft-electronics.com/cns-test-equipment/simulators-and-signal-generators/skyrf-generator/ |
| GroundRF | Handheld receiver for ILS (LOC and GS), DME, marker, VOR, TACAN | [D] navaids test equipment page (above) |
| Navaids services | ILS/VOR/TACAN/DME site acceptance, certification, six-monthly checks; "manufacturer-independent"; a new UK entity to "pioneer hybrid flight inspection capabilities" | [D] https://intersoft-electronics.com/cns-services/navaids-services/ |
| ATC & airport services | "Planning, installation and maintenance of Instrument Landing Systems (ILS)"; ILS flight checks with the SkyRF drone; **MLAT**; AWOS; airfield lighting | [D] https://intersoft-electronics.com/cns-services/atc-and-airport-services/ |
| ASR-M® radar + NGSP® | Modular air surveillance radar with a drone-detection channel, Doppler processing for "low speed and hovering targets", classification of drones versus birds | [D] https://intersoft-electronics.com/radar-technology/drone-detection-for-modern-cuas-missions/ |
| NORA® | Non-rotating arrays for S-band and L-band primary radar and for IFF | [D] Intersoft home page https://intersoft-electronics.com/ ; [D] b2match |
| Field deployments | Drone ILS checks at Dubai World Central; a EUROCONTROL webinar case study in which SkyRF "halved ILS inspection time" | [A] search summary of LinkedIn posts (not opened) |

### 2.5 Similar names that are NOT the sponsor

| Name | What it is | Tag |
|---|---|---|
| **Advion Ltd** (UK, Ipswich) / **Advion Inc** (US, Ithaca NY) | Unrelated (measuring instruments; mass spectrometry) | [A] search summary |
| **ScioTeq** (Belgium) | Belgian avionics/display firm that also signed a Kongsberg LoI. Different company. | [A] https://www.scioteq.com/en/news/scioteq-and-kongsberg-defence-aerospace-sign-loi |
| f.u.n.k.e. AVIONICS, Universal Avionics, LX Avionics, Shadin Avionics, BAE Systems Avionics | Unrelated companies that appeared in the "Advionics" search | [A] search results |

### 2.6 What this tells us about the likely challenge [Y]

- Advionics' own core is **RF hardware, antennas, transponders, IFF and radar manufacturing** for **defence**, plus naval systems (frigates, ship roll).
- The group's civil side is **CNS test and services**: ILS checking, drones flying glidepaths, MLAT, drone detection.
- So "Automated Approach Guidance" likely means one or more of:
  1. **ground-sensor-based guidance**, where a radar or interrogator tracks the aircraft and uplinks corrections (an automated, datalinked PAR, as in TALS/UCARS);
  2. **UAS/drone automatic approach and landing** in GNSS-denied or confined settings, including **ship decks** (frigates are their customer base);
  3. the **SkyRF drone autonomously flying an approach path** to inspect ILS/GBAS/PAPI, which is literally automated approach guidance for a measurement drone;
  4. a **resilient approach for manned aircraft** when GNSS is jammed (Baltic/NATO context, defence growth).
- A plain AI-vision or GA-LPV concept can still score, but should be framed with **RF and radar complementarity** and **integrity**.

---

## 3. State of the art in approach guidance

### 3.1 ILS (Instrument Landing System)

- **Components.** The localiser gives lateral guidance from aerials at the far runway end. The glideslope gives vertical guidance. Optional markers (outer about 5 NM, middle about 1 NM) are now often replaced by DME. [D] https://skybrary.aero/articles/instrument-landing-system-ils
- **Glidepath.** The usual angle is 3°. Geometry gives a threshold crossing of about 50 ft. False glideslopes appear at odd multiples (9°, 15°, 21°). [D] same SKYbrary page
- **Glide path angle range in EASA CS-AWO.** 3° is operationally preferred. Systems must work from 2.5° to 3°, and CAT I is recommended up to 3.5°. [D] EASA Easy Access Rules CS-AWO signal-in-space model, https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-all-weather-operations-cs?page=24
- **Categories** [D] SKYbrary ILS page:

| Category | DH | RVR |
|---|---|---|
| CAT I | 200 ft | 550 m (usual association) |
| CAT II | ≥100 ft | ≥300 m |
| CAT IIIA | <100 ft | ≥200 m |
| CAT IIIB | <50 ft | ≥50 m |
| CAT IIIC | none | none (not routinely available) |

- **Critical areas.** Holding points are moved back for CAT II/III so that aircraft on the ground do not disturb the signal. [D] SKYbrary
- **Signal-in-space numbers** [D] EASA CS-AWO model page (link above):
  - Localiser displacement sensitivity at threshold (point T): **0.00145 DDM/m**.
  - Glide path: **0.0875 DDM ↔ 0.12 θ**.
  - Localiser course alignment standard deviation at threshold: **3.5 m** (facility performance Type I), **1.5 m** (Type II/III).
  - Glide path angle standard deviation: **0.025 θ**.
  - ILS reference datum height: **15 m (50 ft)**.
- **Derived numbers [Y]:**
  - Localiser full-scale (0.155 DDM) ÷ 0.00145 DDM/m ≈ **±107 m at threshold**, i.e. a ~214 m-wide sector at the threshold. One search summary independently says "CS is 106.9 m at threshold" [A], and a patent summary mentions ±350 ft [A].
  - For θ = 3°: 0.0875 DDM ≈ 0.36° below or above the path. **Full-scale GS = 0.175 DDM** [Y; standard value, not re-read], which is ≈ 0.24 θ ≈ 0.72° if linear.
- **Descent rate rules of thumb [Y]:**
  - On a 3° path you lose ~318 ft per NM (6076 ft × tan 3°).
  - Vertical speed (fpm) ≈ 5.3 × groundspeed (kt). At 140 kt GS that is ~740 fpm; at 3.2° it is ~790 fpm; at 5.5° and 110 kt it is ~1,070 fpm, already above the FSF 1,000 fpm "special briefing" line.
- **Cost and limits [Y]:** each runway end needs its own LOC+GS pair. Siting is sensitive to terrain and buildings, and flight inspection is expensive, which is why drones such as SkyRF are attractive. A DFS official notes that raising the glide slope via ILS "requires a complete additional ILS system for each runway and each runway end" [A] (search summary of the Aviation Today / DFS story).

### 3.2 GBAS / GLS

All points below are [D] from the Boeing / ICAO NSP GBAS Working Group slides, "GBAS global developments" (Murphy, Aug 2026, PDF text extracted), https://www.icao.int/sites/default/files/SAM/MeetingDocs/2026/0902-Taller-Radionavegacion-NAMCARSAM/2.%20Presentaciones%20-%20Presentations/Murphy-GBAS-Global-Developments-20260829.pdf

- **Service types:** GAST C = CAT I; GAST D = CAT II/III, initially single-frequency GPS only.
- **Standards:** CAT II/III standards are "operationally validated and published, but no operational experience yet". DFMC GBAS (GAST E) is under development, with operationally validated SARPs not before about 2030 and possible entry into service around 2033.
- **Aircraft:**
  - GLS CAT I is standard on the 787 and 747-8 and an option on the 737NG, A320, A350 and A380.
  - Receivers come from Honeywell and Rockwell Collins.
  - "GLS for CAT II/III currently being certified for 777-9".
- **Frankfurt:** "Cat II operations have been operationally approved on a GAST-C ground station (Frankfurt)".
- **Ground stations:**
  - About 65–140 installations depending on how you count; about 10 are approved for full CAT I.
  - About 120 are in Russia (status unknown).
  - "Deployments have stalled in the last few years"; "No current development for GBAS GAST D capable ground stations".
- **Standards references:** RTCA DO-253 (series) is the airborne GBAS MOPS, and DO-253D includes GAST C and GAST D. EUROCAE ED-114B covers the ground subsystem.
- **Simulation numbers** [D] from the EASA CS-AWO GLS signal model:
  - GLS output latency 400 ms.
  - False-guidance integrity 2×10⁻⁷ per landing (GAST C) and 1×10⁻⁹ per 15 s (GAST D).

### 3.3 SBAS / EGNOS LPV

- **Alert limits.** EGNOS defines LPV-200 availability as the share of epochs with **HPL < 40 m and VPL < 35 m**. [D] https://egnos.gsc-europa.eu/lpv200_availability
- **APV-I and APV-II.**
  - APV-I: HAL 40 m, VAL 50 m.
  - APV-II: HAL 40 m, VAL 20 m.
  - [A] from a transcription of Annex 10 Amdt 85 (search summary of the Philippines CAAP document). I did not read Annex 10 itself.
- **EGNOS service levels.** EGNOS supports an NPA service level, an APV-I level (LPV minima down to 250 ft) and an LPV-200 level (LPV minima down to 200 ft). The Safety-of-Life service needs certified receivers and complies with Annex 10. [D] ESSP slides, ICAO APAC GBAS/SBAS workshop, Oct 2025, https://www.icao.int/sites/default/files/APAC/Meetings/2025/2025%20GBASSBAS%20Implementation%20Workshop%20for%20Air%20Space/Presentations/1-2-6-ESSP-Experience-as-EGNOS-Service-Provider-in-Europe-Martin.pdf
- **European deployment** [D] same ESSP slides, "UPDATED AIRAC 2510" (Oct 2025):
  - **>1015 RNP APCH procedures with LPV (APV-I and LPV-200 service levels)**, serving **546 airports**.
  - **97 of the 1015 are PinS** (helicopter).
  - **>400 more LPV procedures planned**.
  - **>2100 SBAS-approved aircraft units**.
  - Coverage: 27 EU Member States plus 8 non-EU states.
- **Belgium:**
  - A 2018 EGNOS slide reportedly listed 5 Belgian airports with APV-I and 0 with LPV-200 [A].
  - Brussels Airport RNP approaches with LNAV/VNAV and LPV minima were completed in Nov 2018 under a SESAR deployment project [A] https://www.sesardeploymentmanager.eu/projects/013af1
  - Kortrijk is listed in a GSA-funded project with 2 LPV procedures [A].
  - The Belgian AIP GEN 1.5 says that an LPV minimum requires EGNOS and that baro-VNAV is not temperature compensated [A]. The skeyes page returned 403 to me.
  - **The current Belgian LPV count was not verified.**
- **Limitation.** EGNOS LPV-200 is declared unavailable above about 60°N because of ionospheric concerns, and APV-I is recommended there [A] (EGNOS service notice snippet).
- **Receiver standards:** RTCA **DO-229** (GPS/SBAS MOPS, rev F, 2020) and its dual-frequency successor **DO-401** (GPS + Galileo + SBAS, Sept 2023). DO-401A/ED-259B is planned for Sept 2027 [A] (RTCA SC-159 terms of reference snippet).

### 3.4 RNP APCH, baro-VNAV, RNP AR and RF legs

- **Minima types [Y]:** RNP APCH has four kinds of minima. LNAV and LP are lateral only. LNAV/VNAV uses baro-VNAV (or SBAS geometric altitude, see CM-AS-002 [A]). LPV uses SBAS. Baro-VNAV needs temperature limits or compensation.
- **RNP AR:** RNP below 0.3 (typically 0.3 to 0.1), lateral obstacle clearance of 2×RNP, and RF (radius-to-fix) legs for fixed-radius curved paths. [A] EASA Doc 9905 slides snippet, https://www.easa.europa.eu/en/downloads/12207/en ; [A] ICAO PBN seminar slides
- **Why RF legs matter [A]:**
  - They give a repeatable ground track, help noise avoidance and work in mountainous terrain.
  - In a Mexico City study of RNP-1 RF legs, 91.6% of operations chose the RF "Y" approach and about 2,420 NM per day were saved.
  - A DLR paper optimises curved RNP AR approaches for noise.
- **Research to watch [A]:** "Advanced RNP to xLS" approaches, where a curved RNP segment joins an ILS/GLS final, with automatic landings. Source: Aeronautical Journal (Cambridge), https://resolve.cambridge.org/core/journals/aeronautical-journal/article/experimental-advanced-rnp-to-xls-approaches-with-vertical-path-coding-and-automatic-landings/DC8E5D428CF44B0503AAA135E402CE5A
- **Certification basis.** **AMC 20-27** (RNP APCH incl. baro-VNAV) and **AMC 20-28** (LPV using SBAS) were **cancelled for new applications**. PBN airworthiness moved into **CS-ACNS Issue 2, Subpart C (CS ACNS.C.PBN)**, which took effect around April 2019. [A] EASA NPA 2018-02 and an ENAIRE circular snippet
  - **[Y] Pitch wording:** "LPV airworthiness per CS-ACNS (formerly AMC 20-28)".

### 3.5 Autoland, low-visibility rules and runway-overrun protection

- **EASA AWO package.**
  - Regulation (EU) 2021/2237 amended Air OPS for all-weather operations, with new operational credits: SA CAT I, SA CAT II, EFVS-A, EFVS-L and EFVS 200. [A] Malta CAA OAN 08-22 and SASSOFIA snippets
  - **CS-AWO Issue 2** was adopted by **ED Decision 2022/007/R** and covers HUD, EFVS, SVGS, CVS and SA CAT I. [A] https://www.easa.europa.eu/en/document-library/agency-decisions/ed-decision-2022007r
  - SA CAT I goes down to DH 150 ft with RVR 400 m [A] (Malta CAA notice snippet).
- **EFVS in CS-AWO** [D] https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-all-weather-operations-cs?page=14 :
  - EFVS gives a real-time electronic image used to descend below DA/DH or MDA.
  - **EFVS-A:** below 30 m (100 ft) above TDZE, touchdown and roll-out use natural vision.
  - **EFVS-L:** can be used from DA/H through touchdown and roll-out at RVR not less than 300 m (1,000 ft).
- **ROAAS/ROPS.**
  - CS-25 Amendment 24 (ED Decision 2020/001/R) requires ROAAS on new large-aeroplane designs. [A] EASA explanatory note
  - Part-26 point 26.205 (Reg. 2020/1159) requires it on newly produced large CAT aeroplanes from **1 Jan 2025** (draft wording). EASA **Opinion 05/2024 proposed postponing** that date. [A] **The final adopted date was not verified.**
  - ICAO (Annex 6) applies the requirement to turbine aeroplanes above 5,700 kg [A].
- **[D] Spoofing link:** EUROCONTROL lists "Runway Protection Systems failure (RAAS, ROPS)" and "Synthetic Vision System (SVS) failure" among the effects of GNSS interference (OPSGROUP summary in Berz, EUROCONTROL slides, ICAO MID GNSS/PBN workshop, Sep–Oct 2026, PDF text extracted), https://www.icao.int/sites/default/files/MID/MeetingDocs/2026/GNSS%20%26%20PBN%20Workshop/Documentation/GNSS%20Vulnerabilities%20and%20Emerging%20Threats-EUROCONTROL.pdf
  - **[Y]** Any GNSS-based approach aid must explain what happens under spoofing.

### 3.6 Synthetic, enhanced and combined vision (SVS / EVS / CVS / EFVS)

- **Standards.** RTCA **DO-315B** / EUROCAE **ED-179B** are the MASPS for EVS, SVS, CVS and EFVS. DO-315B adds SVS performance standards that can earn lower-than-standard CAT I minima or reduced visibility, and that credit does not require a HUD. [A] NASA NTRS paper snippets
- **FAA advisory guidance:** AC 98-5-1 (Singapore CAAS) references DO-315/ED-179 [A].
- **EASA rules:** see §3.5 above for EFVS-A versus EFVS-L [D].
- **[Y] SVS caveat:** SVS draws its picture from a database plus GNSS position, so it fails or misleads under spoofing. EVS (IR/MMW radar) does not depend on GNSS. A **millimetre-wave radar EVS** is a natural bridge to Advionics' RF competence.

### 3.7 Vision-based landing and AI certification

- **Airbus ATTOL** [D] https://airbus.com/en/newsroom/press-releases/2020-06-airbus-concludes-attol-with-fully-autonomous-flight-tests (29 Jun 2020):
  - Autonomous taxi, take-off and landing of a commercial aircraft using "on-board image recognition technology".
  - **Over 500 test flights**: about 450 for video data and 6 test flights with 5 take-offs and landings each.
  - Partners: Airbus UpNext, Acubed (Wayfinder), ONERA and others.
- **Airbus follow-ons** [D] Airbus story, 10 Jun 2026, https://www.airbus.com/en/newsroom/stories/2026-06-computer-vision-automated-landing-and-embedded-ai-for-tomorrows-cockpits :
  - **DragonFly** (Nov 2020): automated emergency operations and unequipped airfields.
  - **Auto'Mate**: air-to-air refuelling.
  - **Optimate** (2023, 3 years): a gate-to-gate automated mission on an A350 test airframe.
  - **Vision Landing Application** (VivaTech, June 2026): cameras plus AI as "an independent positioning source that could support autoland at airports without advanced ground infrastructure"; "still in the research phase and far from commercial certification".
  - Sensors: multiple cameras, high-precision GNSS, LiDAR.
- **CoDANN.**
  - **CoDANN I** (Mar 2020, 104 pages) was an EASA–Daedalean report. It introduced the **W-shaped learning-assurance process** using a **visual landing guidance** use case. [A] avweb / aviationtoday snippets ; EASA page https://www.easa.europa.eu/en/document-library/general-publications/concepts-design-assurance-neural-networks-codann
  - **CoDANN II** (May 2021, 136 pages) used visual traffic detection as its use case. Its public report v1.1 adds GPU compliance with AMC 20-152A / AMC 20-193. [A]
- **Daedalean.**
  - **Destinus** (Dutch drone/flight-systems firm) agreed to acquire Daedalean for **CHF 180 M (~$225 M)** on **5 Aug 2025**. Daedalean has more than 150 specialists, and its software supports navigation in **GNSS-denied environments**. [D] https://tech.eu/2025/08/05/uav-destinus-acquires-daedalean-in-225m-deal-to-boost-ai-capabilities/
  - The deal closed on 5 Jan 2026 [A].
  - **PilotEye** (with Avidyne) is in concurrent FAA/EASA certification [A] (AOPA Oct 2025 snippet).
- **EASA AI framework:**
  - **AI Roadmap 2.0** (May 2023) defines Level 1 (assistance), Level 2 (human-AI teaming / cooperation) and Level 3 (advanced automation). [A] https://www.easa.europa.eu/en/downloads/137919/en
  - **AI Concept Paper Issue 2** (6 Mar 2024) refines Level 1 guidance (learning assurance, explainability, ethics-based assessment) and adds Level 2 guidance (human-AI teaming, HAII). It also starts RMT.0742. [D] https://www.easa.europa.eu/en/newsroom-and-events/news/easa-publishes-artificial-intelligence-concept-paper-issue-02-guidance
  - **Proposed Issue 03** (3 Jun 2026) covers **Level 3 "advanced automation"**, reinforcement learning and symbolic AI. Consultation closed 12 Aug 2026. It is "the final Concept Paper deliverable foreseen under the EASA Artificial Intelligence Roadmap 2.0". [D] https://www.easa.europa.eu/en/newsroom-and-events/news/easa-releases-latest-issue-its-concept-paper-artificial-intelligence
  - **NPA 2025-07** (Nov 2025) is EASA's first regulatory proposal on AI trustworthiness, "DS.AI" detailed specifications tied to the EU AI Act, linked to ED-324/ARP6983 (EUROCAE WG-114 / SAE G-34). [A] https://www.easa.europa.eu/document-library/notices-of-proposed-amendment/npa-2025-07

### 3.8 Emergency autoland (single pilot or pilot incapacitation)

- **Garmin Autoland** [D] https://www.garmin.com/en-US/newsroom/press-release/aviation/2020-garmin-autoland-achieves-faa-certification-for-general-aviation-aircraft/
  - FAA certification was announced **18 May 2020** on the **Piper M600** (G3000).
  - It is activated by a dedicated button, or automatically "if the system determines it's necessary"; it can be cancelled with the AP key.
  - It picks "the most suitable airport", avoiding terrain and weather, and **requires "a GPS approach with lateral and vertical guidance to the runway"**.
  - It talks to ATC automatically, holds if needed, extends gear and flaps, lands, brakes on centreline and shuts down the engine.
  - **[Y] Insight:** it depends entirely on GNSS plus published LPV/LNAV-VNAV procedures. It is blind to runway obstructions and vulnerable to jamming or spoofing. **This is the gap to attack** with vision, radar or ground-RF backups.
- Daher TBM 940 Autoland got EASA and FAA certification in Aug 2020 [A].

### 3.9 Helicopter PinS (Point-in-Space)

- **First European PinS LPV.** EGNOS enables "Point in Space down to LPV (PinS LPV)". The first PinS LPV in Europe was published at **Bern Insel Hospital in 2014** (HEDGE-NEXT, FP7). [D] https://www.euspa.europa.eu/newsroom-events/news-archive/helicopter-industry-goes-egnos-advantage
- **How PinS works [A]:**
  - The instrument segment ends at the MAPt (the PinS), followed by a visual segment ("proceed visually") or a VFR segment ("proceed VFR").
  - If visual references are not established, the crew flies the missed approach.
  - Norway's air ambulance upgraded 24 PinS from LNAV to LPV.
- **97 of the >1015 EGNOS LPV procedures are PinS** (AIRAC 2510) [D] ESSP slides.
- **[Y] Opportunity:** the visual segment from the PinS to the helipad (hospital roof, offshore deck) has **no guidance**. A local RF or optical aid could make it "proceed visually" with assistance.

### 3.10 UAS and eVTOL automated landing; vertiports

- **EASA PTS-VPT-DSN** (published March 2022) [D] https://verticalmag.com/opinions/easa-publishes-technical-design-specifications-vertiports/
  - Prototype technical design specifications for **VFR** vertiports (day and night) for manned eVTOL in the SC-VTOL enhanced category.
  - Introduces the **obstacle-free volume (OFV)**, "a funnel-shaped volume overhead the vertiport".
  - D-value = "the diameter of the smallest circle enclosing the eVTOL aircraft projection on a horizontal plane".
  - **No instrument approaches are covered yet.**
- **SC-VTOL** [A] evtol.news, EASA SC-VTOL-01:
  - The Enhanced category must achieve continued safe flight and landing to a destination or alternate vertiport, with a ~10⁻⁹ catastrophic target.
  - The Basic category only needs a controlled emergency landing.
- **Military and tactical UAS autoland as a ground-RF precedent** (very close to Advionics' world):
  - **Sierra Nevada TALS:** "Operates without GPS position data", ">99.95%" successful recovery rate, 15-minute field setup, "Interoperable with ship-based UCARS autoland". SNC's portfolio also includes PAR systems. [D] https://www.sncorp.com/what-we-do/mission-solutions/ai-autonomy/vision-systems/ground-based-landing-systems
  - TALS tracks an **airborne transponder** with high-bandwidth loops through touchdown and rollout [A].
  - UCARS-V2 uses a 35 GHz link with its own ship-motion stabilisation, needs no ship GPS, and the transponder draws 28 VDC at 25 W [A] (SNC product-sheet snippets).
- **Precision Approach Radar (PAR):**
  - Primary radar measures lateral and vertical deviation from the nominal approach path and range to touchdown. Controllers talk the pilot down.
  - It is mostly military: AN/FPN-63, AN/MPN, AN/TPN-22, ITT Exelis GCA-2000.
  - [A] https://skybrary.aero/articles/precision-approach-radar-par (snippet; the page itself returned 429), plus defence24.pl and everythingrf snippets.

### 3.11 GNSS jamming and spoofing; resilient PNT

- **EASA SIB 2022-02R4** [D] https://www.easa.europa.eu/en/domains/air-operations/global-navigation-satellite-system-outages-and-alterations and EASA news 3 Jul 2026
  - Issued **3 Jul 2026**, after R3 on 5 Jul 2024. It is a first output of a **joint EASA–EUROCONTROL task force**.
  - Recommendations: standard pilot–ATC phraseology, EFB integration, training, ATC capacity measures. ANSPs are asked to **keep ILS, DME and VOR running**. Manufacturers are asked to assess cumulative jamming and spoofing effects.
  - **"All spoofing events should be reported."**
  - Affected FIR ranking (7-day, snapshot 14 Oct 2026): Ankara 1, Bucuresti 2, Warszawa 3, Sofia 4, Tallinn 5, Vilnius 6, Nicosia 8, Istanbul 9, Helsinki 12, Riga 13.
  - Method: share of aircraft with ADS-B NIC ≤ 7.
- **EU Council note 9188/25** (21 May 2025; Lithuania, Estonia, Finland) [D] (PDF text extracted) https://data.consilium.europa.eu/doc/document/ST-9188-2025-INIT/en/pdf
  - "Since August 2024, a dramatic increase in jamming and spoofing".
  - Monthly cases by unique ICAO ID:
    - **Lithuania:** 556 (Mar 2024) → 890 (Oct 2024) → 1,185 (Jan 2025).
    - **Latvia:** 790 → 1,288.
    - **Estonia:** 1,150 (Oct 2024) and 1,085 (Jan 2025).
    - **Poland:** 1,908 (Oct 2024) → 2,732 (Jan 2025).
  - Calls to "deploy alternative or complementary systems, including ground-based legacy solutions".
- **EUROCONTROL** (Berz slides, Sep 2026) [D] link in §3.5:
  - The pilot reporting ratio versus detected events is only **2.6%–8.1%**, so pilot reports undercount.
  - Of 397 transatlantic flights spoofed over the Black Sea, about 10% still broadcast NIC = 0 when they entered oceanic airspace.
  - Impacts include GPWS failure, false EGPWS alerts, HUD/SVS failure, ROPS/RAAS failure, "Go-Arounds in unexpected positions" and transponder failure.
- **Other figures [A]:**
  - About 1,500 flights per day experienced spoofing by Aug 2024 (EUROCONTROL data via IATA, cited by the Council).
  - 122,607 flights were affected in the Baltic/Nordic region in Jan–Apr 2025, with 27.4% of flights in affected airspace in April.
- **Resilient PNT options [A]:**
  - DME/DME is the planned main backup "in TMA" for RNP operations (EUROCONTROL tender 2026).
  - SESAR PJ14-03-04 is studying DME enhancements, **LDACS-NAV**, **eLORAN** and Mode N.
  - DFMC (L1/L5 + E1/E5) and ARAIM.
  - No European eLORAN deployment decision was found.
  - Sources: https://rntfnd.org/2026/03/28/european-aviation-action-plan-for-gnss-interference-easa-eurocontrol/ ; https://www.eurocontrol.int/sites/default/files/2026-03/ectl-src-260015.pdf
- **[Y] Implications for approach guidance:**
  - **ILS is immune to GNSS spoofing**, which is why EASA wants it kept.
  - **GBAS and SBAS fail under jamming.** Spoofing of GBAS is harder, because the VDB is authenticated in newer standards [Y, not verified].
  - **Vision, radar or transponder ground tracking, and terrain-relative navigation** give dissimilar redundancy.

### 3.12 Continuous descent, steeper and curved approaches (noise and fuel)

- **CDO** [D] https://www.eurocontrol.int/concept/continuous-climb-and-descent-operations (2018 ECAC study on 2017 traffic):
  - Potential savings of **340,000 t fuel**, **>1 M t CO₂** and **€150 M** per year, plus **1–5 dB** noise reduction.
  - **35 kg fuel / 110 kg CO₂ / €15 per arrival** (network average).
  - **46 kg / 145 kg / €20 per flight** not currently flying CDO.
  - Spain: 36% of approaches were CDAs in 2021 versus an 18% European average [A].
- **Frankfurt increased glide slope.**
  - **3.2° ILS (the "ILS Y" procedure) on runway 25R/07L**, specifically for noise.
  - Noise reduction 0.5–1.5 dB(A); no extra go-arounds.
  - GBAS was used to give 3.2° on the other runways (first GBAS 3.2° landings "on March 30th").
  - Heavy types excluded; autoland not permitted on the Y procedure for some types.
  - [A] all from search summaries (International Airport Review, VATSIM briefing, Aviation Today/DFS). **The pages were not opened successfully.**
- **London City (LCY).**
  - **5.5°** steep approach requirement [D] https://aviationweek.com/special-topics/crossover-narrowbody-jets/embraer-e190-e2-certified-steep-approach (E190-E2 EASA steep approach certification, article 21 Jun 2021).
  - Manufacturers demonstrate a margin: about 7.5° for the A318 and Legacy 450, about 8.5° for the CS100 [A].
  - Runway landing distance about 1,319 m [A].
- **[Y] Physics of steeper approaches:**
  - Engines stay nearer idle and the aircraft is higher over the ground, so noise drops by roughly 1 dB per 0.2–0.3° [Y].
  - The penalty is a harder flare, higher sink rate and energy-management risk. A **guidance system that manages energy** (speed, configuration, thrust timing) is a real innovation lever.

---

## 4. Key numbers cheat-sheet (for slides)

| Quantity | Value | Tag |
|---|---|---|
| Standard glide path | 3°; CS-AWO range 2.5–3° (CAT I up to 3.5°) | [D] SKYbrary / EASA CS-AWO |
| Threshold crossing / ILS reference datum height | ~50 ft / 15 m | [D] SKYbrary / CS-AWO |
| Height lost per NM on 3° | ~318 ft | [Y] |
| Vertical speed on 3° | ≈ 5.3 × GS (kt) fpm (140 kt → ~740 fpm) | [Y] |
| LOC sensitivity at threshold | 0.00145 DDM/m → full scale ±~107 m | [D] (sensitivity) / [Y] (derived) |
| GS sensitivity | 0.0875 DDM ↔ 0.12 θ (0.36° at 3°) | [D] CS-AWO |
| LOC course alignment σ at threshold | 3.5 m (Type I), 1.5 m (Type II/III) | [D] CS-AWO |
| CAT I | DH 200 ft, RVR 550 m | [D] SKYbrary |
| CAT II | DH ≥ 100 ft, RVR ≥ 300 m | [D] SKYbrary |
| CAT IIIA / IIIB / IIIC | <100 ft & ≥200 m / <50 ft & ≥50 m / none | [D] SKYbrary |
| SA CAT I | DH 150 ft, RVR 400 m | [A] |
| EFVS-A / EFVS-L | natural vision below 100 ft / to touchdown and roll-out at RVR ≥ 300 m | [D] CS-AWO |
| LPV-200 alert limits | HAL 40 m, VAL 35 m | [D] EGNOS |
| APV-I alert limits | HAL 40 m, VAL 50 m (LPV minima down to 250 ft) | [A] (limits) / [D] (250 ft, ESSP) |
| EGNOS LPV in Europe | >1015 procedures, 546 airports, 97 PinS, >400 planned (AIRAC 2510) | [D] ESSP |
| GBAS integrity (sim model) | 2×10⁻⁷/landing (GAST C); 1×10⁻⁹/15 s (GAST D) | [D] CS-AWO |
| RNP values | RNP APCH final 0.3; RNP AR 0.3–0.1; RNP 1 terminal | [A]/[Y] |
| FSF stabilisation heights | 1,000 ft above airport elevation IMC; 500 ft VMC | [D] FSF ALAR BN 7.1 (PDF text extracted) https://flightsafety.org/?p=9650 |
| FSF speed band | **VREF ≤ IAS ≤ VREF + 20 kt** (NOT "+10/−5"; that is a common airline SOP variant) | [D] FSF BN 7.1 Table 1 |
| FSF sink rate | ≤ 1,000 fpm, else special briefing | [D] FSF BN 7.1 |
| FSF ILS tolerance | within one dot of GS and LOC; CAT II/III within the expanded localizer band | [D] FSF BN 7.1 |
| Unstable approach in accidents | causal factor in **66% of 76** approach-and-landing accidents/serious incidents (1984–1997) | [D] FSF BN 7.1 |
| Garmin Autoland cert | 18 May 2020, Piper M600 | [D] Garmin |
| ATTOL | >500 test flights, concluded Jun 2020 | [D] Airbus |
| GNSS interference (Poland) | 2,732 cases in Jan 2025 | [D] EU Council 9188/25 |
| CDO saving | 35 kg fuel per arrival average; 340 kt fuel per year ECAC | [D] EUROCONTROL |
| Frankfurt 3.2° | −0.5 to −1.5 dB(A) | [A] |
| LCY | 5.5° | [D] Aviation Week |
| Drone flight inspection | ">50%" fewer aircraft flight checks (FOCA-accepted, Skyguide) | [D] CANSO |
| UAS radar/transponder autoland | >99.95% recovery, GPS-independent (TALS) | [D] SNC |

**Radar-guidance geometry numbers [Y]** (useful if the challenge is radar-based):
- An angular error δ at range R gives a cross-track error ≈ R·δ. At 10 NM (18.5 km), 0.1° gives **32 m**; at 1 NM it gives **3.2 m**; at 0.5 NM it gives 1.6 m.
- So **angle accuracy must improve, or a second sensor take over, as the aircraft nears touchdown**. CAT I-like needs are a few metres vertically at 200 ft (about 0.6 NM from threshold on 3°).
- A 3° path at 0.6 NM is about 60 m height. A 35 m VAL (LPV-200) is the order of magnitude a ground-radar alternative must beat **with integrity**, not just accuracy.
- Radar range resolution ΔR = c/(2B): a 150 MHz bandwidth gives **1 m**.
- Ka-band (35 GHz, λ ≈ 8.6 mm) allows a narrow beam from a small aperture. Beamwidth ≈ 70·λ/D degrees, so a 0.5 m dish gives about 1.2°, and monopulse can track to about 1/10–1/20 of the beamwidth. [Y] textbook rules, not re-read

---

## 5. Regulation and certification map

| Domain | Reference | What it covers | Tag |
|---|---|---|---|
| Large aeroplanes | CS-25 (autopilot CS 25.1329; ROAAS since Amdt 24); CS-AWO for autoland and low-visibility certification | Automatic landing certification and LVO credits | [A]/[Y] |
| Normal-category aeroplanes (GA) | CS-23 (Amdt 5 and later is objective-based, with ASTM F44 consensus standards as means of compliance) | Basis for Garmin-Autoland-type STCs | [Y] |
| Rotorcraft | CS-27 / CS-29 (+ CS-AWO for helicopters) | Helicopter autopilot and coupled approaches; PinS ops in Air OPS | [Y] |
| VTOL | SC-VTOL-01 + MOC; PTS-VPT-DSN (vertiports, VFR only) | eVTOL safety objectives; vertiport geometry (OFV) | [A]/[D] |
| UAS | Specific category (SORA), certified category (EASA rules for certified UAS) | Drones; SkyRF-type operations fall into the specific category | [Y] |
| All-weather operations | Reg. (EU) 2021/2237; CS-AWO Issue 2 (ED Decision 2022/007/R) | SA CAT I/II, EFVS-A/L, SVGS, CVS, HUD credits | [A]; EFVS text [D] |
| PBN airworthiness | CS-ACNS Issue 2 Subpart C (replaces AMC 20-27/20-28 for new applications) | RNP APCH, LNAV/VNAV, LPV | [A] |
| SBAS receivers | RTCA DO-229F; DO-401 (DFMC) | Airborne SBAS MOPS | [A] |
| GBAS receivers | RTCA DO-253D; EUROCAE ED-144A; ground ED-114B | GLS | [D] (Boeing slides) |
| Vision systems | RTCA DO-315B / EUROCAE ED-179B | EVS, SVS, CVS, EFVS MASPS | [A] |
| Software | RTCA DO-178C (DAL A catastrophic … E no effect) + DO-330 tools, DO-331 model-based, DO-332 OO, DO-333 formal | Airborne software assurance | [Y] (not re-read) |
| Hardware | RTCA DO-254 (+ AMC 20-152A for complex electronic hardware) | FPGA/ASIC assurance (relevant to Advionics' FPGA work) | [Y]; AMC 20-152A mentioned in CoDANN II context [A] |
| Multicore | AMC 20-193 | Multicore processors | [A] |
| System safety | SAE ARP4754B (development), ARP4761A (safety assessment); CS 25.1309 (catastrophic ≤ 1×10⁻⁹/fh) | FHA, PSSA, SSA, fault trees | [Y] |
| Environment | RTCA DO-160G | Environmental qualification (Advionics tests temperature, shock, vibration) | [Y] |
| AI / ML | EASA AI Roadmap 2.0; Concept Paper Issue 2 (Levels 1–2) and proposed Issue 03 (Level 3); NPA 2025-07 (DS.AI); CoDANN I/II; EUROCAE ED-324/SAE ARP6983 | Learning assurance (W-shaped), explainability, human-AI teaming | [D]/[A] |
| Ground navaids | ICAO Annex 10 Vol I; Doc 8071 (testing of navaids) | ILS/GBAS ground performance and flight inspection | [D] (Doc 8071 named in Boeing slides) |
| Interference | EASA SIB 2022-02R4 | GNSS jamming and spoofing recommendations | [D] |

**[Y] Pitch rule for the certification path:**
- State the **assistance level** (EASA AI Level 1 or 2 versus classic automation), the **DAL** of each function, the **failure condition** of loss and of misleading guidance, and the **means of compliance**.
- Use **dissimilar redundancy** (e.g. a non-ML monitor around an ML estimator), the typical way to argue certifiability of ML in the near term (a run-time assurance or "safety monitor" pattern [Y]).

---

## 6. Predicted challenge formulations (5–7) with concept sketches

The likelihood rankings are my judgement [Y], driven by Advionics' RF/radar/IFF/naval profile and Intersoft's ILS and drone-inspection business.

### P1. GNSS-independent automated approach guidance from a ground RF sensor (radar/transponder "auto-PAR")

**Likelihood: high.** [Y]

- **Possible wording:** "Design an automated approach guidance system that does not rely on GNSS, for military airbases or remote airstrips, using ground-based sensors."
- **Jury expectations [Y]:**
  - a sensor choice justified by physics (band, aperture, accuracy versus range);
  - an uplink and datalink design;
  - integrity and alerting;
  - jamming robustness;
  - a deployable footprint;
  - reuse of existing assets (SSR/IFF interrogators, MLAT, PAR).
- **Numbers to show:**
  - required lateral and vertical accuracy at DH (CAT I-like: VAL ~35 m at 200 ft, compare LPV-200 [D]);
  - angular accuracy needed at each range (R·δ table in §4);
  - update rate ≥ 5–10 Hz for closed-loop autopilot coupling [Y];
  - latency budget < 400 ms (GLS model latency [D] as benchmark);
  - continuity and integrity targets per approach (e.g. ≤ 2×10⁻⁷ misleading information per approach, by analogy with GAST C [D]).
- **Concept sketch [Y]:**
  - **Sensors:**
    - a compact **Ka-band or X-band monopulse tracking radar** or a **phased array**, building on NORA/L-IESA non-rotating array know-how, at the runway side;
    - a **cooperative transponder** (Mode S/Mode 5 reply, or a dedicated beacon) on the aircraft, which raises SNR and identifies the aircraft (the IFF heritage);
    - a second, dissimilar ground sensor: **MLAT** from 3–4 receivers (Intersoft already does MLAT [D]) or a second radar at a different angle.
  - **Fusion:** a ground EKF fuses radar range, azimuth and elevation with MLAT TDOA. It computes deviations from the published path (FAS data block style), then uplinks them over an encrypted, low-probability-of-intercept datalink as **ILS-look-alike deviations (DDM-equivalent)**. The aircraft can then use its existing ILS/GLS autopilot modes. **Retrofit-friendly: "make it look like an ILS to the autopilot".**
  - **Airborne side:** INS/AHRS bridging during datalink dropouts (coast ≤ 5–10 s), plus a radar altimeter for the flare.
  - **Integrity:**
    - RAIM-like consistency checks between radar and MLAT and between ground track and aircraft INS (downlinked);
    - protection levels computed on the ground;
    - an alert within 2 s (time-to-alert similar to LPV [Y]);
    - multipath detection near the ground, where the radar elevation angle is unreliable below ~0.5° because of ground reflection [Y]. Mitigate with siting, a vertical aperture or an aircraft radar altimeter for the last 200 ft.
  - **Failure modes:**
    - multipath at low elevation;
    - rain attenuation at Ka-band (needs a link-budget margin);
    - datalink jamming (frequency hopping, directional antennas);
    - transponder failure (fall back to skin tracking);
    - wrong-aircraft association (Mode S addressing);
    - spoofed uplink (authentication).
  - **Certification:** ground equipment is approved like a navaid (Annex 10-like performance plus a ground software assurance level). Airborne software is DO-178C DAL B/C if guidance is advisory, A if it is coupled to autoland below 200 ft [Y]. Flight inspection reuses SkyRF (the sponsor's own product!) to validate the guidance volume.
  - **HMI:** standard ILS-like deviation bars plus a "GRD" source annunciation. The ground controller console shows the predicted touchdown point and stability criteria (FSF [D]).
- **Sustainability [Y]:**
  - Deployable without ILS civil works at small or temporary airfields, so there are fewer diversions in low visibility (each diversion burns hundreds of kg of fuel).
  - Allows CDO and steeper or curved finals because the ground computes any path. ILS fixes a single straight 3° beam.
  - Keeps operations going when GNSS is jammed (EASA SIB R4 [D]).

### P2. Automated approach and landing of a UAS on a moving deck or confined site (naval / tactical)

**Likelihood: high**, given the frigate/IFF customer base. [Y]

- **Possible wording:** "Propose an automated approach and landing guidance concept for a medium UAS (or VTOL drone) recovering onto a frigate deck in rough sea, without GNSS."
- **Jury expectations:**
  - ship-motion compensation;
  - a relative-navigation sensor suite;
  - prediction of deck quiescent periods;
  - safe abort logic;
  - EMC with the ship's radars;
  - reuse of the ship's IFF/L-IESA hardware.
- **Numbers:**
  - deck heave ±2–4 m and roll ±5–10° in sea state 5 [Y];
  - touchdown dispersion target ≤ 0.5–1 m (a precedent of ~15 cm within the planned point was reported for a 1990s UCARS demo [A]);
  - TALS reference of >99.95% recovery [D].
- **Concept sketch [Y]:**
  - **Sensors:**
    - a ship-mounted tracker. Option A: use the **L-IESA electronically steered IFF array** in a "precision interrogation" mode (monopulse angle plus range from transponder reply timing). Option B: a dedicated Ka-band tracker, as in UCARS.
    - UAS-side: a **camera on deck fiducials** (AprilTag/IR beacons), a laser or radar altimeter, IMU, and a UWB ranging beacon network on deck.
    - Ship-side IMU for the deck motion state.
  - **Fusion:** a relative-state EKF (UAS relative to the deck frame), plus a deck-motion predictor (AR model or Kalman forecaster over 5–10 s) for "quiescent period" landing windows.
  - **Integrity:** cross-check RF track against vision against UWB; vote 2-out-of-3; go around if the protection level exceeds the deck-size budget.
  - **Failure modes:** sea spray and night (use IR beacons), ship radar interference (frequency planning), loss of datalink (autonomous wave-off and loiter), GNSS spoofing (system is GNSS-free by design).
  - **Certification:** military airworthiness (EMAR / STANAG 4671 for UAS [Y]); software to DO-178C-like rigour; HMI for the landing safety officer.
- **Sustainability:**
  - Fewer lost airframes and less crew risk.
  - Electric VTOL UAS replace manned helicopter sorties for ship logistics (a fuel saving).
  - The same tech serves offshore wind farm resupply drones in the North Sea, which is local to Ostend/Bruges [Y].

### P3. Multi-sensor resilient approach guidance for manned aircraft under GNSS jamming/spoofing (the Baltic problem)

**Likelihood: medium-high.** [Y]

- **Possible wording:** "GNSS interference is disrupting approaches across Europe. Design an approach guidance architecture that remains safe and available when GNSS is jammed or spoofed."
- **Jury expectations:**
  - threat model (jamming versus spoofing; spoofing is worse, per EASA [A]);
  - detection;
  - sensor diversity;
  - graceful degradation;
  - crew alerting;
  - use of existing infrastructure (ILS, DME).
- **Numbers:**
  - Council figures (e.g. Poland 2,732 cases in Jan 2025 [D]);
  - pilot reporting ratio 2.6–8.1% [D];
  - LPV-200 limits [D];
  - DME/DME accuracy is typically ~0.1–0.2 NM-class, so RNP 1-ish but **not approach-grade vertical** [Y].
- **Concept sketch [Y]:**
  - **Layers:**
    1. a **GNSS integrity monitor**: multi-constellation consistency, an antenna-array angle-of-arrival spoof check (a CRPA, controlled reception pattern antenna, which is RF-heavy and fits Advionics), clock-jump and C/N0 checks, cross-check against INS, baro and radar altimeter;
    2. **reversion to ILS** where available;
    3. **DME/DME + INS** for the RNP initial segments;
    4. **terminal guidance from vision** (runway edge and threshold detection) **plus a radar altimeter plus terrain-relative navigation**;
    5. optionally a **ground radar or MLAT uplink** (P1).
  - **Fusion:** a federated filter (bank of sub-filters with solution separation, ARAIM-style), so one bad source can be identified and excluded.
  - **HMI:** a single "NAV SOURCE: ILS / GNSS-VERIFIED / GNSS-SUSPECT / VISION+INS" annunciation, a "SPOOF SUSPECTED" alert, and automatic suppression of GNSS-based TAWS false pull-ups (the EASA R3 concern about false TAWS pull-ups [A]).
  - **Certification:** CS-ACNS (PBN), CS-AWO (if vision credit is used), DO-178C/DO-254, AI Level 1 for the vision estimator under a non-ML monitor.
- **Sustainability:** fewer diversions and go-arounds, keeps CDOs flyable, avoids rebuilding expensive VOR/ILS networks, extends LPV use (no ILS hardware) by making it robust.

### P4. Autonomous drone flight inspection of approach aids, where the drone flies the approach path (SkyRF-style)

**Likelihood: medium**, because it is the sister company's product. [Y]

- **Possible wording:** "Automate the guidance of a measurement drone that must fly ILS/GBAS approach paths (and PAPI/radar patterns) precisely and safely near an active runway."
- **Jury expectations:**
  - path accuracy versus measurement accuracy;
  - **independence of the drone's position reference from the navaid under test** (the drone cannot use the ILS it measures);
  - airspace and runway safety;
  - automation of whole flight-inspection campaigns;
  - cost and CO₂ against inspection aircraft.
- **Numbers:**
  - ">50%" fewer aircraft flight checks (FOCA-accepted [D]);
  - the drone needs a position truth better than the ILS tolerances, e.g. ≪ 1.5 m at threshold for CAT II/III course alignment [D] σ. That means **RTK GNSS at cm level, plus a ground-based optical or laser tracker as a dissimilar truth**.
- **Concept sketch [Y]:**
  - **Flight path:** the planner generates LOC arcs, GS level runs, approach "mini-approaches" and PAPI angle sweeps from airport survey data.
  - **Navigation:** RTK + IMU, monitored by a ground total-station or laser tracker.
  - **Geofencing:** geofence and runway-incursion interlock with ATC (UTM/U-space link).
  - **Data:** auto-flagging of DDM/SDM out-of-tolerance live, plus a digital twin of the ILS radiation pattern to optimise the next leg.
  - **Integrity:** if the RTK fix is lost, abort to a safe hover or landing zone. Spoofing is detected by RTK consistency.
- **Sustainability:**
  - A flight-check aircraft (e.g. King Air class) burns about 300–400 kg/h [Y], while a drone runs on a few kWh, so CO₂ drops by orders of magnitude.
  - Less runway closure time and fewer delays.

### P5. Emergency autoland / approach guidance for single-pilot or incapacitation (GA, business aviation)

**Likelihood: medium.** [Y]

- **Possible wording:** "Design an automated approach and landing guidance system that can bring an aircraft safely to a runway if the pilot is incapacitated, including at airports without instrument approaches."
- **Jury expectations:**
  - a comparison with Garmin Autoland (which needs a GPS approach with lateral and vertical guidance [D]);
  - extension to non-instrument runways and GNSS-denied cases;
  - airport and runway selection logic;
  - ATC interaction;
  - the passenger HMI.
- **Numbers:**
  - Garmin cert 2020 [D];
  - FSF stabilisation rules [D] as a monitor (abort or go around if not stable by 500 ft VMC-like);
  - runway length margin factor (e.g. 1.67 × landing distance [Y]).
- **Concept sketch [Y]:**
  - **Ladder:** LPV if the receiver is healthy; else ILS; else a synthetic approach built on board from a runway database plus **vision runway detection** plus a radar altimeter.
  - **Integrity:** vision versus database versus inertial cross-check.
  - **HMI:** a one-button passenger interface, auto squawk 7700 [Y], and synthesised ATC voice.
  - **Certification:** CS-23 STC, DO-178C DAL A for the landing function, AI Level 1/2 with a monitor.
- **Sustainability:** small (social and safety), unless the pitch is "enables single-pilot ops and therefore lower-carbon regional aviation" [Y].

### P6. Approach guidance for low-noise curved, steep or continuous-descent approaches

**Likelihood: medium-low.** [Y]

- **Possible wording:** "Design guidance that lets aircraft fly curved, steeper or continuous-descent approaches safely to reduce noise and fuel."
- **Numbers:**
  - CDO saves 35 kg fuel per arrival average and 340 kt per year ECAC, with 1–5 dB less noise [D];
  - Frankfurt 3.2° gives −0.5 to −1.5 dB(A) [A];
  - LCY 5.5° [D];
  - a 3° → 3.5° path raises the aircraft by ~50 ft per NM [Y].
- **Concept sketch [Y]:**
  - An onboard **energy-management guidance** law (speed, configuration, thrust schedule) for an RNP-AR RF-leg-to-xLS final (or GLS with a selectable angle).
  - A ground-side tool (AMAN) to assign CDO-compatible sequencing.
  - Integrity: stabilisation predictor ("will we be stable at 1,000 ft?") with an early alert, which reduces go-arounds.
  - Certification: CS-ACNS PBN, CS-AWO if autoland; ATC procedure design to PANS-OPS.
- **Sustainability:** the strongest of all the options. Put the CO₂ and noise footprint numbers on a slide.

### P7. Helicopter or eVTOL approaches to hospital, offshore or vertiport sites (PinS + final visual segment)

**Likelihood: medium-low.** [Y]

- **Possible wording:** "Design automated approach guidance for HEMS/eVTOL to rooftop helipads or vertiports in low visibility."
- **Numbers:**
  - 97 PinS LPV in Europe [D];
  - PTS-VPT-DSN is VFR-only, with a funnel-shaped OFV [D];
  - SC-VTOL enhanced category ~10⁻⁹ [A].
- **Concept sketch [Y]:**
  - PinS LPV to the MAPt, then a local "last-mile" aid: a small **UWB/radar beacon or ILS-like micro-transmitter** at the pad, or IR markers plus vision. This turns "proceed visually" into "proceed with guidance".
  - Integrity: dual dissimilar (GNSS-LPV versus local RF versus vision).
  - HMI: hover-target symbology on the HUD/HMD.
- **Sustainability:**
  - Fewer HEMS cancellations in bad weather.
  - Electric eVTOL.
  - No large ground infrastructure.
  - Fits the PTS OFV funnel.

### Ranking for preparation time [Y]

1. P1 (ground RF, GNSS-independent)
2. P2 (UAS ship/confined landing)
3. P3 (jamming-resilient multi-sensor)
4. P4 (drone flight inspection)
5. P6 (CDO/steep/curved)
6. P5 (emergency autoland)
7. P7 (PinS/vertiport)

**Common core:** one fusion and integrity architecture slide that works for all of them: sensors → fusion with fault detection and exclusion → protection level versus alert limit → guidance → HMI and annunciation → fallback ladder.

---

## 7. A reusable 5-hour playbook for this challenge [Y]

| Time | Activity |
|---|---|
| 0:00–0:20 | Parse the brief and restate the requirement: aircraft class, environment, minima target, infrastructure allowed, GNSS assumed or not. Ask the Advionics mentor which part they care about: sensor hardware, algorithms or the operational concept. |
| 0:20–0:50 | **Requirements table**: accuracy (H/V at DH), integrity (alert limit, time-to-alert, risk per approach), continuity, availability, latency, update rate, size/weight/power, cost. Use §4 numbers. |
| 0:50–1:40 | Architecture options (2–3), then a trade matrix (weight the four jury criteria). Pick one. |
| 1:40–2:40 | Detail: sensor physics (band, aperture, accuracy versus range), fusion (EKF + FDE), fallback ladder, failure-mode table (6–8 rows), certification path (standards in §5). |
| 2:40–3:20 | Sustainability quantification: fuel or CO₂ per avoided diversion or go-around, CDO enablement, infrastructure avoided (ILS hardware, flight-check flights). |
| 3:20–4:30 | Slides (8–10): problem → requirement numbers → concept diagram → how it works on approach (timeline from FAF to touchdown) → integrity and failure modes → certification and roadmap (TRL) → sustainability → why Advionics (manufacturing, RF, IFF arrays) → summary. |
| 4:30–5:00 | Rehearse; prepare 3 Q&A answers (spoofing, multipath, certification of ML). |

**"Why Advionics" hooks [Y]:**
- they can **manufacture** the RF front-end (5 MHz–26 GHz, EN 9100);
- **non-rotating arrays and IFF** give cooperative, identity-aware tracking;
- **SkyRF** can flight-check the new guidance volume;
- the **defence demand** context (NATO, GBAD) means dual-use value.

---

## 8. Sustainability arguments (reusable)

| Lever | Argument | Number | Tag |
|---|---|---|---|
| CDO enablement | Guidance that lets aircraft fly CDO/curved finals | 35 kg fuel / 110 kg CO₂ per arrival (avg); 1–5 dB | [D] EUROCONTROL |
| Steeper glide | 3.2° at Frankfurt cut noise 0.5–1.5 dB(A) with no extra go-arounds | as stated | [A] |
| Avoided go-arounds and diversions | Unstable approaches are a causal factor in 66% of approach-and-landing accidents (1984–97); a stability predictor reduces go-arounds | 66% of 76 | [D] FSF |
| Infrastructure | LPV needs no ILS hardware per runway end; >1015 LPV procedures exist | >1015 / 546 airports | [D] ESSP |
| Flight inspection | Drones replace >50% of flight-check flights | >50% | [D] CANSO |
| Resilience | Keeps operations running under GNSS interference, avoiding diversions | Poland 2,732 cases/month | [D] Council |
| Electrification | Automated guidance is a prerequisite for eVTOL/UAS logistics replacing helicopters and vans | qualitative | [Y] |
| Lifecycle | Ground equipment made in an ISO 14001 factory; repairable; obsolescence management (Advionics offers this) | ISO 14001 | [D] Advionics |

Back-of-envelope figures [Y] (state them as estimates):
- A narrowbody **go-around** costs about 100–200 kg of extra fuel (~300–600 kg CO₂).
- A **diversion** costs about 1–3 t of fuel, plus passenger disruption.

---

## 9. What I could NOT find or verify (be honest about these)

- **Ideathon sponsor list / challenge text.** No public page names Advionics as a sponsor or says "Automated Approach Guidance". This comes only from the user's brief.
- **Advionics approach/landing products.** None found on advionics.be. Approach-related offerings belong to sister company Intersoft (SkyRF, GroundRF, ILS services).
- **Advionics predecessor company name and exact founding year.** Conflicting directory data (1960 / 1999 / 2002). The "10 jaar" page suggests the brand dates from ~2016.
- **Advionics patents, CORDIS/EU projects, detailed LinkedIn "About".** Not found (LinkedIn not fetched; one CORDIS search returned nothing relevant [A]).
- **Software/algorithm job ads** (DO-178C, Kalman, CV). None; only hardware, test and production roles were seen.
- **Current number of Belgian LPV procedures.** Not verified (the skeyes eAIP returned 403).
- **ROAAS EU applicability date.** The 1 Jan 2025 date may have been postponed (Opinion 05/2024); final text not read.
- **Exact current CS-AWO / Reg. 2021/2237 credits** (SA CAT I 150 ft/400 m etc.). Search summaries only, except the EFVS text, which I read.
- **ICAO Annex 10 primary text** (APV-I/II alert limits; ILS full-scale DDM values 0.155/0.175). Not read; secondary sources and my knowledge only.
- **Frankfurt 3.2° primary source.** Search summaries only.
- **SKYbrary stabilised-approach and PAR pages.** Blocked (HTTP 429). The FSF primary PDF was read instead.
- **EUROCONTROL "~1,500 flights/day spoofed (Aug 2024)"** and the Baltic 122,607 flights figure. Search summaries only.
- **TALS/UCARS accuracy figures.** No numeric accuracy published; "15 cm" is from a 1990s demo summary [A].
- **Daedalean PilotEye certification status (2026).** Unconfirmed.
- **Advionics' Ideathon jury members.** Unknown.

---

## 10. Source list (main URLs)

**Advionics and IE Group**

- https://advionics.be/ ; https://advionics.be/about/ ; https://advionics.be/news/ ; https://advionics.be/manufacturing/product-development/ ; https://advionics.be/10-jaar-advionics-opening-nieuwe-hal/
- https://jobsopderadar.be/ ; https://jobsopderadar.be/vacature/hardware-development-engineer?jobid=1360473931
- https://www.vrt.be/vrtnws/nl/2025/03/06/radarproducent-advionics-uit-oostkamp-breidt-uit-met-grote-hal/ ; https://www.vrt.be/vrtnws/nl/2026/03/11/advionics-uitbreiding-oostkamp-radarsystemen/
- https://www.janes.com/osint-insights/defence-news/weapons/bedex-2026-kongsberg-signs-lois-with-belgian-companies-for-gbad-co-operation
- https://www.b2match.com/e/feindef-2025/participants/2915895 ; https://www.twoinstitute.com/ent/advionics/
- https://intersoft-electronics.com/ ; https://intersoft-electronics.com/cns-test-equipment/navaids-test-equipment/ ; https://intersoft-electronics.com/cns-services/navaids-services/ ; https://intersoft-electronics.com/cns-services/atc-and-airport-services/ ; https://intersoft-electronics.com/cns-test-equipment/simulators-and-signal-generators/skyrf-generator/ ; https://intersoft-electronics.com/radar-technology/drone-detection-for-modern-cuas-missions/
- https://canso.org/skyguide-and-intersoft-electronics-services-to-deliver-cns-drone-measurements-as-a-service/

**Event**

- https://euroavia.eu/event/ideathon-2026/ ; https://ideathon.euroavia.eu/ ; https://ideathon.euroavia.eu/wp-content/uploads/Ideathon-2026-Regulations-1.1.pdf ; local booklet `D:\Masaustu\Ideathon 2026\EUROAVIA Ideathon 2026.pdf`

**Technical**

- https://skybrary.aero/articles/instrument-landing-system-ils
- https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-all-weather-operations-cs?page=24 (signal-in-space) ; ...?page=14 (EFVS)
- https://egnos.gsc-europa.eu/lpv200_availability
- ESSP slides: https://www.icao.int/sites/default/files/APAC/Meetings/2025/2025%20GBASSBAS%20Implementation%20Workshop%20for%20Air%20Space/Presentations/1-2-6-ESSP-Experience-as-EGNOS-Service-Provider-in-Europe-Martin.pdf
- GBAS slides: https://www.icao.int/sites/default/files/SAM/MeetingDocs/2026/0902-Taller-Radionavegacion-NAMCARSAM/2.%20Presentaciones%20-%20Presentations/Murphy-GBAS-Global-Developments-20260829.pdf
- https://www.easa.europa.eu/en/domains/air-operations/global-navigation-satellite-system-outages-and-alterations ; https://www.easa.europa.eu/en/newsroom-and-events/news/easa-updates-safety-information-bulletin-gnss-interference
- https://data.consilium.europa.eu/doc/document/ST-9188-2025-INIT/en/pdf
- EUROCONTROL GNSS slides: https://www.icao.int/sites/default/files/MID/MeetingDocs/2026/GNSS%20%26%20PBN%20Workshop/Documentation/GNSS%20Vulnerabilities%20and%20Emerging%20Threats-EUROCONTROL.pdf
- FSF ALAR BN 7.1: https://flightsafety.org/?p=9650
- https://www.garmin.com/en-US/newsroom/press-release/aviation/2020-garmin-autoland-achieves-faa-certification-for-general-aviation-aircraft/
- https://airbus.com/en/newsroom/press-releases/2020-06-airbus-concludes-attol-with-fully-autonomous-flight-tests ; https://www.airbus.com/en/newsroom/stories/2026-06-computer-vision-automated-landing-and-embedded-ai-for-tomorrows-cockpits
- https://www.easa.europa.eu/en/newsroom-and-events/news/easa-publishes-artificial-intelligence-concept-paper-issue-02-guidance ; https://www.easa.europa.eu/en/newsroom-and-events/news/easa-releases-latest-issue-its-concept-paper-artificial-intelligence
- https://tech.eu/2025/08/05/uav-destinus-acquires-daedalean-in-225m-deal-to-boost-ai-capabilities/
- https://www.euspa.europa.eu/newsroom-events/news-archive/helicopter-industry-goes-egnos-advantage
- https://verticalmag.com/opinions/easa-publishes-technical-design-specifications-vertiports/
- https://www.sncorp.com/what-we-do/mission-solutions/ai-autonomy/vision-systems/ground-based-landing-systems
- https://www.eurocontrol.int/concept/continuous-climb-and-descent-operations
- https://aviationweek.com/special-topics/crossover-narrowbody-jets/embraer-e190-e2-certified-steep-approach

PDF text was extracted locally with pypdf (`python -I`). Scratch copies are in the session scratchpad and are not part of the project.
