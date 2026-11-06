# R9 — Extra NG: canopy operation, cockpit and systems, take-off performance, canopy events (for the alert retrofit)

- **Read by:** subagent R9-extra, **2026-11-05**.
- **Tags:** [D-ag] = read at the source by R9 in this session (URL + page/section given). [Y] = secondary source, search
  snippet, or R9 interpretation. Facts quoted from earlier project files carry that file's name (for example "R0 [D]").
  They were not re-read here unless stated.
- **Not redone:** the AAIB G-MIIL mechanism details, AD 2025-0156, SB-NG-2-22, PKBWL 2022/1097 and 2023-0061 (see `R0_*`,
  `R1_extra_ng_canopy_design.md`, `R8_canopy_latch_mechanisms.md`). R9 re-read only the AAIB passages listed below.
- **Downloads** (untrusted data): `D:\tmp_ideathon\easa\dl\r9_extra\`. Text extracts and page renders:
  `D:\tmp_ideathon\easa\txt_r9\`. Scripts in the session scratchpad; outputs saved as `txt_r9\r9_tobudget_output.txt` and
  `txt_r9\r9_table_check.txt`.
- **Tables:** all tables are hand-written by R9, except the take-off table in §4.4. That one comes from the script output
  and was checked with `datawiz.tablo.denetle` (0 findings, `r9_table_check.txt`).

## Sources

Hand-written list. sha256 = first 16 hex characters of the downloaded file.

| # | Source | What R9 read | URL | sha256 |
|---|---|---|---|---|
| S1 | Extra, **SB-NG-1-24 Issue A**, 19 Dec 2024, "Canopy-Placard" (5 pp.) | all 5 pages + Fig. 1/2 rendered as images | https://extraaircraft.com/download-pdf/3470/ | 5e3982f8fbb38b9f |
| S2 | Extra, List of SB/SL EXTRA NG, Doc. EX-01704, 19 Dec 2024 (1 p.) | all | https://extraaircraft.com/download-pdf/2767/ | 41efe814440fdc65 |
| S3 | Extra, POH/AFM revision status, dated 19 Dec 2025 (1 p.) | all | https://extraaircraft.com/download-pdf/2751/ | f942c75eb894ce79 |
| S4 | Extra, AMM revision status, dated 19 Dec 2025 (1 p.) | all | https://extraaircraft.com/download-pdf/2757/ | e35f202acef670e7 |
| S5 | Extra, **SL-NG-3-22 Issue A**, 23 Dec 2022, GNX 375 audio to GMA 245R (3 pp.) | all | https://extraaircraft.com/download-pdf/2788/ | 74ebd19c997ddcba |
| S6 | Extra, **SL-NG-1-22 Issue A**, 21 Mar 2022, G3X Touch fuel quantity / FAA AD 2022-03-15 (1 p.) | all | https://extraaircraft.com/download-pdf/2773/ | 0bd5bb574f6d28ce |
| S7 | Extra, **SB-NG-1-21 Issue A**, 14 Jul 2021, starter solenoid circuit (5 pp.) | all | https://extraaircraft.com/download-pdf/2770/ | 5be74f8b4e801936 |
| S8 | Extra tech-service page (document list) | page text via WebFetch, 5 Nov 2026. It answered this time (no block). Items marked "registration required" were **not** opened | https://extraaircraft.com/tech-service/ | — |
| S9 | Extra NG product page | full page text (HTML saved, tags stripped locally) | https://extraaircraft.com/ng | — (ng_page.html) |
| S10 | Extra, "EXTRA NG Lookbook", ©2019 (5 pp.) | text of all pages; p. 3 "INTERIOR" photo rendered and cropped | https://extraaircraft.com/wp-content/uploads/2024/01/EXTRA-NG_Lookbook.pdf | 094cf86de1043835 |
| S11 | EASA **TCDS EASA.A.620 Issue 04**, 02 Dec 2020 (R1's copy `dl\reg\TCDS_104842.txt`) | §A.II, §A.III items 5–19, Notes. EASA page checked: Issue 04 is still the current issue | https://www.easa.europa.eu/en/downloads/104842/en | (R1) |
| S12 | AAIB Bulletin 4/2024, G-MIIL (main session's copy `dl\aaib\G-MIIL.txt`) | text pp. 1–2 (history), p. 3 fn 1, p. 7 (aircraft), p. 8 (canopy, window), p. 9, p. ~24 (pilot's hand on throttle) | https://assets.publishing.service.gov.uk/media/65d61630188d77001103883c/Extra-NG_G-MIIL_04-24.pdf | (main) |
| S13 | Extra, SB-NG-2-22 Issue A (R1's copy) | pp. 2 and 5 rendered as images (step 7 "front most latch opening"; Fig. 2 rear lock) | https://extraaircraft.com/wp-content/uploads/2024/02/SB-NG-2-22A.pdf | (R1) |
| S14 | AOPA Pilot, D. Hirschman, "Extra NG: mild to wild", 11 Aug 2020 (Dec 2020 issue) | article text and spec box via WebFetch | https://aopa.org/news-and-media/all-news/2020/december/pilot/extra-ng-mild-to-wild | — |
| S15 | BEA report **BEA2016-0092**, Extra 300 **D-EFBY**, 18 Feb 2016 (5 pp., French) | all | https://bea.aero/fileadmin/uploads/tx_elydbrapports/BEA2016-0092.pdf | (in dl\r9_extra) |
| S16 | AAIB Bulletin 6/2013, Extra EA 300/L **G-ZXCL**, 7 Feb 2013 (1 p.) | all | https://assets.digital.cabinet-office.gov.uk/media/5422fe06ed915d137100097f/Extra_EA_300_L_G-ZXCL_06-13.pdf | (in dl\r9_extra) |
| S17 | BEA report **BEA2021-0369**, Extra 330LX **F-HLIK**, 1 Aug 2021 (English, 3 pp.) | all | https://bea.aero/fileadmin/user_upload/F-HLIK_EN.pdf | (in dl\r9_extra) |
| S18 | FAA NPRM, FR doc 2025-22445 (main session's copy `dl\reg\FR-2025-22445.txt`) | unsafe-condition paragraph | https://www.transportation.gov/regulations/federal-register-documents/2025-22445 | (main) |
| S19 | IAC news, 29 Jan 2021, "The Extra NG receives FAA Certification" | page text | https://www.iac.org/news/2021-01-29-the-extra-ng-receives-faa-certification | — |
| S20 | globalplanesearch listing, 2022 Extra NG **G-NGSA** | page text | https://www.globalplanesearch.com/aircraft/4126734-2022-extra-300-ng-for-sale-in-lee-on-the-solent- | — |
| S21 | airframer.com Extra NG programme page | page text | https://www.airframer.com/program/ExtraNG | — |

**Tried, blocked or missing (not bypassed):**
- controller.com, aircraft.com and aviationtrader.com.au listings: **403**.
- AOPA nxtbook pages: **403**. aeroexpo brochure: **403**. aviation-safety.net: **403**.
- FAA registry N80NG: **403**.
- NTSB WPR26LA026 PDF (`carol-repgen …/201899/pdf`): **403**. The 403 body is saved as `NTSB_WPR26LA026_403.html`.
- manualshive 330LX POH: bot-protection "Access Denied".
- pilotenschule.ch 330LX checklist and briefing PDFs: **404**.
- Extra POH 1.18, Pilot Information Manual and AMM: registration required, not attempted.

---

## 1. Canopy operation

### 1.1 Hardware the pilot handles

1. **Hinge:** the canopy is hinged on the **right** with three steel hinge pins and brackets. It opens to the right. A woven
   nylon lanyard holds it open. [D-ag, S12 p. 8]
2. **Locks:** three steel **shoot bolts** engage **roller lugs** fixed to the fuselage along the **left** cockpit edge.
   Each bolt ends in a ramp 15 mm long with 5 mm rise, which gives 3:1 mechanical advantage. [D-ag, S12 p. 8]
   - The lug rollers reach the bolts through **"latch openings"** in the canopy inner frame. SB step 7 names the "front
     most latch opening". [D-ag, S13 p. 2]
   - SB Fig. 2, "Rear canopy lock (view from outside…)": the bolt runs along the frame. When the bolt is "fully engaged", the
     lug roller sits on top of it. [D-ag, S13 p. 5]
3. **Handles:** two identical handle sets, one in the front cockpit and one in the rear. Both work the **same linkage tube**,
   and a **tension spring** pulls the tube towards locked. [D-ag, S12 p. 9]
   - The sliding handle sticks out through the canopy frame. To unlock, the pilot squeezes it towards a fixed handle.
     [D-ag, S12 p. 9]
4. **The partial lock:** close the canopy and let go of the handle. The spring moves the handle only until it "just enters
   the green lock area". The handle centres are then 60 mm apart, against 70 mm when locked or open (S12 p. 9, re-read
   here; numbers in R0 [D]). Full lock needs a manual pull **fully rearward**.
   Forces to open (R0 [D], AAIB p. 20, not re-read): **136 N** from full lock, **90 N** from partial lock. Partial to full
   lock takes **60 N**.
5. **What the pilot can see and feel:** the bolts are hidden inside the frame. There is **no visible difference** at the
   frame edge between full and partial lock (R0 [D], AAIB p. 20). The only cues are:
   - the handle position against the placard;
   - a "clunk" at full lock that can be felt and heard (R0 [D], AAIB p. 10; SB-NG-2-22 step 19, "audible / acoustic and
     tactile confirmation", R1 [D-ag]).
6. **Sliding window:** a small sliding window sits on the **left** side of the transparency. It is "positioned for ease of
   operation by the pilot in the rear seat and slides rearwards to open". [D-ag, S12 p. 8]

### 1.2 Step by step: close and lock, rear seat

R9 assembled this sequence from S12, the POH text quoted by the AAIB, and S1. The POH itself was **not** read.

1. Sit in the rear seat and fasten the harness. Close the canopy: pull it down to the **left**, onto the left sill.
   [D-ag, S12 pp. 1–2: "secured his harness and closed the canopy, before completing the pre-start checks and starting
   the engine"]
2. Let go of the sliding handle. The spring takes it only to the **partial-lock** position (60 mm). [S12 p. 9]
3. **Pull the aft locking handle fully rearward to the end stop.** Check that the handle is in the LOCK position (green
   marking). This is the POH 1.11 wording, 23 Dec 2022, as quoted by AAIB pp. 11 and 27 (R0 [D]).
4. Confirm against the placard. The **current** placard (P/N EX-01106.01-Canopy) shows green only in a narrow band at the
   **LOCK** end of the handle slot. The rest of the slot is red, under "← → UNLOCK". [D-ag, S1 p. 3, Fig. 2]
   - The **initial** placard showed two equal circles: green "LOCK" and red "UNLOCK" (S1 Fig. 1). The green circle
     covered almost half the slot. [D-ag]
   - [Y] The partially locked handle stops "just as it enters the green lock area" (S12 p. 9). On the old placard, that
     spot already looked green. On the new placard it sits in the red. This matches the SB purpose: "clarification of the
     indicated canopy locking condition" and to "reduce the misuse of the canopy locking" (S1 p. 1).
   - [Y] The direction "rearward = LOCK" fits the placard having LOCK on the left side as drawn, since the placard is
     viewed on the left frame from inside. Placard orientation in the aircraft is not shown in S1.
5. From the front seat, the same mechanism and placard apply: both handles have placards [D-ag, S1 step 1]. The POH
   wording quoted by the AAIB names the **aft** handle. Whether the front occupant is expected to check the front handle:
   NOT VERIFIED.

### 1.3 Unlock, normal opening and jettison

- **Normal opening:** squeeze the sliding handle towards the fixed handle to unlock, then swing the canopy right.
  [D-ag, S12 p. 9]
- **Emergency (AAIB p. 11, R0 [D]):** open normally. In flight, low pressure flips the canopy open. To jettison, push the
  canopy slightly **forward** while opening.
- PKBWL (R1 [D-ag]): when unlocked, the canopy "moves automatically back on the hinge guides and detaches".
  The two descriptions differ in direction (forward push versus aft movement). R9 cannot resolve this without the POH.
  **NOT VERIFIED.**
- **No separate jettison handle** is mentioned in any source read. [Y]

### 1.4 Serial-number and modification states

| State | Pawls / spring | Placard | Source |
|---|---|---|---|
| NG001–NG060 as built | original pawl contour | initial (two circles) | PKBWL 2023-0061 via R0 [D]; S1 |
| NG061–NG064 as built | new contour + extra spring (ECO-NG-22-09 / 23-07) | initial, unless the canopy is from the later batch | R0 [D]; S1 p. 4 [D-ag] |
| NG065 and up | new | new (EX-01106.01) | S1 p. 4 [D-ag] |
| Older aircraft modified per **AI-NG-01-23** or **AI-NG-02-23** | new (AI-NG-02-23 = retrofit, R0) | new | S1 p. 4 NOTE [D-ag] |
| After SB-NG-1-24 / AD 2025-0156 | unchanged | new on all aircraft | S1; AD (R0) |

Notes on the table:
- Old placards were fitted to aircraft up to **NG064** and to replacement canopies **up to canopy serial 071**.
  Canopy P/N is EX-21300.00. [D-ag, S1 pp. 1, 2, 5]
- **New finding:** S1 names a second work instruction, **AI-NG-01-23**, besides AI-NG-02-23. Its content is unknown.
- **Correction to the brief:** **SB-NG-1-24 is a placard SB only.** It contains no latching change. [D-ag, S1, all pages]
  - Its steps: (1) remove both placards and clean; (2) fit new placards; (3) update the POH/AFM to Rev. 16;
    (4) logbook entry and return form.
  - Extra itself marks it "COMPLIANCE MANDATORY", within 3 months or 25 FH. Applicability: NG002–NG064.
  - The mechanical latching improvement is the ECO / AI-NG work, not this SB.
- **Current manuals:** POH/AFM EX-01701, Edition 1 **Rev. 18, 17 Nov 2025** (approval the same day; status sheet dated
  19 Dec 2025). AMM EX-01702, Edition 2 Rev. 10, 17 Nov 2025. [D-ag, S3, S4]
  The tech-service page lists "POH EXTRA NG 1.18" behind registration [D-ag, S8]. What changed in Rev. 17 and 18 is
  NOT VERIFIED.
- **SB/SL list as of 19 Dec 2024** [D-ag, S2]:
  - SB-NG-01-21 (starter solenoid);
  - SL-NG-01-22 (G3X fuel quantity);
  - SB-NG-01-22 (tank chafing);
  - SL-NG-02-22 and SB-NG-2-23 (tail-spring bracket);
  - SB-NG-02-22 (canopy frame);
  - SL-NG-03-22 (GNX 375 wiring);
  - SB-NG-01-23 (main gear attachment);
  - SB-NG-1-24 (canopy placard).
  - No AD/LTA is listed against any of them on that sheet.

## 2. Checklist items and pilot practice

1. **The POH checklist text was not read** (registration required, S8). Known wording comes only from the AAIB quotes
   (§1.2) and from PKBWL. PKBWL says POH Rev. 11 reworded the pre-flight check (Section 4) and §7.7 (R1/R0).
2. **Before take-off:** "The pre-takeoff checklist is short with fuel selector, canopy latch, and elevator trim among the
   critical items." [D-ag, S14] So the canopy is a before-take-off item on the NG.
3. **Before start:** the G-MIIL pilot closed the canopy before the pre-start checks and engine start, then taxied to the
   hold and did power checks there. [D-ag, S12 pp. 1–2]
   For the predecessor EA 300/S, an NTSB summary says the POH has "close and lock the canopy" in both the Before Starting
   Engine and the Taxi checklists [Y, search snippet of an NTSB report; not opened].
4. **The "push up on the canopy" habit:**
   - D-EFBY's pilot "by habit" pushed upward on the canopy before line-up and found nothing wrong. The handles were
     nevertheless in an intermediate position. [D-ag, S15 p. 5]
   - N330SB's pilot "did not push up on it as usual" (R5 row R5-062 [D-ag by R5]).
   - [Y] The push test is a pilot habit, not a reliable check. On D-EFBY it failed to find an intermediate lock.
5. **Taxi with the canopy open:** **no source found** for the NG. [Y] The left sliding window (S12 p. 8) offers
   ventilation, so taxiing closed is plausible. NOT VERIFIED for the fleet.
6. **Taxi:** "the nose-up deck angle requires S-turns during taxi". [D-ag, S14]
7. **In flight:**
   - The G-MIIL pilot flew "with his left hand permanently on the throttle". [D-ag, S12 p. ~24]
   - The PKBWL 2023-0061 finding that the front passenger may have loosened the locks (R0 [D]) shows that the front handle
     can be moved in flight.

## 3. Cockpit and systems

### 3.1 Seats and roles

- Minimum crew: 1 pilot in the **rear seat**. Passenger in the front seat. [D-ag, S11 item 18]
- Front cockpit: dual controls and "simplified instrumentation". [D-ag, S12 p. 7]
- Type operations: **Day-VFR**, maximum operating altitude 10,000 ft. [D-ag, S11 item 10]
  Extra: "the EXTRA NG is a VFR Day airplane". [D-ag, S6]

### 3.2 Avionics

1. **The type design uses Garmin G3X Touch**, "including the Engine Information System (EIS)". "This configuration is
   included in the EXTRA NG Type Design." The EIS uses a **GEA 24** (connector P244). [D-ag, S6]
   The product page and lookbook list "Garmin G3X Touch" as standard panel equipment. [D-ag, S9, S10 p. 3]
   - **Conflict:** the AAIB says G-MIIL had a "Garmin G1000 EFIS" [D-ag, S12 p. 3 fn 1 and p. 7].
     [Y] Extra's own documents say G3X Touch is the type design (S6, from 2022, covering NG ≤ NG035, which includes
     NG028). The AAIB item is probably an error. Our design should assume **G3X Touch**.
2. **Audio panel: Garmin GMA 245R** (remote unit), "located on the LH side wall of the central tunnel". It is reached by
   removing the bottom fuselage cover. Connector P2401/J2401. [D-ag, S5 pp. 1–2]
   - The audio panel is configured from the G3X ("Audio Panel Configuration Page"). [D-ag, S5 p. 3]
   - Alert inputs: from **NG048**, the GNX 375 traffic audio uses **ALERT 1 IN** (pins 31/32). Before NG048 it used
     NAV 1 IN (pins 17/18), which "could be muted". SL-NG-3-22 moves it to ALERT 1 and sets ALERT 1 volume to 50 %.
     [D-ag, S5]
   - [Y] So ALERT 1 is taken on aircraft with a GNX 375. GMA 245 has more alert inputs (R7: Alert 1–4). Whether they are
     free on the NG: NOT VERIFIED.
3. **Other units:**
   - Standard (S9, S10): Trig TY91 COM, Trig TT2X transponder, analogue ASI, analogue altimeter, magnetic compass.
     [D-ag]
   - AOPA test aircraft: "IFR-capable G3X" PFD/MFD in the rear cockpit, G5 standby, GNX 375, com radio, digital
     autopilot. [D-ag, S14]
   - G-NGSA (2022): G3X MFD, GNX 375, GTR 225A COM, **GSA 28** autopilot servo. [D-ag, S20]
   - Listing snippets [Y, 403 on the pages]: "G3X Touch 10.6" with GMA 245R" (2025 aircraft). A 7-inch GDU 450 in the
     front cockpit (2022 aircraft). "GMA 24R" on NG076 (probably a typo for 245R).
4. **Switches and breakers** (AOPA photo captions [D-ag, S14]):
   - "Electrical switches are color coded and easy to reach on the center console."
   - "Circuit breakers are hidden by a thin cover that opens if any of them pop."

### 3.3 Rear-panel layout (lookbook photo, R9 interpretation)

[Y] S10 p. 3 "INTERIOR" photo, cropped at 250 dpi.
- The seat in the photo carries the "Adj. seat" callout. Only the **rear** seat is adjustable (S9: "Adj. composite rear
  seat", "Composite front seat"). So R9 takes the photo to show the **rear cockpit**. This also fits AOPA (G3X in the rear
  cockpit).
- **Main panel**, left to right:
  - air vent;
  - analogue ASI, with registration and "EXTRA" placards above it (top left);
  - large G3X Touch display in the centre;
  - analogue altimeter, with the magnetic compass above it (right);
  - air vent.
- **Below the panel:** a console with a row of coloured toggle switches and a breaker area, then the Trig COM and XPDR.
  The stick stands in front of the console.
- **Left wall:** a lever with a large **white round knob** running in a slot (taken as the **throttle**). Further forward
  and higher are a **blue** knob and a **red** knob (taken as **propeller** and **mixture**, by the usual colour code).
  **NOT VERIFIED.**
- **Lamp space [Y]:** the placard area top-left beside the ASI, and the strip under the G3X bezel. Both are inside the
  pilot's central view.

### 3.4 Engine controls

- The TCDS lists an **ELOS against CS 23.777/23.781, "Position and shape of Engine Controls"**. [D-ag, S11 §A.II]
  [Y] The NG's engine controls already depart from the standard CS-23 position and knob shapes under an agreed
  equivalence. Any change to the throttle knob (for example a vibrator or a stop) would touch that ELOS.
- Whether the front throttle is mechanically linked to the rear one: **NOT VERIFIED**.

### 3.5 Electrical

1. "Electric starter", "**60 Amp** lightweight alternator", "**12V battery**", "Trickle charger socket".
   [D-ag, S9; S10 p. 2]
   [Y] This means a nominal **14 V DC** bus. It matches R4's earlier inference. No wiring diagram was read.
2. **Main electrical board:** behind the **LH main-gear cuff**, reached through the bottom fuselage access panel. The
   starter solenoid sits on it. [D-ag, S7 pp. 2–3]
   - The positive coil terminal goes to the **SlickStart** module and the ignition switch. An ACS A-510-2 ignition switch
     is an approved alternative. [D-ag, S7]
   - The SB uses MIL-W-22759 20 AWG wire and Extra part numbers. [D-ag, S7 p. 4]
   - A stuck starter is handled with the **master switch**. [D-ag, S7 p. 1]
3. **Central tunnel:** under the bottom fuselage cover. The GMA 245R is mounted there. [D-ag, S5]

## 4. Engine, propeller and performance

### 4.1 TCDS (S11, [D-ag])

- **Engine:** Lycoming **AEIO-580-B1A**. **315 hp at 2700 rpm**; 306 hp at 2600 rpm. Oil pressure during start and
  take-off up to 115 psig.
- **Propeller 1:** MT **MTV-9-B-C/C198-25**, 3 blades, 1980 mm.
  - Maximum take-off and continuous rpm: **2600** (Normal and Aerobatic categories); 2700 (Aerobatic category only).
- **Propeller 2:** MT **MTV-14-B-C/C190-130**, 4 blades, 1900 mm. Maximum rpm **2700**.
- **Note 2:** a standard CofA needs the Gomolzig EA300-606000 silencer. With the 3-blade prop it also needs the 2600 rpm
  limit. Otherwise the CofA is for aerial work only.
- **Speeds:** VNE **221 KIAS**. VO / VNO 144 KIAS (Normal) and 161 KIAS (Aerobatic).
- **Masses:** MTOW 950 kg. ACRO I ±10 g at 820 kg (single seat); ACRO II ±8 g at 900 kg; ACRO III ±6 g at 950 kg.
- **Note 1:** lifetime limited to 1500 h until fatigue testing is complete.

### 4.2 Manufacturer and flight-test numbers

- **Product page (S9, [D-ag]):**
  - Vs 56 kt at 950 kg; 50 kt at 750 kg.
  - Va (acro) 158 kt. Max cruise 202 kt.
  - Typical empty weight 635 kg.
  - Fuel: 193 l usable; 73 l usable for aerobatics.
  - The page gives **no take-off distance and no climb rate**.
- **AOPA flight test (S14, [D-ag]):**
  - Take-off: "light forward stick raises the tailwheel off the runway surface at about **40 KIAS**". The NG "is
    airborne at **80 KIAS**".
  - Climb: "**climbing 3,000 feet per minute** going through pattern altitude" at 95 kt and 30° pitch.
    A power reduction to 25 in MAP / 2,500 rpm follows.
  - Spec box: Vx **80 KIAS**, Vy **105 KIAS**, stall **63 KIAS**, VA 161, VNE 221.
  - Spec box: maximum demonstrated crosswind 15 kt; maximum inverted flight 4 min; price $450,000 (2020).
  - The spec box gives **no take-off distance and no rate-of-climb figure**.
  - The 63 KIAS stall in AOPA against 56 kt on the Extra page is not explained (different weight or flap-less IAS
    versus CAS) [Y].

### 4.3 Take-off distance: the nearest primary number is a predecessor

- **Extra 300 (D-EFBY) flight manual, quoted by the BEA:** at **950 kg**, paved runway, 500 ft, no wind, 5 °C:
  - **ground roll 105 m**;
  - take-off distance over 50 ft **230 m**;
  - landing over 50 ft 548 m; landing roll 175 m.
  - [D-ag, S15 p. 2]
- Extra 330LX POH worked example, "ground roll 112 m at 870 kg": search snippet only (R8 and R9), **not verified**.
- [Y] The NG has 315 hp against the Extra 300's 300 hp, the same 950 kg MTOW and a cleaner airframe. Using the Extra 300
  roll as the NG's short case is a reasonable proxy. It is **not** NG data.

### 4.4 Take-off time budget [Y]

Constant-acceleration model, run by R9. Inputs:
- roll from §4.3;
- lift-off 60–65 kt assumed (≈ 1.1–1.16 × Vs 56 kt);
- AOPA's 80 KIAS lift-off as case B;
- R8's long case (200 m).

Output file: `txt_r9\r9_tobudget_output.txt`. Table generated from the script output with `datawiz.tablo.markdown_tablo`.
Times are from brake release / full power.

**Lift-off comes 6–8 s after brake release on a paved runway, and 30 kt after about 3 s.**

| Case | Accel (m/s²) | t to 30 kt (s) | t to 40 kt (s) | t to lift-off (s) | Roll to lift-off (m) |
|:---|---:|---:|---:|---:|---:|
| A: 105 m roll, lift-off 65 kt | 5.3 | 2.9 | 3.9 | 6.3 | 105 |
| A': 105 m roll, lift-off 60 kt | 4.5 | 3.4 | 4.5 | 6.8 | 105 |
| B: lift-off 80 KIAS, accel. as A | 5.3 | 2.9 | 3.9 | 7.7 | 159 |
| C: 200 m roll, lift-off 65 kt | 2.8 | 5.5 | 7.4 | 12.0 | 200 |

- After lift-off, at the AOPA climb of 3,000 ft/min: 200 ft AGL ≈ 4 s, 500 ft ≈ 10 s, 1,000 ft ≈ 20 s.
  The transition to the climb is ignored.
- Extra 300 AFM: 230 m to 50 ft, so the air segment is about 125 m. [D-ag input, Y arithmetic]

### 4.5 Sortie length and fleet

- **G-MIIL flight** (R0 [D], AAIB p. 5): take-off 1037, about 8 min of aerobatics, canopy event 1057:59. That is about
  **21 min** after take-off on a local aerobatic flight.
  - The fuel limits are 73 l usable for aerobatics and maximum inverted flight 4 min (S9, S14).
  - [Y] Aerobatic sorties of roughly 20–45 min are typical, but there is no fleet data.
- **Fleet:**
  - "built 20 aircraft to date" (Jan 2021). [D-ag, S19]
  - 30 US-registered aircraft (FAA AD, R0 [D]).
  - Initial placards fitted "up to EXTRA NG S/N NG064"; NG065+ new, so at least 65 serials existed by Dec 2024.
    [D-ag, S1]
  - airframer page: "Production: 5 (2026)". [D-ag, S21]
  - Snippets only [Y]: airframer "16 (2024)"; FAA registry N80NG = serial **NG080**, certificated Oct 2025; listing NG076
    (2024).
  - [Y] Estimate: about **80–90 Extra NG built** by late 2026. The serial numbers suggest this; there is no official total.

## 5. Canopy events on the Extra NG and its predecessors

Hand-written. "Mechanism-specific cause" is as stated by the investigator.

| Date | Aircraft | Phase | What happened, and mechanism-specific cause | Source / tag |
|---|---|---|---|---|
| 2013-02-07 | EA 300/L G-ZXCL (s/n 1223) | take-off, ~50 ft, 80 kt | Canopy opened and broke on the right wing; take-off abandoned. The pilot concluded he "must have omitted to lock the canopy properly" despite thorough checks | S16 p. 37 [D-ag] |
| 2016-02-18 | Extra 300 D-EFBY | just after rotation | Opened and hit the right wing; rejected take-off, overrun, fence, **fire**. Mechanism: **two handles on the left** move **two pins** into **two fuselage tenons**; a spring holds the handles at "locked". On test, the handles **stayed in an intermediate position** with the canopy closed. Cause: slight pin–tenon misalignment that the **chamfered pin tip and spring force could not overcome**; the flexible one-piece canopy may contribute. "Slight pressure" on the handles locked them. The pilot's push-up check did not reveal it | S15 pp. 3–5 [D-ag] |
| 2017-05-20 | EA 300/S N68PW | take-off roll | Canopy lifted and separated; the pilot was "fairly sure" it was not latched; no anomalies | R2 row NTSB-068 [D-ag by R2] |
| 2021-08-01 | EA 330LX F-HLIK | aerobatics, ~170 kt | Canopy blown off after the passenger's head struck it. **Not a latch event**; the frame stayed attached | S17 pp. 1–3 [D-ag] |
| 2022-03-18 | **NG** SP-HMM (NG026) | level flight ~350 km/h | Frame vibration and loss of stiffness unlocked the pawls; loose rear fitting; speed near VNE | PKBWL 2022/1097 via R0/R1 |
| 2022-04-02 | **NG** G-MIIL (NG028) | descent, 184 KIAS | AAIB: bonding defect → fatigue break-up. BFU dissents: most probably not completely locked | R0 [D] |
| 2023-08-04 | **NG** SP-HMM (NG026) | level flight after aileron rolls | Pawls **only partially engaged** (rear slider not at max aft); design "did not preclude" partial engagement; the passenger may have loosened the locks | PKBWL 2023-0061 via R0 [D] |
| 2025-10-14 | EA 300/L N300EX | seconds into the take-off roll | Opened and separated; the instructor says he checked the latch three times and thinks the **left lock did not engage its receptacle**; scuffing on the aft receptacles | blog summary of the NTSB preliminary [Y]; NTSB PDF 403 |
| 2026-08-04 | EA 300/LT N330SB | early take-off roll | The pilot did not push up on the canopy "as usual"; probable cause: failure to make sure it was locked | R5 row R5-062 [D-ag by R5] |
| undated (video posted Jun 2024) | Extra 330LX (Netherlands) | aerobatics | "The canopy locking pin had never gone into the locked position, and I failed to notice it during my checks" (pilot) | Jalopnik article [Y] |

- **EASA (AD 2025-0156):** "in most cases" the root cause of NG openings or detachments was a partially or improperly
  locked canopy (R0 [D]).
- **FAA (S18):** the AD addresses "placards/design that did not provide adequate positive canopy locking or
  confirmation". [D-ag]

**Pattern [Y].**
- Across the Extra 300 / 330 / NG family, the spring-loaded handle can **rest in a near-locked intermediate position**:
  - D-EFBY: handles part-way;
  - NG: 60 mm instead of 70 mm, the wedge on the roller.
- Pilot checks (look, push up, "checked three times") repeatedly miss it.
- On the older steel-tube Extras the canopy opens at **rotation or early in the roll**. On the NG, the partially locked
  canopy stayed shut through take-off and opened **at high speed or after aerobatics**.
  So the NG needs both a **pre-take-off** alert and **in-flight** monitoring.

---

## Design implications for the alert retrofit [Y]

1. **What to sense:** bolt depth, not "canopy down" (see R0, R8). The trip point is the change from "lead wedge on
   roller" to "roller on the top flat" (S13 Fig. 2).
2. **Where:** on the **fuselage side at the lug rollers** (fixed structure on the left sill). Reasons:
   - no wire crosses the jettisonable canopy;
   - no drilling of the bonded carbon frame (SB-NG-2-22 warnings; the G-MIIL bond defect);
   - one sensor per latch point (three lugs).
   - If only one sensor is fitted, use the **rear lug**: it is nearest the rear handle and was the "loosened rear
     fitting" on SP-HMM.
   - A handle-travel switch (60 versus 70 mm) can be a second, cheaper channel. Both handles are on one tube, so one
     switch covers both seats.
3. **Rigging per configuration:** the pawl contour changed at NG061 / AI-NG-02-23 (§1.4). The trip point must be set
   and checked per configuration. Also re-check it after any canopy removal, SB-NG-2-22 foam work or canopy
   replacement.
4. **Lamp:** a red CANOPY lamp in the rear panel, top-left by the ASI and registration placard, or under the G3X bezel.
   Both are inside the central view (§3.3). Add a G3X CAS or annunciation through a **GEA 24 discrete input**. The GEA 24
   is already in the type design (S6); the G3X discrete functions are in R7.
   - A front-cockpit repeater is optional. The front handle can be moved in flight (PKBWL finding 9).
5. **Aural:** use the GMA 245R (LH tunnel wall, S5). It is a short harness run from a sill sensor or alert unit.
   - **ALERT 1 is taken** by the GNX 375 from NG048 (S5).
   - Plan for ALERT 2 or the G3X alert audio. Confirm which alert inputs are free on each serial.
6. **Gate / trigger:**
   - The pilot's left hand stays on the throttle (S12). A throttle-position microswitch or G3X EIS rpm / MAP can arm the
     take-off alert.
   - Do not change the throttle knob shape or add a mechanical stop without checking the TCDS **ELOS on engine control
     position and shape** (S11).
7. **Electrical:**
   - 14 V nominal (12 V battery, 60 A alternator).
   - Feed from the avionics bus through a new 1–2 A breaker on the centre-console breaker panel.
   - The main board is behind the LH gear cuff (S7). Use MIL-W-22759 wire as Extra does.
8. **Take-off time budget:** with lift-off 6–8 s after brake release and 30 kt at about 3 s (§4.4), a take-off-power
   alert must sound **within about 1 s of throttle advance** to leave a reject before 30–40 kt. R8's lever-trigger
   figure of 0.35 s fits this.
   - The **best moment** is before power is applied: at the before-take-off check, where AOPA confirms "canopy latch" is
     already an item.
   - After lift-off the climb is steep (3,000 ft/min). 500 ft comes about 10 s after lift-off.
   - **In-flight monitoring** stays essential: the NG events happened at cruise or aerobatic speed, not at rotation.
9. **Recording:** log the lock state on the G3X data log (GEA 24 discrete). After G-MIIL, a log would have settled the
   AAIB–BFU dispute (R0).

## NOT VERIFIED

- The POH/AFM text: §4 checklists, §7.7 canopy, Rev. 16–18 limitations wording. Registration is required.
- AI-NG-01-23, AI-NG-02-23, ECO-NG-22-09 / 23-07: content not public.
- Jettison direction: AAIB says push forward while opening; PKBWL says the canopy moves aft on the hinge guides. Not
  resolved.
- Whether the front throttle is linked to the rear one. Knob colours and the throttle / prop / mixture identities in the
  lookbook photo.
- Which seat the lookbook photo shows (R9 infers rear). The front instrument fit (G5 versus GDU 450 by serial).
- Free GMA 245R alert inputs (ALERT 2–4) and whether the G3X alert audio is already wired to one. Whether a cockpit
  speaker exists.
- Bus voltage stated in a primary document (only "12V battery" was read). The breaker panel layout and spare positions.
- Any NG-specific take-off roll, lift-off speed in the POH, or rate of climb in the POH. The figures above are a
  journalist's flight (S14) plus an Extra 300 AFM proxy (S15).
- Total NG production. Fleet distribution by configuration (§1.4).
- Whether pilots taxi with the canopy open.
- N300EX (WPR26LA026): the NTSB text itself (403); only a secondary summary was read.
- The AAIB's "G1000" against Extra's "G3X Touch" for G-MIIL. R9 believes the AAIB is wrong; not confirmed with the AAIB.
