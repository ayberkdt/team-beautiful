"""Modal and thermal checks of aerokit.design.card_physics against closed forms, and the card checks built on them."""
import json
from pathlib import Path

import numpy as np

from aerokit.design import card as C
from aerokit.design import card_physics as cp
from aerokit.optimization import topology as tp
from aerokit.verification import check, check_true

ROOT = Path(__file__).resolve().parents[1]


def _cantilever(nx, ny):
    g = tp.Grid2D(nx, ny, 0.3)
    return g, [g.dof(0, iy, d) for iy in range(ny + 1) for d in (0, 1)]


def test_mass_matrix_total_mass():
    # each direction of the consistent mass must sum to the element mass (1 for unit density, area, thickness)
    check("Q4 consistent mass sums to the element mass", MASS_SUM := cp.MASS_Q4[0::2, 0::2].sum(), 1.0, rtol=1e-12)
    check_true("mass matrix symmetric", np.allclose(cp.MASS_Q4, cp.MASS_Q4.T) and MASS_SUM > 0)


def test_cantilever_frequency_against_euler_bernoulli():
    # L = 0.2 m, H = 0.02 m, t = 0.01 m, aluminium; f1 = (1.8751^2 / 2 pi) sqrt(E I / (rho A L^4))
    E, rho, t, L, H = 70e9, 2700.0, 0.01, 0.2, 0.02
    g, fixed = _cantilever(100, 10)
    f1 = cp.modal(g, np.ones(g.nel), fixed, E, rho, t, L / 100, n=2)["frequencies_Hz"][0]
    I_, A = t * H ** 3 / 12, t * H
    f_eb = 1.875104 ** 2 / (2 * np.pi) * np.sqrt(E * I_ / (rho * A * L ** 4))
    check("cantilever f1 within 2 % of Euler-Bernoulli", f1, f_eb, rtol=0.02)


def test_tip_mass_frequency():
    # tip mass m: f = sqrt(k / (m + 0.2235 m_beam)) / 2 pi with k = 3 E I / L^3 (Rayleigh, Blevins)
    E, rho, t, L, H, m = 70e9, 2700.0, 0.01, 0.2, 0.02, 0.5
    g, fixed = _cantilever(100, 10)
    f1 = cp.modal(g, np.ones(g.nel), fixed, E, rho, t, L / 100, {g.node(100, 5): m}, n=1)["frequencies_Hz"][0]
    I_, A = t * H ** 3 / 12, t * H
    f = np.sqrt(3 * E * I_ / L ** 3 / (m + 0.2235 * rho * A * L)) / (2 * np.pi)
    check("tip-mass cantilever f1 within 2 % of the Rayleigh formula", f1, f, rtol=0.02)


def test_void_elements_carry_no_modes():
    # a cantilever with its upper half void must give the frequency of the lower half alone
    E, rho, t = 70e9, 2700.0, 0.01
    g, fixed = _cantilever(60, 12)
    half = np.zeros(g.shape)
    half[6:, :] = 1.0                          # rows count from the top: lower half solid
    g2, fixed2 = _cantilever(60, 6)
    f_half = cp.modal(g, g.vector(half), fixed, E, rho, t, 0.002, n=1)["frequencies_Hz"][0]
    f_ref = cp.modal(g2, np.ones(g2.nel), fixed2, E, rho, t, 0.002, n=1)["frequencies_Hz"][0]
    check("void half adds no spurious mode", f_half, f_ref, rtol=1e-9)


def test_thermal_clamped_strip_and_free_body():
    g = tp.Grid2D(20, 4, 0.3)
    clamped = [g.dof(0, iy, 0) for iy in range(5)] + [g.dof(20, iy, 0) for iy in range(5)] + [g.dof(0, 0, 1)]
    s = cp.thermal_unit(g, np.ones(g.nel), clamped)
    mid = np.abs(g.element_center()[:, 0] - 10) < 2
    check("ends held in x: sigma_x = -E alpha dT", float(s[mid, 0].mean()), -1.0, rtol=1e-9)
    check("ends held in x: sigma_y = 0", float(np.abs(s[mid, 1]).max()), 0.0, atol=1e-9)
    free = [g.dof(0, 0, 0), g.dof(0, 0, 1), g.dof(20, 0, 1)]
    check("statically determinate support: no thermal stress",
          float(cp.von_mises(cp.thermal_unit(g, np.ones(g.nel), free)).max()), 0.0, atol=1e-9)


def _bridge_card(**extra):
    raw = json.loads((ROOT / "prev_guess" / "01_Ansys" / "cards" / "template_cantilever.json").read_text(encoding="utf-8"))
    raw["geometry"] = {"type": "bridge", "length_m": 0.2, "height_m": 0.04, "thickness_m": 0.01, "elements": 40}
    raw["volumes"] = [0.5]
    raw.update(extra)
    return C._parse(raw, ROOT)


def test_card_checks_and_missing_data():
    card = _bridge_card(limits={"deflection_m": 1e-3, "frequency_Hz_min": 100.0}, added_mass_kg=0.2,
                        thermal={"delta_T_K": 100.0, "structure_alpha_per_K": 0.0},
                        fatigue={"amplitude_N": 500.0, "mean_N": 500.0, "cycles": 1e7})
    mat = card.candidates[0][0]
    card.material_data = {mat: {"alpha_per_K": 2.3e-5}}           # fatigue data left out on purpose
    solid = {"volume": 0.5, "density": np.ones((8, 40))}
    out = C.run(card, [solid])
    row = next(r for r in out["rows"] if r["material"] == mat)
    check_true("missing fatigue data blocks the pass", not row["passes"]
               and set(row["missing"]) == {"fatigue_strength_Pa", "Ftu_Pa"})
    check_true("frequency and thermal utilisations reported", {"frequency", "thermal"} <= set(row["utilisation"]))
    # a solid bar with both ends clamped (u and v) heated by dT: E alpha dT along the span; the ends also stop
    # the Poisson growth in y, which lifts the peak read 3 elements from the end (St Venant zone ~ one height)
    E = C._material(card, mat).get("E_Pa_at_T", C._material(card, mat)["E"])
    ratio = row["sigma_thermal_Pa"] / (E * 2.3e-5 * 100.0)
    check_true(f"bridge peak thermal stress 1.0-1.15 x E alpha dT (got {ratio:.3f})", 1.0 <= ratio <= 1.15)


def test_load_path_drops_islands_and_corner_hinges():
    g, fixed = _cantilever(10, 6)
    a = np.zeros(g.shape)
    a[2:4, 0:6] = 1.0          # arm held along the clamped edge
    a[4, 6] = 1.0              # touches the arm only at a corner: a hinge
    a[0, 8:10] = 1.0           # island
    keep = cp.load_path(g, g.vector(a), fixed)
    check("only the edge-connected arm is kept", float(keep.sum()), 12.0, atol=0.0)
    expect_mass = cp.modal(g, g.vector(a), fixed, 70e9, 2700.0, 0.01, 0.01, n=1)["structural_mass_kg"]
    check("modal mass counts the kept elements only", expect_mass, 12 * 2700.0 * 0.01 * 0.01 ** 2, rtol=1e-12)
