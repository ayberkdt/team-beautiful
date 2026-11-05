# Copied from Sidera (tests/communications/test_communications_propagation.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""ITU-R Earth slant-path propagation and the sky-noise coupling.

Three layers, as in `test_communications_rf.py`.

**Layer A, legacy parity.** Every migrated ITU-R model is pinned to the value
the source repository produces at revision
91225ca6a190c164a0a0c2a53f1f855236b00de8. The anchors were taken by running that
module directly; they are quoted here to full float precision so that a port
that drifts by one coefficient is caught rather than absorbed.

**Layer B, analytic physics.** The cosecant projection, the P.618 Section 2.5
combination rule, the radiative-transfer emission law, and the monotonicities
the Recommendations imply -- each checked against algebra done in the test
rather than against a stored number.

**Layer C, the structural properties the migration exists for.** That the rain
rate cannot be defaulted, that the rain-height fallback does not claim to be the
P.839 map, that scintillation never reaches the noise model, and that a
sky-noise model sees the attenuation that was actually applied.
"""

from __future__ import annotations

import dataclasses
import math

import pytest

from aerokit.comms import (
    CommunicationLink,
    CommunicationTerminal,
    EarthItuPropagation,
    EarthSiteWeather,
    ExplicitRainHeight,
    FixedAtmosphericAllowance,
    FixedGainAntenna,
    LegacyLatitudeFallback,
    PropagationLossBreakdown,
    Receiver,
    RfError,
    SimplifiedAtmosphericEmissionNoise,
    Transmitter,
    cloud_attenuation_db,
    evaluate_link,
    gaseous_attenuation_db,
    geometry_from_states,
    legacy_rome_ankara_weather,
    rain_attenuation_001_db,
    rain_attenuation_db,
    rain_coefficients_p838,
    scintillation_fade_db,
    wet_term_refractivity,
)
from aerokit.comms.itu_earth import (
    EFFECTIVE_EARTH_RADIUS_KM,
    SCINTILLATION_TURBULENT_LAYER_HEIGHT_M,
)

# The Rome uplink geometry frozen in the source repository's
# ``outputs/geometry_static.csv``. Reused here so the propagation anchors sit on
# the same path as the link-budget anchors in ``test_communications_rf.py``.
ROME_ELEVATION_DEG = 41.59952992966065
ROME_LATITUDE_DEG = 41.9
ROME_HEIGHT_KM = 0.05
UPLINK_GHZ = 14.0


def _rome_weather(**overrides: object) -> EarthSiteWeather:
    fields: dict[str, object] = {
        "rain_rate_001_mm_per_h": 42.0,
        "rain_height": LegacyLatitudeFallback(),
        "columnar_liquid_water_kg_m2": 0.6,
        "polarization_tilt_deg": 90.0,
    }
    fields.update(overrides)
    return EarthSiteWeather(**fields)  # type: ignore[arg-type]


def _slant_geometry(
    range_m: float = 3.7e7, elevation_deg: float = ROME_ELEVATION_DEG
) -> object:
    """A one-dimensional geometry carrying a stated elevation.

    The propagation models depend only on range and elevation, so the two states
    are placed on an axis and the elevation is attached explicitly rather than
    derived from a fabricated station position.
    """
    return geometry_from_states(
        0.0,
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [range_m, 0.0, 0.0, 0.0, 0.0, 0.0],
        elevation_rad=math.radians(elevation_deg),
    )


# ---------------------------------------------------------------------------
# Layer A -- parity with the migrated source
# ---------------------------------------------------------------------------


def test_p838_coefficients_match_the_source() -> None:
    k, alpha = rain_coefficients_p838(UPLINK_GHZ, ROME_ELEVATION_DEG, 90.0)
    assert k == pytest.approx(0.040402457040800595, rel=0.0, abs=1e-15)
    assert alpha == pytest.approx(1.0799030214785728, rel=0.0, abs=1e-15)

    k_c, alpha_c = rain_coefficients_p838(12.0, 39.44310549852194, 45.0)
    assert k_c == pytest.approx(0.024203061156118633, rel=0.0, abs=1e-15)
    assert alpha_c == pytest.approx(1.1515991963044687, rel=0.0, abs=1e-15)


def test_rain_attenuation_matches_the_source() -> None:
    weather = _rome_weather()
    a_001 = rain_attenuation_001_db(
        UPLINK_GHZ, ROME_ELEVATION_DEG, ROME_LATITUDE_DEG, ROME_HEIGHT_KM, weather
    )
    assert a_001 == pytest.approx(9.97258313109183, rel=0.0, abs=1e-12)

    for percent, expected in ((0.1, 3.33645872929147), (1.0, 0.7866711673489801)):
        scaled = rain_attenuation_db(
            UPLINK_GHZ,
            ROME_ELEVATION_DEG,
            ROME_LATITUDE_DEG,
            ROME_HEIGHT_KM,
            weather,
            percent,
        )
        assert scaled == pytest.approx(expected, rel=0.0, abs=1e-12)


def test_gas_cloud_scintillation_and_refractivity_match_the_source() -> None:
    weather = _rome_weather()
    assert gaseous_attenuation_db(
        UPLINK_GHZ, ROME_ELEVATION_DEG, weather
    ) == pytest.approx(0.1119592549818175, rel=0.0, abs=1e-14)
    assert cloud_attenuation_db(
        UPLINK_GHZ, ROME_ELEVATION_DEG, weather
    ) == pytest.approx(0.1623494990172778, rel=0.0, abs=1e-14)
    assert scintillation_fade_db(
        UPLINK_GHZ, ROME_ELEVATION_DEG, 1.2, 0.6, weather, 0.01
    ) == pytest.approx(0.43025080950584943, rel=0.0, abs=1e-14)
    assert wet_term_refractivity(15.0, 60.0) == pytest.approx(
        45.969594310766404, rel=0.0, abs=1e-12
    )


def test_full_breakdown_matches_the_source_total() -> None:
    model = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        antenna_diameter_m=1.2,
        antenna_efficiency=0.6,
    )
    geometry = _slant_geometry(37_658_789.92289017)
    breakdown = model.evaluate(geometry, UPLINK_GHZ * 1.0e9)

    assert breakdown.rain_attenuation_db == pytest.approx(9.97258313109183, abs=1e-12)
    assert breakdown.gaseous_absorption_db == pytest.approx(0.1119592549818175, abs=1e-14)
    assert breakdown.cloud_attenuation_db == pytest.approx(0.1623494990172778, abs=1e-14)
    assert breakdown.scintillation_db == pytest.approx(0.43025080950584943, abs=1e-14)
    assert breakdown.total_carrier_loss_db == pytest.approx(10.256020334053193, abs=1e-12)


def test_legacy_latitude_fallback_reproduces_the_source_rain_heights() -> None:
    fallback = LegacyLatitudeFallback()
    assert fallback.rain_height_km(40.0) == pytest.approx(4.085, abs=1e-12)
    assert fallback.rain_height_km(10.0) == pytest.approx(5.36, abs=1e-12)
    # Far south the piecewise form floors the isotherm at sea level, leaving
    # only the 0.36 km offset. That is the source's behaviour, kept as-is.
    assert fallback.rain_height_km(-75.0) == pytest.approx(0.36, abs=1e-12)


# ---------------------------------------------------------------------------
# Layer B -- the physics, checked by algebra rather than by stored numbers
# ---------------------------------------------------------------------------


def test_gaseous_and_cloud_attenuation_follow_the_cosecant_law() -> None:
    weather = _rome_weather()
    zenith_gas = gaseous_attenuation_db(UPLINK_GHZ, 90.0, weather)
    zenith_cloud = cloud_attenuation_db(UPLINK_GHZ, 90.0, weather)
    for elevation in (10.0, 30.0, 55.0):
        cosecant = 1.0 / math.sin(math.radians(elevation))
        assert gaseous_attenuation_db(
            UPLINK_GHZ, elevation, weather
        ) == pytest.approx(zenith_gas * cosecant, rel=1e-13, abs=0.0)
        assert cloud_attenuation_db(
            UPLINK_GHZ, elevation, weather
        ) == pytest.approx(zenith_cloud * cosecant, rel=1e-13, abs=0.0)


def test_low_elevation_is_clamped_rather_than_diverging() -> None:
    weather = _rome_weather()
    at_floor = gaseous_attenuation_db(UPLINK_GHZ, 5.0, weather)
    # The cosecant projection has no meaning below the 5 degree floor, so the
    # model clamps instead of returning an unbounded number.
    for elevation in (0.5, 2.0, 4.9):
        assert gaseous_attenuation_db(UPLINK_GHZ, elevation, weather) == pytest.approx(
            at_floor, rel=0.0, abs=1e-15
        )


def test_mechanisms_combine_by_the_p618_section_2_5_rule() -> None:
    weather = _rome_weather()
    model = EarthItuPropagation(
        weather=weather,
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        antenna_diameter_m=1.2,
        antenna_efficiency=0.6,
    )
    geometry = _slant_geometry(3.7e7)
    b = model.evaluate(geometry, UPLINK_GHZ * 1.0e9)

    expected = b.gaseous_absorption_db + math.sqrt(
        (b.rain_attenuation_db + b.cloud_attenuation_db) ** 2 + b.scintillation_db**2
    )
    assert b.total_carrier_loss_db == pytest.approx(expected, rel=0.0, abs=1e-15)
    # Rain and cloud are correlated and add; scintillation enters in an RSS
    # sense, so the total must sit strictly below a plain sum of all four.
    plain_sum = (
        b.gaseous_absorption_db
        + b.rain_attenuation_db
        + b.cloud_attenuation_db
        + b.scintillation_db
    )
    assert b.total_carrier_loss_db < plain_sum


def test_absorptive_part_excludes_scintillation_exactly() -> None:
    model = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        antenna_diameter_m=1.2,
        antenna_efficiency=0.6,
    )
    geometry = _slant_geometry(3.7e7)
    b = model.evaluate(geometry, UPLINK_GHZ * 1.0e9)

    assert b.scintillation_db > 0.0
    assert b.absorptive_loss_db == pytest.approx(
        b.rain_attenuation_db + b.cloud_attenuation_db + b.gaseous_absorption_db,
        rel=0.0,
        abs=1e-15,
    )
    # The refractive fade is real loss on the carrier but contributes no
    # emission, so it shows up in the total and nowhere in the absorptive part.
    assert b.total_carrier_loss_db > b.absorptive_loss_db


def test_rain_attenuation_falls_as_the_exceedance_percentage_rises() -> None:
    weather = _rome_weather()
    values = [
        rain_attenuation_db(
            UPLINK_GHZ,
            ROME_ELEVATION_DEG,
            ROME_LATITUDE_DEG,
            ROME_HEIGHT_KM,
            weather,
            percent,
        )
        for percent in (0.001, 0.01, 0.1, 1.0, 5.0)
    ]
    assert values == sorted(values, reverse=True)
    # A fade exceeded 5% of the year must be far smaller than one exceeded
    # 0.001% of it; an order of magnitude is the weakest claim worth making.
    assert values[0] > 10.0 * values[-1]


def test_rain_attenuation_rises_with_rain_rate_and_frequency() -> None:
    def attenuation(frequency_ghz: float, rate: float) -> float:
        return rain_attenuation_001_db(
            frequency_ghz,
            ROME_ELEVATION_DEG,
            ROME_LATITUDE_DEG,
            ROME_HEIGHT_KM,
            _rome_weather(rain_rate_001_mm_per_h=rate),
        )

    rates = [attenuation(UPLINK_GHZ, rate) for rate in (5.0, 20.0, 42.0, 100.0)]
    assert rates == sorted(rates)
    bands = [attenuation(f, 42.0) for f in (2.2, 8.4, 14.0, 20.2, 32.0)]
    assert bands == sorted(bands)


def test_emission_temperature_follows_radiative_transfer() -> None:
    noise = SimplifiedAtmosphericEmissionNoise(medium_temperature_k=275.0)
    assert noise.emission_temperature_k(0.0) == pytest.approx(0.0, abs=1e-15)
    # 3 dB of absorption transmits half the power, so the layer radiates half
    # its physical temperature.
    assert noise.emission_temperature_k(10.0 * math.log10(2.0)) == pytest.approx(
        137.5, rel=1e-12
    )
    # A very opaque layer saturates at its own temperature and never exceeds it.
    assert noise.emission_temperature_k(60.0) == pytest.approx(275.0, rel=1e-5)
    assert noise.emission_temperature_k(1e3) <= 275.0


def test_clear_sky_noise_grows_towards_the_horizon_and_is_capped() -> None:
    noise = SimplifiedAtmosphericEmissionNoise()
    values = [noise.clear_sky_temperature_k(el) for el in (90.0, 60.0, 30.0, 10.0, 5.0)]
    assert values == sorted(values)
    assert values[-1] <= noise.clear_sky_cap_k
    # Below the floor the model stops varying rather than pretending to know
    # what happens at the horizon.
    assert noise.clear_sky_temperature_k(0.5) == pytest.approx(values[-1], abs=1e-15)


def test_scintillation_effective_earth_radius_is_expressed_in_metres() -> None:
    """The km-to-metre conversion is explicit, and is what the physics needs.

    The source wrote the effective Earth radius as ``EFFECTIVE_EARTH_RADIUS_KM *
    SCINTILLATION_TURBULENT_LAYER_HEIGHT_M``, which is numerically right only
    because the layer height happens to be exactly 1000 m. This pins both the
    intended value and the coincidence, so a future change to the layer height
    cannot silently rescale the Earth.
    """
    assert EFFECTIVE_EARTH_RADIUS_KM * 1000.0 == 8.5e6
    assert SCINTILLATION_TURBULENT_LAYER_HEIGHT_M == 1000.0


# ---------------------------------------------------------------------------
# Layer C -- the structural properties the migration exists for
# ---------------------------------------------------------------------------


def test_site_rain_rate_has_no_default() -> None:
    """A site's climate must be stated, never inherited from another site."""
    with pytest.raises(TypeError):
        EarthSiteWeather()  # type: ignore[call-arg]

    field = {f.name: f for f in dataclasses.fields(EarthSiteWeather)}[
        "rain_rate_001_mm_per_h"
    ]
    assert field.default is dataclasses.MISSING
    assert field.default_factory is dataclasses.MISSING


