# Copied from Sidera (sidera.communications.hardware.antennas, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Antenna gain models.

An antenna is represented by its *pattern*: a function from frequency and
off-boresight angle to gain. That is the narrowest interface that covers a
datasheet figure, a parabolic aperture and a tabulated measurement, and it is
what lets an interference model ask a receive antenna what it sees off-axis
without knowing what kind of antenna it is.

Screening versus measurement
----------------------------
`ScreeningOffAxisPattern` is a first-pass sensitivity model, not a regulatory
coordination mask and not a measured radiation pattern. Its name says so, and it
is deliberately a separate type rather than a method on the dish: a caller has
to opt into an approximation by naming it.

The same applies to the half-power beamwidth. ``theta ~ 70 lambda / D`` is a
rule of thumb whose constant depends on the illumination taper; it is exposed as
`approximate_half_power_beamwidth_rad` and used only inside the screening
pattern.

Units
-----
Frequency Hz, diameter metres, angles **radians**, gain dBi. Degrees appear only
in a caller's own code.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from itertools import pairwise
from typing import Any, Protocol, runtime_checkable

from aerokit.comms.rf import RfError, gaussian_beam_loss_db, linear_to_db, wavelength_m

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "PARABOLIC_BEAMWIDTH_FACTOR",
    "AntennaPattern",
    "FixedGainAntenna",
    "GaussianBeamPattern",
    "ItuS465ReferencePattern",
    "ParabolicDishAntenna",
    "ScreeningOffAxisPattern",
    "TabulatedPattern",
    "TaperedApertureAntenna",
    "approximate_half_power_beamwidth_rad",
    "parabolic_dish_diameter_m",
    "parabolic_dish_gain_dbi",
    "tapered_aperture_field",
]

# =============================================================================
# 2.                                 CONSTANTS
# =============================================================================

PARABOLIC_BEAMWIDTH_FACTOR: float = 70.0
"""Constant in the ``theta_3dB ~ k lambda / D`` beamwidth rule of thumb, degrees.

Values between about 58 and 75 appear in the literature depending on the
aperture illumination taper. 70 is the figure the migrated source used and is
retained so the screening pattern reproduces it. It is an engineering
approximation, not a property of any particular reflector.
"""

# Below this the off-boresight angle is treated as boresight. A screening
# pattern has no meaningful structure at arcsecond scales, and the logarithm in
# the side-lobe envelope diverges at zero.
_MIN_OFF_BORESIGHT_RAD: float = math.radians(0.05)


# =============================================================================
# 3.                              PATTERN PROTOCOL
# =============================================================================

@runtime_checkable
class AntennaPattern(Protocol):
    """Gain as a function of frequency and direction.

    ``off_boresight_angle_rad`` is the angle from the antenna's electrical
    boresight. ``azimuth_rad`` is the rotation about boresight, for patterns
    that are not rotationally symmetric; every implementation here ignores it,
    and a tabulated pattern would not.
    """

    def gain_dbi(
        self,
        frequency_hz: float,
        off_boresight_angle_rad: float = 0.0,
        azimuth_rad: float | None = None,
    ) -> float: ...


# =============================================================================
# 4.                          DISH GAIN AND BEAMWIDTH
# =============================================================================

def parabolic_dish_gain_dbi(
    diameter_m: float, frequency_hz: float, aperture_efficiency: float
) -> float:
    """Boresight gain of a circular aperture, ``G = eta (pi D / lambda)^2``.

    Exact for a uniformly illuminated circular aperture; ``eta`` absorbs the
    illumination taper, spillover, blockage and surface error of a real
    reflector into one number, which is how a datasheet quotes it.

    Reference: Friis (1946): Simple transmission formula (checked against a secondary source)
    [SIDERA-ALG-COM-001].
    """
    diameter = float(diameter_m)
    if not math.isfinite(diameter) or diameter <= 0.0:
        raise RfError(f"dish diameter must be finite and positive, got {diameter_m!r}")
    efficiency = float(aperture_efficiency)
    if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
        raise RfError(
            f"aperture efficiency must lie in (0, 1], got {aperture_efficiency!r}"
        )
    wavelength = wavelength_m(frequency_hz)
    return linear_to_db(efficiency * (math.pi * diameter / wavelength) ** 2)


