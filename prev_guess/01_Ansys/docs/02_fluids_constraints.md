# 02 · Fluid mechanics constraints (Fluent)

Prepared: 2026-10-25. For tags and event context: [00_overview.md](00_overview.md). Geometry prerequisites: [01_geometry_constraints.md](01_geometry_constraints.md).
**[D]** I read it in this session · **[A]** a sub-agent read it · **[S]** search summary only · **[Y]** judgement · **[H]** calculation/test (`python -m pytest`).

---

## 0. Decide first: 2D, 3D, or no CFD at all?

If a challenge slot lasts a few hours [D regulations format, duration inference Y], set up CFD in the following order:
1. **Hand calculation:** thin-airfoil theory, Cl_α ≈ 2π/(1 + 2/AR), Cd0 estimate, Breguet range.
2. **2D section:** runs within minutes, compared with XFOIL.
3. **3D half model:** only if the template is ready and the mesh passes in one go.

For the jury, **a single check showing why the result is reliable** is worth more than the number of results [Y].

---

## 1. Licence and computing resources

| # | Constraint | Source |
|---|---|---|
| FA-01 | Flow problem size **1 million cells/nodes**. | [D] Ansys Student page |
| FA-02 | At most **4 CPU cores**. This machine has 6 cores, 4 of them can be used. | [D] · [D] `Get-CimInstance` |
| FA-03 | The exact threshold appears in forums as 1 048 576 cells. The licence is also checked at save time. **Target ≤ 0.9 M.** In a polyhedral mesh the node count exceeds the cell count; monitor both. | [S] · [Y] |
| FA-04 | If the sponsor provides a temporary Academic/Research licence, the limits may be lifted. Ask at the installation meeting. | [Y] |

## 2. Flow conditions

| # | Constraint | Source |
|---|---|---|
| FB-01 | Atmosphere from ISA; state the altitude explicitly: `python -m aerokit aero isa`. | [H] |
| FB-02 | If the local Mach ≲ 0.3, incompressible flow can be assumed (common rule of thumb). If 0.3 is exceeded in regions such as the rotor tip, ideal gas + energy equation. Calculation: `python -m aerokit aero flow` prints the Mach number. | [S] · [Y] |
| FB-03 | Pressure far-field works only with ideal-gas density. For incompressible flow use velocity-inlet + pressure-outlet (0 Pa gauge). | [S] · [Y] |
| FB-04 | **AoA:** velocity components (cos α, sin α); lift direction (−sin α, cos α); drag direction (cos α, sin α). AoA 6° → Ux 0.9945, Uy 0.1045 (Ansys course value, tested). | [A] · [H] |
| FB-05 | **Reference values:** the default area is 1 m². In a half model enter S/2. Reference length MAC (`aerokit geometry planform`). Density and velocity should be computed from the inlet. | [S] · [Y] |
| FB-06 | **Free-stream turbulence:** in Fluent practice Tu 0.1–1%, viscosity ratio 1–10. NASA TMR recommends a much lower μt/μ for SST (1e-5…1e-2). The transition model is sensitive to the inlet Tu. | [A] |
| FB-07 | **Low Re:** for small UAVs Re ≈ 2–5×10⁵ [H]. There is a risk of a laminar separation bubble. Fully turbulent models can give large drag errors in this band; in one S1223 study the error was 40% versus 10%. | [S] |
| FB-08 | A full propeller or rotor model exceeds the budget. A fan / actuator disk / virtual blade simplification should be preferred and stated in the report. Whether these models are enabled in Student was not verified. | [Y] |

**ISA standard atmosphere.** At 10 km the density drops to a third of the sea-level value [H, `aerokit.aero.atmosphere.isa`; sea-level values in the test: ρ0 1.225, a0 340.29, μ0 1.7894e-5].

