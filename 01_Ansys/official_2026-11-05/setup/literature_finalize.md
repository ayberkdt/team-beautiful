# Literature: finalizing a SIMP topology-optimisation result for LPBF (Ti-8Al-1Mo-1V bracket)

Compiled 2026-11-05 by web search and page fetch. No PDFs were downloaded.

**Evidence tags**
- **VERIFIED-PAGE**: I fetched the HTML page in this session and the claim was on it.
- **SNIPPET**: the claim comes only from a search-engine summary. The page was not fetched, or the fetch failed (403/JS).
- **UNVERIFIED**: my own inference or general knowledge. No source was read for it in this session.

Quotes are kept under 15 words. "Fetched page" means the URL in that row.

---

## 1. Reviews and methods of geometric post-processing of TO results

| # | Source | What it says | Tag |
|---|---|---|---|
| 1.1 | Subedi, S.C., Verma, C.S., Suresh, K. (2020). *A Review of Methods for the Geometric Post-Processing of Topology Optimized Models.* J. Comput. Inf. Sci. Eng. 20(6), DOI 10.1115/1.4047429. https://par.nsf.gov/biblio/10191733 | TO outputs are triangulated meshes that are "dense, poor quality, and lack feature/parametric control." Their position: "Separation of post-processing from TO is more robust and flexible." The review sorts methods by target application and by strategy. NB: the third author is Krishnan **Suresh**. There is no separate "Krishnan" author. | VERIFIED-PAGE |
| 1.2 | Swierstra, M.K., Gupta, D.K., Langelaar, M. (2020). *Automated and accurate geometry extraction and shape optimization of 3D topology optimization results.* arXiv:2004.05448. https://ar5iv.labs.arxiv.org/html/2004.05448 | "Density-based TO results exhibit jagged and blurred boundaries." After smoothing into crisp geometry, the design "loses its optimality or even feasibility". They therefore follow it with a shape-optimisation stage. They also attribute the loss to "thresholding of intermediate densities to obtain a binary image". The level-set is shifted so the enclosed volume meets the target volume fraction. Manual redrawing is called the current bottleneck. Journal venue: the fetched page does not state it. Published in SMO per the task brief; I did not check that. | VERIFIED-PAGE (venue UNVERIFIED) |
| 1.3 | Larsen, S., Jensen, C.G. (2009). *Converting topology optimization results into parametric CAD models.* Computer-Aided Design and Applications 6(3), 407–418, DOI 10.3722/cadaps.2009.407-418 | A semi-automated method. It fits 2-D "shape templates" to cross-sections and sweeps or lofts them into parametric CAD. | SNIPPET |
| 1.4 | Ježek, O., Kopačka, J., Isoz, M., Gabriel, D., et al. (submitted 7 Dec 2025). *Smooth geometry extraction from SIMP topology optimization: Signed distance function approach with volume preservation.* arXiv:2512.06976. https://arxiv.org/abs/2512.06976 | Stage 1 builds an SDF of the density isocontours, which can be exported directly to manufacturing formats. Stage 2 refines it with RBFs. Volume-fraction preservation is a stated goal. The abstract reports **18 % lower maximum equivalent stress** than conventional post-processing. This is the closest published analogue of our pipeline. | VERIFIED-PAGE (abstract only) |
| 1.5 | Altair HyperWorks help. *Interpretation of Topology Optimization Results* (OSSmooth). https://help.altair.com/hwdesktop/hwx/topics/pre_processing/optimization/interpretation_of_topology_optimization_results.htm | The interpreted geometry is tetrameshed and inherits the boundary conditions "for quick reanalysis". "simply using a density threshold value … can be misleading" because thin low-density members can still carry load. | VERIFIED-PAGE |
| 1.6 | Re-analysis is required because performance changes. Sources: 1.2 (loses optimality or feasibility), 1.4 (max stress changes by 18 % depending on the post-processing method) and 1.5 (re-analysis is built into the workflow). | Together these support a mandatory FEA re-verification of the finalized shape. | VERIFIED-PAGE (via 1.2, 1.4, 1.5) |

## 2. Isosurface extraction and threshold choice

