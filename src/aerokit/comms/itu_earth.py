# Copied from Sidera (sidera.communications.channel.itu_earth, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Earth slant-path propagation: ITU-R rain, gas, cloud and scintillation.

Migrated from the source study's ``src/itu_propagation.py``. The equations are
the Recommendations' own; what changed is that the meteorology is now an
explicit, named input rather than a module default, and the rain-height fallback
is named for what it is.

What each part is
-----------------
========================  ==================================================
ITU-R P.838-3             rain specific attenuation coefficients k, alpha
ITU-R P.618-13 Sec 2.2.1  slant-path rain attenuation and its p-scaling
ITU-R P.839-4             rain height -- **fallback only**, see below
ITU-R P.676-12 Annex 2    oxygen and water-vapour attenuation
ITU-R P.840-8             cloud liquid-water attenuation
ITU-R P.618-13 Sec 2.4.1  tropospheric scintillation
ITU-R P.453-14            wet-term refractivity, input to scintillation
ITU-R P.618-13 Sec 2.5    mechanism combination
========================  ==================================================

The rain height is a fallback, not a map
----------------------------------------
P.839 distributes the 0 degree isotherm height on a global digital map. This
module does **not** contain that map. `LegacyLatitudeFallback` is a piecewise
latitude approximation carried over from the source, which said plainly that it
"must not be described as a direct P.839 map extraction". That honesty is
preserved: the class is named for what it does, and `ExplicitRainHeight` is
there for a caller who has the mapped or measured value.

Nothing here downloads anything. A deterministic archived run stays
deterministic.

Site meteorology is required, not defaulted
-------------------------------------------
The source used ``R0.01 = 42 mm/h``, representative for its Rome/Ankara
scenario. Reusing that for an arbitrary station would silently import one site's
climate into another's analysis, so `EarthSiteWeather` has no default rain rate.
The legacy figures are available as a *named* preset whose name says whose they
are.

Absorptive and refractive
-------------------------
Rain, cloud and gas attenuate and emit; scintillation fades without emitting.
The breakdown keeps them apart so a sky-noise model is never handed a refractive
fade. That separation was already right in the source and is preserved exactly.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from aerokit.comms.channel import PropagationLossBreakdown
from aerokit.comms.geometry import LinkGeometry
from aerokit.comms.rf import RfError

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "COSMIC_BACKGROUND_TEMPERATURE_K",
    "EFFECTIVE_EARTH_RADIUS_KM",
    "EarthItuPropagation",
    "EarthSiteWeather",
    "ExplicitRainHeight",
    "LegacyLatitudeFallback",
    "MINIMUM_VALID_ELEVATION_DEG",
    "RainHeightProvider",
    "SCINTILLATION_TURBULENT_LAYER_HEIGHT_M",
    "SimplifiedAtmosphericEmissionNoise",
    "cloud_attenuation_db",
    "gaseous_attenuation_db",
    "legacy_rome_ankara_weather",
    "rain_attenuation_001_db",
    "rain_attenuation_db",
    "rain_coefficients_p838",
    "scintillation_fade_db",
    "wet_term_refractivity",
]

# =============================================================================
# 2.                         ITU-R CONSTANTS AND TABLES
# =============================================================================

# Effective Earth radius for the low-elevation slant-path geometry, km. The
# conventional 4/3-Earth value used by P.618.
EFFECTIVE_EARTH_RADIUS_KM: float = 8_500.0

# Below this the cosecant projection of a zenith attenuation stops being a
# usable approximation, so elevations are clamped up to it. P.618's low-angle
# forms take over below about 5 degrees for rain specifically.
MINIMUM_VALID_ELEVATION_DEG: float = 5.0

# Highest frequency of the P.618-13 Sec 2.2.1.1 rain procedure, GHz: it gives
# "estimates of the long-term statistics of the slant-path rain attenuation ...
# for frequencies up to 55 GHz".
_RAIN_MAXIMUM_FREQUENCY_GHZ: float = 55.0

# Frequency range of the P.618-13 Sec 2.4.1 scintillation method, GHz: "for
# frequencies between 4 GHz and 20 GHz".
_SCINTILLATION_FREQUENCY_RANGE_GHZ: tuple[float, float] = (4.0, 20.0)

# Height of the turbulent layer for scintillation, metres (P.618-13 Sec 2.4.1).
SCINTILLATION_TURBULENT_LAYER_HEIGHT_M: float = 1_000.0

COSMIC_BACKGROUND_TEMPERATURE_K: float = 2.725

# --- ITU-R P.838-3 coefficient tables, quoted from the Recommendation -------
# log10(k) or alpha = sum_j a_j exp(-((log10 f - b_j)/c_j)^2) + m log10 f + c
_P838_KH = {
    "a": (-5.33980, -0.35351, -0.23789, -0.94158),
    "b": (-0.10008, 1.26970, 0.86036, 0.64552),
    "c": (1.13098, 0.45400, 0.15354, 0.16817),
    "m": -0.18961,
    "k": 0.71147,
}
_P838_KV = {
    "a": (-3.80595, -3.44965, -0.39902, 0.50167),
    "b": (0.56934, -0.22911, 0.73042, 1.07319),
    "c": (0.81061, 0.51059, 0.11899, 0.27195),
    "m": -0.16398,
    "k": 0.63297,
}
_P838_AH = {
    "a": (-0.14318, 0.29591, 0.32177, -5.37610, 16.1721),
    "b": (1.82442, 0.77564, 0.63773, -0.96230, -3.29980),
    "c": (-0.55187, 0.19822, 0.13164, 1.47828, 3.43990),
    "m": 0.67849,
    "k": -1.95537,
}
_P838_AV = {
    "a": (-0.07771, 0.56727, -0.20238, -48.2991, 48.5833),
    "b": (2.33840, 0.95545, 1.14520, 0.791669, 0.791459),
    "c": (-0.76284, 0.54039, 0.26809, 0.116226, 0.116479),
    "m": -0.053739,
    "k": 0.83433,
}


