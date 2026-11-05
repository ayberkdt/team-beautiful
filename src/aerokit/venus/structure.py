"""First-order structural sizing of VESPER's arms and blades (Euler–Bernoulli beams, thin-walled sections).

**Arm** — a CFRP tube cantilevered from the body carries the rotor thrust ``P`` at its tip. Thin-wall tube of mean
radius ``r`` and wall ``t``: ``I ≈ π r³ t``, area ``2π r t``. The wall is sized for the stiffer of (a) tip deflection
``δ = P L³ / (3 E I) ≤ δ_max`` and (b) root stress ``σ = P L r / I ≤ σ_allow``, with a minimum gauge. Laminate
values (E 70 GPa quasi-isotropic-to-axial mix, ρ 1600 kg/m³, allowable 300 MPa incl. knock-downs) are assumptions
[Y], as is the deflection limit: 3.5 % of the arm length ≙ a 3° tip slope (rotor-plane tilt under the maximum
thrust; slope = 1.5 δ / L for a tip-loaded cantilever), and the 0.8 mm minimum gauge.

**Blade** — first flap frequency of a hingeless blade: non-rotating cantilever ``ω₀ = 1.875² √(EI / (m' L⁴))``,
rotating ``ω² = ω₀² + K Ω²`` with the Southwell coefficient ``K ≈ 1.19`` for the first cantilever mode (textbook
value, not read in this session [Y]). Ratio to rotor speed (per rev) compared with Ingenuity's ~2/rev and the Mars
Science Helicopter hexacopter's 1.55/rev (research notes C_balaram2018, C_johnson2020_msh) [D-ag].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["ArmSizing", "size_arm", "BladeStructure", "blade_flap"]


@dataclass(frozen=True)
class ArmSizing:
    length_m: float
    tip_load_N: float
    diameter_m: float
    wall_m: float
    mass_per_m: float
    tip_deflection_m: float
    root_stress_Pa: float
    governing: str


def size_arm(length_m: float, tip_load_N: float, diameter_m: float = 0.06, E: float = 70e9, rho: float = 1600.0,
             sigma_allow: float = 300e6, deflection_frac: float = 0.035, min_wall: float = 0.8e-3,
             sleeve_kg_m: float = 0.04) -> ArmSizing:
    """Wall thickness and mass per metre of a CFRP arm tube (+ FEP sleeve ``sleeve_kg_m``)."""
    if min(length_m, tip_load_N, diameter_m) <= 0:
        raise ValueError("length, load and diameter must be > 0")
    r = diameter_m / 2.0
    I_defl = tip_load_N * length_m ** 3 / (3.0 * E * deflection_frac * length_m)
    I_str = tip_load_N * length_m * r / sigma_allow
    t_defl = I_defl / (math.pi * r ** 3)
    t_str = I_str / (math.pi * r ** 3)
    t = max(t_defl, t_str, min_wall)
    gov = "deflection" if t == t_defl else ("stress" if t == t_str else "minimum gauge")
    I = math.pi * r ** 3 * t
    return ArmSizing(length_m, tip_load_N, diameter_m, t, 2.0 * math.pi * r * t * rho + sleeve_kg_m,
                     tip_load_N * length_m ** 3 / (3.0 * E * I), tip_load_N * length_m * r / I, gov)


@dataclass(frozen=True)
class BladeStructure:
    radius_m: float
    mass_per_m: float
    EI_Nm2: float
    omega_rad_s: float
    flap_nonrotating_Hz: float
    flap_rotating_per_rev: float
    tip_deflection_m: float
    root_moment_Nm: float


def blade_flap(radius_m: float, root_cutout: float, blade_mass_kg: float, chord_m: float, thickness_ratio: float,
               omega: float, blade_thrust_N: float, E: float = 120e9, spar_width_frac: float = 0.5,
               wall_m: float = 1.0e-3, southwell: float = 1.19) -> BladeStructure:
    """First flap frequency and hover tip deflection of a blade with a rectangular box spar (uniform beam)."""
    L = radius_m * (1.0 - root_cutout)
    b = spar_width_frac * chord_m
    h = thickness_ratio * chord_m
    I = (b * h ** 3 - max(b - 2 * wall_m, 0.0) * max(h - 2 * wall_m, 0.0) ** 3) / 12.0
    EI = E * I
    m_ = blade_mass_kg / L
    w0 = 1.875 ** 2 * math.sqrt(EI / (m_ * L ** 4))
    w = math.sqrt(w0 ** 2 + southwell * omega ** 2)
    q = blade_thrust_N / L                                 # uniform load (conservative for the root moment)
    return BladeStructure(radius_m, m_, EI, omega, w0 / (2 * math.pi), w / omega, q * L ** 4 / (8.0 * EI),
                          0.5 * blade_thrust_N * L)
