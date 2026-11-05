"""ILS DDM receiver: DDM recovered from the tones; any lost signal gives a FLAG, never a centred needle."""
import pytest

from aerokit.atc.ils import ils_baseband, read_ils

FS = 8000


@pytest.mark.parametrize("ddm", [-0.155, -0.08, 0.0, 0.04, 0.155])
def test_ddm_recovered(ddm):
    r = read_ils(ils_baseband(ddm, FS, snr_db=30, seed=2), FS)
    assert not r.flag and r.ddm == pytest.approx(ddm, abs=0.003)
    assert r.dots == pytest.approx(2.0 * ddm / 0.155, abs=0.05)


def test_full_scale_clips_at_two_dots():
    r = read_ils(ils_baseband(0.18, FS, sdm=0.40), FS)
    assert r.dots == pytest.approx(2.0)


def test_no_carrier_flags():
    r = read_ils(ils_baseband(0.0, FS, carrier=0.0, snr_db=20), FS)
    assert r.flag and r.dots is None and "carrier" in r.reason


def test_missing_tone_flags_not_centred():
    # a dead modulator that drops both tones would read DDM = 0 ("on course") without validation
    r = read_ils(ils_baseband(0.0, FS, tones=(False, False)), FS)
    assert r.flag and r.dots is None
    r1 = read_ils(ils_baseband(0.05, FS, tones=(True, False)), FS)
    assert r1.flag and "tone" in r1.reason


def test_sdm_out_of_range_flags():
    r = read_ils(ils_baseband(0.0, FS, sdm=0.15), FS)
    assert r.flag and "sum of modulation" in r.reason
