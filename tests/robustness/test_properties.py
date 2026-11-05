"""Property-based robustness tests (hypothesis): physical invariants, input validation and
serialisation that must hold for *any* admissible input, not just the benchmark cases."""
from __future__ import annotations

import json
import math

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from aerokit.aero import atmosphere
from aerokit.fem import Model
from aerokit.fem.elements.line import Bar
from aerokit.output.report import Report
from aerokit.output.tables import Table
from aerokit.structures.tensor import Stress

finite = st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False)
SETTINGS = settings(max_examples=60, deadline=None)


@SETTINGS
@given(st.floats(min_value=0.0, max_value=20_000.0), st.floats(min_value=1.0, max_value=500.0))
def test_isa_monotone_and_positive(h, dh):
    """Pressure and density fall with altitude; all state variables stay positive and finite."""
    a, b = atmosphere.isa(h), atmosphere.isa(min(h + dh, 20_000.0))
    for k in ("T", "p", "rho", "mu", "a"):
        assert math.isfinite(a[k]) and a[k] > 0
    if b is not a and h + dh <= 20_000.0:
        assert b["p"] < a["p"] and b["rho"] < a["rho"]
    assert a["p"] == pytest.approx(a["rho"] * 287.05287 * a["T"], rel=1e-3)   # ideal gas


@SETTINGS
@given(st.lists(finite, min_size=6, max_size=6), st.floats(min_value=0, max_value=2 * math.pi),
       st.floats(min_value=0, max_value=math.pi))
def test_stress_invariants_under_rotation(s, a1, a2):
    """von Mises, Tresca and the invariants do not depend on the coordinate frame."""
    g = Stress(*s)
    c1, s1, c2, s2 = math.cos(a1), math.sin(a1), math.cos(a2), math.sin(a2)
    R = np.array([[c1, -s1, 0], [s1, c1, 0], [0, 0, 1]]) @ np.array([[1, 0, 0], [0, c2, -s2], [0, s2, c2]])
    r = g.rotate(R)
    scale = max(1.0, max(abs(x) for x in s))
    assert r.von_mises() == pytest.approx(g.von_mises(), abs=1e-9 * scale)
    assert r.tresca() == pytest.approx(g.tresca(), abs=1e-9 * scale)
    for x, y in zip(r.invariants(), g.invariants(), strict=True):
        assert x == pytest.approx(y, abs=1e-8 * scale ** 3)


@SETTINGS
@given(st.floats(min_value=1e9, max_value=4e11), st.floats(min_value=1e-6, max_value=1e-2),
       st.floats(min_value=0.1, max_value=10.0), finite, finite)
def test_truss_equilibrium_and_clapeyron(E, A, L, fx, fy):
    """Two-bar truss: reactions balance the load and strain energy equals ½ Fᵀu (Clapeyron)."""
    assume(abs(fx) + abs(fy) > 1e-6)
    m = Model([[0.0, 0.0], [L, 0.0], [L, L]], ndof=2)
    m.add(Bar(0, 2, E, A))
    m.add(Bar(1, 2, E, A))
    m.fix(0, [0, 1])
    m.fix(1, [0, 1])
    m.load(2, 0, fx)
    m.load(2, 1, fy)
    r = m.static()
    total = r.reaction.reshape(-1, 2).sum(axis=0) + np.array([fx, fy])
    assert np.allclose(r.reaction.reshape(-1, 2).sum(axis=0), -np.array([fx, fy]), atol=1e-9 * (abs(fx) + abs(fy)))
    assert np.allclose(total, 0.0, atol=1e-9 * (abs(fx) + abs(fy)))
    assert r.energy == pytest.approx(0.5 * m.F @ r.u, rel=1e-9)
    json.dumps(r.to_dict())        # results are JSON serialisable


@pytest.mark.parametrize("bad", [[[0.0, np.nan]], [[0.0, np.inf], [1.0, 0.0]], [[0, 0, 0, 0]], [0.0, 1.0]])
def test_model_rejects_invalid_nodes(bad):
    with pytest.raises(ValueError):
        Model(bad, 2)


def test_model_rejects_invalid_definitions():
    m = Model([[0.0, 0.0], [1.0, 0.0]], 2)
    with pytest.raises(ValueError):
        m.load(0, 0, float("nan"))
    with pytest.raises(ValueError):
        m.fix(5, 0)
    with pytest.raises(ValueError):
        m.add(Bar(0, 7, 70e9, 1e-4))
    with pytest.raises(ValueError):
        m.add(Bar(1, 1, 70e9, 1e-4))
    with pytest.raises(ValueError):
        Model([[0.0, 0.0]], 0)


@SETTINGS
@given(st.lists(st.lists(st.text(max_size=12), min_size=3, max_size=3), max_size=6), st.text(max_size=20))
def test_table_renders_any_text(rows, title):
    """Arbitrary cell text renders in every format, one physical line per row, valid JSON/CSV."""
    t = Table(["a", "b (m)", "c"], rows, title)
    text = t.to_text()
    assert len(text.split(chr(10))) == len(rows) + 2 + (1 if t.title else 0)
    md = t.to_markdown()
    assert md.count("\n") >= len(rows) + 1
    assert json.loads(t.to_json())["rows"] == [list(r) for r in t.rows]
    assert t.to_csv().count("\n") >= len(rows) + 1


def test_table_rejects_ragged_rows():
    with pytest.raises(ValueError):
        Table(["a", "b"], [["1"]])
    with pytest.raises(ValueError):
        Table([], [])


@SETTINGS
@given(st.text(max_size=40), st.text(max_size=40), st.lists(st.text(max_size=20), max_size=3))
def test_report_round_trip(res, nxt, notes):
    rep = Report(title="t")
    for n in notes:
        rep.note(n)
    rep.table(["x", "y"], [["1", "2"]])
    rep.conclude(res, nxt)
    d = json.loads(rep.render("json"))
    assert d["result"] == res and d["next_step"] == nxt and d["tables"][0]["rows"] == [["1", "2"]]
    text = rep.render("text")
    if res:
        assert text.splitlines()[-1] == f"Next step: {nxt}".rstrip() or text.endswith(f"Next step: {nxt}")
    with pytest.raises(ValueError):
        rep.render("xml")
