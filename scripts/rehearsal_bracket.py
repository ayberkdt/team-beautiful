"""Dry run of the first half of the Ansys slot on an invented task card (2-D plane-stress stand-in for Discovery).

    python scripts/rehearsal_bracket.py      # writes studies/rehearsal/rehearsal.json and .md
    python scripts/rehearsal_bracket.py --figure-only --lang en   # English F6 from the saved JSON (reports/figures_en/)

Card (invented for the rehearsal, not an official task): A320 cabin/system bracket, L-shaped design space
120 mm x 120 mm with a 48 mm arm, 10 mm thick, top edge bolted, 2.0 kN limit load downward at the arm tip,
tip deflection at limit load <= 0.5 mm, service 20-60 C, material and process free.

Steps: ultimate load (1.5 x 1.15) -> SIMP designs at 50/35/25/15 % retained volume (studies/retain_sweep) ->
binarise -> plane-stress analysis with element-centre von Mises -> per material: margin on yield at ultimate,
deflection at limit, mass -> lightest passing (material, retain) -> life-cycle CO2 with the A320 study factors.
The stress recovery is checked first against a uniform-tension plate (sigma = P / (h t)).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.optimization import topology as tp  # noqa: E402

CARD = {"limit_load_N": 2000.0, "factor_of_safety": 1.5, "fitting_factor": 1.15, "size_m": 0.120, "arm_ratio": 0.4,
        "thickness_m": 0.010, "deflection_limit_m": 0.5e-3, "n_elements": 60, "exclude_elements": 3}
SWEEP = ROOT / "studies" / "retain_sweep" / "retain_sweep.json"
EXTRA_VOLUMES = (0.30,)
STUDY = ROOT / "studies" / "tradeoff" / "bracket_a320_strength.json"
OUT = ROOT / "studies" / "rehearsal"
# (material key in the study file, route, display name)
CANDIDATES = [("Scalmalloy", "am_TO", "Scalmalloy TO + Eİ"), ("Ti-6Al-4V", "am_TO", "Ti-6Al-4V TO + Eİ"),
              ("7075-T6", "machined_TO", "7075 TO + talaşlı"), ("AlSi10Mg", "am_TO", "AlSi10Mg TO + Eİ")]


def centre_stress(grid: tp.Grid2D, U: np.ndarray, nu: float) -> np.ndarray:
    """Element-centre von Mises (plane stress) for unit elements, E = 1, unit thickness."""
    dNdx = np.array([-0.5, 0.5, 0.5, -0.5])
    dNdy = np.array([-0.5, -0.5, 0.5, 0.5])
    ue = U[grid.edof][:, :, 0]                     # (nel, 8): u1 v1 u2 v2 ...
    u, v = ue[:, 0::2], ue[:, 1::2]
    ex, ey = u @ dNdx, v @ dNdy
    gxy = u @ dNdy + v @ dNdx
    c = 1.0 / (1 - nu ** 2)
    sx, sy, txy = c * (ex + nu * ey), c * (ey + nu * ex), c * (1 - nu) / 2 * gxy
    return np.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2)


def tension_check(nu: float = 0.3) -> float:
    """Plate 20 x 10 elements, left edge on rollers (u = 0, one v fixed), unit total load on the right edge."""
    g = tp.Grid2D(20, 10, nu)
    fixed = [g.dof(0, iy, 0) for iy in range(11)] + [g.dof(0, 0, 1)]
    F = {g.dof(20, iy, 0): (0.5 if iy in (0, 10) else 1.0) / 10 for iy in range(11)}
    pr = tp.Problem(g, F, fixed)
    U = pr.analysis(np.ones(g.nel))[2]
    vm = centre_stress(g, U, nu)
    return float(np.median(vm)) / (1.0 / 10)        # expected sigma = P / (n_y h t) = 0.1 -> ratio 1


def analyse(density: np.ndarray, n: int, nu: float = 0.3) -> dict:
    pr = tp.l_bracket(n, P=1.0, ratio=CARD["arm_ratio"], nu=nu)
    b = tp.binarize(density, 0.5)
    x = pr.grid.vector(b["structure"].astype(float))
    x[pr.passive == 1] = 0.0
    U = pr.analysis(x)[2]
    vm = centre_stress(pr.grid, U, nu)
    vm[x < 0.5] = 0.0
    centres = pr.grid.element_center()
    arm = int(round(CARD["arm_ratio"] * n))
    k = CARD["exclude_elements"]
    near_load = (np.abs(centres[:, 0] - n) < k) & (np.abs(centres[:, 1] - arm) < k)
    near_bolts = centres[:, 1] > n - k
    ok = (x > 0.5) & ~near_load & ~near_bolts
    tip = abs(float(U[pr.grid.dof(n, arm, 1), 0]))
    return {"solid_elements": int((x > 0.5).sum()), "vm_unit_max": float(vm[ok].max()),
            "vm_unit_p99": float(np.percentile(vm[ok], 99)), "vm_unit_all_max": float(vm.max()), "tip_unit": tip}


def mesh_check(density: np.ndarray, n: int, factors: tuple[int, ...] = (1, 2, 4)) -> list[dict]:
    """Same black-and-white design re-analysed on meshes refined by ``factors`` (each element split k x k)."""
    base = tp.binarize(density, 0.5)["structure"].astype(float)
    out = []
    for k in factors:
        a = analyse(np.kron(base, np.ones((k, k))), n * k)
        # unit-load quantities scale with the element size: sigma ~ 1/(h t) with h = L/(n k); tip ~ 1/(E t)
        out.append({"refinement": k, "elements_per_side": n * k, "tip_unit": a["tip_unit"],
                    "vm_unit_max_scaled": a["vm_unit_max"] * k, "vm_unit_p99_scaled": a["vm_unit_p99"] * k})
    return out


def main() -> int:
    if "--figure-only" in sys.argv:
        en = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en"
        figure(json.loads((OUT / "rehearsal.json").read_text(encoding="utf-8"))["rows"], en=en)
        return 0
    ratio = tension_check()
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    n, t = CARD["n_elements"], CARD["thickness_m"]
    h = CARD["size_m"] / n
    p_ult = CARD["limit_load_N"] * CARD["factor_of_safety"] * CARD["fitting_factor"]
    life = study["lifecycle"]
    use_factor = (life["fuel_per_kg_per_flight"]["value"] * life["flights"]["value"]
                  * life["co2_per_kg_fuel"]["value"])
    grid_co2 = life["grid_co2_per_MJ"]["value"]
    runs = list(sweep["runs"])
    meta = sweep["meta"]
    for v in EXTRA_VOLUMES:      # finer point between the 35 % and 25 % sweep levels
        r = tp.topopt(tp.l_bracket(n), v, meta["rmin"], ft=meta["ft"], optimizer=meta["optimizer"], max_iter=400)
        runs.append({"volume": v, "density": np.asarray(r["xfiz"]).tolist()})
    runs.sort(key=lambda r: -r["volume"])
    stock_m3 = CARD["size_m"] ** 2 * t      # bounding plate of the L design space
    designs = []
    for run in runs:
        a = analyse(np.asarray(run["density"]), n)
        designs.append({"volume": run["volume"], **a,
                        "sigma_ult_MPa": a["vm_unit_max"] * p_ult / (h * t) / 1e6,
                        "sigma_ult_all_MPa": a["vm_unit_all_max"] * p_ult / (h * t) / 1e6})
    rows = []
    for mat, route, name in CANDIDATES:
        m = study["materials"][mat]
        r = study["routes"][route]
        for d in designs:
            mass = d["solid_elements"] * h * h * t * m["rho"]
            defl = d["tip_unit"] * CARD["limit_load_N"] / (m["E"] * t)
            ms = m["Fty"] / (d["sigma_ult_MPa"] * 1e6) - 1
            btf = stock_m3 * m["rho"] / mass if route.startswith("machined") else r["buy_to_fly"]["value"]
            bought = mass * btf
            prod = bought * m["co2_per_kg"]["value"] + bought * r["process_MJ_per_kg"]["value"] * grid_co2
            rows.append({"option": name, "volume": d["volume"], "mass_g": 1000 * mass, "buy_to_fly": btf,
                         "sigma_ult_MPa": d["sigma_ult_MPa"], "Fty_MPa": m["Fty"] / 1e6, "MS": ms,
                         "deflection_mm": 1000 * defl, "passes": ms >= 0 and defl <= CARD["deflection_limit_m"],
                         "co2_production_kg": prod, "co2_use_kg": mass * use_factor,
                         "co2_total_kg": prod + mass * use_factor})
    best = {}
    for row in rows:
        if row["passes"] and (row["option"] not in best or row["mass_g"] < best[row["option"]]["mass_g"]):
            best[row["option"]] = row
    ranking = sorted(best.values(), key=lambda r: r["co2_total_kg"])
    mesh = mesh_check(np.asarray(next(r for r in runs if r["volume"] == 0.35)["density"]), n)
    k_defl = mesh[-1]["tip_unit"] / mesh[0]["tip_unit"]      # coarse mesh under-predicts the tip deflection
    best_ref: dict[str, dict] = {}
    for row in rows:
        row["deflection_mm_refined"] = row["deflection_mm"] * k_defl
        row["passes_refined"] = row["MS"] >= 0 and row["deflection_mm_refined"] <= 1000 * CARD["deflection_limit_m"]
        if row["passes_refined"] and (row["option"] not in best_ref
                                      or row["mass_g"] < best_ref[row["option"]]["mass_g"]):
            best_ref[row["option"]] = row
    ranking_refined = sorted(best_ref.values(), key=lambda r: r["co2_total_kg"])
    OUT.mkdir(parents=True, exist_ok=True)
    out = {"card": CARD, "ultimate_load_N": p_ult, "element_size_m": h, "tension_check_ratio": ratio,
           "designs": designs, "rows": rows, "ranking": ranking, "mesh_check_35": mesh,
           "deflection_mesh_factor": k_defl, "ranking_refined": ranking_refined,
           "note": "2-D plane stress, element-centre von Mises; elements within 3 of the load point and of the "
                   "bolted edge excluded (singularities); yield at ultimate as the allowable (typical values)"}
    (OUT / "rehearsal.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"stress recovery check (uniform tension): {ratio:.4f} (expected 1)")
    print(f"ultimate load {p_ult:.0f} N, element {1000 * h:.1f} mm")
    for d in designs:
        print(f"V={d['volume']:.2f} solid={d['solid_elements']} sigma_ult={d['sigma_ult_MPa']:.0f} MPa "
              f"(all-elements max {d['sigma_ult_all_MPa']:.0f}) tip_unit={d['tip_unit']:.1f}")
    for r in rows:
        print(f"{r['option']:<22} V={r['volume']:.2f} m={r['mass_g']:.0f} g btf={r['buy_to_fly']:.1f} "
              f"MS={r['MS']:+.2f} d={r['deflection_mm']:.3f} mm pass={r['passes']} CO2={r['co2_total_kg']:.0f} kg")
    print("ranking:", [(r["option"], r["volume"], round(r["mass_g"]), round(r["co2_total_kg"])) for r in ranking])
    for m in mesh:
        m0 = mesh[0]
        print(f"mesh x{m['refinement']}: tip rel {m['tip_unit'] / m0['tip_unit']:.3f}, "
              f"vm max rel {m['vm_unit_max_scaled'] / m0['vm_unit_max_scaled']:.3f}, "
              f"p99 rel {m['vm_unit_p99_scaled'] / m0['vm_unit_p99_scaled']:.3f}")
    print("ranking with the x4-mesh deflection factor:",
          [(r["option"], r["volume"], round(r["mass_g"]), round(r["co2_total_kg"])) for r in ranking_refined])
    figure(rows)
    return 0


def figure(rows: list[dict], en: bool = False) -> None:
    """F6: mass against tip deflection per material, with the card's deflection limit."""
    import datawiz as dw
    fig_dir = ROOT / "reports" / ("figures_en" if en else "figures")
    def name_of(s: str) -> str:
        return s.replace("Eİ", "AM").replace("talaşlı", "machined") if en else s
    S = dw.Seti(str(fig_dir / "rapor.seti.json"))
    S.nicelik("sapma", "Tip deflection at limit load" if en else "Uç sapması, sınır yükte", "mm", eksen="x")
    fig, ax = S.figur(oran=0.45)
    for _, _, name in CANDIDATES:      # the 15 % designs (0.58-0.91 mm) lie far beyond the limit and are left out
        mine = [r for r in rows if r["option"] == name and r["volume"] > 0.2]
        pts = sorted((r["deflection_mm"], r["mass_g"] / 1000) for r in mine)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], **S.stil(name_of(name), tur="cizgi", isaretli=True), ms=7.1)
    dw.notlar.referans(ax, x=1000 * CARD["deflection_limit_m"],
                       metin="deflection limit 0.5 mm" if en else "sapma sınırı 0,5 mm")
    al = next(r for r in rows if r["option"] == "AlSi10Mg TO + Eİ" and r["volume"] == 0.30)
    note = "three aluminium options on one curve" if en else "üç alüminyum seçeneği aynı eğride"
    dw.notlar.ok(ax, (al["deflection_mm"], al["mass_g"] / 1000), note)
    S.eksen(ax, x="sapma", y="kutle")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(fig_dir / "F6_prova_kutle_sapma"), cvd=True)


if __name__ == "__main__":
    raise SystemExit(main())
