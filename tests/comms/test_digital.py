# Copied from Sidera (tests/communications/test_communications_digital.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""MODCOD ladders, digital link schemes, and returned data volume.

**Layer A, legacy parity.** All 28 DVB-S2 normal-FECFRAME thresholds and
spectral efficiencies, the symbol-rate and Es/N0 conversions, and the selection
outcomes at representative Es/N0, pinned to the source repository at revision
91225ca6a190c164a0a0c2a53f1f855236b00de8.

**Layer B, analytic physics.** The symbol-rate identity, the Shannon floor at
its known limits, the relationship between Es/N0 and Eb/N0, and data-volume
integrals whose exact value is available in closed form.

**Layer C, the trajectory capability.** A rate history integrated to a data
volume, the three integration rules ordered as their definitions require, and a
pass that is visible throughout but closes for only part of it.
"""

from __future__ import annotations

import math

import pytest

from aerokit.comms import (
    DVB_S2_NORMAL_FRAME_MODCODS,
    DVB_S2_NORMAL_FRAME_TABLE,
    AdaptiveCodingAndModulation,
    FixedRateDigitalLink,
    Modcod,
    ModcodTable,
    RfError,
    ShannonBound,
    coded_channel_rate_bps,
    coding_gain_shifted_ber,
    custom_modcod_table,
    dvb_s2_acm,
    esn0_from_cn0_db,
    gap_to_shannon_db,
    integrate_data_volume_bits,
    occupied_bandwidth_hz,
    select_best_modcod,
    shannon_capacity_bps,
    shannon_ebn0_limit_db,
    symbol_rate_baud,
    uncoded_ber_awgn,
)

TRANSPONDER_BANDWIDTH_HZ = 36.0e6
ROLLOFF = 0.20

# The full published ladder, in table order: (name, spectral efficiency,
# required Es/N0 in dB). Written out rather than derived so a coefficient that
# moved during migration fails here and not silently in a throughput number.
EXPECTED_LADDER: tuple[tuple[str, float, float], ...] = (
    ("QPSK 1/4", 0.490243, -2.35),
    ("QPSK 1/3", 0.656448, -1.24),
    ("QPSK 2/5", 0.789412, -0.30),
    ("QPSK 1/2", 0.988858, 1.00),
    ("QPSK 3/5", 1.188304, 2.23),
    ("QPSK 2/3", 1.322253, 3.10),
    ("QPSK 3/4", 1.487473, 4.03),
    ("QPSK 4/5", 1.587196, 4.68),
    ("QPSK 5/6", 1.654663, 5.18),
    ("QPSK 8/9", 1.766451, 6.20),
    ("QPSK 9/10", 1.788612, 6.42),
    ("8PSK 3/5", 1.779991, 5.50),
    ("8PSK 2/3", 1.980636, 6.62),
    ("8PSK 3/4", 2.228124, 7.91),
    ("8PSK 5/6", 2.478562, 9.35),
    ("8PSK 8/9", 2.646012, 10.69),
    ("8PSK 9/10", 2.679207, 10.98),
    ("16APSK 2/3", 2.637201, 8.97),
    ("16APSK 3/4", 2.966728, 10.21),
    ("16APSK 4/5", 3.165623, 11.03),
    ("16APSK 5/6", 3.300184, 11.61),
    ("16APSK 8/9", 3.523143, 12.89),
    ("16APSK 9/10", 3.567342, 13.13),
    ("32APSK 3/4", 3.703295, 12.73),
    ("32APSK 4/5", 3.951571, 13.64),
    ("32APSK 5/6", 4.119540, 14.28),
    ("32APSK 8/9", 4.397854, 15.69),
    ("32APSK 9/10", 4.453027, 16.05),
)


# ---------------------------------------------------------------------------
# Layer A -- parity with the migrated source
# ---------------------------------------------------------------------------


def test_the_dvb_s2_ladder_is_reproduced_entry_for_entry() -> None:
    assert len(DVB_S2_NORMAL_FRAME_MODCODS) == 28
    assert len(EXPECTED_LADDER) == 28
    for modcod, (name, efficiency, threshold) in zip(
        DVB_S2_NORMAL_FRAME_MODCODS, EXPECTED_LADDER, strict=True
    ):
        assert modcod.name == name
        assert modcod.spectral_efficiency_bps_hz == efficiency
        assert modcod.required_esn0_db == threshold


def test_the_ladder_carries_its_provenance() -> None:
    assert DVB_S2_NORMAL_FRAME_TABLE.standardized is True
    assert "EN 302 307-1" in DVB_S2_NORMAL_FRAME_TABLE.source
    assert "64 800" in DVB_S2_NORMAL_FRAME_TABLE.source


def test_symbol_rate_and_esn0_conversion_match_the_source() -> None:
    assert symbol_rate_baud(TRANSPONDER_BANDWIDTH_HZ, ROLLOFF) == 30_000_000.0
    assert esn0_from_cn0_db(80.0, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF) == pytest.approx(
        5.228787452803374, rel=0.0, abs=1e-12
    )


@pytest.mark.parametrize(
    ("esn0_db", "expected_mode", "expected_efficiency", "expected_rate_bps"),
    [
        (-3.0, None, 0.0, 0.0),
        (1.0, "QPSK 2/5", 0.789412, 23_682_360.0),
        (6.0, "QPSK 4/5", 1.587196, 47_615_880.0),
        (10.0, "16APSK 2/3", 2.637201, 79_116_030.0),
        (14.0, "32APSK 3/4", 3.703295, 111_098_850.0),
        (20.0, "32APSK 9/10", 4.453027, 133_590_809.99999999),
    ],
)
def test_modcod_selection_matches_the_source(
    esn0_db: float,
    expected_mode: str | None,
    expected_efficiency: float,
    expected_rate_bps: float,
) -> None:
    selection = select_best_modcod(
        esn0_db, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF, implementation_margin_db=1.0
    )
    if expected_mode is None:
        assert selection.selected is None
        assert selection.closed is False
        assert selection.link_margin_db is None
    else:
        assert selection.selected is not None
        assert selection.selected.name == expected_mode
    assert selection.spectral_efficiency_bps_hz == pytest.approx(
        expected_efficiency, rel=0.0, abs=1e-15
    )
    assert selection.net_information_rate_bps == pytest.approx(
        expected_rate_bps, rel=1e-15
    )


def test_a_link_that_closes_nowhere_is_a_result_not_an_exception() -> None:
    """The source's structural "no supported mode" outcome is preserved."""
    selection = select_best_modcod(-20.0, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF)
    assert selection.closed is False
    assert selection.mode_name == "none"
    assert selection.net_information_rate_bps == 0.0
    # The symbol rate is still reported: it is a property of the carrier, not
    # of whether anything closes on it.
    assert selection.symbol_rate_baud == 30_000_000.0


