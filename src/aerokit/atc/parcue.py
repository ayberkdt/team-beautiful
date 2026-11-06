"""Automated PAR guidance: radar plots -> path state -> target heading and descent -> pilot cue.

The Advionics brief (6 Nov 2026): replace the PAR controller; radar data in, heading and glide-slope corrections out.
The logic is what a talk-down controller does, in four small steps:

1. **Filter** (:class:`PathFilter`): an alpha-beta filter per axis. Its rate only predicts the next plot; a plot far
   from the prediction is rejected (gate from the PAR accuracy model of :func:`aerokit.atc.par.par_measure`).
2. **Targets** (:meth:`CueLogic._targets`): position only. Heading target = course + a term that removes the offset in
   ``look_ahead_s`` + a slow trim that learns the wind from the offset that remains (a radar sees no wind and no
   heading). Descent target = nominal descent for the measured ground speed + a term that removes the height error.
3. **Cue**: the needles move with every plot. A target changes only in display steps and at most every ``update_s``, so
   radar noise does not flicker the cue. The pilot holds the last target.
4. **Validity**: delayed, rejected or missing data changes the state. No valid data means no new target and no
   extrapolation. LOST, OUTSIDE LIMITS and MINIMUMS are latched.

Two earlier laws failed in closed loop on 6 Nov and are recorded so nobody repeats them. A relative correction from
filtered radar *rate*, continuous: 0 of 100 runs reached minimums. The same as discrete steps: 0 of 100. The derived
rate is too noisy at 1 Hz PAR accuracy.

All gains and thresholds are design values [Y], not requirements. Educational concept on simulated data only; it is not
approved or ready for flight use. The cue recommends; the pilot decides and flies.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from aerokit.approach import Runway, glide_path_height
from aerokit.atc.par import NM, par_measure

__all__ = ["CueConfig", "Plot", "PathFilter", "CueLogic", "Fault", "PilotModel", "ReplayConfig", "fly_replay",
           "cue_changes", "VOICE_TEXT", "END_STATES"]

FPM = 196.850394                 # ft/min per m/s
FT = 3.28083990
END_STATES = ("LOST", "OUTSIDE LIMITS", "MINIMUMS")

VOICE_TEXT = {"turn_left": "Turn left", "turn_right": "Turn right", "descend_more": "Descend more",
              "descend_less": "Descend less", "on_path": "On path", "delayed": "Data delayed",
              "invalid": "Data invalid", "restored": "Guidance restored", "lost": "Guidance lost. Go around.",
              "limits": "Outside limits. Go around.", "minimums": "Minimums. Guidance ends."}


@dataclass(frozen=True)
class CueConfig:
    look_ahead_s: float = 20.0        # remove the deviation in about this time
    min_look_ahead_s: float = 8.0     # near the runway the time shortens to half the time to go, not below this
    trim_time_s: float = 80.0         # wind trim integrates the remaining offset with this time constant
    max_track_corr_deg: float = 10.0  # offset term limit
    max_trim_deg: float = 10.0
    max_sink_corr_ms: float = 2.5     # about 500 ft/min
    hdg_step_deg: float = 2.0
    sink_step_fpm: float = 100.0
    update_s: float = 5.0             # a target changes at most this often (a talk-down call is about every 5 s)
    show_s: float = 3.0               # TURN / DESCEND wording stays this long, then HOLD
    on_path_dots: float = 0.3         # within this the display says ON COURSE / ON GLIDE PATH
    alpha: float = 0.30               # alpha-beta filter gains (1 Hz plots)
    beta: float = 0.04
    gate_sigma: float = 5.0           # reject a plot further than this many sigma from the prediction
    gate_floor_m: float = 15.0        # the aircraft also moves: the gate never closes below this
    delayed_after_s: float = 2.0      # plot age above this: DELAYED
    lost_after_s: float = 5.0         # about 5 s: PAR lost-communication interval, search summaries only [A]
    reject_to_invalid: int = 2        # consecutive rejected plots
    recover_plots: int = 3            # consecutive good plots before the cue returns
    acquire_plots: int = 3
    lat_full_scale_deg: float = 2.5   # 2 dots
    vert_full_scale_deg: float = 0.7
    limit_dots: float = 2.0           # at or beyond full scale: OUTSIDE LIMITS
    limit_after_range_m: float = 1000.0   # below this range the angle limit is not applied: minimums come first
    max_range_m: float = 9 * NM       # PAR coverage (research note R_par_enri_soumu)
    sector_deg: float = 10.0          # half width of the azimuth sector (SKYbrary, about 20 deg in all)
    decision_height_m: float = 60.96  # 200 ft
    voice_gap_s: float = 4.0          # at least this long between routine voice calls
    voice_dots: float = 0.5           # routine voice only when further off the path than this


@dataclass(frozen=True)
class Plot:
    """One radar plot as it reaches the cue logic. ``t`` is the time of measurement, not of arrival."""

    t: float
    range_m: float
    az_dev_m: float                   # + right of the centreline
    el_dev_m: float                   # + above the glide path
    valid: bool = True


def sigma_m(range_m: float) -> tuple[float, float]:
    """(lateral, vertical) 1-sigma plot noise; the model of :func:`aerokit.atc.par.par_measure` at zero offset."""
    return 0.5 * max(9.0, 0.006 * range_m), 0.5 * max(6.0, 0.004 * range_m)


@dataclass
class PathFilter:
    """Alpha-beta filters on lateral deviation, vertical deviation and range."""

    cfg: CueConfig
    t: float | None = None
    y: float = 0.0
    yr: float = 0.0
    z: float = 0.0
    zr: float = 0.0
    r: float = 0.0
    rr: float = 0.0

    def start(self, plots: list[Plot]) -> None:
        a, b = plots[0], plots[-1]
        self.t = b.t
        self.y, self.z = (float(np.mean([getattr(p, k) for p in plots])) for k in ("az_dev_m", "el_dev_m"))
        self.r = b.range_m
        self.yr, self.zr, self.rr = 0.0, 0.0, (b.range_m - a.range_m) / max(b.t - a.t, 1e-6)

    def predict(self, t: float) -> tuple[float, float, float]:
        dt = t - (self.t if self.t is not None else t)
        return self.y + self.yr * dt, self.z + self.zr * dt, self.r + self.rr * dt

    def accepts(self, p: Plot, rejects: int = 0) -> bool:
        """Innovation gate. It widens after each rejected plot: the prediction gets older, and without this two noise
        rejections in a row could never recover (2 false LOST in 100 clean runs before this change)."""
        py, pz, _ = self.predict(p.t)
        sy, sz = sigma_m(p.range_m)
        k = self.cfg.gate_sigma * (1.0 + 0.5 * rejects)
        return abs(p.az_dev_m - py) <= max(k * sy, self.cfg.gate_floor_m) and \
            abs(p.el_dev_m - pz) <= max(k * sz, self.cfg.gate_floor_m)

    def update(self, p: Plot) -> None:
        dt = p.t - (self.t if self.t is not None else p.t)
        if dt <= 0:
            return                    # an old plot arriving late never moves the state backwards
        a, b = self.cfg.alpha, self.cfg.beta
        py, pz, pr = self.predict(p.t)
        ey, ez, er = p.az_dev_m - py, p.el_dev_m - pz, p.range_m - pr
        self.y, self.yr = py + a * ey, self.yr + b * ey / dt
        self.z, self.zr = pz + a * ez, self.zr + b * ez / dt
        self.r, self.rr = pr + 0.5 * er, self.rr + 0.1 * er / dt
        self.t = p.t


def _step(value: float, step: float) -> float:
    return round(value / step) * step


@dataclass
class CueLogic:
    """Call :meth:`step` once per second with the plot that arrived in that second (or ``None``)."""

    rwy: Runway
    cfg: CueConfig = field(default_factory=CueConfig)
    state: str = "ACQUIRING"
    hdg: float | None = None          # shown heading target, degrees relative to the runway course
    sink: float | None = None         # shown descent target, ft/min

    def __post_init__(self) -> None:
        self.f = PathFilter(self.cfg)
        self.trim = 0.0
        self._first: list[Plot] = []
        self._rejects = 0
        self._good = 0
        self._bad = False             # in INVALID until recover_plots good plots arrived
        self._last_good: float | None = None
        self._last_trim_t: float | None = None
        self._last_voice = -1e9
        self._next = [0.0, 0.0]       # earliest next target change per axis
        self._word = [(0.0, ""), (0.0, "")]  # (command wording ends at, wording) per axis
        self._said = [0, 0]           # direction of the last spoken call per axis
        self._said_on_path = True

    def _take(self, p: Plot) -> None:
        finite = all(math.isfinite(v) for v in (p.range_m, p.az_dev_m, p.el_dev_m))
        if not p.valid or not finite:
            self._rejects += 1
            self._good = 0
            return
        if self.f.t is None:
            self._first.append(p)
            if len(self._first) >= self.cfg.acquire_plots:
                self.f.start(self._first)
                self._last_good = p.t
            return
        if p.t <= self.f.t:
            return
        if self.f.accepts(p, self._rejects):
            self.f.update(p)
            self._last_good = p.t
            self._rejects = 0
            self._good += 1
        else:
            self._rejects += 1
            self._good = 0

    def _dots(self) -> tuple[float, float]:
        c = self.cfg
        r = max(self.f.r, 1.0)
        return (2.0 * math.degrees(math.atan2(self.f.y, r)) / c.lat_full_scale_deg,
                2.0 * math.degrees(math.atan2(self.f.z, r)) / c.vert_full_scale_deg)

    def _height_m(self) -> float:
        return float(glide_path_height(self.rwy, self.f.r + self.rwy.gpip)) + self.f.z

    def _next_state(self, t: float) -> str:
        c = self.cfg
        if self.state in END_STATES:
            return self.state
        if self.f.t is None:
            return "ACQUIRING" if t < c.lost_after_s + c.acquire_plots else "LOST"
        age = t - (t if self._last_good is None else self._last_good)   # both are set when the filter starts
        if age > c.lost_after_s:
            return "LOST"
        if self._rejects >= c.reject_to_invalid:
            self._bad = True
        if self._bad and self._good >= c.recover_plots:
            self._bad = False
        if self._bad:
            return "INVALID"
        if age > c.delayed_after_s:
            return "DELAYED"
        if self._height_m() <= c.decision_height_m:
            return "MINIMUMS"
        ld, vd = self._dots()
        if self.f.r > c.max_range_m or abs(math.degrees(math.atan2(self.f.y, self.f.r))) > c.sector_deg:
            return "OUTSIDE LIMITS"
        if self.f.r > c.limit_after_range_m and max(abs(ld), abs(vd)) >= c.limit_dots:
            return "OUTSIDE LIMITS"
        return "VALID"

    def _targets(self, t: float) -> tuple[float, float]:
        """Raw targets from the filter state: heading relative to the course [deg], descent [ft/min]."""
        c = self.cfg
        f = self.f
        gs = max(-f.rr, 30.0)
        T = min(c.look_ahead_s, max(0.5 * f.r / gs, c.min_look_ahead_s))
        dt = 0.0 if self._last_trim_t is None else t - self._last_trim_t
        self._last_trim_t = t
        ratio = -f.y / (gs * T)
        self.trim = max(-c.max_trim_deg, min(c.max_trim_deg, self.trim + math.degrees(ratio) * dt / c.trim_time_s))
        offset = max(-c.max_track_corr_deg, min(c.max_track_corr_deg, math.degrees(math.atan(ratio))))
        nominal = gs * math.tan(math.radians(self.rwy.glide_path_deg))
        extra = max(-c.max_sink_corr_ms, min(c.max_sink_corr_ms, f.z / T))
        return offset + self.trim, (nominal + extra) * FPM

    def _update_targets(self, t: float) -> tuple[float, float]:
        c = self.cfg
        raw_h, raw_s = self._targets(t)
        if self.hdg is None or self.sink is None:
            self.hdg, self.sink = 0.0, _step(raw_s, c.sink_step_fpm)
        new_h = new_s = 0.0
        ld, vd = self._dots()         # on the path the target needs a bigger reason to change: less flicker
        need_h = (1.5 if abs(ld) <= c.on_path_dots else 0.75) * c.hdg_step_deg
        need_s = (1.5 if abs(vd) <= c.on_path_dots else 0.75) * c.sink_step_fpm
        if t >= self._next[0] and abs(raw_h - self.hdg) >= need_h:
            value = _step(raw_h, c.hdg_step_deg)
            new_h = value - self.hdg
            if new_h:
                self.hdg = value
                self._next[0] = t + c.update_s
                self._word[0] = (t + c.show_s, self._lat_word(new_h))
        if t >= self._next[1] and abs(raw_s - self.sink) >= need_s:
            value = _step(raw_s, c.sink_step_fpm)
            new_s = value - self.sink
            if new_s:
                self.sink = value
                self._next[1] = t + c.update_s
                self._word[1] = (t + c.show_s, self._vert_word(new_s))
        return new_h, new_s

    def _lat_word(self, change: float) -> str:
        """TURN moves towards the path. EASE ends a turn: the aircraft may still be on that side, and a bare TURN RIGHT
        beside a needle on the left would contradict it."""
        side = "RIGHT" if change > 0 else "LEFT"
        return f"TURN {side}" if change * self.f.y < 0 else f"EASE {side}"

    def _vert_word(self, change: float) -> str:
        """DESCEND MORE / LESS move towards the path; EASE DESCENT and RESUME DESCENT end a correction."""
        if change > 0:
            return "DESCEND MORE" if self.f.z > 0 else "RESUME DESCENT"
        return "DESCEND LESS" if self.f.z < 0 else "EASE DESCENT"

    def _texts(self, t: float, ld: float | None, vd: float | None) -> tuple[str, str]:
        """The two command words. Same wording on the display, in the tests and on the slides."""
        if ld is None or vd is None or self.hdg is None:
            return "", ""
        c = self.cfg
        if t < self._word[0][0]:
            lat = self._word[0][1]
        else:
            lat = "ON COURSE" if abs(ld) <= c.on_path_dots else "HOLD HEADING"
        if t < self._word[1][0]:
            vert = self._word[1][1]
        else:
            vert = "ON GLIDE PATH" if abs(vd) <= c.on_path_dots else "HOLD DESCENT"
        return lat, vert

    def _voice(self, t: float, old: str, new_h: float, new_s: float) -> str | None:
        c = self.cfg
        s = self.state
        if s != old:                  # safety calls are not rate limited
            call = {"DELAYED": "delayed", "INVALID": "invalid", "LOST": "lost", "OUTSIDE LIMITS": "limits",
                    "MINIMUMS": "minimums"}.get(s)
            if s == "VALID" and old in ("DELAYED", "INVALID"):
                call = "restored"
            if call:
                self._last_voice = t
                self._said = [0, 0]
                return call
        if s != "VALID" or t - self._last_voice < c.voice_gap_s:
            return None
        call = None
        dh, ds = int(np.sign(new_h)), int(np.sign(new_s))
        ld, vd = self._dots()         # routine voice: only off the path, and only for moves towards the path
        if dh and dh != self._said[0] and abs(ld) > c.voice_dots and self._word[0][1].startswith("TURN"):
            call, self._said[0] = ("turn_right" if dh > 0 else "turn_left"), dh
        elif (ds and ds != self._said[1] and abs(vd) > c.voice_dots and
              self._word[1][1] in ("DESCEND MORE", "DESCEND LESS")):
            call, self._said[1] = ("descend_more" if ds > 0 else "descend_less"), ds
        if call:
            self._said_on_path = False
        elif not self._said_on_path and max(abs(ld), abs(vd)) <= c.on_path_dots:
            call, self._said_on_path, self._said = "on_path", True, [0, 0]
        if call:
            self._last_voice = t
        return call

    def step(self, t: float, plot: Plot | None) -> dict:
        c = self.cfg
        if plot is not None and self.state not in END_STATES:
            self._take(plot)
        old = self.state
        self.state = self._next_state(t)
        new_h = new_s = 0.0
        if self.state == "VALID":
            new_h, new_s = self._update_targets(t)
        else:
            self._last_trim_t = None                      # no valid data: nothing is learned or changed
            self._next = [t + 1.0, t + 1.0]
            self._word = [(0.0, ""), (0.0, "")]
        show = self.state in ("VALID", "DELAYED")
        ld, vd = self._dots() if show else (None, None)
        lat_word, vert_word = self._texts(t, ld, vd)
        return {"t": round(t, 1), "state": self.state, "lat_dots": ld, "vert_dots": vd,
                "hdg_rel_deg": self.hdg if self.state == "VALID" else None,
                "sink_fpm": self.sink if self.state == "VALID" else None,
                "hdg_new": new_h, "sink_new": new_s, "lat_word": lat_word, "vert_word": vert_word,
                "age_s": None if self._last_good is None else t - self._last_good,
                "voice": self._voice(t, old, new_h, new_s),
                "range_nm": None if self.f.t is None else self.f.r / NM,
                "height_ft": self._height_m() * FT if show else None, "trim_deg": self.trim}


@dataclass(frozen=True)
class Fault:
    """A scripted radar fault between ``t0`` and ``t1``. kind: delay (value = s), jump (value = m on both axes),
    invalid (valid flag false) or dropout (no plots)."""

    kind: str
    t0: float
    t1: float
    value: float = 0.0


@dataclass(frozen=True)
class PilotModel:
    """A pilot who holds the last shown target: sees it after ``reaction_s``, reaches it in about ``tau_s``."""

    reaction_s: float = 1.5
    tau_s: float = 3.0
    heading_error_deg: float = 0.0    # the pilot holds the target with this constant error
    follows_cue: bool = True          # False: the no-cue baseline, the aircraft keeps its heading and descent
    go_around_climb_ms: float = 5.0


@dataclass(frozen=True)
class ReplayConfig:
    start_range_nm: float = 5.0
    start_offset_m: float = 150.0     # right of the centreline
    start_above_m: float = 30.0
    crosswind_ms: float = 0.0         # + pushes the aircraft right
    gs_ms: float = 70.0
    gust_sigma_ms: float = 0.4
    gust_tau_s: float = 5.0
    dt: float = 0.1
    after_end_s: float = 15.0         # keep flying this long after LOST or OUTSIDE LIMITS


def fly_replay(rwy: Runway, cfg: CueConfig = CueConfig(), rc: ReplayConfig = ReplayConfig(),
               pilot: PilotModel = PilotModel(), faults: tuple[Fault, ...] = (), seed: int = 0) -> list[dict]:
    """Closed loop at 10 Hz with 1 Hz radar: the aircraft flies the targets the pilot saw ``reaction_s`` ago.

    Returns one frame per second: :meth:`CueLogic.step` plus the truth (``x_m``, ``y_m``, ``z_dev_m``, ``height_m``).
    """
    rng = np.random.default_rng(seed)
    logic = CueLogic(rwy, cfg)
    tan_g = math.tan(math.radians(rwy.glide_path_deg))
    x = rc.start_range_nm * NM + rwy.gpip
    y = rc.start_offset_m
    z = float(glide_path_height(rwy, x)) + rc.start_above_m
    psi = 0.0                                    # heading relative to the course, rad
    sink = rc.gs_ms * tan_g
    gy = gz = 0.0
    ag = math.exp(-rc.dt / rc.gust_tau_s)
    per_s = round(1.0 / rc.dt)
    shown = (0.0, sink * FPM)
    lag = deque([shown] * max(1, round(pilot.reaction_s / rc.dt)))
    in_flight: list[tuple[float, Plot]] = []
    frames: list[dict] = []
    t_end = None
    go_around = False
    n = 0
    while True:
        t = n * rc.dt
        if n % per_s == 0:
            m = par_measure(rwy, t, x, y, z, rng)
            p = Plot(t, m.range_m, m.az_dev_m, m.el_dev_m)
            delay, drop = 0.0, False
            for f in faults:
                if f.t0 <= t < f.t1:
                    if f.kind == "delay":
                        delay = f.value
                    elif f.kind == "dropout":
                        drop = True
                    elif f.kind == "invalid":
                        p = Plot(p.t, p.range_m, p.az_dev_m, p.el_dev_m, valid=False)
                    elif f.kind == "jump":
                        p = Plot(p.t, p.range_m, p.az_dev_m + f.value, p.el_dev_m + f.value)
            if not drop:
                in_flight.append((t + delay, p))
            due = [q for q in in_flight if q[0] <= t + 1e-9]
            in_flight = [q for q in in_flight if q[0] > t + 1e-9]
            fr = logic.step(t, due[-1][1] if due else None)
            fr.update(x_m=x, y_m=y, z_dev_m=z - float(glide_path_height(rwy, x)), height_m=z)
            frames.append(fr)
            if fr["hdg_rel_deg"] is not None:
                shown = (fr["hdg_rel_deg"], fr["sink_fpm"])
            if fr["state"] in END_STATES and t_end is None:
                t_end = t + (2.0 if fr["state"] == "MINIMUMS" else rc.after_end_s)
                go_around = fr["state"] != "MINIMUMS"
            if (t_end is not None and t >= t_end) or x <= rwy.gpip + 100.0:
                return frames
        lag.append(shown)
        seen_h, seen_s = lag.popleft()
        if go_around:
            sink += (-pilot.go_around_climb_ms - sink) * rc.dt / pilot.tau_s
        elif pilot.follows_cue:
            psi += (math.radians(seen_h + pilot.heading_error_deg) - psi) * rc.dt / pilot.tau_s
            sink += (seen_s / FPM - sink) * rc.dt / pilot.tau_s
        gy = ag * gy + math.sqrt(1 - ag ** 2) * rc.gust_sigma_ms * rng.standard_normal()
        gz = ag * gz + math.sqrt(1 - ag ** 2) * rc.gust_sigma_ms * rng.standard_normal()
        x -= rc.gs_ms * math.cos(psi) * rc.dt
        y += (rc.gs_ms * math.sin(psi) + rc.crosswind_ms + gy) * rc.dt
        z += (gz - sink) * rc.dt
        n += 1


def cue_changes(frames: list[dict]) -> int:
    """How many target changes were shown in a run (both axes)."""
    return sum(bool(f["hdg_new"]) + bool(f["sink_new"]) for f in frames)
