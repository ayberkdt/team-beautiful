# Bracket toolchain validation

`python scripts/bracket_validate.py --slow` (2026-11-04 19:52)

| Benchmark | Reference | Ours | Pass | Source |
|---|---|---|---|---|
| patch test, uniform tension (H8) | exact σz = 100 MPa | max |σz/σ − 1| = 2.9e-14 | yes | exact solution |
| patch test, uniform tension (H8IM) | exact σz = 100 MPa | max |σz/σ − 1| = 7.0e-14 | yes | exact solution |
| cantilever tip deflection, H8, 1 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.6428 | info | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| cantilever tip deflection, H8, 2 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.8690 | info | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| cantilever tip deflection, H8, 4 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.9574 | info | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| cantilever tip deflection, H8IM, 1 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.9855 | yes | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| cantilever tip deflection, H8IM, 2 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.9867 | yes | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| cantilever tip deflection, H8IM, 4 voxel(s) thick | Timoshenko beam 2.0156 mm | ratio 0.9904 | yes | Timoshenko & Gere (shear coefficient 5/6) [textbook formula] |
| plate with hole, Kt_net (voxel 1.00 mm, 9440 el.) | Heywood Kt_net = 2.422 (d/W = 0.25) | 1.884 (-22.2 %) | info | Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood |
| plate with hole, Kt_net (voxel 0.67 mm, 31884 el.) | Heywood Kt_net = 2.422 (d/W = 0.25) | 1.936 (-20.1 %) | info | Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood |
| plate with hole, Kt_net (voxel 0.50 mm, 75536 el.) | Heywood Kt_net = 2.422 (d/W = 0.25) | 1.970 (-18.7 %) | info | Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood |
| 3-D SIMP vs repository topology.topopt (24×8×4, V 0.3, density filter, 30 it.) | c = 160.3096 (aerokit.optimization.topology, top88 family) | c = 160.3007 (-0.006 %) | yes | Andreassen et al. 2011 code family; top88 MBB exact in tests/optimization |
| 3-D AM overhang filter adjoint vs central differences | finite differences | max rel. error 6.9e-10 | yes | Langelaar 2017 Eq. (10)-(14) |
| MatML write → parse (all candidates); parser on a real Workbench 23.1 export | values written; Ansys export: rho 7850, E 2e11, Fty 2.5e8 | 5 materials parsed; real export read: rho 7850.0, E 200000000000.0, Fty 250000000.0 | yes | pymaterials-manager test data |
| drawing → STEP (OCC) → gmsh surface → voxels (2 mm) | exact B-rep volume 108475 mm³ | 108480 mm³ (+0.00 %) | yes | gmsh 4.15.2 / OCC |
| drawing → STEP (OCC) → gmsh surface → voxels (1 mm) | exact B-rep volume 108475 mm³ | 108739 mm³ (+0.24 %) | yes | gmsh 4.15.2 / OCC |
| cantilever tip deflection, T10 (gmsh), size 5 mm, 434 el. | Timoshenko beam 2.0156 mm | ratio 0.9905 | yes | Timoshenko & Gere (shear coefficient 5/6) |
| cantilever tip deflection, T10 (gmsh), size 2.5 mm, 3617 el. | Timoshenko beam 2.0156 mm | ratio 0.9921 | yes | Timoshenko & Gere (shear coefficient 5/6) |
| plate with hole, Kt_net, T10 (gmsh), size 2 mm, 10881 el. | Heywood Kt_net = 2.422 | 2.512 (+3.7 %) | yes | Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood |
| plate with hole, Kt_net, T10 (gmsh), size 1 mm, 54132 el. | Heywood Kt_net = 2.422 | 2.479 (+2.4 %) | yes | Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood |
| 3-D cantilever 48×24×24, V 0.12, rmin √3, projection, 100 it. (orientation only) | Ferrari & Sigmund 2020 top3D125: c = 3993.7 (Neumann) / 4074.3 (Dirichlet); their load line, penalty and continuation schedule not confirmed here | c = 12.31 with a unit TOTAL load on the 25-node edge; 7695 if each node carried a unit load (c ∝ load²); 100 it., 465 s — NOT reproduced (load convention, penalty and continuation of top3D125 unconfirmed) | info | arXiv 2005.05436 Sec. 4, Fig. 8 (read by sub-agent) |
