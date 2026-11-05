"""Synthetic traffic chain: SSR code validation over several replies; I/Q-level PSR path smoke test."""
from aerokit.atc.traffic import Scenario, simulate


def test_ssr_code_validation_meets_recommended_figures_at_moderate_fruit():
    one = simulate(Scenario(seed=0, duration_s=90.0))["stats"]["kpi"]
    four = simulate(Scenario(seed=0, duration_s=90.0, ssr_replies_per_mode=4))["stats"]["kpi"]
    assert four["mode_a_valid"] > one["mode_a_valid"]
    assert four["mode_a_valid"] > 0.98 and four["mode_c_valid"] > 0.96        # EUROCONTROL 1997 recommended
    assert four["mode_a_wrong"] == 0.0


def test_validation_removes_wrong_codes_at_high_fruit():
    one = simulate(Scenario(seed=0, fruit_per_s=10000.0))["stats"]["kpi"]
    four = simulate(Scenario(seed=0, fruit_per_s=10000.0, ssr_replies_per_mode=4))["stats"]["kpi"]
    assert one["mode_a_wrong"] > 0.0 and four["mode_a_wrong"] == 0.0


def test_iq_psr_chain_runs_inside_the_traffic_simulation():
    r = simulate(Scenario(seed=0, duration_s=14.4, psr_chain="mtd_cmap", psr_warmup_scans=2))
    assert len(r["frames"]) == 4
    assert r["stats"]["psr_detections"] + r["stats"]["psr_misses"] == 4 * 6
