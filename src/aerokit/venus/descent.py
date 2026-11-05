"""Parachute descent, mid-air deployment of the rotorcraft and the entry-system mass budget.

**Entry-system mass** — Landis (2026, research note B_landis_venus_airplane) budgets a folded Venus aircraft as 20 %
of the entry mass, with heat-shield structure 7 % + TPS 13 %, backshell structure 12 % + TPS 8 %, parachute system
10 %, deployment mechanism 15 %, miscellaneous 15 % (fractions from Pioneer Venus and the Mars airplane) [D-ag];
:func:`entry_system` applies them to our vehicle. Shallow-entry, low-β aeroshells are lighter in TPS than Pioneer
Venus (HEEET / ADEPT envelopes in note D_venkatapathy_2017), so this is conservative.

**Parachute** — quasi-steady descent ``m dV/dt = m g − ½ ρ V² C_D S`` integrated through the probe atmosphere;
opening load ``F = C_x q S C_D`` with an opening-load factor ``C_x`` [Y]. Precedents [D-ag]: Pioneer Venus large
probe heat shield off ~67 km, 17 min on the chute, chute off 47 km; DAVINCI pilot 1.8 m DGB at Mach 0.8, main 5.8 m at
~70 km; Venera 9 three mains 180 m² at 62 km; Vega cap chute 64 km, balloon out 61 km, inflated 54 km.

**Deployment** — two options are simulated for the first seconds after release (vertical point mass):

* *pre-spun* (Dragonfly-like, note C_pensado2025: rotors spun under the main chute, release at 0.8–1 km above the
  Titan surface below 2.9 m/s): thrust starts at the hover value and is raised to ``thrust_margin × W``;
* *drop-then-spin* (Mars MAHD-like, note C_delaune2022: 3 s free fall, 12 s spin-up): no thrust for ``t_free``,
  then thrust rises linearly to ``thrust_margin × W`` over ``t_spin``.

During descent the rotor passes through the vortex-ring state when the descent rate is between ~0.5 and ~1.5 ×
the hover induced velocity ``v_h`` (helicopter practice; Leishman 2006, not read here): the vehicle pitches into
forward flight to cross that band (the code reports the time spent in it).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from aerokit import planetary as P
from aerokit.references import cite
from aerokit.venus import atmosphere as A

__all__ = ["LANDIS_FRACTIONS", "entry_system", "ParachuteResult", "parachute_descent", "opening_load",
           "TerminalResult", "terminal_descent", "DeployMC", "deployment_monte_carlo",
           "DeployResult", "deploy", "density_any"]

LANDIS_FRACTIONS = {"vehicle": 0.20, "heatshield_structure": 0.07, "heatshield_tps": 0.13,
                    "backshell_structure": 0.12, "backshell_tps": 0.08, "parachute_system": 0.10,
                    "deployment_mechanism": 0.15, "misc_comm_power_ballast": 0.15}


@cite("landis_2026_planetary_aircraft", note="entry mass fractions for a folded Venus aircraft")
def entry_system(vehicle_kg: float, contingency: float = 0.30) -> dict:
    """Entry-system mass budget [kg] scaled from the vehicle mass with Landis' fractions (+ contingency)."""
    if vehicle_kg <= 0:
        raise ValueError("vehicle mass must be > 0")
    total = vehicle_kg / LANDIS_FRACTIONS["vehicle"]
    out = {k: v * total for k, v in LANDIS_FRACTIONS.items()}
    out["total"] = total
    out["total_with_contingency"] = total * (1.0 + contingency)
    return out


def density_any(h: float) -> float:
    """Probe-mean density inside 40–64 km, the VIRA-like table elsewhere."""
    if A.Z_MIN <= h <= A.Z_MAX:
        return A.state(h).rho
    return P.venus_atmosphere(min(max(h, 0.0), 100e3)).rho


@dataclass
class ParachuteResult:
    t: np.ndarray
    h: np.ndarray
    V: np.ndarray
    duration_s: float
    V_end: float


