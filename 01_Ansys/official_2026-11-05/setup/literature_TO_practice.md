# Literature / industry practice for the TO setup (non-design regions, lugs, load cases)

Compiled 2026-11-05 by web search plus HTML page fetches. No PDFs were downloaded.
Labels: **VERIFIED-PAGE** means I fetched the HTML page this session and the quote comes from it.
**SNIPPET** means I only saw the search-engine summary, not the page. **UNVERIFIED** means it is my own
recollection or inference and has no source read this session.

---

## 1. Non-design / exclusion / frozen regions at bolt and pin interfaces

### Ansys Mechanical (Structural Optimization, 2024 R2 help)
- Source: "2.4. Define Optimization Method and Regions",
  https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/mech_struct_opt/ds_topo_opt_region.html (VERIFIED-PAGE)
  - Purpose: exclusion region properties let you specify a region "to be excluded from optimization."
  - The default for *Defined By* is *Boundary Condition*. The options are All Boundary Conditions / All Loads / All Supports / None.
    The page gives no default for the sub-option.
  - Recommendation: "Ansys strongly recommends that, at a minimum, you specify the option All Loads".
  - Exclusion thickness: Program Controlled by default, which is "two times the average element size."
    Per the search snippet, this property exists only for the Level Set, Mixable Density and Shape types
    (SNIPPET, not re-checked on the page).
- 2025 R1 release notes (SNIPPET only): the default Optimization Type changed to *Mixable Density*.
  https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/mech_releasenotes/dsTopoAnalysisE.html
- **Implication for us:** in Ansys practice the faces carrying loads (the pin bore) are excluded by recommendation, and the
  supports (bolt bores) usually are too. The excluded layer is only about 2 elements thick, so the tool keeps a thin skin,
  not an engineering-sized boss.

