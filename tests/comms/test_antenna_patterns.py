# Copied from Sidera (tests/communications/test_antenna_patterns.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Radiation patterns against independent references.

- Tapered circular aperture: the closed form ``Lambda_{p+1}`` against a direct
  numerical Hankel transform of the illumination ``(1 - rho^2)^p``; the first
  null of the uniform aperture at the first root of J1 (3.8317); the first
  side-lobe levels -17.57 / -24.64 / -30.61 dB.
- MRO's 3 m high-gain antenna: DESCANSO series article 12, table 2-2, quotes a
  0.69 deg half-power beamwidth at X band (8.439 GHz) and 0.18 deg at Ka
  (32.2 GHz); a uniform aperture of that size gives 0.70 and 0.18 deg.
- Gaussian beam: half power at half the beamwidth, and the same curve as the
  DSN 104 eq. A-3 pointing loss up to its rounded constant (2.773 vs 4 ln 2).
- ITU-R S.465-6: the envelope values at chosen angles and the phi_min rules.
"""

from __future__ import annotations

import math

import pytest
from scipy import integrate, optimize, special

from aerokit.comms.dsn import pointing_loss_db
from aerokit.comms.antennas import (
    GaussianBeamPattern,
    ItuS465ReferencePattern,
    TabulatedPattern,
    TaperedApertureAntenna,
    tapered_aperture_field,
)
from aerokit.comms.rf import RfError, wavelength_m


def _hankel(u: float, p: int) -> float:
    """``int_0^1 (1 - rho^2)^p J0(u rho) rho d rho`` normalised to 1 at u = 0 (value 1 / (2 (p + 1)))."""
    value, _ = integrate.quad(lambda r: (1.0 - r * r) ** p * special.j0(u * r) * r, 0.0, 1.0,
                              epsabs=1e-14, epsrel=1e-12, limit=200)
    return value * 2.0 * (p + 1)


@pytest.mark.parametrize("p", [0, 1, 2])
def test_the_closed_form_far_field_is_the_hankel_transform_of_the_taper(p: int) -> None:
    for u in (0.3, 1.0, 2.5, 4.0, 6.0, 9.0, 13.0, 20.0, 30.0, 45.0):
        closed, numeric = tapered_aperture_field(u, p), _hankel(u, p)
        assert closed == pytest.approx(numeric, abs=1e-11)
        # In dB where the field is not near a null: 1e-6 dB is 1.2e-7 relative.
        if abs(numeric) > 1e-3:
            assert 20 * math.log10(abs(closed)) == pytest.approx(20 * math.log10(abs(numeric)), abs=1e-6)


@pytest.mark.parametrize(("p", "first_sidelobe_db", "hpbw_lambda_over_d"),
                         [(0, -17.57, 1.029), (1, -24.64, 1.270), (2, -30.61, 1.473)])
def test_beamwidth_and_first_side_lobe_of_the_tapers(p: int, first_sidelobe_db: float,
                                                     hpbw_lambda_over_d: float) -> None:
    # First null and first side-lobe peak from the field itself.
    first_null = optimize.brentq(lambda u: tapered_aperture_field(u, p), 3.0, 3.83 + 1.7 * p + 1.0)
    peak = optimize.minimize_scalar(lambda u: -abs(tapered_aperture_field(u, p)),
                                    bounds=(first_null, first_null + 3.5), method="bounded",
                                    options={"xatol": 1e-10})
    level = 20.0 * math.log10(abs(tapered_aperture_field(peak.x, p)))
    assert level == pytest.approx(first_sidelobe_db, abs=0.01)
    if p == 0:
        assert first_null == pytest.approx(3.831705970207512, abs=1e-12)  # first root of J1
    # Beamwidth in lambda/D for a large aperture (small-angle limit).
    antenna = TaperedApertureAntenna(100.0, 0.5, taper_p=p)
    f = 10e9
    assert antenna.half_power_beamwidth(f) / (wavelength_m(f) / 100.0) == pytest.approx(hpbw_lambda_over_d, abs=1e-3)


def test_mro_high_gain_antenna_beamwidth_matches_its_published_value() -> None:
    hga = TaperedApertureAntenna(3.0, 0.665, taper_p=0)
    assert math.degrees(hga.half_power_beamwidth(8.439e9)) == pytest.approx(0.69, abs=0.015)
    assert math.degrees(hga.half_power_beamwidth(32.2e9)) == pytest.approx(0.18, abs=0.005)
    # 46.7 dBi published at X band transmit; an efficiency of 0.665 reproduces it.
    assert hga.boresight_gain_dbi(8.439e9) == pytest.approx(46.7, abs=0.02)


def test_the_tapered_aperture_is_half_power_at_half_its_beamwidth() -> None:
    antenna = TaperedApertureAntenna(3.0, 0.6, taper_p=1)
    f = 8.4e9
    half = 0.5 * antenna.half_power_beamwidth(f)
    assert antenna.gain_dbi(f, half) - antenna.gain_dbi(f, 0.0) == pytest.approx(-10 * math.log10(2), abs=1e-9)
    assert antenna.gain_dbi(f, 2.0) == -10.0  # behind the aperture
    with pytest.raises(RfError, match="exceeds the taper efficiency"):
        TaperedApertureAntenna(3.0, 0.8, taper_p=1)


def test_the_gaussian_beam_is_the_dsn_pointing_loss() -> None:
    beam = GaussianBeamPattern(50.0, math.radians(0.1))
    assert beam.gain_dbi(8.4e9, math.radians(0.05)) == pytest.approx(50.0 - 10 * math.log10(2), abs=1e-12)
    for error_deg in (0.01, 0.03, 0.08):
        ours = 50.0 - beam.gain_dbi(8.4e9, math.radians(error_deg))
        dsn = pointing_loss_db(error_deg, 0.1)
        assert ours == pytest.approx(dsn, rel=2e-4)  # 2.773 against 4 ln 2 = 2.77259
    with pytest.raises(RfError, match="beyond the main lobe"):
        beam.gain_dbi(8.4e9, math.radians(0.2))


def test_itu_s465_envelope() -> None:
    dish = ItuS465ReferencePattern(diameter_m=3.0)
    f = 12e9  # D/lambda = 120: phi_min = max(1, 100/120) = 1 deg
    assert dish.phi_min_deg(f) == pytest.approx(1.0)
    assert dish.gain_dbi(f, math.radians(10.0)) == pytest.approx(32.0 - 25.0, abs=1e-12)
    assert dish.gain_dbi(f, math.radians(48.0)) == -10.0
    assert dish.gain_dbi(f, math.radians(1.0)) == pytest.approx(32.0, abs=1e-12)
    small = ItuS465ReferencePattern(diameter_m=0.6, receiving=False)  # D/lambda = 24 at 12 GHz
    assert small.phi_min_deg(f) == pytest.approx(max(2.0, 114.0 * (0.6 / wavelength_m(f)) ** -1.09))
    assert ItuS465ReferencePattern(diameter_m=0.6).phi_min_deg(f) == 2.5  # note 5
    with pytest.raises(RfError, match="2 to 31 GHz"):
        dish.gain_dbi(0.4e9, 0.1)


def test_a_tabulated_pattern_interpolates_in_theta_and_between_cuts() -> None:
    sym = TabulatedPattern((0.0, math.radians(30), math.radians(60)), (4.7, 2.7, -1.3))
    assert sym.gain_dbi(4e8, math.radians(15)) == pytest.approx(3.7)
    with pytest.raises(RfError, match="outside the table"):
        sym.gain_dbi(4e8, math.radians(61))
    cuts = TabulatedPattern((0.0, 1.0), ((0.0, -10.0), (0.0, -20.0)), phi_rad=(0.0, math.pi / 2))
    assert cuts.gain_dbi(1e9, 1.0, math.pi / 4) == pytest.approx(-15.0)
    # Periodic: between the last cut (90 deg) and the first one turn later (360 deg).
    assert cuts.gain_dbi(1e9, 1.0, math.radians(225.0)) == pytest.approx(-15.0)
    with pytest.raises(RfError, match="needs the azimuth"):
        cuts.gain_dbi(1e9, 0.5)
