"""Material screening gate: decide which materials need a topology/FEA evaluation at all — in seconds, before
any optimisation. Run: python -I analysis/screening.py   (from official_2026-11-05/) -> analysis/screening.{json,md}

Why one topology run is enough for every survivor [K, doc 22 §2]: for a linear isotropic part under prescribed loads
the stress field does not depend on E, and displacements scale with 1/E; a compliance-optimal layout at volume
fraction f is therefore the same for every material. Materials only differ in which layout they can afford.

Gates (each failure records its reason; first failing gate eliminates):
  G0 reference  - the card asks to REPLACE the initial-design steel: S275N is the reference, not a candidate.
  G1 temperature - card: "Working temperature >300 °C". Upper end of the max-service-temperature range must be
                   > 300 °C; a range whose top is exactly 300 fails the strict reading (kept as a flagged sensitivity).
                   Unknown Tmax: aluminium / magnesium / polymer / composite families are eliminated by a family rule
                   [Y: age-hardened Al over-ages above ~200 °C (catalogue: 2618-T61 keeps 60 % Ftu after 1000 h at
                   204 °C, MIL-HDBK-5J Fig 3.2.13.1.1(a)); polymer/epoxy matrices are below 300 °C].
  G2 process    - card: "Ability to be casted or 3D printed": organiser records use the Granta stage-2 result (all
                   three passed it [D-org]); pool records need an AM/L-PBF/powder/casting route in their data.
  G3 toughness  - K1c >= 10 MPa m^0.5 where known [D-org]; unknown metals are not eliminated (flag).
  G4 bound      - analytic lower bound on mass from the BASELINE FEA (runs/baseline_fixed_bores/report.md):
                   strength (fully stressed): f >= 1.5 * sigma0 / Fy ; stiffness (compliance ~ 1/f): f >= u0 E0 / (E u_lim);
                   non-design minimum f >= 0.126 [K]. m_min = rho V0 max(...), CO2_min from the organisers' eco model.
  G5 dominance  - eliminated if its CO2_min (life, first life) is above the CO2 of a design that is GUARANTEED for another
                   survivor (its unchanged geometry, f = 1, which already passes). CO2 ~ mass here (use phase = 97 %).
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from organiser_materials import M as ORG, eco, gm   # noqa: E402

V0 = 0.0193975          # m^3, exact solid (visuals/scripts/out/volume_check.json)
SIG0, U0, E0 = 57.9, 0.2047, 182.7     # MPa, mm, GPa — baseline voxel FEA, worst case (LC1a/b), fixed bores
U_LIM = 661.01 / 400
FOS, T_REQ = 1.5, 300.0
F_MIN = 0.126   # non-design rings around the 6 bores = 12.6 % of the part (topology run 12:20, ValueError text) [K]
USE_PER_KG = 4000 * 180 * 0.000468     # kg CO2 per kg of part over the 1-year life (card)
TR_PER_KG = 500 * 0.241 / 1000
# powder-forming CO2 per kg by family, from the organisers' report (geometric means of S275N / 2618 / Ti-8-1-1) [D-org]
MANUF = {"steel": gm((5.28, 6.79)), "aluminium": gm((3.89, 5.17)), "titanium": gm((6.24, 7.26)), "nickel": gm((5.28, 6.79))}
FAMILY_RULE_FAIL = {"aluminium", "magnesium", "polymer", "composite", "core"}
AM_WORDS = ("am ", "am l-pbf", "l-pbf", "powder", "casting", "cast")


def candidates(with_pool: bool = False) -> list[dict]:
    """The organisers' list only (the task). ``with_pool`` adds our own 31-material pool to show the gate scales."""
    out = []
    for key, m in ORG.items():
        fam = {"S275N": "steel", "Al2618T6": "aluminium", "Ti811SA": "titanium"}[key]
        out.append(dict(name=m["name"], src="organiser Granta report [D-org]", family=fam, rho=gm(m["rho"]),
                        E=gm(m["E"]), Fy=m["Fy"][0], Tmax_hi=m["Tmax"][1], Tmax=m["Tmax"], K1c=m["K1c"][0],
                        process_ok=True, process_note="passed Granta stage 2 (AM or casting) [D-org]",
                        co2_mat=gm(m["co2_virgin"]), manuf=gm(m["co2_powder"]), price=gm(m["price"]),
                        reference=(key == "S275N")))
    # the other names printed in the organisers' report p.1 (no values given there): data in named_materials.json
    # (sources per value inside). Missing values are taken OPTIMISTICALLY (CO2 0, process unknown = not eliminated,
    # missing yield = best value of its family) so a lower bound stays a lower bound and an elimination is safe.
    named = json.loads((HERE / "named_materials.json").read_text(encoding="utf-8"))
    fy_fill = {"Carbon steel, AISI 1010, annealed": 284.4}     # [Y] <= 1015 annealed (named_materials notes)
    k1c_hot = {"Aluminum, 8009, rapid solidification": (9.5, 316)}  # TL at 316 °C, NASA report abstract [D-ag]
    for m in named:
        tm = m.get("Tmax")
        out.append(dict(name=m["name"], src="organiser report p.1 name; values analysis/named_materials.json [D/S/Y]",
                        family=m["family"], rho=m["rho"], E=m["E"], Fy=m["Fy"] or fy_fill.get(m["name"]),
                        Tmax_hi=(tm[1] if tm else None), Tmax=tm, K1c=m.get("K1c"), K1c_hot=k1c_hot.get(m["name"]),
                        process_ok=(True if m.get("process_ok") is None else m["process_ok"]),
                        process_note=("unknown -> not eliminated; " if m.get("process_ok") is None else "") + str(m.get("process_note", "")),
                        co2_mat=m.get("co2_virgin"), manuf=MANUF.get(m["family"]), price=m.get("price"), reference=False))
    if not with_pool:
        return out
    pool = json.loads((HERE.parents[4] / "src/aerokit/data/materials/materials_pool.json").read_text(encoding="utf-8"))
    for name, v in pool["materials"].items():
        p = v["properties"]
        g = lambda k: p[k]["value"] if k in p else None   # noqa: E731
        routes = " ".join(v.get("routes", [])).lower() + " "
        out.append(dict(name=name, src="our pool src/aerokit/data/materials/materials_pool.json [D/S]",
                        family=v["family"], rho=g("rho"), E=g("E"), Fy=g("Fty"), Tmax_hi=g("Tmax"), Tmax=g("Tmax"),
                        K1c=None, process_ok=any(w in routes for w in AM_WORDS),
                        process_note="routes: " + "; ".join(v.get("routes", [])), co2_mat=g("co2"),
                        manuf=MANUF.get(v["family"]), price=g("price"), reference=False))
    return out


