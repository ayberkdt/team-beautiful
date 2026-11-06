"""VESPER budget update, 6 Nov 2026: rotor-rotor interaction, the VEGA gust time scale and the flyable descent profile.

    python 04_Venus/scripts/venus_budget_update.py
    python 04_Venus/scripts/venus_budget_update.py --no-figures --curves <file>

Reads ``guc_egrisi.json`` (simulator power vs speed at 51/53/55/58 km for interaction off/low/nominal/high) and writes
``04_Venus/outputs/variants/budget_update/`` (``result.json``, ``result.md``, figures). The baseline hand-off files
(``design.json``, ``result.json``, ``sim_params.json``) are read only. ``aerokit`` itself is not changed: the
interaction is applied here, as a ratio on aerokit's isolated-rotor power, so that ``off`` at 55 km stays doc 25.

**Power model.** Level flight at altitude h, speed V: ``P = P_iso(V, h) * F(V, h) * G(V, h) / eta + P_sys``.
``P_iso`` is :func:`aerokit.venus.performance.forward_power`. ``F`` = simulator shaft power with / without interaction
(the file). ``G`` = 1 at 55 km; below it the simulator holds 514 rpm where aerokit trims rpm down, so G carries the
simulator's extra profile power into the budget. Rows with ``trim_ok`` false are never used. Descent and climb cannot
come from a level curve; they use the 6-DOF points in ``sim_runs/sim_points.json``.

**Mission.** :func:`fly` is ``aerokit.venus_flight.simulate_rotorcraft_day`` with four additions: release at 61 km,
a descent profile separate from the climb, pack resistance (I2R) and a 0.5 C charge limit taken from the simulator.
``Profile.legacy()`` switches all of them off and must return doc 25's 49.18 h / 44.18 h (test).

**Gusts.** :func:`gust_model` is the linear altitude-hold loop of ``aerokit.venus.control.gust_response`` driven by the
data-book model (component A: Ornstein-Uhlenbeck, 1500 s Lagrangian; component C: Dryden). RMS values are exact
(Lyapunov equation); peaks come from seeded runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import bemt as B  # noqa: E402
from aerokit.venus import control as CT  # noqa: E402
from aerokit.venus import descent as DS  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import entry as EN  # noqa: E402
from aerokit.venus import performance as F  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import sizing as S  # noqa: E402
from aerokit.venus import thermal as TH  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs" / "variants" / "budget_update"
SIM_DIR = Path(r"D:\Custom Yetenekler\sunumatik\.claude\worktrees\venus-rotorcraft-visual-44d0d1"
               r"\presets\venus_rotorcraft\sim")
CURVES = SIM_DIR / "guc_egrisi.json"
TURBULENCE = ROOT / "04_Venus" / "research" / "data" / "venus_turbulence_model.json"
CASES = ("off", "low", "nominal", "high")
V_GRID = np.arange(0.0, 25.01, 0.1)
BASE_FACTOR = 1.05                      # RotorSystem.bemt_power_factor, doc 25 §4.2

# 6-DOF points, read-only runs of the refitted simulator (raw logs and runners in <OUT>/sim_runs/)
SIM_POINTS_FILE = "sim_points.json"

# Li-ion pack as in the simulator (venus-guc.mjs): OCV vs usable state of charge, 14S, 35 mΩ cells [Y]
OCV_SOC = np.array([0, .05, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0])
OCV_V = 14.0 * np.array([3.30, 3.40, 3.46, 3.55, 3.61, 3.67, 3.73, 3.80, 3.87, 3.95, 4.03, 4.12])
CELL_AH, CELL_R, SERIES = 3.35, 0.035, 14

# Mission closure rules [Y]
SOC_FLOOR = 0.20          # lowest state of charge allowed before the sunset dive
RESERVE_HOVER_H = 0.5     # doc 25 sizing rule: battery covers this much hover with no sun
T_DISCHARGE_C = 60.0
RECOMMENDED = "re-closed, 0.10 m gap"


# ---------------------------------------------------------------------------------------------------------------
# interaction curves
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Interaction:
    """Shaft-power ratios on an (altitude, speed) grid: ``F`` with/without interaction, ``G`` simulator rpm schedule."""

    name: str
    km: tuple[float, ...]
    V: tuple[tuple[float, ...], ...]          # valid speeds per altitude (trim_ok rows only)
    F: tuple[tuple[float, ...], ...]
    G: tuple[tuple[float, ...], ...] | None = None
    clearance_m: float = 0.10
    credit: float = 1.0                       # share of W V_d / eta returned in the descent (sim_points)
    climb_k: float = 1.0                      # climb power over W V_c / eta (sim_points)
    v_h55: float = 2.59                       # baseline v_h at 55 km: other vehicles are read at equal V/v_h [Y]

    def _grid(self, table, V: np.ndarray, km: float) -> np.ndarray:
        rows = np.array([np.interp(V, v, t) for v, t in zip(self.V, table, strict=True)])
        x = min(max(km, self.km[0]), self.km[-1])
        i = min(max(int(np.searchsorted(self.km, x)) - 1, 0), len(self.km) - 2)
        w = (x - self.km[i]) / (self.km[i + 1] - self.km[i])
        return (1.0 - w) * rows[i] + w * rows[i + 1]

    def factor(self, V, km: float, v_scale: float = 1.0) -> np.ndarray:
        """Total ratio on aerokit's isolated power at ``km``; ``v_scale`` = v_h(baseline) / v_h(this vehicle)."""
        Vq = np.asarray(V, float) * v_scale
        f = self._grid(self.F, Vq, km)
        if abs(self.clearance_m - 0.10) > 1e-9:
            f = 1.0 + (f - 1.0) * spacing_scale(self.clearance_m, Vq)
        return f if self.G is None else f * self._grid(self.G, Vq, km)

    def hover_ratio(self) -> float:
        return float(self._grid(self.F, np.array([0.0]), 55.0)[0])


def sim_points(folder: Path | None = None) -> dict:
    return json.loads(((folder or OUT / "sim_runs") / SIM_POINTS_FILE).read_text(encoding="utf-8"))


_PTS: dict = {}


def _points() -> dict:
    if not _PTS:
        _PTS.update(sim_points())
    return _PTS


def spacing_scale(c: float, V, pts: dict | None = None) -> np.ndarray:
    """Interaction at clearance ``c`` over interaction at 0.10 m (simulator sweep, interpolated in c and V)."""
    sp = (pts or _points())["spacing"]
    cs = sorted(float(k) for k in sp["nominal_shaft_W"])
    Vs = sp["V"]
    iso = np.array(sp["isolated_shaft_W"])
    excess = np.array([np.array(sp["nominal_shaft_W"][f"{ci:.2f}"]) / iso - 1.0 for ci in cs])
    table = excess / excess[0]
    col = np.array([np.interp(c, cs, table[:, j]) for j in range(len(Vs))])
    return np.interp(np.asarray(V, float), Vs, col)


def proximity_f(D: float, clearance: float, A0: float = 0.0137) -> float:
    """Hover proximity loss of one rotor of a hexacopter: sum of A exp(-g/0.6) over the five others, g = tip gap / D.

    Same law as the simulator (Yoon, Lee & Pulliam 2016 trend, extrapolated below 0.3 D [Y])."""
    arm = D + clearance
    dists = (arm, arm, math.sqrt(3.0) * arm, math.sqrt(3.0) * arm, 2.0 * arm)
    return sum(A0 * math.exp(-((x - D) / D) / 0.6) for x in dists)


def read_curves(raw: dict) -> dict:
    """{km: {case: [valid rows]}} from ``guc_egrisi.json``; a row is valid only if its ``trim_ok`` is true."""
    if raw.get("schema") != "vesper_guc_egrisi/1":
        raise ValueError(f"unexpected schema {raw.get('schema')!r}")
    out: dict[float, dict[str, list[dict]]] = {}
    for key, cases in raw["egri"].items():
        km = float(key.split("_")[0])
        out[km] = {c: [r for r in cases[c] if r["trim_ok"]] for c in CASES}
    return out


