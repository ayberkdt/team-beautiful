"""Automated PAR guidance: radar plots -> path state -> heading target and glide-path information -> pilot cue.

The Advionics brief (6 Nov 2026): replace the PAR controller. The logic follows what the rules ask of that controller.
Evidence: ``03_Advionics/research/R2_par_deep_research.md`` (PAR), ``R3_...`` (tasks), ``R4_...`` (cue), ``R5_...``
(models).

* **The two axes are not treated alike** (ICAO Doc 4444 8.9.7.2.4-5). In azimuth the pilot does not correct unless
  told, so
  the output is a heading. In elevation the pilot corrects from the information alone, so the output is position, trend
  and an advisory rate of descent. No turn or descend commands.
* **Filter** per axis: constant-velocity Kalman (Bar-Shalom), noise from the Annex 10 limits at the antenna range,
  gate on
  the normalised innovation. The gate widens after each rejection so noise cannot lock it out.
* **Heading target** from position only: last known heading + offset term + a slow trim. The controller knows the
  heading last assigned and builds on it (R2 2.4), so the start heading is an input, and the trim follows the wind as
  it changes with height. Corrections get smaller with range and change at most every 5 s (RA 3291, JO 7110.65).
* **Words** are JO 7110.65BB 5-12-4: ON GLIDEPATH, ON COURSE, SLIGHTLY/WELL ABOVE/BELOW GLIDEPATH, SLIGHTLY/WELL
  LEFT/RIGHT
  OF COURSE; trends GOING, COMING DOWN/UP, HOLDING, CORRECTING, RAPIDLY. "On" is one third of the limit (Smolensk report
  p. 253); FAA and ICAO give no numbers.
* **Missed approach** follows JO 7110.65BB 5-10-14: (a) safety limits exceeded, (b) position in doubt, (c) radar contact
  lost or malfunction suspected. The call is the reason, then "if runway or approach lights not in sight, execute missed
  approach". None of these applies after DH. (d) airport or traffic comes from the tower and is out of scope.
* **After DH** position stays on as advisory until the threshold (5-12-7); 14 CFR 91.175 is the pilot's.
* **Elevation failure** ends PAR guidance at once (5-12-10). **Guidance link silent 5 s** is not a missed approach: the
  pilot applies the lost communications instruction given before final (5-10-4).
* **Limits** +-0.5 deg and +-2 deg are defaults from one published set (Smolensk report p. 257). FAA prints no
  number: real
  limits are per runway (UK cursor, RA 3291), so these are inputs. Going outside and staying outside is the trigger
  (AIM 5-4-11).
* **Timers:** target lost above 3 s is told to the pilot and treated as a fault (RA 3291 para 5). Inside 4 NM that
  fault is
  final (para 7b). Outside 4 NM it may wait to the 5 s longest silence (Doc 4444 8.9.7.2.3).
* **Closure:** position alone misses an aircraft sinking fast towards the path, which is what the Smolensk event showed.
  A 10 s line fit gives the trend words and a fast-closure flag, with Raytheon patent bands. The fit is not used in the
  heading or rate targets: a rate from 1 Hz PAR plots is too noisy for control. Three designs that used it failed in
  closed loop on 6 Nov, including a drift estimate from a 10 s track (2-3 deg of noise at 5 NM).
* **Limits and alerts use what the radar is sure of:** deviation minus 1 sigma of the radar at that range.

Gains and some thresholds are design values [Y]. Educational concept on simulated and recorded data only; it is not
approved or ready for flight use. The cue informs; the pilot decides and flies.
"""
from __future__ import annotations

import math
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from aerokit.approach import Runway, glide_path_height
from aerokit.atc.cue_intensity import CueIntensity, IntensityConfig, voice_level_dba
from aerokit.atc.parflight import AIRCRAFT, FT, KT, Aircraft, Atmosphere, PilotModel, wind_at
from aerokit.atc.parradar import NM, ParRadar, RadarConfig, RadarPlot, error_limits_m
from aerokit.atc.voice_arbiter import VoiceArbiter

__all__ = ["CueConfig", "AxisKalman", "CueLogic", "Fault", "ReplayConfig", "fly_replay", "replay_track", "cue_changes",
           "END_STATES", "MISSED_STATES", "PilotModel", "RadarPlot", "dh_frame"]

