# Copied from Sidera (sidera.communications.link.budget, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
One-way link evaluation: EIRP in, margin out, with the breakdown intact.

The result carries every term, not just the answer. A margin of -2.1 dB is not
actionable; the same margin alongside the EIRP, the free-space loss, the rain
attenuation and the required threshold tells a reader which one to change.

The atmospheric double-counting guard
-------------------------------------
The migrated source carried a fixed ``atmospheric_loss_db`` inside its bundle of
engineering losses, and separately offered ITU-R modelled attenuation. Its README
states the rule: the two are alternatives, never addends. That rule lived in
prose and in the discipline of one orchestration function.

Here it is structural. `EngineeringLosses` has no atmospheric field at all.
A fixed allowance is expressed as `FixedAtmosphericAllowance`, which is a
*propagation model*, so it occupies the same slot as the ITU-R model and cannot
coexist with one -- `evaluate_link` refuses a model list containing more than one
atmospheric contributor. Double-counting is not discouraged; it is unreachable.

Sign conventions
----------------
Losses are positive numbers that reduce the carrier. Gains are positive numbers
that increase it. ``margin_db`` is ``achieved - required``, so positive means the
link closes.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from aerokit.comms.channel import (
    PropagationLossBreakdown,
    PropagationModel,
    SkyNoiseModel,
    combine_propagation_losses,
)
from aerokit.comms.geometry import LinkGeometry
from aerokit.comms.terminals import CommunicationTerminal
from aerokit.comms.rf import (
    RfError,
    carrier_to_noise_density_dbhz,
    carrier_to_noise_from_density_db,
    combine_inverse_ratios_db,
    ebn0_from_density_db,
    free_space_path_loss_db,
)

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "CommunicationLink",
    "EngineeringLosses",
    "LinkBudgetResult",
    "evaluate_link",
]


# =============================================================================
# 2.                         LOSSES AND LINK DEFINITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class EngineeringLosses:
    """Fixed losses that do not depend on the atmosphere or the geometry.

    There is deliberately **no** atmospheric field. Environmental attenuation
    belongs to a propagation model, where it is computed from conditions rather
    than assumed, and where it can also drive receiver sky noise. Putting a
    fixed atmospheric allowance here would let it be added to a modelled one.
    """

    pointing_loss_db: float = 0.0
    polarization_loss_db: float = 0.0
    implementation_loss_db: float = 0.0
    other_loss_db: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "pointing_loss_db",
            "polarization_loss_db",
            "implementation_loss_db",
            "other_loss_db",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise RfError(
                    f"{name} must be a finite, non-negative number of dB, got {value!r}"
                )

    @property
    def total_db(self) -> float:
        return (
            self.pointing_loss_db
            + self.polarization_loss_db
            + self.implementation_loss_db
            + self.other_loss_db
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "pointing_loss_db": self.pointing_loss_db,
            "polarization_loss_db": self.polarization_loss_db,
            "implementation_loss_db": self.implementation_loss_db,
            "other_loss_db": self.other_loss_db,
            "total_db": self.total_db,
        }


@dataclass(frozen=True, slots=True)
class CommunicationLink:
    """One directed RF path: a transmitting terminal to a receiving one."""

    name: str
    transmitter: CommunicationTerminal
    receiver: CommunicationTerminal
    frequency_hz: float
    bandwidth_hz: float
    losses: EngineeringLosses = field(default_factory=EngineeringLosses)
    propagation_models: tuple[PropagationModel, ...] = ()
    sky_noise: SkyNoiseModel | None = None
    """Receive system temperature derived from the attenuation, when modelled.

    Evaluated *after* the propagation models, so it sees the attenuation that was
    actually applied. Leave it ``None`` to use the receiver's own stored
    temperature.
    """

    bit_rate_bps: float | None = None
    required_ebn0_db: float | None = None
    polarization: str = "unspecified"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RfError("a link needs a name")
        for label, value in (
            ("frequency_hz", self.frequency_hz),
            ("bandwidth_hz", self.bandwidth_hz),
        ):
            number = float(value)
            if not math.isfinite(number) or number <= 0.0:
                raise RfError(f"{self.name}: {label} must be finite and positive, got {value!r}")
        if self.bit_rate_bps is not None:
            rate = float(self.bit_rate_bps)
            if not math.isfinite(rate) or rate <= 0.0:
                raise RfError(
                    f"{self.name}: bit_rate_bps must be finite and positive when given, "
                    f"got {self.bit_rate_bps!r}"
                )
        if self.required_ebn0_db is not None and not math.isfinite(self.required_ebn0_db):
            raise RfError(f"{self.name}: required_ebn0_db must be finite when given")
        self.transmitter.require_transmitter()
        self.receiver.require_receiver()
        _reject_duplicate_atmospheres(self.name, self.propagation_models)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "frequency_hz": self.frequency_hz,
            "bandwidth_hz": self.bandwidth_hz,
            "bit_rate_bps": self.bit_rate_bps,
            "required_ebn0_db": self.required_ebn0_db,
            "polarization": self.polarization,
            "transmitter": self.transmitter.as_dict(),
            "receiver": self.receiver.as_dict(),
            "losses": self.losses.as_dict(),
            "sky_noise": (
                None if self.sky_noise is None else getattr(self.sky_noise, "as_dict", dict)()
            ),
            "propagation_models": [
                getattr(model, "as_dict", dict)() for model in self.propagation_models
            ],
        }


