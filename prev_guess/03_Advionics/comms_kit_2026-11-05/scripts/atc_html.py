"""Build single-file, offline demo pages from the two mock-ups and the data written by ``03_Advionics/scripts/atc_day.py``.

    python 03_Advionics/scripts/atc_html.py

Reads ``03_Advionics/{cockpit,scope}.html`` and ``outputs/{cockpit,scope}_data.js``; writes
``outputs/cockpit_demo.html`` and ``outputs/scope_demo.html`` with the data inlined (no server, no network: opens from a USB
stick on the event laptop). The links between the two pages point at the demo files.
"""
from __future__ import annotations

from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
BASE = ROOT / "03_Advionics"


def build(name: str) -> Path:
    html = (BASE / "templates" / f"{name}.html").read_text(encoding="utf-8")
    data = (BASE / "outputs" / f"{name}_data.js").read_text(encoding="utf-8")
    tag = f'<script src="outputs/{name}_data.js"></script>'
    if tag not in html:
        raise SystemExit(f"{name}.html does not reference {tag}")
    html = html.replace(tag, "<script>\n" + data.replace("</script", "<\\/script") + "</script>")
    html = html.replace('href="scope.html"', 'href="scope_demo.html"').replace('href="cockpit.html"',
                                                                            'href="cockpit_demo.html"')
    out = BASE / "outputs" / f"{name}_demo.html"
    out.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    for n in ("cockpit", "scope"):
        p = build(n)
        print(f"{p} ({p.stat().st_size / 1024:.0f} kB)")
