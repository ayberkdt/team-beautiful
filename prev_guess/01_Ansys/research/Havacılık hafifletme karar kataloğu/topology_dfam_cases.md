# Topology optimisation & DfAM for aerospace structural components: case studies + Ansys decision list (EUROAVIA Ideathon 2026, Ansys challenge)

Research date: 2026-11-01. Researcher: sub-agent (deep-research).

**Evidence labels used below** (required by the brief):
- **[FULL-SELF]**: I extracted and read the full text myself (PDF text dump in this session).
- **[FULL-WF]**: the full page was fetched with WebFetch. A summariser model condensed it and I read that summary, which includes direct quotes. This is not a verbatim reading by me.
- **[SNIPPET]**: the claim appeared only in a web-search result summary or snippet. The page was not opened.
- **UNVERIFIED (memory)**: comes from my background knowledge and was not checked in this session.

---

## 1. Aerospace case studies: mass reduction %, material, process, load cases

### Takeaway
Published topology optimisation (TO) and DfAM cases report mass savings in two bands. Brackets that are re-designed and redesign-tested as one-off parts save about 30–84%. Structural parts that are TO'd and then sized/shaped for conventional manufacture save about 18–45% at part level, e.g. the A380 ribs. The headline percentages almost always compare against a machined or forged baseline. The only case with fully public load cases and pass/fail rules is the GE/GrabCAD bracket (2013), and its own sources disagree on the baseline mass.

### Cited Findings

**GE Jet Engine Bracket Challenge (GrabCAD, June–Nov 2013)**
- Rules: the design had to fit inside the original part envelope. Material was Ti-6Al-4V with an assumed yield strength of 131 ksi at service temperature (75°F). Minimum feature/wall thickness was 0.050 in. Interface 1 was a 0.75 in pin, treated as infinitely stiff. Interfaces 2–5 were 0.375-24 AS3239-26 bolts, also infinitely stiff. There were four load conditions (Fig. 2) and $20,000 in prizes for the top ten. [FULL-SELF] Carter et al., "The GE Aircraft Engine Bracket Challenge: An Experiment in Crowdsourcing for Mechanical Design Concepts", SFF Symposium 2014, p. 1405 (paper p. 4). https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf
- Baseline: the bracket was "made of titanium and weighs about 1.8 kg (4 lb)" and was machined from titanium bar stock. Its function is to support the cowling weight during engine service. [FULL-SELF] same PDF, p. 1403 (p. 2) and Fig. 1.
- There were almost 700 entrants. [FULL-SELF] same PDF, p. 1402 abstract and p. 1405.
- Judging Phase 1: entries were ranked by volume and checked for envelope fit. Each was then meshed and given four FE analyses, one per load case, with bolts and mounting surfaces treated as rigid. An entry was disqualified if its max von Mises stress exceeded 131 ksi. If the max was within 5% of yield, the result was scrutinised and some geometries were re-meshed finer; "in none of these cases was the outcome reversed". [FULL-SELF] same PDF, pp. 1406–1407.
- Judging Phase 2: the top ten were built on an ARCAM (EBM) machine in titanium powder, all in one build direction. Supports were removed with hand tools. Co-built tensile specimens confirmed 131 ksi yield at 0.2% offset. The parts were load-tested in a 20,000 lb frame, and judges looked for non-linearity in the load–displacement curve to detect plastic deformation. [FULL-SELF] same PDF, p. 1407.
- Result: "The winning designer was able to remove 80% of the weight of the bracket without reducing its load-bearing capacity." The abstract says some entries "achieved 80% reduction in weight". [FULL-SELF] same PDF, p. 1408 and abstract.
- Lessons: many promising entries failed the envelope check. "Many of the light entries failed to meet the yield stress requirement … some of these entrants had not performed the analysis themselves." Some files were over 300 MB and could not be meshed. [FULL-SELF] same PDF, p. 1410.
- Implementing the winning bracket would reduce GE LEAP engine weight by 1.7 kg (3.76 lbm). [FULL-SELF] same PDF, p. 1411.
- GE's own article gives different figures: original 2,033 g (4.48 lb), winner (M. Arie Kurniawan) 327 g (0.72 lb), "nearly 84 percent" lighter. Axial test load was up to 9,500 lb and the torsional test was 5,000 in-lb. "Over 700 entries". The winner received $7,000. [FULL-WF] GE Reports, "How it all began: the rise of 3D printed jet…". https://www.ge.com/news/reports/how-it-all-began-the-rise-of-3d-printed-jet
- **CONFLICT:** the baseline is ~1.8 kg / 4 lb with 80% saving in Carter et al. but 2,033 g / 4.48 lb with 84% saving in GE Reports. 2,033 g → 327 g is 83.9%. If a team quotes one figure, it should cite one source consistently.
- The other three load-case magnitudes and directions (vertical ≈8,000 lbf, horizontal ≈8,500 lbf, 42° ≈9,500 lbf) are **UNVERIFIED (memory)**. They are drawn in Carter Fig. 2, which is an image I could not read, and the GrabCAD challenge page returned HTTP 403.

