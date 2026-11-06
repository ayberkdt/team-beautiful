# Lighten the bracket, then defend every number

**Bottom line.** The Ansys challenge comes down to about 25 decisions, and three of them drive almost the whole result. **(1) Final mass multiplied by lifetime distance** settles the eco audit. In ORNL's topology-optimised Ti bracket, the use phase is **98.3 %** of the machined part's life-cycle energy and manufacturing is about **0.07 %** (shares derived from Table 7 of [ORNL/TM-2014/93](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf), [FULL TEXT]; the note rounds the second figure to 0.06 %). **(2) The buy-to-fly ratio** settles "machined vs AM". With ORNL's Ashby-based inputs, EBM beats machining cradle-to-gate whenever the machined ratio is above **≈1.8** (derived), and real machined brackets sit at **8:1 to 33:1** (same source). **(3) The certification factor chain** sets how much material the topology run may remove: ultimate load is **1.5 × limit** ([14 CFR 25.303](https://www.ecfr.gov/current/title-14/section-25.303), [FULL]), a fitting carries **≥1.15** on top ([§25.625](https://www.ecfr.gov/current/title-14/section-25.625), [FULL]), and only the highest special factor applies ([§25.619](https://www.ecfr.gov/current/title-14/section-25.619), [FULL]). For a flight part the defensible mass claim is **30–50 %**. The famous 80–84 % GE bracket figure comes from an over-designed service bracket, and its two sources disagree on the baseline mass. Most of the eco numbers that look precise are not. Primary aluminium ranges from **4.5 to 22 kg CO2e/kg** depending on the smelter's grid ([IAI](https://international-aluminium.org/landing/aluminium-carbon-footprint-faqs/), [FULL-FETCH]). The autoclave energy differs **≈17×** between Ashby (200 MJ/kg) and Cranfield's curing value (11.8 MJ/kg). Per-alloy values, prices, mechanical properties and EduPack's own aircraft use-phase factor all **must be read from EduPack on the day**. This report gives the team a sourced default for every decision, the spread around it, and the sentence to say when the jury pushes back.

---

## How to read the tags

Every number keeps the **exact tag given in the source note**. No tag has been upgraded. Arithmetic done for this report is tagged **[derived]**; it inherits the weakest tag among its inputs and is logged in the scratchpad (`derived.py`, `derived_out.txt`). Where the notes themselves drew a conclusion, the tag is **[note inference]**. Values that were read from this repository's code or brief in this session are tagged **[K]**.

| Note file | "Read in full" tag(s) | Weaker tags |
|---|---|---|
| `material_eco_data.md` | [FULL-PDF] = PDF text extracted and read; [FULL-FETCH] = whole page via fetch summariser | [SNIPPET], UNVERIFIED (memory) |
| `manufacturing_lca.md` | [FULL TEXT] | [SNIPPET], [UNVERIFIED (memory)] |
| `design_criteria_method.md` | [FULL] | [SNIPPET], UNVERIFIED (memory) |
| `topology_dfam_cases.md` | [FULL-SELF] = PDF read; [FULL-WF] = WebFetch summary with quotes | [SNIPPET], UNVERIFIED (memory) |
| `use_phase_eol.md` | [FULL TEXT]; [PAGE] = fetched page (summarised) | [SNIPPET], UNVERIFIED (memory) |

Treat [FULL-FETCH], [FULL-WF] and [PAGE] as one notch below a self-read PDF, because a summariser model sat between the source and the note. **UNVERIFIED (memory)** items appear here only as gaps or labelled placeholders. None of them should be cited to the jury.

---

## The 25 decisions in workflow order

D-01 to D-06 keep the numbering from the request. The remaining decisions follow the five-hour F7 recipe in `prev_guess/01_Ansys/docs/10_synopsys_2026_brief.md` §6.

| ID | Decision | Default | F7 slot | Evidence strength |
|---|---|---|---|---|
| D-25 | Toolchain if EduPack or Discovery is missing | Mechanical TO + `aerokit` with stated factors | before 0:00 | [K] / brief [D] |
| D-04 | Safety / fitting / process factors | 1.5 × 1.15 = **1.725 × limit**; A-basis if single load path | 0:00–0:20 | strong ([FULL] eCFR) |
| D-12 | Load cases and boundary conditions | ≥ 3 independent cases, rigid bolts, protected rings | 0:00–0:20 | medium |
| D-07 | Ashby translation and index | Run `beam_stiff` **and** `beam_strong`/`tie_strong` | 0:20–0:40 | [K]; method snippets only |
| D-01 | Material family, stiffness-limited bracket | Al alloy; Ti-6Al-4V when strength-limited, hot, or touching CFRP | 0:20–0:40 | medium |
| D-08 | Alloy within family | 7xxx for strength/compression; 2xxx for tension/damage tolerance | 0:20–0:40 | weak ([SNIPPET] patents) |
| D-09 | Mass vs CO2 vs cost trade | Penalty function with a stated exchange constant | 0:20–0:40 | [SNIPPET] + [FULL-SELF] |
| D-16 | Interfaces: galvanic, Mg in cabin | Isolate Al from CFRP; no Mg for cabin structure | 0:20–0:40 | [FULL] / [SNIPPET] |
| D-02 | Machined vs AM route | AM if machined BTF > ≈2 and the shape is organic | 0:40–2:00 | strong ([FULL TEXT] ORNL) |
| D-03 | Volume/mass retain target | Sweep 50 / 35 / 25 %, defined as a Range | 0:40–2:00 | [FULL-WF] Ansys help |
| D-11 | TO manufacturing constraint and mesh | Overhang 45° **or** member size ≥ 2.5 h, never both | 0:40–2:00 | [FULL-WF] Ansys help |
| D-13 | Reconstruction and validation | Validation solve on all cases; re-mesh if within 5 % | 2:00–2:45 | [FULL-SELF] + [FULL-WF] |
| D-14 | Fatigue and AM post-processing | HIP + machine fatigue-critical faces | 2:00–2:45 | [FULL] review |
| D-15 | Composite criteria (if CFRP) | BVID at ultimate; strain cut-off from data, not folklore | 2:00–2:45 | [FULL] AC 20-107B |
| D-10 | Buy-to-fly value | Compute from own stock block ÷ part mass | 2:45–3:30 | [FULL TEXT] ranges |
| D-17 | Primary-material eco data and grid | EduPack record + low/high grid sensitivity | 2:45–3:30 | [FULL-PDF]/[FULL-FETCH] |
| D-18 | Recycled content at start of life | EduPack virgin (or "current supply"), stated | 2:45–3:30 | [FULL] white paper |
| D-19 | Manufacture-phase energy values | EduPack process rows; ORNL values as cross-check | 2:45–3:30 | [FULL TEXT] |
| D-05 | Use-phase fuel-per-kg factor | Steinegger per-trip marginal factor ↔ `aerokit` f/(1−f) | 2:45–3:30 | [FULL TEXT] (non-peer-reviewed) |
| D-20 | Lifetime utilisation | ORNL 15 yr (30.6 M km) base; 150 M km as upper case | 2:45–3:30 | [FULL TEXT] |
| D-21 | CO2 per kg of fuel | 3.16 (placeholder; confirm in EduPack) | 2:45–3:30 | UNVERIFIED (memory) |
| D-22 | Transport phase | Include at the EduPack default; state that it is < 1 % | 2:45–3:30 | [FULL TEXT] |
| D-06 | End-of-life credit method | EduPack recycled-content method; EoL potential as a separate bar | 2:45–3:30 | [FULL] white paper |
| D-23 | Headline claim and payback | % mass + held constraint + payback in flights | 3:30–4:30 | [FULL TEXT] Scelsi |
| D-24 | Jury deliverables | Retain sweep curve, before/after table, phase bars | 3:30–4:30 | [note inference] |

---

## Requested decisions D-01 to D-06

### D-01 · Material family for a stiffness-limited bracket

**Question.** Al, Ti, steel, Mg or CFRP for a bracket whose sizing load is a deflection limit? **Default.** An aluminium alloy. Use Ti-6Al-4V when the part is strength-limited, runs hot, or touches CFRP. Keep CFRP only when the shape can be laminated. A topology-optimised organic shape usually cannot be, which is an inference.

| Evidence | Value | Source | Tag |
|---|---|---|---|
| aerokit stiff-panel ranking (relative mass, AA typical values) | 6061-T6 1.00 · 2024-T351 1.01 · 7075-T6 1.03 · Ti-6Al-4V 1.40 | `prev_guess/01_Ansys/docs/10_synopsys_2026_brief.md` §5 | [K] |
| aerokit strong-tie ranking | Ti-6Al-4V 1.00 · 7075-T6 1.04 · 2024-T351 1.60 · 6061-T6 1.83 | same | [K] |
| aerokit strong-beam ranking | 7075-T6 1.00 · Ti-6Al-4V 1.13 · 2024-T351 1.33 · 6061-T6 1.43 | same | [K] |
| Primary CO2, Al vs Ti (Ashby 2nd ed.) | Al 12 kg/kg; Ti alloys 46.5 kg/kg (≈ 3.9× Al) | [Useful Numbers (Ashby repro.)](https://Polybags.Co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf) | [FULL-PDF] |
| Ti-6Al-4V ingot, grid sensitivity | 37.3 (Chinese grid) / 16.1 (hydro) kg CO2e/kg | [Lessard et al. 2025 SI, Table S-2](https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs40831-025-01258-1/MediaObjects/40831_2025_1258_MOESM1_ESM.pdf) | [FULL-PDF] |
| CFRP must be isolated from Al | "glass plies may be used to isolate carbon composite layers from aluminum" | [FAA AC 20-107B §6.e](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf) | [FULL] |
| Mg in cabins | AS8049 ban replaced by the FTH Ch. 25 oil-burner test; EASA 2015 special conditions cover **seat** parts only | [Canari, FAA Materials WG 2017](https://www.fire.tc.faa.gov/pdf/materials/Oct17Meeting/Canari-1017-EASACRI.pdf) | [SNIPPET] |
| Mechanical properties (E, σy, ρ) in the notes' table | — | `material_eco_data.md` | UNVERIFIED (memory): **do not use** |

**Deviate when.** (a) The validation run shows stress, not deflection, governs. Switch to `beam_strong`/`tie_strong`; Ti and 7075 then lead. (b) The bracket fastens to a CFRP structure. Ti avoids the isolation-layer problem, although Ti–CFRP compatibility itself has **no source** in the notes. (c) The part sits near the engine and is hot. Temperature data are not in the notes, so read them from EduPack. (d) The brief names a cabin part. Drop Mg unless it is a seat component.

**Say to the jury.** "We let the governing constraint pick the index. For our deflection-limited case the aluminium alloys sit within 3 % of each other and titanium is 40 % heavier, so we chose aluminium. Titanium also carries about four times the CO2 per kilogram in Ashby's data."

### D-02 · Machined vs additive route

**Question.** Machine from plate, billet or forging, or print by L-PBF/EBM (or WAAM)? **Default.** If the topology result is organic, print it, and calculate the machined comparison from the team's own stock block. AM wins cradle-to-gate once the machined BTF exceeds ≈2. Its manufacturing-energy penalty disappears inside the use phase either way.

| Evidence | Value | Source | Tag |
|---|---|---|---|
| ORNL Case 1 (same geometry, Ti cabin bracket) | BTF 33:1 machined vs 1.5:1 EBM; life-cycle saving ≈5.9 %, almost all from the material phase | [ORNL/TM-2014/93 pp. 54–56](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf) | [FULL TEXT] |
| ORNL Case 2 (topology-optimised, 65 % lighter) | BTF 8:1 vs 1.5:1; manufacturing energy CM ≈69.1 MJ vs AM ≈69.5 MJ, **essentially equal**; total saving ≈65 % | ORNL pp. 57–58, Table 7 | [FULL TEXT] |
| ORNL Case 2 phase shares (CM part) | use 98.3 %; manufacturing 0.065 % | ORNL Table 7 | [derived] |
| Break-even BTF, Ti, no scrap credit | 1.5 × (627.3 + 118.9) ÷ (612.5 + 8) ≈ **1.8** | ORNL App. 1, 3b, 4a | [derived] (also in the note as an inference) |
| Material energy per kg of finished Ti part | machined BTF 8: ≈4,900 MJ; EBM BTF 1.5: ≈1,119 MJ | same | [derived] |
| EBM loses when little material is removed | qualitative; no threshold read | [Ingarao et al. 2018](https://iris.unipa.it/handle/10447/225481) | [SNIPPET] |
| AM SEC is "1 to 2 orders of magnitude" above conventional | qualitative | [Kellens et al. 2017](https://dspace.mit.edu/handle/1721.1/119453) | [SNIPPET] |
| Each new fabrication method needs a test programme | regulatory hook for AM | [14 CFR 25.605](https://www.ecfr.gov/current/title-14/section-25.605) | [FULL] |
| AM: no CS-level change; design values must cover powder/wire and post-processing | EASA guidance | [EASA CM-S-008 Issue 04 §3.1.1](https://www.easa.europa.eu/en/downloads/142437/en) | [FULL] |

**Deviate when.** (a) The topology run used an Extrusion or Pull-Out constraint and the part is prismatic. Machining is then natural, and the BTF may be low. (b) A near-net forging is available at BTF ≈1.3–2. It can beat AM cradle-to-gate; this is the Ingarao abstract plus the note's inference. (c) The brief demands flight-critical certification evidence in the slot. AM adds HIP, machining and a test programme (D-14).

**Say to the jury.** "Printing costs about the same process energy as machining, ≈69 MJ in ORNL's bracket. Its advantage is the 6.5 kg of titanium per kg of part that we never buy. Above a buy-to-fly of about 2 the printed route wins even before the flight phase starts, and our machined block is at [own BTF]."

### D-03 · Volume- or mass-retain target in the topology run

**Question.** What "Percent to Retain" (Mechanical) or volume target (Discovery) should the team use? **Default.** Do not use the 50 % default as one fixed number. Run three points, 50 / 35 / 25 % retain, each defined as a **Range**. Pick the lightest result that passes the D-13 validation. Remember that reconstruction and fillets add mass back.

| Evidence | Value | Source | Tag |
|---|---|---|---|
| Mechanical default | Percent to Retain **50 %**, range 1–99, treated as an **equality** in density-based TO | [Ansys Help 2024 R2 §2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_respsonse_constraint.html) | [FULL-WF] |
| Ansys recommendation | "specify a range … rather than just a constant value"; a 70 % reduction maps to a 25–30 % retain range; their bracket example used 10–13 % | [Ansys Help, Additive §6.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/add_ag/add_ag_adv_top_topopt.html) | [FULL-WF] |
| Overhang constraint costs mass | "Parts designed using the AM Overhang Constraint are constrained more and results will include more material" | same | [FULL-WF] |
| Academic SIMP reference | 30 % volume fraction on spars; p ≥ 3; SF 1.5; 3 g | [Elelwi et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8544218) | [FULL-WF] |
| Credible flight-part savings | A350 Ti bracket 30 %; Liebherr valve block 35 %; RUAG antenna bracket ≈41 %; Bionic Partition 45 % | [Airbus](https://www.airbus.com/en/newsroom/news/2016-03-pioneering-bionic-3d-printing), [Liebherr](https://www.liebherr.com/en-za/n/world-premier-first-ever-3d-printed-primary-flight-control-component-from-liebherr-aerospace-flown-on-an-airbus-aircraft-24183-6278302), [EOS/RUAG](https://www.eos.info/industries/customer-success-stories/space/ruag-aerospace-3d-printed-satellite-components) | [FULL-WF] |
| Over-designed outlier | GE bracket 80 % (Carter) / ≈84 % (GE Reports) | [Carter et al. 2014](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf), [GE Reports](https://www.ge.com/news/reports/how-it-all-began-the-rise-of-3d-printed-jet) | [FULL-SELF] / [FULL-WF] |
| Discovery only removes material | "can only remove material from the original geometry, it does not add" | [PADT 2020](https://www.padtinc.com/2020/03/10/ansys-discovery-live-a-focus-on-topology-optimization/) | [FULL-WF] |

**Deviate when.** The baseline is clearly over-designed, for example a service-only bracket like GE's. Then extend the sweep down to 15–20 % retain. Stop going lower once the validated peak stress exceeds the allowable after one round of local fixes.

**Say to the jury.** "We did not stake the design on one volume fraction. Three retain targets give a mass–stiffness curve, and we took the lightest point that passes all load cases at ultimate. That lands at [x] %, inside the 30–50 % band that flown parts from Airbus, Liebherr and RUAG report."

### D-04 · Safety, fitting and process factors

**Question.** What load does the validated part have to carry, and with which allowables? **Default.** Margin of safety ≥ 0 at **1.5 × 1.15 = 1.725 × limit**. Use A-basis allowables for a single load path and B-basis for redundant structure. There should be no detrimental permanent deformation at limit load. An optional AM factor can be presented **as an analogy** to the casting factors, never stacked on top of the fitting factor.

| Rule | Value | Source | Tag |
|---|---|---|---|
| Ultimate = limit × factor of safety | **1.5** | [§25.303](https://www.ecfr.gov/current/title-14/section-25.303) | [FULL] |
| Limit: no detrimental permanent deformation; ultimate: no failure for **3 s** | — | [§25.305](https://www.ecfr.gov/current/title-14/section-25.305) | [FULL] |
| By analysis: show deformation effects are insignificant or accounted for | relevant to flexible TO parts | §25.305(b) | [FULL] |
| Fitting factor (fitting, attachment, bearing) | **≥ 1.15**, unless limit and ultimate tests simulate the real stresses | [§25.625](https://www.ecfr.gov/current/title-14/section-25.625) | [FULL] |
| Combination rule | 1.5 × the **highest pertinent** special factor (no stacking) | [§25.619](https://www.ecfr.gov/current/title-14/section-25.619) | [FULL] |
| Casting factors (precedent for process variability) | critical: 1.0 / 1.25 / 1.50; non-critical: 1.0 / 1.25 / 1.5 / **2.0**; bearing ≤ 1.25 | [§25.621](https://www.ecfr.gov/current/title-14/section-25.621) | [FULL] |
| Design values | A-basis 99 %/95 % single load path; B-basis 90 %/95 % redundant | [§25.613](https://www.ecfr.gov/current/title-14/section-25.613) | [FULL] |
| Low-criticality AM parts (Class C/D) | "use of higher design factors", point-design tests, conservative attachments | [CM-S-008 Issue 04](https://www.easa.europa.eu/en/downloads/142437/en) | [FULL] |
| Ultimate multipliers | fitting 1.725; with a casting-analogy 1.25 → **1.875**; with 2.0 → 3.0 | — | [derived] |
| Demonstrated as-built EBM Ti-6Al-4V yield (GE brief) | 131 ksi, confirmed with co-built tensile bars | [Carter et al. 2014 p. 1407](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf) | [FULL-SELF] |

**Deviate when.** (a) The brief gives loads that are already ultimate. §25.303 then adds no further factor. (b) The team claims a test-backed joint. The 1.15 then drops away (§25.625(b)), but nobody will test in a two-hour slot. (c) The part is a seat or harness part, where §25.785(f)(3) applies instead. **Gap.** The EASA CS-25 text itself was not read. The FAR wording is assumed to match it, which is UNVERIFIED (memory).

**Say to the jury.** "Ultimate load is 1.5 times limit, and because this bracket joins two members it is a fitting, so we multiply by 1.15 as well. Every stress plot you see is at 1.725 times limit against an A-basis allowable. We did not invent an AM knock-down. Where we show one, it is the casting-factor logic of §25.621, applied as an analogy."

### D-05 · Use-phase fuel-per-kg factor

**Question.** How much fuel does one kilogram removed save per flight and over the aircraft's life? **Default.** Use Steinegger's **per-trip marginal fuel burn** for the closest aircraft type and stage length. Cross-check it with `aerokit.design.sustainability.lightweighting(mass_saved_kg, fuel_fraction, missions)`, which uses the Breguet factor f/(1−f) at fixed range ([K], `sustainability.py` line 124). Treat EduPack's own "mobile" use-phase factor as a third value and say which one appears in the headline.

| Evidence | Value | Source | Tag |
|---|---|---|---|
| Marginal fuel burn, A320 / A330 / A380 | **2.0–4.1 kg fuel per 100 kg per 1,000 km** (A322 2.8, A333 2.0, A388 4.1) | [Steinegger, ZHAW 2017, p. 4](https://digitalcollection.zhaw.ch/bitstream/11475/1896/2/Steinegger_Fuel_Economy_for_Aircraft_Operation_as_a_Function_of_Weight_and_Distance_v1-0.pdf) | [FULL TEXT] (not peer-reviewed) |
| Per trip (kg fuel per kg) | A322 0.07 / 0.12 / 0.16 at 2,000 / 4,000 / 5,000 km; A333 0.05–0.18 (2,000–7,000 km); A388 0.10–0.45 (2,000–12,000 km) | Steinegger p. 11, Fig. 15 (the column alignment is the note's reading) | [FULL TEXT] |
| Breguet check | f ≈ 0.10–0.15 gives f/(1−f) ≈ 0.11–0.18 kg/kg per trip, consistent with A322 0.12–0.16 | `use_phase_eol.md` | [note inference]; f values UNVERIFIED (memory) |
| Per flight hour | 0.03–0.05 kg fuel per kg per h | [planefyi](https://planefyi.com/guides/sustainable-aviation/aircraft-weight-reduction/) | [SNIPPET] (blog) |
| BA / ICAO 2002 | extra fuel ≈ 3–4 % of the weight increase × hours flown | [ICAO workshop, K. Morris](https://www2023.icao.int/Meetings/EnvironmentalWorkshops/Documents/2002-Workshop-OperationalMeasures-for-FuelEmissionsReduction/kevin_morris.pdf) | [SNIPPET] |
| Eco Audit mobile mode | "Products that are part of a transport system carry an additional energy and CO2 penalty"; **aircraft MJ/t·km not printed** | [Eco Audit white paper p. 10](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf) | [FULL TEXT] |
| ORNL's implied use-phase intensity | 96,500 MJ per kg carried over 15 yr ≈ **3.15 MJ per kg per 1,000 km**; identical in all three ORNL bracket rows, so the factor is linear | [ORNL Tables 6–7](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf) | [derived] |

**Deviate when.** (a) The brief names a regional turboprop, business jet or helicopter. The notes contain **no verified factor** for these, so use `aerokit` with that class's fuel fraction and say so. (b) The jury expects EduPack output. Use the EduPack mobile mode in the bars and show Steinegger and `aerokit` as cross-checks. (c) The stage length is long. Steinegger shows the per-trip factor rising non-linearly (fuel-for-fuel), so use the per-trip column rather than a per-km rate.

**Say to the jury.** "Every kilogram we remove saves about [0.12–0.16] kg of fuel per [4,000–5,000 km] A320 sector. That is a simulation-based marginal value, and the Breguet equation gives the same figure to first order. EduPack's own factor gives [y]. We quote the lower of the two."

### D-06 · End-of-life credit method

**Question.** How should recycling count? Options are recycled content at the start of life, a substitution credit at the end, or none. **Default.** Use EduPack's convention. Recycled content is credited at the start of life, with "no credit for recycling at the end" in the main bars, and the end-of-life benefit appears as a separate cross-hatched **EoL potential** bar. Choose recycle for Al and Ti and landfill or combustion for thermoset CFRP, with downcycling as a sensitivity case.

| Evidence | Value | Source | Tag |
|---|---|---|---|
| EduPack credit rule | credit for recycled content at start; none at end; conforms with PAS 2050 / BSI 2008; EoL potential shown separately | [Eco Audit white paper p. 9](https://ansys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf) | [FULL] / [FULL TEXT] |
| Five EoL options | landfill, combustion (energy recovered, CO2 released), recycling, re-engineer, reuse | same | [FULL] |
| Alternative used in literature | Scelsi: Al "100 % recyclable", credited as positive emissions; CFRP landfilled; **CFRP still wins** over life | [Scelsi et al. 2011 p. 211](https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf) | [FULL TEXT] |
| Airframe recycling rate | 92 % of weight (Tarmac Aerosave), > 99 % of CFM engine parts | [Airbus 2022](https://aircraft.airbus.com/en/newsroom/news/2022-11-end-of-life-reusing-recycling-rethinking) | [PAGE] |
| PAMELA (A300) | up to 85 % (earlier ≈60 %); composites then ≈4 % of the airframe | [EU LIFE project](https://webgate.ec.europa.eu/life/publicWebsite/project/LIFE05-ENV-F-000059/process-for-advanced-management-of-end-of-life-of-aircraft) | [SNIPPET] |
| CFRP recycling energy | thermal ≈3–30 MJ/kg vs virgin CF 183–594 MJ/kg | [Alsubaie & Yang 2026](https://strathprints.strath.ac.uk/97460/1/Alsubaie-Yang-ICMR-2026-Recycled-carbon-fibre-in-circular-economy-applications.pdf) | [SNIPPET] |
| rCF quality | air pyrolysis ≥ 873 K "greatly reduced" strength; solvolysis retains ≈95–98 % | [TechXplore/Obunai](https://techxplore.com/news/2023-11-reclaiming-carbon-fibers-discarded-composite.amp); [RSC Adv. 2019](https://pubs.rsc.org/en/content/articlepdf/2019/ra/c8ra08958b) | [SNIPPET] |

**Deviate when.** The jury or the brief asks for a "recycling credit" result. Show a substitution-credit case next to the default, label it, and never sum it into the first-life total. The 85–92 % airframe rates apply to metal-dominated A300/A320 airframes and must **not** be applied to a CFRP part ([note inference]).

**Say to the jury.** "EduPack credits recycled content at the start of life and shows end-of-life recycling as a separate potential, so nothing is counted twice. Aluminium's recyclability is in that hatched bar. Thermoset CFRP gets landfill, because there is no closed loop today."

---

## Requirements, method and material decisions

### D-07 · Ashby translation and performance index

**Default.** Write function, objective, constraints and free variable, then pick the `aerokit.materials.selection.rank` case that matches. The cases read from `selection.py` are `tie_stiff` E/ρ, `tie_strong` Fty/ρ, `beam_stiff` E^½/ρ, `beam_strong` Fty^⅔/ρ, `panel_stiff` E^⅓/ρ, `panel_strong` Fty^½/ρ and `column_buckling` E^½/ρ ([K]). Feed the function EduPack values as `{name: {"E", "Fty", "rho"}}` in SI units, and pass `co2_per_kg={…}` for the lowest-carbon part instead of the lightest. Run a stiffness index and a strength index, because which one governs only becomes clear after validation.

**Evidence.** The steps of the method (translation, screening, ranking) and the index derivations were **not read from a primary source**. In `design_criteria_method.md` they are UNVERIFIED (memory). The function/constraints/objective split was seen only as a [SNIPPET] of [UIUC ME598 notes](https://courses.grainger.illinois.edu/me598dm/sp2020/4.selection.pdf). The `aerokit` indices are tested against explicit mass formulas (`tests/materials/test_selection.py`, per the brief [K]). **Deviate when** the bracket is really a lug in bearing or a thin web prone to buckling. Then use `column_buckling` or `panel_*`. **Jury line.** "Function: carry [load] between [interfaces]. Objective: minimum mass. Constraint: [deflection] at limit load. Free variable: section size. That gives E^½/ρ, and EduPack's chart shows the guideline."

### D-08 · Alloy within the aluminium family

**Default.** Use 7xxx (7075/7050) when strength or compression governs and 2xxx (2024) for tension-dominated, fatigue-critical parts. **Evidence (weak).** Patent backgrounds state that 2024-T3 has long been standard for lower wing skins because of damage tolerance, and that upper skins are 7x50/7055 ([US 5865911](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5865911), [SNIPPET]). This logic matches §25.571's crack-growth focus ([eCFR](https://www.ecfr.gov/current/title-14/section-25.571), [FULL]). No MMPDS toughness comparison was read. Al-Li (2099/2195/2050) and Scalmalloy have **no verified eco data**. **Jury line.** "We picked [7075] because the validated part is strength-limited in [compression]. A tension-critical fitting would take 2024 for damage tolerance."

### D-09 · Mass vs CO2 vs cost trade-off (exchange constant)

**Default.** Plot the Ashby index against embodied CO2 per functional unit. If cost enters, use the penalty function Z = α₁M₁ + α₂M₂ with a stated α. "Optimum materials are those with the smallest value of Z", and in Ansys's truck example α = $5/kg favours Mg/Al while $500/kg favours CFRP ([Ansys Granta help](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/material_selection_penalty.html), [SNIPPET]). An aircraft α can be built from Carter's fuel-cost estimate of **$0.15–0.28 per lb per trip** ([Carter et al. 2014 p. 1404](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf), [FULL-SELF]). That is $0.33–0.62 per kg per trip [derived]. Multiplied by the team's assumed lifetime trips, it gives hundreds of $/kg once lifetime trips reach about 1,000 [derived]. That is the regime where Ansys's own example flips the choice to composites. **Jury line.** "At our exchange constant of [α] $/kg, which comes from fuel cost per kilogram per trip times lifetime trips, the cheaper but heavier option loses."

### D-16 · Interfaces: galvanic contact and magnesium

**Default.** Isolate any Al bracket from CFRP with a glass ply, sealant or wet-installed fasteners ([AC 20-107B §6.e](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf), [FULL]). CM-S-008 warns of "galvanic incompatibility" at AM attachments ([EASA](https://www.easa.europa.eu/en/downloads/142437/en), [FULL]). For magnesium, the documented acceptance route covers **seat** components via the Ch. 25 test ([Marker, FAA 2018](https://www.fire.tc.faa.gov/pdf/materials/March18Meeting/Marker-0318-magtask.pdf), [SNIPPET]). The policy number "PS-ANM-25-17" was **not confirmed** and must not be cited. **Gap:** Ti–CFRP galvanic compatibility has no source in the notes.

---

## Topology optimisation and structural verification decisions

### D-11 · Manufacturing constraint and mesh size

| Setting | Default | Source | Tag |
|---|---|---|---|
| AM overhang angle | **45°** default; density-based range 27–60°; build direction +Z; may be specified only once | [Ansys Help §2.8](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_manufact_constraint.html) | [FULL-WF] |
| Incompatibility | density-based: AM Overhang **cannot** be combined with Member Size / Extrusion / Pull-Out; **one** manufacturing-constraint object per analysis | same | [FULL-WF] |
| Minimum member size, Program Controlled | **2.5 × element size**; with SOLID187 tets + Pull-Out set ≥ 4 × tet size manually | same | [FULL-WF] |
| Feature-size floor in a real brief | 0.050 in = 1.27 mm minimum wall (GE) | [Carter p. 1405](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf) | [FULL-SELF] |
| Mesh needed to honour 1.27 mm | h ≤ 0.51 mm (default rule); ≤ 0.32 mm (tets + pull-out) | — | [derived] |
| Symmetry with overhang | the build direction must lie in the symmetry plane | Ansys Help §2.8 | [FULL-WF] |
| Ansys Student limit | 128K nodes/elements (structural) | `prev_guess/01_Ansys/docs/10_synopsys_2026_brief.md` §4 | [D] in brief |

**Decision rule.** If the claim is "printable without supports", use Overhang. Otherwise use Member Size. Check before meshing that h ≤ (min wall)/2.5 still fits inside 128K nodes. If it does not, raise the minimum wall, do not coarsen the member-size rule. Whether the two limits actually collide depends on the part size and was not computed in the notes. **Typical L-PBF minimum walls of 0.8–1.5 mm** are UNVERIFIED (memory).

### D-12 · Load cases and boundary conditions

**Default.** Use at least three independent load cases, for example the brief's main load, a perpendicular case and torsion, all at ultimate. GE judged four cases with **one FEA per case**, bolts and mounting faces rigid ([Carter p. 1406](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf), [FULL-SELF]). The physical tests went up to **9,500 lb axial and 5,000 in-lb torsion** ([GE Reports](https://www.ge.com/news/reports/how-it-all-began-the-rise-of-3d-printed-jet), [FULL-WF]). The other three GE vectors (≈8,000 / 8,500 / 9,500 lbf at 42°) are UNVERIFIED (memory). With several upstream environments, Ansys "only applies the minimum number of steps" ([Ansys Help §2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_respsonse_constraint.html), [FULL-WF]). Keep material around bolt holes and load faces with Discovery's "inflation" distance ([PADT](https://www.padtinc.com/2020/03/10/ansys-discovery-live-a-focus-on-topology-optimization/), [FULL-WF]) or with excluded regions. Reading stress away from point loads and fixed edges, and using remote points, is general practice that the notes did not source.

### D-13 · Reconstruction and validation

**Default.** Convert to a smoothed body, repair it, add fillets at the nodes, and re-attach the original interfaces exactly. GE disqualified many light entries for envelope violations, and "some of these entrants had not performed the analysis themselves" ([Carter p. 1410](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf), [FULL-SELF]). Then run "Create Validation Solution" at maximum fidelity on every load case ([PADT](https://www.padtinc.com/2020/03/10/ansys-discovery-live-a-focus-on-topology-optimization/), [FULL-WF]). Expect the stress to **rise**: PADT's peak went **267 → 360 MPa** (+35 %) after TO and back down to **256 MPa** after a thicker backplate, larger fillets and a re-run (same source). If max von Mises is within **5 %** of the limit, re-mesh finer before deciding, as GE did, and "in none of these cases was the outcome reversed" (Carter p. 1406, [FULL-SELF]). Keep STEP files small: GE could not mesh files over 300 MB. An h/h-over-2 convergence check with < 5–10 % change is general practice the notes did not source. A forum post links a constraint-vs-result stress gap to elemental-mean values ([Ansys forum](https://innovationspace.ansys.com/forum/?p=165857), [SNIPPET]). This is a reason to **always** check stress on the validation mesh rather than trust the optimiser's constraint.

### D-14 · Fatigue and AM post-processing

**Default.** State a damage-tolerance philosophy: §25.571 requires avoiding catastrophic failure from fatigue, corrosion, manufacturing defects or accidental damage, and allows safe-life only where damage tolerance is impractical ([§25.571](https://www.ecfr.gov/current/title-14/section-25.571), [FULL]). For an AM Ti-6Al-4V part, specify **HIP plus machining of fatigue-critical surfaces**. The evidence is summarised below.

| Finding | Value | Source | Tag |
|---|---|---|---|
| HIP on L-PBF Ti-6Al-4V | > 100 % increase in 10⁷-cycle fatigue strength (≈550–600 MPa, machined/polished specimens per context) | [Yi et al., arXiv 2311.07046 p. ~34](https://arxiv.org/pdf/2311.07046) | [FULL] |
| HIP alone with rough surface | "HIP does not improve the surface roughness"; not effective for notched as-built specimens | same, p. ~36 | [FULL] |
| EBM chemical polish | +60 % to 200 MPa → as-built ≈125 MPa (back-calculated in the note) | same, p. ~39 | [FULL]; the 125 MPa figure is a [note inference] |
| Ranking | HIPed+Machined ≥ Machined ≥ HIPed+Etched ≥ Etched ≥ As-built | same, Fig. 42 | [FULL] |
| As-built / polished ratio | ≈0.6 (single study) | `design_criteria_method.md` | [note inference] |

**Gap.** There are no fatigue numbers for AlSi10Mg or Scalmalloy and no regulatory AM fatigue knock-down. `aerokit structures life --kind fatigue` (MIL-HDBK-5J allowables, per the brief [K]) covers wrought alloys only.

### D-15 · Composite criteria (only if CFRP is shortlisted)

AC 20-107B, read in full, gives the logic but **no numbers**. Design values must hold in the critical environment, which may be hot/wet for some failure modes and cold/dry for others (§6.d). BVID must not reduce strength below ultimate (§7.f). Impact damage is "accommodated by limiting the design strain levels" (§6.g) ([AC 20-107B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf), [FULL]). The common **3000–4000 µε** CAI strain limit appears only in a generic table ([Engineers Edge](https://engineersedge.com/materials/common_fiber_composites_13604.htm), [SNIPPET]) and a flashcard. Present it as an industry rule of thumb, not as a regulation. Hot/wet knock-downs are material-specific (§25.613(c)), and none was sourced.

---

## Eco audit decisions

### D-10 · Buy-to-fly ratio

**Default.** Calculate BTF = mass of the bounding stock block ÷ final part mass from the team's own CAD, and pass it to `eco_audit(..., buy_to_fly=…)`. That function scales material and manufacture CO2 by bought mass ([K], `sustainability.py` line 166). For AM, use powder mass = part mass × (1 + support ≈0.2 + allowance ≈0.1) ([PoliTo exercise](https://maestro.prz.edu.pl/fcp/eGBUKOQtTKlQhbx08SlkTUgVKQ2pgTx0DDiA-WAJVQG9WFVZpCFghUHcKVj0GQUw/1180/code_RB0QRPwlQIEdwBEQoGhkfBlAHXTgg/outputs/am-machining_comparison_-_exercise-1.pdf), [SNIPPET]). This gives ≈1.3, against ORNL's assumed 1.5. Topology optimisation pushes the machined BTF **up**, because the part shrinks while the stock block does not ([note inference] from ORNL Case 2). Appendix A3 has the full range. **Gap.** It is not verified how EduPack books stock mass and scrap, as material phase or as a manufacture "% removed". Check the EduPack help.

### D-17 · Primary-material eco data and grid sensitivity

**Default.** Use the EduPack record for each candidate and run **one low and one high grid case** to show whether the ranking holds. **Evidence.** IAI: "most" primary Al footprints are 4.5–22 t CO2e/t, the 2023 global average is **14.8**, and electrolysis electricity alone contributes 8.6 ([IAI FAQ](https://international-aluminium.org/landing/aluminium-carbon-footprint-faqs/), [FULL-FETCH]). That is ≈58 % [derived]. Ti-6Al-4V is 16.1 (hydro) to 37.3 (Chinese grid) ([Lessard 2025](https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs40831-025-01258-1/MediaObjects/40831_2025_1258_MOESM1_ESM.pdf), [FULL-PDF]). Carbon fibre is **13.0–34.1 kg CO2e/kg** across grid scenarios, with PAN 37 % and energy 59 % of climate impact ([Polymers 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10780919/), [FULL-FETCH]). ICE is a construction database and has no aerospace alloys, so use it only as a cross-check. **Jury line.** "Even at hydro-smelted titanium and coal-smelted aluminium the ranking [holds / flips], so our choice does not rest on one database."

### D-18 · Recycled content at the start of life

**Default.** Use virgin metal, or EduPack's "recycle fraction in current supply", and **state which**. The white paper says the tool replaces virgin values with "the recycle fraction in current supply" when asked ([white paper p. 12](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf), [FULL TEXT]). Ashby gives Al **41–45 %** recycled supply (2012), Ti 23 %, Ni superalloys 22–26 %, stainless 35–40 % ([Ashby repro.](https://Polybags.Co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf), [FULL-PDF]). Those are generic market figures. Aerospace 2xxx/7xxx plate needs tight Fe/Si limits and is mostly primary plus prime scrap. That is a [note inference] with **no source for the actual recycled content**, so avoid 100 % recycled Al.

### D-19 · Manufacture-phase energy values

**Default.** Use EduPack's process rows and cross-check them with Appendix A2. The decisive message for the slide is that the manufacture bar **will be tiny**: about 0.07 % of the machined part's life-cycle energy in ORNL Case 2 [derived]. For CFRP, fibre production dominates. Changing the cure route moves the per-kg total by only ≈1–5 % unless Ashby's 200 MJ/kg autoclave value is used ([note inference] from [Atescan-Yuksek 2024](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content)). Thermoplastic is not automatically greener. CF-PA6 prepreg had the **highest** manufacturing CO2e in that study: 5,660 kg vs 2,940 kg for NCF epoxy ([FULL TEXT]).

### D-20 · Lifetime utilisation

**Default.** Base case: ORNL's **15 years × 255 days × 4,971 mi/day ≈ 30.6 million km** ([ORNL](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf), [FULL TEXT]; km conversion [derived]). Upper sensitivity case: Scelsi's **30 yr × 14,000 km/day ≈ 150 million km** ([Scelsi 2011 p. 213](https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf), [FULL TEXT]), which Atescan-Yuksek also uses. Pass the assumed flights to `lightweighting(..., missions=…)`. **Correction to the note.** `use_phase_eol.md` calls Scelsi's utilisation "physically impossible" (≈18,700 h/yr). That figure is an arithmetic slip: 14,000 km/day ÷ 750 km/h = **18.7 h per day ≈ 6,810 h per year** [derived], which is below 8,760 h. The assumption is **aggressive, not impossible**. It is more than twice the 3,000 h/yr in the planefyi snippet, so it still belongs only in the upper case. **Gap.** No primary source for typical block hours by aircraft class was read.

### D-21 · CO2 per kilogram of fuel

**Placeholder.** The notes list 3.16 kg CO2/kg Jet-A as **UNVERIFIED (memory)**. `aerokit` hard-codes `CO2_PER_KG_FUEL = 3.16`, and the code comment cites the ICAO CEC methodology v8 and the CORSIA Order 2021 art. 28(5) ([K], `sustainability.py` line 26). That comment is a pointer, not a source read in this session, so the tag stays. Confirm against EduPack's fuel record on the day.

### D-22 · Transport phase

**Default.** Include transport at the EduPack default, then say it is negligible. Scelsi excluded transport "due to their minor contribution" ([p. 211](https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf), [FULL TEXT]). The white paper's 14 t truck is **0.87 MJ/t·km and 0.062 kg CO2/t·km** ([p. 12](https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf), [FULL TEXT]). One kg moved 2,000 km by truck is **1.74 MJ and 0.12 kg CO2** [derived]. The note's 3.5 MJ used 0.002 t instead of 0.001 t. The conclusion is unchanged: this is < 1 % of any total.

### D-23 · Headline claim and payback

**Default.** Give one sentence with three numbers: mass saved (% and kg) with the constraint that was held, life-cycle CO2 saved, and payback in flights from `payback_missions(extra_production_co2_kg, co2_saved_per_mission_kg)` ([K]). Use published cases as anchors. Scelsi's 10 kg Al-2024 panel replaced by an 8 kg CFRP panel breaks even after **45,000 km / 60 h** for climate change, 85,000 km / 113 h for fossil fuel and 70,000 km / 93 h for the Eco-indicator 99 single score ([Scelsi Table 1](https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf), [FULL TEXT]). In Atescan-Yuksek's wing skin, composites overtake Al after **≈100,000–300,000 km**, or 7–21 days of flying ([Cranfield](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content), [FULL TEXT]). Timmis 2015 is at abstract level only ([DOI](https://dx.doi.org/10.1007%2Fs11367-014-0824-0), [SNIPPET]). Every industrial case pairs the % with a held requirement, as RUAG did: "1.6 kg → 940 g, stiffness > 30 % over requirement" ([EOS](https://www.eos.info/industries/customer-success-stories/space/ruag-aerospace-3d-printed-satellite-components), [FULL-WF]). Translate the result to aircraft level the way Carter does: "1.7 kg per LEAP engine" ([Carter p. 1411](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf), [FULL-SELF]).

### D-24 · Jury deliverables

Four deliverables are recommended ([note inference]):

| # | Deliverable | Content |
|---|---|---|
| 1 | Retain-sweep curve | 3–4 points of mass fraction vs compliance (or maximum displacement), with the chosen point marked |
| 2 | Before/after table | per load case: mass, maximum displacement, maximum von Mises, margin of safety at 1.725 × limit |
| 3 | Image strip | raw density → smoothed body → validation stress plot |
| 4 | Eco audit phase bars | for each candidate, the EoL potential bar shown separately, and the sensitivity case |

No public jury rubric was found. The brief's guess at what the jury values is a mass–CO2–cost trade, a justified material choice, credible FEA and life-cycle reasoning ([Y] in brief §6).

### D-25 · Toolchain fallback

Granta EduPack is **not** in the Ansys Student bundle. Discovery needs a listed GPU architecture, and this laptop's GTX 1660 Ti (Turing) is not on the list (`prev_guess/01_Ansys/docs/10_synopsys_2026_brief.md` §4, [D]/[K]). **Default fallback.** Run topology in Mechanical (track 2d). Use `aerokit fem topology` for 2-D/3-D concepts and `aerokit.materials.selection.rank` with properties and CO2 factors from a **stated** source. In that case the eco numbers come from Appendix A1 with their tags shown on the slide.

---

## Decisions added on 1–3 November (D-26 to D-56)

These rules came after the 25 decisions above: D-26 from the rehearsal, D-27 to D-40 for the three side areas (`prev_guess/01_Ansys/docs/11_three_variants.md`), D-41 to D-48 for the five task scenarios and the Ansys set-up (`prev_guess/01_Ansys/docs/12_task_scenarios.md`), D-49 to D-53 for the rest of the task space (`prev_guess/01_Ansys/docs/13_task_space.md`), D-54 to D-56 for topology constraints and FE reportability (`prev_guess/01_Ansys/docs/14_course_playbook.md`). Evidence, tags and deviations for each are in `prev_guess/01_Ansys/tradeoff/decision_rules.json`; this table is generated from that file.

| Id | Area | Question | Default |
|---|---|---|---|
| D-26 | main path | Which constraint governs, and does the aluminium choice still matter? | read margin on yield at ultimate AND deflection at limit for each candidate on the same topology; if deflection governs and aluminium alloys sit within the … |
| D-27 | router | Which of the three side areas (or the main static-bracket path) does the card fall into? | main path (static strength/stiffness bracket: card_day + bracket studies) unless a signal below appears |
| D-28 | A vibration | A minimum natural frequency is given: what governs and which material index applies? | put frequency_Hz_min and added_mass_kg (equipment at the load point) on the card and run card_day; when the attached mass is much larger than the part, f1 ~ … |
| D-29 | A vibration | Cyclic loads: which fatigue strength does a TO + AM part get? | use the as-built-surface S-N value: the inner faces of a topology-optimised AM part cannot be machined; machine or shot-peen only the critical faces and say … |
| D-30 | A vibration | No frequency given but the part vibrates: which target to quote? | rotor-driven part: f1 >= 1.5 x blade-pass frequency (preprint criterion); spacecraft equipment: stay above 100 Hz so no coupled-loads model is needed … |
| D-31 | B material/circularity | A panel must be lighter: change the material or the concept? | change the concept first: a thin-face sandwich of equal bending stiffness weighs about 0.16-0.20 of a 2 mm aluminium plate; a material swap gains 4 % … |
| D-32 | B material/circularity | Cabin interior part: which materials are allowed at all? | screen with the cabin fire tests before ranking: 60 s vertical burn, OSU heat release 65/65, smoke Ds <= 200 (aircraft with >= 20 seats); glass/phenolic on … |
| D-33 | B material/circularity | How to show end of life? | report the end-of-life potential as a separate bar, never inside the life total (Eco Audit avoids crediting recycling twice); for a flying part it is below … |
| D-34 | B material/circularity | Carbon fibre footprint: which number? | quote the range 19.85 (JCMA 2022) to 68 (coal grid, Meng 2017) kg CO2/kg fibre with 33 (EduPack family) as the value; name ecoinvent 81.6 as an outlier; run … |
| D-35 | B material/circularity | Which workflow will the jury recognise for a material-substitution task? | the sponsor course sequence: function/constraints/objective -> index chart -> Synthesizer sandwich (CFRP faces, Al honeycomb) -> Eco Audit of both concepts |
| D-36 | C thermal/energy | Service temperature above about 100 C: which alloys stay? | drop Scalmalloy above 100 C and 7075-T6 for long exposure above about 100 C (34 % of RT yield after 10,000 h at 150 C); hot aluminium = 2618-T61; above … |
| D-37 | C thermal/energy | A metal part bolted to CFRP (or any low-expansion structure) and heated or cooled: what governs? | check the expansion mismatch: sigma ~ E (alpha_part - alpha_structure) dT; it does not fall when material is removed, and stiffer (heavier) designs see more … |
| D-38 | C thermal/energy | Engine or APU fire zone? | engine mounts in or next to a fire zone must be fireproof or shielded (14 CFR 25.865); fireproof = performs at least as well as steel, fire resistant = as … |
| D-39 | C thermal/energy | Can Discovery optimise for heat? | no: Discovery topology optimisation is structural and modal only; run the structural topology, then check temperature and thermal stress in Discovery … |
| D-40 | C thermal/energy | Battery or hydrogen component: what must the design show? | battery enclosure: non-propagation from one cell and containment (MOC-3 SC-VTOL: >= 2 cells in runaway is catastrophic; containment test with runaway in >= … |
| D-41 | scenario router | Which of the five scenarios is the card closest to? | S1 engine-mount bracket unless the card says otherwise (docs/12 §2) |
| D-42 | Ansys set-up | How to apply loads and supports in Discovery or Mechanical? | force through a remote point at the true load origin (pin centre, unit centre of gravity); supports on the bolt faces as cylindrical support or remote … |
| D-43 | Ansys set-up | Which Discovery topology goal? | Maximize Stiffness on all load cases with target volumes of 30, 40 and 50 % kept; plot mass against peak stress |
| D-44 | Ansys set-up | One load case or all of them? | all load cases in one topology run |
| D-45 | Ansys set-up | How much margin to keep before smoothing and rebuilding? | keep 20-30 % stress margin at the topology stage and report only the rebuilt, re-validated mass |
| D-46 | Ansys set-up | How to quote the mass saving? | always name the baseline: against a real part 15-64 %, against a design-space block 60-85 % of volume; a defensible claim for a flight part is 30-50 % |
| D-47 | Ansys set-up | What mesh budget and evidence for the validation run? | stay below 128K nodes/elements in Refine or Mechanical (contacts included); voxel <= smallest feature; show averaged vs unaveraged maximum and a <= 5 % … |
| D-48 | Ansys set-up | Which hand numbers to have before Ansys runs? | reaction sum, worst bolt tension and shear, pin bearing and lug net-section stress; expect the FE peak at 3-4 times the nominal lug stress |
| D-49 | task space | Heat sink or cold plate: material, fin height, cooling mode? | aluminium (6061 or AM AlSi10Mg T6); size the fins for the flow: gaps above 2 x the Blasius thickness (forced) or above the Elenbaas optimum (natural); … |
| D-50 | task space | Pressure vessel or tank: what sizes the wall? | check pressure first, then minimum gauge, buckling, supports and insulation; at a few bar pressure rarely sizes a 1 m tank |
| D-51 | task space | Rotating part: does rotation govern? | compute the rim speed first; rotation governs only at high rim speed (motor rotors, fans); otherwise keep f1 clear of the rotor orders (D-30) |
| D-52 | task space | The card asks for a parameter study instead of topology: how? | 3-level full factorial over at most 3 parameters (9-27 Discovery runs), quadratic surface per response, report R2 and leave-one-out error, pick the lightest … |
| D-53 | task space | The prompt is open (an ideathon idea, not a defined part): what do we pitch? | pick one idea from the idea bank whose simulation hook is already rehearsed, and make the simulation the evidence of the idea |
| D-54 | topology | AM route: set overhang prevention, and what does it cost? | set overhang prevention at 45 deg with the build direction stated; expect some loss of stiffness at the same volume and say so; no support material is the gain |
| D-55 | topology | Symmetry or pull direction in the topology run? | symmetry only if geometry, material, loads and expected response are all symmetric; pull/extrusion when the part will be machined or cast along one axis |
| D-56 | fea | Is this FE number reportable? | run three meshes of the reported quantity: converging -> report the fine value with its GCI (<= 5 % = converged); diverging -> it is a singularity: read … |

## Conflict register

Each row is a disagreement between sources, or inside one source, that the team could trip over.

| # | Conflict | Values | Resolution for competition day |
|---|---|---|---|
| C-01 | IAI chart vs IAI range (same page) | chart: Hydro ≈10, Gas ≈13, **Coal ≈30** t CO2e/t; text: "most" 4.5–22, best ≤4 ([IAI](https://international-aluminium.org/landing/aluminium-carbon-footprint-faqs/), [FULL-FETCH]) | Quote the 4.5–22 range and the 14.8 global average. If the chart is used, say it probably shows full-chain or worst cases |
| C-02 | ICE v3 "Aluminium, general" | 9.16 ([HKUST](https://cejcheng.people.ust.hk/ec/carbonInventoryLocalized.html)) vs 8.24 ([calculator](https://datadrivenaec.com/tools/embodied-carbon-calculator-by-material)); both [SNIPPET] | Do not cite ICE as a headline. It is a construction database |
| C-03 | Primary Al embodied energy | Ashby 210 ± 10 [FULL-PDF]; ORNL 210 [FULL TEXT]; Energy Star 207 [SNIPPET]; IAI-attributed 186 GJ/t [SNIPPET]; Cranfield Al ingot **157.6** [FULL TEXT] | EduPack value; 157.6 shows the boundary/year spread |
| C-04 | "Recycled Al = 5 % of primary" | 4.5 % (8.3/186, [SNIPPET]); 6 % (Energy Star); 7 % (13.6 GJ/t); **12 %** (Ashby 26/210, [FULL-PDF]); CO2 ratio 2.6 % (EU 0.26/10.1, [SNIPPET]) [derived ratios] | Say "5–12 % depending on boundary; 5 % is clean-scrap remelting only" |
| C-05 | Ti-6Al-4V primary | Ashby repro. 650–720 MJ/kg and 46.5 kg CO2/kg [FULL-PDF] vs ORNL (Ashby-based) **612.5** MJ/kg [FULL TEXT] vs Lessard 37.3 / 16.1 kg CO2e/kg [FULL-PDF]; CES 2005 ≈55 kg **carbon** (not CO2) [SNIPPET] | Probably different Ashby editions; use EduPack and show Lessard as the grid band |
| C-06 | Carbon fibre energy (ten values) | process-only 170; fossil 262–498 (Polymers 2024, [FULL-FETCH]); Ashby 450–500 [FULL-PDF]; ORNL CFRP 475 [FULL TEXT]; Cranfield **870** [FULL TEXT]; Das 704 and 771–1,169 [SNIPPET]; Nottingham 198–595, Strathclyde 183–594, Springer 200–900 [SNIPPET] | Boundary (process vs cradle-to-gate incl. PAN), grid, plant scale. EduPack CFRP record, ±2× sensitivity |
| C-07 | Polymers 2024, internal | abstract 13.0–34.1 vs Section 7 13–29 kg CO2e/kg [FULL-FETCH] | Cite the abstract range and flag it |
| C-08 | **Autoclave energy** | Ashby 100–300 [FULL-PDF] / ORNL-Ashby **200** [FULL TEXT] vs Cranfield curing **11.8** (+ prepreg 40) [FULL TEXT] vs Springer ≈21 [SNIPPET]; Scelsi 68 kWh per 8 kg panel ≈ 30.6 MJ/kg electricity, ≈91 MJ/kg primary at Cranfield's 2.98 factor [derived] | Probably whole-run vs per-kg-at-full-load. Say which value EduPack uses; it changes CFRP manufacture by up to ≈17× and the life total by little |
| C-09 | Epoxy embodied energy | Ashby 127–140 [FULL-PDF] vs Cranfield 97.4 [FULL TEXT] vs Springer ≈78 [SNIPPET] | EduPack |
| C-10 | Al machining energy | Cranfield 3.0 [FULL TEXT] vs Ashby finishing 8, heavy **108.9** MJ/kg (ORNL App. 3b) [FULL TEXT] | Per kg *removed* vs per kg part. State the basis |
| C-11 | AM specific energy | EBM 118.9 (Baumers) vs **61** (Arcam A1, Bourhis) [FULL TEXT]; SLM 118.2, DMLS 158.4 [FULL TEXT] vs SLM 26–61 or 253 MJ/kg (WAAM review, [SNIPPET]) [derived kWh→MJ]; PoliTo EBM 60–177 [SNIPPET] | Use 60–160 MJ/kg as a band; ORNL data are 2010–13 machines |
| C-12 | Machined BTF | ORNL **33** and **8** [FULL TEXT]; 12–25 via Huang [SNIPPET]; ≈10 (Northwestern) [SNIPPET]; 21 / 11 (Barnes) [SNIPPET]; 9 (MATEC) [SNIPPET]; > 10 (Suárez) [FULL TEXT] | Compute your own |
| C-13 | **GE bracket** | Carter: ≈1.8 kg (4 lb), **80 %**, "almost 700" entrants [FULL-SELF]; GE Reports: 2,033 g → 327 g, "nearly **84** percent", "over 700" [FULL-WF]. Carter's own "1.7 kg per engine" equals 2,033 − 327 = 1,706 g, not 1.8 × 0.8 = 1.44 kg [derived] | Quote one source consistently; GE Reports' absolute masses are self-consistent |
| C-14 | RUAG bracket | EOS 1.6 kg → 940 g (≈41 %) [FULL-WF] vs Altair "half the weight" [SNIPPET] | Use EOS (it gives absolute masses) |
| C-15 | A380 ribs | > 500 kg vs ≈1,000 kg per aircraft; 18.4 % vs > 40 % rib saving ([Elelwi](https://pmc.ncbi.nlm.nih.gov/articles/PMC8544218) [FULL-WF]; others [SNIPPET]) | Do not quote as a number without the primary source |
| C-16 | Liebherr baseline | titanium **forging** (Liebherr, [FULL-WF]) vs "conventional milling" (3dprintingindustry, [SNIPPET]) | Liebherr |
| C-17 | Bionic Partition part count | 122 Scalmalloy + 40 Ti vs 112 ([SNIPPET]) | Quote the mass (45 %, 30 kg, [FULL-WF]) only |
| C-18 | GE LEAP nozzle | 20 parts → 1 vs brazes 25 → 5; 19 vs "nearly twenty" per engine (all [SNIPPET]) | Avoid, or cite as part consolidation only |
| C-19 | Huang 2016 fleet savings | 70–173 vs 70–174 million GJ/yr (two ORNL records, [SNIPPET]) | Avoid |
| C-20 | Steinegger, internal | abstract 0.02–0.03 vs Fig. 7 0.020–0.041 kg/kg/1,000 km [FULL TEXT] | Use the figure range |
| C-21 | Fuel per kg per hour | Steinegger at 800 km/h ≈ 0.016–0.033 [derived] vs blog 0.03–0.05 vs ICAO/BA 0.03–0.04 vs patent 0.02–0.04 (all [SNIPPET]) | Quote 0.02–0.05 as a band ([note inference]); prefer Steinegger per trip |
| C-22 | ORNL use-phase intensity vs Steinegger | ORNL ≈3.15 MJ per kg per 1,000 km [derived] vs Steinegger 0.020–0.041 kg fuel ≈0.86–1.76 MJ (at ≈43 MJ/kg LHV, UNVERIFIED (memory)) → **ORNL ≈1.8–3.7× higher** | ORNL probably allocates average, not marginal, fuel. Do not mix the two in one chain |
| C-23 | **Scelsi utilisation** | the note says "physically impossible" (18,700 h/yr); the correct value is 18.7 h/day ≈ 6,810 h/yr [derived] | Aggressive, not impossible; upper case only (D-20) |
| C-24 | Atescan-Yuksek ratio | the note: whole-life CO2e = 6,700× manufacturing + disposal for Al; Table 5 values 7.56 × 10⁶ / 604 = **≈12,500×** [derived] | One of the three numbers is misread; check Table 5 before quoting the ratio |
| C-25 | ORNL totals | listed phases sum 0.37–0.53 % above the stated totals in all four columns [derived] | Probably an unlisted EoL credit row; quote the stated totals |
| C-26 | Eco Audit white paper version | cover "Version 2.1 – January 2012" with footer © 2021 (design note) vs "v3, Oct 2021" (use-phase note); two URLs (ansys.com / ansys.synopsys.com) | Cite as "Ashby et al., Eco Audit white paper (Ansys, 2021)" and give the URL |
| C-27 | CFRP recycling energy | 3–30 MJ/kg (Strathclyde 2026) vs ≈110 MJ/kg lab pyrolysis (ISIE 2017); both [SNIPPET] | Scale/boundary; EduPack EoL record |
| C-28 | Ti powder CO2 | 6K ≈27.5 (vendor) vs Xiao ≈20 vs IperionX recycled 7.8 (vendor), all [SNIPPET]; ORNL atomisation **+14.8 MJ/kg** [FULL TEXT] vs Spreafico > 5-fold parametric variation [SNIPPET] | Treat the AM powder premium as uncertain; BTF dominates |
| C-29 | Transport arithmetic in the note | 3.5 MJ (used 0.002 t) vs 1.74 MJ for 1 kg × 2,000 km [derived] | Conclusion unchanged (< 1 %) |
| C-30 | AFRA membership | 72 vs 80 (2022) [SNIPPET] | Do not quote |

---

## Data appendix

### A1 · Family-level eco data (Ashby 2nd ed. via the "Useful Numbers" PDF unless stated)

All rows in the first block are [FULL-PDF] from [Useful Numbers (Ashby repro.)](https://Polybags.Co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf). The table has **no per-alloy rows**. The notes' density, modulus, strength and price columns are UNVERIFIED (memory) and are omitted here on purpose.

| Family | Primary EE (MJ/kg) | Primary CO2 (kg/kg) | Recycling EE (MJ/kg) | Recycling CO2 (kg/kg) | Recycle fraction in supply |
|---|---|---|---|---|---|
| Titanium alloys | 650–720 | 46.5 | 78–96 | 5.2 | 23 % |
| Carbon fibre (fibre only) | 450–500 | 33–36 | – | – | – |
| Magnesium alloys | 300–330 | 36 | 23–26 | 2.9 | 36–41 % |
| Ni superalloys (In718 proxy) | 221–244 | 11.6 | 33.8–37.5 | 2.14 | 22–26 % |
| Aluminium (generic) | 210 ± 10 | 12 | 26 cast / 26.7 wrought (Schubert 1996) | 2.1 | 41–45 % (2012) |
| Epoxy resin | 127–140 | 6.8–7.5 | – | – | – |
| GFRP | 107–118 | 7.47–8.26 | – | – | – |
| Stainless steel (17-4PH proxy) | 81–88 | 5.0 | 11–13 | 0.73 | 35–40 % |

| Cross-check value | kg CO2e/kg | Source | Tag |
|---|---|---|---|
| Ti-6Al-4V ingot, primary, Chinese grid / hydro | 37.3 / 16.1 | [Lessard 2025 SI S-2](https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs40831-025-01258-1/MediaObjects/40831_2025_1258_MOESM1_ESM.pdf) | [FULL-PDF] |
| Ti-6Al-4V ingot, recycled, Chinese grid / hydro | 3.1 / 0.2 | same | [FULL-PDF] |
| 316L ingot primary / 80 % recycled content | 11.4 / 3.3 | same, S-3 | [FULL-PDF] |
| Primary Al, global average 2023 | 14.8 | [IAI](https://international-aluminium.org/landing/aluminium-carbon-footprint-faqs/) | [FULL-FETCH] |
| Primary Al, "most" range | 4.5–22 | same | [FULL-FETCH] |
| Primary Al, EU consumption mix / recycled | ≈10.1 / ≈0.26 | [European Aluminium via greencalculus](https://greencalculus.com/standards/european-aluminium-environmental-profile-report/) | [SNIPPET] |
| Carbon fibre, grid scenarios | 13.0–34.1 | [Polymers 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10780919/) | [FULL-FETCH] |
| Ti-6Al-4V powder | ≈20 (Xiao 2024) to ≈27.5 (6K, vendor) | [Xiao](https://journal.hep.com.cn/ais/EN/10.1007/s43684-024-00079-5), [6K](https://go.6kinc.com/hubfs/LCA/Foresight_6K_Ti_LCA_FINAL.pdf) | [SNIPPET] |

| ORNL App. 1 (Ashby-based), MJ/kg | Primary | Recycled | Tag |
|---|---|---|---|
| Ti-6Al-4V powder (incl. atomisation 14.8) | 627.3 | – | [FULL TEXT] |
| Ti-6Al-4V | 612.5 | 87.0 | [FULL TEXT] |
| CFRP | 475 | – | [FULL TEXT] |
| Al alloys | 210 | 26 | [FULL TEXT] |

Source: [ORNL/TM-2014/93](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf). The MJ/kg values were converted in the note from the printed Btu/lb.

### A2 · Process energies (MJ/kg)

| Process | Value | Source | Tag |
|---|---|---|---|
| Water-jet / EDM / laser cutting (per kg removed) | 2,750 | ORNL App. 3b (Ashby) | [FULL TEXT] |
| Autoclave moulding (Ashby) | 100–300; ORNL lists 200 | [Ashby repro. p. 9](https://Polybags.Co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf) / ORNL App. 3a | [FULL-PDF] / [FULL TEXT] |
| FDM | 178.0 | ORNL App. 4a | [FULL TEXT] |
| DMLS | 158.4 | ORNL App. 4a (Baumers 2013) | [FULL TEXT] |
| EBM (used in ORNL case studies) | 118.9 | same | [FULL TEXT] |
| SLM | 118.2 | same | [FULL TEXT] |
| Machining, heavy | 108.9 | ORNL App. 3b (Ashby) | [FULL TEXT] |
| Laser DED (DMD) | 98.3 | ORNL App. 4a | [FULL TEXT] |
| Kroll sponge electricity (≈25 kWh/kg) | ≈90 | [DRDO DSJ](https://publications.drdo.gov.in/ojs/index.php/dsj/article/download/5966/3094) | [SNIPPET]; conversion [derived] |
| Baked coatings | 65 | ORNL App. 3b | [FULL TEXT] |
| EBM, Arcam A1, Ti-6Al-4V | 61 | ORNL App. 4b (Bourhis 2013) | [FULL TEXT] |
| Prepreg production | 40 | [Atescan-Yuksek 2024 Table 3](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content) | [FULL TEXT] (footnote-digit reading by the note) |
| Grinding | 30 | ORNL App. 3b | [FULL TEXT] |
| Injection moulding + heating (CF-PA6) | 25.3 | Atescan-Yuksek Table 3 | [FULL TEXT] |
| Metal powder forming | 20–30 (Ashby); 25 (ORNL) | Ashby repro. / ORNL App. 3a | [FULL-PDF] / [FULL TEXT] |
| Epoxy moulding | 21–23 (1.7–1.85 kg CO2/kg) | Ashby repro. p. 10 | [FULL-PDF] |
| Rough rolling / forging | 15.9 | ORNL App. 3a | [FULL TEXT] |
| Gas atomisation, Ti-6Al-4V | 14.8 | ORNL App. 1 | [FULL TEXT] |
| Curing (prepreg) | 11.8 | Atescan-Yuksek Table 3 | [FULL TEXT] |
| Wet compression moulding | 11.3 | same | [FULL TEXT] |
| Casting | 8–12 (Ashby); 10 (ORNL) | Ashby repro. / ORNL App. 3a | [FULL-PDF] / [FULL TEXT] |
| Al sheet rolling | 9.6 | same | [FULL TEXT] |
| Machining, finishing | 8 | ORNL App. 3b | [FULL TEXT] |
| Al machining | 3.0 | Atescan-Yuksek Table 3 | [FULL TEXT] |
| Fabric production | 2.6 | same | [FULL TEXT] |
| Primary energy per MJ electricity (EU) | 2.98 | Atescan-Yuksek §3.1 | [FULL TEXT] |
| SLM / WAAM (kWh/kg) | 7.30–17.06 / 3.06–5.39 | [WAAM review 2026](https://link.springer.com/article/10.1007/s00170-026-18690-6) | [SNIPPET] |

The table is sorted by energy, largest first, except the last two rows, which use different units.

### A3 · Buy-to-fly ratios

| Route / case | BTF | Source | Tag |
|---|---|---|---|
| Fokker-related part, solid billet → WAAM | 37 → 6.3 | [Inside Metal AM 2016](https://insidemetaladditivemanufacturing.com/2016/04/03/building-large-metallic-parts-with-wire-arc-additive-manufacturing/) | [SNIPPET] |
| Ti cabin bracket, forged + machined (ORNL Case 1) | 33 | [ORNL p. 54](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf) | [FULL TEXT] |
| Al and Ti aircraft parts, conventional (via Huang) | 12–25 | [ORNL Impact record](https://impact.ornl.gov/en/publications/energy-and-emissions-saving-potential-of-additive-manufacturing-t/) | [SNIPPET] |
| Ti forgings / machined parts (Barnes) | ≈21 / ≈11 | [ResearchGate figure](https://www.researchgate.net/figure/The-effect-on-buy-to-fly-ratios-on-conventional-vs-additive-manufacturing_fig4_312115931) | [SNIPPET] |
| Landing-gear part, billet → WAAM | 11.5 → 1.14 | [ITA 2015](https://cdn.ymaws.com/titanium.org/resource/resmgr/AddisonAdrianTiEU2015-3DAddi.pdf) | [SNIPPET] |
| Ti forged preform (aeronautical) | > 10 | [Suárez 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10672625/) | [FULL TEXT] |
| 1 kg bracket needs ≈10 kg raw material | ≈10 | [Northwestern 2015](https://www.mccormick.northwestern.edu/news/articles/2015/06/saving-money-and-the-environment-with-3-d-printing.html) | [SNIPPET] |
| Ti forged + machined (MATEC) | ≈9 | [MATEC 2020](https://www.matec-conferences.org/articles/matecconf/pdf/2020/17/matecconf_ti2019_02005.pdf) | [SNIPPET] |
| Ti cabin bracket, machined (ORNL Case 2) | 8 | ORNL p. 57 | [FULL TEXT] |
| EBM (ORNL assumption, both cases) | 1.5 | ORNL | [FULL TEXT] |
| EBM with 20 % support + 10 % allowance | ≈1.3 | PoliTo exercise | [SNIPPET]; ratio [derived] |
| Break-even BTF, EBM vs machining, Ti, no scrap credit | ≈1.8 | from ORNL App. 1/3b/4a | [derived] |
| CFRP vs Al study (cited) | 1 and 8 | Atescan-Yuksek intro (their ref. 18) | [FULL TEXT] of the citing paper |

### A4 · Fuel-per-kg factors and lifetime anchors

| Factor | Value | Source | Tag |
|---|---|---|---|
| Patent: kg fuel per kg per h (100,000 h life → ≈4 t/kg) | 0.02–0.04 | [USPTO 12138894](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12138894) | [SNIPPET] (advocacy) |
| Blog: kg fuel per kg per flight hour | 0.03–0.05 | [planefyi](https://planefyi.com/guides/sustainable-aviation/aircraft-weight-reduction/) | [SNIPPET] |
| Marginal, kg fuel per kg per 1,000 km (A320/A330/A380) | 0.020–0.041 | [Steinegger 2017 Fig. 7](https://digitalcollection.zhaw.ch/bitstream/11475/1896/2/Steinegger_Fuel_Economy_for_Aircraft_Operation_as_a_Function_of_Weight_and_Distance_v1-0.pdf) | [FULL TEXT] |
| Average (total) carry cost, kg fuel per kg per 1,000 km | ≈0.2 | Steinegger abstract | [FULL TEXT] |
| Per trip A322 at 2,000 / 4,000 / 5,000 km | 0.07 / 0.12 / 0.16 | Steinegger Fig. 15 | [FULL TEXT] |
| Per trip A333 at 2,000 / 4,000 / 5,000 / 7,000 km | 0.05 / 0.08 / 0.11 / 0.18 | same | [FULL TEXT] |
| Per trip A388 at 2,000 / 4,000 / 5,000 / 7,000 / 12,000 km | 0.10 / 0.17 / 0.18 / 0.26 / 0.45 | same | [FULL TEXT] |
| ICAO/BA: extra fuel as a share of weight increase per hour flown | 3–4 % | [ICAO 2002](https://www2023.icao.int/Meetings/EnvironmentalWorkshops/Documents/2002-Workshop-OperationalMeasures-for-FuelEmissionsReduction/kevin_morris.pdf) | [SNIPPET] |
| ICAO/TC: 500 kg on a 1.5 h flight | 30–50 kg fuel | [ICAO/Transport Canada 2006](https://www.icao.int:443/Meetings/EnvironmentalWorkshops/Documents/ICAO-TransportCanada-2006/Viscotchi.pdf) | [SNIPPET] |
| Lifetime fuel per kg (100 kg → 124–129 t) | ≈1.2–1.3 t/kg | [Léonard & Nylander via SimpliFlying](https://simpliflying.com/green/why-every-kilogram-counts-expliseat) | [SNIPPET] |
| ORNL use-phase energy per kg carried, 15 yr | ≈96,500 MJ/kg (≈3.15 MJ/kg/1,000 km) | ORNL Tables 6–7 | [derived] |
| ORNL lifetime | 15 yr, 255 d/yr, 4,971 mi/day ≈ 30.6 M km | [ORNL](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf) | [FULL TEXT]; km [derived] |
| Scelsi / Atescan-Yuksek lifetime | 30 yr × 14,000 km/day ≈ 150 M km (18.7 h/day at 750 km/h) | [Scelsi p. 213](https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf) | [FULL TEXT]; h/day [derived] |
| CO2 per kg Jet-A | 3.16 | `aerokit` constant; notes | UNVERIFIED (memory) |

No verified factor exists for regional turboprops, business jets or helicopters.

### A5 · Certification factors (14 CFR Part 25, eCFR 2026-10-01, all [FULL])

| Item | Factor | Section |
|---|---|---|
| Non-critical casting, visual inspection only | 2.0 (bearing ≤ 1.25) | §25.621(d) |
| Factor of safety on limit load | 1.5 | §25.303 |
| Casting, critical, surface + radiographic + 1 static test | 1.50 | §25.621(c)(3) |
| Casting, critical, surface + radiographic + 3 static tests | 1.25 (deformation at 1.15 × limit) | §25.621(c)(2) |
| Fitting factor | ≥ 1.15 | §25.625 |
| Pressurisation in residual strength | × 1.15 on maximum differential pressure | §25.571(b) |
| Casting, critical, CoV equivalent to wrought + full inspection + 1 test | 1.0 | §25.621(c)(1) |
| Combination | highest pertinent special factor only | §25.619 |
| Ultimate duration | 3 s without failure (static) | §25.305(b) |
| A-basis (single load path) | 99 % / 95 % | §25.613(b)(1) |
| B-basis (redundant) | 90 % / 95 % | §25.613(b)(2) |
| Fitting at ultimate [derived] | 1.725 × limit | §25.303 × §25.625 |
| AM by analogy, worst-case critical casting [derived] | 1.875 × limit (not a rule) | §25.303 × §25.621(c)(2) |

Rows run from the largest single factor down to 1.0, then the combination and basis rules, then the two derived products.

### A6 · Topology-optimisation settings (Ansys Help 2024 R2 / PADT, [FULL-WF])

| Setting | Value |
|---|---|
| Response constraint default | Mass, Percent to Retain 50 %, equality (density-based) |
| Recommended form | Range (e.g. 25–30 % retain for a ≈70 % reduction; 10–13 % in Ansys' bracket example) |
| Member size min (Program Controlled) | 2.5 × element size; ≥ 4 × with tets + Pull-Out |
| AM overhang | 45° default, 27–60°, +Z, once per analysis |
| Exclusive constraints | Overhang ✕ Member Size / Extrusion / Pull-Out; one manufacturing-constraint object |
| Complexity Index (mixable density) | 1 = bulky; 2–10 suggested |
| 2025 R2 additions | separate min/max/gap member-size categories; "Materials Optimization" multi-material method |
| Discovery | removes material only; inflation distance protects supports and loads; faceted → smoothed; "Create Validation Solution" |

### A7 · aerokit functions mapped to decisions ([K], signatures read in `src/aerokit` this session)

| Function | Decision | Inputs to source from EduPack |
|---|---|---|
| `materials.selection.rank(case, materials, co2_per_kg)` | D-01, D-07, D-09 | E, Fty, ρ (SI); CO2/kg |
| `design.sustainability.lightweighting(mass_saved_kg, fuel_fraction, missions, co2_index=3.16)` | D-05, D-20, D-21 | fuel fraction for the class; missions over life |
| `design.sustainability.eco_audit(part_mass_kg, material_co2_per_kg, manufacture_co2_per_kg, transport_co2_kg, use_co2_kg, end_of_life_co2_per_kg, buy_to_fly)` | D-10, D-17–D-22, D-06 | every per-kg factor |
| `design.sustainability.payback_missions(extra_production_co2_kg, co2_saved_per_mission_kg)` | D-23 | — |
| `python -m aerokit fem topology --problem lbracket --volume 0.3` | D-03, D-25 | — |
| `materials.eco.co2_per_kg(name, which, recycled_content)`, `eco.composite_co2_per_kg(w_f, process)`, `eco.FAMILIES`, `eco.SHAPING` | D-01, D-17, D-18, D-19 | none (A1 family values built in; replace with EduPack per-alloy values when available) |

Added after this report was written (2026-11-01): `aerokit.materials.eco` holds the A1 family values and Ashby's shaping energies (p. 133). The coordinator re-read them from the same PDF text, pp. 1–11 ([FULL-PDF]; tests in `tests/materials/test_eco.py`). Example, catalogue alloys, primary CO₂ mid values: on the `tie_strong` index Ti-6Al-4V is the lightest (7075-T6 at 1.04×), but per part it carries **3.72×** the production CO₂ of 7075-T6. On `beam_stiff` it carries 5.03× that of 2024-T351. G-07 note: `aerokit.design.sustainability` cites the ICAO CEC v8 / CORSIA source for 3.16 kg CO₂ per kg of fuel. That source was read in a previous session on 2026-10-25 and not re-read today.

---

## Gaps and what must be read from EduPack on the day

| # | Gap | Why it matters | Where to get it on the day |
|---|---|---|---|
| G-01 | Per-alloy eco values (2024, 7075, 7050, Al-Li, 6061, AlSi10Mg, Scalmalloy, 17-4PH, In718, PEEK/PEKK, IM7/8552) | Appendix A1 is family-level only | EduPack record → Eco properties |
| G-02 | Mechanical properties and allowables | All values in the notes are UNVERIFIED (memory) | EduPack (typical) or `aerokit materials allowable` (MIL-HDBK-5J) for wrought alloys |
| G-03 | Price per kg | No authoritative price series; vendor and blog snippets only | EduPack price field |
| G-04 | EduPack process rows: machining basis, any AM process, autoclave value | Decides C-08 / C-10 / C-11 | EduPack eco audit process list |
| G-05 | How the eco audit books stock mass and scrap (material phase vs "% removed") | BTF effect may land in the wrong bar | EduPack eco audit help |
| G-06 | Aircraft factor in mobile mode (MJ/t·km, kg CO2/t·km), and whether it is marginal or average | The headline use-phase number; see C-22 | EduPack eco audit → Use → Mobile |
| G-07 | CO2 per kg of jet fuel | 3.16 is unverified in the notes | EduPack fuel record |
| G-08 | Grid factor for AM electricity | Converts 60–160 MJ/kg into CO2 | EduPack country electricity mix |
| G-09 | Recycled content of aerospace Al plate | Avoids an over-credit | Leave at virgin; state it |
| G-10 | EoL options and "EoL potential" values per material, incl. CFRP downcycling | D-06 | EduPack EoL dropdown |
| G-11 | Discovery 2026 R1 topology menus (symmetry, keep-outs, overhang) | Notes rely on PADT 2020 and forums | Installed Discovery help |
| G-12 | EASA CS-25 text (25.303/613/619/621/625) | Only the FAR was read | EASA Easy Access Rules |
| G-13 | Composite CAI strain limit and hot/wet knock-downs | D-15 numbers are folklore | Material B-basis data, CMH-17 |
| G-14 | AlSi10Mg and Scalmalloy fatigue; HIP energy per kg; AM post-processing share | D-14 and D-19 sensitivity | Treat as sensitivity cases |
| G-15 | Ti–CFRP galvanic compatibility | D-16 claim is unsourced | MIL-STD-889 galvanic table |
| G-16 | Fuel factors for turboprop, business jet and helicopter; block hours per class | D-05 / D-20 when the brief is not an airliner | `aerokit` with a stated fuel fraction |
| G-17 | Jury rubric and deliverable format | D-24 | Ask Synopsys on 5 Nov (brief §7) |
| G-18 | GE load-case vectors (Fig. 2 image) | Only needed to copy the GE recipe exactly | Carter et al. Fig. 2 |

---

## Conclusion

The literature changes where the team should spend effort. Three choices often feel decisive but barely move the eco audit once the use phase is included: Ti vs Al per-kg carbon, autoclave vs out-of-autoclave, and EBM vs SLM energy. Use phase is ≥ 93 % of life-cycle energy in all four ORNL bracket rows [derived]. What moves the answer is the validated mass, which depends on the factor chain and the retain sweep, and the use-phase factor, where sources differ by about 2–4× (C-22). The team therefore wins credibility on two things. First, a validation run at 1.725 × limit that holds after reconstruction. Second, one explicit, sourced and internally consistent chain from kilograms saved to fuel to CO2, with the alternatives shown as sensitivity rather than mixed together.

There is also a methodological lesson. Two of the "conflicts" the request asked about turned out to be errors in the research notes, not in the sources. Scelsi's utilisation is 18.7 h/day, not 18,700 h/yr, and the Atescan-Yuksek whole-life ratio does not follow from the table values transcribed in the same note. A further arithmetic slip affects transport. The notes' tags tell the team how a number was obtained. They do not guarantee the arithmetic done on it afterwards. Any number that reaches a slide should be recomputed once from its tagged inputs. The same discipline applies to the reverse case: the GE bracket's 80 % and 84 % are both correctly sourced, and they disagree because the baseline masses differ.
