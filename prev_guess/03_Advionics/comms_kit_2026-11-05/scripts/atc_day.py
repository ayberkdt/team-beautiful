"""Advionics 'Automated Approach Guidance' day kit: signal -> display numbers, figures and demo data.

    python 03_Advionics/scripts/atc_day.py            # everything except real speech recognition (~1 min)
    python 03_Advionics/scripts/atc_day.py --asr      # + Windows SAPI text-to-speech -> noisy WAV -> recogniser sweep (~3 min)
    python 03_Advionics/scripts/atc_day.py --quick    # fewer Monte Carlo draws (for a smoke test)

Writes ``03_Advionics/outputs/``: ``report.md`` (every number with the command that made it),
``*.png/pdf`` + ``*.denetim.txt`` (datawiz audit), ``scope_data.js`` and ``cockpit_data.js`` (read by the two HTML
mock-ups in ``03_Advionics/``), ``decoder_vectors.json``, ``asr_sweep.json``.

All environment variables for D: (TEMP, MPLCONFIGDIR) must be set by the caller (docs/21 rule 1).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.atc import clearance as CL                      # noqa: E402
from aerokit.atc import modes as M                           # noqa: E402
from aerokit.atc import radar as R                           # noqa: E402
from aerokit.atc.channel import WordChannel, degrade_words   # noqa: E402
from aerokit.atc.commhealth import (AdvisoryDisplay, AltLink, CommHealthMonitor, CommInputs,  # noqa: E402
                                    States)
from aerokit.atc.traffic import NM, Scenario, simulate       # noqa: E402
from aerokit.approach import glide_path_height               # noqa: E402

OUT = ROOT / "03_Advionics" / "outputs"
OWN = "BTL123"
RUNWAYS = ("07L", "07R", "25L", "25R")        # the synthetic destination's runways (navigation database)

#: synthetic clearances for our own aircraft (truth = the clean parse) and one for a similar callsign
PHRASES = [
    "beetle one two three turn left heading two seven zero descend and maintain three thousand feet",
    "beetle one two three turn right heading three four zero",
    "beetle one two three descend and maintain four thousand feet reduce speed one eight zero knots",
    "beetle one two three climb flight level one two zero",
    "beetle one two three squawk four six two one",
    "beetle one two three contact approach one one eight decimal five zero five",
    "beetle one two three cleared ils approach runway two five right qnh one zero one three",
    "beetle one two three turn left heading two zero zero",
]
OTHER = "beetle one three two turn right heading zero nine zero descend and maintain five thousand feet"


# --------------------------------------------------------------------------------------------- decoders
def decoder_table() -> list[dict]:
    """Published vectors -> our decoder. 'src' says who read the expected value from the source."""
    v = []

    def row(name, msg, field, got, expected, src):
        v.append({"vector": name, "hex": msg, "field": field, "decoded": got, "expected": expected,
                  "ok": got == expected if not isinstance(expected, float) else abs(got - expected) < 0.01,
                  "read_by": src})
    e, o = M.airborne_position("8D40621D58C382D690C8AC2863A7"), M.airborne_position("8D40621D58C386435CC412692AD6")
    lat, lon = M.cpr_global(e, o, False)
    vel = M.airborne_velocity("8D485020994409940838175B284F")
    tas = M.airborne_velocity("8DA05F219B06B6AF189400CBC33F")
    row("identification", "8D4840D6202CC371C32CE0576098", "callsign", M.callsign("8D4840D6202CC371C32CE0576098"),
        "KLM1023", "[D]")
    row("position pair", "8D40621D58C382D690C8AC2863A7 + ...6435CC412692AD6", "lat", round(lat, 5), 52.2572, "[D]")
    row("position pair", "(same)", "lon", round(lon, 5), 3.91937, "[D]")
    row("position", "8D40621D58C382D690C8AC2863A7", "altitude ft", e.altitude_ft, 38000, "[D]")
    row("velocity st1", "8D485020994409940838175B284F", "ground speed kt", round(vel.speed_kt, 2), 159.20, "[D]")
    row("velocity st1", "(same)", "track deg", round(vel.angle_deg, 2), 182.88, "[D]")
    row("velocity st1", "(same)", "vertical rate fpm", vel.vertical_rate_fpm, -832, "[D]")
    row("velocity st3", "8DA05F219B06B6AF189400CBC33F", "TAS kt", tas.speed_kt, 375, "[D]")
    row("DF4 altitude", "2000171806A983", "altitude ft", M.surveillance_altitude("2000171806A983"), 36000, "[D]")
    row("DF5 identity", "2A00516D492B80", "squawk", M.surveillance_squawk("2A00516D492B80"), "0356", "[D]")
    row("CRC (corrupted)", "8D4CA251204994B1C36E60A5343D", "remainder", M.parity("8D4CA251204994B1C36E60A5343D"),
        16, "[D-ag]")
    row("DF20 address/parity", "A0001838CA380031440000F24177", "ICAO", M.icao("A0001838CA380031440000F24177"),
        "3C6DD0", "[D-ag]")
    row("DF11 all-call", "5D484FDEA248F5", "ICAO", M.icao("5D484FDEA248F5"), "484FDE", "[D-ag]")
    row("DF20 Comm-B BDS 2,0", "A000083E202CC371C31DE0AA1CCF", "callsign",
        M.commb_identification("A000083E202CC371C31DE0AA1CCF"), "KLM1017", "[D-ag]")
    se, so = M.surface_position("8C4841753AAB238733C8CD4020B1"), M.surface_position("8C4841753A8A35323FAEBDAC702D")
    slat, slon = M.cpr_surface_global(se, so, True, 51.990, 4.375)
    sn = M.surface_position("8C4841753A9A153237AEF0F275BE")
    llat, llon = M.cpr_surface_local(sn, 52.320607, 4.734735)
    row("surface pair (ref 51.990, 4.375)", "8C4841753AAB2387... + 8C4841753A8A3532...", "lat", round(slat, 6),
        52.320607, "[D]")
    row("surface pair", "(same)", "lon", round(slon, 6), 4.734735, "[D]")
    row("surface local", "8C4841753A9A153237AEF0F275BE", "lat", round(llat, 6), 52.320561, "[D]")
    row("surface local", "(same)", "lon", round(llon, 6), 4.735735, "[D]")
    row("surface movement", "(same)", "speed kt", sn.speed_kt, 17.0, "[D]")
    row("surface track", "(same)", "track deg", sn.track_deg, 92.8125, "[D]")
    return v


# --------------------------------------------------------------------------------------------- language
def _truth(text: str) -> dict:
    c = CL.parse(text, own_callsign=OWN)
    return {i.kind: i.value for i in c.instructions if i.kind in CL.CRITICAL and i.status == "CONFIRMED"}


def _score(c: CL.Clearance, truth: dict, for_us: bool) -> dict:
    """Outcome counts for one parsed transmission against the truth."""
    r = {"correct": 0, "wrong_shown": 0, "withheld": 0, "n": len(truth) if for_us else 0}
    shown = {} if c.addressed_to_us is False else {
        i.kind: i.value for i in c.instructions if i.kind in CL.CRITICAL and i.status == "CONFIRMED"}
    if not for_us:
        r["wrong_shown"] = len(shown) if c.addressed_to_us is True else 0      # another aircraft's clearance as ours
        return r
    for k, v in truth.items():
        if k in shown and shown[k] == v:
            r["correct"] += 1
        elif k in shown:
            r["wrong_shown"] += 1
        else:
            r["withheld"] += 1
    r["wrong_shown"] += sum(1 for k in shown if k not in truth)                 # invented field
    return r


def _wilson(k: float, n: float, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score 95 % interval for a proportion k/n (k may exceed n for 'per instruction' rates: clipped)."""
    if n <= 0:
        return 0.0, 1.0
    p = min(k / n, 1.0)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def word_channel_sweep(n_per_snr: int, seed: int = 0) -> dict:
    """Monte Carlo: synthetic recogniser errors -> conservative parser vs naive parser (confidence ignored)."""
    snrs = list(range(0, 31, 3))
    res = {"snr_db": snrs, "conservative": [], "naive": [], "n_instructions": [], "wer": []}
    ch = WordChannel()
    rng = np.random.default_rng(seed)
    for snr in snrs:
        acc = {"conservative": np.zeros(4), "naive": np.zeros(4)}
        errs = words = 0
        for k in range(n_per_snr):
            other = rng.random() < 0.2
            text = OTHER if other else PHRASES[k % len(PHRASES)]
            truth = _truth(text) if not other else {}
            heard = degrade_words(text, snr, ch, seed=int(rng.integers(1 << 31)))
            ref = CL.tokenize(text)
            errs += sum(1 for a, b in zip(ref, heard) if a.text != b.text) + abs(len(ref) - len(heard))
            words += len(ref)
            for name, words_in in (("conservative", heard), ("naive", [CL.Word(w.text, 1.0) for w in heard])):
                kw = {"known_runways": RUNWAYS} if name == "conservative" else {}
                s = _score(CL.parse(words_in, own_callsign=OWN, **kw), truth, not other)
                acc[name] += [s["correct"], s["wrong_shown"], s["withheld"], s["n"]]
        for name in ("conservative", "naive"):
            c, w, wh, n = acc[name]
            lo, hi = _wilson(w, n)
            lo2, hi2 = _wilson(wh, n)
            res[name].append({"correct_pct": 100 * c / n, "wrong_per_1000": 1000 * w / n, "withheld_pct": 100 * wh / n,
                              "wrong_ci": (1000 * lo, 1000 * hi), "withheld_ci": (100 * lo2, 100 * hi2),
                              "counts": [int(c), int(w), int(wh), int(n)]})
        res["n_instructions"].append(int(acc["naive"][3]))
        res["wer"].append(100 * errs / words)
    return res


