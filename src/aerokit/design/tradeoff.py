"""Material × manufacturing-route trade-off for a light-weighted part: mass, life-cycle CO₂, cost.

The study is defined in a JSON file so that a person or an agent can replace any input with a value read on
the day (Granta EduPack, a datasheet) without touching code. Every numeric input is a *factor*::

    {"value": 0.12, "low": 0.07, "high": 0.16, "unit": "kg fuel / kg / flight",
     "source": "Steinegger 2017, Fig. 15", "tag": "A"}

``tag`` records how the value was obtained (D read from source in the session that wrote the file, A read by a
sub-agent, S search snippet only, Y assumption / judgement, H calculated). ``low``/``high`` default to ``value``.
Factors with the same optional ``group`` move together in the Monte Carlo (one uniform quantile per group and
sample), e.g. the embodied CO₂ of alloys that share a smelting route.

Model per option (material *m*, route *r*):

* part mass ``M = M_ref · (I_ref / I_m) · k_r`` — the performance-index ratio of
  :func:`aerokit.materials.selection.performance_index` for the governing ``case`` scales the reference part
  (same geometry family, same stiffness or strength), ``k_r`` is the route's mass factor (e.g. < 1 when AM allows
  the topology-optimised shape that machining cannot make);
* production CO₂ ``M · btf_r · c_m + M · btf_r · e_r · g`` — material bought (buy-to-fly ``btf``) times its
  embodied CO₂ ``c_m``, plus process energy ``e_r`` [MJ per kg processed] times the grid factor ``g``
  [kg CO₂/MJ];
* use CO₂ ``M · f · N · c_fuel`` — fuel per kg carried per flight ``f`` (:func:`aerokit.design.sustainability.
  fuel_per_kg_carried` or a published marginal factor), flights over life ``N``, CO₂ per kg fuel;
* cost (optional) ``M · btf_r · p + M · q`` — material price ``p`` per kg bought and route cost ``q`` per kg of
  finished part, either per (material, route) pair (``materials.<m>.cost_by_route.<r>``, preferred: powder and
  plate prices differ, titanium machines dearer than aluminium) or as ``price_per_kg`` / ``cost_per_kg``.

* end of life (optional) ``−M · eol_credit_per_kg`` — the CO₂ a material's recycling route avoids per kg of
  part, reported **apart** from the total as ``co2_eol_potential_kg`` (Granta EduPack's Eco Audit shows the
  end-of-life potential beside the life total, not inside it); the objective ``co2_total_with_eol_kg`` ranks
  with it counted, for a sensitivity view.

Screening (optional) removes options before ranking and says why: a material record may carry
``max_service_C`` and ``flags`` (e.g. ``"fst_cabin"`` for a cabin flammability approval); the study's
``constraints`` give ``service_temperature_C`` and ``require`` (flags every option must have).

Outputs: nominal table, Pareto set (non-dominated on the chosen objectives), penalty ``Z = Σ α_i · objective_i``
with exchange constants, Monte Carlo over uniform factor ranges (probability each option is best, 5/50/95 %
of each objective) and a one-at-a-time tornado on the margin between the best option and the runner-up.
"""
from __future__ import annotations

import json
import math
import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aerokit.materials.selection import performance_index

__all__ = ["Factor", "Study", "OptionResult", "load_study", "evaluate", "pareto", "penalty", "monte_carlo",
           "tornado", "run"]

TAGS = {"D", "A", "S", "Y", "H"}
OBJECTIVES = ("mass_kg", "co2_production_kg", "co2_use_kg", "co2_total_kg", "co2_total_with_eol_kg", "cost")


@dataclass(frozen=True)
class Factor:
    """A numeric input with its uncertainty range and provenance."""

    value: float
    low: float
    high: float
    unit: str = ""
    source: str = ""
    tag: str = "Y"
    group: str = ""

    @classmethod
    def parse(cls, raw: Any, where: str) -> Factor:
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            raise ValueError(f"{where}: give a factor object with 'value', 'unit', 'source', 'tag' (got a bare number)")
        if not isinstance(raw, Mapping) or "value" not in raw:
            raise ValueError(f"{where}: factor needs at least 'value'")
        v = float(raw["value"])
        lo, hi = float(raw.get("low", v)), float(raw.get("high", v))
        tag = str(raw.get("tag", "Y"))
        if tag not in TAGS:
            raise ValueError(f"{where}: tag {tag!r} not in {sorted(TAGS)}")
        if not lo <= v <= hi:
            raise ValueError(f"{where}: need low <= value <= high (got {lo}, {v}, {hi})")
        if not all(math.isfinite(x) for x in (lo, v, hi)):
            raise ValueError(f"{where}: values must be finite")
        return cls(v, lo, hi, str(raw.get("unit", "")), str(raw.get("source", "")), tag, str(raw.get("group", "")))

    def at(self, which: str) -> float:
        return {"value": self.value, "low": self.low, "high": self.high}[which]


