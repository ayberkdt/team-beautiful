"""Write every deliverable of a :class:`aerokit.bracket.pipeline.Study` into one folder.

``<out>/``
    ``report.md``                     the run report (numbers with their files and tags)
    ``result.json``                   everything numeric (film reads ``ranking[]``)
    ``setup.json``                    editable holes / supports / load cases (re-run picks it up)
    ``cad/initial.step|stl``          exact B-rep of a drawing input (gmsh) or the input file's surface
    ``cad/optimised_<v>.stl``         smooth surfaces of the optimised layouts
    ``density_<case>.json``           density fields in the film format (``runs[i].density`` [x][y][z])
    ``loads_film.json``               supports and forces in the film's ``yukler.json`` format
    ``materials/``                    ``materials_engineering_data.xml`` (MatML) + one Markdown card per material
    ``eco_audit.json|md``             baseline vs redesign by phase
    ``crosscheck_template.csv``       fill the Ansys column, then ``python scripts/bracket_crosscheck.py``
    ``figures/``                      datawiz-audited figures (``*.denetim.txt`` beside each)
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import numpy as np

from aerokit.bracket import cards, crosscheck, matdata
from aerokit.bracket.pipeline import Geometry, Options, Study, film_result, save_json, verified_materials

__all__ = ["write_all", "ours_metrics"]


def ours_metrics(st: Study, design_label: str | None = None, material: str | None = None) -> dict[str, float | None]:
    """Our numbers in the cross-check vocabulary (worst load case) for a design and material."""
    mkey = material or st.baseline["material"]
    m = matdata.get(mkey)
    T = st.T
    if design_label in (None, "initial"):
        ev = st.baseline["at_T"]
        scale = st.baseline["at_T"]["E_Pa"] / m.E_at(T)
        cases = ev["cases"]
        vol = st.baseline["volume_m3"]
        tet = (getattr(st, "tet", {}) or {}).get("initial") or []
        if tet:                     # conforming T10 (Ansys SOLID187 analogue) and exact CAD volume take precedence
            t = tet[-1]
            cases = t["cases"]
            vol = t["volume_m3"]
            scale = matdata.get(st.baseline["material"]).E_at(T) / m.E_at(T)
        return {"mass_kg": vol * m.rho.value, "volume_mm3": vol * 1e9,
                "max_deformation_mm": max(c["max_disp_m"] for c in cases) * scale * 1e3,
                "load_point_deformation_mm": max(c.get("load_disp_m", float("nan")) for c in cases) * scale * 1e3,
                "compliance_J": max(c["compliance_J"] for c in cases) * scale,
                "strain_energy_J": max(c["compliance_J"] for c in cases) * scale / 2,
                "max_von_mises_MPa": max(c["vm_max_Pa"] for c in cases) / 1e6,
                "von_mises_outside_MPa": max(c["vm_outside_Pa"] for c in cases) / 1e6,
                "min_safety_factor": m.Fty_at(T) / max(c["vm_outside_Pa"] for c in cases),
                "retained_volume_fraction": 1.0,
                "reaction_force_N": max(float(np.linalg.norm(c["applied_N"])) for c in st.baseline["at_T"]["cases"])}
    d = next(x for x in st.designs if x["label"] == design_label)
    s = max(d["stress_unitE"].values())
    return {"mass_kg": d["volume_m3"] * m.rho.value, "volume_mm3": d["volume_m3"] * 1e9,
            "max_deformation_mm": d["disp_unitE"] / m.E_at(T) * 1e3,
            "compliance_J": d["compliance_unitE"] / m.E_at(T), "strain_energy_J": d["compliance_unitE"] / m.E_at(T) / 2,
            "max_von_mises_MPa": d["vm_max_unitE"] / 1e6, "von_mises_outside_MPa": s / 1e6,
            "min_safety_factor": m.Fty_at(T) / s, "retained_volume_fraction": d["volume_fraction_kept"],
            "reaction_force_N": None}


def _film_loads(st: Study) -> dict[str, Any]:
    """Supports and forces in the film's yukler.json format (mm)."""
    holes = {h["id"]: h for h in st.setup["holes"]}
    sup = []
    for s in st.setup.get("supports", []):
        h = holes[s["hole"]]
        ax = "xyz".index(h["axis"])
        e = [0, 0, 0]
        e[ax] = 1
        c = list(h["center_mm"])
        c[ax] = 0.0
        lo = min(a for a, _ in h["segments_mm"])
        hi = max(b for _, b in h["segments_mm"])
        sup.append({"ad": f"{s['hole']} fixed ({s.get('type', 'fixed_bore')})", "tur": "silindir", "merkez": c,
                    "eksen": e, "yaricap": h["diameter_mm"] / 2, "bas": lo, "son": hi})
    forces = []
    for c in st.setup["load_cases"]:
        for ld in c["loads"]:
            h = holes[ld["hole"]]
            if "force_N" in ld:
                f = np.asarray(ld["force_N"], float)
                n = float(np.linalg.norm(f))
                forces.append({"ad": c["name"], "durum": c["name"].split()[0], "nokta": h["center_mm"],
                               "yon": (f / n).tolist() if n else [0, 0, 0], "buyukluk_N": n})
            else:
                M = np.asarray(ld["moment_Nm"], float)
                forces.append({"ad": c["name"], "durum": c["name"].split()[0], "nokta": h["center_mm"],
                               "yon": (M / np.linalg.norm(M)).tolist(), "buyukluk_N": 0.0,
                               "moment_Nm": float(np.linalg.norm(M)), "_not": "moment vector (axis), not a force"})
    lo, hi = st.vm.bbox()
    return {"_not": f"aerokit.bracket set-up of '{st.name}' in the film's yukler.json format (mm, N). Supports are "
                    "the fixed hole bores; LC moments are listed with the moment axis as 'yon'.",
            "birim": "mm", "tasarim_alani": [{"min": (lo * 1e3).tolist(), "max": (hi * 1e3).tolist()}],
            "destekler": sup, "kuvvetler": forces}


