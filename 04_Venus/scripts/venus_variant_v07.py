"""VESPER v0.7 variant: the recommended 44.63 kg design as VARIANT files. The baseline stays v0.6 until the user says yes.

    python 04_Venus/scripts/venus_variant_v07.py --sweeps        # F7/F9/F10 inputs (trade_sizing.json, sensitivity.json)
    python 04_Venus/scripts/venus_variant_v07.py                 # design.json, sim_params.json, result, F1-F15, CHANGES.md
    python 04_Venus/scripts/venus_variant_v07.py --promote       # dry run: lists what promotion would do
    python 04_Venus/scripts/venus_variant_v07.py --promote --yes # anchors the baseline, copies the variant over it

Everything is written to ``04_Venus/outputs/variants/v0_7_44p6kg/``. Only ``--promote --yes`` writes anywhere else.
Nothing in ``aerokit`` or in the other scripts changes: this wrapper closes the design with
``venus_budget_update.close_with_interaction``, flies it with ``venus_budget_update.fly_case`` (nominal interaction,
6 Nov profile), and feeds that into ``venus_final.compute/figures``, ``aerokit.venus.design.design_document`` and
``venus_sim_params.build`` by patching their inputs for the length of one call.

Inputs are pinned: the interaction curves come from the copy in ``variants/budget_update/sim_runs/`` (sha256 checked),
not from the sunumatik repo, which another session is editing.

**Interaction in the numbers.** ``hover``/``loiter`` power, the sun threshold and the mission include nominal interaction.
The rotor curve in ``sim_params.json`` stays isolated-rotor (factor 1.05): the simulator adds its own wake model.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import hashlib
import json
import math
import pickle
import re
import shutil
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import venus_budget_update as BU  # noqa: E402
import venus_entry_validation as EV  # noqa: E402
import venus_final as VFN  # noqa: E402
import venus_sensitivity as VS  # noqa: E402
import venus_sim_params as SP  # noqa: E402

from aerokit import venus_flight as VF  # noqa: E402
from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import bemt as B  # noqa: E402
from aerokit.venus import control as CT  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import performance as F  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import sizing as S  # noqa: E402

OUTPUTS = ROOT / "04_Venus" / "outputs"
VAR = OUTPUTS / "variants" / "v0_7_44p6kg"
TMP = Path("D:/tmp_ideathon/venus_v07")
CURVES = BU.OUT / "sim_runs" / "guc_egrisi.input.json"
CURVES_SHA = "938bba1d9e5e12d073f078f2897abdb19e5eff21e5e244cbdf4e54594d864f7a"
BUDGET = BU.OUT / "result.json"
VERSION = "0.7"
ME = "python 04_Venus/scripts/venus_variant_v07.py"
RELEASE_RPM_RATIO = 1.30          # doc 25 §5.2: rpm schedule cap, 1.30 x hover rpm (back-EMF cap)
RELEASE_MIN_MU0 = 0.68            # doc 25 §0: no release below cos z 0.68 (52.7 A at 43.66 kg)
# files of the variant folder that are records of the variant, not hand-off files
NOT_PROMOTED = {"CHANGES.md", "baseline_hashes_before.json", "changes_full.json", "sim_params_changes.json",
                "figures_status.json", "PROMOTED.json"}
SERIES_PATHS = ("operations.series_hourly", "operations.events", "deployment_replay.rows", "mission_series.rows",
                "vehicle.rotors.curve_at_55km.rows")


def _write(path: Path, text: str) -> None:
    """All normal writes pass here: nothing outside the variant folder."""
    path = Path(path).resolve()
    if VAR.resolve() not in path.parents:
        raise RuntimeError(f"refusing to write outside the variant folder: {path}")
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------------
# the design and its flight
# ---------------------------------------------------------------------------------------------------------------

@dataclass
class MissionRun:
    """``venus_budget_update.Flight`` in the shape ``aerokit.venus_flight.DayRun`` has, for the code that reads it."""

    t: np.ndarray
    z: np.ndarray
    x: np.ndarray
    mu0: np.ndarray
    p_need: np.ndarray
    p_solar: np.ndarray
    energy_Wh: np.ndarray
    T_interior_C: np.ndarray
    events: list = field(default_factory=list)
    flight_time_s: float = 0.0
    solar_sustained_s: float = 0.0
    no_charge_s: float = 0.0


def as_run(fl: BU.Flight, d: S.Design) -> MissionRun:
    dt = float(fl.t[1] - fl.t[0])
    x = np.cumsum([A.zonal_wind(min(max(float(z), A.Z_MIN), A.Z_MAX)) * dt for z in fl.z])
    x[-1] = fl.drift_km * 1e3
    blocked = (fl.p_sun > fl.p_need) & (fl.T_int > d.req.battery.charge_C[1])
    return MissionRun(fl.t, fl.z, x, fl.mu0, fl.p_need, fl.p_sun, fl.soc * d.battery_Wh, fl.T_int,
                      [(e["t_h"] * 3600.0, e["event"]) for e in fl.events], fl.flight_h * 3600.0, fl.sun_h * 3600.0,
                      float(blocked.sum()) * dt)


def level_curve(d: S.Design, im: BU.Interaction, km: float, V: np.ndarray | None = None) -> np.ndarray:
    """Shaft power with interaction at any altitude and speed. Same formula as ``BU.isolated_table``, which stops at 62 km."""
    V = BU.V_GRID if V is None else np.asarray(V, float)
    sys0 = BU.isolated_system(d)

    def hover_at(k: float):
        st = A.state(k * 1e3)
        fl = B.FlowState(st.rho, st.mu, st.a)
        W = d.gross_kg * st.g
        return F.hover(sys0, W, fl), fl, W

    hp, fl, W = hover_at(km)
    v55 = hover_at(55.0)[0].v_h
    vi = np.sqrt((-V ** 2 + np.sqrt(V ** 4 + 4.0 * hp.v_h ** 4)) / 2.0)
    iso = hp.kappa * W * vi + hp.profile_W * (1.0 + 4.65 * (V / hp.per_rotor.tip_speed) ** 2) \
        + 0.5 * fl.rho * V ** 3 * sys0.drag_area_m2
    return iso * im.factor(V, km, im.v_h55 / v55)


def models() -> tuple[dict, S.Design]:
    raw_bytes = CURVES.read_bytes()
    if hashlib.sha256(raw_bytes).hexdigest() != CURVES_SHA:
        raise SystemExit(f"{CURVES} is not the file the budget used (sha256 {CURVES_SHA[:12]})")
    base = S.close(2.6, 70.0)
    return BU.build_models(json.loads(raw_bytes.decode("utf-8")), base, BU.sim_points()), base


def recommended(ms: dict) -> dict:
    """Close and fly the recommended design; stop if it is not the design of the 6 Nov budget."""
    nom = ms["nominal"]
    prof = BU.Profile()
    d_rec = BU.close_with_interaction(nom)
    case = BU.fly_case(d_rec, nom, prof)
    tab = BU.power_table(d_rec, nom, prof)
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    ref = budget["recommended_cases"]["nominal"]
    for k in ("gross_kg", "battery_Wh", "hover_W", "loiter_W", "mu0_loiter", "flight_h", "sun_h", "drift_km", "lowest_km"):
        if not math.isclose(case[k], ref[k], rel_tol=1e-9):
            raise SystemExit(f"{k}: this run {case[k]} != budget {ref[k]}: the budget result is stale")
    d = replace(d_rec, system=BU.isolated_system(d_rec), P_hover_elec_W=case["hover_W"], P_bucket_elec_W=case["loiter_W"],
                V_bucket=case["loiter_speed_m_s"], sustain_mu0_hover=case["mu0_hover"],
                sustain_mu0_loiter=case["mu0_loiter"])
    return {"d": d, "d_rec": d_rec, "case": case, "tab": tab, "prof": prof, "nom": nom, "budget": budget}


def vehicle_chain(m: dict) -> dict:
    """Entry, chute and deployment of ``aerokit.venus.design.baseline`` for this vehicle and this flight."""
    run = as_run(m["case"]["_flight"], m["d"])
    with mock.patch.object(DES.S, "close", lambda *a, **k: m["d"]), \
            mock.patch.object(VF, "simulate_rotorcraft_day", lambda *a, **k: run):
        return DES.baseline.__wrapped__(DES.BASELINE)


@contextlib.contextmanager
def patched(res: dict, doc: dict | None = None):
    """``DES.baseline`` -> this vehicle; entry validation does not rewrite its baseline files; version 0.7."""
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.object(DES, "baseline", lambda b=None: res))
        st.enter_context(mock.patch.object(DES, "DESIGN_VERSION", VERSION))
        st.enter_context(mock.patch.object(EV, "main", lambda argv: 0))
        st.enter_context(mock.patch.object(VFN, "OUT", VAR))
        if doc is not None:
            st.enter_context(mock.patch.object(DES, "design_document", lambda b=None: doc))
        yield


# ---------------------------------------------------------------------------------------------------------------
# sweeps for F7, F9, F10
# ---------------------------------------------------------------------------------------------------------------

def close_variant(im: BU.Interaction, D: float, vt: float, req: S.Requirements, mm: S.MassModel = S.MassModel()) -> S.Design:
    with BU.hover_loss(im.hover_ratio() - 1.0):
        return S.close(D, vt, req, mm)


def loiter_55(d: S.Design, im: BU.Interaction) -> tuple[float, float, float | None]:
    """(loiter W incl. system load, speed, cos z threshold) at the cruise altitude, with interaction."""
    km = d.req.altitude_m / 1e3
    shaft = level_curve(d, im, km)
    i = int(np.argmin(shaft))
    p = float(shaft[i]) / BU.isolated_system(d).drive_efficiency + d.P_sys_W
    return p, float(BU.V_GRID[i]), S._mu0_for(p, PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency), d.req.altitude_m)


def sweep_trade(im: BU.Interaction) -> dict:
    rows = []
    for opt in ("deck", "halo", "blades"):
        req = replace(S.Requirements(), solar_option=opt)
        for D in (1.4, 1.7, 2.0, 2.3, 2.6, 2.9):
            for vt in (55.0, 70.0, 90.0, 115.0):
                rec = {"D_m": D, "V_tip_m_s": vt, "solar_option": opt}
                try:
                    d = close_variant(im, D, vt, req)
                    sm = d.summary()
                    rec.update({k: sm[k] for k in ("gross_kg", "P_hover_elec_W", "P_bucket_elec_W", "V_bucket",
                                                   "P_solar_overhead_W", "solar_area_m2", "sustain_mu0_hover",
                                                   "sustain_mu0_loiter", "rpm", "FM", "tip_mach", "re75", "theta75_deg",
                                                   "solidity", "disk_loading_N_m2", "battery_Wh", "arm_m", "converged")})
                    rec["P_bucket_elec_W"], rec["V_bucket"], rec["sustain_mu0_loiter"] = loiter_55(d, im)
                    rec["breakdown"] = sm["breakdown"]
                except ValueError as e:
                    rec["error"] = str(e)
                rows.append(rec)
                print(f"{opt} D {D} Vt {vt}: {rec.get('gross_kg', 'no closure')}", flush=True)
    return {"generated_by": f"{ME} --sweeps", "note": "Same rows as venus_trade.py, closed with hover +3.42 % and read "
            "with the nominal interaction at equal V/v_h [Y: the curves were flown at D 2.6 m only].", "rows": rows}


def _flown(im: BU.Interaction, prof: BU.Profile, D: float, req: S.Requirements, mm: S.MassModel) -> dict:
    try:
        d = close_variant(im, D, 70.0, req, mm)
    except ValueError as e:
        return {"error": str(e)}
    try:
        r = BU.fly_case(d, im, prof, step_km=0.5)
    except RuntimeError as e:
        return {"gross_kg": d.gross_kg, "flight_error": str(e), "flight_h": 0.0, "sustained_h": 0.0}
    return {"gross_kg": d.gross_kg, "mu0_loiter": r["mu0_loiter"], "loiter_W": r["loiter_W"],
            "solar_overhead_W": r["solar_overhead_W"], "flight_h": r["flight_h"], "sustained_h": r["sun_h"],
            "release_hour_angle_deg": r["release_hour_angle_deg"], "closes": r["closes"], "span_m": 2 * d.arm_m + D}


def sweep_sensitivity(im: BU.Interaction) -> dict:
    prof = BU.Profile()
    req0, mm0 = S.Requirements(), S.MassModel()
    rows = [dict(_flown(im, prof, 2.6, req0, mm0), label="baseline", case="baseline")]
    for label, name, lo, hi in VS.CASES:
        for tag, val in (("bad", lo), ("good", hi)):
            req, mm = (replace(req0, **{name: val}), mm0) if hasattr(req0, name) else (req0, replace(mm0, **{name: val}))
            rows.append(dict(_flown(im, prof, 2.6, req, mm), label=f"{label} [{tag}]", case=label, side=tag,
                             value=repr(val) if name == "battery" else val))
            print(rows[-1], flush=True)
    adverse = (("nominal", {}, {}), ("cells 180 Wh/kg", {"battery": replace(PW.LI_ION_NCR18650B, cell_specific_energy=180.0)}, {}),
               ("contingency 30 %", {}, {"contingency": 0.30}), ("motors 5 N·m/kg", {}, {"motor_specific_torque": 5.0}),
               ("payload 5 kg", {"payload_kg": 5.0}, {}), ("thin atmosphere", {"atmosphere_case": "thin"}, {}))
    robust = []
    for Dr, gear in ((2.6, 5.0), (2.6, 1.0), (2.3, 5.0)):
        for label, rk, mk in adverse:
            r = _flown(im, prof, Dr, replace(req0, **rk), replace(mm0, **dict(mk, gear_ratio=gear)))
            robust.append(dict(r, D_m=Dr, gear_ratio=gear, case=label))
            print(robust[-1], flush=True)
    return {"generated_by": f"{ME} --sweeps", "D_m": 2.6, "V_tip_m_s": 70.0,
            "note": "Same cases as venus_sensitivity.py, closed with hover +3.42 % and flown with venus_budget_update.fly_case "
                    "(nominal interaction, 6 Nov profile, 0.5 km power grid).", "rows": rows, "robustness": robust}


# ---------------------------------------------------------------------------------------------------------------
# numbers of venus_final.compute() that do not follow from the patched inputs
# ---------------------------------------------------------------------------------------------------------------

def corrected(c: dict, m: dict, gust: dict, gust_mc: dict) -> dict:
    """Replace what ``compute`` takes from isolated rotors, the 80 s gust or the legacy mission."""
    out, d, im, prof = c["out"], m["d"], m["nom"], m["prof"]
    eta, P_sys = d.system.drive_efficiency, d.P_sys_W
    out["generated_by"] = ME
    for r in out["power_vs_altitude"]:
        sh = level_curve(d, im, float(r["km"]))
        r["hover_W"], r["loiter_W"] = float(sh[0]) / eta + P_sys, float(sh.min()) / eta + P_sys
    r55 = next(r for r in out["power_vs_altitude"] if r["km"] == 55)
    for got, want in ((r55["hover_W"], m["case"]["hover_W"]), (r55["loiter_W"], m["case"]["loiter_W"])):
        if not math.isclose(got, want, rel_tol=1e-6):
            raise SystemExit(f"level_curve {got} != power table {want} at 55 km")
    sk = out["station_keeping"]
    sk["electric_W"] = (level_curve(d, im, 55.0, np.array(sk["speeds"])) / eta + P_sys).tolist()
    tab, H0, horizon = m["tab"], m["case"]["release_hour_angle_deg"], m["case"]["sunset_horizon_h"]
    lat_rows = []
    for row in out["latitude_study"]:
        cl, mu = math.cos(math.radians(row["latitude_deg"])), d.sustain_mu0_loiter
        H = -math.degrees(math.acos(min((mu + 0.03) / cl, 1.0))) if mu + 0.03 <= cl else 0.0
        fl = BU.fly(d, tab, replace(prof, sunset_horizon_h=horizon), H, dt=120.0, latitude_deg=row["latitude_deg"])
        lat_rows.append({"latitude_deg": row["latitude_deg"], "release_hour_angle_deg": H, "flight_h": fl.flight_h,
                         "sustained_h": fl.sun_h, "note": row["note"] + "; 6 Nov profile, same sunset horizon as the equator"})
    out["latitude_study"] = lat_rows
    worst = gust["A_plus_C_loiter"]["dT_peak_max_over_W"]
    for x in out["margins"]:
        if x["item"].startswith("Thrust margin"):
            x["ratio"] = gust["thrust_margin"] / worst
    for r in out["risks"]:
        r["evidence"] = (r["evidence"]
                         .replace("loiter 1.34 kW vs 1.04 kWh", f"loiter {d.P_bucket_elec_W / 1e3:.2f} kW vs "
                                  f"{d.battery_Wh / 1e3:.2f} kWh")
                         .replace("cos z > 0.60", f"cos z > {d.sustain_mu0_loiter:.2f}")
                         .replace("~49 h", f"~{m['case']['flight_h']:.0f} h")
                         .replace("51 km dives peak ~57 °C", f"52 km dives peak ~{m['case']['T_peak_before_sunset_C']:.1f} °C"))
    out["variant"] = {"version": VERSION, "gust": gust, "gust_mission": gust_mc, "case": BU.strip(m["case"]),
                      "pack": dict(zip(("parallel", "resistance_ohm", "charge_limit_A"), BU.pack(d), strict=True)),
                      "max_discharge_A": d.req.battery.max_C_rate * BU.CELL_AH * BU.pack(d)[0],
                      "not_recomputed": "link, navigation, BEMT validation, entry validation: no mass input"}
    return out


def max_airspeed(d: S.Design, im: BU.Interaction) -> float:
    """``control.max_airspeed`` with interaction: the shaft limit stays 1.6^1.5 x hover shaft power."""
    Vs = np.arange(0.0, 60.0, 0.25)
    shaft = level_curve(d, im, 55.0, Vs)
    best = 0.0
    for V, p in zip(Vs, shaft, strict=True):
        if p <= d.hover.shaft_W * 1.6 ** 1.5:
            best = float(V)
        elif V > 5.0:
            break
    return best


# ---------------------------------------------------------------------------------------------------------------
# design.json
# ---------------------------------------------------------------------------------------------------------------

KIND_OF = {"cruise altitude reached": "release", "array no longer carries loiter": "sunset"}   # the enum has no "other"


def event_kind(text: str) -> str:
    if text.startswith("end:"):
        return "end"
    return KIND_OF.get(text, DES._event_kind(text))


def design_doc(c: dict, m: dict, res: dict) -> dict:
    d, case, run = m["d"], m["case"], res["mission"]
    comps_src = d.breakdown
    doc = DES.design_document(DES.BASELINE)
    steps = {s["step"]: s for s in doc["deployment_sequence"]}
    rotors = next(x for x in doc["vehicle"]["components"] if x["id"] == "rotors")
    rotors["mass_kg"] = round(comps_src["blades+hubs"] + comps_src["motors"] + comps_src["ESCs"], 3)   # no gram lost to rounding
    ev = {e["event"]: e for e in case["events"]}
    t_cruise_h = ev["cruise altitude reached"]["t_h"]
    t_rel = steps[8]["time_s"]
    dep = res["deploy"]
    rpm_rel = RELEASE_RPM_RATIO * d.hover.rpm
    mu_rel = ev["release at 61.0 km"]["mu0"]
    wind = c["term"]["windmilling"]
    steps[7]["load"] = (f"zero-lift collective, about -16 deg at 0.75 R (no thrust on the bridle at the {res['chute'].V_end:.1f} "
                        "m/s descent); spin-up ~2.3 s per rotor; alternating spins cancel torque")
    steps[8]["name"] = (f"Release at {res['chute'].V_end:.0f} m/s descent on an rpm schedule up to {rpm_rel:.0f} rpm "
                        f"({RELEASE_RPM_RATIO:.2f} x hover); pull-out in {dep.t_arrest_s:.1f} s, {dep.altitude_loss_m:.0f} m "
                        "lost (forward flight through vortex-ring band)")
    steps[8]["decision"] = (f"release window 63-60 km, descent < 16 m/s, battery > 90 %, cos z >= {RELEASE_MIN_MU0:.2f} "
                            f"(planned release at cos z {mu_rel:.2f})")
    steps[9]["name"] = ("Descend at 1.5 m/s with 3.5 m/s forward to the 55 km cruise level, on sunlight; begin air-mass-frame "
                        "science loiter")
    steps[9]["time_s"] = round(t_rel + t_cruise_h * 3600.0, 0)
    steps[10]["name"] = (f"Solar-sustained flight ~{run.solar_sustained_s / 3600:.0f} h, science dives to "
                         f"{m['prof'].dive_km:.0f} km (abort above {m['prof'].dive_abort_C:.0f} °C)")
    steps[10]["time_s"] = round(steps[9]["time_s"] + 3600.0, 0)
    steps[11]["name"] = (f"Sunset: final dive measuring through the lower cloud to about {case['lowest_km']:.1f} km, "
                         "where the battery reaches the 60 °C limit")
    steps[11]["time_s"] = round(t_rel + run.flight_time_s, 0)
    steps[12]["name"] = (f"No landing: unpowered fall with windmilling rotors (~{wind.t_surface_s / 3600:.0f} h to the surface, "
                         f"{wind.impact_speed:.1f} m/s at impact); electronics pass 125 °C near "
                         f"{wind.h_electronics_125C_m / 1e3:.0f} km; the vehicle reaches the surface as debris")
    doc["operating_band"]["rationale"] = doc["operating_band"]["rationale"].replace(
        "dives to 51 km thermally limited", f"dives to {m['prof'].dive_km:.0f} km thermally limited")
    for e in doc["operations"]["events"]:
        e["kind"] = event_kind(e["event"])
    doc["note"] += (" VARIANT v0.7: 44.63 kg re-closure and 6 Nov profile (venus_budget_update.py, nominal interaction); "
                    "not confirmed by the team, the baseline stays v0.6 in outputs/design.json.")
    doc["generated_by"] = ME
    doc["generated_at"] = _dt.datetime.now().astimezone().isoformat(timespec="minutes")
    total = sum(x["mass_kg"] for x in doc["vehicle"]["components"])
    if abs(total - doc["vehicle"]["total_mass_kg"]) >= 0.0005:
        raise SystemExit(f"components sum to {total:.4f} kg, total_mass_kg is {doc['vehicle']['total_mass_kg']}")
    return doc


# ---------------------------------------------------------------------------------------------------------------
# sim_params.json
# ---------------------------------------------------------------------------------------------------------------

CLOSURE = "aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction)"
SIM_WHY = {
    "vehicle.mass": ("K", CLOSURE),
    "vehicle.cg": ("K", "component layout of the variant design.json"),
    "vehicle.inertia": ("K", "point masses + rods from the variant design.json"),
    "vehicle.power.battery_capacity": ("K", "0.5 h of 2219 W hover; " + CLOSURE),
    "vehicle.power.hover_electric_55km": ("K/Y", "BEMT + hover interaction +3.42 % (guc_egrisi.json, extrapolated to 0.04 D [Y])"),
    "vehicle.power.loiter_electric_55km": ("K/Y", "aerokit level power x nominal interaction ratio (guc_egrisi.json)"),
    "vehicle.power.loiter_airspeed": ("K/Y", "minimum-power speed with nominal interaction"),
}


def sim_doc(c: dict, m: dict, doc: dict, gust: dict) -> tuple[dict, list[dict]]:
    d, case, prof, nom = m["d"], m["case"], m["prof"], m["nom"]
    base = json.loads((OUTPUTS / "sim_params.json").read_text(encoding="utf-8"))
    tm = json.loads(BU.TURBULENCE.read_text(encoding="utf-8"))["component_A_mesoscale_convective_vertical_wind"]
    sim_v = VFN.simulator_parameters(c)
    sim_v["max_airspeed_m_s"] = max_airspeed(d, nom)
    _write(VAR / "vesper_for_simulator.json", json.dumps(sim_v, indent=1))
    fake = TMP / "root"                                     # venus_sim_params.build reads its vehicle block from ROOT
    (fake / "04_Venus" / "outputs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(VAR / "vesper_for_simulator.json", fake / "04_Venus" / "outputs" / "vesper_for_simulator.json")
    with mock.patch.object(SP, "ROOT", fake):
        new = SP.build()
    new["generated_by"] = ME
    s55 = A.state(55e3)
    W = d.gross_kg * s55.g
    eta = d.system.drive_efficiency
    lag = tm["lagrangian_time_scale"]
    gv = new["atmosphere_and_wind"]["vertical_gust_correlation"]
    gv.update(value=float(lag["value"]), tag="K",
              source=f"{lag['source']} Tag in venus_turbulence_model.json: {lag['tag']}. Lagrangian time; flying through the "
                     f"cells at airspeed V the effective time is 1/tau = 1/1500 s + V/5000 m "
                     f"({BU.correlation_time(case['loiter_speed_m_s']):.0f} s at {case['loiter_speed_m_s']:.1f} m/s).")
    lim = {x["name"]: x for x in new["limits"]}
    lim["max airspeed"].update(value=sim_v["max_airspeed_m_s"], tag="K/Y",
                               source=lim["max airspeed"]["source"] + ", with nominal interaction (ratio held at its 20 m/s "
                                                                      "value above the last trimmed curve point)")
    lim["science dive floor"].update(value=prof.dive_km, tag="K",
                                     source=f"battery {case['T_peak_before_sunset_C']:.1f} degC peak after the 5 min hold at "
                                            f"{prof.dive_km:.0f} km at 1.5 m/s down (venus_budget_update.fly)")
    n_par = BU.pack(d)[0]
    new["limits"] += [
        {"name": "dive abort battery temperature", **SP.v(prof.dive_abort_C, "degC", "K/Y", "doc 25 §0: 50 -> 52 degC, the 5 min hold at 52 km at 1.5 m/s needs it; venus_budget_update.Profile")},
        {"name": "release sun height, minimum cos z", **SP.v(RELEASE_MIN_MU0, "-", "K/Y", "doc 25 §0: 52.7 A at cos z 0.68 against the 2C limit; simulator at 43.66 kg, not rerun at 44.63 kg")},
        {"name": "release rotor speed, maximum", **SP.v(float(round(RELEASE_RPM_RATIO * d.hover.rpm)), "rpm", "K", "doc 25 §5.2: 1.30 x hover rpm, back-EMF cap")},
        {"name": "descent to cruise", **SP.v({"down_m_s": prof.down_rate, "forward_m_s": prof.down_speed}, "m/s", "K/Y", "doc 25 §5.2: outside the vortex-ring band; venus_budget_update.Profile")},
        {"name": "battery discharge current 2C", **SP.v(round(d.req.battery.max_C_rate * BU.CELL_AH * n_par, 1), "A", "K/Y", f"14S{n_par}P pack (venus_budget_update.pack at {d.battery_Wh:.0f} Wh); 2C is an aerokit input, not a measured limit")},
    ]
    t_lost = BU.event(case["_flight"], "array no longer carries loiter")
    t_dive = BU.event(case["_flight"], "sunset dive starts")
    w_ep = 3.0                                              # same speed the baseline's +1.4 kW was written for
    fm = {f["name"]: f for f in new["failure_modes"]}
    fm["downdraft"]["effect"] = f"+{CT.downdraft_hold_power(W, w_ep, eta) / 1e3:.1f} kW to hold altitude"
    fm["downdraft"]["recovery"] = (f"ride it within {prof.dive_km:.0f}-58 km, climb back "
                                   f"({CT.downdraft_ride_energy(W, 2900.0, eta) / 3.6e6:.1f} kWh)")
    fm["battery hot"]["trigger"] = f"interior > {prof.dive_abort_C:.0f} degC during a dive"
    fm["sun too low"]["trigger"] = f"cos zenith < {case['mu0_loiter']:.3f} at 55 km"
    fm["sun too low"]["effect"] = f"battery drains, up to ~{t_dive['p_need_W'] - t_dive['p_sun_W']:.0f} W before the sunset dive"
    fm["sun too low"]["recovery"] = f"~{t_dive['t_h'] - t_lost['t_h']:.1f} h on battery, then sunset dive"
    fm["night"]["effect"] = (f"0 W solar; {d.battery_Wh / 1e3:.2f} kWh vs ~{case['night_need_kWh']:.0f} kWh needed "
                             "(loiter power x half the 154 h air-mass day)")
    fm["acid degradation"]["recovery"] = f"mission ends at ~{case['flight_h']:.0f} h anyway"
    changes = mark_sim(base, new)
    return new, changes


def mark_sim(base: dict, new: dict) -> list[dict]:
    """Every value that differs from the baseline: old value, new value, tag, source. Scalars carry it in ``source``."""
    out: list[dict] = []

    def rec(path: str, old, val, unit, tag, source) -> None:
        out.append({"path": path, "old": old, "new": val, "unit": unit, "tag": tag, "source": source})

    def walk(o, n, path: str) -> None:
        if path in SERIES_PATHS:
            if o != n:
                rec(path, f"{len(o)} rows", f"{len(n)} rows", "table", "K", "rebuilt for the variant; rows in sim_params.json")
            return
        if isinstance(n, dict) and "value" in n and "unit" in n:
            old = None if o is None else o.get("value")
            if o is None or old != n["value"]:
                tag, why = SIM_WHY.get(path, (n["tag"], None))
                n["tag"] = tag
                base_src = why if why else (n["source"] if path.startswith(("limits", "atmosphere")) else f"{n['source']}; {CLOSURE}")
                n["source"] = f"{base_src} [v0.7: {'new row' if o is None else f'was {json.dumps(old, ensure_ascii=False)} in v0.6'}]"
                rec(path, old, n["value"], n["unit"], n["tag"], n["source"])
            return
        if isinstance(n, dict):
            for k in n:
                walk((o or {}).get(k), n[k], f"{path}.{k}" if path else k)
        elif isinstance(n, list) and n and isinstance(n[0], dict) and "name" in n[0]:
            om = {x["name"]: x for x in (o or [])}
            for x in n:
                walk(om.get(x["name"]), x, f"{path}[{x['name']}]")
        elif o != n and path not in ("version", "generated_by", "generated_at"):
            rec(path, o, n, "-", "K", f"recomputed for the variant ({ME})")

    walk(base, new, "")
    return out


SIM_NOTE = """## v0.7 variant note (44.63 kg, not confirmed)

