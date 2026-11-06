"""The ring: the point on the ideal path T seconds ahead. The pilot puts the flight path marker in the ring.

    T = min(20 s, max(r / (2 Vg), 8 s)),  track = -atan(y / (Vg T)),  sink = Vg tan(gamma) + z / T

The marker shows the real track from aircraft sensors, so a wind needs no term. With the marker in the ring, the offset decays
with time constant T. The ring uses only what the cue shows: filtered y and z, range and ground speed. The drift term comes
from the marker, which the pilot can see.
"""
from __future__ import annotations

import math
import sys

from par_cue import parcue
from par_cue.parflight import PilotModel

DRIFT_TIME_S = 6.0         # [Y] the pilot reads drift from the marker, averaged over about this time


class RingPilot:
    """The pilot model, except that the vertical gain follows the ring."""

    vertical_wc = 0.05

    def __getattr__(self, name):
        return getattr(PilotModel, name)


class RingCue(parcue.CueLogic):
    """The cue with the ring added. The aircraft state comes from the replay loop that calls this step."""

    pilot: RingPilot | None = None
    drift_deg: float | None = None

    def step(self, t, plot, *args, **kwargs):
        out = super().step(t, plot, *args, **kwargs)
        self._ring(out, sys._getframe(1).f_locals)
        return out

    def _ring(self, out: dict, loc: dict) -> None:
        c = self.cfg
        out["aim_trk_deg"], out["aim_gam_deg"] = None, None
        psi, tas, cross = loc.get("psi"), loc.get("tas"), loc.get("cross_f")
        if psi is not None and tas:
            now = math.degrees(math.atan2(cross, tas)) if cross is not None else -math.degrees(psi)
            d = RingCue.drift_deg
            RingCue.drift_deg = now if d is None else d + (now - d) / DRIFT_TIME_S
        if out["state"] != "VALID":
            return
        y, z, r, gs = float(self.ky.x[0]), float(self.kz.x[0]), out["range_nm"] * parcue.NM, out["gs_ms"]
        T = min(c.look_ahead_s, max(0.5 * r / gs, c.min_look_ahead_s))
        cap = c.cap_near_deg if r < c.near_nm * parcue.NM else c.cap_far_deg
        trk = max(-cap, min(cap, math.degrees(math.atan(-y / (gs * T)))))
        sink = gs * math.tan(math.radians(self.rwy.glide_path_deg)) + max(-c.max_rod_corr_ms, min(c.max_rod_corr_ms, z / T))
        out["aim_trk_deg"], out["aim_gam_deg"] = trk, -math.degrees(math.atan2(sink, gs))
        out["hdg_rel_deg"] = trk - (RingCue.drift_deg or 0.0)
        RingCue.pilot.vertical_wc = 1.0 / T


def fly_ring(runway, rc, seed):
    """One replay in which the pilot flies the marker into the ring."""
    logic, parcue.CueLogic = parcue.CueLogic, RingCue
    RingCue.pilot, RingCue.drift_deg = RingPilot(), None
    try:
        return parcue.fly_replay(runway, parcue.CueConfig(), rc, pilot=RingCue.pilot, seed=seed)
    finally:
        parcue.CueLogic = logic
