"""Numerical verification helpers used by the test-suite and ``aerokit fem verify``.

Every check carries a name, the computed value, the expected value and (when there is one) the
literature source of the expected value, so that a failing benchmark points straight at its
reference. A failed check raises :class:`CheckFailed` (an :class:`AssertionError`) immediately,
which is what pytest reports; every check, passed or failed, is also appended to :data:`RESULTS`
so the test session can print how many numerical checks ran.

Example
-------
>>> from aerokit.verification import check
>>> check("Euler column, pinned-pinned", 9.8696044, 3.14159265**2, rtol=1e-6,
...       source="Timoshenko & Gere 1961, Sec. 2.1")
True
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

__all__ = ["CheckFailed", "CheckRecord", "RESULTS", "check", "check_true", "expect_error", "summary"]


@dataclass(frozen=True)
class CheckRecord:
    """One numerical or logical check."""

    name: str
    ok: bool
    value: Any
    expected: Any
    source: str = ""

    def describe(self) -> str:
        """Human-readable one-line description used in failure messages."""
        if isinstance(self.value, float) and isinstance(self.expected, float):
            body = f"{self.value:.6g} != {self.expected:.6g}"
        else:
            body = f"{self.value}"
        return f"{self.name}: {body}" + (f"  [{self.source}]" if self.source else "")


class CheckFailed(AssertionError):
    """Raised when a check does not hold."""


RESULTS: list[CheckRecord] = []


def _record(rec: CheckRecord) -> bool:
    RESULTS.append(rec)
    if not rec.ok:
        raise CheckFailed(rec.describe())
    return True


def check(name: str, value: Any, expected: Any, rtol: float = 1e-6, atol: float = 0.0,
          source: str = "") -> bool:
    """Assert ``value ≈ expected`` with :func:`math.isclose` semantics.

    Parameters
    ----------
    name : str
        Short description of the quantity.
    value, expected : float-like
        Computed and reference values (converted with :class:`float`).
    rtol, atol : float
        Relative and absolute tolerance.
    source : str
        Bibliographic source of ``expected`` (see ``docs/references.md``).

    Raises
    ------
    CheckFailed
        If ``value`` is not finite or not within tolerance.
    """
    v, e = float(value), float(expected)
    ok = math.isfinite(v) and math.isclose(v, e, rel_tol=rtol, abs_tol=atol)
    return _record(CheckRecord(name, ok, v, e, source))


def check_true(name: str, condition: Any, detail: Any = "", source: str = "") -> bool:
    """Assert that ``condition`` is truthy; ``detail`` is shown on failure."""
    return _record(CheckRecord(name, bool(condition), detail, "", source))


def expect_error(name: str, function: Callable[..., Any], *args: Any,
                 error: type[BaseException] | tuple[type[BaseException], ...] = Exception,
                 **kwargs: Any) -> bool:
    """Assert that ``function(*args, **kwargs)`` raises ``error``."""
    try:
        function(*args, **kwargs)
    except error:
        return check_true(name, True)
    return check_true(name, False, "no exception raised")


def summary() -> tuple[int, int]:
    """Return ``(passed, total)`` over all checks recorded in this process."""
    return sum(r.ok for r in RESULTS), len(RESULTS)