def _density_file(st: Study) -> dict[str, Any]:
    """Film density file. Every run: final density; the CHOSEN run also ``snapshots`` (iteration, density every
    ``snapshot_every`` iterations, same grid, 3 decimals) — runs are warm-started from the previous volume
    fraction (``warm_start_from``), so the chosen run's first snapshot already looks like that layout."""
    from aerokit.bracket.topo3d import to_grid
    runs = []
    chosen = st.choice.get("design") if st.choice else None
    prev = "uniform start"
    for d in st.designs[1:]:
        tag = round(100 * d["volfrac"])
        key = f"xphys_{tag}"
        if key not in st.fields:
            continue
        g = st.fields[key]
        run = {"volume": float(d["volume_m3"] / (st.mesh.volume * st.vol_corr)), "volfrac_target": d["volfrac"],
               "iterations": d["iterations"], "label": d["label"], "warm_start_from": prev,
               "density": np.round(g, 4).tolist()}
        snaps = st.fields.get(f"snap_{tag}") or []
        if d["label"] == chosen and snaps:
            run["snapshots"] = [{"iteration": int(it), "density": np.round(to_grid(st.mesh, v.astype(float)), 3).tolist()}
                                for it, v in snaps]
        runs.append(run)
        prev = d["label"]
    return {"meta": {"voxel_mm": st.mesh.h * 1e3, "origin_mm": (st.mesh.origin * 1e3).tolist(),
                     "grid": list(st.vm.shape), "order": "[x][y][z], z up, origin = corner of voxel (0,0,0)",
                     "outside_part": 0.0, "case": st.name,
                     "snapshots": "chosen run only: runs[i].snapshots = [{iteration, density}] (raw physical density, "
                                  "before the connectivity clean-up of the final layout)"},
            "runs": runs}