# =============================================================================
# 3.                              PRIVATE HELPERS
# =============================================================================

def _p838_sum(table: dict[str, Any], log_f: float) -> float:
    total = 0.0
    for a_j, b_j, c_j in zip(table["a"], table["b"], table["c"], strict=True):
        total += a_j * math.exp(-(((log_f - b_j) / c_j) ** 2))
    return total + float(table["m"]) * log_f + float(table["k"])


# =============================================================================
# 4.                         RAIN COEFFICIENTS (P.838)
# =============================================================================

def rain_coefficients_p838(
    frequency_ghz: float,
    elevation_deg: float,
    polarization_tilt_deg: float = 90.0,
) -> tuple[float, float]:
    """``(k, alpha)`` for ``gamma_R = k R^alpha``, per ITU-R P.838-3.

    The horizontal and vertical base coefficients are rotated to the path
    geometry by the elevation ``theta`` and the polarization tilt ``tau``:

        k     = [kH + kV + (kH - kV) cos^2(theta) cos(2 tau)] / 2
        alpha = [kH aH + kV aV + (kH aH - kV aV) cos^2(theta) cos(2 tau)] / (2k)

    ``tau`` is 0 degrees for horizontal linear, 90 for vertical linear, and 45
    for circular polarization.

    Reference: Recommendation ITU-R P.838-3 (2005): Specific attenuation coefficients and
    polarization rotation (checked against a secondary source) [SIDERA-ALG-COM-002].
    """
    frequency = float(frequency_ghz)
    if not 1.0 <= frequency <= 1000.0:
        raise RfError(
            f"ITU-R P.838-3 is defined for 1-1000 GHz, got {frequency_ghz!r} GHz"
        )
    log_f = math.log10(frequency)
    k_h = 10.0 ** _p838_sum(_P838_KH, log_f)
    k_v = 10.0 ** _p838_sum(_P838_KV, log_f)
    a_h = _p838_sum(_P838_AH, log_f)
    a_v = _p838_sum(_P838_AV, log_f)

    cos2_theta = math.cos(math.radians(elevation_deg)) ** 2
    cos_2tau = math.cos(2.0 * math.radians(polarization_tilt_deg))

    k = (k_h + k_v + (k_h - k_v) * cos2_theta * cos_2tau) / 2.0
    alpha = (
        k_h * a_h + k_v * a_v + (k_h * a_h - k_v * a_v) * cos2_theta * cos_2tau
    ) / (2.0 * k)
    return k, alpha


# =============================================================================
# 5.                            RAIN HEIGHT PROTOCOL
# =============================================================================

@runtime_checkable
class RainHeightProvider(Protocol):
    """The rain height ``h_R`` at a site, in km."""

    @property
    def name(self) -> str:
        """A short label for the provider."""
        ...

    def rain_height_km(self, latitude_deg: float) -> float:
        """The rain height ``h_R``, km, at a site of this latitude."""
        ...


# =============================================================================
# 6.                        RAIN HEIGHT AND SITE WEATHER
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExplicitRainHeight:
    """A mapped or measured 0 degree isotherm height, ``h_R = h0 + 0.36`` km.

    The right provider when the P.839 digital map or a radiosonde figure is
    available. Nothing is inferred.
    """

    isotherm_height_km: float
    name: str = "explicit 0 deg C isotherm"

    def __post_init__(self) -> None:
        value = float(self.isotherm_height_km)
        if not math.isfinite(value) or value < 0.0:
            raise RfError(
                f"the 0 deg C isotherm height must be finite and non-negative km, "
                f"got {self.isotherm_height_km!r}"
            )

    def rain_height_km(self, latitude_deg: float) -> float:
        """``h0 + 0.36`` km; latitude is not consulted, the isotherm already fixes it."""
        del latitude_deg
        return self.isotherm_height_km + 0.36


@dataclass(frozen=True, slots=True)
class LegacyLatitudeFallback:
    """A piecewise latitude approximation to the rain height. **Not** the P.839 map.

    Carried over from the migrated source, which stated that it "must not be
    described as a direct P.839 map extraction". It is kept under a name that
    says so. Use `ExplicitRainHeight` whenever a mapped or measured ``h0`` is
    available; a site-specific study needs one.
    """

    name: str = "legacy latitude fallback (not the P.839 map)"

    def rain_height_km(self, latitude_deg: float) -> float:
        """The piecewise-latitude ``h0`` estimate, plus 0.36 km, clamped non-negative."""
        phi = float(latitude_deg)
        if phi > 23.0:
            h0 = 5.0 - 0.075 * (phi - 23.0)
        elif -21.0 <= phi <= 23.0:
            # The tropical band, north and south of the equator alike, is flat
            # at 5 km in this approximation.
            h0 = 5.0
        elif -71.0 < phi < -21.0:
            h0 = 5.0 + 0.1 * (phi + 21.0)
        else:
            h0 = 0.0
        return max(h0, 0.0) + 0.36


