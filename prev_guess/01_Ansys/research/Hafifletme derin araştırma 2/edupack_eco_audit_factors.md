# Ansys Granta EduPack Eco Audit: factors and workflow for hand cross-checking (targets G-04, G-05, G-06, G-07, G-08, G-10)

Scope note (session 2026-11-01): about 30 tool calls. Source access, stated plainly:
- **Granta EduPack 2021 R1 help, "About the Eco Audit tool"** (https://support.grantadesign.com/resources/grantaedupack/2021r1/help/html/eco/eco_audit_about.htm). This page carries the factor tables. I could **not** read it in full. WebFetch failed with "unable to verify the first certificate". The in-app browser was redirected to the Ansys Help login (ansyshelp.ansys.com/public/account/secured). An archive.org copy was refused by the permission system as walled content. **Every number taken from this page is [SNIPPET]**: it comes from search-engine extracts of the page. The page is no longer public; it now sits behind an Ansys ID.
- **Ansys Help v261 (2026 R1) Eco Audit pages** (public): read in full via WebFetch, but they contain **no factor values**.
- **CES EduPack 2008 eco audit report PDF** (cse.buffalo.edu): downloaded and text-extracted locally with pypdf. [FULL]
- **"Granta EduPack for Eco Design – A White Paper"**, Ashby et al., Version 6, Oct 2021: downloaded and text-extracted locally. [FULL]
- **Pereira & Fredriksson, SEFI 2015**: downloaded and text-extracted locally. [FULL]
- The University of Trieste lecture slides (moodle2.units.it, Lezione 7, 2021-22) are image-only. No text could be extracted, so nothing is cited from them.
- Not repeated here: the Eco Audit white paper (PAPEAUEN21) content already in `design_criteria_method.md` and `use_phase_eol.md`.

---

## Q1. Use phase, mobile mode: which "Fuel and mobility type" rows exist, and with what factors?

### Takeaway
EduPack (2021 R1 help) prices each mobile-mode row as **MJ of fuel per tonne·km**. It multiplies that by an "energy equivalence" (MJ primary per MJ fuel) and a CO2 factor **per MJ**, not per t·km. The aircraft rows are:
- long-haul aircraft: 6.5 MJ/t·km;
- short-haul aircraft: 13 MJ/t·km;
- helicopter: 55 MJ/t·km.

All use 1 MJ/MJ and 0.072 kg CO2/MJ. All of this is [SNIPPET].

### Cited Findings
- Mobile mode: the vehicle is chosen from a "Fuel and mobility type" drop-down. The tool multiplies that row's energy by the product's **life distance and mass**. — [SNIPPET] [Granta EduPack 2021 R1 help, About the Eco Audit tool](https://support.grantadesign.com/resources/grantaedupack/2021r1/help/html/eco/eco_audit_about.htm), mobile-mode section. Version: EduPack 2021 R1.
- Row "Kerosene - long haul aircraft": **6.5 MJ/tonne.km | energy equivalence 1 MJ/MJ | CO2 0.072 kg/MJ**. — [SNIPPET] same page, fuel-and-mobility table.
- Row "Kerosene - helicopter": **55 MJ/tonne.km | 1 MJ/MJ | 0.072 kg/MJ**. — [SNIPPET] same page.
- Short-haul aircraft: the snippet gives "roughly 13 MJ/tonne.km" for short-haul air in the transport table, with 0.072 kg/MJ. I did **not** see the literal mobile-mode row name "Kerosene - short haul aircraft" in a snippet. — [SNIPPET] same page.
- The page's example block names a default mobile setting "Diesel - ocean shipping". Its value was not visible. — [SNIPPET] same page.
- CES EduPack 2008 mobile-mode report fields: "Fuel and Mobility type", "Energy Consumption (J/kg.m)", "CO2 Emission (kg/kg.m)", "Distance (m per day)", "Usage (days per year)", "Product Life (years)", "Total Life Distance (m)". In 2008 the CO2 was booked **per kg·m**. By 2021 R1 it is per MJ. Note that 1 J/(kg·m) = 1 MJ/(t·km). — [FULL] [CES EduPack 2008 Eco Audit Report, "Beer" (cse.buffalo.edu)](https://cse.buffalo.edu/~bina/music/Documents%20from%20old%20computer/LifePhaseReportbeer.pdf), pp. 2–3.

### Inferences
- **Hand formula, mobile mode** (assembled from the 2021 R1 snippets; not seen as one printed equation):
  - E_use [MJ] = m_part [t] × L_life [km] × e_mode [MJ/t·km] × (energy equivalence, 1 MJ/MJ);
  - CO2_use [kg] = m_part [t] × L_life [km] × e_mode × 0.072 kg/MJ.
- Implied CO2 per t·km (my arithmetic, 0.072 × e):
  - long haul: 6.5 × 0.072 = **0.468 kg CO2/t·km**;
  - short haul: 13 × 0.072 = **0.936**;
  - helicopter: 55 × 0.072 = **3.96**.
- **Average, not marginal (G-06).** The factor is a mode-average freight intensity, applied pro rata to the part's mass. It is not a marginal fuel-burn-per-added-kg factor (Breguet / BADA style). EduPack therefore treats 1 kg of bracket like 1 kg of freight. A marginal mass-to-fuel factor is a different, usually different-valued, number. If the team uses one alongside EduPack, label it "outside EduPack".
- **Pick the row by mission.** A transport-category airliner part goes in "long haul aircraft" (or short haul for regional types). A rotorcraft part goes in "helicopter", which is about 8.5× long haul per t·km. The "long haul" vs "short haul" choice alone doubles the use-phase bar.
- **Example (illustrative, not a source value).**
  - Inputs: 0.5 kg bracket, 25 years × 3,000 h/yr × 800 km/h ≈ 6.0 × 10^7 km.
  - E = 0.0005 × 6.0e7 × 6.5 ≈ **1.95 × 10^5 MJ**.
  - CO2 ≈ 1.95e5 × 0.072 ≈ **1.4 × 10^4 kg**.
  - The life inputs are assumptions. Check them against the team's own mission definition.

### Gaps
- I did not obtain the full mobile-mode table, so these rows are unseen: cars (petrol/diesel/electric), trucks, rail, ship, and the exact short-haul aircraft row. The values are in the installed EduPack: Eco Audit → Use → Mobile → Fuel and mobility type, and the Help icon on that panel. The help page needs an Ansys ID login.
- The 2026 R1 values were not seen. The 2008 and 2021 R1 air-freight values differ (Q2), so the database **does** change between releases. On competition day, read the row from the installed version.

---

## Q2. Transport phase table (truck / rail / sea / air freight)

### Takeaway
Transport is distance × product mass × MJ/t·km, then × 0.072 kg CO2/MJ for every row. The 2021 R1 rows and the 2008 rows **differ** (air freight long haul 6.5 vs 8.3 MJ/t·km), so the version matters.

### Cited Findings
- Method: transport energy = energy per unit mass·distance × distance × product mass. CO2 = that energy × the source CO2 footprint. The table is headed "Transport type | Transport energy (MJ/tonne.km) | CO2 footprint by source (kg/MJ)". — [SNIPPET] [EduPack 2021 R1 help, About the Eco Audit tool](https://support.grantadesign.com/resources/grantaedupack/2021r1/help/html/eco/eco_audit_about.htm)
- 2021 R1 rows (all [SNIPPET], same page), each at 0.072 kg/MJ:

  | Row | MJ/tonne.km |
  |---|---|
  | Ocean freight | 0.18 |
  | Coastal freight | 0.27 |
  | Rail freight | 0.35 |
  | 32 tonne (4 axle) truck | 0.94 |
  | 14 tonne (2 axle) truck | 1.5 |
  | Air freight – long haul | 6.5 |
  | Air freight – short haul | 13 |
  | Helicopter | 55 |

- **Internal conflict in the 2021 R1 page:** a second, diesel-specific table on the same page gives the 32 t truck as **0.84** MJ/tonne.km rather than 0.94. — [SNIPPET] same page. Unresolved.
- CES EduPack 2008 report rows (text-extracted from the PDF; [FULL], p. 2):
  - "32 tonne truck" **0.46 J/kg.m** (= 0.46 MJ/t·km);
  - "Air freight - long haul" **8.3 J/kg.m** (= 8.3 MJ/t·km).

  Arithmetic check in the report: 0.6 kg × 6.1e6 m × 8.3 = 3.0e7 J, which matches the printed 3.1e7 J. — [CES EduPack 2008 report](https://cse.buffalo.edu/~bina/music/Documents%20from%20old%20computer/LifePhaseReportbeer.pdf)
- Transport-type names used in a 2015 Granta paper: "14 tonne truck", "Light goods vehicle". No values given. — [FULL] [Pereira & Fredriksson, SEFI 2015, "Teaching Circularity using CES EduPack", Table 3, p. 4](https://www.sefi.be/wp-content/uploads/2017/09/56147.-A.PEREIRA.pdf)
- Already in the earlier notes: the white-paper PET example uses a 14 t truck at 0.87 MJ/t·km and 0.062 kg CO2/t·km. That **conflicts** with the 1.5 MJ/t·km "14 tonne (2 axle)" snippet above. It may be a different row or version (the Ansys help exercise names a "7.5-16 tonne truck"). Unresolved.

### Inferences
- Hand check: transport = m [t] × d [km] × e [MJ/t·km]. A 0.5 kg part air-freighted long haul for 10,000 km costs 0.0005 × 1e4 × 6.5 = 32.5 MJ and ≈ 2.3 kg CO2. That is negligible next to the use phase in Q1.
- The CO2/energy ratio in the white-paper truck example is 0.062 / 0.87 ≈ 0.071 kg/MJ. This agrees with the 0.072 kg/MJ snippet to rounding. That is weak cross-support for the per-MJ convention.

### Gaps
- Light goods vehicle, 7.5–16 t truck, barge, and the electric options: values not seen.
- The 0.94 vs 0.84 (32 t truck) and 0.87 vs 1.5 (14 t truck) conflicts are unresolved. Read the values in the installed version.

---

## Q3. How scrap / "% removed" is booked, and the effect on the material phase (buy-to-fly, G-05)

### Takeaway
The public 2026 R1 help confirms these input fields:
- per component: material, recycled content, mass, primary process, secondary process with "% removed", EoL option, % recovered;
- a separate joining-and-finishing list.

I found **no public text** saying whether "% removed" raises the material-phase mass. Treat the buy-to-fly booking as **unverified**.

### Cited Findings
- Component inputs: quantity, name, material, recycled content, mass, primary process, secondary process, "% removed", end-of-life option, % recovered. Secondary processes are optional and carry a "% removed" value. The primary-process choices are limited by the selected material and do not apply to reused parts. — [FULL] [Ansys Help v261 (2026 R1), Creating an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/eco_audit_tool.html)
- Recycled-content options: Virgin (0 %), Typical (material dependent), Reused part, or a custom value. — [FULL] same page.
- A custom process needs only "Process name", "Process energy" and "Climate change (CO2-eq)". It applies only to the material it was created for, and it is saved in the .prd. The help page states no unit and no per-kg-processed vs per-kg-removed basis. — [FULL] [Ansys Help v261, Defining a custom process for an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/defining_process_eco.html)
- The 2008 report books manufacture as **processing energy (J/kg) × component mass**. Example: "Forging, rolling" 2.4e6 J/kg × 0.005 kg = 1.2e4 J; "Glass molding" 8.6e6 J/kg × 0.23 kg = 1.9e6 J. Material is likewise booked as primary production energy × component mass. That edition had no "% removed" field. — [FULL] [CES EduPack 2008 report, p. 2](https://cse.buffalo.edu/~bina/music/Documents%20from%20old%20computer/LifePhaseReportbeer.pdf)
- Ashby (2021): "In-house scrap, generated at the point of production or manufacture is localized and is already recycled efficiently (near 100% recovery)". This is context for why removed swarf may be treated as low-burden. — [FULL] [Granta EduPack for Eco Design – A White Paper, v6 Oct 2021, p. 12](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-design-white-paper-PAPECOEN21.pdf)

### Inferences
- **UNVERIFIED (memory): how "% removed" probably works.** In EduPack versions since about 2012, entering a secondary process such as "Machining (fine)" with X % removed is thought to do two things:
  - scale the **material phase** up to the pre-machining stock mass, m/(1 − X);
  - book the **machining energy on the removed mass**.

  If true, a buy-to-fly of BTF = 1/(1 − X) lands in the **material** bar (X = 90 % → BTF 10). This is memory only. It has not been checked against help text this session.
- **Two-run test on competition day.** In the installed tool, audit one component twice: once with 0 % removed and once with 50 % removed. Then compare:
  - if the Material bar doubles, stock mass is booked in the material phase;
  - if only the Manufacture bar moves, scrap sits in manufacture.

  This takes one minute and closes G-05 with output as evidence.
- If "% removed" turns out not to scale the material bar, enter the **stock (buy) mass** as the component mass and the finished mass separately for the use phase. Mobile mode uses product mass, so keep a separate audit or a correction note.

### Gaps
- No public primary text on the "% removed" arithmetic was found. The 2021 R1 help page (behind login) probably has it in the Manufacture section.

---

## Q4. AM and machining rows (G-04)

### Takeaway
No public source this session listed EduPack's primary-process rows for additive manufacturing, nor the machining energy values. The process list is material-dependent and must be read from the installed tool.

### Cited Findings
- The primary-process list is restricted by the chosen material. — [FULL] [Ansys Help v261, Creating an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/eco_audit_tool.html)
- Order-of-magnitude anchors at 30 % efficiency (Ashby 2021, p. 11) — [FULL] [Eco Design White Paper v6](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-design-white-paper-PAPECOEN21.pdf):
  - melting metals and alloys: 0.4–4 MJ/kg;
  - vaporisation (PVD): 3–30 MJ/kg;
  - deformation at 90 % strain: 0.01–1 MJ/kg.

  "Casting or deformation require processing energies that are small compared to the embodied energy." This is a physics floor, not EduPack's process records.
- Same white paper: embodied production energies "generally lie in the range 50–500 MJ/kg" and recycling energies typically 10–100 MJ/kg (p. 10). — [FULL] same source.

### Inferences
- The Ashby melting floor (0.4–4 MJ/kg) is one to two orders of magnitude below the 60–160 MJ/kg PBF electricity in the earlier notes. That is consistent with laser and atmosphere overheads dominating real AM energy. It is not evidence of EduPack's AM value.
- If no AM row exists for the chosen alloy, use the documented "Add custom process" (name, process energy, CO2-eq). Cite the external source of the AM energy in the report.

### Gaps
- Not found: AM row names (e.g. "Additive manufacturing – powder bed fusion"), machining row values ("Machining – fine/coarse"), autoclave/prepreg rows. The 2026 R1 process list is not public.

---

## Q5. Fuel CO2 factor (G-07), grid factor (G-08), EoL options and EoL potential (G-10)

### Takeaway
EduPack books fuel CO2 **per MJ**, at 0.072 kg CO2/MJ for kerosene and diesel transport rows [SNIPPET]. It does not book per kg of fuel. The EoL options are listed in the current help [FULL]. The numeric EoL potential per material was not found.

### Cited Findings
- CO2 footprint 0.072 kg/MJ on the kerosene aircraft and helicopter rows, and on every transport row. — [SNIPPET] [EduPack 2021 R1 help](https://support.grantadesign.com/resources/grantaedupack/2021r1/help/html/eco/eco_audit_about.htm)
- EoL options in 2026 R1: **Landfill, Combust, Downcycle, Recycle, Re-manufacture, Reuse, None**. "% recovered" is defined as "The amount of the material (if any) that can be recovered when the product reaches end of life." — [FULL] [Ansys Help v261, Creating an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/eco_audit_tool.html)
- The 2021 white paper (already noted) listed five options. The 2026 R1 tool adds **Downcycle, Re-manufacture and None**: seven entries.
- Granta's definitions of the circular options — [FULL] [Pereira & Fredriksson, SEFI 2015, p. 3](https://www.sefi.be/wp-content/uploads/2017/09/56147.-A.PEREIRA.pdf):
  - reuse: the product is reintroduced in its original form after minimal maintenance;
  - remanufacture: disassembly and return to working condition, with the energy of replaced parts counted;
  - recycling: recovered materials feed back as crude feedstock, and recycling-process energy and CO2 are counted.

  The paper's Circularity Audit uses the "advanced version" of the Eco Audit.
- Ashby 2021: continuous-fibre composites "cannot be re-separated economically into fiber and polymer … though they can be chopped and used as fillers". This supports **Downcycle** (not Recycle) as the EoL option for CFRP. — [FULL] [Eco Design White Paper v6, p. 12](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-design-white-paper-PAPECOEN21.pdf)
- The 2026 R1 Use step asks for the **country of use**. The static-mode electricity CO2 therefore comes from a country mix. — [FULL] [Ansys Help v261](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/eco_audit_tool.html)
- The 2008 report shows a static-mode "CO2 Emission (kg/J)" of 4.6e-08, i.e. 0.166 kg/kWh, for "Electric to mechanical". The grid region is not stated in the extracted text. — [FULL] [CES EduPack 2008 report, p. 2](https://cse.buffalo.edu/~bina/music/Documents%20from%20old%20computer/LifePhaseReportbeer.pdf)

### Inferences
- **G-07, per-kg equivalent.** 0.072 kg/MJ × LHV of Jet-A ≈ 43 MJ/kg ≈ **3.1 kg CO2/kg fuel**. Both the LHV (43 MJ/kg) and the commonly quoted 3.16 kg/kg are **UNVERIFIED (memory)**. The 3.1 is my arithmetic from a [SNIPPET] factor. For a hand cross-check of an EduPack number, use EduPack's own route (MJ × 0.072), not 3.16, so the two agree.
- "Energy equivalence 1 MJ/MJ" means fuel energy is counted at face value, with no upstream refinery multiplier on the energy bar. This is inferred from the column name.
- **G-08.** The AM electricity CO2 depends on the country chosen in EduPack. A custom AM process carries its own CO2-eq value, so state which grid factor was used to derive it.
- **EoL potential.** Credit comes from recycled content at the start of life, and EoL is shown as a separate hatched potential bar (already noted). The size of the potential depends on the option and on % recovered. The per-material formula was not found publicly.

### Gaps
- Not found publicly: the EoL-potential formula and per-option energy/CO2 values per material, and the country electricity factors in 2026 R1.

---

## Q6. Eco Audit workflow as in the tool, and the "Material selection and eco analysis for chassis" course

### Takeaway
The tool order is:
1. Product name.
2. BoM rows (material, recycled content, mass, primary process, secondary process + % removed, EoL option, % recovered).
3. Joining & finishing.
4. Transport stages.
5. Use (product life, country, static and/or mobile).
6. Report (Summary chart with energy/CO2 toggle, Detailed report, export to PDF/Word, saved as .prd).

No public description of the chassis course was found.

### Cited Findings
- Steps (2026 R1) — [FULL] [Ansys Help v261, Creating an Eco Audit project](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/eco_audit_tool.html):
  1. Open Eco Audit from the toolbar. Every stage is optional.
  2. Enter the product name.
  3. Enter the component rows.
  4. Enter joining and finishing processes (name, process type, amount, unit).
  5. Enter transport stages (name, transport type, distance with units).
  6. Enter Use: country of use plus energy use or further transport over the product's life.
  7. Create the Summary chart or the Detailed report.
  8. Save as a .prd. Eco Audit projects are separate from .ces selection projects.
- Exercise 20 (2026 R1): in the BoM step, enter material, manufacture and EoL. Transport runs "from site of manufacture to point of sale". Product life and country follow. Static-mode energy comes next, and **Mobile Mode only if the product is part of a vehicle**. The Summary chart toggles energy vs Climate change (CO2-eq). Clicking a phase shows reduction strategies. The Detailed report can be saved as PDF or Word. — [FULL] [Ansys Help v261, Exercise 20: Define and audit a product](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/define_audit_product.html)
- Exercise sample: "Level 2 - Bottle PET.prd"; a 7.5-16 tonne truck over 550 km. "Enhanced Eco Audit" adds restricted-substance warnings, cost analysis and secondary processes. — [FULL] [Ansys Help v261, Eco Audit tool exercises](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Edu_Pack_Help/sel_edu/eco_tool_exercises.html)

### Inferences
- **Competition-day hand-check recipe.** Per component:
  - Material = m_buy × embodied energy;
  - Manufacture = m × process energy, scrap per the Q3 test;
  - Transport = m × d × e_mode;
  - Use (mobile) = m × L × e_mode, CO2 = MJ × 0.072;
  - EoL = shown separately.

  Read each factor from the installed EduPack and screenshot it. That gives output evidence even where the public help is walled.
- "Secondary process / % removed" appears in the 2026 R1 standard component fields. The exercises page calls secondary processes an "Enhanced Eco Audit" option. Check which edition (Level 2 / Level 3 / Aerospace) the competition licence has.

### Gaps
- No public listing or syllabus was found for "Material selection and eco analysis for chassis". Searches returned only general Ansys education-resource pages.
- The 2021 R1 help page that holds the factor tables now needs an Ansys ID. Its full text could not be read, so its values stay [SNIPPET].