| Altitude (m) | T (K) | p (Pa) | ρ (kg/m³) | μ ×10⁵ (Pa·s) | ν ×10⁵ (m²/s) | a (m/s) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 288.15 | 101 325 | 1.225 | 1.789 | 1.46 | 340.3 |
| 1 000 | 281.65 | 89 875 | 1.112 | 1.758 | 1.58 | 336.4 |
| 2 000 | 275.15 | 79 495 | 1.006 | 1.726 | 1.71 | 332.5 |
| 3 000 | 268.65 | 70 109 | 0.909 | 1.694 | 1.86 | 328.6 |
| 5 000 | 255.65 | 54 020 | 0.736 | 1.628 | 2.21 | 320.5 |
| 10 000 | 223.15 | 26 436 | 0.413 | 1.457 | 3.53 | 299.5 |
| 11 000 | 216.65 | 22 632 | 0.364 | 1.422 | 3.91 | 295.1 |

The T column was left with two decimals because these are the canonical ISA values.

**Typical cases.** Small UAVs are in the Re ≈ 2–5×10⁵ band; the rotor section crosses the compressibility limit [H].

| Case | U (m/s) | c (m) | h (m) | Re ×10⁶ | Mach | Δy₁ (y⁺=1) ×10⁵ (m) | Δy₁ (y⁺=30) ×10⁵ (m) |
|:---|---:|---:|---:|---:|---:|---:|---:|
| Small UAV | 15 | 0.20 | 0 | 0.21 | 0.04 | 4.1 | 123 |
| Small UAV | 20 | 0.25 | 0 | 0.34 | 0.06 | 3.2 | 96 |
| Small UAV | 25 | 0.30 | 0 | 0.51 | 0.07 | 2.6 | 79 |
| eVTOL wing | 60 | 1.00 | 500 | 3.95 | 0.18 | 1.3 | 39 |
| eVTOL rotor section | 120 | 0.15 | 0 | 1.23 | 0.35 | 0.6 | 17 |

Method: flat plate Cf = 0.026·Re^(−1/7). Because Fluent reports y⁺ at the cell centre, Δy₁ = 2·y_p was used. **Check the y⁺ contour after the solution.**

## 3. Mesh

| # | Constraint | Source |
|---|---|---|
| FC-01 | **Fluent baseline values:** minimum orthogonal quality > 0.01; in a tetra mesh maximum skewness < 0.95. The averages should be clearly better. No flow passage should have fewer than 5 cells. | [A] Fluent UG v261 |
| FC-02 | **Practical target:** minimum orthogonal quality ≥ 0.1; maximum skewness ≤ 0.85–0.9. | [S] · [Y] |
| FC-03 | Skewness bands: 0–0.25 excellent · 0.25–0.5 good · 0.5–0.75 fair · 0.75–0.9 poor · 0.9–1 bad. | [A] wb_msh v261 |
| FC-04 | **y⁺:** SST and enhanced wall treatment ≈ 1 (≤ 5). Wall functions 30–300. **Avoid the 5–30 range.** The SA model requires y⁺ ≈ 1 or ≥ 30. | [A] · [S] |
| FC-05 | **Transition SST:** y⁺ ≤ 1. When y⁺ > 8 the transition moves upstream; at y⁺ ≈ 25 the flow is almost fully turbulent. Growth normal to the wall < 1.1. Version read: v24.2. | [A] Theory Guide §4.7.3 |
| FC-06 | **Inflation:** growth 1.1–1.2 (DPW < 1.25; CRM-NLF < 1.15). The default number of layers is too low for aero. Example: c 0.25 m, 20 m/s, y⁺ 1, δ ≈ 7.2 mm → 22 layers at growth 1.2, 26 at 1.15, 34 at 1.1. Calculation: `aerokit aero flow --growth`. | [A] · [H] |
| FC-07 | **Surface:** ~0.1% c in the chordwise direction at the leading and trailing edges (DPW medium grid). ≥ 200–250 divisions on a 2D airfoil. Curvature + proximity sizing at the wing tip and leading edge. | [A] · [Y] |
| FC-08 | **Domain:** 2D far-field radius ≥ 20–50 c (DPW ~100 c_ref). 3D: inlet ≥ 10–15 c, outlet ≥ 20–30 c, lateral ≥ 10–20 c. In poly-hexcore the far field is cheap. | [A] · [Y] |
| FC-09 | **Fill:** poly-hexcore (Mosaic). Reported to give 20–50% fewer cells than hexcore. | [S] |
| FC-10 | **Watertight order:** Import → Local Sizing → Surface Mesh → Describe Geometry → Update Boundaries → Update Regions → Boundary Layers → Volume Mesh → Switch to Solution. | [A] PyFluent documentation |
| FC-11 | **1 M budget (3D half model):** prism cells ≈ surface faces × layers. 25k faces × 20 layers = 0.5 M; ~0.4 M remains for the core. Calculation: `aerokit aero flow --surface 25000`. If the budget gets tight, switch to y⁺ 30–100 wall functions + 8–10 layers and say so in the report, or go down to 2D. | [H] · [Y] |
| FC-12 | **Mesh independence:** three grids, r > 1.3 (Celik 2008). In 3D ~2.2× cells per step: ≈ 0.2 / 0.45 / 1.0 M. GCI calculation `aerokit.aero.flow.gci`; p = 2 and the Richardson value are verified by a test. If there is no time, 2 grids and the percentage difference. | [A] Celik 2008 · [H] |

