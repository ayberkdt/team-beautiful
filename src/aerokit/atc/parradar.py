"""PAR radar model: what the sensor really gives, with the errors ICAO Annex 10 allows and those it does not state.

Geometry and accuracy from ICAO Annex 10 Vol I 3.2.3 (read in ``03_Advionics/research/R2_par_deep_research.md``):

* the antenna stands beside the runway, set back from touchdown (915 m and 120 m in the Annex example);
* azimuth and elevation errors depend on the distance **from the antenna**, range error on distance from touchdown;
* azimuth limit max(0.6 % R + 10 % of deviation, 9 m); elevation limit max(0.4 % R + 10 % of displacement, 6 m);
  distance limit 30 m **plus** 3 % of distance (not "or", an error in our earlier note);
* one plot per second at least, coverage 20 deg x 7 deg, 9 NM.

Annex 10 gives limits only: no percentile, no bias, no correlation. Three things here are our assumptions [Y]:

* 1 sigma = limit / 2. Supported by "about a tenth of a degree" for a typical PAR (Raytheon patent, R2 S12);
* part of the variance is correlated with a time constant, so a filter cannot average all of it (R5 B4);
* elevation multipath: a sinusoid in antenna elevation angle. Lobe spacing lambda / (2 h) is two-ray geometry [Y]; the
  amplitude is assumed, 0.03-0.1 deg (no measured PAR multipath data was found, R2 1.4).

Plot detection above 90 % is the PSR/PAR figure (R5 B4).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from aerokit.approach import Runway, glide_path_height

__all__ = ["RadarConfig", "RadarPlot", "ParRadar", "error_limits_m", "NM"]

NM = 1852.0


@dataclass(frozen=True)
class RadarConfig:
    setback_m: float = 915.0          # Annex 10 example
    offset_m: float = 120.0           # Annex 10 example: antenna to the side of the runway
    update_s: float = 1.0             # Annex 10: at least once per second
    sigma_of_limit: float = 0.5       # [Y] 1 sigma = limit / 2
    correlated_share: float = 0.5     # [Y] share of the variance that is correlated
    correlation_s: float = 5.0        # [Y] R5 B4: filtering gives little once noise lasts this long
    multipath_deg: float = 0.05       # [Y] assumed, inside 0.03-0.1
    antenna_height_m: float = 3.0     # [Y] R2 1.4 used 3-5 m
    wavelength_m: float = 0.033       # X band, R2 1.4
    detection: float = 0.95           # above 90 % in the sources; 0.90 is tested as the pessimistic case
    max_range_m: float = 9 * NM


@dataclass(frozen=True)
class RadarPlot:
    """One plot in runway-centred terms. Deviations are from the nominal path; ``t`` is the time of measurement."""

    t: float
    range_m: float                    # to touchdown
    az_dev_m: float                   # + right of the centreline
    el_dev_m: float                   # + above the glide path
    az_valid: bool = True
    el_valid: bool = True


def error_limits_m(r_antenna_m: float, d_touchdown_m: float, lat_dev_m: float = 0.0,
                   vert_dev_m: float = 0.0) -> tuple[float, float, float]:
    """Annex 10 3.2.3.3 limits (azimuth, elevation, distance) in metres."""
    az = max(0.006 * r_antenna_m + 0.1 * abs(lat_dev_m), 9.0)
    el = max(0.004 * r_antenna_m + 0.1 * abs(vert_dev_m), 6.0)
    return az, el, 30.0 + 0.03 * max(d_touchdown_m, 0.0)


@dataclass
class ParRadar:
    """Measures an aircraft at runway coordinates (x before the threshold, y right, z up, metres)."""

    rwy: Runway
    cfg: RadarConfig = field(default_factory=RadarConfig)
    rng: np.random.Generator = field(default_factory=np.random.default_rng)

    def __post_init__(self) -> None:
        self._az = float(self.rng.standard_normal())
        self._el = float(self.rng.standard_normal())
        self._phase = float(self.rng.uniform(0.0, 2.0 * math.pi))
        self._t: float | None = None

    def _red(self, state: float, dt: float) -> float:
        a = math.exp(-dt / self.cfg.correlation_s)
        return a * state + math.sqrt(1.0 - a * a) * float(self.rng.standard_normal())

    def measure(self, t: float, x: float, y: float, z: float) -> RadarPlot | None:
        """A plot, or ``None`` when the target is not detected this scan."""
        c = self.cfg
        dt = c.update_s if self._t is None else max(t - self._t, 1e-3)
        self._t = t
        self._az, self._el = self._red(self._az, dt), self._red(self._el, dt)
        white_az, white_el, white_r = (float(v) for v in self.rng.standard_normal(3))
        if float(self.rng.uniform()) > c.detection:
            return None
        d = max(x - self.rwy.gpip, 1.0)                       # distance to touchdown
        gp = float(glide_path_height(self.rwy, x))
        lat, vert = y, z - gp
        r_ant = math.hypot(d + c.setback_m, y - c.offset_m)
        l_az, l_el, l_r = error_limits_m(r_ant, d, lat, vert)
        s = c.sigma_of_limit
        w, k = math.sqrt(1.0 - c.correlated_share), math.sqrt(c.correlated_share)
        err_az = s * l_az * (w * white_az + k * self._az)
        err_el = s * l_el * (w * white_el + k * self._el)
        elev_deg = math.degrees(math.atan2(max(z, 0.0), r_ant))
        lobe_deg = math.degrees(c.wavelength_m / (2.0 * c.antenna_height_m))
        err_el += r_ant * math.radians(c.multipath_deg) * math.sin(2.0 * math.pi * elev_deg / lobe_deg + self._phase)
        d_meas = d + s * l_r * white_r
        # a range error also moves the path height the radar compares with
        gp_meas = float(glide_path_height(self.rwy, d_meas + self.rwy.gpip))
        return RadarPlot(t, d_meas, lat + err_az, z + err_el - gp_meas)
