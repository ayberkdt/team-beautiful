# Copied from Sidera (sidera.communications.geometry, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Link geometry: where the two ends are, relative to each other.

This replaces the migrated source's GEO-specific geometry entirely. There is no
satellite longitude, no spherical Earth and no orbit model here. A `LinkGeometry`
is produced from two states at an epoch, and it does not care whether those
states came from a propagated trajectory, an ephemeris, a ground site rotating
with its body, or an analytic function.

Visibility is a reason, not a boolean
-------------------------------------
`VisibilityStatus` records *why* a link is unavailable. "Below the elevation
mask" and "occulted by the Moon" call for entirely different responses, and a
single ``False`` erases the difference.

Sign conventions
----------------
- ``line_of_sight_unit`` points **from the transmitter to the receiver**.
- ``range_rate_m_s`` is positive when the two are separating.
- Doppler is ``-f0 * rho_dot / c``: **positive** shift on approach, negative on
  recession, which is the usual radio convention. It is applied to the carrier
  frequency the transmitter emits.

Units
-----
Metres, metres per second, radians, hertz, seconds.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.comms.constants import C_LIGHT
from aerokit.comms.rf import RfError

if TYPE_CHECKING:
    from aerokit.comms.state import StateProvider

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "BoresightPointing",
    "GeometryError",
    "LightTimeMode",
    "LinkGeometry",
    "VisibilityStatus",
    "doppler_shift_hz",
    "geometry_from_states",
    "geometry_with_light_time",
    "one_way_light_time_s",
    "with_pointing",
]

# =============================================================================
# 2.                                   TYPES
# =============================================================================

VisibilityStatus = Literal[
    "VISIBLE",
    "BELOW_ELEVATION_MASK",
    "OCCULTED_BY_BODY",
    "OUTSIDE_POINTING_LIMIT",
    "OUT_OF_RANGE",
    "BLOCKED_BY_STRUCTURE",
    "SUN_EXCLUSION",
    "AZIMUTH_RATE_LIMIT",
]

LightTimeMode = Literal["INSTANTANEOUS_GEOMETRY", "ITERATED_ONE_WAY_LIGHT_TIME"]
"""Which epochs the two endpoint states are taken at.

``INSTANTANEOUS_GEOMETRY`` takes both at the same epoch. It is what the migrated
source did, it is right for near-Earth work where the light time is milliseconds,
and it is the default so a result is never silently light-time corrected.

``ITERATED_ONE_WAY_LIGHT_TIME`` solves ``t_r - t_t = |r_r(t_r) - r_t(t_t)| / c``
for the transmit epoch given the receive epoch, so the two states are taken
at different epochs: `geometry_with_light_time` does the solve from two
state providers. `geometry_from_states` accepts the mode only together with
both epochs (states the caller has already corrected) and refuses it
otherwise, rather than silently returning the instantaneous geometry.
Newtonian light time in one inertial frame: no Shapiro delay, no
aberration of the receiving frame.
"""


# =============================================================================
# 3.                                 EXCEPTIONS
# =============================================================================

class GeometryError(RfError):
    """The link geometry is not defined for these inputs.

    Subclasses `RfError` (itself a `ValueError`) so an ``except RfError``
    catches a geometry failure too, rather than needing a second handler for
    what is, to a caller, the same kind of thing: bad or undefined RF input.
    """


@runtime_checkable
class BoresightPointing(Protocol):
    """Anything that knows where an antenna points (``hardware.pointing.AntennaPointing``).

    Structural, so this module needs no import of the hardware layer below it.
    ``off_boresight(epoch_s, los)`` returns the angle between the boresight and
    the inertial direction ``los`` and the azimuth of ``los`` about the
    boresight, in radians, in the frame the link states are given in.
    """

    def off_boresight(self, epoch_s: float, line_of_sight_inertial: ArrayLike) -> tuple[float, float]: ...


# =============================================================================
# 4.                              PRIVATE HELPERS
# =============================================================================

def _degrees_or_none(angle_rad: float | None) -> float | None:
    return None if angle_rad is None else math.degrees(angle_rad)


def _frozen(array: ArrayLike) -> NDArray[np.float64]:
    copy = np.array(array, dtype=np.float64, copy=True)
    copy.setflags(write=False)
    return copy


# =============================================================================
# 5.                           LIGHT TIME AND DOPPLER
# =============================================================================