def parabolic_dish_diameter_m(
    gain_dbi: float, frequency_hz: float, aperture_efficiency: float
) -> float:
    """Diameter of the circular aperture that gives ``gain_dbi``, the inverse of `parabolic_dish_gain_dbi`.

    ``D = (lambda / pi) sqrt(G / eta)``. Gain is set by the effective aperture
    (``G = 4 pi A_e / lambda^2``), so any antenna type reaching the same gain at
    the same frequency needs a comparable area: at 401.6 MHz with ``eta`` = 0.6,
    20 dBi takes a 3.1 m dish.

    Reference: Friis (1946): Simple transmission formula (checked against a secondary source)
    [SIDERA-ALG-COM-001].
    """
    gain = float(gain_dbi)
    if not math.isfinite(gain):
        raise RfError(f"gain must be finite, got {gain_dbi!r}")
    efficiency = float(aperture_efficiency)
    if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
        raise RfError(
            f"aperture efficiency must lie in (0, 1], got {aperture_efficiency!r}"
        )
    return wavelength_m(frequency_hz) / math.pi * math.sqrt(10.0 ** (gain / 10.0) / efficiency)


def approximate_half_power_beamwidth_rad(diameter_m: float, frequency_hz: float) -> float:
    """``theta_3dB ~ 70 lambda / D`` in radians. An approximation, by name.

    Not a property of any specific reflector: see `PARABOLIC_BEAMWIDTH_FACTOR`.
    """
    diameter = float(diameter_m)
    if not math.isfinite(diameter) or diameter <= 0.0:
        raise RfError(f"dish diameter must be finite and positive, got {diameter_m!r}")
    return math.radians(PARABOLIC_BEAMWIDTH_FACTOR * wavelength_m(frequency_hz) / diameter)


# =============================================================================
# 5.                               ANTENNA MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class FixedGainAntenna:
    """An antenna described only by its boresight gain.

    The gain is returned regardless of direction, so this models perfect
    tracking and nothing else. Pointing loss, if any, belongs in the link's
    engineering losses where it is visible.
    """

    gain_dbi_boresight: float
    name: str = "fixed-gain antenna"

    def __post_init__(self) -> None:
        if not math.isfinite(self.gain_dbi_boresight):
            raise RfError(f"gain must be finite dBi, got {self.gain_dbi_boresight!r}")

    def gain_dbi(
        self,
        frequency_hz: float,
        off_boresight_angle_rad: float = 0.0,
        azimuth_rad: float | None = None,
    ) -> float:
        del frequency_hz, off_boresight_angle_rad, azimuth_rad
        return self.gain_dbi_boresight

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "fixed_gain",
            "name": self.name,
            "gain_dbi_boresight": self.gain_dbi_boresight,
        }


@dataclass(frozen=True, slots=True)
class ParabolicDishAntenna:
    """A circular aperture, described by diameter and efficiency.

    The gain is frequency-dependent, which is the point: the same reflector has
    a different gain on an uplink and a downlink band, and a model that took one
    datasheet number would miss it.

    Off-boresight gain is **not** modelled here -- `gain_dbi` returns the
    boresight value for any angle. A dish's real pattern is a measurement, and
    inventing one silently would be worse than assuming perfect pointing.
    Wrap it in `ScreeningOffAxisPattern` when an off-axis estimate is needed and
    an approximation is acceptable.
    """

    diameter_m: float
    aperture_efficiency: float = 0.62
    name: str = "parabolic dish"

    def __post_init__(self) -> None:
        # Validated by the gain function itself at a probe frequency, so the
        # rules live in exactly one place.
        parabolic_dish_gain_dbi(self.diameter_m, 1.0e9, self.aperture_efficiency)

    def gain_dbi(
        self,
        frequency_hz: float,
        off_boresight_angle_rad: float = 0.0,
        azimuth_rad: float | None = None,
    ) -> float:
        del off_boresight_angle_rad, azimuth_rad
        return parabolic_dish_gain_dbi(
            self.diameter_m, frequency_hz, self.aperture_efficiency
        )

    def half_power_beamwidth_rad(self, frequency_hz: float) -> float:
        """The approximate beamwidth. See `approximate_half_power_beamwidth_rad`."""
        return approximate_half_power_beamwidth_rad(self.diameter_m, frequency_hz)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "parabolic_dish",
            "name": self.name,
            "diameter_m": self.diameter_m,
            "aperture_efficiency": self.aperture_efficiency,
        }


