"""Radio links: RF primitives, antennas, terminals, ITU-R Earth-path propagation and one-way link budgets.

Copied from Sidera (the author's own package) on 2026-10-25; see ``SOURCES.md`` for every file, its source
module and the commit. Only the import paths differ from Sidera. Units are SI throughout (Hz, m, W/dBW, K,
radians); decibel references are in every name (``_db``, ``_dbw``, ``_dbi``, ``_dbhz``).

Typical use::

    from aerokit.comms import (CommunicationLink, CommunicationTerminal, FixedGainAntenna, FreeSpaceOnly,
                               Receiver, Transmitter, evaluate_link, geometry_from_states)
"""
from aerokit.comms.antennas import (
    FixedGainAntenna,
    GaussianBeamPattern,
    ItuS465ReferencePattern,
    ParabolicDishAntenna,
    ScreeningOffAxisPattern,
    TabulatedPattern,
    TaperedApertureAntenna,
    approximate_half_power_beamwidth_rad,
    parabolic_dish_diameter_m,
    parabolic_dish_gain_dbi,
)
from aerokit.comms.budget import CommunicationLink, EngineeringLosses, LinkBudgetResult, evaluate_link
from aerokit.comms.channel import (
    FixedAtmosphericAllowance,
    FreeSpaceOnly,
    PropagationLossBreakdown,
    combine_propagation_losses,
)
from aerokit.comms.data_volume import integrate_data_volume_bits
from aerokit.comms.digital import (
    AdaptiveCodingAndModulation,
    DigitalLinkPerformance,
    DigitalLinkScheme,
    FixedRateDigitalLink,
    ShannonBound,
    coded_channel_rate_bps,
    coding_gain_shifted_ber,
    dvb_s2_acm,
    gap_to_shannon_db,
    occupied_bandwidth_hz,
    shannon_capacity_bps,
    shannon_ebn0_limit_db,
    uncoded_ber_awgn,
)
from aerokit.comms.geometry import LinkGeometry, doppler_shift_hz, geometry_from_states, one_way_light_time_s
from aerokit.comms.itu_earth import (
    EarthItuPropagation,
    EarthSiteWeather,
    ExplicitRainHeight,
    LegacyLatitudeFallback,
    SimplifiedAtmosphericEmissionNoise,
    cloud_attenuation_db,
    gaseous_attenuation_db,
    legacy_rome_ankara_weather,
    rain_attenuation_001_db,
    rain_attenuation_db,
    rain_coefficients_p838,
    scintillation_fade_db,
    wet_term_refractivity,
)
from aerokit.comms.modcod import (
    DVB_S2_NORMAL_FRAME_MODCODS,
    DVB_S2_NORMAL_FRAME_TABLE,
    Modcod,
    ModcodTable,
    custom_modcod_table,
    esn0_from_cn0_db,
    select_best_modcod,
    symbol_rate_baud,
)
from aerokit.comms.rf import (
    RfError,
    carrier_to_noise_density_dbhz,
    db_to_linear,
    ebn0_from_density_db,
    free_space_path_loss_db,
    linear_to_db,
    noise_power_dbw,
    wavelength_m,
)
from aerokit.comms.state import StateProvider
from aerokit.comms.terminals import CommunicationTerminal, Receiver, Transmitter

__all__ = [
    "CommunicationLink", "CommunicationTerminal", "EarthItuPropagation", "EarthSiteWeather", "EngineeringLosses",
    "ExplicitRainHeight", "FixedAtmosphericAllowance", "FixedGainAntenna", "FreeSpaceOnly", "GaussianBeamPattern",
    "ItuS465ReferencePattern", "LegacyLatitudeFallback", "LinkBudgetResult", "LinkGeometry", "ParabolicDishAntenna",
    "PropagationLossBreakdown", "Receiver", "RfError", "ScreeningOffAxisPattern", "SimplifiedAtmosphericEmissionNoise",
    "StateProvider", "TabulatedPattern", "TaperedApertureAntenna", "Transmitter",
    "approximate_half_power_beamwidth_rad", "carrier_to_noise_density_dbhz", "cloud_attenuation_db",
    "combine_propagation_losses", "db_to_linear", "doppler_shift_hz", "ebn0_from_density_db", "evaluate_link",
    "free_space_path_loss_db", "gaseous_attenuation_db", "geometry_from_states", "legacy_rome_ankara_weather",
    "linear_to_db", "noise_power_dbw", "one_way_light_time_s", "parabolic_dish_diameter_m", "parabolic_dish_gain_dbi",
    "rain_attenuation_001_db", "rain_attenuation_db", "rain_coefficients_p838", "scintillation_fade_db",
    "wavelength_m", "wet_term_refractivity",
    "AdaptiveCodingAndModulation", "DigitalLinkPerformance", "DigitalLinkScheme", "FixedRateDigitalLink", "ShannonBound",
    "coded_channel_rate_bps", "coding_gain_shifted_ber", "dvb_s2_acm", "gap_to_shannon_db", "occupied_bandwidth_hz",
    "shannon_capacity_bps", "shannon_ebn0_limit_db", "uncoded_ber_awgn", "DVB_S2_NORMAL_FRAME_MODCODS",
    "DVB_S2_NORMAL_FRAME_TABLE", "Modcod", "ModcodTable", "custom_modcod_table", "esn0_from_cn0_db",
    "select_best_modcod", "symbol_rate_baud", "integrate_data_volume_bits",
]