@dataclass(frozen=True, slots=True)
class EarthSiteWeather:
    """The meteorology of one ground site.

    ``rain_rate_001_mm_per_h`` has **no default**. It is the point rainfall rate
    exceeded 0.01% of an average year at this site, from an ITU-R P.837 map or
    local measurement, and it varies from a few mm/h in a desert to over
    100 mm/h in the tropics. A default would silently import one site's climate
    into another's analysis.
    """

    rain_rate_001_mm_per_h: float
    rain_height: RainHeightProvider
    surface_pressure_hpa: float = 1013.25
    surface_temperature_c: float = 15.0
    water_vapour_density_g_m3: float = 7.5
    relative_humidity_percent: float = 60.0
    columnar_liquid_water_kg_m2: float = 0.0
    polarization_tilt_deg: float = 90.0
    source: str = "caller supplied"

    def __post_init__(self) -> None:
        rate = float(self.rain_rate_001_mm_per_h)
        if not math.isfinite(rate) or rate < 0.0:
            raise RfError(
                f"R0.01 must be a finite, non-negative rain rate in mm/h, got {rate!r}"
            )
        for name, low, high in (
            ("surface_pressure_hpa", 0.0, math.inf),
            ("water_vapour_density_g_m3", 0.0, math.inf),
            ("columnar_liquid_water_kg_m2", 0.0, math.inf),
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or not low <= value <= high:
                raise RfError(f"{name} must be finite and non-negative, got {value!r}")
        humidity = float(self.relative_humidity_percent)
        if not math.isfinite(humidity) or not 0.0 <= humidity <= 100.0:
            raise RfError(f"relative humidity must lie in [0, 100] %, got {humidity!r}")

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "rain_rate_001_mm_per_h": self.rain_rate_001_mm_per_h,
            "rain_height_provider": self.rain_height.name,
            "surface_pressure_hpa": self.surface_pressure_hpa,
            "surface_temperature_c": self.surface_temperature_c,
            "water_vapour_density_g_m3": self.water_vapour_density_g_m3,
            "relative_humidity_percent": self.relative_humidity_percent,
            "columnar_liquid_water_kg_m2": self.columnar_liquid_water_kg_m2,
            "polarization_tilt_deg": self.polarization_tilt_deg,
            "source": self.source,
        }


# =============================================================================
# 7.                          RAIN ATTENUATION (P.618)
# =============================================================================

def legacy_rome_ankara_weather() -> EarthSiteWeather:
    """The migrated study's representative inputs, named for what they are.

    These are the values from the source scenario: ``R0.01 = 42 mm/h`` shared
    between Rome and Ankara, a fixed 0.6 kg/m^2 cloud column, and the latitude
    rain-height fallback. They exist so the legacy result can be reproduced
    exactly, and the name says whose climate they describe. Do not use them for
    another site.
    """
    return EarthSiteWeather(
        rain_rate_001_mm_per_h=42.0,
        rain_height=LegacyLatitudeFallback(),
        surface_pressure_hpa=1013.25,
        surface_temperature_c=15.0,
        water_vapour_density_g_m3=7.5,
        relative_humidity_percent=60.0,
        columnar_liquid_water_kg_m2=0.6,
        polarization_tilt_deg=90.0,
        source="legacy GEO study representative values (Rome/Ankara scenario)",
    )


# ---------------------------------------------------------------------------
# Rain, ITU-R P.618-13 Section 2.2.1.1
# ---------------------------------------------------------------------------

def rain_attenuation_001_db(
    frequency_ghz: float,
    elevation_deg: float,
    latitude_deg: float,
    station_height_km: float,
    weather: EarthSiteWeather,
) -> float:
    """Rain attenuation exceeded 0.01% of an average year, ``A_0.01`` in dB.

    Reference: Recommendation ITU-R P.618-13 (2017), section 2.2.1.1 (attenuation due to rain) and
    2.5 (combination of mechanisms) (checked against a secondary source) [SIDERA-ALG-COM-003].
    """
    if not float(frequency_ghz) <= _RAIN_MAXIMUM_FREQUENCY_GHZ:
        raise RfError(
            "the P.618-13 Sec 2.2.1.1 rain procedure is defined for frequencies up to "
            f"{_RAIN_MAXIMUM_FREQUENCY_GHZ:g} GHz, got {frequency_ghz!r} GHz"
        )
    if weather.rain_rate_001_mm_per_h <= 0.0:
        return 0.0

    theta = float(elevation_deg)
    theta_rad = math.radians(theta)
    sin_theta = math.sin(theta_rad)
    cos_theta = math.cos(theta_rad)
    if sin_theta <= 0.0:
        raise RfError(
            f"rain attenuation needs a positive elevation, got {elevation_deg!r} deg"
        )

    h_r = weather.rain_height.rain_height_km(latitude_deg)
    delta_h = h_r - float(station_height_km)
    if delta_h <= 0.0:
        return 0.0  # The station is at or above the rain layer.

    if theta >= MINIMUM_VALID_ELEVATION_DEG:
        slant_length = delta_h / sin_theta
    else:
        slant_length = (
            2.0
            * delta_h
            / (
                math.sqrt(sin_theta**2 + 2.0 * delta_h / EFFECTIVE_EARTH_RADIUS_KM)
                + sin_theta
            )
        )

    horizontal = slant_length * cos_theta
    k, alpha = rain_coefficients_p838(
        frequency_ghz, theta, weather.polarization_tilt_deg
    )
    gamma_r = k * weather.rain_rate_001_mm_per_h**alpha

    r_001 = 1.0 / (
        1.0
        + 0.78 * math.sqrt(horizontal * gamma_r / frequency_ghz)
        - 0.38 * (1.0 - math.exp(-2.0 * horizontal))
    )

    zeta_deg = math.degrees(math.atan2(delta_h, horizontal * r_001))
    rain_path = (
        horizontal * r_001 / cos_theta if zeta_deg > theta else delta_h / sin_theta
    )

    abs_lat = abs(float(latitude_deg))
    chi = 36.0 - abs_lat if abs_lat < 36.0 else 0.0
    v_001 = 1.0 / (
        1.0
        + math.sqrt(sin_theta)
        * (
            31.0
            * (1.0 - math.exp(-(theta / (1.0 + chi))))
            * math.sqrt(rain_path * gamma_r)
            / frequency_ghz**2
            - 0.45
        )
    )
    return gamma_r * rain_path * v_001