FPM = 196.850394                 # ft/min per m/s
#: JO 7110.65 5-10-14 a-c: conditional missed approach, before DH only
MISSED_STATES = ("RADAR LOST", "RADAR SUSPECT", "OUTSIDE LIMITS", "ELEVATION FAILED")
END_STATES = (*MISSED_STATES, "LINK LOST", "OVER THRESHOLD")


@dataclass(frozen=True)
class CueConfig:
    look_ahead_s: float = 20.0        # [Y] remove the offset in about this time
    min_look_ahead_s: float = 8.0     # [Y] near the runway half the time to go, not below this
    trim_time_s: float = 80.0         # [Y] chosen by sweep, 6 Nov
    gs_prior_ms: float = 65.0         # [Y] prior for the range filter; range noise is about 150 m at 5 NM
    gs_min_ms: float = 40.0
    gs_max_ms: float = 110.0
    max_trim_deg: float = 20.0        # [Y] wind at 1000 ft is 1.8 x W20 (R5); 19 kt at 20 ft needs about 15 deg
    near_nm: float = 3.0              # 2-5 deg corrections inside about 3 NM (R2 2.4)
    cap_far_deg: float = 10.0         # one historic sample: 10 deg far out (R2 2.4)
    cap_near_deg: float = 5.0
    change_far_deg: float = 4.0       # avoid small changes at long range (RA 3291 para 24)
    change_near_deg: float = 2.0
    update_s: float = 5.0             # about every 5 s (JO 7110.65 5-12-4a)
    rod_step_fpm: float = 100.0
    accel_lat: float = 0.5            # [Y] process noise, m/s^2 rms; half-rate turn peak is about 1.8
    accel_vert: float = 0.2           # [Y]
    accel_range: float = 0.05         # [Y]
    gate_sigma: float = 5.0           # [Y] on the normalised innovation
    limit_vert_deg: float = 0.5       # Smolensk report p. 257
    limit_lat_deg: float = 2.0        # same
    limit_floor_vert_m: float = 18.0  # 60 ft, UK "slightly" band: keeps the limit above radar error near DH [Y]
    on_fraction: float = 1.0 / 3.0    # Smolensk report p. 253
    slight_fraction: float = 2.0 / 3.0   # [Y] FAA has two words and no numbers
    limit_frames: int = 3             # outside and staying outside (AIM 5-4-11) [Y] 3 s
    latch_limits: bool = True         # False: words and alerts keep working past a limit (replay analysis only)
    track_lost_s: float = 3.0         # RA 3291 para 5
    lost_s: float = 5.0               # longest silence on final, Doc 4444 8.9.7.2.3
    no_resume_nm: float = 4.0         # RA 3291 para 7b
    link_lost_s: float = 5.0          # JO 7110.65 5-10-4a: PAR final
    reject_to_invalid: int = 2        # [Y]
    recover_plots: int = 3            # [Y]
    acquire_plots: int = 3            # [Y]
    lat_full_scale_deg: float = 2.5   # needle: 2 dots
    vert_full_scale_deg: float = 0.7  # ILS glide slope: 1 dot 0.35 deg (NTSB FDR report)
    max_range_m: float = 9 * NM       # Annex 10 coverage
    sector_deg: float = 10.0          # Annex 10: 20 deg sector
    dh_ft: float = 200.0              # set by the pilot (RA 3291 para 1b)
    max_rod_corr_ms: float = 1.2      # about 1 deg of pitch at approach speed (R2 section 4)
    trend_window_s: float = 10.0      # [Y] 2 PAR calls; a controller needs 5-6 s (Smolensk report p. 267)
    trend_slow_dps: float = 0.025     # Raytheon bands; the 0.01 band is below our noise at 3 km
    trend_fast_dps: float = 0.05
    predict_s: float = 10.0           # [Y] fast closure looks this far ahead
    fast_window_s: float = 10.0       # [Y] tuned on 300 real approaches and the Smolensk track, 6 Nov
    fast_margin: float = 0.3          # [Y] 1/s, slope noise as a share of the radar sigma
    fast_frames: int = 5              # [Y] frames in a row
    fast_max_ft: float = 1000.0       # the stabilised approach rule starts at the gate (FSF ALAR 7.1)
    sink_limit_fpm: float = 1000.0    # stabilised approach limit (FSF ALAR 7.1)
    threshold_m: float = 0.0          # guidance ends over the threshold (5-12-8)


