"""Shared T10 check of a layout STL with the organisers' Ti-8Al-1Mo-1V data (used by verify_v2.py and
finalize_v2.py so the TO shape and the finalized shape are judged by exactly the same code).

Cases: the set-up's 4 card cases (LC1a/b/c per lug, LC2 torsion My 2000 N m) + 6 combined LC1a/b/c + LC2 (±My) [Y].
LC2 is a torque about the pin axis applied as tangential traction on the bores: valid for a clamped/keyed pin [Y].
Unit-E solve: stress is E-independent, displacement = u(E=1)/E."""
import copy, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[4] / "src"), "D:/tmp_ideathon/pylib", str(HERE)]
from aerokit.bracket import tetfem   # noqa: E402
from organiser_materials import M, gm   # noqa: E402

TI = M["Ti811SA"]
# Both checks use the LOW end of the organisers' range (5 Nov fix: stiffness used the geometric mean 124 GPa while
# strength used the low-end yield). 300 °C knock-downs from catalogue/materials_catalogue.md (MIL-HDBK-5J Ti-8-1-1
# SA): E 104.8/120.7 = 0.868, Fty 518/758 = 0.683. Low-end E at 300 °C = 121 × 0.868 = 105.1 GPa (MIL: 104.8).
E23 = TI["E"][0] * 1e9
E300 = E23 * (104.8 / 120.7)
FY23 = TI["Fy"][0]
FY300 = FY23 * (518.0 / 758.0)
LIM_MM = 661.01 / 400


def with_combined(setup):
    s = copy.deepcopy(setup)
    lc = {c["name"][:4]: c for c in s["load_cases"]}
    for a in ("LC1a", "LC1b", "LC1c"):          # LC1c included (5 Nov review: it governs the displacement)
        for sgn, tag in ((1, "+"), (-1, "-")):
            loads = copy.deepcopy(lc[a]["loads"]) + [dict(ld, moment_Nm=[sgn * v for v in ld["moment_Nm"]])
                                                     for ld in copy.deepcopy(lc["LC2 "]["loads"])]
            s["load_cases"].append({"name": f"LC3 {a} + LC2 ({tag}My) combined [Y]", "loads": loads})
    return s


def check(stl, setup, size_mm, bore_tol_m):
    t0 = time.perf_counter()
    m = tetfem.mesh_stl(stl, size_mm)
    r = tetfem.static_t10(m, setup, 1.0, bore_tol_m=bore_tol_m)
    # governing stress: von Mises everywhere except the fixed-support zones (lug eyes INCLUDED)
    sig = max(c["vm_outside_supports_Pa"] for c in r["cases"]) / 1e6
    wc = max(r["cases"], key=lambda c: c["vm_outside_supports_Pa"])
    sig_hz = max(c["vm_outside_Pa"] for c in r["cases"]) / 1e6          # old measure (all hole zones excluded)
    u1 = max(c["max_disp_m"] for c in r["cases"])
    wu = max(r["cases"], key=lambda c: c["max_disp_m"])
    mass = r["volume_m3"] * gm(TI["rho"])
    return {"T10_elements": r["elements"], "mesh_size_mm": size_mm, "volume_m3": r["volume_m3"], "mass_Ti811_kg": mass,
            "per_case": [{"name": c["name"], "vm_out_MPa": c["vm_outside_Pa"] / 1e6, "vm_max_MPa": c["vm_max_Pa"] / 1e6,
                          "vm_out_supports_MPa": c["vm_outside_supports_Pa"] / 1e6,
                          "at_supports_mm": [round(x * 1e3) for x in c["vm_outside_supports_at_m"]],
                          "bolt_reactions_kN": {k: [round(v / 1e3, 2) for v in r_] for k, r_ in c["reactions_N"].items()},
                          "disp_mm_300C": c["max_disp_m"] / E300 * 1e3,
                          "at_mm": [round(x * 1e3) for x in c["vm_outside_at_m"]]} for c in r["cases"]],
            "sigma_max_MPa": sig, "sigma_case": wc["name"],
            "sigma_at_mm": [round(x * 1e3) for x in wc["vm_outside_supports_at_m"]],
            "sigma_outside_all_hole_zones_MPa": sig_hz,
            "disp_mm_23C": u1 / E23 * 1e3, "disp_mm_300C": u1 / E300 * 1e3, "disp_case": wu["name"],
            "util_23C": 1.5 * sig / FY23, "util_300C": 1.5 * sig / FY300, "disp_limit_mm": LIM_MM,
            "allow_vm_300C_MPa": FY300 / 1.5,
            "passes_300C": bool(1.5 * sig <= FY300 and u1 / E300 * 1e3 < LIM_MM), "solve_s": time.perf_counter() - t0}