def asr_recognise(out_dir: Path, snrs=(30, 20, 15, 10, 6, 3, 0), seeds=(1, 2), fresh: bool = False) -> dict | None:
    """Real speech: SAPI TTS -> VHF band-limit + noise -> SAPI recogniser (grammar and dictation). Raw results are
    cached in ``asr_raw.json`` (re-used unless ``fresh``) so scoring can be redone without the 8-minute run."""
    import os
    from aerokit.atc import asr_sapi
    from aerokit.atc.channel import degrade_audio, read_wav, vhf_voice_band, write_wav
    cache = out_dir / "asr_raw.json"
    if cache.exists() and not fresh:
        return json.loads(cache.read_text(encoding="utf-8"))
    if not asr_sapi.available():
        return None
    wav_dir = Path(os.environ.get("TEMP", str(out_dir))) / "asr_wav"
    wav_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for i, ph in enumerate(PHRASES):
        p = wav_dir / f"clean_{i}.wav"
        if not p.exists():
            asr_sapi.synthesize(ph, p)
        x, fs = read_wav(p)
        x = vhf_voice_band(x, fs)
        for snr in snrs:
            for sd in seeds:
                q = wav_dir / f"p{i}_snr{snr}_s{sd}.wav"
                write_wav(q, degrade_audio(x, fs, snr_db=snr, seed=sd + 100 * i), fs)
                jobs.append((i, snr, sd, q))
    raw = {"snr_db": list(snrs), "phrases": PHRASES, "modes": {}}
    for mode in ("grammar", "dictation"):
        t0 = time.time()
        rec = asr_sapi.recognize_batch([j[3] for j in jobs], mode=mode)
        raw["modes"][mode] = {"seconds": round(time.time() - t0, 1),
                              "rows": [{"phrase": i, "snr_db": snr, "seed": sd, "text": r["text"],
                                        "conf": r["confidence"], "words": r["words"], "alternates": r["alternates"]}
                                       for (i, snr, sd, _), r in zip(jobs, rec)]}
    cache.write_text(json.dumps(raw, indent=1), encoding="utf-8")
    return raw


def _parse_asr(row: dict, hi: float, naive: bool) -> CL.Clearance:
    if row["text"] is None:
        return CL.parse("", own_callsign=OWN)
    words = [tuple(w) for w in row["words"]] if row["words"] else row["text"]
    if naive:
        return CL.parse(CL.tokenize(row["text"]), own_callsign=OWN)            # best text at face value
    hyps = [(words, row["conf"])] + [(a[0], a[1]) for a in row["alternates"][1:]]
    return CL.parse_nbest(hyps, own_callsign=OWN, hi=hi, lo=min(0.5, hi), known_runways=RUNWAYS)


def score_asr(raw: dict, hi: float = 0.85) -> dict:
    """Score cached recognitions with the conservative parser (threshold ``hi``) and the naive one."""
    res = {"snr_db": raw["snr_db"], "modes": {}, "hi": hi}
    for mode, block in raw["modes"].items():
        rows = []
        for row in block["rows"]:
            truth = _truth(raw["phrases"][row["phrase"]])
            for kind in ("conservative", "naive"):
                s = _score(_parse_asr(row, hi, kind == "naive"), truth, True)
                rows.append({**{k: row[k] for k in ("phrase", "snr_db", "seed", "text", "conf")}, "parser": kind,
                             "rejected": row["text"] is None, **s})
        agg = []
        for snr in raw["snr_db"]:
            for kind in ("conservative", "naive"):
                sub = [x for x in rows if x["snr_db"] == snr and x["parser"] == kind]
                n = sum(x["n"] for x in sub)
                agg.append({"snr_db": snr, "parser": kind, "correct_pct": 100 * sum(x["correct"] for x in sub) / n,
                            "wrong_per_1000": 1000 * sum(x["wrong_shown"] for x in sub) / n,
                            "wrong_count": sum(x["wrong_shown"] for x in sub),
                            "withheld_pct": 100 * sum(x["withheld"] for x in sub) / n,
                            "rejected_pct": 100 * sum(x["rejected"] for x in sub) / len(sub), "n_instructions": n})
        res["modes"][mode] = {"rows": rows, "by_snr": agg, "seconds": block["seconds"]}
    return res


def threshold_sweep(raw: dict, his=(0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95), min_snr: int = 10) -> list[dict]:
    """Operating curve of the confidence threshold for the SAPI grammar recogniser (SNR >= ``min_snr`` pooled)."""
    out = []
    rows = [r for r in raw["modes"]["grammar"]["rows"] if r["snr_db"] >= min_snr]
    for hi in his:
        c = w = wh = n = 0
        for row in rows:
            s = _score(_parse_asr(row, hi, False), _truth(raw["phrases"][row["phrase"]]), True)
            c, w, wh, n = c + s["correct"], w + s["wrong_shown"], wh + s["withheld"], n + s["n"]
        out.append({"hi": hi, "correct_pct": 100 * c / n, "wrong_count": w, "wrong_per_1000": 1000 * w / n,
                    "withheld_pct": 100 * wh / n, "n": n})
    return out


# --------------------------------------------------------------------------------------------- comm health
def comm_scenario() -> dict:
    """A scripted 300 s approach: normal -> degraded -> RX lost -> alternate (CPDLC) -> all lost -> recovered."""
    cpdlc = AltLink("CPDLC (VDL Mode 2)", True, bus="BUS2", antenna="ANT3", authorised_for="datalink, non-urgent")
    msgs = {
        10.0: ("beetle one two three turn left heading two seven zero descend and maintain three thousand feet",
               1.0, "VHF voice (ASR)"),
        250.0: ("beetle one two three cleared ils approach runway two five right qnh one zero one three", 1.0,
                "VHF voice (ASR)"),
        45.0: ("beetle one three two turn right heading zero nine zero descend and maintain five thousand feet", 1.0,
               "VHF voice (ASR)"),
        70.0: ([("beetle", .9), ("one", .9), ("two", .9), ("three", .9), ("reduce", .9), ("speed", .9),
                ("one", .9), ("six", .35), ("zero", .9), ("knots", .9)], None, "VHF voice (ASR)"),
        # a dropout swallowed the level: the heading arrived, the altitude did not
        88.0: ([("beetle", .9), ("one", .9), ("two", .9), ("three", .9), ("turn", .9), ("right", .9),
                ("heading", .9), ("one", .9), ("niner", .9), ("zero", .9), ("descend", .9), ("and", .9),
                ("maintain", .9), ("<gap>", 0.0), ("feet", .6)], "partial", "VHF voice (ASR)"),
    }
    ticks, cl = [], {}
    mid = 0
    for t in range(0, 301, 1):
        tt = float(t)
        alt = ()
        if 160 <= t < 200:
            alt = (cpdlc,)
        elif 200 <= t < 240:                        # the datalink drops too -> nothing independent is left
            alt = (AltLink(cpdlc.name, False, cpdlc.bus, cpdlc.antenna, cpdlc.authorised_for),)
        if t < 60:
            x = CommInputs(tt, True, 24.0, 0.92, heard_traffic=t % 7 == 0, atc_to_us=t in (10, 40),
                           we_transmitted=t in (12, 41))
        elif t < 100:
            x = CommInputs(tt, True, 7.0, 0.55, dropout_fraction=0.2, heard_traffic=t % 9 == 0, atc_to_us=t == 70,
                           we_transmitted=t == 72)
        elif t < 240:
            x = CommInputs(tt, False, None, None, we_transmitted=t in (105, 118, 131), alt_links=alt)
        else:
            x = CommInputs(tt, True, 22.0, 0.9, heard_traffic=t % 5 == 0, atc_to_us=t == 250, we_transmitted=t == 252)
        ticks.append(x)
        if tt in msgs and x.carrier:
            mid += 1
            text, flag, src = msgs[tt]
            cl[tt] = CL.parse(text, own_callsign=OWN, t_received=tt, msg_id=mid, source=src,
                              partial=(flag == "partial"))
    from aerokit.atc.traffic import default_aircraft
    traffic = [a.callsign for a in default_aircraft() if a.adsb]
    mon, disp = CommHealthMonitor(), AdvisoryDisplay(similar_callsigns=tuple(CL.similar_callsigns(OWN, traffic)))
    views = []
    from aerokit.atc.datalink import Uplink, uplink_to_clearance
    cpdlc_msgs = {170.0: Uplink(190, 250, OWN, 170.0, 100)}     # arrives over the alternate while VHF is lost
    for x in ticks:
        st = mon.step(x)
        if x.t in cl:
            disp.receive(cl[x.t])
        if x.t in cpdlc_msgs and any(a.up for a in x.alt_links):
            disp.receive(uplink_to_clearance(cpdlc_msgs[x.t], OWN))
        if x.t == 30.0:
            disp.acknowledge(1)                     # pilot confirmed message 1 by ear
        v = disp.view(x.t, st)
        v["reasons"] = list(mon.reasons)
        views.append(v)
    return {"views": views, "states": [v["state"] for v in views], "t": [v["t"] for v in views]}


