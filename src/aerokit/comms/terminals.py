# Copied from Sidera (sidera.communications.hardware.terminals, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Communication hardware: transmitters, receivers and terminals.

The migrated source had a single ``LinkEndpoint`` carrying transmit power,
receive noise temperature, feeder losses and an antenna, whether or not the
endpoint did both jobs. Splitting it means a receive-only ground station cannot
silently acquire a transmit power it does not have, and a relay's uplink
receiver and downlink transmitter are separate objects with separate antennas --
which they are in hardware.

Where the feeder loss goes
--------------------------
This is the detail most easily got wrong, so it is stated once and enforced:

- **Transmit**: ``EIRP = P_t + G_t - L_feeder,tx``. The loss is between the
  amplifier output and the antenna, so it reduces radiated power.
- **Receive**: G/T is invariant under the choice of reference plane as long as
  gain and temperature are evaluated at the *same* plane. Referenced **at the
  antenna output** (ahead of the feeder), ``T_sys`` already folds in the
  feeder's own noise contribution, so ``G/T = G_r - 10 log10(T_sys)`` with no
  loss term. Referenced **at the receiver input** (behind the feeder), both
  the gain and the temperature move past the feeder together, so
  ``G/T = (G_r - L_feeder,rx) - 10 log10(T_sys)`` -- the same number, by a
  different route.

`Receiver` takes ``noise_temperature_reference`` to say which plane ``T_sys``
belongs to, and applies the feeder loss only for ``"receiver_input"``. An
explicit ``G/T`` override bypasses both, and then no feeder loss is applied at
all.

Units
-----
Power watts or dBW, temperature kelvin, loss dB (positive numbers are losses),
frequency Hz.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from aerokit.comms.antennas import AntennaPattern
from aerokit.comms.rf import RfError, linear_to_db, watts_to_dbw

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "CommunicationTerminal",
    "Receiver",
    "Transmitter",
]

# =============================================================================
# 2.                              PRIVATE HELPERS
# =============================================================================