This file is the **variant** of `outputs/sim_params_README.md`. The baseline `outputs/sim_params.json` is still v0.6
(43.66 kg, 80 s gust). Same schema and same keys; five rows are added to `limits`. Regenerate: `{me}`. Do not use
`python 04_Venus/scripts/venus_sim_params.py` for it: that script writes the baseline.

- **Vertical gust correlation is 1500 s, not 80 s.** It is the Lagrangian 1/e time of the VEGA vertical wind
  (`research/data/venus_turbulence_model.json`, component A). A vehicle that moves through the cells sees a shorter
  time: 1/τ = 1/1500 s + V/5000 m, {tau:.0f} s at {v:.1f} m/s. The 75.5 s VEGA sampling does not resolve periods under about
  150 s; the Dryden component C in the same file covers those. The 80 s value is withdrawn, it was an assumption.
- **Do not count interaction twice.** `vehicle.rotors.curve_at_55km` is an isolated rotor (factor 1.05), so the simulator
  adds its own wake model. `hover_electric_55km` and `loiter_electric_55km` already include nominal interaction; use them
  as reference values only.
- `max airspeed` holds the interaction ratio at its 20 m/s value above the last trimmed curve point.
- The simulator has not flown this mass. Pull-out current (52.7 A at cos z 0.68), canopy clearance and motor-out numbers
  in doc 25 were run at 43.66 kg.