| # | Source | What it says | Tag |
|---|---|---|---|
| 2.1 | Lorensen, W.E., Cline, H.E. (1987). *Marching cubes: A high resolution 3D surface construction algorithm.* SIGGRAPH '87, Computer Graphics 21(4), 163–169. https://history.siggraph.org/?p=116072 | Creates "triangle models of constant density surfaces from 3D medical data". The SIGGRAPH page gives DOI 10.1145/37401.37422. Other catalogues give 37402.37422, so check the DOI before citing. Pages 163–169 come from search snippets. | VERIFIED-PAGE (pages: SNIPPET) |
| 2.2 | Threshold = volume match: Swierstra et al. 2020 (1.2) | They shift the level-set so the enclosed volume equals the TO target volume fraction. This is exactly our "volume-matching iso-level". | VERIFIED-PAGE |
| 2.3 | Altair OSSmooth (1.5) | Example parameter file uses threshold 0.3. The choice should be "based on your needs". Connection detection keeps members at higher thresholds. Extra Laplacian smoothing can drift from the density field, so check the reported smoothing error. | VERIFIED-PAGE |
| 2.4 | nTop, *Post-processing* lesson. https://docs.ntop.com/lessons/intro-to-topology-optimization/post-processing | Choose the threshold by comparing several values. A higher threshold removes more material. | VERIFIED-PAGE |
| 2.5 | Wang, F., Lazarov, B.S., Sigmund, O. (2011). *On projection methods, convergence and robust formulations in topology optimization.* SMO 43, 767–784, DOI 10.1007/s00158-010-0602-y | Heaviside projection with threshold η. Eroded, intermediate and dilated designs. Robust formulations remove one-node hinges. | SNIPPET |

## 3. Mesh smoothing

| # | Source | What it says | Tag |
|---|---|---|---|
| 3.1 | Taubin, G. (1995). *A signal processing approach to fair surface design.* SIGGRAPH '95, pp. 351–358, DOI 10.1145/218380.218473. https://history.siggraph.org/?p=118754 | Reduces "surface smoothing, or fairing, to low-pass filtering". Linear time and space. | VERIFIED-PAGE (pages: SNIPPET) |
| 3.2 | Same paper: the λ\|μ scheme | Each step is a positive-λ Laplacian step followed by a negative-μ step with μ < −λ. This counteracts the shrinkage of plain Laplacian smoothing. λ and μ must be tuned (pass-band frequency). | SNIPPET (secondary course notes, OpenFOAM docs) |
| 3.3 | Taubin, G., Zhang, T., Golub, G. (1996). *Optimal surface smoothing as filter design.* ECCV '96, LNCS 1064, 283–292, DOI 10.1007/BFb0015544 | Applies classical FIR filter design (windowing) to surface smoothing and gives faster, better filters. This is the basis of the windowed-sinc filter. | SNIPPET |
| 3.4 | VTK, *vtkWindowedSincPolyDataFilter* class reference. https://vtk.org/doc/nightly/html/classvtkWindowedSincPolyDataFilter.html | Cites Taubin 1995 and Taubin–Zhang–Golub. PassBand ranges 0–2: "A good default value for the PassBand is 0.1". "Ten or twenty iterations is all the is usually necessary" (sic). Defaults: 20 iterations, passband 0.1, feature angle 45°. Normalising coordinates improves numerical stability, but the default is off. Plain Laplacian smoothing (vtkSmoothPolyDataFilter) "can cause the geometry to shrink". | VERIFIED-PAGE |
| 3.5 | Vollmer, J., Mencl, R., Müller, H. (1999). *Improved Laplacian Smoothing of Noisy Surface Meshes.* Computer Graphics Forum 18(3), 131–138, DOI 10.1111/1467-8659.00334 | HC algorithm: pushes Laplacian-smoothed vertices back towards their previous or original positions, which prevents shrinkage. Converges for suitable α and β. | SNIPPET (Eurographics page returned 403) |

## 4. Offset-based rounding and filleting, implicit tools, commercial TO-to-CAD

