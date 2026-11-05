# Copied from Sidera (sidera.communications.link.digital, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Digital link schemes: turning a carrier-to-noise ratio into a data rate.

`DigitalLinkScheme` is the seam between the RF layer and the waveform. Above it,
a link budget produces C/N0 and knows nothing about coding; below it, a scheme
decides what that C/N0 is worth in information bits per second. Keeping the two
apart is what lets a DVB-S2 ACM carrier, a fixed-rate CCSDS downlink and a
mission's own modem curves share one geometry and one propagation model.

Three schemes ship here:

===========================  ===============================================
`FixedRateDigitalLink`       one rate, one threshold: closed or not
`AdaptiveCodingAndModulation` walk a `ModcodTable`, take the best point
`ShannonBound`               the capacity ceiling, for reference only
===========================  ===============================================

`dvb_s2_acm()` is the migrated source's configuration of the second.

What "closed" means
-------------------
A scheme reports closure as a *state*, never an exception. An inaccessible or
too-weak epoch is a zero-rate sample, and a data-volume integral that silently
skipped those epochs would over-report the return. `DigitalLinkPerformance`
therefore always has a rate, which is 0.0 when the link is shut.

Screening metrics are labelled as screening
-------------------------------------------
`uncoded_ber_awgn` and `coding_gain_shifted_ber` are carried over from the
source, which was explicit that a coding-gain shift is not a decoder simulation.
That distinction is kept in the names and in the docstrings: they are for
sensitivity studies, and a link that must be trusted uses a threshold from a
`ModcodTable` instead.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from aerokit.comms.modcod import (
    DVB_S2_NORMAL_FRAME_TABLE,
    ModcodTable,
    esn0_from_cn0_db,
    select_best_modcod,
    symbol_rate_baud,
)
from aerokit.comms.rf import RfError, db_to_linear, ebn0_from_density_db

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "AdaptiveCodingAndModulation",
    "DigitalLinkPerformance",
    "DigitalLinkScheme",
    "FixedRateDigitalLink",
    "ShannonBound",
    "coded_channel_rate_bps",
    "coding_gain_shifted_ber",
    "dvb_s2_acm",
    "gap_to_shannon_db",
    "occupied_bandwidth_hz",
    "shannon_capacity_bps",
    "shannon_ebn0_limit_db",
    "uncoded_ber_awgn",
]


# =============================================================================
# 2.                            PERFORMANCE CONTRACT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DigitalLinkPerformance:
    """What one scheme achieves at one carrier-to-noise density.

    ``information_rate_bps`` is the net rate after coding -- the rate of useful
    bits, not of channel symbols -- and is 0.0 whenever ``closed`` is false.

    ``spectral_efficiency_bps_hz`` is ``information_rate_bps`` divided by the
    *occupied* bandwidth (``bandwidth_hz`` as passed to `DigitalLinkScheme.evaluate`,
    which already includes the pulse-shaping rolloff), so it means the same thing
    for every scheme and a Shannon-bound figure is a true ceiling for it.
    ``spectral_efficiency_bits_per_symbol`` is the modulation-and-coding figure
    referenced to the *symbol* rate instead -- the quantity a MODCOD table
    publishes -- and is ``None`` for a scheme with no symbol-rate concept.
    """

    scheme_name: str
    closed: bool
    mode_name: str
    information_rate_bps: float
    margin_db: float | None
    spectral_efficiency_bps_hz: float
    symbol_rate_baud: float | None = None
    required_esn0_db: float | None = None
    required_ebn0_db: float | None = None
    spectral_efficiency_bits_per_symbol: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        rate = float(self.information_rate_bps)
        if not math.isfinite(rate) or rate < 0.0:
            raise RfError(
                f"{self.scheme_name}: the information rate must be finite and "
                f"non-negative bit/s, got {rate!r}"
            )
        if not self.closed and rate != 0.0:
            raise RfError(
                f"{self.scheme_name}: a link that does not close carries no bits, "
                f"but the rate is {rate!r} bit/s"
            )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "scheme_name": self.scheme_name,
            "closed": self.closed,
            "mode_name": self.mode_name,
            "information_rate_bps": self.information_rate_bps,
            "margin_db": self.margin_db,
            "spectral_efficiency_bps_hz": self.spectral_efficiency_bps_hz,
            "symbol_rate_baud": self.symbol_rate_baud,
            "required_esn0_db": self.required_esn0_db,
            "required_ebn0_db": self.required_ebn0_db,
            "spectral_efficiency_bits_per_symbol": self.spectral_efficiency_bits_per_symbol,
            "diagnostics": self.diagnostics,
        }