**Airbus / APWorks "Bionic Partition" (A320 cabin–galley partition, 2015–16)**
- It weighs "45% (30 kg) less than current designs". It uses Scalmalloy®, "a second-generation aluminium-magnesium-scandium alloy created by APWorks". The design came from generative design with cloud computing and was then made by AM. The partition has to support crew jump-seats. The same Airbus page cites up to 465,000 t CO2/yr potential across the cabin and the A320 backlog. [FULL-WF] Airbus newsroom, 2016-03. https://www.airbus.com/en/newsroom/news/2016-03-pioneering-bionic-3d-printing
- Approximately 35 kg vs about 65 kg for a standard A320 partition. 122 Scalmalloy parts plus 40 Ti parts were printed on Concept Laser M2 and EOS M400 machines. One report gives 112 parts. Under 9 g forward acceleration it deflects 8% (9 mm) less than the honeycomb-composite partition. [SNIPPET] search summary of architectmagazine.com / tctmagazine.com etc. Not opened. Part counts conflict between sources.
- The load case was not stated on the Airbus page. The 16 g emergency-landing requirement is **UNVERIFIED (memory)**.

**Airbus A350 XWB titanium cabin bracket**
- "30% lighter than its milled equivalent", made by SLM in titanium. [FULL-WF] same Airbus newsroom page as above. No load case or absolute mass was given there.

**Airbus A380 leading-edge ribs (Altair OptiStruct)**
- A Biomimetics 2021 review section says the best-known A380 TO components are the leading-edge ribs and fuselage door intercostals, with "weight savings of approximately 1000 kg for each aircraft". The same section says Boeing 787 leading-edge ribs (topology + sizing + shape) were 24–45% lighter than the B-777's. [FULL-WF] Elelwi, Botez, Dao, Biomimetics 6(4):55, 2021, Section 1, DOI 10.3390/biomimetics6040055. https://pmc.ncbi.nlm.nih.gov/articles/PMC8544218. This is a secondary citation; the review cites earlier work.
- Altair's case study is reported to give ">500 kg per aircraft". The workflow was loads from Airbus → OptiStruct topology → refinement by detailed sizing and shape optimisation. An 18.4% rib-weight reduction appears in a WCSMO-2015 paper. A 2010 promotional article claims ">40% … 1100 lb". [SNIPPET] only. The altair.com/resource/airbus URL now redirects to Siemens, the WCSMO-2015 PDF (web.aeromech.usyd.edu.au/WCSMO2015/papers/1218_paper.pdf) returned 404, and eurekamagazine returned 403.
- **CONFLICT:** 500 kg vs 1000 kg per aircraft, depending on the source and on whether door intercostals are included.
- The primary engineering reference is Krog, Tucker, Kemp, Boyd, "Topology optimization of aircraft wing box ribs", Altair Technology Conference 2004. A related SlideShare copy by Krog, Tucker and Rollema covers leading-edge ribs, wing-box ribs, trailing-edge brackets, door stops and intercostals. [SNIPPET] https://www.slideshare.net/slideshow/airbus-topology-optimization-methods-for-optimal-aircraft-components/8693047. Not read.

**GE LEAP fuel nozzle tip (CFM LEAP, AM cobalt-chrome)**
- 25% lighter, 5× more durable, and 20 parts consolidated into 1. One GE-linked fact sheet instead says brazes/welds went from 25 to 5. Sources disagree on 19 vs "nearly twenty" nozzles per engine. It is described as the first FAA-approved AM part in a commercial engine. [SNIPPET] search summary of ge.com "fit to print", metal-am.com, etc. Not opened; the GE page I opened did not cover the nozzle.
- The nozzle is a **part-consolidation / DfAM** case, not a classic compliance-TO case. Material CoCr is **UNVERIFIED (memory)**.