# =============================================================================
# 3.                              PRIVATE HELPERS
# =============================================================================

def _reject_duplicate_atmospheres(
    link_name: str, models: Sequence[PropagationModel]
) -> None:
    """Refuse more than one model claiming the same atmospheric attenuation.

    This is the structural form of the source project's rule that a fixed
    allowance and a modelled attenuation must not be added together. Each model
    declares whether it accounts for the atmosphere; two that do would
    double-count, so the combination is rejected rather than summed.
    """
    atmospheric = [
        getattr(model, "name", type(model).__name__)
        for model in models
        if getattr(model, "accounts_for_atmosphere", False)
    ]
    if len(atmospheric) > 1:
        raise RfError(
            f"{link_name}: {len(atmospheric)} propagation models each account for "
            f"atmospheric attenuation ({', '.join(atmospheric)}). A fixed allowance and "
            "a modelled attenuation describe the same physics, so adding them would "
            "count the atmosphere twice. Use exactly one."
        )


# =============================================================================
# 4.                             LINK BUDGET RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class LinkBudgetResult:
    """Every term of a one-way link evaluation.

    Kept whole so a reader can audit why a link failed rather than being handed
    a single number.
    """

    link_name: str
    geometry: LinkGeometry
    frequency_hz: float
    bandwidth_hz: float

    eirp_dbw: float
    transmit_gain_dbi: float | None
    receive_gain_dbi: float | None
    g_over_t_db_per_k: float
    system_noise_temperature_k: float | None

    free_space_path_loss_db: float
    propagation: PropagationLossBreakdown
    engineering_losses_db: float
    total_path_loss_db: float

    cn0_dbhz: float
    cn_db: float
    carrier_power_dbw: float | None

    bit_rate_bps: float | None = None
    ebn0_db: float | None = None
    required_ebn0_db: float | None = None
    margin_db: float | None = None
    carrier_to_interference_db: float | None = None
    cn0_with_interference_dbhz: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def closes(self) -> bool | None:
        """Whether the link meets its threshold. ``None`` when none was set."""
        if self.margin_db is None:
            return None
        return self.margin_db >= 0.0

    @property
    def effective_cn0_dbhz(self) -> float:
        """``C/N0`` after interference, when interference was modelled."""
        return self.cn0_dbhz if self.cn0_with_interference_dbhz is None else (
            self.cn0_with_interference_dbhz
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "link_name": self.link_name,
            "frequency_hz": self.frequency_hz,
            "bandwidth_hz": self.bandwidth_hz,
            "range_m": self.geometry.range_m,
            "elevation_rad": self.geometry.elevation_rad,
            "eirp_dbw": self.eirp_dbw,
            "transmit_gain_dbi": self.transmit_gain_dbi,
            "receive_gain_dbi": self.receive_gain_dbi,
            "g_over_t_db_per_k": self.g_over_t_db_per_k,
            "system_noise_temperature_k": self.system_noise_temperature_k,
            "free_space_path_loss_db": self.free_space_path_loss_db,
            "propagation": self.propagation.as_dict(),
            "engineering_losses_db": self.engineering_losses_db,
            "total_path_loss_db": self.total_path_loss_db,
            "cn0_dbhz": self.cn0_dbhz,
            "cn_db": self.cn_db,
            "carrier_power_dbw": self.carrier_power_dbw,
            "bit_rate_bps": self.bit_rate_bps,
            "ebn0_db": self.ebn0_db,
            "required_ebn0_db": self.required_ebn0_db,
            "margin_db": self.margin_db,
            "closes": self.closes,
            "carrier_to_interference_db": self.carrier_to_interference_db,
            "cn0_with_interference_dbhz": self.cn0_with_interference_dbhz,
            "diagnostics": self.diagnostics,
        }


# =============================================================================
# 5.                              LINK EVALUATION
# =============================================================================

