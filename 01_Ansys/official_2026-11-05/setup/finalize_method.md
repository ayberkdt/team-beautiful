# Finalize stage: from the topology result to a manufacturing-ready part (5 Nov 2026)

Three models are kept side by side:

| # | Model | File | How it is made |
|---|---|---|---|
| 1 | Initial design (S275N) | `visuals/initial_exact.step` / `.stl` | organisers' CAD |
| 2 | Topology-optimised shape | `runs/topo_v2_base_kept/cad/optimised_<tag>.stl` | SIMP densities → volume-matched iso-surface, light Taubin smoothing (`cadout.density_to_stl`) |
| 3 | Finalized shape, nominal + print-stock variant | `runs/topo_v2_base_kept/cad/finalized_<tag>.stl` and `finalized_<tag>_print_stock.stl` | `src/aerokit/bracket/finalize.py`, driven by `analysis/finalize_v2.py` |

Model 3 is re-analysed with exactly the same T10 code, cases and material values as model 2 (`analysis/t10check.py`).
The literature is explicit that smoothing changes performance and can even cost feasibility (Swierstra, Gupta &
Langelaar 2020; Subedi, Verma & Suresh 2020).

## Pipeline (code order) and its sources

Sources: `setup/literature_finalize.md` (research subagent, 5 Nov). Evidence levels are kept from that file.

| Step | What `finalize.py` does | Why / source |
|---|---|---|
| 1 Fine grid | original part voxelised at h = 2 mm (10.5 M cells) with partial volumes. The envelope SDF uses (0.5 − frac)·h within one voxel of the surface | sub-voxel planes, arcs and flanks. Recommended grid ≤ 3.9 mm, ideally ~2 mm [literature_finalize §implications; grid rule UNVERIFIED reasoning] |
| 2 Density → shape | trilinear interpolation of the TO densities, **normalised** Gaussian inside the envelope (σ = 4 mm: blur(ρ·dom)/blur(dom), so the surface skins are not diluted by the empty exterior — review fix #16), threshold by bisection so the volume equals the optimised Σfrac·h³ volume | volume-preserving iso-level, as Swierstra et al. shift the level set to the target volume (VERIFIED-PAGE). Marching cubes: Lorensen & Cline 1987 |
| 3 SDF | exact Euclidean distance transforms of both phases | standard implicit representation. Closest published analogue: Ježek et al. 2025 (arXiv 2512.06976, SDF-based smooth extraction with volume preservation) |
| 4 Opening, adaptive r ≤ 6 mm | erode then dilate. The radius starts at 6 mm and is reduced in 1 mm steps until the opening removes ≤ 2 % of the volume, so it rounds edges and removes spikes **without deleting members** (review fix #15: a fixed 6 mm removed 34 % and the part failed). The radius used is logged | offset rounding (Rossignac & Requicha 1986; SNIPPET). Recommended 6–8 mm |
| 5 Interfaces re-inserted | union with the EXACT bolt bosses Ø105, lug eyes r 61.4 and the base flange z 30–46, all inside the original envelope | same order as nTop's lesson (implicit TO body → smooth → union with interfaces → intersect with original body; VERIFIED-PAGE) and Altair (intersect with the design space) |
| 6 Closing r = 10 mm | dilate then erode: every concave corner, including member-to-flange and member-to-lug, gets a fillet ≥ 10 mm | stress-concentration relief. Pilkey flat-bar Kt (D/d = 2, d = 30): 2.22 at r = 2 mm → 1.34 at r = 8 mm → 1.24 at r = 12 mm (computed by the subagent from the amesweb formula). Opening/closing order matters (Schevenels & Sigmund 2016) → wall check runs on the final shape |
| 7 SDF blur 1 voxel, then exact re-imposition | Gaussian σ = 2 mm on the SDF removes the staircase of the binary re-distancing. Then the exact interfaces again (min), the envelope (max) and the exact Ø60 bores (subtracted) | functional faces at nominal size and position. Measured after Taubin: bore radius 30.03 mm (test run on v1) |
| 8 Clean-up | largest body kept, islands counted. Enclosed voids filled | trapped powder cannot be removed from closed voids (Xometry design guide: powder escape holes 2–5 mm; VERIFIED-PAGE) |
| 9 Surface | flying-edges iso-surface, Taubin λ\|μ 40 iterations at pass band 0.05 (non-shrinking), decimation to 120 k faces for FEA | Taubin 1995; VTK windowed-sinc documentation (VERIFIED-PAGE). Plain Laplacian smoothing shrinks the part |
| 10 Print geometry | separate STL with 1.5 mm machining stock: bores printed at R − 1.5, mounting face extended 1.5 mm below z = 30 | functional surfaces are printed with stock and machined (MSC Apex: print and nominal geometry, 1 mm as an example; SNIPPET). CNC is needed below ±0.1 mm tolerance (Hubs; VERIFIED-PAGE). 1–2 mm range = reasoning, UNVERIFIED |
| 11 Checks (gate: one body, watertight, wall p1 ≥ 1.2 mm) | bodies; enclosed voids; open or non-manifold edges; minimum wall = 2 × medial-axis distance (min / p1 / p5); overhang area with nz < −cos 45° above the build plate (+z build); bore radius after smoothing | LPBF rules: 45° self-support, walls ≥ 0.8–1.2 mm (Xometry; VERIFIED-PAGE). VDI 3405-3 is withdrawn → ISO/ASTM 52911-1/-2 (DIN page; VERIFIED-PAGE). No Ti-8Al-1Mo-1V LPBF guide was found: the rules are Ti-6Al-4V / generic |

## Known limits (said plainly)

* Ti-8Al-1Mo-1V has no published LPBF design guide that we found. The 45° and wall rules are for Ti-6Al-4V or generic
  LPBF.
* The horizontal Ø60 pin bores are overhangs for a +z build. They need support, a teardrop shape or undersize
  printing followed by boring. The print geometry does the last option; supports are not modelled.
* The finalized model is an STL (faceted, 120 k faces). A B-rep/STEP needs a surface fit (Discovery "convert to
  solid", Altair PolyNURBS). For Ansys Discovery an STL import is enough to re-run the analysis.
* The minimum wall is measured on the 2 mm grid, so its resolution is ±2 mm.
