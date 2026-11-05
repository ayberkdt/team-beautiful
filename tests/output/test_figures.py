"""Figures: every figure passes the datawiz audit with 0 errors and writes its files."""
import os
import tempfile

import numpy as np

from aerokit.data import EXAMPLES_DIR
from aerokit.verification import check, check_true


def _files_written(base: str) -> bool:
    return all(os.path.exists(base + ext) for ext in (".png", ".pdf", ".cvd.png", ".denetim.txt"))


def test_figures_audit_passes():
    from aerokit.aero import wing
    from aerokit.fem import Model, reader
    from aerokit.fem.elements.plane import Q8, D_isotropic
    from aerokit.fem.mesh import mesh2d
    from aerokit.output import figures
    d = tempfile.mkdtemp(prefix="aerokit_plot_")
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
    u = m.static().u
    for field in ("von_mises", "sx"):
        base = os.path.join(d, f"contour_{field}")
        r = figures.fem2d_contour(m, u, base, field=field)
        check(f"figure: 2-D contour ({field}) datawiz audit 0 errors", r.report.errors, 0)
        check_true(f"figure: 2-D contour ({field}) files written", _files_written(base))
        check_true(f"figure: 2-D contour ({field}) peak is finite", np.isfinite(r["peak_value"]))
    m2, _ = reader.from_file(EXAMPLES_DIR / "truss_bridge.json")
    r = figures.frame_shape(m2, m2.static().u, os.path.join(d, "truss"))
    check("figure: frame shape audit 0 errors", r.report.errors, 0)
    check_true("figure: English audit summary with counts", r.report.summary.startswith("datawiz audit: 0 error(s)"),
               r.report.summary)
    y = wing.span_loads(5000 * 9.81, 3.0, 15.0, 2.2, 1.1)
    r = figures.span_distribution(y["y"], y["V"], y["M"], os.path.join(d, "span"))
    check("figure: span distribution audit 0 errors", r.report.errors, 0)


def test_vn_figure():
    from aerokit.aero import loads
    from aerokit.output import figures
    d = tempfile.mkdtemp(prefix="aerokit_plot_vn_")
    vn = loads.vn_diagram(5974.0 * 9.80665, 27.5, 1.81, 2.0, 5.2)       # W in newtons
    r = figures.vn_diagram(vn, os.path.join(d, "vn"))
    check("figure: V-n audit 0 errors", r.report.errors, 0)
    check_true("figure: V-n files written", _files_written(os.path.join(d, "vn")))


def test_optimization_figures():
    from aerokit.fem import reader
    from aerokit.output import figures
    d = tempfile.mkdtemp(prefix="aerokit_plot_opt_")
    yy, xx = np.mgrid[0:20, 0:60]
    x = np.clip(np.abs(np.sin(xx / 9.0) * np.cos(yy / 6.0)) * 1.3, 0, 1)
    r = figures.topology_map(x, os.path.join(d, "topo"), title="Topology", note="60×20 · volume 0.5")
    check("figure: topology map audit 0 errors", r.report.errors, 0)
    m, _ = reader.from_file(EXAMPLES_DIR / "truss_bridge.json")
    r = figures.truss_areas(m, np.linspace(1e-4, 8e-4, len(m.elements)), os.path.join(d, "truss"), A_min=1e-4)
    check("figure: truss areas audit 0 errors", r.report.errors, 0)


def test_figure_input_validation():
    import pytest

    from aerokit.fem import reader
    from aerokit.output import figures
    d = tempfile.mkdtemp(prefix="aerokit_plot_bad_")
    with pytest.raises(ValueError):
        figures.topology_map(np.zeros(5), os.path.join(d, "x"))
    m, _ = reader.from_file(EXAMPLES_DIR / "truss_bridge.json")
    with pytest.raises(ValueError):
        figures.truss_areas(m, [1e-4], os.path.join(d, "y"))