def build_models(raw: dict, d: S.Design, pts: dict | None = None) -> dict[str, Interaction]:
    """One :class:`Interaction` per case. ``d`` is the baseline design the simulator flew (for ``G``)."""
    pts = pts or _points()
    cur = read_curves(raw)
    kms = tuple(sorted(cur))
    sys0 = isolated_system(d)
    iso: dict[float, dict[float, float]] = {}
    for km in kms:
        st = A.state(km * 1e3)
        fl = B.FlowState(st.rho, st.mu, st.a)
        W = d.gross_kg * st.g
        iso[km] = {float(r["V"]): F.forward_power(sys0, W, fl, float(r["V"])) for r in cur[km]["off"]}
    off55 = {float(r["V"]): r["shaft_W"] for r in cur[55.0]["off"]}
    models = {}
    for case in CASES:
        Vs, Fs, Gs = [], [], []
        for km in kms:
            on = {float(r["V"]): r["shaft_W"] for r in cur[km][case]}
            off = {float(r["V"]): r["shaft_W"] for r in cur[km]["off"]}
            v = sorted(set(on) & set(off) & set(off55))
            Vs.append(tuple(v))
            Fs.append(tuple(on[x] / off[x] for x in v))
            Gs.append(tuple((off[x] / iso[km][x]) / (off55[x] / iso[55.0][x]) for x in v))
        models[case] = Interaction(case, kms, tuple(Vs), tuple(Fs), tuple(Gs),
                                   credit=pts["descent_credit"][case], climb_k=pts["climb_k"][case])
    return models


# ---------------------------------------------------------------------------------------------------------------
# power table
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Profile:
    """How the vehicle flies. ``legacy`` reproduces doc 25 (release at cruise, 3 m/s both ways, ideal battery)."""

    start_km: float = 61.0
    down_rate: float = 1.5
    down_speed: float = 3.5
    up_rate: float = 3.0
    dive_km: float = 52.0
    hold_s: float = 300.0
    dive_times_h: tuple[float, ...] = (6.0, 20.0)
    dive_abort_C: float = 52.0       # doc 25: 50 °C at 51 km; at 1.5 m/s the 5 min hold at 52 km needs 52 °C
    sunset_horizon_h: float = 1.6
    pack_model: bool = True
    calibrated: bool = True          # descent and climb from sim_points; False = aerokit (no credit, W V / η)
    label: str = "6 Nov"

    @staticmethod
    def legacy() -> Profile:
        return Profile(start_km=55.0, down_rate=3.0, down_speed=7.8, dive_km=51.0, dive_abort_C=50.0,
                       sunset_horizon_h=0.9, pack_model=False, calibrated=False, label="doc 25")


@dataclass
class PowerTable:
    km: np.ndarray
    level_W: np.ndarray       # rotors only, electric, at the best speed
    v_best: np.ndarray
    down_W: np.ndarray        # rotors only, electric, flying the descent profile
    climb_W_per_ms: np.ndarray
    hover_W: np.ndarray
    v_h: np.ndarray

    def at(self, arr: np.ndarray, z: float) -> float:
        return float(np.interp(z / 1e3, self.km, arr))


def isolated_system(d: S.Design) -> F.RotorSystem:
    return replace(d.system, bemt_power_factor=BASE_FACTOR)


_ISO_CACHE: dict[tuple, dict] = {}


def isolated_table(d: S.Design, step_km: float = 0.25) -> dict:
    """BEMT hover at each altitude and the isolated-rotor power over :data:`V_GRID` (slow part, cached per design)."""
    key = (round(d.gross_kg, 6), d.D, d.req.clearance_m, d.req.altitude_m, step_km)
    if key not in _ISO_CACHE:
        sys0 = isolated_system(d)
        kms = np.arange(45.0, 62.01, step_km)
        rows, vh, Ws = [], [], []
        for km in kms:
            st = A.state(km * 1e3)
            fl = B.FlowState(st.rho, st.mu, st.a)
            W = d.gross_kg * st.g
            hp = F.hover(sys0, W, fl)
            vi = np.sqrt((-V_GRID ** 2 + np.sqrt(V_GRID ** 4 + 4.0 * hp.v_h ** 4)) / 2.0)       # = F.forward_power
            mu = V_GRID / hp.per_rotor.tip_speed
            rows.append(hp.kappa * W * vi + hp.profile_W * (1.0 + 4.65 * mu * mu)
                        + 0.5 * fl.rho * V_GRID ** 3 * sys0.drag_area_m2)
            vh.append(hp.v_h)
            Ws.append(W)
        _ISO_CACHE[key] = {"km": kms, "iso": np.array(rows), "vh": np.array(vh), "W": np.array(Ws)}
    return _ISO_CACHE[key]


def power_table(d: S.Design, im: Interaction | None, prof: Profile, step_km: float = 0.25) -> PowerTable:
    eta = isolated_system(d).drive_efficiency
    base = isolated_table(d, step_km)
    cols: dict[str, list[float]] = {k: [] for k in ("lv", "vb", "dn", "cl", "hv")}
    j = int(np.argmin(abs(V_GRID - prof.down_speed)))
    v55 = float(np.interp(55.0, base["km"], base["vh"]))
    for km, iso, W in zip(base["km"], base["iso"], base["W"], strict=True):
        shaft = iso if im is None else iso * im.factor(V_GRID, float(km), im.v_h55 / v55)
        i = int(np.argmin(shaft))
        cols["lv"].append(shaft[i] / eta)
        cols["vb"].append(float(V_GRID[i]))
        cols["hv"].append(float(shaft[0]) / eta)
        if prof.calibrated and im is not None:
            cols["dn"].append(max(shaft[j] / eta - im.credit * W * prof.down_rate / eta, 0.0))
            cols["cl"].append(im.climb_k * W / eta)
        else:
            cols["dn"].append(shaft[i] / eta)
            cols["cl"].append(W / eta)
    return PowerTable(base["km"], *(np.array(cols[k]) for k in ("lv", "vb", "dn", "cl", "hv")), base["vh"])


# ---------------------------------------------------------------------------------------------------------------
# mission
# ---------------------------------------------------------------------------------------------------------------

@dataclass
class Flight:
    t: np.ndarray
    z: np.ndarray
    mu0: np.ndarray
    p_need: np.ndarray
    p_sun: np.ndarray
    soc: np.ndarray
    T_int: np.ndarray
    events: list[dict] = field(default_factory=list)
    flight_h: float = 0.0
    sun_h: float = 0.0
    drift_km: float = 0.0
    end_reason: str = ""


def pack(d: S.Design) -> tuple[int, float, float]:
    """(parallel strings, pack resistance Ω, 0.5 C charge current A) sized like the simulator."""
    mean_ocv = float(np.mean(np.interp((np.arange(200) + 0.5) / 200, OCV_SOC, OCV_V)))
    parallel = math.ceil(d.battery_Wh / mean_ocv / (CELL_AH * d.req.battery.usable_dod))
    return parallel, SERIES * CELL_R / parallel, 0.5 * CELL_AH * parallel


def battery_step(P_bat: float, soc: float, cap: float, R: float, I_max: float, dt: float) -> float:
    """New state of charge after ``dt`` s at terminal power ``P_bat`` [W] (+ discharge), with I²R and a charge limit."""
    ocv = float(np.interp(soc, OCV_SOC, OCV_V))
    if P_bat >= 0.0:
        disc = ocv * ocv - 4.0 * R * P_bat
        current = ocv / (2.0 * R) if disc <= 0.0 else (ocv - math.sqrt(disc)) / (2.0 * R)
        chem = ocv * current
    else:
        current = min(-P_bat / ocv, I_max)
        chem = -(ocv * current - current * current * R)
    return soc - chem * dt / 3600.0 / cap