class AxisKalman:
    """Constant-velocity Kalman filter on one axis; discrete white-noise acceleration."""

    def __init__(self, value: float, rate: float, var: float, accel_rms: float, t: float, rate_var: float = 25.0):
        self.x = np.array([value, rate])
        self.P = np.diag([var, rate_var])
        self.q = accel_rms ** 2
        self.t = t

    def predict(self, t: float) -> tuple[np.ndarray, np.ndarray]:
        dt = t - self.t
        f = np.array([[1.0, dt], [0.0, 1.0]])
        g = np.array([dt * dt / 2.0, dt])
        return f @ self.x, f @ self.P @ f.T + self.q * np.outer(g, g)

    def nis(self, value: float, var: float, t: float) -> float:
        """Innovation squared over its variance: one degree of freedom."""
        x, p = self.predict(t)
        return float((value - x[0]) ** 2 / (p[0, 0] + var))

    def update(self, value: float, var: float, t: float) -> None:
        x, p = self.predict(t)
        s = p[0, 0] + var
        k = p[:, 0] / s
        self.x = x + k * (value - x[0])
        self.P = p - np.outer(k, p[0, :])
        self.t = t


def _slope(samples: Sequence[tuple[float, float]]) -> float | None:
    if len(samples) < 4:
        return None
    t = np.array([s[0] for s in samples])
    v = np.array([s[1] for s in samples])
    return float(np.polyfit(t - t[0], v, 1)[0])


