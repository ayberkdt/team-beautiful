"""One-at-a-time sensitivity of the VESPER baseline (D 2.6 m, tip speed 70 m/s, 55 km) and of the lighter 2.3 m point.

    python 04_Venus/code/analysis/venus_sensitivity.py

For each parameter, low/high values (stated with their reason) → closed gross mass, cos-zenith above which the array
sustains loiter, and flight hours of the mission (released when the sun is just high enough: entry targeted
to that local time, :func:`aerokit.venus.design.release_hour_angle`). Output:
``04_Venus/outputs/sensitivity.json``. Each run closes the mass loop (BEMT) and re-flies the mission.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit import venus_flight as VF  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import sizing as S  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs" / "sensitivity.json"
D, VT = 2.6, 70.0


def run(req: S.Requirements, mm: S.MassModel, label: str) -> dict:
    try:
        d = S.close(D, VT, req, mm)
    except ValueError as e:
        return {"label": label, "error": str(e)}
    H0 = DES.release_hour_angle(d)
    r = VF.simulate_rotorcraft_day(d, start_hour_angle_deg=H0, cruise_km=req.altitude_m / 1e3, dt=60.0)
    return {"label": label, "gross_kg": d.gross_kg, "mu0_loiter": d.sustain_mu0_loiter,
            "loiter_W": d.P_bucket_elec_W, "solar_overhead_W": d.P_solar_overhead_W,
            "flight_h": r.flight_time_s / 3600.0, "sustained_h": r.solar_sustained_s / 3600.0,
            "release_hour_angle_deg": H0}


CASES = (
    ("battery cell energy 180 / 280 Wh/kg", "battery",
     replace(PW.LI_ION_NCR18650B, cell_specific_energy=180.0), replace(PW.LI_ION_NCR18650B, cell_specific_energy=280.0)),
    ("solar array efficiency 0.25 / 0.32", "solar_efficiency", 0.25, 0.32),
    ("mass contingency 30 % / 10 %", "contingency", 0.30, 0.10),
    ("atmosphere thin / dense (PV envelope)", "atmosphere_case", "thin", "dense"),
    ("payload 5 kg / 1.5 kg", "payload_kg", 5.0, 1.5),
    ("cruise altitude 53 / 58 km", "altitude_m", 53e3, 58e3),
    ("battery reserve 1.0 / 0.25 h hover", "reserve_hover_h", 1.0, 0.25),
    ("blade areal mass 3.3 / 1.5 kg/m²", "blade_areal", 3.3, 1.5),
    ("motor specific torque 5 / 10 N·m/kg", "motor_specific_torque", 5.0, 10.0),
    ("gearbox torque density 12 / 40 N·m/kg", "gearbox_torque_density", 12.0, 40.0),
)


def main(argv: list[str]) -> int:
    t0 = time.time()
    base_req, base_mm = S.Requirements(), S.MassModel()
    rows = [dict(run(base_req, base_mm, "baseline"), case="baseline")]
    print(f"[{time.time() - t0:5.0f} s] baseline {rows[0]}", flush=True)
    for label, field, lo, hi in CASES:
        for tag, val in (("bad", lo), ("good", hi)):
            if hasattr(base_req, field):
                req, mm = replace(base_req, **{field: val}), base_mm
            else:
                req, mm = base_req, replace(base_mm, **{field: val})
            r = run(req, mm, f"{label} [{tag}]")
            r.update(case=label, side=tag, value=repr(val) if field == "battery" else val)
            rows.append(r)
            print(f"[{time.time() - t0:5.0f} s] {r}", flush=True)
    robust = []
    adverse = (("nominal", {}, {}), ("cells 180 Wh/kg", {"battery": replace(PW.LI_ION_NCR18650B,
                                                                              cell_specific_energy=180.0)}, {}),
               ("contingency 30 %", {}, {"contingency": 0.30}), ("motors 5 N·m/kg", {}, {"motor_specific_torque": 5.0}),
               ("payload 5 kg", {"payload_kg": 5.0}, {}), ("thin atmosphere", {"atmosphere_case": "thin"}, {}))
    for Dr, gear in ((2.6, 5.0), (2.6, 1.0), (2.3, 5.0)):
        for label, rk, mk in adverse:
            try:
                d = S.close(Dr, VT, replace(base_req, **rk), replace(base_mm, **dict(mk, gear_ratio=gear)))
                r = VF.simulate_rotorcraft_day(d, start_hour_angle_deg=DES.release_hour_angle(d), dt=120.0)
                rec = {"D_m": Dr, "gear_ratio": gear, "case": label, "gross_kg": d.gross_kg,
                       "flight_h": r.flight_time_s / 3600.0, "span_m": 2 * d.arm_m + Dr}
            except ValueError as e:
                rec = {"D_m": Dr, "gear_ratio": gear, "case": label, "error": str(e)}
            robust.append(rec)
            print(f"[{time.time() - t0:5.0f} s] robustness {rec}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generated_by": "python 04_Venus/code/analysis/venus_sensitivity.py", "D_m": D, "V_tip_m_s": VT,
                               "rows": rows, "robustness": robust}, indent=1, default=str), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