def life_co2(mass: float, c: dict) -> float:
    return mass * ((c["co2_mat"] or 0.0) + (c["manuf"] or 0.0) + TR_PER_KG + USE_PER_KG + 7.45 / 152)


def screen(with_pool: bool = False, ref: tuple[str, float] | None = None) -> list[dict]:
    """``ref`` = (label, life CO2 in kg) of a design that EXISTS and passes (e.g. the chosen topology layout); then
    G5 eliminates every material whose best possible CO2 is above it. Without it the unchanged-shape design is used."""
    rows = []
    for c in candidates(with_pool):
        r = dict(c, gate="pass", reason="")
        if c["reference"]:
            r.update(gate="G0", reason="reference material to be replaced (card)")
        elif c["Tmax_hi"] is not None and c["Tmax_hi"] <= T_REQ:
            r.update(gate="G1", reason=f"max service temperature {c['Tmax']} °C, card needs > {T_REQ:g} °C")
        elif c["Tmax_hi"] is None and c["family"] in FAMILY_RULE_FAIL:
            r.update(gate="G1", reason=f"{c['family']}: no Tmax in data, family rule [Y] (< 300 °C)")
        elif not c["process_ok"]:
            r.update(gate="G2", reason="no casting / AM / powder route in its data (" + c["process_note"][8:60] + "...)")
        elif c["K1c"] is not None and c["K1c"] < 10:
            r.update(gate="G3", reason=f"K1c {c['K1c']} < 10")
        elif c.get("K1c_hot") and c["K1c_hot"][0] < 10:
            r.update(gate="G3", reason=f"K1c {c['K1c_hot'][0]} MPa m^0.5 at {c['K1c_hot'][1]} °C (TL) < 10 at working temperature")
        elif None in (c["rho"], c["E"], c["Fy"]):
            r.update(gate="data", reason="rho, E or Fy missing - cannot bound")
        if c["rho"] and c["E"] and c["Fy"]:
            # RIGOROUS lower bound = stiffness + non-design minimum only: the topology run shows max |u| grows FASTER
            # than 1/f (x2.87 at 35 %, x4.90 at 25 %, vs 2.86 / 4.0), so u0/f underestimates u -> f_u is a true bound.
            # Strength is NOT bounded this way: vM grows SLOWER than 1/f (x1.86 at 35 %, x3.48 at 25 %) because the
            # optimiser removes the least-stressed material first -> f_s is reported as an estimate only [K, 5 Nov 12:45].
            f_s, f_u = FOS * SIG0 / c["Fy"], U0 * E0 / (c["E"] * U_LIM)
            f = max(f_u, F_MIN)
            r.update(f_strength_estimate=f_s, f_stiffness=f_u, f_bound=f, governs=("stiffness" if f == f_u else "min gauge"),
                     strength_estimate_f=f_s, m_strength_estimate=V0 * c["rho"] * max(f_s, f),
                     m_full=V0 * c["rho"], m_min=V0 * c["rho"] * f, co2_min=life_co2(V0 * c["rho"] * f, c),
                     guaranteed=(f_s <= 1 and f_u <= 1), co2_guaranteed=life_co2(V0 * c["rho"], c),
                     cost_min=(V0 * c["rho"] * f * c["price"]) if c["price"] else None)
        rows.append(r)
    alive = [r for r in rows if r["gate"] == "pass"]
    best_guar = min((r for r in alive if r.get("guaranteed")), key=lambda r: r["co2_guaranteed"], default=None)
    if ref is None and best_guar is not None:
        ref = (f"{best_guar['name']} unchanged shape", best_guar["co2_guaranteed"])
    for r in rows:
        if r["gate"] in ("pass", "G0") and ref is not None and r.get("co2_min") and r["co2_min"] > ref[1] \
                and not ref[0].startswith(r["name"]):
            tag = "G5" if r["gate"] == "pass" else "G0+G5"
            r.update(gate=tag, reason=(r["reason"] + "; " if r["reason"] else "") +
                     f"dominated: best possible {r['co2_min']/1e3:.1f} t CO2 > {ref[0]} {ref[1]/1e3:.1f} t")
    return rows


