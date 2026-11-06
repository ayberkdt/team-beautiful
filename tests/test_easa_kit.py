"""EASA day kit (02_EASA/scripts/easa_kit.py): the any-aircraft latch study, traceability coverage and the 4:00 budget."""
import importlib.util
import pathlib

from aerokit.verification import check, check_true

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "02_EASA" / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_latch_study_one_sensor_per_point_is_needed():
    kit = _load("easa_kit")
    cfg = _load("canopy_day").load(ROOT / "02_EASA" / "inputs" / "inputs.json")
    rows = {r["points"]: r for r in kit.latch_study(cfg, points=(2, 4), n=20_000)}
    for k, r in rows.items():
        check(f"{k} points: seated-only misses every partial lock", r["seated"]["miss_partial"], 1.0, atol=1e-9)
        check(f"{k} points: one latch sensor misses a single point out (N-1)/N of the time", r["one"]["miss_one"],
              (k - 1) / k, atol=0.02)
        check_true(f"{k} points: one sensor per point keeps the one-out miss below 1 %", r["per_latch"]["miss_one"] < 0.01)
        check_true(f"{k} points: per-point sensing beats one sensor by > 10x (pilot acts)",
                   r["per_latch"]["rf_full"] > 10 * r["one"]["rf_full"])


def test_traceability_covers_every_requirement_and_hazard():
    kit = _load("easa_kit")
    reqs = [r[0] for r in kit.TRACE]
    check_true("14 requirements traced, in order (R-13 shaker, R-14 gate added 5 Nov)", reqs == [f"R-{i}" for i in range(1, 15)])
    hazards = " ".join(r[2] for r in kit.TRACE)
    check_true("hazards H1-H6 all appear", all(f"H{i}" in hazards for i in range(1, 7)))
    check_true("every row names a verification step", all(r[4].strip() for r in kit.TRACE))


def test_talk_fits_four_minutes_and_bom_totals():
    kit = _load("easa_kit")
    lines = kit.talk_check()
    check_true("no talk block over its slot", not any("OVER" in ln for ln in lines))
    words = int(lines[-1].split("total ")[1].split(" words")[0])
    check_true("spoken text fits inside the 240 s hard cut", words / kit.WORDS_PER_S < 240)
    _, tot = kit.bom_rows()
    check_true("sensor power 4 x 10 mA x 14 V is inside the upper total", round(tot["p_hi"], 2) >= 0.56)
    check_true("mass range ordered", tot["m_lo"] < tot["m_hi"])
