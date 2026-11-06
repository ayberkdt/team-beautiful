# Topology optimisation v2: what was wrong in v1 and what changed (5 Nov 2026)

## 1. What was wrong in v1 (`runs/topo_fixed_bores`, 25 % layout)

Read from `src/aerokit/bracket/features.py::non_design_mask` and `pipeline.py` as they were, and from
`runs/topo_fixed_bores/figures/f5_shapes.png`:

* The only frozen (non-design) regions were rings of 0.75·r around each hole: bolt bores r 30 → 52.5 mm and pin
  bores r 30 → 52.5 mm (12.6 % of the part). The base plate and the lug bodies were fully free.
* The optimiser therefore deleted the base plate between the bolts. Each lug became an arch standing on its own two
  bolt pads, and the two lugs were joined only by a thin bridge: structurally two separate brackets, with no
  continuous mounting face.
* The lug eyes were perforated just outside the 52.5 mm ring (holes visible in panel b). The original eye has 61.4 mm
  of edge distance above the pin centre (pin at z 260, arc R80 centred at z 241.37). v1 kept only 22.5 mm of the
  31.4 mm ligament.
* Torsion LC2 **was** in the optimisation, with equal weight. The weights are 1/C₀ per case (`pipeline.py`, the
  normalised weighted-sum formulation), so LC2 was not lost.
* A volume fraction below the frozen fraction was rejected only after all earlier layouts had run, and nothing was
  written (24 min lost on 5 Nov).

## 2. v2 set-up (`setup/setup_official_v2_base_kept.json`)

| Item | v2 |
|---|---|
| Supports | Fixed Support on the 4 bolt bores Ø60, z 30–100 (unchanged locations and distances: card requirement) |
| LC1a / LC1b | **each lug** (each pin bore): F = (0, ±24, 97) kN. Fz as bearing load on the upper half of the bore; Fy uniform on the bore |
| LC1c | each lug, opposite Fy (+24 on H1, −24 on H2). Sensitivity case |
| LC2 | torsion My = 2000 N·m about the pin axis y, 1000 N·m per lug bore, rigid distribution |
| Verification only | LC1a/LC1b + LC2 with ±My (combined, our conservative extra). Compliance does not depend on the sign of a single load (c(−F) = c(F)), so one sign of My in the optimisation is enough |
| Non-design: bolt bosses | r 30 → 52.5 mm (Ø105) over the full plate depth z 30–100. The fixed faces and the seat under the bolt stay |
| Non-design: lug eyes | r 30 → 61.4 mm (ring factor 1.047) over each lug thickness (70 / 71.12 mm). This is the ORIGINAL edge distance above the pin, so the hinge is not thinned |
| Non-design: base skin | the original footprint, z 30–46 (2 voxel layers = 15.6 mm), corner radii R100 kept. One continuous mounting flange ties both lugs and all four bolts |
| Frozen fraction | 0.2946 (supports 0.0841, lug eyes 0.0634, base skin 0.1471) — printed by `scratchpad keepfrac.py` and the run log |
| Volume fractions | 0.45, 0.38, 0.33 (all > frozen fraction + 0.01; checked up front now) |
| Optimiser | SIMP p = 3, density filter rmin = 2 voxels (15.6 mm), Heaviside projection with β continuation, OC, 50 iterations, weighted sum of compliances normalised by each case's initial compliance |

The base-skin thickness equals the filter's length scale (2 voxels). A thinner frozen layer would sit below the
smallest member the filter can resolve.

## 3. Code changes

* `features.non_design_mask`: `non_design.ring_factor_by_role` (a ring size per role: support / load); the existing
  `boxes_mm` now carries the base skin.
* `pipeline.run_design`: rejects volume fractions ≤ frozen fraction + 0.01 **before** any solve, and logs the
  frozen fractions.
* `analysis/verify_v2.py` (new), an independent check of every v2 layout:
  * the 4 card cases plus 4 combined cases, on a conforming T10 mesh;
  * the organisers' Ti-8Al-1Mo-1V data at 23 °C and with the 300 °C knock-downs;
  * connectivity: one component, and both lugs tied through the plate region z < 100 mm;
  * x-mirror symmetry.

## 4. Literature basis

Sources with URLs and evidence levels are in `setup/literature_TO_practice.md`. That file was written by a research
subagent; VERIFIED-PAGE = page read in this session. How each source maps onto v2:

| Practice in the literature | Source (evidence level) | v2 |
|---|---|---|
| Boundary-condition faces are excluded from removal. The default exclusion is a skin of 2 × average element size, and loading with "All Loads" is strongly recommended | Ansys Mechanical 2024 R2 help, *Define Optimization Method and Regions* (VERIFIED-PAGE) | bolt and pin bores frozen. All 4 card cases are in the objective |
| Published GE-bracket TO studies freeze solid volumes at the bolts and at the pin/clevis | SimJEB arXiv 2105.03534; dolfiny 3-D GE bracket demo; CalculiX BESO engine-bracket example; COMSOL Bracket TO (VERIFIED-PAGE) | bolt bosses through the full plate depth; full lug eye |
| Bolt seat = washer footprint. ISO 7089 M56: d2 = 105 mm | supplier table (VERIFIED-PAGE) | boss Ø105 = r + 0.75 r |
| Lugs with e/D < 1.5 are likely to fail in shear-out or hoop tension | Air Force Stress Manual, *Lug Analysis* (VERIFIED-PAGE) | the original lug has e/D = 61.4/60 = 1.02, so the eye is kept at **its full original edge distance** (it cannot grow beyond the original outline inside this design domain). Shear-out hand check: τ = P / (2 t (e − D/2)) = 99.9 kN / (2 · 70 · 31.4 mm²) = 22.7 MPa, using the resultant √(97² + 24²) kN (Ti-8-1-1 Fsy ≫ 100 MPa) [K] |
| Multiple load cases: weighted sum of normalised compliances (Bendsøe & Sigmund 2003) or min–max bound formulation (Achtziger 1998) | Zhang, de Sturler & Paulino, arXiv 1609.03099 (VERIFIED-PAGE) | weighted sum with w = 1/C₀. LC2 torsion gets the same weight as each LC1 case |
| Mirror symmetry is imposed by tying the variables of mirrored elements | Altair OptiStruct *Pattern Grouping*; COMSOL (VERIFIED-PAGE) | not imposed (the grid is not mirror-exact by 0.5 mm, and the lugs differ by 1.12 mm). The symmetry of the result is **measured** in `verify_v2.py` |
| Keeping the whole base plate as non-design | no source found (UNVERIFIED as a published rule) | our engineering choice, from the requirement that the part stays **one** bracket with a continuous mounting face. v1 showed that without it the lugs become two independent arches |

## 5. Results

Filled from `analysis/verify_v2.json` after the run: see `analysis/verify_v2.md`.

## 6. v3 (5 Nov ~14:00): symmetric, H8IM, after the code review

The v2 run (`runs/topo_v2_base_kept`) is **superseded** because of three problems:

* The optimiser element was H8, while every evaluation used H8IM (`setup/code_review_fixes_2026-11-05.md` #3).
* The layout was not symmetric: lug-to-lug y-mirror match 0.944, x-mirror match 0.948. One lug was a solid web, the
  other an arch with face skins.
* The checks it was judged by had bugs (#9–#14).

v3 = `runs/topo_v3_sym_h8im`:

* same set-up and frozen regions;
* `symmetry_planes_mm = {x: 500, y: 200.28}`. Design variables are tied over the 4-element mirror group (pattern
  grouping: Altair OptiStruct; COMSOL mirror symmetry, see `literature_TO_practice.md` §6). This is valid because
  the supports (bolt pattern 510 × 210 about x 500, y 200) and the load set are mirror-symmetric: LC1a and LC1b are
  each other's y-mirror, LC1c is its own mirror, and the sign of LC2 is not given, so ±My must both be carried. The
  grid mirror is the nearest voxel: 98.3 % of the elements have all 3 mirrors in the domain;
* H8IM in the optimiser;
* 70 iterations, volume fractions 0.45 / 0.41 / 0.38.

The load sharing between the 4 bolts is reported per case (`bolt_reactions_kN` in `analysis/verify_*.json`). That is
the action-reaction check: with the frozen flange and the symmetric layout, every bolt takes its share and the
members thicken along the paths to the bolts that react the most.

## 7. v3 skeleton (5 Nov ~14:00): no frozen base

User decision: freezing the whole base is a designer's choice the optimiser should make. The lugs can be tied by X
braces and struts like a skeleton. `setup/setup_official_v3_skeleton.json` therefore freezes **only the functional
interfaces**: the bolt bosses (supports) and the lug eyes (loads). The plate region is free design space.

"One part" is enforced as a **result gate**, not as frozen material:

* `pipeline.run_design` rejects a layout with more than one body;
* `verify_v2.topology_checks` additionally requires both lug eyes in the same body.

The coupling between the lugs is asked for by the loads themselves:

* LC1c pushes the two lugs towards each other (+24 / −24 kN). A strut or X between the lug roots carries this
  self-equilibrated pair with far less bending than two independent arches;
* LC2 torsion and the ±Fy cases bend the lugs out of plane, which a braced frame resists.

Run: `runs/topo_v3_skeleton` (volume fractions 0.35 and 0.30, symmetric, H8IM). The base-skin run
`runs/topo_v3_sym_h8im` (45 %) is kept as the fallback.

### 7a. Lug-to-lug connection restriction (5 Nov 14:03)

User: what matters is that the two lugs are connected to each other. The result gate alone does not steer the
optimiser, which can still return two arches (v1 did). The restriction added is a **minimum-section frozen tie**:

* 2 × 2 voxels, 15.6 × 15.6 mm (the filter length scale);
* on the symmetry plane x = 500, at the top of the plate (z 84–100);
* along y 30–371.12, joining both lug roots;
* about 0.3 kg.

The optimiser may thicken it and add braces around it. The clevis gap at pin height stays free, because it is
outside the design domain (the mating fitting sits there). Frozen fraction 0.1518 (run log).

A more general method is an auxiliary lug-to-lug load case: one lug held, the other loaded, bolts free. It needs
per-case supports in the solver and was not done in the time available (an UNVERIFIED design idea, no source read).