| # | Source | What it says | Tag |
|---|---|---|---|
| 4.1 | Rossignac, J.R., Requicha, A.A.G. (1986). *Offsetting operations in solid modelling.* Computer Aided Geometric Design 3(2), 129–148, DOI 10.1016/0167-8396(86)90017-8. Record: https://portal.mardi4nfdi.de/wiki/Item:Q1094855 | Fetched page (zbMATH review): r-offsets of solids, CSG-based boundary evaluation, an experimental modeller. **Constant-radius rounds and fillets as combinations of grow and shrink offsets** (opening = shrink r then grow r rounds convex edges; closing = grow r then shrink r fillets concave edges). That point comes from citing literature and the author's PDF summary only. | VERIFIED-PAGE (bibliography); SNIPPET (round/fillet = open/close) |
| 4.2 | Sigmund, O. (2007). *Morphology-based black and white filters for topology optimization.* SMO 33(4–5), 401–424, DOI 10.1007/s00158-006-0087-x. https://orbit.dtu.dk/en/publications/morphology-based-black-and-white-filters-for-topology-optimizatio/ | Bibliography verified on the page. The content was not on the page: erosion, dilation, open and close operators give minimum hole size and minimum member size. | VERIFIED-PAGE (bibliography); SNIPPET (content) |
| 4.3 | Schevenels, M., Sigmund, O. (2016). *On the implementation and effectiveness of morphological close-open and open-close filters for topology optimization.* SMO 54(1), 15–21, DOI 10.1007/s00158-015-1393-y. https://orbit.dtu.dk/en/publications/on-the-implementation-and-effectiveness-of-morphological-close-op/ | "Each close or open operation ruins the effect of the preceding filters". A sequence like open→close guarantees a length scale in only **one** phase. **Relevant to our open-then-close order**: the final closing can recreate thin solid features smaller than the opening radius. Run the min-wall check *after* both steps. | VERIFIED-PAGE |
| 4.4 | nTop, *Post-processing* lesson (2.4). https://docs.ntop.com/lessons/intro-to-topology-optimization/post-processing | The workflow is the same as ours: (1) "Implicit Body from Topology Optimization"; (2) "Smoothen Body". Grid size: "start with 2x greater than the element feature size". The page also mentions a grid of half the mesh size, so the wording is ambiguous. (3) Boolean Union with the interface bodies, Blend Radius 2 mm. (4) "Boolean Intersect … with … the original CAD body". The page says nothing about re-simulation. | VERIFIED-PAGE |
| 4.5 | Ansys Innovation Courses, *CAD Conversion in Ansys Discovery Software — Lesson 3* (quadcopter landing gear). https://innovationspace.ansys.com/courses/courses/topology-optimization-of-quadcopter-landing-gear/lessons/cad-conversion-in-ansys-discovery-software-lesson-3 | Discovery facet tools "including shrink wrap, smooth, and reduce" refine the faceted TO body. It is then converted to a smooth solid and sent to Mechanical. Validation happens in a separate Lesson 4. | VERIFIED-PAGE |
| 4.6 | Ansys forum threads: Convert to Sub-D or Convert to Solid; SpaceClaim **Skin** tool for faceted data | Convert-to-solid can leave curved regions tessellated. A version-dependent facet-shelling bug was reported (2024). | SNIPPET (exact menu names unverified for our Ansys version) |
| 4.7 | Altair Inspire help, *Fit PolyNURBS to the Generated Shape.* https://help.altair.com/inspire/en_us/topics/inspire/structure/fit_polynurbs_c.htm | "It is best to smooth the results before attempting to fit a PolyNURBS". Default 2500 faces, curvature 50 %, shrinkwrap size. **Intersect** trims to the design space so the fit stays aligned with non-design regions. | VERIFIED-PAGE |

## 5. Re-inserting exact functional features; machining allowance

| # | Source | What it says | Tag |
|---|---|---|---|
| 5.1 | nTop (4.4) | Restore interfaces with a Boolean Union of the smoothed TO body and the exact interface bodies, blended at 2 mm. Then intersect with the original body. | VERIFIED-PAGE |
| 5.2 | Altair Inspire (4.7) | Intersect with the design space keeps the fit aligned with the non-design regions. | VERIFIED-PAGE |
| 5.3 | MSC Apex Generative Design help (Hexagon; mirror pages marked "outdated"), e.g. https://amendate.atlassian.net/wiki/x/GgCGY | Add a machining allowance to **all functional surfaces**, together with the non-design spaces. The software writes a *print geometry* (with allowance) and a *nominal geometry*. The allowance is applied after the optimisation and **before smoothing**. Tutorial example value: 1 mm, which depends on part size and process. | SNIPPET (page is JS-rendered; fetch returned empty) |
| 5.4 | Langelaar, M. (2019). *Integrated component-support topology optimization for additive manufacturing with post-machining.* Rapid Prototyping Journal 25(2), 255–265, DOI 10.1108/RPJ-12-2017-0246. https://research.tudelft.nl/en/publications/integrated-component-support-topology-optimization-for-additive-m | Handles "post-print machining requirements": stiffness against machining loads and "a way to handle non-design regions in an AM setting". | VERIFIED-PAGE |
| 5.5 | No standard allowance for PBF-LB. An Aalto dissertation notes their absence. Teich et al. 2021 (J. Machine Eng.) size reaming allowance from simulated distortion. | Allowance should come from predicted distortion plus roughness, not a fixed number. | SNIPPET |
| 5.6 | Protolabs Network (Hubs), *Metal 3D printing design guide.* https://www.hubs.com/knowledge-base/how-design-parts-metal-3d-printing/ | CNC machining is used where tolerances tighter than ±0.1 mm are needed. | VERIFIED-PAGE |

