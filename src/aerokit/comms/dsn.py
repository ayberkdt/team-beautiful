# Copied from Sidera (sidera.communications.ground.dsn, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""NASA Deep Space Network ground antennas as the DSN's own link-design handbook models them.

JPL's DSN Telecommunications Link Design Handbook (810-005) gives, for each
34-m beam-waveguide antenna and configuration, a vacuum gain that peaks at an
elevation ``gamma`` and falls off as the reflector deforms under gravity, and
an antenna-microwave noise temperature that rises towards the horizon
(module 104, Rev. Q, Appendix A):

    G(theta)    = G0 - G1 (theta - gamma)^2 - A_zen / sin(theta)      dBi   (A-1)
    T_AMW       = T1 + T2 exp(-a theta)                               K     (A3)
    T_op        = T_AMW + T_atm + T_CMB'                              K     (A2, A4)
    T_atm       = T_p (1 - 1/L),  T_p = 255 + 25 CD,  L = 10^(A/10)   K     (A6-A8)
    T_CMB'      = 2.725 / L                                           K     (A9)
    A(theta)    = A_zen / sin(theta)                                  dB    (A5)

valid for 6 <= theta <= 90 deg, with ``A_zen`` the zenith attenuation at the
weather's cumulative distribution ``CD`` (module 104 Table A-5, from module
105 Rev. E). The handbook's own advice is kept: the atmospheric attenuation is
a line item of its own and is not folded into the antenna gain again
(:mod:`aerokit.comms.dsn_atmosphere` carries it).

The catalog holds the receive configurations of each complex's beam-waveguide
antennas at X (8425 MHz) and Ka (32050 MHz) band, read from the handbook's
tables (page images, 104 Rev. Q of 2026-08-03), and the station positions of
module 301 Rev. P Table 2 (ITRF93, epoch 2003.03, +-3 cm).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from aerokit.comms.rf import RfError, gaussian_beam_loss_db

Band = Literal["X", "Ka"]
Complex = Literal["goldstone", "canberra", "madrid"]

#: Cosmic microwave background [K] (810-005 module 105 Rev. E, eq. 4).
T_CMB_K = 2.725
#: The handbook's elevation range of validity [deg] (module 104 Appendix A).
MIN_ELEVATION_DEG, MAX_ELEVATION_DEG = 6.0, 90.0

#: Zenith atmospheric attenuation [dB] by complex, band and cumulative distribution
#: (810-005 module 104 Rev. Q Table A-5, "Module 105, Rev. E, 10/2015").
ZENITH_ATTENUATION_DB: dict[Complex, dict[Band, dict[float, float]]] = {
    "goldstone": {"X": {0.00: 0.037, 0.25: 0.039, 0.50: 0.040, 0.90: 0.045},
                  "Ka": {0.00: 0.116, 0.25: 0.150, 0.50: 0.171, 0.90: 0.239}},
    "canberra": {"X": {0.00: 0.039, 0.25: 0.045, 0.50: 0.047, 0.90: 0.057},
                 "Ka": {0.00: 0.124, 0.25: 0.208, 0.50: 0.238, 0.90: 0.384}},
    "madrid": {"X": {0.00: 0.038, 0.25: 0.043, 0.50: 0.045, 0.90: 0.058},
               "Ka": {0.00: 0.121, 0.25: 0.192, 0.50: 0.221, 0.90: 0.407}},
}


def zenith_attenuation_db(complex_name: Complex, band: Band, cumulative_distribution: float) -> float:
    """``A_zen`` [dB] from 104 Table A-5; only its four weather levels (0, 0.25, 0.5, 0.9) are tabulated.

    Other levels are in module 105 Tables 13-18 by month; they are not interpolated here.
    """
    try:
        by_cd = ZENITH_ATTENUATION_DB[complex_name][band]
    except KeyError as error:
        raise RfError(f"no DSN zenith attenuation for complex {complex_name!r}, band {band!r}") from error
    cd = float(cumulative_distribution)
    if cd not in by_cd:
        raise RfError(f"the zenith attenuation is tabulated at CD = {sorted(by_cd)} only, got {cd!r}")
    return by_cd[cd]


def atmosphere_attenuation_db(zenith_db: float, elevation_deg: float) -> float:
    """``A = A_zen / sin(theta)`` [dB], flat-Earth air masses (105 Rev. E eq. 2; valid to 1-3 % at 6 deg).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """
    _check_elevation(elevation_deg)
    return float(zenith_db) / math.sin(math.radians(float(elevation_deg)))


def sky_noise_temperature_k(attenuation_db: float, cumulative_distribution: float) -> float:
    """``T_atm + T_CMB'`` [K] for an atmospheric attenuation ``A`` (105 Rev. E eqs. 1, 3-5).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """
    cd = float(cumulative_distribution)
    if not 0.0 <= cd <= 0.99:
        raise RfError(f"the cumulative distribution must lie in [0, 0.99], got {cd!r}")
    a = float(attenuation_db)
    if not (math.isfinite(a) and a >= 0.0):
        raise RfError(f"the attenuation must be finite and non-negative dB, got {a!r}")
    loss = 10.0 ** (a / 10.0)
    return (255.0 + 25.0 * cd) * (1.0 - 1.0 / loss) + T_CMB_K / loss