def write(rows: list[dict]) -> None:
    (HERE / "screening.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    order = {"pass": 0, "G5": 1, "G0": 2, "G0+G5": 2, "G1": 3, "G2": 4, "G3": 5, "data": 6}
    rows = sorted(rows, key=lambda r: (order.get(r["gate"], 9), r.get("co2_min") or 1e99))
    n = {k: sum(r["gate"] == k for r in rows) for k in order}
    s = ["# Material screening gate — which materials go to the topology evaluation", "",
         f"{len(rows)} materials in, {n['pass']} survive. Command: `python -I analysis/screening.py` (seconds). "
         "Baseline FEA: vM 57.9 MPa outside the hole zones, 0.2047 mm at E = 182.7 GPa (runs/baseline_fixed_bores). "
         "Bounds are screening estimates [Y], not designs.", "",
         "| Gate | Material | Source | Lower-bound mass (kg) | Governs | Life CO₂ lower bound (t) | Reason |",
         "|---|---|---|---:|---|---:|---|"]
    for r in rows:
        mm = f"{r['m_min']:.1f}" if r.get("m_min") else "–"
        cc = f"{r['co2_min']/1e3:.1f}" if r.get("co2_min") else "–"
        s.append(f"| {r['gate']} | {r['name']} | {'org (values)' if r['src'].startswith('organiser Granta') else 'org (name only)' if r['src'].startswith('organiser report') else 'pool'} | {mm} | {r.get('governs','–')} | {cc} | {r['reason'] or 'survives'} |")
    (HERE / "screening.md").write_text("\n".join(s) + "\n", encoding="utf-8")
    print("\n".join(s))


if __name__ == "__main__":
    fc = HERE / "final_choice.json"      # once a design exists and passes, it becomes the dominance reference
    ref = None
    if fc.exists() and "--no-ref" not in sys.argv:
        f = json.loads(fc.read_text(encoding="utf-8"))
        ref = (f"Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed {f['layout']} (T10-verified)", f["life_co2_new_t"] * 1e3)
    write(screen(with_pool="--with-pool" in sys.argv, ref=ref))
