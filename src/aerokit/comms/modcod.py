# Copied from Sidera (sidera.communications.link.modcod, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Modulation-and-coding ladders, and selecting a point on one.

A MODCOD is one operating point: a constellation, an inner code rate, the net
spectral efficiency that combination delivers, and the Es/N0 it needs to reach
quasi-error-free operation. A *ladder* is an ordered set of them; adaptive
coding and modulation means walking the ladder and taking the most efficient
point the channel currently supports.

Nothing here is specific to DVB-S2 except `DVB_S2_NORMAL_FRAME_TABLE`, which is
one `ModcodTable` among however many a mission needs. A CCSDS ladder, a deep-space
coding table or a modem vendor's measured curves are the same structure with
different numbers, which is the point of keeping the table separate from the
selection rule.

Provenance
----------
The DVB-S2 figures are the published ETSI EN 302 307-1 reference values for the
normal FECFRAME (64 800 bits) at quasi-error-free operation -- a post-FEC packet
error rate of about 1e-7 -- on an AWGN channel. They were migrated unchanged
from the source study; a threshold that moved during migration would be a
silent change to every throughput number downstream, so the test suite pins all
28 of them.

What a table is not
-------------------
A ladder is a set of *thresholds*, measured or published for an AWGN channel. It
says nothing about how a real modem behaves in fading, about acquisition, or
about the latency of switching modes. `implementation_margin_db` is the one
concession to reality, and it is an input rather than a built-in number.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from aerokit.comms.rf import RfError

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "DVB_S2_NORMAL_FRAME_MODCODS",
    "DVB_S2_NORMAL_FRAME_TABLE",
    "Modcod",
    "ModcodSelection",
    "ModcodTable",
    "custom_modcod_table",
    "esn0_from_cn0_db",
    "select_best_modcod",
    "symbol_rate_baud",
]


# =============================================================================
# 2.                              MODCOD CONTRACT
# =============================================================================

@dataclass(frozen=True, slots=True)
class Modcod:
    """One modulation-and-coding operating point.

    ``code_rate_label`` is stored rather than inferred. The migrated source
    recovered "2/3" by finding the nearest entry in a small table of rounded
    fractions, which works for the 11 rates DVB-S2 happens to use and mislabels
    anything else. A ladder that a mission supplies is not restricted to those
    rates, so the label is an input.

    ``spectral_efficiency_bps_hz`` is information bits per modulation symbol
    (the "spectral efficiency" of DVB-S2 MODCOD tables). It equals bit/s/Hz
    only at zero roll-off; the information rate is it times the symbol rate,
    never times the occupied bandwidth ``R_s (1 + alpha)``.
    """

    modulation: str
    code_rate: float
    code_rate_label: str
    spectral_efficiency_bps_hz: float
    required_esn0_db: float

    def __post_init__(self) -> None:
        if not self.modulation.strip():
            raise RfError("a MODCOD needs a modulation name")
        if not self.code_rate_label.strip():
            raise RfError(f"{self.modulation}: a MODCOD needs a code-rate label")
        rate = float(self.code_rate)
        if not math.isfinite(rate) or not 0.0 < rate <= 1.0:
            raise RfError(
                f"{self.modulation}: the code rate must lie in (0, 1], got {rate!r}"
            )
        efficiency = float(self.spectral_efficiency_bps_hz)
        if not math.isfinite(efficiency) or efficiency <= 0.0:
            raise RfError(
                f"{self.name}: the spectral efficiency must be finite and positive, "
                f"got {efficiency!r}"
            )
        if not math.isfinite(self.required_esn0_db):
            raise RfError(f"{self.name}: the required Es/N0 must be finite")

    @property
    def name(self) -> str:
        """A compact identifier such as ``8PSK 3/4``."""
        return f"{self.modulation} {self.code_rate_label}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "modulation": self.modulation,
            "code_rate": self.code_rate,
            "code_rate_label": self.code_rate_label,
            "spectral_efficiency_bps_hz": self.spectral_efficiency_bps_hz,
            "required_esn0_db": self.required_esn0_db,
        }


# =============================================================================
# 3.                         DVB-S2 NORMAL-FRAME LADDER
# =============================================================================