## 6. LPBF design rules (Ti alloys)

| # | Source | What it says | Tag |
|---|---|---|---|
| 6.1 | VDI 3405 Blatt 3:2015-12. *Additive manufacturing processes, rapid manufacturing – Design rules for part production using laser sintering and laser beam melting.* https://www.dinmedia.de/en/technical-rule/vdi-3405-blatt-3/241795108 | **WITHDRAWN.** DIN recommends DIN EN ISO/ASTM 52911-1:2020-05 and 52911-2 instead. Cite 52911-1, not VDI 3405-3. | VERIFIED-PAGE |
| 6.2 | ISO/ASTM 52911-1:2019. *Additive manufacturing — Design — Part 1: Laser-based powder bed fusion of metals.* | PBF-LB/M design recommendations. Contents include support design and **powder residue removal**. Extends 52910. Numeric values not seen. | SNIPPET (iso.org 403) |
| 6.3 | ISO/ASTM 52910:2018. *Additive manufacturing — Design — Requirements, guidelines and recommendations.* | General DfAM guidance. Explicitly not process- or material-specific data. | SNIPPET |
| 6.4 | Kranz, J., Herzog, D., Emmelmann, C. (2015). *Design guidelines for laser additive manufacturing of lightweight structures in TiAl6V4.* J. Laser Appl. 27(S1), S14001, DOI 10.2351/1.4885235. https://tore.tuhh.de/entities/publication/434fa4a1-6587-48b1-8aca-3aa828ec9012 | Ti-6Al-4V walls, bars and bores built at several orientations. Catalogue per DIN 2222. **The abstract gives no numbers.** | VERIFIED-PAGE (no numerics) |
| 6.5 | Langelaar (2016/2017). *An additive manufacturing filter for topology optimization of print-ready designs.* SMO, DOI 10.1007/s00158-016-1522-2 | Critical self-supporting overhang angle "typically amounts to 45°" (cites Wang 2013, Mertens 2014, Kranz 2015). | SNIPPET (Springer redirected to login) |
| 6.6 | Xometry Pro (8 Oct 2024). *9 Mistakes To Avoid When Designing for Direct Metal Laser Sintering (DMLS) 3D Printing.* https://xometry.pro/en-eu/articles/dmls-design-tips/ | Min wall 0.8 mm in general, 1 mm supported, 1.2 mm unsupported. Min hole Ø1 mm. Holes 0.5–6 mm print without support; larger holes need orientation changes or supports. Self-supporting ≥ 45° (the page also says 30°, internally inconsistent). Powder escape holes 2–5 mm. Add fillets or chamfers at corners and overhangs. Tolerance ±0.1–0.2 mm. | VERIFIED-PAGE |
| 6.7 | Protolabs Network (Hubs) (5.6) | DMLS/SLM: min wall 0.4 mm, unsupported edge 0.5 mm, min hole Ø1.5 mm, overhang **50°**. Teardrop for horizontal holes. | VERIFIED-PAGE |
| 6.8 | Renishaw, *Design for metal AM – a beginner's guide*. Laser-melting slide deck | Overhangs below 45° to the plate need support. Round lateral holes below about 10 mm self-support. Teardrop or diamond holes need no internal support. | SNIPPET (the Renishaw page I fetched had no such text) |
| 6.9 | Grünewald et al. (2021, Metals), Ti6Al4V overhangs | Down-skin roughness rises as the overhang angle falls. Tuned pulsed exposure reached about 20°. The 45° limit is a parameter-dependent rule of thumb. | SNIPPET |
| 6.10 | Adam, G.A.O., Zimmer, D. (2014). *Design for Additive Manufacturing—Element transitions and aggregated structures.* CIRP J. Manuf. Sci. Technol. 7(1), 20–28, DOI 10.1016/j.cirpj.2013.10.001 | Design-rule catalogue for LS, LM and FDM, including element transitions (edges, fillets) and overhangs. | SNIPPET |
| 6.11 | Ti-8Al-1Mo-1V specifically | **No Ti-8-1-1 LPBF design guide was found.** Every number above is for Ti-6Al-4V or generic metal LPBF. Applying them to Ti-8-1-1 is an assumption. | UNVERIFIED |
| 6.12 | Ansys Additive, EOS, GE Additive design guides | Searched. No HTML page with numeric rules was found or fetched. | n/a |

