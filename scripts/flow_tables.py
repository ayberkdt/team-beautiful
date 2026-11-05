"""Regenerate the ISA and first-cell tables of ``docs/02_fluids_constraints.md``.

The numbers come from :mod:`aerokit.aero.atmosphere` and :mod:`aerokit.aero.flow` (no formula is
duplicated here). Tables are printed as Markdown with the user's ``datawiz`` table audit when that
library is importable, else with :class:`aerokit.output.tables.Table`.

Usage::

    python scripts/flow_tables.py           # print both tables + boundary-layer layer counts
    python scripts/flow_tables.py --check   # exit 1 if a value differs from the doc table
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.aero import atmosphere, flow  # noqa: E402
from aerokit.output.tables import Table  # noqa: E402

ALTITUDES = [0, 1000, 2000, 3000, 5000, 10000, 11000]
CASES = [("Small UAV", 15, 0.20, 0), ("Small UAV", 20, 0.25, 0), ("Small UAV", 25, 0.30, 0),
         ("eVTOL wing", 60, 1.0, 500), ("eVTOL rotor section", 120, 0.15, 0)]


def isa_rows() -> list[list[str]]:
    rows = []
    for h in ALTITUDES:
        d = atmosphere.isa(h)
        rows.append([f"{h:,}".replace(",", " "), f"{d['T']:.2f}", f"{d['p']:,.0f}".replace(",", " "),
                     f"{d['rho']:.3f}", f"{d['mu'] * 1e5:.3f}", f"{d['nu'] * 1e5:.2f}", f"{d['a']:.1f}"])
    return rows


def cell_rows() -> list[list[str]]:
    rows = []
    for name, U, c, h in CASES:
        y1, _, Re, _ = flow.first_cell(U, c, 1.0, h)
        y30, _, _, _ = flow.first_cell(U, c, 30.0, h)
        rows.append([name, f"{U}", f"{c:.2f}", f"{h}", f"{Re / 1e6:.2f}", f"{flow.mach(U, h):.2f}",
                     f"{y1 * 1e5:.1f}", f"{y30 * 1e5:.0f}"])
    return rows


ISA_HEAD = ["Altitude (m)", "T (K)", "p (Pa)", "ρ (kg/m³)", "μ ×10⁵ (Pa·s)", "ν ×10⁵ (m²/s)", "a (m/s)"]
CELL_HEAD = ["Case", "U (m/s)", "c (m)", "h (m)", "Re ×10⁶", "Mach", "Δy₁ (y⁺=1) ×10⁵ (m)", "Δy₁ (y⁺=30) ×10⁵ (m)"]


def _doc_rows(doc: str, first_header: str) -> list[list[str]]:
    lines = doc.splitlines()
    i = next(k for k, line in enumerate(lines) if line.startswith(f"| {first_header} |"))
    out = []
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        out.append([c.strip() for c in line.strip("|").split("|")])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="compare with the tables in docs/02_fluids_constraints.md")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):          # never crash on a non-UTF-8 console/pipe
        sys.stdout.reconfigure(encoding="utf-8" if not sys.stdout.isatty() else sys.stdout.encoding,
                               errors="replace")
    isa, cells = isa_rows(), cell_rows()
    if a.check:
        doc = (ROOT / "docs" / "02_fluids_constraints.md").read_text(encoding="utf-8")
        bad = 0
        for head, mine in ((ISA_HEAD[0], isa), (CELL_HEAD[0], cells)):
            theirs = _doc_rows(doc, head)
            for r_doc, r_new in zip(theirs, mine, strict=False):
                norm = [re.sub(r"\s+", " ", c) for c in r_doc]
                if norm != r_new:
                    bad += 1
                    print(f"differs: doc {norm} vs computed {r_new}")
        print(f"{bad if bad else 'OK'} — {len(isa) + len(cells)} rows compared")
        return 1 if bad else 0
    print(Table(ISA_HEAD, isa).to_markdown(), "\n")
    print(Table(CELL_HEAD, cells).to_markdown(), "\n")
    y1, _, Re, _ = flow.first_cell(20, 0.25, 1.0, 0)
    delta = flow.boundary_layer(20, 0.25, 0)
    for g in (1.1, 1.15, 1.2):
        print(f"δ = {delta:.4f} m, growth {g:.2f} → {flow.layer_count(y1, delta, g)} layers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