# ETSI EN 302 307-1, normal FECFRAME, quasi-error-free on AWGN.
# (modulation, code rate, label, net spectral efficiency, required Es/N0 dB)
DVB_S2_NORMAL_FRAME_MODCODS: tuple[Modcod, ...] = (
    Modcod("QPSK", 1 / 4, "1/4", 0.490243, -2.35),
    Modcod("QPSK", 1 / 3, "1/3", 0.656448, -1.24),
    Modcod("QPSK", 2 / 5, "2/5", 0.789412, -0.30),
    Modcod("QPSK", 1 / 2, "1/2", 0.988858, 1.00),
    Modcod("QPSK", 3 / 5, "3/5", 1.188304, 2.23),
    Modcod("QPSK", 2 / 3, "2/3", 1.322253, 3.10),
    Modcod("QPSK", 3 / 4, "3/4", 1.487473, 4.03),
    Modcod("QPSK", 4 / 5, "4/5", 1.587196, 4.68),
    Modcod("QPSK", 5 / 6, "5/6", 1.654663, 5.18),
    Modcod("QPSK", 8 / 9, "8/9", 1.766451, 6.20),
    Modcod("QPSK", 9 / 10, "9/10", 1.788612, 6.42),
    Modcod("8PSK", 3 / 5, "3/5", 1.779991, 5.50),
    Modcod("8PSK", 2 / 3, "2/3", 1.980636, 6.62),
    Modcod("8PSK", 3 / 4, "3/4", 2.228124, 7.91),
    Modcod("8PSK", 5 / 6, "5/6", 2.478562, 9.35),
    Modcod("8PSK", 8 / 9, "8/9", 2.646012, 10.69),
    Modcod("8PSK", 9 / 10, "9/10", 2.679207, 10.98),
    Modcod("16APSK", 2 / 3, "2/3", 2.637201, 8.97),
    Modcod("16APSK", 3 / 4, "3/4", 2.966728, 10.21),
    Modcod("16APSK", 4 / 5, "4/5", 3.165623, 11.03),
    Modcod("16APSK", 5 / 6, "5/6", 3.300184, 11.61),
    Modcod("16APSK", 8 / 9, "8/9", 3.523143, 12.89),
    Modcod("16APSK", 9 / 10, "9/10", 3.567342, 13.13),
    Modcod("32APSK", 3 / 4, "3/4", 3.703295, 12.73),
    Modcod("32APSK", 4 / 5, "4/5", 3.951571, 13.64),
    Modcod("32APSK", 5 / 6, "5/6", 4.119540, 14.28),
    Modcod("32APSK", 8 / 9, "8/9", 4.397854, 15.69),
    Modcod("32APSK", 9 / 10, "9/10", 4.453027, 16.05),
)


# =============================================================================
# 4.                                MODCOD TABLE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ModcodTable:
    """A named, sourced ladder of operating points.

    ``standardized`` separates a published standard's table from one a mission
    supplied. It changes no arithmetic; it travels with the result so a reader
    can tell whether a throughput figure rests on EN 302 307-1 or on a modem
    datasheet somebody typed in.
    """

    name: str
    modcods: tuple[Modcod, ...]
    source: str
    standardized: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RfError("a MODCOD table needs a name")
        if not self.modcods:
            raise RfError(f"{self.name}: a MODCOD table needs at least one entry")
        if not self.source.strip():
            raise RfError(
                f"{self.name}: a MODCOD table must say where its thresholds come "
                "from. A throughput figure is only as good as its provenance."
            )
        seen: set[str] = set()
        for modcod in self.modcods:
            if modcod.name in seen:
                raise RfError(
                    f"{self.name}: duplicate operating point {modcod.name!r}. Two "
                    "entries with the same name cannot be told apart in a result."
                )
            seen.add(modcod.name)

    def __len__(self) -> int:
        return len(self.modcods)

    def __iter__(self) -> Iterable[Modcod]:
        return iter(self.modcods)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "standardized": self.standardized,
            "entries": [modcod.as_dict() for modcod in self.modcods],
        }


# =============================================================================
# 5.                               DEFAULT TABLE
# =============================================================================

DVB_S2_NORMAL_FRAME_TABLE = ModcodTable(
    name="DVB-S2 normal FECFRAME",
    modcods=DVB_S2_NORMAL_FRAME_MODCODS,
    source=(
        "ETSI EN 302 307-1, normal FECFRAME (64 800 bits), quasi-error-free "
        "(post-FEC PER ~1e-7) on an AWGN channel"
    ),
    standardized=True,
)


# =============================================================================
# 6.                           TABLE AND RATE HELPERS
# =============================================================================

def custom_modcod_table(
    name: str, modcods: Sequence[Modcod], source: str
) -> ModcodTable:
    """A mission-supplied ladder, marked as not coming from a standard.

    The same structure as `DVB_S2_NORMAL_FRAME_TABLE` with ``standardized``
    false, so a result built on measured modem curves never reads as if it came
    from a published Recommendation.
    """
    return ModcodTable(
        name=name, modcods=tuple(modcods), source=source, standardized=False
    )


def symbol_rate_baud(bandwidth_hz: float, rolloff_factor: float) -> float:
    """``R_s = B / (1 + alpha)`` for a root-raised-cosine shaped carrier."""
    bandwidth = float(bandwidth_hz)
    rolloff = float(rolloff_factor)
    if not math.isfinite(bandwidth) or bandwidth <= 0.0:
        raise RfError(f"bandwidth must be finite and positive, got {bandwidth_hz!r}")
    if not math.isfinite(rolloff) or rolloff < 0.0:
        raise RfError(
            f"the rolloff factor must be finite and non-negative, got {rolloff_factor!r}"
        )
    return bandwidth / (1.0 + rolloff)