## 7. Fillet radius vs stress concentration

| # | Source | What it says | Tag |
|---|---|---|---|
| 7.1 | Pilkey, W.D., Pilkey, D.F., Bi, Z. (2020). *Peterson's Stress Concentration Factors*, 4th ed., Wiley, ISBN 978-1-119-53251-4. https://www.wiley-vch.de/en/areas-interest/engineering/peterson-39-s-stress-concentration-factors-978-1-119-53251-4 | Bibliography verified. The shoulder-fillet chapter (Ch. 3) comes from a TOC listing. | VERIFIED-PAGE (bibliography); SNIPPET (TOC) |
| 7.2 | Curve fit after Pilkey (2005), *Formulas for Stress, Strain, and Structural Matrices*, 2nd ed., as implemented at https://amesweb.info/stress-concentration-factor-calculator/shoulder-fillets-in-flat-bar.aspx | Flat bar with opposite shoulder fillets, Kt = C1 + C2(2h/D) + C3(2h/D)² + C4(2h/D)³, with coefficients in √(h/r) for 0.1 ≤ h/r ≤ 20. My evaluation for bending, D = 60 mm, d = 30 mm (h = 15 mm) is in the table below. | VERIFIED-PAGE (formula); numbers computed by me |
| 7.3 | Mraz, S.J. (9 Jan 2009). *Shoulder-Fillet Stresses Finesse.* Machine Design (Tipton, Sorem, Schmidt, Univ. Tulsa). https://www.machinedesign.com/3d-printing-cad/fea-and-simulation/article/21832451/shoulderfillet-stresses-finesse | Peterson's shaft-shoulder equations "can underestimate the stress concentration … by as much as 24%". This supports FEA re-verification over handbook Kt values. | VERIFIED-PAGE |

**Kt for a flat bar in bending, D/d = 2 (my calculation with the 7.2 formula):**

| r (mm) | r/d | Kt |
|---|---|---|
| 2 | 0.067 | 2.22 |
| 4 | 0.133 | 1.78 |
| 8 | 0.267 | 1.34 |
| 12 | 0.40 | 1.24 |
| 15 | 0.50 | 1.20 |
| 20 | 0.67 | 1.16 |

Returns diminish beyond r/d ≈ 0.25–0.3.

---

## Implications for our finalize parameters

Our case: voxel h = 7.8 mm, bores Ø60, Ti-8-1-1, LPBF, build direction +z.