**Liebherr-Aerospace spoiler actuator valve block (Airbus A380, flown 30 Mar 2017)**
- "35% lighter" with fewer parts and "the same performance as the conventional valve block made from a titanium forging". It is laser powder-bed titanium and was developed with Airbus and TU Chemnitz under partial funding from the German Federal Ministry for Economic Affairs (BMWi). It is the first 3D-printed primary flight-control hydraulic component flown on an Airbus. The press release does not say whether topology optimisation was used. [FULL-WF] Liebherr press release, 13 Apr 2017. https://www.liebherr.com/en-za/n/world-premier-first-ever-3d-printed-primary-flight-control-component-from-liebherr-aerospace-flown-on-an-airbus-aircraft-24183-6278302
- **CONFLICT:** 3dprintingindustry.com describes the baseline as "conventional milling" [SNIPPET], while Liebherr says titanium forging.

**RUAG Space antenna bracket (Sentinel satellites)**
- Mass went from 1.6 kg to 940 g ("saving of over 40%"). Minimum rigidity requirements were exceeded by more than 30%. The part is about 40 cm long, in EOS Aluminium AlSi10Mg, built on an EOS M 400 at citim GmbH with 60 µm layers in about 80 h. Two antennas plus 30 tensile specimens fit in one 400×400×400 mm build. TO used Altair CAD/FEM. Qualification included CT scans and tests deliberately above load limits; aerospace testing can be up to 80% of project scope. [FULL-WF] EOS case study. https://www.eos.info/industries/customer-success-stories/space/ruag-aerospace-3d-printed-satellite-components
- An Altair write-up says the final Sentinel-1 bracket is "half the weight", i.e. ~50% vs ~41%. The workflow was OptiStruct TO followed by CAD interpretation in solidThinking Evolve. [SNIPPET] https://altair.co.kr/c2r/ws2016/3d-printed-satellite-component-presents-lesson-rethinking-design
- **CONFLICT:** ~41% (EOS) vs ~50% (Altair). EOS gives absolute masses, so prefer it.

**Academic wing example (useful as a "student-scale" reference)**
- Span-morphing wing: SIMP with penalty p ≥ 3, a 30% volume-fraction constraint on spars, a uniform 3 mm tetrahedral mesh, a 1.5 safety factor (FAR 25.303) and a 3 g load factor. Segment mass fell from 16.3 to 7.96 kg (fixed) and from 10.3 to 4.57 kg (moving). Spars lost 50.9–67.6% and ribs 19.6–70.1% (Tables 5–6). The optimised density was remodelled to CAD and re-checked by FEA. [FULL-WF] Elelwi et al. 2021, Sections 4–7. https://pmc.ncbi.nlm.nih.gov/articles/PMC8544218

### Inferences
- The 80–84% bracket figures come from an over-designed, machined, non-flight-critical baseline: a cowling-support bracket used only during service, with a single static strength check. A credible Ideathon claim on a flight part should expect about 30–50%. The A350 bracket (30%), Liebherr (35%), RUAG (~41%) and Bionic Partition (45%) all sit in that band.
- In every case with details, the mass saving is coupled with a stated stiffness or strength requirement: RUAG +30% stiffness margin, GE yield at 131 ksi with no plastic deformation, Liebherr "same performance". Jury-facing claims should therefore pair the % mass number with the constraint that was held.
- The GE judging protocol is a ready-made validation recipe a team can copy: envelope check → one FEA per load case → von Mises < yield → re-mesh when within 5% of the limit.

### Gaps
- The exact four GE load-case vectors (Fig. 2 image). The GrabCAD page was 403 and the PDF figure is not text.
- A380 rib primary data: absolute rib mass, material (believed machined aluminium, **UNVERIFIED (memory)**), and load cases. No primary Airbus or Altair document was readable.
- Boeing TO/AM hydraulic or other parts: I found no primary Boeing source with numbers in this session. The 24–45% B787 rib figure is a secondary citation.
- Thales Alenia Space satellite brackets: not researched for lack of tool budget. I found no sourced numbers.
- Bionic Partition qualification load case (16 g or other): not on the Airbus page.

---

## 2. Ansys-specific workflow (Discovery Explore mode, Mechanical Topology Optimization)