def fly(d: S.Design, tab: PowerTable, prof: Profile, H0_deg: float, dt: float = 60.0, cruise_km: float | None = None,
        w_hold: np.ndarray | None = None, latitude_deg: float = 0.0, max_days: float = 7.0, soc0: float = 1.0,
        T0_C: float | None = None, stop_h: float | None = None) -> Flight:
    """Fly from release until the battery is empty or too hot. See the module docstring.

    ``w_hold``: vertical air speed [m/s, + up] per step, held against by the rotors (gust Monte Carlo)."""
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    batt, cap = d.req.battery, d.battery_Wh
    vessel = TH.Vessel()
    eta, m, P_sys = d.system.drive_efficiency, d.gross_kg, d.P_sys_W
    cruise = (cruise_km if cruise_km is not None else d.req.altitude_m / 1e3) * 1e3
    z = prof.start_km * 1e3
    st0 = A.state(z)
    Ts = st0.T
    Ti = st0.T if prof.start_km * 1e3 <= cruise else 273.15 + 25.0     # vessel kept near 25 °C on the way down [Y]
    if T0_C is not None:
        Ti = T0_C + 273.15
    period = PW.air_mass_day_s(A.zonal_wind(cruise), cruise)
    H = math.radians(H0_deg)
    _, R, I_chg = pack(d)
    soc = soc0
    rec: dict[str, list[float]] = {k: [] for k in ("t", "z", "mu", "pn", "ps", "soc", "Ti")}
    events: list[dict] = []
    t = x = sustained = 0.0
    state = {"cruise_seen": z <= cruise, "sun_lost": False, "min_after": None}
    dive_plan = [(h * 3600.0, prof.dive_km, prof.hold_s) for h in prof.dive_times_h]
    dive_idx, target, hold_until, final = 0, cruise, None, False
    end = ""

    def note(name: str) -> None:
        events.append({"t_h": t / 3600.0, "event": name, "z_km": z / 1e3, "soc": soc, "T_C": Ti - 273.15,
                       "mu0": math.cos(H), "p_need_W": rec["pn"][-1] if rec["pn"] else None,
                       "p_sun_W": rec["ps"][-1] if rec["ps"] else None})

    note(f"release at {z / 1e3:.1f} km")
    step = 0
    while t < (max_days * 86400.0 if stop_h is None else stop_h * 3600.0):
        zc = min(max(z, A.Z_MIN), A.Z_MAX)
        st = A.state(zc)
        mu0 = math.cos(math.radians(latitude_deg)) * math.cos(H)
        p_sun = arr.power(zc, mu0) if mu0 > 0 else 0.0
        if not state["cruise_seen"] and z <= cruise + 1.0:
            state["cruise_seen"] = True
            note("cruise altitude reached")
        if not final and state["cruise_seen"] and dive_idx < len(dive_plan) and t >= dive_plan[dive_idx][0] \
                and target == cruise:
            target = dive_plan[dive_idx][1] * 1e3
            note(f"science dive {dive_idx + 1} starts")
        down = prof.down_rate
        if not final and target != cruise and abs(z - target) <= max(down, prof.up_rate) * dt:
            if hold_until is None:
                hold_until = t + dive_plan[dive_idx][2]
                note(f"science dive {dive_idx + 1} bottom")
            elif t >= hold_until:
                target, hold_until = cruise, None
                dive_idx += 1
                note("climb back to cruise")
                state["min_after"] = dive_idx
        if not final and target < cruise and Ti - 273.15 > prof.dive_abort_C:
            target, hold_until = cruise, None
            dive_idx += 1
            note(f"dive aborted: battery above {prof.dive_abort_C:.0f} °C")
            state["min_after"] = dive_idx
        p_level = tab.at(tab.level_W, z)
        afternoon = math.sin(H) > 0.0
        deficit = p_level + P_sys - p_sun
        if afternoon and deficit > 0.0 and not state["sun_lost"] and target == cruise and state["cruise_seen"]:
            state["sun_lost"] = True
            note("array no longer carries loiter")
        if not final and afternoon and deficit > 0.0 and target == cruise and abs(z - cruise) < 1.0 \
                and soc * cap < deficit * prof.sunset_horizon_h:
            final = True
            target = A.Z_MIN + 500.0
            note("sunset dive starts")
        rate = down if target < z else prof.up_rate
        vz = (target - z) / dt if abs(target - z) <= rate * dt else math.copysign(rate, target - z)
        if vz < -0.01:
            p_rotor = tab.at(tab.down_W, z)
        else:
            p_rotor = p_level + tab.at(tab.climb_W_per_ms, z) * max(vz, 0.0)
        p_need = p_rotor + P_sys
        if w_hold is not None and step < len(w_hold) and abs(vz) < 0.01:
            p_need = max(p_need - m * st.g * float(w_hold[step]) / eta, P_sys)
        net = p_sun - p_need
        if net > 0.0 and not batt.can_charge(Ti - 273.15):
            net = 0.0
        if p_sun >= p_need:
            sustained += dt
        if prof.pack_model:
            soc = min(1.0, battery_step(-net, soc, cap, R, I_chg, dt))
        else:
            soc = min(1.0, soc + net * dt / 3600.0 / cap)
        internal = P_sys * 0.8 + 0.03 * p_need
        h_c = TH.convection_coefficient(8.0, vessel.diameter_m, st.T, st.rho)
        for _ in range(6):
            q_i = internal - TH.conductance(vessel, Ti, Ts) * (Ti - Ts)
            q_s = TH._shell_balance(vessel, Ts, Ti, st.T, h_c, 0.0)
            Ti += q_i * dt / 6 / vessel.interior_heat_capacity_J_K
            Ts += q_s * dt / 6 / vessel.shell_heat_capacity_J_K
        for k, v in (("t", t), ("z", z), ("mu", mu0), ("pn", p_need), ("ps", p_sun), ("soc", soc), ("Ti", Ti - 273.15)):
            rec[k].append(v)
        if soc <= 0.0:
            end = f"battery empty at {z / 1e3:.1f} km"
            break
        if not batt.can_discharge(Ti - 273.15) and final:
            end = f"battery above {T_DISCHARGE_C:.0f} °C at {z / 1e3:.1f} km"
            break
        z += vz * dt
        x += A.zonal_wind(min(max(z, A.Z_MIN), A.Z_MAX)) * dt
        H += 2.0 * math.pi * dt / period
        t += dt
        step += 1
    note(f"end: {end or 'time limit'}")
    a = {k: np.array(v) for k, v in rec.items()}
    return Flight(a["t"], a["z"], a["mu"], a["pn"], a["ps"], a["soc"], a["Ti"], events,
                  float(a["t"][-1]) / 3600.0, sustained / 3600.0, x / 1e3, end)


def threshold_mu0(d: S.Design, tab: PowerTable, km: float | None = None) -> float | None:
    """cos z at which the array covers loiter at the cruise altitude (None: never)."""
    z = (km if km is not None else d.req.altitude_m / 1e3) * 1e3
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    return S._mu0_for(tab.at(tab.level_W, z) + d.P_sys_W, arr, z)


def window_budget(d: S.Design, tab: PowerTable) -> dict:
    """Closed-form sun window and energy margin, as ``venus_crosscheck.py`` does it."""
    z = d.req.altitude_m
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    Pl = tab.at(tab.level_W, z) + d.P_sys_W
    mu = threshold_mu0(d, tab)
    T_day = PW.air_mass_day_s(A.zonal_wind(z), z) / 3600.0
    if mu is None:
        return {"loiter_W": Pl, "mu0": None, "zenith_deg": None, "window_h": 0.0, "margin": 0.0, "air_mass_day_h": T_day}
    Hs = np.linspace(-math.acos(mu), math.acos(mu), 2001)
    p = np.array([arr.power(z, math.cos(h)) for h in Hs])
    window = 2.0 * math.acos(mu) / (2.0 * math.pi) * T_day
    e_sun = float(np.trapezoid(p, Hs)) / (2.0 * math.pi) * T_day
    return {"loiter_W": Pl, "mu0": mu, "zenith_deg": math.degrees(math.acos(mu)), "window_h": window,
            "energy_in_kWh": e_sun / 1e3, "energy_need_kWh": Pl * window / 1e3, "margin": e_sun / (Pl * window),
            "air_mass_day_h": T_day}


def release_angle(mu0: float | None, margin: float = 0.03) -> float:
    return 0.0 if mu0 is None else -math.degrees(math.acos(min(mu0 + margin, 1.0)))


# ---------------------------------------------------------------------------------------------------------------
# gust model
# ---------------------------------------------------------------------------------------------------------------

