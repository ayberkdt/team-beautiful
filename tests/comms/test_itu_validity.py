# Copied from Sidera (tests/communications/test_audit_fix_itu_validity.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Audit fix L7: ITU-R P.618-13 validity limits read from the Recommendation.

Sec 2.2.1.1 gives the rain procedure "for frequencies up to 55 GHz"; Sec 2.4.1 is
the scintillation method for free-space elevations of 5 degrees and above (it
used to clamp at 4 degrees).
"""

from __future__ import annotations

import math
import warnings

import pytest

from aerokit.comms.itu_earth import (
    MINIMUM_VALID_ELEVATION_DEG,
    EarthSiteWeather,
    LegacyLatitudeFallback,
    rain_attenuation_001_db,
    rain_attenuation_db,
    scintillation_fade_db,
)
from aerokit.comms.rf import RfError


def _weather() -> EarthSiteWeather:
    return EarthSiteWeather(
        rain_rate_001_mm_per_h=42.0,
        rain_height=LegacyLatitudeFallback(),
        columnar_liquid_water_kg_m2=0.6,
        polarization_tilt_deg=90.0,
    )


@pytest.mark.parametrize("frequency_ghz", [55.0001, 80.0, 400.0])
def test_rain_above_55_ghz_is_refused(frequency_ghz: float) -> None:
    with pytest.raises(RfError, match="up to 55 GHz"):
        rain_attenuation_001_db(frequency_ghz, 30.0, 41.9, 0.05, _weather())
    with pytest.raises(RfError, match="up to 55 GHz"):
        rain_attenuation_db(frequency_ghz, 30.0, 41.9, 0.05, _weather(), 0.01)


def test_rain_at_55_ghz_is_still_computed() -> None:
    assert rain_attenuation_001_db(55.0, 30.0, 41.9, 0.05, _weather()) > 0.0


@pytest.mark.parametrize("frequency_ghz", [2.2, 3.9999, 20.0001, 20.2, 30.0])
def test_scintillation_outside_4_to_20_ghz_warns_and_still_computes(frequency_ghz: float) -> None:
    with pytest.warns(RuntimeWarning, match="specified for 4-20 GHz.*extrapolation"):
        fade = scintillation_fade_db(frequency_ghz, 30.0, 1.2, 0.6, _weather(), 0.01)
    assert math.isfinite(fade)
    assert fade > 0.0


@pytest.mark.parametrize("frequency_ghz", [4.0, 20.0])
def test_scintillation_at_the_edges_of_4_to_20_ghz_does_not_warn(frequency_ghz: float) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert scintillation_fade_db(frequency_ghz, 30.0, 1.2, 0.6, _weather(), 0.01) > 0.0


@pytest.mark.parametrize("frequency_ghz", [0.0, -14.0, float("nan"), float("inf")])
def test_scintillation_refuses_a_non_positive_or_non_finite_frequency(frequency_ghz: float) -> None:
    with pytest.raises(RfError, match="frequency"):
        scintillation_fade_db(frequency_ghz, 30.0, 1.2, 0.6, _weather(), 0.01)


def test_scintillation_below_5_degrees_is_evaluated_at_5_degrees() -> None:
    assert MINIMUM_VALID_ELEVATION_DEG == 5.0

    def fade(elevation_deg: float) -> float:
        return scintillation_fade_db(14.0, elevation_deg, 1.2, 0.6, _weather(), 0.01)

    at_floor = fade(5.0)
    assert fade(3.0) == at_floor
    assert fade(4.5) == at_floor
    assert fade(6.0) < at_floor
