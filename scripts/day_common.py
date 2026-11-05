"""Helpers shared by the competition-day scripts (approach_day, investigation_day, venus_day)."""
from __future__ import annotations

import sys

# characters a Windows console on code page 857/1254 cannot show → readable ASCII
_ASCII = {"σ": "sigma", "°": "deg", "·": "*", "−": "-", "–": "-", "—": "-", "≥": ">=", "≤": "<=", "→": "->",
          "²": "^2", "³": "^3", "×": "x", "₂": "2", "√": "sqrt", "≈": "~", "Δ": "d", "β": "beta", "ρ": "rho",
          "±": "+/-"}


def console_text(text: str, stream=None) -> str:
    """``text`` unchanged if the stream's encoding can show it; else with the symbols above spelled out."""
    enc = getattr(stream or sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(enc)
        return text
    except UnicodeEncodeError:
        for k, v in _ASCII.items():
            text = text.replace(k, v)
        return text.encode(enc, errors="replace").decode(enc)


def protect_streams() -> None:
    """Never crash mid-run on an unprintable character (the datawiz audit prints arrows)."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def sig(x: float, digits: int = 2) -> str:
    """``x`` with ``digits`` significant figures, never in exponent form for 1e-4 ≤ |x| < 1e6."""
    if x == 0:
        return "0"
    from math import floor, log10
    d = max(0, digits - 1 - floor(log10(abs(x))))
    return f"{x:.{d}f}"


def wants_help(argv: list[str]) -> bool:
    """``-h``, ``--help``, ``/?`` or no argument at all."""
    return not argv or argv[0].lower() in ("-h", "--help", "/?", "help")


def progress(message: str) -> None:
    """One progress line on stderr, flushed at once (the work after it takes longer than ~0.4 s)."""
    print(console_text("> " + message, sys.stderr), file=sys.stderr, flush=True)


def audit_summary(folder) -> tuple[int, str]:
    """(number of HATA, one-line summary) from the datawiz ``*.denetim.txt`` and ``*.tutarlilik.txt`` in ``folder``."""
    import re
    from pathlib import Path

    folder = Path(folder)
    reports = sorted(folder.glob("*.denetim.txt"))
    errors = 0
    for r in reports + sorted(folder.glob("*.tutarlilik.txt")):
        first = r.read_text(encoding="utf-8").splitlines()[0]
        m = re.search(r"(\d+) HATA", first)
        errors += int(m.group(1)) if m else 1          # unreadable report counts as a failure
    return errors, (f"figure audit: {len(reports)} figures + set consistency, {errors} errors "
                    f"(details in {folder.name}/*.denetim.txt)")