def one_way_light_time_s(range_m: float) -> float:
    """``R / c``. The geometric one-way signal travel time.

    Geometric only: no media delay, no relativistic term. Naming it
    ``one_way`` rather than ``light_time`` keeps the two-way case from being
    assumed.
    """
    distance = float(range_m)
    if not math.isfinite(distance) or distance < 0.0:
        raise GeometryError(f"range must be finite and non-negative, got {range_m!r}")
    return distance / C_LIGHT


def doppler_shift_hz(carrier_frequency_hz: float, range_rate_m_s: float) -> float:
    """First-order classical Doppler, ``-f0 * rho_dot / c``.

    Positive when the endpoints are closing. First order in ``rho_dot / c``:
    no relativistic time dilation, no two-way term, no media contribution. It is
    a diagnostic, not a radiometric observable model.
    """
    frequency = float(carrier_frequency_hz)
    if not math.isfinite(frequency) or frequency <= 0.0:
        raise GeometryError(f"carrier frequency must be finite and positive, got {frequency!r}")
    rate = float(range_rate_m_s)
    if not math.isfinite(rate):
        raise GeometryError(f"range rate must be finite, got {range_rate_m_s!r}")
    return -frequency * rate / C_LIGHT


# =============================================================================
# 6.                               LINK GEOMETRY
# =============================================================================

@dataclass(frozen=True, slots=True)
class LinkGeometry:
    """The relative geometry of one link at one epoch."""

    epoch_s: float
    transmit_position_m: NDArray[np.float64]
    receive_position_m: NDArray[np.float64]
    range_m: float
    line_of_sight_unit: NDArray[np.float64]
    range_rate_m_s: float

    transmit_epoch_s: float | None = None
    receive_epoch_s: float | None = None
    light_time_mode: LightTimeMode = "INSTANTANEOUS_GEOMETRY"

    elevation_rad: float | None = None
    azimuth_rad: float | None = None
    transmit_off_boresight_rad: float | None = None
    receive_off_boresight_rad: float | None = None
    transmit_boresight_azimuth_rad: float | None = None
    receive_boresight_azimuth_rad: float | None = None

    visibility: VisibilityStatus = "VISIBLE"
    occulting_body: str | None = None

    @property
    def visible(self) -> bool:
        return self.visibility == "VISIBLE"

    @property
    def one_way_light_time_s(self) -> float:
        return one_way_light_time_s(self.range_m)

    def doppler_shift_hz(self, carrier_frequency_hz: float) -> float:
        return doppler_shift_hz(carrier_frequency_hz, self.range_rate_m_s)

    def elevation_deg(self) -> float | None:
        return None if self.elevation_rad is None else math.degrees(self.elevation_rad)

    def azimuth_deg(self) -> float | None:
        return None if self.azimuth_rad is None else math.degrees(self.azimuth_rad)

    def as_dict(self) -> dict[str, Any]:
        return {
            "epoch_s": self.epoch_s,
            "range_m": self.range_m,
            "range_rate_m_s": self.range_rate_m_s,
            "one_way_light_time_s": self.one_way_light_time_s,
            "elevation_deg": self.elevation_deg(),
            "azimuth_deg": self.azimuth_deg(),
            "visibility": self.visibility,
            "occulting_body": self.occulting_body,
            "light_time_mode": self.light_time_mode,
            "transmit_epoch_s": self.transmit_epoch_s,
            "receive_epoch_s": self.receive_epoch_s,
            **self._pointing_dict(),
        }

    def _pointing_dict(self) -> dict[str, Any]:
        # Only when pointing was evaluated, so a result without it serialises as before.
        if self.transmit_off_boresight_rad is None and self.receive_off_boresight_rad is None:
            return {}
        return {
            "transmit_off_boresight_deg": _degrees_or_none(self.transmit_off_boresight_rad),
            "receive_off_boresight_deg": _degrees_or_none(self.receive_off_boresight_rad),
        }


# =============================================================================
# 7.                            GEOMETRY FROM STATES
# =============================================================================

