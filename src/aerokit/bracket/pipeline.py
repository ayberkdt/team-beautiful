"""One-call bracket redesign: geometry → set-up → baseline FEA (+ 3-level convergence) → topology optimisation at
several volume fractions → stress check per material at the working temperature → material choice → eco audit →
files (report data, CAD/STL, cards, cross-check template, film hand-off).

Material independence: for a homogeneous isotropic part under prescribed loads, the stress field does not depend on
E and the displacements scale with 1/E (Poisson's ratio is held at 0.3 for all candidates — a stated
approximation, ν of the candidates is 0.27-0.33). The topology layouts are therefore computed once and every
material is checked on every layout; the lightest passing (material, layout) pair wins.

Strength criterion [Y, team assumption until the organisers state one]: loads in the set-up are LIMIT loads; at limit
load the von Mises stress outside the support/load zones must not exceed Fty(T), and at ultimate load
(``limit_to_ultimate`` × limit, CS 25.303 factor 1.5) it must not exceed Ftu(T): utilisation
``U = max(σ/Fty(T), 1.5 σ/Ftu(T)) ≤ 1``.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

from aerokit.bracket import ecoaudit, features, geometry, matdata, voxfem
from aerokit.bracket.features import Hole
from aerokit.bracket.topo3d import optimize, overhang_violations, to_grid

__all__ = ["Options", "load_geometry", "holes_from_drawing", "evaluate", "run_design", "Study"]

NU = 0.3


@dataclass
class Options:
    target_elements: int = 25_000
    voxel_mm: float | None = None
    temperature_C: float | None = None              # None → set-up value (default 300)
    baseline: str = "structural_steel"
    candidates: list[str] | None = None
    snapshot_every: int = 5                          # density snapshots of the topology runs (film: iterations)
    volfracs: tuple[float, ...] = (0.5, 0.35, 0.25)
    rmin_vox: float = 2.0
    max_iter: int = 50
    am_filter: bool = False
    convergence: bool = True
    limit_to_ultimate: float = 1.5
    exclusion_vox: float = 3.0                      # stress-exclusion margin = 3 voxels of the BASE mesh, stored in mm
    hole_resolution: float = 2.5                     # smallest support/load bore radius in voxels (at least)
    max_elements: int = 80_000
    calibrate_utilisation: float | None = None       # scale ALL loads so the baseline initial design has this U
    tet_check: bool = True                           # conforming T10 check (needs gmsh and a CAD/drawing input)
    tet_sizes_vox: tuple[float, ...] = (2.0, 1.3)    # T10 mesh sizes in voxel edges (add 0.9 for a third level)
    unit: str = "mm"
    magnitude_N: float = 10_000.0
    element: str = "H8IM"
    log: bool = True


# ------------------------------------------------------------------------------------------------ geometry
@dataclass
class Geometry:
    kind: str                      # "drawing" | "surface"
    drawing: geometry.Drawing | None
    V: np.ndarray | None
    F: np.ndarray | None
    name: str
    source: str
    frame: dict[str, Any] | None = None
    bodies: dict[str, Any] | None = None      # multi-body STEP: body table, selection, fused volume, overlap

    def voxelize(self, h: float) -> geometry.VoxelModel:
        if self.drawing is not None:
            return geometry.voxelize_drawing(self.drawing, h)
        if self.V is None or self.F is None:
            raise ValueError("surface geometry without vertices/faces")
        return geometry.voxelize_surface(self.V, self.F, h, name=self.name)

    def bbox(self) -> tuple[np.ndarray, np.ndarray]:
        if self.drawing is not None:
            return self.drawing.bbox()
        if self.V is None:
            raise ValueError("surface geometry without vertices")
        return self.V.min(0), self.V.max(0)


def rotation_matrix(rx: float, ry: float, rz: float) -> np.ndarray:
    """R = Rz Ry Rx for angles in degrees (applied to column vectors)."""
    a, b, c = np.radians([rx, ry, rz])
    Rx = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    Rz = np.array([[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def pca_rotation(V: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Rotation that maps the principal axes of the solid (area-weighted surface covariance) onto x, y, z
    (largest extent → x, smallest → z), proper (det = +1)."""
    T = V[F]
    A = 0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
    C = T.mean(axis=1)
    c0 = (A[:, None] * C).sum(0) / A.sum()
    D = C - c0
    cov = (A[:, None, None] * np.einsum("ni,nj->nij", D, D)).sum(0) / A.sum()
    w, Q = np.linalg.eigh(cov)
    Q = Q[:, np.argsort(w)[::-1]]
    if np.linalg.det(Q) < 0:
        Q[:, 2] *= -1
    return Q.T


def load_geometry(path: str | Path, unit: str = "mm", rotate: tuple[float, float, float] | None = None,
                  align: str | None = None, bodies: str | list[int] | None = None,
                  work_dir: str | Path | None = None) -> Geometry:
    """Drawing JSON or a mesh/CAD file (STL, OBJ, PLY, STEP, IGES).

    For surface inputs, ``rotate`` (degrees about x, y, z, applied about the centroid) or ``align="pca"`` brings
    an arbitrarily oriented part onto the axes (hole detection and supports work on x/y/z bores). The rotation
    is stored in ``Geometry.frame`` and written to ``setup.json`` (``_frame``) so results can be mapped back.
    """
    p = Path(path)
    if p.suffix.lower() == ".json":
        if rotate or align:
            raise ValueError("--rotate/--align apply to STL/STEP inputs; author drawings in the part's axes")
        d = geometry.load_drawing(p)
        return Geometry("drawing", d, None, None, d.name, str(p))
    from aerokit.bracket.cadout import read_any
    info = None
    if p.suffix.lower() in (".step", ".stp", ".iges", ".igs"):
        info, p = _one_solid(p, bodies, work_dir)
    elif bodies not in (None, "all"):
        raise ValueError("--bodies applies to STEP/IGES inputs")
    V, F = read_any(p, unit=unit)
    g = Geometry("surface", None, V, F, Path(path).stem, str(p), bodies=info)
    if rotate or align:
        R = pca_rotation(V, F) if align == "pca" else rotation_matrix(*rotate)  # type: ignore[misc]
        c = V.mean(axis=0)
        g.V = (V - c) @ R.T + c
        g.frame = {"rotation_matrix": R.tolist(), "about_point_m": c.tolist(),
                   "how": "x_new = R (x_file - c) + c", "source": align or f"rotate {rotate} deg"}
    return g