def rain_attenuation_db(
    frequency_ghz: float,
    elevation_deg: float,
    latitude_deg: float,
    station_height_km: float,
    weather: EarthSiteWeather,
    exceedance_percent: float,
) -> float:
    """``A_p``: rain attenuation exceeded ``p`` percent of an average year.

    ``A_0.01`` scaled by the published power law, valid for
    ``0.001 <= p <= 5``. Outside that range the Recommendation gives no scaling,
    so this raises rather than extrapolating a statistic.

    Reference: Recommendation ITU-R P.618-13 (2017), section 2.2.1.1 (attenuation due to rain) and
    2.5 (combination of mechanisms) (checked against a secondary source) [SIDERA-ALG-COM-003].
    """
    p = float(exceedance_percent)
    if not 0.001 <= p <= 5.0:
        raise RfError(
            f"ITU-R P.618-13 rain scaling is defined for 0.001% <= p <= 5%, got {p!r}%"
        )
    a_001 = rain_attenuation_001_db(
        frequency_ghz, elevation_deg, latitude_deg, station_height_km, weather
    )
    if a_001 <= 0.0:
        return 0.0
    if p == 0.01:
        return a_001

    abs_lat = abs(float(latitude_deg))
    theta = float(elevation_deg)
    if p >= 1.0 or abs_lat >= 36.0:
        beta = 0.0
    elif theta >= 25.0:
        beta = -0.005 * (abs_lat - 36.0)
    else:
        beta = -0.005 * (abs_lat - 36.0) + 1.8 - 4.25 * math.sin(math.radians(theta))

    exponent = (
        0.655
        + 0.033 * math.log(p)
        - 0.045 * math.log(a_001)
        - beta * (1.0 - p) * math.sin(math.radians(theta))
    )
    return a_001 * (p / 0.01) ** (-exponent)


# ---------------------------------------------------------------------------
# Gases, ITU-R P.676-12 Annex 2
# ---------------------------------------------------------------------------

# =============================================================================
# 8.                              PRIVATE HELPERS
# =============================================================================

def _gaseous_specific_attenuation_db_per_km(
    frequency_ghz: float,
    pressure_hpa: float,
    temperature_c: float,
    water_vapour_density_g_m3: float,
) -> tuple[float, float]:
    """``(gamma_oxygen, gamma_water)`` in dB/km.

    The oxygen branch is the ``f <= 54 GHz`` approximation, which covers L
    through lower Ka. Above that the resonance complex needs the full
    line-by-line model, so it raises rather than extrapolating.
    """
    f = float(frequency_ghz)
    if f > 54.0:
        raise RfError(
            f"the ITU-R P.676-12 Annex 2 oxygen approximation implemented here is "
            f"valid to 54 GHz, which covers L through lower Ka band; got {f} GHz. "
            "Higher frequencies need the line-by-line model of Annex 1."
        )
    if f <= 0.0:
        raise RfError(f"frequency must be positive, got {frequency_ghz!r} GHz")

    rho = float(water_vapour_density_g_m3)
    r_p = float(pressure_hpa) / 1013.0
    r_t = 288.0 / (273.0 + float(temperature_c))

    def phi(a: float, b: float, c: float, d: float) -> float:
        return r_p**a * r_t**b * math.exp(c * (1.0 - r_p) + d * (1.0 - r_t))

    xi1 = phi(0.0717, -1.8132, 0.0156, -1.6515)
    xi2 = phi(0.5146, -4.6368, -0.1921, -5.7416)
    xi3 = phi(0.3414, -6.5851, 0.2130, -8.5854)

    gamma_o = (
        7.2 * r_t**2.8 / (f**2 + 0.34 * r_p**2 * r_t**1.6)
        + 0.62 * xi3 / ((54.0 - f) ** (1.16 * xi1) + 0.83 * xi2)
    ) * f**2 * r_p**2 * 1.0e-3

    eta1 = 0.955 * r_p * r_t**0.68 + 0.006 * rho
    eta2 = 0.735 * r_p * r_t**0.5 + 0.0353 * r_t**4 * rho

    def g(fi: float) -> float:
        return 1.0 + ((f - fi) / (f + fi)) ** 2

    gamma_w = (
        3.98 * eta1 * math.exp(2.23 * (1.0 - r_t)) / ((f - 22.235) ** 2 + 9.42 * eta1**2) * g(22.0)
        + 11.96 * eta1 * math.exp(0.70 * (1.0 - r_t)) / ((f - 183.31) ** 2 + 11.14 * eta1**2)
        + 0.081 * eta1 * math.exp(6.44 * (1.0 - r_t)) / ((f - 321.226) ** 2 + 6.29 * eta1**2)
        + 3.660 * eta1 * math.exp(1.60 * (1.0 - r_t)) / ((f - 325.153) ** 2 + 9.22 * eta1**2)
        + 25.37 * eta1 * math.exp(1.09 * (1.0 - r_t)) / ((f - 380.0) ** 2)
        + 17.40 * eta1 * math.exp(1.46 * (1.0 - r_t)) / ((f - 448.0) ** 2)
        + 844.6 * eta1 * math.exp(0.17 * (1.0 - r_t)) / ((f - 557.0) ** 2) * g(557.0)
        + 290.0 * eta1 * math.exp(0.41 * (1.0 - r_t)) / ((f - 752.0) ** 2) * g(752.0)
        + 8.3328e4 * eta2 * math.exp(0.99 * (1.0 - r_t)) / ((f - 1780.0) ** 2) * g(1780.0)
    ) * f**2 * r_t**2.5 * rho * 1.0e-4

    return gamma_o, gamma_w


