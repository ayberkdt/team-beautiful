"""Design-space sweep of the VESPER hexacopter: rotor diameter × hover tip speed × solar option.

    python 04_Venus/scripts/venus_trade.py [--quick]

Writes ``04_Venus/outputs/trade_sizing.json`` (one record per point: gross mass, breakdown, hover and
bucket power, solar output at overhead sun, cos-zenith above which the array sustains hover / loiter). Physics:
:func:`aerokit.venus.sizing.close` (BEMT hover, MSH-style mass relations; assumptions listed there).
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.venus import sizing as S  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs" / "trade_sizing.json"


def main(argv: list[str]) -> int:
    quick = "--quick" in argv
    Ds = (1.6, 2.2) if quick else (1.4, 1.7, 2.0, 2.3, 2.6, 2.9)
    Vts = (70.0,) if quick else (55.0, 70.0, 90.0, 115.0)
    options = ("deck",) if quick else ("deck", "halo", "blades")
    rows = []
    t0 = time.time()
    for opt in options:
        req = replace(S.Requirements(), solar_option=opt)
        for D in Ds:
            for vt in Vts:
                rec = {"D_m": D, "V_tip_m_s": vt, "solar_option": opt}
                try:
                    d = S.close(D, vt, req)
                    sm = d.summary()
                    rec.update({k: sm[k] for k in ("gross_kg", "P_hover_elec_W", "P_bucket_elec_W", "V_bucket",
                                                   "P_solar_overhead_W", "solar_area_m2", "sustain_mu0_hover",
                                                   "sustain_mu0_loiter", "rpm", "FM", "tip_mach", "re75",
                                                   "theta75_deg", "solidity", "disk_loading_N_m2", "battery_Wh",
                                                   "arm_m", "converged")})
                    rec["breakdown"] = sm["breakdown"]
                except ValueError as e:
                    rec["error"] = str(e)
                rows.append(rec)
                print(f"[{time.time() - t0:6.0f} s] {opt:6s} D {D:.1f} Vt {vt:5.1f} -> "
                      f"{rec.get('gross_kg', float('nan')):.1f} kg  hover {rec.get('P_hover_elec_W', float('nan')):.0f} W"
                      f"  loiter {rec.get('P_bucket_elec_W', float('nan')):.0f} W  sun {rec.get('P_solar_overhead_W', float('nan')):.0f} W"
                      f"  mu0* {rec.get('sustain_mu0_loiter')}  {rec.get('error', '')}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"generated_by": "python 04_Venus/scripts/venus_trade.py", "requirements": repr(S.Requirements()),
                               "mass_model": repr(S.MassModel()), "rows": rows}, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
