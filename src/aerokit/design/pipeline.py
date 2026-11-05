"""One-command conceptual design: requirements file → sized aircraft → compliance → figures → report.

``run(requirements, assumptions, out_dir)`` chains :func:`aerokit.design.sizing.size`, the point
performance of :mod:`aerokit.aero.performance` (requirement compliance and payload-range), the V-n
diagram, the wing planform, the one-at-a-time sensitivity study, and writes ``report.md`` plus the
datawiz-audited figures into ``out_dir``. Every number in the report is produced in the same run.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from aerokit import units
from aerokit.aero import geometry, loads
from aerokit.aero import performance as perf
from aerokit.aero.aircraft import G0
from aerokit.design import labels
from aerokit.design.requirements import Assumptions, Requirements, load_assumptions, load_requirements
from aerokit.design.sensitivity import SensitivityRow, tornado
from aerokit.design.sizing import SizingResult, constraint_curves, size
from aerokit.output.report import Report
from aerokit.output.writers import write_text_atomic
from aerokit.references import cite

__all__ = ["DesignRun", "lift_slope", "lift_slope_helmbold", "run"]

#: Anderson's rule of thumb for the high-aspect-ratio (lifting-line) formula: "AR > 4" (PDF p. 497)
LIFTING_LINE_MIN_AR = 4.0


@cite("anderson_2017", note="Helmbold, Eq. 5.81, for low-aspect-ratio straight wings, 'remarkably accurate "
                            "for wings with AR < 4' (PDF p. 497)")
def lift_slope_helmbold(AR: float, a0: float = 2 * math.pi) -> float:
    """Low-aspect-ratio wing lift-curve slope a = a0 / (√(1 + (a0/πAR)²) + a0/(πAR)) [1/rad]."""
    if not AR > 0 or not a0 > 0:
        raise ValueError("AR and a0 must be > 0")
    k = a0 / (math.pi * AR)
    return a0 / (math.sqrt(1.0 + k * k) + k)


@cite("anderson_2017", note="Eq. 5.69 (elliptic) / 5.70 (general planform, τ 0.05–0.25), PDF pp. 478–479; "
                            "high-AR straight wings 'AR > 4, as a rule of thumb', else Helmbold Eq. 5.81 (PDF p. 497)")
def lift_slope(AR: float, a0: float = 2 * math.pi, tau: float = 0.0) -> tuple[float, str]:
    """Straight-wing lift-curve slope [1/rad] with the formula Anderson recommends for this aspect ratio.

    ``AR > 4``: lifting line a = a0 / (1 + (a0/πAR)(1 + τ)) (τ = 0: elliptic loading).
    ``AR ≤ 4``: Helmbold, :func:`lift_slope_helmbold`. Returns ``(a, method label)``.
    """
    if not AR > 0 or not a0 > 0:
        raise ValueError("AR and a0 must be > 0")
    if not 0.0 <= tau < 1.0:
        raise ValueError("tau must be in [0, 1) (Anderson: typically 0.05–0.25)")
    if AR > LIFTING_LINE_MIN_AR:
        return a0 / (1.0 + a0 / (math.pi * AR) * (1.0 + tau)), f"lifting line, Anderson Eq. {'5.70' if tau else '5.69'}"
    return lift_slope_helmbold(AR, a0), "Helmbold, Anderson Eq. 5.81"


@dataclass
class DesignRun:
    """Everything one pipeline run produced."""

    requirements: Requirements
    assumptions: Assumptions
    sizing: SizingResult
    compliance: list[dict[str, Any]]
    sensitivity: list[SensitivityRow]
    planform: dict[str, float]
    vn: dict[str, Any]
    payload_range: dict[str, Any] | None
    report: Report
    files: list[str] = field(default_factory=list)


def _fmt(v: float, nd: int = 4) -> str:
    return "—" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f"{v:.{nd}g}"


#: requirement key → (display unit, dimension) for report tables (SI is kept in the JSON output)
_SHOW: dict[str, tuple[str, str]] = {
    "range": ("km", "length"), "loiter": ("min", "time"), "stall_speed": ("km/h", "speed"),
    "max_speed": ("km/h", "speed"), "max_speed_altitude": ("m", "length"), "service_ceiling": ("m", "length"),
    "rate_of_climb": ("m/s", "speed"), "takeoff_ground_roll": ("m", "length"), "landing_distance": ("m", "length"),
    "person_mass": ("kg", "mass"), "cargo_mass": ("kg", "mass"),
}


def _show(key: str, si: float | None) -> str:
    """Value of requirement ``key`` in its display unit, grouped digits, never E notation."""
    if si is None or not math.isfinite(si):
        return "—"
    if key in ("crew", "passengers"):
        return f"{si:.0f}"
    if key == "payload":
        return f"{si / G0:,.0f} kg".replace(",", " ")
    unit, dim = _SHOW.get(key, ("", "dimensionless"))
    v = units.to_unit(si, unit, dim) if unit else si
    text = f"{v:,.1f}" if abs(v) < 100 else f"{v:,.0f}"
    return (text.replace(",", " ") + (f" {unit}" if unit else "")).strip()


def run(requirements: str | Path | Requirements, assumptions: str | Path | Assumptions | None = None,
        out_dir: str | Path | None = None, figures: bool = True, target: str = "web-640") -> DesignRun:
    """Run the full chain (see module docstring); ``out_dir=None`` skips writing files."""
    req = requirements if isinstance(requirements, Requirements) else load_requirements(requirements)
    asm = assumptions if isinstance(assumptions, Assumptions) else load_assumptions(assumptions)
    rep = Report(title=f"Conceptual design — {req.name}")
    polar = None
    if asm["drag_method"] == "buildup":
        from aerokit.design.configuration import size_with_buildup
        s, polar, n_it = size_with_buildup(req, asm)
        asm = asm.with_(CD0_override=float(polar.CD0), e_override=float(polar.e))
        rep.table(["Component", "Re ×10⁶", "Cf", "FF", "Q", "Swet (m²)", "CD0 share"],
                  [[str(r["name"]), f"{float(r['Re']) / 1e6:.1f}", f"{float(r['Cf']):.4f}", f"{float(r['FF']):.3f}",
                    f"{float(r['Q']):.2f}", f"{float(r['Swet']):.2f}", f"{float(r['share']) * 100:.1f} %"]
                   for r in polar.buildup.as_rows() if "Re" in r],
                  title=f"Drag build-up on the sized wing: CD0 {polar.CD0:.4f}, e {polar.e:.3f}, "
                        f"L/Dmax {polar.LD_max:.2f} ({n_it} sizing iterations)")
    else:
        s = size(req, asm)
    ac = s.aircraft
    for w in s.warnings:
        rep.warn(w)

    # --- requirements and sizing
    rep.table(["Requirement", "As given", "Read as"], [[k, str(req.raw.get(k, "")), _show(k, v)]
                                                       for k, v in req.values.items()],
              title="Requirements (as given, and as parsed by the unit layer)")
    rep.table(["Constraint", "P/W at design W/S (W/N)", "Power (kW)"],
              [[k, f"{v:.2f}", f"{v * s.W0 / 1e3:.0f}"] for k, v in s.constraints.items()],
              title="Constraint diagram at the stall-limited wing loading")
    rep.table(["Quantity", "Value"], [
        ["Take-off mass W0", f"{s.mass:.0f} kg"], ["Wing area S", f"{s.S:.2f} m²"],
        ["Wing loading W/S", f"{s.WS:.0f} N/m² ({s.ws_basis})"],
        ["W/S limits", " · ".join(f"{k} {v:.0f} N/m²" for k, v in s.ws_limits.items())],
        ["Installed power (SL)", f"{s.P_installed / 1e3:.0f} kW"],
        ["Governing constraint", s.governing], ["Fuel fraction Wf/W0", f"{s.Wf_W0:.3f}"],
        ["Empty-weight fraction We/W0", f"{s.We_W0:.3f} (engine-mass correction {s.engine_we_add:+.4f}, "
                                        f"power_weight_coupling {asm['power_weight_coupling']})"],
        ["L/Dmax · CD0 · e", f"{s.LD_max:.1f} · {s.CD0:.4f} · {s.e:.3f}"],
        ["Payload", f"{s.payload_mass:.0f} kg"], ["Mission weight fraction", f"{s.mission_fraction:.4f}"]],
        title="Sized design")

    # --- geometry and loads
    taper = float(asm["taper_ratio"])
    pf = geometry.planform(s.S, float(asm["aspect_ratio"]), taper)
    CLa, cla_method = lift_slope(float(asm["aspect_ratio"]))
    vn = loads.vn_diagram(s.W0, s.S, float(pf["MAC"]), float(asm["CLmax_clean"]), CLa)
    plan_names = {"b": "Span b", "c_root": "Root chord", "c_tip": "Tip chord", "MAC": "Mean aerodynamic chord",
                  "y_MAC": "Spanwise MAC position"}
    rep.table(["Quantity", "Value"], [[plan_names.get(k, k), f"{v:.3f} m"] for k, v in pf.items()] +
              [[f"CLα ({cla_method})", f"{CLa:.3f} 1/rad"],
               ["n_max · n_min", f"{vn['n_max']:.2f} · {vn['n_min']:.2f}"]],
              title="Planform and loads")

    # --- compliance of the sized design (point performance)
    req_si = {k: v for k, v in req.values.items() if k in perf.REQUIREMENT_KEYS}
    req_si["payload"] = s.payload_mass * G0
    comp: list[dict[str, Any]] = [dict(r) for r in perf.compliance(ac, req_si)]
    for r in comp:
        # the design is sized exactly on its governing constraint: a relative miss below 1e-5 is the
        # tolerance of the constraint grid vs. the performance optimiser, not a real shortfall
        if not r["passed"] and r["margin"] > -1e-5:
            r["passed"] = True
            r["method"] = f"{r['method']} (on the sizing constraint, |margin| < 1e-5)"
    rep.table(["Requirement", "Required", "Achieved", "Margin", "Pass", "Note"],
              [[r["requirement"], _show(r["requirement"], r["required"]), _show(r["requirement"], r["achieved"]),
                labels.signed_percent(r["margin"]), "yes" if r["passed"] else "NO", f"[{i + 1}]"]
               for i, r in enumerate(comp)],
              title="Requirement compliance of the sized design (point performance)")
    for i, r in enumerate(comp):
        rep.note(f"[{i + 1}] {r['method']}")
    failed: list[str] = [str(r["requirement"]) for r in comp if not r["passed"]]
    if failed:
        rep.warn("requirements not met by the sized design: " + ", ".join(failed))

    # --- payload-range
    pr: dict[str, Any] | None = None
    try:
        h_cruise = float(req.get("max_speed_altitude", 3000.0) or 3000.0)
        pr = dict(perf.payload_range(ac, payload_max=s.payload_mass * G0, fuel_max=ac.W_fuel, h_cruise=h_cruise))
    except (ValueError, KeyError, TypeError) as exc:
        rep.warn(f"payload-range not computed: {exc}")

    # --- sensitivity
    _, sens = tornado(req, asm)
    sens = [x for x in sens if x.power_swing > 0.5e3]
    rep.table(["Assumption (low–high)", "W0 low / high (kg)", "Power low / high (kW)", "Governing low / high"],
              [[labels.label(x.key, x.low, x.high), f"{x.mass_low:.0f} / {x.mass_high:.0f}",
                f"{x.power_low / 1e3:.0f} / {x.power_high / 1e3:.0f}", f"{x.governing_low} / {x.governing_high}"]
               for x in sens], title="One-at-a-time sensitivity (sorted by power swing)")
    rep.table(["Assumption", "Value", "Source"], asm.table(), title="Assumptions")

    files: list[str] = []
    if out_dir is not None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        if figures:
            from aerokit.output import figures as F
            WS = np.linspace(0.4 * s.WS, 1.65 * s.WS, 80)
            limiting = min(s.ws_limits, key=lambda k: s.ws_limits[k])
            figs = [("constraint_diagram", lambda p: F.constraint_diagram(
                        WS, constraint_curves(req, asm, WS), s.ws_limits[limiting], (s.WS, s.PW), p,
                        governing=s.governing, target=target, limit_label=f"{limiting} limit")),
                    ("sensitivity_tornado", lambda p: F.tornado(
                        [labels.label(x.key, x.low, x.high) for x in sens[:8]], [x.power_low for x in sens[:8]],
                        [x.power_high for x in sens[:8]], s.P_installed, p, target=target)),
                    ("vn_diagram", lambda p: F.vn_diagram(vn, p, target=target))]
            if pr is not None:
                figs.append(("payload_range", lambda p: F.payload_range(
                    np.asarray(pr["range"]) / 1e3, np.asarray(pr["payload"]) / G0, p,
                    requirement=(req.require("range") / 1e3, s.payload_mass), target=target)))
            for name, build in figs:
                fig = build(str(out / name))
                files.append(f"{name}.png")
                if fig.report.errors:
                    rep.warn(f"figure {name}: {fig.report.summary}")
            rep.items.append("Figures: " + ", ".join(f"![{f}]({f})" for f in files))
        ok = not failed
        rep.conclude(f"W0 ≈ {s.mass:.0f} kg, S ≈ {s.S:.1f} m², P ≈ {s.P_installed / 1e3:.0f} kW ({s.governing} "
                     f"governs); {len(comp) - len(failed)}/{len(comp)} requirements met.",
                     "Replace the K_LD guess with the drag build-up (largest sensitivity), then plan the mission."
                     if ok else "Resize for the failed requirements (see the compliance table) and re-run.")
        write_text_atomic(out / "report.md", rep.render("md") + "\n", suffixes={".md"})
        files.append("report.md")
    else:
        rep.conclude(f"W0 ≈ {s.mass:.0f} kg, {s.governing} governs.", "Run with out_dir to write the report.")
    return DesignRun(req, asm, s, comp, sens, {k: float(v) for k, v in pf.items()}, vn, pr, rep, files)