def geometry_from_states(
    epoch_s: float,
    transmit_state: ArrayLike,
    receive_state: ArrayLike,
    *,
    transmit_epoch_s: float | None = None,
    receive_epoch_s: float | None = None,
    light_time_mode: LightTimeMode = "INSTANTANEOUS_GEOMETRY",
    elevation_rad: float | None = None,
    azimuth_rad: float | None = None,
    visibility: VisibilityStatus = "VISIBLE",
    occulting_body: str | None = None,
    transmit_pointing: BoresightPointing | None = None,
    receive_pointing: BoresightPointing | None = None,
) -> LinkGeometry:
    """Build a `LinkGeometry` from two six-element states in one frame.

    Both states must be in the same inertial frame; that is the caller's
    contract and nothing here can check it. The range rate is the projection of
    the relative velocity on the line of sight, which is the quantity Doppler
    depends on -- not the magnitude of the relative velocity.

    With ``transmit_pointing`` / ``receive_pointing`` the off-boresight angles
    are filled by `with_pointing`; without them they stay ``None`` (boresight
    gain, the behaviour before pointing existed).
    """
    if light_time_mode == "ITERATED_ONE_WAY_LIGHT_TIME" and (
        transmit_epoch_s is None or receive_epoch_s is None
    ):
        # This function takes states, not providers, so it cannot solve for
        # the transmit epoch. Without both epochs the mode would be a label
        # on an instantaneous geometry; refuse rather than mislabel.
        raise NotImplementedError(
            "ITERATED_ONE_WAY_LIGHT_TIME needs transmit_epoch_s and receive_epoch_s "
            "for states already taken at those epochs; use geometry_with_light_time "
            "to solve for them from two state providers."
        )
    transmit = np.asarray(transmit_state, dtype=np.float64).ravel()
    receive = np.asarray(receive_state, dtype=np.float64).ravel()
    for label, state in (("transmit state", transmit), ("receive state", receive)):
        if state.shape != (6,) or not np.all(np.isfinite(state)):
            raise GeometryError(f"{label} must be a finite 6-vector [x,y,z,vx,vy,vz]")
    if not math.isfinite(epoch_s):
        raise GeometryError(f"epoch must be finite, got {epoch_s!r}")

    separation = receive[:3] - transmit[:3]
    distance = float(np.linalg.norm(separation))
    if distance <= 0.0:
        raise GeometryError(
            "the two terminals are at the same point, so the link has no direction "
            "and no range"
        )
    line_of_sight = separation / distance
    relative_velocity = receive[3:] - transmit[3:]
    range_rate = float(np.dot(relative_velocity, line_of_sight))

    geometry = LinkGeometry(
        epoch_s=float(epoch_s),
        transmit_position_m=_frozen(transmit[:3]),
        receive_position_m=_frozen(receive[:3]),
        range_m=distance,
        line_of_sight_unit=_frozen(line_of_sight),
        range_rate_m_s=range_rate,
        transmit_epoch_s=transmit_epoch_s,
        receive_epoch_s=receive_epoch_s,
        light_time_mode=light_time_mode,
        elevation_rad=elevation_rad,
        azimuth_rad=azimuth_rad,
        visibility=visibility,
        occulting_body=occulting_body,
    )
    return with_pointing(geometry, transmit_pointing, receive_pointing)


def with_pointing(geometry: LinkGeometry, transmit_pointing: BoresightPointing | None = None,
                  receive_pointing: BoresightPointing | None = None) -> LinkGeometry:
    """``geometry`` with its off-boresight angles and azimuths from the antenna pointing.

    The transmitter is asked at its own epoch (``transmit_epoch_s``, the
    emission, when the geometry carries light time) toward the line of sight;
    the receiver at the reception epoch toward the reversed line of sight, the
    direction the signal arrives from. Aberration is not modelled (a
    direction error of |v|/c, 1e-5 rad at 3 km/s).
    """
    if transmit_pointing is None and receive_pointing is None:
        return geometry
    los = geometry.line_of_sight_unit
    tx_theta = geometry.transmit_off_boresight_rad
    tx_phi = geometry.transmit_boresight_azimuth_rad
    rx_theta = geometry.receive_off_boresight_rad
    rx_phi = geometry.receive_boresight_azimuth_rad
    if transmit_pointing is not None:
        epoch = geometry.transmit_epoch_s if geometry.transmit_epoch_s is not None else geometry.epoch_s
        tx_theta, tx_phi = (float(x) for x in transmit_pointing.off_boresight(epoch, los))
    if receive_pointing is not None:
        epoch = geometry.receive_epoch_s if geometry.receive_epoch_s is not None else geometry.epoch_s
        rx_theta, rx_phi = (float(x) for x in receive_pointing.off_boresight(epoch, -los))
    return replace(geometry, transmit_off_boresight_rad=tx_theta, transmit_boresight_azimuth_rad=tx_phi,
                   receive_off_boresight_rad=rx_theta, receive_boresight_azimuth_rad=rx_phi)