def test_legacy_weather_preset_names_the_site_it_describes() -> None:
    weather = legacy_rome_ankara_weather()
    assert weather.rain_rate_001_mm_per_h == 42.0
    assert "legacy" in weather.source.lower()
    assert "rome" in weather.source.lower() or "ankara" in weather.source.lower()


def test_the_rain_height_fallback_does_not_claim_to_be_the_p839_map() -> None:
    name = LegacyLatitudeFallback().name
    assert "fallback" in name.lower()
    assert "not the p.839 map" in name.lower()


def test_explicit_rain_height_adds_the_standard_offset_and_ignores_latitude() -> None:
    provider = ExplicitRainHeight(isotherm_height_km=3.2)
    assert provider.rain_height_km(41.9) == pytest.approx(3.56, abs=1e-12)
    assert provider.rain_height_km(-60.0) == pytest.approx(3.56, abs=1e-12)
    with pytest.raises(RfError, match="finite and non-negative"):
        ExplicitRainHeight(isotherm_height_km=-1.0)


def test_a_station_above_the_rain_layer_sees_no_rain() -> None:
    weather = _rome_weather(rain_height=ExplicitRainHeight(isotherm_height_km=1.0))
    # The provider puts the rain top at 1.36 km; a station at 4 km is above it.
    assert (
        rain_attenuation_001_db(UPLINK_GHZ, 30.0, ROME_LATITUDE_DEG, 4.0, weather) == 0.0
    )