def test_shannon_and_ber_helpers_match_the_source() -> None:
    assert shannon_capacity_bps(TRANSPONDER_BANDWIDTH_HZ, 10.0) == pytest.approx(
        124_539_538.2709427, rel=0.0, abs=1e-6
    )
    assert shannon_ebn0_limit_db(2.0) == pytest.approx(
        1.7609125905568124, rel=0.0, abs=1e-12
    )
    assert uncoded_ber_awgn(10.0, "QPSK") == pytest.approx(
        3.872108215522038e-06, rel=1e-13, abs=0.0
    )
    assert uncoded_ber_awgn(10.0, "8PSK") == pytest.approx(
        0.0010113953207128905, rel=1e-13, abs=0.0
    )
    assert uncoded_ber_awgn(10.0, "16QAM") == pytest.approx(
        0.0017541506178927245, rel=1e-13, abs=0.0
    )


# ---------------------------------------------------------------------------
# Layer B -- the algebra
# ---------------------------------------------------------------------------


def test_selection_is_by_efficiency_not_by_table_order() -> None:
    """QPSK 9/10 beats 8PSK 3/5, and sits above it in the table.

    A scan that kept the last passing row would return 8PSK 3/5 at 1.780
    bit/s/Hz where QPSK 9/10 delivers 1.789 for a lower threshold. The two rows
    are the reason selection compares efficiency rather than position.
    """
    # usable = 7.5 - 1.0 = 6.5 dB, which clears QPSK 9/10 (6.42) and 8PSK 3/5
    # (5.50) but not 8PSK 2/3 (6.62).
    selection = select_best_modcod(
        7.5, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF, implementation_margin_db=1.0
    )
    assert selection.selected is not None
    assert selection.selected.name == "QPSK 9/10"
    assert selection.spectral_efficiency_bps_hz > 1.779991