def _gas_equivalent_heights_km(frequency_ghz: float, pressure_hpa: float) -> tuple[float, float]:
    f = float(frequency_ghz)
    r_p = float(pressure_hpa) / 1013.0

    t1 = (
        4.64
        / (1.0 + 0.066 * r_p**-2.3)
        * math.exp(-(((f - 59.7) / (2.87 + 12.4 * math.exp(-7.9 * r_p))) ** 2))
    )
    t2 = 0.14 * math.exp(2.12 * r_p) / ((f - 118.75) ** 2 + 0.031 * math.exp(2.2 * r_p))
    t3 = (
        0.0114
        / (1.0 + 0.14 * r_p**-2.6)
        * f
        * (-0.0247 + 0.0001 * f + 1.61e-6 * f**2)
        / (1.0 - 0.0169 * f + 4.1e-5 * f**2 + 3.2e-7 * f**3)
    )
    h_o = 6.1 / (1.0 + 0.17 * r_p**-1.1) * (1.0 + t1 + t2 + t3)
    if f < 70.0:
        h_o = min(h_o, 10.7 * r_p**0.3)

    sigma_w = 1.013 / (1.0 + math.exp(-8.6 * (r_p - 0.57)))
    h_w = 1.66 * (
        1.0
        + 1.39 * sigma_w / ((f - 22.235) ** 2 + 2.56 * sigma_w)
        + 3.37 * sigma_w / ((f - 183.31) ** 2 + 4.69 * sigma_w)
        + 1.58 * sigma_w / ((f - 325.1) ** 2 + 2.89 * sigma_w)
    )
    return h_o, h_w


# =============================================================================
# 9.                        GASEOUS ATTENUATION (P.676)
# =============================================================================

def gaseous_attenuation_db(
    frequency_ghz: float, elevation_deg: float, weather: EarthSiteWeather
) -> float:
    """Slant-path oxygen plus water-vapour attenuation, dB.

    Zenith attenuation from the specific attenuations and their equivalent
    heights, projected by the cosecant law. The elevation is clamped up to
    5 degrees because the cosecant projection diverges at the horizon.

    Reference: Recommendation ITU-R P.676-12 (2019), Annex 2 (approximate estimation of gaseous
    attenuation) (checked against a secondary source) [SIDERA-ALG-COM-004].
    """
    gamma_o, gamma_w = _gaseous_specific_attenuation_db_per_km(
        frequency_ghz,
        weather.surface_pressure_hpa,
        weather.surface_temperature_c,
        weather.water_vapour_density_g_m3,
    )
    h_o, h_w = _gas_equivalent_heights_km(frequency_ghz, weather.surface_pressure_hpa)
    zenith = gamma_o * h_o + gamma_w * h_w
    sin_theta = math.sin(
        math.radians(max(float(elevation_deg), MINIMUM_VALID_ELEVATION_DEG))
    )
    return zenith / sin_theta


# ---------------------------------------------------------------------------
# Cloud, ITU-R P.840-8
# ---------------------------------------------------------------------------

# =============================================================================
# 10.                             PRIVATE HELPERS
# =============================================================================

def _cloud_specific_attenuation_coefficient(
    frequency_ghz: float, temperature_c: float = 0.0
) -> float:
    """``K_l`` in (dB/km)/(g/m^3): Rayleigh scattering with a double-Debye water permittivity."""
    f = float(frequency_ghz)
    theta = 300.0 / (273.15 + float(temperature_c))

    eps0 = 77.66 + 103.3 * (theta - 1.0)
    eps1 = 0.0671 * eps0
    eps2 = 3.52
    fp = 20.20 - 146.0 * (theta - 1.0) + 316.0 * (theta - 1.0) ** 2
    fs = 39.8 * fp

    eps_imag = f * (eps0 - eps1) / (fp * (1.0 + (f / fp) ** 2)) + f * (eps1 - eps2) / (
        fs * (1.0 + (f / fs) ** 2)
    )
    eps_real = (
        (eps0 - eps1) / (1.0 + (f / fp) ** 2)
        + (eps1 - eps2) / (1.0 + (f / fs) ** 2)
        + eps2
    )
    eta = (2.0 + eps_real) / eps_imag
    return 0.819 * f / (eps_imag * (1.0 + eta**2))


# =============================================================================
# 11.                  CLOUD ATTENUATION AND WET REFRACTIVITY
# =============================================================================