# =============================================================================
# 8.                       GEOMETRY WITH ONE-WAY LIGHT TIME
# =============================================================================

# The fixed-point map t_t -> t_r - |r_r(t_r) - r_t(t_t)| / c contracts by
# |v_t| / c (1e-5 for a 3 km/s spacecraft), so a handful of iterations reach
# the tolerance. 1e-12 s is 0.3 mm of range, below any range measurement the
# estimator models.
_LIGHT_TIME_TOLERANCE_S = 1.0e-12
_LIGHT_TIME_MAX_ITERATIONS = 20


def geometry_with_light_time(
    receive_epoch_s: float,
    transmitter: StateProvider,
    receiver: StateProvider,
    *,
    tolerance_s: float = _LIGHT_TIME_TOLERANCE_S,
    elevation_rad: float | None = None,
    azimuth_rad: float | None = None,
    visibility: VisibilityStatus = "VISIBLE",
    occulting_body: str | None = None,
    transmit_pointing: BoresightPointing | None = None,
    receive_pointing: BoresightPointing | None = None,
) -> LinkGeometry:
    """One-way link geometry with the transmit epoch solved for.

    The signal arrives at ``receive_epoch_s``; the transmit epoch ``t_t``
    satisfies ``t_r - t_t = |r_r(t_r) - r_t(t_t)| / c``, solved by fixed-point
    iteration from ``t_t = t_r``. Both providers must answer in the same
    inertial frame (the caller's contract, as for `geometry_from_states`).

    ``range_m`` is the light-time range and ``range_rate_m_s`` its derivative
    with respect to the receive epoch, ``los . (v_r - v_t) / (1 - los . v_t / c)``:
    the transmit epoch moves with the receive epoch, which the instantaneous
    projection ``los . (v_r - v_t)`` ignores (a 1e-5 relative difference at
    3 km/s).

    Reference: Montenbruck & Gill (2000) (source identified; content not yet checked)
    [SIDERA-ALG-COM-010].
    """
    if not math.isfinite(receive_epoch_s):
        raise GeometryError(f"receive epoch must be finite, got {receive_epoch_s!r}")
    if not math.isfinite(tolerance_s) or tolerance_s <= 0.0:
        raise GeometryError(f"tolerance_s must be finite and positive, got {tolerance_s!r}")
    t_r = float(receive_epoch_s)
    receive = np.asarray(receiver.state_at(t_r), dtype=np.float64).ravel()
    if receive.shape != (6,) or not np.all(np.isfinite(receive)):
        raise GeometryError("receive state must be a finite 6-vector [x,y,z,vx,vy,vz]")
    t_t = t_r
    transmit = np.asarray(transmitter.state_at(t_t), dtype=np.float64).ravel()
    for _ in range(_LIGHT_TIME_MAX_ITERATIONS):
        if transmit.shape != (6,) or not np.all(np.isfinite(transmit)):
            raise GeometryError("transmit state must be a finite 6-vector [x,y,z,vx,vy,vz]")
        updated = t_r - float(np.linalg.norm(receive[:3] - transmit[:3])) / C_LIGHT
        converged = abs(updated - t_t) <= tolerance_s
        t_t = updated
        transmit = np.asarray(transmitter.state_at(t_t), dtype=np.float64).ravel()
        if converged:
            break
    else:
        raise GeometryError(
            f"the light-time iteration did not converge to {tolerance_s} s in "
            f"{_LIGHT_TIME_MAX_ITERATIONS} iterations; a transmitter moving near c "
            "has no fixed point here"
        )
    geometry = geometry_from_states(
        t_r, transmit, receive,
        transmit_epoch_s=t_t,
        receive_epoch_s=t_r,
        light_time_mode="ITERATED_ONE_WAY_LIGHT_TIME",
        elevation_rad=elevation_rad,
        azimuth_rad=azimuth_rad,
        visibility=visibility,
        occulting_body=occulting_body,
    )
    los = geometry.line_of_sight_unit
    stretch = 1.0 - float(np.dot(los, transmit[3:])) / C_LIGHT
    geometry = replace(
        geometry,
        range_rate_m_s=float(np.dot(los, receive[3:] - transmit[3:])) / stretch,
    )
    # The transmitter's attitude at the emission epoch, the receiver's at the reception.
    return with_pointing(geometry, transmit_pointing, receive_pointing)