# =============================================================================
# 3.                              SCHEME PROTOCOL
# =============================================================================

@runtime_checkable
class DigitalLinkScheme(Protocol):
    """A waveform's answer to "what rate does this C/N0 support?".

    Implementations must return a `DigitalLinkPerformance` for any finite
    ``cn0_dbhz``, including one far below threshold, where the answer is a
    closed link at zero rate rather than an exception.
    """

    @property
    def name(self) -> str:
        """A short label for the scheme, carried into its performance result."""
        ...

    def evaluate(
        self, cn0_dbhz: float, bandwidth_hz: float
    ) -> DigitalLinkPerformance:
        """The achievable rate and margin at this C/N0 and bandwidth."""
        ...


# =============================================================================
# 4.                         FIXED-RATE AND ACM SCHEMES
# =============================================================================

@dataclass(frozen=True, slots=True)
class FixedRateDigitalLink:
    """One rate and one Eb/N0 threshold. The link is open or it is not.

    The right scheme for a mission that flies a single coded mode: a CCSDS
    concatenated downlink, a fixed telemetry rate, a transponder with no ACM.
    The margin is ``Eb/N0 achieved - Eb/N0 required``, with the implementation
    margin folded into the requirement rather than hidden in the threshold.
    """

    information_rate_bps: float
    required_ebn0_db: float
    implementation_margin_db: float = 0.0
    mode_name: str = "fixed rate"
    name: str = "fixed-rate digital link"

    def __post_init__(self) -> None:
        rate = float(self.information_rate_bps)
        if not math.isfinite(rate) or rate <= 0.0:
            raise RfError(
                f"{self.name}: the information rate must be finite and positive, "
                f"got {self.information_rate_bps!r}"
            )
        if not math.isfinite(self.required_ebn0_db):
            raise RfError(f"{self.name}: the required Eb/N0 must be finite")
        margin = float(self.implementation_margin_db)
        if not math.isfinite(margin) or margin < 0.0:
            raise RfError(
                f"{self.name}: the implementation margin must be finite and "
                f"non-negative dB, got {self.implementation_margin_db!r}"
            )

    def evaluate(self, cn0_dbhz: float, bandwidth_hz: float) -> DigitalLinkPerformance:
        """Open at `information_rate_bps` if the margin closes, else shut at zero rate."""
        if not math.isfinite(cn0_dbhz):
            raise RfError(f"{self.name}: C/N0 must be finite, got {cn0_dbhz!r}")
        bandwidth = float(bandwidth_hz)
        if not math.isfinite(bandwidth) or bandwidth <= 0.0:
            raise RfError(
                f"{self.name}: the bandwidth must be finite and positive, got {bandwidth_hz!r}"
            )
        achieved = ebn0_from_density_db(cn0_dbhz, self.information_rate_bps)
        required = self.required_ebn0_db + self.implementation_margin_db
        margin = achieved - required
        closed = margin >= 0.0
        return DigitalLinkPerformance(
            scheme_name=self.name,
            closed=closed,
            mode_name=self.mode_name if closed else "none",
            information_rate_bps=self.information_rate_bps if closed else 0.0,
            margin_db=margin,
            spectral_efficiency_bps_hz=(
                self.information_rate_bps / bandwidth if closed else 0.0
            ),
            required_ebn0_db=required,
            diagnostics={"achieved_ebn0_db": achieved},
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "kind": "fixed_rate",
            "name": self.name,
            "information_rate_bps": self.information_rate_bps,
            "required_ebn0_db": self.required_ebn0_db,
            "implementation_margin_db": self.implementation_margin_db,
        }


