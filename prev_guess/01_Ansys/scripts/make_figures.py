"""Regenerate every figure in ``outputs/`` through the public API (reproducible, datawiz-audited).

Usage::

    python prev_guess/01_Ansys/scripts/make_figures.py            # all figures
    python prev_guess/01_Ansys/scripts/make_figures.py vn topo    # only figures whose name contains one of the words

Each figure writes PNG, PDF, a colour-vision preview and ``<name>.denetim.txt``; the script prints
the audit line of every figure and exits 1 if any audit reports an error.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "prev_guess" / "01_Ansys" / "outputs"

from aerokit.output import figures  # noqa: E402


def plate_hole_vm(path: str) -> figures.Figure:
    """Quarter model of a plate with a central hole under 100 MPa tension (Kirsch problem)."""
    from aerokit.fem import Model
    from aerokit.fem.elements.plane import Q8, D_isotropic
    from aerokit.fem.mesh import mesh2d
    X, conn, edges = mesh2d.quarter_plate_with_hole(0.01, 0.05, 6, 8, "Q8", ratio=3)
    m = Model(X, 2)
    for c in conn:
        m.add(Q8(c, D_isotropic(70e9, 0.33, "stress"), t=0.002))
    right = [k for k in edges["right"] if all(abs(X[i, 0] - 0.05) < 1e-9 for i in k)]
    m.F += mesh2d.edge_load(X, right, traction=lambda x, y: (100e6, 0.0), t=0.002)
    for n in mesh2d.edge_nodes(edges["lower"]):
        m.fix(n, 1)
    for n in mesh2d.edge_nodes(edges["upper"]):
        m.fix(n, 0)
    return figures.fem2d_contour(m, m.static().u, path, title="Plate with hole, σ∞ = 100 MPa (quarter model)")


def _truss_bridge():
    from aerokit.data import example_path
    from aerokit.fem import reader
    return reader.from_file(example_path("truss_bridge.json"))[0]


def truss_bridge_shape(path: str) -> figures.Figure:
    m = _truss_bridge()
    return figures.frame_shape(m, m.static().u, path, title="Warren truss bridge, deformed shape")


def truss_bridge_optimum(path: str) -> figures.Figure:
    import numpy as np

    from aerokit.optimization import sizing
    m = _truss_bridge()
    pr = sizing.SizeProblem(m, lower=1e-6)
    pr.stress_limit(150e6)
    pr.displacement_limit([m.dof(2, 1)], 0.01)
    r = sizing.slsqp(pr, np.array([e.A for e in m.elements]))
    return figures.truss_areas(m, r.areas, path, A_min=1e-6, title=f"Optimum truss: mass {r.mass:.2f} kg")


def ten_bar_optimum(path: str) -> figures.Figure:
    from aerokit.optimization import sizing
    pr = sizing.ten_bar_truss(1)
    r = sizing.slsqp(pr)
    return figures.truss_areas(pr.model, r.areas, path, A_min=float(pr.lower[0]), unit="in", area_unit=("in²", 1.0),
                               title=f"10-bar truss, case 1: {r.mass:.2f} lb")


def _topology(problem: str, ft: int, path: str) -> figures.Figure:
    from aerokit.optimization import topology as tp
    pr = tp.mbb_half(60, 20) if problem == "mbb" else tp.cantilever(60, 30)
    r = tp.topopt(pr, 0.5, 2.4 if problem == "mbb" else 3.0, ft=ft)
    return figures.topology_map(r["xfiz"], path, title=f"Topology: {problem}, ft = {ft}",
                                note=f"compliance {r['compliance'][-1]:.2f} · grey {r['gray']:.1f} %")


def vn_2023(path: str) -> figures.Figure:
    from aerokit.aero import loads
    vn = loads.vn_diagram(5974 * 9.80665, 27.5, 1.81, 2.0, 5.2)
    return figures.vn_diagram(vn, path, title="V-n diagram, FAR 23 normal, 5974 kg (2023 task)")


def wing_span(path: str) -> figures.Figure:
    from aerokit.aero import wing
    y = wing.span_loads(5974 * 9.80665, 3.14, 15.73, 2.33, 1.17)
    return figures.span_distribution(y["y"], y["V"], y["M"], path, title="Half-wing limit loads, n = 3.14 (Schrenk)")


FIGURES: dict[str, Callable[[str], figures.Figure]] = {
    "plate_hole_vm": plate_hole_vm,
    "truss_bridge_shape": truss_bridge_shape,
    "truss_bridge_optimum": truss_bridge_optimum,
    "ten_bar_optimum": ten_bar_optimum,
    "topology_mbb_ft1": lambda p: _topology("mbb", 1, p),
    "topology_mbb_ft3": lambda p: _topology("mbb", 3, p),
    "topology_cantilever": lambda p: _topology("cantilever", 1, p),
    "vn_2023": vn_2023,
    "wing_span": wing_span,
}


def main(argv: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    chosen = [n for n in FIGURES if not argv or any(w in n for w in argv)]
    failed = 0
    for name in chosen:
        fig = FIGURES[name](str(OUT / name))
        failed += fig.report.errors > 0
        print(f"{name:<22} {fig.report.summary}")
    print(f"{len(chosen)} figure(s), {failed} with audit errors")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
