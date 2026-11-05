"""Independent cross-checks of VESPER's headline numbers with simpler methods (no BEMT, no simulation).

    python scripts/venus_crosscheck.py

1. Hover power — ideal momentum theory ``P = W^1.5 / √(2ρA)`` divided by a figure-of-merit range 0.55–0.75 (measured
   rotor FM: Harrington 1951 0.615/0.635, Knight & Hefner 1937 0.56–0.62, Ingenuity chamber ~0.63 — agent notes
   [D-ag]) and the drive efficiency, plus the 55 W system load; density over the probe envelope (thin/dense).
2. Mass — top-down payload and battery fractions of studied/flown rotorcraft (Mars Science Helicopter baseline:
   17.69 kg gross, 2.02 kg payload, 2.31 kg battery; max-capability 31.2 kg with 5 kg payload; Ingenuity 1.8 kg with a
   0.273 kg battery — notes C_johnson2020_msh, C_balaram2018 [D-ag]) applied to VESPER's 3 kg payload, then the
   Venus-only items (solar deck, acid coating, thermal, Ti vessel growth) added on top.
3. Solar margin — closed-form sun threshold from the in-cloud law ``P = P₀ μ(μ+⅔)/(5/3)``: ``μ* = (−⅔ + √(4/9 +
   (20/3) P_l/P₀))/2``; flight window ``= 2 arccos(μ*)/(2π) × T_day``; hand integral of the array energy over the window
   against the loiter demand.

Writes ``studies/final_2026/venus/out/crosscheck.json`` and ``.md``.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402

OUT = ROOT / "studies" / "final_2026" / "venus" / "out"


def main(argv: list[str]) -> int:
    res = DES.baseline()
    d = res["design"]
    run = res["mission"]
    h = DES.BASELINE.cruise_km * 1e3
    out: dict = {"generated_by": "python scripts/venus_crosscheck.py"}

    # 1. hover power
    A_disk = d.system.disk_area
    eta = d.system.drive_efficiency
    rows = []
    for case in ("thin", "mean", "dense"):
        s = A.state(h, case)
        W = d.gross_kg * s.g
        p_ideal = W ** 1.5 / math.sqrt(2.0 * s.rho * A_disk)
        for fm in (0.55, 0.65, 0.75):
            rows.append({"case": case, "FM": fm, "electric_W": p_ideal / fm / eta + d.P_sys_W, "ideal_W": p_ideal})
    lo = min(r["electric_W"] for r in rows)
    hi = max(r["electric_W"] for r in rows)
    out["hover_power"] = {"bemt_W": d.P_hover_elec_W, "momentum_range_W": [lo, hi], "rows": rows,
                          "bemt_FM": d.hover.FM, "drive_efficiency": eta}

    # 2. mass, top-down
    payload = d.req.payload_kg
    venus_items = d.breakdown["solar"] + d.breakdown["coating"] + d.breakdown["thermal"]
    refs = {"MSH baseline (payload 11.4 %)": 2.02 / 17.69, "MSH max capability (payload 16.0 %)": 5.0 / 31.2}
    mass_rows = []
    for name, f in refs.items():
        core = payload / f
        mass_rows.append({"reference": name, "payload_fraction": f, "mars_like_kg": core,
                          "plus_venus_items_kg": core + venus_items * 1.2})
    out["mass"] = {"vesper_kg": d.gross_kg, "venus_only_items_kg": venus_items, "rows": mass_rows,
                   "battery_fraction_vesper": d.breakdown["battery"] / d.gross_kg,
                   "battery_fraction_msh": 2.31 / 17.69, "battery_fraction_ingenuity": 0.273 / 1.8,
                   "payload_fraction_vesper": payload / d.gross_kg}

    # 3. solar margin by hand
    P0 = d.P_solar_overhead_W
    Pl = d.P_bucket_elec_W
    mu_star = (-2.0 / 3.0 + math.sqrt(4.0 / 9.0 + (20.0 / 3.0) * Pl / P0)) / 2.0
    T_day = PW.air_mass_day_s(A.zonal_wind(h), h) / 3600.0
    window_h = 2.0 * math.acos(mu_star) / (2.0 * math.pi) * T_day
    Hs = np.linspace(-math.acos(mu_star), math.acos(mu_star), 2001)
    mu = np.cos(Hs)
    p = P0 * mu * (mu + 2.0 / 3.0) / (5.0 / 3.0)
    e_solar = float(np.trapezoid(p, Hs)) / (2.0 * math.pi) * T_day           # Wh in the window
    e_need = Pl * window_h
    daylight = P0 * (math.pi / 2 + 4.0 / 3.0) / (5.0 / 3.0) / (2.0 * math.pi) * T_day   # Wh over the whole daylight
    out["solar"] = {"P0_W": P0, "loiter_W": Pl, "mu_star_hand": mu_star, "mu_star_code": d.sustain_mu0_loiter,
                    "window_h_hand": window_h, "battery_tail_h": d.battery_Wh / Pl,
                    "flight_h_hand": window_h + d.battery_Wh / Pl, "flight_h_sim": run.flight_time_s / 3600.0,
                    "energy_window_solar_kWh": e_solar / 1e3, "energy_window_need_kWh": e_need / 1e3,
                    "energy_margin_window": e_solar / e_need, "daylight_solar_kWh": daylight / 1e3,
                    "full_cycle_need_kWh": Pl * T_day / 1e3, "air_mass_day_h": T_day}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "crosscheck.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    hp, so = out["hover_power"], out["solar"]
    md = ["| Quantity | Main method | Simple method | Spread |", "|---|---|---|---|",
          f"| Hover electric power at 55 km | BEMT {hp['bemt_W']:.0f} W (FM {hp['bemt_FM']:.2f}) | momentum theory, FM 0.55–0.75, "
          f"thin–dense air: {hp['momentum_range_W'][0]:.0f}–{hp['momentum_range_W'][1]:.0f} W | "
          f"{100 * (hp['momentum_range_W'][0] / hp['bemt_W'] - 1):+.0f} … {100 * (hp['momentum_range_W'][1] / hp['bemt_W'] - 1):+.0f} % |",
          f"| Gross mass | closed budget {out['mass']['vesper_kg']:.1f} kg | MSH payload fraction 11–16 % → "
          f"{mass_rows[1]['mars_like_kg']:.0f}–{mass_rows[0]['mars_like_kg']:.0f} kg Mars-like, "
          f"+{venus_items * 1.2:.1f} kg Venus-only items → {mass_rows[1]['plus_venus_items_kg']:.0f}–{mass_rows[0]['plus_venus_items_kg']:.0f} kg | "
          f"{100 * (mass_rows[1]['plus_venus_items_kg'] / out['mass']['vesper_kg'] - 1):+.0f} … "
          f"{100 * (mass_rows[0]['plus_venus_items_kg'] / out['mass']['vesper_kg'] - 1):+.0f} % |",
          f"| Sun threshold cos z | code {so['mu_star_code']:.3f} | closed form {so['mu_star_hand']:.3f} | "
          f"{100 * (so['mu_star_hand'] / so['mu_star_code'] - 1):+.1f} % |",
          f"| Flight time | simulation {so['flight_h_sim']:.1f} h | window {so['window_h_hand']:.1f} h + battery "
          f"{so['battery_tail_h']:.1f} h = {so['flight_h_hand']:.1f} h | {100 * (so['flight_h_hand'] / so['flight_h_sim'] - 1):+.0f} % |",
          f"| Solar energy margin in the window | — | {so['energy_window_solar_kWh']:.0f} kWh in / "
          f"{so['energy_window_need_kWh']:.0f} kWh needed = {so['energy_margin_window']:.2f}× | — |",
          f"| Whole air-mass day | — | daylight array energy {so['daylight_solar_kWh']:.0f} kWh vs "
          f"{so['full_cycle_need_kWh']:.0f} kWh to loiter all {so['air_mass_day_h']:.0f} h | "
          f"{so['daylight_solar_kWh'] / so['full_cycle_need_kWh']:.2f}× |"]
    (OUT / "crosscheck.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
