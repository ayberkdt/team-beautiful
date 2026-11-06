"""Validation table of the bracket toolchain (benchmarks against analytical / published / repository references).

    python 01_Ansys/scripts/bracket_validate.py [--slow]

Writes 01_Ansys/outputs/validation/validation.json and validation.md. ``--slow`` adds the 3-D cantilever
of Ferrari & Sigmund (2020, top3D125: 48 x 24 x 24, f = 0.12) as an orientation run (minutes).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
if os.path.isdir(r"D:\tmp_ideathon\pylib"):
    sys.path.append(r"D:\tmp_ideathon\pylib")

from aerokit.bracket import cards, geometry, matdata  # noqa: E402
from aerokit.bracket import topo3d as t3  # noqa: E402
from aerokit.bracket import voxfem as vf  # noqa: E402
from aerokit.optimization import topology as tp  # noqa: E402
from aerokit.structures.fatigue import kt_hole_heywood  # noqa: E402

OUT = ROOT / "01_Ansys" / "outputs" / "validation"


def patch() -> list[dict]:
    rows = []
    for el in ("H8", "H8IM"):
        h, E, nu, sig = 1e-3, 200e9, 0.3, 100e6
        m = vf.VoxelMesh(np.ones((4, 3, 5), bool), h)
        L = 5 * h
        bot = m.nodes_where(lambda X: np.isclose(X[:, 2], 0))
        A = np.zeros(m.nn)
        for e in np.flatnonzero(m.ijk[:, 2] == 4):
            for n in m.conn[e]:
                if np.isclose(m.X[n, 2], L):
                    A[n] += h * h / 4
        F = np.zeros(m.ndof)
        F[3 * np.arange(m.nn) + 2] = sig * A
        o = m.nodes_where(lambda X: np.all(np.isclose(X, 0), axis=1))[0]
        o2 = m.nodes_where(lambda X, h=h: np.isclose(X[:, 0], 4 * h) & np.isclose(X[:, 1], 0) & np.isclose(X[:, 2], 0))[0]
        r = vf.static(m, E, nu, F, np.r_[3 * bot + 2, 3 * o, 3 * o + 1, 3 * o2 + 1], element=el)[0]
        err = float(np.abs(r.stress_node[:, 2] / sig - 1).max())
        rows.append({"benchmark": f"patch test, uniform tension ({el})", "reference": "exact σz = 100 MPa",
                     "ours": f"max |σz/σ − 1| = {err:.1e}", "pass": err < 1e-9, "source": "exact solution"})
    return rows


def cantilever() -> list[dict]:
    rows = []
    E, nu, P, Lx, b, t = 200e9, 0.3, 1000.0, 100e-3, 10e-3, 10e-3
    I = b * t ** 3 / 12
    G = E / 2 / (1 + nu)
    timo = P * Lx ** 3 / (3 * E * I) + P * Lx / (5 / 6 * G * b * t)
    for el in ("H8", "H8IM"):
        for n in (1, 2, 4):
            h = t / n
            m = vf.VoxelMesh(np.ones((round(Lx / h), n, n), bool), h)
            fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
            tip = m.nodes_where(lambda X: np.isclose(X[:, 0], Lx))
            F = np.zeros(m.ndof)
            F[3 * tip + 2] = -P / len(tip)
            r = vf.static(m, E, nu, F, (3 * fix[:, None] + np.arange(3)).ravel(), element=el)[0]
            ratio = float(-r.U[3 * tip + 2].mean() / timo)
            rows.append({"benchmark": f"cantilever tip deflection, {el}, {n} voxel(s) thick",
                         "reference": f"Timoshenko beam {timo * 1e3:.4f} mm",
                         "ours": f"ratio {ratio:.4f}", "pass": (0.97 < ratio < 1.01) if el == "H8IM" else None,
                         "source": "Timoshenko & Gere (shear coefficient 5/6) [textbook formula]"})
    return rows


def plate_hole() -> list[dict]:
    """Thin plate W 40, L 120, t 2 mm, central hole d 10 mm, uniform tension; Kt_net vs Heywood."""
    rows = []
    W, L, t, d = 40e-3, 120e-3, 2e-3, 10e-3
    kt_ref = kt_hole_heywood(d, W, "net")
    for h in (1e-3, 2e-3 / 3, 0.5e-3):
        dr = geometry.load_drawing({"units": "m", "solids": [
            {"op": "add", "type": "box", "min": [0, 0, 0], "max": [L, W, t]},
            {"op": "cut", "type": "cylinder", "p0": [L / 2, W / 2, -1e-3], "p1": [L / 2, W / 2, t + 1e-3],
             "radius": d / 2}]})
        vm = geometry.voxelize_drawing(dr, h)
        m = vf.VoxelMesh(vm.solid, vm.h, vm.origin, frac=vm.frac_of_solid())
        x0 = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
        x1 = m.nodes_where(lambda X: np.isclose(X[:, 0], L))
        sig = 100e6
        F = np.zeros(m.ndof)
        F[3 * x1] = sig * W * t / len(x1)
        corner = m.nodes_where(lambda X: np.isclose(X[:, 0], 0) & np.isclose(X[:, 1], 0) & np.isclose(X[:, 2], 0))
        c2 = m.nodes_where(lambda X: np.isclose(X[:, 0], 0) & np.isclose(X[:, 1], W) & np.isclose(X[:, 2], 0))
        fixed = np.r_[3 * x0, 3 * corner + 1, 3 * corner + 2, 3 * c2 + 2]
        r = vf.static(m, 200e9, 0.3, F, fixed)[0]
        mid = np.abs(m.X[:, 0] - L / 2) < 0.6 * h
        smax = float(r.stress_node[mid, 0].max())
        kt = smax / (sig * W / (W - d))
        rows.append({"benchmark": f"plate with hole, Kt_net (voxel {h * 1e3:.2f} mm, {m.ne} el.)",
                     "reference": f"Heywood Kt_net = {kt_ref:.3f} (d/W = 0.25)", "ours": f"{kt:.3f} "
                     f"({100 * (kt / kt_ref - 1):+.1f} %)", "pass": None,
                     "source": "Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood"})
    return rows


def topo_vs_repo() -> list[dict]:
    nx, ny, nz = 24, 8, 4
    r0 = tp.topopt(tp.cantilever_3d(nx, ny, nz), 0.3, 1.5, ft=2, max_iter=30)
    m = vf.VoxelMesh(np.ones((nx, ny, nz), bool), 1.0)
    fix = m.nodes_where(lambda X: X[:, 0] == 0)
    tip = m.nodes_where(lambda X: (X[:, 0] == nx) & (X[:, 1] == 0))
    F = np.zeros(m.ndof)
    F[3 * tip + 1] = -1.0 / len(tip)
    r = t3.optimize(m, F, (3 * fix[:, None] + np.arange(3)).ravel(), 0.3, rmin=1.5, projection=False,
                    emin_ratio=1e-9, max_iter=30)
    a, b = r0["compliance"][-1], r.compliance[-1]
    return [{"benchmark": "3-D SIMP vs repository topology.topopt (24×8×4, V 0.3, density filter, 30 it.)",
             "reference": f"c = {a:.4f} (aerokit.optimization.topology, top88 family)",
             "ours": f"c = {b:.4f} ({100 * (b / a - 1):+.3f} %)", "pass": abs(b / a - 1) < 5e-3,
             "source": "Andreassen et al. 2011 code family; top88 MBB exact in tests/optimization"}]


def am_adjoint() -> list[dict]:
    m = vf.VoxelMesh(np.ones((5, 4, 6), bool), 1.0)
    am = t3.AMFilter3D(m, 2, 1)
    rng = np.random.default_rng(1)
    x = rng.uniform(0.1, 0.9, m.ne)
    w = rng.normal(size=m.ne)
    g = am.backward(x, w)
    err = 0.0
    for i in range(m.ne):
        d = np.zeros(m.ne)
        d[i] = 1e-6
        num = (w @ am.forward(x + d) - w @ am.forward(x - d)) / 2e-6
        err = max(err, abs(num - g[i]))
    rel = err / np.abs(g).max()
    return [{"benchmark": "3-D AM overhang filter adjoint vs central differences", "reference": "finite differences",
             "ours": f"max rel. error {rel:.1e}", "pass": rel < 1e-6, "source": "Langelaar 2017 Eq. (10)-(14)"}]


def cards_roundtrip(tmp: Path) -> list[dict]:
    p = cards.write_matml(tmp / "ed.xml", [matdata.get(k) for k in matdata.names()])
    back = cards.read_matml(p)
    real = cards.read_matml(Path(r"D:\tmp_ideathon\ansys\steel_eglass_air.xml")) \
        if Path(r"D:\tmp_ideathon\ansys\steel_eglass_air.xml").exists() else {}
    ok = all(isinstance(v.get("Young's Modulus"), list) for v in back.values())
    rs = real.get("Structural Steel", {})
    return [{"benchmark": "MatML write → parse (all candidates); parser on a real Workbench 23.1 export",
             "reference": "values written; Ansys export: rho 7850, E 2e11, Fty 2.5e8",
             "ours": f"{len(back)} materials parsed; real export read: rho {rs.get('Density')}, E "
                     f"{rs.get(chr(89) + 'oung' + chr(39) + 's Modulus')}, Fty {rs.get('Tensile Yield Strength')}",
             "pass": ok and (not rs or rs.get("Density") == 7850), "source": "pymaterials-manager test data"}]


def step_roundtrip(tmp: Path) -> list[dict]:
    from aerokit.bracket import cadout
    if not cadout.gmsh_available():
        return [{"benchmark": "STEP round trip", "reference": "-", "ours": "gmsh not available", "pass": None,
                 "source": "-"}]
    d = geometry.load_drawing(ROOT / "01_Ansys" / "inputs" / "sketch_bracket.json")
    r = cadout.drawing_to_cad(d, tmp / "s.step")
    V, F = cadout.read_any(tmp / "s.step")
    rows = []
    for h in (2e-3, 1e-3):
        vs = geometry.voxelize_surface(V, F, h)
        rows.append({"benchmark": f"drawing → STEP (OCC) → gmsh surface → voxels ({h * 1e3:.0f} mm)",
                     "reference": f"exact B-rep volume {r['volume_mm3']:.0f} mm³",
                     "ours": f"{vs.volume * 1e9:.0f} mm³ ({100 * (vs.volume * 1e9 / r['volume_mm3'] - 1):+.2f} %)",
                     "pass": abs(vs.volume * 1e9 / r["volume_mm3"] - 1) < 0.03, "source": "gmsh 4.15.2 / OCC"})
    return rows


def t10_benchmarks(tmp: Path) -> list[dict]:
    """Conforming 10-node tets (gmsh): cantilever and plate-with-hole Kt, same references as the voxel rows."""
    from aerokit.bracket import cadout, tetfem
    if not cadout.gmsh_available():
        return [{"benchmark": "T10 benchmarks", "reference": "-", "ours": "gmsh not available", "pass": None,
                 "source": "-"}]
    rows = []
    E, nu, P = 200e9, 0.3, 1000.0
    d = geometry.load_drawing({"units": "mm", "solids": [{"op": "add", "type": "box", "min": [0, 0, 0],
                                                           "max": [100, 10, 10]}]})
    cadout.drawing_to_cad(d, tmp / "beam.step")
    I = 0.01 ** 4 / 12
    G = E / 2 / (1 + nu)
    timo = P * 0.1 ** 3 / (3 * E * I) + P * 0.1 / (5 / 6 * G * 1e-4)
    for size in (5.0, 2.5):
        m = tetfem.mesh_cad(tmp / "beam.step", size)
        K, _ = tetfem._stiffness(m, E, nu)
        a = tetfem._face_weights(m)
        fix = np.flatnonzero(np.isclose(m.X[:, 0], 0))
        tip = np.flatnonzero(np.isclose(m.X[:, 0], 0.1))
        F = np.zeros(m.ndof)
        F[3 * tip + 2] = -P * a[tip] / a[tip].sum()
        U, _ = vf.solve(K, F, (3 * fix[:, None] + np.arange(3)).ravel(), m.X, direct_limit=10**7)
        ratio = float(-(U[3 * tip + 2] * a[tip]).sum() / a[tip].sum() / timo)
        rows.append({"benchmark": f"cantilever tip deflection, T10 (gmsh), size {size:g} mm, {len(m.T)} el.",
                     "reference": f"Timoshenko beam {timo * 1e3:.4f} mm", "ours": f"ratio {ratio:.4f}",
                     "pass": 0.97 < ratio < 1.01, "source": "Timoshenko & Gere (shear coefficient 5/6)"})
    W, L, t, dh = 40.0, 120.0, 2.0, 10.0
    kt_ref = kt_hole_heywood(dh, W, "net")
    d = geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [L, W, t]},
        {"op": "cut", "type": "cylinder", "p0": [L / 2, W / 2, -1], "p1": [L / 2, W / 2, t + 1], "radius": dh / 2}]})
    cadout.drawing_to_cad(d, tmp / "plate.step")
    for size in (2.0, 1.0):
        m = tetfem.mesh_cad(tmp / "plate.step", size, curvature=24)
        K, edof = tetfem._stiffness(m, E, nu)
        a = tetfem._face_weights(m)
        x0 = np.flatnonzero(np.isclose(m.X[:, 0], 0))
        x1 = np.flatnonzero(np.isclose(m.X[:, 0], L * 1e-3))
        F = np.zeros(m.ndof)
        sig = 100e6
        F[3 * x1] = sig * W * t * 1e-6 * a[x1] / a[x1].sum()
        c0 = int(np.argmin(np.linalg.norm(m.X - [0, 0, 0], axis=1)))
        c1 = int(np.argmin(np.linalg.norm(m.X - [0, W * 1e-3, 0], axis=1)))
        fixed = np.r_[3 * x0, 3 * c0 + 1, 3 * c0 + 2, 3 * c1 + 2]
        U, _ = vf.solve(K, F, fixed, m.X, direct_limit=10**7)
        setup = {"holes": [], "supports": [], "load_cases": []}
        del setup
        # nodal sigma_x averaged (same routine as static_t10)
        D = E * vf.D_iso(nu)
        sn = np.zeros((len(m.X), 6))
        cnt = np.bincount(m.T.ravel(), minlength=len(m.X)).astype(float)
        for k in range(10):
            J = np.einsum("nk,enl->ekl", tetfem._DN_NODES[k], m.X[m.T])
            dNx = np.einsum("ekl,nl->enk", np.linalg.inv(J), tetfem._DN_NODES[k])
            ue = U[edof].reshape(-1, 10, 3)
            gr = np.einsum("eni,enj->eij", ue, dNx)
            eps = np.stack([gr[:, 0, 0], gr[:, 1, 1], gr[:, 2, 2], gr[:, 1, 2] + gr[:, 2, 1], gr[:, 0, 2] + gr[:, 2, 0],
                            gr[:, 0, 1] + gr[:, 1, 0]], axis=1)
            np.add.at(sn, m.T[:, k], eps @ D.T)
        sn /= cnt[:, None]
        kt = float(sn[:, 0].max() / (sig * W / (W - dh)))
        rows.append({"benchmark": f"plate with hole, Kt_net, T10 (gmsh), size {size:g} mm, {len(m.T)} el.",
                     "reference": f"Heywood Kt_net = {kt_ref:.3f}", "ours": f"{kt:.3f} ({100 * (kt / kt_ref - 1):+.1f} %)",
                     "pass": abs(kt / kt_ref - 1) < 0.05,
                     "source": "Heywood 1952 via aerokit.structures.fatigue.kt_hole_heywood"})
    return rows


def ferrari_sigmund() -> list[dict]:
    nx, ny, nz = 48, 24, 24
    m = vf.VoxelMesh(np.ones((nx, ny, nz), bool), 1.0)
    fix = m.nodes_where(lambda X: X[:, 0] == 0)
    tip = m.nodes_where(lambda X: (X[:, 0] == nx) & (X[:, 1] == 0))
    F = np.zeros(m.ndof)
    F[3 * tip + 1] = -1.0 / len(tip)
    t0 = time.time()
    r = t3.optimize(m, F, (3 * fix[:, None] + np.arange(3)).ravel(), 0.12, rmin=math.sqrt(3), max_iter=100,
                    beta_every=20, beta_max=16, emin_ratio=1e-9)
    return [{"benchmark": "3-D cantilever 48×24×24, V 0.12, rmin √3, projection, 100 it. (orientation only)",
             "reference": "Ferrari & Sigmund 2020 top3D125: c = 3993.7 (Neumann) / 4074.3 (Dirichlet); their "
                          "load line, penalty and continuation schedule not confirmed here",
             "ours": f"c = {r.compliance[-1]:.4g} with a unit TOTAL load on the {len(tip)}-node edge; "
                     f"{r.compliance[-1] * len(tip) ** 2:.4g} if each node carried a unit load (c ∝ load²); "
                     f"{r.iterations} it., {time.time() - t0:.0f} s — NOT reproduced (load convention, penalty and "
                     "continuation of top3D125 unconfirmed)", "pass": None,
             "source": "arXiv 2005.05436 Sec. 4, Fig. 8 (read by sub-agent)"}]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(os.environ.get("TEMP", str(OUT)))
    rows: list[dict] = []
    for f in (patch, cantilever, plate_hole, topo_vs_repo, am_adjoint):
        t0 = time.time()
        rows += f()
        print(f"{f.__name__}: {time.time() - t0:.1f} s", flush=True)
    rows += cards_roundtrip(tmp)
    rows += step_roundtrip(tmp)
    rows += t10_benchmarks(tmp)
    if "--slow" in sys.argv:
        rows += ferrari_sigmund()
    for r in rows:
        r["pass"] = None if r["pass"] is None else bool(r["pass"])
    (OUT / "validation.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    md = "# Bracket toolchain validation\n\n`python 01_Ansys/scripts/bracket_validate.py" + (" --slow" if "--slow" in sys.argv
                                                                                  else "") + "` " \
         f"({time.strftime('%Y-%m-%d %H:%M')})\n\n| Benchmark | Reference | Ours | Pass | Source |\n|---|---|---|---|---|\n"
    for r in rows:
        ps = {True: "yes", False: "**NO**", None: "info"}[r["pass"]]
        md += f"| {r['benchmark']} | {r['reference']} | {r['ours']} | {ps} | {r['source']} |\n"
    (OUT / "validation.md").write_text(md, encoding="utf-8")
    sys.stdout.buffer.write(md.encode("utf-8"))
    return 0 if all(r["pass"] is not False for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