def parachute_descent(mass_kg: float, diameter_m: float, h0: float, h1: float, V0: float,
                      drag_coefficient: float = 0.55, dt: float = 0.05) -> ParachuteResult:
    """Vertical descent under a canopy of nominal ``diameter_m`` from ``h0`` to ``h1`` [m] starting at ``V0``."""
    if min(mass_kg, diameter_m) <= 0 or h1 >= h0:
        raise ValueError("mass, diameter > 0 and h1 < h0")
    S = math.pi * diameter_m ** 2 / 4.0
    t, h, V = 0.0, h0, V0
    T, H, VV = [t], [h], [V]
    while h > h1 and t < 7200:
        g = P.venus_gravity(h)
        a = g - 0.5 * density_any(h) * V * abs(V) * drag_coefficient * S / mass_kg
        V += a * dt
        h -= V * dt
        t += dt
        T.append(t)
        H.append(h)
        VV.append(V)
    return ParachuteResult(np.array(T), np.array(H), np.array(VV), t, V)


def opening_load(diameter_m: float, V: float, h: float, drag_coefficient: float = 0.55,
                 load_factor: float = 1.5) -> float:
    """Peak opening force [N] ``C_x q S C_D`` (``load_factor`` C_x assumed)."""
    S = math.pi * diameter_m ** 2 / 4.0
    return load_factor * 0.5 * density_any(h) * V * V * S * drag_coefficient


@dataclass
class DeployResult:
    t: np.ndarray
    h: np.ndarray
    Vd: np.ndarray            # descent rate, + down
    altitude_loss_m: float
    max_descent_m_s: float
    time_in_vrs_s: float
    t_arrest_s: float


def deploy(mass_kg: float, h_release: float, V_release: float, v_h: float, thrust_margin: float = 1.6,
           mode: str = "pre-spun", t_free: float = 3.0, t_spin: float = 12.0, drag_area_m2: float = 0.45,
           thrust_ramp_s: float = 2.0, dt: float = 0.01) -> DeployResult:
    """Vertical motion after release until the descent is arrested (rate ≤ 0)."""
    if mode not in ("pre-spun", "drop-then-spin"):
        raise ValueError("mode is 'pre-spun' or 'drop-then-spin'")
    t, h, V = 0.0, h_release, V_release
    T, H, VV = [t], [h], [V]
    vrs = 0.0
    while t < 600:
        g = P.venus_gravity(h)
        W = mass_kg * g
        if mode == "pre-spun":
            thrust = W * (1.0 + (thrust_margin - 1.0) * min(t / thrust_ramp_s, 1.0))
        else:
            thrust = 0.0 if t < t_free else W * thrust_margin * min((t - t_free) / t_spin, 1.0)
        drag = 0.5 * density_any(h) * V * abs(V) * drag_area_m2
        a = (W - thrust - drag) / mass_kg
        V += a * dt
        h -= V * dt
        t += dt
        if 0.5 * v_h <= V <= 1.5 * v_h:
            vrs += dt
        T.append(t)
        H.append(h)
        VV.append(V)
        if V <= 0.0 and t > 0.1:
            break
    H_arr = np.array(H)
    return DeployResult(np.array(T), H_arr, np.array(VV), h_release - float(H_arr.min()), float(max(VV)), vrs, t)


# ---------------------------------------------------------------------------------------------------------------
# End of mission: unpowered terminal descent to the surface and how long the electronics would survive
# ---------------------------------------------------------------------------------------------------------------

def _ambient(h: float) -> tuple[float, float, float]:
    """(T [K], ρ [kg/m³], g) — probe mean inside 40–64 km, the VIRA-like table elsewhere (0–100 km)."""
    if A.Z_MIN <= h <= A.Z_MAX:
        s = A.state(h)
        return s.T, s.rho, s.g
    t = P.venus_atmosphere(min(max(h, 0.0), 100e3))
    return t.T, t.rho, t.g


@dataclass
class TerminalResult:
    t: np.ndarray
    h: np.ndarray
    V: np.ndarray
    T_ambient_C: np.ndarray
    T_interior_C: np.ndarray
    t_surface_s: float
    impact_speed: float
    t_battery_60C_s: float | None
    t_electronics_125C_s: float | None
    h_electronics_125C_m: float | None
    surface_survival_s: float | None