def gust_system(mass: float, Z_w: float, tau_a: float, kp: float, kd: float, sigma_a: float, tau_w: float,
                sigma_c: float = 0.0, L_c: float = 533.0, V: float = 7.8) -> tuple[np.ndarray, np.ndarray]:
    """Continuous (A, B) of altitude hold driven by white noise. States: z, ż, ΔT, w_A, c1, c2.

    Same loop as ``control.gust_response``; w = w_A + w_C. w_A: first-order, σ_a, τ_w. w_C: Dryden vertical
    (1 + √3 Ts) / (1 + Ts)², T = L/max(V, 2), scaled to σ_c."""
    T = L_c / max(V, 2.0)
    a = np.zeros((6, 6))
    b = np.zeros((6, 2))
    # c1' = c2, c2' = (-c1 - 2T c2 + ξ)/T²; output w_C = g (c1 + √3 T c2)
    a[4, 5] = 1.0
    a[5, 4] = -1.0 / T ** 2
    a[5, 5] = -2.0 / T
    b[5, 1] = 1.0 / T ** 2
    from scipy.linalg import solve_continuous_lyapunov as lyap

    sub = lyap(a[4:, 4:], -b[4:, 1:2] @ b[4:, 1:2].T)
    c_out = np.array([1.0, math.sqrt(3.0) * T])
    g = sigma_c / math.sqrt(float(c_out @ sub @ c_out)) if sigma_c > 0 else 0.0
    a[0, 1] = 1.0
    a[1, 1] = Z_w / mass
    a[1, 2] = 1.0 / mass
    a[1, 3] = -Z_w / mass
    a[1, 4] = -Z_w / mass * g
    a[1, 5] = -Z_w / mass * g * math.sqrt(3.0) * T
    a[2, 0] = -mass * kp / tau_a
    a[2, 1] = -mass * kd / tau_a
    a[2, 2] = -1.0 / tau_a
    a[3, 3] = -1.0 / tau_w
    b[3, 0] = sigma_a * math.sqrt(2.0 / tau_w)
    return a, b


def gust_model(mass: float, weight: float, Z_w: float, sigma_a: float, tau_w: float, sigma_c: float, L_c: float, V: float,
               kp: float = 0.1, kd: float = 1.0, tau_a: float = 0.1, hours: float = 49.0, seeds: int = 32,
               dt: float = 0.5, eta: float = 0.80256) -> dict:
    """Exact RMS and seeded peaks of altitude error and thrust, plus the slow power excursion ``W w / η``."""
    from scipy.linalg import expm, solve_continuous_lyapunov as lyap

    a, b = gust_system(mass, Z_w, tau_a, kp, kd, sigma_a, tau_w, sigma_c, L_c, V)
    cov = lyap(a, -b @ b.T)
    n = a.shape[0]
    big = np.zeros((2 * n, 2 * n))
    big[:n, :n], big[:n, n:], big[n:, n:] = -a, b @ b.T, a.T
    e = expm(big * dt)
    ad = e[n:, n:].T
    q = ad @ e[:n, n:]
    q = 0.5 * (q + q.T)
    lq = np.linalg.cholesky(q + 1e-14 * np.eye(n) * np.trace(q))
    rng = np.random.default_rng(1)
    x = rng.standard_normal((seeds, n)) @ np.linalg.cholesky(cov + 1e-12 * np.eye(n) * np.trace(cov)).T
    zp = np.zeros(seeds)
    tp = np.zeros(seeds)
    for _ in range(int(hours * 3600.0 / dt)):
        x = x @ ad.T + rng.standard_normal((seeds, n)) @ lq.T
        np.maximum(zp, np.abs(x[:, 0]), out=zp)
        np.maximum(tp, np.abs(x[:, 2]), out=tp)
    return {"sigma_w_A": sigma_a, "tau_w_s": tau_w, "sigma_w_C": sigma_c, "V_m_s": V,
            "z_rms_m": math.sqrt(cov[0, 0]), "z_peak_median_m": float(np.median(zp)), "z_peak_max_m": float(zp.max()),
            "dT_rms_over_W": math.sqrt(cov[2, 2]) / weight, "dT_peak_median_over_W": float(np.median(tp)) / weight,
            "dT_peak_max_over_W": float(tp.max()) / weight, "hours_per_run": hours, "runs": seeds,
            "hold_power_rms_W": weight * sigma_a / eta}


def correlation_time(V: float, tau_L: float = 1500.0, L: float = 5000.0) -> float:
    """Data book §2.5: 1/τ = 1/1500 s + V/5000 m."""
    return 1.0 / (1.0 / tau_L + V / L)


def ou_series(n: int, dt: float, sigma: float, tau: float, rng: np.random.Generator) -> np.ndarray:
    a = math.exp(-dt / tau)
    b = sigma * math.sqrt(1.0 - a * a)
    w = np.empty(n)
    w[0] = sigma * rng.standard_normal()
    noise = rng.standard_normal(n)
    for i in range(1, n):
        w[i] = a * w[i - 1] + b * noise[i]
    return w


# ---------------------------------------------------------------------------------------------------------------
# closed designs
# ---------------------------------------------------------------------------------------------------------------

@contextmanager
def hover_loss(f: float):
    """Inside the block ``sizing.close`` sizes rotors, motors and battery for hover power × (1 + f).

    aerokit has no interaction term; this leaves ``src/`` untouched. Mass closure only: flight power is
    rebuilt from the isolated system in :func:`power_table`."""
    base = F.RotorSystem

    def make(*args, **kw):
        return base(*args, bemt_power_factor=BASE_FACTOR * (1.0 + f), **kw)

    F.RotorSystem = make
    try:
        yield
    finally:
        F.RotorSystem = base


def close_with_interaction(im: Interaction, clearance: float = 0.10, D: float = 2.6, V_tip: float = 70.0,
                           **req_kw) -> S.Design:
    """Mass closure with the hover loss of ``im`` scaled to ``clearance`` by the proximity law."""
    f = (im.hover_ratio() - 1.0) * proximity_f(D, clearance) / proximity_f(D, 0.10)
    with hover_loss(f):
        return S.close(D, V_tip, replace(S.Requirements(), clearance_m=clearance, **req_kw))


def tuned_flight(d: S.Design, tab: PowerTable, prof: Profile, H0: float, dt: float = 60.0, soc_end: float = 0.05,
                 **kw) -> tuple[Flight, float]:
    """Latest sunset-dive start that still ends with ``soc_end`` left: longest flight for this vehicle."""
    best = None
    for horizon in np.arange(0.4, 3.01, 0.1):
        fl = fly(d, tab, replace(prof, sunset_horizon_h=float(horizon)), H0, dt, **kw)
        if fl.soc[-1] >= soc_end and "empty" not in fl.end_reason:
            best = (fl, float(horizon))
            break
    if best is None:
        raise RuntimeError("no sunset horizon leaves the battery above the end limit")
    return best


def event(fl: Flight, text: str) -> dict | None:
    return next((e for e in fl.events if text in e["event"]), None)