def test_a_dry_site_gets_no_rain_and_a_clear_sky_gets_no_cloud() -> None:
    dry = _rome_weather(rain_rate_001_mm_per_h=0.0, columnar_liquid_water_kg_m2=0.0)
    assert rain_attenuation_001_db(
        UPLINK_GHZ, 30.0, ROME_LATITUDE_DEG, ROME_HEIGHT_KM, dry
    ) == 0.0
    assert cloud_attenuation_db(UPLINK_GHZ, 30.0, dry) == 0.0


def test_out_of_range_statistics_are_refused_not_extrapolated() -> None:
    weather = _rome_weather()
    for percent in (0.0005, 7.5):
        with pytest.raises(RfError, match="0.001"):
            rain_attenuation_db(
                UPLINK_GHZ,
                ROME_ELEVATION_DEG,
                ROME_LATITUDE_DEG,
                ROME_HEIGHT_KM,
                weather,
                percent,
            )
    with pytest.raises(RfError, match="0.01"):
        scintillation_fade_db(UPLINK_GHZ, 30.0, 1.2, 0.6, weather, 80.0)
    with pytest.raises(RfError, match="1-1000 GHz"):
        rain_coefficients_p838(0.4, 30.0)


def test_the_oxygen_approximation_refuses_frequencies_it_cannot_model() -> None:
    with pytest.raises(RfError, match="54 GHz"):
        gaseous_attenuation_db(60.0, 30.0, _rome_weather())


