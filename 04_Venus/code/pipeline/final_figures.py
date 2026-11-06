"""Figures F1-F15 of ``venus_final`` (datawiz, audited on save); ``OUT`` is the folder they go to."""
from __future__ import annotations

import math

import numpy as np

from aerokit.venus import atmosphere as A
from aerokit.venus import risk as RK


def figures(c: dict, OUT) -> None:
    import datawiz as dw

    out, res = c["out"], c["res"]
    d = res["design"]
    S = dw.Seti(str(OUT / "vesper.seti.json"), hedef="sunum-tam")
    S.nicelik("alt", "Altitude", "km", eksen="y")
    S.nicelik("temp", "Temperature", "°C", eksen="x")
    S.nicelik("rho", "Density", "kg/m³", eksen="x")
    S.nicelik("wind", "Westward wind", "m/s", eksen="x")
    S.nicelik("pw", "Electrical power", "kW", eksen="x")
    S.nicelik("t_s", "Time from entry interface", "s", eksen="x")
    S.nicelik("g", "Deceleration", "g", eksen="y")
    S.nicelik("q", "Stagnation heat flux", "W/cm²", eksen="y")
    S.nicelik("hours", "Mission time", "h", eksen="x")
    S.nicelik("alt2", "Altitude", "km", eksen="y")
    S.nicelik("pwy", "Power", "kW", eksen="y")
    S.nicelik("soc", "Battery charge", "Wh", eksen="y")
    S.nicelik("mass", "Mass", "kg", eksen="x")
    S.nicelik("D", "Rotor diameter", "m", eksen="x")
    S.nicelik("gross", "Gross mass", "kg", eksen="y")
    S.nicelik("mu", "Sun height needed, cos z", "", eksen="y")
    S.nicelik("cq_m", "Measured torque coefficient", "", eksen="x")
    S.nicelik("cq_p", "Predicted torque coefficient", "", eksen="y")
    S.nicelik("hrs", "Flight time", "h", eksen="x")
    S.nicelik("L", "Likelihood", "", eksen="x")
    S.nicelik("C", "Consequence", "", eksen="y")
    for n in ("VESPER", "Hover", "Loiter at bucket speed", "Sun overhead", "Knight & Hefner 1937",
              "Harrington 1951", "tip 55 m/s"):
        S.varlik(n)
    S.varlik("tip 115 m/s", renk=dw.renk.koyu_ton("#f0e442"), cizgi="--")
    S.varlik("Sun at cos z 0.7", renk=S.renk("Sun overhead"), cizgi="--", renk_paylas=True)
    S.varlik("tip 70 m/s (VESPER)", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("D 2.6 m, geared 5:1 (VESPER)", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("D 2.6 m, direct drive", renk=S.renk("tip 55 m/s"), cizgi=":", renk_paylas=True)
    S.varlik("D 2.3 m, geared 5:1", renk=S.renk("Harrington 1951"), cizgi="--", renk_paylas=True)
    S.varlik("Pioneer Venus probes", renk=S.renk("Harrington 1951"), renk_paylas=True)
    S.varlik("Venera and Vega", renk=S.renk("Knight & Hefner 1937"), renk_paylas=True)
    S.varlik("Pull-out in forward flight", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("Pull-out straight down", renk=S.renk("tip 55 m/s"), cizgi=":", renk_paylas=True)
    S.varlik("Rotors windmilling", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("Rotors failed", renk=S.renk("Hover"), cizgi="--", renk_paylas=True)
    S.varlik("Pioneer Venus", baglam=True)
    S.varlik("Probe envelope", baglam=True)

    # F1 altitude justification ---------------------------------------------------------------------------------
    km = np.arange(45, 64.01, 0.25)
    h = km * 1e3
    mean = [A.state(x) for x in h]
    lo = [A.state(x, "min") for x in h]
    hi = [A.state(x, "max") for x in h]
    wl, wm, wh = zip(*[A.zonal_wind_band(x) for x in h])
    fig, axs = S.figur(oran=0.55, ncols=3, sharey=True)
    band = dw.renk.alan_tonu(S.renk("VESPER"))
    for ax in axs:
        ax.axhspan(53, 58, color=dw.renk.alan_tonu("#7a7a7a", acik=0.75), lw=0, zorder=0)
    axs[0].fill_betweenx(km, [s.T - 273.15 for s in lo], [s.T - 273.15 for s in hi], color=band, lw=0)
    axs[0].plot([s.T - 273.15 for s in mean], km, **S.stil("VESPER"))
    axs[0].axvspan(0, 45, color=dw.renk.alan_tonu("#009E73", acik=0.8), lw=0, zorder=0)
    axs[1].fill_betweenx(km, [s.rho for s in lo], [s.rho for s in hi], color=band, lw=0)
    axs[1].plot([s.rho for s in mean], km, **S.stil("VESPER"))
    axs[2].fill_betweenx(km, wl, wh, color=band, lw=0)
    axs[2].plot(wm, km, **S.stil("VESPER"))
    for ax, q in zip(axs, ("temp", "rho", "wind")):
        S.eksen(ax, x=q, y="alt")
    for ax in axs[1:]:
        ax.set_ylabel("")
    axs[0].set_xticks([0, 50, 100])
    axs[0].text(22.5, 46.0, "Li-ion\ncharges\n0–45 °C", ha="center", va="bottom", fontsize=plt_size() * 0.8,
                color="#00694d")
    axs[1].text(2.6, 55.5, "operating\nband\n53–58 km", ha="right", va="center", fontsize=plt_size() * 0.8,
                color="#4d4d4d")
    S.kaydet(fig, str(OUT / "F1_altitude_justification"), sessiz=True)

    # F2 power vs altitude -------------------------------------------------------------------------------------
    rows = out["power_vs_altitude"]
    kms = [r["km"] for r in rows]
    fig, ax = S.figur(oran=0.55)
    for key, name in (("hover_W", "Hover"), ("loiter_W", "Loiter at bucket speed"),
                      ("solar_mu1_W", "Sun overhead"), ("solar_mu07_W", "Sun at cos z 0.7")):
        ax.plot([r[key] / 1e3 for r in rows], kms, **S.stil(name))
    S.eksen(ax, x="pw", y="alt")
    dw.lejant.yerlestir(ax)
    dw.notlar.referans(ax, y=55.0, metin="cruise 55 km")
    S.kaydet(fig, str(OUT / "F2_power_vs_altitude"), sessiz=True)

    # F3 entry --------------------------------------------------------------------------------------------------
    ent, pv = res["entry"], c["pv_run"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    t0 = float(ent.t[int(np.argmax(ent.decel_g))]) - 40.0
    tp = float(pv.t[int(np.argmax(pv.decel_g))]) - 40.0
    m1 = (ent.t >= t0) & (ent.t <= t0 + 80)
    m2 = (pv.t >= tp) & (pv.t <= tp + 80)
    axs[0].plot(ent.t[m1] - t0, ent.decel_g[m1], **S.stil("VESPER"))
    axs[0].plot(pv.t[m2] - tp, pv.decel_g[m2], **S.stil("Pioneer Venus"))
    axs[1].plot(ent.t[m1] - t0, (ent.q_conv[m1] + np.nan_to_num(ent.q_rad[m1])) / 1e4, **S.stil("VESPER"))
    axs[1].plot(pv.t[m2] - tp, (pv.q_conv[m2] + np.nan_to_num(pv.q_rad[m2])) / 1e4, **S.stil("Pioneer Venus"))
    S.eksen(axs[0], x="t_s", y="g")
    S.eksen(axs[1], x="t_s", y="q")
    for ax in axs:
        ax.set_xlabel("Time around peak deceleration (s)")
    gv, gp = float(ent.peak_g), float(pv.peak_g)
    axs[0].text(44.0, gp * 0.92, f"Pioneer Venus\nlarge probe\n{gp:.0f} g", ha="left", va="top",
                fontsize=plt_size() * 0.8, color=S.renk("Pioneer Venus"))
    axs[0].text(50.0, gv + 15.0, f"VESPER {gv:.0f} g", ha="left", va="bottom", fontsize=plt_size() * 0.8,
                color=S.renk("VESPER"))
    qv = float(np.nanmax(ent.q_conv + np.nan_to_num(ent.q_rad))) / 1e4
    axs[1].text(44.0, 4000.0, "Pioneer Venus", ha="left", va="top", fontsize=plt_size() * 0.8,
                color=S.renk("Pioneer Venus"))
    axs[1].text(50.0, qv + 250.0, f"VESPER {qv:.0f}", ha="left", va="bottom", fontsize=plt_size() * 0.8,
                color=S.renk("VESPER"))
    S.kaydet(fig, str(OUT / "F3_entry"), sessiz=True)

    # F4 mass budget ------------------------------------------------------------------------------------------
    bd = dict(d.breakdown)
    nice = {"blades+hubs": "blades + hubs", "arms+hinges": "arms + hinges", "contingency": "contingency 20 %"}
    small = [k for k, v in bd.items() if v < 0.9]
    other = sum(bd.pop(k) for k in small)
    items = {nice.get(k, k): v for k, v in bd.items()}
    items["other: " + ", ".join(small)] = other
    fig, ax = S.figur(oran=0.6)
    dw.ciz.cubuk(ax, list(items.keys()), list(items.values()), renk=S.renk("VESPER"), sirala=True, yatay=True,
                 deger_yaz=True, bicim="{:.1f}")
    S.eksen(ax, x="mass")
    ax.set_ylabel("Component")
    S.kaydet(fig, str(OUT / "F4_mass_budget"), sessiz=True)

    # F5 risk matrix --------------------------------------------------------------------------------------------
    fig, ax = S.figur(oran=0.75)
    for L in range(1, 6):
        for C in range(1, 6):
            band_c = {"red": "#d55e00", "amber": "#e69f00", "green": "#009e73"}[RK.colour_band(L * C)]
            ax.add_patch(__import__("matplotlib").patches.Rectangle((L - 0.5, C - 0.5), 1, 1,
                                                                      color=dw.renk.alan_tonu(band_c, acik=0.75), lw=0))
    offsets = {}
    for r in RK.RISKS:
        key = (r["L2"], r["C2"])
        k = offsets.get(key, 0)
        offsets[key] = k + 1
        x, y = r["L2"] - 0.32 + 0.32 * (k % 3), r["C2"] + 0.25 - 0.25 * (k // 3)
        ax.annotate("", xy=(x, y), xytext=(r["L"], r["C"]),
                    arrowprops=dict(arrowstyle="->", color="#7a7a7a", lw=0.8, shrinkA=6, shrinkB=6))
        ax.text(x, y, r["id"], ha="center", va="center", fontsize=plt_size() * 0.8, color="#000000")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    S.eksen(ax, x="L", y="C")
    ax.set_xlabel("Likelihood (1–5)")
    ax.set_ylabel("Consequence (1–5)")
    S.kaydet(fig, str(OUT / "F5_risk_matrix"), sessiz=True)

    # F6 mission ------------------------------------------------------------------------------------------------
    run = res["mission"]
    hrs = run.t / 3600.0
    fig, axs = S.figur(oran=1.25, nrows=3, sharex=True, gridspec_kw={"hspace": 0.3})
    axs[0].plot(hrs, run.z / 1e3, **S.stil("VESPER"))
    axs[1].plot(hrs, run.p_need / 1e3, **S.stil("Loiter at bucket speed"))
    axs[1].plot(hrs, run.p_solar / 1e3, **S.stil("Sun overhead"))
    axs[2].plot(hrs, run.energy_Wh, **S.stil("VESPER"))
    S.eksen(axs[0], x="hours", y="alt2")
    S.eksen(axs[1], x="hours", y="pwy")
    S.eksen(axs[2], x="hours", y="soc")
    axs[1].lines[1].set_label("Solar array")
    axs[1].lines[0].set_label("Demand")
    for ax in axs[:2]:
        ax.set_xlabel("")
    axs[0].set_ylim(45, 57)
    axs[0].set_yticks([47, 55])
    pmax = float(max(run.p_need.max(), run.p_solar.max())) / 1e3
    axs[1].set_ylim(0, math.ceil(pmax * 1.05))
    axs[1].set_yticks([0, 2 * math.ceil(pmax / 2.0 * 0.5)] if pmax > 2 else [0, 1])
    emax = float(run.energy_Wh.max())
    axs[2].set_ylim(0, emax * 1.1)
    axs[2].set_yticks([0, 1000 * round(emax / 1000.0)])
    dw.etiket.cizgi_sonu(axs[1])
    S.kaydet(fig, str(OUT / "F6_mission"), sessiz=True)

    # F7 trade --------------------------------------------------------------------------------------------------
    if c["trade"]:
        rows = [r for r in c["trade"]["rows"] if r["solar_option"] == "deck" and "error" not in r]
        fig, axs = S.figur(oran=0.55, ncols=2)
        for vt in (55.0, 70.0, 115.0):
            rr = sorted([r for r in rows if r["V_tip_m_s"] == vt], key=lambda r: r["D_m"])
            name = "tip 70 m/s (VESPER)" if vt == 70.0 else f"tip {vt:.0f} m/s"
            axs[0].plot([r["D_m"] for r in rr], [r["gross_kg"] for r in rr], **S.stil(name, isaretli=True))
            pts = [r for r in rr if r["sustain_mu0_loiter"] is not None]
            axs[1].plot([r["D_m"] for r in pts], [r["sustain_mu0_loiter"] for r in pts], **S.stil(name, isaretli=True))
        S.eksen(axs[0], x="D", y="gross")
        S.eksen(axs[1], x="D", y="mu")
        axs[1].set_ylabel("Sun height needed (cos z)")
        dw.lejant.yerlestir(axs[0])
        S.kaydet(fig, str(OUT / "F7_trade"), sessiz=True)

    # F8 BEMT validation ----------------------------------------------------------------------------------------
    val = out["bemt_validation"]
    fig, ax = S.figur(oran=0.75)
    m = np.array(val["measured_CQ"]) * 1e4
    p = np.array(val["predicted_CQ"]) * 1e4
    xs = np.geomspace(m.min() * 0.8, m.max() * 1.25, 20)
    ax.fill_between(xs, xs * 0.9, xs * 1.1, color=dw.renk.alan_tonu("#7a7a7a", acik=0.7), lw=0)
    ax.plot(xs, xs, color="#7a7a7a", lw=0.8)
    for srcname in ("Knight & Hefner 1937", "Harrington 1951"):
        sel = [i for i, s in enumerate(val["source"]) if s.startswith(srcname.split()[0])]
        st = S.stil(srcname, tur="sacilim")
        if srcname.startswith("Harrington"):
            st = dict(st, facecolors="none", edgecolors=st.get("color", st.get("c")), linewidths=1.5)
            st.pop("color", None)
            st.pop("c", None)
        ax.scatter(m[sel], p[sel], **st)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Measured torque coefficient (×10⁻⁴)")
    ax.set_ylabel("Predicted torque coefficient (×10⁻⁴)")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(OUT / "F8_bemt_validation"), sessiz=True)

    # F9 sensitivity --------------------------------------------------------------------------------------------
    if c["sens"]:
        rows = c["sens"]["rows"]
        base = next(r for r in rows if r["case"] == "baseline")["flight_h"]
        names = {"battery cell energy 180 / 280 Wh/kg": ("Battery cell energy", "180", "280 Wh/kg"),
                 "gearbox torque density 12 / 40 N·m/kg": ("Gearbox torque density", "12", "40 N·m/kg"),
                 "solar array efficiency 0.25 / 0.32": ("Solar array efficiency", "25 %", "32 %"),
                 "mass contingency 30 % / 10 %": ("Mass contingency", "30 %", "10 %"),
                 "atmosphere thin / dense (PV envelope)": ("Atmosphere (probe envelope)", "thin", "dense"),
                 "payload 5 kg / 1.5 kg": ("Payload", "5 kg", "1.5 kg"),
                 "cruise altitude 53 / 58 km": ("Cruise altitude", "53 km", "58 km"),
                 "battery reserve 1.0 / 0.25 h hover": ("Battery reserve (hover)", "1 h", "0.25 h"),
                 "blade areal mass 3.3 / 1.5 kg/m²": ("Blade areal mass", "3.3", "1.5 kg/m²"),
                 "motor specific torque 5 / 10 N·m/kg": ("Motor specific torque", "5", "10 N·m/kg")}
        dev = []
        for cs, (nm, la, lb) in names.items():
            a = next((r for r in rows if r.get("case") == cs and r.get("side") == "bad"), None)
            b = next((r for r in rows if r.get("case") == cs and r.get("side") == "good"), None)
            if a is None or b is None:
                continue
            da = (a["flight_h"] - base) if "flight_h" in a else -base
            db = (b["flight_h"] - base) if "flight_h" in b else -base
            dev.append((nm, la + (" (no closure)" if "error" in a else ""), da,
                        lb + (" (no closure)" if "error" in b else ""), db))
        dev.sort(key=lambda x: max(abs(x[2]), abs(x[4])))
        fig, ax = S.figur(oran=0.62)
        y = np.arange(len(dev))
        neg, pos = "#d55e00", "#0072b2"
        for i, (nm, la, da, lb, db) in enumerate(dev):
            for val, lab in ((da, la), (db, lb)):
                col = neg if val < 0 else pos
                if "no closure" in lab:            # no design exists: no bar, a word at the axis
                    ax.text(-0.8, i, lab, ha="right", va="center", fontsize=plt_size() * 0.8,
                            color=dw.renk.koyu_ton(neg))
                    continue
                ax.barh(i, val, height=0.6, color=dw.renk.alan_tonu(col), edgecolor=col, lw=0.8)
                ax.text(val + (-0.8 if val < 0 else 0.8), i, lab, ha="right" if val < 0 else "left", va="center",
                        fontsize=plt_size() * 0.8, color=dw.renk.koyu_ton(col))
        ax.axvline(0, color="#000000", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([x[0] for x in dev])
        lim = max(max(abs(v) for v, lab in ((x[2], x[1]), (x[4], x[3])) if "no closure" not in lab) for x in dev)
        ax.set_xlim(-lim * 1.45, lim * 1.45)
        ax.set_xlabel(f"Change in flight time from the {base:.0f} h baseline (h)")
        ax.set_ylabel("")
        S.kaydet(fig, str(OUT / "F9_sensitivity"), sessiz=True)

    # F10 robustness: flight hours of three rotor sizes under adverse assumptions -------------------------------
    if c["sens"] and c["sens"].get("robustness"):
        rob = c["sens"]["robustness"]
        cases = list(dict.fromkeys(r["case"] for r in rob))
        fig, ax = S.figur(oran=0.6)
        y = np.arange(len(cases))[::-1] + 1.0                       # rows at 1..n: no zero baseline through a row
        variants = ((2.6, 5.0, "D 2.6 m, geared 5:1 (VESPER)"), (2.6, 1.0, "D 2.6 m, direct drive"),
                    (2.3, 5.0, "D 2.3 m, geared 5:1"))
        for k, (Dr, gr, name) in enumerate(variants):
            yy = y + (1 - k) * 0.18                                   # small vertical dodge per variant
            xs = [next((r.get("flight_h", 0.0) for r in rob if r["D_m"] == Dr and r.get("gear_ratio") == gr
                        and r["case"] == cs), 0.0) for cs in cases]
            st = S.stil(name, tur="cizgi", isaretli=True)
            st["linestyle"] = "none"
            st.pop("ls", None)
            keep = [i for i, xv in enumerate(xs) if xv > 0.0]
            ax.plot([xs[i] for i in keep], [yy[i] for i in keep], **st)
        for i, cs in enumerate(cases):                                 # one label per row for designs that do not close
            bad = [("geared" if r.get("gear_ratio", 1.0) > 1 else "direct") + f" {r['D_m']:.1f} m"
                   for r in rob if r["case"] == cs and "error" in r]
            if bad:
                ax.text(0.8, y[i], "no closure: " + ", ".join(bad), ha="left", va="center",
                        fontsize=plt_size() * 0.8, color="#7a3b00")
        ax.set_yticks(y)
        ax.set_yticklabels(cases)
        S.eksen(ax, x="hrs")
        ax.set_ylabel("")
        xmax = max(r.get("flight_h", 0.0) for r in rob)
        ax.set_xlim(0, xmax * 1.15)
        ax.set_ylim(0.4, len(cases) + 1.9)                          # free band above the top row for the legend
        dw.lejant.yerlestir(ax)
        S.kaydet(fig, str(OUT / "F10_robustness"), sessiz=True)
    figures_extra(c, S, dw, OUT)


def figures_extra(c: dict, S, dw, OUT) -> None:
    """F11-F15: entry validation, deployment Monte Carlo, air-mass day + station keeping, terminal descent, margins."""
    out = c["out"]
    # F11 entry validation ---------------------------------------------------------------------------------------
    ev = out["entry_validation"]["rows"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    for grp, name in (("PV", "Pioneer Venus probes"), ("V", "Venera and Vega")):
        sel = [r for r in ev if r["case"].startswith("PV")] if grp == "PV" else [r for r in ev if not r["case"].startswith("PV")]
        axs[0].scatter([r["dutta_g"] for r in sel], [r["peak_g"] for r in sel], zorder=3, **S.stil(name, tur="sacilim"))
        axs[1].scatter([r["dutta_q_kW_cm2"] for r in sel], [r["peak_q_kW_cm2"] for r in sel], zorder=3,
                       **S.stil(name, tur="sacilim"))
    for ax, lo, hi in ((axs[0], 110.0, 560.0), (axs[1], 2.5, 36.0)):
        xs = np.geomspace(lo, hi, 20)
        ax.fill_between(xs, xs * 0.9, xs * 1.1, color=dw.renk.alan_tonu("#7a7a7a", acik=0.7), lw=0, zorder=0)
        ax.plot(xs, xs, color="#7a7a7a", lw=0.8, zorder=1)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_xscale("log")
        ax.set_yscale("log")
    axs[0].set_xlabel("Published peak deceleration (g)")
    axs[0].set_ylabel("Model peak deceleration (g)")
    axs[1].set_xlabel("Published peak heat flux (kW/cm²)")
    axs[1].set_ylabel("Model peak heat flux (kW/cm²)")
    dw.lejant.yerlestir(axs[0])
    S.kaydet(fig, str(OUT / "F11_entry_validation"), sessiz=True)

    # F12 deployment Monte Carlo ---------------------------------------------------------------------------------
    mc = c["mc"]
    fig, ax = S.figur(oran=0.55)
    for proc, name in (("forward", "Pull-out in forward flight"), ("vertical", "Pull-out straight down")):
        x = np.sort(mc[proc].altitude_loss_m)
        ax.step(x, np.arange(1, len(x) + 1) / len(x), where="post", **S.stil(name))
    ax.set_xlabel("Altitude lost after release (m)")
    ax.set_ylabel("Fraction of 300 runs")
    ax.set_ylim(0, 1.02)
    dw.etiket.cizgi_sonu(ax)
    S.kaydet(fig, str(OUT / "F12_deployment_monte_carlo"), sessiz=True)

    # F13 air-mass day and station keeping -----------------------------------------------------------------------
    day, sk = out["air_mass_day"], out["station_keeping"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    hrs = np.array(day["hours"])
    axs[0].axvspan(day["mission_start_h"], day["mission_start_h"] + day["mission_h"],
                   color=dw.renk.alan_tonu("#7a7a7a", acik=0.75), lw=0)
    axs[0].plot(hrs, np.array(day["solar_W"]) / 1e3, **S.stil("Sun overhead"))
    axs[0].axhline(day["loiter_W"] / 1e3, **S.stil("Loiter at bucket speed"))
    axs[0].axhline(day["hover_W"] / 1e3, **S.stil("Hover"))
    axs[0].set_xlabel("Hours from dawn, drifting at 55 km")
    axs[0].set_ylabel("Power over the day (kW)")
    axs[0].text(day["mission_start_h"] + day["mission_h"] / 2, 0.15, "VESPER flies", ha="center", va="bottom",
                fontsize=plt_size() * 0.8, color="#4d4d4d")
    axs[0].text(hrs[-1] * 0.78, 2.4, "night: 0 W", ha="center", va="center", fontsize=plt_size() * 0.8,
                color="#4d4d4d")
    sp = np.array(sk["speeds"])
    axs[1].plot(sp, np.array(sk["electric_W"]) / 1e3, **S.stil("VESPER"))
    band = sk["wind_band_m_s"]
    ub = np.linspace(band[0], band[2], 20)
    axs[1].plot(ub, [0.5 * A.state(55e3).rho * u ** 3 * c["res"]["design"].system.drag_area_m2 / 1e3 for u in ub],
                **S.stil("Pioneer Venus"))
    axs[1].set_yscale("log")
    axs[1].set_xlabel("Airspeed (m/s)")
    axs[1].set_ylabel("Power to hold that airspeed (kW)")
    axs[1].text(band[0] - 2.0, 0.5 * A.state(55e3).rho * band[2] ** 3 * c["res"]["design"].system.drag_area_m2 / 1e3,
                "airframe drag alone\nat wind speed", ha="right", va="top", fontsize=plt_size() * 0.8, color="#4d4d4d")
    S.kaydet(fig, str(OUT / "F13_day_and_station_keeping"), sessiz=True)

    # F14 terminal descent ---------------------------------------------------------------------------------------
    term = c["term"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    for key, name in (("windmilling", "Rotors windmilling"), ("rotors_failed", "Rotors failed")):
        r = term[key]
        axs[0].plot(r.t / 3600.0, r.h / 1e3, **S.stil(name))
        axs[1].plot(r.t / 3600.0, r.T_interior_C, **S.stil(name))
    axs[1].axhline(125.0, color="#7a3b00", lw=0.8, ls="--")
    tmax = max(float(term[k].t[-1]) for k in term) / 3600.0
    axs[1].text(0.97 * tmax, 118.0, "electronics 125 °C", ha="right", va="top", fontsize=plt_size() * 0.8,
                color="#7a3b00")
    axs[0].set_xlabel("Hours after the sunset dive")
    axs[1].set_xlabel("Hours after the sunset dive")
    axs[0].set_ylabel("Altitude (km)")
    axs[1].set_ylabel("Battery-bay temperature (°C)")
    dw.etiket.cizgi_sonu(axs[0])
    S.kaydet(fig, str(OUT / "F14_end_of_mission"), sessiz=True)

    # F15 margins ------------------------------------------------------------------------------------------------
    mg = sorted(out["margins"], key=lambda m: m["ratio"])
    fig, ax = S.figur(oran=0.62)
    y = np.arange(len(mg)) + 1.0
    ax.scatter([m["ratio"] for m in mg], y, **S.stil("VESPER", tur="sacilim"))
    ax.axvline(1.0, color="#7a3b00", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlim(0.005, 400.0)
    ax.set_xticks([0.01, 0.1, 1.0, 10.0, 100.0])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100"])
    ax.minorticks_off()
    ax.set_yticks(y)
    ax.set_yticklabels([m["item"] for m in mg])
    ax.set_xlabel("Margin ratio (above 1 = margin, log scale)")
    ax.set_ylabel("")
    S.kaydet(fig, str(OUT / "F15_margins"), sessiz=True)


def plt_size() -> float:
    import matplotlib.pyplot as plt

    return float(plt.rcParams.get("font.size", 18))
