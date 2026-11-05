"""Linear finite elements for aircraft structures: statics, modes, buckling, heat conduction.

Sub-modules
-----------
:mod:`~aerokit.fem.model`
    :class:`Model`: nodes, elements, single- and multi-point constraints, cached sparse assembly
    and the static / modal / buckling drivers.
:mod:`~aerokit.fem.solvers`
    Sparse direct (SuperLU) and preconditioned CG solvers with singularity diagnostics
    (:class:`SolverOptions`, :class:`SingularMatrixError`), condition estimate, eigen-solvers.
:mod:`~aerokit.fem.results`
    Typed, mapping-compatible result objects (:class:`StaticResult`, :class:`ModalResult`, ...).
:mod:`~aerokit.fem.elements`
    ``line`` (:class:`Bar`, :class:`Frame2D`, :class:`Frame3D`), ``plane`` (:class:`T3`,
    :class:`Q4`, :class:`QM6`, :class:`Q8`; plane stress / plane strain / axisymmetric),
    ``solid`` (:class:`T4`, :class:`T10`, :class:`H8`), ``plate`` (:class:`MITC4`) and
    ``discrete`` (springs / masses, when available).
:mod:`~aerokit.fem.mesh`
    ``mesh2d`` structured mapped meshes and edge loads; ``mesh3d`` box meshes, tetrahedral meshes
    from closed surfaces and surface loads.
:mod:`~aerokit.fem.quadrature`
    Gauss-Legendre and triangle rules.
:mod:`~aerokit.fem.thermal`
    Steady heat conduction elements (``ndof = 1``), convection / heat-flux boundaries and
    thermal-stress coupling (equivalent loads of ``α ΔT`` and stress recovery).
:mod:`~aerokit.fem.error_estimation`
    Zienkiewicz-Zhu recovery-based a-posteriori error estimate for 2-D continuum meshes.
:mod:`~aerokit.fem.dynamics`, :mod:`~aerokit.fem.nonlinear`
    Transient / harmonic response and geometrically non-linear analysis.
:mod:`~aerokit.fem.convergence`
    Mesh-convergence study with the grid convergence index.
:mod:`~aerokit.fem.reader`
    JSON model input used by the command-line interface.

The optional sub-modules (``thermal``, ``error_estimation``, ``dynamics``, ``nonlinear``, ``reader``,
``convergence``) are imported lazily on first attribute access, so a problem in one of them never
breaks ``import aerokit.fem``.

Units SI; tension positive.
"""
from __future__ import annotations

import importlib
from typing import Any

from aerokit.fem.elements.line import Bar, Frame2D, Frame3D
from aerokit.fem.elements.plane import Q4, Q8, QM6, T3, D_isotropic, D_orthotropic
from aerokit.fem.elements.plate import MITC4
from aerokit.fem.elements.solid import H8, T4, T10, D_isotropic3d
from aerokit.fem.model import Model
from aerokit.fem.results import (BucklingResult, HarmonicResult, ModalResult, NonlinearResult, Result,
                                 SolverInfo, StaticResult, TransientResult)
from aerokit.fem.solvers import SingularMatrixError, SolverOptions

__all__ = ["Model", "SolverOptions", "SingularMatrixError",
           "Result", "StaticResult", "ModalResult", "BucklingResult", "TransientResult", "HarmonicResult",
           "NonlinearResult", "SolverInfo",
           "Bar", "Frame2D", "Frame3D", "T3", "Q4", "QM6", "Q8", "MITC4", "T4", "T10", "H8",
           "D_isotropic", "D_orthotropic", "D_isotropic3d"]

_LAZY_MODULES = ("thermal", "error_estimation", "dynamics", "nonlinear", "reader", "convergence", "mesh",
                 "elements", "quadrature", "solvers", "results", "model")
_LAZY_NAMES = {
    "HeatT3": "thermal", "HeatQ4": "thermal", "HeatQ8": "thermal", "HeatTet4": "thermal", "HeatH8": "thermal",
    "ConvectionBoundary": "thermal", "HeatFluxBoundary": "thermal",
    "thermal_load": "thermal", "thermal_stresses": "thermal",
    "zz_error_estimate": "error_estimation", "ErrorEstimate": "error_estimation",
}


def __getattr__(name: str) -> Any:
    """Lazy access to the optional sub-modules and their main classes (PEP 562)."""
    if name in _LAZY_MODULES:
        return importlib.import_module(f"aerokit.fem.{name}")
    if name in _LAZY_NAMES:
        return getattr(importlib.import_module(f"aerokit.fem.{_LAZY_NAMES[name]}"), name)
    raise AttributeError(f"module 'aerokit.fem' has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_MODULES) | set(_LAZY_NAMES))