def _one_solid(p: Path, bodies: str | list[int] | None, work_dir: str | Path | None
               ) -> tuple[dict[str, Any] | None, Path]:
    """A multi-body STEP/IGES (or an explicit ``bodies`` selection) becomes one fused solid STEP in ``work_dir``;
    a single-solid file is used as it is. Disconnected solids after the fuse stop the run with the body table:
    the day command must not guess which part is the bracket."""
    import tempfile

    from aerokit.bracket import cadout
    table = cadout.step_bodies(p)
    if len(table) <= 1 and bodies in (None, "all"):
        return None, p
    wd = Path(work_dir) if work_dir else Path(tempfile.gettempdir()) / "aerokit_bracket"
    info = cadout.normalise_step(p, wd / f"{p.stem}_solid.step", bodies or "all")
    if info["solids_after_fuse"] > 1:
        rows = "; ".join(f"{b['index']}: {b['volume_mm3']:.0f} mm3, bbox {np.round(b['bbox_mm'], 1).tolist()} mm"
                         for b in table)
        raise ValueError(f"{p.name}: {info['solids_after_fuse']} separate solids remain after fusing bodies "
                         f"{info['selected']} ({rows}). Choose the bracket with --bodies largest or "
                         "--bodies 1,3 (1-based, file order)")
    info["original"] = str(p)
    return info, Path(info["file"])


