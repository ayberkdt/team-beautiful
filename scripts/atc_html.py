"""Build single-file, offline demo pages from the two mock-ups and the data written by ``scripts/atc_day.py``.

    python scripts/atc_html.py

Reads ``studies/final_2026/advionics/{cockpit,scope}.html`` and ``out/{cockpit,scope}_data.js``; writes
``out/cockpit_demo.html`` and ``out/scope_demo.html`` with the data inlined (no server, no network: opens from a USB
stick on the event laptop). The links between the two pages point at the demo files.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "studies" / "final_2026" / "advionics"


def build(name: str) -> Path:
    html = (BASE / f"{name}.html").read_text(encoding="utf-8")
    data = (BASE / "out" / f"{name}_data.js").read_text(encoding="utf-8")
    tag = f'<script src="out/{name}_data.js"></script>'
    if tag not in html:
        raise SystemExit(f"{name}.html does not reference {tag}")
    html = html.replace(tag, "<script>\n" + data.replace("</script", "<\\/script") + "</script>")
    html = html.replace('href="scope.html"', 'href="scope_demo.html"').replace('href="cockpit.html"',
                                                                            'href="cockpit_demo.html"')
    out = BASE / "out" / f"{name}_demo.html"
    out.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    for n in ("cockpit", "scope"):
        p = build(n)
        print(f"{p} ({p.stat().st_size / 1024:.0f} kB)")
