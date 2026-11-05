"""Plate-fin heat sink: thermal resistance and mass for forced or natural convection (scenario S6, docs/13).

A base plate ``W × L × t_b`` carries ``n`` straight rectangular fins of height ``H`` and thickness ``t`` running
along ``L``. Heat enters the base uniformly; air at ``T_amb`` flows along ``L`` (forced) or rises along ``L``
(natural, base vertical).

Model (each piece read on 2026-11-02, see ``SOURCES``):

* fin: ``m² = h P / (k A_c)``, heat rate with an adiabatic tip ``√(h P k A_c) θ_b tanh(mL)`` (Wikipedia, *Fin
  (extended surface)*), hence efficiency ``η = tanh(mH)/(mH)`` — the tip is treated as adiabatic, which is
  conservative by the tip area;
* forced: laminar flat plate ``Nu_L = 0.664 Re_L^½ Pr^⅓`` (Pr > 0.6) on every wetted face, with ``L`` the flow
  length; the channel is assumed wide enough for separate boundary layers, checked against the Blasius
  thickness ``δ99 ≈ 5.29 √(ν L / U)`` — a gap narrower than ``2 δ99`` is flagged (developing channel flow, the
  flat-plate ``h`` is then optimistic);
* natural: Churchill and Chu, vertical plate, ``Nu_L = 0.68 + 0.67 Ra^¼ / (1 + (0.492/Pr)^(9/16))^(4/9)`` for
  ``10⁻¹ < Ra < 10⁹``, ``β = 1/T`` (ideal gas), solved for the base temperature by fixed-point iteration; valid
  only while the fins act as separate plates: Elenbaas puts the optimum spacing where the channel Rayleigh number
  ``Ra_b · b/L`` is about 50 (Simons 2002), i.e. ``b_opt = (50 L ν α / (g β ΔT))^¼`` — a narrower gap is flagged;
* resistance ``R = t_b/(k W L) + 1 / (h (A_base,exposed + η A_fins))``; radiation is not included.

Air at 25 °C: k 0.02624 W/m K, ν 15.52e-6 m²/s, Pr 0.707 (Engineering ToolBox tables).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["AIR_25C", "SOURCES", "HeatSink", "fin_efficiency", "forced_h", "natural_h", "elenbaas_spacing",
           "evaluate", "sweep"]

AIR_25C = {"k": 0.02624, "nu": 15.52e-6, "Pr": 0.707}
"""Air at 1 atm, 25 °C."""

SOURCES = {
    "fin": "https://en.wikipedia.org/wiki/Fin_(extended_surface) (m^2 = hP/kA_c; adiabatic-tip rate)",
    "nusselt": "https://en.wikipedia.org/wiki/Nusselt_number (flat plate laminar; Churchill-Chu vertical plate)",
    "blasius": "https://en.wikipedia.org/wiki/Blasius_boundary_layer (delta99 = 5.29 sqrt(nu x / U))",
    "air": "engineeringtoolbox.com air thermal conductivity, kinematic viscosity and Prandtl tables (25 C)",
    "elenbaas": "R. E. Simons, Electronics Cooling, 1 Feb 2002 (channel Rayleigh number Ra_b b/L ~ 50 at optimum)",
}


@dataclass(frozen=True)
class HeatSink:
    W: float          # base width across the fins [m]
    L: float          # flow length (fin length) [m]
    t_b: float        # base thickness [m]
    H: float          # fin height [m]
    t: float          # fin thickness [m]
    n: int            # number of fins

    @property
    def gap(self) -> float:
        return (self.W - self.n * self.t) / (self.n - 1) if self.n > 1 else self.W - self.t

    def volume(self) -> float:
        return self.W * self.L * self.t_b + self.n * self.H * self.t * self.L


def fin_efficiency(h: float, k: float, t: float, H: float) -> float:
    """Straight rectangular fin of thickness ``t`` and height ``H``, adiabatic tip (per unit length P ≈ 2)."""
    m = math.sqrt(2.0 * h / (k * t))
    mH = m * H
    return 1.0 if mH < 1e-12 else math.tanh(mH) / mH


def forced_h(U: float, L: float, air: dict[str, float] = AIR_25C) -> float:
    """Mean laminar flat-plate h over length ``L`` [W/m² K]."""
    Re = U * L / air["nu"]
    return 0.664 * Re ** 0.5 * air["Pr"] ** (1 / 3) * air["k"] / L


def natural_h(dT: float, L: float, T_amb_C: float = 25.0, air: dict[str, float] = AIR_25C) -> float:
    """Mean h of a vertical plate of height ``L`` at ``dT`` above ambient (Churchill-Chu, laminar form)."""
    T_film = T_amb_C + 273.15 + dT / 2
    alpha = air["nu"] / air["Pr"]
    Ra = 9.81 * (1 / T_film) * dT * L ** 3 / (air["nu"] * alpha)
    if not 1e-1 < Ra < 1e9:
        raise ValueError(f"Rayleigh number {Ra:.3g} outside the laminar Churchill-Chu range 1e-1..1e9")
    Nu = 0.68 + 0.67 * Ra ** 0.25 / (1 + (0.492 / air["Pr"]) ** (9 / 16)) ** (4 / 9)
    return Nu * air["k"] / L


def elenbaas_spacing(dT: float, L: float, T_amb_C: float = 25.0, air: dict[str, float] = AIR_25C) -> float:
    """Plate spacing where the channel Rayleigh number ``Ra_b · b/L`` equals 50 [m]."""
    T_film = T_amb_C + 273.15 + dT / 2
    alpha = air["nu"] / air["Pr"]
    return float((50.0 * L * air["nu"] * alpha / (9.81 * (1 / T_film) * dT)) ** 0.25)


def evaluate(hs: HeatSink, k: float, rho: float, Q: float, U: float | None = None, T_amb_C: float = 25.0,
             air: dict[str, float] = AIR_25C) -> dict[str, float | bool]:
    """Thermal resistance, base temperature rise, mass and checks for heat input ``Q`` [W].

    ``U`` given: forced convection at speed ``U`` [m/s]; ``U`` None: natural convection, base vertical.
    """
    if hs.gap <= 0:
        raise ValueError("fins do not fit across the base")
    A_fins = hs.n * 2 * hs.H * hs.L
    A_base = (hs.W - hs.n * hs.t) * hs.L
    R_base = hs.t_b / (k * hs.W * hs.L)
    if U is not None:
        h = forced_h(U, hs.L, air)
        eta = fin_efficiency(h, k, hs.t, hs.H)
        R = R_base + 1 / (h * (A_base + eta * A_fins))
        dT = Q * R
        delta = 5.29 * math.sqrt(air["nu"] * hs.L / U)
    else:
        dT = 30.0
        for _ in range(200):
            h = natural_h(dT, hs.L, T_amb_C, air)
            eta = fin_efficiency(h, k, hs.t, hs.H)
            R = R_base + 1 / (h * (A_base + eta * A_fins))
            new = Q * R
            if abs(new - dT) < 1e-6:
                break
            dT = 0.5 * (dT + new)
        dT = Q * R
        delta = elenbaas_spacing(dT, hs.L, T_amb_C, air) / 2      # half the optimum spacing, so gap_ok: gap >= b_opt
    return {"h_W_m2K": h, "fin_efficiency": eta, "R_K_W": R, "dT_K": dT, "mass_kg": rho * hs.volume(),
            "gap_m": hs.gap, "boundary_layer_m": delta, "gap_ok": bool(hs.gap >= 2 * delta)}


def sweep(W: float, L: float, t_b: float, H: float, k: float, rho: float, Q: float, U: float | None,
          dT_max: float, t_options: tuple[float, ...] = (0.5e-3, 1e-3, 1.5e-3, 2e-3),
          n_max: int = 60, require_gap_ok: bool = True) -> list[dict]:
    """Every (fin count, fin thickness) that keeps the base rise below ``dT_max``, lightest first.

    With ``require_gap_ok`` (default) designs whose gap breaks the model's separate-plate assumption are left out.
    """
    out = []
    for t in t_options:
        for n in range(2, n_max + 1):
            hs = HeatSink(W, L, t_b, H, t, n)
            if hs.gap <= 0.5e-3:
                break
            r = evaluate(hs, k, rho, Q, U)
            if r["dT_K"] <= dT_max and (r["gap_ok"] or not require_gap_ok):
                out.append({"n": n, "t_m": t, **r})
    return sorted(out, key=lambda r: r["mass_kg"])