Each changed scalar carries its old value in `source` as `[v0.7: was …]`. The full list is `sim_params_changes.json`.

| Value | Old | New | Unit | Tag | Source |
|---|---|---|---|---|---|
"""


def fmt(x) -> str:
    if isinstance(x, float):
        return f"{x:.6g}"
    s = json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x
    return (s if len(s) <= 90 else s[:87] + "…").replace("|", "\\|")


def sim_readme(changes: list[dict], m: dict) -> str:
    text = (OUTPUTS / "sim_params_README.md").read_text(encoding="utf-8")
    note = SIM_NOTE.format(me=ME, tau=BU.correlation_time(m["case"]["loiter_speed_m_s"]), v=m["case"]["loiter_speed_m_s"])
    note += "\n".join(f"| `{c['path']}` | {fmt(c['old'])} | {fmt(c['new'])} | {c['unit']} | {c['tag']} | {fmt(c['source'])} |"
                      for c in changes)
    head, sep, rest = text.partition("## Value format")
    return head.replace("Regenerate: `python 04_Venus/scripts/venus_sim_params.py` (needs `PYTHONPATH=src`). ", "") + note + "\n\n" + sep + rest


# ---------------------------------------------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------------------------------------------

BRIEFS = """## Figure briefs (written before drawing)

