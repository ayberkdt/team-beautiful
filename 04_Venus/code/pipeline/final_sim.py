"""Flight-model parameters for ``venus_final`` (``vesper_for_simulator.json``); ``BASE`` is the baseline in use."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import bemt as B  # noqa: E402
from aerokit.venus import control as CT  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402


def simulator_parameters(c: dict, BASE) -> dict:
    """Flight-model parameters for a game/simulator engine (Liftoff Core / Unity): rigid body + 6 rotors.

    Inertia: point masses of the design components at their positions, arms as thin rods, each rotor+motor as a point
    mass at its hub [K from design.json masses, which are themselves K/Y]. Rotor thrust/torque curves: BEMT at the
    cruise altitude for the trimmed collective, 40-160 % of hover rpm [K]."""
    res = c["res"]
    d = res["design"]
    doc = DES.design_document(BASE)
    comps = {x["id"]: x for x in doc["vehicle"]["components"]}
    arm = d.arm_m
    az = [math.radians(a) for a in (30, 90, 150, 210, 270, 330)]
    z_rot = comps["rotors"]["position_m"][2]
    m_rotor = comps["rotors"]["mass_kg"] / 6.0
    I = np.zeros((3, 3))
    pts = []
    for cid, cm in comps.items():
        if cid in ("rotors", "arms") or cm.get("position_m") is None:
            continue
        pts.append((cm["mass_kg"], np.array(cm["position_m"], dtype=float)))
    for a in az:
        pts.append((m_rotor, np.array([arm * math.cos(a), arm * math.sin(a), z_rot])))
    m_arm = comps["arms"]["mass_kg"] / 6.0
    for a in az:                                   # thin rod from the body edge to the hub, 5 lumps
        for k in range(5):
            rr = 0.3 + (arm - 0.3) * (k + 0.5) / 5
            pts.append((m_arm / 5, np.array([rr * math.cos(a), rr * math.sin(a), z_rot])))
    unplaced = sum(x["mass_kg"] for x in comps.values() if x.get("position_m") is None)
    pts.append((unplaced, np.zeros(3)))           # wiring + contingency lumped at the centre [Y]
    m_tot = sum(m for m, _ in pts)
    cg = sum(m * r for m, r in pts) / m_tot
    for m, r in pts:
        q = r - cg
        I += m * (np.dot(q, q) * np.eye(3) - np.outer(q, q))
    s = A.state(BASE.cruise_km * 1e3)
    fl = B.FlowState(s.rho, s.mu, s.a)
    om_h = d.hover.per_rotor.omega
    curve = []
    for f in np.linspace(0.4, 1.6, 13):
        r = B.solve(d.rotor, om_h * f, fl)
        curve.append({"rpm": round(om_h * f * 30 / math.pi, 1), "thrust_N": round(r.thrust, 2),
                      "torque_Nm": round(r.torque * d.system.bemt_power_factor, 3),
                      "shaft_W": round(r.power * d.system.bemt_power_factor, 1)})
    I_rot = (d.breakdown["blades+hubs"] / 6 - 0.12) * d.rotor.radius ** 2 / 3.0   # blades as uniform rods [K]
    dep = res["deploy"]
    step = max(1, len(dep.t) // 200)
    return {
        "units": "SI; body frame x forward (between arms 1 and 6), y left, z up; rotor i at azimuth 30+60 i deg",
        "source": "python 04_Venus/code/pipeline/venus_day.py --final (aerokit.venus); tags K unless stated",
        "mass_kg": round(m_tot, 3), "cg_m": [round(x, 4) for x in cg],
        "inertia_kg_m2": [[round(x, 3) for x in row] for row in I],
        "rotors": [{"position_m": [round(arm * math.cos(a), 4), round(arm * math.sin(a), 4), round(z_rot, 3)],
                    "spin": sp, "radius_m": d.rotor.radius, "blades": d.rotor.blades,
                    "polar_inertia_kg_m2": round(I_rot, 4)} for a, sp in zip(az, ["ccw", "cw"] * 3)],
        "rotor_curve_at_cruise": curve,
        "hover": {"rpm": round(d.hover.rpm, 1), "thrust_per_rotor_N": round(d.hover.per_rotor.thrust, 2),
                  "shaft_W_total": round(d.hover.shaft_W, 0), "collective_deg": round(d.rotor.theta75_deg, 2)},
        "drag_area_m2": d.system.drag_area_m2,
        "max_airspeed_m_s": round(CT.max_airspeed(d.system, d.gross_kg * s.g, fl, d.hover.shaft_W * 1.6 ** 1.5), 2),
        "environment_cruise": {"altitude_m": BASE.cruise_km * 1e3, "density": round(s.rho, 4),
                               "temperature_K": round(s.T, 2), "gravity": round(s.g, 4),
                               "speed_of_sound": round(s.a, 1), "wind_west_m_s": round(A.zonal_wind(s.h), 1),
                               "vertical_gust_sigma_m_s": 0.7, "downdraft_episode_m_s": [2.0, 4.0]},
        "deployment_replay": [{"t_s": round(float(dep.t[i]), 3), "altitude_m": round(float(dep.h[i]), 2),
                               "descent_rate_m_s": round(float(dep.Vd[i]), 3)} for i in range(0, len(dep.t), step)],
        "mission_series": doc["operations"]["series_hourly"],
    }
