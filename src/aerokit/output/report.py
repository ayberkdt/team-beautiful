"""Structured command output: a :class:`Report` collects tables, notes, warnings, the result
sentence and the next step, and renders them as text, Markdown or JSON.

Every CLI command fills one report; the format is chosen once, at the edge
(``--format`` or the extension of ``--out``). The text layout always ends with exactly one
``Result:`` sentence and one ``Next step:`` line, so the last thing a user reads is the answer.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

from aerokit.output.tables import Table

__all__ = ["Report", "Format", "FORMATS", "format_from_path"]

Format = Literal["text", "md", "json", "csv"]
FORMATS: tuple[str, ...] = ("text", "md", "json", "csv")
_SUFFIX = {".md": "md", ".markdown": "md", ".json": "json", ".csv": "csv", ".txt": "text"}


def format_from_path(path: str, default: str = "text") -> str:
    """Output format implied by a file name (``report.md`` → ``"md"``)."""
    lower = path.lower()
    for suffix, fmt in _SUFFIX.items():
        if lower.endswith(suffix):
            return fmt
    return default


@dataclass
class Report:
    """Collected output of one command."""

    title: str = ""
    items: list[Table | str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    result: str = ""
    next_step: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ building
    def table(self, headers: list[str], rows: list[list[Any]], title: str = "") -> Table:
        """Append a table and return it."""
        t = Table(headers, rows, title)
        self.items.append(t)
        return t

    def note(self, text: str) -> None:
        """Append a free-text line (context, assumptions)."""
        self.items.append(str(text))

    def warn(self, text: str) -> None:
        """Record a warning (rendered before the result)."""
        self.warnings.append(str(text))

    def file(self, path: str) -> None:
        """Record a file written by the command."""
        self.files.append(str(path))

    def conclude(self, result: str, next_step: str) -> None:
        """Set the result sentence and the single next step."""
        self.result, self.next_step = str(result), str(next_step)

    @property
    def tables(self) -> list[Table]:
        """Tables in order of appearance."""
        return [i for i in self.items if isinstance(i, Table)]

    # ------------------------------------------------------------------ rendering
    def render(self, fmt: str = "text") -> str:
        """Render as ``text``, ``md``, ``json`` or ``csv`` (CSV: tables only, blank-line separated)."""
        if fmt == "text":
            return self._text()
        if fmt == "md":
            return self._markdown()
        if fmt == "json":
            return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        if fmt == "csv":
            if not self.tables:
                raise ValueError("this command produced no table to write as CSV")
            return "\n".join(t.to_csv() for t in self.tables)
        raise ValueError(f"unknown output format {fmt!r}; choose one of {', '.join(FORMATS)}")

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready dictionary."""
        return {"title": self.title,
                "tables": [{"title": t.title, "headers": list(t.headers), "rows": [list(r) for r in t.rows]}
                           for t in self.tables],
                "notes": [i for i in self.items if isinstance(i, str)],
                "warnings": self.warnings, "files": self.files,
                "result": self.result, "next_step": self.next_step, "data": self.data}

    def _text(self) -> str:
        parts = [self.title] if self.title else []
        parts += [i.to_text() if isinstance(i, Table) else i for i in self.items]
        parts += [f"WARNING: {w}" for w in self.warnings]
        parts += [f"File: {f}" for f in self.files]
        out = "\n\n".join(p for p in parts if p)
        if self.result:
            out += f"\n\nResult: {self.result}\nNext step: {self.next_step}"
        return out.strip("\n")

    def _markdown(self) -> str:
        parts = [f"## {self.title}"] if self.title else []
        parts += [i.to_markdown() if isinstance(i, Table) else i for i in self.items]
        parts += [f"> **Warning:** {w}" for w in self.warnings]
        parts += [f"- File: `{f}`" for f in self.files]
        if self.result:
            parts.append(f"**Result:** {self.result}\n\n**Next step:** {self.next_step}")
        return "\n\n".join(p for p in parts if p)