@dataclass
class CueLogic:
    """Call :meth:`step` once per second with the plot that arrived in that second (or ``None``)."""

    rwy: Runway
    cfg: CueConfig = field(default_factory=CueConfig)
    radar: RadarConfig = field(default_factory=RadarConfig)
    intensity: IntensityConfig = field(default_factory=IntensityConfig)
    state: str = "ACQUIRING"
    hdg: float = 0.0                  # heading target, degrees relative to the runway course
    rod: float | None = None          # advisory rate of descent, ft/min

    def __post_init__(self) -> None:
        self.ky: AxisKalman | None = None
        self.kz: AxisKalman | None = None
        self.kr: AxisKalman | None = None
        self.trim = self.hdg          # the heading last assigned is known
        self.alert = CueIntensity(self.intensity)
        self.arbiter = VoiceArbiter()
        self._flag = {"az": 0, "el": 0}
        self._last_plot = -1e9
        self._last_link = 0.0
        self._call: str | None = None
        self._first: list[RadarPlot] = []
        self._rej = {"az": 0, "el": 0}
        self._good = {"az": 0, "el": 0}
        self._bad = {"az": False, "el": False}
        self._last = {"az": -1e9, "el": -1e9}
        self._trim_t: float | None = None
        self._next = [0.0, 0.0]
        self._out = 0
        self._hb = 0
        self._last_hdg_t = -1e9
        self._hist: deque[tuple[float, float, float, float]] = deque()
        self._fast_hist: deque[tuple[float, float]] = deque()
        self._fast_n = 0

    def _vars(self, p: RadarPlot) -> tuple[float, float, float]:
        c = self.radar
        r_ant = math.hypot(p.range_m + c.setback_m, p.az_dev_m - c.offset_m)
        l_az, l_el, l_r = error_limits_m(r_ant, p.range_m, p.az_dev_m, p.el_dev_m)
        s = c.sigma_of_limit
        return (s * l_az) ** 2, (s * l_el) ** 2, (s * l_r) ** 2

    def _axis(self, key: str, kal: AxisKalman, value: float, valid: bool, var: float, t: float) -> None:
        self._flag[key] = 0 if valid else self._flag[key] + 1
        if not valid or not math.isfinite(value):
            self._rej[key] += 1
            self._good[key] = 0
            return
        limit = (self.cfg.gate_sigma * (1.0 + 0.5 * self._rej[key])) ** 2
        if kal.nis(value, var, t) <= limit:
            kal.update(value, var, t)
            self._last[key] = t
            self._rej[key] = 0
            self._good[key] += 1
        else:
            self._rej[key] += 1
            self._good[key] = 0

    def _take(self, p: RadarPlot, t: float) -> None:
        self._last_plot = t
        if self.kr is None or self.ky is None or self.kz is None:
            if p.az_valid and p.el_valid and all(map(math.isfinite, (p.range_m, p.az_dev_m, p.el_dev_m))):
                self._first.append(p)
            if len(self._first) >= self.cfg.acquire_plots:
                self._start()
            return
        if p.t <= self.kr.t:
            return                    # an old plot arriving late never moves the state backwards
        v_az, v_el, v_r = self._vars(p)
        self._axis("az", self.ky, p.az_dev_m, p.az_valid, v_az, p.t)
        self._axis("el", self.kz, p.el_dev_m, p.el_valid, v_el, p.t)
        if math.isfinite(p.range_m):
            self.kr.update(p.range_m, v_r, p.t)
        self._hb += 1

    def _start(self) -> None:
        c = self.cfg
        b = self._first[-1]
        v_az, v_el, v_r = self._vars(b)
        n = len(self._first)
        y = float(np.mean([p.az_dev_m for p in self._first]))
        z = float(np.mean([p.el_dev_m for p in self._first]))
        self.ky = AxisKalman(y, 0.0, v_az / n, c.accel_lat, b.t)
        self.kz = AxisKalman(z, 0.0, v_el / n, c.accel_vert, b.t)
        self.kr = AxisKalman(b.range_m, -c.gs_prior_ms, v_r, c.accel_range, b.t, rate_var=15.0 ** 2)
        self._last = {"az": b.t, "el": b.t}

    def _limits_m(self, r: float) -> tuple[float, float]:
        c = self.cfg
        return (r * math.tan(math.radians(c.limit_lat_deg)),
                max(r * math.tan(math.radians(c.limit_vert_deg)), c.limit_floor_vert_m))

    def _dots(self, y: float, z: float, r: float) -> tuple[float, float]:
        c = self.cfg
        rr = max(r, 1.0)
        return (2.0 * math.degrees(math.atan2(y, rr)) / c.lat_full_scale_deg,
                2.0 * math.degrees(math.atan2(z, rr)) / c.vert_full_scale_deg)

    def _word(self, dev: float, limit: float, on: str, plus: str, minus: str) -> str:
        c = self.cfg
        share = abs(dev) / limit
        if share <= c.on_fraction:
            return on
        side = plus if dev > 0 else minus
        return f"{'SLIGHTLY' if share <= c.slight_fraction else 'WELL'} {side}"

    def _trend_word(self, dev: float, rate_dps: float | None, word: str, toward: str, plus: str, minus: str) -> str:
        c = self.cfg
        if rate_dps is None or word.startswith("ON "):
            return ""
        size = abs(rate_dps)
        if size < c.trend_slow_dps:
            return "HOLDING"
        if rate_dps * dev < 0:
            head = toward
        else:
            head = f"GOING {plus if dev > 0 else minus}"
        return f"{head} RAPIDLY" if size >= c.trend_fast_dps else head

    def _next_state(self, t: float, y: float, z: float, r: float, height_ft: float) -> str:
        c = self.cfg
        if self.state in END_STATES:
            return self.state
        if r <= c.threshold_m - self.rwy.gpip:
            return "OVER THRESHOLD"
        if self.state == "ADVISORY":
            return self.state          # below DH: 5-10-14 a-c do not apply, position stays advisory
        if self._flag["el"] >= c.reject_to_invalid and self._flag["az"] == 0:
            self._call = "no_glidepath"
            return "ELEVATION FAILED"  # 5-12-10: at once
        age = max(t - self._last["az"], t - self._last["el"])
        if age > (c.track_lost_s if r < c.no_resume_nm * NM else c.lost_s):
            arriving = t - self._last_plot <= 1.5
            self._call = "radar_suspect" if arriving else "radar_lost"
            return "RADAR SUSPECT" if arriving else "RADAR LOST"
        for k in ("az", "el"):
            if self._rej[k] >= c.reject_to_invalid:
                self._bad[k] = True
            if self._bad[k] and self._good[k] >= c.recover_plots:
                self._bad[k] = False
        if self._bad["az"] or self._bad["el"]:
            return "INVALID"
        if age > c.track_lost_s:
            return "DELAYED"
        if height_ft <= c.dh_ft:
            return "ADVISORY"
        lim_y, lim_z = self._limits_m(r)
        v_az, v_el, _ = self._vars(RadarPlot(t, r, y, z))
        outside = (abs(y) - math.sqrt(v_az) > lim_y or abs(z) - math.sqrt(v_el) > lim_z or r > c.max_range_m or
                   abs(math.degrees(math.atan2(y, max(r, 1.0)))) > c.sector_deg)
        self._out = self._out + 1 if outside else 0
        if c.latch_limits and self._out >= c.limit_frames:
            if abs(z) / lim_z >= abs(y) / lim_y:
                self._call = "too_high" if z > 0 else "too_low"
            else:
                self._call = "too_right" if y > 0 else "too_left"
            return "OUTSIDE LIMITS"
        return "VALID"

    def _closing_fast(self, t: float, z: float, r: float, y: float, nominal: float, lim_z: float,
                      height_ft: float) -> bool:
        """Heading below the limit, with a sink rate above the stabilised limit by more than the slope noise, for some
        frames in a row. Tuned on real data: without the margin 43 % of normal approaches raised a false caution."""
        c = self.cfg
        self._fast_hist.append((t, z))
        while self._fast_hist[0][0] < t - c.fast_window_s:
            self._fast_hist.popleft()
        rate = _slope(list(self._fast_hist))
        hit = False
        if rate is not None and height_ft <= c.fast_max_ft and t - self._fast_hist[0][0] >= c.fast_window_s - 2.0:
            noise = c.fast_margin * math.sqrt(self._vars(RadarPlot(t, r, y, z))[1])
            hit = (rate < 0 and z + rate * c.predict_s < -lim_z and (nominal - rate - noise) * FPM > c.sink_limit_fpm)
        self._fast_n = self._fast_n + 1 if hit else 0
        return self._fast_n >= c.fast_frames

    def _update_targets(self, t: float, y: float, z: float, r: float, gs: float) -> tuple[float, float]:
        c = self.cfg
        T = min(c.look_ahead_s, max(0.5 * r / gs, c.min_look_ahead_s))
        dt = 0.0 if self._trim_t is None else t - self._trim_t
        self._trim_t = t
        ratio = -y / (gs * T)
        self.trim = max(-c.max_trim_deg, min(c.max_trim_deg, self.trim + math.degrees(ratio) * dt / c.trim_time_s))
        near = r < c.near_nm * NM
        cap = c.cap_near_deg if near else c.cap_far_deg
        raw_h = max(-cap, min(cap, math.degrees(math.atan(ratio)))) + self.trim
        nominal = gs * math.tan(math.radians(self.rwy.glide_path_deg))
        raw_s = (nominal + max(-c.max_rod_corr_ms, min(c.max_rod_corr_ms, z / T))) * FPM
        new_h = new_s = 0.0
        need = c.change_near_deg if near else c.change_far_deg
        if t >= self._next[0] and abs(raw_h - self.hdg) >= need:
            value = float(round(raw_h))
            new_h, self.hdg = value - self.hdg, value
            self._next[0] = t + c.update_s
            self._last_hdg_t = t
        step = c.rod_step_fpm
        if self.rod is None:
            self.rod = round(raw_s / step) * step
        elif t >= self._next[1] and abs(raw_s - self.rod) >= 1.5 * step:
            value = round(raw_s / step) * step
            new_s, self.rod = value - self.rod, value
            self._next[1] = t + c.update_s
        return new_h, new_s

    def step(self, t: float, plot: RadarPlot | None, aircraft: Sequence[str] = (), radio: bool = False,
             link_ok: bool = True) -> dict:
        """``aircraft``: aircraft alerts sounding now. ``radio``: a transmission is on. ``link_ok``: the guidance link
        is delivering."""
        c = self.cfg
        if link_ok:
            self._last_link = t
        if self.state not in END_STATES and t - self._last_link > c.link_lost_s:
            self.state, self._call = "LINK LOST", "link_lost"
        if plot is not None and self.state not in END_STATES:
            self._take(plot, t)
        if self.ky is None or self.kz is None or self.kr is None:
            if self.state not in END_STATES:
                self.state = "ACQUIRING" if t <= c.lost_s + c.acquire_plots else "RADAR LOST"
            self._call = "radar_lost" if self.state == "RADAR LOST" else self._call
            v = self.alert.step(t, self.state, None, None, None, None, call=self._call)
            return self._frame(t, self._speak(t, v, aircraft, radio))
        y, z = float(self.ky.x[0]), float(self.kz.x[0])        # shown values are never extrapolated
        r = max(float(self.kr.predict(t)[0][0]), 1.0)
        gs = min(max(-float(self.kr.x[1]), c.gs_min_ms), c.gs_max_ms)
        height_ft = (float(glide_path_height(self.rwy, r + self.rwy.gpip)) + z) / FT
        self.state = self._next_state(t, y, z, r, height_ft)
        self._hist.append((t, math.degrees(math.atan2(y, r)), math.degrees(math.atan2(z, r)), z))
        while self._hist[0][0] < t - c.trend_window_s:
            self._hist.popleft()
        new_h = new_s = 0.0
        if self.state == "VALID":
            new_h, new_s = self._update_targets(t, y, z, r, gs)
        else:
            self._trim_t = None
            self._next = [t + 1.0, t + 1.0]
        lim_y, lim_z = self._limits_m(r)
        lat_word = self._word(y, lim_y, "ON COURSE", "RIGHT OF COURSE", "LEFT OF COURSE")
        vert_word = self._word(z, lim_z, "ON GLIDEPATH", "ABOVE GLIDEPATH", "BELOW GLIDEPATH")
        rate_lat = _slope([(h[0], h[1]) for h in self._hist])
        rate_vert = _slope([(h[0], h[2]) for h in self._hist])
        rate_z = _slope([(h[0], h[3]) for h in self._hist])
        nominal = gs * math.tan(math.radians(self.rwy.glide_path_deg))
        sink_fpm = None if rate_z is None else (nominal - rate_z) * FPM
        fast = self.state == "VALID" and self._closing_fast(t, z, r, y, nominal, lim_z, height_ft)
        v_az, v_el, _ = self._vars(RadarPlot(t, r, y, z))
        call = self._call if self.state in END_STATES else None
        v = self.alert.step(t, self.state, y, z, r, height_ft, closing_fast=fast, call=call,
                            resolve_m=(math.sqrt(v_az), math.sqrt(v_el)))
        v = self._speak(t, v, aircraft, radio)
        live = self.state in ("VALID", "DELAYED", "INVALID", "ADVISORY")
        if self.state == "ADVISORY":   # data faults below DH: remove the needle, no call
            stale = {k: t - self._last[k] > c.track_lost_s or self._rej[k] >= c.reject_to_invalid for k in ("az", "el")}
            self._bad = stale
        show_lat, show_vert = live and not self._bad["az"], live and not self._bad["el"]
        ld, vd = self._dots(y, z, r)
        note = "ADVISORY ONLY" if self.state == "ADVISORY" else ""
        lat_trend = self._trend_word(y, rate_lat, lat_word, "CORRECTING", "RIGHT", "LEFT")
        return self._frame(t, v, ld if show_lat else None, vd if show_vert else None, lat_word if show_lat else "",
                           vert_word if show_vert else "", lat_trend if show_lat else "",
                           self._trend_word(z, rate_vert, vert_word, "COMING DOWN" if z > 0 else "COMING UP", "ABOVE",
                                            "BELOW") if show_vert else "", new_h, new_s, r,
                           height_ft if show_vert else None, gs, sink_fpm, fast, note)

    def _speak(self, t: float, v: dict, aircraft: Sequence[str], radio: bool) -> dict:
        """Pass the wanted call through the arbiter. The level and the display do not change, only the voice."""
        a = self.arbiter.step(v["voice"], v["level"], aircraft, radio)
        out = dict(v)
        out.update(voice=a["voice"], voice_held=a["held"], voice_dropped=a["dropped"],
                   voice_dba=voice_level_dba(a["voice_level"], self.intensity) if a["voice"] else None,
                   tone_first=bool(a["voice"]) and a["voice_level"] == 4)
        return out

    def _frame(self, t: float, v: dict, ld: float | None = None, vd: float | None = None, lat_word: str = "",
               vert_word: str = "", lat_trend: str = "", vert_trend: str = "", new_h: float = 0.0, new_s: float = 0.0,
               r: float | None = None, height_ft: float | None = None, gs: float | None = None,
               sink_fpm: float | None = None, fast: bool = False, note: str = "") -> dict:
        ok = self.state == "VALID"
        ages = [t - a for a in self._last.values() if a > -1e8]
        return {"t": round(t, 1), "state": self.state, "lat_dots": ld, "vert_dots": vd,
                "hdg_rel_deg": self.hdg if ok else None, "rod_fpm": self.rod if ok else None, "hdg_new": new_h,
                "rod_new": new_s, "lat_word": lat_word, "vert_word": vert_word, "lat_trend": lat_trend,
                "vert_trend": vert_trend, "age_s": max(ages) if ages else None, "heartbeat": self._hb,
                "range_nm": None if r is None else r / NM, "height_ft": height_ft, "gs_ms": gs, "sink_fpm": sink_fpm,
                "closing_fast": fast, "note": note, "trim_deg": self.trim, "level": v["level"], "voice": v["voice"],
                "voice_dba": v["voice_dba"], "tone_first": v["tone_first"], "visual": v["visual"], "blink": v["blink"],
                "intensity": v["intensity"], "voice_held": v["voice_held"], "voice_dropped": v["voice_dropped"],
                "missed_approach": self.state in MISSED_STATES}