def test_the_implementation_margin_shifts_the_whole_ladder() -> None:
    zero = select_best_modcod(
        10.0, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF, implementation_margin_db=0.0
    )
    one = select_best_modcod(
        11.0, TRANSPONDER_BANDWIDTH_HZ, ROLLOFF, implementation_margin_db=1.0
    )
    # Raising both the available Es/N0 and the margin by 1 dB is a no-op.
    assert zero.mode_name == one.mode_name
    assert zero.link_margin_db == pytest.approx(one.link_margin_db)


def test_the_symbol_rate_identity_holds_across_rolloffs() -> None:
    for rolloff in (0.0, 0.05, 0.20, 0.25, 0.35):
        rate = symbol_rate_baud(TRANSPONDER_BANDWIDTH_HZ, rolloff)
        assert rate * (1.0 + rolloff) == pytest.approx(
            TRANSPONDER_BANDWIDTH_HZ, rel=1e-15
        )
        # Es/N0 referenced to the symbol rate exceeds the bandwidth-referenced
        # C/N by exactly 10 log10(1 + alpha).
        esn0 = esn0_from_cn0_db(80.0, TRANSPONDER_BANDWIDTH_HZ, rolloff)
        cn = 80.0 - 10.0 * math.log10(TRANSPONDER_BANDWIDTH_HZ)
        assert esn0 - cn == pytest.approx(10.0 * math.log10(1.0 + rolloff), abs=1e-12)


def test_the_shannon_floor_approaches_minus_1_59_db() -> None:
    """``(2^eta - 1)/eta`` tends to ln 2 as the efficiency tends to zero.

    The tolerance is the first-order term of the expansion, not a fudge: the
    ratio is ``ln2 (1 + eta ln2 / 2 + ...)``, so at eta = 1e-4 the floor sits
    about ``10 log10(1 + 3.5e-5)`` = 1.5e-4 dB above the limit. Going much
    smaller makes it worse, not better -- ``2^eta - 1`` loses its significant
    digits to cancellation below about eta = 1e-7.
    """
    assert shannon_ebn0_limit_db(1e-4) == pytest.approx(
        10.0 * math.log10(math.log(2.0)), abs=2e-4
    )
    assert 10.0 * math.log10(math.log(2.0)) == pytest.approx(-1.5917, abs=1e-4)
    # And it is monotone: a more efficient scheme needs more energy per bit.
    limits = [shannon_ebn0_limit_db(eta) for eta in (0.5, 1.0, 2.0, 4.0, 8.0)]
    assert limits == sorted(limits)


def test_gap_to_shannon_is_positive_for_a_real_modcod() -> None:
    """DVB-S2 QPSK 1/2 operates above its own Shannon floor.

    Eb/N0 = Es/N0 - 10 log10(eta) for a scheme of spectral efficiency eta
    referenced to the symbol rate.
    """
    modcod = next(m for m in DVB_S2_NORMAL_FRAME_MODCODS if m.name == "QPSK 1/2")
    ebn0 = modcod.required_esn0_db - 10.0 * math.log10(
        modcod.spectral_efficiency_bps_hz
    )
    gap = gap_to_shannon_db(ebn0, modcod.spectral_efficiency_bps_hz)
    assert gap > 0.0
    # A modern LDPC code sits roughly 1 dB from the bound; anything under 0 dB
    # would mean the table or the conversion is wrong.
    assert gap < 3.0


