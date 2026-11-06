""""Translate signal": the two chains from a received signal to a display item, stage by stage.

* **Voice** — transmitted phrase → VHF channel (recogniser error model at a given SNR) → recognised words with
  confidences → structured clearance (``clearance.parse``) → advisory display item (``commhealth.AdvisoryDisplay``).
* **Surveillance** — Mode S / ADS-B extended squitter with bit errors → CRC check / single-bit repair → decoded
  fields → ASTERIX CAT021 record → display label; Mode A/C pulse train (+ FRUIT) → bracket decoding → code.

Each trace returns a list of :class:`Stage` so a slide or a test can show *where* a value is lost, masked or
rejected. Nothing here invents a value: a stage that cannot produce one says so.

The sweeps (:func:`voice_sweep`, :func:`modes_ber_outcomes`) are the parameterised versions of the studies in
``prev_guess/03_Advionics/comms_kit_2026-11-05/scripts/atc_day.py``; the case runners in ``prev_guess/03_Advionics/comms_kit_2026-11-05/cases/`` call them with numbers from
``params.json``.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from aerokit.atc import clearance as CL
from aerokit.atc import modeac as MAC
from aerokit.atc import modes as M
from aerokit.atc.channel import WordChannel, degrade_words

__all__ = ["Stage", "voice_trace", "voice_sweep", "wilson", "flip_bits", "modes_outcome", "modes_ber_outcomes",
           "adsb_trace", "mode_a_trace"]


@dataclass(frozen=True)
class Stage:
    name: str
    output: str
    ok: bool = True
    note: str = ""


def wilson(k: float, n: float, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score 95 % interval for a proportion k/n (clipped to [0, 1])."""
    if n <= 0:
        return 0.0, 1.0
    p = min(k / n, 1.0)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# ------------------------------------------------------------------------------------------------ voice
def voice_trace(text: str, snr_db: float, *, own_callsign: str, seed: int = 0, channel: WordChannel = WordChannel(),
                known_runways: Sequence[str] | None = None, hi: float = 0.85, lo: float = 0.5,
                t_received: float = 0.0) -> list[Stage]:
    """One transmission through the voice chain; each stage's output as text."""
    from aerokit.atc.commhealth import AdvisoryDisplay, States
    heard = degrade_words(text, snr_db, channel, seed=seed)
    c = CL.parse(heard, own_callsign=own_callsign, known_runways=known_runways, hi=hi, lo=lo,
                 t_received=t_received, msg_id=1)
    st = [Stage("1 transmitted (truth)", text),
          Stage(f"2 channel @ {snr_db:g} dB (word error rate {100 * channel.error_rate(snr_db):.0f} %)",
                " ".join(f"{w.text}({w.conf:.2f})" for w in heard), ok=True),
          Stage("3 structured clearance", f"callsign {c.callsign} (to us: {c.addressed_to_us}); " + "; ".join(
              f"{i.display} [{i.status}]" for i in c.instructions if i.status != "INFO") or "no instruction",
                ok=c.status == "CONFIRMED")]
    d = AdvisoryDisplay()
    d.receive(c)
    v = d.view(t_received, States.NORMAL)
    shown = "; ".join(f"{it['text']} [{it['tag']}]" for it in v["items"]) or (
        f"not shown (clearance for {v['not_for_us']['callsign']})" if v["not_for_us"] else "nothing to show")
    st.append(Stage("4 cockpit advisory display", shown, ok=bool(v["items"]),
                    note="advisory only; pilot confirms by ear / readback"))
    return st


def _truth(text: str, own: str) -> dict:
    c = CL.parse(text, own_callsign=own)
    return {i.kind: i.value for i in c.instructions if i.kind in CL.CRITICAL and i.status == "CONFIRMED"}


def _score(c: CL.Clearance, truth: dict, for_us: bool) -> tuple[int, int, int, int]:
    """(correct, wrong shown, withheld, n) for one parsed transmission against the truth."""
    shown = {} if c.addressed_to_us is False else {
        i.kind: i.value for i in c.instructions if i.kind in CL.CRITICAL and i.status == "CONFIRMED"}
    if not for_us:
        return 0, (len(shown) if c.addressed_to_us is True else 0), 0, 0
    ok = sum(1 for k, v in truth.items() if k in shown and shown[k] == v)
    wrong = sum(1 for k, v in truth.items() if k in shown and shown[k] != v) + sum(1 for k in shown if k not in truth)
    withheld = sum(1 for k in truth if k not in shown)
    return ok, wrong, withheld, len(truth)


