# Copied from Sidera (sidera.frames.teme (gmst82_rad only), commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Greenwich mean sidereal time, IAU 1982 (Aoki et al. 1982), as in ERFA ``eraGmst82``."""
from __future__ import annotations

import math

from aerokit.comms.constants import DAY_S, JULIAN_CENTURY_DAYS

__all__ = ["gmst82_rad"]

# eraGmst82 coefficients [s of time]; A carries the -12 h of a noon-based JD.
_GMST82_A = 24110.54841 - DAY_S / 2.0
_GMST82_B = 8640184.812866
_GMST82_C = 0.093104
_GMST82_D = -6.2e-6
_SECONDS_TO_RAD = 2.0 * math.pi / DAY_S


def gmst82_rad(ut1_days_since_j2000: float) -> float:
    """Greenwich mean sidereal time (IAU 1982) for UT1 = JD 2451545.0 + days, in [0, 2 pi).

    Reference: Vallado et al. (2006), AIAA 2006-6753 (source identified; content not yet checked)
    [SIDERA-STD-FRM-006].
    """
    days = float(ut1_days_since_j2000)
    centuries = days / JULIAN_CENTURY_DAYS
    fraction_s = DAY_S * math.fmod(days, 1.0)  # JD 2451545.0 has no fractional part
    seconds = (
        _GMST82_A + (_GMST82_B + (_GMST82_C + _GMST82_D * centuries) * centuries) * centuries
    ) + fraction_s
    return (seconds * _SECONDS_TO_RAD) % (2.0 * math.pi)