### Ansys Discovery
- (SNIPPET only, page fetch returned navigation only) Ansys Knowledge FAQ, https://innovationspace.ansys.com/knowledge/?p=160280 .
  The summary says there is no standard exclude feature, and the workarounds are a small pressure or a 0 kg dummy mass on faces to keep.
  The Discovery 2026 R1 overview (https://simutechgroup.com/resources/blog/ansys-discovery-2026-r1-structural-optimization/)
  mentions "protected regions". UNVERIFIED: how that feature works.

### SOLIDWORKS Simulation (comparison point for defaults)
- (SNIPPET only, help pages are JavaScript-rendered and the fetch returned nothing)
  https://help.solidworks.com/2019/english/SolidWorks/cworks/hidd_topology_options.htm . Per the summary, faces with loads
  and fixtures are frozen automatically by default. The Preserved Region manager adds faces with a "Preserved Area Depth".

### Altair OptiStruct
- Official help "Design Space", https://help.altair.com/hwdesktop/hwx/topics/chapter_heads/design_space_c.htm (not fetched).
- Altair community answer (SNIPPET): regions that must survive have to be non-design properties, and only the design property
  is put in the topology DESVAR.
  https://community.altair.com/discussion/21628/problems-with-defining-geometry-for-topology-optimization
- Same forum (SNIPPET): OptiStruct may not connect all bolt holes with material. This matches our failure mode.
- OptiStruct also has a "boundary skip" option that leaves loaded or constrained nodes out of the design domain
  (SNIPPET, https://2017.help.altair.com/2017/hwsolvers/dtpg.htm).

### GE Jet Engine Bracket Challenge (GrabCAD 2013) and papers on it
- Challenge page https://grabcad.com/challenges/ge-jet-engine-bracket-challenge returned HTTP 403, so the rules were not read.
- "SimJEB: Simulated Jet Engine Bracket Dataset" (Whalen, Beyene, Mueller), https://arxiv.org/html/2105.03534 (VERIFIED-PAGE):
  - entries "were required to have four bolt holes and an interface hole in specific locations"
  - "Entries were limited to designs that fit within a provided package space"
  - The four cases are vertical, horizontal, diagonal and torsional. Bolts are rigid RBE2 elements with an SPC at the centre,
    and the load reaches the pin bore through an RBE3 spider.
  - The paper says nothing about a clevis keep-out or a minimum material ring.
- Load magnitudes (SNIPPET only, secondary sources: a student write-up on slideshare and the CAESS case study PDF, not opened):
  8000 lb vertical, 8500 lb horizontal, 9500 lb at 42 deg, 5000 lb-in torsion at the pin/clevis centre. Treat as UNVERIFIED.
- Carter et al. 2014 SFF paper, URL https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf ,
  title begins "The GE Aircraft Engine Bracket Challenge:". The full subtitle ("An Experiment in Crowdsourcing for
  Mechanical Design Concepts") is UNVERIFIED. It is a PDF and was not opened.
- dolfiny demo "topopt 3d ge bracket", https://dolfiny.uni.lu/structural-optimisation/topopt-3d-ge-bracket (VERIFIED-PAGE):
  - uses "the bolt volumes where the density is fixed to 1"
  - reason: "the bolts need to be in contact with solid material."
  - uses a Helmholtz filter (Lazarov & Sigmund 2010) and models the torsion case as a force couple.
- CalculiX BESO wiki "Example 2: engine bracket", https://github.com/calculix/beso/wiki/Example-2:-engine-bracket (VERIFIED-PAGE):
  - "Geometry was divided by intersections to obtain non-design space around bolts and a pin."
  - It notes that a larger non-design space around the bolts could lower stress concentration. No dimensions are given.
- COMSOL "Bracket — Topology Optimization",
  https://doc.comsol.com/6.3/doc/com.comsol.help.models.opt.bracket_topology_optimization_stl/bracket_topology_optimization_stl.html (VERIFIED-PAGE):
  - "the circles around the holes can be excluded from the design space"
  - It also warns that a stiff design "can be quite different from finding a design that does not fail".

**Takeaway:** every reproduction of the GE bracket freezes solid volumes around both the bolts and the pin/clevis. None of the
pages I read gives a numeric ring size. The size is a designer choice. Bolt seating (washer OD, see section 4) and lug
rules (section 3) are the defensible ways to set it.

## 2. Keeping the mounting face / flange (base plate) as non-design
- I found no source read this session that explicitly prescribes freezing the whole base plate.
- Supporting practice:
  - The SimJEB/GE entries keep fixed interface geometry.
  - The level-set bracket paper treats the payload box, supports and bolts as non-design (SNIPPET, https://arxiv.org/pdf/1909.10703, PDF not opened).
  - The SolidWorks default freezes all faces with fixtures (SNIPPET, see above).
- UNVERIFIED (engineering reasoning, not literature): a support on the bolt bores alone lets SIMP delete the plate between
  them. Freezing a minimum-thickness skin of the plate, or adding the bolt seat or mating face as a support or exclusion,
  keeps the interface continuous. This is how the Ansys "All Supports" exclusion would treat the plate faces if the
  support were put on the mating face.

## 3. Lug (pin-loaded) design rules
- Air Force Flight Dynamics Lab "Stress Analysis Manual" (Oct 1986), lug chapter, as reproduced at
  "Lug Analysis", https://engineeringlibrary.org/reference/lug-analysis-air-force-stress-manual (VERIFIED-PAGE):
  - "For values of e/D less than 1.5, lug failures are likely to involve shear-out or hoop tension."
  - Above 1.5, "the bearing is likely to be critical."
  - The K chart (Fig. 9-2) "applies only to cases where D/t is 5 or less".
- MechaniCalc "Lug Analysis", https://mechanicalc.com/reference/lug-analysis (VERIFIED-PAGE):
  - the Air Force method "follows closely with the methods presented in Melcon & Hoblit and Bruhn."
  - It gives no explicit minimum e/D.
- ESDU 91008: the title is "Strength of lugs under axial load" (SNIPPET from the IHS/GlobalSpec listing; that page returned 403).
  Transverse loads are covered by ESDU 06021 and oblique loads by ESDU 08007 (SNIPPET).
- Melcon & Hoblit (1953, Product Engineering) are cited as the origin of the method together with Cozzone (SNIPPET).
- UNVERIFIED (common practice, not read this session): e/D of about 1.5 or more is the usual design target, so that bearing
  rather than shear-out governs. e/D below about 1.0 is avoided.
- **Arithmetic for our lug (D = 60 mm, t = 70 mm):** D/t = 0.86, which is within the Fig. 9-2 range.
  - e/D = 1.5 means e = 90 mm from the pin centre to the lug edge.
  - A frozen ring of 0.75·r = 22.5 mm gives an outer radius of 52.5 mm, so e/D = 0.875. That is well inside the
    shear-out/hoop-tension regime, and a ring of that size is not a "lug" by these rules.

## 4. ISO 7089 washer for M56 / ISO 273 clearance holes
- ISO 7089 M56, from Westfield Fasteners "Washer ISO7089 M", https://www.westfieldfasteners.co.uk/Standards/Washer-ISO7089-M.html
  (VERIFIED-PAGE, supplier table, not the standard itself):
  - d1 nom 62.00 (max 62.74), d2 nom 105.00 (min 103.60), h 10 mm.
  - The supplier accu-components lists 62 / 105 / 11 mm (SNIPPET), so the thickness is inconsistent between sources.
- Arithmetic: washer OD/2 = 52.5 mm = r + 0.75·r for r = 30 mm. Our current 0.75·r bolt ring is therefore exactly the
  washer seat footprint, with no margin.
- ISO 273:1979 "Fasteners - Clearance holes for bolts and screws", https://www.iso.org/standard/4183.html (SNIPPET).
  It covers 1 to 150 mm in fine, medium and coarse series. The M56 values 58 / 62 / 66 mm are UNVERIFIED (from recollection;
  the table was not read). If they are right, our Ø60 bore sits between fine and medium.

## 5. Multiple load cases: weighted sum vs min–max
- Zhang, de Sturler, Paulino, "Stochastic Sampling for Structural Topology Optimization with Many Load Cases: Density-Based
  and Ground Structure Approaches", https://ar5iv.arxiv.org/html/1609.03099 (VERIFIED-PAGE):
  - weighted sum: "minimizes a weighted sum of the vector of compliances from all load cases" [ref 4 = Bendsøe & Sigmund 2003, Springer]
  - min–max: "minimizes the worst-case compliance, or the infinity-norm, of all load cases" [ref 6 = Achtziger 1998, JOTA 98(2):255–280]
- dolfiny GE bracket demo (VERIFIED-PAGE): it sums compliances and notes that "Other options include minimising the maximum
  compliance or minimising a weighted sum of compliances."
- Standard book: Bendsøe M.P., Sigmund O., *Topology Optimization: Theory, Methods, and Applications*, Springer 2003.
  The citation is verified through ref [4] above. The chapter or page number is UNVERIFIED.
- UNVERIFIED (standard practice): min–max is usually implemented as a bound formulation, min β s.t. c_i/c_i0 ≤ β, which MMA
  handles directly. With a weighted sum, a weak load case such as our torsion can be under-served when its normalised share
  is small.

## 6. Symmetry constraints in density-based TO
- Altair OptiStruct "Pattern Grouping",
  https://2025.help.altair.com/2025/hwsolvers/altair_help/topics/solvers/os/topology_opt_pattern_grouping_r.htm (VERIFIED-PAGE):
  - one-plane symmetry needs "an anchor grid and a reference grid"
  - "A symmetric mesh is not necessary."
- COMSOL bracket example (VERIFIED-PAGE): two load cases "actually corresponds to four load cases, because symmetry is imposed"
  through the Mirror Symmetry feature.
- nTop "Planar Symmetry Constraint", pyMOTO flexure example, COMSOL "Mirror Symmetry" (SNIPPET only).
  The common method is to tie mirrored elements to one master design variable and map that variable before the density
  filter and projection.
  https://docs.ntop.com/Product-Documentation/ntop/block-documentation/blocks/optimization/constraints/planar-symmetry-constraint
  https://pymoto.readthedocs.io/en/latest/auto_examples/topology_optimization/ex_flexure.html
- UNVERIFIED (implementation note): in a voxel SIMP code the simplest equivalent is x_full = 0.5·(x + mirror(x)) applied to
  the design field before filtering, with sensitivities symmetrised the same way. This only holds if the loads are
  symmetric or the load cases are mirror pairs. Our ±24 kN lateral components are mirror pairs.
