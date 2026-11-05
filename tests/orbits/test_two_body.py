# Copied from Sidera (tests/common/test_two_body.py, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Closed-form two-body relations: the one Kepler-period and ellipse-radii home."""

from __future__ import annotations

import math
import subprocess
import sys

import numpy as np
import pytest

from aerokit.orbits.two_body import (
    calculate_ae_from_radii,
    calculate_periapsis_apoapsis_radii,
    orbital_period_s,
)

MU_EARTH = 3.986004418e14  # [m^3/s^2]


def test_period_hand_case_geostationary() -> None:
    # a = 42 164 km under Earth's GM gives one sidereal day to ~1 s.
    assert orbital_period_s(42_164.0e3, MU_EARTH) == pytest.approx(86_164.1, abs=1.0)


def test_period_is_keplers_third_law_inverted() -> None:
    period = 7_200.0
    # cbrt is within 1 ulp; cubing triples the relative error of a and the
    # square root halves it again, plus a few roundings: ~4 eps, allow 8 eps.
    # (``** (1/3)`` would not do: 1/3 is inexact, which costs ~1e-15 here.)
    a = float(np.cbrt(MU_EARTH * (period / (2.0 * math.pi)) ** 2))
    eps = np.finfo(np.float64).eps
    assert orbital_period_s(a, MU_EARTH) == pytest.approx(period, rel=8.0 * eps)


def test_scalar_in_float_out_and_array_in_array_out() -> None:
    assert type(orbital_period_s(7.0e6, MU_EARTH)) is float
    out = orbital_period_s(np.array([[7.0e6, 8.0e6]]), MU_EARTH)
    assert isinstance(out, np.ndarray) and out.shape == (1, 2)
    assert out[0, 0] == orbital_period_s(7.0e6, MU_EARTH)


def test_unbound_or_undefined_orbit_has_no_period() -> None:
    out = orbital_period_s(np.array([-7.0e6, 0.0, np.nan, np.inf, 7.0e6]), MU_EARTH)
    assert np.isnan(out[:4]).all() and np.isfinite(out[4])
    assert math.isnan(orbital_period_s(-1.0, MU_EARTH))


@pytest.mark.parametrize("mu", [0.0, -1.0, math.nan, math.inf])
def test_period_rejects_a_bad_mu(mu: float) -> None:
    with pytest.raises(ValueError, match="mu"):
        orbital_period_s(7.0e6, mu)


def test_radii_round_trip_and_apoapsis_order() -> None:
    rp, ra = calculate_periapsis_apoapsis_radii(8.0e6, 0.25)
    assert (rp, ra) == (6.0e6, 10.0e6)
    assert calculate_ae_from_radii(rp, ra) == (8.0e6, 0.25)
    assert calculate_ae_from_radii(ra, rp) == (8.0e6, 0.25)  # order-insensitive


def test_radii_must_be_positive() -> None:
    with pytest.raises(ValueError, match="periapsis_radius"):
        calculate_ae_from_radii(-1.0, 2.0)


def test_import_is_light() -> None:
    code = (
        "import sys, aerokit.orbits.two_body; "
        "print(','.join(m for m in ('numba', 'torch', 'scipy') if m in sys.modules))"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == ""
