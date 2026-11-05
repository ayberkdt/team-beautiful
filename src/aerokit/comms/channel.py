# Copied from Sidera (sidera.communications.channel.models, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Propagation-loss models: the composable interface, and the simplest models.

A propagation model answers one question -- how much does the medium take out of
this carrier, and by which mechanism. Mechanisms are kept separate because they
are not interchangeable downstream:

**Absorptive** mechanisms (rain, cloud, gas) attenuate the carrier *and* emit
thermal noise into the receive antenna, because a lossy medium at a physical
temperature radiates. **Refractive** mechanisms (scintillation) redistribute
energy by focusing and defocusing; they fade the carrier without adding thermal
emission. Summing the two and feeding the total into a sky-noise model would
invent noise that is not there.

`PropagationLossBreakdown` therefore carries ``absorptive_loss_db`` separately
from ``total_carrier_loss_db``, and the receiver-noise models consume the first.

Accounting for the atmosphere exactly once
------------------------------------------
Every model declares ``accounts_for_atmosphere``. `CommunicationLink` refuses a
model list with more than one such model, which is what makes the source
project's "fixed allowance and modelled attenuation are alternatives" rule
structural rather than advisory.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from aerokit.comms.geometry import LinkGeometry
from aerokit.comms.rf import RfError

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "FixedAtmosphericAllowance",
    "FreeSpaceOnly",
    "PropagationLossBreakdown",
    "PropagationModel",
    "SkyNoiseModel",
    "combine_propagation_losses",
]


# =============================================================================
# 2.                               LOSS BREAKDOWN
# =============================================================================

@dataclass(frozen=True, slots=True)
class PropagationLossBreakdown:
    """Attenuation by mechanism, in dB.

    ``total_carrier_loss_db`` is what the carrier loses. ``absorptive_loss_db``
    is the part of it that also raises the antenna noise temperature. They are
    equal only when no refractive mechanism is modelled.
    """

    gaseous_absorption_db: float = 0.0
    rain_attenuation_db: float = 0.0
    cloud_attenuation_db: float = 0.0
    scintillation_db: float = 0.0
    other_loss_db: float = 0.0
    total_carrier_loss_db: float = 0.0
    absorptive_loss_db: float = 0.0
    system_noise_temperature_k: float | None = None
    """Set by a model that computes sky noise; ``None`` leaves the receiver's own."""

    sources: tuple[str, ...] = ()
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "gaseous_absorption_db",
            "rain_attenuation_db",
            "cloud_attenuation_db",
            "scintillation_db",
            "other_loss_db",
            "total_carrier_loss_db",
            "absorptive_loss_db",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise RfError(
                    f"{name} must be a finite, non-negative number of dB, got {value!r}"
                )
        if self.absorptive_loss_db > self.total_carrier_loss_db + 1e-9:
            raise RfError(
                f"absorptive loss ({self.absorptive_loss_db} dB) exceeds the total "
                f"carrier loss ({self.total_carrier_loss_db} dB); the part of a loss "
                "that also emits cannot be larger than the loss itself"
            )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "gaseous_absorption_db": self.gaseous_absorption_db,
            "rain_attenuation_db": self.rain_attenuation_db,
            "cloud_attenuation_db": self.cloud_attenuation_db,
            "scintillation_db": self.scintillation_db,
            "other_loss_db": self.other_loss_db,
            "total_carrier_loss_db": self.total_carrier_loss_db,
            "absorptive_loss_db": self.absorptive_loss_db,
            "system_noise_temperature_k": self.system_noise_temperature_k,
            "sources": list(self.sources),
            "diagnostics": self.diagnostics,
        }


# =============================================================================
# 3.                              MODEL PROTOCOLS
# =============================================================================

@runtime_checkable
class PropagationModel(Protocol):
    """One environmental contribution to a link's loss.

    The two attributes are declared read-only so that a frozen dataclass -- which
    is what every model here is -- satisfies the protocol.
    """

    @property
    def name(self) -> str:
        """A short label for the model, carried into its loss breakdown."""
        ...

    @property
    def accounts_for_atmosphere(self) -> bool:
        """Whether this model already covers the atmosphere, for the one-model rule."""
        ...

    def evaluate(
        self,
        geometry: LinkGeometry,
        frequency_hz: float,
        context: Any | None = None,
    ) -> PropagationLossBreakdown:
        """The loss and noise contribution this model adds for `geometry` at `frequency_hz`."""
        ...


@runtime_checkable
class SkyNoiseModel(Protocol):
    """A receive system temperature that depends on the path and its attenuation.

    Separate from `PropagationModel` because of the direction of the coupling: a
    sky-noise model consumes the attenuation, so it can only run once the
    propagation models have. Expressing it as a propagation model would put it in
    a list whose members are evaluated independently and in arbitrary order, and
    it would silently read a breakdown that did not yet include the rain.

    `evaluate_link` runs the propagation models first and hands the combined
    breakdown here, so the emission always corresponds to the attenuation that
    was actually applied to the carrier.
    """

    @property
    def name(self) -> str:
        """A short label for the model."""
        ...

    def system_temperature_k(
        self, geometry: LinkGeometry, propagation: PropagationLossBreakdown
    ) -> float:
        """The receive system noise temperature, kelvin, given the applied attenuation."""
        ...


