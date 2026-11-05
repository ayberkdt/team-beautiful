"""Console front-end of the output layer.

Command handlers call :func:`table`, :func:`note`, :func:`warn`, :func:`file` and :func:`result`.
Inside :func:`capture` these calls fill a :class:`~aerokit.output.report.Report` that the CLI
renders once in the requested format; outside it they print immediately as plain text, so the
helpers also work in scripts and notebooks.

>>> with capture("demo") as rep:
...     _ = table(["x", "y (m)"], [["a", "1.5"]])
...     result("y is 1.5 m.", "Use it.")
>>> rep.result
'y is 1.5 m.'
"""
from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, TextIO

from aerokit.output.report import Report, format_from_path
from aerokit.output.tables import Table
from aerokit.output.writers import write_text_atomic

__all__ = ["capture", "table", "note", "warn", "file", "progress", "result", "emit", "get_material", "current_report"]

_CURRENT: ContextVar[Report | None] = ContextVar("aerokit_report", default=None)


def current_report() -> Report | None:
    """The report being captured, if any."""
    return _CURRENT.get()


@contextmanager
def capture(title: str = "") -> Iterator[Report]:
    """Collect console output of the enclosed block into a :class:`Report`."""
    rep = Report(title=title)
    token = _CURRENT.set(rep)
    try:
        yield rep
    finally:
        _CURRENT.reset(token)


def table(headers: list[str], rows: list[list[Any]], title: str = "") -> Table:
    """Add (or print) a table: numbers right-aligned, text left-aligned, no vertical rules."""
    rep = _CURRENT.get()
    if rep is not None:
        return rep.table(headers, rows, title)
    t = Table(headers, rows, title)
    print(t.to_text())
    return t


def note(text: str) -> None:
    """Add (or print) a free-text line."""
    rep = _CURRENT.get()
    if rep is not None:
        rep.note(text)
    else:
        print(text)


def warn(text: str) -> None:
    """Add (or print to stderr) a warning."""
    rep = _CURRENT.get()
    if rep is not None:
        rep.warn(text)
    else:
        print(f"WARNING: {text}", file=sys.stderr)


def file(path: str) -> None:
    """Record (or print) a file the command wrote."""
    rep = _CURRENT.get()
    if rep is not None:
        rep.file(path)
    else:
        print(f"File: {path}")


def progress(text: str) -> None:
    """Print a progress line to stderr immediately (never part of the report; Doherty threshold)."""
    print(f"... {text}", file=sys.stderr, flush=True)


def result(sentence: str, next_step: str) -> None:
    """Set (or print) the closing result sentence and the single next step."""
    rep = _CURRENT.get()
    if rep is not None:
        rep.conclude(sentence, next_step)
    else:
        print(f"\nResult: {sentence}\nNext step: {next_step}")


def emit(report: Report, fmt: str | None = None, out: str | None = None, stream: TextIO | None = None) -> str:
    """Render ``report`` and write it to ``out`` (atomically) or to ``stream`` (default stdout).

    The format defaults to the extension of ``out`` (``.md``, ``.json``, ``.csv``) and else text.
    Returns the rendered string.
    """
    fmt = fmt or (format_from_path(out) if out else "text")
    text = report.render(fmt)
    if out:
        path = write_text_atomic(out, text + "\n", suffixes={".txt", ".md", ".markdown", ".json", ".csv"})
        print(f"Report written: {path}", file=stream or sys.stdout)
    else:
        print(text, file=stream or sys.stdout)
    return text


def get_material(name: str | None) -> dict[str, Any] | None:
    """Look up a material by name for CLI options (``None`` passes through).

    ``"list"`` or ``"?"`` prints the catalogue and exits.
    """
    if name is None:
        return None
    from aerokit.materials import library
    if name.strip().lower() in ("list", "?"):
        library.print_catalogue()
        raise SystemExit(0)
    return library.find(name)
