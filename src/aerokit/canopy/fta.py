"""Fault-tree algebra for independent basic events: exact gates, minimal cut sets, importance measures.

A tree is a nested tuple: a basic event is a string; a gate is ``("AND", child, ...)`` or ``("OR", child, ...)``.
Exact evaluation assumes independent basic events *and no repeated events*; with repeated events use
:func:`cut_set_probability` (rare-event sum over minimal cut sets) or :func:`exact_by_enumeration` (2ⁿ states).
"""
from __future__ import annotations

import itertools
from collections.abc import Mapping, Sequence
from typing import Union

from aerokit.references import cite

Tree = Union[str, tuple]

__all__ = ["Tree", "p_and", "p_or", "evaluate", "basic_events", "minimal_cut_sets", "cut_set_probability",
           "exact_by_enumeration", "importance", "standby_unavailability"]


def p_and(*p: float) -> float:
    out = 1.0
    for v in p:
        out *= v
    return out


def p_or(*p: float) -> float:
    q = 1.0
    for v in p:
        q *= 1.0 - v
    return 1.0 - q


def _check(tree: Tree) -> None:
    if isinstance(tree, str):
        return
    if not isinstance(tree, tuple) or len(tree) < 2 or tree[0] not in ("AND", "OR"):
        raise ValueError(f"not a gate: {tree!r}")
    for ch in tree[1:]:
        _check(ch)


def basic_events(tree: Tree) -> list[str]:
    if isinstance(tree, str):
        return [tree]
    out: list[str] = []
    for ch in tree[1:]:
        out += [e for e in basic_events(ch) if e not in out]
    return out


def evaluate(tree: Tree, probs: Mapping[str, float]) -> float:
    """Exact top probability by gate algebra (independent events, each basic event used once)."""
    _check(tree)
    ev = basic_events(tree)
    flat = _flat_events(tree)
    if len(flat) != len(ev):
        raise ValueError("repeated basic event: use cut_set_probability or exact_by_enumeration")
    return _eval(tree, probs)


def _flat_events(tree: Tree) -> list[str]:
    return [tree] if isinstance(tree, str) else [e for ch in tree[1:] for e in _flat_events(ch)]


def _eval(tree: Tree, probs: Mapping[str, float]) -> float:
    if isinstance(tree, str):
        return float(probs[tree])
    vals = [_eval(ch, probs) for ch in tree[1:]]
    return p_and(*vals) if tree[0] == "AND" else p_or(*vals)


def minimal_cut_sets(tree: Tree) -> list[frozenset[str]]:
    """Minimal cut sets by top-down expansion with absorption."""
    _check(tree)

    def cs(t: Tree) -> list[frozenset[str]]:
        if isinstance(t, str):
            return [frozenset([t])]
        kids = [cs(ch) for ch in t[1:]]
        if t[0] == "OR":
            return [s for k in kids for s in k]
        out: list[frozenset[str]] = [frozenset()]
        for k in kids:
            out = [a | b for a in out for b in k]
        return out

    sets = sorted(set(cs(tree)), key=lambda s: (len(s), sorted(s)))
    minimal: list[frozenset[str]] = []
    for s in sets:
        if not any(m <= s for m in minimal):
            minimal.append(s)
    return minimal


@cite("nasa_fth_2002", note="sec. 7.1 and App. B Eq. B.8: sum of minimal-cut-set products, conservative, P < 0.1")
def cut_set_probability(tree: Tree, probs: Mapping[str, float]) -> float:
    """Rare-event approximation: Σ over minimal cut sets of ∏ basic-event probabilities."""
    return sum(p_and(*(probs[e] for e in s)) for s in minimal_cut_sets(tree))


def _bool(tree: Tree, state: Mapping[str, bool]) -> bool:
    if isinstance(tree, str):
        return state[tree]
    vals = [_bool(ch, state) for ch in tree[1:]]
    return all(vals) if tree[0] == "AND" else any(vals)


def exact_by_enumeration(tree: Tree, probs: Mapping[str, float]) -> float:
    """Exact top probability for independent events, repeated events allowed (2ⁿ states; n ≤ 20)."""
    ev = basic_events(tree)
    if len(ev) > 20:
        raise ValueError("too many basic events to enumerate")
    total = 0.0
    for bits in itertools.product((False, True), repeat=len(ev)):
        if _bool(tree, dict(zip(ev, bits))):
            w = 1.0
            for e, b in zip(ev, bits):
                w *= probs[e] if b else 1.0 - probs[e]
            total += w
    return total


@cite("nasa_fth_2002", note="pp. 90-91: Fussell-Vesely, RRW, RAW, Birnbaum = P(top|1) - P(top|0)")
def importance(tree: Tree, probs: Mapping[str, float]) -> dict[str, dict[str, float]]:
    """Per basic event: Fussell-Vesely (share of the cut-set sum), risk reduction worth and risk achievement worth
    (as ratios top/top(0) and top(1)/top) and Birnbaum (difference), all from exact enumeration."""
    top = exact_by_enumeration(tree, probs)
    mcs = minimal_cut_sets(tree)
    rare = sum(p_and(*(probs[e] for e in s)) for s in mcs)
    out: dict[str, dict[str, float]] = {}
    for e in basic_events(tree):
        p1 = exact_by_enumeration(tree, {**probs, e: 1.0})
        p0 = exact_by_enumeration(tree, {**probs, e: 0.0})
        fv = sum(p_and(*(probs[x] for x in s)) for s in mcs if e in s) / rare if rare > 0 else 0.0
        out[e] = {"fussell_vesely": fv, "rrw": top / p0 if p0 > 0 else float("inf"),
                  "raw": p1 / top if top > 0 else float("inf"), "birnbaum": p1 - p0}
    return out


@cite("nasa_fth_2002", note="Eq. 7.6: q = (lambda*T/2)/(1 + lambda*T/2) for a periodically tested standby component")
def standby_unavailability(rate_per_h: float, test_interval_h: float) -> float:
    """Mean unavailability of a latent (hidden) failure found only by a test every ``test_interval_h`` hours."""
    if rate_per_h < 0 or test_interval_h < 0:
        raise ValueError("rate and interval must be >= 0")
    x = 0.5 * rate_per_h * test_interval_h
    return x / (1.0 + x)


def tree_text(tree: Tree, indent: str = "") -> str:
    """Indented plain-text drawing of a tree (for reports)."""
    if isinstance(tree, str):
        return f"{indent}- {tree}\n"
    return f"{indent}{tree[0]}\n" + "".join(tree_text(ch, indent + "    ") for ch in tree[1:])


__all__.append("tree_text")

