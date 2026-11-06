# Code review of the bracket topology / finalize / verification chain — 5 Nov 2026

Sources: my own reading of the code and an independent read-only review subagent that got the code, not my
conclusions (17 findings). Each row: what was wrong, the evidence, what it cost, the fix, and what prevents a repeat.

## Topology optimisation and selection (`src/aerokit/bracket/`)

| # | Bug | Evidence | Effect | Fix | Guard |
|---|---|---|---|---|---|
| 1 | Only 0.75·r rings were frozen. Base plate and lug eyes were free | `features.non_design_mask` + v1 renders | v1 deleted the base. **Every v1 layout is 2 separate bodies** (`bodies_kept = 2` for 35/25/20 %, measured by `verify_v2.topology_checks` on `runs/topo_fixed_bores`) | `ring_factor_by_role` (lug eye to original edge distance) + base-skin box. Setup v2 | one-body gate below |
| 2 | Connectivity filter kept every body touching any support ring | `pipeline.run_design` | a layout of 2 bodies was analysed and **chosen** | layout with ≠ 1 body is recorded as failed | `tests/test_bracket_strength_basis.py` + verify gate `lugs_in_one_body` |
| 3 | Optimiser ran on H8 (full integration), evaluation on H8IM | `optimize(...)` had no `element=`; settings show "H8" | H8 locks in bending with 1–2 elements per member → layouts optimised against over-stiff members | `element=opt.element` in both calls | re-run `runs/topo_v3_h8im` |
| 4 | Displacement criterion L/400 never applied | `rank_materials` passes = U ≤ 1 only | 38 % layout chosen with T10 2.17 mm > 1.65 mm | passes = strength AND displacement. T10 governing ratio = max(strength, u/u_lim) | — |
| 5 | T10 feedback corrected stress only | `verify_choice` | a T10 displacement failure never changed the choice and `passes` stayed True | T10/voxel displacement factor fed back. A final T10 failure sets `passes = False` | log line "T10 check of the final choice FAILS" |
| 6 | Strength basis: max(σ/Fty, 1.5σ/Ftu) | pipeline (5 call sites) | less conservative than the mentor's rule (FoS 1.5 on **yield**, mentor 5 Nov ~13:45) | `strength_util()`. `design_criteria.strength_basis = "yield"` in setup v2. Default unchanged for old runs | test |
| 7 | Volume fraction below the frozen fraction failed after 24 min, writing nothing | coordination log 12:21 | 24 min lost | checked before any solve | — |
| 8 | Report text: old strength rule and "0.75 × r" exclusions | `report.py` | report contradicted its own numbers | text follows `strength_basis`, ring factors per role and frozen boxes | — |

## T10 verification (`tetfem.py`, `analysis/t10check.py`, `analysis/verify_v2.py`)

| # | Bug | Effect | Fix |
|---|---|---|---|
| 9 | `_bore` picked nodes by radius ± tol only | on a voxel STL (tol 4.7 mm) the supports also fixed, and the loads also hit, an annulus of the plane faces at each bore mouth | node must have a boundary normal ≥ 60° from the bore axis (cylindrical face only) |
| 10 | Strength used von Mises outside ALL hole zones | the zone (R + 23.4 mm) covered most of the 31.4 mm lug ligament: **the lug net section was never checked** | governing stress excludes only the fixed-support zones (`vm_outside_supports_Pa`). The old value is still reported |
| 11 | Stiffness used the geometric-mean E (124 GPa), strength the low-end Fy | displacement optimistic by about 15 % | low-end E 121 GPa × 104.8/120.7 (MIL-HDBK-5J) = 105.1 GPa at 300 °C |
| 12 | "Lugs tied through base" check | trivially true (the frozen skin joins everything below z 100) | replaced by: one body, both lug eyes in it, and each lug reaches the flange with the bolt bosses removed. Discriminates: v1 FAIL, v2 PASS |
| 13 | Combined cases lacked LC1c ± My | LC1c governs the displacement | 6 combined cases |
| 14 | TO-STL target volume = voxel count × h³, finalize = Σfrac·h³ | the two models were 2.9 % apart by construction | both use Σfrac·h³ |

## Finalize (`src/aerokit/bracket/finalize.py`)

| # | Bug | Evidence | Effect | Fix |
|---|---|---|---|---|
| 15 | Fixed opening radius r = 6 mm | stages 8524 → 5591 cm³ (−34 %) | load-carrying members deleted. σ 542 MPa, U 1.57 (finalize_v2_45.json 13:36, superseded) | radius reduced until the opening removes ≤ 2 % of the volume (edge rounding only). Radius and loss are logged |
| 16 | Plain Gaussian over the zero exterior | lug mid-plane slice: the 45 % lug is an arch whose **face skins** carry the out-of-plane Fy bending. The finalized lug lost them (open triangle in the side view) | σ 350 MPa at the lug flank (599, 40, 143) mm | normalised convolution blur(ρ·dom)/blur(dom) and nearest-value interpolation |
| 17 | Bores extended ±64 mm | — | could drill members between lugs or above bosses | ±2 fine voxels |
| 18 | Wall thickness = 2·EDT (centre to centre) | — | overstated by one voxel | 2·(EDT − h/2) |
| 19 | `enclosed_voids_filled >= 0` gate | always true | manufacturing gate meaningless | gate: one body, watertight, wall p1 ≥ 1.2 mm (LPBF rule) |
| 20 | Bore radius metric | averaged only ±1.5 mm around nominal | could not show a deviation | mean / min / max within ±6 mm, all segments |
| 21 | Print-face height = min vertex z | read 28.20 vs designed 28.5 | stock misreported | median z of the down-facing faces |

## Known limits (not bugs, stated)

* The volume constraint counts elements, not partial volumes (boundary voxels count as full). Small effect,
  documented.
* The 50/70-iteration runs end with β = 16 and "converged = False" by the strict change test. Grey fraction is about 2 %.
* LC2 is a torque about the pin axis (tangential traction on the bores): valid for a clamped/keyed pin [Y].
* Load-case weights 1/C₀ give LC2 torsion the same normalised weight as each LC1 case (the user asked for torsion
  to count). A min–max (bound) formulation is the alternative (Achtziger 1998, cited in `literature_TO_practice.md`).
