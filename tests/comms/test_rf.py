# Copied from Sidera (tests/communications/test_communications_rf.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""RF primitive, antenna and static link-budget validation.

Three layers, as the migration brief requires.

**Layer A, legacy parity.** The numbers come from the source repository at
revision 91225ca6a190c164a0a0c2a53f1f855236b00de8: its own regression tests and
its frozen ``outputs/*.csv``. Where Sidera deliberately differs, the difference
is asserted to its exact measured size rather than absorbed into a loose
tolerance.

**Layer B, analytic physics.** FSPL scaling, dish-gain scaling, dB linearity,
and the inverse-linear combination rule -- each checked against algebra done in
the test.

**Layer C** lives in the trajectory suites.
"""

from __future__ import annotations

import math

import pytest

from aerokit.comms.constants import BOLTZMANN_J_PER_K, C_LIGHT
from aerokit.comms import (
    CommunicationLink,
    CommunicationTerminal,
    EngineeringLosses,
    FixedAtmosphericAllowance,
    FixedGainAntenna,
    FreeSpaceOnly,
    ParabolicDishAntenna,
    Receiver,
    RfError,
    ScreeningOffAxisPattern,
    Transmitter,
    evaluate_link,
    geometry_from_states,
)
from aerokit.comms.antennas import (
    parabolic_dish_diameter_m,
    parabolic_dish_gain_dbi,
)
from aerokit.comms.rf import (
    BOLTZMANN_DB_W_PER_K_HZ,
    carrier_to_noise_density_dbhz,
    carrier_to_noise_from_density_db,
    combine_inverse_ratios_db,
    db_to_linear,
    dbw_to_watts,
    ebn0_from_carrier_to_noise_db,
    ebn0_from_density_db,
    free_space_path_loss_db,
    linear_to_db,
    noise_power_dbw,
    watts_to_dbw,
    wavelength_m,
)

# --- Legacy values, read from the pinned source revision --------------------
# outputs/geometry_static.csv and outputs/link_budget_static.csv
LEGACY_UPLINK_RANGE_KM = 37_658.789_922_890_17
LEGACY_UPLINK_FSPL_DB = 206.889_887_930_919_2
LEGACY_UPLINK_TX_GAIN_DBI = 48.857_285_838_103_54
LEGACY_UPLINK_EIRP_DBW = 60.867_585_794_743_356
LEGACY_UPLINK_CN0_DBHZ = 84.076_865_037_041_81

LEGACY_DOWNLINK_RANGE_KM = 37_822.525_205_787
LEGACY_DOWNLINK_FSPL_DB = 205.588_635_340_444_57
LEGACY_DOWNLINK_RX_GAIN_DBI = 38.998_975_400_045_66
LEGACY_DOWNLINK_G_OVER_T = 16.738_062_809_488_845
LEGACY_DOWNLINK_CN0_DBHZ = 84.248_594_642_261_93
LEGACY_DOWNLINK_CARRIER_DBW = -122.589_659_940_398_92

# The legacy FSPL used a rounded 92.45 dB constant where the exact value is
# 92.447 783 2. Every legacy FSPL is therefore high by this fixed amount.
LEGACY_FSPL_ROUNDING_BIAS_DB = 92.45 - 20.0 * math.log10(4.0 * math.pi * 1.0e12 / C_LIGHT)


# ---------------------------------------------------------------------------
# Layer B: decibel conversions
# ---------------------------------------------------------------------------

def test_decibel_conversions_round_trip():
    for ratio in (1.0e-6, 0.5, 1.0, 2.0, 1.0e9):
        assert db_to_linear(linear_to_db(ratio)) == pytest.approx(ratio, rel=1e-12, abs=0.0)
    for power_w in (1.0e-12, 20.0, 1.0e6):
        assert dbw_to_watts(watts_to_dbw(power_w)) == pytest.approx(power_w, rel=1e-12, abs=0.0)


def test_decibels_are_power_ratios_not_amplitude_ratios():
    """Factor 10, not 20. A doubling of power is 3.0103 dB."""
    assert linear_to_db(2.0) == pytest.approx(3.010_299_956_639_812, rel=1e-15, abs=0.0)
    assert linear_to_db(10.0) == pytest.approx(10.0, rel=1e-15, abs=0.0)
    assert watts_to_dbw(1.0) == 0.0


@pytest.mark.parametrize("bad", [0.0, -1.0, -1e-30])
def test_a_non_positive_ratio_has_no_decibel_value(bad):
    with pytest.raises(RfError, match="finite and positive"):
        linear_to_db(bad)
    with pytest.raises(RfError, match="finite and positive"):
        watts_to_dbw(bad)


def test_the_boltzmann_term_matches_the_conventional_228_6():
    """The link equation's '+228.6' is -10 log10(k), computed not hard-coded."""
    assert -BOLTZMANN_DB_W_PER_K_HZ == pytest.approx(228.599_167_173, abs=1e-9)
    assert BOLTZMANN_DB_W_PER_K_HZ == pytest.approx(
        10.0 * math.log10(BOLTZMANN_J_PER_K), rel=1e-15, abs=0.0
    )


def test_thermal_noise_power_follows_ktb():
    """N = kTB, checked against the linear product."""
    temperature, bandwidth = 290.0, 1.0e6
    expected = 10.0 * math.log10(BOLTZMANN_J_PER_K * temperature * bandwidth)
    assert noise_power_dbw(temperature, bandwidth) == pytest.approx(expected, rel=1e-12)
    # Doubling the bandwidth adds 3.01 dB of noise.
    assert noise_power_dbw(temperature, 2.0 * bandwidth) - noise_power_dbw(
        temperature, bandwidth
    ) == pytest.approx(3.010_299_956_639_812, rel=1e-12)


# ---------------------------------------------------------------------------
# Layer B: free-space path loss
# ---------------------------------------------------------------------------

def test_fspl_rises_by_6_0206_db_when_range_doubles():
    base = free_space_path_loss_db(1.0e6, 12.0e9)
    assert free_space_path_loss_db(2.0e6, 12.0e9) - base == pytest.approx(
        20.0 * math.log10(2.0), rel=1e-12
    )
    assert 20.0 * math.log10(2.0) == pytest.approx(6.020_599_913_279_624, rel=1e-12)


def test_fspl_rises_by_6_0206_db_when_frequency_doubles():
    base = free_space_path_loss_db(1.0e6, 12.0e9)
    assert free_space_path_loss_db(1.0e6, 24.0e9) - base == pytest.approx(
        20.0 * math.log10(2.0), rel=1e-12
    )


def test_fspl_is_one_wavelength_at_the_defining_radius():
    """At R = lambda / (4 pi) the loss is exactly 0 dB, by construction."""
    frequency = 12.0e9
    radius = wavelength_m(frequency) / (4.0 * math.pi)
    assert free_space_path_loss_db(radius, frequency) == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize(
    ("range_m", "frequency_hz"),
    [(0.0, 12e9), (-1.0, 12e9), (1e6, 0.0), (1e6, -1.0)],
)
def test_fspl_rejects_non_physical_inputs(range_m, frequency_hz):
    with pytest.raises(RfError, match="finite and positive"):
        free_space_path_loss_db(range_m, frequency_hz)


# ---------------------------------------------------------------------------
# Layer A: FSPL parity with the legacy repository
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("range_km", "frequency_hz", "legacy_db"),
    [
        (LEGACY_UPLINK_RANGE_KM, 14.0e9, LEGACY_UPLINK_FSPL_DB),
        (LEGACY_DOWNLINK_RANGE_KM, 12.0e9, LEGACY_DOWNLINK_FSPL_DB),
    ],
)
def test_fspl_differs_from_legacy_by_exactly_the_rounding_bias(
    range_km, frequency_hz, legacy_db
):
    """An intentional model correction, quantified rather than tolerated.

    The legacy implementation used ``92.45 + 20log10(f_GHz) + 20log10(R_km)``.
    The exact constant is 92.447 783 2, so every legacy FSPL is high by
    0.002 216 8 dB. Sidera computes ``20 log10(4 pi R f / c)`` in SI.

    Asserting the difference to 1e-12 is much stronger than asserting agreement
    to 0.01 dB: it proves the *only* difference is the constant.
    """
    sidera_db = free_space_path_loss_db(range_km * 1e3, frequency_hz)
    assert legacy_db - sidera_db == pytest.approx(LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-12)
    assert LEGACY_FSPL_ROUNDING_BIAS_DB == pytest.approx(0.002_216_778, abs=1e-9)


def test_fspl_matches_the_legacy_smoke_value():
    """The source's own test: FSPL(12 GHz, 38 000 km) ~ 205.6 dB."""
    assert free_space_path_loss_db(38_000e3, 12.0e9) == pytest.approx(205.6, abs=0.05)


# ---------------------------------------------------------------------------
# Layer A + B: antenna gain
# ---------------------------------------------------------------------------

def test_dish_gain_matches_the_legacy_uplink_antenna_exactly():
    """2.4 m, 14 GHz, eta 0.62 -- the Rome uplink dish. Pure algebra, so exact."""
    gain = parabolic_dish_gain_dbi(2.4, 14.0e9, 0.62)
    assert gain == pytest.approx(LEGACY_UPLINK_TX_GAIN_DBI, abs=1e-12)
    assert gain == pytest.approx(48.86, abs=0.01)


def test_dish_gain_matches_the_legacy_downlink_antenna_exactly():
    """0.9 m, 12 GHz, eta 0.62 -- the Ankara receive dish."""
    assert parabolic_dish_gain_dbi(0.9, 12.0e9, 0.62) == pytest.approx(
        LEGACY_DOWNLINK_RX_GAIN_DBI, abs=1e-12
    )


def test_dish_diameter_inverts_the_dish_gain():
    """``parabolic_dish_diameter_m`` returns the diameter that ``parabolic_dish_gain_dbi`` maps back to the gain."""
    for gain, frequency, eta in ((48.86, 14.0e9, 0.62), (20.0, 401.585625e6, 0.6), (3.0, 2.2e9, 0.55)):
        diameter = parabolic_dish_diameter_m(gain, frequency, eta)
        assert parabolic_dish_gain_dbi(diameter, frequency, eta) == pytest.approx(gain, abs=1e-10)
    # The Rome uplink dish back from its legacy gain.
    assert parabolic_dish_diameter_m(LEGACY_UPLINK_TX_GAIN_DBI, 14.0e9, 0.62) == pytest.approx(2.4, rel=1e-12)
    # Effective aperture form G = 4 pi A_e / lambda^2 with A_e = eta pi D^2 / 4 (independent of the gain code).
    lam = 299792458.0 / 401.585625e6
    d = parabolic_dish_diameter_m(20.0, 401.585625e6, 0.6)
    assert 4.0 * math.pi * (0.6 * math.pi * d * d / 4.0) / lam**2 == pytest.approx(100.0, rel=1e-12)
    with pytest.raises(RfError):
        parabolic_dish_diameter_m(20.0, 401.6e6, 0.0)
    with pytest.raises(RfError):
        parabolic_dish_diameter_m(float("nan"), 401.6e6, 0.6)


def test_dish_gain_scales_as_diameter_squared():
    base = parabolic_dish_gain_dbi(1.0, 12e9, 0.62)
    assert parabolic_dish_gain_dbi(2.0, 12e9, 0.62) - base == pytest.approx(
        20.0 * math.log10(2.0), rel=1e-12
    )


def test_dish_gain_scales_as_frequency_squared():
    base = parabolic_dish_gain_dbi(2.4, 12e9, 0.62)
    assert parabolic_dish_gain_dbi(2.4, 24e9, 0.62) - base == pytest.approx(
        20.0 * math.log10(2.0), rel=1e-12
    )


def test_dish_gain_scales_linearly_with_efficiency():
    base = parabolic_dish_gain_dbi(2.4, 12e9, 0.30)
    assert parabolic_dish_gain_dbi(2.4, 12e9, 0.60) - base == pytest.approx(
        10.0 * math.log10(2.0), rel=1e-12
    )


@pytest.mark.parametrize(
    ("diameter", "efficiency"),
    [(0.0, 0.62), (-1.0, 0.62), (2.4, 0.0), (2.4, -0.1), (2.4, 1.5)],
)
def test_a_non_physical_dish_is_refused(diameter, efficiency):
    with pytest.raises(RfError):
        parabolic_dish_gain_dbi(diameter, 12e9, efficiency)


def test_a_dish_is_frequency_dependent_and_a_fixed_gain_antenna_is_not():
    dish = ParabolicDishAntenna(diameter_m=2.4, aperture_efficiency=0.62)
    fixed = FixedGainAntenna(gain_dbi_boresight=48.86)
    assert dish.gain_dbi(14e9) != pytest.approx(dish.gain_dbi(12e9), abs=0.5)
    assert fixed.gain_dbi(14e9) == fixed.gain_dbi(12e9) == 48.86


def test_a_bare_dish_reports_boresight_gain_at_any_angle():
    """It does not invent an off-axis pattern; that needs a named approximation."""
    dish = ParabolicDishAntenna(diameter_m=2.4)
    assert dish.gain_dbi(14e9, math.radians(5.0)) == dish.gain_dbi(14e9, 0.0)


# ---------------------------------------------------------------------------
# The screening pattern is labelled as one
# ---------------------------------------------------------------------------

def test_the_screening_pattern_falls_off_and_says_it_is_screening():
    dish = ParabolicDishAntenna(diameter_m=2.4, aperture_efficiency=0.62)
    pattern = ScreeningOffAxisPattern(base=dish)
    boresight = pattern.gain_dbi(14e9, 0.0)

    assert boresight == pytest.approx(dish.gain_dbi(14e9), abs=1e-9)
    previous = boresight
    for angle_deg in (0.5, 1.0, 2.0, 5.0, 10.0):
        gain = pattern.gain_dbi(14e9, math.radians(angle_deg))
        assert gain < previous, angle_deg
        previous = gain
    # Far off-axis it must be far below boresight.
    assert boresight - pattern.gain_dbi(14e9, math.radians(10.0)) > 20.0
    assert pattern.as_dict()["screening_only"] is True


def test_the_screening_envelope_never_exceeds_the_antenna_gain():
    """A screening envelope that reported more than boresight would be nonsense."""
    small = ParabolicDishAntenna(diameter_m=0.45, aperture_efficiency=0.62)
    pattern = ScreeningOffAxisPattern(base=small)
    boresight = small.gain_dbi(12e9)
    for angle_deg in (0.1, 1.0, 3.0, 30.0, 90.0):
        assert pattern.gain_dbi(12e9, math.radians(angle_deg)) <= boresight


def test_the_screening_envelope_does_not_jump_up_outside_the_main_lobe():
    """The envelope must be non-increasing across the main-lobe edge.

    A 9 m dish at 12 GHz has a beamwidth under 0.2 degree, where
    ``log10(degrees(angle))`` is negative just past the edge, so a loose
    boresight - 3 dB cap let the raw envelope value exceed the main lobe's
    own edge value and the reported gain jumped up right outside the lobe.
    """
    dish = ParabolicDishAntenna(diameter_m=9.0, aperture_efficiency=0.62)
    pattern = ScreeningOffAxisPattern(base=dish)
    beamwidth = pattern._main_lobe_width_rad(12.0e9)

    # A fine grid from boresight out past the main lobe, straddling the edge
    # densely and then continuing out to 90 degrees, sorted by angle so each
    # step is a genuine "further off axis" comparison.
    grid = [beamwidth * factor for factor in (0.0, 0.25, 0.5, 0.75, 0.99, 0.999, 1.0)]
    grid += [
        beamwidth + delta
        for delta in (1e-6, 1e-4, 1e-3, 1e-2, 0.1 * beamwidth, beamwidth, 5.0 * beamwidth)
    ]
    grid += [math.radians(deg) for deg in (1.0, 2.0, 5.0, 10.0, 30.0, 90.0)]
    grid.sort()
    previous = pattern.gain_dbi(12.0e9, 0.0)
    for angle in grid:
        gain = pattern.gain_dbi(12.0e9, angle)
        assert gain <= previous + 1e-9, angle
        previous = gain


def test_the_screening_pattern_works_without_an_aperture():
    """A datasheet gain has no diameter, so no beamwidth can be derived."""
    pattern = ScreeningOffAxisPattern(base=FixedGainAntenna(gain_dbi_boresight=40.0))
    assert pattern.gain_dbi(12e9, 0.0) == pytest.approx(40.0)
    assert pattern.gain_dbi(12e9, math.radians(5.0)) < 40.0


# ---------------------------------------------------------------------------
# Layer A + B: carrier-to-noise quantities
# ---------------------------------------------------------------------------

def test_cn0_shifts_one_for_one_with_eirp():
    base = carrier_to_noise_density_dbhz(60.0, 16.0, 200.0)
    assert carrier_to_noise_density_dbhz(61.0, 16.0, 200.0) - base == pytest.approx(
        1.0, rel=1e-12
    )
    assert carrier_to_noise_density_dbhz(60.0, 17.0, 200.0) - base == pytest.approx(
        1.0, rel=1e-12
    )
    assert carrier_to_noise_density_dbhz(60.0, 16.0, 201.0) - base == pytest.approx(
        -1.0, rel=1e-12
    )


def test_the_two_ebn0_routes_agree():
    """C/N0 - 10log(Rb) and C/N + 10log(B/Rb) are the same quantity."""
    cn0, bandwidth, rate = 84.25, 36.0e6, 10.0e6
    cn = carrier_to_noise_from_density_db(cn0, bandwidth)
    assert ebn0_from_density_db(cn0, rate) == pytest.approx(
        ebn0_from_carrier_to_noise_db(cn, bandwidth, rate), rel=1e-12
    )


def test_legacy_uplink_cn0_is_reproduced_within_the_fspl_correction():
    """The whole uplink chain, against the frozen legacy value.

    Sidera's FSPL is 0.0022 dB lower, so C/N0 must be 0.0022 dB *higher* and
    nothing else may differ. Asserting that exactly is a far stronger statement
    than agreeing to a tenth of a dB.
    """
    eirp = 20.0 * 0.0 + LEGACY_UPLINK_EIRP_DBW  # legacy EIRP, reproduced below
    fspl = free_space_path_loss_db(LEGACY_UPLINK_RANGE_KM * 1e3, 14.0e9)
    cn0 = carrier_to_noise_density_dbhz(eirp, 3.0, fspl + 1.5)
    assert cn0 - LEGACY_UPLINK_CN0_DBHZ == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-9
    )


def test_the_legacy_uplink_eirp_is_reproduced_exactly():
    """20 W, 2.4 m dish at 14 GHz, 1.0 dB feeder loss."""
    transmitter = Transmitter(
        antenna=ParabolicDishAntenna(diameter_m=2.4, aperture_efficiency=0.62),
        rf_power_w=20.0,
        feeder_loss_db=1.0,
    )
    assert transmitter.eirp_dbw(14.0e9) == pytest.approx(
        LEGACY_UPLINK_EIRP_DBW, abs=1e-12
    )


def test_the_legacy_downlink_g_over_t_is_reproduced_exactly():
    """0.9 m at 12 GHz, Tsys 150 K referenced at the receiver input, 0.5 dB feeder loss."""
    receiver = Receiver(
        antenna=ParabolicDishAntenna(diameter_m=0.9, aperture_efficiency=0.62),
        system_noise_temperature_k=150.0,
        feeder_loss_db=0.5,
        noise_temperature_reference="receiver_input",
    )
    assert receiver.g_over_t_db_per_k(12.0e9) == pytest.approx(
        LEGACY_DOWNLINK_G_OVER_T, abs=1e-12
    )


# ---------------------------------------------------------------------------
# Inverse-linear combination
# ---------------------------------------------------------------------------

def test_two_equal_ratios_combine_to_2_99_db_below_not_by_adding():
    """The legacy test's value, and the error it guards against.

    Two 10 dB contributions combine to 6.9897 dB. Adding decibels would give
    20 dB -- better than either, which is physically backwards.
    """
    assert combine_inverse_ratios_db([10.0, 10.0]) == pytest.approx(
        6.989_700_043_360_187, rel=1e-12
    )
    assert combine_inverse_ratios_db([10.0, 10.0]) == pytest.approx(6.99, abs=0.01)
    assert combine_inverse_ratios_db([10.0, 10.0]) < 10.0


def test_combination_is_dominated_by_the_worst_contributor():
    assert combine_inverse_ratios_db([10.0, 40.0]) == pytest.approx(9.9957, abs=1e-3)
    assert combine_inverse_ratios_db([10.0]) == pytest.approx(10.0, rel=1e-12)


def test_none_entries_contribute_nothing():
    """An unmodelled impairment must not default to something."""
    assert combine_inverse_ratios_db([12.0, None, None]) == pytest.approx(12.0, rel=1e-12)
    with pytest.raises(RfError, match="at least one"):
        combine_inverse_ratios_db([None, None])


def test_combination_is_order_independent():
    assert combine_inverse_ratios_db([10.0, 15.0, 20.0]) == pytest.approx(
        combine_inverse_ratios_db([20.0, 10.0, 15.0]), rel=1e-14, abs=0.0
    )


# ---------------------------------------------------------------------------
# Hardware rules
# ---------------------------------------------------------------------------

def test_an_eirp_override_is_not_reduced_by_the_feeder_loss_again():
    """A published EIRP is already effective radiated power."""
    transmitter = Transmitter(eirp_dbw_override=46.0, feeder_loss_db=2.0)
    assert transmitter.eirp_dbw(12.0e9) == 46.0


def test_a_transmitter_without_power_or_override_says_what_is_missing():
    with pytest.raises(RfError, match="EIRP is undefined"):
        Transmitter(antenna=FixedGainAntenna(gain_dbi_boresight=40.0)).eirp_dbw(12e9)


def test_a_transmitter_with_power_but_no_antenna_says_what_is_missing():
    with pytest.raises(RfError, match="needs an antenna"):
        Transmitter(rf_power_w=20.0).eirp_dbw(12e9)


def test_power_may_be_given_once_only():
    with pytest.raises(RfError, match="not both"):
        Transmitter(rf_power_w=20.0, rf_power_dbw=13.0)


def test_the_feeder_loss_reference_plane_gives_the_same_g_over_t():
    """G/T is invariant under the reference plane; the formula is not.

    40 dBi, 2 dB feeder loss, T_A = 50 K, T0 = 290 K, T_R = 100 K. Referenced
    at the antenna output, T_sys already folds in the feeder's noise
    contribution, so the loss is not applied again to the gain. Referenced at
    the receiver input, both the gain and the temperature move past the
    feeder together and the loss is applied to the gain.
    """
    t_ant_ref = 50.0 + 290.0 * (10 ** 0.2 - 1.0) + 10**0.2 * 100.0
    antenna_output = Receiver(
        antenna=FixedGainAntenna(gain_dbi_boresight=40.0),
        system_noise_temperature_k=t_ant_ref,
        feeder_loss_db=2.0,
        noise_temperature_reference="antenna_output",
    )
    t_rx_ref = t_ant_ref / 10**0.2
    receiver_input = Receiver(
        antenna=FixedGainAntenna(gain_dbi_boresight=40.0),
        system_noise_temperature_k=t_rx_ref,
        feeder_loss_db=2.0,
        noise_temperature_reference="receiver_input",
    )
    assert antenna_output.g_over_t_db_per_k(12e9) == pytest.approx(14.224, abs=1e-3)
    assert receiver_input.g_over_t_db_per_k(12e9) == pytest.approx(
        antenna_output.g_over_t_db_per_k(12e9), rel=1e-12
    )


def test_a_receiver_input_referenced_temperature_with_no_feeder_loss():
    """A figure with no feeder loss is a degenerate case of either plane."""
    receiver = Receiver(
        antenna=FixedGainAntenna(gain_dbi_boresight=40.0),
        system_noise_temperature_k=150.0,
        noise_temperature_reference="receiver_input",
    )
    assert receiver.g_over_t_db_per_k(12e9) == pytest.approx(
        40.0 - 10.0 * math.log10(150.0), rel=1e-12
    )


def test_a_g_over_t_override_bypasses_the_feeder_loss():
    """A quoted G/T is already a system figure."""
    receiver = Receiver(g_over_t_db_per_k_override=3.0, feeder_loss_db=2.0)
    assert receiver.g_over_t_db_per_k(14e9) == 3.0


def test_a_g_over_t_override_wins_over_a_supplied_noise_temperature():
    """A sky-noise model feeds a temperature in; a quoted G/T must not be dropped."""
    receiver = Receiver(
        antenna=FixedGainAntenna(gain_dbi_boresight=40.0), g_over_t_db_per_k_override=10.0
    )
    assert receiver.g_over_t_db_per_k(12e9, system_noise_temperature_k=100.0) == 10.0


def test_a_terminal_must_be_able_to_do_something():
    with pytest.raises(RfError, match="it has neither"):
        CommunicationTerminal(name="empty")


def test_a_receive_only_terminal_cannot_be_a_link_source():
    terminal = CommunicationTerminal(
        name="ground receiver",
        receiver=Receiver(g_over_t_db_per_k_override=20.0),
    )
    assert terminal.can_receive and not terminal.can_transmit
    with pytest.raises(RfError, match="no transmitter"):
        terminal.require_transmitter()


# ---------------------------------------------------------------------------
# The atmospheric double-counting guard
# ---------------------------------------------------------------------------

def _terminals():
    tx = CommunicationTerminal(
        name="tx",
        transmitter=Transmitter(
            antenna=ParabolicDishAntenna(diameter_m=2.4, aperture_efficiency=0.62),
            rf_power_w=20.0,
            feeder_loss_db=1.0,
        ),
    )
    rx = CommunicationTerminal(
        name="rx",
        receiver=Receiver(g_over_t_db_per_k_override=3.0),
    )
    return tx, rx


def test_two_atmospheric_models_are_structurally_refused():
    """The source's rule, enforced by the type system rather than by prose."""
    tx, rx = _terminals()
    with pytest.raises(RfError, match="count the atmosphere twice"):
        CommunicationLink(
            name="doubled",
            transmitter=tx,
            receiver=rx,
            frequency_hz=14e9,
            bandwidth_hz=36e6,
            propagation_models=(
                FixedAtmosphericAllowance(loss_db=0.5),
                FixedAtmosphericAllowance(loss_db=1.2),
            ),
        )


def test_one_atmospheric_model_alongside_free_space_is_fine():
    tx, rx = _terminals()
    link = CommunicationLink(
        name="ok",
        transmitter=tx,
        receiver=rx,
        frequency_hz=14e9,
        bandwidth_hz=36e6,
        propagation_models=(FreeSpaceOnly(), FixedAtmosphericAllowance(loss_db=0.5)),
    )
    assert len(link.propagation_models) == 2


def test_engineering_losses_have_no_atmospheric_field():
    """Removing the field is what makes the double count unreachable."""
    losses = EngineeringLosses(
        pointing_loss_db=0.5, polarization_loss_db=0.3, other_loss_db=0.2
    )
    assert losses.total_db == pytest.approx(1.0, rel=1e-12)
    assert not hasattr(losses, "atmospheric_loss_db")
    with pytest.raises(TypeError):
        EngineeringLosses(atmospheric_loss_db=0.5)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Layer B: link geometry
# ---------------------------------------------------------------------------

def test_iterated_light_time_without_epochs_is_refused_not_mislabelled():
    """From bare states the mode would only be a label; it must point to the solver."""
    from aerokit.comms.geometry import geometry_from_states as _gfs

    with pytest.raises(NotImplementedError, match="geometry_with_light_time"):
        _gfs(
            0.0,
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [1.0e6, 0.0, 0.0, 0.0, 0.0, 0.0],
            light_time_mode="ITERATED_ONE_WAY_LIGHT_TIME",
        )


class _Linear:
    """A point moving at constant velocity: state_at(t) = (x0 + v t, 0, 0, v, 0, 0)."""

    def __init__(self, x0: float, speed: float) -> None:
        self.x0, self.speed = x0, speed

    def state_at(self, epoch_s: float):
        import numpy as np

        return np.array([self.x0 + self.speed * epoch_s, 0.0, 0.0, self.speed, 0.0, 0.0])


def test_the_light_time_solve_matches_the_closed_form_for_a_moving_transmitter():
    """Receiver fixed at D, transmitter at x0 + v t: closed-form transmit epoch.

    t_r - t_t = (D - x0 - v t_t) / c  gives  t_t = (t_r - (D - x0)/c) / (1 - v/c),
    and the range rate d(range)/d(t_r) = -v / (1 - v/c). v = 30 km/s exaggerates
    the light-time terms (1e-4) so the check has teeth; agreement to 1e-15 s and
    1e-12 m/s relative is round-off.
    """
    from aerokit.comms.constants import C_LIGHT
    from aerokit.comms.geometry import geometry_with_light_time

    distance, x0, speed, t_r = 3.844e8, 1.0e7, 3.0e4, 500.0
    geometry = geometry_with_light_time(t_r, _Linear(x0, speed), _Linear(distance, 0.0))
    t_t = (t_r - (distance - x0) / C_LIGHT) / (1.0 - speed / C_LIGHT)
    assert geometry.light_time_mode == "ITERATED_ONE_WAY_LIGHT_TIME"
    assert geometry.receive_epoch_s == t_r
    assert geometry.transmit_epoch_s == pytest.approx(t_t, rel=0.0, abs=1e-12)
    assert geometry.range_m == pytest.approx(distance - x0 - speed * t_t, rel=1e-15)
    assert geometry.range_m == pytest.approx(C_LIGHT * (t_r - geometry.transmit_epoch_s), rel=1e-12)
    expected_rate = -speed / (1.0 - speed / C_LIGHT)
    assert geometry.range_rate_m_s == pytest.approx(expected_rate, rel=1e-12)
    # The instantaneous projection would have said -v: a 1e-4 relative error.
    assert abs(geometry.range_rate_m_s + speed) > 1e-5 * speed


def test_geometry_error_is_caught_by_except_rf_error():
    from aerokit.comms.geometry import GeometryError

    assert issubclass(GeometryError, RfError)
    with pytest.raises(RfError):
        geometry_from_states(
            0.0,
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        )


# ---------------------------------------------------------------------------
# Layer A: the full legacy one-way links, end to end
# ---------------------------------------------------------------------------

def _static_geometry(range_m: float):
    """Two states separated along +x, at rest. Geometry only, no dynamics."""
    return geometry_from_states(
        0.0,
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [range_m, 0.0, 0.0, 0.0, 0.0, 0.0],
    )


def test_the_legacy_uplink_budget_is_reproduced_end_to_end():
    """Rome 2.4 m, 20 W, 14 GHz to a satellite of G/T 3 dB/K.

    Every term matches the frozen legacy CSV exactly except FSPL, which differs
    by the documented rounding bias and shifts C/N0 and Eb/N0 by the same amount.
    """
    tx = CommunicationTerminal(
        name="GS1 Rome",
        transmitter=Transmitter(
            antenna=ParabolicDishAntenna(diameter_m=2.4, aperture_efficiency=0.62),
            rf_power_w=20.0,
            feeder_loss_db=1.0,
        ),
    )
    rx = CommunicationTerminal(
        name="satellite receiver",
        receiver=Receiver(g_over_t_db_per_k_override=3.0),
    )
    link = CommunicationLink(
        name="Uplink: GS1 to GEO satellite",
        transmitter=tx,
        receiver=rx,
        frequency_hz=14.0e9,
        bandwidth_hz=36.0e6,
        bit_rate_bps=10.0e6,
        required_ebn0_db=7.0,
        # 1.5 dB of legacy fixed losses, of which 0.5 dB was the atmospheric
        # allowance -- now a propagation model, so it cannot be double-counted.
        losses=EngineeringLosses(
            pointing_loss_db=0.5, polarization_loss_db=0.3, other_loss_db=0.2
        ),
        propagation_models=(FixedAtmosphericAllowance(loss_db=0.5),),
    )

    result = evaluate_link(link, _static_geometry(LEGACY_UPLINK_RANGE_KM * 1e3))

    assert result.transmit_gain_dbi == pytest.approx(LEGACY_UPLINK_TX_GAIN_DBI, abs=1e-12)
    assert result.eirp_dbw == pytest.approx(LEGACY_UPLINK_EIRP_DBW, abs=1e-12)
    assert result.g_over_t_db_per_k == 3.0
    assert result.engineering_losses_db == pytest.approx(1.0, rel=1e-12)
    assert result.propagation.total_carrier_loss_db == pytest.approx(0.5, rel=1e-12, abs=0.0)
    # Legacy grouped all 1.5 dB together; the split must still total 1.5.
    assert result.engineering_losses_db + result.propagation.total_carrier_loss_db == (
        pytest.approx(1.5, rel=1e-12)
    )
    assert LEGACY_UPLINK_FSPL_DB - result.free_space_path_loss_db == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-12
    )
    assert result.cn0_dbhz - LEGACY_UPLINK_CN0_DBHZ == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-9
    )
    assert result.ebn0_db is not None
    assert result.ebn0_db - 14.076_865_037_041_813 == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-9
    )
    assert result.margin_db is not None and result.closes is True


def test_the_legacy_downlink_budget_is_reproduced_end_to_end():
    """46 dBW EIRP to Ankara 0.9 m, Tsys 150 K, 12 GHz."""
    tx = CommunicationTerminal(
        name="satellite transmitter",
        transmitter=Transmitter(eirp_dbw_override=46.0),
    )
    rx = CommunicationTerminal(
        name="GS2 Ankara",
        receiver=Receiver(
            antenna=ParabolicDishAntenna(diameter_m=0.9, aperture_efficiency=0.62),
            system_noise_temperature_k=150.0,
            feeder_loss_db=0.5,
            noise_temperature_reference="receiver_input",
        ),
    )
    link = CommunicationLink(
        name="Downlink: GEO satellite to GS2",
        transmitter=tx,
        receiver=rx,
        frequency_hz=12.0e9,
        bandwidth_hz=36.0e6,
        bit_rate_bps=10.0e6,
        required_ebn0_db=7.0,
        losses=EngineeringLosses(
            pointing_loss_db=0.5, polarization_loss_db=0.3, other_loss_db=0.2
        ),
        propagation_models=(FixedAtmosphericAllowance(loss_db=0.5),),
    )

    result = evaluate_link(link, _static_geometry(LEGACY_DOWNLINK_RANGE_KM * 1e3))

    assert result.receive_gain_dbi == pytest.approx(LEGACY_DOWNLINK_RX_GAIN_DBI, abs=1e-12)
    assert result.g_over_t_db_per_k == pytest.approx(LEGACY_DOWNLINK_G_OVER_T, abs=1e-12)
    assert result.cn0_dbhz - LEGACY_DOWNLINK_CN0_DBHZ == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-9
    )
    assert result.carrier_power_dbw is not None
    assert result.carrier_power_dbw - LEGACY_DOWNLINK_CARRIER_DBW == pytest.approx(
        LEGACY_FSPL_ROUNDING_BIAS_DB, abs=1e-9
    )


def test_the_result_keeps_enough_breakdown_to_audit_a_failure():
    """Not just 'margin = -2.1 dB'."""
    tx, rx = _terminals()
    link = CommunicationLink(
        name="audit",
        transmitter=tx,
        receiver=rx,
        frequency_hz=14e9,
        bandwidth_hz=36e6,
        bit_rate_bps=10e6,
        required_ebn0_db=7.0,
        propagation_models=(FixedAtmosphericAllowance(loss_db=0.5),),
    )
    payload = evaluate_link(link, _static_geometry(3.8e7)).as_dict()
    import json

    json.dumps(payload)
    for key in (
        "eirp_dbw",
        "g_over_t_db_per_k",
        "free_space_path_loss_db",
        "engineering_losses_db",
        "total_path_loss_db",
        "cn0_dbhz",
        "ebn0_db",
        "required_ebn0_db",
        "margin_db",
        "closes",
    ):
        assert key in payload, key
    assert payload["propagation"]["total_carrier_loss_db"] == pytest.approx(0.5)


def test_interference_is_combined_in_the_linear_domain_not_by_adding_db():
    tx, rx = _terminals()
    link = CommunicationLink(
        name="with interference",
        transmitter=tx,
        receiver=rx,
        frequency_hz=14e9,
        bandwidth_hz=36e6,
        bit_rate_bps=10e6,
        required_ebn0_db=7.0,
    )
    geometry = _static_geometry(3.8e7)
    clean = evaluate_link(link, geometry)
    degraded = evaluate_link(link, geometry, carrier_to_interference_db=20.0)

    assert degraded.cn0_with_interference_dbhz is not None
    # Interference can only make it worse.
    assert degraded.cn0_with_interference_dbhz < clean.cn0_dbhz
    # And the combination is the inverse-linear one, done at C/N.
    expected_cn = combine_inverse_ratios_db([clean.cn_db, 20.0])
    assert degraded.cn0_with_interference_dbhz == pytest.approx(
        expected_cn + (clean.cn0_dbhz - clean.cn_db), rel=1e-12
    )
    assert degraded.effective_cn0_dbhz == degraded.cn0_with_interference_dbhz


def test_a_link_without_a_bit_rate_has_no_margin_rather_than_a_wrong_one():
    tx, rx = _terminals()
    link = CommunicationLink(
        name="carrier only", transmitter=tx, receiver=rx,
        frequency_hz=14e9, bandwidth_hz=36e6,
    )
    result = evaluate_link(link, _static_geometry(3.8e7))
    assert result.ebn0_db is None
    assert result.margin_db is None
    assert result.closes is None
    assert math.isfinite(result.cn0_dbhz)
