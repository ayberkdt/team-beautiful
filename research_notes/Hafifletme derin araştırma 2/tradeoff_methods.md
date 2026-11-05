# Multi-objective material and design trade-off methods for aerospace light-weighting (mass vs life-cycle CO2 vs cost vs manufacturability)

Scope and tag legend. Researched 2026-11-01. Tags: **[FULL]** = I read the full source text this session (PDF text extracted with `pdftotext`, or a page fetched in full). **[SNIPPET]** = search-result snippet or secondary summary only. **[FULL-2nd]** = full text of a secondary page that quotes the primary; the primary itself was not read. **UNVERIFIED (memory)** = from my training memory, not read this session. **[derived]** = my arithmetic on cited numbers. **[catalog, not re-read]** = taken from `reports\Havacılık hafifletme karar kataloğu.md` or `research_notes\Havacılık hafifletme karar kataloğu\use_phase_eol.md`. Those notes were written in an earlier session, and I did not re-open the primary this session.

Access failures this session: the ZHAW server for Steinegger (DNS failure), ScienceDirect topic pages (403), the ANSI ISO 14044 preview (403), and the SAI ISO 14044 preview (404). Full texts of Atzeni & Salmi, Rickenbacher and Jahan & Edwards were not obtained.

## Q1. Ashby penalty function and exchange constants for aerospace transport

### Takeaway
The primary, full-text source for Ashby's sector table is **Ashby, "Multi-objective optimization in material design and selection", Acta Materialia 48 (2000) 359–369, Table 3, p. 363**. It gives exchange constants in **£/kg (with $/lb in parentheses)**:

| Sector | £/kg | $/lb |
|---|---|---|
| Civil aircraft | 100–500 | 75–300 |
| Military vehicle | 500–1000 | 350–750 |
| Space vehicle | 3000–10,000 | — |

The same paper says that when α is hard to model, you can still bound it between limits and proceed. This is the basis for a defensible break-even-α argument. I could not read the textbook chapter (4th/5th ed.) this session. Its table number and page remain unverified.