def test_coded_rate_and_occupied_bandwidth_are_consistent() -> None:
    information = 10.0e6
    channel = coded_channel_rate_bps(information, 0.5)
    assert channel == pytest.approx(20.0e6)
    # QPSK carries 2 bit/symbol, so 20 Mbit/s coded is 10 Mbaud, occupying
    # 12 MHz at a rolloff of 0.2.
    assert occupied_bandwidth_hz(information, 0.5, 2.0, 0.2) == pytest.approx(12.0e6)


def test_a_coding_gain_shift_is_exactly_a_shift() -> None:
    assert coding_gain_shifted_ber(6.0, 4.0, "QPSK") == pytest.approx(
        uncoded_ber_awgn(10.0, "QPSK"), rel=0.0, abs=0.0
    )


def test_the_ber_screening_helper_refuses_a_modulation_it_has_no_curve_for() -> None:
    with pytest.raises(RfError, match="no uncoded BER curve"):
        uncoded_ber_awgn(10.0, "256APSK")


# ---------------------------------------------------------------------------
# The schemes
# ---------------------------------------------------------------------------


def test_a_fixed_rate_link_opens_and_shuts_at_its_threshold() -> None:
    scheme = FixedRateDigitalLink(
        information_rate_bps=2.0e6, required_ebn0_db=3.0, mode_name="CCSDS r=1/2"
    )
    # Eb/N0 = C/N0 - 10 log10(Rb); 10 log10(2e6) = 63.0103 dB.
    threshold_cn0 = 3.0 + 10.0 * math.log10(2.0e6)

    above = scheme.evaluate(threshold_cn0 + 2.0, 4.0e6)
    assert above.closed is True
    assert above.information_rate_bps == 2.0e6
    assert above.margin_db == pytest.approx(2.0, abs=1e-12)
    assert above.mode_name == "CCSDS r=1/2"

    below = scheme.evaluate(threshold_cn0 - 2.0, 4.0e6)
    assert below.closed is False
    assert below.information_rate_bps == 0.0
    assert below.margin_db == pytest.approx(-2.0, abs=1e-12)
    assert below.mode_name == "none"


@pytest.mark.parametrize("bandwidth_hz", [0.0, -4.0e6, math.inf, math.nan])
def test_a_fixed_rate_link_refuses_a_non_positive_or_non_finite_bandwidth(
    bandwidth_hz: float,
) -> None:
    scheme = FixedRateDigitalLink(information_rate_bps=2.0e6, required_ebn0_db=3.0)
    with pytest.raises(RfError, match="bandwidth"):
        scheme.evaluate(80.0, bandwidth_hz)


def test_a_scheme_far_below_threshold_returns_a_result_not_an_exception() -> None:
    for scheme in (
        FixedRateDigitalLink(information_rate_bps=1.0e6, required_ebn0_db=3.0),
        dvb_s2_acm(rolloff_factor=0.2),
    ):
        performance = scheme.evaluate(-200.0, TRANSPONDER_BANDWIDTH_HZ)
        assert performance.closed is False
        assert performance.information_rate_bps == 0.0


def test_dvb_s2_acm_agrees_with_the_selection_it_wraps() -> None:
    scheme = dvb_s2_acm(rolloff_factor=ROLLOFF, implementation_margin_db=1.0)
    cn0 = 10.0 + 10.0 * math.log10(symbol_rate_baud(TRANSPONDER_BANDWIDTH_HZ, ROLLOFF))
    performance = scheme.evaluate(cn0, TRANSPONDER_BANDWIDTH_HZ)
    assert performance.mode_name == "16APSK 2/3"
    assert performance.information_rate_bps == pytest.approx(79_116_030.0, rel=1e-12)
    assert performance.required_esn0_db == 8.97
    assert performance.diagnostics["table_standardized"] is True


