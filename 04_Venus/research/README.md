# Venus rotorcraft — research notes (LuGus final, 4 Nov 2026)

One file per source. Who read what:

| Prefix | Read by | Topic | Index |
|---|---|---|---|
| `A_` | research agent A | atmosphere: Pioneer Venus probes (PDS raw data), VEGA balloons, winds (VEX/Akatsuki), solar flux, clouds, lightning, CO₂ properties; VIRA not obtainable | `A_00_index.md` |
| `B_` | research agent B | mission precedents: Venera 4–14, Vega, Pioneer Venus, DAVINCI, JPL aerobots, VAPS, Landis airplane, NASA Ames Venus rotary-wing (Young 2026) | `B_00_index.md` |
| `C_` | research agent C | rotorcraft: Ingenuity, MSH, Dragonfly, Harrington 1951 & Knight–Hefner 1937 (BEMT validation data), coaxial theory, low-Re airfoils | `C_00_index.md` |
| `D_` | research agent D | engineering constants: Sutton–Graves, Tauber radiative, materials vs H₂SO₄, batteries, solar cells, comms, magnets, electronics | `D_00_index.md` |
| `K_` | **this session** | sources read and checks computed by the Venus session itself: NIST CO₂ data (`K_nist_co2_properties`), entry-model cross-checks (`K_entry_crosschecks`), review of docs/25 (`K_review_doc25`) | — |
| `R_` | a fresh audit agent, then this session | `R_audit_2026-11-04`: 15 random [D]/[D-ag] values of docs/25 re-read at their sources (seeded draw), with the Venus session's resolution of every flagged item | — |

Tags inside the notes: **[D-ag]** read in the source by the agent, **[A]** abstract/snippet/secondary only, *derived*
or *[calc]* = the agent's arithmetic. In the code and in `04_Venus/docs/25_lugus_venus_rotorcraft.md` these become [D-ag];
values the Venus session read or extracted itself are [D]: NIST tables, JPL SSD constants, and the Pioneer Venus PDS
tables extracted by `04_Venus/scripts/venus_pds_extract.py`.

Downloads (data only, not in the repo): `D:\tmp_ideathon\venus\downloads\{atmo,missions,rotor,eng,nist}\`.


Appended 5 Nov 2026:

| Prefix | Read by | Topic | Index |
|---|---|---|---|
| `E_` | simulator data-book agent (5 Nov 2026) | re-read PV/VEGA/NIST/JPL data; RO thermal structure, LES convection, dynamics review, cloud microphysics, Dryden, VRS, dynamic inflow, multirotor interaction, MSH weights, LuGus/Skypersonic simulator, Venus Flagship aerobot; data files in `data/` | `E_00_index.md` |