def write_all(st: Study, g: Geometry, opt: Options, figures: bool = True) -> dict[str, Any]:
    out = st.out
    (out / "cad").mkdir(exist_ok=True)
    (out / "materials").mkdir(exist_ok=True)
    files: dict[str, Any] = {}
    T = st.T
    # ---------------- CAD
    from aerokit.bracket import cadout
    cad: dict[str, Any] = {}
    if g.drawing is not None and cadout.gmsh_available():
        try:
            cad["initial"] = cadout.drawing_to_cad(g.drawing, out / "cad" / "initial.step", out / "cad" / "initial.stl")
        except Exception as e:                       # noqa: BLE001 - CAD is optional; the voxel surface follows
            cad["initial_error"] = str(e)
    elif g.drawing is None:
        dst = out / "cad" / ("initial" + Path(g.source).suffix.lower())
        shutil.copyfile(g.source, dst)
        cad["initial"] = {"copied": str(dst)}
    cad["initial_voxel_surface"] = cadout.voxel_surface_stl(st.vm, out / "cad" / "initial_voxels.stl")
    for d in st.designs[1:]:
        key = f"solid_{round(100 * d['volfrac'])}"
        if key in st.fields:
            cad[d["label"]] = cadout.density_to_stl(st.mesh.origin, st.mesh.h,
                                                     st.fields[f"xphys_{round(100 * d['volfrac'])}"] *
                                                     st.fields[key], out / "cad" / f"optimised_{round(100 * d['volfrac'])}.stl",
                                                     target_volume_mm3=float(st.fields[key].sum()) * st.mesh.h ** 3 * 1e9)
    files["cad"] = cad
    # ---------------- materials
    mats = [matdata.get(k) for k in (opt.candidates or matdata.names())]
    cards.write_matml(out / "materials" / "materials_engineering_data.xml", mats, T)
    for m in mats:
        (out / "materials" / f"card_{m.key}.md").write_text(cards.markdown_card(m, T), encoding="utf-8")
    # ---------------- result + film files
    res = film_result(st, opt)
    full = {"result": res, "options": opt.__dict__, "setup": st.setup, "baseline": st.baseline,
            "convergence": st.convergence, "designs": st.designs, "materials": verified_materials(st, opt), "choice": st.choice,
            "eco": st.eco, "timings": st.timings, "cad": cad, "tet": getattr(st, "tet", {}),
            "verification": getattr(st, "verification", []), "stress_factors": getattr(st, "stress_factors", {}),
            "voxel": {"h_m": st.mesh.h, "shape": list(st.vm.shape), "origin_m": st.mesh.origin.tolist(),
                      "elements": st.mesh.ne, "keep_elements": int(st.keep.sum())}}
    bolts = bolt_check(st, opt)
    full["bolt_check"] = bolts
    save_json(out / "result.json", {**res, "details": full})
    save_json(out / f"density_{st.out.name}.json", _density_file(st))
    save_json(out / "loads_film.json", _film_loads(st))
    # ---------------- cross-check template (initial design in the baseline material, and the chosen design)
    src = ("T10 conforming mesh" if (getattr(st, "tet", {}) or {}).get("initial") else "voxel H8IM")
    crosscheck.write_template(out / "crosscheck_template.csv", ours_metrics(st),
                              f"[initial design, baseline material, ours = {src}]")
    if st.choice:
        crosscheck.write_template(out / "crosscheck_template_redesign.csv",
                                  ours_metrics(st, st.choice["design"], st.choice["material"]),
                                  f"{st.choice['design']}, {st.choice['material']}")
    # ---------------- eco audit
    save_json(out / "eco_audit.json", st.eco)
    (out / "eco_audit.md").write_text(_eco_md(st), encoding="utf-8")
    # ---------------- figures
    figs: dict[str, Any] = {}
    if figures:
        from aerokit.bracket import figures as fg
        figs = fg.make_all(st, out / "figures")
    files["figures"] = figs
    files["bolt_check"] = bolts
    (out / "report.md").write_text(_report_md(st, g, opt, files), encoding="utf-8")
    return files


