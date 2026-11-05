# Copied from Sidera (sidera.communications.channel.dsn_atmosphere, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""The DSN handbook's atmosphere, sky noise and elevation gain loss as link-budget models.

Three pieces that plug into :class:`~aerokit.comms.budget.CommunicationLink`
for a downlink received by a DSN antenna
(:class:`~aerokit.comms.dsn.DsnAntenna`):

- :class:`DsnAtmosphere` -- the propagation model: the zenith attenuation of
  the complex at the weather's cumulative distribution, over ``sin(elevation)``
  air masses (810-005 module 105 Rev. E eq. 2). Absorptive, so it also feeds
  the sky noise. It accounts for the atmosphere (no second atmosphere model
  is accepted beside it).
- :class:`DsnSystemNoise` -- the sky-noise model: ``T_op = T_AMW + T_atm +
  T_CMB'`` with ``T_atm`` and ``T_CMB'`` from the attenuation the link actually
  applied (module 104 eqs. A2-A9), so emission and attenuation always agree.
- :class:`DsnElevationGainLoss` -- the antenna's gravity-deformation loss
  ``G1 (theta - gamma)^2`` below its peak ``G0``: the receive antenna then
  carries ``G0`` (a :class:`~aerokit.comms.antennas.FixedGainAntenna`)
  and this loss line makes the gain the handbook's ``G(theta)``.

All three need the link geometry's elevation at the DSN end.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from aerokit.comms.channel import PropagationLossBreakdown
from aerokit.comms.geometry import LinkGeometry
from aerokit.comms.dsn import (
    DsnAntenna,
    atmosphere_attenuation_db,
    sky_noise_temperature_k,
    zenith_attenuation_db,
)
from aerokit.comms.rf import RfError


def _elevation_deg(geometry: LinkGeometry, what: str) -> float:
    if geometry.elevation_rad is None:
        raise RfError(f"{what} needs the elevation at the DSN antenna; the link geometry has none")
    return math.degrees(float(geometry.elevation_rad))


@dataclass(frozen=True, slots=True)
class DsnAtmosphere:
    """The DSN complex's atmospheric attenuation at a weather level (810-005 105 Rev. E, 104 Table A-5).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """

    antenna: DsnAntenna
    cumulative_distribution: float
    name: str = "DSN atmosphere (810-005 105 Rev. E)"
    accounts_for_atmosphere: bool = True

    def __post_init__(self) -> None:
        zenith_attenuation_db(self.antenna.complex_name, self.antenna.band, self.cumulative_distribution)

    def evaluate(self, geometry: LinkGeometry, frequency_hz: float, context: Any | None = None) -> PropagationLossBreakdown:
        """``A_zen / sin(elevation)`` as absorptive loss (gas and cloud together, as the handbook tabulates)."""
        del frequency_hz, context
        zenith = zenith_attenuation_db(self.antenna.complex_name, self.antenna.band, self.cumulative_distribution)
        loss = atmosphere_attenuation_db(zenith, _elevation_deg(geometry, self.name))
        return PropagationLossBreakdown(
            other_loss_db=loss, total_carrier_loss_db=loss, absorptive_loss_db=loss, sources=(self.name,),
            diagnostics={"zenith_attenuation_db": zenith, "cumulative_distribution": self.cumulative_distribution,
                         "complex": self.antenna.complex_name, "band": self.antenna.band},
        )


@dataclass(frozen=True, slots=True)
class DsnSystemNoise:
    """``T_op`` of a DSN antenna from the attenuation the link applied (810-005 104 Rev. Q eqs. A2-A9).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """

    antenna: DsnAntenna
    cumulative_distribution: float
    name: str = "DSN system noise (810-005 104 Rev. Q)"

    def system_temperature_k(self, geometry: LinkGeometry, propagation: PropagationLossBreakdown) -> float:
        """``T1 + T2 exp(-a theta) + T_p (1 - 1/L) + 2.725 / L``, ``L`` from the applied absorptive loss."""
        elevation = _elevation_deg(geometry, self.name)
        return self.antenna.antenna_microwave_temperature_k(elevation) + sky_noise_temperature_k(
            propagation.absorptive_loss_db, self.cumulative_distribution)


@dataclass(frozen=True, slots=True)
class DsnElevationGainLoss:
    """The DSN antenna's gain loss ``G1 (theta - gamma)^2`` below ``G0``, as a loss line (not absorptive).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """

    antenna: DsnAntenna
    name: str = "DSN elevation gain loss (810-005 104 Rev. Q eq. A-1)"
    accounts_for_atmosphere: bool = False

    def evaluate(self, geometry: LinkGeometry, frequency_hz: float, context: Any | None = None) -> PropagationLossBreakdown:
        """The deformation loss at the geometry's elevation; it emits nothing."""
        del frequency_hz, context
        loss = self.antenna.elevation_gain_loss_db(_elevation_deg(geometry, self.name))
        return PropagationLossBreakdown(other_loss_db=loss, total_carrier_loss_db=loss, absorptive_loss_db=0.0,
                                        sources=(self.name,), diagnostics={"station": self.antenna.station})


__all__ = ["DsnAtmosphere", "DsnElevationGainLoss", "DsnSystemNoise"]