def test_scintillation_without_an_aperture_is_refused_not_silently_dropped() -> None:
    """The source skipped scintillation when no diameter was given. This does not.

    Aperture averaging is what sets the fade depth, so a missing diameter is a
    missing input rather than a reason to return a smaller number.
    """
    with pytest.raises(RfError, match="antenna_diameter_m"):
        EarthItuPropagation(
            weather=_rome_weather(),
            latitude_deg=ROME_LATITUDE_DEG,
            station_height_km=ROME_HEIGHT_KM,
            exceedance_percent=0.01,
        )
    # Saying so explicitly is allowed.
    model = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        include_scintillation=False,
    )
    assert model.include_scintillation is False


def test_a_slant_path_model_refuses_a_space_to_space_geometry() -> None:
    model = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        include_scintillation=False,
    )
    space_to_space = geometry_from_states(
        0.0,
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0e7, 0.0, 0.0, 0.0, 0.0, 0.0],
    )
    assert space_to_space.elevation_rad is None
    with pytest.raises(RfError, match="elevation"):
        model.evaluate(space_to_space, UPLINK_GHZ * 1.0e9)
    with pytest.raises(RfError, match="elevation"):
        SimplifiedAtmosphericEmissionNoise().system_temperature_k(
            space_to_space, PropagationLossBreakdown()
        )