def bolt_check(st: Study, opt: Options) -> dict[str, Any]:
    """FEA reaction per support bolt (initial design, baseline material at T) next to the classical rigid-plate
    bolt-group split (:mod:`aerokit.bracket.handcheck`); ``rows`` empty when the supports do not share one axis."""
    from aerokit.bracket import handcheck
    try:
        fea = handcheck.bolt_reactions(st.mesh, st.setup, matdata.get(opt.baseline).E_at(st.T), element=opt.element)
        cl = handcheck.classical_bolt_loads(st.setup, fea["_applied"], fea["_mesh_X"])
    except Exception as exc:                          # noqa: BLE001 - a hand check must never stop the report
        return {"rows": [], "error": str(exc)}
    return {"rows": handcheck.compare_bolts(fea, cl), "axis": cl["axis"] if cl else None,
            "reaction_N": fea["reaction_N"], "clamp_moment_Nm": fea["clamp_moment_Nm"]}


def _bolt_md(bc: dict[str, Any]) -> str:
    rows = bc.get("rows") or []
    if not rows:
        why = bc.get("error") or "the support bolts do not share one axis (or there is only one)"
        return f"### Bolt loads: FEA vs classical bolt group\n\nNot computed: {why}.\n\n"
    s = ("### Bolt loads: FEA vs classical bolt group (initial design)\n\n"
         f"Bolt axis {bc['axis']}. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, "
         "elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints."
         "bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid "
         "clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel "
         "between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries "
         "less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — "
         "size the bolts with the larger value.\n\n"
         "| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | "
         "Clamp moment FEA (N m) |\n|---|---|---|---|---|---|---|\n")
    for r in rows:
        s += (f"| {r['case']} | {r['hole']} | {r['fea_shear_N']:.0f} | {r['classical_shear_N']:.0f} | "
              f"{r['fea_axial_N']:.0f} | {r['classical_axial_N']:.0f} | {r['fea_clamp_moment_Nm']:.2f} |\n")
    return s + "\n"


def fatigue_screen(st: Study) -> str:
    """Temperature-aware life screening (:mod:`aerokit.bracket.lifecheck`) of every material at its best layout
    (or the chosen one), with the stress basis of the hand-off (T10 on the verified layout, else voxel)."""
    from aerokit.bracket import lifecheck
    from aerokit.bracket.pipeline import _layout_stress
    rows = []
    for x in st.materials:
        r_ = x["best"] or next((d for d in x["designs"] if st.choice and d["design"] == st.choice["design"]
                                and x["key"] == st.choice["material"]), None)
        if r_ is None:
            continue
        sig, basis = _layout_stress(st, r_)
        row = lifecheck.screen(x["key"], sig, st.T)
        row["design"] = f"{r_['design']} ({basis})"
        rows.append(row)
    return lifecheck.markdown(rows, st.T)