def voice_sweep(phrases: Sequence[str], snrs: Sequence[float], n_per_snr: int, *, own_callsign: str,
                other_phrase: str | None = None, p_other: float = 0.2, channel: WordChannel = WordChannel(),
                known_runways: Sequence[str] | None = None, hi: float = 0.85, lo: float = 0.5,
                seed: int = 0) -> dict:
    """Monte Carlo of the voice chain: conservative parser (confidences, masking, runway check) vs naive parser
    (every recognised word taken at face value). Per SNR: correct %, wrong per 1000 instructions (with Wilson 95 %
    interval), withheld % and the simulated word error rate."""
    rng = np.random.default_rng(seed)
    out: dict = {"snr_db": list(snrs), "conservative": [], "naive": [], "wer_pct": [], "n_instructions": []}
    for snr in snrs:
        acc = {"conservative": np.zeros(4), "naive": np.zeros(4)}
        errs = words = 0
        for k in range(n_per_snr):
            other = other_phrase is not None and rng.random() < p_other
            text: str = other_phrase if (other and other_phrase is not None) else phrases[k % len(phrases)]
            truth = {} if other else _truth(text, own_callsign)
            heard = degrade_words(text, snr, channel, seed=int(rng.integers(1 << 31)))
            ref = CL.tokenize(text)
            errs += sum(1 for a, b in zip(ref, heard) if a.text != b.text) + abs(len(ref) - len(heard))
            words += len(ref)
            cons = CL.parse(heard, own_callsign=own_callsign, known_runways=known_runways, hi=hi, lo=lo)
            naive = CL.parse([CL.Word(w.text, 1.0) for w in heard], own_callsign=own_callsign)
            acc["conservative"] += _score(cons, truth, not other)
            acc["naive"] += _score(naive, truth, not other)
        for name in ("conservative", "naive"):
            c, w, wh, n = acc[name]
            lo_w, hi_w = wilson(w, n)
            out[name].append({"correct_pct": 100 * c / max(n, 1), "wrong_per_1000": 1000 * w / max(n, 1),
                              "wrong_ci": (1000 * lo_w, 1000 * hi_w), "withheld_pct": 100 * wh / max(n, 1),
                              "counts": [int(c), int(w), int(wh), int(n)]})
        out["n_instructions"].append(int(acc["naive"][3]))
        out["wer_pct"].append(100 * errs / max(words, 1))
    return out


# ------------------------------------------------------------------------------------------------ Mode S / ADS-B
def flip_bits(msg: str, ber: float, rng: np.random.Generator) -> tuple[str, int]:
    """Flip each bit independently with probability ``ber``; returns (message, number of flipped bits)."""
    n = len(msg) * 4
    mask = 0
    flips = 0
    for k in np.flatnonzero(rng.random(n) < ber):
        mask |= 1 << (n - 1 - int(k))
        flips += 1
    return f"{int(msg, 16) ^ mask:0{len(msg)}X}", flips


def modes_outcome(original: str, received: str) -> str:
    """'intact', 'repaired', 'rejected', or 'wrong' (a message that reaches the display different from what was
    sent: CRC passed on a corrupted message, or a bad single-bit repair)."""
    if M.is_valid(received):
        return "intact" if received == original else "wrong"
    fixed, bit = M.correct_single_bit(received)
    if bit is None:
        return "rejected"
    return "repaired" if fixed == original else "wrong"


def modes_ber_outcomes(bers: Sequence[float], n_messages: int, seed: int = 0, icao_hex: str = "4B1A23") -> dict:
    """Share of DF17 airborne-position messages per outcome at each bit error rate (uniform random positions)."""
    rng = np.random.default_rng(seed)
    rows = []
    for ber in bers:
        cnt = {"intact": 0, "repaired": 0, "rejected": 0, "wrong": 0}
        flips = 0
        for _ in range(n_messages):
            msg = M.encode_position(icao_hex, float(rng.uniform(50, 52)), float(rng.uniform(3, 5)),
                                    float(rng.integers(10, 300)) * 100, bool(rng.integers(2)))
            rx, nf = flip_bits(msg, ber, rng)
            flips += nf
            cnt[modes_outcome(msg, rx)] += 1
        lo_w, hi_w = wilson(cnt["wrong"], n_messages)
        rows.append({"ber": ber, **{k: v / n_messages for k, v in cnt.items()}, "counts": cnt, "n": n_messages,
                     "mean_flipped_bits": flips / n_messages, "wrong_ci": (lo_w, hi_w)})
    return {"rows": rows}