# --------------------------------------------------------------------------------------------- PAR
def par_demo(voice_lost_at_s: float = 100.0) -> dict:
    """Ground PAR talks down an aircraft whose own navigation is biased (+25 m high, 40 m right in its sensed frame);
    the voice channel fails at ``voice_lost_at_s``."""
    from aerokit.approach import ApproachSimConfig, NavSensor, Runway, simulate_approach
    from aerokit.atc.par import ParGuidanceMonitor, parse_talkdown, talkdown_series
    rwy = Runway(51.0, 4.0, 10.0, 250.0)
    run = simulate_approach(rwy, NavSensor("biased on-board nav", bias=(0, 40, -25), sigma=(0, 5, 3)),
                            ApproachSimConfig(x0=8 * 1852, y0=150, gust_sigma=1.0), rng=np.random.default_rng(1))
    ser = talkdown_series(rwy, run.t, run.x, run.y, run.z)
    mon = ParGuidanceMonitor()
    rows, views = [], []
    for m, ph in ser:
        heard = m.t < voice_lost_at_s
        if heard:
            mon.receive(parse_talkdown(ph, m.t))
        rows.append({"t": round(m.t, 1), "range_nm": round(m.range_m / NM, 2), "el_dev_m": round(m.el_dev_m, 1),
                     "az_dev_m": round(m.az_dev_m, 1), "phrase": ph, "heard": heard})
    for tt in np.arange(voice_lost_at_s - 10, voice_lost_at_s + 12, 2.0):
        v = mon.view(float(tt))
        views.append({"t": float(tt), "status": v["status"]})
    return {"calls": rows, "views": views, "voice_lost_at_s": voice_lost_at_s,
            "dh_reached_s": rows[-1]["t"] if rows else None}


def par_asr(par: dict, out_dir: Path, snrs=(30, 15, 10), fresh: bool = False, conf_gate: float = 0.7) -> dict | None:
    """Real speech for PAR: talk-down phrases -> SAPI TTS -> 300-3400 Hz + noise -> SAPI PAR grammar -> display
    classes. A recognition below ``conf_gate`` utterance confidence is treated as not received [Y]."""
    import os
    from aerokit.atc import asr_sapi
    from aerokit.atc.channel import degrade_audio, read_wav, vhf_voice_band, write_wav
    from aerokit.atc.par import parse_talkdown
    cache = out_dir / "par_asr_raw.json"
    phrases = [c["phrase"] for c in par["calls"][:12]] + [par["calls"][-1]["phrase"]]
    if cache.exists() and not fresh:
        raw = json.loads(cache.read_text(encoding="utf-8"))
    else:
        if not asr_sapi.available():
            return None
        wav_dir = Path(os.environ.get("TEMP", str(out_dir))) / "par_wav"
        wav_dir.mkdir(parents=True, exist_ok=True)
        jobs = []
        for i, ph in enumerate(phrases):
            p = wav_dir / f"par_{i}.wav"
            asr_sapi.synthesize(ph, p)
            x, fs = read_wav(p)
            x = vhf_voice_band(x, fs)
            for snr in snrs:
                q = wav_dir / f"par_{i}_snr{snr}.wav"
                write_wav(q, degrade_audio(x, fs, snr_db=snr, seed=7 + i), fs)
                jobs.append((i, snr, q))
        rec = asr_sapi.recognize_batch([j[2] for j in jobs], mode="par")
        raw = {"phrases": phrases, "rows": [{"phrase": i, "snr_db": snr, "text": r["text"], "conf": r["confidence"]}
                                            for (i, snr, _), r in zip(jobs, rec)]}
        cache.write_text(json.dumps(raw, indent=1), encoding="utf-8")
    agg = []
    for snr in sorted({r["snr_db"] for r in raw["rows"]}, reverse=True):
        n = right = wrong = withheld = 0
        for r in (x for x in raw["rows"] if x["snr_db"] == snr):
            truth = parse_talkdown(raw["phrases"][r["phrase"]], 0.0)
            got = parse_talkdown(r["text"], 0.0) if r["text"] and r["conf"] >= conf_gate else None
            for field_ in ("glidepath", "course"):
                tv = getattr(truth, field_)
                if tv == "?":
                    continue
                n += 1
                gv = getattr(got, field_) if got else "?"
                if gv == "?":
                    withheld += 1
                elif gv == tv:
                    right += 1
                else:
                    wrong += 1
        agg.append({"snr_db": snr, "n": n, "right": right, "wrong": wrong, "withheld": withheld})
    return {"raw": raw, "by_snr": agg, "conf_gate": conf_gate}


# --------------------------------------------------------------------------------------------- approach guidance
def guidance_demo() -> dict:
    """End to end: voice approach clearance + ground PAR uplink + on-board navigation -> pilot's guidance panel.

    Script [Y]: the aircraft flies on a biased on-board source (25 m low-reading -> flies high, 40 m lateral); the
    approach clearance arrives by voice at 20 s; the PAR uplink is lost 120-150 s; the on-board protection level
    exceeds the alert limit 135-145 s (so 135-145 s has no valid source at all)."""
    from aerokit.approach import ApproachSimConfig, NavSensor, Runway, simulate_approach
    from aerokit.atc.guidance import GuidancePanel, SourceReading, panel_frame
    from aerokit.atc.par import par_measure
    rwy = Runway(51.0, 4.0, 10.0, 250.0)
    run = simulate_approach(rwy, NavSensor("biased on-board nav", bias=(0, 40, -25), sigma=(0, 5, 3)),
                            ApproachSimConfig(x0=8 * NM, y0=150, gust_sigma=1.0), rng=np.random.default_rng(1))
    clr = CL.parse("beetle one two three cleared ils approach runway two five right", own_callsign=OWN,
                   t_received=20.0, msg_id=1, known_runways=RUNWAYS)
    disp = AdvisoryDisplay()
    panel = GuidancePanel(rwy, "25R")
    rng = np.random.default_rng(4)
    views, next_t = [], 0.0
    for ti, xi, yi, zi in zip(run.t, run.x, run.y, run.z):
        if ti + 1e-9 < next_t:
            continue
        next_t = float(ti) + 1.0
        if ti >= 20.0 and not disp.received:
            disp.receive(clr)
        if not 120.0 <= ti < 150.0:                               # ground uplink alive
            m = par_measure(rwy, float(ti), float(xi), float(yi), float(zi), rng)
            panel.receive(SourceReading("GND PAR uplink", float(ti), float(xi), m.az_dev_m,
                                        float(glide_path_height(rwy, xi)) + m.el_dev_m))
        pl = 80.0 if 135.0 <= ti < 145.0 else 12.0
        panel.receive(SourceReading("ON-BOARD", float(ti), float(xi), float(yi) - 40.0, float(zi) - 25.0, pl))
        v = disp.view(float(ti), States.NORMAL)
        rwy_item = next((it for it in v["items"] if it["kind"] == "runway"), None)
        cleared = rwy_item["text"].split()[-1] if rwy_item else None
        pv = panel.view(float(ti), cleared, rwy_item["tag"] if rwy_item else None)
        pv["true_vert_dots"] = float(to_dots_true(rwy, xi, zi))
        views.append(pv)
    spans: dict[str, list[list[float]]] = {}
    for v in views:
        for a in v["annunciations"]:
            key = a.split(" (")[0].split(" - ")[0].split(":")[0]
            key = "SOURCES DISAGREE" if key.startswith("SOURCES DISAGREE") else key
            sp = spans.setdefault(key, [])
            if sp and v["t"] - sp[-1][1] <= 1.01:
                sp[-1][1] = v["t"]
            else:
                sp.append([v["t"], v["t"]])
    return {"views": views, "spans": spans, "summary": panel_frame(views)}


