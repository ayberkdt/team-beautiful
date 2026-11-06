"""Command handlers of the ``aerokit`` CLI.

Each handler takes the parsed :class:`argparse.Namespace` and reports through
:mod:`aerokit.output.console` (``table``, ``note``, ``warn``, ``file``, ``result``); the entry point
captures these calls into one :class:`~aerokit.output.report.Report` and renders it once, in the
requested format. Long computations announce themselves with ``progress`` on stderr. Units are SI
unless an option says otherwise (stress inputs in MPa).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import time
from typing import Any

import numpy as np

from aerokit.data import EXAMPLES_DIR
from aerokit.output.console import file, get_material, note, progress, result, table, warn

Args = argparse.Namespace
G0 = 9.80665


def _require(a: Args, names: str, what: str) -> None:
    missing = [f"--{n.replace('_', '-')}" for n in names.split() if getattr(a, n, None) is None]
    if missing:
        raise ValueError(f"{what} needs {', '.join(missing)}")


def _figure(path: str, build: Any) -> None:
    """Build a figure (``build()`` returns an :class:`aerokit.output.figures.Figure`) and report it."""
    progress("rendering and auditing the figure")
    fig = build()
    file(f"{path}.png")
    if fig.report.errors:
        warn(f"figure audit found {fig.report.errors} error(s): {fig.report.summary}")
    else:
        note(fig.report.summary)


def _num(v: float, unit: str = "") -> str:
    """Readable number with unit: grouped digits above 1000, never E notation."""
    if v != v:
        return "—"
    text = f"{v:,.0f}".replace(",", " ") if abs(v) >= 1000 else (f"{v:.1f}" if abs(v) >= 10 else f"{v:.4g}")
    return f"{text} {unit}" if unit and unit != "-" else text


def _sequence(text: str) -> list[float]:
    """Parse a stacking sequence such as ``"0,45,-45,90,s"`` (trailing ``s`` = symmetric)."""
    parts = [x.strip() for x in text.replace(";", ",").split(",") if x.strip()]
    if not parts:
        raise ValueError("empty stacking sequence")
    sym = parts[-1].lower() == "s"
    try:
        angles = [float(x) for x in (parts[:-1] if sym else parts)]
    except ValueError as exc:
        raise ValueError(f"stacking sequence must be numbers separated by commas: {text!r}") from exc
    return angles + angles[::-1] if sym else angles


# ============================================================ aero
def isa(a: Args) -> None:
    """ISA atmosphere table."""
    from aerokit.aero import atmosphere
    rows = []
    for h in a.h:
        d = atmosphere.isa(h)
        rows.append([f"{h:.0f}", f"{d['T']:.2f}", f"{d['p']:.0f}", f"{d['rho']:.4f}", f"{d['mu'] * 1e5:.4f}",
                     f"{d['nu'] * 1e5:.3f}", f"{d['a']:.1f}"])
    table(["h (m)", "T (K)", "p (Pa)", "ρ (kg/m³)", "μ×1e5 (Pa·s)", "ν×1e5 (m²/s)", "a (m/s)"], rows)
    last = atmosphere.isa(a.h[-1])
    result(f"At {a.h[-1]:.0f} m ρ = {last['rho']:.4f} kg/m³ (σ = {atmosphere.sigma(a.h[-1]):.3f}).",
           "Enter ρ and μ as constants in the Fluent material panel, or compute Re with 'aero flow'.")


def flow(a: Args) -> None:
    """Reynolds and Mach numbers, first-cell height, layer count, cell budget."""
    from aerokit.aero import flow as fl
    y1, _, Re, _ = fl.first_cell(a.U, a.L, a.yplus, a.h)
    M = fl.mach(a.U, a.h)
    d = fl.boundary_layer(a.U, a.L, a.h)
    n = fl.layer_count(y1, d, a.growth)
    rows = [["Reynolds", f"{Re:.3e}", ""], ["Mach", f"{M:.3f}", "≲ 0.3 incompressible"],
            [f"First cell (y⁺ = {a.yplus:g})", f"{y1:.3e}", "m, Fluent cell height"],
            ["Boundary layer δ (x = L)", f"{d:.3e}", "m, turbulent flat plate"],
            [f"Layers (growth {a.growth:g})", f"{n}", "to cover δ"]]
    budget = None
    if a.surface:
        budget = fl.cell_budget(a.surface, n)
        rows.append(["Prism cells", f"{budget['prism']:.3e}", f"{a.surface:.0f} faces × {n}"])
        rows.append(["Estimated total", f"{budget['total']:.3e}", "45 % core share assumed"])
    table(["Quantity", "Value", "Note"], rows)
    if budget and budget["total"] > 0.9e6:
        warn("estimated total exceeds the 0.9 M cell target (student licence limit 1 M).")
        result(f"Re = {Re:.2e}, first cell {y1:.2e} m, {n} layers; the cell budget is exceeded.",
               "Reduce surface faces, raise growth to 1.2, or switch to y⁺ 30–100 wall functions.")
        return
    regime = "compressible: enable ideal gas + energy" if M > 0.3 else "incompressible is acceptable"
    result(f"Re = {Re:.2e}, first cell {y1:.2e} m, {n} layers; flow {regime}.",
           "After solving, check the y⁺ contour (target ≈ 1, avoid 5–30).")


# ============================================================ geometry
def airfoil(a: Args) -> None:
    """NACA 4-digit airfoil points."""
    from aerokit.aero import geometry
    x, y = geometry.naca4(a.naca, n=a.points, closed_trailing_edge=a.closed, chord=a.chord)
    te = geometry.trailing_edge_thickness(x, y)
    if a.output:
        geometry.write_point_file(a.output, x, y, format=a.file_format)
        file(a.output)
    table(["Quantity", "Value"], [["Chord (m)", f"{a.chord:g}"], ["Points", f"{len(x)}"],
                                  ["Trailing-edge thickness (m)", f"{te:.3e}"]], title=f"NACA {a.naca}")
    if not a.output:
        note("Point file not written (give --output).")
    result(f"NACA {a.naca}: {len(x)} points, trailing-edge thickness {te / a.chord * 100:.3f} % c.",
           "Import the file into Discovery/DesignModeler as a point curve and close the surface.")


def planform(a: Args) -> None:
    """Trapezoidal wing planform dimensions."""
    from aerokit.aero import geometry
    p = geometry.planform(a.S, a.AR, a.taper)
    table(["Quantity", "Value (m)"], [[k, f"{v:.4f}"] for k, v in p.items()])
    result(f"b = {p['b']:.3f} m, MAC = {p['MAC']:.3f} m (y = {p['y_MAC']:.3f} m).",
           "Fluent reference length = MAC; on a half model the reference area is S/2.")


def cad(a: Args) -> None:
    """Import STL/OBJ/PLY → geometry report, optional tetrahedral FEM."""
    from aerokit.cad import geometry_report, read
    from aerokit.cad.report import NEXT_STEP_MARKER
    t0 = time.perf_counter()
    surface = read(a.file, unit=a.unit)
    rep = geometry_report(surface, material=a.material)
    lines = rep["text"].rstrip().splitlines()
    last = lines[-1] if lines else ""
    for line in lines[:-1]:
        note(line)
    head, _, tail = last.partition(NEXT_STEP_MARKER)
    if not a.fem:
        result(head.removeprefix("Result:").strip(), tail.strip() or "Run with --fem for a first stress estimate.")
        return
    from aerokit.fem import Model
    from aerokit.fem.elements.solid import T4, T10, D_isotropic3d
    from aerokit.fem.mesh import mesh3d
    if not rep["topology"].get("watertight", True):
        raise ValueError("FEM needs a closed (watertight) surface; see the report's suggestions")
    mat = get_material(a.material or "6061-T6")
    if mat is None or "E" not in mat:
        raise ValueError("CAD FEM needs an isotropic material")
    extent = np.ptp(surface.V, axis=0)
    h = a.h or min(0.08 * extent.max(), 0.5 * extent.min())     # keep interior nodes across thin parts
    progress(f"tetrahedral mesh (h = {h:.4g} m)")
    X, tets, info = mesh3d.tet_mesh_from_surface(surface.V, surface.F, h, kind=a.element)
    note(f"Mesh: {info['n_element']} elements, {info['n_node']} nodes, volume ratio {info['ratio']:.4f}, "
         f"slivers removed {info['n_sliver_removed']}")
    D = D_isotropic3d(mat["E"], mat["nu"])
    cls = T10 if a.element == "T10" else T4
    m = Model(X, 3)
    for t in tets:
        m.add(cls(t, D, rho=mat["rho"]))
    ax = "xyz".index(a.axis)
    lo, hi = X[:, ax].min(), X[:, ax].max()
    tol = 1e-6 * (hi - lo) + 1e-12
    fixed, loaded = np.where(X[:, ax] <= lo + tol)[0], np.where(X[:, ax] >= hi - tol)[0]
    if fixed.size == 0 or loaded.size == 0:
        raise ValueError("no node found on the fixed or the loaded face")
    for d in fixed:
        m.fix(int(d), [0, 1, 2])
    ld = "xyz".index(a.load_direction)
    for d in loaded:
        m.load(int(d), ld, a.load / loaded.size)
    progress(f"static solve ({m.n_dof} DOFs)")
    s = m.static()
    vm = np.array([e["center"]["von_mises"] for e in m.element_results(s.u)])
    U = s.u.reshape(-1, 3)
    i, j = int(np.argmax(np.linalg.norm(U, axis=1))), int(np.argmax(vm))
    xj = X[m.elements[j].nodes[:4]].mean(axis=0)
    table(["Quantity", "Value", "Unit"], [
        ["Fixed / loaded face nodes", f"{fixed.size} / {loaded.size}", f"{a.axis} min / max"],
        ["Max displacement", f"{np.linalg.norm(U[i]) * 1e3:.4g}", "mm"],
        ["Max von Mises (element centre)", f"{vm[j] / 1e6:.4g}", "MPa"],
        ["Location (x, y, z)", ", ".join(f"{v:.3g}" for v in xj), "m"],
        ["Safety factor against yield", f"{mat['Fty'] / vm[j]:.2f}", mat["name"]]])
    warn("preliminary mesh: the load is spread equally over the nodes and stress peaks depend on the mesh "
         f"(reduce h to see convergence); {time.perf_counter() - t0:.1f} s.")
    result(f"Under {a.load:g} N the max displacement is {np.linalg.norm(U[i]) * 1e3:.3g} mm and von Mises "
           f"{vm[j] / 1e6:.3g} MPa.", "Import the same STL into Ansys Mechanical and compare.")


# ============================================================ mechanics
def tensor(a: Args) -> None:
    """Stress tensor: principal values, invariants, von Mises, Tresca, safety."""
    from aerokit.structures import tensor as ts
    if len(a.s) > 6:
        raise ValueError("--s takes at most 6 components")
    g = ts.Stress(*([v * 1e6 for v in a.s] + [0.0] * (6 - len(a.s))))
    w, v = g.principal()
    I1, I2, I3 = g.invariants()
    rows = [[f"σ{i + 1}", f"{w[i] / 1e6:.3f}", f"({v[0, i]:+.3f}, {v[1, i]:+.3f}, {v[2, i]:+.3f})"] for i in range(3)]
    rows += [["von Mises", f"{g.von_mises() / 1e6:.3f}", ""], ["Tresca (σ1−σ3)", f"{g.tresca() / 1e6:.3f}", ""],
             ["τ max", f"{g.max_shear() / 1e6:.3f}", ""], ["Hydrostatic", f"{g.hydrostatic() / 1e6:.3f}", ""],
             ["I1 · I2 · I3", f"{I1 / 1e6:.3f}", f"{I2 / 1e12:.3f} · {I3 / 1e18:.3f} (MPa², MPa³)"]]
    table(["Quantity", "MPa", "Principal direction"], rows)
    mat = get_material(a.material)
    yield_mpa = mat["Fty"] / 1e6 if mat else a.yield_strength
    if yield_mpa:
        fs = g.safety_coefficient(yield_mpa * 1e6)
        result(f"von Mises {g.von_mises() / 1e6:.1f} MPa; safety factor against yield {fs:.2f}.",
               "If FS < 1.5 enlarge the section or change the material (limit load, no-yield criterion).")
    else:
        result(f"von Mises {g.von_mises() / 1e6:.1f} MPa, σ1 = {w[0] / 1e6:.1f} MPa.",
               "Give --yield-strength <MPa> or --material <name> for the safety factor.")


def wing(a: Args) -> None:
    """Wing-root loads, box-beam stresses and margins."""
    from aerokit.aero import wing as wg
    from aerokit.structures import beam
    mat = get_material(a.material)
    W = a.mass * G0
    n_source = "user"
    n = a.n
    if n is None:
        n, _ = wg.n_limit_far23_normal(W)
        n_source = "FAR 23.337 normal category"
    y = wg.span_loads(W, n, a.b, a.c_root, a.c_tip)
    V0, M0 = y["V"][0], y["M"][0]
    sec = beam.box(a.box_b, a.box_h, a.t_skin, a.t_spar)
    sig = beam.bending_stress(M0, sec)
    tau = beam.mean_shear(V0, 2 * a.box_h * a.t_spar)
    panel_b = a.panel_b or a.box_b
    rows = [["Root shear (limit)", f"{V0 / 1e3:.2f} kN", ""], ["Root moment (limit)", f"{M0 / 1e3:.2f} kN·m", ""],
            ["Skin bending stress", f"{sig / 1e6:.1f} MPa", "at limit load"],
            ["Spar shear stress", f"{tau / 1e6:.1f} MPa", "webs carry the shear"]]
    margins: list[tuple[str, float]] = []
    if mat:
        ms_y = beam.safety_margin(mat["Fty"], sig, 1.0)
        ms_u = beam.safety_margin(mat["Ftu"], sig, a.FS)
        s_cr = beam.plate_buckling(mat["E"], mat["nu"], a.t_skin, panel_b)
        ms_b = beam.safety_margin(s_cr, sig, a.FS)
        rows += [["MS yield (limit)", f"{ms_y:+.2f}", f"Fty {mat['Fty'] / 1e6:.0f} MPa"],
                 [f"MS ultimate (×{a.FS:g})", f"{ms_u:+.2f}", f"Ftu {mat['Ftu'] / 1e6:.0f} MPa"],
                 [f"MS panel buckling (×{a.FS:g})", f"{ms_b:+.2f}", f"σ_cr {s_cr / 1e6:.1f} MPa, b {panel_b:g} m"]]
        margins = [("yield", ms_y), ("ultimate", ms_u), ("buckling", ms_b)]
    table(["Quantity", "Value", "Note"], rows)
    note(f"Assumptions: Schrenk distribution, no wing-weight relief, constant box section at the root, "
         f"n = {n:.2f} ({n_source}).")
    if margins:
        mode, ms = min(margins, key=lambda t: t[1])
        result(f"Critical mode {mode}, MS = {ms:+.2f} ({'sufficient' if ms >= 0 else 'INSUFFICIENT'}).",
               "If MS < 0 increase the thickness or reduce the rib spacing (--panel-b); verify in Mechanical.")
    else:
        result(f"Root moment {M0 / 1e3:.1f} kN·m, skin stress {sig / 1e6:.1f} MPa.",
               "Give --material <name> for the margins (list: aerokit materials list).")


def section(a: Args) -> None:
    """Section properties of a rectangle, tube, I-section or DXF profile."""
    from aerokit.structures import section as ks
    if a.shape == "dxf":
        if not a.dxf:
            raise ValueError("--shape dxf needs --dxf <file>")
        from aerokit.cad import dxf
        o = dict(dxf.section_dxf(a.dxf))
        o.setdefault("theta_p", o.get("theta", 0.0))       # cad.dxf names the angle "theta"
    else:
        need = {"rectangle": 2, "tube": 2, "I": 4}[a.shape]
        if len(a.dimension) != need:
            raise ValueError(f"--shape {a.shape} needs {need} values in --dimension")
        if a.shape == "rectangle":
            b, h = a.dimension
            outer, holes = ks.rectangle_polygon(b, h, -b / 2, -h / 2), []
        elif a.shape == "tube":
            D, t = a.dimension
            outer, holes = ks.circle_polygon(D / 2, n=720), [ks.circle_polygon(D / 2 - t, n=720)[::-1]]
        else:
            outer, holes = ks.i_section_polygon(*a.dimension), []
        o = ks.polygon_properties(outer, holes)
    table(["Quantity", "Value", "Unit"], [
        ["Area A", f"{o['A'] * 1e6:.2f}", "mm²"],
        ["Centroid x · y", f"{o['xc'] * 1e3:.2f} · {o['yc'] * 1e3:.2f}", "mm"],
        ["Ix · Iy", f"{o['Ix'] * 1e12:.4g} · {o['Iy'] * 1e12:.4g}", "mm⁴"],
        ["Ixy", f"{o['Ixy'] * 1e12:.4g}", "mm⁴"],
        ["I1 · I2", f"{o['I1'] * 1e12:.4g} · {o['I2'] * 1e12:.4g}", "mm⁴"],
        ["Principal angle θp", f"{o['theta_p']:.2f}", "°"]])
    result(f"A = {o['A'] * 1e6:.1f} mm², Ix = {o['Ix'] * 1e12:.4g} mm⁴.",
           "Unsymmetric bending: aerokit.structures.section.bending_stress; thin-walled open sections: "
           "ThinOpenSection.")


def buckling(a: Args) -> None:
    """Column (Euler/Johnson), plate and thin-cylinder buckling."""
    from aerokit.structures import buckling as bk
    mat = get_material(a.material)
    if mat is None and a.E is None:
        raise ValueError("give --material or --E")
    E = mat["E"] if mat else a.E * 1e9
    nu = mat["nu"] if mat else 0.3
    if a.kind == "column":
        _require(a, "I A L", "a column")
        P = bk.euler_critical(E, a.I, a.L, a.K)
        slender = a.K * a.L / math.sqrt(a.I / a.A)
        rows = [["Euler P_cr", f"{P / 1e3:.3f}", "kN"], ["Slenderness KL/ρ", f"{slender:.1f}", ""]]
        sc = mat["Fty"] if mat else (a.sigma_cy * 1e6 if a.sigma_cy else None)
        regime = "Euler"
        if sc:
            g = bk.johnson_transition_slenderness(sc, E)
            sj = bk.johnson_stress(sc, E, slender)
            rows += [["Johnson transition slenderness", f"{g:.1f}", ""], ["Johnson σ_cr", f"{sj / 1e6:.1f}", "MPa"]]
            if slender < g:
                P, regime = sj * a.A, "Johnson (inelastic)"
        table(["Quantity", "Value", "Unit"], rows)
        result(f"Critical load ≈ {P / 1e3:.2f} kN ({regime} regime).",
               "Compare with 1.5 × the applied load; FEM check: Frame2D buckling (aerokit fem solve).")
    elif a.kind == "plate":
        _require(a, "a_b t b", "a plate")
        k = bk.plate_compression_k(a.a_b, a.edge, nu=nu)
        s = bk.plate_critical_stress(k, E, nu, a.t, a.b)
        table(["Quantity", "Value", "Unit"], [["k (compression)", f"{k:.3f}", f"{a.edge}, a/b = {a.a_b:g}"],
                                              ["σ_cr (elastic)", f"{s / 1e6:.1f}", "MPa"]])
        result(f"Elastic panel buckling stress {s / 1e6:.1f} MPa (k = {k:.2f}).",
               "If σ_cr approaches yield apply the plasticity correction: buckling.plate_plastic_critical.")
    else:
        _require(a, "r t", "a cylinder")
        s = bk.cylinder_axial(E, nu, a.r, a.t)
        table(["Quantity", "Value", "Unit"], [["σ_cr axial (incl. SP-8007 γ)", f"{s / 1e6:.1f}", "MPa"],
                                              ["r/t", f"{a.r / a.t:.0f}", ""]])
        result(f"Thin-cylinder axial buckling {s / 1e6:.1f} MPa (with knock-down factor).",
               "Bending, external pressure, torsion: buckling.cylinder_bending / cylinder_external_pressure / "
               "cylinder_torsion.")


def vessel(a: Args) -> None:
    """Thick-walled cylinder (Lamé) or rotating disk."""
    from aerokit.structures import pressure, rotating
    mat = get_material(a.material)
    if mat is None:
        raise ValueError("--material is required")
    if a.kind == "cylinder":
        _require(a, "ri ro p", "a cylinder")
        r = pressure.lame_inner_surface(a.ri, a.ro, pi=a.p * 1e6, nu=mat["nu"], yield_=mat["Fty"])
        table(["Quantity", "Value", "Unit"], [["Inner-surface von Mises", f"{r['von_mises'] / 1e6:.1f}", "MPa"],
                                              ["Inner-surface Tresca", f"{float(r['tresca']) / 1e6:.1f}", "MPa"],
                                              ["Safety against yield (von Mises)", f"{r['n_von_mises']:.2f}", ""]])
        result(f"Inner-surface von Mises {r['von_mises'] / 1e6:.1f} MPa, safety {r['n_von_mises']:.2f}.",
               "Shrink fits: pressure.interference_pressure; FEM check: axisymmetric Q8.")
    else:
        _require(a, "rpm b", "a disk")
        w = a.rpm * 2 * math.pi / 60
        s = rotating.disk_max_stress(mat["rho"], w, a.b, mat["nu"], a=a.a)
        speed = rotating.disk_speed_limit(mat["Fty"], mat["rho"], a.b, mat["nu"], a=a.a)
        rpm_y = speed * 60 / (2 * math.pi)
        table(["Quantity", "Value", "Unit"], [["Max hoop stress", f"{s / 1e6:.1f}", "MPa"],
                                              ["Speed at first yield", f"{rpm_y:.0f}", "rpm"]])
        result(f"σθ,max = {s / 1e6:.1f} MPa; yield is reached at ≈ {rpm_y:.0f} rpm.",
               "Burst speed: rotating.disk_burst_speed; thermal gradient: rotating.thermal_disk.")


def life(a: Args) -> None:
    """Fatigue safety factor, or critical crack size and Paris life."""
    from aerokit.structures import fatigue, fracture
    if a.kind == "fatigue":
        _require(a, "sa Se Sut", "a fatigue check")
        n = fatigue.safety_coefficient(a.sa * 1e6, a.sm * 1e6, a.Se * 1e6, Sut=a.Sut * 1e6, method=a.method)
        table(["Quantity", "Value"], [["Method", a.method], ["Fatigue safety factor", f"{n:.2f}"]])
        result(f"Fatigue safety factor {n:.2f} ({a.method}).",
               "Variable amplitude: fatigue.rainflow + fatigue.miner_damage.")
        return
    _require(a, "Kc sigma", "a crack check")
    Yf: Any = (lambda x: fracture.Y_center_secant(x, a.W)) if a.W else 1.0
    ac = fracture.critical_crack(a.Kc * 1e6, a.sigma * 1e6, Y=Yf, a_max=0.499 * a.W if a.W else None)
    rows = [["Critical half crack length a_c", f"{ac * 1e3:.2f}", "mm"]]
    if a.C and a.dsigma:
        N = (fracture.paris_life_numeric(a.C, a.m, a.dsigma * 1e6, a.a0, ac, Y=Yf) if a.W
             else fracture.paris_life(a.C, a.m, a.dsigma * 1e6, a.a0, ac))
        rows.append(["Paris life (a0 → a_c)", f"{N:.3g}", "cycles"])
    table(["Quantity", "Value", "Unit"], rows)
    result(f"Critical half crack length {ac * 1e3:.2f} mm.", "Inspection interval = life / scatter factor (e.g. 2).")


def joint(a: Args) -> None:
    """Margins of a single-row bolted/riveted joint."""
    from aerokit.structures import joints
    mat = get_material(a.material)
    if mat is None:
        raise ValueError("--material is required")
    Fsu = a.Fsu * 1e6 if a.Fsu else mat.get("Fsu")
    if Fsu is None:
        raise ValueError("the material has no Fsu; give --Fsu")
    r = joints.joint_margins(a.P, a.d, a.t, Fsu, a.Fbru * 1e6, mat["Ftu"], a.w, a.e, shear_plane=a.planes, FS=a.FS)
    table(["Mode", "MS"], [[k, f"{v:+.2f}"] for k, v in r.items() if k != "critical"])
    result(f"Critical mode {r['critical']}, MS = {r[r['critical']]:+.2f}.",
           "Bolt groups and flexibility-based load sharing: joints.bolt_group, joints.load_distribution.")


# ============================================================ composites
def lamina(a: Args) -> None:
    """CLT ply stresses and Tsai-Wu safety factors."""
    from aerokit.composites import lamina as lm
    mat = get_material(a.material)
    if not mat or "E1" not in mat:
        raise ValueError("--material must be a composite ply (list: aerokit materials list)")
    plies = [(t, a.t) for t in _sequence(a.sequence)]
    Q = lm.Q_matrix(mat["E1"], mat["E2"], mat["nu12"], mat["G12"])
    r = lm.layer_stresses(Q, plies, np.array(a.N), np.array(a.M))
    rows, worst = [], (math.inf, 0)
    for i, k in enumerate(r["layers"], start=1):
        tw = lm.tsai_wu(k["sig12"], mat["Xt"], mat["Xc"], mat["Yt"], mat["Yc"], mat["S12"])
        s1, s2, t12 = (round(v / 1e6, 1) + 0.0 for v in k["sig12"])        # avoid printing −0.0
        rows.append([f"{i}", f"{k['angle']:+.0f}", f"{s1:.1f}", f"{s2:.1f}", f"{t12:.1f}", f"{tw['safety']:.2f}"])
        worst = min(worst, (tw["safety"], i))
    table(["Ply", "Angle (°)", "σ1 (MPa)", "σ2 (MPa)", "τ12 (MPa)", "Tsai-Wu SF"], rows)
    note(f"Material: {mat['name']} · total thickness {len(plies) * a.t * 1e3:.3f} mm · F12* = −0.5 assumed")
    result(f"Weakest ply {worst[1]}, Tsai-Wu safety factor {worst[0]:.2f}.",
           "If SF < 1.5 add plies or align the angles with the load; verify in ACP.")


def failure(a: Args) -> None:
    """Laminate constants and first/last-ply failure."""
    from aerokit.composites import laminate
    mat = get_material(a.material)
    if not mat or "E1" not in mat:
        raise ValueError("--material must be a composite ply")
    plies = laminate.layers(mat, [(t, a.t) for t in _sequence(a.sequence)])
    s = laminate.laminate_constants(plies)
    r = laminate.progressive_failure(plies, (*a.load, 0.0, 0.0, 0.0), criterion=a.criterion)
    table(["Quantity", "Value", "Unit"], [["Ex · Ey", f"{s['Ex'] / 1e9:.2f} · {s['Ey'] / 1e9:.2f}", "GPa"],
                                          ["Gxy · νxy", f"{s['Gxy'] / 1e9:.2f} · {s['nuxy']:.3f}", "GPa · –"],
                                          ["First-ply failure (FPF)", f"{r['fpf']:.4g}", "× load"],
                                          ["Last-ply failure (LPF)", f"{r['lpf']:.4g}", "× load"]])
    result(f"FPF at {r['fpf']:.3g} × the given load, LPF at {r['lpf']:.3g} × ({a.criterion}).",
           "Compare with mode-separating criteria (hashin, puck, larc03); verify in ACP.")


def layup(a: Args) -> None:
    """Stacking-sequence optimisation."""
    from aerokit.optimization import laminate as lo
    mat = get_material(a.material)
    if not mat or "E1" not in mat:
        raise ValueError("--material must be a composite ply")
    progress(f"stacking-sequence search: {a.objective}, {4 * a.n_stack} plies (symmetric, ±45 pairs)")
    search = lo.exhaustive_search if a.method == "exhaustive" else lo.genetic_algorithm
    r = search(mat, a.t, a.n_stack, objective=a.objective, load=tuple(a.load), a=a.a, b=a.b)
    table(["Quantity", "Value"], [["Best stack", r["stack"]], ["Objective value", f"{r['value']:.6g}"],
                                  ["Max contiguous identical plies", str(r.get("adjacency", "–"))],
                                  ["Designs evaluated", str(r.get("n_evaluation", "–"))]])
    result(f"Best stack {r['stack']} (objective {r['value']:.4g}).",
           "Check manufacturing rules (±45 outer plies, balance); verify in ACP.")


# ============================================================ fem
def fem_solve(a: Args) -> None:
    """Solve a JSON model (static, modal or buckling)."""
    from aerokit.fem import reader
    t0 = time.perf_counter()
    m, settings = reader.from_file(a.file)
    progress(f"model {m.n_node} nodes, {len(m.elements)} elements, {m.n_dof} DOFs · {settings['analysis']}")
    o = reader.solve(m, settings)
    if o["analysis"] == "static":
        table(["Quantity", "Value"], [["Node with max displacement", str(o["max_node"])],
                                      ["Displacement (DOF order)", ", ".join(f"{v:.4e}" for v in o["max_disp"])],
                                      ["Strain energy (J)", f"{o['energy']:.4e}"],
                                      ["Reaction sum", ", ".join(f"{v:.4g}" for v in o["reaction_total"])]])
        summary = f"Max displacement at node {o['max_node']}"
    elif o["analysis"] == "modal":
        table(["Mode", "f (Hz)"], [[str(i + 1), f"{f:.4g}"] for i, f in enumerate(o["f"])])
        summary = f"First natural frequency {o['f'][0]:.4g} Hz"
    else:
        table(["Mode", "Load factor λ"], [[str(i + 1), f"{v:.4g}"] for i, v in enumerate(o["lambda_"])])
        summary = f"First buckling load factor {o['lambda_'][0]:.4g}"
    if getattr(a, "plot", None) and o["analysis"] == "static":
        from aerokit.output import figures
        u = o["result"]["u"]
        continuum = m.ndof == 2 and hasattr(m.elements[0], "NATURAL")
        _figure(a.plot, lambda: figures.fem2d_contour(m, u, a.plot) if continuum else figures.frame_shape(m, u, a.plot))
    note(f"Run time {time.perf_counter() - t0:.2f} s")
    result(summary + ".", "Compare with a hand calculation; refine the mesh ('fem convergence') and watch the change.")


def fem_example(a: Args) -> None:
    """List or run the bundled example models."""
    files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not a.name:
        rows = []
        for p in files:
            with open(p, encoding="utf-8") as fh:
                rows.append([p.stem, json.load(fh).get("description", "")])
        table(["Example", "Description"], rows)
        result(f"{len(files)} example models are available.",
               "Run one with 'aerokit fem example <name>' or copy its JSON and edit it.")
        return
    names = {p.stem for p in files}
    if a.name not in names:
        raise ValueError(f"no example named {a.name!r}; choose one of: {', '.join(sorted(names))}")
    a.file = str(EXAMPLES_DIR / f"{a.name}.json")
    fem_solve(a)


def fem_convergence(a: Args) -> None:
    """Mesh-convergence study: refinement, observed order, Richardson, GCI."""
    import copy

    from aerokit.fem import reader
    from aerokit.fem.convergence import study
    with open(a.file, encoding="utf-8") as fh:
        data = json.load(fh)
    if "mesh" not in data:
        raise ValueError("automatic convergence works only for JSON models with a structured 'mesh' entry")
    nx0, ny0 = data["mesh"]["nx"], data["mesh"]["ny"]

    def solve(k: int) -> float:
        v = copy.deepcopy(data)
        v["mesh"]["nx"], v["mesh"]["ny"] = nx0 * k, ny0 * k
        m, _ = reader.build_model(v)
        progress(f"mesh ×{k}: {m.n_node} nodes")
        return float(np.linalg.norm(reader.solve(m, {"analysis": "static", "n": 1})["max_disp"]))
    s = study(solve, tuple(a.levels), label="max displacement")
    table(["Mesh factor", "Elements (nx×ny)", "Value (m)", "Time (s)"],
          [[f"×{k}", f"{nx0 * k}×{ny0 * k}", f"{v:.6e}", f"{t:.2f}"]
           for k, v, t in zip(s["n"], s["values"], s["duration"], strict=True)])
    note(f"Observed order p = {s['p']:.2f} · Richardson value {s['f_ext']:.6e} · "
         f"GCI(fine) = {s['gci_fine'] * 100:.3f} %")
    result(s["interpretation"] + ".",
           "If GCI > 1 % refine one more level, or report the Richardson value together with the GCI.")


def fem_topology(a: Args) -> None:
    """SIMP topology optimisation (top88: OC/MMA, filters)."""
    from aerokit.optimization import topology as tp
    builders = {"mbb": lambda: tp.mbb_half(a.nelx, a.nely), "cantilever": lambda: tp.cantilever(a.nelx, a.nely),
                "lbracket": lambda: tp.l_bracket(a.nelx)}
    pr = builders[a.problem]()
    progress(f"SIMP {a.problem} {a.nelx}×{a.nely}, volume {a.volume:g}, rmin {a.rmin:g}, ft {a.ft}, {a.optimizer}")
    t0 = time.perf_counter()
    r = tp.topopt(pr, a.volume, a.rmin, ft=a.ft, optimizer=a.optimizer, max_iter=a.max_iter)
    table(["Quantity", "Value"], [["Final compliance", f"{r['compliance'][-1]:.4f}"],
                                  ["Iterations · converged", f"{r['iteration']} · {'yes' if r['converged'] else 'no'}"],
                                  ["Volume fraction", f"{r['volume'][-1]:.4f}"],
                                  ["Grey measure M_nd", f"{r['gray']:.1f} %"],
                                  ["Run time", f"{time.perf_counter() - t0:.1f} s"]])
    if a.plot:
        from aerokit.output import figures
        text = (f"{a.nelx}×{a.nely} · volume {a.volume:g} · rmin {a.rmin:g} · "
                f"compliance {r['compliance'][-1]:.2f} · grey {r['gray']:.1f} %")
        _figure(a.plot, lambda: figures.topology_map(r["xfiz"], a.plot, title=f"Topology: {a.problem}, ft = {a.ft}",
                                                     note=text))
    result(f"Compliance {r['compliance'][-1]:.3f} after {r['iteration']} iterations, grey measure {r['gray']:.1f} %.",
           "If the grey measure is high try ft 3 (Heaviside); redraw the result in CAD and check it with FEM.")


def fem_optimum(a: Args) -> None:
    """Minimum-mass truss sizing of a JSON model."""
    from aerokit.fem import reader
    from aerokit.optimization import sizing as so
    m, _ = reader.from_file(a.file)
    A0 = np.array([e.A for e in m.elements])
    pr = so.SizeProblem(m, lower=a.A_min)
    pr.stress_limit(a.tension * 1e6, a.compression * 1e6 if a.compression else None)
    if a.disp_limit is not None:
        if a.disp_node is None:
            raise ValueError("--disp-limit needs --disp-node")
        pr.displacement_limit([m.dof(a.disp_node, a.disp_dof)], a.disp_limit)
    if a.euler:
        pr.euler_buckling_limit()
    m0 = float(pr.mass(A0))                                    # type: ignore[arg-type]
    progress(f"section optimisation (SLSQP, analytic sensitivities): {len(A0)} bars")
    r = so.slsqp(pr, A0)
    table(["Element", "Nodes", "A before (cm²)", "A after (cm²)"],
          [[str(i), f"{e.nodes[0]}-{e.nodes[1]}", f"{A0[i] * 1e4:.3f}", f"{r.areas[i] * 1e4:.3f}"]
           for i, e in enumerate(m.elements)])
    note(r.summary().replace("Result:", "Optimiser status:"))
    if a.plot:
        from aerokit.output import figures
        _figure(a.plot, lambda: figures.truss_areas(m, r.areas, a.plot, A_min=a.A_min,
                                                    title=f"Optimum truss: mass {r.mass:.2f} kg"))
    mass = float(r.mass) if r.mass is not None else float(pr.mass(r.areas))      # type: ignore[arg-type]
    result(f"Mass {m0:.2f} → {mass:.2f} kg ({(mass / m0 - 1) * 100:+.1f} %).",
           "Review the active constraints; round to standard sections and re-solve (fem solve).")


def fem_verify(_a: Args) -> None:
    """Run the FEM test-suite (source checkout only)."""
    import pytest
    tests_dir = pathlib.Path(__file__).resolve().parents[3] / "tests" / "fem"
    if not tests_dir.is_dir():
        raise ValueError(f"FEM test folder not found: {tests_dir} (run from a source checkout)")
    raise SystemExit(pytest.main(["-q", str(tests_dir)]))


# ============================================================ sizing
def raymer(a: Args) -> None:
    """Raymer first-cut sizing with a constraint diagram (defaults: 2023 Ansys task)."""
    from aerokit.aero import sizing
    payload = (a.crew + a.passengers) * a.person_kg + a.extra_load_kg
    W_fixed = payload * G0
    e = sizing.oswald_raymer(a.AR)
    LDmax = a.KLD * math.sqrt(a.AR / a.swet_sref)
    CD0, K = sizing.cd0_ldmax(LDmax, a.AR, e)
    legs = [sizing.SEGMENT["heating_takeoff"], sizing.SEGMENT["climb"],
            sizing.cruise_propeller(a.range_km * 1e3, a.cbhp_cruise, a.eta, LDmax),
            sizing.loiter_propeller(a.loiter_min * 60, a.V_loiter_kmh / 3.6, a.cbhp_loiter, a.eta, 0.866 * LDmax),
            sizing.SEGMENT["landing"]]
    mission = math.prod(legs)
    s = sizing.takeoff_weight(W_fixed, sizing.fuel_ratio(mission), a.kind)
    WS = sizing.ws_stall(a.V_stall_kmh / 3.6, a.CLmax_landing)
    Vmax = a.Vmax_kmh / 3.6
    constraints = {
        f"Climb {a.climb:g} m/s (SL)": sizing.pw_en_good_climb(WS, a.climb, 0, CD0, K, a.eta, a.CLmax_clean, Vmax)[0],
        f"Ceiling {a.ceiling:.0f} m": sizing.pw_en_good_climb(WS, sizing.SERVICE_CEILING_VV, a.ceiling, CD0, K, a.eta,
                                                              a.CLmax_clean, Vmax)[0],
        f"Vmax {a.Vmax_kmh:.0f} km/h ({a.h_vmax:.0f} m)": sizing.pw_required(WS, Vmax, 0, a.h_vmax, CD0, K, a.eta),
        f"Take-off run {a.takeoff_m:.0f} m": sizing.pw_takeoff(WS, a.takeoff_m, a.CLmax_takeoff, a.eta_takeoff),
    }
    governing = max(constraints, key=lambda k: constraints[k])
    PW = constraints[governing]
    S = s["W0"] / WS
    table(["Constraint", "P/W (W/N)", "Power (kW)"],
          [[k, f"{v:.2f}", f"{v * s['W0'] / 1e3:.0f}"] for k, v in constraints.items()],
          title="Constraint diagram (W/S at the stall limit)")
    table(["Quantity", "Value", "Source / assumption"], [
        ["Payload + crew", f"{payload:.0f} kg", f"{a.person_kg:g} kg/person (Raymer example 200 lb)"],
        ["L/Dmax · e · CD0", f"{LDmax:.1f} · {e:.3f} · {CD0:.4f}", f"KLD {a.KLD:g}, Swet/Sref {a.swet_sref:g} assumed"],
        ["Mission fraction Wx/W0", f"{mission:.4f}", "Raymer Table 3.2 + Breguet"],
        ["Wf/W0 · We/W0", f"{s['Wf_W0']:.3f} · {s['We_W0']:.3f}", f"Raymer Table 3.1 ({a.kind})"],
        ["Take-off mass W0", f"{s['W0'] / G0:.0f} kg", "fixed-point iteration"],
        ["W/S · wing area", f"{WS:.0f} N/m² · {S:.1f} m²", f"CLmax landing {a.CLmax_landing:g}"],
        ["Installed power (SL)", f"{PW * s['W0'] / 1e3:.0f} kW", f"governing: {governing}"]])
    result(f"W0 ≈ {s['W0'] / G0:.0f} kg, S ≈ {S:.1f} m², power ≈ {PW * s['W0'] / 1e3:.0f} kW ({governing} governs).",
           "Compare with similar aircraft (prev_guess/01_Ansys/docs/04_2023_example_solution.md), then vary one assumption at a time.")


def vn(a: Args) -> None:
    """V-n diagram (FAR 23 maneuver + gust)."""
    from aerokit.aero import loads
    r = loads.vn_diagram(a.mass * G0, a.S, a.c, a.CLmax, a.CLa, h=a.h, category=a.category)
    table(["Point", "V (m/s)", "V (kt)", "n", "Source"],
          [[p["name"], f"{p['V']:.1f}", f"{p['V_kt']:.0f}", f"{p['n']:.2f}", p["source"]] for p in r["points"]])
    note("Assumptions: " + "; ".join(r["assumptions"]))
    if a.plot:
        from aerokit.output import figures
        _figure(a.plot, lambda: figures.vn_diagram(r, a.plot,
                                                   title=f"V-n diagram, FAR 23 {a.category}, {a.mass:.0f} kg"))
    result(f"n_max = {r['n_max']:.2f}, n_min = {r['n_min']:.2f} ({r['critical']} governs).",
           "Wing root with this n: aerokit mechanics wing --n <n_max> …")


def design(a: Args) -> None:
    """Requirements file → sized aircraft, compliance, sensitivity, figures and report.md."""
    from aerokit.design.pipeline import run
    from aerokit.design.requirements import load_assumptions
    asm = load_assumptions(a.assumptions)
    if a.drag:
        asm = asm.with_(drag_method=a.drag)
    progress("sizing, performance check, sensitivity study" + ("" if a.no_figures else " and figures"))
    r = run(a.requirements, asm, a.out_dir, figures=not a.no_figures)
    s = r.sizing
    table(["Quantity", "Value"], [["Take-off mass", f"{s.mass:.0f} kg"], ["Wing area", f"{s.S:.2f} m²"],
                                  ["Installed power", f"{s.P_installed / 1e3:.0f} kW"], ["Governing", s.governing],
                                  ["L/Dmax · CD0 · e", f"{s.LD_max:.2f} · {s.CD0:.4f} · {s.e:.3f}"],
                                  ["Drag method", str(asm["drag_method"])]])
    from aerokit.design.labels import signed_percent
    table(["Requirement", "Margin", "Pass"], [[c["requirement"], signed_percent(c["margin"]),
                                              "yes" if c["passed"] else "NO"] for c in r.compliance])
    for f in r.files:
        file(str(pathlib.Path(a.out_dir) / f))
    for w in r.report.warnings:
        warn(w)
    result(r.report.result, f"Read {pathlib.Path(a.out_dir) / 'report.md'}; then plan the mission "
                            "('aerokit sizing mission').")


def mission(a: Args) -> None:
    """Search mission for the sized aircraft: route, coverage, waypoints, Aviator sheet, emissions."""
    from aerokit.design import sustainability as su
    from aerokit.design.mission_plan import load_mission, map_figure, optimize, plan, write_outputs
    from aerokit.design.requirements import load_assumptions, load_requirements
    from aerokit.design.sizing import size
    req = load_requirements(a.requirements)
    asm = load_assumptions(a.assumptions)
    if a.drag == "buildup" or (a.drag is None and asm["drag_method"] == "buildup"):
        from aerokit.design.configuration import size_with_buildup
        s = size_with_buildup(req, asm)[0]
    else:
        s = size(req, asm)
    for w in s.warnings:
        warn(w)
    spec = load_mission(a.mission)
    if a.optimize:
        progress("search optimisation: altitude × speed × overlap (grid + refinement)")
        opt, spec = optimize(s.aircraft, spec)
        top = opt.table()
        cols = [0, 1, 2, 3, 5, 6, 8]          # altitude, TAS, spacing, coverage, time, fuel, status: ≤ 7 (Miller)
        table([top.headers[i] for i in cols], [[r[i] for i in cols] for r in top.rows[:5]],
              title=f"Best 5 of {len(opt.candidates)} search plans (largest covered area, then least fuel)")
        tried = sorted({c.altitude for c in opt.candidates})
        if opt.best.altitude >= tried[-1] - 1e-6 and spec.max_search_altitude == math.inf:
            warn(f"the best altitude {opt.best.altitude:.0f} m is the top of the grid and no sensor limit is set: "
                 "give max_search_altitude (from the required ground resolution) in the mission file")
    progress(f"mission simulation ({spec.pattern}, {spec.search_altitude:.0f} m) and fuel-limited coverage")
    mp = plan(s.aircraft, spec)
    fuel_kg = mp.result.fuel_used / G0
    em = su.emissions(fuel_kg, area_km2=mp.area_km2 * mp.coverage)
    table(["Quantity", "Value"], [
        ["Aircraft", f"{s.mass:.0f} kg, {s.P_installed / 1e3:.0f} kW, fuel {s.aircraft.W_fuel / G0:.0f} kg"],
        ["Sensor swath · track spacing", f"{mp.swath:.0f} m · {mp.spacing:.0f} m"],
        ["Pattern", f"{spec.pattern}, {mp.pattern.length / 1e3:.0f} km, area {mp.area_km2:.0f} km²"
                    + (" (polygon)" if spec.area_polygon else "")],
        ["Search altitude · speed", f"{spec.search_altitude:.0f} m · "
                                    + (f"{spec.search_speed * 3.6:.0f} km/h" if spec.search_speed
                                       else "best endurance")],
        ["Wind", "none" if spec.wind is None else
                 f"{spec.wind.speed * 3.6:.0f} km/h from {math.degrees(spec.wind.from_direction) % 360:.0f}°"],
        ["Time on station", f"{mp.time_on_station / 3600:.2f} h"],
        ["Area covered", f"{mp.coverage * 100:.1f} %" + ("" if mp.full_pattern_fits else " (fuel-limited)")],
        ["Mission fuel · CO₂", f"{fuel_kg:.0f} kg · {em.co2_kg:.0f} kg"],
        ["Fuel per km² searched", f"{em.fuel_per_km2:.2f} kg/km²" if em.fuel_per_km2 else "—"]],
        title=spec.name)
    tl = mp.result.timeline()
    keep = [i for i, h in enumerate(tl.headers) if not str(h).startswith("start")]   # ≤ 7 columns (Miller)
    table([tl.headers[i] for i in keep], [[r[i] for i in keep] for r in tl.rows], title="Mission timeline")
    if a.out_dir:
        for f in write_outputs(s.aircraft, mp, a.out_dir):
            file(f)
        if not a.no_figures:
            _figure(str(pathlib.Path(a.out_dir) / "mission_map"),
                    lambda: map_figure(mp, str(pathlib.Path(a.out_dir) / "mission_map")))
    warn("CO2 is tank-to-wake (3.16 kg/kg, ICAO CEC v8 / CORSIA); STK import formats "
         "are not verified — the KML/CSV are the safe hand-off.")
    result(f"{mp.time_on_station / 3600:.1f} h on station covers {mp.coverage * 100:.0f} % of the "
           f"{mp.area_km2:.0f} km² area" + ("." if mp.full_pattern_fits else " (the full pattern needs more fuel)."),
           "Load waypoints.kml into STK/Google Earth and type aviator_sheet.md into Aviator's performance models.")


def validate(a: Args) -> None:
    """Predict King Air 350i performance with the toolkit and compare with published data."""
    from aerokit.design.labels import signed_percent
    from aerokit.design.validation import calibrate_lapse_exponent, validate_king_air
    progress("King Air 350i: drag build-up, ceiling, max speed, take-off, empty weight")
    rows = validate_king_air()
    table(["Quantity", "Published", "Model", "Error", "Note"],
          [[r.quantity, _num(r.published, r.unit), _num(r.predicted, r.unit),
            signed_percent(r.error) if r.published == r.published else "—", r.note]
           for r in rows], title="King Air 350i (Wikipedia 350i column; wing area unverified)")
    n = calibrate_lapse_exponent()
    note(f"Ceiling-calibrated power lapse: P/P_SL = σ^{n:.3f} (one-aircraft calibration).")
    result(f"Largest model errors: take-off {rows[2].error * 100:+.0f} %, empty weight {rows[3].error * 100:+.0f} %, "
           f"ceiling {rows[0].error * 100:+.0f} %.",
           "Use empty_weight_factor 1.118 and power_lapse sigma^n with this n as a calibrated variant in "
           "'sizing design --assumptions'.")


def design_point(a: Args) -> None:
    """Optimum design point of the constraint diagram (2023 requirements)."""
    from aerokit.optimization import design
    g = design.requirement()
    p = design.design_point(g, rule=a.rule)
    table(["Constraint", "P/W (W/N)"], [[k, f"{v:.2f}"] for k, v in p["PW_constraints"].items()])
    result(f"W/S {p['WS']:.0f} N/m², P/W {p['PW']:.2f} W/N ({', '.join(p['active'])} governs).",
           "Take-off weight at this point: 'aerokit sizing raymer'; change requirements with "
           "optimization.design.requirement(...).")


def wing_box(a: Args) -> None:
    """Minimum-mass wing box (regional thicknesses, stringer/rib spacing)."""
    from aerokit.optimization import design
    mat = get_material(a.material)
    if mat is None:
        raise ValueError("--material is required")
    progress(f"minimum-mass wing box ({a.regions} regions, {mat['name']})")
    r = design.wing_box_optimize(a.mass * G0, a.n, a.b, a.c_root, a.c_tip, a.t_c, mat, n_region=a.regions)
    table(["Region", "y (m)", "t skin (mm)", "t web (mm)", "MS min", "Skin mode", "Web mode"],
          [[str(i + 1), f"{g['y0']:.2f}–{g['y1']:.2f}", f"{g['t_skin'] * 1e3:.2f}", f"{g['t_web'] * 1e3:.2f}",
            f"{round(g['MS_min'], 3) + 0.0:+.3f}", g["mod_skin"], g["mod_web"]] for i, g in enumerate(r["regions"])])
    items = [[k, f"{float(v):.1f}"] for k, v in r["items"].items()]
    table(["Item", "Mass (kg)"], [*items, ["Total", f"{r['mass']:.1f}"]])
    note(f"Stringer spacing {r['b_s'] * 1e3:.0f} mm · rib spacing {r['a'] * 1e3:.0f} mm · "
         f"active bounds: {', '.join(r['active_bounds']) or 'none'}")
    result(f"Box mass {r['mass']:.1f} kg, min MS {round(r['MS_min'], 3) + 0.0:+.3f} "
           "(the governing mode of every region has MS ≈ 0).",
           "Review the range of any variable at its bound; verify the result at the wing root with FEM.")


# ============================================================ materials
def materials_list(a: Args) -> None:
    """Catalogue materials and MIL-HDBK-5J sheets."""
    from aerokit.materials import handbook, library
    if a.handbook:
        names = handbook.list_materials()
        table(["MIL-HDBK-5J sheet"], [[n] for n in names])
        result(f"{len(names)} MIL-HDBK-5J material sheets are available.",
               "Read design values with 'aerokit materials allowable <sheet> --thickness <mm>'.")
        return
    rows = []
    for k, v in library.MATERIALS.items():
        rows.append([k, "composite ply" if "E1" in v else "isotropic", v["name"],
                     library.HANDBOOK_SLUG.get(k, "—")])
    table(["Material", "Kind", "Description", "MIL-HDBK-5J sheet"], rows)
    result("Catalogue values are typical (aluminium: AA typical), not design allowables.",
           "Use 'aerokit materials allowable <name>' for MIL-HDBK-5J A/B-basis design values.")


def materials_allowable(a: Args) -> None:
    """MIL-HDBK-5J design allowables of one material, basis, direction and thickness."""
    from aerokit.materials import library
    d = library.design_values(a.name, basis=a.basis, direction=a.direction, thickness=a.thickness,
                              thickness_units=a.thickness_units)
    units = {"Ftu": ("MPa", 1e6), "Fty": ("MPa", 1e6), "Fcy": ("MPa", 1e6), "Fsu": ("MPa", 1e6),
             "E": ("GPa", 1e9), "G": ("GPa", 1e9), "nu": ("–", 1.0), "rho": ("kg/m³", 1.0)}
    rows = [[k, f"{d[k] / f:.4g}", u] for k, (u, f) in units.items() if k in d]
    th = "any" if a.thickness is None else f"{a.thickness:g} {a.thickness_units}"
    table(["Property", "Value", "Unit"], rows,
          title=f"{a.name} · {a.basis}-basis · {a.direction} · thickness {th}")
    note("Source: " + d["source"])
    for u in d["unverified"]:
        warn(u)
    result(f"{a.name} {a.basis}-basis: Ftu {d.get('Ftu', float('nan')) / 1e6:.0f} MPa, "
           f"Fty {d.get('Fty', float('nan')) / 1e6:.0f} MPa.",
           "Pass these values to the sizing commands, or read single values with "
           "aerokit.materials.handbook.get_allowable(...).")


def materials_curve(a: Args) -> None:
    """Ramberg-Osgood stress-strain curve from MIL-HDBK-5J E, Fty and n."""
    from aerokit.materials import handbook, library
    d = library.design_values(a.name, basis=a.basis, direction=a.direction, thickness=a.thickness,
                              thickness_units=a.thickness_units)
    slug = library.handbook_slug(a.name)
    ro = handbook.get_ramberg_osgood_n(slug, a.direction)
    E, f02, n = d["E"], d["Fty"], ro.n
    strain, stress = handbook.ramberg_osgood_curve(E, f02, n, stress_max=a.stress_max * f02, num=a.points)
    Et = handbook.ramberg_osgood_tangent_modulus(stress, E, f02, n)
    rows = [[f"{s / 1e6:.1f}", f"{e * 100:.4f}", f"{t / 1e9:.2f}"] for s, e, t in zip(stress, strain, Et, strict=True)]
    table(["σ (MPa)", "ε (%)", "E_t (GPa)"], rows, title=f"Ramberg-Osgood curve, n = {n:g}")
    note(f"n from MIL-HDBK-5J {ro.figure} (PDF p. {ro.pdf_page}): {ro.caption}")
    warn("n comes from a typical curve; pairing it with A/B-basis Fty is an engineering approximation.")
    result(f"At Fty = {f02 / 1e6:.0f} MPa the plastic strain is 0.2 %; E_t there is "
           f"{float(handbook.ramberg_osgood_tangent_modulus(f02, E, f02, n)) / 1e9:.1f} GPa.",
           "Use E_t in inelastic column/plate buckling (buckling.tangent_modulus_column).")