def cloud_attenuation_db(
    frequency_ghz: float,
    elevation_deg: float,
    weather: EarthSiteWeather,
    cloud_temperature_c: float = 0.0,
) -> float:
    """Slant-path cloud liquid-water attenuation, dB.

    Reference: Recommendation ITU-R P.840-8 (2019): Attenuation due to clouds (specific attenuation
    coefficient K_l) (checked against a secondary source) [SIDERA-ALG-COM-005].
    """
    if weather.columnar_liquid_water_kg_m2 <= 0.0:
        return 0.0
    k_l = _cloud_specific_attenuation_coefficient(frequency_ghz, cloud_temperature_c)
    sin_theta = math.sin(
        math.radians(max(float(elevation_deg), MINIMUM_VALID_ELEVATION_DEG))
    )
    return weather.columnar_liquid_water_kg_m2 * k_l / sin_theta


# ---------------------------------------------------------------------------
# Scintillation, ITU-R P.618-13 Section 2.4.1
# ---------------------------------------------------------------------------

def wet_term_refractivity(temperature_c: float, relative_humidity_percent: float) -> float:
    """``N_wet`` via the Magnus saturation vapour pressure, 17.502 / 240.97.

    These are the Buck (1981) constants of the older ITU-R P.453 revisions, not
    the saturation-pressure form P.453-14 is understood to use (Buck 1996:
    a = 6.1121, b = 18.678, c = 257.14, d = 234.5; the Recommendation text was
    not re-read here). Evaluated side by side, the two differ by less than
    0.1 % in ``e_sat`` (and so in ``N_wet``) between -16 and 46 degC and by
    1.1 % at -40 degC.

    Reference: Recommendation ITU-R P.618-13 (2017), section 2.4.1 (calculation of monthly and
    long-term statistics of scintillation) (checked against a secondary source)
    [SIDERA-ALG-COM-006].
    """
    temperature_k = 273.15 + float(temperature_c)
    e_sat = 6.1121 * math.exp(
        17.502 * float(temperature_c) / (float(temperature_c) + 240.97)
    )
    e = (float(relative_humidity_percent) / 100.0) * e_sat
    return 3.732e5 * e / temperature_k**2


# =============================================================================
# 12.                             PRIVATE HELPERS
# =============================================================================

def _scintillation_aperture_factor(x: float) -> float:
    """Antenna aperture-averaging factor ``g(x)``."""
    if x >= 1.0e6:
        return 0.0
    value = 3.86 * (x**2 + 1.0) ** (11.0 / 12.0) * math.sin(
        11.0 / 6.0 * math.atan(1.0 / x)
    ) - 7.08 * x ** (5.0 / 6.0)
    return math.sqrt(value) if value > 0.0 else 0.0


# =============================================================================
# 13.                              SCINTILLATION
# =============================================================================

def scintillation_fade_db(
    frequency_ghz: float,
    elevation_deg: float,
    antenna_diameter_m: float,
    antenna_efficiency: float,
    weather: EarthSiteWeather,
    exceedance_percent: float,
) -> float:
    """Tropospheric scintillation fade depth, dB.

    A **refractive** effect: it fades the carrier by focusing and defocusing,
    and does not raise the antenna noise temperature. The breakdown keeps it out
    of the absorptive total for exactly that reason.

    The effective Earth radius here is converted from km to metres explicitly.
    The migrated source wrote it as ``EFFECTIVE_EARTH_RADIUS_KM *
    SCINTILLATION_TURBULENT_LAYER_HEIGHT_M``, which gives the right number only
    because the layer height happens to be exactly 1000 m; changing the layer
    height would have silently scaled the Earth. Numerically identical today,
    and no longer a trap.

    Outside the method's 4-20 GHz range a `RuntimeWarning` is issued and the
    value is computed anyway, as an extrapolation.

    Reference: Recommendation ITU-R P.618-13 (2017), section 2.4.1 (calculation of monthly and
    long-term statistics of scintillation) (checked against a secondary source)
    [SIDERA-ALG-COM-006].
    """
    p = float(exceedance_percent)
    if not 0.01 <= p <= 50.0:
        raise RfError(
            f"the P.618-13 scintillation model is defined for 0.01% <= p <= 50%, got {p!r}%"
        )
    frequency = float(frequency_ghz)
    if not math.isfinite(frequency) or frequency <= 0.0:
        raise RfError(f"frequency must be finite and positive, got {frequency_ghz!r} GHz")
    low_ghz, high_ghz = _SCINTILLATION_FREQUENCY_RANGE_GHZ
    if not low_ghz <= frequency <= high_ghz:
        warnings.warn(
            f"ITU-R P.618 scintillation is specified for {low_ghz:g}-{high_ghz:g} GHz; "
            f"got {frequency:g} GHz - the value is an extrapolation",
            RuntimeWarning,
            stacklevel=2,
        )
    # Sec 2.4.1 is the method for free-space elevations of 5 degrees and above
    # (its low-angle companions, Sec 2.4.2-2.4.3, are not implemented), so a
    # lower elevation is clamped to 5 degrees like the gas and cloud paths.
    theta = max(float(elevation_deg), MINIMUM_VALID_ELEVATION_DEG)
    sin_theta = math.sin(math.radians(theta))

    n_wet = wet_term_refractivity(
        weather.surface_temperature_c, weather.relative_humidity_percent
    )
    sigma_ref = 3.6e-3 + 1.0e-4 * n_wet

    h_l = SCINTILLATION_TURBULENT_LAYER_HEIGHT_M
    effective_radius_m = EFFECTIVE_EARTH_RADIUS_KM * 1000.0
    path_length_m = (
        2.0 * h_l / (math.sqrt(sin_theta**2 + 2.0 * h_l / effective_radius_m) + sin_theta)
    )

    d_eff = math.sqrt(max(float(antenna_efficiency), 0.0)) * float(antenna_diameter_m)
    x = 1.22 * d_eff**2 * (float(frequency_ghz) / path_length_m)
    g_x = _scintillation_aperture_factor(x)

    sigma = sigma_ref * float(frequency_ghz) ** (7.0 / 12.0) * g_x / sin_theta**1.2
    log_p = math.log10(p)
    a_p = -0.061 * log_p**3 + 0.072 * log_p**2 - 1.71 * log_p + 3.0
    return a_p * sigma