### Cited Findings
- **Value function (verbatim structure), Ashby 2000, p. 362, eq. (9)–(11):** V = α1P1 + α2P2 + … + αiPi. "the values of α are exchange constants: they relate the performance metrics P1, P2, … to value, V, which is measured in units of currency". They are defined as αi = (∂V/∂Pi) with all other metrics held constant. When one objective is cost, α for cost = 1 and V = C + α2P2 + …. "The best solution is the one with the smallest value of V". **[FULL]** — [Ashby 2000, MIT-hosted PDF](https://stuff.mit.edu/afs/athena/course/4/4.464/www/MultiObjectiveOptimization-Ashby.pdf) (journal DOI from the PII in the PDF metadata: 10.1016/S1359-6454(99)00304-3, reconstructed from the PII, so treat the DOI as UNVERIFIED).
- **Table 3 "Exchange constants α for transport systems", p. 363 [FULL, same PDF].** Values as printed in the text layer:

  | Sector | Basis of estimate | α, £/kg | ($/lb) |
  |---|---|---|---|
  | Family car, structural | fuel saving | 0.5–1.5 | (0.4–1.1) |
  | Truck, structural components | payload | 5–10 | (4–8) |
  | Civil aircraft, structural | payload | 100–500 | (75–300) |
  | Military vehicle, structural | payload, performance | 500–1000 | (350–750) |
  | Space vehicle, structural | payload | 3000–10,000 | (2000–75,000) |
  | Bicycle, structural components | perceived value (price–mass plots) | 80–1000 | (50–700) |

  Caveats:
  - The currency symbol is garbled in the PDF text layer. I read it as **£** because $/lb is given separately and the ratio implies ≈1.3–1.8 $/£ **[derived]**.
  - The "basis" column alignment is my reading of a multi-column layout.
  - The space-vehicle $/lb figure "2000–75,000" does not match 3000–10,000 £/kg, which would give ≈2000–7500 $/lb. It is probably a typo in the original. Quote the £/kg column.
  - The row is "Military **vehicle**", not "military aircraft".
- **How α is derived, p. 363–364 [FULL]:** "the value of weight saving in transport systems is derived from the value of the fuel saved or that of the increased payload which this allows (Table 3)". Alternatives are historical price–mass slopes (the bicycle example, Fig. 6, "the slope −dP/dm") and interviewing techniques. Circumstances can raise α "sometimes, dramatically". Examples are an auto-maker facing fleet fuel rules, or an aero-engine maker contracted to a power-to-weight ratio.
- **Bounding α when it is uncertain, p. 368 conclusions [FULL]:** "Estimates for the exchange constants can sometimes be made by modelling, and when this is difficult it may still be possible to devise limits between which they must lie, allowing the selection to proceed."
- **Worked flip in the ranking with α, Tables 4–5, pp. 366–367 [FULL]:**
  - Stiffness-limited panel: at α = 0.5 £/kg nodular cast iron is best; at α = 500 £/kg "SR-200 grade beryllium is a better choice than any of the other materials".
  - Strength-limited panel: low-alloy steel is best at low α; Ti-6-4 is best at high α.
  - Beyond two metrics, "graphical methods cease to be useful and ranking by V … becomes the best approach" (p. 367).
- **Graphical form (Granta EduPack help) [FULL]:** "The penalty function, Z, is defined as Z = α1M1 + α2M2". "Optimum materials are those with the smallest value of Z". α2 "reflects how much the user is willing to pay for each unit of weight saving". Line form: M2 = −M1/α + Z/α, so you add "a display line of slope −1/α" to a linear-scale trade-off plot. The page has **no** sector table. — [Ansys Granta Selector help, penalty functions](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/material_selection_penalty.html)
- **Truck vs high-α example [SNIPPET]:** the truck example uses α = $5/kg. It notes that if α = $500/kg the optimal materials would be composites like CFRP. — [Ansys help, plotting a penalty function as a line](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/penalty_function_line.html)
- **Textbook pointer [FULL-2nd]:** Wikipedia says "For commercial aircraft, this number is closer to $450/kg" and "for spacecraft, launch costs around $20,000/kg dominate". It cites "Ashby, Michael F. (2005). Materials Selection in Mechanical Design. … Elsevier. p. 251", ISBN 978-0-7506-6168-3 (3rd ed.). I did **not** verify p. 251. — [Wikipedia, Material selection](https://en.wikipedia.org/wiki/Material_selection)
- **Independent cross-check, National Research Council (2003), *Materials Research to Meet 21st-Century Defense Needs*, Appendix C, printed p. 247 [FULL, page fetched]:**
  - "For a commercial aircraft, the fuel savings over a 100,000-hour life of the fuselage is $200 per pound."
  - "For military aircraft, the value can be $1,000 per pound."
  - Spacecraft: "$20,000" per lb to orbit once, or "$10,000 per pound" for the reusable Shuttle.
  - Automobile: "$2.00 over a 100,000-mile life".
  - Converted: ≈ $441/kg civil, ≈ $2,205/kg military, ≈ $44,000/kg expendable space **[derived]**.
  - — [NAP 10631, ch. 13](https://www.nationalacademies.org/read/10631/chapter/13)
- **Aircraft-specific α from fuel cost [catalog, not re-read]:** Carter et al. 2014 give $0.15–0.28 per lb per trip, i.e. $0.33–0.62 per kg per trip. — [Carter et al. 2014, p. 1404](https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf)

### Inferences
- Two independent primary sources agree on order of magnitude for civil aircraft: Ashby 100–500 £/kg (≈ 130–800 $/kg at the implied 1.3–1.65 $/£) and NRC ≈ $440/kg. The jury-safe statement is "**α_civil ≈ 10² – 10³ $/kg**, base case ≈ $400–500/kg" [derived from both].
- The textbook figures ($450/kg in the 3rd ed. per Wikipedia) fall inside the Ashby 2000 range. Cite the Acta paper as the verifiable primary and the textbook as secondary.
- Military: Ashby's 500–1000 £/kg is a *vehicle* row. NRC's $1,000/lb (≈ $2,200/kg) is the aircraft-specific value. Quote both and say which is which.
- The most defensible use of α is a **break-even α** (switch point). Compute the α at which the ranking between the two finalists flips, α* = −ΔC/Δm. Then show where α* sits relative to the 100–500 £/kg band (Ashby p. 368, "limits between which they must lie").

### Gaps
- I could not read the 4th/5th edition chapter "Multiple constraints and conflicting objectives". The table number, page and whether values were updated (e.g. to $/kg) are unverified. UNVERIFIED (memory): the 4th ed. chapter is ch. 9 and has a similar "exchange constants for transport" table.
- No Granta teaching-resource PDF reproducing the table was found. The Granta help pages read have no sector table.

---

## Q2. A CO2-vs-mass exchange constant (kg CO2 per kg mass saved) for aircraft

### Takeaway
No primary source read this session gives a ready "kg CO2 per kg saved" for aircraft. It has to be built as:

α_CO2 = (fuel saved per kg per trip) × (lifetime trips) × (kg CO2 per kg fuel)

The per-trip factor comes from Steinegger 2017 [catalog, not re-read] and the emission factor is 3.16 kg CO2/kg fuel [catalog, not re-read]. The result is ~10³–10⁴ kg CO2 per kg saved over a life, compared with ~10¹ kg CO2/kg embodied for primary Al/Ti/CFRP. This is why use-phase dominates. Carry it as a stated assumption with a range.

### Cited Findings
- **Fuel per kg [catalog, not re-read]:** marginal fuel burn 0.020–0.041 kg fuel per kg per 1,000 km (A320/A330/A380). Per trip 0.05–0.45 kg fuel/kg depending on type and stage. The paper gives no lifetime. — [Steinegger, ZHAW 2017, p. 4 Fig. 7 and p. 11 Fig. 15](https://digitalcollection.zhaw.ch/bitstream/11475/1896/2/Steinegger_Fuel_Economy_for_Aircraft_Operation_as_a_Function_of_Weight_and_Distance_v1-0.pdf) (the server was unreachable this session)
- **Snippet confirmation [SNIPPET]:** "A reduction in weight by one kg saves ~0.02 to 0.03 kg of fuel per 1'000 km"; average carry cost ≈ 0.2 kg/kg/1,000 km (total, not marginal). — [Steinegger v1-1 PDF](https://srv-clst-301-data66.zhaw.ch/bitstream/11475/1896/6/Steinegger_Fuel_Economy_as_a_Function_of_Weight_and_Distance_v1-1.pdf)
- **Airline datum [SNIPPET]:** SAA: "For each kilo of weight saved [on an international flight], we save about 300 g of fuel". — [Mining Weekly 2015](https://www.miningweekly.com/article/saa-seeks-save-fuel-by-cutting-weight-on-its-long-range-flights-2015-03-06)
- **Emission factor 3.16 kg CO2/kg fuel [catalog, not re-read]:** the project dev plan records it as "verified 2026-10-25 from ICAO CEC v8 and CORSIA Order 2021" (`docs\06_development_plan.md` line 115).
- **Lifetime basis:**
  - Scelsi et al. 2011 assume 30 yr × 14,000 km/day ≈ 150 million km [catalog, not re-read]. The catalog note flags this as physically implausible (> 8,760 h/yr at 750 km/h).
  - NRC 2003 uses a "100,000-hour life of the fuselage" [FULL, NAP p. 247 above]. That life basis can be reused for the CO2 constant.
- **Lightweighting LCA framing [SNIPPET]:** Lewis et al. (2019, Environ. Sci. Technol.) say the majority of energy spent in aircraft is used to move vehicle mass and propose 10 lightweighting principles. — [U-M CSS record](https://css.umich.edu/publications/research-publications/green-principles-vehicle-lightweighting)
- **Automotive analogue [SNIPPET]:** the "Fuel Reduction Value" (FRV, fuel saving per 100 kg mass cut) coefficient is used in vehicle lightweighting LCA. — [preprints.org supplementary](https://preprints.org/manuscript/201611.0059/v1/download/supplementary)
- **AM aircraft-bracket LCA [SNIPPET]:** Huang, Riddle, Graziano, Warren et al., J. Cleaner Production 135 (2016). It combines engineering criteria, LCI data and fleet fuel models, reports up to 6.4 % fuel reduction if all candidate parts are replaced, and gives the 1 kg bracket ≈ 10 kg raw material. — [ORNL Impact record](https://impact.ornl.gov/en/publications/energy-and-emissions-saving-potential-of-additive-manufacturing-t/)

### Inferences (worked derivation, all [derived])
- Per kg saved, using the Steinegger A320 per-trip value 0.07–0.16 kg fuel/kg at 2,000–5,000 km [catalog]:
  - CO2 per trip = 0.07–0.16 × 3.16 ≈ **0.22–0.51 kg CO2 per kg per trip**.
  - At an assumed 1,000–3,000 trips/yr × 25 yr = 25,000–75,000 trips (these utilisation figures are UNVERIFIED (memory) and must be stated by the team as assumptions):
  - **α_CO2 ≈ 5,500–38,000 kg CO2 per kg saved over life**.
- Hour-based alternative: NRC's 100,000 h × 0.02–0.05 kg fuel/kg/h (catalog band, mostly [SNIPPET]) × 3.16 ≈ 6,300–16,000 kg CO2/kg. This brackets the same order (10³.⁸–10⁴.²).
- Monetising, if the team wants a single Z: α_CO2,$ = α_CO2 (kg CO2/kg) × carbon price ($/kg CO2). No carbon price was read this session, so leave it as a named assumption. Under ISO 14044 4.4.5 (Q4), keep CO2 as a separate axis whenever the result is a public comparative claim.
- Embodied-CO2 payback for a mass-saving that costs extra production CO2: payback trips = ΔCO2_production / (0.22–0.51 kg CO2 per kg per trip × Δm). This matches `aerokit.design.sustainability.payback_missions` [catalog A7].
- Do **not** mix the marginal factor (0.02–0.04) with the average factor (0.2) or with ORNL's average-allocation intensity. The catalog C-22 entry found ORNL ≈ 1.8–3.7× higher [catalog].

### Gaps
- No peer-reviewed aircraft paper read in full this session states a "kg CO2 per kg saved" constant. One search snippet attributed "0.94 kg" CO2 per kg to Airbus with no time horizon, and I could not tie it to a specific URL, so it is **not usable**.
- Timmis et al. 2015 (Int J LCA, B787 composites) and Helms & Lambrecht 2006 were not reached.
- Lifetime utilisation (trips/yr, years) by aircraft class has no primary source read here.

---

## Q3. Pareto fronts, normalisation, weighted-sum vs TOPSIS vs AHP: which is most defensible

### Takeaway
For a jury, the most defensible chain is:

1. A **Pareto (non-dominated) trade-off plot** of the physical metrics (mass index vs CO2 vs cost), which needs no weights (Ashby 2000).
2. A **physically derived exchange constant** with a stated range, instead of subjective weights. Ashby's α is a weighted sum whose "weights" carry units and an economic meaning.
3. TOPSIS or AHP only as a **robustness cross-check**, because both depend on normalisation and suffer rank reversal.

### Cited Findings
- **Trade-off surface first, then value function [FULL]:** "trade-off surfaces give a way of visualizing the alternative compromises, and that value functions (or 'utility' functions) identify the part of the surface on which optimal solutions lie" (abstract, p. 359). The best solution is where a value-line of slope set by α1/α2 "is tangent to the trade-off surface" (p. 362). — [Ashby 2000](https://stuff.mit.edu/afs/athena/course/4/4.464/www/MultiObjectiveOptimization-Ashby.pdf)
- **Substitution test [FULL, p. 362–363]:** a candidate replaces the incumbent only if ΔV = ΔC + αΔP < 0. "while negative ΔV is a necessary condition for substitution, it may not be a sufficient one; sufficiency requires that the difference in value ΔV be large enough to justify the investment in new technology". This gives a ready-made jury caveat.
- **Normalisation changes rankings, in materials selection [SNIPPET]:** Jahan, A. & Edwards, K.L. (2015), "A state-of-the-art survey on the influence of normalization techniques in ranking: improving the materials selection process in engineering design", *Materials & Design* 65: 335–342, DOI 10.1016/j.matdes.2014.09.022. A listing summary says 31 normalisation methods were identified, classified and evaluated for materials selection. A citing paper says "most of the current normalization methods have shortcomings". — [Peeref listing](https://peeref.com/works/1029383); [Vilnius Tech WASPAS-RTB paper citing it](https://btp.vilniustech.lt/index.php/TEDE/article/download/3104/2569)
- **Yazdani, Jahan & Zavadskas [SNIPPET]:** "depending on the number of criteria and number of alternatives, material ranking can be changed when different normalization tools are considered" (COPRAS-G). — [Universidad Europea repository](https://abacus.universidadeuropea.com/entities/publication/12353667-6bf6-41b0-b133-959c5a2331a7)
- **General normalisation survey [SNIPPET]:** pairing different normalisation methods with an MCDM method "could deliver diverging results". — [PMC9433668](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9433668/); [Frontiers in Big Data 2022](https://www.frontiersin.org/articles/10.3389/fdata.2022.990699/full)
- **TOPSIS rank reversal [SNIPPET]:**
  - A 2022 *Materials Research Express* paper calls rank reversal the main drawback of traditional TOPSIS and proposes modified normalisation. — [DOAJ record](https://doaj.org/article/8780166dcfa74ab4b445710270fe238a)
  - A materials-selection paper proposes R-TOPSIS to resist rank reversal, defined as violation of the independence of irrelevant alternatives. — [UFRGS repository](https://bibliotecadigital.ufrgs.br/handle/10183/263560?show=full)
  - Foundational reference: García-Cascales & Lamata (2012), "On rank reversal and TOPSIS method", *Math. Comput. Modelling* (cited in a Springer chapter, not read). — [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-031-09577-1_3)
- **AHP rank reversal [SNIPPET]:** Belton & Gear (1983) added a copy of an existing alternative, and the previous favourite dropped to second (distributive mode). The debate with Saaty and Vargas continues, and a 2022 ISAHP paper disputes the original evidence. — [Wikipedia, Rank reversals in decision-making](https://en.wikipedia.org/wiki/Rank_reversals_in_decision-making)
- **Weight sensitivity of TOPSIS [SNIPPET, practitioner guide, low quality]:** it advises comparing equal-weight and weighted results and treating closeness differences < 0.02 as ties. — [MetricGate TOPSIS docs](https://metricgate.com/docs/topsis-multi-criteria/)
- **Jahan's book [SNIPPET, listing only]:** *Multi-criteria Decision Analysis for Supporting the Selection of Engineering Materials in Product Design* (Elsevier). — [Elsevier shop](https://shop.elsevier.com/books/multi-criteria-decision-analysis-for-supporting-the-selection-of-engineering-materials-in-product-design/jahan/978-0-08-100536-1)

### Inferences
- **Why exchange constants beat subjective weights before a jury:** α is a measurable quantity (fuel or payload value per kg, NRC/Ashby) with a published range. A % weight in AHP or TOPSIS is an opinion that a juror can simply dispute. Ashby's ranking by V needs no normalisation, because every term is already in currency. That removes the Jahan & Edwards normalisation problem entirely.
- **Weighted-sum with normalised scores** inherits both normalisation dependence and weight subjectivity. **TOPSIS** adds rank reversal when alternatives are added or removed. **AHP** adds rank reversal plus pairwise-consistency overhead. All three are fine as cross-checks, but none should be the headline.
- **Manufacturability** usually cannot be monetised in 5 h. Treat it as a **screening constraint** (pass/fail: BTF, overhang, minimum member size, NDT access) rather than a weighted objective. This keeps the objective function physical. This is a design choice, not a sourced rule.
- If a weighted MCDM is shown, report (a) two normalisations, (b) equal weights vs the chosen weights, and (c) the weight at which the winner flips. This follows from the cited normalisation and rank-reversal findings.

### Gaps
- Rao's materials-selection MCDM work (e.g. graph-theory/MADM book) was not reached.
- No full text of Jahan & Edwards 2015 was read, so its specific recommended normalisation (e.g. for target-based criteria) is unverified.
- No full-text materials paper comparing WSM, TOPSIS and AHP rankings head-to-head was read. Triantaphyllou's WSM/AHP comparison was not found.

---

## Q4. Sensitivity analysis and presenting uncertainty in comparative LCA

### Takeaway
- ISO 14044 4.4.5 forbids weighting in LCA studies used for comparative assertions disclosed to the public [FULL-2nd]. Public comparative assertions also need a panel critical review (≥ 3 members, per secondary sources).
- For uncertainty, overlapping error bars from independent Monte Carlo runs mislead. The defensible practice is **paired (dependent) sampling**, reporting the share of runs where A < B (discernibility).
- A tornado chart of one-at-a-time factor ranges is the quick 5-hour version. I found no source this session for tornado practice in LCA.

### Cited Findings
- **ISO 14044 §4.4.5 [FULL-2nd]:** "weighting … shall not be used in LCA studies intended to be used in comparative assertions intended to be disclosed to the public." (quoted by NIST BEES). — [NIST BEES "no weighting" page](https://ws680.nist.gov/BEES/(A(-2bkExZH3QEkAAAAZTMyN2UyMWEtZGYyNC00YmYxLTgzYTgtNmE3YmE3ZDUwZDU5aiUzEzepYeUldBsgBzmjmGVQkGQgUUWgnHiT6ZSU3jk1))/ViewSelectNoWeighting.aspx)
- **Clause locations [SNIPPET]:** 4.4.5 "LCIA intended to be used in comparative assertions intended to be disclosed to the public" (AS ISO 14044:2019 listing). 5.3 is further reporting for public comparative assertions, and 6.3 is the panel review. — [Standards Australia listing](https://store.standards.org.au/product/as-iso-14044-2019); [ANSI preview](https://webstore.ansi.org/preview-pages/ASQ/preview_ASQ+ANSI+ISO+14044-2006.pdf) (403 to me)
- **Panel review [SNIPPET, secondary]:** for a public comparative assertion, the review is by a panel of at least three interested parties independent of the study. — [Chalmers summary](https://webfiles.portal.chalmers.se/ita/tli/index.html@p=3683.html); [Projet Celsius blog](https://projetcelsius.com/en/blog/comparative-lca-review-panel-or-expert/)
- **Sensitivity and uncertainty analysis [SNIPPET]:** secondary sources list sensitivity and uncertainty analysis among the requirements for public comparative LCAs. The exact clause wording was not read. — [GreenCalculus](https://greencalculus.com/standards/iso-14040-14044-lca/)
- **Dependent sampling [SNIPPET]:** Heijungs and co-authors argue uncertainties in comparisons should be sampled dependently, like a paired test. Henriksson et al. 2015 (PLoS One) show strongly overlapping error bars when systems are analysed separately but a clear-cut answer under dependent analysis. — [Leiden repository item](https://scholarlypublications.universiteitleiden.nl/access/item%3A2887587/download); [Springer s11367-017-1287-x](https://link.springer.com/doi/10.1007/s11367-017-1287-x)
- **Critique [SNIPPET]:** the critique calls the method "paired or blocked simulations". — [eScholarship](https://escholarship.org/uc/item/0301m2mc)
- **Interpretation methods compared [SNIPPET]:** Mendoza Beltrán, Prado, Heijungs et al. compare discernibility analysis, the overlap area of distributions and null-hypothesis significance testing. — [Springer s11367-020-01827-4](https://link.springer.com/article/10.1007/s11367-020-01827-4)
- **Number of MC runs [SNIPPET]:** Heijungs (2019) argues the number of Monte Carlo runs should not exceed the sample sizes behind the inputs. — [AGRIS record](https://agris.fao.org/search/en/records/65dfbdae4c5aef494fe4ddc6)

### Inferences
- For a student comparison (not a public ISO claim), you may compute Z with an α_CO2. Still show CO2 on its own axis and state that it is "not an ISO 14044 comparative assertion". This pre-empts a juror who knows §4.4.5.
- 5-hour practice:
  - **Tornado:** vary each factor between its sourced low and high (α, fuel/kg/trip, trips, BTF, material CO2/kg, AM machine rate). Keep the others at base, and rank the swings in Z or in life-cycle CO2.
  - **Paired Monte Carlo:** about 1,000 draws, sampling *shared* factors (fuel/kg, trips, grid) once per draw for both designs. Report P(design A < design B).
- Both are standard practice (UNVERIFIED (memory) for tornado as LCA convention). The paired logic is sourced above.

### Gaps
- The ISO 14044 clause text itself (4.2.3.7, 5.3, 6.3) was not read. Both previews failed.
- No source read for tornado-diagram conventions in LCA.

---

## Q5. Cost models: buy-to-fly material cost, AM cost per kg, machining cost

### Takeaway
- **Machined part:** material cost = BTF × m_part × C_m. Aerospace Ti BTF can reach 25–41:1, where material is ~44 % of fabrication cost and machining ~27 % (Mitsui Seiki/Boeing slides, [FULL]).
- **Metal L-PBF:** cost is machine-time dominated (~73 % in Lindemann 2012, [FULL]). A machine-hour model gives ≈ 25–30 €/h machine rate. That is ~10² € per kg deposited for steel at 2012 build rates [derived].
- Cite Atzeni & Salmi and Rickenbacher as the model structure ([SNIPPET]), not for numbers.

### Cited Findings
- **Lindemann, Jahnke, Moi, Koch (2012), "Analyzing Product Lifecycle Costs for a Better Understanding of Cost Drivers in Additive Manufacturing", SFF Symp. pp. 177–188 [FULL].**
  - Model inputs, p. 183: "AM-machine utilization: 4500 h/year", "Depreciation time: 5 years", "Investment costs: 500,000", "Costs for maintenance 21,666 / Year", "Build rate: 6.3 cm³/h", "Build Material: Stainless Steel 316L", "Material Price 89 /kg", part volume 1 cm³, batch 190 parts per build (Fig. 4). The currency symbol is lost in the text layer; € is likely for a Paderborn paper, but I have not confirmed it.
  - Breakdown, Fig. 4, p. 184: machine 73.73 %, material 11.37 %, then post-processing, preparation, oven and build-process items of 6.65 / 4.25 / 2.62 / 1.37 %. The label-to-percentage pairing is my reading of the figure. The text states: "The major cost driver consists mainly of machine costs (73%) … followed by the material costs, which only make 12%" (p. 184).
  - Titanium "can raise costs up to nearly 50% even for low volume parts" (p. 185).
  - Optimised scenario, p. 186: 20 cm³/h, 7,800 h/yr (90 %), 40 /kg material, 320,000 investment gives "may reduce part costs by over 50%".
  - — [Lindemann et al. 2012 PDF](https://utw10945.utweb.utexas.edu/Manuscripts/2012/2012-12-Lindemann.pdf)
- **Machine-hour rate from Lindemann's inputs [derived]:**
  - Base case: (500,000 / 5 + 21,666) / 4,500 h ≈ **27 per h**, excluding overhead, gas and energy.
  - At 6.3 cm³/h × ≈7.9 g/cm³ (316L density UNVERIFIED (memory)) ≈ 50 g/h, that is ≈ **540 per kg deposited** of machine cost alone.
  - Optimised case: (64,000 + 21,666) / 7,800 ≈ 11 /h. At 20 cm³/h ≈ 158 g/h, that is ≈ 70 per kg.
- **Atzeni & Salmi (2012), "Economics of additive manufacturing for end-usable metal parts", Int J Adv Manuf Technol, DOI 10.1007/s00170-011-3878-1 [SNIPPET]:** compares HPDC with DMLS on an aluminium aircraft component and finds AM competitive for small to medium batches. A later Atzeni et al. paper compares SLM, HPDC and 5-axis machining on an aeronautical part with a break-even volume. — [UNIMORE record](https://unimore.unifind.cineca.it/resource/item/178300); [PoliTo IRIS](https://iris.polito.it/handle/11583/2460538)
- **Rickenbacher, Spierings, Wegener (2013), "An integrated cost-model for selective laser melting (SLM)", Rapid Prototyping J. 19(3) 208–214, DOI 10.1108/13552541311312201 [SNIPPET]:** it allocates per-part cost inside mixed build jobs. A 2023 paper lists per-part terms (preparation, build-job assembly, machine set-up, build, removal, heat treatment at ≈ 100 €/job). — [Emerald](https://www.emerald.com/insight/content/doi/10.1108/13552541311312201/full/html); [SN Appl Sci 2023](https://link.springer.com/10.1007/s42452-023-05382-z)
- **Quantity dependence disputed [SNIPPET]:** Baumers & Holweg report some studies find unit cost depends on quantity while others (incl. Atzeni & Salmi 2012) argue it is absent. — [Nottingham repository](https://nottingham-repository.worktribe.com/OutputFile/4894053)
- **Build-utilisation dependence [FULL, polymer LS not metal]:** Baumers, Holweg & Rowley, "The economics of 3D Printing: A total cost perspective" (Cambridge IfM, 3DP-RDM report) say "the unit cost achievable with LS is dependent on the degree of build volume utilisation" (p. 2). Multi-part LS builds typically use "5% to 10%" of the build volume, and build-failure risk is included in cost. — [IfM report PDF](https://www.ifm.eng.cam.ac.uk/uploads/Research/TEG/3DP-RDM_Total_cost_report.pdf)
- **Machine usage rate [SNIPPET]:** about $30–50/h, not including overhead, under the article's depreciation and utilisation assumptions. — [Modern Machine Shop](https://www.mmsonline.com/news/why-does-my-am-part-cost-so-much)
- **Titanium machining, Walker (Mitsui Seiki), Titanium USA 2013 slides, with contributions from Boeing, Sikorsky, Kennametal [FULL, slide text extracted; no slide numbers in the PDF]:**
  - B787 side-of-body chord open-die forgings at **41:1** (upper) and **25:1** (lower); "Buy-To-Fly 25.6:1".
  - "Typical Titanium Fabrication Costs": **Material 43.6 %, Machining 27 %, Cutter cost 10.4 %, Secondary processing 19 %**.
  - Maximum MRR by machine class: 3 in³/min (29 lb/h) light, 7 in³/min (67 lb/h) medium, 15 in³/min (145 lb/h) heavy, 35 in³/min (336 lb/h) purpose-built.
  - "Cutting Tool costs averages 30 cents per cubic inch of titanium stock removal".
  - — [Walker, TiUSA 2013](https://cdn.ymaws.com/titanium.org/resource/resmgr/2010_2014_papers/WalkerScottTiUSA2013TiMachin.pdf)
- **Derived from Walker [derived]:** $0.30/in³ ÷ 16.39 cm³/in³ ÷ 4.43 g/cm³ (Ti-6Al-4V density UNVERIFIED (memory)) ≈ **$4 per kg of Ti removed** in cutter cost. At BTF 25, a 1 kg part removes 24 kg, which is ≈ $100 of cutters.

### Inferences
- **Order-of-magnitude template for the 5-hour slot [derived]:**
  - **C_machined ≈ BTF·m·C_m + (BTF−1)·m·c_cut + t_mach·R_mach.** Use the team's own BTF (catalog D-10) and C_m from EduPack. c_cut ≈ $4/kg removed for Ti (Walker). R_mach is an assumed shop rate.
  - Walker's 43.6/27 split is a sanity check: material should be ~1.6× machining at high BTF.
  - **C_AM ≈ (t_build·R_AM + m_powder·C_powder + setup/job + HIP/heat-treat/job + support removal + machining of interfaces) / parts per build.** R_AM ≈ 11–27 /h machine-only (Lindemann inputs), or $30–50/h (MMS snippet). Machine time dominates (~73 %), so build rate and utilisation are the two levers to put on the tornado.
- These figures are 2012–2013 vintage. Build rates have risen since, so treat the AM per-kg figure as an upper bound and say so.

### Gaps
- No full-text numbers from Atzeni & Salmi or Rickenbacher (paywalled or 403).
- No sourced aerospace 5-axis shop rate ($/h). No recent (2020+) metal L-PBF $/kg benchmark was read.
- Ti-6Al-4V powder price and 316L/Ti densities are unverified here.

---

## Recommended method recipe (5-hour slot), with source per step

1. **Define function, objectives, constraints and free variables.** Example: a bracket of given stiffness and strength. Objectives are mass, life-cycle CO2 and cost. Manufacturability is treated as a constraint. — Ashby 2000, Table 1, p. 360 [FULL]
2. **Screen on manufacturability as pass/fail** (BTF threshold, AM overhang or member size, galvanic isolation) before ranking. — catalog D-02/D-10/D-11/D-16 [catalog, not re-read]; rationale in Q3 Inferences (design choice, unsourced)
3. **Compute each objective physically per candidate:**
   - m from the Ashby index.
   - C = BTF·m·C_m + machining or AM machine-hour cost (Q5 template).
   - CO2 = embodied (material × BTF + process) + use-phase m × α_CO2. — Ashby 2000 eq. 9–11 [FULL]; Lindemann 2012 [FULL]; Walker 2013 [FULL]; Steinegger and 3.16 factor [catalog, not re-read]
4. **Plot the Pareto front (mass vs cost, mass vs CO2) and drop dominated candidates.** — Ashby 2000, pp. 359, 362, 365 (Figs. 4, 8, 9) [FULL]
5. **Collapse mass and cost with the exchange constant: Z = C + α·m.** Base α = 400–500 $/kg for civil aircraft, range 100–500 £/kg; use NRC ≈ $2,200/kg for military aircraft. — Ashby 2000, Table 3, p. 363 [FULL]; NRC 2003, p. 247 [FULL]; Granta help [FULL]
6. **Report the break-even α\* = −ΔC/Δm** between the top two candidates and where it sits in the band ("limits between which they must lie"). — Ashby 2000, p. 368 [FULL]
7. **Keep CO2 as its own axis** and state that the study is not an ISO 14044 public comparative assertion, because weighting is barred there. If a single score is wanted internally, monetise CO2 with a *stated* carbon price. — ISO 14044 §4.4.5 via NIST BEES [FULL-2nd]
8. **Tornado:** swing α, fuel/kg/trip, lifetime trips, BTF, material CO2/kg, AM build rate and utilisation between sourced bounds, then rank the swings. — factor ranges from Q1, Q2 and Q5. Tornado convention UNVERIFIED (memory).
9. **Paired Monte Carlo** (shared factors sampled once per draw for both designs). Report P(A better than B), not overlapping bars. — Heijungs et al. / Henriksson et al. 2015 [SNIPPET]
10. **Optional cross-check: TOPSIS with two normalisations and equal vs chosen weights.** Show whether the winner survives, and mention rank-reversal limits. — Jahan & Edwards 2015 [SNIPPET]; García-Cascales & Lamata 2012 [SNIPPET]; Belton & Gear 1983 [SNIPPET]
11. **Jury line:**
    - "Our winner is on the Pareto front."
    - "It wins for any α above α\* = __ $/kg, and the published civil-aircraft α is 100–500 £/kg (Ashby 2000) or ≈ $440/kg (NRC 2003)."
    - "It is robust in __ % of paired Monte Carlo draws."
    - "Substitution also needs ΔV large enough to justify new technology." — Ashby 2000, p. 363 [FULL]