## 4. Solver and convergence

| # | Constraint | Source |
|---|---|---|
| FD-01 | Pressure-based coupled solver, pseudo-transient, hybrid initialization. | [A] ONERA M6 example |
| FD-02 | **Turbulence model:** baseline solution SST k-ω (fully turbulent). If Re < 10⁶, add a Transition SST sensitivity run. Cross-check the 2D section with XFOIL. SA does not predict transition. | [Y] · [A] |
| FD-03 | **Convergence:** residuals 1e-4…1e-6 are necessary but not sufficient. Cl, Cd and Cm should change by < 0.1% over the last 200–500 iterations. Check the mass imbalance. | [A] · [Y] |
| FD-04 | **Common errors:** reference area left at 1 m² · not rotating the force directions when the AoA changes · mm/m confusion · not checking y⁺ · pressure far-field + constant density · too few inflation layers · far field too close · skewed cells at a sharp trailing edge. | [Y] · [S] |
| FD-05 | The Fluent Aero workspace automates AoA/Mach sweeps. Whether it is enabled in Student was not verified. | [A] |

## 5. Reporting

| # | Constraint | Source |
|---|---|---|
| FE-01 | With every result give: cell count, y⁺ range, model, convergence criterion, grid difference (%). The jury consists of technical experts. | [D] · [Y] |
| FE-02 | Tie the CFD to a hand calculation. If there is a deviation, write down the reason. | [Y] |
| FE-03 | Write down the simplifications with their justification. 2023 card: "with the right justification there is no such thing as a wrong answer". | [D] |

## 6. Sources

- [D] Ansys Student: https://ansys.synopsys.com/academic/students/ansys-student
- [A] Fluent UG mesh quality v261: https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/flu_ug/flu_ug_GridQuality.html
- [A] Watertight workflow + ONERA M6: https://fluent.docs.pyansys.com/version/stable/examples/00-fluent/external_compressible_flow.html
- [A] Watertight CFD geometry: https://ansys.synopsys.com/blog/watertight-cfd-geometry-ansys-fluent
- [A] Transition SST grid v242: https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_turb_sst_grid.html
- [A] Skewness v261: https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/wb_msh/msh_skewness.html
- [A] DPW summary (Levy et al.): https://cfd.ku.edu/JRV/Levy.pdf
- [A] CRM-NLF grid guidelines: https://transitionmodeling.larc.nasa.gov/wp-content/uploads/sites/109/2020/02/CRM-NLF_GridGuidelines.pdf
- [A] Celik et al. 2008: https://qa12.asme.org/wwwasmeorg/media/ResourceFiles/Shop/Journals/JFENumAccuracy.pdf
- [A] NASA TMR: https://tmbwg.github.io/turbmodels/sst.html · https://tmbwg.github.io/turbmodels/spalart.html
- [A] Ansys airfoil course: https://innovationspace.ansys.com/courses/wp-content/uploads/sites/5/2024/09/airfoil_solution_outline.pdf

## 7. Quick commands

```bash
python -m aerokit aero isa --h 0 3000 10000
```
```bash
python -m aerokit aero flow --U 20 --L 0.25 --yplus 1 --growth 1.15 --surface 25000
```