def summarise(d: S.Design, tab: PowerTable, fl: Flight, horizon: float | None, H0: float) -> dict:
    """Numbers of one flown mission, and the closure checks of doc 25 §5.4."""
    z = d.req.altitude_m
    w = window_budget(d, tab)
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    hover = tab.at(tab.hover_W, z) + d.P_sys_W
    mu_h = S._mu0_for(hover, arr, z)
    dive_ev = [e for e in fl.events if "dive" in e["event"] and ("starts" in e["event"]) and "sunset" not in e["event"]]
    aborted = [e for e in fl.events if "aborted" in e["event"]]
    bottoms = [e for e in fl.events if "bottom" in e["event"]]
    sunset = event(fl, "sunset dive starts")
    t_sunset = sunset["t_h"] if sunset else fl.flight_h
    lost = event(fl, "array no longer carries loiter")
    pre = fl.t / 3600.0 < t_sunset
    sunlit = fl.t / 3600.0 < (lost["t_h"] if lost else t_sunset)
    min_soc = float(fl.soc[sunlit].min())
    i_min = int(np.argmin(fl.soc[sunlit]))
    lowest = float(fl.z.min()) / 1e3
    pre_dive = fl.z[pre].min() / 1e3
    checks = {
        "sun_carries_loiter": w["mu0"] is not None,
        "soc_floor": min_soc >= SOC_FLOOR,
        "dives_reach_floor": len(bottoms) == len(dive_ev) and len(dive_ev) > 0,
        "dive_battery_below_60C": float(fl.T_int[pre].max()) < T_DISCHARGE_C,
        "dives_at_sun_rule": all(e["mu0"] >= (mu_h or 1.0) for e in dive_ev),
        "hover_reserve": d.battery_Wh >= RESERVE_HOVER_H * hover * 0.999,
        "charges_at_cruise": d.req.battery.can_charge(TH.vessel_steady(TH.Vessel(), z, 80.0)[0]),
    }
    leave = [e for e in fl.events if "climb back" in e["event"] or "aborted" in e["event"]]
    holds = [60.0 * (b["t_h"] - x["t_h"]) * 1.0 for b, x in zip(leave, bottoms, strict=False)]
    return {"gross_kg": d.gross_kg, "battery_Wh": d.battery_Wh, "solar_area_m2": d.solar_area_m2,
            "solar_overhead_W": arr.power(z, 1.0), "hover_W": hover, "loiter_W": w["loiter_W"],
            "loiter_speed_m_s": tab.at(tab.v_best, z), "descent_W": tab.at(tab.down_W, z) + d.P_sys_W,
            "mu0_loiter": w["mu0"], "sun_zenith_deg": w["zenith_deg"], "mu0_hover": mu_h,
            "window_h": w["window_h"], "energy_in_kWh": w.get("energy_in_kWh"), "energy_need_kWh": w.get("energy_need_kWh"),
            "energy_margin": w["margin"], "release_hour_angle_deg": H0, "flight_h": fl.flight_h, "sun_h": fl.sun_h,
            "drift_km": fl.drift_km, "end": fl.end_reason, "lowest_km": lowest, "deepest_science_km": float(pre_dive),
            "min_soc_before_sun_lost": min_soc, "min_soc_t_h": float(fl.t[sunlit][i_min]) / 3600.0,
            "T_peak_before_sunset_C": float(fl.T_int[pre].max()), "end_soc": float(fl.soc[-1]),
            "sunset_horizon_h": horizon, "reserve_h": d.battery_Wh / hover, "dive_hold_min": holds,
            "night_need_kWh": w["loiter_W"] * w["air_mass_day_h"] / 2.0 / 1e3,
            "dives_aborted": len(aborted), "events": fl.events, "checks": checks,
            "closes": all(checks.values())}


def fly_case(d: S.Design, im: Interaction | None, prof: Profile, step_km: float = 0.25, dt: float = 60.0) -> dict:
    tab = power_table(d, im, prof, step_km)
    H0 = release_angle(threshold_mu0(d, tab))
    z = d.req.altitude_m
    mu_h = S._mu0_for(tab.at(tab.hover_W, z) + d.P_sys_W, PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency), z)
    if mu_h is not None:                                  # doc 25 §7.2-7: dive only when the array covers hover
        period_h = PW.air_mass_day_s(A.zonal_wind(z), z) / 3600.0
        t_rule = (-math.degrees(math.acos(mu_h)) - H0) / 360.0 * period_h
        prof = replace(prof, dive_times_h=(max(prof.dive_times_h[0], math.ceil(4.0 * t_rule + 0.5) / 4.0),
                                           *prof.dive_times_h[1:]))
    fl, horizon = tuned_flight(d, tab, prof, H0, dt)
    out = summarise(d, tab, fl, horizon, H0)
    out["_flight"] = fl
    return out


# ---------------------------------------------------------------------------------------------------------------
# studies
# ---------------------------------------------------------------------------------------------------------------

def gust_study(d: S.Design, v_loiter: float, seeds: int = 32) -> dict:
    """Doc 25 §4.7 result, then the same loop with the data-book gust model."""
    st = A.state(55e3)
    fl = B.FlowState(st.rho, st.mu, st.a)
    W = d.gross_kg * st.g
    sys0 = isolated_system(d)
    Z_w = CT.heave_derivative(sys0, W, fl)
    eta = sys0.drive_efficiency
    tm = json.loads(TURBULENCE.read_text(encoding="utf-8"))
    a_par = tm["component_A_mesoscale_convective_vertical_wind"]
    c_par = tm["component_C_small_scale_turbulence_dryden"]
    b_par = tm["component_B_downdraft_events"]
    sig_a = a_par["sigma_w"]["value"]
    tau_l = a_par["lagrangian_time_scale"]["value"]
    L_e = a_par["eulerian_length_scale"]["value"]
    sig_c = c_par["sigma_w"]["value"]
    L_c = c_par["L_u_L_v_L_w"]["value"]
    tau_v = correlation_time(v_loiter, tau_l, L_e)
    kw = dict(kp=0.1, kd=1.0)
    old = CT.gust_response(d.gross_kg, W, Z_w, 0.1, **kw)
    same_loop = CT.gust_response(d.gross_kg, W, Z_w, 0.1, gust_time_s=tau_l, duration_s=20 * 3600.0, dt=0.05, **kw)
    a_hover = gust_model(d.gross_kg, W, Z_w, sig_a, tau_l, 0.0, L_c, 0.0, seeds=seeds, eta=eta)
    a_only = gust_model(d.gross_kg, W, Z_w, sig_a, tau_v, 0.0, L_c, v_loiter, seeds=seeds, eta=eta)
    full = gust_model(d.gross_kg, W, Z_w, sig_a, tau_v, sig_c, L_c, v_loiter, seeds=seeds, eta=eta)
    w_dd = max(abs(x) for x in b_par["amplitude"]["value"])
    return {"Z_w_N_per_m_s": Z_w, "weight_N": W, "gains": kw, "doc25_80s_as_run": old,
            "same_loop_tau_1500s_20h": same_loop, "A_only_hover_tau_1500s": a_hover, "A_only_loiter": a_only,
            "A_plus_C_loiter": full, "tau_loiter_s": tau_v,
            "downdraft": {"w_m_s": w_dd, "thrust_over_W": abs(Z_w) * w_dd / W,
                          "z_offset_m": abs(Z_w) * w_dd / (d.gross_kg * kw["kp"]), "hold_W": W * w_dd / eta},
            "cell_energy_Wh": W * sig_a / eta * tau_l / 3600.0, "thrust_margin": d.req.thrust_margin - 1.0}


def gust_mission(d: S.Design, tab: PowerTable, prof: Profile, H0: float, horizon: float, v_loiter: float,
                 n: int = 40, dt: float = 60.0) -> dict:
    """The nominal mission re-flown with altitude held against component A (seeded), all else equal."""
    tau = correlation_time(v_loiter)
    p = replace(prof, sunset_horizon_h=horizon)
    hours, floors, soc_end, empty = [], [], [], 0
    for seed in range(n):
        w = ou_series(6000, dt, 0.70, tau, np.random.default_rng(1000 + seed))
        fl = fly(d, tab, p, H0, dt, w_hold=w)
        lost = event(fl, "array no longer carries loiter")
        t_lost = lost["t_h"] if lost else fl.flight_h
        hours.append(fl.flight_h)
        floors.append(float(fl.soc[fl.t / 3600.0 < t_lost].min()))
        soc_end.append(float(fl.soc[-1]))
        empty += "empty" in fl.end_reason
    return {"runs": n, "tau_s": tau, "runs_ending_empty": empty, "flight_h_p5": float(np.percentile(hours, 5)),
            "flight_h_median": float(np.median(hours)), "flight_h_p95": float(np.percentile(hours, 95)),
            "min_soc_before_sun_lost_p5": float(np.percentile(floors, 5)),
            "min_soc_before_sun_lost_worst": float(min(floors)), "end_soc_worst": float(min(soc_end))}