def mechanical_steps(st: Study, opt: Options) -> str:
    """How to reproduce exactly our set-up in Ansys Mechanical (names of Mechanical objects; not run here)."""
    holes = {h["id"]: h for h in st.setup["holes"]}
    T = st.T
    s = ("## 6. Reproduce this set-up in Ansys Mechanical (checklist)\n\n"
         "Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.\n\n"
         "1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign "
         f"*{matdata.get(st.baseline['material']).name} @ {T:g} C (aerokit)* to the initial body (E is a table over "
         f"temperature: set the body/environment temperature to {T:g} °C, otherwise Mechanical uses 22 °C).\n")
    s += "2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):\n"
    for sp in st.setup.get("supports", []):
        h = holes[sp["hole"]]
        s += (f"   - {sp['hole']}: Ø {h['diameter_mm']:.2f} mm, axis {h['axis']}, centre "
              f"({', '.join(f'{v:.1f}' for v in h['center_mm'])}) mm → "
              + ("Fixed Support on the bore face" if sp.get("type", "fixed_bore") == "fixed_bore"
                 else "Fixed Support on the seat face annulus") + "\n")
    s += "3. **Loads** (one load step or one analysis per case; units N, N·m):\n"
    for c in st.setup["load_cases"]:
        for ld in c["loads"]:
            h = holes[ld["hole"]]
            if "force_N" in ld:
                kind = {"bearing": "Bearing Load (components)", "force": "Force (components) on the face"}.get(
                    ld.get("type", "bearing"), "Force")
                f = ld["force_N"]
                s += (f"   - {c['name']}: {kind} on bore {ld['hole']} (Ø {h['diameter_mm']:.2f}): "
                      f"X {f[0]:.1f}, Y {f[1]:.1f}, Z {f[2]:.1f} N\n")
            else:
                M = ld["moment_Nm"]
                s += (f"   - {c['name']}: Moment, scoped to bore {ld['hole']}, behaviour Deformable: "
                      f"X {M[0]:.2f}, Y {M[1]:.2f}, Z {M[2]:.2f} N·m\n")
    sizes = [f"{r['size_mm']:.1f}" for r in ((getattr(st, 'tet', {}) or {}).get("initial") or [])]
    s += (f"4. **Mesh**: quadratic tets (default SOLID187); element size {', '.join(sizes) or '3 × voxel'} mm to "
          "match our T10 runs; refine once more for a convergence pair.\n")
    s += (f"5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), "
          f"Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius "
          f"+ {st.setup.get('exclusion_mm', 0):.1f} mm.\n")
    if st.choice and st.choice["design"] != "initial":
        d = next(x for x in st.designs if x["label"] == st.choice["design"])
        s += (f"6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all "
              f"load steps); Response Constraint Mass/Volume = {100 * d['volfrac']:.0f} % ; Exclusion Regions: the "
              f"faces of every support and load bore with a ring of {st.setup['non_design']['ring_factor']:g} × bore "
              f"radius (≥ {st.setup['non_design']['ring_min_voxels']} × {st.mesh.h * 1e3:.1f} mm); "
              + ("Manufacturing constraint AM Overhang, 45°, build direction "
                 f"{st.setup.get('build_direction', '+z')}; " if opt.am_filter else "")
              + "then Validation with the chosen material.\n")
    return s + "\n"


def _f(v: float | None, n: int = 3) -> str:
    return "—" if v is None else f"{v:.{n}g}"


def _eco_md(st: Study) -> str:
    b = st.eco["baseline"]
    s = "# Eco audit — baseline vs redesign candidates\n\n"
    s += ("Structure of the Granta EduPack Eco Audit (material, manufacture, transport, use, end of life). Factors, "
          "sources and tags: `aerokit.bracket.ecoaudit.EcoInputs` (each value tagged D / D-ag / S / Y). "
          "EoL potential is shown separately, as EduPack does.\n\n")
    s += f"Baseline: **{b['material']}**, {b['mass_kg']:.3f} kg, route machined (buy-to-fly {b['inputs']['buy_to_fly_used']:g}).\n\n"
    s += "| Phase | Baseline CO₂ (kg) | Baseline energy (MJ) |\n|---|---|---|\n"
    for k, v in b["phases"].items():
        s += f"| {k} | {v['co2_kg']:.4g} | {v['energy_MJ']:.4g} |\n"
    s += f"| **total** | **{b['total']['co2_kg']:.4g}** | **{b['total']['energy_MJ']:.4g}** |\n"
    if b["eol_potential"]["co2_kg"] == 0 and b["eol_potential"]["energy_MJ"] == 0:
        s += "| EoL potential | n/a (no recycled-route value for this material in our data) | |\n\n"
    else:
        s += f"| EoL potential | {b['eol_potential']['co2_kg']:.4g} | {b['eol_potential']['energy_MJ']:.4g} |\n\n"
    s += "## Candidates (lightest passing design of each material, AM route where printable)\n\n"
    s += "### Production (cradle to gate, kg CO₂e)\n\n| Material | Mass (kg) | Material | Manufacture | Transport | Production total |\n|---|---|---|---|---|---|\n"
    for c in st.eco["candidates"].values():
        a = c["audit"]
        ph = a["phases"]
        prod = ph["material"]["co2_kg"] + ph["manufacture"]["co2_kg"] + ph["transport"]["co2_kg"]
        s += (f"| {a['material']} | {a['mass_kg']:.3f} | {ph['material']['co2_kg']:.4g} | "
              f"{ph['manufacture']['co2_kg']:.4g} | {ph['transport']['co2_kg']:.3g} | {prod:.4g} |\n")
    s += "\n### Whole life (kg CO₂e)\n\n| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |\n|---|---|---|---|---|---|\n"
    for c in st.eco["candidates"].values():
        a, v = c["audit"], c["vs_baseline"]
        s += (f"| {a['material']} | {a['phases']['use']['co2_kg']:.4g} | {a['total']['co2_kg']:.4g} | "
              f"{v['delta_total_co2_kg']:+.4g} | {_f(v['break_even_km'])} | {a['use_marginal_co2_kg']:.4g} |\n")
    s += ("\nUse phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ "
          "(long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. "
          "Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × "
          "25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.\n")
    return s