def to_dots_true(rwy, x: float, z: float) -> float:
    from aerokit.approach import deviation, to_dots
    return float(to_dots(deviation(rwy, x, 0.0, z).vertical_angle_deg, 0.7))


# --------------------------------------------------------------------------------------------- SSR code validation
def ssr_validation_study() -> list[dict]:
    """Mode A/C per-scan validity with 1 reply vs 4 replies per mode and 2-must-agree validation, two FRUIT rates."""
    rows = []
    for fruit in (3000.0, 10000.0):
        for n in (1, 4):
            r = simulate(Scenario(seed=0, ssr_replies_per_mode=n, fruit_per_s=fruit))
            k = r["stats"]["kpi"]
            rows.append({"fruit_per_s": fruit, "replies_per_mode": n, "mode_a_valid": k["mode_a_valid"],
                         "mode_a_wrong": k["mode_a_wrong"], "mode_c_valid": k["mode_c_valid"],
                         "garbled": r["stats"]["ssr_garbled"], "replies": r["stats"]["ssr_replies"]})
    return rows


# --------------------------------------------------------------------------------------------- PSR processing
def _false_track_count(sim: dict) -> tuple[int, int]:
    """(false displayed track-scans, scans in which the no-transponder aircraft has a displayed PSR-only track)."""
    ft = psr_ok = 0
    for fr in sim["frames"]:
        for t in fr["tracks"]:
            if t["status"] in ("CONFIRMED", "COASTING") and \
                    min(math.hypot(t["x"] - a["x"], t["y"] - a["y"]) for a in fr["truth"]) > 2000:
                ft += 1
        a = next(x for x in fr["truth"] if x["cs"] == "(no transponder)")
        psr_ok += any(t["primary_only"] and t["status"] in ("CONFIRMED", "COASTING")
                      and math.hypot(t["x"] - a["x"], t["y"] - a["y"]) < 2000 for t in fr["tracks"])
    return ft, psr_ok


def psr_study(out_dir: Path, fresh: bool = False) -> dict:
    """I/Q-level PSR chains: (1) false plots and target hits vs clutter jitter, processing only; (2) full chain with
    the tracker. Cached in ``psr_chains.json`` (the tracker runs take ~10 min)."""
    from aerokit.atc import psr_processing as pp
    cache = out_dir / "psr_chains.json"
    if cache.exists() and not fresh:
        return json.loads(cache.read_text(encoding="utf-8"))
    g = pp.PsrGrid()
    base = [(20, 100, 120, 3.0), (25, 60, 0.0, 3.0), (30, 140, 53.5, 3.0), (8, 250, 90, 30.0), (8, 260, 0.5, 30.0)]
    names = ["radial 120 m/s", "tangential 0 m/s", "blind speed 53.5 m/s", "over terrain 90 m/s",
             "over terrain 0.5 m/s"]
    sweep = []
    for jit in (0.01, 0.003, 0.001):
        scene = pp.ClutterScene(jitter=jit)
        rng = np.random.default_rng(0)
        cm = pp.ClutterMap()
        for _ in range(5):
            pp.process_scan(pp.synthesize_scan(g, scene, [], rng), g, "mtd_cmap", cm)
        res = {ch: [0, [0] * len(base)] for ch in pp.CHAINS}
        n_scans = 8
        for k in range(n_scans):
            ech = [pp.Echo(r * NM, az + 2.4 * k, v, snr) for r, az, v, snr in base]
            z = pp.synthesize_scan(g, scene, ech, rng)
            for ch in pp.CHAINS:
                d = pp.process_scan(z, g, ch, cm if ch == "mtd_cmap" else None)
                hit = [False] * len(ech)
                fa = 0
                for x in d:
                    near = [abs(x.range_m - e.range_m) < 300 and abs((x.az_deg - e.az_deg + 180) % 360 - 180) < 2.5
                            for e in ech]
                    if any(near):
                        hit[near.index(True)] = True
                    else:
                        fa += 1
                res[ch][0] += fa
                res[ch][1] = [a + int(b) for a, b in zip(res[ch][1], hit)]
        for ch, (fa, h) in res.items():
            sweep.append({"jitter": jit, "chain": ch, "false_plots_per_scan": fa / n_scans, "hits": h,
                          "scans": n_scans})
    runs = []
    for label, kw in (("baseline: random clutter plots", {}),
                      ("MTI + CFAR", {"psr_chain": "mti"}), ("MTD + CFAR", {"psr_chain": "mtd"}),
                      ("MTD + CFAR + clutter map", {"psr_chain": "mtd_cmap"}),
                      ("MTD + CFAR + clutter map, PSR-only 3-of-4 and >= 40 kt", {"psr_chain": "mtd_cmap",
                                                                                 "psr_min_speed_kt": 40,
                                                                                 "psr_m": 3, "psr_n": 4}),
                      ("baseline + PSR-only 3-of-4 and >= 40 kt", {"psr_min_speed_kt": 40, "psr_m": 3, "psr_n": 4})):
        sim = simulate(Scenario(seed=0, **kw))
        ft, ok = _false_track_count(sim)
        runs.append({"label": label, "kw": kw, "false_plots_per_scan": sim["stats"]["clutter"] / len(sim["frames"]),
                     "pd_psr": sim["stats"]["kpi"]["pd_psr"], "false_track_scans": ft,
                     "psr_only_aircraft_tracked_scans": ok, "scans": len(sim["frames"])})
    out = {"targets": names, "sweep": sweep, "runs": runs, "blind_speed_mps": pp.blind_speed(g),
           "grid": {"range_bin_m": g.range_bin_m, "n_range": g.n_range, "n_az": g.n_az, "n_pulses": g.n_pulses,
                    "prf_hz": g.prf_hz}}
    cache.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


# --------------------------------------------------------------------------------------------- radar
def radar_numbers() -> dict:
    sc = Scenario()
    out = {"psr": [], "ssr": [], "params": {k: getattr(sc, k) for k in ("psr_power_w", "psr_gain_dbi", "psr_freq_hz",
                                                                     "psr_bw_hz", "psr_nf_db", "psr_losses_db",
                                                                     "psr_pulses", "pfa")}}
    for r_nm in np.arange(5, 81, 5):
        for rcs in (2.0, 10.0):
            snr = R.psr_snr(sc.psr_power_w, sc.psr_gain_dbi, sc.psr_freq_hz, rcs, r_nm * NM, sc.psr_bw_hz,
                            sc.psr_nf_db, sc.psr_losses_db, n_coherent=sc.psr_pulses)
            out["psr"].append({"range_nm": float(r_nm), "rcs_m2": rcs, "snr_db": 10 * math.log10(snr),
                               "pd_sw1": R.pd_swerling1(snr, sc.pfa), "pd_sw0": R.pd_nonfluctuating(snr, sc.pfa)})
    out["ssr"] = R.coverage_table(np.array([10, 50, 100, 150, 200, 250]))
    out["horizon_nm"] = {f"{h} ft": R.radar_horizon_m(20.0, h * 0.3048) / NM for h in (1000, 3000, 10000, 30000)}
    out["hits_per_scan"] = R.hits_per_scan(250, 2.4, 4.8)
    out["pd_4_of_8_at_p0.8"] = R.pd_m_of_n(0.8, 8, 4)
    out["fruit_free_at"] = {f"{f}/s": R.fruit_free_probability(f) for f in (1000, 5000, 20000)}
    out["albersheim_0.9_1e-6"] = R.albersheim_snr_db(0.9, 1e-6)
    out["sw1_snr_0.9_1e-6"] = 10 * math.log10(math.log(1e-6) / math.log(0.9) - 1)
    return out


def tracker_compare(seeds=range(6)) -> dict:
    res = {}
    for imm in (False, True):
        breaks, gs_err = [], []
        for sd in seeds:
            r = simulate(Scenario(imm=imm, seed=sd))
            ids: set[int] = set()
            for fr in r["frames"]:
                truth = {a["cs"]: a for a in fr["truth"]}
                for tr in fr["tracks"]:
                    if tr["callsign"] == OWN and tr["status"] != "TENTATIVE":
                        ids.add(tr["id"])
                        a = truth[OWN]
                        gs_err.append(math.hypot(tr["x"] - a["x"], tr["y"] - a["y"]))
            breaks.append(len(ids))
        res["IMM" if imm else "CV Kalman"] = {"track_ids_per_run": breaks, "mean_ids": float(np.mean(breaks)),
                                             "pos_err_m_median": float(np.median(gs_err)),
                                             "pos_err_m_p95": float(np.percentile(gs_err, 95))}
    return res