def test_spectral_efficiency_means_rate_over_occupied_bandwidth_for_every_scheme() -> None:
    """`spectral_efficiency_bps_hz` must mean the same thing for every scheme.

    Before this, ACM reported the MODCOD table's own bits/symbol figure
    (referenced to ``Rs = B / (1 + alpha)``) under this name, which reads
    ``(1 + alpha)`` times higher than the bandwidth-referenced figure
    `FixedRateDigitalLink` and `ShannonBound` report for the same field --
    comparing them directly could make an ACM link look more efficient than
    the Shannon bound for the same channel, which is not physically possible.
    """
    cn0 = 10.0 + 10.0 * math.log10(TRANSPONDER_BANDWIDTH_HZ)
    acm = dvb_s2_acm(rolloff_factor=ROLLOFF).evaluate(cn0, TRANSPONDER_BANDWIDTH_HZ)
    assert acm.closed
    assert acm.spectral_efficiency_bps_hz == pytest.approx(
        acm.information_rate_bps / TRANSPONDER_BANDWIDTH_HZ, rel=1e-12
    )
    # The MODCOD table's own bits/symbol figure is still available, under its
    # own name, and is the larger of the two by (1 + rolloff).
    assert acm.spectral_efficiency_bits_per_symbol == pytest.approx(
        acm.spectral_efficiency_bps_hz * (1.0 + ROLLOFF), rel=1e-12
    )


def test_fixed_rate_and_shannon_report_no_symbol_rate_concept() -> None:
    """Neither scheme takes a rolloff, so neither has a bits/symbol figure."""
    fixed = FixedRateDigitalLink(information_rate_bps=2.0e6, required_ebn0_db=3.0).evaluate(
        80.0, 4.0e6
    )
    bound = ShannonBound().evaluate(80.0, 4.0e6)
    assert fixed.spectral_efficiency_bits_per_symbol is None
    assert bound.spectral_efficiency_bits_per_symbol is None


def test_a_custom_table_is_marked_as_not_standardized() -> None:
    table = custom_modcod_table(
        "mission modem",
        [
            Modcod("BPSK", 0.5, "1/2", 0.45, -1.0),
            Modcod("QPSK", 0.5, "1/2", 0.95, 2.0),
        ],
        source="modem vendor measured curves, 2026 acceptance test",
    )
    assert table.standardized is False
    scheme = AdaptiveCodingAndModulation(rolloff_factor=0.35, table=table)
    performance = scheme.evaluate(
        3.0 + 10.0 * math.log10(symbol_rate_baud(1.0e6, 0.35)), 1.0e6
    )
    assert performance.mode_name == "QPSK 1/2"
    assert performance.diagnostics["table_standardized"] is False


def test_a_table_must_declare_where_its_thresholds_came_from() -> None:
    with pytest.raises(RfError, match="where its thresholds come from"):
        ModcodTable(name="anonymous", modcods=DVB_S2_NORMAL_FRAME_MODCODS, source="  ")
    with pytest.raises(RfError, match="duplicate operating point"):
        ModcodTable(
            name="doubled",
            modcods=(
                Modcod("QPSK", 0.5, "1/2", 0.95, 2.0),
                Modcod("QPSK", 0.5, "1/2", 1.05, 2.5),
            ),
            source="test",
        )


def test_the_shannon_bound_says_it_is_not_achievable() -> None:
    bound = ShannonBound()
    performance = bound.evaluate(
        10.0 + 10.0 * math.log10(TRANSPONDER_BANDWIDTH_HZ), TRANSPONDER_BANDWIDTH_HZ
    )
    assert performance.diagnostics["achievable"] is False
    assert performance.information_rate_bps == pytest.approx(
        shannon_capacity_bps(TRANSPONDER_BANDWIDTH_HZ, 10.0), rel=1e-12
    )
    # And no real MODCOD beats it at the same C/N0.
    acm = dvb_s2_acm(rolloff_factor=ROLLOFF)
    achieved = acm.evaluate(
        10.0 + 10.0 * math.log10(TRANSPONDER_BANDWIDTH_HZ), TRANSPONDER_BANDWIDTH_HZ
    )
    assert achieved.information_rate_bps < performance.information_rate_bps


def test_a_closed_link_cannot_be_given_a_nonzero_rate() -> None:
    from aerokit.comms import DigitalLinkPerformance

    with pytest.raises(RfError, match="carries no bits"):
        DigitalLinkPerformance(
            scheme_name="broken",
            closed=False,
            mode_name="none",
            information_rate_bps=1.0e6,
            margin_db=-3.0,
            spectral_efficiency_bps_hz=0.0,
        )


