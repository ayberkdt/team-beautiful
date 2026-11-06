"""04_Venus/scripts/venus_budget_update.py: interaction curves, mission flight, gust model and the written result."""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from aerokit.venus import atmosphere as A
from aerokit.venus import bemt as B
from aerokit.venus import control as CT
from aerokit.venus import design as DES
from aerokit.venus import sizing as S
from aerokit.verification import check, check_true, expect_error

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "04_Venus" / "scripts" / "venus_budget_update.py"
RESULT = ROOT / "04_Venus" / "outputs" / "variants" / "budget_update" / "result.json"
BASELINE_RESULT = ROOT / "04_Venus" / "outputs" / "result.json"


def _load():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("venus_budget_update", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["venus_budget_update"] = mod
    spec.loader.exec_module(mod)
    return mod


U = _load()
POINTS = {"descent_credit": dict.fromkeys(U.CASES, 0.5), "climb_k": dict.fromkeys(U.CASES, 1.2)}


def _rows(ratio: float, bad_from: float = 99.0) -> list[dict]:
    return [{"V": v, "shaft_W": 1000.0 * ratio, "electric_W": 1300.0 * ratio, "trim_ok": v < bad_from}
            for v in range(21)]


def _curves(ratio_nominal: float = 1.2) -> dict:
    ratios = {"off": 1.0, "low": 1.1, "nominal": ratio_nominal, "high": 1.3}
    return {"schema": "vesper_guc_egrisi/1", "uretildi": "test",
            "egri": {f"{km}_km": {c: _rows(r, 18.0 if km == 51 else 99.0) for c, r in ratios.items()}
                     for km in (51, 53, 55, 58)}}


@pytest.fixture(scope="module")
def design() -> S.Design:
    return S.close(2.6, 70.0)


@pytest.fixture(scope="module")
def models(design):
    return U.build_models(_curves(), design, POINTS)


def test_curve_reader_drops_untrimmed_rows_and_checks_the_schema():
    cur = U.read_curves(_curves())
    check("51 km keeps V 0-17 only", max(r["V"] for r in cur[51.0]["nominal"]), 17)
    check("55 km keeps V 0-20", max(r["V"] for r in cur[55.0]["nominal"]), 20)
    expect_error("wrong schema", U.read_curves, {"schema": "x", "egri": {}}, error=ValueError)


def test_ratio_is_read_by_case_and_rpm_term_is_one_at_55km(models):
    V = np.array([2.0, 8.0, 12.0])
    check("off is 1 at 55 km", float(np.abs(models["off"].factor(V, 55.0) - 1.0).max()), 0.0, atol=1e-12)
    check("nominal ratio from the file", float(models["nominal"].factor(np.array([8.0]), 55.0)[0]), 1.2, rtol=1e-9)
    check_true("cases ordered", models["low"].factor(V, 55.0)[1] < models["nominal"].factor(V, 55.0)[1]
               < models["high"].factor(V, 55.0)[1])
    check("hover ratio", models["nominal"].hover_ratio(), 1.2, rtol=1e-9)


def test_proximity_law_matches_the_simulator_and_falls_with_spacing():
    check("0.10 m gap: simulator 3.52 %", U.proximity_f(2.6, 0.10), 0.0352, rtol=2e-3)
    check_true("wider gap loses less", U.proximity_f(2.6, 0.78) < U.proximity_f(2.6, 0.26) < U.proximity_f(2.6, 0.10))


def test_correlation_time_is_the_data_book_formula():
    check("1500 s at rest", U.correlation_time(0.0), 1500.0)
    check("loiter", U.correlation_time(8.0), 1.0 / (1.0 / 1500.0 + 8.0 / 5000.0), rtol=1e-12)


def test_pack_loses_energy_on_discharge_and_limits_charge():
    cap, R = 1044.0, 0.06
    soc = U.battery_step(2000.0, 0.8, cap, R, 13.4, 3600.0)
    check_true("I2R: more than the terminal energy leaves the cells", (0.8 - soc) * cap > 2000.0)
    ideal = (0.8 - U.battery_step(1.0, 0.8, cap, 1e-9, 13.4, 3600.0)) * cap
    check("no resistance: terminal energy", ideal, 1.0, rtol=1e-4)
    up = U.battery_step(-5000.0, 0.5, cap, R, 13.4, 60.0)
    ocv = float(np.interp(0.5, U.OCV_SOC, U.OCV_V))
    check_true("charge limited to the current limit", (up - 0.5) * cap * 60.0 <= 13.4 * ocv + 1e-6)


def test_legacy_profile_reproduces_doc25(design):
    """Regression anchor: with every addition off, fly() is simulate_rotorcraft_day."""
    base = json.loads(BASELINE_RESULT.read_text(encoding="utf-8"))["mission"]
    leg = U.Profile.legacy()
    fl = U.fly(design, U.power_table(design, None, leg), leg, DES.release_hour_angle(design))
    check("flight hours", fl.flight_h, base["flight_h"], rtol=1e-9, source="04_Venus/outputs/result.json")
    check("sunlit hours", fl.sun_h, base["sustained_h"], rtol=1e-9, source="04_Venus/outputs/result.json")
    check("drift", fl.drift_km, base["drift_km"], rtol=1e-6, source="04_Venus/outputs/result.json")


def test_closed_form_window_reproduces_the_crosscheck(design):
    w = U.window_budget(design, U.power_table(design, None, U.Profile.legacy()))
    check("cos z", w["mu0"], 0.5953, rtol=1e-3)
    check("window", w["window_h"], 45.76, rtol=1e-3)
    check("margin", w["margin"], 1.77, rtol=2e-3)


def test_interaction_raises_the_sun_threshold(design, models):
    prof = U.Profile()
    mus = [U.threshold_mu0(design, U.power_table(design, models[c], prof)) for c in U.CASES]
    check_true("threshold rises with interaction", all(a < b for a, b in zip(mus, mus[1:], strict=False)), mus)


def test_mission_energy_balance(design, models):
    """Ideal pack, no charge limit reached: state of charge follows the integral of array minus demand."""
    prof = replace(U.Profile(), pack_model=False, start_km=55.0, dive_times_h=())
    tab = U.power_table(design, models["nominal"], prof)
    fl = U.fly(design, tab, prof, 60.0, stop_h=1.0)
    net = (fl.p_sun - fl.p_need) * 60.0 / 3600.0
    check("SoC drop = energy deficit", (1.0 - fl.soc[-1]) * design.battery_Wh, -float(net.sum()), rtol=1e-9)


def test_old_gust_result_reproduces_and_model_rms_is_exact(design):
    st = A.state(55e3)
    fl = B.FlowState(st.rho, st.mu, st.a)
    W = design.gross_kg * st.g
    sys0 = U.isolated_system(design)
    Zw = CT.heave_derivative(sys0, W, fl)
    old = CT.gust_response(design.gross_kg, W, Zw, 0.1, kp=0.1, kd=1.0)
    check("doc 25: 4 m RMS", old["z_rms_m"], 4.1, atol=0.05)
    check("doc 25: 14 % thrust peak", old["dT_peak_over_W"], 0.14, atol=0.005)
    slow = U.gust_model(design.gross_kg, W, Zw, 0.7, 1e6, 0.0, 533.0, 0.0, hours=0.1, seeds=2)
    quasi = abs(Zw) * 0.7 / (design.gross_kg * 0.1)
    check("very slow gust: static altitude offset", slow["z_rms_m"], quasi, rtol=1e-3)
    check("very slow gust: thrust = |Z_w| sigma", slow["dT_rms_over_W"], abs(Zw) * 0.7 / W, rtol=1e-3)


def test_dryden_part_has_the_requested_sigma():
    from scipy.linalg import solve_continuous_lyapunov as lyap

    a, b = U.gust_system(43.7, -31.8, 0.1, 0.1, 1.0, 1e-9, 1500.0, 0.5, 533.0, 8.0)
    sub = lyap(a[4:, 4:], -b[4:, 1:2] @ b[4:, 1:2].T)
    T = 533.0 / 8.0
    g = -a[1, 4] / (31.8 / 43.7)
    out = np.array([g, g * math.sqrt(3.0) * T])
    check("sigma of w_C", math.sqrt(float(out @ sub @ out)), 0.5, rtol=1e-6)


def test_hover_loss_context_restores_aerokit(design):
    with U.hover_loss(0.05):
        d = S.close(2.6, 70.0)
    check_true("sizing sees the loss", d.gross_kg > design.gross_kg)
    check("aerokit restored", S.close(2.6, 70.0).gross_kg, design.gross_kg, rtol=1e-12)


@pytest.mark.skipif(not RESULT.is_file(), reason="run venus_budget_update.py first")
class TestWrittenResult:
    r = json.loads(RESULT.read_text(encoding="utf-8")) if RESULT.is_file() else {}

    def test_legacy_anchor_recorded(self):
        check("flight", self.r["legacy_check"]["flight_h"], 49.1833, atol=1e-3)
        check("sun", self.r["legacy_check"]["sun_h"], 44.1833, atol=1e-3)

    def test_every_case_is_present_and_ordered(self):
        c = self.r["cases"]
        check_true("all cases", set(c) == set(U.CASES))
        loiter = [c[k]["loiter_W"] for k in U.CASES]
        hours = [c[k]["flight_h"] for k in U.CASES]
        check_true("more interaction, more power", all(a < b for a, b in zip(loiter, loiter[1:], strict=False)), loiter)
        check_true("more interaction, fewer hours", all(a > b for a, b in zip(hours, hours[1:], strict=False)), hours)

    def test_budget_follows_the_file_within_two_percent(self):
        for k in U.CASES:
            check(f"{k} loiter vs file minimum", self.r["cases"][k]["loiter_W"],
                  self.r["file_minimum_55km"][k]["electric_W"], rtol=0.02)

    def test_each_mission_records_its_events(self):
        for k in U.CASES:
            names = " ".join(e["event"] for e in self.r["cases"][k]["events"])
            for word in ("release", "cruise altitude", "science dive 1", "science dive 2", "sunset dive", "end:"):
                check_true(f"{k}: {word}", word in names)

    def test_recommended_option_exists_and_closes(self):
        rec = next(o for o in self.r["options"] if o["option"] == self.r["recommended"])
        check_true("recommended design closes", rec["closes"])

    def test_recommended_design_closes_in_every_interaction_case(self):
        for k in U.CASES:
            check_true(f"{k} closes", self.r["recommended_cases"][k]["closes"], self.r["recommended_cases"][k]["checks"])

    def test_as_built_misses_only_the_reserve_rule_with_interaction(self):
        for k in ("low", "nominal", "high"):
            failed = [n for n, ok in self.r["cases"][k]["checks"].items() if not ok]
            check_true(f"{k}: only the reserve rule fails", failed == ["hover_reserve"], failed)

    def test_cruise_below_the_charge_window_is_rejected(self):
        row = next(o for o in self.r["options"] if o["option"] == "cruise 54 km")
        check_true("54 km cannot charge", not row["checks"]["charges_at_cruise"])

    def test_new_release_keeps_pull_out_current_inside_the_limit(self):
        pts = {round(x["mu0"], 2): x["Ipeak"] for x in self.r["simulator_points"]["release_current"]}
        mu = math.cos(math.radians(self.r["recommended_cases"]["nominal"]["release_hour_angle_deg"]))
        check_true("old release over the limit", pts[0.63] > 53.6)
        check_true("new release under the limit", pts[round(mu, 2)] < 53.6, mu)

    def test_budget_agrees_with_the_simulator_in_calm_air(self):
        for row in self.r["sim_crosscheck"]:
            if row["air"] == "calm":
                check(row["name"], row["budget_end_soc"], row["sim_end_soc"], atol=0.05)


def test_doc25_is_anchored_before_the_update():
    old = ROOT / "04_Venus" / "docs" / "versions" / "25_lugus_venus_rotorcraft_2026-11-06_before_budget_update.md"
    check_true("anchor exists", old.is_file())
    check_true("anchor is the 4 Nov text", "~49 h of flight" in old.read_text(encoding="utf-8"))
