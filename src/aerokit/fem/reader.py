"""JSON model input → :class:`~aerokit.fem.model.Model`, and a solution summary.

Format (SI units)::

    {
      "ndof": 3,
      "nodes": [[0, 0], [2, 0]],
      "elements": [{"kind": "Frame2D", "nodes": [0, 1], "material": "7075-T6", "A": 1e-3, "I": 2e-6,
                    "q": -500}],
      "fixed": [{"node": 0, "dof": [0, 1, 2]}],
      "loads": [{"node": 1, "dof": 1, "value": -1000}],
      "analysis": "static" | "modal" | "buckling", "n": 4
    }

For plane problems a ``"mesh"`` key generates a structured rectangle instead of
``"nodes"``/``"elements"``::

    "mesh": {"kind": "Q8", "Lx": 1, "Ly": 0.1, "nx": 20, "ny": 2, "format": "stress", "t": 0.01,
             "material": "6061-T6"},
    "edge_fixed": {"left": [0, 1]},
    "edge_load": {"right": {"traction": [0, -1e6]}}     or  {"upper": {"pressure": 1e5}}

Edge names are those of :func:`aerokit.fem.mesh.mesh2d.mapped_mesh` (``lower``, ``right``,
``upper``, ``left``). A material is either a name from :mod:`aerokit.materials.library` or a
``{"E": .., "nu": .., "rho": ..}`` dictionary. Element kinds: ``Bar``, ``Frame2D``, ``Frame3D``,
``T3``, ``Q4``, ``QM6``, ``Q8`` (key ``"format"``: ``stress`` | ``strain`` | ``axisymmetric``) and
``MITC4`` (keys ``h``, ``q``, ``prestress``).
"""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from aerokit.fem.elements.line import Bar, Frame2D, Frame3D
from aerokit.fem.elements.plane import Q4, Q8, QM6, T3, D_isotropic
from aerokit.fem.elements.plate import MITC4
from aerokit.fem.mesh import mesh2d
from aerokit.fem.model import Model

__all__ = ["build_model", "from_file", "solve"]

ELEMENT_KINDS = ("Bar", "Frame2D", "Frame3D", "T3", "Q4", "QM6", "Q8", "MITC4")


def _material(m: Any) -> dict[str, Any]:
    """Material name or dictionary → ``{"E", "nu", "rho", "G"}``."""
    if isinstance(m, str):
        from aerokit.materials import library
        k = library.find(m)
        if "E" not in k:
            raise ValueError(f"'{m}' is not isotropic; give E, nu and rho explicitly in the FEM input")
        return {"E": k["E"], "nu": k["nu"], "rho": k.get("rho", 0.0), "G": k.get("G")}
    if not isinstance(m, dict) or "E" not in m:
        raise ValueError("material must be a name or an {'E', 'nu', 'rho'} dictionary")
    return {"E": m["E"], "nu": m.get("nu", 0.3), "rho": m.get("rho", 0.0), "G": m.get("G")}


def _element(e: Mapping[str, Any], ndof: int) -> Any:
    """One element dictionary → element object."""
    kind = e.get("kind")
    mat = _material(e.get("material", e))
    d = e["nodes"]
    if kind == "Bar":
        return Bar(d[0], d[1], mat["E"], e["A"], rho=mat["rho"], dim=ndof)
    if kind == "Frame2D":
        return Frame2D(d[0], d[1], mat["E"], e["A"], e["I"], rho=mat["rho"], q=e.get("q", 0.0))
    if kind == "Frame3D":
        G = mat["G"] or mat["E"] / (2 * (1 + mat["nu"]))
        return Frame3D(d[0], d[1], mat["E"], G, e["A"], e["Iy"], e["Iz"], e["J"], rho=mat["rho"],
                       ref=e.get("ref", (0.0, 0.0, 1.0)))
    if kind in ("T3", "Q4", "QM6", "Q8"):
        format = e.get("format", "stress")
        cls = {"T3": T3, "Q4": Q4, "QM6": QM6, "Q8": Q8}[kind]
        return cls(d, D_isotropic(mat["E"], mat["nu"], format), format=format, t=e.get("t", 1.0),
                   rho=mat["rho"], nu=mat["nu"], omega=e.get("omega", 0.0))
    if kind == "MITC4":
        return MITC4(d, mat["E"], mat["nu"], e["h"], rho=mat["rho"], q=e.get("q", 0.0),
                     prestress=e.get("prestress", (0.0, 0.0, 0.0)))
    raise ValueError(f"unknown element kind {kind!r} ({', '.join(ELEMENT_KINDS)})")