def pointing_loss_db(pointing_error_deg: float, half_power_beamwidth_deg: float) -> float:
    """The gain reduction [dB, >= 0] for a pointing error: ``-10 log10(exp(-2.773 e^2 / HPBW^2))`` (104 eq. A-3).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """
    error, hpbw = float(pointing_error_deg), float(half_power_beamwidth_deg)
    if not (math.isfinite(error) and math.isfinite(hpbw) and hpbw > 0.0):
        raise RfError("the pointing error must be finite and the beamwidth finite and positive")
    return gaussian_beam_loss_db(error, hpbw, k=2.773)


def _check_elevation(elevation_deg: float) -> None:
    theta = float(elevation_deg)
    if not MIN_ELEVATION_DEG <= theta <= MAX_ELEVATION_DEG:
        raise RfError(f"the DSN antenna models hold for 6 <= elevation <= 90 deg, got {theta!r}")


@dataclass(frozen=True, slots=True)
class DsnAntenna:
    """One DSN antenna in one receive configuration (810-005 module 104 Appendix A).

    ``itrf93_position_m`` is module 301 Rev. P Table 2 (epoch 2003.03).

    Reference: DSN No. 810-005, 104, Rev. Q (2026), formula A-1; A2; A3; A4; A5; A6; A7; A8; A9; A-3
    [SIDERA-STD-COM-001].
    """

    station: str
    complex_name: Complex
    band: Band
    configuration: str
    g0_receive_dbi: float
    g1_db_per_deg2: float
    gamma_deg: float
    t1_k: float
    t2_k: float
    a_per_deg: float
    itrf93_position_m: tuple[float, float, float]
    source: str

    @property
    def frequency_hz(self) -> float:
        """The nominal deep-space downlink frequency the table holds for (8425 or 32050 MHz)."""
        return 8.425e9 if self.band == "X" else 32.05e9

    def vacuum_gain_dbi(self, elevation_deg: float) -> float:
        """``G0 - G1 (theta - gamma)^2`` [dBi]: the gain without the atmosphere (104 eq. A-1)."""
        _check_elevation(elevation_deg)
        return self.g0_receive_dbi - self.elevation_gain_loss_db(elevation_deg)

    def elevation_gain_loss_db(self, elevation_deg: float) -> float:
        """``G1 (theta - gamma)^2`` [dB, >= 0]: the gravity-deformation loss below the peak gain."""
        _check_elevation(elevation_deg)
        return self.g1_db_per_deg2 * (float(elevation_deg) - self.gamma_deg) ** 2

    def antenna_microwave_temperature_k(self, elevation_deg: float) -> float:
        """``T1 + T2 exp(-a theta)`` [K] (104 eq. A3)."""
        _check_elevation(elevation_deg)
        return self.t1_k + self.t2_k * math.exp(-self.a_per_deg * float(elevation_deg))

    def system_noise_temperature_k(self, elevation_deg: float, cumulative_distribution: float) -> float:
        """``T_op`` [K] at an elevation and a tabulated weather level (104 eqs. A2-A9)."""
        attenuation = atmosphere_attenuation_db(
            zenith_attenuation_db(self.complex_name, self.band, cumulative_distribution), elevation_deg)
        return self.antenna_microwave_temperature_k(elevation_deg) + sky_noise_temperature_k(
            attenuation, cumulative_distribution)

    def g_over_t_db_per_k(self, elevation_deg: float, cumulative_distribution: float) -> float:
        """Vacuum gain over ``T_op`` [dB/K]; the atmosphere's attenuation of the carrier is not in it."""
        return self.vacuum_gain_dbi(elevation_deg) - 10.0 * math.log10(
            self.system_noise_temperature_k(elevation_deg, cumulative_distribution))


_GOLDSTONE_25 = (-2355022.014, -4646953.204, 3669040.567)
_GOLDSTONE_26 = (-2354890.797, -4647166.328, 3668871.755)
_CANBERRA_34 = (-4461147.093, 2682439.239, -3674393.133)
_CANBERRA_35 = (-4461273.090, 2682568.925, -3674152.093)
_CANBERRA_36 = (-4461168.415, 2682814.657, -3674083.901)
_MADRID_54 = (4849434.488, -360723.8999, 4114618.835)
_MADRID_55 = (4849525.256, -360606.0932, 4114495.084)

_X = "810-005 104 Rev. Q Table A-2"
_KA = "810-005 104 Rev. Q Table A-4"