@dataclass(frozen=True, slots=True)
class AdaptiveCodingAndModulation:
    """Walk a `ModcodTable` and take the most efficient point that closes.

    The table is an input, so this is not a DVB-S2 class. `dvb_s2_acm()` builds
    the migrated source's configuration of it; a CCSDS ladder or a modem's
    measured curves go in the same slot.

    The comparison is done in Es/N0, referenced to the symbol rate
    ``R_s = B / (1 + alpha)``, because that is the quantity a published
    threshold is quoted against.

    Reference: EN 302 307-1 (2014): Normal FECFRAME performance at quasi-error-free operation
    (checked against a secondary source) [SIDERA-ALG-COM-007].
    """

    rolloff_factor: float
    table: ModcodTable = DVB_S2_NORMAL_FRAME_TABLE
    implementation_margin_db: float = 1.0
    name: str = "adaptive coding and modulation"

    def __post_init__(self) -> None:
        # Validated once here so an out-of-range rolloff fails at configuration
        # time rather than on the first sample of a thousand-epoch pass.
        symbol_rate_baud(1.0, self.rolloff_factor)

    def evaluate(self, cn0_dbhz: float, bandwidth_hz: float) -> DigitalLinkPerformance:
        """The most efficient `table` entry that closes at this C/N0 and bandwidth."""
        esn0 = esn0_from_cn0_db(cn0_dbhz, bandwidth_hz, self.rolloff_factor)
        selection = select_best_modcod(
            esn0,
            bandwidth_hz,
            self.rolloff_factor,
            table=self.table,
            implementation_margin_db=self.implementation_margin_db,
        )
        # `selection.spectral_efficiency_bps_hz` is the MODCOD table's own
        # figure, referenced to the *symbol* rate (bits/symbol), not to the
        # occupied bandwidth. Dividing the net rate by `bandwidth_hz` instead
        # gives a spectral efficiency that means the same thing as
        # `FixedRateDigitalLink` and `ShannonBound` report, so the three are
        # comparable -- an ACM link can never show as "more efficient" than
        # the Shannon bound for the same channel.
        efficiency_bps_hz = selection.net_information_rate_bps / float(bandwidth_hz)
        return DigitalLinkPerformance(
            scheme_name=self.name,
            closed=selection.closed,
            mode_name=selection.mode_name,
            information_rate_bps=selection.net_information_rate_bps,
            margin_db=selection.link_margin_db,
            spectral_efficiency_bps_hz=efficiency_bps_hz,
            symbol_rate_baud=selection.symbol_rate_baud,
            required_esn0_db=(
                None if selection.selected is None else selection.selected.required_esn0_db
            ),
            spectral_efficiency_bits_per_symbol=selection.spectral_efficiency_bps_hz,
            diagnostics={
                "available_esn0_db": esn0,
                "table_name": self.table.name,
                "table_standardized": self.table.standardized,
            },
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "kind": "adaptive_coding_and_modulation",
            "name": self.name,
            "rolloff_factor": self.rolloff_factor,
            "implementation_margin_db": self.implementation_margin_db,
            "table": {
                "name": self.table.name,
                "source": self.table.source,
                "standardized": self.table.standardized,
                "entries": len(self.table),
            },
        }


# =============================================================================
# 5.                             DVB-S2 ACM FACTORY
# =============================================================================