# =============================================================================
# 4.                   FREE-SPACE AND FIXED-ALLOWANCE MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class FreeSpaceOnly:
    """No medium at all. Vacuum between the terminals.

    The right model for a spacecraft-to-spacecraft link above the atmosphere,
    and the honest default: it adds nothing rather than assuming an allowance.
    """

    name: str = "free space only"
    accounts_for_atmosphere: bool = False

    def evaluate(
        self,
        geometry: LinkGeometry,
        frequency_hz: float,
        context: Any | None = None,
    ) -> PropagationLossBreakdown:
        """An empty breakdown: no loss, no noise, vacuum only."""
        del geometry, frequency_hz, context
        return PropagationLossBreakdown(sources=(self.name,))

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {"kind": "free_space_only", "name": self.name}


@dataclass(frozen=True, slots=True)
class FixedAtmosphericAllowance:
    """A constant atmospheric budget, in dB.

    The migrated source carried this as ``atmospheric_loss_db`` inside its fixed
    engineering losses, where it could be added to a modelled attenuation. Here
    it is a propagation model, so it occupies the same slot as an ITU-R model and
    the two cannot both be present.

    It is a *budget*, not a computation: it does not depend on elevation,
    frequency or weather. Use it for a design allowance or to reproduce a legacy
    result; use a real model when the answer matters.

    ``absorptive_fraction`` says how much of the allowance should drive sky
    noise. It defaults to 1.0 -- an allowance stands in mostly for gas and rain,
    both absorptive -- but a caller who means something else can say so.
    """

    loss_db: float
    absorptive_fraction: float = 1.0
    name: str = "fixed atmospheric allowance"
    accounts_for_atmosphere: bool = True

    def __post_init__(self) -> None:
        value = float(self.loss_db)
        if not math.isfinite(value) or value < 0.0:
            raise RfError(
                f"fixed atmospheric allowance must be a finite, non-negative number "
                f"of dB, got {self.loss_db!r}"
            )
        fraction = float(self.absorptive_fraction)
        if not math.isfinite(fraction) or not 0.0 <= fraction <= 1.0:
            raise RfError(
                f"absorptive_fraction must lie in [0, 1], got {self.absorptive_fraction!r}"
            )

    def evaluate(
        self,
        geometry: LinkGeometry,
        frequency_hz: float,
        context: Any | None = None,
    ) -> PropagationLossBreakdown:
        """The stated `loss_db`, unconditionally; `geometry` and `frequency_hz` are not consulted."""
        del geometry, frequency_hz, context
        return PropagationLossBreakdown(
            other_loss_db=self.loss_db,
            total_carrier_loss_db=self.loss_db,
            absorptive_loss_db=self.loss_db * self.absorptive_fraction,
            sources=(self.name,),
            diagnostics={"fixed_allowance": True},
        )

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "kind": "fixed_atmospheric_allowance",
            "name": self.name,
            "loss_db": self.loss_db,
            "absorptive_fraction": self.absorptive_fraction,
        }


# =============================================================================
# 5.                                COMBINATION
# =============================================================================

def combine_propagation_losses(
    models: Sequence[PropagationModel],
    *,
    geometry: LinkGeometry,
    frequency_hz: float,
    context: Any | None = None,
) -> PropagationLossBreakdown:
    """Evaluate every model and sum the mechanisms.

    Decibel losses in series **do** add: each is a multiplicative transmissivity,
    so their logarithms sum. That is different from combining carrier-to-noise
    ratios, which must be done in the linear domain. The two are distinguished
    here so neither rule leaks into the other.

    A system noise temperature set by any model is carried through; if more than
    one sets it, the last wins and the diagnostics record that, because two
    independent sky-noise models is a configuration error the caller should see.
    """
    if not models:
        return PropagationLossBreakdown(sources=("none",))

    gaseous = rain = cloud = scintillation = other = 0.0
    total = absorptive = 0.0
    temperature: float | None = None
    temperature_setters: list[str] = []
    sources: list[str] = []
    diagnostics: dict[str, Any] = {}

    for model in models:
        breakdown = model.evaluate(geometry, frequency_hz, context)
        gaseous += breakdown.gaseous_absorption_db
        rain += breakdown.rain_attenuation_db
        cloud += breakdown.cloud_attenuation_db
        scintillation += breakdown.scintillation_db
        other += breakdown.other_loss_db
        total += breakdown.total_carrier_loss_db
        absorptive += breakdown.absorptive_loss_db
        if breakdown.system_noise_temperature_k is not None:
            temperature = breakdown.system_noise_temperature_k
            temperature_setters.append(getattr(model, "name", type(model).__name__))
        sources.extend(breakdown.sources)
        diagnostics.update(breakdown.diagnostics)

    if len(temperature_setters) > 1:
        diagnostics["conflicting_noise_models"] = temperature_setters

    return PropagationLossBreakdown(
        gaseous_absorption_db=gaseous,
        rain_attenuation_db=rain,
        cloud_attenuation_db=cloud,
        scintillation_db=scintillation,
        other_loss_db=other,
        total_carrier_loss_db=total,
        absorptive_loss_db=min(absorptive, total),
        system_noise_temperature_k=temperature,
        sources=tuple(sources),
        diagnostics=diagnostics,
    )
