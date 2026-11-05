# Copied from Sidera (sidera.communications.rf, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Radio-frequency primitives: the pure equations, in SI.

Everything here is a few lines of named algebra over quantities defined in the
docstring, so a reader who wants to check a number against a textbook can read
the formula rather than trust the name.

Logarithmic quantities
----------------------
The single largest source of silent error in link analysis is mixing decibel
quantities that reference different things. ``dB`` is a bare ratio, ``dBW`` is
referenced to one watt, ``dBi`` to an isotropic radiator, ``dB-Hz`` to one hertz,
and ``dB/K`` is a gain-to-temperature ratio. Adding a ``dBW`` to a ``dB`` is
meaningful; adding two ``dBW`` values is not.

Sidera keeps the reference in the name of every function and every argument, as
the rest of the package does with units. There is no wrapper class: a float with
an unambiguous name matches Sidera's style and does not pretend the type system
is checking something it is not.

Two ratios that are *independently* degrading the same carrier combine in the
linear domain, not by adding decibels. `combine_inverse_ratios_db` is the only
correct way to put a thermal ``C/N`` together with an interference ``C/I``.

Units
-----
Frequency Hz, distance metres, power watts or dBW at logarithmic boundaries,
temperature kelvin, data rate bit/s, bandwidth Hz, angles radians. Kilometres and
gigahertz appear only where a caller's convenience function converts at the
boundary -- never inside the physics.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from collections.abc import Iterable

from aerokit.comms.constants import BOLTZMANN_J_PER_K, C_LIGHT
from aerokit.comms.errors import SideraError

# =============================================================================
# 1.                            PUBLIC API (__all__)
# =============================================================================

__all__ = [
    "AnalysisCancelled",
    "BOLTZMANN_DB_W_PER_K_HZ",
    "RfError",
    "carrier_to_noise_density_dbhz",
    "carrier_to_noise_from_density_db",
    "combine_inverse_ratios_db",
    "db_to_linear",
    "dbw_to_watts",
    "ebn0_from_carrier_to_noise_db",
    "ebn0_from_density_db",
    "free_space_path_loss_db",
    "gaussian_beam_loss_db",
    "linear_to_db",
    "noise_power_dbw",
    "polarization_mismatch_loss_db",
    "watts_to_dbw",
    "wavelength_m",
]

# =============================================================================
# 2.                                 CONSTANTS
# =============================================================================

BOLTZMANN_DB_W_PER_K_HZ: float = 10.0 * math.log10(BOLTZMANN_J_PER_K)
"""``10 log10(k)`` = -228.599... dB(W/K/Hz).

The link equation is conventionally written with ``-228.6`` added; that is this
constant negated. It is computed from Sidera's Boltzmann constant rather than
written as a rounded literal, so it carries the same provenance as every other
physical constant in the package.
"""


# =============================================================================
# 3.                                 EXCEPTIONS
# =============================================================================

class RfError(SideraError, ValueError):
    """An RF quantity was requested where it is not defined."""


class AnalysisCancelled(RfError):
    """A long analysis stopped because its caller asked it to.

    Raised from inside the loop, between samples, so nothing half-written is
    returned. A desktop worker raises the request when its window closes.
    """


# =============================================================================
# 4.                              PRIVATE HELPERS
# =============================================================================