# --------------------------------------------------------------------------------------------- figures
def figures(wc: dict, asr: dict | None, rad: dict, comm: dict, folder: Path, psr: dict | None = None,
            gd: dict | None = None) -> list[str]:
    import datawiz as dw
    S = dw.Seti(str(folder / "advionics.seti.json"), hedef="sunum-tam")
    S.nicelik("snr", "Signal-to-noise ratio of the voice channel", "dB", eksen="x")
    S.nicelik("wrong", "Wrong values shown as confirmed", "per 1000 instructions", eksen="y")
    S.nicelik("withheld", "Values withheld (say again)", "%", eksen="y")
    S.nicelik("rng", "Range from the radar", "NM", eksen="x")
    S.nicelik("pd", "Probability of detection per scan", None, eksen="y", sinir=(0, 1.02))
    S.nicelik("t", "Time on approach", "s", eksen="x")
    S.nicelik("state", "Communication state", None, eksen="y")
    for n in ("Naive parser", "Conservative parser"):
        S.varlik(n)
    for n in ("Swerling 1, 2 m²", "Swerling 1, 10 m²"):
        S.varlik(n)
    if asr:
        S.nicelik("thr", "Word-confidence threshold for CONFIRMED", None, eksen="x")
        S.nicelik("share", "Share of instructions (SAPI grammar, SNR 10-30 dB)", "%", eksen="y")
        S.varlik("Correct value shown")
        S.varlik("Withheld (say again)", renk="#6b5a00", degistir=True)  # palette yellow is 1.3:1 on the background
        S.varlik("Wrong value shown", renk="#9e1b32", degistir=True)     # the palette's next colour (yellow) fails 3:1
    S.varlik("State", renk="#3b3b3b", degistir=True)
    made = []
    snr = wc["snr_db"]

    fig, ax = S.figur(oran=0.55)
    for name, key in (("Naive parser", "naive"), ("Conservative parser", "conservative")):
        st = S.stil(name)
        ax.fill_between(snr, [r["wrong_ci"][0] for r in wc[key]], [r["wrong_ci"][1] for r in wc[key]],
                        color=st["color"], alpha=0.15, linewidth=0)
        ax.plot(snr, [r["wrong_per_1000"] for r in wc[key]], **st)
    S.eksen(ax, x="snr", y="wrong")
    ax.set_ylim(0, None)
    dw.etiket.cizgi_sonu(ax)
    S.kaydet(fig, str(folder / "F1_wrong_values_vs_snr"), sessiz=True)
    made.append("F1_wrong_values_vs_snr")

    fig, ax = S.figur(oran=0.55)
    for name, key in (("Naive parser", "naive"), ("Conservative parser", "conservative")):
        st = S.stil(name)
        ax.fill_between(snr, [r["withheld_ci"][0] for r in wc[key]], [r["withheld_ci"][1] for r in wc[key]],
                        color=st["color"], alpha=0.15, linewidth=0)
        ax.plot(snr, [r["withheld_pct"] for r in wc[key]], **st)
    S.eksen(ax, x="snr", y="withheld")
    ax.set_ylim(0, 100)
    dw.etiket.cizgi_sonu(ax)
    S.kaydet(fig, str(folder / "F2_withheld_vs_snr"), sessiz=True)
    made.append("F2_withheld_vs_snr")

    fig, ax = S.figur(oran=0.55)
    for rcs, name in ((2.0, "Swerling 1, 2 m²"), (10.0, "Swerling 1, 10 m²")):
        rows = [r for r in rad["psr"] if r["rcs_m2"] == rcs]
        ax.plot([r["range_nm"] for r in rows], [r["pd_sw1"] for r in rows], **S.stil(name))
    # the steady-target curve (8 dB less SNR needed) is in the report table; on the slide it crowded the labels
    S.eksen(ax, x="rng", y="pd")
    dw.notlar.referans(ax, y=0.9, metin="PSR Pd 0.9 (EUROCONTROL 1997)")
    dw.etiket.cizgi_sonu(ax)
    S.kaydet(fig, str(folder / "F3_psr_pd_vs_range"), sessiz=True)
    made.append("F3_psr_pd_vs_range")

    fig, ax = S.figur(oran=0.55)
    order = list(States.ALL)
    ax.step(comm["t"], [order.index(s) for s in comm["states"]], where="post", **S.stil("State"))
    ax.set_yticks(range(len(order)), [s.replace("_", " ") for s in order])
    S.eksen(ax, x="t", y="state")
    S.kaydet(fig, str(folder / "F4_comm_state_timeline"), sessiz=True)
    made.append("F4_comm_state_timeline")

    if asr:
        fig, ax = S.figur(oran=0.55)
        ts = asr["threshold_sweep"]
        for key, name in (("correct_pct", "Correct value shown"), ("withheld_pct", "Withheld (say again)"),
                          ("wrong_pct", "Wrong value shown")):
            ys = [t[key] if key != "wrong_pct" else 100 * t["wrong_count"] / t["n"] for t in ts]
            ax.plot([t["hi"] for t in ts], ys, **S.stil(name))
        S.eksen(ax, x="thr", y="share")
        ax.set_ylim(0, 100)
        dw.etiket.cizgi_sonu(ax)
        S.kaydet(fig, str(folder / "F5_real_asr_threshold"), sessiz=True)
        made.append("F5_real_asr_threshold")
    if gd:
        S.nicelik("tg", "Time on final", "s", eksen="x")
        S.nicelik("vdots", "Vertical deviation shown to the pilot", "dots", eksen="y", sinir=(-2.2, 2.2))
        S.varlik("Panel needle", renk="#1f3a93", degistir=True)     # palette full: explicit dark blue
        S.varlik("True deviation", baglam=True)
        fig, ax = S.figur(oran=0.55)
        tt = [v["t"] for v in gd["views"]]
        ax.plot(tt, [v["true_vert_dots"] for v in gd["views"]], **S.stil("True deviation"))
        ax.plot(tt, [np.nan if v["vert_dots"] is None else v["vert_dots"] for v in gd["views"]],
                **S.stil("Panel needle"))
        S.eksen(ax, x="tg", y="vdots")
        for a, b in gd["spans"].get("V FLAG", []):
            dw.notlar.bolge(ax, a, b + 1)
        sp = gd["spans"].get("V FLAG", [])
        if sp:
            dw.notlar.ok(ax, ((sp[0][0] + sp[0][1]) / 2, 1.6), "needle removed: V FLAG", nokta=False)
        lost = gd["spans"].get("GND GUIDANCE LOST", [])
        if lost:
            dw.notlar.ok(ax, (lost[0][0] + 4, 0.0), "on-board fallback looks on path (bias unseen)",
                         adaylar=[(70, -80), (100, -100), (60, -120), (130, -70)])   # below-right, away from ticks
        dw.etiket.cizgi_sonu(ax)
        S.kaydet(fig, str(folder / "F7_guidance_needle"), sessiz=True)
        made.append("F7_guidance_needle")
    if psr:
        S.nicelik("fps", "False plots per scan", None, eksen="x")
        S.nicelik("chain", "PSR processing chain", None, eksen="y")
        for n in ("Jitter -40 dB", "Jitter -50 dB", "Jitter -60 dB"):
            S.varlik(n)
        fig, ax = S.figur(oran=0.55)
        chains = ["fixed", "mti", "mtd", "mtd_cmap"]
        labels = {"fixed": "Fixed threshold", "mti": "MTI + CFAR", "mtd": "MTD + CFAR", "mtd_cmap": "MTD + clutter map"}
        for k, (jit, name) in enumerate(((0.01, "Jitter -40 dB"), (0.003, "Jitter -50 dB"), (0.001, "Jitter -60 dB"))):
            xs = [max(next(r["false_plots_per_scan"] for r in psr["sweep"] if r["jitter"] == jit and r["chain"] == c),
                      0.1) for c in chains]
            ax.scatter(xs, np.arange(len(chains)) + (k - 1) * 0.18, edgecolors="#333333", linewidths=0.8,
                       **S.stil(name, tur="sacilim"))
        ax.set_xscale("log")
        ax.set_yticks(range(len(chains)), [labels[c] for c in chains])
        S.eksen(ax, x="fps", y="chain")
        dw.lejant.yerlestir(ax)
        S.kaydet(fig, str(folder / "F6_psr_false_plots"), sessiz=True)
        made.append("F6_psr_false_plots")
    return made


# --------------------------------------------------------------------------------------------- demo data
def _typ(sensors: list[str]) -> int:
    """I048/020 TYP for the sensors that fed the track (ADS-B-fed tracks reported as Mode S roll-call)."""
    psr = "PSR" in sensors
    if "ADS-B" in sensors:
        return 7 if psr else 5
    if "SSR" in sensors:
        return 3 if psr else 2
    return 1