def dvb_s2_acm(
    rolloff_factor: float, implementation_margin_db: float = 1.0
) -> AdaptiveCodingAndModulation:
    """The migrated source's DVB-S2 ACM configuration.

    The normal-FECFRAME table from EN 302 307-1 with a 1 dB implementation
    margin, which is what the source used by default.

    Reference: EN 302 307-1 (2014): Normal FECFRAME performance at quasi-error-free operation
    (checked against a secondary source) [SIDERA-ALG-COM-007].
    """
    return AdaptiveCodingAndModulation(
        rolloff_factor=rolloff_factor,
        table=DVB_S2_NORMAL_FRAME_TABLE,
        implementation_margin_db=implementation_margin_db,
        name="DVB-S2 ACM",
    )


# =============================================================================
# 6.                               SHANNON BOUND
# =============================================================================

@dataclass(frozen=True, slots=True)
class ShannonBound:
    """The AWGN capacity ceiling, ``C = B log2(1 + S/N)``.

    **A bound, not a waveform.** No modem reaches it, and nothing here models
    coding, framing or acquisition. It exists so an achievable rate can be
    reported next to the ceiling it is being compared against, which is the
    only honest way to quote a "gap to Shannon".

    ``closed`` is true whenever the capacity is positive, which it always is for
    a finite C/N0. That is the correct statement about a bound and a reminder
    that it is not a link.
    """

    name: str = "Shannon bound (not achievable)"

    def evaluate(self, cn0_dbhz: float, bandwidth_hz: float) -> DigitalLinkPerformance:
        """The AWGN capacity ceiling at this C/N0 and bandwidth. Not achievable."""
        cn_db = float(cn0_dbhz) - 10.0 * math.log10(float(bandwidth_hz))
        capacity = shannon_capacity_bps(bandwidth_hz, cn_db)
        return DigitalLinkPerformance(
            scheme_name=self.name,
            closed=capacity > 0.0,
            mode_name="capacity",
            information_rate_bps=capacity,
            margin_db=None,
            spectral_efficiency_bps_hz=capacity / float(bandwidth_hz),
            diagnostics={"cn_db": cn_db, "achievable": False},
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {"kind": "shannon_bound", "name": self.name, "achievable": False}


# ---------------------------------------------------------------------------
# Diagnostic metrics
# ---------------------------------------------------------------------------


# =============================================================================
# 7.                        RATE, BANDWIDTH AND CAPACITY
# =============================================================================

def coded_channel_rate_bps(information_rate_bps: float, code_rate: float) -> float:
    """``R_c = R_b / r``: the channel rate an inner code of rate ``r`` produces."""
    rate = float(code_rate)
    if not math.isfinite(rate) or not 0.0 < rate <= 1.0:
        raise RfError(f"the code rate must lie in (0, 1], got {code_rate!r}")
    information = float(information_rate_bps)
    if not math.isfinite(information) or information <= 0.0:
        raise RfError(
            f"the information rate must be finite and positive, got {information_rate_bps!r}"
        )
    return information / rate


def occupied_bandwidth_hz(
    information_rate_bps: float,
    code_rate: float,
    bits_per_symbol: float,
    rolloff_factor: float,
) -> float:
    """``B = R_s (1 + alpha)`` for the symbol rate the coded stream implies.

    An *estimate*: it accounts for coding and pulse shaping and for nothing
    else -- no pilots, no framing overhead, no guard band.
    """
    bits = float(bits_per_symbol)
    if not math.isfinite(bits) or bits <= 0.0:
        raise RfError(f"bits per symbol must be finite and positive, got {bits_per_symbol!r}")
    rolloff = float(rolloff_factor)
    if not math.isfinite(rolloff) or rolloff < 0.0:
        raise RfError(
            f"the rolloff factor must be finite and non-negative, got {rolloff_factor!r}"
        )
    symbol_rate = coded_channel_rate_bps(information_rate_bps, code_rate) / bits
    return symbol_rate * (1.0 + rolloff)


def shannon_capacity_bps(bandwidth_hz: float, cn_db: float) -> float:
    """Shannon-Hartley capacity ``C = B log2(1 + S/N)``."""
    bandwidth = float(bandwidth_hz)
    if not math.isfinite(bandwidth) or bandwidth <= 0.0:
        raise RfError(f"bandwidth must be finite and positive, got {bandwidth_hz!r}")
    if not math.isfinite(cn_db):
        raise RfError(f"C/N must be finite, got {cn_db!r}")
    return bandwidth * math.log2(1.0 + db_to_linear(cn_db))


def shannon_ebn0_limit_db(spectral_efficiency_bps_hz: float) -> float:
    """The AWGN Eb/N0 floor for a spectral efficiency: ``(2^eta - 1) / eta``.

    As ``eta`` tends to zero this tends to ln 2, the -1.59 dB Shannon limit. No
    code of that efficiency can work below this Eb/N0, whatever its complexity.
    """
    eta = float(spectral_efficiency_bps_hz)
    if not math.isfinite(eta) or eta <= 0.0:
        raise RfError(
            f"spectral efficiency must be finite and positive, got "
            f"{spectral_efficiency_bps_hz!r}"
        )
    return 10.0 * math.log10((2.0**eta - 1.0) / eta)


def gap_to_shannon_db(achieved_ebn0_db: float, spectral_efficiency_bps_hz: float) -> float:
    """How far above the AWGN floor a scheme operates, in dB.

    Positive is the only physical answer for a real code; a negative gap means
    either the efficiency or the Eb/N0 is wrong.
    """
    return float(achieved_ebn0_db) - shannon_ebn0_limit_db(spectral_efficiency_bps_hz)


def uncoded_ber_awgn(ebn0_db: float, modulation: str = "QPSK") -> float:
    """An **uncoded** AWGN bit-error-rate estimate. For screening only.

    ``Pb = 0.5 erfc(sqrt(Eb/N0))`` is exact for coherent BPSK and Gray-coded
    QPSK. The 8PSK and 16QAM branches are the usual high-SNR engineering
    approximations and are accurate only well above threshold. None of these
    describes a coded link; use a `ModcodTable` threshold for that.
    """
    if not math.isfinite(ebn0_db):
        raise RfError(f"Eb/N0 must be finite, got {ebn0_db!r}")
    gamma_b = db_to_linear(ebn0_db)
    name = modulation.strip().upper().replace("-", "").replace("_", "")

    if name in {"BPSK", "QPSK", "OQPSK", "4QAM"}:
        pb = 0.5 * math.erfc(math.sqrt(gamma_b))
    elif name == "8PSK":
        m = 8.0
        k = math.log2(m)
        pb = (1.0 / k) * math.erfc(math.sqrt(k * gamma_b) * math.sin(math.pi / m))
    elif name == "16QAM":
        m = 16.0
        k = math.log2(m)
        pb = (
            (4.0 / k)
            * (1.0 - 1.0 / math.sqrt(m))
            * 0.5
            * math.erfc(math.sqrt(3.0 * k * gamma_b / (2.0 * (m - 1.0))))
        )
    else:
        raise RfError(
            f"no uncoded BER curve for modulation {modulation!r}; this screening "
            "helper covers BPSK, QPSK, 8PSK and 16QAM"
        )
    return min(max(pb, 0.0), 1.0)


def coding_gain_shifted_ber(
    ebn0_db: float, coding_gain_db: float, modulation: str = "QPSK"
) -> float:
    """`uncoded_ber_awgn` evaluated at ``Eb/N0 + G``. **Not a decoder model.**

    Representing forward error correction as a constant dB shift ignores the
    waterfall shape, the error floor and the block length -- everything that
    distinguishes one code from another. It is a sensitivity tool. The source
    study said so and the name says so here.
    """
    if not math.isfinite(coding_gain_db):
        raise RfError(f"the coding gain must be finite, got {coding_gain_db!r}")
    return uncoded_ber_awgn(float(ebn0_db) + float(coding_gain_db), modulation)