def evaluate_link(
    link: CommunicationLink,
    geometry: LinkGeometry,
    *,
    system_noise_temperature_k: float | None = None,
    carrier_to_interference_db: float | None = None,
    context: Any | None = None,
) -> LinkBudgetResult:
    """Evaluate one link at one geometry.

    ``system_noise_temperature_k`` overrides the receiver's stored temperature,
    which is how an environment-dependent sky-noise model feeds in an
    elevation- and weather-dependent value without mutating the hardware.

    ``carrier_to_interference_db`` is combined with the thermal ratio in the
    linear domain, never by adding decibels.

    Reference: Friis (1946): Simple transmission formula (checked against a secondary source)
    [SIDERA-ALG-COM-001].
    """
    transmitter = link.transmitter.require_transmitter()
    receiver = link.receiver.require_receiver()

    transmit_boresight = geometry.transmit_off_boresight_rad or 0.0
    receive_boresight = geometry.receive_off_boresight_rad or 0.0
    transmit_azimuth = geometry.transmit_boresight_azimuth_rad
    receive_azimuth = geometry.receive_boresight_azimuth_rad

    eirp = transmitter.eirp_dbw(link.frequency_hz, transmit_boresight, transmit_azimuth)
    transmit_gain = transmitter.gain_dbi(link.frequency_hz, transmit_boresight, transmit_azimuth)
    receive_gain = receiver.gain_dbi(link.frequency_hz, receive_boresight, receive_azimuth)

    propagation = combine_propagation_losses(
        link.propagation_models,
        geometry=geometry,
        frequency_hz=link.frequency_hz,
        context=context,
    )

    # Precedence: an explicit override, then a sky-noise model fed by the
    # attenuation just computed, then a temperature a propagation model set for
    # itself, and finally the receiver's own stored value.
    effective_temperature = system_noise_temperature_k
    if effective_temperature is None and link.sky_noise is not None:
        effective_temperature = link.sky_noise.system_temperature_k(geometry, propagation)
    if effective_temperature is None:
        effective_temperature = propagation.system_noise_temperature_k
    g_over_t = receiver.g_over_t_db_per_k(
        link.frequency_hz,
        receive_boresight,
        system_noise_temperature_k=effective_temperature,
        azimuth_rad=receive_azimuth,
    )

    fspl = free_space_path_loss_db(geometry.range_m, link.frequency_hz)
    engineering = link.losses.total_db
    total_loss = fspl + engineering + propagation.total_carrier_loss_db

    cn0 = carrier_to_noise_density_dbhz(eirp, g_over_t, total_loss)
    cn = carrier_to_noise_from_density_db(cn0, link.bandwidth_hz)

    cn0_with_interference: float | None = None
    if carrier_to_interference_db is not None:
        # C/I is a ratio in the same bandwidth as C/N, so the combination is
        # done there and converted back to a density.
        combined_cn = combine_inverse_ratios_db([cn, carrier_to_interference_db])
        cn0_with_interference = combined_cn + (cn0 - cn)

    carrier_power: float | None = None
    if receive_gain is not None:
        carrier_power = eirp - total_loss + receive_gain - receiver.feeder_loss_db

    working_cn0 = cn0 if cn0_with_interference is None else cn0_with_interference
    ebn0: float | None = None
    margin: float | None = None
    if link.bit_rate_bps is not None:
        ebn0 = ebn0_from_density_db(working_cn0, link.bit_rate_bps)
        if link.required_ebn0_db is not None:
            margin = ebn0 - link.required_ebn0_db

    return LinkBudgetResult(
        link_name=link.name,
        geometry=geometry,
        frequency_hz=link.frequency_hz,
        bandwidth_hz=link.bandwidth_hz,
        eirp_dbw=eirp,
        transmit_gain_dbi=transmit_gain,
        receive_gain_dbi=receive_gain,
        g_over_t_db_per_k=g_over_t,
        system_noise_temperature_k=effective_temperature
        if effective_temperature is not None
        else receiver.system_noise_temperature_k,
        free_space_path_loss_db=fspl,
        propagation=propagation,
        engineering_losses_db=engineering,
        total_path_loss_db=total_loss,
        cn0_dbhz=cn0,
        cn_db=cn,
        carrier_power_dbw=carrier_power,
        bit_rate_bps=link.bit_rate_bps,
        ebn0_db=ebn0,
        required_ebn0_db=link.required_ebn0_db,
        margin_db=margin,
        carrier_to_interference_db=carrier_to_interference_db,
        cn0_with_interference_dbhz=cn0_with_interference,
        diagnostics={
            "sky_noise_model": (
                None if link.sky_noise is None else getattr(link.sky_noise, "name", None)
            ),
            "propagation_models": [
                getattr(model, "name", type(model).__name__)
                for model in link.propagation_models
            ],
        },
    )