def scope_js(sim: dict, path: Path) -> dict:
    """Tracks -> ASTERIX CAT048 block per scan -> decoded back -> scope frames. Returns ASTERIX statistics."""
    from aerokit.atc.asterix import (Cat021Record, Cat048Record, decode_block, decode_cat021_block, encode_block,
                                     encode_cat021_block)
    from aerokit.atc.traffic import local_to_latlon
    frames, n_bytes, n_rec, sample_hex = [], 0, 0, None
    n21 = b21 = 0
    err21 = 0.0
    for fr in sim["frames"]:
        live = [t for t in fr["tracks"] if t["status"] in ("CONFIRMED", "COASTING")]
        recs = []
        for t in live:
            rho = math.hypot(t["x"], t["y"]) / NM
            theta = math.degrees(math.atan2(t["x"], t["y"])) % 360
            recs.append(Cat048Record(sac=0, sic=1, time_of_day_s=fr["t"], typ=_typ(t["sensors"]),
                                     rho_nm=rho, theta_deg=theta, squawk=t["squawk"],
                                     flight_level=None if t["alt_ft"] is None else t["alt_ft"] / 100,
                                     address=t["ident"] if t["ident"] and not t["ident"].startswith("A") else None,
                                     callsign=t["callsign"], track_number=t["id"],
                                     ground_speed_kt=t["gs_kt"], heading_deg=t["trk_deg"]))
        blk = encode_block(recs) if recs else b""
        dec = decode_block(blk) if recs else []
        n_bytes += len(blk)
        r21 = []
        for t in live:
            if "ADS-B" in t["sensors"] and t["ident"] and not t["ident"].startswith("A"):
                lat, lon = local_to_latlon(t["x"], t["y"])
                r21.append(Cat021Record(sac=0, sic=2, track_number=t["id"], time_pos_s=fr["t"], lat=lat, lon=lon,
                                        address=t["ident"], squawk=t["squawk"],
                                        flight_level=None if t["alt_ft"] is None else t["alt_ft"] / 100,
                                        ground_speed_kt=t["gs_kt"], track_angle_deg=t["trk_deg"],
                                        callsign=t["callsign"]))
        if r21:
            b = encode_cat021_block(r21)
            back = decode_cat021_block(b)
            n21 += len(r21)
            b21 += len(b)
            err21 = max(err21, max(math.hypot((a.lat - d.lat) * 111_195, (a.lon - d.lon) * 111_195 * math.cos(math.radians(a.lat)))
                                   for a, d in zip(r21, back)))
        n_rec += len(recs)
        if sample_hex is None and len(recs) >= 3:
            sample_hex = blk.hex(" ").upper()
        tr = []
        for t, d in zip(live, dec):
            x, y = d.rho_nm * math.sin(math.radians(d.theta_deg)), d.rho_nm * math.cos(math.radians(d.theta_deg))
            tr.append({"id": d.track_number, "cs": d.callsign or None, "sq": d.squawk,
                       "alt": None if d.flight_level is None else d.flight_level * 100,
                       "x": round(x, 2), "y": round(y, 2), "gs": round(d.ground_speed_kt), "trk": round(d.heading_deg),
                       "st": t["status"], "sens": t["sensors"], "typ": d.typ,
                       "alert": {"7500": "HIJACK", "7600": "RADIO FAILURE", "7700": "EMERGENCY"}.get(d.squawk or ""),
                       "psr": d.typ == 1, "hist": [(round(hx / NM, 2), round(hy / NM, 2)) for hx, hy in t["history"]]})
        frames.append({"t": fr["t"], "tracks": tr})
    sample = [x for x in sim["log"] if x.get("tc") in (4, 11, 19)][:12]
    stats = {"records": n_rec, "bytes": n_bytes, "bytes_per_record": n_bytes / max(n_rec, 1), "sample_block": sample_hex,
             "cat021_records": n21, "cat021_bytes": b21, "cat021_max_pos_err_m": err21}
    data = {"frames": frames, "stats": sim["stats"], "scan_s": sim["scan_s"], "log_sample": sample, "asterix": stats}
    path.write_text("window.SCOPE_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    return stats


def cockpit_js(comm: dict, path: Path) -> None:
    keep = [v for v in comm["views"] if int(v["t"]) % 2 == 0]
    path.write_text("window.COCKPIT_DATA = " + json.dumps({"views": keep}, separators=(",", ":")) + ";\n",
                    encoding="utf-8")


# --------------------------------------------------------------------------------------------- report
def _false_tracks(sim: dict) -> int:
    """Displayed tracks (confirmed or coasting) farther than 2 km from every true aircraft -- clutter-born tracks."""
    n = 0
    for fr in sim["frames"]:
        for t in fr["tracks"]:
            if t["status"] not in ("CONFIRMED", "COASTING"):
                continue
            if min(math.hypot(t["x"] - a["x"], t["y"] - a["y"]) for a in fr["truth"]) > 2000:
                n += 1
    return n


def report(dec, wc, asr, rad, comm, trk, sim, made, args, ast, psr=None, ssrv=None, gd=None) -> str:
    L = ["# Advionics comms/ATC day kit — computed numbers", "",
         f"Generated by `python scripts/atc_day.py{' --asr' if args.asr else ''}{' --quick' if args.quick else ''}` "
         f"on {time.strftime('%Y-%m-%d %H:%M')} (laptop clock). Every value below is [K] (computed here) unless "
         "tagged otherwise; model parameters marked [Y] are our assumptions.", "",
         "## 1. Decoders against published vectors", "",
         "| Vector | Field | Decoded | Expected | OK | Expected value read by |", "|---|---|---|---|---|---|"]
    for v in dec:
        L.append(f"| {v['vector']} | {v['field']} | {v['decoded']} | {v['expected']} | {'yes' if v['ok'] else 'NO'} "
                 f"| {v['read_by']} |")
    L += ["", "[D] = read from Sun (2021) by this session; [D-ag] = read by the research agent "
          "(`03_Advionics/research/R_1090_riddle.md`). The 44 Gillham table rows (Wikipedia, [D-ag]) and a "
          "full 8192-code cross-check against pyModeS 3.6.1 are in `tests/test_atc_modes.py`.", ""]
    L += ["## 2. Voice -> structured clearance: what the safety rules buy", "",
          f"Word-level recogniser error model (`aerokit.atc.channel.WordChannel`, parameters [Y]), "
          f"{args.n} transmissions per SNR, 20 % of them addressed to the similar callsign BTL132. "
          "'Wrong shown' = a value displayed as CONFIRMED that differs from what was said, or another aircraft's "
          "clearance displayed as ours. 'Withheld' = value not offered (masked digit, ambiguous, invalid) -> SAY AGAIN.", "",
          "| SNR dB | model WER % | naive: wrong shown /1000 | conservative: wrong shown /1000 | naive: withheld % "
          "| conservative: withheld % | conservative: correct % |", "|---|---|---|---|---|---|---|"]
    for k, s in enumerate(wc["snr_db"]):
        n, c = wc["naive"][k], wc["conservative"][k]
        L.append(f"| {s} | {wc['wer'][k]:.0f} | {n['wrong_per_1000']:.0f} | {c['wrong_per_1000']:.0f} | "
                 f"{n['withheld_pct']:.0f} | {c['withheld_pct']:.0f} | {c['correct_pct']:.0f} |")
    L += ["", "Reading: the conservative parser trades availability (more SAY AGAIN) for integrity (fewer wrong values "
          "shown as confirmed). The residual wrong values come from the model's 'confidently wrong' share "
          "(`p_confident_error` = 0.15, [Y]) — no confidence threshold can catch those; only readback/hearback and "
          "cross-checks (direction vs present level, valid channel, octal squawk) can.", ""]
    if asr:
        L += ["## 3. Real speech in the loop (Windows SAPI TTS -> 300-3400 Hz band + white noise -> SAPI recogniser)",
              "", "General-purpose desktop recogniser, synthetic voice (Microsoft David), 8 phrases x 2 noise seeds per "
              "SNR. Not ATC-grade ASR; it shows the chain with real recognition errors and real confidences. "
              f"Conservative parser threshold hi = {asr['hi']}; naive = best text taken at face value.", "",
              "| SNR dB | recogniser | parser | correct % | wrong shown (count) | withheld % | rejected utterances % |",
              "|---|---|---|---|---|---|---|"]
        for mode in ("grammar", "dictation"):
            for b in asr["modes"][mode]["by_snr"]:
                L.append(f"| {b['snr_db']} | {mode} | {b['parser']} | {b['correct_pct']:.0f} | {b['wrong_count']} | "
                         f"{b['withheld_pct']:.0f} | {b['rejected_pct']:.0f} |")
        L += ["", "Real recognition errors seen (grammar, wrong value in the best text):", ""]
        seen = set()
        for r in asr["modes"]["grammar"]["rows"]:
            if r["parser"] == "naive" and r["wrong_shown"] and (r["phrase"], r["text"]) not in seen:
                seen.add((r["phrase"], r["text"]))
                L.append(f"- SNR {r['snr_db']} dB: said \"{PHRASES[r['phrase']]}\" -> heard \"{r['text']}\" "
                         f"(utterance confidence {r['conf']:.2f})")
        L += ["", "Confidence-threshold operating curve, SAPI grammar, SNR >= 10 dB pooled:", "",
              "| threshold hi | correct shown % | wrong shown (count) | withheld % | instructions |", "|---|---|---|---|---|"]
        for t in asr["threshold_sweep"]:
            L.append(f"| {t['hi']} | {t['correct_pct']:.0f} | {t['wrong_count']} | {t['withheld_pct']:.0f} | {t['n']} |")
        L += ["", "Transcripts and per-file scores: `asr_sweep.json`; raw recognitions: `asr_raw.json`.", ""]
    else:
        L += ["## 3. Real speech in the loop", "", "Not run (use `--asr`; needs Windows System.Speech).", ""]
    L += ["## 4. Surveillance numbers", "",
          f"PSR budget parameters [Y]: {rad['params']}.", "",
          "| Range NM | Pd Swerling 1, 2 m² | Pd Swerling 1, 10 m² | Pd steady 2 m² |", "|---|---|---|---|"]
    for r_nm in (10, 20, 30, 40, 50, 60, 70, 80):
        a = next(r for r in rad["psr"] if r["range_nm"] == r_nm and r["rcs_m2"] == 2.0)
        b = next(r for r in rad["psr"] if r["range_nm"] == r_nm and r["rcs_m2"] == 10.0)
        L.append(f"| {r_nm} | {a['pd_sw1']:.2f} | {b['pd_sw1']:.2f} | {a['pd_sw0']:.2f} |")
    L += ["", f"- Required SNR for Pd 0.9 at Pfa 1e-6: steady target (Albersheim) {rad['albersheim_0.9_1e-6']:.1f} dB, "
          f"Swerling 1 {rad['sw1_snr_0.9_1e-6']:.1f} dB -> fluctuation costs ~{rad['sw1_snr_0.9_1e-6'] - rad['albersheim_0.9_1e-6']:.0f} dB.",
          f"- SSR hits per scan at PRF 250 Hz, 2.4° beam, 4.8 s scan: {rad['hits_per_scan']:.1f}; P(>= 4 of 8 replies) "
          f"at 0.8 per reply = {rad['pd_4_of_8_at_p0.8']:.3f}.",
          "- FRUIT-free probability of one Mode A/C reply: " + ", ".join(f"{k}: {v:.3f}" for k, v in rad["fruit_free_at"].items()),
          "- Radar horizon from a 20 m mast (4/3 earth): " + ", ".join(f"{k}: {v:.0f} NM" for k, v in rad["horizon_nm"].items()),
          "", "SSR link margins (illustrative [Y] powers/gains, `aerokit.atc.radar.ssr_link` defaults):", "",
          "| Range NM | uplink margin dB | downlink margin dB | downlink SNR dB |", "|---|---|---|---|"]
    for r in rad["ssr"]:
        L.append(f"| {r['range_nm']:.0f} | {r['uplink_margin_db']:.1f} | {r['downlink_margin_db']:.1f} | "
                 f"{r['downlink_snr_db']:.1f} |")
    st = sim["stats"]
    L += ["", "## 5. Synthetic traffic chain (ADS-B hex + Mode A/C pulses + PSR plots -> decoders -> IMM tracker)", "",
          f"- ADS-B messages {st['adsb_msgs']}: repaired by CRC syndrome (1 bit) {st['adsb_corrected']}, "
          f"rejected {st['adsb_rejected']} (bit error rate 2e-3 per bit, [Y]).",
          f"- Mode A/C replies {st['ssr_replies']}: garbled/unusable {st['ssr_garbled']} (FRUIT 3000/s, [Y]).",
          f"- PSR detections {st['psr_detections']}, misses {st['psr_misses']}, clutter plots {st['clutter']}.", "",
          "Quality figures in the sponsor's (RASS radar-comparator) vocabulary, synthetic chain vs truth, "
          f"{st['kpi']['scans']} scans (inputs: PSR sigma 60 m / 0.08 deg, SSR 30 m / 0.05 deg, ADS-B 15 m, all [Y]):", "",
          "| KPI | value | reference figure |", "|---|---|---|",
          f"| PSR Pd per scan | {st['kpi']['pd_psr']:.3f} | > 0.90 (EUROCONTROL 1997 6.4.2.1, [D]) |",
          f"| SSR Pd per scan | {st['kpi']['pd_ssr']:.3f} | > 0.97 (EUROCONTROL 1997 6.3.2.1, [D]) |",
          f"| Mode A code valid / wrong, per reply | {st['kpi']['mode_a_valid']:.3f} / {st['kpi']['mode_a_wrong']:.3f} | per scan: Mode A > 0.98, validated false < 0.001 (1997 6.3.2.4 / 6.3.3.2, [D]) |",
          f"| Mode A valid per scan if 4 Mode A replies per scan (1 - (1 - p)^4) | {1 - (1 - st['kpi']['mode_a_valid']) ** 4:.4f} | > 0.98 |",
          f"| Mode C valid, per reply | {st['kpi']['mode_c_valid']:.3f} | per scan > 0.96 (1997 6.3.2.4, [D]) |",
          f"| Mode C valid per scan if 4 Mode C replies per scan | {1 - (1 - st['kpi']['mode_c_valid']) ** 4:.4f} | > 0.96 |",
          f"| SSR range bias / sigma | {st['kpi']['ssr_range_bias_m']:.1f} / {st['kpi']['ssr_range_sigma_m']:.1f} m | bias < 100 m, sigma < 70 m (1997 6.3.3.1, [D]) |",
          f"| SSR azimuth bias / sigma | {st['kpi']['ssr_az_bias_deg']:.3f} / {st['kpi']['ssr_az_sigma_deg']:.3f} deg | bias < 0.1, sigma < 0.08 deg (1997 6.3.3.1, [D]) |",
          f"| PSR range bias / sigma | {st['kpi']['psr_range_bias_m']:.1f} / {st['kpi']['psr_range_sigma_m']:.1f} m | sigma < 120 m (1997 6.4.3.1, [D]) |",
          f"| PSR azimuth bias / sigma | {st['kpi']['psr_az_bias_deg']:.3f} / {st['kpi']['psr_az_sigma_deg']:.3f} deg | sigma < 0.15 deg (1997 6.4.3.1, [D]) |",
          f"| False PSR plots per scan | {st['kpi']['false_psr_plots_per_scan']:.1f} | < 20 (1997 6.4.2.2, [D]) |",
          f"| ADS-B position update per scan / median error | {st['kpi']['adsb_update_probability']:.3f} / {st['kpi']['adsb_pos_err_m_median']:.0f} m | — |",
          f"| False tracks shown (confirmed/coasting, > 2 km from every aircraft), track-scans / scans | {_false_tracks(sim)} / {len(sim['frames'])} | — |", "",
          "The sigma values recover the injected noise (a self-consistency check of the chain, not equipment data); "
          "SSR Pd counts a plot whenever the transponder replied, Mode A 'valid' needs an ungarbled reply. The chain "
          "uses ONE reply per mode per scan; a real SSR gets ~8 hits per scan (section 4) and validates the code over "
          "several replies, which is what the per-scan rows estimate (independent garbling assumed).", "",
          "| Filter | track ids for the turning ownship per run (1 = never broken) | mean | position error median m | P95 m |",
          "|---|---|---|---|---|"]
    for k, v in trk.items():
        L.append(f"| {k} | {v['track_ids_per_run']} | {v['mean_ids']:.1f} | {v['pos_err_m_median']:.0f} | "
                 f"{v['pos_err_m_p95']:.0f} |")
    L += ["", f"ASTERIX CAT048 output of the tracker: {ast['records']} records in {ast['bytes']} octets "
          f"({ast['bytes_per_record']:.1f} octets per record, items 010/140/020/040/070/090/220/240/161/200); the scope "
          "draws what is decoded back from these bytes. First block with >= 3 records:", "", "```",
          ast["sample_block"] or "(none)", "```", "",
          f"ADS-B tracks also sent as ASTERIX CAT021 (ed. 2.7 items 010/040/161/071/130/080/070/145/160/170): "
          f"{ast.get('cat021_records', 0)} records in {ast.get('cat021_bytes', 0)} octets; worst WGS-84 position "
          f"round-trip error {ast.get('cat021_max_pos_err_m', 0.0):.2f} m (LSB 180/2^23 deg ~ 2.4 m)."]
    seq = []
    for t, s in zip(comm["t"], comm["states"]):
        if not seq or seq[-1][1] != s:
            seq.append((t, s))
    if ssrv:
        L += ["", "SSR code validation (replies decoded from pulse trains through FRUIT; with 4 replies per mode a code "
              "is accepted only if >= 2 ungarbled replies agree):", "",
              "| FRUIT / s | replies per mode | Mode A valid per scan | Mode A WRONG per scan | Mode C valid per scan | garbled replies |",
              "|---|---|---|---|---|---|"]
        for r in ssrv:
            L.append(f"| {r['fruit_per_s']:.0f} | {r['replies_per_mode']} | {r['mode_a_valid']:.4f} | {r['mode_a_wrong']:.4f} | "
                     f"{r['mode_c_valid']:.4f} | {r['garbled']} / {r['replies']} |")
        L += ["", "Reference (EUROCONTROL 1997, [D]): Mode A code detection > 98 %, Mode C > 96 %, validated false Mode A "
              "< 0.1 %.", ""]
    if psr:
        g = psr["grid"]
        L += ["", "## 5a. Primary radar at the I/Q level: MTI, MTD, CFAR, clutter map", "",
              f"Grid {g['n_range']} range bins x {g['n_az']} azimuth cells, {g['n_pulses']} pulses per CPI at "
              f"{g['prf_hz']:.0f} Hz (blind speed lambda PRF / 2 = {psr['blind_speed_mps']:.1f} m/s); terrain clutter "
              "45 dB mean per pulse (lognormal), a 5-cell wind farm with Doppler spread, Swerling-1 aircraft. All scene "
              "and waveform values are [Y]; `aerokit.atc.psr_processing`.", "",
              "Processing only, 8 scans, moving test targets (hits out of 8):", "",
              "| clutter jitter | chain | false plots / scan | " + " | ".join(psr["targets"]) + " |",
              "|---|---|---|" + "---|" * len(psr["targets"])]
        for r in psr["sweep"]:
            L.append(f"| {r['jitter']} | {r['chain']} | {r['false_plots_per_scan']:.1f} | "
                     + " | ".join(str(h) for h in r["hits"]) + " |")
        L += ["", "Full chain (plots -> IMM tracker, ADS-B/SSR as before), 38 scans:", "",
              "| PSR processing | false plots / scan | PSR Pd (all aircraft) | false track-scans | no-transponder aircraft tracked (scans) |",
              "|---|---|---|---|---|"]
        for r in psr["runs"]:
            L.append(f"| {r['label']} | {r['false_plots_per_scan']:.1f} | {r['pd_psr']:.2f} | {r['false_track_scans']} | "
                     f"{r['psr_only_aircraft_tracked_scans']} / {r['scans']} |")
        L += ["", "Reading: clutter that has physics (zero Doppler, fixed position, a wind farm) is not like random "
              "clutter plots: its residue clusters, so the tracker confirms it. Doppler filtering alone (MTI, MTD) "
              "leaves thousands of false track-scans in this scene; the clutter map removes the persistent residue "
              "and also restores tangential and blind-speed targets over clear ground; a stricter PSR-only "
              "initiation (3 of 4, moving) removes the rest. Slow targets over terrain stay invisible to every "
              "Doppler chain -- that is physics, not a bug.", ""]
    if gd:
        L += ["", "## 5c. Approach guidance panel, end to end (clearance + ground PAR uplink + on-board nav)", "",
              "Script [Y]: biased on-board source (flies ~25 m high, 40 m off); approach clearance by voice at 20 s; "
              "PAR uplink lost 120-150 s; on-board protection level above the 35 m alert limit 135-145 s. "
              "`aerokit.atc.guidance` on `aerokit.approach` geometry (read-only).", "",
              "| annunciation | when (s) |", "|---|---|"]
        for k, sp in gd["spans"].items():
            L.append(f"| {k} | " + ", ".join(f"{a:.0f}-{b:.0f}" for a, b in sp) + " |")
        s_ = gd["summary"]
        L += ["", f"{s_['n']} panel frames; needles removed (V/L FLAG) in {s_['needles_removed']}; never centred or "
              "extrapolated while removed. While the ground source is valid it drives the needles and the panel shows "
              "the true ~25 m high deviation that the biased on-board source hides.", ""]
    par = sim.get("_par")
    if par:
        L += ["", "## 5b. PAR talk-down (radar -> voice -> display) and voice loss", "",
              "Aircraft guided by a biased on-board source (`aerokit.approach.simulate_approach`, bias 25 m vertical / "
              "40 m lateral, [Y]); a ground PAR (accuracy model from the ENRI summary of Annex 10, [D-ag], 2 sigma "
              "assumption [Y]) measures at 1 Hz and talks every 5 s from the 5-measurement mean; deviation classes "
              "[Y]; phrase words [A] (FAA JO 7110.65 ch. 5 s. 12 via search summary).", "",
              "| t s | range NM | true-ish el dev m | az dev m | transmission | heard |", "|---|---|---|---|---|---|"]
        shown = par["calls"][::3]
        if par["calls"] and shown[-1] is not par["calls"][-1]:
            shown = shown + par["calls"][-1:]
        for r in shown:
            L.append(f"| {r['t']:.0f} | {r['range_nm']:.1f} | {r['el_dev_m']:.0f} | {r['az_dev_m']:.0f} | {r['phrase']} | "
                     f"{'yes' if r['heard'] else 'NO (voice lost)'} |")
        if par.get("asr"):
            pa = par["asr"]
            L += ["", f"Real speech (SAPI TTS -> 300-3400 Hz + noise -> SAPI PAR grammar), {len(pa['raw']['phrases'])} "
                  f"talk-down transmissions, utterance-confidence gate {pa['conf_gate']} [Y]; needle classes "
                  "(glidepath, course) vs what was transmitted:", "",
                  "| SNR dB | classes | correct | wrong shown | withheld ('?') |", "|---|---|---|---|---|"]
            for b in pa["by_snr"]:
                L.append(f"| {b['snr_db']} | {b['n']} | {b['right']} | {b['wrong']} | {b['withheld']} |")
        L += ["", f"Voice lost at {par['voice_lost_at_s']:.0f} s; cockpit PAR panel: " +
              "; ".join(f"{v['t']:.0f} s {v['status'].split(' - ')[0]}" for v in par["views"]), ""]
    L += ["", "## 6. Comm-health scenario (scripted 300 s)", "",
          "State changes: " + " -> ".join(f"{s} @ {t:.0f} s" for t, s in seq), "",
          "Invariant checked in `tests/test_atc_commhealth.py`: every displayed item has a received message id and "
          "time; in RX_LOST / ALL_COMMS_LOST every item is STALE; no carrier -> nothing received.", "",
          "## 7. Figures (datawiz audit reports next to each PNG)", ""]
    L += [f"- `{m}.png` (+ `.pdf`, `.denetim.txt`)" for m in made]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asr", action="store_true", help="score the real SAPI speech sweep (cached recognitions if any)")
    ap.add_argument("--asr-fresh", action="store_true", help="re-run TTS + recognition (~8 min)")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--psr", action="store_true", help="I/Q-level PSR chain study (cached in outputs/psr_chains.json)")
    ap.add_argument("--psr-fresh", action="store_true", help="recompute the PSR chain study (~10 min)")
    args = ap.parse_args()
    args.n = 120 if args.quick else 600
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    dec = decoder_table()
    (OUT / "decoder_vectors.json").write_text(json.dumps(dec, indent=1), encoding="utf-8")
    wc = word_channel_sweep(args.n)
    raw = asr_recognise(OUT, fresh=args.asr_fresh) if (args.asr or args.asr_fresh) else None
    asr = score_asr(raw) if raw else None
    if asr:
        asr["threshold_sweep"] = threshold_sweep(raw)
        (OUT / "asr_sweep.json").write_text(json.dumps(asr, indent=1), encoding="utf-8")
    rad = radar_numbers()
    ssrv = ssr_validation_study()
    gd = guidance_demo()
    (OUT / "guidance_panel.json").write_text(json.dumps(gd, indent=1), encoding="utf-8")
    psr = psr_study(OUT, fresh=args.psr_fresh) if (args.psr or args.psr_fresh or (OUT / "psr_chains.json").exists()) \
        else None
    comm = comm_scenario()
    trk = tracker_compare(range(2) if args.quick else range(6))
    sim = simulate(Scenario(seed=0))
    sim["_par"] = par_demo()
    if args.asr or args.asr_fresh:
        pa = par_asr(sim["_par"], OUT, fresh=args.asr_fresh)
        if pa:
            sim["_par"]["asr"] = pa
    (OUT / "par_talkdown.json").write_text(json.dumps(sim["_par"], indent=1), encoding="utf-8")
    ast = scope_js(sim, OUT / "scope_data.js")
    cockpit_js(comm, OUT / "cockpit_data.js")
    made = figures(wc, asr, rad, comm, OUT, psr, gd)
    (OUT / "report.md").write_text(report(dec, wc, asr, rad, comm, trk, sim, made, args, ast, psr, ssrv, gd),
                                   encoding="utf-8")
    bad = [v for v in dec if not v["ok"]]
    print(f"done in {time.time() - t0:.0f} s; decoder vectors {len(dec) - len(bad)}/{len(dec)} OK; out: {OUT}")
    if bad:
        print("DECODER MISMATCH:", bad)
        sys.exit(1)


if __name__ == "__main__":
    main()
