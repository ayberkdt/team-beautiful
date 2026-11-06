"""PAR talk-down: phrase classes, round trip phrase -> display state, guidance-lost timer, decision height."""
import numpy as np

from aerokit.approach import ApproachSimConfig, NavSensor, Runway, simulate_approach
from aerokit.atc.par import (ParGuidanceMonitor, ParMeasurement, TalkdownRules, parse_talkdown, talkdown_phrase,
                             talkdown_series)

RWY = Runway(51.0, 4.0, 10.0, 250.0)


def m(t, el, az, rng_nm=5.0):
    return ParMeasurement(t, rng_nm * 1852, el, az, 0.0, 0.0)


def test_phrase_classes():
    r = TalkdownRules()
    assert "on course" in talkdown_phrase(m(0, 0.0, 0.1), None, 250, r)
    assert "on glidepath" in talkdown_phrase(m(0, 0.05, 0.0), None, 250, r)
    p = talkdown_phrase(m(0, -0.2, 0.4), None, 250, r)
    assert "slightly below glidepath" in p and "slightly right of course turn left heading two four six" in p
    assert "well above glidepath" in talkdown_phrase(m(0, 0.5, 0.0), None, 250, r)


def test_trend_and_correcting():
    p_up = talkdown_phrase(m(5, 0.25, 0), m(0, 0.1, 0), 250)          # +0.03 deg/s
    assert "going up slowly" in p_up
    p_down = talkdown_phrase(m(5, 0.15, 0), m(0, 0.65, 0), 250)       # -0.10 deg/s
    assert "coming down rapidly" in p_down


def test_round_trip_to_display():
    p = talkdown_phrase(m(5, -0.4, -0.7, 2.95), m(0, -0.2, -0.5, 3.05), 250, callsign_words="beetle one two three")
    st = parse_talkdown(p, 5.0)
    assert (st.glidepath, st.course, st.trend) == ("WELL BELOW", "WELL LEFT", "COMING DOWN SLOWLY")
    assert st.heading == 257 and st.miles == 3          # 0.7 deg left x 10 deg/deg -> 7 deg right


def test_unheard_parts_stay_unknown():
    st = parse_talkdown("beetle one two three slightly above", 1.0)
    assert st.glidepath == "?" and st.course == "?" and st.heading is None


def test_guidance_lost_after_5_s():
    mon = ParGuidanceMonitor()
    assert mon.view(0.0)["status"] == "NO PAR GUIDANCE YET"
    mon.receive(parse_talkdown("on course on glidepath", 10.0))
    assert mon.view(14.0)["status"] == "PAR GUIDANCE"
    v = mon.view(15.5)
    assert v["status"].startswith("PAR GUIDANCE LOST") and v["state"] is None


def test_series_on_simulated_approach_detects_biased_aircraft():
    run = simulate_approach(RWY, NavSensor("biased", bias=(0, 40, -25), sigma=(0, 5, 3)),
                            ApproachSimConfig(x0=8 * 1852, y0=150, gust_sigma=1.0), rng=np.random.default_rng(1))
    ser = talkdown_series(RWY, run.t, run.x, run.y, run.z)
    phrases = [p for _, p in ser]
    assert phrases[-1].endswith("at decision height")
    late = " ".join(phrases[-8:-1])
    assert "above glidepath" in late and "left of course" in late        # the ground radar sees the bias
    assert all(b.t - a.t >= 4.9 for (a, _), (b, _) in zip(ser[:-2], ser[1:-1]))


def test_par_call_overdue_and_age_display():
    mon = ParGuidanceMonitor(lost_after_s=10.0, expected_every_s=5.0)
    mon.receive(parse_talkdown("beetle one two three on glidepath on course", 0.0))
    assert mon.view(3.0)["display"] == "PAR GUIDANCE - last call 3 s"
    v = mon.view(7.0)
    assert v["status"].startswith("PAR CALL OVERDUE") and v["caution"] and v["state"] is not None
    assert mon.view(11.0)["status"].startswith("PAR GUIDANCE LOST")
    assert ParGuidanceMonitor().view(0.0)["display"] == "NO PAR GUIDANCE YET"