@dataclass(frozen=True, slots=True)
class ScreeningOffAxisPattern:
    """A first-pass off-axis envelope for interference **screening**.

    Combines a quadratic main-lobe roll-off with a logarithmic side-lobe
    envelope of the form ``A - B log10(theta_deg)``. Both parts are engineering
    approximations chosen to show discrimination *trends*.

    This is emphatically not:

    - a measured radiation pattern,
    - a regulatory coordination mask,
    - a basis for a filing or an interference finding.

    It exists so an adjacent-emitter screening study can ask "roughly how much
    discrimination does this aperture give at 3 degrees off-axis" and get an
    answer that is the right order of magnitude. Any result derived from it
    should be labelled as screening, and the interference models that use it do.

    The default envelope constants ``32`` and ``25`` are the values used by the
    migrated source. They resemble the classical ``32 - 25 log(theta)`` sidelobe
    reference, but nothing here enforces the conditions under which that
    reference applies.

    Reference: none, a Sidera heuristic without a published source [SIDERA-HEUR-COM-001].
    """

    base: AntennaPattern
    envelope_constant_a_db: float = 32.0
    envelope_constant_b_db: float = 25.0
    beamwidth_rad: float | None = None
    """Main-lobe width. Taken from the base antenna when it can supply one."""

    def __post_init__(self) -> None:
        for name in ("envelope_constant_a_db", "envelope_constant_b_db"):
            if not math.isfinite(float(getattr(self, name))):
                raise RfError(f"{name} must be finite dB")
        width = self.beamwidth_rad
        if width is not None and (not math.isfinite(width) or width <= 0.0):
            raise RfError(f"beamwidth must be finite and positive radians, got {width!r}")

    def _main_lobe_width_rad(self, frequency_hz: float) -> float:
        if self.beamwidth_rad is not None:
            return self.beamwidth_rad
        width = getattr(self.base, "half_power_beamwidth_rad", None)
        if width is not None:
            return float(width(frequency_hz))
        # No aperture to derive a width from: protect a small boresight cone and
        # fall straight to the envelope outside it.
        return _MIN_OFF_BORESIGHT_RAD * 5.0

    def gain_dbi(
        self,
        frequency_hz: float,
        off_boresight_angle_rad: float = 0.0,
        azimuth_rad: float | None = None,
    ) -> float:
        boresight = self.base.gain_dbi(frequency_hz, 0.0, azimuth_rad)
        angle = abs(float(off_boresight_angle_rad))
        if not math.isfinite(angle):
            raise RfError(f"off-boresight angle must be finite, got {off_boresight_angle_rad!r}")
        width = max(self._main_lobe_width_rad(frequency_hz), _MIN_OFF_BORESIGHT_RAD)

        if angle <= width:
            # Quadratic roll-off reaching about 12 dB down at the stated width.
            # The true angle is used here, so boresight returns boresight gain;
            # the floor below exists only to keep the envelope's logarithm
            # finite and must not leak into the main lobe.
            return boresight - 12.0 * (angle / width) ** 2

        envelope = (
            self.envelope_constant_a_db
            - self.envelope_constant_b_db
            * math.log10(math.degrees(max(angle, _MIN_OFF_BORESIGHT_RAD)))
        )
        # Capped at the main lobe's own edge value (boresight - 12 dB, the
        # quadratic branch's value at angle == width), not a looser boresight -
        # 3 dB: for a narrow beam (width under 1 degree) the raw envelope is
        # boosted just past the edge -- log10(degrees) is negative there -- and
        # a looser cap let the reported gain jump *up* right outside the main
        # lobe. `envelope` itself is monotonically non-increasing in angle
        # (deg(angle) and log10 both increasing), so once the envelope drops
        # below the cap the combined curve keeps falling with it.
        return min(boresight - 12.0, envelope)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "screening_off_axis",
            "screening_only": True,
            "base": getattr(self.base, "as_dict", dict)(),
            "envelope_constant_a_db": self.envelope_constant_a_db,
            "envelope_constant_b_db": self.envelope_constant_b_db,
        }