def _terminal(name: str, *, transmit: bool) -> CommunicationTerminal:
    antenna = FixedGainAntenna(gain_dbi_boresight=45.0)
    if transmit:
        return CommunicationTerminal(
            name=name, transmitter=Transmitter(antenna=antenna, rf_power_w=100.0)
        )
    return CommunicationTerminal(
        name=name,
        receiver=Receiver(antenna=antenna, system_noise_temperature_k=150.0),
    )


def _link(**overrides: object) -> CommunicationLink:
    fields: dict[str, object] = {
        "name": "uplink",
        "transmitter": _terminal("station", transmit=True),
        "receiver": _terminal("spacecraft", transmit=False),
        "frequency_hz": UPLINK_GHZ * 1.0e9,
        "bandwidth_hz": 36.0e6,
    }
    fields.update(overrides)
    return CommunicationLink(**fields)  # type: ignore[arg-type]


def test_the_sky_noise_model_sees_the_attenuation_that_was_applied() -> None:
    """The coupling runs in the right order, and only on the absorptive part."""
    geometry = _slant_geometry(3.7e7)
    noise = SimplifiedAtmosphericEmissionNoise()
    rainy = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        antenna_diameter_m=1.2,
        antenna_efficiency=0.6,
    )
    clear = EarthItuPropagation(
        weather=_rome_weather(rain_rate_001_mm_per_h=0.0, columnar_liquid_water_kg_m2=0.0),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        antenna_diameter_m=1.2,
        antenna_efficiency=0.6,
    )

    rainy_result = evaluate_link(
        _link(propagation_models=(rainy,), sky_noise=noise), geometry
    )
    clear_result = evaluate_link(
        _link(propagation_models=(clear,), sky_noise=noise), geometry
    )

    assert rainy_result.system_noise_temperature_k is not None
    assert clear_result.system_noise_temperature_k is not None
    # Rain both attenuates and emits, so the receive temperature rises with it.
    assert rainy_result.system_noise_temperature_k > clear_result.system_noise_temperature_k

    # And the temperature is exactly what the model computes from the combined
    # breakdown, which is what "sees the attenuation that was applied" means.
    assert rainy_result.system_noise_temperature_k == pytest.approx(
        noise.system_temperature_k(geometry, rainy_result.propagation), rel=0.0, abs=1e-15
    )


