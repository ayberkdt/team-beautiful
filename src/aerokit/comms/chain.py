"""Multi-hop links: a chain of one-way links through relays (aerokit code on the copied Sidera link budget).

Each hop is evaluated with :func:`aerokit.comms.budget.evaluate_link`. The end-to-end quality depends on the
relay type:

* **transparent** (bent-pipe, e.g. the Cospas-Sarsat MEOSAR/GEOSAR repeaters): the relay retransmits the received
  noise with the signal, so the noise densities of the hops add,
  ``1/(C/N0)_total = Σ 1/(C/N0)_i`` (linear), via :func:`aerokit.comms.rf.combine_inverse_ratios_db`;
* **regenerative** (demodulate and re-modulate): noise does not propagate; to first order the weakest hop sets the
  chain (bit errors of the hops add, which is second order at useful error rates). ``C/N0`` is the minimum.

End-to-end ``Eb/N0 = C/N0 − 10 log10(R_b)``; the margin is ``Eb/N0 − required``. The one-way light time is the
sum over the hops (relay processing delay not included).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from aerokit.comms.budget import CommunicationLink, LinkBudgetResult, evaluate_link
from aerokit.comms.geometry import LinkGeometry, one_way_light_time_s
from aerokit.comms.rf import RfError, combine_inverse_ratios_db, ebn0_from_density_db

__all__ = ["Hop", "ChainResult", "evaluate_chain"]

RelayType = Literal["transparent", "regenerative"]


@dataclass(frozen=True)
class Hop:
    """One link of the chain and its geometry."""

    link: CommunicationLink
    geometry: LinkGeometry


@dataclass(frozen=True)
class ChainResult:
    """End-to-end result plus every hop's own budget."""

    relay: RelayType
    hops: tuple[LinkBudgetResult, ...]
    cn0_dbhz: float
    limiting_hop: int
    ebn0_db: float | None
    margin_db: float | None
    light_time_s: float

    @property
    def closes(self) -> bool | None:
        """``margin_db >= 0`` (``None`` without a bit rate and a requirement)."""
        return None if self.margin_db is None else self.margin_db >= 0.0


def evaluate_chain(hops: Sequence[Hop], relay: RelayType = "transparent", *, bit_rate_bps: float | None = None,
                   required_ebn0_db: float | None = None) -> ChainResult:
    """Evaluate a chain of hops (see module docstring).

    Raises
    ------
    RfError
        No hops, an unknown relay type, a hop that is not visible, or a requirement without a bit rate.
    """
    if not hops:
        raise RfError("a chain needs at least one hop")
    if relay not in ("transparent", "regenerative"):
        raise RfError("relay must be 'transparent' or 'regenerative'")
    if required_ebn0_db is not None and bit_rate_bps is None:
        raise RfError("a required Eb/N0 needs a bit rate")
    for k, h in enumerate(hops):
        if h.geometry.visibility != "VISIBLE":
            raise RfError(f"hop {k} ({h.link.name}) is not visible: {h.geometry.visibility}")
    results = tuple(evaluate_link(h.link, h.geometry) for h in hops)
    cn0s = [r.cn0_dbhz for r in results]
    limiting = min(range(len(cn0s)), key=lambda k: cn0s[k])
    total = combine_inverse_ratios_db(cn0s) if relay == "transparent" else cn0s[limiting]
    ebn0 = None if bit_rate_bps is None else ebn0_from_density_db(total, bit_rate_bps)
    margin = None if (ebn0 is None or required_ebn0_db is None) else ebn0 - required_ebn0_db
    light = math.fsum(one_way_light_time_s(h.geometry.range_m) for h in hops)
    return ChainResult(relay, results, total, limiting, ebn0, margin, light)
