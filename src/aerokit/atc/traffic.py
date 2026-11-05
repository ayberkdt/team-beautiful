"""Synthetic terminal-area traffic -> real signal formats -> decoders -> tracker -> radar-scope data.

Every number on the demo scope has gone through the same chain a real system uses: aircraft truth is *encoded*
into ADS-B DF17 hex messages (with random bit errors), SSR Mode A/C pulse trains (with FRUIT) and noisy PSR plots
(detected with a Swerling-1 probability from the radar budget); the decoders of :mod:`aerokit.atc.modes` and
:mod:`aerokit.atc.modeac` turn them back into identity, altitude and position; :class:`aerokit.atc.tracker.Tracker`
fuses them. Nothing is copied from truth to the display.

Geography is synthetic (radar at 51.0 N, 4.0 E, an imaginary runway 25 near it); flat-earth local coordinates are
used within ~60 NM.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from aerokit.atc import modeac, modes
from aerokit.atc.radar import pd_swerling1
from aerokit.atc.tracker import Plot, Tracker, polar_to_plot

__all__ = ["Aircraft", "Scenario", "default_aircraft", "simulate", "LAT0", "LON0", "local_to_latlon",
           "latlon_to_local"]

LAT0, LON0 = 51.0, 4.0
R_E = 6_371_000.0
NM = 1852.0
KT = 0.514444


def local_to_latlon(x: float, y: float) -> tuple[float, float]:
    return LAT0 + math.degrees(y / R_E), LON0 + math.degrees(x / (R_E * math.cos(math.radians(LAT0))))


def latlon_to_local(lat: float, lon: float) -> tuple[float, float]:
    return (math.radians(lon - LON0) * R_E * math.cos(math.radians(LAT0)), math.radians(lat - LAT0) * R_E)


@dataclass
class Aircraft:
    """Truth state of one aircraft (straight segments with constant turn rate and vertical speed)."""

    callsign: str
    icao: str
    squawk: str
    x: float                       # m east of the radar
    y: float                       # m north
    alt_ft: float
    gs_kt: float
    trk_deg: float
    vs_fpm: float = 0.0
    turn_dps: float = 0.0
    adsb: bool = True
    transponder: bool = True
    rcs_m2: float = 10.0
    events: list[tuple[float, str, object]] = field(default_factory=list)   # (t, attribute, value)

    def step(self, dt: float, t: float) -> None:
        for (te, attr, val) in self.events:
            if t - dt < te <= t:
                setattr(self, attr, val)
        self.trk_deg = (self.trk_deg + self.turn_dps * dt) % 360
        v = self.gs_kt * KT
        self.x += v * math.sin(math.radians(self.trk_deg)) * dt
        self.y += v * math.cos(math.radians(self.trk_deg)) * dt
        self.alt_ft = max(0.0, self.alt_ft + self.vs_fpm / 60 * dt)


def default_aircraft() -> list[Aircraft]:
    """Five arrivals: our ownship being vectored, one radio-failure (7600), one without transponder (PSR only)."""
    own = Aircraft("BTL123", "4B1A23", "4621", -28 * NM, 18 * NM, 7000, 220, 120, vs_fpm=-800)
    own.events = [(60.0, "turn_dps", 1.5), (120.0, "turn_dps", 0.0)]          # 90 deg right turn to 210
    rcf = Aircraft("NVA77", "4CA2B9", "3255", 20 * NM, 30 * NM, 9000, 250, 200, vs_fpm=-500)
    rcf.events = [(70.0, "squawk", "7600")]
    psr_only = Aircraft("(no transponder)", "000000", "0000", -10 * NM, -22 * NM, 2500, 110, 45,
                        adsb=False, transponder=False, rcs_m2=2.0)
    ssr_only = Aircraft("STU42", "3C66B1", "1207", 35 * NM, -8 * NM, 12000, 280, 290, vs_fpm=-1200, adsb=False)
    other = Aircraft("EXA901", "4D2228", "5132", -40 * NM, -30 * NM, 15000, 300, 60, vs_fpm=0)
    twin = Aircraft("BTL132", "4B1A32", "4632", -18 * NM, 34 * NM, 9000, 240, 150, vs_fpm=-600)   # similar callsign
    return [own, rcf, psr_only, ssr_only, other, twin]


@dataclass
class Scenario:
    scan_s: float = 4.8
    duration_s: float = 180.0
    psr_power_w: float = 25e3      # [Y] illustrative S-band terminal radar values
    psr_gain_dbi: float = 34.0
    psr_freq_hz: float = 2.8e9
    psr_bw_hz: float = 1e6
    psr_nf_db: float = 3.0
    psr_losses_db: float = 8.0
    psr_pulses: int = 16
    pfa: float = 1e-6
    sigma_r_m: float = 60.0
    sigma_az_deg: float = 0.08
    ssr_sigma_r_m: float = 30.0
    ssr_sigma_az_deg: float = 0.05
    adsb_sigma_m: float = 15.0
    adsb_bit_error_rate: float = 2e-3
    fruit_per_s: float = 3000.0
    clutter_per_scan: float = 3.0
    imm: bool = True
    psr_chain: str | None = None    # None: plot-level PSR model with random clutter plots; else a psr_processing chain
    psr_warmup_scans: int = 5       # scans used to train the clutter map before t = 0
    psr_min_speed_kt: float = 0.0   # PSR-only track initiation: minimum speed to confirm (0 = off)
    psr_m: int | None = None        # PSR-only M-of-N (None = same as all tracks, 2 of 3)
    ssr_replies_per_mode: int = 1   # Mode A and Mode C replies decoded per scan (8 hits/scan -> up to 4 each)
    ssr_validate_min: int = 2       # with > 1 reply: a code is accepted only if this many ungarbled replies agree
    psr_n: int | None = None
    seed: int = 0


def _psr_snr(sc: Scenario, rcs: float, r_m: float) -> float:
    from aerokit.atc.radar import psr_snr
    return psr_snr(sc.psr_power_w, sc.psr_gain_dbi, sc.psr_freq_hz, rcs, max(r_m, 500.0), sc.psr_bw_hz,
                   sc.psr_nf_db, sc.psr_losses_db, n_coherent=sc.psr_pulses)


def simulate(sc: Scenario | None = None, aircraft: list[Aircraft] | None = None) -> dict:
    """Run the full chain; returns scope frames, decoded message log and statistics."""
    sc = sc or Scenario()
    _SQUAWK_OF.clear()
    acs = aircraft or default_aircraft()
    rng = np.random.default_rng(sc.seed)
    tracker = Tracker(imm=sc.imm, psr_min_speed_mps=sc.psr_min_speed_kt * KT, psr_m=sc.psr_m, psr_n=sc.psr_n)
    frames, log = [], []
    stats: dict = {"adsb_msgs": 0, "adsb_corrected": 0, "adsb_rejected": 0, "ssr_replies": 0, "ssr_garbled": 0,
             "psr_detections": 0, "psr_misses": 0, "clutter": 0}
    kpi_log: list[dict] = []
    cpr_store: dict[str, dict[bool, tuple[float, modes.AirbornePosition]]] = {}
    callsigns: dict[str, str] = {}
    sig = _SignalPsr(sc) if sc.psr_chain else None
    t = 0.0
    while t <= sc.duration_s + 1e-9:
        plots: list[Plot] = []
        echoes: list = []
        coop: list[bool] = []
        for ac in acs:
            ac.step(sc.scan_s if t > 0 else 0.0, t)
            r = math.hypot(ac.x, ac.y)
            az = math.degrees(math.atan2(ac.x, ac.y)) % 360
            # --- PSR: detection is random, position noisy, no identity
            if sig is not None:
                echoes.append(sig.echo(ac, r, az))
                psr_plot = None
            elif rng.random() < pd_swerling1(_psr_snr(sc, ac.rcs_m2, r), sc.pfa):
                stats["psr_detections"] += 1
                psr_plot = polar_to_plot(t, r + rng.normal(0, sc.sigma_r_m), az + rng.normal(0, sc.sigma_az_deg),
                                         sc.sigma_r_m, sc.sigma_az_deg, "PSR")
            else:
                stats["psr_misses"] += 1
                psr_plot = None
            # --- SSR Mode A then Mode C reply as pulse trains through FRUIT
            ssr_plot = None
            if ac.transponder:
                ok_a = ok_c = None
                for mode in ("A", "C"):
                    got: list = []
                    for _ in range(max(1, sc.ssr_replies_per_mode)):
                        pulses = (modeac.reply_for_squawk(ac.squawk, 100.0) if mode == "A"
                                  else modeac.reply_for_altitude(int(round(ac.alt_ft / 100) * 100), 100.0))
                        pulses = [p + rng.normal(0, 0.02) for p in modeac.add_fruit(pulses, sc.fruit_per_s, 300.0,
                                                                                    seed=int(rng.integers(1 << 30)))]
                        fr = [f for f in modeac.decode_pulses(pulses) if abs(f.t_f1_us - 100.0) < 0.2]
                        stats["ssr_replies"] += 1
                        if not fr or fr[0].garbled:
                            stats["ssr_garbled"] += 1
                            continue
                        got.append(modeac.mode_a_code(fr[0]) if mode == "A" else modeac.mode_c_altitude(fr[0]))
                    if sc.ssr_replies_per_mode > 1:
                        # code validation: the most frequent ungarbled value, accepted only if enough replies agree
                        best = max(set(got), key=got.count) if got else None
                        val = best if best is not None and got.count(best) >= sc.ssr_validate_min else None
                    else:
                        val = got[0] if got else None
                    if mode == "A":
                        ok_a = val
                    else:
                        ok_c = val
                ssr_plot = polar_to_plot(t, r + rng.normal(0, sc.ssr_sigma_r_m),
                                         az + rng.normal(0, sc.ssr_sigma_az_deg), sc.ssr_sigma_r_m,
                                         sc.ssr_sigma_az_deg, "SSR", ident=ok_a and f"A{ok_a}", altitude_ft=ok_c)
            # --- ADS-B: real DF17 hex with bit errors, decoded
            adsb_plot = None
            if ac.adsb:
                lat, lon = local_to_latlon(ac.x, ac.y)
                msgs = [modes.encode_identification(ac.icao, ac.callsign),
                        modes.encode_position(ac.icao, lat, lon, ac.alt_ft, odd=False),
                        modes.encode_position(ac.icao, lat, lon, ac.alt_ft, odd=True),
                        modes.encode_velocity(ac.icao, ac.gs_kt, ac.trk_deg, ac.vs_fpm)]
                for k, raw in enumerate(msgs):
                    n = int(raw, 16)
                    for bit in range(112):
                        if rng.random() < sc.adsb_bit_error_rate:
                            n ^= 1 << bit
                    rx = f"{n:028X}"
                    d = modes.decode(rx)
                    stats["adsb_msgs"] += 1
                    if d.get("status") == "CRC_FAIL" or d.get("df") not in (17, 18):
                        stats["adsb_rejected"] += 1
                        log.append({"t": t, "hex": rx, "status": "REJECTED (CRC)"})
                        continue
                    if d.get("corrected_bit"):
                        stats["adsb_corrected"] += 1
                    log.append({"t": t, "hex": rx, **{k2: v for k2, v in d.items() if k2 != "msg"}})
                    if "callsign" in d:
                        callsigns[d["icao"]] = d["callsign"]
                    if "lat_cpr" in d:
                        fixed = modes.correct_single_bit(rx)[0]
                        cpr_store.setdefault(d["icao"], {})[d["odd"]] = (t + 0.01 * k,
                                                                         modes.airborne_position(fixed))
                st = cpr_store.get(ac.icao, {})
                if True in st and False in st and abs(st[True][0] - st[False][0]) < 10:
                    newest_odd = st[True][0] >= st[False][0]
                    pos = modes.cpr_global(st[False][1], st[True][1], newest_odd)
                    if pos is not None:
                        x, y = latlon_to_local(*pos)
                        x += rng.normal(0, sc.adsb_sigma_m)
                        y += rng.normal(0, sc.adsb_sigma_m)
                        alt = (st[True] if newest_odd else st[False])[1].altitude_ft
                        adsb_plot = Plot(t, (x, y), ((sc.adsb_sigma_m ** 2, 0), (0, sc.adsb_sigma_m ** 2)),
                                         "ADS-B", ac.icao, alt)
            kpi_log.append({"t": t, "r": r, "az": az, "alt": ac.alt_ft, "squawk": ac.squawk, "xy": (ac.x, ac.y),
                            "transponder": ac.transponder, "adsb_eq": ac.adsb,
                            "psr": None if psr_plot is None else psr_plot.xy,
                            "ssr": None if ssr_plot is None else (ssr_plot.xy, ssr_plot.ident, ssr_plot.altitude_ft),
                            "adsb": None if adsb_plot is None else adsb_plot.xy})
            # plot combination as a radar data processor would: SSR/ADS-B carry identity; PSR may reinforce
            for p in (adsb_plot, ssr_plot):
                if p is not None:
                    plots.append(p)
            coop.append(adsb_plot is not None or ssr_plot is not None)
            if psr_plot is not None and adsb_plot is None and ssr_plot is None:
                plots.append(psr_plot)
        if sig is not None:
            plots += sig.plots(t, acs, echoes, coop, stats, kpi_log[-len(acs):])
        else:
            n_clutter = int(rng.poisson(sc.clutter_per_scan))
            for _ in range(n_clutter):
                rr, aa = rng.uniform(2 * NM, 25 * NM), rng.uniform(0, 360)
                plots.append(polar_to_plot(t, rr, aa, sc.sigma_r_m, sc.sigma_az_deg, "PSR"))
                stats["clutter"] += 1
        # SSR identities are squawks ("A4621"), ADS-B identities are ICAO addresses: bind them per aircraft
        live = tracker.scan(_merge_identities(plots))
        frames.append({"t": round(t, 2), "tracks": [_label(tr, callsigns) for tr in live],
                       "truth": [{"cs": a.callsign, "x": a.x, "y": a.y} for a in acs]})
        t += sc.scan_s
    stats["kpi"] = surveillance_kpis(kpi_log, stats["clutter"], len(frames))
    return {"frames": frames, "log": log, "stats": stats, "scan_s": sc.scan_s,
            "origin": {"lat": LAT0, "lon": LON0}}


class _SignalPsr:
    """I/Q-level PSR (``aerokit.atc.psr_processing``) feeding plots into the same tracker."""

    def __init__(self, sc: Scenario):
        from aerokit.atc import psr_processing as pp
        self.pp, self.sc = pp, sc
        self.grid, self.scene, self.cmap = pp.PsrGrid(), pp.ClutterScene(), pp.ClutterMap()
        self.rng = np.random.default_rng(sc.seed + 1000)
        if sc.psr_chain == "mtd_cmap":
            for _ in range(sc.psr_warmup_scans):          # the map learns the site before the run
                pp.process_scan(pp.synthesize_scan(self.grid, self.scene, [], self.rng), self.grid, "mtd_cmap",
                                self.cmap)
        self.sigma_r = self.grid.range_bin_m / math.sqrt(12)
        self.sigma_az = self.grid.az_bin_deg / math.sqrt(12)
        self.false_plots = 0
        self.scans = 0

    def echo(self, ac: Aircraft, r: float, az: float):
        v = ac.gs_kt * KT
        vx, vy = v * math.sin(math.radians(ac.trk_deg)), v * math.cos(math.radians(ac.trk_deg))
        vr = (vx * ac.x + vy * ac.y) / max(r, 1.0)
        snr1 = _psr_snr(self.sc, ac.rcs_m2, r) / self.sc.psr_pulses          # per pulse
        return self.pp.Echo(r, az, vr, snr1)

    def plots(self, t: float, acs: list[Aircraft], echoes: list, coop: list[bool], stats: dict,
              kpi_rows: list[dict]) -> list[Plot]:
        z = self.pp.synthesize_scan(self.grid, self.scene, echoes, self.rng)
        dets = self.pp.process_scan(z, self.grid, self.sc.psr_chain or "mtd", self.cmap, self.sc.pfa)
        self.scans += 1
        hit = [False] * len(acs)
        out: list[Plot] = []
        for d in dets:
            x, y = d.range_m * math.sin(math.radians(d.az_deg)), d.range_m * math.cos(math.radians(d.az_deg))
            dist = [math.hypot(x - a.x, y - a.y) for a in acs]
            k = int(np.argmin(dist)) if dist else -1
            if k >= 0 and dist[k] < 1500.0:
                hit[k] = True
                kpi_rows[k]["psr"] = (x, y)
                if coop[k]:
                    continue                                     # merged with the SSR/ADS-B plot of that aircraft
            else:
                stats["clutter"] += 1
                self.false_plots += 1
            out.append(polar_to_plot(t, d.range_m, d.az_deg, self.sigma_r, self.sigma_az, "PSR"))
        for h in hit:
            stats["psr_detections" if h else "psr_misses"] += 1
        return out


def _merge_identities(plots: list[Plot]) -> list[Plot]:
    """Drop an SSR plot that coincides with an ADS-B plot (same aircraft) after copying its squawk into a note.

    Simple rule for the demo: within 1 km and 300 ft -> same aircraft; ADS-B position kept, SSR squawk kept.
    """
    adsb = [p for p in plots if p.sensor == "ADS-B"]
    out = []
    for p in plots:
        if p.sensor == "SSR":
            twin = next((a for a in adsb if math.hypot(a.xy[0] - p.xy[0], a.xy[1] - p.xy[1]) < 1000 and
                         (a.altitude_ft is None or p.altitude_ft is None or abs(a.altitude_ft - p.altitude_ft) < 300)),
                        None)
            if twin is not None:
                if twin.ident is not None:
                    _SQUAWK_OF[twin.ident] = p.ident
                continue
        out.append(p)
    return out


_SQUAWK_OF: dict[str, str | None] = {}


def _label(tr, callsigns: dict[str, str]) -> dict:
    lab = tr.label()
    ident = lab["ident"]
    if ident and ident.startswith("A"):
        lab["squawk"], lab["callsign"] = ident[1:], None
    else:
        lab["callsign"] = callsigns.get(ident or "", None)
        sq = _SQUAWK_OF.get(ident or "")
        lab["squawk"] = sq[1:] if sq else None
    lab["history"] = [(round(x), round(y)) for (_, x, y) in tr.history[-6:]]
    lab["alert"] = {"7500": "HIJACK", "7600": "RADIO FAILURE", "7700": "EMERGENCY"}.get(lab["squawk"] or "", None)
    lab["primary_only"] = lab["sensors"] == ["PSR"]
    return lab


def _polar(xy: tuple[float, float]) -> tuple[float, float]:
    return math.hypot(*xy), math.degrees(math.atan2(xy[0], xy[1])) % 360


def surveillance_kpis(log: list[dict], clutter: int, scans: int) -> dict:
    """RASS-style quality figures of the synthetic chain against truth: detection probability per sensor, code
    correctness, range/azimuth bias and random error, ADS-B position error, false plots per scan."""
    def stats_of(vals: list[float]) -> tuple[float, float]:
        a = np.asarray(vals, float)
        return (float(a.mean()), float(a.std(ddof=1))) if len(a) > 1 else (float("nan"), float("nan"))
    out: dict = {"scans": scans, "false_psr_plots_per_scan": clutter / max(scans, 1)}
    psr = [e for e in log]
    out["pd_psr"] = sum(e["psr"] is not None for e in psr) / len(psr)
    ssr = [e for e in log if e["transponder"]]
    out["pd_ssr"] = sum(e["ssr"] is not None for e in ssr) / max(len(ssr), 1)
    a_ok = [e["ssr"][1] == f"A{e['squawk']}" for e in ssr if e["ssr"] is not None]
    a_wrong = [e["ssr"][1] is not None and e["ssr"][1] != f"A{e['squawk']}" for e in ssr if e["ssr"] is not None]
    c_ok = [e["ssr"][2] is not None and abs(e["ssr"][2] - round(e["alt"] / 100) * 100) < 1 for e in ssr
            if e["ssr"] is not None]
    out["mode_a_valid"] = float(np.mean(a_ok)) if a_ok else float("nan")
    out["mode_a_wrong"] = float(np.mean(a_wrong)) if a_wrong else float("nan")
    out["mode_c_valid"] = float(np.mean(c_ok)) if c_ok else float("nan")
    for name, key in (("psr", "psr"), ("ssr", "ssr")):
        dr, da = [], []
        for e in log:
            if e[key] is None:
                continue
            xy = e[key] if key == "psr" else e[key][0]
            rm, am = _polar(xy)
            dr.append(rm - e["r"])
            da.append((am - e["az"] + 180) % 360 - 180)
        out[f"{name}_range_bias_m"], out[f"{name}_range_sigma_m"] = stats_of(dr)
        out[f"{name}_az_bias_deg"], out[f"{name}_az_sigma_deg"] = stats_of(da)
    ad = [e for e in log if e["adsb_eq"]]
    out["adsb_update_probability"] = sum(e["adsb"] is not None for e in ad) / max(len(ad), 1)
    err = [math.hypot(e["adsb"][0] - e["xy"][0], e["adsb"][1] - e["xy"][1]) for e in ad if e["adsb"] is not None]
    out["adsb_pos_err_m_median"] = float(np.median(err)) if err else float("nan")
    return out


__all__ += ["surveillance_kpis"]