def _constant(value: tuple[float, ...]) -> Callable[[float, float], tuple[float, ...]]:
    """Traction function returning the same vector everywhere."""
    def traction(x: float, y: float) -> tuple[float, ...]:
        return value
    return traction


def build_model(data: Mapping[str, Any]) -> tuple[Model, dict[str, Any]]:
    """Build a model from a parsed JSON dictionary (format in the module docstring).

    Parameters
    ----------
    data : mapping
        Model description.

    Returns
    -------
    model : Model
    settings : dict
        ``{"analysis": "static" | "modal" | "buckling", "n": number of modes}``.

    Raises
    ------
    ValueError
        Unknown element kind or invalid material.
    KeyError
        Missing required key.
    """
    if "mesh" in data:
        a = data["mesh"]
        kind = a.get("kind", "Q4")
        topology = "Q4" if kind == "MITC4" else kind
        X, conn, edges = mesh2d.rectangle(a["Lx"], a["Ly"], a["nx"], a["ny"], topology,
                                          a.get("x0", 0.0), a.get("y0", 0.0))
        ndof = 3 if kind == "MITC4" else 2
        m = Model(X, ndof)
        for c in conn:
            m.add(_element(dict(a, kind=kind, nodes=c), ndof))
        for edge, dofs in data.get("edge_fixed", {}).items():
            for n in mesh2d.edge_nodes(edges[edge]):
                m.fix(n, dofs)
        for edge, y in data.get("edge_load", {}).items():
            format = a.get("format", "stress")
            if "traction" in y:
                tr = tuple(float(v) for v in y["traction"])
                m.F += mesh2d.edge_load(X, edges[edge], traction=_constant(tr), format=format,
                                        t=a.get("t", 1.0))
            else:
                m.F += mesh2d.edge_load(X, edges[edge], pressure=y["pressure"], format=format, t=a.get("t", 1.0))
    else:
        ndof = data["ndof"]
        m = Model(data["nodes"], ndof)
        for e in data["elements"]:
            m.add(_element(e, ndof))
    for s in data.get("fixed", []):
        m.fix(s["node"], s["dof"], s.get("value", 0.0))
    for y in data.get("loads", []):
        m.load(y["node"], y["dof"], y["value"])
    return m, {"analysis": data.get("analysis", "static"), "n": data.get("n", 4)}


def from_file(path: str | os.PathLike[str]) -> tuple[Model, dict[str, Any]]:
    """Read a JSON model file (UTF-8) with :func:`build_model`."""
    with open(path, encoding="utf-8") as f:
        return build_model(json.load(f))


def solve(model: Model, settings: Mapping[str, Any]) -> dict[str, Any]:
    """Run the requested analysis and return a summary dictionary.

    Parameters
    ----------
    model : Model
    settings : mapping
        ``{"analysis": "static" | "modal" | "buckling", "n": int}`` from :func:`build_model`.

    Returns
    -------
    dict
        static: ``max_node``, ``max_disp`` (all DOFs of that node), ``energy`` [J], ``reaction_total``;
        modal: ``f`` [Hz]; buckling: ``lambda_``. Always ``analysis`` and the full ``result``.

    Raises
    ------
    ValueError
        Unknown analysis type.
    """
    if settings["analysis"] == "static":
        r = model.static()
        u = r["u"].reshape(-1, model.ndof)
        if any(isinstance(e, MITC4) for e in model.elements):
            translation = [0]                               # plate: w
        else:
            translation = list(range(min(model.ndof, model.X.shape[1])))
        i = int(np.argmax(np.linalg.norm(u[:, translation], axis=1)))
        return {"analysis": "static", "max_node": i, "max_disp": u[i], "energy": r["energy"],
                "reaction_total": r["reaction"].reshape(-1, model.ndof).sum(axis=0), "result": r}
    if settings["analysis"] == "modal":
        rm = model.modal(settings["n"])
        return {"analysis": "modal", "f": rm["f"], "result": rm}
    if settings["analysis"] == "buckling":
        rb = model.buckling(settings["n"])
        return {"analysis": "buckling", "lambda_": rb["lambda_"], "result": rb}
    raise ValueError("analysis must be 'static' | 'modal' | 'buckling'")