@dataclass
class Study:
    """Parsed study file."""

    name: str
    case: str
    reference_material: str
    reference_mass: Factor
    lifecycle: dict[str, Factor]
    materials: dict[str, dict[str, Any]]          # props (floats) + "co2_per_kg", optional "price_per_kg" (Factor)
    routes: dict[str, dict[str, Factor]]
    options: list[tuple[str, str]]
    objectives: tuple[str, ...]
    exchange: dict[str, float] = field(default_factory=dict)
    exchange_unit: str = ""
    screened: list[dict[str, str]] = field(default_factory=list)

    def factors(self) -> dict[str, Factor]:
        """Every uncertain input, keyed by a dotted path (used by Monte Carlo and the tornado)."""
        out = {"reference_mass": self.reference_mass}
        out.update({f"lifecycle.{k}": v for k, v in self.lifecycle.items()})
        for m, rec in self.materials.items():
            for k in ("co2_per_kg", "price_per_kg", "eol_credit_per_kg"):
                if k in rec:
                    out[f"materials.{m}.{k}"] = rec[k]
            for r, pair in rec.get("cost_by_route", {}).items():
                for k, f in pair.items():
                    out[f"materials.{m}.cost_by_route.{r}.{k}"] = f
        for r, rec in self.routes.items():
            out.update({f"routes.{r}.{k}": v for k, v in rec.items()})
        return out


_LIFE = ("fuel_per_kg_per_flight", "flights", "co2_per_kg_fuel", "grid_co2_per_MJ")
_ROUTE = ("buy_to_fly", "process_MJ_per_kg", "mass_factor")