# ---------------------------------------------------------------------------
# Layer C -- data volume
# ---------------------------------------------------------------------------


def test_a_constant_rate_integrates_to_rate_times_duration() -> None:
    epochs = [0.0, 10.0, 20.0, 30.0]
    rates = [2.0e6] * 4
    for method in ("held_previous_sample", "trapezoidal", "held_lower"):
        assert integrate_data_volume_bits(epochs, rates, method) == pytest.approx(
            2.0e6 * 30.0, rel=1e-15
        )


def test_the_three_integration_rules_are_ordered_as_their_definitions_require() -> None:
    """For a rising rate: held_lower <= trapezoidal <= held_previous is false.

    On a *rising* history the left-held value is the smaller one, so
    ``held_previous_sample`` equals ``held_lower`` and both sit below the
    trapezoid. On a falling history the left-held value is the larger one. The
    invariant that holds either way is that ``held_lower`` never exceeds the
    other two, which is what makes it a bound.
    """
    epochs = [0.0, 1.0, 2.0, 3.0]
    rising = [0.0, 1.0, 2.0, 3.0]
    falling = list(reversed(rising))

    for rates in (rising, falling):
        lower = integrate_data_volume_bits(epochs, rates, "held_lower")
        trapezoid = integrate_data_volume_bits(epochs, rates, "trapezoidal")
        held = integrate_data_volume_bits(epochs, rates, "held_previous_sample")
        assert lower <= trapezoid
        assert lower <= held

    # On this symmetric ramp the exact area is 4.5 and the trapezoid is exact.
    assert integrate_data_volume_bits(epochs, rising, "trapezoidal") == pytest.approx(
        4.5, rel=1e-15, abs=0.0
    )
    assert integrate_data_volume_bits(
        epochs, rising, "held_previous_sample"
    ) == pytest.approx(3.0, rel=1e-15, abs=0.0)
    assert integrate_data_volume_bits(epochs, rising, "held_lower") == pytest.approx(
        3.0, rel=1e-15, abs=0.0
    )
    assert integrate_data_volume_bits(
        epochs, falling, "held_previous_sample"
    ) == pytest.approx(6.0, rel=1e-15, abs=0.0)


def test_a_single_sample_spans_no_interval_and_returns_zero() -> None:
    assert integrate_data_volume_bits([5.0], [1.0e9]) == 0.0


def test_an_unknown_method_is_refused_even_with_a_single_sample():
    """The method is validated before the sample-count short-circuit.

    A single-sample call used to return 0.0 for *any* ``method`` string,
    valid or not, because the "fewer than two samples" early return ran
    before the method was ever checked.
    """
    with pytest.raises(RfError, match="unknown data-volume integration method"):
        integrate_data_volume_bits([5.0], [1.0e9], "simpson")  # type: ignore[arg-type]


def test_a_data_volume_refuses_an_unordered_or_negative_history() -> None:
    with pytest.raises(RfError, match="strictly increasing"):
        integrate_data_volume_bits([0.0, 10.0, 5.0], [1.0, 1.0, 1.0])
    with pytest.raises(RfError, match="cannot be negative"):
        integrate_data_volume_bits([0.0, 10.0], [1.0, -1.0])
    with pytest.raises(RfError, match="same length"):
        integrate_data_volume_bits([0.0, 10.0], [1.0])
    with pytest.raises(RfError, match="unknown data-volume integration method"):
        integrate_data_volume_bits([0.0, 1.0], [1.0, 1.0], "simpson")  # type: ignore[arg-type]


def test_a_dropout_removes_exactly_its_own_interval() -> None:
    """A held-sample integral over a pass with one shut interval."""
    epochs = [0.0, 100.0, 200.0, 300.0, 400.0]
    rates = [1.0e6, 1.0e6, 0.0, 1.0e6, 1.0e6]
    # Three of the four intervals carry 1 Mbit/s for 100 s; the interval that
    # starts at the shut sample carries nothing.
    assert integrate_data_volume_bits(
        epochs, rates, "held_previous_sample"
    ) == pytest.approx(3.0e8, rel=1e-15)