### Takeaway
Mechanical's Topology Optimization, density-based (SIMP-type), defaults to a mass/volume response constraint of "Percent to Retain" = 50%. It supports stress, displacement, frequency, compliance and reaction-force constraints. Its manufacturing constraints are member size, pull-out, extrusion, AM overhang (default 45°, allowed 27–60°), symmetry, and cyclic/pattern repetition, but only one manufacturing-constraint object is allowed and AM-overhang cannot be combined with member size/extrusion/pull-out in the density method. Discovery's workflow runs: structural setup → add topology → volume target → convert to faceted/smoothed body → "Create Validation Solution". The Discovery-specific points come from a third-party (PADT) 2019–20 article, not from ansyshelp.

### Cited Findings

**Mechanical: response constraints (Ansys Help 2024 R2 §2.7)** [FULL-WF] https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_respsonse_constraint.html
- Mass (default) or Volume. Define By can be Constant (default), Range, Absolute Constant or Absolute Range. **Percent to Retain defaults to 50**, range 1–99. "For the Density Based Optimization method, this constraint is handled as an equality constraint."
- Global Stress (Static Structural). Stress type is Equivalent von-Mises (default), Local Equivalent von-Mises, Maximum Principal, or Local Strain Energy. Scope is Optimization Region only. The page says these have method-support requirements, and the Objective/Capability-Map topic gives them.
- Local von-Mises Stress can be scoped to geometry or named selections, including elements outside the optimisation region.
- Other constraints: displacement (nodal component max), reaction force, compliance (upper limit), natural frequency (Modal; several mode numbers allowed), centre of gravity, moment of inertia, thermal compliance/temperature, criterion.
- For shell bodies, stress constraints use "the elemental mean of the top and bottom surfaces".
- With several upstream environments ("All Static Structural"), "the application only applies the minimum number of steps as determined from the upstream analyses."
- A forum user saw the optimised peak stress come in well below the constraint, and an Ansys employee attributed it to elemental-mean values. [SNIPPET] https://innovationspace.ansys.com/forum/?p=165857. This is user-forum content, not official.

**Mechanical: manufacturing constraints (Ansys Help 2024 R2 §2.8)** [FULL-WF] https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_manufact_constraint.html
- Density-based methods offer Member Size (min/max), Pull Out Direction, Extrusion and AM Overhang. Level-set methods add min gap, stamping and no-hole options. Mixable density adds Housing and Complexity Index.
- **Member Size min, density-based, "Program Controlled"**: the application "automatically sets the minimum size at 2.5 times the mesh element size". Max size has no default and is required for casting/extrusion.
- With SOLID187 tets and Pull-Out, set the minimum member size manually to "at least four times the Tetrahedron element size".
- Level set: the value is automatically raised to four element sizes if it is too small. Min gap should be ≤ 2 × max member size.
- With Member Size min set manually, the solver performs two optimisations; the first ignores the manufacturing constraint. [SNIPPET] search summary of the same page.
- **AM Overhang: default angle 45°**, density-based range "between 27° and 60°", default build direction +Z, and it can be specified only once.
- With symmetry, the build direction must lie in the symmetry plane. With cyclic repetition it must be parallel to the cyclic axis, and with pattern repetition perpendicular to the pattern axis.
- **Unsupported in density-based:** AM Overhang + Member Size/Extrusion/Pull-Out, and Uniform + Extrusion/Pull-Out/AM-Overhang.
- Only one Manufacturing Constraint object is allowed per analysis.
- Complexity Index (mixable): 1 gives a bulky, sphere-like shape; 2–10 is suggested.

**Mechanical: TO-for-AM workflow (Ansys Help 2024 R2, Additive guide §6.1)** [FULL-WF] https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/add_ag/add_ag_adv_top_topopt.html
- A: baseline static structural. B: TO with AM Overhang (example 45°, +Z) and a Mass/Volume response constraint **Defined By Range**: "we recommend you specify a range for the response constraint rather than just a constant value". The example says a 70% mass reduction would be a 25–30% retain range; the bracket example used 10–13%. C: clean up in SpaceClaim, then validate in Mechanical ("Performing Design Validation"). D–E: AM process simulation.
- "Parts designed using the AM Overhang Constraint are constrained more and results will include more material."
- Overhang logic: an element is kept only if a supporting element at an angle ≥ the overhang angle exists below it. Contact with the base plate is required. Excluded elements always count as support, so their support is not guaranteed.