# =============================================================================
# 6.                         RADIATION PATTERN MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class GaussianBeamPattern:
    """A Gaussian main beam: ``G(theta) = G0 - 10 k (theta / H)^2 / ln 10`` dBi, ``k = 4 ln 2``.

    The usual main-lobe model of a pointed high-gain antenna (DSN 810-005 104
    eq. A-3 is the same curve). It has no side lobes, so it is refused beyond
    ``valid_to_hpbw`` half-power beamwidths rather than returning a loss that
    keeps growing where a real antenna has side lobes; use
    `TaperedApertureAntenna` or a measured `TabulatedPattern` there.

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """

    boresight_gain_dbi: float
    half_power_beamwidth_rad: float
    valid_to_hpbw: float = 1.5
    name: str = "Gaussian beam"

    def __post_init__(self) -> None:
        if not math.isfinite(self.boresight_gain_dbi):
            raise RfError("boresight gain must be finite dBi")
        h = float(self.half_power_beamwidth_rad)
        if not (math.isfinite(h) and 0.0 < h < math.pi):
            raise RfError(f"half-power beamwidth must lie in (0, pi) rad, got {self.half_power_beamwidth_rad!r}")
        if not (math.isfinite(self.valid_to_hpbw) and self.valid_to_hpbw > 0.0):
            raise RfError("valid_to_hpbw must be finite and > 0")

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float:
        del frequency_hz, azimuth_rad
        theta = abs(float(off_boresight_angle_rad))
        if theta > self.valid_to_hpbw * self.half_power_beamwidth_rad:
            raise RfError(
                f"{self.name}: {math.degrees(theta):.3f} deg is beyond the main lobe this model covers "
                f"({self.valid_to_hpbw} x HPBW = "
                f"{math.degrees(self.valid_to_hpbw * self.half_power_beamwidth_rad):.3f} deg)"
            )
        return self.boresight_gain_dbi - gaussian_beam_loss_db(theta, self.half_power_beamwidth_rad)

    def half_power_beamwidth(self, frequency_hz: float) -> float:
        del frequency_hz
        return self.half_power_beamwidth_rad


def tapered_aperture_field(u: float, taper_p: int) -> float:
    """Normalised far field ``Lambda_{p+1}(u) = 2^{p+1} (p+1)! J_{p+1}(u) / u^{p+1}`` of a circular aperture.

    Aperture illumination ``(1 - rho^2)^p`` (``rho`` the normalised radius;
    ``p = 0`` uniform). ``u = pi D sin(theta) / lambda``. ``Lambda(0) = 1``.

    Reference: National Institute of Standards and Technology (2026), Eq. 10.22.19
    [SIDERA-ALG-COM-013].
    """
    from scipy.special import (
        jv,  # scipy is a core dependency; imported here to keep the module light
    )

    p = int(taper_p)
    x = abs(float(u))
    if x < 1e-6:
        # Series: Lambda = 1 - x^2 / (4 (p + 2)) + O(x^4); the closed form loses digits near 0.
        return 1.0 - x * x / (4.0 * (p + 2))
    return float(2.0 ** (p + 1) * math.factorial(p + 1) * jv(p + 1, x) / x ** (p + 1))


