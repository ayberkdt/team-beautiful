"""Task-card driven first half of a light-weighting slot: loads → topology sweep → verification → trade-off.

A *card* is a JSON file holding what the competition task card gives (geometry, loads, limits, service
temperature) plus the trade-off study whose life-cycle factors apply. :func:`run` turns it into a JSON-ready
result: ultimate load, one SIMP design per retained-volume level, a plane-stress check of every
(material, design) pair, the lightest passing design per material and its life-cycle CO₂.

The structural model is 2-D plane stress on unit-square Q4 elements (``aerokit.optimization.topology``).
Quantities are solved for unit load, unit modulus and unit thickness and then scaled:
``σ = σ_unit · P / (h · t)`` and ``δ = δ_unit · P / (E · t)`` with element size ``h`` and thickness ``t``.
Stress is the element-centre von Mises value; elements within ``exclude_elements`` of the load node or of any
fixed node are left out (point-load and support singularities). The coarse-mesh deflection is multiplied by a
factor measured by re-solving one design on a 4× refined mesh (:func:`mesh_check`).

Card schema (SI units)::

    {"name": str, "source": str,
     "geometry": {"type": "l_bracket", "size_m": 0.12, "arm_ratio": 0.4, "thickness_m": 0.01, "elements": 60}
              | {"type": "cantilever", "length_m": 0.2, "height_m": 0.1, "thickness_m": 0.01, "elements": 60,
                 "load_at": "lower" | "middle"}
              | {"type": "bridge", "length_m": 0.2, "height_m": 0.05, "thickness_m": 0.01, "elements": 80}
              | {"type": "pin_link", "length_m": 0.12, "height_m": 0.04, "bore_diameter_m": 0.012,
                 "ring_m": 0.003, "load_cases": [[1, 0], [-1, 0], [0, -0.3]], "thickness_m": 0.01, "elements": 90}
                 (both short edges bolted, load at mid-span on the lower edge),
     "loads": {"value_N": 2000, "kind": "limit" | "ultimate"},
     "factors": {"factor_of_safety": 1.5, "fitting_factor": 1.15},
     "limits": {"deflection_m": 0.0005, "service_temperature_C": 60, "frequency_Hz_min": 150},
     "added_mass_kg": 0.4,                        # equipment carried at the load node (counts in the modal check)
     "thermal": {"delta_T_K": 150, "structure_alpha_per_K": 2e-6},   # part vs the structure it is bolted to
     "fatigue": {"amplitude_N": 600, "mean_N": 600, "cycles": 1e7},
     "material_data": {"Ti-6Al-4V": {"alpha_per_K": 8.6e-6, "fatigue_strength_Pa": 5.0e8, "Ftu_Pa": 9.5e8,
                                     "E_Pa_at_T": 1.05e11, "Fty_Pa_at_T": 7.0e8, "source": "..."}},
     "volumes": [0.5, 0.35, 0.3, 0.25],
     "topology": {"rmin": 2.4, "ft": 2, "optimizer": "OC", "max_iter": 400},
     "study": "prev_guess/01_Ansys/tradeoff/bracket_a320_strength.json",
     "candidates": [["Scalmalloy", "am_TO"], ["7075-T6", "machined_TO"], ...]}

Optional checks (each adds a utilisation; the largest one is ``governs``; a check whose material data is missing
marks the row as not passing and lists the missing key — silence is not a pass):

* ``frequency``: f₁ of the solid part with ``added_mass_kg`` lumped at the load node must reach
  ``frequency_Hz_min`` (utilisation f_min / f₁);
* ``thermal``: von Mises of ultimate-load stress plus the stress of a uniform ``delta_T_K`` with
  ``α_eff = α_part − structure_alpha_per_K`` against ``Fty_Pa_at_T`` (or ``Fty``);
* ``fatigue``: Goodman ``σ_a / S_f + σ_m / F_tu`` from ``amplitude_N`` and ``mean_N`` with the peak unit stress
  (no notch factor: the topology result has no fillets yet).
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from aerokit.design import card_physics as cp
from aerokit.optimization import topology as tp

__all__ = ["Card", "TEMPERATURE_LIMITS_C", "load_card", "problem", "centre_von_mises", "tension_check", "analyse",
           "mesh_check", "run"]

TEMPERATURE_LIMITS_C: dict[str, tuple[float, str]] = {
    "Scalmalloy": (100.0, "properties fall sharply above 373 K (Mehta et al. 2022, Metals 12:57); yield 319 MPa at "
                          "150 C and 60 MPa at 300 C vs 475 MPa at room temperature (Colibrium Additive datasheet "
                          "2025-08-21)"),
}
"""Service-temperature ceilings used to screen candidates, with their source."""


@dataclass
class Card:
    name: str
    geometry: dict[str, Any]
    load_N: float
    load_kind: str
    factor_of_safety: float
    fitting_factor: float
    deflection_limit_m: float | None
    service_temperature_C: float | None
    volumes: list[float]
    topology: dict[str, Any]
    study: dict[str, Any]
    candidates: list[tuple[str, str]]
    source: str = ""
    frequency_Hz_min: float | None = None
    added_mass_kg: float = 0.0
    thermal: dict[str, float] | None = None
    fatigue: dict[str, float] | None = None
    material_data: dict[str, dict[str, Any]] | None = None

    @property
    def ultimate_N(self) -> float:
        if self.load_kind == "ultimate":
            return self.load_N
        return self.load_N * self.factor_of_safety * self.fitting_factor

    @property
    def limit_N(self) -> float:
        return self.load_N if self.load_kind == "limit" else self.load_N / (self.factor_of_safety * self.fitting_factor)


def load_card(path: str | Path, root: str | Path | None = None) -> Card:
    """Read and validate a card; ``study`` is resolved against ``root`` (default: the nearest folder above the card
    that holds ``pyproject.toml``, i.e. the project root; the card's grandparent if there is none)."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if root is None:
        here = path.resolve()
        root = next((p for p in here.parents if (p / "pyproject.toml").is_file()), here.parents[2])
    return _parse(raw, Path(root))


def _parse(raw: Mapping[str, Any], root: Path) -> Card:
    for key in ("name", "geometry", "loads", "volumes", "study", "candidates"):
        if key not in raw:
            raise ValueError(f"card: missing {key!r}")
    g = dict(raw["geometry"])
    if g.get("type") not in ("l_bracket", "cantilever", "bridge", "pin_link"):
        raise ValueError("geometry.type must be 'l_bracket', 'cantilever', 'bridge' or 'pin_link'")
    if g["type"] == "pin_link":
        for k in ("length_m", "height_m", "bore_diameter_m", "ring_m"):
            if not float(g.get(k, 0)) > 0:
                raise ValueError(f"geometry.{k} must be > 0 for a pin_link")
        if not g.get("load_cases"):
            raise ValueError("geometry.load_cases: give at least one [fx, fy] case for a pin_link")
    for k in ("thickness_m", "elements"):
        if not float(g.get(k, 0)) > 0:
            raise ValueError(f"geometry.{k} must be > 0")
    loads = raw["loads"]
    kind = loads.get("kind", "limit")
    if kind not in ("limit", "ultimate") or not float(loads.get("value_N", 0)) > 0:
        raise ValueError("loads: value_N > 0 and kind 'limit' or 'ultimate'")
    vols = [float(v) for v in raw["volumes"]]
    if not vols or not all(0 < v < 1 for v in vols):
        raise ValueError("volumes must lie in (0, 1)")
    study_path = Path(raw["study"])
    study = json.loads((study_path if study_path.is_absolute() else root / study_path).read_text(encoding="utf-8"))
    cands = [(str(m), str(r)) for m, r in raw["candidates"]]
    for m, r in cands:
        if m not in study["materials"] or r not in study["routes"]:
            raise ValueError(f"candidate ({m}, {r}) not in the study file")
    f = raw.get("factors", {})
    lim = raw.get("limits", {})
    return Card(str(raw["name"]), g, float(loads["value_N"]), kind, float(f.get("factor_of_safety", 1.5)),
                float(f.get("fitting_factor", 1.15)),
                float(lim["deflection_m"]) if lim.get("deflection_m") is not None else None,
                float(lim["service_temperature_C"]) if lim.get("service_temperature_C") is not None else None,
                vols, {"rmin": 2.4, "ft": 2, "optimizer": "OC", "max_iter": 400, **raw.get("topology", {})},
                study, cands, str(raw.get("source", "")),
                float(lim["frequency_Hz_min"]) if lim.get("frequency_Hz_min") is not None else None,
                float(raw.get("added_mass_kg", 0.0)),
                _numbers(raw.get("thermal")),
                _numbers(raw.get("fatigue")),
                {m: dict(d) for m, d in raw.get("material_data", {}).items()})


def _numbers(block: Mapping[str, Any] | None) -> dict[str, float] | None:
    """Numeric fields of an optional card block; keys starting with ``_`` are notes and are skipped."""
    return {k: float(v) for k, v in block.items() if not k.startswith("_")} if block else None


def problem(card: Card, refine: int = 1) -> tuple[tp.Problem, tuple[int, int], float, float]:
    """(Problem with P = 1, load node (ix, iy), element size h [m], design-space area [m²]) for ``refine``×mesh."""
    g = card.geometry
    n = int(g["elements"]) * refine
    if g["type"] == "l_bracket":
        size = float(g["size_m"])
        ratio = float(g.get("arm_ratio", 0.4))
        pr = tp.l_bracket(n, P=1.0, ratio=ratio)
        h = size / n
        area = size ** 2
        return pr, (n, int(round(ratio * n))), h, area
    length, height = float(g["length_m"]), float(g["height_m"])
    nely = int(round(height / length * n))
    if g["type"] == "pin_link":
        h = length / n
        r = float(g["bore_diameter_m"]) / 2 / h
        pr = tp.pin_link(n, nely, r, float(g["ring_m"]) / h, [(float(c[0]), float(c[1])) for c in g["load_cases"]])
        return pr, (n - nely // 2 + int(round(r)), nely // 2), h, length * height
    if g["type"] == "bridge":
        grid = tp.Grid2D(n, nely)
        fixed = [grid.dof(ix, iy, d) for ix in (0, n) for iy in range(nely + 1) for d in (0, 1)]
        mid = n // 2
        return tp.Problem(grid, {grid.dof(mid, 0, 1): -1.0}, fixed), (mid, 0), length / n, length * height
    at = g.get("load_at", "lower")
    if at == "middle" and nely % 2:
        nely += 1
    pr = tp.cantilever(n, nely, P=1.0, load=at)
    return pr, (n, 0 if at == "lower" else nely // 2), length / n, length * height


def centre_von_mises(grid: tp.Grid2D, U: np.ndarray, nu: float, case: int = 0) -> np.ndarray:
    """Element-centre von Mises (plane stress) for unit elements, unit modulus and unit thickness (load ``case``)."""
    dNdx = np.array([-0.5, 0.5, 0.5, -0.5])
    dNdy = np.array([-0.5, -0.5, 0.5, 0.5])
    ue = U[grid.edof][:, :, case]
    u, v = ue[:, 0::2], ue[:, 1::2]
    ex, ey, gxy = u @ dNdx, v @ dNdy, u @ dNdy + v @ dNdx
    c = 1.0 / (1 - nu ** 2)
    sx, sy, txy = c * (ex + nu * ey), c * (ey + nu * ex), c * (1 - nu) / 2 * gxy
    return np.sqrt(sx ** 2 - sx * sy + sy ** 2 + 3 * txy ** 2)


def tension_check(nu: float = 0.3) -> float:
    """σ(von Mises) / (P / (h t)) in a uniformly stretched 20 × 10 plate; 1 when the stress recovery is right."""
    g = tp.Grid2D(20, 10, nu)
    fixed = [g.dof(0, iy, 0) for iy in range(11)] + [g.dof(0, 0, 1)]
    F = {g.dof(20, iy, 0): (0.5 if iy in (0, 10) else 1.0) / 10 for iy in range(11)}
    U = tp.Problem(g, F, fixed).analysis(np.ones(g.nel))[2]
    return float(np.median(centre_von_mises(g, U, nu))) / 0.1


def analyse(card: Card, structure: np.ndarray, refine: int = 1, exclude: int = 3, nu: float = 0.3,
            fields: bool = False) -> dict:
    """Unit-load response of a black-and-white ``structure`` (density-array shape of the unrefined grid).

    With ``fields=True`` the result also holds ``"_fields"``: grid, problem, element densities, displacements,
    the mask of elements read for stress and the load node, for the modal and thermal checks.
    """
    pr, (lx, ly), h, _ = problem(card, refine)
    grid = pr.grid
    if not isinstance(grid, tp.Grid2D):
        raise TypeError(f"card analysis needs a Grid2D, got {type(grid).__name__}")
    s = np.kron(np.asarray(structure, float), np.ones((refine, refine))) if refine > 1 else np.asarray(structure, float)
    x = pr.grid.vector(s)
    x[pr.passive == 1] = 0.0
    # protected solid rings (pin_link) stay solid on a refined mesh: the up-sampled coarse pixels do not follow the
    # finer bore edge, and a loaded node left among void elements would make a mechanism
    x[pr.passive == 2] = 1.0
    U = pr.analysis(x)[2]
    # several load cases (pin_link): the envelope of the element stresses, and per case the displacement along
    # the load, F·U / Σ|F| (a single unit nodal load gives exactly that node's displacement, as before)
    vm = np.max([centre_von_mises(grid, U, nu, k) for k in range(pr.F.shape[1])], axis=0)
    along = [abs(float(pr.F[:, k] @ U[:, k])) / float(np.abs(pr.F[:, k]).sum()) for k in range(pr.F.shape[1])]
    vm[x < 0.5] = 0.0
    c = grid.element_center()
    k = exclude * refine
    fixed_nodes = np.unique(pr.fixed // 2)
    fx = grid.X[fixed_nodes]
    near_fixed = np.zeros(len(c), bool)
    for start in range(0, len(fixed_nodes), 256):
        d = np.abs(c[:, None, :] - fx[None, start:start + 256, :]).max(axis=2)
        near_fixed |= (d < k).any(axis=1)
    loaded = grid.X[np.unique(np.flatnonzero(np.abs(pr.F).sum(axis=1)) // 2)]
    near_load = np.abs(c[:, None, :] - loaded[None, :, :]).max(axis=2).min(axis=1) < k
    ok = (x > 0.5) & ~near_fixed & ~near_load
    out: dict[str, Any] = {"solid_elements": int((x > 0.5).sum()), "solid_fraction": float((x > 0.5).mean()),
           "vm_unit_max": float(vm[ok].max()) * refine, "vm_unit_p99": float(np.percentile(vm[ok], 99)) * refine,
           "tip_unit": max(along), "element_size_m": h}
    if fields:
        out["_fields"] = {"grid": grid, "problem": pr, "x": x, "U": U, "ok": ok, "load_node": grid.node(lx, ly)}
    return out


def mesh_check(card: Card, structure: np.ndarray, factors: tuple[int, ...] = (1, 2, 4)) -> list[dict]:
    """The same design re-solved with every element split k × k; stresses already rescaled to the base size."""
    return [{"refinement": k, **analyse(card, structure, refine=k)} for k in factors]


def _designs(card: Card) -> list[dict]:
    pr, *_ = problem(card)
    t = card.topology
    out = []
    for v in sorted(card.volumes, reverse=True):
        r = tp.topopt(pr, v, float(t["rmin"]), ft=int(t["ft"]), optimizer=str(t["optimizer"]),
                      max_iter=int(t["max_iter"]))
        out.append({"volume": v, "density": np.asarray(r["xfiz"]), "iterations": int(r["iteration"]),
                    "grey_percent": float(r["gray"]), "compliance": float(r["compliance"][-1])})
    return out


def _material(card: Card, mat: str) -> dict[str, Any]:
    """Study-file properties of ``mat`` overlaid with the card's ``material_data`` for it."""
    m = dict(card.study["materials"][mat])
    m.update((card.material_data or {}).get(mat, {}))
    return m


def run(card: Card, designs: list[dict] | None = None) -> dict:
    """Full first-half evaluation; ``designs`` may be passed to skip the topology runs (e.g. in tests)."""
    g = card.geometry
    t = float(g["thickness_m"])
    designs = designs if designs is not None else _designs(card)
    want_fields = card.frequency_Hz_min is not None or card.thermal is not None
    for d in designs:
        d["structure"] = tp.binarize(d["density"], 0.5)["structure"]
        d.update(analyse(card, d["structure"], fields=want_fields))
        if card.thermal is not None:
            f = d["_fields"]
            d["_thermal_unit"] = cp.thermal_unit(f["grid"], f["x"], f["problem"].fixed)
            d["_mech_unit"] = cp.centre_stress(f["grid"], f["U"], f["grid"].nu)
    pivot = min(designs, key=lambda d: abs(d["volume"] - 0.35))
    mesh = mesh_check(card, pivot["structure"])
    k_defl = mesh[-1]["tip_unit"] / mesh[0]["tip_unit"]
    _, _, h, area = problem(card)
    s = card.study
    life = s["lifecycle"]
    use_factor = (life["fuel_per_kg_per_flight"]["value"] * life["flights"]["value"]
                  * life["co2_per_kg_fuel"]["value"])
    grid_co2 = life["grid_co2_per_MJ"]["value"]
    rows, excluded = [], []
    for mat, route in card.candidates:
        lim = TEMPERATURE_LIMITS_C.get(mat)
        if lim and card.service_temperature_C is not None and card.service_temperature_C > lim[0]:
            excluded.append({"material": mat, "route": route, "reason": f"service {card.service_temperature_C} C > "
                                                                          f"{lim[0]} C: {lim[1]}"})
            continue
        m, r = _material(card, mat), s["routes"][route]
        E = float(m.get("E_Pa_at_T", m["E"]))
        Fty = float(m.get("Fty_Pa_at_T", m["Fty"]))
        for d in designs:
            mass = d["solid_elements"] * h * h * t * m["rho"]
            sigma = d["vm_unit_max"] * card.ultimate_N / (h * t)
            defl = d["tip_unit"] * card.limit_N / (E * t) * k_defl
            btf = area * t * m["rho"] / mass if route.startswith("machined") else r["buy_to_fly"]["value"]
            bought = mass * btf
            prod = bought * m["co2_per_kg"]["value"] + bought * r["process_MJ_per_kg"]["value"] * grid_co2
            util: dict[str, float] = {"strength": sigma / Fty}
            if card.deflection_limit_m:
                util["deflection"] = defl / card.deflection_limit_m
            missing: list[str] = []
            extra: dict[str, Any] = {}
            if card.frequency_Hz_min is not None:
                f = d["_fields"]
                pm = {f["load_node"]: card.added_mass_kg} if card.added_mass_kg > 0 else None
                try:
                    f1 = cp.modal(f["grid"], f["x"], f["problem"].fixed, E, m["rho"], t, h, pm,
                                  n=1)["frequencies_Hz"][0]
                except ValueError:          # one-element diagonal members: the thresholded design is a mechanism
                    f1 = 0.0
                    extra["load_path"] = "broken: the load node is held only through corner contacts"
                extra["f1_Hz"] = f1
                util["frequency"] = card.frequency_Hz_min / f1 if f1 > 0 else float("inf")
            if card.thermal is not None:
                if "alpha_per_K" not in m:
                    missing.append("alpha_per_K")
                else:
                    a_eff = float(m["alpha_per_K"]) - card.thermal.get("structure_alpha_per_K", 0.0)
                    th = E * a_eff * card.thermal["delta_T_K"] * d["_thermal_unit"]
                    mech = d["_mech_unit"] * card.ultimate_N / (h * t)
                    ok = d["_fields"]["ok"]
                    s_th = float(cp.von_mises(th)[ok].max())
                    s_comb = float(cp.von_mises(th + mech)[ok].max())
                    extra.update({"sigma_thermal_Pa": s_th, "sigma_combined_Pa": s_comb, "alpha_eff_per_K": a_eff})
                    util["thermal"] = s_comb / Fty
            if card.fatigue is not None:
                need = [k for k in ("fatigue_strength_Pa", "Ftu_Pa") if k not in m]
                if need:
                    missing += need
                else:
                    per_N = d["vm_unit_max"] / (h * t)
                    sa = per_N * card.fatigue.get("amplitude_N", 0.0)
                    sm = per_N * card.fatigue.get("mean_N", 0.0)
                    extra.update({"sigma_a_Pa": sa, "sigma_m_Pa": sm})
                    util["fatigue"] = sa / float(m["fatigue_strength_Pa"]) + sm / float(m["Ftu_Pa"])
            governs = max(util, key=lambda k: util[k])
            rows.append({"material": mat, "route": route, "volume": d["volume"], "mass_kg": mass,
                         "sigma_ult_Pa": sigma, "sigma_over_Fty": sigma / Fty, "deflection_m": defl,
                         "buy_to_fly": btf, "passes": bool(not missing and max(util.values()) <= 1.0),
                         "governs": governs, "utilisation": util, "missing": missing, **extra,
                         "co2_production_kg": prod, "co2_use_kg": mass * use_factor,
                         "co2_total_kg": prod + mass * use_factor})
    best: dict[str, dict] = {}
    for row in rows:
        key = f"{row['material']} / {row['route']}"
        if row["passes"] and (key not in best or row["mass_kg"] < best[key]["mass_kg"]):
            best[key] = row
    ranking = sorted(best.values(), key=lambda r: r["co2_total_kg"])
    hidden = ("density", "structure", "_fields", "_thermal_unit", "_mech_unit")
    return {"card": card.name, "source": card.source, "ultimate_N": card.ultimate_N, "limit_N": card.limit_N,
            "element_size_m": h, "tension_check": tension_check(), "deflection_mesh_factor": k_defl,
            "mesh_check": [{k: v for k, v in m.items() if k != "element_size_m"} for m in mesh],
            "designs": [{k: v for k, v in d.items() if k not in hidden} for d in designs],
            "rows": rows, "ranking": ranking, "excluded": excluded,
            "note": "2-D plane stress; element-centre von Mises excluding elements near the load and supports; "
                    "deflection multiplied by the 4x-mesh factor; yield at ultimate as the allowable"
                    + ("; f1 from the solid elements with consistent mass" if card.frequency_Hz_min else "")
                    + ("; thermal: uniform dT, supports held by a structure growing with structure_alpha"
                       if card.thermal else "")
                    + ("; fatigue: Goodman on peak unit stress, no notch factor" if card.fatigue else "")}