Set: `vesper.seti.json` copied from the baseline, so colours, axes and margins stay those of F1–F15. Reader: mixed jury.
Target: `sunum-tam`. Each brief gives the message; form and data are the baseline figure's unless stated.

- **F2.** Power with interaction leaves the array a smaller margin; loiter sits at 1.62 kW at 55 km.
- **F3.** One more kilogram of vehicle does not move the entry: still 56 g.
- **F4.** The added mass is mostly battery, motors and the 20 % contingency on them. Thermal joins the "other" bar.
- **F6.** The mission now starts at 61 km and ends at 50.4 km at the 60 °C limit. The altitude axis is set for that range.
- **F7.** Trade shape stays; every point carries the interaction, so the sun threshold is higher.
- **F9, F10.** Sensitivities and rotor choices re-flown with interaction and the 6 Nov profile.
- **F12.** Pull-out loss barely changes with mass.
- **F13.** The sun window shrinks against the higher loiter line.
- **F14.** The fall starts at 50.4 km, not 47.3 km.
- **F15.** Thrust against gust peak is the tightest flight margin with the 1500 s gust.
"""


def _f6(fig) -> None:
    """``venus_final`` fixes the altitude axis at 45-57 km for a mission at 55 km; this one starts at 61 km."""
    alt, pw = fig.axes[0], fig.axes[1]
    alt.set_ylim(49, 62)
    alt.set_yticks([50, 55, 60])
    pw.set_yticks(range(0, int(pw.get_ylim()[1]) + 1, 2))


def _f7(fig) -> None:
    """Same x range in both panels: the right one ends at 2.3 m because below that the array never carries loiter."""
    fig.axes[1].set_xlim(fig.axes[0].get_xlim())


def _f12(fig) -> None:
    """The end label of the forward-flight curve touched the dotted curve (also in the baseline)."""
    label = next(t for t in fig.axes[0].texts if t.get_text() == "Pull-out in forward flight")
    del label._dw_uc                    # takes it out of the spacing pass that dw.cila runs at save time
    label.set_y(0.925)


def _f13(fig) -> None:
    """A grid line ran through the note (also in the baseline): the note gets the panel colour behind it."""
    ax = fig.axes[1]
    note = next(t for t in ax.texts if t.get_text().startswith("airframe drag"))
    note.set_bbox({"facecolor": ax.get_facecolor(), "edgecolor": "none", "pad": 1.5})


TWEAKS = {"F6_mission": _f6, "F7_trade": _f7, "F12_deployment_monte_carlo": _f12, "F13_day_and_station_keeping": _f13}


def draw(c: dict) -> None:
    """``venus_final.figures`` with the fixes above applied just before each save, and F4 kept to 11 bars.

    F4: thermal is 0.902 kg here, over the 0.9 kg cut of the baseline code. A twelfth bar makes ``dw.ciz.cubuk`` drop the
    smallest one and print a note, so thermal joins the "other" bar."""
    import datawiz as dw

    save, bars = dw.Seti.kaydet, dw.ciz.cubuk

    def kaydet(self, fig, yol, *a, **k):
        TWEAKS.get(Path(yol).name, lambda f: None)(fig)
        return save(self, fig, yol, *a, **k)

    def cubuk(ax, names, values, **k):
        items = dict(zip(names, values, strict=True))
        other = next(n for n in items if n.startswith("other:"))
        items["other: thermal, " + other.removeprefix("other: ")] = items.pop(other) + items.pop("thermal")
        return bars(ax, list(items), list(items.values()), **k)

    with mock.patch.object(dw.Seti, "kaydet", kaydet), mock.patch.object(dw.ciz, "cubuk", cubuk):
        VFN.figures(c)


def figure_status() -> dict:
    rows = {}
    for p in sorted(OUTPUTS.glob("F*.png"), key=lambda q: int(re.match(r"F(\d+)", q.name).group(1))):
        v = VAR / p.name
        audit = VAR / (p.stem + ".denetim.txt")
        rec = {"regenerated": v.is_file()}
        if v.is_file():
            head = audit.read_text(encoding="utf-8").splitlines()[0]
            rec.update(audit=head, hata=int(re.search(r"(\d+) HATA", head).group(1)),
                       same_pixels_as_baseline=hashlib.sha256(v.read_bytes()).digest() == hashlib.sha256(p.read_bytes()).digest())
        rows[p.stem] = rec
    return rows


# ---------------------------------------------------------------------------------------------------------------
# CHANGES.md
# ---------------------------------------------------------------------------------------------------------------

def leaf_diff(o, n, path: str = "") -> list[tuple[str, object, object]]:
    if path in SERIES_PATHS:
        return [] if o == n else [(path, f"{len(o)} rows", f"{len(n)} rows")]
    if isinstance(o, dict) and isinstance(n, dict):
        rows = []
        for k in n:
            rows += leaf_diff(o.get(k), n[k], f"{path}.{k}" if path else k)
        return rows
    if isinstance(o, list) and isinstance(n, list) and len(o) == len(n):
        rows = []
        for i, (a, b) in enumerate(zip(o, n, strict=True)):
            name = b.get("id", b.get("step", i)) if isinstance(b, dict) else i
            rows += leaf_diff(a, b, f"{path}[{name}]")
        return rows
    return [] if o == n else [(path, o, n)]


def why_design(path: str) -> tuple[str, str]:
    for key, val in (("generated", ("-", "file stamp")), ("version", ("-", "this variant")), ("note", ("-", "this variant")),
                     ("vehicle.components", ("K", CLOSURE)), ("vehicle.total_mass", ("K", CLOSURE)),
                     ("vehicle.performance_55km", ("K/Y", "venus_budget_update power table, nominal interaction")),
                     ("vehicle.rotor", ("K", CLOSURE + "; blade chord follows weight at fixed C_T/σ")),
                     ("entry", ("K", "entry chain of aerokit.venus.design.baseline at the new vehicle mass")),
                     ("deployment_sequence", ("K/Y", "doc 25 §0 and §5.2; numbers from this run")),
                     ("operating_band", ("K", "doc 25 §0: floor 52 km")),
                     ("operations", ("K", "venus_budget_update.fly, nominal, 6 Nov profile"))):
        if path.startswith(key):
            return val
    return "K", ME


def mass_table(base: dict, doc: dict, budget: dict) -> list[str]:
    ob = budget["recommended_design"]["baseline_breakdown"]
    nb = budget["recommended_design"]["breakdown"]
    parts = {"rotors": ("blades+hubs", "motors", "ESCs"), "arms": ("arms+hinges",), "body": ("vessel",), "battery": ("battery",),
             "solar": ("solar",), "payload": ("payload",), "avionics": ("avionics",), "antenna": ("comms",),
             "thermal": ("thermal",), "coating": ("coating",), "attach": ("attach",), "wiring": ("wiring",),
             "contingency": ("contingency",)}
    why = {"rotors": "blades + hubs {blades+hubs:+.0f} g (chord follows weight), motors + gearboxes {motors:+.0f} g (torque and power: "
                     "weight and +3.42 % hover), ESCs {ESCs:+.0f} g",
           "battery": "0.5 h of hover at 2219 W instead of 2088 W", "body": "vessel grows 12 % of the battery mass added",
           "thermal": "6 % of the battery mass added", "wiring": "4 % of the base mass", "coating": "2 % of the base mass",
           "contingency": "20 % of everything above"}
    L = ["## Mass: which component takes each gram", "",
         "Grams from the unrounded breakdown in `variants/budget_update/result.json` (`baseline_breakdown` → `breakdown`).", "",
         "| Component | v0.6 kg | v0.7 kg | Added g | Why |", "|---|---:|---:|---:|---|"]
    ob_c = {c["id"]: c for c in base["vehicle"]["components"]}
    total_g = 0.0
    for c in doc["vehicle"]["components"]:
        keys = parts[c["id"]]
        g = 1000.0 * sum(nb[k] - ob[k] for k in keys)
        total_g += g
        text = why.get(c["id"], "no change")
        if c["id"] == "rotors":
            text = text.format(**{k: 1000.0 * (nb[k] - ob[k]) for k in keys})
        L.append(f"| {c['id']} | {sum(ob[k] for k in keys):.3f} | {c['mass_kg']:.3f} | {g:+.0f} | {text} |")
    s_new = sum(c["mass_kg"] for c in doc["vehicle"]["components"])
    s_old = sum(ob.values())
    L += [f"| **sum** | **{s_old:.3f}** | **{s_new:.3f}** | **{total_g:+.0f}** | total_mass_kg {doc['vehicle']['total_mass_kg']} |", "",
          f"The v0.6 `design.json` lists 43.651 kg against 43.66 kg because `rotors` was rounded to 6.08 kg; here it keeps three "
          f"decimals (6.353 kg), so the 13 components sum to {s_new:.3f} kg. `arms` stays 7.660 kg: the 0.8 mm minimum gauge "
          "governs the tube, not the load. Span, deck and rotor diameter do not change; blade chord does (table below).", ""]
    return L


def changes_md(base: dict, doc: dict, sim_changes: list[dict], m: dict, figs: dict, c: dict, skipped: dict) -> tuple[str, list]:
    rows = leaf_diff(base, doc)
    full = [{"path": p, "old": o, "new": n, "tag": why_design(p)[0], "source": why_design(p)[1]} for p, o, n in rows]
    out = c["out"]
    g = out["variant"]["gust"]
    gm = out["variant"]["gust_mission"]
    case = m["case"]
    L = ["# VESPER v0.7 variant: 44.63 kg, 6 Nov profile", "",
         f"**Status: variant. The team has not confirmed 44.6 kg.** Nothing in `outputs/` outside this folder changed. Written by "
         f"`{ME}` on {_dt.date.today().isoformat()}. Every number below is from that run, or read from "
         "`variants/budget_update/result.json` where the text says so.", ""]
    L += mass_table(base, doc, m["budget"])
    L += ["## Mission and margins of this variant", "",
          f"Nominal interaction: {case['flight_h']:.1f} h flight, {case['sun_h']:.1f} h on sunlight, ends at {case['lowest_km']:.1f} km "
          f"with the battery at the 60 °C limit. Loiter {case['loiter_W']:.0f} W at {case['loiter_speed_m_s']:.1f} m/s, hover "
          f"{case['hover_W']:.0f} W, sun threshold cos z {case['mu0_loiter']:.3f}. Release at cos z "
          f"{case['events'][0]['mu0']:.3f}. Pack 14S{out['variant']['pack']['parallel']}P, 2C limit {out['variant']['max_discharge_A']:.1f} A.", "",
          f"Gust model re-run at 44.63 kg and {case['loiter_speed_m_s']:.1f} m/s (doc 25 §4.7 is at 43.66 kg and 8.8 m/s): altitude RMS "
          f"{g['A_plus_C_loiter']['z_rms_m']:.1f} m, peak {g['A_plus_C_loiter']['z_peak_max_m']:.1f} m, thrust peak "
          f"{100 * g['A_plus_C_loiter']['dT_peak_max_over_W']:.1f} % W, margin "
          f"{g['thrust_margin'] / g['A_plus_C_loiter']['dT_peak_max_over_W']:.2f}×. Mission with component A held, {gm['runs']} seeds: "
          f"{gm['flight_h_p5']:.1f} / {gm['flight_h_median']:.1f} / {gm['flight_h_p95']:.1f} h (p5 / median / p95), "
          f"{gm['runs_ending_empty']} runs end empty.", ""]
    e, mc, w = out["entry"], out["deployment_mc"]["forward"], out["end_of_mission"]["windmilling"]
    gl = g["A_plus_C_loiter"]
    L += ["## Numbers that move against doc 25 when the mass is 44.63 kg", "",
          "Doc 25 quotes these for 43.66 kg, or from the simulator at 43.66 kg. Doc 25 is not edited; update it on promotion.", "",
          "| Quantity | Doc 25 | This variant |", "|---|---|---|",
          f"| Pull-out loss (1-D model) | 26 m | {e['pullout_loss_m']:.1f} m |",
          f"| Descent rate at release | 12.8 m/s | {e['release_rate']:.1f} m/s |",
          f"| Time on the parachute | 716 s | {e['chute_s']:.0f} s |",
          f"| Pull-out loss p99, Monte Carlo | 41 m | {mc['loss_p99_m']:.1f} m (maximum {mc['loss_max_m']:.1f} m) |",
          f"| Gust altitude RMS / peak | 5.9 m / 27 m | {gl['z_rms_m']:.1f} m / {gl['z_peak_max_m']:.1f} m |",
          f"| Gust thrust peak, margin | 33 % W, 1.8× | {100 * gl['dT_peak_max_over_W']:.1f} % W, "
          f"{g['thrust_margin'] / gl['dT_peak_max_over_W']:.2f}× |",
          f"| Fall to the surface, windmilling | ~12 h | {w['t_surface_h']:.1f} h, from {w['start_km']:.1f} km |", "",
          "**Not rerun at 44.63 kg:** the simulator (sunumatik). Pull-out current 52.7 A at cos z 0.68, canopy clearance 0.33 m and the "
          "motor-out result stay 43.66 kg numbers. The 2C limit is 53.6 A, so only 0.9 A separates it from the cos z 0.68 case; "
          "recheck that case at the new mass before relying on the rule. Planned release is at cos z "
          f"{case['events'][0]['mu0']:.2f}.", ""]
    L += ["## Figures", "", "| Figure | State | Audit |", "|---|---|---|"]
    for name, r in figs.items():
        if not r["regenerated"]:
            L.append(f"| {name} | not regenerated: {skipped.get(name, 'see report')} | - |")
        else:
            state = "numbers unchanged, same PNG bytes as baseline" if r["same_pixels_as_baseline"] else "regenerated"
            L.append(f"| {name} | {state} | {r['audit']} |")
    L += ["", "UYARI in F2 and F13: the pink of the set is 2.93:1 on the background, as in the baseline; the colour stays for set "
          "consistency. Save-time changes against `venus_final.py`: F4 thermal in the \"other\" bar, F6 altitude axis, F7 shared x range, "
          "F12 label moved off the dotted curve, F13 note background.", "", BRIEFS, "## design.json: every changed value", "",
          f"{len(rows)} changed leaves. `operations.events` and `operations.series_hourly` are replaced whole; their rows are in "
          "`design.json`. Same list as JSON: `changes_full.json`.", "",
          "| Path | Old | New | Tag | Source |", "|---|---|---|---|---|"]
    L += [f"| `{r['path']}` | {fmt(r['old'])} | {fmt(r['new'])} | {r['tag']} | {r['source']} |" for r in full]
    L += ["", "**Event kinds.** The visual's enum has no `other` (`tests/test_venus_system.py`), so `cruise altitude reached` is "
          "kind `release` and `array no longer carries loiter` is kind `sunset`.", "",
          "## sim_params.json: every changed value", "",
          f"{len(sim_changes)} changed values. Same list as JSON: `sim_params_changes.json`.", "",
          "| Path | Old | New | Unit | Tag | Source |", "|---|---|---|---|---|---|"]
    L += [f"| `{x['path']}` | {fmt(x['old'])} | {fmt(x['new'])} | {x['unit']} | {x['tag']} | {fmt(x['source'])} |" for x in sim_changes]
    L += ["", "@@PROMOTION@@", ""]
    return "\n".join(L), full


# ---------------------------------------------------------------------------------------------------------------
# promotion: only on the user's yes
# ---------------------------------------------------------------------------------------------------------------

PROMOTION = """## Promotion: only after the team says yes