@dataclass(frozen=True, slots=True)
class TaperedApertureAntenna:
    """A circular aperture with a ``(1 - rho^2)^p`` illumination taper: main lobe, nulls and side lobes.

    ``G(theta) = G0 + 20 log10 |Lambda_{p+1}(pi D sin(theta) / lambda)|`` with
    ``G0 = eta (pi D / lambda)^2``; ``aperture_efficiency`` is the total
    efficiency (taper, spill-over, blockage, surface), as a datasheet quotes
    it, and must not exceed the taper efficiency ``(2p + 1) / (p + 1)^2``.
    Half-power beamwidth: 1.029, 1.270, 1.473 lambda/D for p = 0, 1, 2; first
    side lobe -17.6, -24.6, -30.6 dB. MRO's 3 m HGA (HPBW 0.69 deg at
    8.4 GHz, DESCANSO 12 table 2-2) is 1.02 lambda/D, near-uniform.

    Exact nulls of the ideal aperture are floored at ``null_depth_db`` below
    boresight (a real reflector fills them by blockage and surface error), and
    beyond 90 deg the gain is ``rear_gain_dbi`` (default -10 dBi, the
    far-sidelobe level of ITU-R S.465-6): the aperture formula is a
    forward-hemisphere result.

    Reference: National Institute of Standards and Technology (2026), Eq. 10.22.19
    [SIDERA-ALG-COM-013].
    """

    diameter_m: float
    aperture_efficiency: float
    taper_p: int = 1
    null_depth_db: float = 60.0
    rear_gain_dbi: float = -10.0
    name: str = "tapered aperture"

    def __post_init__(self) -> None:
        parabolic_dish_gain_dbi(self.diameter_m, 1.0e9, self.aperture_efficiency)
        if int(self.taper_p) != self.taper_p or not 0 <= self.taper_p <= 4:
            raise RfError(f"taper_p must be an integer 0..4, got {self.taper_p!r}")
        if self.aperture_efficiency > self.taper_efficiency + 1e-12:
            raise RfError(f"aperture efficiency {self.aperture_efficiency} exceeds the taper efficiency "
                          f"{self.taper_efficiency:.4f} of p = {self.taper_p}")
        if not (math.isfinite(self.null_depth_db) and self.null_depth_db > 0.0):
            raise RfError("null_depth_db must be finite and > 0")

    @property
    def taper_efficiency(self) -> float:
        """``(2p + 1) / (p + 1)^2``: 1 (uniform), 0.75 (p = 1), 0.556 (p = 2)."""
        p = int(self.taper_p)
        return (2 * p + 1) / (p + 1) ** 2

    def boresight_gain_dbi(self, frequency_hz: float) -> float:
        return parabolic_dish_gain_dbi(self.diameter_m, frequency_hz, self.aperture_efficiency)

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float:
        del azimuth_rad
        theta = abs(float(off_boresight_angle_rad))
        if not math.isfinite(theta):
            raise RfError(f"off-boresight angle must be finite, got {off_boresight_angle_rad!r}")
        g0 = self.boresight_gain_dbi(frequency_hz)
        if theta > 0.5 * math.pi:
            return self.rear_gain_dbi
        u = math.pi * self.diameter_m * math.sin(theta) / wavelength_m(frequency_hz)
        field = abs(tapered_aperture_field(u, self.taper_p))
        floor = 10.0 ** (-self.null_depth_db / 20.0)
        return g0 + 20.0 * math.log10(max(field, floor))

    def half_power_beamwidth(self, frequency_hz: float) -> float:
        """Full width between the -3.0103 dB points [rad] (root of ``Lambda^2 = 1/2``)."""
        from scipy.optimize import brentq

        u_half = brentq(lambda u: tapered_aperture_field(u, self.taper_p) ** 2 - 0.5, 1e-3, 3.83 + self.taper_p * 1.6,
                        xtol=1e-14)
        return 2.0 * math.asin(u_half * wavelength_m(frequency_hz) / (math.pi * self.diameter_m))


@dataclass(frozen=True, slots=True)
class TabulatedPattern:
    """A measured or published pattern: gain [dBi] at off-boresight angles, optionally per azimuth cut.

    ``theta_rad`` increasing from 0; ``gain_dbi`` shaped ``(n_theta,)`` for a
    rotationally symmetric pattern or ``(n_phi, n_theta)`` with ``phi_rad``
    the cut azimuths (increasing, within one turn). Linear interpolation in
    dB along theta, then between the two neighbouring cuts in azimuth
    (periodic). Angles outside the table are refused. ``screening_only``
    marks a pattern read off a figure, and ``source`` says which.
    """

    theta_rad: tuple[float, ...]
    gain_dbi_table: tuple[float, ...] | tuple[tuple[float, ...], ...]
    phi_rad: tuple[float, ...] | None = None
    source: str = ""
    screening_only: bool = False
    name: str = "tabulated pattern"

    def __post_init__(self) -> None:
        theta = tuple(float(t) for t in self.theta_rad)
        if len(theta) < 2 or theta[0] != 0.0 or any(b <= a for a, b in pairwise(theta)) \
                or theta[-1] > math.pi:
            raise RfError("theta_rad must start at 0, increase strictly and end at or below pi")
        object.__setattr__(self, "theta_rad", theta)
        if self.phi_rad is None:
            row = tuple(float(g) for g in self.gain_dbi_table)  # type: ignore[arg-type]
            if len(row) != len(theta) or not all(math.isfinite(g) for g in row):
                raise RfError("gain_dbi_table must hold one finite dBi value per theta")
            object.__setattr__(self, "gain_dbi_table", row)
        else:
            phi = tuple(float(f) for f in self.phi_rad)
            if any(b <= a for a, b in pairwise(phi)) or phi[-1] - phi[0] >= 2.0 * math.pi:
                raise RfError("phi_rad must increase strictly within one turn")
            rows = tuple(tuple(float(g) for g in r) for r in self.gain_dbi_table)  # type: ignore[union-attr]
            if len(rows) != len(phi) or any(len(r) != len(theta) for r in rows) \
                    or not all(math.isfinite(g) for r in rows for g in r):
                raise RfError("gain_dbi_table must be (n_phi, n_theta) finite dBi values")
            object.__setattr__(self, "phi_rad", phi)
            object.__setattr__(self, "gain_dbi_table", rows)

    def _cut(self, row: tuple[float, ...], theta: float) -> float:
        t = self.theta_rad
        if theta > t[-1] + 1e-12:
            raise RfError(f"{self.name}: {math.degrees(theta):.2f} deg is outside the table (to "
                          f"{math.degrees(t[-1]):.2f} deg)")
        k = min(max(bisect_right(t, theta) - 1, 0), len(t) - 2)
        f = (theta - t[k]) / (t[k + 1] - t[k])
        return row[k] + f * (row[k + 1] - row[k])

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float:
        del frequency_hz
        theta = abs(float(off_boresight_angle_rad))
        if self.phi_rad is None:
            return self._cut(self.gain_dbi_table, theta)  # type: ignore[arg-type]
        if azimuth_rad is None:
            raise RfError(f"{self.name}: a pattern with azimuth cuts needs the azimuth about boresight")
        phi = self.phi_rad
        rows: tuple[tuple[float, ...], ...] = self.gain_dbi_table  # type: ignore[assignment]
        a = phi[0] + (float(azimuth_rad) - phi[0]) % (2.0 * math.pi)
        k = bisect_right(phi, a) - 1
        lo, hi = phi[k], (phi[k + 1] if k + 1 < len(phi) else phi[0] + 2.0 * math.pi)
        g_lo = self._cut(rows[k], theta)
        g_hi = self._cut(rows[(k + 1) % len(phi)], theta)
        return g_lo + (a - lo) / (hi - lo) * (g_hi - g_lo)


