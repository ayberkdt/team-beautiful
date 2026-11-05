"""Entry-model validation against every historical Venus entry with published conditions.

    python scripts/venus_entry_validation.py

Inputs per case — ballistic coefficient β, entry angle γ and speed at a 200 km interface, diameter, shape — from
Dutta, Smith, Prabhu & Venkatapathy 2012, Table 1 (research note D_dutta_2012_venus_entry, [D-ag]); their peak
deceleration and peak heat flux (cold-wall convective + radiative) are *engineering re-simulations*, not
measurements. Flight-reported peak g where it exists: Pioneer Venus (SP-461, Venkatapathy 2016), Venera 8 / 10
(Siddiqi 2018) [D-ag]. Parachute/heat-shield events: PV large heat shield off ~67 km (SP-461), Venera 9 cover off
~65 km and mains at 62 km (Siddiqi), DAVINCI pilot at Mach 0.8, main at ~70 km (Dutta 2023), Vega cap chute 64 km
[A, PDS summary].

Our model: :func:`aerokit.venus.entry.fly_entry` (planar 3-DOF, probe/VIRA-like atmosphere, isothermal above 100 km),
Sutton–Graves + Tauber radiative heating at the stagnation point. Nose radius: sphere D/2, 45° sphere-cone D/4 (PV
large: 0.356 vs 0.363 m published) — assumption [Y]. "Parachute altitude" = where the speed falls to Mach 0.8
(local speed of sound from :mod:`aerokit.venus.gas`). Output: ``studies/final_2026/venus/out/entry_validation.json``
and ``.md``.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit import planetary as P  # noqa: E402
from aerokit.venus import descent as DS  # noqa: E402
from aerokit.venus import entry as E  # noqa: E402
from aerokit.venus import gas  # noqa: E402

OUT = ROOT / "studies" / "final_2026" / "venus" / "out"

# name, beta, gamma, V km/s, D m, shape, Dutta n_max, Dutta q_max kW/cm², flight-reported g (source), chute km (source)
CASES = (
    ("Venera 4", 519, -78.0, 10.7, 1.0, "sphere", 450, 9.66, (300, "Siddiqi 2018 'experienced'"), None),
    ("Venera 8", 670, -77.0, 11.6, 1.0, "sphere", 500, 30.0, (335, "Siddiqi 2018"), None),
    ("Venera 9", 367, -20.5, 10.7, 2.4, "sphere", 150, 3.04, None, (65.0, "cover off ~65 km, Siddiqi 2018")),
    ("Venera 10", 367, -23.0, 10.7, 2.4, "sphere", 170, 3.37, (168, "Siddiqi 2018"), None),
    # Dutta Table 1: beta 376 / 379 / 387 / 387 (V11 / V12 / V13 / V14); gamma "-18 to -21" and n_max "138-167" are
    # shared by all four. The two rows span both ranges; pairing 138 g with -18 deg and 167 g with -21 deg is ours [Y].
    ("Venera 11 (-18°)", 376, -18.0, 11.2, 2.4, "sphere", 138, 4.35, None, None),
    ("Venera 13/14 (-21°)", 387, -21.0, 11.2, 2.4, "sphere", 167, 4.35, None, None),
    ("Vega 1", 412, -18.23, 10.7, 2.4, "sphere", 130, 3.06, None, (64.0, "cap chute 64 km, PDS summary [A]")),
    ("Vega 2", 412, -19.08, 10.8, 2.4, "sphere", 139, 3.29, None, None),
    ("PV North", 190, -68.7, 11.5, 0.7653, "cone45", 487, 10.6, (458, "SP-461 steepest"), None),
    ("PV Night", 190, -41.5, 11.5, 0.7653, "cone45", 350, 7.8, None, None),
    ("PV Day", 190, -25.4, 11.5, 0.7653, "cone45", 219, 5.2, (223, "SP-461 shallowest"), None),
    ("PV Large", 188, -32.4, 11.5, 1.4228, "cone45", 276, 6.9, (280, "SP-461"), (67.0, "heat shield off ~67 km, SP-461")),
)


def mach08_altitude(r: E.EntryResult) -> float | None:
    """First altitude after peak deceleration where V ≤ 0.8 × local speed of sound."""
    i0 = int(np.argmax(r.decel_g))
    for k in range(i0, len(r.t)):
        h = float(r.h[k])
        T = P.venus_atmosphere(min(max(h, 0.0), 100e3)).T
        if r.V[k] <= 0.8 * gas.speed_of_sound(T):
            return h
    return None


def run_case(beta: float, gamma: float, V: float, D: float, shape: str, h0: float = 200e3) -> dict:
    rn = D / 2.0 if shape == "sphere" else D / 4.0
    cd = 1.05
    m = beta * cd * math.pi * D * D / 4.0
    veh = E.EntryVehicle(m, D, cd, nose_radius_m=rn)
    r = E.fly_entry(veh, V * 1e3, gamma, h0=h0, dt=0.005 if abs(gamma) > 40 else 0.01, stop_speed=120.0)
    q_tot = r.q_conv + np.nan_to_num(r.q_rad)
    return {"peak_g": r.peak_g, "peak_g_km": r.peak_g_altitude / 1e3, "peak_q_kW_cm2": float(np.max(q_tot)) / 1e7,
            "peak_qconv_kW_cm2": float(np.nanmax(r.q_conv)) / 1e7, "mach08_km": (mach08_altitude(r) or float("nan")) / 1e3,
            "nose_radius_m": rn}


def main(argv: list[str]) -> int:
    rows = []
    for name, beta, gamma, V, D, shape, g_pub, q_pub, flown, chute in CASES:
        res = run_case(beta, gamma, V, D, shape)
        row = {"case": name, "beta": beta, "gamma_deg": gamma, "V_km_s": V, "D_m": D, "shape": shape, **res,
               "dutta_g": g_pub, "dutta_q_kW_cm2": q_pub, "err_g_vs_dutta": res["peak_g"] / g_pub - 1.0,
               "err_q_vs_dutta": res["peak_q_kW_cm2"] / q_pub - 1.0}
        if flown:
            row["flight_g"], row["flight_g_source"] = flown
            row["err_g_vs_flight"] = res["peak_g"] / flown[0] - 1.0
        if chute:
            row["event_km"], row["event_source"] = chute
        rows.append(row)
        print(f"{name:22s} g {res['peak_g']:6.1f} vs {g_pub:4d} ({100 * row['err_g_vs_dutta']:+5.1f} %)  "
              f"q {res['peak_q_kW_cm2']:5.2f} vs {q_pub:5.2f} kW/cm2 ({100 * row['err_q_vs_dutta']:+5.1f} %)  "
              f"M0.8 at {res['mach08_km']:5.1f} km" + (f"  [event {chute[0]} km]" if chute else ""), flush=True)
    # DAVINCI: beta not published (entry-system mass not found) -> sweep; its -6.3 deg is quoted at the 145 km
    # atmospheric entry interface (AEI 145 km in note B_davinci); at a 200 km interface it would skip out
    dav = []
    for beta in (50.0, 100.0, 150.0, 200.0):
        res = run_case(beta, -6.3, 10.4, 2.24, "cone45", h0=145e3)
        dav.append({"beta": beta, **res})
        print(f"DAVINCI beta {beta:5.0f}: g {res['peak_g']:5.1f} (published 32 g), M0.8 at {res['mach08_km']:.1f} km "
              f"(pilot at Mach 0.8, main ~70 km)", flush=True)
    vesper = run_case(25.1, -9.5, 10.78, 3.7, "cone45")
    print(f"VESPER (beta 25, -9.5 deg): {vesper['peak_g']:.1f} g, {1e3 * vesper['peak_q_kW_cm2']:.0f} W/cm2 "
          "(Dutta 2012 Fig. 1: beta ~30, -10 deg -> ~50-60 g, 250-350 W/cm2 [D-ag])")
    errs = np.array([r["err_g_vs_dutta"] for r in rows])
    errq = np.array([r["err_q_vs_dutta"] for r in rows if r["case"] != "Venera 8"])
    summary = {"rms_err_g_vs_dutta": float(np.sqrt(np.mean(errs ** 2))), "max_abs_err_g": float(np.max(np.abs(errs))),
               "rms_err_q_vs_dutta_excl_venera8": float(np.sqrt(np.mean(errq ** 2)))}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "entry_validation.json").write_text(json.dumps({"generated_by": "python scripts/venus_entry_validation.py",
                                                            "rows": rows, "davinci_beta_sweep": dav,
                                                            "vesper": vesper, "summary": summary}, indent=1),
                                               encoding="utf-8")
    lines = ["| Case | β (kg/m²) | γ (°) | V (km/s) | peak g: ours / Dutta (err) | flown g (err) | peak q kW/cm²: ours / Dutta (err) | Mach 0.8 alt. ours (event) |",
             "|---|---:|---:|---:|---|---|---|---|"]
    for r in rows:
        fl = f"{r['flight_g']} ({100 * r['err_g_vs_flight']:+.0f} %)" if "flight_g" in r else "—"
        ev = f"{r['mach08_km']:.1f} km ({r['event_km']:.0f} km)" if "event_km" in r else f"{r['mach08_km']:.1f} km"
        lines.append(f"| {r['case']} | {r['beta']} | {r['gamma_deg']} | {r['V_km_s']} | {r['peak_g']:.0f} / {r['dutta_g']} "
                     f"({100 * r['err_g_vs_dutta']:+.0f} %) | {fl} | {r['peak_q_kW_cm2']:.1f} / {r['dutta_q_kW_cm2']} "
                     f"({100 * r['err_q_vs_dutta']:+.0f} %) | {ev} |")
    (OUT / "entry_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