@cite("young_2004_rwd", note="rotary-wing decelerator concept: spinning rotors as a descent brake")
def terminal_descent(mass_kg: float, drag_area_m2: float, h0: float, Ti0_C: float, internal_W: float = 30.0,
                     dt: float = 2.0, surface_hold_s: float = 3.0 * 3600.0) -> TerminalResult:
    """Unpowered fall from ``h0`` to the surface at terminal speed ``√(2 m g / (ρ C_D A))`` (``drag_area_m2`` =
    C_D·A: windmilling rotors act as a rotary-wing decelerator; folded/broken rotors leave only the airframe), with
    the sealed vessel's interior temperature (two-node model of :mod:`aerokit.venus.thermal`, insulation only — the
    heat-pipe diode stays closed because the air is hotter than the interior). After touchdown the vessel sits in
    surface air for ``surface_hold_s`` to give the survivable time to 125 °C (AEC-Q100 grade 1)."""
    from aerokit.venus import thermal as TH

    v = TH.Vessel()
    h = h0
    T_amb, _, _ = _ambient(h)
    Ti = Ti0_C + 273.15
    Ts = T_amb
    t = 0.0
    rec: dict[str, list[float]] = {k: [] for k in ("t", "h", "V", "Ta", "Ti")}
    t60 = t125 = h125 = None
    t_surf = None
    impact = 0.0
    while t < 30 * 3600.0:
        T_amb, rho, g = _ambient(max(h, 0.0))
        on_ground = h <= 0.0
        V = 0.0 if on_ground else math.sqrt(2.0 * mass_kg * g / (rho * drag_area_m2))
        h_c = TH.convection_coefficient(max(V, 1.0), v.diameter_m, T_amb, rho)
        for _ in range(4):
            G = TH.conductance(v, Ti, Ts)
            Ti += (internal_W - G * (Ti - Ts)) * dt / 4 / v.interior_heat_capacity_J_K
            Ts += TH._shell_balance(v, Ts, Ti, T_amb, h_c, 0.0) * dt / 4 / v.shell_heat_capacity_J_K
        for k, val in (("t", t), ("h", max(h, 0.0)), ("V", V), ("Ta", T_amb - 273.15), ("Ti", Ti - 273.15)):
            rec[k].append(val)
        if t60 is None and Ti - 273.15 >= 60.0:
            t60 = t
        if t125 is None and Ti - 273.15 >= 125.0:
            t125, h125 = t, max(h, 0.0)
            if on_ground:
                break
        if not on_ground:
            h -= V * dt
            if h <= 0.0:
                t_surf, impact = t, V
        elif t_surf is not None and t - t_surf > surface_hold_s:
            break
        t += dt
    a = {k: np.array(x) for k, x in rec.items()}
    survival = None
    if t_surf is not None:
        survival = (t125 - t_surf) if (t125 is not None and t125 >= t_surf) else (0.0 if t125 is not None else None)
    return TerminalResult(a["t"], a["h"], a["V"], a["Ta"], a["Ti"], t_surf if t_surf is not None else float("nan"),
                          impact, t60, t125, h125, survival)


# ---------------------------------------------------------------------------------------------------------------
# Deployment Monte Carlo: parachute drift through the measured wind shear, release and pull-out in gusts
# ---------------------------------------------------------------------------------------------------------------

@dataclass
class DeployMC:
    n: int
    altitude_loss_m: np.ndarray
    vrs_time_s: np.ndarray
    release_airspeed_m_s: np.ndarray
    swing_deg: np.ndarray
    max_descent_m_s: np.ndarray
    probe: list[str]
    procedure: str


