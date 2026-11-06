"""Deterministic check: re-extract every value we use from the organisers' selection report (word positions, not
manual reading) and diff it against analysis/organiser_materials.py. Exit 1 on any mismatch.
python -I analysis/verify_organiser_values.py "<path to Material selection report Ideathon challenge.pdf>" """
import re, sys
from pathlib import Path
import fitz
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from organiser_materials import M  # noqa: E402

ROWS = {  # our key -> exact label text at the start of the row in the report
    "rho": "Density (kg/m^3)", "E": "Young's modulus (GPa)", "Fy": "Yield strength (elastic limit)",
    "Fu": "Tensile strength (MPa)", "elong": "Elongation (% strain)", "fatigue_1e7": "Fatigue strength at 10^7 cycles",
    "K1c": "Fracture toughness", "Tmax": "Maximum service temperature", "price": "Price (USD/kg)",
    # (first-line text, n-th occurrence) where several rows start with the same words; the PDF drops the "ff"/"ffi"
    # ligatures ("sti ness", "coe cient"), so those labels are matched on the words before the ligature
    "cte": ("Thermal expansion", 0), "k": ("Thermal conductivity", 0), "co2_virgin": "Climate change (CO2-eq) (virgin",
    "co2_typical": ("Climate change (CO2-eq)", 1), "ee_virgin": "Embodied energy (virgin", "co2_powder": "Metal powder forming, climate",
    "ee_powder": ("Metal powder forming,", 1), "co2_cast": "Metal casting, climate", "co2_recycle": ("Climate change (CO2-eq),", 0),
    "mass_per_stiffness": ("Mass per unit of", 0), "cost_per_stiffness": ("Cost per unit of", 0),
    "casting": "Metal casting", "oxidation_500C": "Oxidation at 500C", "scc": "Stress corrosion cracking", "weldability": "Weldability",
    "recycle_fraction": "Recycle fraction in current",
}
KEYS = ["S275N", "Al2618T6", "Ti811SA"]
doc = fitz.open(sys.argv[1])
# column x-boundaries from the table header on p.7 (points): label | S275N | 2618 | Ti
words_all = []
for pno in range(6, 13):
    for w in doc[pno].get_text("words"):
        words_all.append((pno, *w[:5]))
def col(x0):
    return None if x0 < 188 else 0 if x0 < 277 else 1 if x0 < 365 else 2 if x0 < 455 else None
def row_values(label):
    label, nth = label if isinstance(label, tuple) else (label, None)
    first = label.split()
    hits = []
    for pno in range(6, 13):
        ws = [w for w in words_all if w[0] == pno]
        for i, w in enumerate(ws):
            if w[5] == first[0] and col(w[1]) is None and all(i + j < len(ws) and ws[i + j][5] == first[j] for j in range(len(first))):
                hits.append((pno, w[2]))
    out = []
    for pno, y in hits:
        cells = ["", "", ""]
        for w in words_all:
            if w[0] == pno and abs(w[2] - y) < 3.5 and col(w[1]) is not None:
                cells[col(w[1])] += (" " if cells[col(w[1])] else "") + w[5]
        if any(cells):
            out.append(cells)
    return [out[nth]] if nth is not None and len(out) > nth else out
def parse(s):
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", s.replace(" - ", " "))]
    return nums
bad = 0
for key, label in ROWS.items():
    cand = row_values(label)
    if not cand:
        print(f"?? {key:20s} label not found: {label!r}"); bad += 1; continue
    cells = cand[0] if key != "casting" else [c for c in cand if not any(ch.isdigit() for ch in "".join(c))][0]
    for j, mk in enumerate(KEYS):
        ours = M[mk].get(key)
        pdf = cells[j]
        if isinstance(ours, str) or ours is None and not parse(pdf):
            ok = (ours or "").lower() == pdf.lower() or (ours is None and pdf == "")
        elif isinstance(ours, (int, float)):
            ok = parse(pdf) == [float(ours)]
        else:
            ok = ours is not None and parse(pdf) == [float(v) for v in ours]
        flag = "ok " if ok else "XX "
        if not ok: bad += 1
        print(f"{flag}{key:20s} {mk:9s} pdf={pdf!r:30s} ours={ours}")
print("MISMATCHES:", bad)
sys.exit(1 if bad else 0)