def esn0_from_cn0_db(
    cn0_dbhz: float, bandwidth_hz: float, rolloff_factor: float
) -> float:
    """``Es/N0 = C/N0 - 10 log10(R_s)``.

    Es/N0 is referenced to the *symbol* rate, which is the rate a MODCOD
    threshold is quoted against. Referencing it to the allocated bandwidth
    instead would understate it by ``10 log10(1 + alpha)`` -- 0.79 dB at a
    rolloff of 0.20 -- and would quietly select a lower MODCOD.

    Reference: EN 302 307-1 (2014): Normal FECFRAME performance at quasi-error-free operation
    (checked against a secondary source) [SIDERA-ALG-COM-007].
    """
    rate = symbol_rate_baud(bandwidth_hz, rolloff_factor)
    return float(cn0_dbhz) - 10.0 * math.log10(rate)


# =============================================================================
# 7.                             SELECTION CONTRACT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ModcodSelection:
    """The outcome of walking a ladder at one Es/N0.

    ``selected`` is ``None`` when no operating point closes. That is a state, not
    an error: a pass has epochs where the link is shut, and reporting them as
    zero-rate samples is what makes a data-volume integral correct. The migrated
    source made the same choice and it is preserved. ``spectral_efficiency_bps_hz``
    is bits per symbol (see :class:`Modcod`), so ``net_information_rate_bps`` is
    it times ``symbol_rate_baud``.
    """

    table_name: str
    available_esn0_db: float
    implementation_margin_db: float
    selected: Modcod | None
    link_margin_db: float | None
    spectral_efficiency_bps_hz: float
    net_information_rate_bps: float
    symbol_rate_baud: float

    @property
    def closed(self) -> bool:
        """True when some operating point is usable at this Es/N0."""
        return self.selected is not None

    @property
    def mode_name(self) -> str:
        return "none" if self.selected is None else self.selected.name

    def as_dict(self) -> dict[str, Any]:
        return {
            "table_name": self.table_name,
            "available_esn0_db": self.available_esn0_db,
            "implementation_margin_db": self.implementation_margin_db,
            "selected_modcod": None if self.selected is None else self.selected.name,
            "selected_required_esn0_db": (
                None if self.selected is None else self.selected.required_esn0_db
            ),
            "spectral_efficiency_bps_hz": self.spectral_efficiency_bps_hz,
            "link_margin_db": self.link_margin_db,
            "net_information_rate_bps": self.net_information_rate_bps,
            "symbol_rate_baud": self.symbol_rate_baud,
            "closed": self.closed,
        }


# =============================================================================
# 8.                                 SELECTION
# =============================================================================

def select_best_modcod(
    available_esn0_db: float,
    bandwidth_hz: float,
    rolloff_factor: float,
    *,
    table: ModcodTable = DVB_S2_NORMAL_FRAME_TABLE,
    implementation_margin_db: float = 1.0,
) -> ModcodSelection:
    """The most efficient operating point whose threshold the channel meets.

    Selection is by spectral efficiency, not by position in the table, because a
    ladder is not required to be sorted and the two orders differ even in
    DVB-S2: 8PSK 3/5 (1.780 bit/symbol at 5.50 dB) is *less* efficient than QPSK
    9/10 (1.789 at 6.42 dB), so at 6.0 dB the better choice is the earlier row.

    ``implementation_margin_db`` is subtracted from the available Es/N0 before
    comparison. It stands for modem implementation loss -- typically 0.8 to
    1.5 dB -- and is an input because it belongs to the hardware, not to the
    standard.

    Reference: EN 302 307-1 (2014): Normal FECFRAME performance at quasi-error-free operation
    (checked against a secondary source) [SIDERA-ALG-COM-007].
    """
    if not math.isfinite(available_esn0_db):
        raise RfError(f"the available Es/N0 must be finite, got {available_esn0_db!r}")
    margin = float(implementation_margin_db)
    if not math.isfinite(margin) or margin < 0.0:
        raise RfError(
            f"the implementation margin must be finite and non-negative dB, got "
            f"{implementation_margin_db!r}"
        )

    rate = symbol_rate_baud(bandwidth_hz, rolloff_factor)
    usable = float(available_esn0_db) - margin

    selected: Modcod | None = None
    for modcod in table.modcods:
        if modcod.required_esn0_db > usable:
            continue
        if (
            selected is None
            or modcod.spectral_efficiency_bps_hz > selected.spectral_efficiency_bps_hz
        ):
            selected = modcod

    if selected is None:
        return ModcodSelection(
            table_name=table.name,
            available_esn0_db=float(available_esn0_db),
            implementation_margin_db=margin,
            selected=None,
            link_margin_db=None,
            spectral_efficiency_bps_hz=0.0,
            net_information_rate_bps=0.0,
            symbol_rate_baud=rate,
        )

    return ModcodSelection(
        table_name=table.name,
        available_esn0_db=float(available_esn0_db),
        implementation_margin_db=margin,
        selected=selected,
        link_margin_db=usable - selected.required_esn0_db,
        spectral_efficiency_bps_hz=selected.spectral_efficiency_bps_hz,
        net_information_rate_bps=selected.spectral_efficiency_bps_hz * rate,
        symbol_rate_baud=rate,
    )