def dive_study(d: S.Design, im: Interaction, prof: Profile, H0: float) -> list[dict]:
    """Deepest science dive at 1.5 m/s down: battery peak with the 50 °C abort switched off."""
    tab = power_table(d, im, prof)
    rows = []
    for km, up in ((51.0, 3.0), (51.5, 3.0), (52.0, 3.0), (52.5, 3.0), (53.0, 3.0), (52.0, 2.0), (52.0, 1.5)):
        p = replace(prof, dive_km=km, up_rate=up, dive_abort_C=99.0, sunset_horizon_h=0.5)
        fl = fly(d, tab, p, H0, stop_h=30.0)
        bottom = event(fl, "bottom")
        rows.append({"floor_km": km, "up_rate": up, "T_at_bottom_C": bottom["T_C"] if bottom else None,
                     "T_peak_C": float(fl.T_int.max()), "min_soc": float(fl.soc.min())})
    return rows


def sim_crosscheck(d: S.Design, models: dict[str, Interaction], pts: dict) -> list[dict]:
    """Budget model flown at the simulator's own start conditions, against what the 6-DOF run ended with."""
    rows = []
    for r in pts["dive_checks"]:
        im = models[r["interaction"]]
        base = Profile()
        tab = power_table(d, im, base)
        if r["kind"] == "dive":
            p = replace(base, start_km=55.0, dive_km=51.0, dive_times_h=(5.0 / 3600.0,), dive_abort_C=99.0,
                        sunset_horizon_h=0.0)
        else:
            p = replace(base, start_km=55.0, dive_times_h=(), sunset_horizon_h=1e9)
        fl = fly(d, tab, p, r["H0_deg"], dt=10.0, soc0=r["soc0"], T0_C=31.8, stop_h=r["t_end_s"] / 3600.0)
        rows.append({**r, "budget_end_soc": float(fl.soc[-1]), "budget_T_peak_C": float(fl.T_int.max()),
                     "budget_end_km": float(fl.z[-1]) / 1e3})
    return rows


def option_rows(models: dict[str, Interaction], prof: Profile) -> list[dict]:
    """Closed designs that answer the nominal case. Each one is sized, then flown (1 km power grid is not used:
    0.5 km keeps a run under a minute)."""
    nom = models["nominal"]
    plan = [("re-closed, 0.10 m gap", dict()),
            ("gap 0.26 m (0.1 D)", dict(clearance=0.26)), ("gap 0.52 m (0.2 D)", dict(clearance=0.52)),
            ("gap 0.78 m (0.3 D)", dict(clearance=0.78)),
            ("halo deck 0.15 m", dict(solar_option="halo", halo_width_m=0.15)),
            ("halo deck 0.30 m", dict(solar_option="halo", halo_width_m=0.30)),
            ("battery 0.75 h hover", dict(reserve_hover_h=0.75)), ("battery 1.0 h hover", dict(reserve_hover_h=1.0)),
            ("cruise 54 km", dict(altitude_m=54e3)), ("cruise 56 km", dict(altitude_m=56e3))]
    out = []
    for label, kw in plan:
        c = kw.pop("clearance", 0.10)
        im = replace(nom, clearance_m=c)
        try:
            d = close_with_interaction(im, c, **kw)
        except ValueError as e:
            out.append({"option": label, "error": str(e)})
            continue
        r = fly_case(d, im, prof, step_km=0.5)
        r.pop("_flight")
        r.update(option=label, clearance_m=c, span_m=2.0 * d.arm_m + d.D, arm_m=d.arm_m,
                 interior_cruise_C=TH.vessel_steady(TH.Vessel(), d.req.altitude_m, 80.0)[0])
        high = fly_case(d, replace(models["high"], clearance_m=c), prof, step_km=0.5)
        r["high_flight_h"], r["high_closes"], r["high_sun_h"] = high["flight_h"], high["closes"], high["sun_h"]
        out.append(r)
        print(f"  {label}: {r['gross_kg']:.1f} kg, {r['flight_h']:.1f} h, closes {r['closes']}", flush=True)
    return out


def entry_check(gross_kg: float) -> dict:
    """Entry numbers for another vehicle mass, same 3.7 m shell and -9.5 deg (as ``design.baseline``)."""
    b = DES.BASELINE
    es = DS.entry_system(gross_kg)
    m_entry = es["total_with_contingency"]
    veh = EN.EntryVehicle(m_entry, b.aeroshell_D, 1.05, nose_radius_m=0.25 * b.aeroshell_D)
    ent = EN.fly_entry(veh, EN.entry_speed(b.v_inf, b.entry_altitude), b.gamma_deg, h0=b.entry_altitude)
    return {"entry_mass_kg": m_entry, "beta_kg_m2": veh.beta, "peak_g": ent.peak_g}


def strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if not k.startswith("_")}


def compute(curves: Path, seeds: int = 32, mc_runs: int = 40) -> dict:
    t0 = time.time()
    raw_bytes = curves.read_bytes()
    raw = json.loads(raw_bytes.decode("utf-8"))
    pts = _points()
    base = S.close(2.6, 70.0)
    models = build_models(raw, base, pts)
    log = lambda m: print(f"[{time.time() - t0:5.0f} s] {m}", flush=True)   # noqa: E731

    legacy = Profile.legacy()
    leg_tab = power_table(base, None, legacy)
    leg = fly(base, leg_tab, legacy, DES.release_hour_angle(base))
    log(f"legacy check {leg.flight_h:.2f} h / {leg.sun_h:.2f} h")
    prof = Profile()
    cases = {}
    for c in CASES:
        cases[c] = fly_case(base, models[c], prof)
        log(f"{c}: {cases[c]['loiter_W']:.0f} W at {cases[c]['loiter_speed_m_s']:.1f} m/s, {cases[c]['flight_h']:.1f} h")
    file_min = {c: raw["en_az_guc"]["55_km"][c] for c in CASES}
    nominal = cases["nominal"]
    tab_n = power_table(base, models["nominal"], prof)
    dives = dive_study(base, models["nominal"], prof, nominal["release_hour_angle_deg"])
    log("dive study done")
    cross = sim_crosscheck(base, models, pts)
    log("simulator cross-check done")
    gust = gust_study(base, nominal["loiter_speed_m_s"], seeds)
    log("gust study done")
    gust_mc = gust_mission(base, tab_n, prof, nominal["release_hour_angle_deg"], nominal["sunset_horizon_h"],
                           nominal["loiter_speed_m_s"], mc_runs)
    log("gust mission Monte Carlo done")
    opts = option_rows(models, prof)
    log("options done")
    rec = next(o for o in opts if o["option"] == RECOMMENDED)
    d_rec = close_with_interaction(models["nominal"])
    rec_cases = {c: fly_case(d_rec, models[c], prof) for c in CASES}
    log("recommended design flown in all cases")
    out = {"generated_by": "python 04_Venus/scripts/venus_budget_update.py", "curves_file": str(curves),
           "curves_sha256": hashlib.sha256(raw_bytes).hexdigest(), "curves_generated": raw["uretildi"],
           "legacy_check": {"flight_h": leg.flight_h, "sun_h": leg.sun_h, "drift_km": leg.drift_km},
           "closure_rules": {"soc_floor": SOC_FLOOR, "reserve_hover_h": RESERVE_HOVER_H,
                             "T_discharge_C": T_DISCHARGE_C, "tag": "Y"},
           "profile": {k: getattr(prof, k) for k in ("start_km", "down_rate", "down_speed", "up_rate", "dive_km",
                                                     "hold_s", "dive_times_h", "dive_abort_C")},
           "simulator_points": pts, "file_minimum_55km": file_min,
           "cases": {c: strip(v) for c, v in cases.items()},
           "recommended_cases": {c: strip(v) for c, v in rec_cases.items()},
           "recommended_design": {"gross_kg": d_rec.gross_kg, "battery_Wh": d_rec.battery_Wh, "rpm": d_rec.hover.rpm,
                                  "breakdown": d_rec.breakdown, "baseline_breakdown": base.breakdown,
                                  "hover_tip_mach": d_rec.hover.per_rotor.tip_mach},
           "dive_study": dives, "sim_crosscheck": cross,
           "gust": gust, "gust_mission": gust_mc, "options": opts, "recommended": RECOMMENDED,
           "entry_baseline": entry_check(base.gross_kg), "entry_recommended": entry_check(rec["gross_kg"]),
           "_flights": {c: rec_cases[c]["_flight"] for c in CASES}}
    return out


# ---------------------------------------------------------------------------------------------------------------
# outputs
# ---------------------------------------------------------------------------------------------------------------

