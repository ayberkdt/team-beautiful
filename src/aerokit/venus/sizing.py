"""Mass-budget closure of a solar-electric Venus multirotor (NDARC-style spreadsheet sizing, much simplified).

**Loop.** Guess gross mass → weight at the design altitude → rotor solidity from the design blade loading
``C_T/σ`` and the hover tip speed → collective from BEMT → hover power → motor torque/power at the control
margin → component masses → battery for the energy reserve → sum + contingency → repeat until the mass changes by
< 1 g.

**Rules taken from the Mars Science Helicopter study** (Johnson et al. 2020, research note C_johnson2020_msh)
[D-ag]: ``C_T/σ`` ≈ 0.10–0.115 at design; ≥ 40 % thrust margin from design blade loading to stall; 20 %
weight contingency; avionics 1.2 kg. Every other mass relation is an assumption [Y], listed in :class:`MassModel`
so that a reviewer sees and changes it in one place.

**Geometry.** Hexacopter with rotors touching-plus-clearance: arm length ``D + c``; the bifacial solar deck is a
hexagon centred on the body whose corners stay ``c/2`` inside every rotor disk edge (no shading of / by the rotor
wake): circumradius ``arm − R − c/2``. Options add solar area outside the disks: ``"halo"`` (a ring of panels
outside the rotor tips, width ``halo_width``) or ``"blades"`` (cells on the upper and lower blade skins).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, replace
from typing import Any

from aerokit.references import cite
from aerokit.venus import atmosphere as A
from aerokit.venus import bemt as B
from aerokit.venus import performance as F
from aerokit.venus import power as PW

__all__ = ["MassModel", "Requirements", "Design", "close", "VENUS_AIRFOIL"]

# Section polar for Re ~ 2-5e5, M < 0.5 (cambered, moderately thick) — assumption [Y]
VENUS_AIRFOIL = B.Airfoil(cl_alpha=5.73, alpha0=math.radians(-2.0), cl_max=1.3, cd0=0.012, d1=0.0, d2=0.6,
                          re_ref=3.0e5, re_exponent=0.2)


@dataclass(frozen=True)
class MassModel:
    """Mass-estimating relations [Y] (kg, m, N·m, W)."""

    blade_areal: float = 2.2              # kg per m² of blade planform (CFRP shell + spar + FEP wrap)
    hub_per_rotor: float = 0.12
    motor_specific_torque: float = 7.0    # N·m per kg, direct-drive outrunner, continuous peak
    motor_specific_power: float = 4000.0  # W per kg
    esc_specific_power: float = 15000.0
    gear_ratio: float = 5.0               # 1 = direct drive; 5 = single-stage sealed planetary (baseline: robustness
    #                                       study — direct drive does not close below ~185 Wh/kg cells or 5.2 N·m/kg)
    gearbox_torque_density: float = 25.0  # N·m of output torque per kg of gearbox [Y]
    gearbox_efficiency: float = 0.95      # [Y]
    arm_linear: float | None = None       # kg/m; None = sized by aerokit.venus.structure.size_arm (2 % tip deflection)
    arm_tube_d: float = 0.08              # arm tube diameter [m] (80 mm: lightest deflection-governed tube) [K/Y]
    fold_hinge: float = 0.15              # per arm (Ti hinge, latch, spring)
    vessel_base: float = 2.2              # Ti pressure vessel, seals, N2 fill
    vessel_per_internal_kg: float = 0.12  # vessel growth per kg of battery + avionics inside
    thermal_base: float = 0.4
    thermal_frac: float = 0.06            # insulation/radiator per kg inside
    avionics: float = 1.2                 # MSH value [D-ag]
    comms: float = 0.8                    # UHF/S radio + antenna
    wiring_frac: float = 0.04
    coating_frac: float = 0.02            # FEP/PFA/Parylene on exposed parts
    attach: float = 0.8                   # bridle ring, pyro release, deployment fittings
    contingency: float = 0.20             # MSH [D-ag]
    halo_structure_per_m2: float = 0.6    # extra frame for halo panels


@dataclass(frozen=True)
class Requirements:
    payload_kg: float = 3.0
    payload_W: float = 30.0
    avionics_W: float = 25.0
    heater_W: float = 0.0
    altitude_m: float = 55e3
    atmosphere_case: str = "mean"
    reserve_hover_h: float = 0.5          # battery covers this much hover with no sun [Y]
    thrust_margin: float = 1.6            # T_max / W for motor sizing (control, gusts, climb) [Y]
    ct_sigma: float = 0.10                # design blade loading (MSH 0.11-0.115) [D-ag]
    rotors: int = 6
    blades: int = 2
    twist_deg: float = -12.0
    taper: float = 0.6                    # tip / root chord
    clearance_m: float = 0.10
    solar_option: str = "deck"            # deck | halo | blades
    halo_width_m: float = 0.30
    solar_efficiency: float = 0.29
    battery: PW.Battery = field(default_factory=lambda: PW.LI_ION_NCR18650B)


@dataclass
class Design:
    D: float
    V_tip: float
    req: Requirements
    gross_kg: float
    breakdown: dict
    rotor: B.Rotor
    system: F.RotorSystem
    hover: F.HoverPoint
    arm_m: float
    deck_circumradius_m: float
    solar_area_m2: float
    battery_Wh: float
    P_hover_elec_W: float
    P_bucket_elec_W: float
    V_bucket: float
    P_sys_W: float
    P_solar_overhead_W: float
    sustain_mu0_hover: float | None
    sustain_mu0_loiter: float | None
    iterations: int
    converged: bool

    def summary(self) -> dict:
        out = {k: v for k, v in asdict(self).items() if k not in ("req", "rotor", "system", "hover", "breakdown")}
        out["breakdown"] = self.breakdown
        out["rpm"] = self.hover.rpm
        out["FM"] = self.hover.FM
        out["tip_mach"] = self.hover.per_rotor.tip_mach
        out["re75"] = self.hover.per_rotor.re75
        out["theta75_deg"] = self.rotor.theta75_deg
        out["solidity"] = self.rotor.solidity
        out["disk_loading_N_m2"] = self.hover.weight_N / self.system.disk_area
        return out


def _mu0_for(power_needed: float, arr: PW.SolarArray, h: float) -> float | None:
    """Smallest cos(zenith) at which the array covers ``power_needed`` (None if never)."""
    if arr.power(h, 1.0) < power_needed:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if arr.power(h, mid) >= power_needed:
            hi = mid
        else:
            lo = mid
    return hi


@cite("johnson_2020_msh", "leishman_2006_helicopter", note="MSH sizing rules; BEMT hover")
def close(D: float, V_tip: float, req: Requirements = Requirements(), mm: MassModel = MassModel(),
          m0: float = 30.0, tol: float = 1e-3, max_iter: int = 60) -> Design:
    """Close the mass budget for rotor diameter ``D`` [m] and hover tip speed ``V_tip`` [m/s]."""
    if D <= 0 or V_tip <= 0:
        raise ValueError("D and V_tip must be > 0")
    s = A.state(req.altitude_m, req.atmosphere_case)
    flow = B.FlowState(s.rho, s.mu, s.a)
    R = D / 2.0
    n = req.rotors
    arm = D + req.clearance_m
    deck_rc = arm - R - req.clearance_m / 2.0
    body_d = 0.6
    deck_area = max(1.5 * math.sqrt(3.0) * deck_rc ** 2 - math.pi * body_d ** 2 / 4.0, 0.0)
    def evaluate(m: float) -> dict:
        W = m * s.g
        T = W / n
        sigma = T / (s.rho * math.pi * R * R * V_tip ** 2 * req.ct_sigma)
        c75 = sigma * math.pi * R / req.blades
        # linear taper about 0.75 R (root cut-out 0.15): c(r) = c_root + (c_tip - c_root) x, x = (r-0.15)/0.85
        x75 = (0.75 - 0.15) / 0.85
        c_root = c75 / (1.0 + (req.taper - 1.0) * x75)
        rot = B.Rotor(R, req.blades, c_root, c_root * req.taper, 10.0, req.twist_deg, 0.15, VENUS_AIRFOIL)
        rot, res = B.solve_collective(rot, T, V_tip / R, flow)
        system = F.RotorSystem(rot, n, motor_efficiency=0.88 * (mm.gearbox_efficiency if mm.gear_ratio > 1 else 1.0))
        hp = F.hover_from(system, W, flow, res)
        Q_h = hp.per_rotor.torque * system.bemt_power_factor
        Q_max = Q_h * req.thrust_margin
        P_max_rotor = hp.shaft_W / n * req.thrust_margin ** 1.5
        planform = req.blades * R * 0.85 * (c_root + c_root * req.taper) / 2.0
        blades_m = n * planform * mm.blade_areal
        motors_m = n * max(Q_max / mm.gear_ratio / mm.motor_specific_torque, P_max_rotor / mm.motor_specific_power)
        if mm.gear_ratio > 1:
            motors_m += n * Q_max / mm.gearbox_torque_density            # gearbox in the same sealed can
        escs_m = n * P_max_rotor / mm.esc_specific_power
        if mm.arm_linear is None:
            from aerokit.venus.structure import size_arm

            arm_kg_m = size_arm(arm, req.thrust_margin * W / n, mm.arm_tube_d).mass_per_m
        else:
            arm_kg_m = mm.arm_linear
        arms_m = n * (arm * arm_kg_m + 2.0 * mm.fold_hinge)          # Z-fold: two hinges per arm
        solar_area = deck_area
        solar_extra = 0.0
        if req.solar_option == "halo":
            halo = 2.0 * math.pi * (arm + R + req.halo_width_m / 2.0) * req.halo_width_m
            solar_area += halo
            solar_extra = halo * mm.halo_structure_per_m2
        elif req.solar_option == "blades":
            solar_area += n * planform          # one face up; bifacial response covers the lower skin
        arr = PW.SolarArray(solar_area, req.solar_efficiency)
        solar_m = arr.mass + solar_extra
        P_sys = req.payload_W + req.avionics_W + req.heater_W
        P_h_el = hp.electric_W + P_sys
        battery_Wh = req.reserve_hover_h * P_h_el
        battery_m = req.battery.mass_for(battery_Wh)
        inside = battery_m + mm.avionics
        vessel_m = mm.vessel_base + mm.vessel_per_internal_kg * inside
        thermal_m = mm.thermal_base + mm.thermal_frac * inside
        base = (blades_m + n * mm.hub_per_rotor + motors_m + escs_m + arms_m + solar_m + battery_m + vessel_m
                + thermal_m + mm.avionics + mm.comms + mm.attach + req.payload_kg)
        wiring = mm.wiring_frac * base
        coating = mm.coating_frac * base
        new_m = (base + wiring + coating) * (1.0 + mm.contingency)
        breakdown = {"blades+hubs": blades_m + n * mm.hub_per_rotor, "motors": motors_m, "ESCs": escs_m,
                     "arms+hinges": arms_m, "solar": solar_m, "battery": battery_m, "vessel": vessel_m,
                     "thermal": thermal_m, "avionics": mm.avionics, "comms": mm.comms, "attach": mm.attach,
                     "payload": req.payload_kg, "wiring": wiring, "coating": coating,
                     "contingency": new_m - (base + wiring + coating)}
        return dict(new_m=new_m, rot=rot, system=system, breakdown=breakdown, solar_area=solar_area, arr=arr,
                    P_sys=P_sys, battery_Wh=battery_Wh)

    # secant iteration on g(m) = f(m) - m (growth factor < 1 for a closable design)
    m_a, e_a = m0, None
    ev = evaluate(m_a)
    e_a = ev["new_m"] - m_a
    m_b = ev["new_m"]
    converged = False
    it = 1
    for it in range(2, max_iter + 1):
        ev = evaluate(m_b)
        if ev["new_m"] > 50.0 * m0 or not math.isfinite(ev["new_m"]):
            raise ValueError(f"mass closure diverges (> {50 * m0:.0f} kg): growth factor above 1")
        e_b = ev["new_m"] - m_b
        if abs(e_b) < tol:
            converged = True
            break
        slope = (e_b - e_a) / (m_b - m_a) if m_b != m_a else -1.0
        if slope >= 0.0:                      # growth factor >= 1: no fixed point above this mass
            raise ValueError("mass closure diverges: growth factor above 1")
        m_new = m_b - e_b / slope
        if m_new <= 0 or m_new > 50.0 * m0:
            raise ValueError("mass closure diverges")
        m_a, e_a, m_b = m_b, e_b, m_new
    m = ev["new_m"] if converged else m_b
    rot, system, breakdown, solar_area, arr = ev["rot"], ev["system"], ev["breakdown"], ev["solar_area"], ev["arr"]
    P_sys, battery_Wh = ev["P_sys"], ev["battery_Wh"]
    W = m * s.g
    hp = F.hover(system, W, flow)
    vb, pb = F.bucket(system, W, flow)
    P_h_el = hp.electric_W + P_sys
    P_b_el = pb / system.drive_efficiency + P_sys
    return Design(D, V_tip, req, m, {k: round(v, 3) for k, v in breakdown.items()}, rot, system, hp, arm, deck_rc,
                  solar_area, battery_Wh, P_h_el, P_b_el, vb, P_sys, arr.power(req.altitude_m, 1.0),
                  _mu0_for(P_h_el, arr, req.altitude_m), _mu0_for(P_b_el, arr, req.altitude_m), it, converged)

def with_option(req: Requirements, **kw: Any) -> Requirements:
    return replace(req, **kw)
