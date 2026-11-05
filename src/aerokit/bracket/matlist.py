"""Material list from the organisers (CSV, YAML or plain text) → keys of the temperature-dependent pool
(:mod:`aerokit.bracket.matdata`), with a report of every decision. Never a silent guess.

Matching, per entry:

1. normalise (lower case; spaces, hyphens, underscores, dots, slashes and brackets removed);
2. **alias**: equal to a known designation of a pool alloy (trade names, UNS, EN numbers, common short forms);
3. **close**: difflib ratio ≥ 0.85 to one alias and ≥ 0.10 above the best alias of any other alloy (typos such as
   "Ti-6Al4-V", "Inconel718");
4. otherwise **unknown** (no alloy close enough) or **ambiguous** (two alloys close) → error with the list.

Route words in the entry ("wrought", "cast", "forged", "plate", "AM", "L-PBF", "SLM", "DMLS", "EBM") are compared
with the pool entry's route; a mismatch is reported as ``route differs`` (the alloy matched, but our 300 °C data and
AM cost/CO₂ belong to the pool route). ``strict=True`` turns that into an error as well.
"""
from __future__ import annotations

import csv
import difflib
import re
from pathlib import Path
from typing import Any

from aerokit.bracket import matdata

__all__ = ["ALIASES", "normalise", "match", "read_list", "resolve", "markdown"]

ALIASES: dict[str, list[str]] = {
    "structural_steel": ["structural steel", "ansys structural steel", "steel", "mild steel", "carbon steel",
                         "S235", "S235JR", "S275", "1.0038", "A36", "ASTM A36", "low carbon steel"],
    "ss_17_4ph": ["17-4PH", "17-4 PH", "17/4 PH", "17-4", "AISI 630", "SAE 630", "UNS S17400", "S17400", "1.4542",
                  "X5CrNiCuNb16-4", "630 stainless", "17-4PH H1025", "stainless 17-4", "17-4PH stainless", "17-4PH stainless steel",
                  "17-4 PH stainless steel", "17-4PH steel"],
    "ti64_lpbf": ["Ti-6Al-4V", "Ti6Al4V", "Ti 6-4", "Ti64", "Ti-64", "Grade 5 titanium", "Ti grade 5", "TC4",
                  "UNS R56400", "R56400", "3.7165", "Ti-6Al-4V ELI", "Grade 23"],
    "in718_lpbf": ["Inconel 718", "IN718", "IN 718", "Alloy 718", "Nickel 718", "UNS N07718", "N07718", "2.4668",
                   "NiCr19Fe19Nb5Mo3", "Inconel718", "718"],
    "scalmalloy": ["Scalmalloy", "AlMgSc", "Al-Mg-Sc", "Al Mg Sc", "Scalmalloy RP", "aluminium scandium",
                   "aluminum scandium"],
}

_ROUTE_WORDS = {"wrought": "wrought", "cast": "cast", "casting": "cast", "forged": "wrought", "forging": "wrought",
                "plate": "wrought", "bar": "wrought", "machined": "wrought", "am": "am", "lpbf": "am", "slm": "am",
                "dmls": "am", "ebm": "am", "printed": "am", "additive": "am", "pbf": "am"}


def normalise(s: str) -> str:
    return re.sub(r"[\s\-_./()\[\],]+", "", str(s).lower())


_GENERIC = {"steel", "mildsteel", "carbonsteel", "lowcarbonsteel", "718"}
"""Short or generic names that map to one pool alloy only by convention: matched, with a note."""

_NORM = {k: {normalise(a) for a in [*v, matdata.get(k).name, k]} for k, v in ALIASES.items()}


def _route_of(entry: str) -> str | None:
    words = re.findall(r"[a-z]+", entry.lower().replace("l-pbf", "lpbf"))
    found = {_ROUTE_WORDS[w] for w in words if w in _ROUTE_WORDS}
    return found.pop() if len(found) == 1 else None


def _strip_route(entry: str) -> str:
    s = entry.lower().replace("l-pbf", " ")
    return " ".join(w for w in re.split(r"[\s,;]+", s) if re.sub(r"[^a-z]", "", w) not in _ROUTE_WORDS)