**2025 R2 release notes** [FULL-WF] https://ansyshelp.ansys.com/public/views/secured/corp/v252/en/mech_releasenotes/dsTopoAnalysisE.html
- Member Size min/max/gap are separate categories, with a new Measurement Type. Level-set Pull-Out "Both Directions" gains a Parting Surface Control Group. A new "Materials Optimization" method distributes several materials in one domain.

**Discovery (Live/Explore) topology workflow, third-party** [FULL-WF] PADT, "ANSYS Discovery Live: A Focus on Topology Optimization", 10 Mar 2020 (Discovery Live 2019 R3 / 2020 R1). https://www.padtinc.com/2020/03/10/ansys-discovery-live-a-focus-on-topology-optimization/
- Start from a structural setup (in the example, three bolt holes fixed plus a load) and add topology optimisation. The target is "reduce the total volume by a percent of the original or … until we reach a specific model volume"; the example used 30 cm³.
- Material near supports and loads is protected by an "inflation" normal distance.
- "Discovery Live can only remove material from the original geometry, it does not add." A thin region may need thickening and a re-run.
- The result is converted to a faceted body from the solution tree, with an optional smoothed version.
- **Validation:** right-click the result and choose "Create Validation Solution", which copies the geometry into a new structural analysis with the original supports and loads, run at maximum fidelity.
- The 2020 R1 additions listed are: compliance-increase objective while minimising volume, maximum thickness control, internal-overhang prevention, and link to modal.
- Numbers: the first optimised design had less than half the original volume, and validated peak stress rose from 267 MPa to about 360 MPa. Thickening the backplate, enlarging fillets and re-optimising to 30 cm³ brought the peak down to 256 MPa. Default fidelity solve time was 7 min 50 s on a Quadro K4000.
- Forum summary of Discovery goals: maximise stiffness (minimise compliance), maximise natural frequency, or balance the two. The volume constraint is a max % or max volume, and/or a target frequency. [SNIPPET] https://innovationspace.ansys.com/forum/?p=255933. Forum content, not official help.
- Ansys Discovery 2021 R2 has a "quick tip" video on activating manufacturing constraints for topology optimisation. [SNIPPET] I did not verify its contents.
- AM Overhang in Mechanical applies to the whole optimisation space, and a user question about per-part overhang went unanswered. [SNIPPET] innovationspace forum.

### Inferences
- In a 2-hour sprint, a team should not use the 50% default blindly. Set the retain target from the stress/stiffness budget and use a Range, as Ansys itself recommends.
- PADT's 267 → 360 MPa example shows the core risk: a pure stiffness/volume-driven TO result can raise peak stress by about 35%. The validation run, followed by local thickening/fillets and a re-run, is mandatory, not optional.
- Because density-based Mechanical cannot combine AM-overhang with member-size, a team must choose. If the claim is "printable without supports", use overhang. Otherwise use member size with a minimum ≥ 2.5× element size (default) or ≥ 4× for tets with pull-out.

