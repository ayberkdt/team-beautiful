"""Markdown summary of the ``venus_final`` numbers (``result.md``)."""
from __future__ import annotations


def markdown(out: dict) -> str:
    v, e, m = out["vehicle"], out["entry"], out["mission"]
    a = out["atmosphere_55km"]
    lines = ["# VESPER — computed numbers (python 04_Venus/code/pipeline/venus_day.py --final)", "",
             "| Quantity | Value | Tag |", "|---|---:|---|",
             f"| 55 km: T, p, ρ (Pioneer Venus mean) | {a['T_C']:.1f} °C, {a['p_bar']:.3f} bar, {a['rho']:.3f} kg/m³ | D/K |",
             f"| Gross mass | {v['gross_kg']:.1f} kg | K |",
             f"| Rotors | 6 × {v['D']:.1f} m, {v['rpm']:.0f} rpm, tip Mach {v['tip_mach']:.2f}, Re₀.₇₅ {v['re75']:.2g}, FM {v['FM']:.2f} | K |",
             f"| Hover / loiter electric power | {v['P_hover_elec_W']:.0f} W / {v['P_bucket_elec_W']:.0f} W at {v['V_bucket']:.1f} m/s | K |",
             f"| Solar overhead / sustains loiter above cos z | {v['P_solar_overhead_W']:.0f} W / {v['sustain_mu0_loiter']:.2f} | K |",
             f"| Battery | {v['battery_Wh']:.0f} Wh | K |",
             f"| Entry | {e['m_entry']:.0f} kg, β {e['beta']:.1f} kg/m², {e['VE'] / 1e3:.2f} km/s at {e['gamma_deg']}° | K |",
             f"| Peak deceleration / heating | {e['peak_g']:.0f} g; {e['peak_qconv_W_cm2']:.0f} + {e['peak_qrad_W_cm2']:.0f} W/cm²; {e['heat_load_kJ_cm2']:.1f} kJ/cm² (PV large probe {e['pv_peak_g']:.0f} g) | K |",
             f"| Parachute | opens {e['chute_km']:.1f} km, {e['chute_s']:.0f} s to release, {e['release_rate']:.1f} m/s at release | K |",
             f"| Release altitude loss | {e['pullout_loss_m']:.0f} m pre-spun vs {e['drop_loss_m']:.0f} m dropped unspun | K |",
             f"| Mission | {m['flight_h']:.1f} h flight, {m['sustained_h']:.1f} h on sunlight, {m['drift_km']:.0f} km drift | K |",
             f"| Relay (1000 km orbit, 5 W UHF) | {out['link']['pass_min']:.1f} min passes, {out['link']['Mbit_per_pass']:.0f} Mbit/pass | K |",
             f"| BEMT validation (torque, 27 points) | rms {100 * out['bemt_validation']['rms_error']:.1f} % | K vs D-ag |",
             f"| Hybrid alternative (neutral He cell) | {out['hybrid']['diameter_m']:.1f} m sphere, +{out['hybrid']['envelope_kg']:.0f} kg envelope | K |",
             "", "Events:", ""]
    lines += [f"- {t / 3600:.2f} h — {ev}" for t, ev in m["events"]]
    return "\n".join(lines) + "\n"