def adsb_trace(callsign: str, icao_hex: str, lat: float, lon: float, alt_ft: float, *, ber: float = 0.0,
               seed: int = 0) -> list[Stage]:
    """Identification + position squitter → (bit errors) → CRC / repair → fields → CAT021 → display label."""
    from aerokit.atc.asterix import Cat021Record, decode_cat021_block, encode_cat021_block
    rng = np.random.default_rng(seed)
    ident, pos = M.encode_identification(icao_hex, callsign), M.encode_position(icao_hex, lat, lon, alt_ft, False)
    st = [Stage("1 squitters sent (112 bit, 1090 MHz)", f"ident {ident}, position {pos}")]
    rx = []
    for name, m in (("ident", ident), ("position", pos)):
        r, nf = flip_bits(m, ber, rng)
        oc = modes_outcome(m, r)
        rx.append((name, m, r, oc))
        st.append(Stage(f"2 received {name} (BER {ber:g}, {nf} bit(s) flipped)", f"{r} -> CRC: {oc}",
                        ok=oc in ("intact", "repaired"), note="rejected messages never reach the display"))
    good = {name: (M.correct_single_bit(r)[0]) for name, _, r, oc in rx if oc in ("intact", "repaired")}
    cs = M.callsign(good["ident"]) if "ident" in good else None
    alt = M.airborne_position(good["position"]).altitude_ft if "position" in good else None
    if "position" in good:
        latlon = M.cpr_local(M.airborne_position(good["position"]), lat, lon)
        st.append(Stage("3 decoded fields", f"ICAO {icao_hex}, callsign {cs}, CPR local "
                                            f"{latlon[0]:.5f} {latlon[1]:.5f}, {alt} ft"))
        rec = Cat021Record(time_pos_s=0.0, lat=latlon[0], lon=latlon[1], address=icao_hex,
                           flight_level=None if alt is None else alt / 100, callsign=cs)
        blk = encode_cat021_block([rec])
        back = decode_cat021_block(blk)[0]
        st.append(Stage("4 ASTERIX CAT021 block", f"{len(blk)} octets: {blk.hex().upper()}"))
        fl = "FL---" if back.flight_level is None else f"FL{back.flight_level:03.0f}"
        st.append(Stage("5 display label", f"{back.callsign or '(no ident)'}  {fl}  {back.lat:.4f} {back.lon:.4f}"))
    else:
        st.append(Stage("3 decoded fields", "position message rejected: no position this update", ok=False,
                        note="the track coasts; nothing is invented"))
    return st


def mode_a_trace(squawk: str, *, fruit_per_s: float = 0.0, window_us: float = 60.0, seed: int = 0,
                 p1_p3_us: float = 8.0) -> list[Stage]:
    """Mode A interrogation (P1–P3 spacing) → reply pulses (+ FRUIT) → bracket decoding → code or 'unknown'."""
    mode = MAC.interrogation_mode(p1_p3_us)
    pulses = MAC.reply_for_squawk(squawk, t0_us=10.0)
    rx = MAC.add_fruit(pulses, fruit_per_s, window_us, seed=seed) if fruit_per_s > 0 else pulses
    frames = MAC.decode_pulses(rx)
    st = [Stage("1 interrogation", f"P1-P3 {p1_p3_us:g} us -> Mode {mode}"),
          Stage("2 reply pulses (+FRUIT)", f"{len(pulses)} own + {len(rx) - len(pulses)} FRUIT pulse edges")]
    own = [f for f in frames if abs(f.t_f1_us - 10.0) < 0.2]
    if not own:
        st.append(Stage("3 decoded", "own bracket not found -> code unknown", ok=False))
        return st
    f = own[0]
    code = MAC.mode_a_code(f) if mode == "A" else str(MAC.mode_c_altitude(f))
    ok = not f.garbled and not f.phantom_risk
    st.append(Stage("3 decoded", f"code {code}" + (" GARBLED -> shown as unknown" if f.garbled else "")
                    + (" (phantom risk)" if f.phantom_risk else ""), ok=ok))
    st.append(Stage("4 display", f"squawk {code}" if ok else "squawk ---- (not validated)", ok=ok,
                    note="a code is validated only when >= 2 replies agree (traffic.Scenario.ssr_validate_min)"))
    return st
