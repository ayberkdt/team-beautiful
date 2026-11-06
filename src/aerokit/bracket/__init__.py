"""Aircraft bracket redesign toolchain (EUROAVIA Ideathon 2026, Ansys challenge).

From a bracket geometry (STEP/IGES via gmsh, STL/OBJ/PLY, or a parametric JSON drawing) to a verified,
lighter design and the documents the challenge asks for:

``geometry``   parametric CSG drawing (JSON), voxelisation of drawings and closed triangle surfaces
``features``   through-hole detection, bolt/lug classification, editable load + boundary JSON
``voxfem``     3-D linear static FEA on voxel H8 / H8 incompatible-mode bricks (SI units)
``topo3d``     SIMP compliance topology optimisation on the voxel design domain (density filter,
               Heaviside projection, AM overhang filter, multiple load cases, stress-aware volume search)
``matdata``    temperature-dependent material data at the working temperature (20 / 300 °C)
``cards``      Ansys Engineering Data (MatML XML) and human-readable material cards
``ecoaudit``   Granta-EduPack-style eco audit (material, manufacture, transport, use, end of life)
``crosscheck`` Ansys result vs our result agreement table with likely causes of discrepancies
``pipeline``   one-call driver used by ``01_Ansys/scripts/bracket_day.py``

Every number that comes from literature is tied to :mod:`aerokit.references` with :func:`aerokit.references.cite`.
"""