# ---------------------------------------------------------------------------
# The composed model
# ---------------------------------------------------------------------------

# =============================================================================
# 14.                     PROPAGATION AND SKY-NOISE MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class EarthItuPropagation:
    """Earth slant-path attenuation from the ITU-R Recommendations.

    Combines the mechanisms per P.618-13 Section 2.5:

        A_total = A_gas + sqrt((A_rain + A_cloud)^2 + A_scint^2)

    Rain and cloud are correlated and add; scintillation is statistically
    independent of the slow fades and enters in an RSS sense.

    ``exceedance_percent`` is the fraction of an average year the result is
    exceeded: 0.01 means 99.99% availability. It is a **long-term statistic**,
    not the weather at an epoch, so a time history evaluated with this model
    shows the same fade throughout. That is what the model means, and calling it
    a time-varying weather model would be wrong.

    Only applicable where the path actually crosses the atmosphere, which is the
    slant path at the Earth station. On an Earth-Moon link it applies to the
    station's slant path, not to the 380 000 km beyond it.

    Gas, cloud and scintillation are evaluated at an elevation of at least
    ``MINIMUM_VALID_ELEVATION_DEG`` (5 deg; the low-angle methods are not
    implemented): below it they are optimistic, and the breakdown's
    diagnostics record that elevation as ``model_elevation_deg``.

    Reference: Recommendation ITU-R P.618-13 (2017), section 2.2.1.1 (attenuation due to rain) and
    2.5 (combination of mechanisms) (checked against a secondary source) [SIDERA-ALG-COM-003].
    """

    weather: EarthSiteWeather
    latitude_deg: float
    station_height_km: float
    exceedance_percent: float
    antenna_diameter_m: float | None = None
    antenna_efficiency: float = 0.5
    include_gaseous: bool = True
    include_cloud: bool = True
    include_scintillation: bool = True
    name: str = "ITU-R Earth slant path"
    accounts_for_atmosphere: bool = True

    def __post_init__(self) -> None:
        p = float(self.exceedance_percent)
        if not 0.001 <= p <= 5.0:
            raise RfError(
                f"exceedance percent must lie in [0.001, 5] for the rain model, got {p!r}"
            )
        if self.include_scintillation and self.antenna_diameter_m is None:
            raise RfError(
                "scintillation depends on aperture averaging, so it needs "
                "antenna_diameter_m. Supply one, or set include_scintillation=False."
            )

    def evaluate(
        self,
        geometry: LinkGeometry,
        frequency_hz: float,
        context: Any | None = None,
    ) -> PropagationLossBreakdown:
        """The ITU-R rain, gas, cloud and scintillation loss at the given elevation."""
        del context
        if geometry.elevation_rad is None:
            raise RfError(
                f"{self.name}: the slant-path models need an elevation angle, which "
                "is only defined when one end of the link is a surface site. This "
                "model does not apply to a space-to-space path."
            )
        elevation_deg = math.degrees(geometry.elevation_rad)
        frequency_ghz = float(frequency_hz) / 1.0e9

        rain = rain_attenuation_db(
            frequency_ghz,
            elevation_deg,
            self.latitude_deg,
            self.station_height_km,
            self.weather,
            self.exceedance_percent,
        )
        gaseous = (
            gaseous_attenuation_db(frequency_ghz, elevation_deg, self.weather)
            if self.include_gaseous
            else 0.0
        )
        cloud = (
            cloud_attenuation_db(frequency_ghz, elevation_deg, self.weather)
            if self.include_cloud
            else 0.0
        )
        scintillation = 0.0
        if self.include_scintillation and self.antenna_diameter_m is not None:
            scintillation = scintillation_fade_db(
                frequency_ghz,
                elevation_deg,
                self.antenna_diameter_m,
                self.antenna_efficiency,
                self.weather,
                max(self.exceedance_percent, 0.01),
            )

        total = gaseous + math.sqrt((rain + cloud) ** 2 + scintillation**2)
        # Only the absorptive mechanisms emit thermal noise. Scintillation is
        # refractive: it fades the carrier without heating the receiver, so it
        # is in the total and not in the absorptive part. The absorptive sum can
        # never exceed the total, because sqrt((r+c)^2 + s^2) >= r + c.
        absorptive = rain + cloud + gaseous

        return PropagationLossBreakdown(
            gaseous_absorption_db=gaseous,
            rain_attenuation_db=rain,
            cloud_attenuation_db=cloud,
            scintillation_db=scintillation,
            total_carrier_loss_db=total,
            absorptive_loss_db=absorptive,
            sources=(self.name,),
            diagnostics={
                "exceedance_percent": self.exceedance_percent,
                "availability_percent": 100.0 - self.exceedance_percent,
                "elevation_deg": elevation_deg,
                # Gas, cloud and scintillation are evaluated at no less than
                # this; below it they are optimistic against the cosecant law.
                "model_elevation_deg": max(float(elevation_deg), MINIMUM_VALID_ELEVATION_DEG),
                "weather": self.weather.as_dict(),
            },
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "kind": "earth_itu_slant_path",
            "name": self.name,
            "exceedance_percent": self.exceedance_percent,
            "latitude_deg": self.latitude_deg,
            "station_height_km": self.station_height_km,
            "include_gaseous": self.include_gaseous,
            "include_cloud": self.include_cloud,
            "include_scintillation": self.include_scintillation,
            "weather": self.weather.as_dict(),
            "recommendations": [
                "ITU-R P.838-3",
                "ITU-R P.618-13",
                "ITU-R P.676-12",
                "ITU-R P.840-8",
                "ITU-R P.453-14",
            ],
        }


