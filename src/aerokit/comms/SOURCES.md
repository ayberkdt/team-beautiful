# aerokit.comms — sources

Copied from Sidera (`D:\sidera`, commit `02029b76`) on 2026-10-25 at the author's request. Only import paths
were changed (`sidera.…` → `aerokit.comms.…`) and a two-line provenance header was added; Sidera is
proprietary (Copyright (c) 2026 Ayberk Demirkanat). sha256 is of the source file as read.

| Source | Destination | sha256 (first 16) | lines |
|---|---|---|---|
| `sidera.common.constants` | `aerokit.comms.constants` | `91180f0c0bfe3df3` | 534 |
| `sidera.common.errors` | `aerokit.comms.errors` | `77e383dd8c366f1e` | 26 |
| `sidera.communications.rf` | `aerokit.comms.rf` | `3cdfd07af1b631ac` | 317 |
| `sidera.communications.geometry` | `aerokit.comms.geometry` | `456690ae99658a50` | 432 |
| `sidera.communications.link.budget` | `aerokit.comms.budget` | `6eec5c96c4d8a782` | 416 |
| `sidera.communications.channel.models` | `aerokit.comms.channel` | `020cb7417cb6c7ff` | 331 |
| `sidera.communications.channel.itu_earth` | `aerokit.comms.itu_earth` | `7b68b321fc2b1406` | 1055 |
| `sidera.communications.channel.tropospheric_refraction` | `aerokit.comms.refraction` | `39aa66c4c1353b5c` | 102 |
| `sidera.communications.hardware.antennas` | `aerokit.comms.antennas` | `212679d5b77a4223` | 607 |
| `sidera.communications.hardware.terminals` | `aerokit.comms.terminals` | `8ee0b9d423a9f34f` | 329 |
| `sidera.communications.ground.dsn` | `aerokit.comms.dsn` | `fc4c83e0724174c4` | 258 |
| `sidera.communications.channel.dsn_atmosphere` | `aerokit.comms.dsn_atmosphere` | `d7178f0bfcb5890e` | 113 |
| `sidera.communications.link.digital` | `aerokit.comms.digital` | `3056a62439fbcbbb` | 505 |
| `sidera.communications.link.modcod` | `aerokit.comms.modcod` | `12a8e2e1bd36ac02` | 400 |
| `sidera.communications.ground.stations (StateProvider)` | `aerokit.comms.state` | `060eff3b6bc2471b` | 13 |
| `sidera.communications.coverage.timeline (integrate_data_volume_bits)` | `aerokit.comms.data_volume` | `4fe08677135b210c` | 44 |
| `tests/communications/test_communications_rf.py` | `tests/comms/test_rf.py` | `6cd5fb2119ffbfca` | 841 |
| `tests/communications/test_communications_propagation.py` | `tests/comms/test_propagation.py` | `0ecf02d621e7f085` | 561 |
| `tests/communications/test_antenna_patterns.py` | `tests/comms/test_antenna_patterns.py` | `ac6f39c76550080f` | 122 |
| `tests/communications/test_audit_fix_itu_validity.py` | `tests/comms/test_itu_validity.py` | `14d322efd734a75b` | 77 |
| `tests/communications/test_communications_digital.py` | `tests/comms/test_digital.py` | `ad7bb514be0411e9` | 513 |
