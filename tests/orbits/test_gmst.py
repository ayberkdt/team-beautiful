# Copied from Sidera (tests/frames/test_frames_teme.py (test_gmst82_matches_erfa only), commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""GMST82 against ERFA."""
from __future__ import annotations

import pytest

from aerokit.orbits.gmst import gmst82_rad


def test_gmst82_matches_erfa():
    erfa = pytest.importorskip("erfa")
    for days in (-9000.25, -0.5, 0.0, 0.3, 1234.567891, 9600.75):
        expected = erfa.gmst82(2451545.0, days)
        # Same expression and order of operations: measured identical bits
        # over 2001 dates from 1975 to 2026; asserted to 1e-12 rad.
        assert gmst82_rad(days) == pytest.approx(expected, abs=1e-12)
