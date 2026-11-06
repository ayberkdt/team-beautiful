"""Card requirement -> organiser property rows -> the three materials. Values are copied BY PROGRAM from the verified
record analysis/organiser_table_full.json (no hand transcription). Verdicts only where the card gives a number.
python -I analysis/conditions_matrix.py -> analysis/conditions_matrix.md"""
import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
T = {r["property"]: r for r in json.loads((HERE / "organiser_table_full.json").read_text(encoding="utf-8"))["rows"]}
COLS = [("S275N", "S275N (reference)"), ("Al2618T6", "Al 2618-T6"), ("Ti811SA", "Ti-8Al-1Mo-1V SA")]


def lo_hi(s):
    n = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s or "")]
    return (n[0], n[-1]) if n else (None, None)


def row(prop, note=""):
    r = T[prop]
    return f"| {prop} | " + " | ".join(r[c] or "–" for c, _ in COLS) + f" | p.{r['page']} {note} |"


def verdict(prop, test, text):
    cells = []
    for c, _ in COLS:
        lo, hi = lo_hi(T[prop][c])
        cells.append(("✔ " if test(lo, hi) else "✘ ") + text(lo, hi))
    return f"| **verdict** | " + " | ".join(cells) + " | |"


H = "| Property (organisers' wording) | " + " | ".join(n for _, n in COLS) + " | Source |\n|---|---|---|---|---|"
s = ["# Card requirements vs the organisers' data — S275N, Al 2618-T6, Ti-8Al-1Mo-1V", "",
     "Card: `Ideathon_Challenge_Ansys_2026.docx` (re-read from Files.zip). Values: the organisers' Material selection "
     "report p.7–13, copied by `conditions_matrix.py` from the verified record `organiser_table_full.json` "
     "(two extraction methods identical on 160 value rows; third engine found 447/450 cells, the 3 others checked on the "
     "page image). **All organiser values are at 23 °C** (report p.14 'Functional parameters: Temperature 23'); rows "
     "marked # are 'with temperature' attributes evaluated at that 23 °C, not at 300 °C.", ""]

s += ["## 0. Condition (heat treatment) of each record", "", H, row("Condition"), row("Materials Data for Simulation name"),
      row("EN name"), row("UNS number"), "",
      "What the condition means for > 300 °C service: S275N normalized — no ageing treatment to lose. 2618 **T6 = solution "
      "treated and artificially aged**: strength comes from precipitates formed at the ageing temperature (≈ 195 °C for "
      "2618A, BAM data set [S]); service above it over-ages the alloy (MIL-HDBK-5J: 2618-T61 keeps 60 % of Ftu after "
      "1000 h at 204 °C [D-ag]). Ti-8-1-1 **single annealed = 1450 °F (788 °C) 8 h, furnace cool** (MIL-HDBK-5J p.5-27 "
      "[D]) — a stable mill condition far above 300 °C; MIL notes duplex anneal gives the higher fracture toughness [D].", ""]

s += ["## 1. 'Working temperature >300°C'", "", H, row("Maximum service temperature (°C)"),
      verdict("Maximum service temperature (°C)", lambda lo, hi: hi > 300, lambda lo, hi: f"top of range {hi:g} °C {'>' if hi > 300 else '≤'} 300"),
      row("Oxidation at 500C"), row("Melting point (°C)"), row("Young's modulus with temperature (GPa) #", "(at 23 °C)"),
      row("Yield strength with temperature (MPa) #", "(at 23 °C)"), row("Thermal expansion coefficient (µstrain/°C)"),
      row("Thermal conductivity (W/m.°C)"), row("Thermal shock resistance (°C)"), "",
      "Note: the organisers' Granta filter was '≥ 300' with 'pass when any part of record within selection' (report p.4) — "
      "that is why 2618 (250–300) passed their filter while failing the card's strict '> 300'.", ""]

s += ["## 2. 'Ability to be casted or 3D printed'", "", H, row("Metal casting"),
      row("Metal powder forming, climate change (CO2-eq) (kg/kg)", "(process data exist for all three)"),
      row("Metal casting, climate change (CO2-eq) (kg/kg)"), row("Machining speed (m/min)"), row("Weldability"),
      row("Weldability Notes _"), "",
      "All three passed the organisers' stage 2 (ProcessUniverse: Additive manufacturing OR Casting, report p.5). The "
      "report has no 'additive manufacturing suitability' row; 'Metal casting' is the only process rating given.", ""]

s += ["## 3. 'Minimum fracture toughness of 10MPa.m^1/2'", "", H, row("Fracture toughness (MPa.m^0.5)"),
      verdict("Fracture toughness (MPa.m^0.5)", lambda lo, hi: lo >= 10, lambda lo, hi: f"low end {lo:g} {'≥' if lo >= 10 else '<'} 10"),
      row("Toughness (G) (kJ/m^2)"), row("Elongation (% strain)"), ""]

s += ["## 4. Structural: 'Factor of Safety of 1.5', 'Max displacement below 1/400 of largest dimension'", "", H,
      row("Young's modulus (GPa)"), row("Yield strength (elastic limit) (MPa)"), row("Tensile strength (MPa)"),
      row("Compressive strength (MPa)"), row("Shear modulus (GPa)"), row("Poisson's ratio"),
      row("Specific stiffness (MN.m/kg)"), row("Specific strength (kN.m/kg)"), row("Fatigue strength at 10^7 cycles (MPa)"), "",
      "Allowable von Mises with FoS 1.5 on the LOW end of yield: " + ", ".join(
          f"{n} {lo_hi(T['Yield strength (elastic limit) (MPa)'][c])[0] / 1.5:.0f} MPa" for c, n in COLS) + " (23 °C).", ""]

s += ["## 5. Objectives: weight, cost, CO₂ over the full life", "", H, row("Density (kg/m^3)"), row("Price (USD/kg)"),
      row("Price per unit volume (USD/m^3)"), row("Mass per unit of stiffness"), row("Cost per unit of stiffness"),
      row("Climate change (CO2-eq) (virgin grade production) (kg/kg)", "(card: use virgin)"),
      row("Metal powder forming, climate change (CO2-eq) (kg/kg)", "(card: powder forming)"),
      row("Climate change (CO2-eq), recycling (kg/kg)"), row("Recycle"), row("Functional recycle"),
      row("Recycle fraction in current supply (%)"), row("Embodied energy (virgin grade production) (MJ/kg)"), ""]

s += ["## 6. Not in the card but relevant for an engine-cowling bracket", "", H, row("Stress corrosion cracking"),
      row("Stress corrosion cracking Notes _"), row("Water (salt)"), row("Galvanic potential (V)"),
      row("Galling resistance (adhesive wear)"), row("Flammability"), row("Contains >5wt% critical elements?"),
      row("Sourcing and geopolitical risk level"), row("Price volatility risk level"), row("Conflict material risk level"), ""]
(HERE / "conditions_matrix.md").write_text("\n".join(s) + "\n", encoding="utf-8")
print("\n".join(s))