@dataclass(frozen=True, slots=True)
class ItuS465ReferencePattern:
    """ITU-R S.465-6 reference earth-station pattern (2-31 GHz) for coordination and interference.

    ``G = 32 - 25 log10(phi)`` dBi for ``phi_min <= phi < 48`` deg and -10 dBi
    from 48 to 180 deg, with ``phi_min = max(1, 100 lambda/D)`` deg for
    ``D/lambda >= 50`` and ``max(2, 114 (D/lambda)^-1.09)`` deg below (2.5 deg
    for receiving antennas with ``D/lambda < 33.3``, note 5). Inside
    ``phi_min`` the Recommendation gives no gain; this model then returns the
    boresight gain ``eta (pi D / lambda)^2`` only up to the half-power point of
    a Gaussian beam with ``HPBW = 70 lambda/D`` and refuses between there and
    ``phi_min``, since the Recommendation is an envelope for side lobes, not a
    main-beam model.

    Reference: Recommendation ITU-R S.465-6 (2010): recommends 2 and notes 1-5 [SIDERA-STD-COM-006].
    """

    diameter_m: float
    aperture_efficiency: float = 0.65
    receiving: bool = True
    name: str = "ITU-R S.465-6 reference pattern"

    def __post_init__(self) -> None:
        parabolic_dish_gain_dbi(self.diameter_m, 1.0e9, self.aperture_efficiency)

    def phi_min_deg(self, frequency_hz: float) -> float:
        f = float(frequency_hz)
        if not 2.0e9 <= f <= 31.0e9:
            raise RfError(f"ITU-R S.465-6 covers 2 to 31 GHz, got {f / 1e9:.3f} GHz")
        d_over_l = self.diameter_m / wavelength_m(f)
        if d_over_l >= 50.0:
            return max(1.0, 100.0 / d_over_l)
        if self.receiving and d_over_l < 33.3:
            return 2.5
        return max(2.0, 114.0 * d_over_l ** -1.09)

    def gain_dbi(self, frequency_hz: float, off_boresight_angle_rad: float = 0.0,
                 azimuth_rad: float | None = None) -> float:
        del azimuth_rad
        phi = math.degrees(abs(float(off_boresight_angle_rad)))
        phi_min = self.phi_min_deg(frequency_hz)
        if phi >= 48.0:
            return -10.0
        if phi >= phi_min:
            return 32.0 - 25.0 * math.log10(phi)
        g0 = parabolic_dish_gain_dbi(self.diameter_m, frequency_hz, self.aperture_efficiency)
        hpbw_deg = PARABOLIC_BEAMWIDTH_FACTOR * wavelength_m(frequency_hz) / self.diameter_m
        if phi <= 0.5 * hpbw_deg:
            return g0 - gaussian_beam_loss_db(phi, hpbw_deg)
        raise RfError(f"{self.name}: {phi:.3f} deg lies between the main beam and phi_min = {phi_min:.3f} deg, "
                      "where the Recommendation gives no gain")

