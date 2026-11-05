"""aerokit.bracket.lifecheck: temperature/surface knock-downs and the 0 → σ cycle."""
import pytest

from aerokit.bracket import lifecheck as lc
from aerokit.bracket import matdata
from aerokit.structures.fatigue import marin_kd


def test_steel_uses_marin_kd_and_goodman_or_swt():
    r = lc.screen("structural_steel", 100e6, 300.0)
    assert r["k_T"] == pytest.approx(marin_kd(300.0))
    assert r["se_T_Pa"] == pytest.approx(86.2e6 * marin_kd(300.0))
    sut = matdata.get("structural_steel").Ftu_at(300.0)
    good = 50e6 / (1 - 50e6 / sut)
    swt = (100e6 * 50e6) ** 0.5
    assert r["sigma_ar_Pa"] == pytest.approx(max(good, swt))


def test_r01_reference_converted_and_surface_factor():
    r = lc.screen("scalmalloy", 50e6, 100.0)
    sm = 87e6 * 1.1 / 0.9
    assert r["se_ref_R-1_Pa"] == pytest.approx(87e6 / (1 - sm / 520e6), rel=1e-3)
    assert r["k_surface"] == pytest.approx(41 / 87)
    assert r["margin_machined"] == pytest.approx(r["margin"] / r["k_surface"])


def test_no_data_and_temperature_lowers_margin():
    assert lc.screen("ss_17_4ph", 100e6, 300.0)["status"] == "no data"
    cold, hot = lc.screen("ti64_lpbf", 200e6, 20.0), lc.screen("ti64_lpbf", 200e6, 300.0)
    assert hot["k_T"] < 1.0 == pytest.approx(cold["k_T"]) and hot["margin"] < cold["margin"]
    md = lc.markdown([hot, lc.screen("ss_17_4ph", 1e6, 300.0)], 300.0)
    assert "Margin, machined surface" in md and "no endurance value" in md