def holes_from_drawing(d: geometry.Drawing) -> list[Hole]:
    """Exact holes of a drawing: axis-aligned ``cut`` cylinders, intersected with the material they pass through."""
    holes: list[Hole] = []
    for s in d.solids:
        if s.get("op") != "cut" or s["type"] != "cylinder":
            continue
        p0, p1 = np.asarray(s["p0"]), np.asarray(s["p1"])
        u = p1 - p0
        ax = int(np.argmax(np.abs(u)))
        if np.linalg.norm(np.delete(u, ax)) > 1e-9:
            continue
        r = s["radius"]
        # segments: where a ring just outside the hole is solid
        lo, hi = sorted((p0[ax], p1[ax]))
        t = np.linspace(lo, hi, 400)
        ring = np.array([[math.cos(a), math.sin(a)] for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
        solid = np.zeros(len(t), bool)
        i, j = [a for a in range(3) if a != ax]
        for k, tt in enumerate(t):
            P = np.zeros((len(ring), 3))
            P[:, ax] = tt
            P[:, i] = p0[i] + 1.05 * r * ring[:, 0]
            P[:, j] = p0[j] + 1.05 * r * ring[:, 1]
            solid[k] = d.inside(P).mean() > 0.5
        segs = []
        k = 0
        while k < len(t):
            if solid[k]:
                k0 = k
                while k < len(t) and solid[k]:
                    k += 1
                segs.append((float(t[k0]), float(t[k - 1])))
            k += 1
        if not segs:
            continue
        c = p0.astype(float).copy()
        c[ax] = 0.5 * (segs[0][0] + segs[-1][1])
        holes.append(Hole("", ax, c, float(r), segs, 0.0))
    holes.sort(key=lambda q: (q.axis, round(q.center[0], 6), round(q.center[1], 6), round(q.center[2], 6)))
    for n, hl in enumerate(holes, 1):
        hl.id = f"H{n}"
    return holes


def choose_h(g: Geometry, target: int) -> float:
    lo, hi = g.bbox()
    h0 = float(max(hi - lo)) / 40
    v = g.voxelize(h0).volume
    h = (v / target) ** (1 / 3)
    return float(np.round(h * 1e4) / 1e4)                     # 0.1 mm steps


# ------------------------------------------------------------------------------------------------ evaluation
def zone_nodes(mesh: voxfem.VoxelMesh, setup: dict[str, Any], margin_m: float) -> np.ndarray:
    """(nn,) True for nodes inside the support/load exclusion zones (hole radius + margin, segments ± margin)."""
    roles = {d["id"]: d.get("role", "free") for d in setup["holes"]}
    m = np.zeros(mesh.nn, bool)
    g = margin_m
    for d in setup["holes"]:
        if roles.get(d["id"]) not in ("support", "load"):
            continue
        hl = Hole.from_json(d)
        rel = mesh.X - hl.center
        rad = np.linalg.norm(np.delete(rel, hl.axis, axis=1), axis=1)
        za = mesh.X[:, hl.axis]
        inseg = np.zeros(mesh.nn, bool)
        for a, b in hl.segments:
            inseg |= (za >= a - g) & (za <= b + g)
        m |= inseg & (rad <= hl.radius + g)
    return m


def evaluate(mesh: voxfem.VoxelMesh, setup: dict[str, Any], E: float, nu: float = NU, element: str = "H8IM",
             margin_vox: float = 3.0) -> dict[str, Any]:
    """Static analysis of every load case; stresses with limit loads as given in the set-up. The exclusion margin
    is ``setup["exclusion_mm"]`` when present (fixed in mm across meshes), else ``margin_vox`` voxels."""
    ap = features.apply_setup(mesh, setup)
    res = voxfem.static(mesh, E, nu, ap.F, ap.fixed, element=element)
    margin = setup["exclusion_mm"] * 1e-3 if "exclusion_mm" in setup else margin_vox * mesh.h
    zone = zone_nodes(mesh, setup, margin)
    load_holes = sorted({ld["hole"] for c in setup["load_cases"] for ld in c["loads"]})
    cases = []
    for name, r, k in zip(ap.names, res, range(len(res)), strict=True):
        vm_out = np.where(zone, 0.0, r.vm_node)
        j = int(np.argmax(vm_out))
        jall = int(np.argmax(r.vm_node))
        Fk = ap.F[:, k].reshape(-1, 3).sum(0)
        lnodes = np.unique(np.concatenate([ap.nodes[h] for h in load_holes])) if load_holes else np.zeros(0, int)
        u3 = r.U.reshape(-1, 3)
        load_disp = float(np.linalg.norm(u3[lnodes].mean(axis=0))) if len(lnodes) else float("nan")
        cases.append({"name": name, "compliance_J": r.compliance, "max_disp_m": r.max_disp, "load_disp_m": load_disp,
                      "max_disp_at_m": mesh.X[r.max_disp_node].tolist(),
                      "vm_outside_Pa": float(vm_out[j]), "vm_outside_at_m": mesh.X[j].tolist(),
                      "vm_max_Pa": float(r.vm_node[jall]), "vm_max_at_m": mesh.X[jall].tolist(),
                      "vm_element_max_Pa": float(r.vm_element.max()),
                      "applied_N": Fk.tolist(), "reaction_N": r.reaction.tolist(),
                      "solver": r.solve.method, "solve_s": r.solve.seconds, "residual": r.solve.residual})
    return {"cases": cases, "volume_m3": mesh.volume, "elements": mesh.ne, "dofs": mesh.ndof, "h_m": mesh.h,
            "E_Pa": E, "nu": nu, "element": element, "_results": res, "_applied": ap}


def worst(ev: dict[str, Any]) -> dict[str, float]:
    c = ev["cases"]
    return {"max_disp_m": max(x["max_disp_m"] for x in c), "compliance_J": max(x["compliance_J"] for x in c),
            "load_disp_m": max((x.get("load_disp_m", float("nan")) for x in c), default=float("nan")),
            "vm_outside_Pa": max(x["vm_outside_Pa"] for x in c), "vm_max_Pa": max(x["vm_max_Pa"] for x in c)}


# ------------------------------------------------------------------------------------------------ study
@dataclass
class Study:
    name: str
    out: Path
    setup: dict[str, Any]
    vm: geometry.VoxelModel
    mesh: voxfem.VoxelMesh
    keep: np.ndarray
    T: float
    keep_support: np.ndarray = field(default_factory=lambda: np.zeros(0, bool))
    keep_load: np.ndarray = field(default_factory=lambda: np.zeros(0, bool))
    baseline: dict[str, Any] = field(default_factory=dict)
    convergence: list[dict[str, Any]] = field(default_factory=list)
    designs: list[dict[str, Any]] = field(default_factory=list)
    materials: list[dict[str, Any]] = field(default_factory=list)
    choice: dict[str, Any] = field(default_factory=dict)
    eco: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)
    fields: dict[str, Any] = field(default_factory=dict)
    vol_corr: float = 1.0          # (Σ fraction of all voxels) / (Σ fraction of the element voxels): mass correction
    tet: dict[str, Any] = field(default_factory=dict)
    verification: list[dict[str, Any]] = field(default_factory=list)
    stress_factors: dict[str, float] = field(default_factory=dict)
    disp_factors: dict[str, float] = field(default_factory=dict)


def _progress(opt: Options, vf: float) -> Any:
    """Topology callback printing one line every 10 iterations (Doherty: visible progress on long stages)."""
    def cb(it: int, c: float, v: float) -> None:
        if it % 10 == 0:
            _log(opt, f"  topo {round(100 * vf)} %: iteration {it}/{opt.max_iter}, volume {v:.3f}")
    return cb


def _log(opt: Options, *a: Any) -> None:
    if opt.log:
        import sys
        msg = " ".join(str(x) for x in (time.strftime("%H:%M:%S"),) + a)
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(msg.encode(enc, errors="replace").decode(enc, errors="replace"), flush=True)


def _signature(setup: dict[str, Any]) -> str:
    """Hash of what a person edits in a set-up (hole roles, supports, load cases): equal to the stored proposal
    signature → ``roles_source`` "auto", else "edited"."""
    import hashlib
    import json as _json
    core = {"roles": sorted((h["id"], h.get("role")) for h in setup.get("holes", [])),
            "supports": setup.get("supports", []), "load_cases": setup.get("load_cases", [])}
    return hashlib.sha256(_json.dumps(core, sort_keys=True, default=str).encode()).hexdigest()[:16]


def prepare(g: Geometry, out: Path, opt: Options, setup_path: str | Path | None = None) -> Study:
    out.mkdir(parents=True, exist_ok=True)
    h = opt.voxel_mm * 1e-3 if opt.voxel_mm else choose_h(g, opt.target_elements)
    vm = g.voxelize(h)
    if g.drawing is not None:
        holes0 = holes_from_drawing(g.drawing)
    else:
        # STL/STEP: scan for bores at half the voxel size — a bore under ~3 voxels is invisible at h and would be
        # lost silently (4 Nov: Ø4 and Ø6 mm bores missed at 2 mm voxels, all five Ø4–16 mm found at 1 mm)
        holes0 = features.detect_holes(g.voxelize(h / 2))
        _log(opt, f"hole scan at {h * 0.5e3:.2f} mm voxels: {len(holes0)} bores"
                  + (f", smallest Ø {2e3 * min(hl.radius for hl in holes0):.1f} mm" if holes0 else ""))
    if not opt.voxel_mm:
        # resolve the smallest support/load bore: radius >= hole_resolution voxels (element cap max_elements)
        if holes0:
            r_min = min(hl.radius for hl in holes0)
            h_need = r_min / opt.hole_resolution
            if h_need < h:
                h_cap = h * (vm.solid.sum() / opt.max_elements) ** (1 / 3)
                h_new = max(h_need, h_cap)
                _log(opt, f"voxel {h * 1e3:.2f} -> {h_new * 1e3:.2f} mm to resolve the smallest bore "
                          f"(r = {r_min * 1e3:.2f} mm){' - capped by max_elements' if h_new > h_need else ''}")
                h = float(np.round(h_new * 1e4) / 1e4)
                vm = g.voxelize(h)
    _log(opt, f"voxels {vm.shape}, h = {h * 1e3:.2f} mm, solid {int(vm.solid.sum())}")
    if setup_path and Path(setup_path).exists():
        setup = features.load_setup(setup_path)
        setup["roles_source"] = "auto" if _signature(setup) == setup.get("_proposal_signature") else "edited"
        _log(opt, f"set-up read from {setup_path} (roles {setup['roles_source']})")
    elif (out / "setup.json").exists():
        setup = features.load_setup(out / "setup.json")
        setup["roles_source"] = "auto" if _signature(setup) == setup.get("_proposal_signature") else "edited"
        _log(opt, f"set-up read from {out / 'setup.json'} (roles {setup['roles_source']})")
    else:
        holes = holes0                          # drawing: exact; surface: the finer scan (sizes, centres)
        if not holes:
            holes = features.detect_holes(vm)
        small = [hl for hl in holes if hl.radius < 1.5 * h]
        if small:
            _log(opt, f"WARNING {len(small)} bore(s) below 3 voxels at {h * 1e3:.2f} mm (Ø "
                      f"{', '.join(f'{2e3 * hl.radius:.1f}' for hl in small)} mm): their supports/loads act on a "
                      "coarse bore — refine with --voxel or --elements")
        setup = features.propose_setup(vm, holes, magnitude_N=opt.magnitude_N,
                                       temperature_C=opt.temperature_C or 300.0)
        setup["roles_source"] = "auto"
        setup["_proposal_signature"] = _signature(setup)
        _log(opt, f"set-up PROPOSED ({len(holes)} holes) -> edit {out / 'setup.json'} and re-run")
    setup.setdefault("temperature_C", 300.0)
    if g.frame:
        setup["_frame"] = g.frame
    setup.setdefault("exclusion_mm", round(opt.exclusion_vox * h * 1e3, 3))
    if opt.temperature_C is not None:
        setup["temperature_C"] = opt.temperature_C
    features.save_setup(setup, out / "setup.json")
    mesh = voxfem.VoxelMesh(vm.solid, vm.h, vm.origin, frac=vm.frac_of_solid())
    keep = features.non_design_mask(mesh, setup)
    sup = features.non_design_mask(mesh, setup, roles=("support",))
    lod = features.non_design_mask(mesh, setup, roles=("load",))
    vol_all = vm.volume_frac if vm.frac is not None else mesh.volume
    _log(opt, f"partial-volume voxels: fractions of all voxels {vol_all * 1e9:.0f} mm3, of the {mesh.ne} elements "
              f"{mesh.volume * 1e9:.0f} mm3, voxel count {mesh.ne * mesh.h ** 3 * 1e9:.0f} mm3")
    st = Study(g.name, out, setup, vm, mesh, keep, float(setup["temperature_C"]), sup, lod)
    st.vol_corr = vol_all / mesh.volume
    exact = _exact_volume(g, out)
    if exact:                       # B-rep volume known: masses of every layout follow the exact CAD volume
        st.vol_corr = exact / mesh.volume
        _log(opt, f"exact CAD volume {exact * 1e9:.0f} mm3 (voxel fractions {vol_all * 1e9:.0f} mm3, "
                  f"{100 * (vol_all / exact - 1):+.2f} %)")
    return st


def _exact_volume(g: Geometry, out: Path) -> float | None:
    """Exact solid volume [m³] from the B-rep (drawing via OCC, or STEP/IGES input), None without gmsh/CAD."""
    try:
        from aerokit.bracket import cadout
        if not cadout.gmsh_available():
            return None
        if g.drawing is not None:
            (out / "cad").mkdir(parents=True, exist_ok=True)
            return cadout.drawing_to_cad(g.drawing, out / "cad" / "initial.step")["volume_mm3"] * 1e-9
        if Path(g.source).suffix.lower() in (".step", ".stp", ".iges", ".igs"):
            return cadout.cad_volume(g.source) * 1e-9
    except Exception:               # noqa: BLE001 - optional refinement
        return None
    return None


def run_design(g: Geometry, out: str | Path, opt: Options | None = None,
               setup_path: str | Path | None = None) -> Study:
    """Everything except writing the report (see :mod:`aerokit.bracket.report`)."""
    opt = opt or Options()
    out = Path(out)
    t0 = time.perf_counter()
    st = prepare(g, out, opt, setup_path)
    # fail BEFORE any solve when a volume fraction cannot hold the non-design regions (5 Nov: a 0.12 request was
    # rejected only after 24 min of earlier layouts and nothing was written)
    kf = float(st.keep.mean())
    bad = [vf for vf in opt.volfracs if vf <= kf + 0.01]
    if bad:
        raise ValueError(f"volfracs {bad} <= non-design fraction {kf:.3f} + 0.01: raise them or shrink the "
                         "non-design regions")
    _log(opt, f"non-design fraction {kf:.4f} (support {st.keep_support.mean():.4f}, load {st.keep_load.mean():.4f})")
    T = st.T
    crit = st.setup.get("design_criteria", {})
    if "limit_to_ultimate" in crit:
        opt.limit_to_ultimate = float(crit["limit_to_ultimate"])
    base = matdata.get(opt.baseline)
    cands = [matdata.get(k) for k in (opt.candidates or matdata.names())]
    # ---- baseline FEA at T and at 20 °C
    ev = evaluate(st.mesh, st.setup, base.E_at(T), element=opt.element, margin_vox=opt.exclusion_vox)
    ev20 = evaluate(st.mesh, st.setup, base.E_at(20.0), element=opt.element, margin_vox=opt.exclusion_vox)
    if opt.calibrate_utilisation:
        s0 = worst(ev)["vm_outside_Pa"]
        u0 = strength_util(st.setup, opt, s0, base.Fty_at(T), base.Ftu_at(T))
        k = opt.calibrate_utilisation / u0
        st.setup = features.scaled_setup(st.setup, k)
        st.setup["_calibration"] = (f"all loads multiplied by {k:.6g} so that {base.key} on the initial design has "
                                    f"utilisation {opt.calibrate_utilisation:g} at {T:g} C [Y: no loads were given]")
        if st.setup.get("roles_source") == "auto":           # our own scaling is not a person's edit
            st.setup["_proposal_signature"] = _signature(st.setup)
        features.save_setup(st.setup, st.out / "setup.json")
        _log(opt, f"loads calibrated x{k:.4g} (baseline utilisation {u0:.3f} -> {opt.calibrate_utilisation:g})")
        ev = evaluate(st.mesh, st.setup, base.E_at(T), element=opt.element, margin_vox=opt.exclusion_vox)
        ev20 = evaluate(st.mesh, st.setup, base.E_at(20.0), element=opt.element, margin_vox=opt.exclusion_vox)
        st.timings["calibration_factor"] = k
    sn = st.mesh.surface_nodes()
    st.fields["vm_surface_initial"] = (st.mesh.X[sn], np.max([r.vm_node[sn] for r in ev["_results"]], axis=0))
    st.baseline = {"material": base.key, "T_C": T, "mass_kg": st.mesh.volume * st.vol_corr * base.rho.value,
                   "volume_m3": st.mesh.volume * st.vol_corr, "volume_elements_m3": st.mesh.volume,
                   "vol_corr": st.vol_corr, "at_T": {k: v for k, v in ev.items() if not k.startswith("_")},
                   "at_20C": {k: v for k, v in ev20.items() if not k.startswith("_")},
                   "worst_T": worst(ev), "worst_20C": worst(ev20)}
    thermal_sensitivity(st, opt)
    st.timings["baseline_s"] = time.perf_counter() - t0
    _log(opt, f"baseline: mass {st.baseline['mass_kg']:.3f} kg, worst vm_out {worst(ev)['vm_outside_Pa'] / 1e6:.1f} MPa,"
              f" max disp {worst(ev)['max_disp_m'] * 1e3:.4f} mm")
    # ---- 3-level convergence on the initial design
    if opt.convergence:
        h = st.mesh.h
        for f in (1.5, 1.0, 0.75):
            hh = h * f
            if f == 1.0:
                e = ev
                n = st.mesh.ne
            else:
                vmc = g.voxelize(hh)
                if vmc.solid.sum() > 160_000:
                    _log(opt, f"convergence level h = {hh * 1e3:.2f} mm skipped (> 160k elements)")
                    continue
                mc = voxfem.VoxelMesh(vmc.solid, vmc.h, vmc.origin, frac=vmc.frac_of_solid())
                e = evaluate(mc, st.setup, base.E_at(T), element=opt.element, margin_vox=opt.exclusion_vox)
                n = mc.ne
            w = worst(e)
            st.convergence.append({"h_mm": hh * 1e3, "elements": n, "dofs": e["dofs"], **w,
                                   "volume_m3": e["volume_m3"]})
            _log(opt, f"convergence h={hh * 1e3:.2f} mm: n={n}, disp {w['max_disp_m'] * 1e3:.4f} mm, "
                      f"vm_out {w['vm_outside_Pa'] / 1e6:.1f} MPa")
        st.timings["convergence_s"] = time.perf_counter() - t0 - st.timings["baseline_s"]
    # ---- topology optimisation (layout independent of E)
    ap = ev["_applied"]
    c0 = np.array([c["compliance_J"] for c in ev["cases"]]) * base.E_at(T)     # per unit E
    weights = 1.0 / np.maximum(c0, 1e-30)
    bd = st.setup.get("build_direction", "+z")
    am_axis = "xyz".index(bd[-1]) if opt.am_filter else None
    am_sign = -1 if bd.startswith("-") else 1
    x0 = None
    from aerokit.bracket.topo3d import mirror_groups
    planes = st.setup.get("symmetry_planes_mm")
    if planes == "auto":                       # planes detected from the holes, supports and load set (no hand input)
        planes = features.detect_symmetry(st.setup)
        st.setup["_symmetry_detected_mm"] = planes
    sym = mirror_groups(st.mesh, planes) if planes else None
    if sym is not None:
        _log(opt, f"symmetry: {planes} -> {sym.shape[1]} tied variables per group, "
                  f"{100 * float(np.mean(np.all(sym >= 0, axis=1))):.1f} % of elements with every mirror")
    st.designs.append({"label": "initial", "volfrac": 1.0, "volume_m3": st.mesh.volume * st.vol_corr,
                       "stress_unitE": {c["name"]: c["vm_outside_Pa"] for c in ev["cases"]},
                       "disp_unitE": max(c["max_disp_m"] for c in ev["cases"]) * base.E_at(T),
                       "compliance_unitE": max(c["compliance_J"] for c in ev["cases"]) * base.E_at(T),
                       "vm_max_unitE": max(c["vm_max_Pa"] for c in ev["cases"])})
    for vf in sorted(opt.volfracs, reverse=True):
        # 5 Nov: the optimiser ran on fully integrated H8 (shear locking in bending with 1-2 elements through a
        # member) while every evaluation used H8IM -> pass the same element to both
        r = optimize(st.mesh, ap.F, ap.fixed, vf, E0=1.0, nu=NU, keep=st.keep, rmin=opt.rmin_vox, element=opt.element,
                     max_iter=opt.max_iter, am_axis=am_axis, am_sign=am_sign, weights=weights, x0=x0,
                     beta_every=max(8, opt.max_iter // 5),
                     callback=_progress(opt, vf), snapshot_every=getattr(opt, "snapshot_every", 0), sym=sym)
        st.fields[f"snap_{round(100 * vf)}"] = r.snapshots
        x0 = r.x
        solid = r.xphys > 0.5
        # keep only material connected (face to face) to a SUPPORT ring; a load ring outside that set means the
        # layout has no load path and is recorded as failed instead of being analysed (singular stiffness)
        grid = to_grid(st.mesh, solid.astype(float)) > 0.5
        lab, _ = ndimage.label(grid)
        sup_lab = np.unique(lab[tuple(st.mesh.ijk[st.keep_support].T)])
        sup_lab = sup_lab[sup_lab > 0]
        grid &= np.isin(lab, sup_lab)
        load_ok = bool(np.all(grid[tuple(st.mesh.ijk[st.keep_load].T)])) if st.keep_load.any() else True
        # 5 Nov: a layout of SEVERAL bodies (each lug standing on its own bolts) passed this filter — the official
        # v1 layouts were 2 separate parts. One part means one body: the layout is recorded as failed otherwise.
        n_bodies = int(len(np.unique(lab[grid])))
        if n_bodies != 1:
            load_ok = False
            _log(opt, f"topo {round(100 * vf)} %: {n_bodies} separate bodies (not one part)")
        frac_grid = to_grid(st.mesh, np.asarray(st.mesh.frac))
        dm = voxfem.VoxelMesh(grid, st.mesh.h, st.mesh.origin, frac=frac_grid[grid])
        label = f"topo {round(100 * vf)} %"
        try:
            if not load_ok:
                raise ValueError("load ring not connected to the supports, or the layout is not one body")
            e = evaluate(dm, st.setup, 1.0, element=opt.element, margin_vox=opt.exclusion_vox)
        except Exception as exc:                       # noqa: BLE001 - a broken layout must not stop the day
            _log(opt, f"{label}: layout FAILED ({exc}); kept in the report as failed")
            st.designs.append({"label": label, "volfrac": vf, "volume_m3": dm.volume * st.vol_corr, "failed": str(exc),
                               "iterations": r.iterations, "converged": r.converged, "gray_pct": r.gray(),
                               "seconds": r.seconds, "compliance_history": r.compliance, "beta_history": r.beta,
                               "volume_fraction_kept": dm.ne / st.mesh.ne, "overhang_violations": -1,
                               "stress_unitE": {"failed": float("inf")}, "disp_unitE": float("inf"),
                               "compliance_unitE": float("inf"), "vm_max_unitE": float("inf"),
                               "settings": {k: v for k, v in r.settings.items() if k != "cg_iterations"}})
            st.fields[f"xphys_{round(100 * vf)}"] = to_grid(st.mesh, r.xphys)
            continue
        ovh = overhang_violations(dm, np.ones(dm.ne), *(("xyz".index(bd[-1]), am_sign)))
        st.fields[f"xphys_{round(100 * vf)}"] = to_grid(st.mesh, r.xphys)
        st.designs.append({"label": label, "volfrac": vf, "volume_m3": dm.volume * st.vol_corr,
                           "iterations": r.iterations,
                           "converged": r.converged, "gray_pct": r.gray(), "seconds": r.seconds,
                           "compliance_history": r.compliance, "beta_history": r.beta,
                           "volume_fraction_kept": dm.ne / st.mesh.ne, "overhang_violations": ovh,
                           "stress_unitE": {c["name"]: c["vm_outside_Pa"] for c in e["cases"]},
                           "disp_unitE": max(c["max_disp_m"] for c in e["cases"]),
                           "compliance_unitE": max(c["compliance_J"] for c in e["cases"]),
                           "vm_max_unitE": max(c["vm_max_Pa"] for c in e["cases"]),
                           "settings": {k: v for k, v in r.settings.items() if k != "cg_iterations"}})
        st.fields[f"solid_{round(100 * vf)}"] = grid
        sn = dm.surface_nodes()
        st.fields[f"vm_surface_{round(100 * vf)}"] = (dm.X[sn], np.max([q.vm_node[sn] for q in e["_results"]], axis=0))
        _log(opt, f"{label}: {r.iterations} it, {r.seconds:.0f} s, kept {dm.ne / st.mesh.ne:.3f}, "
                  f"vm_out/limit {max(c['vm_outside_Pa'] for c in e['cases']) / 1e6:.1f} MPa")
    st.timings["topology_s"] = time.perf_counter() - t0 - sum(st.timings.values())
    # ---- materials × layouts
    rank_materials(st, opt, cands)
    decide(st, opt)
    if opt.tet_check:
        t2 = time.perf_counter()
        conforming_check(st, g, opt)
        verify_choice(st, g, opt, cands)
        st.timings["tet_check_s"] = time.perf_counter() - t2
    st.timings["total_s"] = time.perf_counter() - t0
    return st


def replay_topology(st: Study, opt: Options, snapshot_every: int = 5) -> dict[str, float]:
    """Re-run the cached study's warm-started topology chain with density snapshots (studies made before
    ``snapshot_every`` existed). Same arguments as :func:`run_design`; returns, per run, the largest difference
    between the replayed and the cached final density (0 when the replay is exact) and stores the snapshots in
    ``st.fields["snap_<vf>"]``."""
    T = st.T
    ap = features.apply_setup(st.mesh, st.setup)
    E = st.baseline["at_T"]["E_Pa"]
    c0 = np.array([c["compliance_J"] for c in st.baseline["at_T"]["cases"]]) * E
    weights = 1.0 / np.maximum(c0, 1e-30)
    bd = st.setup.get("build_direction", "+z")
    am_axis = "xyz".index(bd[-1]) if opt.am_filter else None
    am_sign = -1 if bd.startswith("-") else 1
    x0 = None
    diff: dict[str, float] = {}
    for vf in sorted(opt.volfracs, reverse=True):
        # 5 Nov: the optimiser ran on fully integrated H8 (shear locking in bending with 1-2 elements through a
        # member) while every evaluation used H8IM -> pass the same element to both
        r = optimize(st.mesh, ap.F, ap.fixed, vf, E0=1.0, nu=NU, keep=st.keep, rmin=opt.rmin_vox, element=opt.element,
                     max_iter=opt.max_iter, am_axis=am_axis, am_sign=am_sign, weights=weights, x0=x0,
                     beta_every=max(8, opt.max_iter // 5), snapshot_every=snapshot_every)
        x0 = r.x
        tag = str(round(100 * vf))
        st.fields[f"snap_{tag}"] = r.snapshots
        cached = st.fields.get(f"xphys_{tag}")
        diff[tag] = float(np.abs(to_grid(st.mesh, r.xphys) - cached).max()) if cached is not None else float("nan")
        _log(opt, f"replay topo {tag} %: {r.iterations} it, {len(r.snapshots)} snapshots, max |Δx| vs cache "
                  f"{diff[tag]:.2e} (T = {T:g} C)")
    return diff


def thermal_sensitivity(st: Study, opt: Options) -> dict[str, Any] | None:
    """Constrained expansion of the baseline (fixed bores, no mechanical load) at ΔT = T − 22 °C, the reference
    temperature of Ansys Engineering Data — what Mechanical shows if a Thermal Condition of T is applied with fixed
    supports. Not part of the strength criterion (the mounts are assumed to expand with the bracket) [Y]."""
    base = matdata.get(opt.baseline)
    if base.cte is None:
        return None
    T = st.T
    dT = T - 22.0
    ap0 = features.apply_setup(st.mesh, st.setup)
    rth = voxfem.static(st.mesh, base.E_at(T), NU, np.zeros(st.mesh.ndof), ap0.fixed, element=opt.element,
                        thermal_strain=base.cte.value * dT)[0]
    margin = st.setup["exclusion_mm"] * 1e-3 if "exclusion_mm" in st.setup else opt.exclusion_vox * st.mesh.h
    vth = np.where(zone_nodes(st.mesh, st.setup, margin), 0.0, rth.vm_node)
    th = {"delta_T_K": dT, "alpha_per_K": base.cte.value, "E_T_Pa": base.E_at(T),
          "E_alpha_dT_Pa": base.E_at(T) * base.cte.value * dT, "vm_outside_Pa": float(vth.max()),
          "vm_max_Pa": float(rth.vm_node.max()), "max_disp_m": rth.max_disp}
    st.baseline["thermal"] = th
    _log(opt, f"thermal sensitivity (fixed bores, dT {dT:g} K): vm_out {vth.max() / 1e6:.0f} MPa "
              f"(E alpha dT = {th['E_alpha_dT_Pa'] / 1e6:.0f} MPa)")
    return th


def strength_util(setup: dict[str, Any] | None, opt: Options, s: float, fty: float, ftu: float) -> float:
    """Strength utilisation of a limit-load stress ``s``. Default (unchanged): max(s/Fty, 1.5 s/Ftu). With
    ``design_criteria.strength_basis == "yield"`` (mentor answer 5 Nov 2026: FoS 1.5 on yield): fos · s / Fty."""
    dc = (setup or {}).get("design_criteria", {})
    if dc.get("strength_basis") == "yield":
        return float(dc.get("factor_of_safety", 1.5)) * s / fty
    return max(s / fty, opt.limit_to_ultimate * s / ftu)


def rank_materials(st: Study, opt: Options, cands: list[Any], knockdown: dict[str, float] | None = None,
                   disp_factor: dict[str, float] | None = None) -> None:
    """Every material on every layout. ``knockdown[label]`` multiplies that layout's voxel stress (T10/voxel ratio
    measured on a conforming re-mesh); a layout without a measured ratio keeps its voxel stress and is measured
    itself when it becomes the choice (``verify_choice``)."""
    T = st.T
    kd = knockdown or {}
    k_default = 1.0
    lim_mm = (getattr(st, "setup", None) or {}).get("design_criteria", {}).get("max_displacement_mm")
    u_lim = float(lim_mm) * 1e-3 if lim_mm else None
    st.materials = []
    for m in cands:
        rows = []
        for d in st.designs:
            k = kd.get(d["label"], 1.0 if d["label"] == "initial" and "initial" not in kd else k_default)
            s = max(d["stress_unitE"].values()) * k
            fty, ftu = m.Fty_at(T), m.Ftu_at(T)
            U = strength_util(getattr(st, "setup", None), opt, s, fty, ftu)
            u = d["disp_unitE"] / m.E_at(T) * (disp_factor or {}).get(d["label"], 1.0)
            # 5 Nov: the card's stiffness criterion (max displacement < L/400) was not applied — a 2.17 mm layout
            # passed against a 1.65 mm limit. A layout now passes only if BOTH strength and displacement pass.
            ok_u = u <= u_lim if u_lim else True
            rows.append({"design": d["label"], "mass_kg": d["volume_m3"] * m.rho.value, "vm_limit_Pa": s,
                         "stress_factor": k, "utilisation": U, "passes": U <= 1.0 and ok_u,
                         "max_disp_m": u, "disp_ratio": u / u_lim if u_lim else None})
        temp_ok = m.Tmax.value >= T
        passing = [r_ for r_ in rows if r_["passes"]] if temp_ok else []
        best = min(passing, key=lambda r_: r_["mass_kg"]) if passing else None
        st.materials.append({"key": m.key, "name": m.name, "route": m.route, "am": m.am, "temp_ok": temp_ok,
                             "Tmax_C": m.Tmax.value, "E_T_Pa": m.E_at(T), "Fty_T_Pa": m.Fty_at(T),
                             "Ftu_T_Pa": m.Ftu_at(T), "rho": m.rho.value, "co2_per_kg": m.co2.value,
                             "designs": rows, "best": best})


def verify_choice(st: Study, g: Geometry, opt: Options, cands: list[Any], max_rounds: int = 4) -> None:
    """Re-check the chosen optimised layout on a conforming T10 mesh; if its T10 stress exceeds the voxel stress,
    store the ratio as that layout's stress factor, re-rank and re-decide, and repeat until the chosen layout's T10
    check passes (or the initial design is chosen, which the T10 initial-design check already covers)."""
    from aerokit.bracket import tetfem
    kd: dict[str, float] = {}
    ku: dict[str, float] = {}
    st.verification = []
    for _ in range(max_rounds):
        c = (st.tet or {}).get("chosen")
        if not st.choice or st.choice["design"] == "initial" or c is None:
            break
        d = next(x for x in st.designs if x["label"] == st.choice["design"])
        s_vox = max(d["stress_unitE"].values())
        k = max(1.0, c["worst"]["vm_outside_supports_Pa"] / s_vox)
        st.verification.append({"material": st.choice["material"], "design": st.choice["design"],
                                "voxel_stress_Pa": s_vox, "t10_stress_Pa": c["worst"]["vm_outside_supports_Pa"],
                                "factor": k, "t10_utilisation": c["utilisation"], "passes": c["utilisation"] <= 1.0})
        _log(opt, f"verify {st.choice['material']} / {st.choice['design']}: T10/voxel stress {k:.3f}, "
                  f"T10 utilisation {c['utilisation']:.3f}")
        kd[d["label"]] = k
        # T10/voxel displacement ratio (5 Nov: only stress was corrected, so a T10 displacement above L/400 never
        # changed the choice and the layout stayed "passes")
        mat = matdata.get(st.choice["material"])
        u_vox = d["disp_unitE"] / mat.E_at(st.T)
        ku[d["label"]] = max(1.0, c["worst"]["max_disp_m"] / u_vox) if u_vox > 0 else 1.0
        st.verification[-1]["disp_factor"] = ku[d["label"]]
        before = (st.choice["material"], st.choice["design"])
        rank_materials(st, opt, cands, kd, ku)
        decide(st, opt)
        if c["utilisation"] <= 1.0 and (st.choice["material"], st.choice["design"]) == before:
            break                      # passed, and the measured factor did not change the choice
        st.tet["chosen"] = None
        if st.choice and st.choice["design"] != "initial":
            _chosen_t10(st, opt, tetfem)
    c = (st.tet or {}).get("chosen")
    if st.choice and st.choice["design"] != "initial" and c is not None and c["utilisation"] > 1.0:
        st.choice["passes"] = False            # the T10 check of the final choice failed: never report it as passing
        _log(opt, f"T10 check of the final choice FAILS (governing ratio {c['utilisation']:.3f})")
    st.stress_factors = kd
    st.disp_factors = ku


def decide(st: Study, opt: Options) -> None:
    """Choice (lightest passing AM material and layout, else the least-utilised AM option flagged as failing) and
    the eco audits (baseline machined steel vs every candidate at its best — or chosen — layout)."""
    base = matdata.get(opt.baseline)
    ok = [x for x in st.materials if x["best"] is not None and x["am"]]
    ok.sort(key=lambda x: x["best"]["mass_kg"])
    st.choice = {"material": ok[0]["key"], "design": ok[0]["best"]["design"], "mass_kg": ok[0]["best"]["mass_kg"],
                 "utilisation": ok[0]["best"]["utilisation"], "passes": True} if ok else {}
    if not ok:      # nothing passes: report the least-utilised AM option, flagged, so every document still exists
        rows = [(x, r_) for x in st.materials if x["am"] and x["temp_ok"] for r_ in x["designs"]
                if np.isfinite(r_["utilisation"])]
        if rows:
            x, r_ = min(rows, key=lambda q: (q[1]["utilisation"], q[1]["mass_kg"]))
            st.choice = {"material": x["key"], "design": r_["design"], "mass_kg": r_["mass_kg"],
                         "utilisation": r_["utilisation"], "passes": False}
            _log(opt, f"NO material passes; least-utilised AM option {x['key']} / {r_['design']} "
                      f"(U = {r_['utilisation']:.2f}) is reported and flagged FAILS")
    base_mass = st.baseline["mass_kg"]
    a_base = ecoaudit.audit(base_mass, base, ecoaudit.EcoInputs(route="machined"), "baseline (initial, machined)")
    st.eco = {"baseline": a_base.to_json(), "candidates": {}}
    for x in st.materials:
        best = x["best"]
        if best is None and st.choice and x["key"] == st.choice["material"]:
            best = next(r_ for r_ in x["designs"] if r_["design"] == st.choice["design"])
        if best is None:
            continue
        m = matdata.get(x["key"])
        a = ecoaudit.audit(best["mass_kg"], m, ecoaudit.EcoInputs(route="am" if m.am else "machined"),
                           f"{m.name} · {best['design']}")
        st.eco["candidates"][x["key"]] = {"audit": a.to_json(), "vs_baseline": ecoaudit.compare(a_base, a),
                                          "passes": bool(best.get("passes", False))}


def _chosen_t10(st: Study, opt: Options, tetfem: Any) -> None:
    """T10 analysis of the chosen optimised layout (smoothed STL) with the chosen material; result in
    ``st.tet["chosen"]``, errors in ``st.tet["errors"]``."""
    out = st.tet
    T = st.T
    if not (st.choice and st.choice["design"] != "initial"):
        return
    d = next(x for x in st.designs if x["label"] == st.choice["design"])
    tag = round(100 * d["volfrac"])
    stl = st.out / "cad" / f"optimised_{tag}.stl"
    try:
        from aerokit.bracket import cadout as co
        (st.out / "cad").mkdir(exist_ok=True)
        info = co.density_to_stl(st.mesh.origin, st.mesh.h, st.fields[f"xphys_{tag}"] * st.fields[f"solid_{tag}"],
                                 stl, target_volume_mm3=float(st.fields[f"solid_{tag}"].sum()) * st.mesh.h ** 3 * 1e9)
        out.setdefault("stl", {})[d["label"]] = info
        mat = matdata.get(st.choice["material"])
        m = tetfem.mesh_stl(stl, min(opt.tet_sizes_vox) * st.mesh.h * 1e3)
        r = tetfem.static_t10(m, st.setup, mat.E_at(T), bore_tol_m=0.6 * st.mesh.h)
        r["worst"] = tetfem.worst(r)
        s_lim = r["worst"]["vm_outside_supports_Pa"]     # lug eyes included; only the clamp zones excluded
        r["strength_utilisation"] = strength_util(st.setup, opt, s_lim, mat.Fty_at(T), mat.Ftu_at(T))
        lim_mm = st.setup.get("design_criteria", {}).get("max_displacement_mm")
        r["disp_ratio"] = r["worst"]["max_disp_m"] * 1e3 / float(lim_mm) if lim_mm else 0.0
        r["utilisation"] = max(r["strength_utilisation"], r["disp_ratio"])     # governing ratio (strength or L/400)
        r["voxel_utilisation"] = st.choice.get("utilisation")
        out["chosen"] = r
        _log(opt, f"T10 chosen layout: {r['elements']} el, disp {r['worst']['max_disp_m'] * 1e3:.4f} mm, "
                  f"vm_out {s_lim / 1e6:.1f} MPa, utilisation {r['utilisation']:.3f}")
    except Exception as exc:                       # noqa: BLE001
        out["errors"].append(f"chosen layout: {exc}")


def conforming_check(st: Study, g: Geometry, opt: Options) -> dict[str, Any]:
    """T10 (Ansys-SOLID187-like) analysis of the initial design (exact CAD, several sizes) and of the chosen
    optimised layout (its smoothed STL) with the chosen material at T. Stored in ``st.tet``; never raises."""
    from aerokit.bracket import cadout, tetfem
    out: dict[str, Any] = {"initial": [], "chosen": None, "errors": []}
    if not cadout.gmsh_available():
        out["errors"].append("gmsh not available")
        st.tet = out
        return out
    T = st.T
    base = matdata.get(opt.baseline)
    step = None
    if g.drawing is not None:
        step = st.out / "cad" / "initial.step"
        if not step.exists():
            (st.out / "cad").mkdir(exist_ok=True)
            cadout.drawing_to_cad(g.drawing, step)
    elif Path(g.source).suffix.lower() in (".step", ".stp", ".iges", ".igs"):
        step = Path(g.source)
    stl = None
    if step is None and Path(g.source).suffix.lower() == ".stl" and not g.frame:
        stl = Path(g.source)                     # e.g. an Ansys/Discovery result; units handled below
    if step is not None or stl is not None:
        for k in opt.tet_sizes_vox:
            try:
                if step is not None:
                    m = tetfem.mesh_cad(step, k * st.mesh.h * 1e3)
                    r = tetfem.static_t10(m, st.setup, base.E_at(T))
                else:
                    src: Path = Path(g.source)
                    if opt.unit != "mm" and g.V is not None and g.F is not None:   # gmsh reads STL numbers as is
                        from aerokit.optimization import extract
                        src = st.out / "cad" / "_input_mm.stl"
                        (st.out / "cad").mkdir(exist_ok=True)
                        extract.write_stl(src, np.asarray(g.V) * 1e3, np.asarray(g.F))
                    m = tetfem.mesh_stl(src, k * st.mesh.h * 1e3)
                    r = tetfem.static_t10(m, st.setup, base.E_at(T), bore_tol_m=0.5 * st.mesh.h)
                r["size_mm"] = k * st.mesh.h * 1e3
                r["worst"] = tetfem.worst(r)
                out["initial"].append(r)
                _log(opt, f"T10 initial, size {r['size_mm']:.2f} mm: {r['elements']} el, disp "
                          f"{r['worst']['max_disp_m'] * 1e3:.4f} mm, vm_out {r['worst']['vm_outside_Pa'] / 1e6:.1f} MPa")
            except Exception as exc:                   # noqa: BLE001
                out["errors"].append(f"initial {k} h: {exc}")
    st.tet = out
    _chosen_t10(st, opt, tetfem)
    return out


def _verified_stress(st: Study, x: dict[str, Any]) -> float:
    """Limit-load stress of a ranked material's best layout: the T10 value when that layout is the T10-verified
    chosen one (stress does not depend on E, so it holds for every material on that layout), else the voxel one."""
    return _layout_stress(st, x["best"])[0]


def _layout_stress(st: Study, row: dict[str, Any]) -> tuple[float, str]:
    """(limit-load stress [Pa], basis "T10" | "voxel") of one material × layout row."""
    t10 = (getattr(st, "tet", {}) or {}).get("chosen")
    if t10 and st.choice and row["design"] == st.choice["design"]:
        return float(t10["worst"]["vm_outside_Pa"]), "T10"
    return float(row["vm_limit_Pa"]), "voxel"


def verified_materials(st: Study, opt: Options) -> list[dict[str, Any]]:
    """Copy of ``st.materials`` for output: every row on the T10-verified layout carries the T10 stress and the
    utilisation that follows from it (``voxel_vm_limit_Pa`` / ``voxel_utilisation`` keep the ranking values);
    ``stress_basis`` says which. The ranking itself (``st.materials``) is not changed."""
    import copy
    out = copy.deepcopy(st.materials)
    for x in out:
        m = matdata.get(x["key"])
        for row in x["designs"] + ([x["best"]] if x["best"] is not None else []):
            if "stress_basis" in row:                 # best may be the same object as a designs row (kept by deepcopy)
                continue
            s, basis = _layout_stress(st, row)
            row["voxel_vm_limit_Pa"], row["voxel_utilisation"] = row["vm_limit_Pa"], row["utilisation"]
            row["vm_limit_Pa"], row["stress_basis"] = s, basis
            row["utilisation"] = strength_util(st.setup, opt, s, m.Fty_at(st.T), m.Ftu_at(st.T))
    return out


def film_result(st: Study, opt: Options) -> dict[str, Any]:
    """``result.json`` in the format the film reads (``ranking[]`` with material, route, mass, CO₂ …)."""
    ranking = []
    loads = [np.linalg.norm(c["applied_N"]) for c in st.baseline["at_T"]["cases"]]
    mats = sorted(st.materials, key=lambda x: (x["best"] is None, not x["am"], x["best"]["mass_kg"] if x["best"] else 1e9))
    if st.choice and not st.choice.get("passes", True):     # failing fallback goes first, flagged
        x = next(m for m in st.materials if m["key"] == st.choice["material"])
        x = dict(x, best=next(r_ for r_ in x["designs"] if r_["design"] == st.choice["design"]))
        mats = [x] + [m for m in mats if m["key"] != x["key"]]
    for x in mats:
        if x["best"] is None:
            continue
        eco = st.eco["candidates"].get(x["key"], {}).get("audit", {})
        ph = eco.get("phases", {})
        d = next(d for d in st.designs if d["label"] == x["best"]["design"])
        sv, m = _verified_stress(st, x), matdata.get(x["key"])     # σ and U from the same (verified) stress
        ranking.append({"material": x["name"], "route": x["route"], "mass_kg": x["best"]["mass_kg"],
                        "co2_production_kg": ph.get("material", {}).get("co2_kg", 0) +
                        ph.get("manufacture", {}).get("co2_kg", 0),
                        "co2_use_kg": ph.get("use", {}).get("co2_kg", 0),
                        "volume": d["volume_m3"] / (st.mesh.volume * st.vol_corr),
                        "sigma_ult_Pa": opt.limit_to_ultimate * sv,
                        "utilisation": strength_util(st.setup, opt, sv, m.Fty_at(st.T), m.Ftu_at(st.T)),
                        "voxel_utilisation": x["best"]["utilisation"], "stress_basis": _layout_stress(st, x["best"])[1],
                        "ultimate_N": opt.limit_to_ultimate * max(loads),
                        "design": x["best"]["design"], "temperature_C": st.T,
                        "passes": bool(x["best"].get("passes", True))})
    return {"case": st.name, "temperature_C": st.T, "ranking": ranking,
            "baseline": {"material": st.baseline["material"], "mass_kg": st.baseline["mass_kg"]},
            "element_size_m": st.mesh.h, "_about": "aerokit.bracket.pipeline result (film reads ranking[])"}


def dump(obj: Any) -> Any:
    """JSON-safe copy (numpy → lists, NaN/inf → None)."""
    if isinstance(obj, dict):
        return {str(k): dump(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [dump(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return dump(obj.tolist())
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        return None if not math.isfinite(f) else f
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def save_json(path: Path, obj: Any) -> Path:
    path.write_text(json.dumps(dump(obj), indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def options_dict(opt: Options) -> dict[str, Any]:
    return asdict(opt)