def test_a_purely_refractive_fade_does_not_raise_the_noise_temperature() -> None:
    geometry = _slant_geometry(3.7e7)
    noise = SimplifiedAtmosphericEmissionNoise()
    scintillation_only = PropagationLossBreakdown(
        scintillation_db=3.0, total_carrier_loss_db=3.0, absorptive_loss_db=0.0
    )
    nothing = PropagationLossBreakdown()
    assert noise.system_temperature_k(geometry, scintillation_only) == pytest.approx(
        noise.system_temperature_k(geometry, nothing), rel=0.0, abs=1e-15
    )


def test_an_explicit_temperature_still_overrides_the_sky_noise_model() -> None:
    geometry = _slant_geometry(3.7e7)
    link = _link(sky_noise=SimplifiedAtmosphericEmissionNoise())
    result = evaluate_link(link, geometry, system_noise_temperature_k=210.0)
    assert result.system_noise_temperature_k == pytest.approx(210.0)


def test_the_modelled_atmosphere_still_excludes_a_fixed_allowance() -> None:
    """The Phase 2 double-counting guard holds against the real ITU-R model."""
    modelled = EarthItuPropagation(
        weather=_rome_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        include_scintillation=False,
    )
    assert modelled.accounts_for_atmosphere is True
    with pytest.raises(RfError, match="count the atmosphere twice"):
        _link(propagation_models=(modelled, FixedAtmosphericAllowance(loss_db=1.5)))


def test_the_simplified_noise_model_declares_that_it_is_not_standards_grade() -> None:
    described = SimplifiedAtmosphericEmissionNoise().as_dict()
    assert described["standards_grade"] is False


def test_the_model_records_the_recommendations_it_implements() -> None:
    described = EarthItuPropagation(
        weather=legacy_rome_ankara_weather(),
        latitude_deg=ROME_LATITUDE_DEG,
        station_height_km=ROME_HEIGHT_KM,
        exceedance_percent=0.01,
        include_scintillation=False,
    ).as_dict()
    assert "ITU-R P.838-3" in described["recommendations"]
    assert "ITU-R P.618-13" in described["recommendations"]
    assert described["weather"]["rain_height_provider"] == LegacyLatitudeFallback().name