| Parameter | Recommendation | Basis |
|---|---|---|
| Working grid after upsampling | ≤ h/2 = 3.9 mm. Preferably h/4 ≈ 2 mm so that 2–5 mm fillets and the Ø60 bores resolve. | nTop gives a grid-size rule but its wording is ambiguous (4.4, VERIFIED-PAGE). The h/4 choice is my inference (UNVERIFIED). |
| Iso-level | Solve by bisection so that V(iso) = V_TO within ±0.5 % on the smoothed, upsampled field, *before* adding features. Log the iso value. Do not use a fixed 0.5 or 0.3. | Swierstra 2020 volume-matched level-set (1.2, VERIFIED-PAGE). Altair's 0.3 is only an example (2.3). The ±0.5 % tolerance is mine (UNVERIFIED). |
| Opening radius r_o (convex rounding, flap removal) | r_o ≈ 1 voxel ≈ 6–8 mm. It must stay below half the thinnest load-carrying member in the TO result, otherwise opening deletes the member. Check member survival with a component count before and after. | Rossignac & Requicha 1986 (4.1, SNIPPET for open/close semantics). The radius rule is my geometric inference (UNVERIFIED). Altair warns that thin members carry load (1.5, VERIFIED-PAGE). |
| Closing radius r_c (concave fillets) | r_c ≈ 8 mm at member roots, where d is about 30 mm, giving r/d ≈ 0.27 and Kt ≈ 1.34 vs 2.22 at 2 mm. Above r/d ≈ 0.4 the gain is small (Kt 1.24 → 1.16) while mass grows. | Pilkey formula (7.2, VERIFIED-PAGE, my numbers). Peterson may under-predict by up to 24 % (7.3), so FEA governs. |
| Order of open and close | Open then close is fine, but closing can re-create thin solids. Run the min-wall check on the **final** mesh, not after opening. | Schevenels & Sigmund 2016 (4.3, VERIFIED-PAGE). |
| Feature blend at boss, eye and flange unions | 2 mm blend in nTop's example. For our scale, apply the same r_c (≈ 8 mm) via the closing step after the union. | nTop 2 mm (4.4, VERIFIED-PAGE). Scaling it to 8 mm is my choice (UNVERIFIED). |
| Final mesh smoothing | Windowed-sinc, passband 0.1, 10–20 iterations, normalised coordinates. Or Taubin λ\|μ. Never plain Laplacian. **Freeze vertices on exact bores and mating faces**, or smooth before the exact CSG, so the exact geometry is not perturbed. Report the max vertex displacement. | VTK (3.4, VERIFIED-PAGE). Taubin (3.1/3.2). Freezing vertices is my inference (UNVERIFIED), consistent with Apex's "allowance before smoothing" ordering (5.3, SNIPPET). |
| Min wall thickness check | Manufacturing gate ≥ 1.2 mm (unsupported, most conservative source). Our members are around 10× thicker, so the gate that binds in practice is FEA resolution: ≥ 2 elements through thickness (UNVERIFIED rule of thumb). | Xometry 0.8/1.0/1.2 mm (6.6, VERIFIED-PAGE). Hubs 0.4 mm (6.7, VERIFIED-PAGE). |
| Overhang check (+z build) | Flag down-facing area with surface inclination < 45° from horizontal, i.e. normal n_z < −cos 45° ≈ −0.707. Also report it at 50° (Hubs) as a sensitivity. | 45°: Xometry (6.6, VERIFIED-PAGE), Langelaar (6.5, SNIPPET), Renishaw (6.8, SNIPPET). 50°: Hubs (6.7, VERIFIED-PAGE). |
| Ø60 bores | Ø60 is far above the 6–10 mm self-supporting hole limit. Vertical (+z-axis) bolt bores are fine. **Horizontal lug pin bores** need internal support, a teardrop or diamond print profile, or printing undersize/solid and boring. | Xometry 6 mm (6.6, VERIFIED-PAGE). Renishaw ~10 mm and teardrop/diamond (6.8, SNIPPET). |
| Machining allowance | Print geometry = nominal + 1 mm stock on bores, bolt seats and the base mating face (1–2 mm if distortion is unknown). Run FEA on the **nominal** geometry. Bores and pin fits need better than ±0.1 mm, so they must be machined. | Apex example 1 mm, all functional surfaces (5.3, SNIPPET). Hubs ±0.1 mm → CNC (5.6, VERIFIED-PAGE). No standard exists (5.5, SNIPPET). 1–2 mm is my range (UNVERIFIED). |
| Enclosed voids | Target 0. If any survive, either fill them or add ≥ 2 escape holes of 2–5 mm. Filling is the default for a TO bracket. | Xometry (6.6, VERIFIED-PAGE). ISO/ASTM 52911-1 covers powder removal (6.2, SNIPPET). |
| Islands | Keep only the largest connected component that touches the bolt and pin features. Log the volume of everything removed. | Standard practice (UNVERIFIED). Swierstra's thresholding-loss argument applies (1.2). |
| Re-verification | Mandatory FEA on the finalized nominal geometry. Compare compliance and max von Mises with the TO result. Accept only after a new margin check. Expect changes in both directions: Ježek et al. report −18 % max stress from SDF smoothing, while Swierstra et al. report possible loss of feasibility. | 1.2, 1.4, 1.5, 7.3 (all VERIFIED-PAGE). |

**Gaps.** I found no source for:
- Ti-8Al-1Mo-1V LPBF design numbers (6.11)
- numeric content of ISO/ASTM 52911-1
- EOS, GE or Ansys Additive guides

The open/close = round/fillet equivalence rests on SNIPPET-level evidence for Rossignac & Requicha. It is also standard mathematical morphology, but I read no primary text for it.
