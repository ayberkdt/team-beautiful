"""Mean-element satellites with J2 secular drift, Earth rotation by GMST, and nominal constellations.

A :class:`MeanElements` satellite is propagated with Kepler's equation and the first-order J2 secular rates of
node, perigee and mean anomaly (:mod:`aerokit.orbits.kepler_j2`). Its inertial frame is the quasi-inertial
equator-and-equinox frame of the GMST rotation, so the Earth-fixed position is ``R3(GMST82) r``
(:mod:`aerokit.orbits.gmst`, UT1 taken equal to UTC: |UT1 − UTC| < 0.9 s, i.e. < 0.004° of Earth rotation).
Precession, nutation and polar motion are not modelled, and the short-period J2 terms (≈ km) are dropped:
right for visibility statistics and coverage, not for navigation-grade positions (use TLE/SGP4 for those).

Nominal constellations — tables as published, not the satellites' current positions:

* :func:`gps_baseline_24` — GPS SPS PS (4th ed., 2008) Table 3.2-1 slots at 00:00 UTC 1 July 1993,
  a = 26 559.7 km, e = 0, i = 55° (Table 3.2-3). The satellites carry the Cospas-Sarsat DASS repeaters
  (21 in use in May 2024).
* :func:`galileo_nominal_24` — EUSPA GSC reference constellation, Walker 24/3/1 at 2016-11-21 00:00 UTC,
  a = 29 599.8 km, i = 56°; the SAR/Galileo repeaters (23 in use in May 2024) are the main MEOSAR payloads.
* :func:`geostationary`, :func:`circular`, :func:`walker` — generic builders (GEOSAR longitudes and the LEOSAR
  orbits were not found in a source read here, so they are parameters).

Decades after a table's epoch the J2-drifted planes no longer match the maintained real ones; the relative
geometry (spacing, inclination, altitude) is what these models are for.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np
from numpy.typing import NDArray

from aerokit.comms.constants import J2_EARTH_EGM2008, MU_EARTH, OMEGA_EARTH, R_EARTH_EQUATORIAL_EGM2008_M
from aerokit.orbits.gmst import gmst82_rad
from aerokit.orbits.kepler_j2 import j2_secular_rates_rad_s, solve_kepler_elliptic, true_anomaly_from_eccentric
from aerokit.references import cite

__all__ = ["J2000_UTC", "MeanElements", "ut1_days_since_j2000", "gmst_rad", "eci_to_ecef", "gps_baseline_24",
           "galileo_nominal_24", "geostationary", "circular", "walker", "GPS_EPOCH", "GALILEO_EPOCH"]

FloatArray = NDArray[np.float64]
Times = datetime | Sequence[datetime]

#: JD 2451545.0 (2000-01-01 12:00), the GMST82 origin; UTC stands in for UT1
J2000_UTC = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
GPS_EPOCH = datetime(1993, 7, 1, 0, 0, 0, tzinfo=UTC)
GALILEO_EPOCH = datetime(2016, 11, 21, 0, 0, 0, tzinfo=UTC)


def _as_list(t: Times) -> list[datetime]:
    out = [t] if isinstance(t, datetime) else list(t)
    for x in out:
        if x.tzinfo is None:
            raise ValueError("times must be timezone-aware (UTC)")
    return out


def ut1_days_since_j2000(t: datetime) -> float:
    """Days from JD 2451545.0 to ``t`` (UTC used for UT1)."""
    return (_as_list(t)[0] - J2000_UTC).total_seconds() / 86400.0


def gmst_rad(t: datetime) -> float:
    """Greenwich mean sidereal angle (IAU 1982) at ``t`` [rad]."""
    return gmst82_rad(ut1_days_since_j2000(t))


def eci_to_ecef(r_eci: FloatArray, theta: float) -> FloatArray:
    """Rotate ``(…, 3)`` inertial vectors by the sidereal angle ``theta``: ``r_ECEF = R3(θ) r``."""
    c, s = math.cos(theta), math.sin(theta)
    r = np.asarray(r_eci, float)
    return np.stack([c * r[..., 0] + s * r[..., 1], -s * r[..., 0] + c * r[..., 1], r[..., 2]], axis=-1)


@dataclass(frozen=True)
class MeanElements:
    """Mean Keplerian elements at ``epoch`` (SI, radians) of an Earth satellite.

    ``j2=False`` propagates pure two-body motion (used for a geostationary satellite pinned to a longitude).
    """

    name: str
    a: float
    e: float
    i: float
    raan: float
    argp: float
    mean_anomaly: float
    epoch: datetime
    j2: bool = True

    def __post_init__(self) -> None:
        if not (math.isfinite(self.a) and self.a > R_EARTH_EQUATORIAL_EGM2008_M and 0.0 <= self.e < 1.0):
            raise ValueError(f"{self.name}: need a above the Earth's radius and 0 <= e < 1")
        if self.a * (1.0 - self.e) <= R_EARTH_EQUATORIAL_EGM2008_M:
            raise ValueError(f"{self.name}: perigee below the Earth's surface")
        if self.epoch.tzinfo is None:
            raise ValueError("epoch must be timezone-aware (UTC)")

    @property
    def rates(self) -> tuple[float, float, float]:
        """(dΩ/dt, dω/dt, dM/dt) [rad/s]."""
        if not self.j2:
            return 0.0, 0.0, math.sqrt(MU_EARTH / self.a ** 3)
        return j2_secular_rates_rad_s(self.a, self.e, self.i, MU_EARTH, J2_EARTH_EGM2008,
                                      R_EARTH_EQUATORIAL_EGM2008_M)

    @property
    def period_s(self) -> float:
        """Anomalistic period 2π / (dM/dt) [s]."""
        return 2.0 * math.pi / self.rates[2]

    def state_eci(self, t: Times) -> FloatArray:
        """Inertial ``[x, y, z, vx, vy, vz]`` [m, m/s] at each time, shape ``(N, 6)`` (two-body velocity)."""
        ts = _as_list(t)
        dW, dw, dM = self.rates
        p = self.a * (1.0 - self.e ** 2)
        out = np.empty((len(ts), 6))
        for k, tk in enumerate(ts):
            dt = (tk - self.epoch).total_seconds()
            W, w, M = self.raan + dW * dt, self.argp + dw * dt, self.mean_anomaly + dM * dt
            E = M if self.e == 0.0 else solve_kepler_elliptic(M, self.e)
            nu = true_anomaly_from_eccentric(E, self.e)
            r = p / (1.0 + self.e * math.cos(nu))
            pos = np.array([r * math.cos(nu), r * math.sin(nu), 0.0])
            vel = math.sqrt(MU_EARTH / p) * np.array([-math.sin(nu), self.e + math.cos(nu), 0.0])
            cW, sW, ci, si, cw, sw = math.cos(W), math.sin(W), math.cos(self.i), math.sin(self.i), math.cos(w), \
                math.sin(w)
            Q = np.array([[cW * cw - sW * sw * ci, -cW * sw - sW * cw * ci, sW * si],
                          [sW * cw + cW * sw * ci, -sW * sw + cW * cw * ci, -cW * si],
                          [sw * si, cw * si, ci]])
            out[k, :3], out[k, 3:] = Q @ pos, Q @ vel
        return out

    def position_ecef(self, t: Times) -> FloatArray:
        """Earth-fixed position [m] at each time, shape ``(N, 3)``."""
        ts = _as_list(t)
        r = self.state_eci(ts)[:, :3]
        return np.stack([eci_to_ecef(r[k], gmst_rad(tk)) for k, tk in enumerate(ts)])


def _deg(x: float) -> float:
    return math.radians(x)


#: GPS SPS PS 2008 Table 3.2-1: slot → (RAAN, argument of latitude) [deg] at 00:00 UTC 1 July 1993
GPS_SLOTS: dict[str, tuple[float, float]] = {
    "A1": (272.847, 268.126), "A2": (272.847, 161.786), "A3": (272.847, 11.676), "A4": (272.847, 41.806),
    "B1": (332.847, 80.956), "B2": (332.847, 173.336), "B3": (332.847, 309.976), "B4": (332.847, 204.376),
    "C1": (32.847, 111.876), "C2": (32.847, 11.796), "C3": (32.847, 339.666), "C4": (32.847, 241.556),
    "D1": (92.847, 135.226), "D2": (92.847, 265.446), "D3": (92.847, 35.156), "D4": (92.847, 167.356),
    "E1": (152.847, 197.046), "E2": (152.847, 302.596), "E3": (152.847, 66.066), "E4": (152.847, 333.686),
    "F1": (212.847, 238.886), "F2": (212.847, 345.226), "F3": (212.847, 105.206), "F4": (212.847, 135.346),
}
#: the table's ground-track equatorial crossings (GEC/GLAN) [deg], kept for verification
GPS_GEC: dict[str, float] = {
    "A1": 127.85, "A2": 74.68, "A3": 179.63, "A4": 14.69, "B1": 94.27, "B2": 140.46, "B3": 28.78, "B4": 155.98,
    "C1": 169.73, "C2": 119.69, "C3": 103.62, "C4": 54.57, "D1": 61.40, "D2": 126.51, "D3": 11.37, "D4": 77.47,
    "E1": 152.31, "E2": 25.09, "E3": 86.82, "E4": 40.63, "F1": 53.23, "F2": 106.40, "F3": 166.39, "F4": 1.46,
}
GPS_A, GPS_I = 26_559.7e3, 55.0

#: EUSPA GSC nominal Galileo slots: slot → (RAAN, mean anomaly) [deg] at 2016-11-21 00:00 UTC (ω = 0)
GALILEO_SLOTS: dict[str, tuple[float, float]] = {
    "A01": (317.632, 180.153), "A02": (317.632, 225.153), "A03": (317.632, 270.153), "A04": (317.632, 315.153),
    "A05": (317.632, 0.153), "A06": (317.632, 45.153), "A07": (317.632, 90.153), "A08": (317.632, 135.153),
    "B01": (77.632, 195.153), "B02": (77.632, 240.153), "B03": (77.632, 285.153), "B04": (77.632, 330.153),
    "B05": (77.632, 15.153), "B06": (77.632, 60.153), "B07": (77.632, 105.153), "B08": (77.632, 150.153),
    "C01": (197.632, 210.153), "C02": (197.632, 255.153), "C03": (197.632, 300.153), "C04": (197.632, 345.153),
    "C05": (197.632, 30.153), "C06": (197.632, 75.153), "C07": (197.632, 120.153), "C08": (197.632, 165.153),
}
GALILEO_A, GALILEO_I = 29_599.8e3, 56.0


@cite("gps_sps_ps_2008", note="Table 3.2-1 slots, Table 3.2-3 reference orbit")
@cite("cospas_sarsat_2024", note="GPS satellites carry the MEOSAR DASS repeaters")
def gps_baseline_24() -> tuple[MeanElements, ...]:
    """The 24 baseline GPS slots as mean elements (circular, ω = 0, so the mean anomaly is the argument of latitude)."""
    return tuple(MeanElements(f"GPS {s}", GPS_A, 0.0, _deg(GPS_I), _deg(W), 0.0, _deg(u), GPS_EPOCH)
                 for s, (W, u) in GPS_SLOTS.items())


@cite("gsc_galileo_2026", note="nominal satellites of the reference constellation")
@cite("cospas_sarsat_2024", note="SAR/Galileo MEOSAR repeaters")
def galileo_nominal_24() -> tuple[MeanElements, ...]:
    """The 24 nominal Galileo slots (Walker 24/3/1) as mean elements."""
    return tuple(MeanElements(f"Galileo {s}", GALILEO_A, 0.0, _deg(GALILEO_I), _deg(W), 0.0, _deg(M), GALILEO_EPOCH)
                 for s, (W, M) in GALILEO_SLOTS.items())


def geostationary(longitude_deg: float, epoch: datetime, name: str | None = None) -> MeanElements:
    """A satellite fixed over ``longitude_deg``: a = (μ/ω_E²)^(1/3), e = i = 0, two-body (no J2 drift)."""
    a = (MU_EARTH / OMEGA_EARTH ** 2) ** (1.0 / 3.0)
    lam = math.radians(longitude_deg) + gmst_rad(epoch)
    return MeanElements(name or f"GEO {longitude_deg:g}°", a, 0.0, 0.0, 0.0, 0.0, lam % (2 * math.pi), epoch, j2=False)


def circular(name: str, altitude_m: float, inclination_deg: float, raan_deg: float, arg_latitude_deg: float,
             epoch: datetime) -> MeanElements:
    """A circular orbit at ``altitude_m`` above the equatorial radius."""
    return MeanElements(name, R_EARTH_EQUATORIAL_EGM2008_M + altitude_m, 0.0, _deg(inclination_deg), _deg(raan_deg),
                        0.0, _deg(arg_latitude_deg), epoch)


def walker(name: str, total: int, planes: int, phasing: int, a_m: float, inclination_deg: float, epoch: datetime,
           raan0_deg: float = 0.0) -> tuple[MeanElements, ...]:
    """Walker delta pattern i:T/P/F: ``P`` planes 360/P apart, ``T/P`` satellites per plane, plane ``k`` phased by
    ``k·F·360/T`` (Walker's definition)."""
    if not (total > 0 and planes > 0 and total % planes == 0 and 0 <= phasing < planes):
        raise ValueError("need T divisible by P and 0 <= F < P")
    s = total // planes
    sats = []
    for k in range(planes):
        for j in range(s):
            sats.append(MeanElements(f"{name} P{k + 1}S{j + 1}", a_m, 0.0, _deg(inclination_deg),
                                     _deg(raan0_deg + 360.0 * k / planes), 0.0,
                                     _deg(360.0 * j / s + 360.0 * phasing * k / total), epoch))
    return tuple(sats)
