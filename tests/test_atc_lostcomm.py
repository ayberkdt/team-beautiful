"""Lost-comm rule sets: EU 20 min / 30 min / 7601, ICAO-EUR legacy 7 min, US no timer; the aid never picks 7601 for
the pilot; every comm state has a display policy."""
import pytest

from aerokit.atc import lostcomm as LC
from aerokit.atc.commhealth import States


def test_eu_timeline_numbers_and_order():
    tl = LC.timeline("EU_SERA_2025", eat_min=35.0, eta_min=30.0)
    times = [m.t_min for m in tl if m.t_min is not None]
    assert times == sorted(times)
    assert any(m.t_min == 20.0 and "20 min hold" in m.text for m in tl)
    assert any(m.t_min == 35.0 and "EAT" in m.text for m in tl)                  # descent at the EAT
    assert any(m.t_min == 65.0 and "30 min" in m.text for m in tl)               # later of ETA/EAT + 30
    assert all(m.source for m in tl)


def test_legacy_and_us_differ():
    assert LC.RULE_SETS["ICAO_EUR_LEGACY"].hold_min == 7.0
    us = LC.timeline("US_14CFR_91_185", eta_min=30.0)
    assert LC.RULE_SETS["US_14CFR_91_185"].hold_min is None
    assert not any("hold of last assigned" in m.text for m in us)
    assert not any("Land, if possible" in m.text for m in us)                    # no 30-min window in 91.185


def test_no_eta_gives_untimed_descent_reminder():
    tl = LC.timeline("EU_SERA_2025")
    assert any(m.t_min is None and "no EAT/ETA" in m.text for m in tl)


def test_7601_needs_the_commander():
    assert LC.squawk_guidance("EU_SERA_2025", vmc=True, ifr=True, commander_continues_vmc=None)["suggest"] == \
        "7600 or 7601"
    assert LC.squawk_guidance("EU_SERA_2025", vmc=True, ifr=True, commander_continues_vmc=True)["suggest"] == "7601"
    assert LC.squawk_guidance("EU_SERA_2025", vmc=False, ifr=True, commander_continues_vmc=True)["suggest"] == "7600"
    assert LC.squawk_guidance("ICAO_EUR_LEGACY", vmc=True, ifr=True, commander_continues_vmc=True)["suggest"] == "7600"


def test_display_policy_covers_every_state_and_forbids_new_items_when_lost():
    assert set(LC.DISPLAY_POLICY) == set(States.ALL)
    for s in (States.RX_LOST, States.ALL_COMMS_LOST):
        assert LC.display_policy(s)["new_voice_items"].startswith("none")
    with pytest.raises(KeyError):
        LC.display_policy("SOMETHING")