One command, from the repo root:

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"; python 04_Venus/scripts/venus_variant_v07.py --promote --yes
```

Without `--yes` it prints the plan and writes nothing. It refuses if any baseline file differs from
`baseline_hashes_before.json`. It copies every file it will replace to
`outputs/versions/baseline_v0.6_before_v0.7_<stamp>/`, checks each copy by hash, anchors `design_v0.6_<hash>.json` as
`venus_design.py` does, copies the variant over the baseline, checks each copy by hash and writes
`promotion_manifest.json`. **It has not been run.**
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def promote(variant: Path, outputs: Path, execute: bool) -> dict:
    """Anchor every baseline file the variant replaces in ``versions/``, then copy the variant over it."""
    anchors = json.loads((variant / "baseline_hashes_before.json").read_text(encoding="utf-8"))["files"]
    files = sorted(p for p in variant.iterdir() if p.is_file() and p.name not in NOT_PROMOTED)
    moved = [p for p in sorted(outputs.iterdir()) if p.is_file() and p.name in anchors and sha(p) != anchors[p.name]]
    if moved:
        raise SystemExit("baseline changed since the variant was built, promotion refused: " + ", ".join(p.name for p in moved))
    old_design = json.loads((outputs / "design.json").read_text(encoding="utf-8"))
    if old_design["version"] == VERSION:
        raise SystemExit("baseline design.json is already v" + VERSION)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M")
    anchor_dir = outputs / "versions" / f"baseline_v{old_design['version']}_before_v{VERSION}_{stamp}"
    plan = {"anchor_dir": str(anchor_dir), "copy": [p.name for p in files],
            "replaces": [p.name for p in files if (outputs / p.name).is_file()], "execute": execute}
    if not execute:
        return plan
    anchor_dir.mkdir(parents=True)
    for name in plan["replaces"]:
        shutil.copy2(outputs / name, anchor_dir / name)
        if sha(anchor_dir / name) != sha(outputs / name):
            raise SystemExit(f"anchor copy of {name} is not identical; nothing was overwritten")
    design_text = (outputs / "design.json").read_text(encoding="utf-8")
    shutil.copy2(outputs / "design.json", outputs / "versions" /
                 f"design_v{old_design['version']}_{hashlib.sha256(design_text.encode()).hexdigest()[:8]}.json")
    for p in files:
        shutil.copy2(p, outputs / p.name)
    done = {p.name: sha(outputs / p.name) for p in files}
    if any(done[p.name] != sha(p) for p in files):
        raise SystemExit("copy check failed; restore from " + str(anchor_dir))
    plan["hashes"] = done
    (anchor_dir / "promotion_manifest.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    (variant / "PROMOTED.json").write_text(json.dumps({"anchor_dir": str(anchor_dir), "at": stamp}, indent=1), encoding="utf-8")
    return plan


# ---------------------------------------------------------------------------------------------------------------

def run_sweeps() -> int:
    ms, _ = models()
    VAR.mkdir(parents=True, exist_ok=True)
    _write(VAR / "trade_sizing.json", json.dumps(sweep_trade(ms["nominal"]), indent=1))
    _write(VAR / "sensitivity.json", json.dumps(sweep_sensitivity(ms["nominal"]), indent=1, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sweeps", action="store_true")
    ap.add_argument("--promote", action="store_true")
    ap.add_argument("--yes", action="store_true", help="with --promote: really do it")
    ap.add_argument("--reuse", action="store_true", help="figure iteration only: reuse the compute cache in D:/tmp_ideathon")
    args = ap.parse_args(argv)
    if args.promote:
        print(json.dumps(promote(VAR, OUTPUTS, args.yes), indent=1, ensure_ascii=False))
        return 0
    if args.sweeps:
        return run_sweeps()
    TMP.mkdir(parents=True, exist_ok=True)
    VAR.mkdir(parents=True, exist_ok=True)
    if not (VAR / "baseline_hashes_before.json").is_file():
        shutil.copy2(TMP / "baseline_hashes_before.json", VAR / "baseline_hashes_before.json")
    if not (VAR / "vesper.seti.json").is_file():
        shutil.copy2(OUTPUTS / "vesper.seti.json", VAR / "vesper.seti.json")
    ms, _ = models()
    m = recommended(ms)
    d = m["d"]
    res = vehicle_chain(m)
    cache = TMP / "c.pkl"
    if args.reuse and cache.is_file():
        c, gust, gust_mc = pickle.loads(cache.read_bytes())
        res = c["res"]
    else:
        gust = BU.gust_study(d, m["case"]["loiter_speed_m_s"])
        gust_mc = BU.gust_mission(d, m["tab"], m["prof"], m["case"]["release_hour_angle_deg"], m["case"]["sunset_horizon_h"],
                                  m["case"]["loiter_speed_m_s"])
        with patched(res):
            c = VFN.compute()
        cache.write_bytes(pickle.dumps((c, gust, gust_mc)))
    corrected(c, m, gust, gust_mc)
    sweeps = {k: VAR / f for k, f in (("trade", "trade_sizing.json"), ("sens", "sensitivity.json"))}
    for k, f in sweeps.items():              # never the baseline sweeps: they are isolated-rotor numbers
        c[k] = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else None
    with patched(res):
        doc = design_doc(c, m, res)
    _write(VAR / "design.json", json.dumps(doc, indent=1, ensure_ascii=False))
    with patched(res, doc):
        sim, sim_changes = sim_doc(c, m, doc, gust)
        draw(c)
    _write(VAR / "sim_params.json", json.dumps(sim, indent=1, ensure_ascii=False))
    _write(VAR / "sim_params_changes.json", json.dumps(sim_changes, indent=1, ensure_ascii=False))
    _write(VAR / "sim_params_README.md", sim_readme(sim_changes, m))
    _write(VAR / "result.json", json.dumps(c["out"], indent=1, default=float, ensure_ascii=False))
    _write(VAR / "result.md", f"Variant v{VERSION}, not confirmed. Written by `{ME}`, not by the command in the title.\n\n"
           + VFN.markdown(c["out"]))
    figs = figure_status()
    _write(VAR / "figures_status.json", json.dumps(figs, indent=1, ensure_ascii=False))
    base = json.loads((OUTPUTS / "design.json").read_text(encoding="utf-8"))
    text, full = changes_md(base, doc, sim_changes, m, figs, c,
                            {"F7_trade": "no variant trade_sizing.json", "F9_sensitivity": "no variant sensitivity.json",
                             "F10_robustness": "no variant sensitivity.json"})
    _write(VAR / "changes_full.json", json.dumps(full, indent=1, ensure_ascii=False, default=float))
    _write(VAR / "CHANGES.md", text.replace("@@PROMOTION@@", PROMOTION))
    n_err = sum(r.get("hata", 0) for r in figs.values())
    print(f"v{doc['version']} {doc['vehicle']['total_mass_kg']} kg; components sum "
          f"{sum(x['mass_kg'] for x in doc['vehicle']['components']):.3f} kg; "
          f"{sum(r['regenerated'] for r in figs.values())} figures, {n_err} HATA")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
