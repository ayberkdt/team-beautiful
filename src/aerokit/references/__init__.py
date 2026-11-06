"""Bibliography registry and the :func:`cite` decorator.

Every formula, coefficient or benchmark taken from the literature is tied to a key of
:data:`REFERENCES`. Decorating a function with :func:`cite` does three things:

* checks at import time that every key exists (a typo fails loudly, not silently);
* stores the keys in ``obj.__references__`` so tools and tests can query them;
* appends a NumPy-style ``References`` section to the docstring.

The registry is split by subject (``_core``, ``_aero``, ``_structures``, ``_composites``,
``_fem``, ``_fem_dynamics``, ``_optimization``, ``_cad``, ``_materials``); :data:`REFERENCES` merges them and rejects
duplicate keys. ``00_Common/docs/references.md`` is generated from it by ``scripts/build_references.py``.

Example
-------
>>> from aerokit.references import cite
>>> @cite("timoshenko_gere_1961", note="Eq. 2-4")
... def euler_load(E, I, L):
...     '''Pinned-pinned Euler buckling load.'''
...     return 3.141592653589793 ** 2 * E * I / L ** 2
>>> euler_load.__references__
('timoshenko_gere_1961',)
"""
from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, TypeVar

__all__ = ["Reference", "REFERENCES", "cite", "references_of", "format_bibliography"]

T = TypeVar("T")


@dataclass(frozen=True)
class Reference:
    """One bibliographic entry.

    Attributes
    ----------
    key : str
        Stable identifier, ``firstauthor[_secondauthor]_year[suffix]`` in lower case.
    authors, title : str
        As printed on the source.
    year : int
        Publication year of the edition actually used.
    publisher : str
        Publisher, journal (with volume/pages) or issuing body.
    edition, doi, url, note : str
        Optional details. ``note`` records what the code uses from the source.
    """

    key: str
    authors: str
    year: int
    title: str
    publisher: str = ""
    edition: str = ""
    doi: str = ""
    url: str = ""
    note: str = ""

    def format(self) -> str:
        """Return a one-line citation (author-year style)."""
        parts = [f"{self.authors} ({self.year}). {self.title.rstrip('.')}."]
        for extra in (self.edition, self.publisher):
            if extra:
                parts.append(f"{extra.rstrip('.')}.")
        if self.doi:
            parts.append(f"doi:{self.doi}.")
        elif self.url:
            parts.append(f"<{self.url}>.")
        return " ".join(parts)


def _merge(groups: Iterable[Iterable[Reference]]) -> Mapping[str, Reference]:
    out: dict[str, Reference] = {}
    for group in groups:
        for ref in group:
            if ref.key in out:
                raise ValueError(f"duplicate reference key {ref.key!r}")
            if ref.key != ref.key.strip().lower() or " " in ref.key:
                raise ValueError(f"reference key must be lower-case without spaces: {ref.key!r}")
            out[ref.key] = ref
    return MappingProxyType(dict(sorted(out.items())))


def _load() -> Mapping[str, Reference]:
    from aerokit.references import (_aero, _cad, _composites, _core, _fem, _fem_dynamics, _ideathon2026,
                                    _materials, _optimization, _structures, _task_atc, _task_bracket,
                                    _task_canopy, _task_venus2)
    modules = (_core, _aero, _structures, _composites, _fem, _fem_dynamics, _optimization, _cad, _materials,
               _ideathon2026, _task_bracket, _task_canopy, _task_atc, _task_venus2)
    return _merge(m.REFERENCES for m in modules)


REFERENCES: Mapping[str, Reference] = _load()


def cite(*keys: str, note: str = "") -> Callable[[T], T]:
    """Decorator attaching literature references to a function or class.

    Parameters
    ----------
    *keys : str
        Keys of :data:`REFERENCES`.
    note : str
        Where in the source (equation, table, section) the implementation comes from.

    Raises
    ------
    KeyError
        At decoration (import) time, if a key is unknown.
    """
    if not keys:
        raise ValueError("cite() needs at least one reference key")
    missing = [k for k in keys if k not in REFERENCES]
    if missing:
        raise KeyError(f"unknown reference key(s): {', '.join(missing)}")

    def deco(obj: T) -> T:
        existing: tuple[str, ...] = getattr(obj, "__references__", ())
        merged = existing + tuple(k for k in keys if k not in existing)
        lines = [f".. [{k}] {REFERENCES[k].format()}" for k in keys]
        if note:
            lines.append(f"   ({note})")
        doc = inspect.cleandoc(obj.__doc__ or "")
        header = "References\n----------"
        if header in doc:
            doc = doc + "\n" + "\n".join(lines)
        else:
            doc = (doc + "\n\n" if doc else "") + header + "\n" + "\n".join(lines)
        try:
            obj.__doc__ = doc
            obj.__references__ = merged  # type: ignore[attr-defined]
        except (AttributeError, TypeError):           # pragma: no cover - builtins / slots
            pass
        return obj

    return deco


def references_of(obj: Any) -> tuple[Reference, ...]:
    """Return the :class:`Reference` objects attached to ``obj`` by :func:`cite`."""
    return tuple(REFERENCES[k] for k in getattr(obj, "__references__", ()))


def format_bibliography(keys: Iterable[str] | None = None) -> str:
    """Markdown bibliography of ``keys`` (default: all), sorted by key."""
    chosen = sorted(set(keys)) if keys is not None else list(REFERENCES)
    return "\n".join(f"- **[{k}]** {REFERENCES[k].format()}" + (f" — {REFERENCES[k].note}" if REFERENCES[k].note
                                                                    else "") for k in chosen)
