"""Stress recovery used by prev_guess/01_Ansys/scripts/rehearsal_bracket.py, checked against closed-form cases."""
import importlib.util
from pathlib import Path

import numpy as np

from aerokit.optimization import topology as tp
from aerokit.verification import check, check_true

_SPEC = importlib.util.spec_from_file_location(
    "rehearsal_bracket", Path(__file__).resolve().parents[1] / "prev_guess" / "01_Ansys" / "scripts" / "rehearsal_bracket.py")
R = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(R)


def test_uniform_tension():
    check("element-centre von Mises equals P/(h t) in uniform tension", R.tension_check(0.3), 1.0, rtol=1e-6)


def test_pure_shear_von_mises():
    # Unit element with u = gamma*y (simple shear, y up): tau = G*gamma, von Mises = sqrt(3)*tau.
    g = tp.Grid2D(1, 1, 0.3)
    U = np.zeros((g.ndof, 1))
    gamma = 1e-3
    for ix in (0, 1):
        for iy in (0, 1):
            U[g.dof(ix, iy, 0), 0] = gamma * iy
    vm = R.centre_stress(g, U, 0.3)[0]
    G = 1.0 / (2 * (1 + 0.3))
    check("simple shear: von Mises = sqrt(3) G gamma", vm, np.sqrt(3) * G * gamma, rtol=1e-12)


def test_l_bracket_analysis_scales():
    rng = np.random.default_rng(0)
    d = np.ones((20, 20))
    d[: 12, 8:] = rng.uniform(0, 0.4, (12, 12))      # void corner, roughly where the passive region is
    a = R.analyse(d, 20)
    check_true("finite positive stress and tip displacement", a["vm_unit_max"] > 0 and a["tip_unit"] > 0, a)
