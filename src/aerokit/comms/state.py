# Copied from Sidera (sidera.communications.ground.stations (StateProvider protocol only), commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""The one interface the link geometry needs: something with an inertial state at an epoch."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

__all__ = ["StateProvider"]

@runtime_checkable
class StateProvider(Protocol):
    """Where something is, at an epoch.

    The entire coupling between communications and the rest of Sidera. A
    ``MissionResult``, a propagated trajectory, an ephemeris wrapper and a
    ground station all satisfy it without either side importing the other.
    """

    def state_at(self, epoch_s: float) -> NDArray[np.float64]:
        """Inertial ``[x, y, z, vx, vy, vz]`` in metres and metres per second."""
        ...