def match(entry: str) -> dict[str, Any]:
    """Decision for one entry: ``status`` alias | close | unknown | ambiguous, ``key``, ``score``, ``note``."""
    raw = str(entry).strip()
    n = normalise(_strip_route(raw)) or normalise(raw)
    hits = [k for k, al in _NORM.items() if n in al]
    if len(hits) == 1:
        res: dict[str, Any] = {"entry": raw, "status": "alias", "key": hits[0], "score": 1.0}
        if n in _GENERIC:
            res["note"] = f"generic name: taken as {matdata.get(hits[0]).name}; give the grade if it is another"
    else:
        best = {k: max(difflib.SequenceMatcher(None, n, a).ratio() for a in al) for k, al in _NORM.items()}
        order = sorted(best, key=lambda k: -best[k])
        k1, k2 = order[0], order[1]
        if best[k1] >= 0.85 and best[k1] - best[k2] >= 0.10:
            res = {"entry": raw, "status": "close", "key": k1, "score": round(best[k1], 3)}
        elif best[k1] >= 0.85:
            res = {"entry": raw, "status": "ambiguous", "key": None, "score": round(best[k1], 3),
                   "note": f"as close to {k1} ({best[k1]:.2f}) as to {k2} ({best[k2]:.2f})"}
        else:
            res = {"entry": raw, "status": "unknown", "key": None, "score": round(best[k1], 3),
                   "note": f"nearest {k1} ({best[k1]:.2f} < 0.85); no 300 °C data for anything else"}
    if res["key"]:
        m = matdata.get(res["key"])
        want = _route_of(raw)
        have = "am" if m.am else "wrought"
        if want and want != have:
            res["route_differs"] = True
            res["note"] = (f"alloy matched, but the entry says '{want}' and the pool entry is '{m.route}': "
                           "strength, cost and CO₂ are those of the pool route")
        res["name"] = m.name
    return res


def read_list(path: str | Path) -> list[str]:
    """Entries from CSV (column ``material`` / ``name``, else the first column), YAML (list, or ``materials:``
    list of strings or of mappings with ``name``) or plain text (one per line, ``#`` comments)."""
    p = Path(path)
    txt = p.read_text(encoding="utf-8-sig")
    suf = p.suffix.lower()
    if suf in (".yaml", ".yml"):
        import yaml
        data = yaml.safe_load(txt)
        if isinstance(data, dict):
            data = data.get("materials", data.get("candidates", []))
        return [str(d.get("name", d.get("material", ""))) if isinstance(d, dict) else str(d) for d in data or []]
    if suf == ".csv":
        rows = list(csv.reader(txt.splitlines()))
        if not rows:
            return []
        head = [h.strip().lower() for h in rows[0]]
        col = next((head.index(c) for c in ("material", "name", "materials") if c in head), None)
        body = rows[1:] if col is not None else rows
        return [r[col or 0].strip() for r in body if r and r[col or 0].strip()]
    return [ln.split("#")[0].strip() for ln in txt.splitlines() if ln.split("#")[0].strip()]


def resolve(entries: list[str], strict: bool = False) -> dict[str, Any]:
    """Match every entry; ``ok`` False when anything is unknown/ambiguous (or a route differs with ``strict``).
    ``keys`` keeps the list order without duplicates."""
    rows = [match(e) for e in entries]
    bad = [r for r in rows if r["key"] is None or (strict and r.get("route_differs"))]
    keys: list[str] = []
    for r in rows:
        if r["key"] and r["key"] not in keys:
            keys.append(r["key"])
    return {"rows": rows, "keys": keys, "ok": not bad and bool(keys), "problems": bad}


def markdown(res: dict[str, Any]) -> str:
    s = ("| Entry | Decision | Pool material | Score | Note |\n|---|---|---|---|---|\n")
    for r in res["rows"]:
        s += (f"| {r['entry']} | {r['status']}{' · route differs' if r.get('route_differs') else ''} | "
              f"{r.get('name', '—')} | {r['score']:.2f} | {r.get('note', '')} |\n")
    return s