def _loss_db(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise RfError(
            f"{name} must be a finite, non-negative number of dB (losses are "
            f"positive), got {value!r}"
        )
    return number


# =============================================================================
# 3.                     TRANSMITTER, RECEIVER AND TERMINAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class Transmitter:
    """The transmit chain: power, feeder loss and an optional EIRP override.

    Exactly one of ``rf_power_w``/``rf_power_dbw`` or ``eirp_dbw_override`` must
    resolve to an EIRP. An override models a published figure -- a footprint
    contour, a datasheet EIRP -- where the underlying power and gain are not
    separable, and it takes precedence over everything else.
    """

    antenna: AntennaPattern | None = None
    rf_power_w: float | None = None
    rf_power_dbw: float | None = None
    feeder_loss_db: float = 0.0
    eirp_dbw_override: float | None = None
    name: str = "transmitter"

    def __post_init__(self) -> None:
        if self.rf_power_w is not None and self.rf_power_dbw is not None:
            raise RfError(
                f"{self.name}: give the transmit power once, as watts or dBW, not both"
            )
        if self.rf_power_w is not None:
            watts_to_dbw(self.rf_power_w)  # validates positivity
        if self.rf_power_dbw is not None and not math.isfinite(self.rf_power_dbw):
            raise RfError(f"{self.name}: rf_power_dbw must be finite")
        _loss_db(self.feeder_loss_db, f"{self.name}: feeder_loss_db")
        if self.eirp_dbw_override is not None and not math.isfinite(self.eirp_dbw_override):
            raise RfError(f"{self.name}: eirp_dbw_override must be finite")

    @property
    def power_dbw(self) -> float | None:
        """The transmit power in dBW, from whichever of `rf_power_w`/`rf_power_dbw` is set."""
        if self.rf_power_dbw is not None:
            return self.rf_power_dbw
        if self.rf_power_w is not None:
            return watts_to_dbw(self.rf_power_w)
        return None

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float | None:
        """`antenna`'s gain at this frequency and angle, or ``None`` with no antenna."""
        if self.antenna is None:
            return None
        return self.antenna.gain_dbi(frequency_hz, off_boresight_angle_rad, azimuth_rad)

    def eirp_dbw(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float:
        """``P_t + G_t - L_feeder``, or the override when one is given.

        An override is returned unchanged: it is already an effective radiated
        power and applying a feeder loss to it would subtract the loss twice.
        """
        if self.eirp_dbw_override is not None:
            return self.eirp_dbw_override
        power = self.power_dbw
        if power is None:
            raise RfError(
                f"{self.name}: EIRP is undefined. Supply rf_power_w or rf_power_dbw "
                "together with an antenna, or an eirp_dbw_override."
            )
        gain = self.gain_dbi(frequency_hz, off_boresight_angle_rad, azimuth_rad)
        if gain is None:
            raise RfError(
                f"{self.name}: EIRP needs an antenna to supply transmit gain, or an "
                "eirp_dbw_override."
            )
        return power + gain - self.feeder_loss_db

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "name": self.name,
            "rf_power_dbw": self.power_dbw,
            "feeder_loss_db": self.feeder_loss_db,
            "eirp_dbw_override": self.eirp_dbw_override,
            "antenna": None if self.antenna is None else getattr(self.antenna, "as_dict", dict)(),
        }


@dataclass(frozen=True, slots=True)
class Receiver:
    """The receive chain: noise temperature, feeder loss and an optional G/T.

    ``noise_temperature_reference`` says which plane
    ``system_noise_temperature_k`` is referred to. For ``"antenna_output"``
    (the default), the temperature already folds in the feeder's own noise
    contribution, so the feeder loss is not applied to the gain again. For
    ``"receiver_input"``, both the gain and the temperature sit behind the
    feeder, so the loss is subtracted from the gain. Both give the same G/T
    for the same physical system; only the plane, and therefore whether
    ``feeder_loss_db`` enters the G/T calculation, differs.
    """

    antenna: AntennaPattern | None = None
    system_noise_temperature_k: float | None = None
    feeder_loss_db: float = 0.0
    g_over_t_db_per_k_override: float | None = None
    noise_temperature_reference: str = "antenna_output"
    name: str = "receiver"

    def __post_init__(self) -> None:
        if self.system_noise_temperature_k is not None:
            temperature = float(self.system_noise_temperature_k)
            if not math.isfinite(temperature) or temperature <= 0.0:
                raise RfError(
                    f"{self.name}: system noise temperature must be finite and "
                    f"positive kelvin, got {self.system_noise_temperature_k!r}"
                )
        _loss_db(self.feeder_loss_db, f"{self.name}: feeder_loss_db")
        if self.g_over_t_db_per_k_override is not None and not math.isfinite(
            self.g_over_t_db_per_k_override
        ):
            raise RfError(f"{self.name}: g_over_t_db_per_k_override must be finite")
        if self.noise_temperature_reference not in ("antenna_output", "receiver_input"):
            raise RfError(
                f"{self.name}: noise_temperature_reference must be 'antenna_output' or "
                f"'receiver_input', got {self.noise_temperature_reference!r}"
            )

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float | None:
        """`antenna`'s gain at this frequency and angle, or ``None`` with no antenna."""
        if self.antenna is None:
            return None
        return self.antenna.gain_dbi(frequency_hz, off_boresight_angle_rad, azimuth_rad)

    def _plane_gain_dbi(self, gain: float) -> float:
        """`gain` reduced by the feeder loss iff `T_sys` sits behind the feeder."""
        if self.noise_temperature_reference == "receiver_input":
            return gain - self.feeder_loss_db
        return gain

    def g_over_t_db_per_k(
        self,
        frequency_hz: float,
        off_boresight_angle_rad: float = 0.0,
        system_noise_temperature_k: float | None = None,
        azimuth_rad: float | None = None,
    ) -> float:
        """``G_r - 10 log10(T_sys)`` at the plane `T_sys` is referenced to, or the override.

        The feeder loss is subtracted from the gain only when
        ``noise_temperature_reference`` is ``"receiver_input"``; for
        ``"antenna_output"`` it is already folded into `T_sys` and applying it
        again would count it twice.

        ``system_noise_temperature_k`` overrides the stored value for this
        evaluation, which is how an environment-dependent sky-noise model feeds
        an elevation- and weather-dependent temperature in without mutating the
        hardware description.

        An explicit ``g_over_t_db_per_k_override`` wins over both, and no feeder
        loss is applied to it: a quoted G/T is already a system figure.
        """
        if self.g_over_t_db_per_k_override is not None:
            return self.g_over_t_db_per_k_override

        if system_noise_temperature_k is not None:
            temperature = float(system_noise_temperature_k)
            if not math.isfinite(temperature) or temperature <= 0.0:
                raise RfError(
                    f"{self.name}: supplied system noise temperature must be finite "
                    f"and positive, got {system_noise_temperature_k!r}"
                )
            gain = self.gain_dbi(frequency_hz, off_boresight_angle_rad, azimuth_rad)
            if gain is None:
                raise RfError(
                    f"{self.name}: an environment-dependent G/T needs an antenna to "
                    "supply receive gain."
                )
            return self._plane_gain_dbi(gain) - linear_to_db(temperature)

        if self.system_noise_temperature_k is None:
            raise RfError(
                f"{self.name}: G/T is undefined. Supply system_noise_temperature_k "
                "with an antenna, or a g_over_t_db_per_k_override."
            )
        gain = self.gain_dbi(frequency_hz, off_boresight_angle_rad, azimuth_rad)
        if gain is None:
            raise RfError(
                f"{self.name}: G/T needs an antenna to supply receive gain, or a "
                "g_over_t_db_per_k_override."
            )
        return self._plane_gain_dbi(gain) - linear_to_db(self.system_noise_temperature_k)

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "name": self.name,
            "system_noise_temperature_k": self.system_noise_temperature_k,
            "noise_temperature_reference": self.noise_temperature_reference,
            "feeder_loss_db": self.feeder_loss_db,
            "g_over_t_db_per_k_override": self.g_over_t_db_per_k_override,
            "antenna": None if self.antenna is None else getattr(self.antenna, "as_dict", dict)(),
        }