@dataclass(frozen=True)
class Fault:
    """A scripted fault between ``t0`` and ``t1``. kind: delay (value = s), jump (value = m on both axes), invalid (both
    axes), el_invalid, az_invalid, dropout (no plots), link (guidance link silent)."""

    kind: str
    t0: float
    t1: float
    value: float = 0.0


@dataclass(frozen=True)
class ReplayConfig:
    aircraft: Aircraft = AIRCRAFT["C-130H"]
    start_range_nm: float = 5.0
    start_offset_m: float = 150.0     # right of the centreline
    start_above_m: float = 30.0
    headwind_ms: float = 0.0          # at 20 ft; wind grows with height
    crosswind_ms: float = 0.0         # at 20 ft; + pushes the aircraft right
    start_heading_error_deg: float = 0.0   # the aircraft arrives crabbed for the wind; this is the error in that crab
    turbulence_w20_kt: float = 15.0   # light
    dt: float = 0.1
    after_end_s: float = 15.0         # keep flying this long after a missed approach
    aircraft_alerts: tuple[tuple[float, float, str], ...] = ()   # (from, to, name): aircraft alert sounding
    radio: tuple[tuple[float, float], ...] = ()                  # (from, to): a transmission is on


def _apply_faults(faults: Sequence[Fault], p: RadarPlot | None, t: float) -> tuple[RadarPlot | None, float]:
    delay = 0.0
    for f in faults:
        if not f.t0 <= t < f.t1:
            continue
        if f.kind == "delay":
            delay = f.value
        elif f.kind == "dropout":
            return None, 0.0
        elif p is not None and f.kind == "jump":
            p = RadarPlot(p.t, p.range_m, p.az_dev_m + f.value, p.el_dev_m + f.value)
        elif p is not None and f.kind in ("invalid", "az_invalid", "el_invalid"):
            p = RadarPlot(p.t, p.range_m, p.az_dev_m, p.el_dev_m, az_valid=f.kind == "el_invalid",
                          el_valid=f.kind == "az_invalid")
    return p, delay