def load_study(path: str | Path) -> Study:
    """Read and validate a study JSON file (see ``studies/tradeoff/README.md`` for the schema)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return _parse(raw)


def _parse(raw: Mapping[str, Any]) -> Study:
    for key in ("name", "case", "reference_material", "reference_mass", "lifecycle", "materials", "routes"):
        if key not in raw:
            raise ValueError(f"study: missing {key!r}")
    life = {k: Factor.parse(raw["lifecycle"].get(k), f"lifecycle.{k}") for k in _LIFE}
    mats: dict[str, dict[str, Any]] = {}
    for m, rec in raw["materials"].items():
        props = {k: float(rec[k]) for k in ("E", "Fty", "rho") if k in rec}
        if "rho" not in props:
            raise ValueError(f"materials.{m}: 'rho' is required")
        props_src = rec.get("properties_source", "")
        entry: dict[str, Any] = {**props, "properties_source": props_src,
                                 "co2_per_kg": Factor.parse(rec.get("co2_per_kg"), f"materials.{m}.co2_per_kg")}
        for k in ("price_per_kg", "eol_credit_per_kg"):
            if k in rec:
                entry[k] = Factor.parse(rec[k], f"materials.{m}.{k}")
        if "max_service_C" in rec:
            entry["max_service_C"] = float(rec["max_service_C"])
        entry["flags"] = [str(x) for x in rec.get("flags", [])]
        if "cost_by_route" in rec:
            entry["cost_by_route"] = {
                r: {k: Factor.parse(pair[k], f"materials.{m}.cost_by_route.{r}.{k}")
                    for k in ("price_per_kg", "route_cost_per_kg")}
                for r, pair in rec["cost_by_route"].items()}
        mats[m] = entry
    routes: dict[str, dict[str, Factor]] = {}
    for r, rec in raw["routes"].items():
        routes[r] = {k: Factor.parse(rec.get(k), f"routes.{r}.{k}") for k in _ROUTE}
        if "cost_per_kg" in rec:
            routes[r]["cost_per_kg"] = Factor.parse(rec["cost_per_kg"], f"routes.{r}.cost_per_kg")
    if raw["reference_material"] not in mats:
        raise ValueError("reference_material must be one of materials")
    opts_raw = raw.get("options", "all")
    if opts_raw == "all":
        opts = [(m, r) for m in mats for r in routes]
    else:
        opts = [(o["material"], o["route"]) for o in opts_raw]
        for m, r in opts:
            if m not in mats or r not in routes:
                raise ValueError(f"option ({m}, {r}) refers to an unknown material or route")
    cons = raw.get("constraints", {})
    screened: list[dict[str, str]] = []
    keep = []
    for m, r in opts:
        why = []
        t_req = cons.get("service_temperature_C")
        if t_req is not None and "max_service_C" in mats[m] and float(t_req) > mats[m]["max_service_C"]:
            why.append(f"service {float(t_req):g} C > max {mats[m]['max_service_C']:g} C")
        lacking = [f for f in cons.get("require", []) if f not in mats[m]["flags"]]
        if lacking:
            why.append("lacks " + ", ".join(lacking))
        if why:
            screened.append({"material": m, "route": r, "reason": "; ".join(why)})
        else:
            keep.append((m, r))
    if not keep:
        raise ValueError("every option is screened out by the constraints")
    opts = keep
    objectives = tuple(raw.get("objectives", ["mass_kg", "co2_total_kg"]))
    for o in objectives:
        if o not in OBJECTIVES:
            raise ValueError(f"objective {o!r} not in {OBJECTIVES}")
    if "cost" in objectives:
        missing = [f"{m}/{r}" for m, r in opts
                   if r not in mats[m].get("cost_by_route", {})
                   and ("price_per_kg" not in mats[m] or "cost_per_kg" not in routes[r])]
        if missing:
            raise ValueError(f"cost objective needs price_per_kg / cost_per_kg for: {', '.join(sorted(set(missing)))}")
    exchange = {k: float(v) for k, v in raw.get("exchange", {}).items()}
    for k in exchange:
        if k not in objectives:
            raise ValueError(f"exchange constant for {k!r}, which is not an objective")
    return Study(str(raw["name"]), str(raw["case"]), str(raw["reference_material"]),
                 Factor.parse(raw["reference_mass"], "reference_mass"), life, mats, routes, opts, objectives,
                 exchange, str(raw.get("exchange_unit", "")), screened)


@dataclass(frozen=True)
class OptionResult:
    material: str
    route: str
    mass_kg: float
    co2_production_kg: float
    co2_use_kg: float
    cost: float | None
    co2_eol_potential_kg: float = 0.0
    co2_material_kg: float = 0.0          # share of co2_production_kg from the material bought

    @property
    def co2_total_kg(self) -> float:
        return self.co2_production_kg + self.co2_use_kg

    @property
    def co2_total_with_eol_kg(self) -> float:
        return self.co2_total_kg + self.co2_eol_potential_kg

    @property
    def label(self) -> str:
        return f"{self.material} / {self.route}"

    def objective(self, name: str) -> float:
        v = getattr(self, name)
        if v is None:
            raise ValueError(f"objective {name!r} not computed (missing cost inputs)")
        return float(v)

    def as_dict(self) -> dict[str, Any]:
        return {"material": self.material, "route": self.route, "mass_kg": self.mass_kg,
                "co2_production_kg": self.co2_production_kg, "co2_use_kg": self.co2_use_kg,
                "co2_total_kg": self.co2_total_kg, "co2_eol_potential_kg": self.co2_eol_potential_kg,
                "co2_material_kg": self.co2_material_kg,
                "co2_process_kg": self.co2_production_kg - self.co2_material_kg, "cost": self.cost}


def evaluate(study: Study, pick: Callable[[str, Factor], float] | None = None) -> list[OptionResult]:
    """Evaluate every option; ``pick(path, factor)`` chooses the value of each factor (default: nominal)."""
    def val(path: str, f: Factor) -> float:
        return pick(path, f) if pick else f.value

    ref = study.materials[study.reference_material]
    i_ref = performance_index(ref, study.case)
    m_ref = val("reference_mass", study.reference_mass)
    life = {k: val(f"lifecycle.{k}", f) for k, f in study.lifecycle.items()}
    out = []
    for m, r in study.options:
        rec, route = study.materials[m], study.routes[r]
        rv = {k: val(f"routes.{r}.{k}", f) for k, f in route.items()}
        mass = m_ref * i_ref / performance_index(rec, study.case) * rv["mass_factor"]
        bought = mass * rv["buy_to_fly"]
        co2_mat = val(f"materials.{m}.co2_per_kg", rec["co2_per_kg"])
        prod = bought * co2_mat + bought * rv["process_MJ_per_kg"] * life["grid_co2_per_MJ"]
        use = mass * life["fuel_per_kg_per_flight"] * life["flights"] * life["co2_per_kg_fuel"]
        cost = None
        pair = rec.get("cost_by_route", {}).get(r)
        if pair:
            cost = (bought * val(f"materials.{m}.cost_by_route.{r}.price_per_kg", pair["price_per_kg"])
                    + mass * val(f"materials.{m}.cost_by_route.{r}.route_cost_per_kg", pair["route_cost_per_kg"]))
        elif "price_per_kg" in rec and "cost_per_kg" in route:
            cost = bought * val(f"materials.{m}.price_per_kg", rec["price_per_kg"]) + mass * rv["cost_per_kg"]
        eol = -mass * val(f"materials.{m}.eol_credit_per_kg", rec["eol_credit_per_kg"]) \
            if "eol_credit_per_kg" in rec else 0.0
        out.append(OptionResult(m, r, mass, prod, use, cost, eol, bought * co2_mat))
    return out


def pareto(results: list[OptionResult], objectives: tuple[str, ...]) -> list[OptionResult]:
    """Non-dominated options (all objectives minimised)."""
    def dominates(a: OptionResult, b: OptionResult) -> bool:
        av, bv = [a.objective(o) for o in objectives], [b.objective(o) for o in objectives]
        return all(x <= y for x, y in zip(av, bv, strict=True)) and any(x < y for x, y in zip(av, bv, strict=True))
    return [a for a in results if not any(dominates(b, a) for b in results if b is not a)]


def penalty(results: list[OptionResult], exchange: Mapping[str, float]) -> dict[str, float]:
    """``Z = Σ α_i · objective_i`` per option label (Ashby's penalty function; exchange constants α_i)."""
    if not exchange:
        raise ValueError("no exchange constants given")
    return {r.label: sum(a * r.objective(o) for o, a in exchange.items()) for r in results}


def _score(results: list[OptionResult], study: Study) -> dict[str, float]:
    return penalty(results, study.exchange) if study.exchange else {r.label: r.co2_total_kg for r in results}


def monte_carlo(study: Study, samples: int = 2000, seed: int = 1) -> dict[str, Any]:
    """Uniform sampling of every factor in [low, high]; best = lowest penalty (or total CO₂ without exchange)."""
    if samples < 1:
        raise ValueError("samples must be >= 1")
    rng = random.Random(seed)  # noqa: S311 - reproducible sampling, not cryptography
    wins: dict[str, int] = {}
    hist: dict[str, dict[str, list[float]]] = {}
    for _ in range(samples):
        shared: dict[str, float] = {}

        def draw(path: str, f: Factor, shared: dict[str, float] = shared) -> float:
            if f.low == f.high:
                return f.value
            u = shared.setdefault(f.group, rng.random()) if f.group else rng.random()
            return f.low + u * (f.high - f.low)
        res = evaluate(study, draw)
        sc = _score(res, study)
        best = min(sc, key=lambda k: sc[k])
        wins[best] = wins.get(best, 0) + 1
        for r in res:
            h = hist.setdefault(r.label, {})
            for o in study.objectives:
                h.setdefault(o, []).append(r.objective(o))

    def q(xs: list[float], p: float) -> float:
        s = sorted(xs)
        return s[min(len(s) - 1, max(0, int(round(p * (len(s) - 1)))))]

    return {"samples": samples, "seed": seed,
            "p_best": {k: wins.get(k, 0) / samples for k in hist},
            "quantiles": {k: {o: {"p05": q(v, 0.05), "p50": q(v, 0.5), "p95": q(v, 0.95)} for o, v in h.items()}
                          for k, h in hist.items()}}


def tornado(study: Study) -> list[dict[str, Any]]:
    """One factor at a time at low/high: margin = score(runner-up) − score(best) at nominal ranking.

    A negative margin means that factor alone, at that end of its range, reverses the nominal choice.
    """
    nominal = _score(evaluate(study), study)
    order = sorted(nominal, key=lambda k: nominal[k])
    if len(order) < 2:
        raise ValueError("tornado needs at least two options")
    best, second = order[0], order[1]
    rows = []
    for path, f in study.factors().items():
        if f.low == f.high:
            continue
        m = {}
        for end in ("low", "high"):
            def one(p: str, g: Factor, path: str = path, end: str = end) -> float:
                return g.at(end) if p == path else g.value
            sc = _score(evaluate(study, one), study)
            m[end] = sc[second] - sc[best]
        rows.append({"factor": path, "unit": f.unit, "low": f.low, "high": f.high, "tag": f.tag,
                     "margin_low": m["low"], "margin_high": m["high"],
                     "swing": abs(m["high"] - m["low"]), "reverses": min(m.values()) < 0})
    return sorted(rows, key=lambda r: -r["swing"])


def run(study: Study, samples: int = 2000, seed: int = 1) -> dict[str, Any]:
    """Everything in one JSON-ready dictionary."""
    res = evaluate(study)
    sc = _score(res, study)
    ranked = sorted(res, key=lambda r: sc[r.label])
    unsourced = sorted(p for p, f in study.factors().items() if f.tag in ("S", "Y"))
    return {"study": study.name, "case": study.case, "objectives": list(study.objectives),
            "score": "penalty" if study.exchange else "co2_total_kg", "exchange": study.exchange,
            "exchange_unit": study.exchange_unit,
            "nominal": [dict(r.as_dict(), score=sc[r.label], rank=i + 1) for i, r in enumerate(ranked)],
            "pareto": [r.label for r in pareto(res, study.objectives)],
            "monte_carlo": monte_carlo(study, samples, seed), "tornado": tornado(study),
            "weak_inputs": unsourced, "screened": study.screened}