@dataclass(frozen=True, slots=True)
class CommunicationTerminal:
    """Hardware at one end of a link, optionally with a state provider.

    A terminal may transmit, receive, or both. ``state_provider`` is how the
    terminal knows where it is; it is left ``None`` for a terminal whose
    position is supplied some other way, such as a ground station that carries
    its own geodetic site.
    """

    name: str
    transmitter: Transmitter | None = None
    receiver: Receiver | None = None
    state_provider: Any | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RfError("a communication terminal needs a name")
        if self.transmitter is None and self.receiver is None:
            raise RfError(
                f"{self.name}: a terminal must be able to transmit, receive or both; "
                "it has neither"
            )

    @property
    def can_transmit(self) -> bool:
        """Whether the terminal has a `Transmitter`."""
        return self.transmitter is not None

    @property
    def can_receive(self) -> bool:
        """Whether the terminal has a `Receiver`."""
        return self.receiver is not None

    def require_transmitter(self) -> Transmitter:
        """The transmitter, or raise if the terminal cannot be a link source."""
        if self.transmitter is None:
            raise RfError(f"{self.name} has no transmitter, so it cannot be a link source")
        return self.transmitter

    def require_receiver(self) -> Receiver:
        """The receiver, or raise if the terminal cannot be a link destination."""
        if self.receiver is None:
            raise RfError(f"{self.name} has no receiver, so it cannot be a link destination")
        return self.receiver

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict form for serialization."""
        return {
            "name": self.name,
            "transmitter": None if self.transmitter is None else self.transmitter.as_dict(),
            "receiver": None if self.receiver is None else self.receiver.as_dict(),
        }
