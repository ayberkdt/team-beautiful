"""Risk register for VESPER (likelihood L and consequence C on 1–5 scales, before and after mitigation).

Scores are our judgement [Y]; each row names the computed or sourced evidence behind it so a reviewer can check the
reasoning. Risk score = L × C; ≥ 15 red, 8–14 amber, ≤ 7 green.
"""
from __future__ import annotations

__all__ = ["RISKS", "score", "colour_band"]

RISKS: tuple[dict, ...] = (
    {"id": "R1", "risk": "Mid-air deployment fails (unfold, spin-up, release)", "L": 3, "C": 5, "L2": 2, "C2": 5,
     "evidence": "NASA Ames 2026: folding/deploying from the aeroshell is the biggest challenge (above-cloud aircraft); only 2-4 fold aircraft "
                 "demonstrated [D-ag]; pre-spun release loses 26 m vs 559 m unspun [K]",
     "mitigation": "spin up while hanging on a bridle (Dragonfly practice), spring hinges with latches, "
                   "balloon-drop tests on Earth at 1-2 km (ρ match 54-55 km, Izraelevitz 2025)"},
    {"id": "R2", "risk": "Energy: night falls before mission goals are met", "L": 4, "C": 3, "L2": 3, "C2": 3,
     "evidence": "loiter 1.34 kW vs 1.04 kWh battery; solar sustains loiter only for cos z > 0.60 → ~49 h per "
                 "air-mass day [K]", "mitigation": "release at the morning hour angle where the array first covers loiter; science prioritised early; sunset dive as "
                 "planned end; hybrid He cell as mentor-approved alternative"},
    {"id": "R3", "risk": "Acid degrades blades, cells, seals", "L": 3, "C": 4, "L2": 2, "C2": 3,
     "evidence": "75-98 wt% H2SO4 [D-ag]; FEP 0 % weight gain at 120 °C [D-ag]; CFRP in conc. acid: no data [A]",
     "mitigation": "FEP/PFA on every wetted surface, Parylene on cells (−5 % power), sealed motor cans; "
                   "acid-chamber qualification of wrapped CFRP"},
    {"id": "R4", "risk": "Battery overheats in dives / cannot charge", "L": 3, "C": 3, "L2": 2, "C2": 3,
     "evidence": "interior > 60 °C for any dive to 48 km; 51 km dives peak ~57 °C [K]",
     "mitigation": "variable-conductance heat pipe (diode), dive abort at 50 °C, PCM heat sink option"},
    {"id": "R5", "risk": "Downdraft pushes vehicle 2-3 km down", "L": 4, "C": 2, "L2": 4, "C2": 1,
     "evidence": "VEGA-2 downdraft -2..-3.3 m/s over ~2 h pushed the balloon ~2.9 km down [D-ag]; holding costs W·w/η ≈ 1.4 kW "
                 "at 3 m/s [K]", "mitigation": "ride it (altitude band 51-58 km), climb back after (~0.37 kWh)"},
    {"id": "R6", "risk": "Large slow rotors: poor control bandwidth, flap dynamics", "L": 3, "C": 4, "L2": 2, "C2": 3,
     "evidence": "rpm-control response ~0.3-1 s for +20 % thrust: fine for slow vertical gusts, too slow for attitude [K]; MSH found a large coaxial hard to control [D-ag]",
     "mitigation": "per-rotor collective actuators (fast thrust), stiff blades, control-law tests in simulator"},
    {"id": "R7", "risk": "Communications blackout between relay passes", "L": 2, "C": 2, "L2": 1, "C2": 2,
     "evidence": "1000 km relay orbit: 13 min passes, ~330 Mbit/pass [K]; above 53 km path absorption ~0 [D-ag]",
     "mitigation": "onboard storage and autonomy; 2 relay passes per orbit geometry; direct-to-Earth beacon"},
    {"id": "R8", "risk": "Navigation drift (no GNSS, no magnetic field)", "L": 3, "C": 2, "L2": 2, "C2": 2,
     "evidence": "baro altitude ±0.2 km from probe spread [K]; ground position error grows ~5 m/s × t [K]",
     "mitigation": "navigate in the air-mass frame; orbiter Doppler/range fixes each pass"},
    {"id": "R9", "risk": "Entry loads on folded structure", "L": 2, "C": 4, "L2": 1, "C2": 4,
     "evidence": "β 25 kg/m² aeroshell at −9.5°: 56 g peak [K] (PV large probe 280 g [D-ag]); shallow-entry peak g "
                 "is model-sensitive: our 29 g vs 48 g published for a rigid β 208 case at −8.5° (Venkatapathy 2016 "
                 "via agent), not explained by the upper atmosphere (Venus-GRAM profile: < 3 % change) → factor ~1.7 [K]",
     "mitigation": "shallow entry corridor −8…−11°, folded arms locked against body, qualification to 100 g; "
                   "obtain the published case's interface altitude / lift assumptions"},
    {"id": "R10", "risk": "Atmosphere differs from model (density, winds)", "L": 3, "C": 2, "L2": 2, "C2": 2,
     "evidence": "probe spread ±2 % ρ at 55 km, VIRA at dense edge; wind 50-90 m/s band [K/D-ag]",
     "mitigation": "size on 'thin' case; air-mass-frame operations make wind speed irrelevant to survival"},
)


def score(r: dict, after: bool = False) -> int:
    return (r["L2"] * r["C2"]) if after else (r["L"] * r["C"])


def colour_band(s: int) -> str:
    return "red" if s >= 15 else ("amber" if s >= 8 else "green")