def _yes(v: bool) -> str:
    return "yes" if v else "NO"


def markdown(r: dict) -> str:
    c = r["cases"]
    fm = r["file_minimum_55km"]
    L = ["# VESPER budget update, 6 Nov 2026", "",
         f"`{r['generated_by']}`. Curves: `{r['curves_file']}` (generated {r['curves_generated']}, "
         f"sha256 {r['curves_sha256'][:12]}). Legacy check: {r['legacy_check']['flight_h']:.2f} h / "
         f"{r['legacy_check']['sun_h']:.2f} h (doc 25: 49.18 / 44.18).", ""]

    def table(title: str, cc: dict) -> None:
        L.extend([f"## {title}", "", "| Quantity | " + " | ".join(CASES) + " |", "|---|" + "---:|" * len(CASES)])

        def row(name, f):
            L.append(f"| {name} | " + " | ".join(f(cc[k], k) for k in CASES) + " |")

        row("File minimum at 55 km (43.66 kg), W at m/s", lambda v, k: f"{fm[k]['electric_W']:.0f} at {fm[k]['V']}")
        row("Loiter in this budget, W", lambda v, k: f"{v['loiter_W']:.0f}")
        row("Loiter speed, m/s", lambda v, k: f"{v['loiter_speed_m_s']:.1f}")
        row("Hover, W", lambda v, k: f"{v['hover_W']:.0f}")
        row("Descent 1.5 m/s + 3.5 m/s forward, W", lambda v, k: f"{v['descent_W']:.0f}")
        row("Sun threshold cos z", lambda v, k: f"{v['mu0_loiter']:.3f}")
        row("Sun within, degrees of zenith", lambda v, k: f"{v['sun_zenith_deg']:.1f}")
        row("Sun window (closed form), h", lambda v, k: f"{v['window_h']:.1f}")
        row("Energy margin in the window", lambda v, k: f"{v['energy_margin']:.2f}")
        row("Release hour angle, deg", lambda v, k: f"{v['release_hour_angle_deg']:.1f}")
        row("Flight on sunlight, h", lambda v, k: f"{v['sun_h']:.1f}")
        row("Total flight, h", lambda v, k: f"{v['flight_h']:.1f}")
        row("Drift, km", lambda v, k: f"{v['drift_km']:.0f}")
        row("Lowest state of charge before sun loss", lambda v, k: f"{100 * v['min_soc_before_sun_lost']:.0f} %")
        row("Battery peak before sunset, °C", lambda v, k: f"{v['T_peak_before_sunset_C']:.1f}")
        row("Lowest altitude, km", lambda v, k: f"{v['lowest_km']:.1f}")
        row("End state of charge", lambda v, k: f"{100 * v['end_soc']:.0f} %")
        row("Hover reserve, h (rule 0.5)", lambda v, k: f"{v['reserve_h']:.3f}")
        row("Hold at the dive floor, min (plan 5)", lambda v, k: f"{min(v['dive_hold_min']):.0f}")
        for key in cc["nominal"]["checks"]:
            row(f"Check: {key}", lambda v, k, key=key: _yes(v["checks"][key]))
        row("**Closes**", lambda v, k: _yes(v["closes"]))
        L.append("")

    table("As built (43.66 kg, 4.45 m², 1044 Wh), 6 Nov profile", c)
    rd = r["recommended_design"]
    table(f"Recommended design ({rd['gross_kg']:.2f} kg, {rd['battery_Wh']:.0f} Wh), 6 Nov profile", r["recommended_cases"])
    L += ["## Battery at each mission event, recommended design", ""]
    for k in CASES:
        L += [f"### {k}", "", "| t (h) | Event | z (km) | SoC | battery °C | cos z |", "|---:|---|---:|---:|---:|---:|"]
        L += [f"| {e['t_h']:.2f} | {e['event']} | {e['z_km']:.2f} | {100 * e['soc']:.0f} % | {e['T_C']:.1f} | "
              f"{e['mu0']:.3f} |" for e in r["recommended_cases"][k]["events"]]
        L.append("")
    L += ["## Science dive floor at 1.5 m/s down (nominal, 50 °C abort off)", "",
          "| Floor (km) | Climb (m/s) | Battery at bottom (°C) | Peak (°C) | Lowest SoC |", "|---:|---:|---:|---:|---:|"]
    L += [f"| {x['floor_km']:.1f} | {x['up_rate']:.1f} | {x['T_at_bottom_C']:.1f} | {x['T_peak_C']:.1f} | "
          f"{100 * x['min_soc']:.0f} % |" for x in r["dive_study"]]
    L += ["", "## Simulator end state against this budget", "",
          "| Run | Interaction | Air | Start cos z | Start SoC | Sim end SoC | Budget end SoC | Sim peak °C (1 node) | "
          "Budget peak °C (2 nodes) |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {x['name']} | {x['interaction']} | {x['air']} | {x['mu0_start']:.2f} | {100 * x['soc0']:.0f} % | "
          f"{100 * x['sim_end_soc']:.0f} % | {100 * x['budget_end_soc']:.0f} % | {x['sim_T_peak_C']:.1f} | "
          f"{x['budget_T_peak_C']:.1f} |" for x in r["sim_crosscheck"]]
    for km in ("52", "51"):
        L += ["", f"Simulator dives to {km} km (cos z 0.87, nominal): " + "; ".join(
            f"{x['seed']}: max tilt {x['tilt']:.1f}°, lowest SoC {100 * x['minsoc']:.0f} %, peak {x['Tmax']:.1f} °C"
            for x in r["simulator_points"][f"dive_{km}km"]) + "."]
    g = r["gust"]
    o, s1, a, f = (g["doc25_80s_as_run"], g["same_loop_tau_1500s_20h"], g["A_only_hover_tau_1500s"], g["A_plus_C_loiter"])
    gm = r["gust_mission"]
    L += ["", "## Gust re-run", "", "| Model | z RMS (m) | z peak (m) | Thrust RMS / W | Thrust peak / W |",
          "|---|---:|---:|---:|---:|",
          f"| Doc 25: σ 0.7, 80 s, 2 h, one seed | {o['z_rms_m']:.1f} | {o['z_peak_m']:.1f} | "
          f"{o['dT_rms_N'] / g['weight_N']:.3f} | {o['dT_peak_over_W']:.3f} |",
          f"| Same loop, 1500 s, 20 h, one seed | {s1['z_rms_m']:.1f} | {s1['z_peak_m']:.1f} | "
          f"{s1['dT_rms_N'] / g['weight_N']:.3f} | {s1['dT_peak_over_W']:.3f} |",
          f"| Component A, hover, 1500 s, {a['hours_per_run']:.0f} h × {a['runs']} | {a['z_rms_m']:.1f} | "
          f"{a['z_peak_max_m']:.1f} | {a['dT_rms_over_W']:.3f} | {a['dT_peak_max_over_W']:.3f} |",
          f"| A + C, loiter, τ {g['tau_loiter_s']:.0f} s, {f['hours_per_run']:.0f} h × {f['runs']} | {f['z_rms_m']:.1f} | "
          f"{f['z_peak_max_m']:.1f} | {f['dT_rms_over_W']:.3f} | {f['dT_peak_max_over_W']:.3f} |", "",
          f"A -{g['downdraft']['w_m_s']:.1f} m/s downdraft held: thrust {g['downdraft']['thrust_over_W']:.3f} W, "
          f"altitude offset {g['downdraft']['z_offset_m']:.0f} m, +{g['downdraft']['hold_W']:.0f} W. "
          f"Holding one 0.7 m/s cell for 1500 s costs {g['cell_energy_Wh']:.0f} Wh. "
          f"Nominal mission with component A held, {gm['runs']} seeds: {gm['flight_h_p5']:.1f} / "
          f"{gm['flight_h_median']:.1f} / {gm['flight_h_p95']:.1f} h (p5 / median / p95), lowest SoC before sun loss "
          f"{100 * gm['min_soc_before_sun_lost_worst']:.0f} %, {gm['runs_ending_empty']} runs end with an empty "
          "battery.", "",
          "## Closed designs for the nominal case", "",
          "| Option | Gross kg | Deck m² | Battery Wh | Span m | Loiter W | cos z | Sun h | Flight h | High h | Cruise interior °C | "
          "Closes |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for x in r["options"]:
        if "error" in x:
            L.append(f"| {x['option']} | no closure: {x['error']} |" + " |" * 10)
            continue
        L.append(f"| {x['option']} | {x['gross_kg']:.1f} | {x['solar_area_m2']:.2f} | {x['battery_Wh']:.0f} | "
                 f"{x['span_m']:.1f} | {x['loiter_W']:.0f} | {x['mu0_loiter']:.3f} | {x['sun_h']:.1f} | "
                 f"{x['flight_h']:.1f} | {x['high_flight_h']:.1f} | {x['interior_cruise_C']:.1f} | {_yes(x['closes'])} |")
    rc = r["simulator_points"]["release_current"]
    L += ["", "## Pull-out battery current against the 53.6 A 2C limit (simulator, 43.66 kg, 14S8P)", "",
          "| Release cos z | Peak A | Bus W | Array W |", "|---:|---:|---:|---:|"]
    L += [f"| {x['mu0']:.3f} | {x['Ipeak']:.1f} | {x['Pbus']:.0f} | {x['Psol']:.0f} |" for x in rc]
    L += ["", "## Model uncertainty carried by these numbers", "",
          "Wake model fitted to NASA MTB wind-tunnel thrust ratios (tip gap 0.47 D, kw 0.50; low/high 0.30/0.70, rms 0.041). "
          "The fit covers V ≥ 3.5 m/s and may under-predict below that. VESPER's 0.04 D gap is outside the tested range. "
          "`guc_egrisi.json` predates a yaw-shed change; level trim agrees (harness 1578 W at 7.8 m/s). Low to high is the "
          "bracket on these curves, not a confidence interval.", ""]
    eb, er = r["entry_baseline"], r["entry_recommended"]
    L += ["", f"Recommended: **{r['recommended']}**. Entry: {eb['entry_mass_kg']:.0f} → {er['entry_mass_kg']:.0f} kg, "
          f"β {eb['beta_kg_m2']:.1f} → {er['beta_kg_m2']:.1f} kg/m², {eb['peak_g']:.1f} → {er['peak_g']:.1f} g.", ""]
    return "\n".join(L)


BRIEFS = """## Figure briefs (written before drawing)

- **B1 power curve.** Message: interaction lifts minimum power at 55 km and moves it from 8 to 9 m/s. Reader: mixed jury.
  Target: sunum-tam. Data: airspeed vs electric power, four cases, `trim_ok` rows only. Form: lines, direct labels.
- **B2 mission.** Message: every case stays far above the battery floor; more interaction only shortens the day.
  Reader: mixed jury. Data: altitude and state of charge vs time, four cases, recommended design. Form: two panels.
- **B3 options.** Message: small changes buy hours cheaply; a bigger deck or battery costs far more mass.
  Reader: mixed jury. Data: one point per closed design; battery 0.75 h (62 kg, 30 h), halo 0.30 m (81 kg) and battery
  1.0 h (no closure) are off this scale and stay in the table. Form: labelled scatter (flight time is the outcome, so
  it stays on y although it is a duration).
"""
LABEL_AT = {"re-closed, 0.10 m gap": ("recommended", 10, -5, "left"), "gap 0.26 m (0.1 D)": ("gap 0.26 m", -10, 4, "right"),
            "cruise 56 km": ("cruise 56 km", 10, -2, "left"), "gap 0.52 m (0.2 D)": ("gap 0.52 m", 0, 12, "center"),
            "gap 0.78 m (0.3 D)": ("gap 0.78 m", 0, -24, "center"), "halo deck 0.15 m": ("halo 0.15 m", 0, 12, "center"),
            "cruise 54 km": ("cruise 54 km", 10, -5, "left")}


def _draw(Sx, r: dict, raw: dict, names: dict) -> None:
    import datawiz as dw

    cur = read_curves(raw)[55.0]
    fig, ax = Sx.figur(oran=0.55)
    for c in CASES:
        rows = [x for x in cur[c] if x["V"] <= 15]
        ax.plot([x["V"] for x in rows], [x["electric_W"] / 1e3 for x in rows], **Sx.stil(names[c]))
    Sx.eksen(ax, x="speed", y="pw")
    ax.set_ylim(0, 2.4)
    dw.etiket.cizgi_sonu(ax)
    Sx.kaydet(fig, str(OUT / "B1_power_curve"), sessiz=True)

    fl = r["_flights"]
    fig, axs = Sx.figur(oran=0.9, nrows=2, sharex=True, gridspec_kw={"hspace": 0.3})
    for c in CASES:
        h = fl[c].t / 3600.0
        axs[0].plot(h, fl[c].z / 1e3, **Sx.stil(names[c]))
        axs[1].plot(h, 100.0 * fl[c].soc, **Sx.stil(names[c]))
    Sx.eksen(axs[0], x="hours", y="alt")
    Sx.eksen(axs[1], x="hours", y="soc")
    axs[0].set_xlabel("")
    axs[1].set_ylim(0, 105)
    dw.lejant.ortak(fig)
    Sx.kaydet(fig, str(OUT / "B2_mission"), sessiz=True)

    ok = [o for o in r["options"] if "error" not in o and o["option"] in LABEL_AT]
    fig, ax = Sx.figur(oran=0.6)
    ax.plot([o["gross_kg"] for o in ok], [o["flight_h"] for o in ok], linestyle="none", marker="o", markersize=9,
            color=Sx.renk("Closed design"))
    for o in ok:
        text, dx, dy, ha = LABEL_AT[o["option"]]
        ax.annotate(text, (o["gross_kg"], o["flight_h"]), xytext=(dx, dy), textcoords="offset points", ha=ha)
    Sx.eksen(ax, x="gross", y="flight")
    ax.set_xlim(40, 65)
    ax.set_ylim(40, 54)
    Sx.kaydet(fig, str(OUT / "B3_options"), sessiz=True)


def figures(r: dict, raw: dict) -> int:
    """Three audited slide figures. Returns the number of HATA in the set."""
    import datawiz as dw

    from day_common import audit_summary

    Sx = dw.Seti(str(OUT / "budget.seti.json"), hedef="sunum-tam")
    Sx.nicelik("speed", "Airspeed", "m/s", eksen="x")
    Sx.nicelik("pw", "Electric power at 55 km", "kW", eksen="y")
    Sx.nicelik("hours", "Time from release", "h", eksen="x")
    Sx.nicelik("alt", "Altitude", "km", eksen="y")
    Sx.nicelik("soc", "Battery state of charge", "%", eksen="y")
    Sx.nicelik("gross", "Gross mass", "kg", eksen="x")
    Sx.nicelik("flight", "Flight time", "h", eksen="y")
    names = {"off": "No interaction", "low": "Low", "nominal": "Nominal", "high": "High"}
    for c in ("off", "low", "nominal"):
        Sx.varlik(names[c])
    Sx.varlik(names["high"], renk=dw.renk.koyu_ton("#cc79a7"), cizgi="-.", degistir=True)
    Sx.varlik("Closed design", renk="#000000", cizgi="none", isaret="o", degistir=True)
    for _ in range(2):
        _draw(Sx, r, raw, names)
        if Sx.d.get("kenar_mm"):
            break
        left, bottom, right, top = Sx.kenar_oner()
        Sx.kenar(left, bottom, right + 14.0, top)
    errors, audit = audit_summary(OUT)
    print(audit)
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--curves", type=Path, default=CURVES)
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args(argv)
    if not args.curves.is_file():
        print(f"{args.curves} not found", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    r = compute(args.curves)
    raw = json.loads(args.curves.read_text(encoding="utf-8"))
    (OUT / "sim_runs").mkdir(exist_ok=True)
    shutil.copy2(args.curves, OUT / "sim_runs" / "guc_egrisi.input.json")
    public = {k: v for k, v in r.items() if not k.startswith("_")}
    (OUT / "result.json").write_text(json.dumps(public, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    (OUT / "result.md").write_text(markdown(r) + "\n" + BRIEFS, encoding="utf-8")
    errors = 0 if args.no_figures else figures(r, raw)
    print(f"wrote {OUT}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
