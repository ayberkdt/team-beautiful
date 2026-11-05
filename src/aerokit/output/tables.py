"""Plain-data tables with text, Markdown, CSV and JSON renderers.

A :class:`Table` holds already formatted cell strings (formatting numbers is the caller's job,
because the right number of digits depends on the quantity). Renderers follow one rule set:
numbers right-aligned, text left-aligned, no vertical rules, units in the header.

Example
-------
>>> t = Table(["h (m)", "T (K)"], [["0", "288.15"], ["1000", "281.65"]])
>>> print(t.to_text())
h (m)  T (K)
-----  ------
0      288.15
1000   281.65
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Table", "is_numeric"]

_NUMERIC = re.compile(r"[+\-−]?(?:\d{1,3}(?:[  ]\d{3})+(?:\.\d+)?|\d[\d.,]*(?:e[+\-]?\d+)?|inf|nan)"
                      r"(?: [^\s]+)?", re.IGNORECASE)          # "10 668 m": space-grouped digits count


def is_numeric(cell: str) -> bool:
    """True if ``cell`` reads as a number, optionally followed by one unit token (``"12.5 MPa"``)."""
    return bool(_NUMERIC.fullmatch(cell.strip())) and any(ch.isdigit() for ch in cell)


def _clean(cell: Any) -> str:
    text = "" if cell is None else str(cell)
    # one line per cell; control characters would break terminal and Markdown layouts
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text.replace("\r", " ").replace("\n", " "))


@dataclass(frozen=True)
class Table:
    """A titled table of string cells.

    Attributes
    ----------
    headers : sequence of str
        Column headers, with units in parentheses, e.g. ``"σ (MPa)"``.
    rows : sequence of sequences
        Cell values; converted with :class:`str` and stripped of control characters.
    title : str
        Optional caption (rendered above the table).
    """

    headers: Sequence[str]
    rows: Sequence[Sequence[Any]] = field(default_factory=list)
    title: str = ""

    def __post_init__(self) -> None:
        n = len(self.headers)
        if n == 0:
            raise ValueError("a table needs at least one column")
        for i, r in enumerate(self.rows):
            if len(r) != n:
                raise ValueError(f"row {i} has {len(r)} cells, table has {n} columns")
        object.__setattr__(self, "headers", [_clean(h) for h in self.headers])
        object.__setattr__(self, "rows", [[_clean(c) for c in r] for r in self.rows])
        object.__setattr__(self, "title", _clean(self.title).strip())     # one line, or no title at all

    @property
    def numeric_columns(self) -> list[bool]:
        """Columns (after the first) whose non-empty cells are all numeric."""
        out = []
        for j in range(len(self.headers)):
            cells = [r[j] for r in self.rows if r[j] not in ("", "—", "-")]
            out.append(j > 0 and bool(cells) and all(is_numeric(c) for c in cells))
        return out

    # ------------------------------------------------------------------ renderers
    def to_text(self) -> str:
        """Aligned plain text with a dashed header rule."""
        cells = [list(self.headers)] + [list(r) for r in self.rows]
        width = [max(len(r[j]) for r in cells) for j in range(len(self.headers))]
        right = self.numeric_columns            # one alignment per column, never per cell

        def line(r: list[str], header: bool = False) -> str:
            return "  ".join(c.rjust(width[j]) if right[j] and not header else c.ljust(width[j])
                             for j, c in enumerate(r)).rstrip()
        out = [self.title] if self.title else []
        out += [line(cells[0], header=True), "  ".join("-" * w for w in width)]
        out += [line(r) for r in cells[1:]]
        return "\n".join(out)

    def to_markdown(self) -> str:
        """GitHub-flavoured Markdown (numeric columns right-aligned)."""
        def esc(c: str) -> str:
            return c.replace("|", "\\|")
        num = self.numeric_columns
        out = [f"**{esc(self.title)}**", ""] if self.title else []
        out.append("| " + " | ".join(esc(h) for h in self.headers) + " |")
        out.append("|" + "|".join("---:" if n else ":---" for n in num) + "|")
        out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in self.rows]
        return "\n".join(out)

    def to_csv(self) -> str:
        """RFC 4180 CSV (header row first)."""
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(self.headers)
        w.writerows(self.rows)
        return buf.getvalue()

    def to_records(self) -> list[dict[str, str]]:
        """List of ``{header: cell}`` dictionaries."""
        return [dict(zip(self.headers, r, strict=True)) for r in self.rows]

    def to_json(self) -> str:
        """JSON object ``{"title", "headers", "rows"}``."""
        return json.dumps({"title": self.title, "headers": list(self.headers), "rows": [list(r) for r in self.rows]},
                          ensure_ascii=False, indent=2)

    @classmethod
    def from_records(cls, records: Iterable[dict[str, Any]], title: str = "") -> Table:
        """Build a table from dictionaries sharing the same keys (key order of the first record)."""
        recs = list(records)
        if not recs:
            raise ValueError("no records")
        headers = list(recs[0])
        return cls(headers, [[r.get(h, "") for h in headers] for r in recs], title)
