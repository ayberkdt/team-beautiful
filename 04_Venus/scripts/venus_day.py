"""Competition-day command for the LuGus slot: Venus concept card JSON → concept trade, simulator parameters and
slide figures.

    python 04_Venus/scripts/venus_day.py prev_guess/04_Venus/cards/venus_rehearsal.json
    python 04_Venus/scripts/venus_day.py --final        # LuGus final (VESPER rotorcraft) -> 04_Venus/outputs/

Writes ``<card folder>/out/<card>/result.json``, ``result.md``, ``vehicles_for_simulator.json`` (one block per
concept: mass, buoyant force, rotor/wing area, drag area, power — the numbers a Liftoff/Unity flight model needs) and
three English slide figures (datawiz, sunum-tam): ``V1_power_altitude``, ``V2_environment`` and
``V3_station_keeping``. Physics: ``aerokit.planetary``; every vehicle number is from the card.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from day_common import audit_summary, console_text, progress, protect_streams, wants_help  # noqa: E402

from aerokit import planetary as P  # noqa: E402
from aerokit import venus_flight as VF  # noqa: E402

GASES = {"He": P.M_HE, "H2": P.M_H2, "N2": P.M_N2, "air": P.M_AIR_EARTH}


def power(c: dict, h: float) -> float:
    """Electrical power [W] to stay aloft at altitude ``h`` [m] (hover for rotors, level flight for wings)."""
    s = P.venus_atmosphere(h)
    if c["kind"] == "rotor":
        gas = GASES[c.get("gas", "He")]
        shaft = P.assisted_hover_power(c["mass_kg"], h, gas, c.get("gas_volume_m3", 0.0), c["rotor_area_m2"],
                                       c["figure_of_merit"])
        return shaft / c["electrical_efficiency"]
    v = P.level_flight_speed(c["mass_kg"], c["wing_area_m2"], c["CL"], s.rho, s.g)
    return P.level_flight_power(c["mass_kg"], v, c["LD"], c["electrical_efficiency"], s.g)


def run(card: dict) -> dict:
    h_op = card["operating_altitude_km"] * 1e3
    sol = card["solar"]
    solar_avg = P.solar_power(sol["panel_area_m2"], sol["efficiency"], h_op, upward_ratio=sol["upward_ratio"])
    solar_peak = P.solar_power(sol["panel_area_m2"], sol["efficiency"], h_op, sun_factor=1.0,
                               upward_ratio=sol["upward_ratio"])
    s = P.venus_atmosphere(h_op)
    rows, sim = [], []
    for c in card["concepts"]:
        p = power(c, h_op)
        lift = (P.buoyant_lift_per_m3(h_op, GASES[c.get("gas", "He")]) * c.get("gas_volume_m3", 0.0)
                if c["kind"] == "rotor" else 0.0)
        row = {"concept": c["name"], "power_W": p, "specific_power_W_kg": p / c["mass_kg"],
               "buoyancy_share": lift / (c["mass_kg"] * s.g),
               "panel_m2_for_day_average": p / (solar_avg / sol["panel_area_m2"])}
        if c["kind"] == "wing":
            row["airspeed_ms"] = P.level_flight_speed(c["mass_kg"], c["wing_area_m2"], c["CL"], s.rho, s.g)
        rows.append(row)
        sim.append({"name": c["name"], "kind": c["kind"], "mass_kg": c["mass_kg"],
                    "weight_N": c["mass_kg"] * s.g, "buoyant_force_N": lift,
                    "rotor_disk_area_m2": c.get("rotor_area_m2"), "wing_area_m2": c.get("wing_area_m2"),
                    "power_to_stay_aloft_W": p, "air_density_kg_m3": s.rho, "gravity_m_s2": s.g,
                    "altitude_m": h_op, "zonal_wind_m_s": P.venus_zonal_wind(h_op)})
    sk = card["station_keeping"]
    wind = P.venus_zonal_wind(h_op)
    hold = P.envelope_drag_power(sk["envelope_m3"], wind, h_op, sk["drag_coefficient"])
    return {"card": card["name"], "note": card.get("note", ""), "altitude_km": card["operating_altitude_km"],
            "T_C": s.T - 273.15, "p_bar": s.p / 1e5, "rho": s.rho, "g": s.g, "wind_ms": wind,
            "solar_avg_W": solar_avg, "solar_peak_W": solar_peak, "solar_note": sol["note"],
            "panel_m2": sol["panel_area_m2"], "concepts": rows, "simulator": sim,
            "station_keeping_W": hold, "envelope_m3": sk["envelope_m3"]}


def mission(card: dict) -> tuple[dict, VF.FlightRun] | None:
    """Fly the card's mission with ``aerokit.venus_flight`` (time-stepped, rotors + superpressure cell + battery +
    solar + hull temperature); ``None`` if the card has no mission block."""
    if "mission" not in card:
        return None
    m = card["mission"]
    drone = VF.VenusDrone(**m.get("vehicle", {}))
    run_ = VF.simulate_mission(drone, m["steps"], m["start_km"], dt=m.get("dt_s", 0.5))
    summary = {"float_altitude_km": VF.float_altitude(drone) / 1e3, "duration_h": float(run_.t[-1]) / 3600,
               "drift_km": float(run_.x[-1]) / 1e3, "battery_min_Wh": float(run_.energy_Wh.min()),
               "battery_end_Wh": float(run_.energy_Wh[-1]), "battery_Wh": drone.battery_Wh,
               "power_max_W": float(run_.power.max()), "hull_max_C": float(run_.T_hull_C.max()),
               "temp_limit_C": drone.temp_limit_C, "time_over_temp_min": run_.time_over_temp_s / 60,
               "brownout": run_.brownout, "events": [{"t_s": t, "event": e} for t, e in run_.events],
               "steps": m["steps"]}
    return summary, run_


def markdown(out: dict) -> str:
    L = [f"# {out['card']}", "", out["note"], "",
         f"## Operating point: {out['altitude_km']:.0f} km", "",
         f"{out['T_C']:.0f} °C, {out['p_bar']:.2f} bar, ρ {out['rho']:.3f} kg/m³, g {out['g']:.2f} m/s², zonal wind "
         f"{out['wind_ms']:.0f} m/s. A {out['panel_m2']:g} m² bifacial panel gives {out['solar_avg_W']:.0f} W "
         f"averaged over a solar day ({out['solar_peak_W']:.0f} W with the Sun overhead).", "",
         "| Concept | Power to stay aloft (W) | Specific power (W/kg) | Weight carried by gas | Panel for day "
         "average (m²) |", "|---|---:|---:|---:|---:|"]
    for r in sorted(out["concepts"], key=lambda r: r["power_W"]):
        L.append(f"| {r['concept']} | {r['power_W']:.0f} | {r['specific_power_W_kg']:.0f} | "
                 f"{100 * r['buoyancy_share']:.0f} % | {r['panel_m2_for_day_average']:.1f} |")
    L += ["", f"Holding position against the {out['wind_ms']:.0f} m/s wind with a {out['envelope_m3']:g} m³ envelope "
          f"would take {out['station_keeping_W'] / 1e3:.0f} kW: live in the air-mass frame and drift.", "",
          "Simulator parameters: `vehicles_for_simulator.json` (SI). Environment profile: "
          "`prev_guess/00_general/challenges_2026/venus_environment.json`.", ""]
    if "mission" in out:
        m = out["mission"]
        L += ["## Mission flown (time-stepped: superpressure He cell, rotors, battery, solar, hull temperature)", "",
              f"Float altitude of the cell alone {m['float_altitude_km']:.1f} km. Mission {m['duration_h']:.1f} h, "
              f"drifted {m['drift_km']:.0f} km east with the wind. Battery lowest {m['battery_min_Wh']:.0f} of "
              f"{m['battery_Wh']:.0f} Wh, end {m['battery_end_Wh']:.0f} Wh; peak draw {m['power_max_W']:.0f} W. "
              f"Hull peak {m['hull_max_C']:.0f} °C, above the {m['temp_limit_C']:.0f} °C electronics limit for "
              f"{m['time_over_temp_min']:.0f} min." + (" Battery ran empty." if m["brownout"] else ""), "",
              "| Time (h) | Event |", "|---:|---|"]
        L += [f"| {e['t_s'] / 3600:.2f} | {e['event']} |" for e in m["events"]]
        L += ["", "Replay for the simulator: `mission_replay.json` (1 Hz frames, SI, temperatures in °C).", ""]
    return "\n".join(L)


def figures(out: dict, card: dict, folder: Path, flight: VF.FlightRun | None = None) -> None:
    import datawiz as dw
    S = dw.Seti(str(folder / "venus.seti.json"), hedef="sunum-tam")
    S.nicelik("alt", "Altitude", "km", eksen="y")
    S.nicelik("pw", "Electrical power to stay aloft", "W", eksen="x")
    S.nicelik("temp", "Temperature", "°C", eksen="x")
    S.nicelik("rho", "Density, log scale", "kg/m³", eksen="x")
    S.nicelik("wind", "Zonal wind", "m/s", eksen="x")
    S.nicelik("speed", "Airspeed through the air mass", "m/s", eksen="x")
    S.nicelik("drag", "Power to push the envelope, log scale", "W", eksen="y", olcek="log")
    S.nicelik("hours", "Mission time", "h", eksen="x")
    S.nicelik("hull", "Hull temperature", "°C", eksen="y")
    S.nicelik("batt", "Battery", "Wh", eksen="y")
    names = [c["name"] for c in card["concepts"]]
    for n in names:
        S.varlik(n)
    S.varlik("Solar, day average", baglam=True)
    S.varlik("Venus", renk="#000000", cizgi="-")     # single-series figures: black, solid, full contrast
    for _ in range(2):
        _slides(S, out, card, folder, names, flight)
        if S.d.get("kenar_mm"):
            break
        left, bottom, right, top = S.kenar_oner()
        S.kenar(left, bottom, right + 14.0, top)


def _slides(S, out: dict, card: dict, folder: Path, names: list[str], flight: VF.FlightRun | None = None) -> None:
    import datawiz as dw
    lo, hi = card["altitude_range_km"]
    alt = np.linspace(lo, hi, 60)
    fig, ax = S.figur(oran=0.55)
    for c in card["concepts"]:
        pw = [power(c, a * 1e3) for a in alt]
        kw = S.stil(c["name"])
        floats = [a for a, p in zip(alt, pw, strict=True) if p == 0.0]
        if floats:                                  # its gas carries all the weight there
            kw["label"] = f"{c['name']} (0 W below {max(floats):.0f} km)"
        ax.plot(pw, alt, **kw)
    sol = card["solar"]
    a_sol = alt[alt >= P.SOLAR_FRACTION_ANCHORS[0][0]]
    ax.plot([P.solar_power(sol["panel_area_m2"], sol["efficiency"], a * 1e3, upward_ratio=sol["upward_ratio"])
             for a in a_sol], a_sol, **S.stil("Solar, day average"))
    ax.set_xlim(0, None)
    S.eksen(ax, x="pw", y="alt")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(folder / "V1_power_altitude"), sessiz=True)

    alt = np.arange(0.0, 81.0, 1.0)
    st = [P.venus_atmosphere(a * 1e3) for a in alt]
    fig, axs = S.figur(oran=0.55, ncols=3, sharey=True)
    axs[0].plot([s.T - 273.15 for s in st], alt, **S.stil("Venus"))
    axs[1].plot([s.rho for s in st], alt, **S.stil("Venus"))
    axs[1].set_xscale("log")  # datawiz: izin density spans 5 decades; axis name says log scale
    from matplotlib.ticker import FuncFormatter
    axs[1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
    axs[2].plot([P.venus_zonal_wind(a * 1e3) for a in alt], alt, **S.stil("Venus"))
    for a, q in zip(axs, ("temp", "rho", "wind"), strict=True):
        S.eksen(a, x=q, y="alt")
        a.axhspan(50, 60, color="0.92", zorder=0)
    for a in axs[1:]:
        a.set_ylabel("")
    dw.notlar.referans(axs[0], x=0.0, metin="0 °C")
    axs[0].annotate("grey: 50-60 km,\nEarth-like p, T", (0.98, 67), xycoords=("axes fraction", "data"),
                    ha="right", va="center", color=S.renk("Venus"))      # empty corner: the profile is at T < 0 there
    S.kaydet(fig, str(folder / "V2_environment"), sessiz=True)

    sk = card["station_keeping"]
    v = np.linspace(sk["airspeeds_ms"][0], sk["airspeeds_ms"][1], 100)
    h_op = card["operating_altitude_km"] * 1e3
    fig, ax = S.figur(oran=0.55)
    ax.plot(v, [P.envelope_drag_power(sk["envelope_m3"], x, h_op, sk["drag_coefficient"]) for x in v],
            **S.stil("Venus"))
    S.eksen(ax, x="speed", y="drag")
    ax.set_yscale("log")  # datawiz: izin power spans 5 decades; axis name says log scale
    ax.set_ylim(10, 1e6)
    dw.notlar.referans(ax, x=out["wind_ms"], metin=f"wind at {out['altitude_km']:.0f} km")
    best = min(r["power_W"] for r in out["concepts"])
    dw.notlar.referans(ax, y=best)
    dw.notlar.ok(ax, (35.0, best), f"staying aloft, best concept: {best:.0f} W", nokta=False)
    S.kaydet(fig, str(folder / "V3_station_keeping"), sessiz=True)

    if flight is not None:
        hrs = flight.t / 3600
        # each panel's quantity name sits above its top-left corner: leave room for it between the panels
        fig, axs = S.figur(oran=0.95, nrows=3, sharex=True, gridspec_kw={"hspace": 0.75})
        axs[0].plot(hrs, flight.z / 1e3, **S.stil("Venus"))
        axs[1].plot(hrs, flight.T_hull_C, **S.stil("Venus"))
        axs[2].plot(hrs, flight.energy_Wh, **S.stil("Venus"))
        for a, q in zip(axs, ("alt", "hull", "batt"), strict=True):
            S.eksen(a, x="hours", y=q)
        for a in axs[:-1]:
            a.set_xlabel("")
        axs[2].set_ylim(0, None)
        z_km = flight.z / 1e3
        axs[0].set_ylim(z_km.min() - 1.0, z_km.max() + 1.0)
        dw.notlar.referans(axs[1], y=out["mission"]["temp_limit_C"], metin="electronics limit")
        S.kaydet(fig, str(folder / "V4_mission"), sessiz=True)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0].lower().lstrip("-") == "final":   # LuGus final 2026: VESPER pipeline (04_Venus/scripts/venus_final.py)
        import venus_final

        return venus_final.main(argv[1:])
    if wants_help(argv):
        print(console_text(__doc__))
        return 0 if argv else 2
    protect_streams()
    path = Path(argv[0])
    card = json.loads(path.read_text(encoding="utf-8"))
    out = run(card)
    flown = mission(card)
    flight = None
    if flown is not None:
        progress("flying the mission (time-stepped simulation)")
        out["mission"], flight = flown
    folder = path.parent / "out" / path.stem
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    (folder / "result.md").write_text(markdown(out), encoding="utf-8")
    (folder / "vehicles_for_simulator.json").write_text(json.dumps(
        {"units": "SI", "source": "04_Venus/scripts/venus_day.py (aerokit.planetary)", "vehicles": out["simulator"]},
        indent=1, default=float), encoding="utf-8")
    if flight is not None:
        (folder / "mission_replay.json").write_text(json.dumps(
            {"units": "SI, temperatures in degC", "source": "04_Venus/scripts/venus_day.py (aerokit.venus_flight)",
             "frames": VF.replay(flight, card["mission"].get("replay_every_s", 1.0))}), encoding="utf-8")
    progress("drawing and auditing the slide figures")
    figures(out, card, folder, flight)
    errors, audit = audit_summary(folder)
    best = min(out["concepts"], key=lambda r: r["power_W"])
    print(console_text(markdown(out)))
    print(console_text(audit))
    print(console_text(f"Result: {best['concept']} stays aloft on {best['power_W']:.0f} W at "
                       f"{out['altitude_km']:.0f} km. Next: load {folder / 'vehicles_for_simulator.json'} and "
                       "prev_guess/00_general/challenges_2026/venus_environment.json into the simulator"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