def _positive(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise RfError(f"{name} must be finite and positive, got {value!r}")
    return number


# ---------------------------------------------------------------------------
# Decibel conversions
# ---------------------------------------------------------------------------

# =============================================================================
# 5.                               LINK EQUATIONS
# =============================================================================

def linear_to_db(ratio: float) -> float:
    """``10 log10(ratio)`` for a positive power ratio.

    Power ratios, not amplitude ratios: the factor is 10, not 20. Everything in
    this module is a power quantity.
    """
    return 10.0 * math.log10(_positive(ratio, "ratio"))


def db_to_linear(value_db: float) -> float:
    """Inverse of `linear_to_db`. Accepts any finite decibel value."""
    number = float(value_db)
    if not math.isfinite(number):
        raise RfError(f"decibel value must be finite, got {value_db!r}")
    return 10.0 ** (number / 10.0)


def watts_to_dbw(power_w: float) -> float:
    """Power in watts to dBW, referenced to one watt."""
    return 10.0 * math.log10(_positive(power_w, "power"))


def dbw_to_watts(power_dbw: float) -> float:
    """dBW back to watts."""
    return db_to_linear(power_dbw)


# ---------------------------------------------------------------------------
# Propagation
# ---------------------------------------------------------------------------

def wavelength_m(frequency_hz: float) -> float:
    """``c / f``, in metres."""
    return C_LIGHT / _positive(frequency_hz, "frequency")


def free_space_path_loss_db(range_m: float, frequency_hz: float) -> float:
    """Free-space path loss, ``20 log10(4 pi R f / c)``.

    Computed in SI from the defining expression rather than from a
    frequency-in-GHz, range-in-km form with a pre-rounded constant. The common
    engineering shorthand uses ``92.45``; the exact value of that constant is
    ``92.44782...``, so the shorthand biases every link high by about
    ``0.0022 dB``. Small, systematic, and avoidable.

    This is the loss of an ideal isotropic path: the spreading of power over a
    sphere, with the ``f`` dependence coming from the receive aperture implied by
    an isotropic antenna. It is not an absorption.

    Reference: Friis (1946): Simple transmission formula (checked against a secondary source)
    [SIDERA-ALG-COM-001].
    """
    distance = _positive(range_m, "range")
    frequency = _positive(frequency_hz, "frequency")
    return 20.0 * math.log10(4.0 * math.pi * distance * frequency / C_LIGHT)


# ---------------------------------------------------------------------------
# Noise and carrier-to-noise quantities
# ---------------------------------------------------------------------------

def gaussian_beam_loss_db(off_boresight_rad: float, half_power_beamwidth_rad: float,
                          *, k: float = 4.0 * math.log(2.0)) -> float:
    """Gain reduction [dB, >= 0] of a Gaussian main beam: ``10 k (theta / H)^2 / ln 10``.

    ``G(theta) / G0 = exp(-k theta^2 / H^2)`` with ``H`` the full half-power
    beamwidth; ``k = 4 ln 2`` puts the half-power point at ``theta = H / 2``.
    DSN 810-005 104 eq. A-3 rounds ``k`` to 2.773 (1.3e-4 relative). Both
    angles in the same unit. A main-lobe model: beyond about the first null it
    has no meaning (`GaussianBeamPattern` refuses there).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """
    error, hpbw, kk = float(off_boresight_rad), float(half_power_beamwidth_rad), float(k)
    if not (math.isfinite(error) and math.isfinite(hpbw) and hpbw > 0.0 and math.isfinite(kk) and kk > 0.0):
        raise RfError("the angle must be finite, the beamwidth and k finite and positive")
    return 10.0 * kk * (error / hpbw) ** 2 / math.log(10.0)


def polarization_mismatch_loss_db(axial_ratio_tx_db: float, axial_ratio_rx_db: float, *, same_sense: bool = True,
                                  tilt_rad: float = 0.0) -> float:
    """Power lost [dB, >= 0] between two elliptically polarised antennas, from their axial ratios.

    Each polarisation is a point on the Poincare sphere at longitude
    ``2 tau`` (tilt of the major axis) and latitude ``2 eps``, with the
    ellipticity angle ``eps = +-atan(1 / r)`` (``r`` the voltage axial ratio,
    ``r = 10^(AR_dB / 20) >= 1``; the sign is the sense of rotation). The
    fraction of the power the receiving antenna takes is ``(1 + cos g) / 2``
    with ``g`` the angle between the wave's point and the antenna's matched
    point: ``cos g = sin 2e1 sin 2e2 + cos 2e1 cos 2e2 cos 2(t1 - t2)``. Special
    cases: two circular antennas of the same sense lose nothing, of opposite
    sense everything (``inf``); linear against circular 3.01 dB; two linear
    antennas ``cos^2`` of the angle between them. ``tilt_rad`` is the angle
    between the two major axes (the loss is worst at 90 deg for the same sense).
    ``AR_dB = 0`` is circular; a very large ``AR_dB`` tends to linear.

    Reference: none, a Sidera heuristic without a published source [SIDERA-HEUR-COM-007].
    """
    values = (float(axial_ratio_tx_db), float(axial_ratio_rx_db), float(tilt_rad))
    if not all(math.isfinite(v) for v in values) or values[0] < 0.0 or values[1] < 0.0:
        raise RfError("axial ratios must be finite and >= 0 dB, the tilt finite")
    e1 = math.atan(10.0 ** (-values[0] / 20.0))
    e2 = math.atan(10.0 ** (-values[1] / 20.0)) * (1.0 if same_sense else -1.0)
    cos_g = math.sin(2 * e1) * math.sin(2 * e2) + math.cos(2 * e1) * math.cos(2 * e2) * math.cos(2 * values[2])
    factor = 0.5 * (1.0 + max(-1.0, min(1.0, cos_g)))
    return math.inf if factor <= 0.0 else -10.0 * math.log10(factor)


def noise_power_dbw(system_noise_temperature_k: float, bandwidth_hz: float) -> float:
    """Thermal noise power ``N = k T B``, in dBW.
    """
    temperature = _positive(system_noise_temperature_k, "system noise temperature")
    bandwidth = _positive(bandwidth_hz, "bandwidth")
    return BOLTZMANN_DB_W_PER_K_HZ + linear_to_db(temperature) + linear_to_db(bandwidth)


def carrier_to_noise_density_dbhz(
    eirp_dbw: float,
    g_over_t_db_per_k: float,
    total_path_loss_db: float,
) -> float:
    """``C/N0 = EIRP + G/T - L - 10 log10(k)``, in dB-Hz.

    ``total_path_loss_db`` is every loss between the transmit antenna's output
    and the receive antenna's output: free space, environmental attenuation and
    fixed engineering losses. It is a positive number for a real link.

    Note the sign: Boltzmann's constant enters as ``-10 log10(k)``, which is
    ``+228.6``, and `BOLTZMANN_DB_W_PER_K_HZ` is the *negative* of that.

    Reference: Friis (1946): Simple transmission formula (checked against a secondary source)
    [SIDERA-ALG-COM-001].
    """
    for name, value in (
        ("EIRP", eirp_dbw),
        ("G/T", g_over_t_db_per_k),
        ("total path loss", total_path_loss_db),
    ):
        if not math.isfinite(float(value)):
            raise RfError(f"{name} must be finite, got {value!r}")
    return (
        float(eirp_dbw)
        + float(g_over_t_db_per_k)
        - float(total_path_loss_db)
        - BOLTZMANN_DB_W_PER_K_HZ
    )


def carrier_to_noise_from_density_db(cn0_dbhz: float, bandwidth_hz: float) -> float:
    """``C/N = C/N0 - 10 log10(B)``, the ratio in a stated bandwidth."""
    return float(cn0_dbhz) - linear_to_db(_positive(bandwidth_hz, "bandwidth"))


def ebn0_from_density_db(cn0_dbhz: float, bit_rate_bps: float) -> float:
    """``Eb/N0 = C/N0 - 10 log10(Rb)``, energy per information bit."""
    return float(cn0_dbhz) - linear_to_db(_positive(bit_rate_bps, "bit rate"))


def ebn0_from_carrier_to_noise_db(
    cn_db: float, bandwidth_hz: float, bit_rate_bps: float
) -> float:
    """``Eb/N0 = C/N + 10 log10(B / Rb)``.

    The same quantity as `ebn0_from_density_db` reached from a bandwidth-referred
    ratio. Both are provided because link budgets are quoted both ways, and a
    test asserts they agree.
    """
    bandwidth = _positive(bandwidth_hz, "bandwidth")
    rate = _positive(bit_rate_bps, "bit rate")
    return float(cn_db) + linear_to_db(bandwidth / rate)


def combine_inverse_ratios_db(values_db: Iterable[float | None]) -> float:
    """Combine independently degrading ratios: ``1/X = sum(1/X_i)``.

    A thermal ``C/N`` and an interference ``C/I`` both reduce the same carrier's
    effective quality, and they combine as noise powers add -- in the **linear**
    domain. Adding the decibel values instead is a common and severe error: two
    10 dB contributions combine to 6.99 dB, not 20 dB.

    ``None`` entries are skipped, so an optional impairment that is not modelled
    contributes nothing rather than defaulting to something.
    """
    inverse_sum = 0.0
    used = 0
    for value_db in values_db:
        if value_db is None:
            continue
        number = float(value_db)
        if not math.isfinite(number):
            raise RfError(f"ratio must be finite dB, got {value_db!r}")
        inverse_sum += 1.0 / db_to_linear(number)
        used += 1
    if used == 0:
        raise RfError("at least one finite dB ratio is required to combine")
    if inverse_sum <= 0.0:  # pragma: no cover - unreachable for finite inputs
        raise RfError("the combined ratio is not positive")
    return linear_to_db(1.0 / inverse_sum)
