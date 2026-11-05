# aerokit.orbits — sources

Copied from Sidera (`D:\sidera`, commit `02029b76`) on 2026-10-25 at the author's request; only import paths
changed. Sidera is proprietary (Copyright (c) 2026 Ayberk Demirkanat). `constellations.py` and
`visibility.py` are aerokit code written on top of these leaves.

| Source | Destination | sha256 (first 16) | lines |
|---|---|---|---|
| `sidera.core.kepler_j2` | `aerokit.orbits.kepler_j2` | `b00e33b114578585` | 79 |
| `sidera.common.two_body` | `aerokit.orbits.two_body` | `31f79c7a4bb48449` | 245 |
| `sidera.frames.teme (gmst82_rad)` | `aerokit.orbits.gmst` | `a50d6c0629c026b4` | 21 |
| `tests/common/test_two_body.py` | `tests/orbits/test_two_body.py` | `d3687363eb378f10` | 74 |
| `tests/frames/test_frames_teme.py (test_gmst82_matches_erfa)` | `tests/orbits/test_gmst.py` | `2a26b8d7073d7214` | 8 |