def _report_md(st: Study, g: Geometry, opt: Options, files: dict[str, Any]) -> str:
    T = st.T
    b = st.baseline
    w = b["worst_T"]
    s = f"# Bracket redesign run — {st.name}\n\n"
    s += (f"Input: `{g.source}` ({g.kind}) · voxel {st.mesh.h * 1e3:.2f} mm · {st.mesh.ne} elements · "
          f"{st.mesh.ndof} DOFs · working temperature **{T:g} °C** · element {opt.element} · total "
          f"{st.timings.get('total_s', 0):.0f} s.\n\n")
    s += ("All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and "
          "supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength "
          f"criterion: von Mises outside the hole zones (radius + {opt.exclusion_vox:g} voxels) "
          f"≤ Fty(T) at limit load and ≤ Ftu(T) at {opt.limit_to_ultimate:g} × limit [Y].\n\n")
    s += "## 1. Set-up\n\n| Hole | Axis | Ø (mm) | Centre (mm) | Role |\n|---|---|---|---|---|\n"
    for h in st.setup["holes"]:
        s += f"| {h['id']} | {h['axis']} | {h['diameter_mm']:.2f} | {', '.join(f'{v:.1f}' for v in h['center_mm'])} | {h['role']} |\n"
    s += "\n| Load case | Loads |\n|---|---|\n"
    for c in st.setup["load_cases"]:
        s += f"| {c['name']} | " + "; ".join(
            f"{ld['hole']} {ld.get('type')} " + (f"F = {[round(v, 1) for v in ld['force_N']]} N" if "force_N" in ld
                                                  else f"M = {[round(v, 1) for v in ld['moment_Nm']]} N m")
            for ld in c["loads"]) + " |\n"
    s += f"\nNon-design rings: {int(st.keep.sum())} of {st.mesh.ne} elements kept solid.\n\n"
    s += f"## 2. Initial design, {b['material']} at {T:g} °C\n\n"
    s += f"Mass **{b['mass_kg']:.4f} kg** (voxel volume {b['volume_m3'] * 1e9:.0f} mm³"
    ini = files.get("cad", {}).get("initial", {})
    if isinstance(ini, dict) and "volume_mm3" in ini:
        s += f"; exact CAD volume {ini['volume_mm3']:.0f} mm³, voxel/CAD = {b['volume_m3'] * 1e9 / ini['volume_mm3']:.4f}"
    s += ").\n\n| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |\n|---|---|---|---|---|---|\n"
    for c in b["at_T"]["cases"]:
        s += (f"| {c['name']} | {c['max_disp_m'] * 1e3:.4g} | {c['compliance_J']:.4g} | {c['vm_outside_Pa'] / 1e6:.4g} | "
              f"{c['vm_max_Pa'] / 1e6:.4g} | {np.linalg.norm(c['reaction_N']):.4g} |\n")
    from aerokit.bracket.geometry import member_thickness
    mt = member_thickness(st.vm.solid, st.mesh.h)
    s += (f"\nThinnest members (distance-transform ridge): minimum {mt['min_m'] * 1e3:.1f} mm = {mt['min_vox']:.1f} "
          f"voxels, 10th percentile {mt['p10_m'] * 1e3:.1f} mm = {mt['p10_vox']:.1f} voxels"
          + (". **Below ~5 voxels the voxel model is too soft in bending** (GE: +21 % deformation at 3.5 voxels, "
             "+1 % at 6.3): trust the T10 numbers or rerun with a smaller `--voxel`.\n"
             if mt["p10_vox"] < 5 else ".\n"))
    th = b.get("thermal")
    if th:
        s += (f"\n**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of {T:g} °C (reference 22 °C) "
              f"with the bores fixed, constrained expansion alone gives von Mises {th['vm_outside_Pa'] / 1e6:.4g} MPa "
              f"outside the hole zones (E α ΔT = {th['E_alpha_dT_Pa'] / 1e6:.4g} MPa, α = {th['alpha_per_K']:.3g} /K). "
              "Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the "
              "mentors (§11 Q1).\n")
    w20 = b["worst_20C"]
    s += (f"\nAt 20 °C the worst deformation is {w20['max_disp_m'] * 1e3:.4g} mm (vs {w['max_disp_m'] * 1e3:.4g} mm at "
          f"{T:g} °C: ratio {w['max_disp_m'] / w20['max_disp_m']:.3f} = E(20)/E(T)).\n\n")
    if st.convergence:
        s += "### Mesh convergence (initial design)\n\n| Voxel (mm) | Elements | Max deformation (mm) | Compliance (J) | vM outside (MPa) | Volume (mm³) |\n|---|---|---|---|---|---|\n"
        for c in st.convergence:
            s += (f"| {c['h_mm']:.2f} | {c['elements']} | {c['max_disp_m'] * 1e3:.4g} | {c['compliance_J']:.4g} | "
                  f"{c['vm_outside_Pa'] / 1e6:.4g} | {c['volume_m3'] * 1e9:.0f} |\n")
        s += "\n"
    tet = getattr(st, "tet", {}) or {}
    if tet.get("initial") or tet.get("chosen") or tet.get("errors"):
        s += ("### Conforming check: 10-node tetrahedra on the exact geometry (Ansys SOLID187 analogue)\n\n"
              "gmsh/OCC mesh of the CAD, same set-up, consistent bore loads, PARDISO. Compare THESE numbers with an "
              "Ansys run; the voxel-vs-T10 gap is a measured discretisation effect.\n\n")
        if tet.get("initial"):
            s += "| Mesh size (mm) | T10 elements | Volume (mm³) | Max deformation (mm) | vM outside (MPa) | vM max (MPa) | Time (s) |\n|---|---|---|---|---|---|---|\n"
            for r in tet["initial"]:
                w = r["worst"]
                s += (f"| {r['size_mm']:.2f} | {r['elements']} | {r['volume_m3'] * 1e9:.0f} | {w['max_disp_m'] * 1e3:.4g} | "
                      f"{w['vm_outside_Pa'] / 1e6:.4g} | {w['vm_max_Pa'] / 1e6:.4g} | {r['total_s']:.0f} |\n")
            wv = b["worst_T"]
            wt = tet["initial"][-1]["worst"]
            s += (f"\nVoxel / T10 (finest): deformation {wv['max_disp_m'] / wt['max_disp_m']:.3f}, vM outside "
                  f"{wv['vm_outside_Pa'] / wt['vm_outside_Pa']:.3f}. A vM outside that grows with refinement marks a "
                  "sharp re-entrant edge (singular): Ansys will show the same growth; judge such peaks with a fillet "
                  "or at a probe away from the edge.\n\n")
        if tet.get("chosen"):
            c = tet["chosen"]
            w = c["worst"]
            s += (f"Chosen layout ({st.choice['design']}, {st.choice['material']}) re-meshed from its smoothed STL: "
                  f"{c['elements']} T10, deformation {w['max_disp_m'] * 1e3:.4g} mm, vM outside {w['vm_outside_Pa'] / 1e6:.4g} "
                  f"MPa at limit load, utilisation **{c['utilisation']:.3f}** (voxel {c['voxel_utilisation']:.3f}).\n\n")
        ver = getattr(st, "verification", []) or []
        if ver:
            s += ("**Verified selection** (each chosen layout re-meshed with T10; when its T10 stress exceeds the voxel "
                  "stress the ratio becomes that layout's stress factor, all materials are re-ranked and the new "
                  "choice is checked again):\n\n| Round | Material | Layout | Voxel vM (MPa) | T10 vM (MPa) | Factor | "
                  "T10 utilisation |\n|---|---|---|---|---|---|---|\n")
            for i, v in enumerate(ver, 1):
                s += (f"| {i} | {v['material']} | {v['design']} | {v['voxel_stress_Pa'] / 1e6:.4g} | "
                      f"{v['t10_stress_Pa'] / 1e6:.4g} | {v['factor']:.3f} | {v['t10_utilisation']:.3f} |\n")
            s += "\n"
        for e in tet.get("errors", []):
            s += f"- T10 check note: {e}\n"
        s += "\n"
    s += "## 3. Topology optimisation (SIMP, density filter + projection, OC)\n\n| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |\n|---|---|---|---|---|---|---|\n"
    for d in st.designs[1:]:
        vm = max(d["stress_unitE"].values())
        s += (f"| {d['label']}{' (FAILED: ' + d['failed'] + ')' if d.get('failed') else ''} | {d['volfrac']:.2f} | "
              f"{d['volume_fraction_kept']:.3f} | {d['iterations']} | {d['gray_pct']:.1f} | {d['overhang_violations']} | "
              f"{vm / 1e6:.4g} |\n")
    s += ("\nStress is the same for every isotropic material (ν = 0.3); run times: "
          + ", ".join(f"{d['label']} {d['seconds']:.0f} s" for d in st.designs[1:]) + ".\n")
    s += f"\n## 4. Materials and eco audit at {T:g} °C (every material on every layout)\n\n"
    s += "| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |\n|---|---|---|---|---|---|---|\n"
    for x in st.materials:
        bst = x["best"]
        s += (f"| {x['name']} ({'AM' if x['am'] else 'machined'}) | {x['Tmax_C']:g} | {x['E_T_Pa'] / 1e9:.1f} | "
              f"{x['Fty_T_Pa'] / 1e6:.0f} | "
              f"{bst['design'] if bst else ('fails Tmax' if not x['temp_ok'] else 'none passes')} | "
              f"{_f(bst['mass_kg'] if bst else None, 4)} | {_f(bst['utilisation'] if bst else None)} |\n")
    if st.choice:
        flag = "" if st.choice.get("passes", True) else (
            f" — **FAILS the strength criterion (utilisation {st.choice['utilisation']:.2f}); no candidate passes "
            "on any layout: check loads, criterion and sharp edges (fillets) before using this**")
        s += (f"\n**Choice [K]:** {st.choice['material']} · {st.choice['design']} · {st.choice['mass_kg']:.4f} kg "
              f"(baseline {b['mass_kg']:.4f} kg, saving {100 * (1 - st.choice['mass_kg'] / b['mass_kg']):.1f} %)"
              f"{flag}.\n")
    s += "\nMaterial cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).\n\n"
    s += "Eco audit by phase (baseline vs every candidate): `eco_audit.md`.\n\n"
    s += fatigue_screen(st)
    s += _bolt_md(files.get("bolt_check") or {})
    s += ("## 5. Ansys cross-check\n\nFill the `ansys` column of `crosscheck_template.csv` (initial design, baseline "
          "material) and `crosscheck_template_redesign.csv`, then run `python scripts/bracket_crosscheck.py "
          f"{st.out}`.\n\n")
    s += mechanical_steps(st, opt)
    figs = files.get("figures", {})
    if figs:
        s += "## 7. Figures\n\n" + "".join(f"- `{Path(p).name}` — {cap}\n" for p, cap in figs.items())
    return s
