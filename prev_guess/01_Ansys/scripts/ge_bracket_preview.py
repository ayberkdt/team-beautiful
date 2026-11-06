"""Scenario S1 (docs/12): coarse 3-D topology preview of a GE-type engine-mount bracket, four load cases.

    python prev_guess/01_Ansys/scripts/ge_bracket_preview.py --check            # set-up only: grid, supports, loads, passive regions
    python prev_guess/01_Ansys/scripts/ge_bracket_preview.py 0.138 0.065        # one run per volume fraction of the envelope
    python prev_guess/01_Ansys/scripts/ge_bracket_preview.py --nx 30 0.138      # coarser grid (30 x 18 x 10 voxels of 5.95 mm)

Geometry from the dolfiny STEP frame as parsed in prev_guess/01_Ansys/research/Görev senaryoları/R3 §1b [Y]: envelope about
178.5 x 108 x 62 mm, four bolts on the base (z = 0), a clevis with two 7.6 mm arms around a 19.05 mm pin at
(y, z) = (-56.8, 44.6). Loads GE/GrabCAD [D]: LC1 35,586 N up (+z), LC2 37,810 N out (-y), LC3 42,258 N at 42 deg
from vertical, LC4 564.9 N m about z as a +-y couple on the two arms. Bolt seats fixed; bolt bosses (dia 30.48,
two voxels high) and the lug rings are kept solid; the bore is void.

Scaling: unit-cube H8 elements of size h and unit modulus, so the physical displacement is u = u_hat / (E h) with
the loads in N. The volume fractions 0.138 and 0.065 of the envelope give about 0.73 kg (Elmas 2026, Ansys SIMP)
and 0.35 kg (GrabCAD winner) in Ti-6Al-4V. The coarse voxels (4.46 mm) make thin members too stiff or too soft by
an unknown amount: read the result as a load-path preview and an order-of-magnitude stiffness, not a margin.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.optimization import topology as tp  # noqa: E402

E, RHO = 110e9, 4430.0                      # Ti-6Al-4V (Elmas / dolfiny values, R3 §1a [S])
X0, Y0, Z0 = -163.3, -74.6, 0.0             # envelope origin [mm] in the dolfiny frame
NX = int(sys.argv[sys.argv.index("--nx") + 1]) if "--nx" in sys.argv else 40
NY, NZ = round(NX * 107.1 / 178.5), round(NX * 62.475 / 178.5)      # 40 -> 24 x 14, 30 -> 18 x 10
H = 178.5 / NX                               # voxel edge [mm]
BOLTS = [(-148.1, -33.6), (-148.1, 18.5), (0.0, -38.1), (0.0, 0.0)]
PIN_Y, PIN_Z, BORE_R, LUG_R = -56.8, 44.6, 19.11 / 2, 35.56 / 2
ARMS = [(-92.1, -84.5), (-63.6, -55.9)]
S42, C42 = np.sin(np.radians(42.0)), np.cos(np.radians(42.0))
OUT = ROOT / "prev_guess" / "01_Ansys" / "scenarios" / "ge_bracket_preview.json"


def build() -> tuple[tp.Problem, dict]:
    g = tp.Grid3D(NX, NY, NZ)
    ix, iy, iz = np.meshgrid(np.arange(NX), np.arange(NY), np.arange(NZ), indexing="ij")
    cx, cy, cz = (X0 + (ix + 0.5) * H).ravel(), (Y0 + (iy + 0.5) * H).ravel(), (Z0 + (iz + 0.5) * H).ravel()
    passive = np.zeros(g.nel, int)
    for bx, by in BOLTS:
        passive[(np.hypot(cx - bx, cy - by) <= 30.48 / 2) & (cz < 2 * H)] = 2          # bolt bosses
    r_pin = np.hypot(cy - PIN_Y, cz - PIN_Z)
    in_arm = np.zeros(g.nel, bool)
    for a, b in ARMS:
        in_arm |= (cx >= a - H / 2) & (cx <= b + H / 2)
    passive[in_arm & (r_pin <= LUG_R)] = 2                                              # lug rings
    passive[(cx > ARMS[0][0] - H) & (cx < ARMS[1][1] + H) & (r_pin < BORE_R)] = 1       # bore / pin
    nx, ny, nz = np.meshgrid(np.arange(NX + 1), np.arange(NY + 1), np.arange(NZ + 1), indexing="ij")
    px, py, pz = X0 + nx.ravel() * H, Y0 + ny.ravel() * H, Z0 + nz.ravel() * H
    node = (nx.ravel() * (NY + 1) + ny.ravel()) * (NZ + 1) + nz.ravel()
    seat = np.zeros(len(node), bool)
    for bx, by in BOLTS:
        seat |= (np.hypot(px - bx, py - by) <= 14.17 / 2 + H / 2) & (pz == 0)
    fixed = [3 * n + d for n in node[seat] for d in range(3)]
    rn = np.hypot(py - PIN_Y, pz - PIN_Z)
    ring = (rn >= BORE_R - H / 2) & (rn <= BORE_R + H)          # node shell on the bore surface
    arm_nodes = []
    for a, b in ARMS:
        arm_nodes.append(node[ring & (px >= a - H / 2) & (px <= b + H / 2)])
    both = np.concatenate(arm_nodes)

    def spread(nodes: np.ndarray, vec: np.ndarray) -> dict[int, float]:
        f: dict[int, float] = {}
        for n in nodes:
            for d in range(3):
                if vec[d]:
                    f[3 * int(n) + d] = f.get(3 * int(n) + d, 0.0) + vec[d] / len(nodes)
        return f

    arm_dx = (np.mean(ARMS[1]) - np.mean(ARMS[0])) / 1000.0
    couple = 564.9 / arm_dx
    lc4 = spread(arm_nodes[0], np.array([0.0, couple, 0.0]))
    for k, v in spread(arm_nodes[1], np.array([0.0, -couple, 0.0])).items():
        lc4[k] = lc4.get(k, 0.0) + v
    loads = [spread(both, np.array([0.0, 0.0, 35586.0])), spread(both, np.array([0.0, -37810.0, 0.0])),
             spread(both, 42258.0 * np.array([0.0, -S42, C42])), lc4]
    info = {"voxel_mm": H, "elements": g.nel, "dofs": g.ndof, "fixed_nodes": int(seat.sum()),
            "load_nodes_per_arm": [len(a) for a in arm_nodes], "solid_kept": int((passive == 2).sum()),
            "void_kept": int((passive == 1).sum()), "envelope_mass_kg": NX * NY * NZ * (H / 1000) ** 3 * RHO,
            "load_sums_N": [round(sum(v for k, v in f.items() if k % 3 == d), 1) for f in loads[:3] for d in (1, 2)],
            "lc4_couple_N": couple, "arm_spacing_m": arm_dx, "load_nodes": [int(n) for n in both]}
    return tp.Problem(g, loads, fixed, passive=passive), info


def response(pr: tp.Problem, x: np.ndarray, load_nodes: list[int]) -> list[float]:
    """Mean displacement magnitude of the bore nodes per load case [mm], physical units."""
    U = pr.analysis(x)[2]
    out = []
    for k in range(U.shape[1]):
        u = U[:, k].reshape(-1, 3)[load_nodes]
        out.append(float(np.linalg.norm(u, axis=1).mean() / (E * H / 1000) * 1000))
    return out


def main() -> int:
    pr, info = build()
    print({k: v for k, v in info.items() if k != "load_nodes"})
    if "--check" in sys.argv:
        return 0
    runs = []
    args = [a for i, a in enumerate(sys.argv[1:], 1) if a != "--nx" and sys.argv[i - 1] != "--nx"]
    for v in [float(a) for a in args]:
        t = time.time()
        r = tp.topopt(pr, v, 1.5, ft=1, optimizer="OC", max_iter=50)
        xb = tp.binarize(r["xfiz"], 0.5)["structure"]
        xv = pr.grid.vector(np.asarray(xb, float))
        xv[pr.passive == 1] = 0.0
        xv[pr.passive == 2] = 1.0
        mass = float(xv.sum()) * (H / 1000) ** 3 * RHO
        disp = response(pr, xv, info["load_nodes"])
        runs.append({"volume": v, "iterations": int(r["iteration"]), "grey_percent": float(r["gray"]),
                     "seconds": round(time.time() - t), "mass_kg": mass, "disp_mm_LC1_4": disp,
                     "density": np.asarray(r["xfiz"]).round(3).tolist()})
        print(f"V={v}: {r['iteration']} it, grey {r['gray']:.1f} %, mass {mass:.3f} kg, "
              f"disp LC1-4 {[round(d, 3) for d in disp]} mm, {runs[-1]['seconds']} s", flush=True)
        _save(info, runs)                      # write after every run, so a stopped job keeps what it finished
    return 0


def _save(info: dict, runs: list[dict]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": {k: v for k, v in info.items() if k != "load_nodes"} | {
        "grid": [NX, NY, NZ],
        "note": "coarse 3-D SIMP preview, sum of 4 compliances, OC, rmin 1.5, ft 1, 50 iterations; displacement = "
                "mean |u| of the bore nodes; shape order (nx, ny, nz) of the dolfiny frame"}, "runs": runs}),
        encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
