"""Ashby performance indices and rankings (aerokit.materials.selection)."""
import math

from aerokit.materials import selection as S
from aerokit.materials.library import MATERIALS
from aerokit.verification import check, check_true, expect_error

SRC = "UIUC ME598 lecture 4 (after Ashby), pp. 16, 22, 26; read 2026-11-01"
A = {"E": 70e9, "Fty": 300e6, "rho": 2700.0}
B = {"E": 110e9, "Fty": 830e6, "rho": 4430.0}


def _mass(case, rec):
    """Explicit mass of the part for unit load, length and limit, from the governing formula of each case."""
    F, L, delta, M_bend, stiff = 1e3, 1.0, 1e-3, 1e3, 1e5
    E, s, rho = rec["E"], rec["Fty"], rec["rho"]
    if case == "tie_stiff":
        return F * L ** 2 * rho / (delta * E)
    if case == "tie_strong":
        return L * F * rho / s
    if case in ("beam_stiff", "column_buckling"):   # square section side a: I = a⁴/12
        a = (12 * stiff * L ** 3 / (3 * E)) ** 0.25 if case == "beam_stiff" else (12 * F * L ** 2 / (math.pi ** 2 * E)) ** 0.25
        return rho * a * a * L
    if case == "beam_strong":                       # Z = a³/6
        a = (6 * M_bend / s) ** (1 / 3)
        return rho * a * a * L
    if case == "panel_stiff":                       # D = E t³/12 per unit width
        t = (12 * stiff / E) ** (1 / 3)
        return rho * t * L * L
    if case == "panel_strong":                      # σ = 6 M / t² per unit width
        t = (6 * M_bend / s) ** 0.5
        return rho * t * L * L
    raise KeyError(case)


def test_index_matches_explicit_mass_ratio():
    for case in S.CASES:
        ratio = _mass(case, B) / _mass(case, A)
        check(f"{case}: mass ratio B/A = index ratio A/B", ratio,
              S.performance_index(A, case) / S.performance_index(B, case), rtol=1e-12,
              source=SRC if case in ("tie_stiff", "tie_strong", "beam_strong") else "")


def test_rank_catalogue():
    r = S.rank("tie_strong")
    check_true("best has relative mass 1", r[0].relative_mass == 1.0)
    check_true("sorted by mass", all(a.relative_mass <= b.relative_mass for a, b in zip(r, r[1:])))
    check_true("composite plies are skipped (no 'Fty')", all("E1" not in MATERIALS[x.name] for x in r))
    check("7075-T6 vs 6061-T6 strong tie = (276/2700)/(503/2810)",
          next(x for x in r if x.name == "6061-T6").relative_mass /
          next(x for x in r if x.name == "7075-T6").relative_mass,
          (503e6 / 2810) / (276e6 / 2700), rtol=1e-12)


def test_co2_weighting_can_flip_the_choice():
    pool = {"A": A, "B": B}
    check_true("lightest stiff panel: A", S.rank("panel_stiff", pool)[0].name == "A")
    flip = S.rank("tie_strong", pool, co2_per_kg={"A": 1.0, "B": 100.0})
    check_true("B lightest strong tie but A wins on CO₂ when B is 100× dirtier",
               S.rank("tie_strong", pool)[0].name == "B" and flip[0].name == "A")


def test_errors():
    expect_error("unknown case", S.performance_index, A, "shell", error=KeyError)
    expect_error("ply record has no E", S.performance_index, MATERIALS["IM7-8552"], "tie_stiff", error=KeyError)
    expect_error("missing CO₂ factor", S.rank, "tie_stiff", {"A": A, "B": B}, co2_per_kg={"A": 1.0}, error=KeyError)
    expect_error("zero density", S.performance_index, {"E": 1.0, "rho": 0.0}, "tie_stiff", error=ValueError)


def test_plate_and_sandwich_for_stiffness():
    from aerokit.materials.selection import plate_for_stiffness, sandwich_for_stiffness
    D = 73.1e9 * 0.002 ** 3 / 12                      # 2 mm aluminium strip, nu = 0
    check("plate thickness back from D", plate_for_stiffness(D, 73.1e9, 2780)["thickness_m"], 0.002, rtol=1e-12)
    s = sandwich_for_stiffness(D, 22.0e9, 1830, 0.25e-3, 48)
    d = s["core_m"] + 0.25e-3
    check("thin-face sandwich: E_f t d^2 / 2 = D", 22.0e9 * 0.25e-3 * d ** 2 / 2, D, rtol=1e-12)
    check("areal mass = 2 faces + core", s["areal_mass_kg_m2"], 2 * 0.25e-3 * 1830 + s["core_m"] * 48, rtol=1e-12)
    expect_error("faces already too stiff", sandwich_for_stiffness, 1e-6, 70e9, 2700, 1e-3, 48, error=ValueError)