### Gaps
- An official ansyshelp page for **Discovery** topology optimisation (Explore/Refine modes, current 2025–2026 menu names, symmetry, keep-out, overhang in Discovery) was not found. The Discovery points rely on the PADT 2020 article and forums. Verify in the team's installed version.
- The Mechanical "Objective" topic and the "Objective and Response Constraint Capability Map" (which methods support stress constraints and stress objectives) were not opened.
- The Ansys Innovation Space course page for topology optimisation was not opened, so course content is not sourced.
- No source in this session documents Discovery 2026 R1 changes. A SimuTech blog title "What's New in Ansys Discovery 2026 R1 … Structural Optimization" exists [SNIPPET, title only] (https://simutechgroup.com/resources/blog/ansys-discovery-2026-r1-structural-optimization/) but was not read.

---

## 3. Good-practice decisions for a credible ~2-hour TO run

### Takeaway
The sourced, defensible decisions are a short list:
- retain-mass range instead of a single value
- min member size ≥ 2.5× element size (≥ 4× for tets with pull-out)
- overhang 45° (27–60°) with build direction in the symmetry plane
- one FEA per load case, using the minimum common steps across environments
- validation re-analysis of the smoothed geometry
- stress check against yield with a safety factor
- re-mesh when the result is within ~5% of the limit
- only one manufacturing-constraint object

Other common practices (non-design inflation at supports, singularity handling, mesh convergence) are partly sourced and partly general knowledge, as labelled below.

### Cited Findings
- **Mass target:** use a "Percent to Retain" Range, e.g. 25–30% retain for a ~70% reduction; the bracket example used 10–13%. Default is 50% and density-based treats it as an equality. [FULL-WF] Ansys help §6.1 and §2.7, URLs above.
- **Volume fraction reference:** 30% volume fraction for wing spars in an academic SIMP study. [FULL-WF] Elelwi et al. 2021 §6.
- **SIMP penalty:** p ≥ 3 is commonly used to penalise intermediate densities. [FULL-WF] Elelwi et al. 2021 §4.1, Eq. 6.
- **Member size vs mesh:** program-controlled min = 2.5 × element size. With tet SOLID187 and pull-out, manual min ≥ 4 × tet size. Level-set raises it automatically to 4 element sizes. [FULL-WF] Ansys help §2.8.
- **Feature-size floor in a real brief:** the GE challenge set a 0.050 in (1.27 mm) minimum wall. [FULL-SELF] Carter et al. p. 1405. In Ansys terms the mesh must then be ≤ 1.27/2.5 ≈ 0.5 mm for the default member-size control to honour it (my arithmetic from the two sources).
- **Overhang:** default 45°, density-based range 27–60°, build direction +Z by default. It must lie in the symmetry plane if symmetry is used. Overhang adds material. [FULL-WF] Ansys help §2.8 and §6.1.
- **Multiple load cases:** GE judged one FEA per each of the four load cases with rigid bolts. [FULL-SELF] Carter p. 1406. Ansys "All Static Structural" uses the minimum common number of steps. [FULL-WF] Ansys help §2.7.
- **Stress vs compliance:** Ansys offers global and local von Mises response constraints (density/level-set support per the capability map, not read). [FULL-WF] Ansys help §2.7. OptiStruct guidance warns that combining a global stress constraint with a mass/volume constraint is not recommended, because the mass limit may prevent the stress constraint being met. [SNIPPET] Altair community: https://community.altair.com/discussion/4085/topology-optimization-with-optistruct-objective-minimizing-compliance. The analogous behaviour in Ansys is **UNVERIFIED**.
- **Protecting supports and loads:** Discovery's "inflation" distance keeps material around supports and loads. [FULL-WF] PADT 2020. Excluded (non-design) regions always count as overhang support. [FULL-WF] Ansys help §6.1.
- **Reconstruction:** use Discovery's convert to faceted body plus an optional smoothed body [FULL-WF] PADT, or SpaceClaim cleanup [FULL-WF] Ansys help §6.1. Industrial cases re-interpreted the TO load path as CAD: RUAG used solidThinking Evolve [SNIPPET], and the Elelwi et al. wing was remodelled to CAD [FULL-WF].
- **Verification FEA:** use "Create Validation Solution" at maximum fidelity [FULL-WF] PADT, or Mechanical "Performing Design Validation" [FULL-WF] Ansys help §6.1. GE rule: if max von Mises is within 5% of yield, re-mesh finer before deciding. [FULL-SELF] Carter p. 1406.
- **Expect stress to rise after TO:** 267 → 360 MPa before local fixes (thicker backplate, larger fillets), then 256 MPa after re-optimisation. [FULL-WF] PADT 2020.
- **File-size hygiene:** GE could not mesh some STEP files over 300 MB. [FULL-SELF] Carter p. 1410.
- **Material and process data for AM:** GE verified the as-built Ti-6Al-4V EBM yield (131 ksi) with co-built tensile bars. [FULL-SELF] Carter p. 1407. RUAG co-built 30 tensile specimens. [FULL-WF] EOS.

### Inferences
Proposed 2-hour decision list, based on the sources above. Items marked (G) are general practice not sourced in this session.
1. **0:00–0:15 Baseline:** model the existing part with real interfaces. Separate design and non-design regions: keep material around bolt holes and load faces with a ring of about 2–3 elements or a Discovery inflation distance. Run baseline static FEA and record mass, max displacement and max von Mises per load case.
2. **Load cases:** include at least 2–3 independent cases, e.g. limit load × 1.5 ultimate factor and a torsion/side case. A single-load TO gives a part that fails under the unmodelled direction; the GE brief deliberately used four cases.
3. **Objective:** minimise compliance (maximise stiffness) subject to a mass-retain Range. Add a global von Mises constraint, or check stress afterwards, only if time allows.
4. **Mass target:** run 3 points, e.g. retain 50%, 35% and 25%, to build a mass–stiffness curve (see §4) instead of betting on one value.
5. **Mesh/member size:** choose element size h so that 2.5h ≤ the minimum printable wall. For L-PBF a minimum wall of about 0.8–1.5 mm is typical, **UNVERIFIED (memory)**; GE used 1.27 mm. Discovery fidelity: draft at low fidelity, final at maximum.
6. **Manufacturing constraint:** use AM overhang at 45° with the build direction chosen and stated, OR member size, since both cannot be used together in density-based Mechanical. Symmetry is allowed if the build direction lies in the symmetry plane.
7. **Singularities (G):** do not judge peak stress at point loads, sharp re-entrant corners or fixed-support edges. Use remote points or bolt-face distributed loads, and read stress a few elements away or on fillets. This is consistent with GE's practice of treating bolts as rigid bodies over the mounting faces.
8. **Reconstruction:** convert to smoothed body, then repair gaps and add fillets at nodes. If time allows, rebuild as clean CAD (SpaceClaim/Discovery). Re-attach the original interface features exactly so the envelope and interfaces are preserved, the GE disqualification lesson.
9. **Validation:** re-run all load cases on the reconstructed geometry. Check σ_vM,max × SF < yield (or allowable), check displacement against the baseline, and if the margin is under 5%, refine the mesh once (GE rule). A two-level mesh check (h and h/2, peak stress change under ~5–10%) is (G).
10. **Report:** mass before/after (%), stiffness before/after, peak stress before/after, and the constraint held.

### Gaps
- No source in this session gives a quantitative rule for filter radius vs element size beyond Ansys' 2.5×/4× member-size rule.
- Mesh-convergence and singularity-handling guidance specific to TO validation was not sourced from a journal (e.g. Struct Multidisc Optim). Items marked (G) should be treated as general practice.
- AM process minimum wall/feature sizes for Ti-6Al-4V or AlSi10Mg L-PBF were not sourced.
- Post-processing chain (HIP, stress relief, support removal, machining of interfaces): only GE "supports removed with hand tools" was sourced. HIP/machining practice is **UNVERIFIED (memory)**.

---

## 4. Jury-friendly outputs (Pareto, before/after)

### Takeaway
The public cases present results as a before/after mass pair plus a held performance constraint: "−45% (30 kg)", "1.6 kg → 940 g, stiffness +30% over requirement", "2,033 g → 327 g, passed 9,500 lb axial and 5,000 in-lb torsion". Ansys' own guidance to specify a retain Range naturally supports a small mass-vs-stiffness sweep. I found no sourced jury rubric.

### Cited Findings
- Before/after with constraint: RUAG 1.6 kg → 940 g with rigidity requirement exceeded by >30%. [FULL-WF] EOS.
- Before/after with test evidence: GE 2,033 g → 327 g with axial 9,500 lb and torsion 5,000 in-lb tests [FULL-WF] GE Reports; ranking by lowest mass among designs meeting all criteria [FULL-SELF] Carter p. 1406–1407.
- Absolute plus %: Bionic Partition "45% (30 kg) less" [FULL-WF] Airbus. System-level translation: the GE bracket would save 1.7 kg per LEAP engine [FULL-SELF] Carter p. 1411. Fuel/$ per pound: Carter p. 1404 estimates ~$0.15–0.28 per lb per trip [FULL-SELF].
- Peak-stress before/after (honest reporting of the stress rise): 267 → 360 → 256 MPa. [FULL-WF] PADT.

### Inferences
- Recommended deliverables:
  - (a) A 3–4 point mass-fraction vs compliance (or max displacement) curve from the retain sweep, with the chosen design marked.
  - (b) A before/after table: mass, max displacement, max von Mises, safety factor, and per load case.
  - (c) Side-by-side images: raw density result → smoothed/reconstructed body → validation stress plot.
  - (d) A one-line system translation: kg saved × parts per aircraft, like GE's per-engine figure, with a sourced fuel-per-kg factor if one is used.
- Claim discipline: compare against the same material and the same load cases. State whether the baseline is machined, forged or cast, since all industrial % figures above depend on it.

### Gaps
- No public EUROAVIA/Ansys Ideathon judging criteria were found or searched for in this session.
- No published aerospace Pareto front (mass vs stiffness) from a vendor case study was found. The Pareto recommendation is an inference.
