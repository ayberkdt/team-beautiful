"""Result figures built and audited with datawiz.

Sub-modules: :mod:`.fem` (stress contour, deformed frame, truss areas), :mod:`.aero` (V-n diagram,
span loads), :mod:`.optimization` (topology map); shared saving/report types in :mod:`._common`.
Every function returns a :class:`Figure` whose ``report.errors`` must be 0 before a figure is used.
"""
from aerokit.output.figures._common import DEFAULT_TARGET, Figure, FigureReport
from aerokit.output.figures.aero import span_distribution, vn_diagram
from aerokit.output.figures.design import constraint_diagram, payload_range, tornado
from aerokit.output.figures.fem import fem2d_contour, frame_shape, truss_areas
from aerokit.output.figures.mission import mission_map
from aerokit.output.figures.optimization import topology_map

__all__ = ["DEFAULT_TARGET", "Figure", "FigureReport", "fem2d_contour", "frame_shape", "truss_areas",
           "vn_diagram", "span_distribution", "topology_map", "constraint_diagram", "tornado", "payload_range",
           "mission_map"]