@dataclass(frozen=True, slots=True)
class SimplifiedAtmosphericEmissionNoise:
    """A simplified elevation- and fade-dependent receive system temperature.

    **This is not a standards-grade receiver noise model.** It is an engineering
    model, kept under a name that says so, and `as_dict` reports
    ``standards_grade: False``.

    What it models:

    - a fixed receiver and spillover contribution,
    - a clear-sky term that grows as elevation falls, bounded so it cannot
      stand in for a propagation standard,
    - thermal emission from the **absorptive** attenuation on the path, via
      ``T = T_medium (1 - 10^(-A/10))``, the radiative-transfer result for a
      lossy layer at a single physical temperature,
    - the cosmic microwave background.

    What it omits: the real vertical temperature profile, the different emission
    heights of oxygen and water vapour, antenna-pattern weighting of the sky,
    ground pickup as a function of elevation, and any frequency dependence
    beyond what the attenuation already carries.

    Scintillation is excluded from the emitting attenuation by construction: it
    reads ``absorptive_loss_db``, and a refractive fade never enters that term.
    A refractive fade redistributes energy rather than radiating, so counting it
    here would invent noise that is not there.

    Reference: none, a Sidera heuristic without a published source [SIDERA-HEUR-COM-002].
    """

    receiver_internal_noise_k: float = 90.0
    spillover_noise_k: float = 20.0
    clear_sky_base_noise_k: float = 12.0
    low_elevation_extra_noise_k: float = 35.0
    medium_temperature_k: float = 275.0
    minimum_elevation_deg: float = 5.0
    clear_sky_cap_k: float = 120.0
    name: str = "simplified atmospheric emission noise"

    def __post_init__(self) -> None:
        for field_name in (
            "receiver_internal_noise_k",
            "spillover_noise_k",
            "clear_sky_base_noise_k",
            "low_elevation_extra_noise_k",
            "medium_temperature_k",
            "clear_sky_cap_k",
        ):
            value = float(getattr(self, field_name))
            if not math.isfinite(value) or value < 0.0:
                raise RfError(f"{field_name} must be finite and non-negative K, got {value!r}")

    def emission_temperature_k(self, absorptive_loss_db: float) -> float:
        """``T_medium (1 - 10^(-A/10))``: emission from an absorbing layer."""
        loss = max(float(absorptive_loss_db), 0.0)
        transmissivity = 10.0 ** (-loss / 10.0)
        return self.medium_temperature_k * (1.0 - transmissivity)

    def clear_sky_temperature_k(self, elevation_deg: float) -> float:
        """Cosmic background plus a cosecant-shaped low-elevation term, capped."""
        effective = max(float(elevation_deg), self.minimum_elevation_deg)
        sin_el = max(math.sin(math.radians(effective)), 0.03)
        return min(
            COSMIC_BACKGROUND_TEMPERATURE_K
            + self.clear_sky_base_noise_k
            + self.low_elevation_extra_noise_k * (1.0 / sin_el - 1.0) / 8.0,
            self.clear_sky_cap_k,
        )

    def system_temperature_k(
        self,
        geometry: LinkGeometry,
        propagation: PropagationLossBreakdown,
    ) -> float:
        """The receive system temperature for this geometry and attenuation.

        The signature is `SkyNoiseModel`'s: the combined propagation breakdown
        arrives already evaluated, so the emission always corresponds to the
        attenuation that was applied to the carrier -- the two cannot drift
        apart.
        """
        if geometry.elevation_rad is None:
            raise RfError(
                f"{self.name}: an elevation-dependent sky-noise model needs an "
                "elevation angle, which is only defined when one end of the link "
                "is a surface site. A space-to-space path has no sky to look "
                "through and no elevation to look at it from."
            )
        elevation_deg = math.degrees(geometry.elevation_rad)
        return (
            self.receiver_internal_noise_k
            + self.spillover_noise_k
            + self.clear_sky_temperature_k(elevation_deg)
            + self.emission_temperature_k(propagation.absorptive_loss_db)
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "kind": "simplified_atmospheric_emission_noise",
            "name": self.name,
            "standards_grade": False,
            "receiver_internal_noise_k": self.receiver_internal_noise_k,
            "spillover_noise_k": self.spillover_noise_k,
            "clear_sky_base_noise_k": self.clear_sky_base_noise_k,
            "low_elevation_extra_noise_k": self.low_elevation_extra_noise_k,
            "medium_temperature_k": self.medium_temperature_k,
            "clear_sky_cap_k": self.clear_sky_cap_k,
        }
