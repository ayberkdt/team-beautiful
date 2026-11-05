"""Default twin-turboprop configuration for the drag build-up, and the drag/sizing fixed point.

The geometry beyond the wing (fuselage, nacelles, tails) is a King Air 350-class template taken from
the drag build-up test (``tests/aero/test_drag.py``): wing span and length from Wikipedia (read
2026-10-25), everything else an **assumption**. Tail areas scale with the wing area (constant tail
area ratio, assumption). Replace the template with real geometry as soon as there is one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit.aero import drag as D
from aerokit.design.requirements import Assumptions, Requirements
from aerokit.design.sizing import SizingResult, size

__all__ = ["Configuration", "TWIN_TURBOPROP", "buildup_polar", "size_with_buildup"]


@dataclass(frozen=True)
class Configuration:
    """Non-wing geometry for the build-up (SI)."""

    fuselage_length: float = 14.22          # Wikipedia King Air 350i overall length (upper bound for the body)
    fuselage_diameter: float = 1.60         # assumption: equivalent circular diameter
    nose_length: float = 2.5                # assumption
    tail_cone_length: float = 5.5           # assumption
    wing_t_c: float = 0.15                  # assumption: mean of NACA 23018 root / 23012 tip
    wing_Q: float = 1.10                    # unverified interference factor
    nacelle: tuple[float, float, float, float] = (4.0, 0.80, 0.8, 1.5)   # length, diameter, nose, tail (assumption)
    nacelle_Q: float = 1.5                  # unverified
    n_nacelles: int = 2
    htail_ratio: float = 6.5 / 28.8         # S_h/S of the template (assumption)
    vtail_ratio: float = 4.0 / 28.8         # S_v/S of the template (assumption)
    tail_Q: float = 1.04                    # unverified
    upsweep: float = 0.14                   # rad, assumption
    leakage_fraction: float = 0.05          # assumption, no source
    Re_transition: float = 5e5              # Anderson's conservative example value (PDF p. 411)


TWIN_TURBOPROP = Configuration()


def buildup_polar(S: float, AR: float, taper: float, V: float, h: float,
                  cfg: Configuration = TWIN_TURBOPROP) -> D.DragPolar:
    """Component build-up polar of a wing (S, AR, taper) on the configuration ``cfg``."""
    d = cfg.fuselage_diameter
    hs, vs = cfg.htail_ratio * S, cfg.vtail_ratio * S
    nl, nd, nn, nt = cfg.nacelle
    rt = cfg.Re_transition
    comps = [
        D.lifting_surface("wing", S, AR, taper, cfg.wing_t_c, body_width=d, Q=cfg.wing_Q, Re_transition=rt),
        D.body("fuselage", cfg.fuselage_length, d, cfg.nose_length, cfg.tail_cone_length, Re_transition=rt),
        D.nacelle("nacelles", nl, nd, nn, nt, count=cfg.n_nacelles, Q=cfg.nacelle_Q, Re_transition=rt),
        D.lifting_surface("horizontal tail", hs, 4.5, 0.6, 0.12, Q=cfg.tail_Q, Re_transition=rt),
        D.lifting_surface("vertical tail", vs, 1.32, 0.6, 0.12, sweep_max_t=math.radians(30.0), Q=cfg.tail_Q,
                          Re_transition=rt),
    ]
    misc = [("aft-fuselage upsweep", D.upsweep_drag_area(cfg.upsweep, math.pi * d ** 2 / 4))]
    b = D.component_buildup(comps, V, h, S_ref=S, misc=misc, leakage_fraction=cfg.leakage_fraction)
    return D.drag_polar_from_buildup(b, AR)


def size_with_buildup(req: Requirements, asm: Assumptions, cfg: Configuration = TWIN_TURBOPROP,
                      tol_kg: float = 0.1, max_iter: int = 30) -> tuple[SizingResult, D.DragPolar, int]:
    """Fixed point: size → build-up on the sized wing (CD0, e) → resize, until W0 changes < ``tol_kg``.

    The build-up is evaluated at the maximum-speed requirement and ``cruise_altitude``.

    Raises
    ------
    ValueError
        No convergence within ``max_iter`` iterations.
    """
    V = req.require("max_speed")
    h = float(asm["cruise_altitude"])
    cur = asm.with_(CD0_override=0.0, e_override=0.0)
    s = size(req, cur)
    for it in range(1, max_iter + 1):
        polar = buildup_polar(s.S, float(asm["aspect_ratio"]), float(asm["taper_ratio"]), V, h, cfg)
        cur = cur.with_(CD0_override=float(polar.CD0), e_override=float(polar.e))
        new = size(req, cur)
        if abs(new.mass - s.mass) < tol_kg:
            return new, polar, it
        s = new
    raise ValueError(f"drag build-up / sizing did not converge in {max_iter} iterations")
