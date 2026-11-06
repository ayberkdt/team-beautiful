# R4 — Environmental qualification (RTCA DO-160G) and light-aircraft wiring practice

- read by: subagent R4
- date read: 2026-11-04
- Tags: **[D-ag]** = read directly from the source in this session. **[Y]** = secondary source, or R4's interpretation.
- Local copies: `D:\tmp_ideathon\easa\dl\hf\`
- **RTCA DO-160G itself was NOT read.** It is paywalled (RTCA). Section titles below come from FAA AC 21-16G. Category examples come from a qualified aerospace sensor's datasheet. No category definitions, levels or curves are given from DO-160G itself.

## Sources

| ID | Document | Edition / date | URL |
|---|---|---|---|
| E1 | FAA AC 21-16G, RTCA Document DO-160 versions D, E, F and G | 06/22/2011 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_21-16G.pdf |
| E2 | Honeywell GAPS & HAPS Series Aerospace Proximity Sensors datasheet, Table 2 | 000843-2-EN, 04/21 | https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/en-us/products/sensors/motion-position-sensors/common/documents/sps-siot-haps-gaps-combined-datasheet-000843-1-en-ciid-180941.pdf |
| E3 | Chroma, "RTCA DO-160G Power Group Supports Test Items" (test-equipment brochure) | undated | https://chromausa.com/pdf/RTCA%20DO-160G.pdf |
| E4 | AE Techron webinar slides, DO-160 Sections 16, 18, 19 | ©2025 | https://aetechron.com/wp-content/uploads/2025/09/DO-160-Webinar-For-Download.pdf |
| E5 | Wikipedia, "DO-160" | read 2026-11-04 | https://en.wikipedia.org/wiki/DO-160 |
| W1 | FAA AC 43.13-1B CHG 1, ch. 11 Aircraft Electrical Systems | 9/8/98; CHG 1 9/27/01 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf |
| X1 | EASA TCDS EASA.A.620 EXTRA NG | Issue 04, 02 Dec 2020 | https://www.easa.europa.eu/en/downloads/104842/en |
| X2 | Extra Aircraft, "EXTRA NG Lookbook" | ©2019 | https://extraaircraft.com/wp-content/uploads/2024/01/EXTRA-NG_Lookbook.pdf |

## 1. DO-160 status and section list

### Status
- E1 §1a [D-ag]: lists DO-160D (27 Jul 1997), E (20 Dec 2005), F (6 Dec 2007) and **G (8 Dec 2010)** as acceptable. The FAA "strongly encourages" G for new articles.
- E5 [Y]: DO-160G **Change 1** is dated 16 Dec 2014. A DO-160H was reported "under development" (vendor FAQ, not verified).
- E1 §7e (p.4) [D-ag]: some sections (e.g. waterproofness, sand and dust, salt fog) "may not be applicable" depending on installed location. **The installer must determine which sections and categories apply.**
- E1 §7b (p.3) [D-ag]: installers compare the manufacturer's Environmental Qualification Form (EQF) with their installation.
- E1 §7f–g (p.4) [D-ag]: for HIRF (§23.1308) use DO-160F or G (see AC 20-158). For lightning use DO-160D or later (see AC 20-136).

### Section titles (E1 Appendix 1) [D-ag], with R4's applicability call [Y]

Column key:
- **Annunc.** = panel annunciator / alert unit in the cockpit.
- **Canopy sensor** = sensor on the canopy frame or sill.
- "Example cat." = the category the Honeywell GAPS aerospace proximity sensor is qualified to (E2 Table 2, p.4) [D-ag]. **These are a reference point only, not a recommendation.** GAPS targets landing gear, doors and other harsh zones.

| § | Title (E1) | Annunc. | Canopy sensor | Example cat. (GAPS, E2) | R4 rationale [Y] |
|---|---|---|---|---|---|
| 4 | Temperature and Altitude | yes | yes | D3 | Unpressurised cockpit; X1 gives max operating altitude 3,048 m / 10,000 ft |
| 5 | Temperature Variation | yes | yes | S2 | Ramp sun soak, then climb |
| 6 | Humidity | yes | yes | C | Canopy seal area sees condensation |
| 7 | Operational Shocks and Crash Safety | yes | yes | B | ±10 g aerobatic (X1 §A.III.6). Crash safety: a unit must not come loose in the cockpit |
| 8 | Vibration | yes | yes | R | Reciprocating engine + propeller; the curve choice needs DO-160G Table 8-1 (not read) |
| 9 | Explosion Proofness | no | no | E&H | No flammable-vapour zone in the cockpit (assumption) |
| 10 | Waterproofness | optional | **yes** | R | Rain enters the frame with the canopy open |
| 11 | Fluids Susceptibility | optional | yes | F | Cleaning fluids, canopy polish |
| 12 | Sand and Dust | no | optional | D | Grass strips; frame sill collects dirt |
| 13 | Fungus Resistance | optional | optional | F | Material choice can cover it (assumption) |
| 14 | Salt Fog | no | optional | T | Coastal basing only |
| 15 | Magnetic Effect | **yes** | **yes** | A | Compass deviation. **Critical if a magnet-actuated (reed or Hall) target is used near the compass** |
| 16 | Power Input | yes | yes (if powered) | A | 14 V system, see §2. E3 lists only **B14** as the DO-160G test set-up at 14 V DC (A28/B28/Z28 at 28 V) [Y] |
| 17 | Voltage Spike | yes | yes (if powered) | A | Starter and alternator transients |
| 18 | Audio Frequency Conducted Susceptibility | yes | yes (if powered) | Z | Alternator ripple |
| 19 | Induced Signal Susceptibility | yes | yes | CWE | Long harness from frame to panel. E4: four categories A, B, C, Z [Y] |
| 20 | RF Susceptibility (Radiated and Conducted) | yes | yes | F radiated / W conducted | HIRF (E1 §7f) |
| 21 | Emission of RF Energy | yes | yes (if active) | M | Must not interfere with COM/GPS; E1 §6f recommends cat. P or Q near GPS antennas |
| 22 | Lightning Induced Transient Susceptibility | yes | yes | B3K3L3 | Carbon fuselage gives poor shielding (assumption; the X2 lookbook says "carbon monocoque" fuselage) |
| 23 | Lightning Direct Effects | no | maybe | — | Only if the sensor is externally exposed |
| 24 | Icing | no | optional | A | Frame exposed when open |
| 25 | Electrostatic Discharge | yes | yes | A | Pilot handling; canopy acrylic charging |
| 26 | Fire, Flammability | yes | yes | — | Cockpit material flammability (CS 23.853 not read) |

## 2. Extra NG electrical system and wiring practice

### Extra NG data
- X2 p.2 [D-ag]: "Electric starter", "60 Amp lightweight alternator", "12V battery".
  - R4 inference [Y]: a 12 V battery with an alternator means a nominal **14 V DC bus**, i.e. AC 43.13-1B "14 V nominal" and DO-160G §16 14 V DC equipment.
  - **Not verified against the Extra NG AMM or POH** (not accessible). The Scribd "AMM 24-00" was not opened.
- X1 [D-ag]:
  - Certification basis CS-23 Amdt 4.
  - Load factors: Normal +6/−3 g at MTOW 950 kg; ACRO I ±10 g at 820 kg; ACRO II ±8 g at 900 kg; ACRO III ±6 g at 950 kg (§A.III.6).
  - Max operating altitude 10,000 ft.
  - Engine Textron-Lycoming AEIO-580-B1A.
  - The TCDS gives no electrical data.

### AC 43.13-1B (W1) [D-ag]
- **§11-47 (p.11-15):** every wire needs circuit protection. Put the protector as close as possible to the bus. SAE ARP 1199 is cited for recommended practice.
- **§11-48 (p.11-15):** a breaker must open before the wire rating or the cumulative load rating is exceeded, whichever is lowest, and before any downstream component can overheat.
- **Table 11-3 (p.11-15), DC wire vs circuit protector.** Basis: bundles at 135 °F ambient and ≤30,000 ft; MIL-W-5088 wire; MIL-C-5809 breakers.
  - AWG 22: CB 5 A, fuse 5 A
  - AWG 20: CB 7.5 A, fuse 5 A
  - AWG 18: CB 10 A, fuse 10 A
  - AWG 16: CB 15 A, fuse 10 A
  - AWG 14: CB 20 A, fuse 15 A
  - AWG 12: CB 30 A, fuse 20 A
  - AWG 10: CB 40 A, fuse 30 A
- **§11-49:** the chart "is conservative for all ordinary aircraft electrical installations".
- **§11-50 (p.11-15):** breakers must be trip-free. Automatic-reset breakers are not recommended.
- **§11-51 (p.11-15/16):** breakers protect the wire, not black boxes. Using a breaker as a switch is not recommended.
- **§11-53 (p.11-16/17):**
  - Use aircraft-service switches where a malfunction can be hazardous.
  - (a) A spring-loaded switch can fail internally and "remain closed".
  - (c) Proximity switches are usually solid-state, "usually rated 0.5 amps or less".
  - (d)(1) Lamp inrush can be 15× the continuous current.
  - (g) Silver contacts are not for loads below 8 V or below 0.5 A unless rated for low energy. Typical logic loads are 0.5–28 V at <0.5 A.
- **Table 11-4 (p.11-17), switch derating factors.** 12 VDC: lamp 5, inductive 2, resistive 1, motor 2. 28 VDC: lamp 8, inductive 4, resistive 2, motor 3.
- **§11-66a (p.11-21):** wires smaller than #20 need extra mechanical care (clamps, grouping with at least three other wires, support at terminations). Wire with fewer than 19 strands "must not be used".
- **§11-66b and Table 11-6 (p.11-21):** main power feeder drop ≤2 % of regulated voltage. Bus-to-equipment drop at **14 V nominal: 0.5 V continuous, 1 V intermittent**; at 28 V: 1 V and 2 V.
- **§11-66c (p.11-21):** treating structure return as negligible assumes adequate bonding or a dedicated return path.
  - R4 note [Y]: the Extra NG fuselage is carbon (X2). Plan a **dedicated ground wire** for the sensor and annunciator, not a structure return.

### Implications for the design (R4 [Y])
- A canopy-sensor and annunciator loop draws well under 1 A: an LED annunciator is tens of mA, and the GAPS sensor draws <10 mA (E2). On Table 11-3 this fits 22 AWG on a 5 A breaker, but §11-66a's mechanical cautions for <#20 apply on a canopy hinge or flex loop. **Prefer 20 AWG in the flex zone** (judgement).
- Use a gold-contact or low-energy-rated microswitch (W1 §11-53g).
- Put the alert on its own breaker, or a shared avionics breaker. A1 §12e (AC 25.1322-1) says pulling a breaker is not an acceptable primary way to silence a false alert, so give a protected acknowledge or suppress control.

## NOT VERIFIED

1. DO-160G text: all category definitions, Table 8-1 vibration curves for reciprocating-engine fixed-wing aircraft, Section 4 temperature limits, Section 16 14 V limits. The Ametek-manual 14 V figures (11.0 V / 12.5 V) seen in a search snippet were **not read**.
2. DO-357 (DO-160G User Guide supplement): not read. One test-lab page claimed DO-160G "cannot be read without" DO-357.
3. DO-160H release status.
4. Extra NG bus voltage, breaker panel, wire gauges: no AMM, POH or wiring diagram read. "14 V" is an inference from "12V battery".
5. AC 43.13-1B Table 11-3 rows for AWG 8 and larger: present on p.11-15 but not transcribed here (not needed).
6. SAE ARP 1199, MIL-W-5088 / SAE AS50881 wiring specs: not read.
7. Whether EASA would require DO-160 qualification for a CS-23 minor change or STC alert unit (vs CS 23.1309 / 23.1431 analysis only): not verified.