def deployment_monte_carlo(mass_kg: float, susp_mass_kg: float, chute_D: float, v_h: float, drag_area_m2: float = 0.45,
                           payload_cda_m2: float = 1.0, thrust_margin: float = 1.6, n: int = 400, seed: int = 7,
                           procedure: str = "forward", motor_fail_p: float = 0.02, h_release: float = 61e3,
                           h_open: float = 69e3) -> DeployMC:
    """Monte Carlo of the hanging-and-release phase.

    Per sample [Y distributions, D/D-ag inputs]: (1) a measured Pioneer Venus DLBI wind profile (one of the four
    probes with data at the deployment altitudes, [D]) plus a uniform ±2 m/s per km shear perturbation (VEX: 8 ± 2
    m/s/km at 61–66 km [D-ag]); (2) horizontal gusts σ 1 m/s (VEGA fluctuations up to 1–2 m/s × 1.5 [D-ag]) and
    vertical gusts σ 0.7 m/s (VEGA [D-ag]); (3) density case thin / mean / dense (probe envelope); (4) thrust ramp
    1–3 s; (5) one motor failed with probability ``motor_fail_p`` (thrust margin reduced by 1/6).

    The parachute system drifts with drag relaxation towards the local wind while descending at terminal speed; at
    release the rotorcraft keeps that horizontal velocity, so its air-relative speed is the shear-induced lag plus
    the gust. Swing angle under the chute: payload side force from the relative wind over its weight. Pull-out:
    vertical point mass, thrust ramp to ``thrust_margin``·W; inside the vortex-ring band (descent 0.5–1.5 v_h with
    horizontal airspeed < v_h) thrust is cut by 20 % (helicopter practice, [Y]). ``procedure="forward"`` pitches to
    gain 2 v_h airspeed within 2 s (leaves the band); ``"vertical"`` keeps the airspeed it has."""
    rng = np.random.default_rng(seed)
    z = _grid_km = np.array(A._load()["grid_km"], dtype=float) * 1e3      # noqa: F841
    winds = {p: np.array([np.nan if v is None else v for v in A._load()["wind"][p]["west_m_s"]], dtype=float)
             for p in A.PROBES}
    usable = [p for p, w in winds.items() if np.isfinite(np.interp([h_release / 1e3], z / 1e3, w)).all()
              and np.isfinite(w[(z >= h_release - 1e3) & (z <= min(h_open, A.Z_MAX))]).sum() >= 2]
    S = math.pi * chute_D ** 2 / 4.0
    losses, vrs_t, airs, swings, vmaxs, probes = [], [], [], [], [], []
    for _ in range(n):
        p = usable[int(rng.integers(len(usable)))]
        w = winds[p]
        ok = np.isfinite(w)
        dshear = rng.uniform(-2.0, 2.0) / 1e3                      # extra shear [m/s per m]
        case = ["thin", "mean", "dense"][int(rng.integers(3))]

        def u_w(hh: float) -> float:
            return float(np.interp(hh, z[ok], w[ok])) + dshear * (hh - h_release)

        def rho_at(hh: float) -> float:
            hh = min(max(hh, A.Z_MIN), A.Z_MAX)
            return A.state(hh, case).rho

        # parachute descent with horizontal drag relaxation (start: moving with the wind at h_open)
        h = min(h_open, A.Z_MAX)
        u = u_w(h)
        dt = 0.5
        Vd = 0.0
        while h > h_release:
            rho = rho_at(h)
            g = P.venus_gravity(h)
            Vd = math.sqrt(2.0 * susp_mass_kg * g / (rho * 0.55 * S))
            rel = u - u_w(h)
            u -= 0.5 * rho * math.hypot(Vd, rel) * 0.55 * S * rel / susp_mass_kg * dt
            h -= Vd * dt
        gust_h = rng.normal(0.0, 1.0)
        rel_air = abs(u - u_w(h) + gust_h)
        rho = rho_at(h)
        W = mass_kg * P.venus_gravity(h)
        swings.append(math.degrees(math.atan2(0.5 * rho * rel_air ** 2 * payload_cda_m2, W)))
        airs.append(rel_air)
        # pull-out
        margin = thrust_margin * (5.0 / 6.0 if rng.random() < motor_fail_p else 1.0)
        ramp = rng.uniform(1.0, 3.0)
        V, hh, t, vrs, vmax, wv = Vd, h, 0.0, 0.0, Vd, 0.0
        air = rel_air
        while t < 120.0:
            wv = 0.98 * wv + 0.7 * math.sqrt(1 - 0.98 ** 2) * rng.normal()      # vertical gust, ~2.5 s memory
            if procedure == "forward":
                air = min(2.0 * v_h, rel_air + v_h * t)                      # pitch over: +v_h per s up to 2 v_h
            thrust = W * (1.0 + (margin - 1.0) * min(t / ramp, 1.0))
            in_vrs = 0.5 * v_h <= V + wv <= 1.5 * v_h and air < v_h
            if in_vrs:
                thrust *= 0.8
                vrs += 0.05
            drag = 0.5 * rho_at(hh) * (V + wv) * abs(V + wv) * drag_area_m2
            V += (W - thrust - drag) / mass_kg * 0.05
            hh -= V * 0.05
            t += 0.05
            vmax = max(vmax, V)
            if V <= 0.0 and t > 0.5:
                break
        losses.append(h - hh)
        vrs_t.append(vrs)
        vmaxs.append(vmax)
        probes.append(p)
    return DeployMC(n, np.array(losses), np.array(vrs_t), np.array(airs), np.array(swings), np.array(vmaxs), probes,
                    procedure)
