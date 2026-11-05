"""Command line: ``python -m aerokit <group> <command> [options]``.

Seven top-level groups (Hick budget ≤ 7): ``aero``, ``geometry``, ``mechanics``, ``composite``,
``fem``, ``sizing``, ``materials``. Every command accepts ``--format {text,md,json,csv}`` and
``--out FILE`` (format taken from the extension) and ends with exactly one ``Result:`` sentence
and one ``Next step:``. Units are SI; stress inputs are in MPa unless stated. Errors print one
line; set ``AEROKIT_TRACE=1`` for the full traceback.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from aerokit.cli import commands as C
from aerokit.output.console import capture, emit
from aerokit.output.report import FORMATS

__all__ = ["build_parser", "parser", "main"]


def _common(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("output")
    g.add_argument("--format", choices=FORMATS, default=None, help="report format (default: text, or from --out)")
    g.add_argument("--out", metavar="FILE", help="write the report to FILE (.txt, .md, .json, .csv)")


def _leaf(sub: argparse._SubParsersAction, name: str, func: object, help: str) -> argparse.ArgumentParser:  # noqa: A002
    s = sub.add_parser(name, help=help, description=help)
    s.set_defaults(func=func)
    _common(s)
    return s


def _group(sub: argparse._SubParsersAction, name: str, help: str) -> argparse._SubParsersAction:  # noqa: A002
    return sub.add_parser(name, help=help, description=help).add_subparsers(dest="command", required=True,
                                                                             metavar="command")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    p = argparse.ArgumentParser(prog="python -m aerokit",
                                description="Ideathon 2026 engineering toolkit (SI units; stress inputs in MPa).")
    top = p.add_subparsers(dest="group", required=True, metavar="group")

    # ---- aero
    g = _group(top, "aero", "atmosphere and flow set-up")
    s = _leaf(g, "isa", C.isa, "ISA atmosphere table")
    s.add_argument("--h", type=float, nargs="+", default=[0, 1000, 3000, 5000, 10000], help="altitude(s) [m]")
    s = _leaf(g, "flow", C.flow, "Re, Mach, first-cell height, layer count, cell budget")
    s.add_argument("--U", type=float, required=True, help="speed [m/s]")
    s.add_argument("--L", type=float, required=True, help="reference length (chord) [m]")
    s.add_argument("--h", type=float, default=0.0, help="altitude [m] (0)")
    s.add_argument("--yplus", type=float, default=1.0, help="target y⁺ (1)")
    s.add_argument("--growth", type=float, default=1.15, help="inflation growth ratio (1.15)")
    s.add_argument("--surface", type=float, help="number of surface faces → cell budget")

    # ---- geometry
    g = _group(top, "geometry", "airfoil, planform, CAD import + preliminary FEM")
    s = _leaf(g, "airfoil", C.airfoil, "NACA 4-digit airfoil points")
    s.add_argument("--naca", required=True, help="4-digit code, e.g. 2412")
    s.add_argument("--chord", type=float, default=1.0, help="chord [m] (1)")
    s.add_argument("--points", type=int, default=121, help="points per surface (121)")
    s.add_argument("--closed", action="store_true", help="sharp (closed) trailing edge")
    s.add_argument("--output", help="point-file path")
    s.add_argument("--file-format", dest="file_format", choices=["xyz", "dm"], default="xyz",
                   help="xyz | dm (DesignModeler, not verified)")
    s = _leaf(g, "planform", C.planform, "trapezoidal wing dimensions (b, chords, MAC)")
    s.add_argument("--S", type=float, required=True, help="wing area [m²]")
    s.add_argument("--AR", type=float, required=True, help="aspect ratio")
    s.add_argument("--taper", type=float, default=0.5, help="taper ratio (0.5)")
    s = _leaf(g, "cad", C.cad, "import STL/OBJ/PLY → geometry report, optional FEM")
    s.add_argument("file")
    s.add_argument("--unit", default="mm", help="file unit: mm | cm | m | in (mm)")
    s.add_argument("--material", help="material for mass and FEM")
    s.add_argument("--fem", action="store_true", help="tetrahedral mesh + static solve (cantilever-like)")
    s.add_argument("--h", type=float, help="mesh size [m] (8 %% of the largest dimension)")
    s.add_argument("--element", choices=["T4", "T10"], default="T10")
    s.add_argument("--axis", choices=["x", "y", "z"], default="y", help="min face fixed, max face loaded (y)")
    s.add_argument("--load", type=float, default=1000.0, help="total load [N] (1000)")
    s.add_argument("--load-direction", dest="load_direction", choices=["x", "y", "z"], default="z")

    # ---- mechanics
    g = _group(top, "mechanics", "stress, wing, section, buckling, vessel, life, joint")
    s = _leaf(g, "tensor", C.tensor, "stress tensor: principal values, von Mises, Tresca, safety")
    s.add_argument("--s", type=float, nargs="+", required=True, metavar="MPa",
                   help="σxx [σyy σzz τxy τyz τxz]; missing components are 0")
    s.add_argument("--yield-strength", dest="yield_strength", type=float, help="yield strength [MPa]")
    s.add_argument("--material", help="material name (list: aerokit materials list)")
    s = _leaf(g, "wing", C.wing, "wing-root loads, box-beam stresses, margins")
    s.add_argument("--mass", type=float, required=True, help="aircraft mass [kg]")
    s.add_argument("--n", type=float, help="limit load factor (default: FAR 23.337 normal-category formula)")
    s.add_argument("--FS", type=float, default=1.5, help="ultimate factor (1.5)")
    s.add_argument("--b", type=float, required=True, help="wing span [m]")
    s.add_argument("--c-root", dest="c_root", type=float, required=True, help="root chord [m]")
    s.add_argument("--c-tip", dest="c_tip", type=float, required=True, help="tip chord [m]")
    s.add_argument("--box-b", dest="box_b", type=float, required=True, help="box width (between spars) [m]")
    s.add_argument("--box-h", dest="box_h", type=float, required=True, help="box height [m]")
    s.add_argument("--t-skin", dest="t_skin", type=float, required=True, help="upper/lower skin thickness [m]")
    s.add_argument("--t-spar", dest="t_spar", type=float, required=True, help="spar web thickness [m]")
    s.add_argument("--panel-b", dest="panel_b", type=float, help="buckling panel width [m] (box-b)")
    s.add_argument("--material", help="material name")
    s = _leaf(g, "section", C.section, "section properties: rectangle, tube, I or DXF profile")
    s.add_argument("--shape", choices=["rectangle", "tube", "I", "dxf"], required=True)
    s.add_argument("--dimension", type=float, nargs="+", default=[],
                   help="rectangle: b h · tube: D t · I: bf tf h tw [m]")
    s.add_argument("--dxf", help="DXF profile file (--shape dxf)")
    s = _leaf(g, "buckling", C.buckling, "column (Euler/Johnson), plate, thin cylinder")
    s.add_argument("--kind", choices=["column", "plate", "cylinder"], required=True)
    s.add_argument("--material", help="material name (E, ν, Fty taken from it)")
    s.add_argument("--E", type=float, help="E [GPa] (without --material)")
    s.add_argument("--I", type=float, help="column: I [m⁴]")
    s.add_argument("--A", type=float, help="column: A [m²]")
    s.add_argument("--L", type=float, help="column: length [m]")
    s.add_argument("--K", type=float, default=1.0, help="effective-length factor (1)")
    s.add_argument("--sigma-cy", dest="sigma_cy", type=float, help="column: compressive yield [MPa] (Johnson)")
    s.add_argument("--a-b", dest="a_b", type=float, help="plate: a/b")
    s.add_argument("--edge", default="SS-SS", help="unloaded plate edges: SS-SS, C-C, SS-F … (SS-SS)")
    s.add_argument("--t", type=float, help="plate/cylinder thickness [m]")
    s.add_argument("--b", type=float, help="plate width [m]")
    s.add_argument("--r", type=float, help="cylinder radius [m]")
    s = _leaf(g, "vessel", C.vessel, "thick-walled cylinder (Lamé) or rotating disk")
    s.add_argument("--kind", choices=["cylinder", "disk"], required=True)
    s.add_argument("--material", required=True)
    s.add_argument("--ri", type=float, help="inner radius [m]")
    s.add_argument("--ro", type=float, help="outer radius [m]")
    s.add_argument("--p", type=float, help="internal pressure [MPa]")
    s.add_argument("--rpm", type=float, help="rotational speed [rpm]")
    s.add_argument("--b", type=float, help="disk outer radius [m]")
    s.add_argument("--a", type=float, default=0.0, help="disk bore radius [m] (0)")
    s = _leaf(g, "life", C.life, "fatigue safety factor, or critical crack / Paris life")
    s.add_argument("--kind", choices=["fatigue", "crack"], required=True)
    s.add_argument("--sa", type=float, help="stress amplitude [MPa]")
    s.add_argument("--sm", type=float, default=0.0, help="mean stress [MPa] (0)")
    s.add_argument("--Se", type=float, help="endurance limit [MPa]")
    s.add_argument("--Sut", type=float, help="ultimate tensile strength [MPa]")
    s.add_argument("--method", default="goodman", choices=["goodman", "gerber", "soderberg"])
    s.add_argument("--Kc", type=float, help="fracture toughness [MPa√m]")
    s.add_argument("--sigma", type=float, help="applied stress [MPa]")
    s.add_argument("--W", type=float, help="plate width [m] (centre crack, Feddersen correction)")
    s.add_argument("--a0", type=float, default=1e-3, help="initial half crack length [m] (0.001)")
    s.add_argument("--C", type=float, help="Paris C (m/cycle with MPa√m)")
    s.add_argument("--m", type=float, default=3.0, help="Paris exponent (3)")
    s.add_argument("--dsigma", type=float, help="stress range [MPa]")
    s = _leaf(g, "joint", C.joint, "margins of a single-row bolted/riveted joint")
    s.add_argument("--P", type=float, required=True, help="load per fastener [N]")
    s.add_argument("--d", type=float, required=True, help="diameter [m]")
    s.add_argument("--t", type=float, required=True, help="sheet thickness [m]")
    s.add_argument("--w", type=float, required=True, help="sheet width [m]")
    s.add_argument("--e", type=float, required=True, help="edge distance [m]")
    s.add_argument("--Fbru", type=float, required=True, help="sheet bearing strength [MPa]")
    s.add_argument("--Fsu", type=float, help="fastener shear strength [MPa] (default: from material)")
    s.add_argument("--planes", type=int, default=1, help="number of shear planes (1)")
    s.add_argument("--FS", type=float, default=1.5, help="safety factor (1.5)")
    s.add_argument("--material", required=True, help="sheet material")

    # ---- composite
    g = _group(top, "composite", "laminate stresses, constants, progressive failure, layup")
    s = _leaf(g, "lamina", C.lamina, "CLT: ply stresses and Tsai-Wu")
    s.add_argument("--sequence", required=True, help='angles, trailing "s" = symmetric: "0,45,-45,90,s"')
    s.add_argument("--t", type=float, default=0.000125, help="ply thickness [m] (0.000125)")
    s.add_argument("--N", type=float, nargs=3, default=[0, 0, 0], metavar=("Nx", "Ny", "Nxy"), help="[N/m]")
    s.add_argument("--M", type=float, nargs=3, default=[0, 0, 0], metavar=("Mx", "My", "Mxy"), help="[N·m/m]")
    s.add_argument("--material", required=True, help="composite ply name")
    s = _leaf(g, "failure", C.failure, "laminate constants + first/last-ply failure (FPF/LPF)")
    s.add_argument("--sequence", required=True, help='e.g. "0,45,-45,90,s"')
    s.add_argument("--t", type=float, default=0.000131, help="ply thickness [m]")
    s.add_argument("--load", type=float, nargs=3, default=[1.0, 0.0, 0.0], metavar=("Nx", "Ny", "Nxy"),
                   help="load direction/magnitude [N/m] (1 0 0)")
    s.add_argument("--criterion", default="tsai_wu",
                   choices=["max_stress", "max_strain", "tsai_hill", "hoffman", "tsai_wu", "hashin", "puck", "larc03"])
    s.add_argument("--material", required=True)
    s = _leaf(g, "layup", C.layup, "stacking-sequence optimisation (buckling/stiffness/FPF)")
    s.add_argument("--material", required=True)
    s.add_argument("--t", type=float, default=0.000131, help="ply thickness [m]")
    s.add_argument("--n-stack", dest="n_stack", type=int, default=6, help="half-symmetric stacks (6 → 24 plies)")
    s.add_argument("--objective", default="buckling",
                   choices=["buckling", "stiffness", "fpf", "strain", "buckling_strain"])
    s.add_argument("--load", type=float, nargs=2, default=[1.0, 0.0], metavar=("Nx", "Ny"))
    s.add_argument("--a", type=float, default=0.5, help="plate length [m] (0.5)")
    s.add_argument("--b", type=float, default=0.25, help="plate width [m] (0.25)")
    s.add_argument("--method", choices=["exhaustive", "genetic"], default="exhaustive")

    # ---- fem
    g = _group(top, "fem", "solve JSON models, examples, convergence, optimisation, verification")
    s = _leaf(g, "solve", C.fem_solve, "solve a JSON model (static / modal / buckling)")
    s.add_argument("file")
    s.add_argument("--plot", help="figure path without extension (static analysis)")
    s = _leaf(g, "example", C.fem_example, "list or run the bundled example models")
    s.add_argument("name", nargs="?")
    s.add_argument("--plot", help="figure path without extension")
    s = _leaf(g, "convergence", C.fem_convergence, "mesh convergence: refinement, order, Richardson, GCI")
    s.add_argument("file", help="JSON model with a 'mesh' entry")
    s.add_argument("--levels", type=int, nargs="+", default=[1, 2, 4], help="mesh factors (1 2 4)")
    s = _leaf(g, "topology", C.fem_topology, "SIMP topology optimisation (top88: OC/MMA, filters)")
    s.add_argument("--problem", choices=["mbb", "cantilever", "lbracket"], default="mbb")
    s.add_argument("--nelx", type=int, default=60, help="elements in x (60); side length for the L-bracket")
    s.add_argument("--nely", type=int, default=20, help="elements in y (20)")
    s.add_argument("--volume", type=float, default=0.5, help="volume fraction (0.5)")
    s.add_argument("--rmin", type=float, default=2.4, help="filter radius [elements] (2.4)")
    s.add_argument("--ft", type=int, choices=[0, 1, 2, 3], default=1,
                   help="0 none, 1 sensitivity, 2 density, 3 Heaviside")
    s.add_argument("--optimizer", choices=["OC", "MMA"], default="OC")
    s.add_argument("--max-iter", dest="max_iter", type=int, default=1000)
    s.add_argument("--plot", help="figure path without extension")
    s = _leaf(g, "optimum", C.fem_optimum, "minimum-mass truss (stress, displacement, Euler)")
    s.add_argument("file")
    s.add_argument("--tension", type=float, required=True, help="allowable tension [MPa]")
    s.add_argument("--compression", type=float, help="allowable compression [MPa] (default: = tension)")
    s.add_argument("--A-min", dest="A_min", type=float, default=1e-6, help="minimum area [m²] (1e-6)")
    s.add_argument("--disp-node", dest="disp_node", type=int, help="node with a displacement limit")
    s.add_argument("--disp-dof", dest="disp_dof", type=int, default=1, help="local DOF (1 = y)")
    s.add_argument("--disp-limit", dest="disp_limit", type=float, help="displacement limit [m]")
    s.add_argument("--euler", action="store_true", help="add Euler buckling constraints (solid square section)")
    s.add_argument("--plot", help="figure path without extension")
    _leaf(g, "verify", C.fem_verify, "run the FEM verification tests")

    # ---- sizing
    g = _group(top, "sizing", "conceptual sizing and preliminary design")
    s = _leaf(g, "raymer", C.raymer, "Raymer sizing (defaults = 2023 Ansys task)")
    from aerokit.aero import sizing
    s.add_argument("--kind", default="twin turboprop", choices=list(sizing.EMPTY_WEIGHT), help="Raymer Table 3.1 type")
    s.add_argument("--crew", type=int, default=4)
    s.add_argument("--passengers", type=int, default=10)
    s.add_argument("--person-kg", dest="person_kg", type=float, default=91.0, help="mass per person [kg] (91)")
    s.add_argument("--extra-load-kg", dest="extra_load_kg", type=float, default=200.0, help="cargo [kg] (200)")
    s.add_argument("--range-km", dest="range_km", type=float, default=1300.0)
    s.add_argument("--loiter-min", dest="loiter_min", type=float, default=30.0)
    s.add_argument("--V-loiter-kmh", dest="V_loiter_kmh", type=float, default=250.0, help="loiter speed (250, assumed)")
    s.add_argument("--V-stall-kmh", dest="V_stall_kmh", type=float, default=150.0)
    s.add_argument("--Vmax-kmh", dest="Vmax_kmh", type=float, default=500.0)
    s.add_argument("--h-vmax", dest="h_vmax", type=float, default=0.0, help="altitude of Vmax [m] (0)")
    s.add_argument("--ceiling", type=float, default=10000.0, help="service ceiling [m]")
    s.add_argument("--climb", type=float, default=10.0, help="sea-level climb rate [m/s]")
    s.add_argument("--takeoff-m", dest="takeoff_m", type=float, default=800.0, help="ground run [m]")
    s.add_argument("--AR", type=float, default=9.0, help="aspect ratio (9, assumed)")
    s.add_argument("--KLD", type=float, default=11.0,
                   help="L/Dmax = KLD·√(AR/(Swet/Sref)) (11: retractable-gear propeller aircraft)")
    s.add_argument("--swet-sref", dest="swet_sref", type=float, default=5.5, help="wetted-area ratio (5.5, assumed)")
    s.add_argument("--eta", type=float, default=0.8, help="propeller efficiency (0.8)")
    s.add_argument("--eta-takeoff", dest="eta_takeoff", type=float, default=0.6,
                   help="take-off propeller efficiency (0.6, assumed)")
    s.add_argument("--cbhp-cruise", dest="cbhp_cruise", type=float, default=0.5, help="lb/(hp·h) (turboprop 0.5)")
    s.add_argument("--cbhp-loiter", dest="cbhp_loiter", type=float, default=0.6, help="lb/(hp·h) (turboprop 0.6)")
    s.add_argument("--CLmax-landing", dest="CLmax_landing", type=float, default=2.0, help="(2.0; Scholz 1.6–2.5)")
    s.add_argument("--CLmax-takeoff", dest="CLmax_takeoff", type=float, default=1.7, help="(1.7; Scholz 1.4–2.0)")
    s.add_argument("--CLmax-clean", dest="CLmax_clean", type=float, default=1.5, help="(1.5; Scholz 1.2–1.8)")
    s = _leaf(g, "design", C.design, "requirements file → sizing, compliance, sensitivity, figures, report.md")
    s.add_argument("requirements",
                   help="requirements JSON with units, e.g. data/examples/design/ansys_2023_requirements.json")
    s.add_argument("--assumptions", help="assumptions JSON (missing keys take documented defaults)")
    s.add_argument("--out-dir", dest="out_dir", default="design_report", help="output folder (design_report)")
    s.add_argument("--drag", choices=["kld", "buildup"], help="override the drag method of the assumptions")
    s.add_argument("--no-figures", dest="no_figures", action="store_true", help="skip figures (faster)")
    s = _leaf(g, "mission", C.mission, "search mission: route, coverage, waypoints, STK Aviator sheet, emissions")
    s.add_argument("mission", help="mission JSON with units, e.g. data/examples/design/ansys_2023_mission.json")
    s.add_argument("--requirements", required=True, help="requirements JSON used to size the aircraft")
    s.add_argument("--assumptions", help="assumptions JSON")
    s.add_argument("--drag", choices=["kld", "buildup"], help="override the drag method")
    s.add_argument("--out-dir", dest="out_dir", help="write waypoints, Aviator sheet and the map here")
    s.add_argument("--no-figures", dest="no_figures", action="store_true", help="skip the map figure")
    s.add_argument("--optimize", action="store_true",
                   help="search altitude × speed × overlap for the largest covered area first (PS/CS)")
    _leaf(g, "validate", C.validate, "compare the model with King Air 350i published data")
    s = _leaf(g, "vn", C.vn, "V-n diagram (FAR 23 maneuver + gust)")
    s.add_argument("--mass", type=float, required=True, help="mass [kg]")
    s.add_argument("--S", type=float, required=True, help="wing area [m²]")
    s.add_argument("--c", type=float, required=True, help="mean aerodynamic chord [m]")
    s.add_argument("--CLmax", type=float, default=1.5, help="clean CLmax (1.5)")
    s.add_argument("--CLa", type=float, default=5.0, help="aircraft CLα [1/rad] (5.0)")
    s.add_argument("--h", type=float, default=0.0, help="altitude [m] (0)")
    s.add_argument("--category", default="normal", choices=["normal", "utility", "acrobatic", "commuter"])
    s.add_argument("--plot", help="figure path without extension")
    s = _leaf(g, "point", C.design_point, "optimum design point of the constraint diagram (2023 requirements)")
    s.add_argument("--rule", choices=["ws_max", "pw_min"], default="ws_max", help="largest W/S or smallest P/W")
    s = _leaf(g, "box", C.wing_box, "minimum-mass wing box (regional thickness, stringer/rib spacing)")
    s.add_argument("--mass", type=float, required=True, help="aircraft mass [kg]")
    s.add_argument("--n", type=float, required=True, help="limit load factor")
    s.add_argument("--b", type=float, required=True, help="span [m]")
    s.add_argument("--c-root", dest="c_root", type=float, required=True, help="root chord [m]")
    s.add_argument("--c-tip", dest="c_tip", type=float, required=True, help="tip chord [m]")
    s.add_argument("--t-c", dest="t_c", type=float, default=0.12, help="thickness ratio (0.12)")
    s.add_argument("--regions", type=int, default=6, help="spanwise regions (6)")
    s.add_argument("--material", default="7075-T6")

    # ---- materials
    g = _group(top, "materials", "material catalogue and MIL-HDBK-5J design allowables")
    s = _leaf(g, "list", C.materials_list, "catalogue materials (or --handbook: all MIL-HDBK-5J sheets)")
    s.add_argument("--handbook", action="store_true", help="list the MIL-HDBK-5J sheets instead")
    for name, func, text in (("allowable", C.materials_allowable, "MIL-HDBK-5J design allowables"),
                             ("curve", C.materials_curve, "Ramberg-Osgood stress-strain curve and tangent modulus")):
        s = _leaf(g, name, func, text)
        s.add_argument("name", help="catalogue name (7075-T6) or MIL-HDBK-5J sheet (al-7050-t7451)")
        s.add_argument("--basis", choices=["A", "B", "S"], default="A", type=str.upper)
        s.add_argument("--direction", choices=["L", "LT", "ST", "T"], default="L", type=str.upper)
        s.add_argument("--thickness", type=float, help="product thickness (selects the table row)")
        s.add_argument("--thickness-units", dest="thickness_units", choices=["m", "mm", "in"], default="mm",
                       help="unit of --thickness (mm)")
    s.add_argument("--stress-max", dest="stress_max", type=float, default=1.1, help="curve end as a multiple of Fty")
    s.add_argument("--points", type=int, default=12, help="number of curve points (12)")
    return p


parser = build_parser          # backwards-compatible name


def _safe_streams() -> None:
    """Never crash on a console or pipe that cannot encode σ, ρ, μ (e.g. cp1254)."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                if stream.isatty():
                    stream.reconfigure(errors="replace")
                else:
                    stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):           # pragma: no cover - exotic streams
                stream.reconfigure(errors="replace")


def main(argv: Sequence[str] | None = None) -> None:
    """Parse ``argv``, run the command and print or write its report."""
    _safe_streams()
    args = build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))
    title = f"aerokit {args.group} {getattr(args, 'command', '')}".strip()
    try:
        with capture(title) as report:
            args.func(args)
        emit(report, args.format, args.out)
    except SystemExit:
        raise
    except Exception as exc:                       # one line for the user; AEROKIT_TRACE=1 for the trace
        if os.environ.get("AEROKIT_TRACE"):
            raise
        sys.exit(f"Error ({type(exc).__name__}): {exc}")


if __name__ == "__main__":
    main()
