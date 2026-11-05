"""Live voice -> display demo for the event laptop (Windows): speak a clearance, pass it through the VHF channel model,
recognise it, parse it, print what the cockpit advisory panel would show.

    python scripts/atc_live.py "beetle one two three turn left heading two seven zero" --snr 20
    python scripts/atc_live.py --text "beetle one two three squawk seven six zero zero"     # no speech, typed

The clean synthetic voice is passed through the 300-3400 Hz band and noise on purpose: that is the radio, and the
desktop recogniser was found to reject some clean full-band synthetic utterances that it recognises after the band
limit (4 Nov test, docs/24 section 11). Output: at most 7 lines.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.atc import clearance as CL                               # noqa: E402

RUNWAYS = ("07L", "07R", "25L", "25R")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("phrase", nargs="?", default="beetle one two three turn left heading two seven zero "
                                                 "descend and maintain three thousand feet")
    ap.add_argument("--snr", type=float, default=20.0, help="voice channel SNR [dB] (default 20)")
    ap.add_argument("--text", help="skip speech: parse this typed text")
    ap.add_argument("--own", default="BTL123", help="own callsign (default BTL123)")
    ap.add_argument("--dropout", help="cut the received audio from START to END seconds, e.g. 2.0:2.8")
    args = ap.parse_args()
    if args.text:
        heard, conf, how = args.text, 1.0, "typed text"
        words: object = args.text
        partial = "<gap>" in args.text.lower()
    else:
        from aerokit.atc import asr_sapi
        from aerokit.atc.channel import degrade_audio, measure_audio, read_wav, vhf_voice_band, write_wav
        tmp = Path(os.environ.get("TEMP", ".")) / "atc_live"
        tmp.mkdir(parents=True, exist_ok=True)
        try:                                   # no separate availability probe: it cost ~1 s of PowerShell start-up
            x, fs = read_wav(asr_sapi.synthesize(args.phrase, tmp / "said.wav"))
        except (OSError, RuntimeError) as exc:
            print(f"speech not available on this machine ({exc.__class__.__name__}); use --text")
            return 2
        drop = [tuple(float(v) for v in args.dropout.split(":"))] if args.dropout else []
        y = degrade_audio(vhf_voice_band(x, fs), fs, snr_db=args.snr, dropouts=drop, seed=1)
        write_wav(tmp / "heard.wav", y, fs)
        am = measure_audio(y, fs)
        partial = am.dropout_fraction > 0.03           # [Y] share of near-silent frames inside the transmission
        r = asr_sapi.recognize(tmp / "heard.wav", "grammar")
        mode = "SAPI grammar"
        if r["text"] is None and partial:                # grammar cannot match a cut phrase: try free dictation
            r, mode = asr_sapi.recognize(tmp / "heard.wav", "dictation"), "SAPI dictation fallback"
        if r["text"] is None:
            print(f"SAID   : {args.phrase}")
            print(f"HEARD  : (recogniser rejected the audio at {args.snr:.0f} dB SNR"
                  + (f", dropout {100 * am.dropout_fraction:.0f} % of the transmission)" if partial else ")"))
            print("DISPLAY: nothing new shown -- SAY AGAIN")
            return 0
        heard, conf, how = r["text"], r["confidence"], f"VHF voice, {args.snr:.0f} dB, {mode}"
        words = r["words"] or r["text"]
    c = CL.parse(words, own_callsign=args.own, known_runways=RUNWAYS, partial=partial)  # type: ignore[arg-type]
    if not args.text:
        print(f"SAID   : {args.phrase}")
    print(f"HEARD  : {heard}  (confidence {conf:.2f}, {how}{', DROPOUT detected' if partial else ''})")
    who = {True: f"for us ({args.own})", False: f"NOT for us ({c.callsign}) -- not shown",
           None: f"callsign unsure (heard {c.callsign}) -- shown, check the callsign"}
    print(f"CALL   : {who[c.addressed_to_us]}")
    def tag(i: CL.Instruction) -> str:
        st = "UNCONFIRMED (partial reception)" if partial and i.status == "CONFIRMED" else i.status
        if c.addressed_to_us is None and i.status == "CONFIRMED":
            st = "CHECK CALLSIGN"
        return f"{i.display} [{st}{': ' + i.detail if i.detail and i.status not in ('CONFIRMED',) else ''}]"
    shown = [tag(i) for i in c.instructions if c.addressed_to_us is not False]
    print("DISPLAY: " + (" | ".join(shown) if shown else "nothing to show"))
    print("NOTE   : advisory only -- confirm by ear / readback")
    return 0


if __name__ == "__main__":
    sys.exit(main())