def fly_replay(rwy: Runway, cfg: CueConfig = CueConfig(), rc: ReplayConfig = ReplayConfig(),
               pilot: PilotModel = PilotModel(), faults: Sequence[Fault] = (), seed: int = 0,
               radar: RadarConfig = RadarConfig()) -> list[dict]:
    """Closed loop at 10 Hz with 1 Hz radar. One frame per second: :meth:`CueLogic.step` plus the truth."""
    rng = np.random.default_rng(seed)
    sensor = ParRadar(rwy, radar, rng)
    atm = Atmosphere(rc.headwind_ms, rc.crosswind_ms, rc.turbulence_w20_kt, rng)
    tan_g = math.tan(math.radians(rwy.glide_path_deg))
    tas = rc.aircraft.vat_kt * KT
    resp = rc.aircraft.response_s
    x = rc.start_range_nm * NM + rwy.gpip
    y = rc.start_offset_m
    z = float(glide_path_height(rwy, x)) + rc.start_above_m
    psi = -math.asin(max(-0.5, min(0.5, wind_at(z, rc.crosswind_ms) / tas))) + math.radians(rc.start_heading_error_deg)
    logic = CueLogic(rwy, cfg, radar, hdg=math.degrees(psi))
    sink = tas * tan_g
    head_f = cross_f = up_f = None
    per_s = round(1.0 / rc.dt)
    shown: tuple[float, float | None] = (math.degrees(psi), None)
    lag = deque([shown] * max(1, round(pilot.reaction_s / rc.dt)))
    in_flight: list[tuple[float, RadarPlot]] = []
    frames: list[dict] = []
    t_end = None
    go_around = False
    n = 0
    while True:
        t = n * rc.dt
        if n % per_s == 0:
            p, delay = _apply_faults(faults, sensor.measure(t, x, y, z), t)
            if p is not None:
                in_flight.append((t + delay, p))
            due = [q for q in in_flight if q[0] <= t + 1e-9]
            in_flight = [q for q in in_flight if q[0] > t + 1e-9]
            alerts = [a[2] for a in rc.aircraft_alerts if a[0] <= t < a[1]]
            on_air = any(a <= t < b for a, b in rc.radio)
            link = not any(f.kind == "link" and f.t0 <= t < f.t1 for f in faults)
            fr = logic.step(t, due[-1][1] if due else None, alerts, on_air, link)
            fr.update(x_m=x, y_m=y, z_dev_m=z - float(glide_path_height(rwy, x)), height_m=z)
            frames.append(fr)
            z_seen = float(logic.kz.x[0]) if logic.kz is not None and fr["vert_dots"] is not None else None
            shown = (fr["hdg_rel_deg"] if fr["hdg_rel_deg"] is not None else shown[0], z_seen)
            if fr["state"] in END_STATES and t_end is None:
                t_end = t + (0.0 if fr["state"] == "OVER THRESHOLD" else rc.after_end_s)
                go_around = fr["state"] != "OVER THRESHOLD"
            if (t_end is not None and t >= t_end) or x <= rwy.gpip + 100.0:
                return frames
        lag.append(shown)
        seen_h, seen_z = lag.popleft()
        head, cross, up = atm.step(z, tas, rc.dt)
        head_f = head if head_f is None else head_f + (head - head_f) * rc.dt / resp
        cross_f = cross if cross_f is None else cross_f + (cross - cross_f) * rc.dt / resp
        up_f = up if up_f is None else up_f + (up - up_f) * rc.dt / resp
        gs = tas * math.cos(psi) - head_f
        nominal = gs * tan_g
        if go_around:
            sink += (-pilot.go_around_climb_ms - sink) * rc.dt / resp
        elif pilot.follows_cue:
            max_turn = math.radians(pilot.turn_rate_dps) * rc.dt
            psi += max(-max_turn, min(max_turn, math.radians(seen_h + pilot.heading_error_deg) - psi))
            if seen_z is not None:
                cap = gs * math.tan(math.radians(pilot.max_pitch_change_deg))
                sink += (nominal + max(-cap, min(cap, pilot.vertical_wc * seen_z)) - sink) * rc.dt / resp
        x -= gs * rc.dt
        y += (tas * math.sin(psi) + cross_f) * rc.dt
        z += (up_f - sink) * rc.dt
        n += 1