#: Receive configurations read from 810-005 module 104 Rev. Q (page images, 2026-10-18).
DSN_ANTENNAS: tuple[DsnAntenna, ...] = (
    DsnAntenna("DSS-25", "goldstone", "X", "X/Ka, HEMT-1, RCP, Diplexed",
               68.22, 0.000047, 42.44, 16.2, 12.0, 0.2, _GOLDSTONE_25, _X),
    DsnAntenna("DSS-26", "goldstone", "X", "X/Ka, HEMT-1, RCP, Diplexed",
               68.29, 0.000059, 42.46, 16.29, 5.2, 0.08, _GOLDSTONE_26, _X),
    DsnAntenna("DSS-34", "canberra", "X", "X/Ka, HEMT-1, RCP, Diplexed",
               68.18, 0.000041, 48.8, 15.86, -3.0, 0.20, _CANBERRA_34, _X),
    DsnAntenna("DSS-35", "canberra", "X", "X/Ka, HEMT-1, RCP, Diplexed, w/ M7 XXKa mirror",
               68.35, 0.000045, 45.00, 14.7, 0.0, 0.00, _CANBERRA_35, _X),
    DsnAntenna("DSS-54", "madrid", "X", "X/Ka, HEMT-1, RCP, Diplexed",
               68.37, 0.000058, 45.25, 18.31, 11.0, 0.15, _MADRID_54, _X),
    DsnAntenna("DSS-55", "madrid", "X", "X/Ka, HEMT-1, RCP, Diplexed, w/ M7 XXKa mirror",
               68.34, 0.000035, 43.55, 17.42, 13.2, 0.15, _MADRID_55, _X),
    DsnAntenna("DSS-25", "goldstone", "Ka", "X/Ka, HEMT-1, RCP, Diplexed (w/ M7 XXKaKa dichroic)",
               78.40, 0.00036, 53.83, 24.2, 10.0, 0.15, _GOLDSTONE_25, _KA),
    DsnAntenna("DSS-26", "goldstone", "Ka", "X/Ka, HEMT-1, RCP, Non-Diplexed",
               79.13, 0.00022, 44.38, 19.35, 5.0, 0.075, _GOLDSTONE_26, _KA),
    DsnAntenna("DSS-34", "canberra", "Ka", "X/Ka, HEMT-1, RCP, Non-Diplexed",
               78.63, 0.00046, 50.2, 19.1, -43.0, 0.15, _CANBERRA_34, _KA),
    DsnAntenna("DSS-36", "canberra", "Ka", "X/Ka, HEMT-1, RCP, Non-Diplexed",
               79.34, 0.00060, 47.52, 12.54, -13.0, 0.060, _CANBERRA_36, _KA),
    DsnAntenna("DSS-54", "madrid", "Ka", "X/Ka, HEMT-1, RCP, Non-Diplexed",
               78.38, 0.00020, 45.00, 21.80, 0.0, 0.000, _MADRID_54, _KA),
)


#: ITRF93 positions [m] at epoch 2003.0 of every DSN antenna in service or planned (810-005 module 301 Rev. P
#: Table 2, read 2026-10-19; the table's note 1, +-3 cm per coordinate, marks DSS-23/34/35/36/53/56; DSS-15 and
#: DSS-45 are decommissioned and left out; DSS-33 is "estimated, good to a few meters"). The site velocities
#: (Table 3, about 2 cm/yr) are not applied.
DSN_ITRF93_POSITIONS_M: dict[str, tuple[float, float, float]] = {
    "DSS-13": (-2351112.659, -4655530.636, 3660912.728),
    "DSS-14": (-2353621.420, -4641341.472, 3677052.318),
    "DSS-23": (-2354702.027, -4646969.709, 3669213.211),
    "DSS-24": (-2354906.711, -4646840.095, 3669242.325),
    "DSS-25": _GOLDSTONE_25,
    "DSS-26": _GOLDSTONE_26,
    "DSS-33": (-4461103.0, 2682649.0, -3674286.0),
    "DSS-34": _CANBERRA_34,
    "DSS-35": _CANBERRA_35,
    "DSS-36": _CANBERRA_36,
    "DSS-43": (-4460894.917, 2682361.507, -3674748.152),
    "DSS-53": (4849338.209, -360657.812, 4114746.173),
    "DSS-54": _MADRID_54,
    "DSS-55": _MADRID_55,
    "DSS-56": (4849421.679, -360549.659, 4114646.987),
    "DSS-63": (4849092.518, -360180.3480, 4115109.251),
    "DSS-65": (4849339.634, -360427.6637, 4114750.733),
}


def dsn_antenna(station: str, band: Band) -> DsnAntenna:
    """The catalog entry for ``station`` (``"DSS-26"``) at ``band``."""
    for antenna in DSN_ANTENNAS:
        if antenna.station == station and antenna.band == band:
            return antenna
    available = sorted({f"{a.station} {a.band}" for a in DSN_ANTENNAS})
    raise RfError(f"no DSN antenna {station!r} at {band!r} band; the catalog holds {available}")


__all__ = [
    "DSN_ANTENNAS",
    "DSN_ITRF93_POSITIONS_M",
    "MAX_ELEVATION_DEG",
    "MIN_ELEVATION_DEG",
    "T_CMB_K",
    "ZENITH_ATTENUATION_DB",
    "Band",
    "Complex",
    "DsnAntenna",
    "atmosphere_attenuation_db",
    "dsn_antenna",
    "pointing_loss_db",
    "sky_noise_temperature_k",
    "zenith_attenuation_db",
]
