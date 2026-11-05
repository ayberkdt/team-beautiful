# Bracket hand-off — changes for the film (written by the Ansys bracket session)

## 4 Nov 2026, 23:20 — `handoff/dryrun_cold/` is a DRY RUN, not for the film

Cold timed test of the day command on a new invented angle bracket (doc 22 §7). It uses the same schema (snapshots,
roles_source, stress_basis) and can serve as a test render, but it is not a challenge result. `sketch/` and `ge/`
were not touched by this run.

## 4 Nov 2026, 22:52–22:53 (file times) — requests 13–15 of handoff_requests.md

**Re-render: optional (topology evolution).** Additions only; every existing key and file is unchanged
(checked against the 22:51 copies: `ranking`, `baseline`, all final densities, `gerilme.txt`, `parca.stl`,
`baslangic.stl`, `yukler.json`, `girdi.json` identical).

* 13 · `yogunluk.json` (sketch): `runs[i].snapshots = [{"iteration": k, "density": [x][y][z]}]` on the **chosen run**
  (topo 25 %): iterations 5, 10, …, 50 (10 snapshots), same grid / `meta.voxel_mm` / `meta.origin_mm`, 0–1 at
  3 decimals, raw physical density (before the connectivity clean-up of the final layout). Every run has
  `warm_start_from` ("uniform start" → "topo 50 %" → "topo 35 %"): the 25 % run starts from the 35 % layout, so its
  first snapshot already looks like it. The snapshots come from a replay of the cached chain; the replayed final
  densities equal the cached ones to 3.1e-8. File size 4.3 → 21 MB. ge: chosen design is "initial" (no topology
  run chosen) → no snapshots.
* 14 · `details.setup.roles_source`: sketch "auto" (proposed, untouched), ge "edited" (read from
  inputs/ge_setup.json). New runs set it from a signature of the proposal (roles, supports, load cases).
* 15 · the fake-Ansys rehearsal never touches `handoff/` or `out/`: it lives in
  `studies/final_2026/ansys/rehearsal_crosscheck/<case>/<scenario>/` with `REHEARSAL_fake_ansys_crosscheck_template.csv`
  ("FAKE ANSYS DATA" in every row) and `REHEARSAL.json` (`"fake_ansys_data": true`). For a test render of the
  cross-check shot, use one of those folders explicitly; none of them is a real Ansys result.


## 4 Nov 2026, ~22:20 — round 2 (coordinator brief 21:05)

**Re-render needed: no.** No file in `handoff/sketch/` or `handoff/ge/` changed after the 20:48–20:49 rewrite (file times)
(`result.json` with `stress_basis`, `details`, `eco_audit.*`, `materials/`). Numbers on screen stay valid.

New content the film *may* use (optional, not in the hand-off folders; source files in `out/<case>/`):

| What | Where | One line |
|---|---|---|
| Life screening at 300 °C with AM-surface knock-downs | `out/<case>/report.md` §4, "Life screening" | sketch Ti-6Al-4V 25 %: margin 0.67 as-built, 2.29 machined — surface finish decides life |
| Bolt loads, FEA vs classical bolt group | `out/<case>/report.md` §4, "Bolt loads" | GE: support idealisation moves single bolt loads up to 4× |
| "Ansys result arrives" rehearsal | `studies/final_2026/ansys/rehearsal_crosscheck/<case>/REHEARSAL_summary.md` (FAKE ANSYS DATA, never under the real template names) | 4 planted errors (units, missing support, 22 °C, none) → 4 correct verdicts per case |

Not for the film: the 3-D stress-constrained topology (`stress3d`) is EXPERIMENTAL (doc 22 §4c); the layouts in
the hand-off still come from the compliance topology + T10 verification.

## 4 Nov 2026, 20:48–20:49 (file times; my earlier message said ~21:10, which was an estimate)

`result.json`: every material on the T10-verified layout carries the T10 stress (`stress_basis` "T10"/"voxel",
`voxel_*` keep the ranking values); hand-off folders carry `details`, `eco_audit.json/.md` and `materials/`.