def replay_track(rwy: Runway, t: Sequence[float], x: Sequence[float], y: Sequence[float], z: Sequence[float],
                 cfg: CueConfig = CueConfig(), radar: RadarConfig = RadarConfig(), seed: int = 0, noise: bool = True,
                 stop_at_end_state: bool = False) -> list[dict]:
    """Open loop: a recorded track (seconds, runway metres) through the radar model and the cue. The aircraft does not
    react. With ``noise=False`` the plots are the track itself."""
    logic = CueLogic(rwy, cfg, radar)
    sensor = ParRadar(rwy, radar, np.random.default_rng(seed))
    tt, xs, ys, zs = (np.asarray(v, float) for v in (t, x, y, z))
    frames = []
    for ti in np.arange(tt[0], tt[-1] + 1e-9, 1.0):
        xi, yi, zi = (float(np.interp(ti, tt, v)) for v in (xs, ys, zs))
        if noise:
            p = sensor.measure(float(ti), xi, yi, zi)
        else:
            p = RadarPlot(float(ti), xi - rwy.gpip, yi, zi - float(glide_path_height(rwy, xi)))
        fr = logic.step(float(ti), p)
        fr.update(x_m=xi, y_m=yi, z_dev_m=zi - float(glide_path_height(rwy, xi)), height_m=zi)
        frames.append(fr)
        if stop_at_end_state and fr["state"] in END_STATES:
            break
    return frames


def dh_frame(frames: Sequence[dict]) -> dict | None:
    """The frame where the aircraft reached decision height, or ``None`` if it never did."""
    return next((f for f in frames if f["state"] == "ADVISORY"), None)


def cue_changes(frames: Sequence[dict]) -> int:
    """How many target changes were shown in a run (both axes)."""
    return sum(bool(f["hdg_new"]) + bool(f["rod_new"]) for f in frames)
