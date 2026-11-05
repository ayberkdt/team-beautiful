# Copied from Sidera (sidera.common.constants, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
# sidera/common/constants.py
"""
Sidera Physical Constants & Reference Values
==============================================

This module serves as the Single Source of Truth (SSOT) for all physical,
astronomical, and mathematical constants used throughout the Sidera project.
It eliminates the use of "magic numbers" scattered across the codebase.

Architectural Design Principles
-------------------------------
1. Dependency-Free: This module is written in Pure Python. It deliberately
   avoids imports from `numpy`, `scipy`, or `numba`.
   - Reasoning: This ensures that constants can be imported directly into
     Numba JIT-compiled kernels (`@njit`) without triggering compilation overhead
     or type inference conflicts.

2. SI Units: Unless explicitly stated otherwise, all quantities conform to
   the International System of Units (SI):
   - Length: Metres (m)
   - Time: Seconds (s)
   - Mass: Kilograms (kg)
   - Angle: Radians (rad)

3. Traceability: Constants are derived from authoritative astronomical sources
   (e.g., JPL DE440 Ephemerides, IAU 2012, CODATA 2018) to ensure high-fidelity
   dynamical propagation.

Usage Guidelines
----------------
- Gravitational Parameters: Use the pre-defined `MU_*` (mu = G * M)
  constants instead of multiplying `G * Mass` manually. Ephemeris providers usually
  determine mu with higher precision than the individual mass.

- Time Systems: Constants like `DAY_S` and `JD_J2000_TT` define the continuous
  time grid (TDB/TT). This module does **not** account for UTC leap seconds.
  For UTC <-> TDB transformations, use `sidera.common.timekeeping` (`Epoch`
  and the leap-second table in `scales`).
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

# =============================================================================
# 1.                          UNIVERSAL CONSTANTS
# =============================================================================

# Speed of light [m/s] (exact, by definition)
C_LIGHT: float = 299_792_458.0

# Stefan-Boltzmann constant [W m^-2 K^-4].
# Exact after the 2019 SI redefinition through fixed h, k_B, and c.
SIGMA_SB: float = 5.670_374_419e-8

# Boltzmann constant [J/K] (exact, fixed by the 2019 SI redefinition).
# Used by the communications subsystem: thermal noise power is N = k T B, and
# the link equation's conventional "+228.6" term is -10 log10(k).
BOLTZMANN_J_PER_K: float = 1.380_649e-23

# Newtonian gravitational constant [m^3 kg^-1 s^-2] (CODATA 2018)
G: float = 6.6743e-11

# Conventional standard acceleration of gravity [m/s^2] (exact by definition).
# Used by the ideal rocket equation for impulsive maneuver mass bookkeeping.
STANDARD_GRAVITY: float = 9.80665


# =============================================================================
# 2.                            TIME CONSTANTS
# =============================================================================

# Seconds per hour [s]
HOUR_S: float = 3_600.0

# Seconds per day [s]
DAY_S: float = 86_400.0

# Days per Julian year [day]
JULIAN_YEAR_DAYS: float = 365.25

# Days per Julian century [day]
JULIAN_CENTURY_DAYS: float = 36_525.0

# J2000 epoch as a Julian Date:
#   2000-01-01 12:00:00 (TT)
JD_J2000_TT: float = 2_451_545.0

# J2000 epoch in Modified Julian Date:
#   2000-01-01 12:00:00 (TT)
MJD_J2000_TT: float = 51_544.5


# =============================================================================
# 3.                            MOON PARAMETERS
# =============================================================================

# Lunar gravitational parameter mu = GM [m^3/s^2]: JPL DE440 (gm_de440.tpc
# BODY301_GM = 4902.8001184575 km^3/s^2) truncated to 10 digits (9.3e-11 relative).
MU_MOON: float = 4_902_800_118_000.0

# Reference radius of the GRAIL lunar gravity fields [m] (JGGRX 1800F header:
# 1738.0 km). Not the LOLA sphere: LDEM/LDAM rasters use OFFSET = 1737.4 km.
R_MOON: float = 1_738_000.0

# Mean lunar radius [m] (pck00011 BODY301_RADII; also the LOLA rasters' sphere)
R_MOON_MEAN: float = 1_737_400.0

# Sidereal rotation rate of the Moon [rad/s]
OMEGA_MOON: float = 2.6616995e-06


# =============================================================================
# 4.                            EARTH PARAMETERS
# =============================================================================

# Earth gravitational parameter [m^3/s^2] (Standard: 3.986004418e14)
MU_EARTH: float = 398_600_441_800_000.0

# Earth Equatorial Radius (WGS-84 semi-major axis) [m]
R_EARTH_EQUATORIAL: float = 6_378_137.0

# Earth mean radius, rounded to 6371 km [m]: a spherical-Earth convention of
# this project, not the WGS-84 mean radius R1 = 6 371 008.771 m.
R_EARTH_MEAN: float = 6_371_000.0

# Earth Mean Angular Velocity of Rotation [rad/s]
# Standard WGS-84 value: 7.2921150e-5 rad/s
OMEGA_EARTH: float = 7.292_115_0e-5

# WGS-84 flattening and derived polar radius [m].
F_EARTH: float = 1.0 / 298.257223563
R_EARTH_POLAR: float = R_EARTH_EQUATORIAL * (1.0 - F_EARTH)

# Earth reference ellipsoid semi-major axis and dynamical form factor (J2)
# used specifically as the default for the Earth-J2 third-body perturbation
# (EarthJ2Params). This is the EGM2008 value (6,378,136.3 m), which
# differs from WGS-84's R_EARTH_EQUATORIAL (6,378,137.0 m) by 0.7 m -- a
# distinct model convention, not interchangeable, so it is its own named
# constant rather than a silent substitution. Both come from the ICGEM
# EGM2008.gfc header and coefficients (fully normalized, tide-free):
# radius 6378136.3 m and C20 = -0.484165143790815e-3, so J2 = -sqrt(5) C20.
# The earlier 1.08262668e-3 was not EGM2008's (4.7e-7 relative off).
R_EARTH_EQUATORIAL_EGM2008_M: float = 6_378_136.3
J2_EARTH_EGM2008: float = 1.0826261738522227e-3

# Mars-only GM (NAIF gm_de440.tpc, BODY499_GM), converted from km^3/s^2.
# BODY4_GM is the Mars system including satellites and is intentionally not used.
MU_MARS: float = 4.282837362069909e13
R_MARS_MEAN: float = 3_389_500.0
R_MARS_EQUATORIAL: float = 3_396_190.0
R_MARS_POLAR: float = 3_376_200.0
MARS_SIDEREAL_ROTATION_S: float = 1.02595676 * DAY_S
# Mean solar day on Mars (one sol), 1.0274912517 Earth days.
MARS_SOL_S: float = 1.0274912517 * DAY_S


# -----------------------------------------------------------------------------
# IAU WGCCRE rotation poles, J2000.0 right ascension / declination [deg]
# -----------------------------------------------------------------------------
# These are the *secular* terms (the T^0 coefficient of alpha_0 and delta_0) of
# the IAU 2015 rotation models, as distributed by NAIF in pck00011.tpc
# (BODY399/BODY499_POLE_RA / _POLE_DEC). They give a reference pole direction on
# J2000 axes via physics.atmosphere.unit_pole_from_ra_dec.
#
# THEY ARE NOT A HIGH-ACCURACY POLE. The published models add secular rates and
# periodic (nutation/precession) terms that these constants deliberately omit.
# Measured against SPICE ``pxform(IAU_<BODY>, J2000, et)`` with pck00011.tpc:
#   Earth: 0.000000 deg at J2000 (the J2000 z-axis IS Earth's pole at J2000.0),
#          0.127 deg by 2022 from precession.
#   Mars : 1.565 deg at J2000 -- the periodic terms dominate, so the secular
#          pole is more than a degree and a half off the true IAU_MARS pole.
# For work where that matters, take the pole from SPICE instead. The tolerance
# is pinned by a test so this statement cannot silently go stale.
EARTH_POLE_RA_J2000_DEG: float = 0.0
EARTH_POLE_DEC_J2000_DEG: float = 90.0
MARS_POLE_RA_J2000_DEG: float = 317.269202
MARS_POLE_DEC_J2000_DEG: float = 54.432516


# =============================================================================
# 5.                             SOLAR SYSTEM
# =============================================================================

# Solar gravitational parameter [m^3/s^2]. Pre-DE440 value rounded to 12
# digits; DE440 (gm_de440.tpc BODY10_GM) gives 1.3271244004127942e20, a
# relative difference of 5.4e-12.
MU_SUN: float = 1.32712440042e+20

# IAU 2015 nominal solar radius [m]
R_SUN_MEAN: float = 695_700_000.0

# Astronomical Unit [m] (IAU 2012 exact)
AU: float = 149_597_870_700.0

# Obliquity of the ecliptic at J2000.0 [deg]: 84381.406 arcsec (IAU 2006).
OBLIQUITY_J2000_DEG: float = 84381.406 / 3600.0

# Reference orbit sizes, NOT instantaneous distances or ephemeris vectors.
# The Earth proxy is explicitly the Earth-Moon barycenter (JPL table 1, J2000).
A_EARTH_MOON_BARYCENTER_J2000: float = 1.00000261 * AU
A_MARS_J2000: float = 1.52371034 * AU
A_MOON_REFERENCE: float = 384_400_000.0

# IAU 2015 nominal total solar irradiance at 1 AU [W/m^2].
# The irradiance is the primary physical quantity; radiation pressure is
# derived below as P = S / c so SRP, albedo, and thermal models stay scaled
# from the same source.
SOLAR_FLUX_1AU: float = 1361.0

# Solar radiation pressure at 1 AU [N/m^2], derived as P = S / c.
P_SUN_1AU: float = SOLAR_FLUX_1AU / C_LIGHT


# =============================================================================
# 6.                 MATHEMATICAL CONSTANTS & CONVERSIONS
# =============================================================================

# Keep PI as a plain float so this module stays dependency-free.
PI: float = 3.141592653589793

TWO_PI: float = 2.0 * PI
OMEGA_MARS: float = TWO_PI / MARS_SIDEREAL_ROTATION_S

# -----------------------------------------------------------------------------
# Other planets: third-body perturbers and optional central bodies
# -----------------------------------------------------------------------------
# GM from NAIF gm_de440.tpc [m^3/s^2]. Mercury and Venus are single bodies
# (BODY1_GM/BODY2_GM equal their centers); Jupiter and Saturn carry the SYSTEM
# barycenter GM (BODY5_GM/BODY6_GM), which is what the DE440 ephemeris positions.
MU_MERCURY: float = 2.2031868551400003e13
MU_VENUS: float = 3.2485859200000000e14
MU_JUPITER_SYSTEM: float = 1.2671276409999998e17
MU_SATURN_SYSTEM: float = 3.7940584841799997e16
# Mean radii from the JPL planetary physical parameters table; reference
# ellipsoids from NAIF pck00011.tpc BODYnnn_RADII [m].
R_MERCURY_MEAN: float = 2_439_400.0
R_MERCURY_EQUATORIAL: float = 2_440_530.0
R_MERCURY_POLAR: float = 2_438_260.0
R_VENUS_MEAN: float = 6_051_800.0
R_JUPITER_MEAN: float = 69_911_000.0
R_JUPITER_EQUATORIAL: float = 71_492_000.0
R_JUPITER_POLAR: float = 66_854_000.0
R_SATURN_MEAN: float = 58_232_000.0
R_SATURN_EQUATORIAL: float = 60_268_000.0
R_SATURN_POLAR: float = 54_364_000.0
# Prime-meridian rates from pck00011.tpc BODYnnn_PM[1] [deg/day] -> [rad/s];
# Venus is retrograde (negative). (PI is defined above; DEG2RAD below.)
OMEGA_MERCURY: float = 6.1385108 * (PI / 180.0) / DAY_S
OMEGA_VENUS: float = -1.4813688 * (PI / 180.0) / DAY_S
OMEGA_JUPITER: float = 870.5360000 * (PI / 180.0) / DAY_S
OMEGA_SATURN: float = 810.7939024 * (PI / 180.0) / DAY_S
# J2000 reference semimajor axes (JPL table 1), NOT instantaneous distances.
A_MERCURY_J2000: float = 0.38709927 * AU
A_VENUS_J2000: float = 0.72333566 * AU
A_JUPITER_J2000: float = 5.20288700 * AU
A_SATURN_J2000: float = 9.53667594 * AU

# -----------------------------------------------------------------------------
# Mars satellites (NAIF mar099s.bsp gives Phobos, Deimos and the Mars center
# about the Mars barycenter)
# -----------------------------------------------------------------------------
# GM from NAIF gm_de440.tpc BODY401_GM / BODY402_GM (km^3/s^2 x 1e9) [m^3/s^2]; the same
# values as the MAR099 fit (mar099s.cmt). That fit used a Mars GM of 4.282837485735626e4
# km^3/s^2, 2.9e-8 above the DE440 BODY499_GM that MU_MARS keeps.
MU_PHOBOS: float = 7.087546066894452e5
MU_DEIMOS: float = 9.615569648120313e4
# Mean radii from the JPL satellite physical parameters; the triaxial NAIF
# pck00011.tpc BODY401/402_RADII (13.0 x 11.4 x 9.1 and 7.8 x 6.0 x 5.1 km)
# reduced to the catalog's biaxial ellipsoid: largest axis equatorial,
# smallest polar, so the collision sphere encloses the body [m].
R_PHOBOS_MEAN: float = 11_080.0
R_PHOBOS_EQUATORIAL: float = 13_000.0
R_PHOBOS_POLAR: float = 9_100.0
R_DEIMOS_MEAN: float = 6_200.0
R_DEIMOS_EQUATORIAL: float = 7_800.0
R_DEIMOS_POLAR: float = 5_100.0
# Synchronous prime-meridian rates, pck00011.tpc BODY401/402_PM[1] [deg/day -> rad/s].
OMEGA_PHOBOS: float = 1128.84475928 * (PI / 180.0) / DAY_S
OMEGA_DEIMOS: float = 285.16188899 * (PI / 180.0) / DAY_S
# MAR099 mean semimajor axes about Mars (JPL mean elements, Laplace plane,
# epoch 2000-01-01.5), NOT instantaneous distances [m].
A_PHOBOS_MAR099: float = 9_375_000.0
A_DEIMOS_MAR099: float = 23_457_000.0
HALF_PI: float = 0.5 * PI

DEG2RAD: float = PI / 180.0
RAD2DEG: float = 180.0 / PI


KM_TO_M: float = 1_000.0
M_TO_KM: float = 1e-3

KM3_TO_M3: float = 1e9
M3_TO_KM3: float = 1e-9


NEARLY_UNIT: float = 0.9995

EPS_1E6: float = 1e-6
EPS_1E12: float = 1e-12
EPS_1E15: float = 1e-15
EPS_1E18: float = 1e-18
EPS_1E24: float = 1e-24
EPS_1E30: float = 1e-30


# =============================================================================
# 7.                            METADATA & PROVENANCE
# =============================================================================

# Dictionary mapping constant names to their authoritative sources.
# This ensures scientific traceability for orbit determination audits.
CONSTANT_SOURCES: Final[Mapping[str, str]] = MappingProxyType({
    # --- Universal ---
    "C_LIGHT": "SI definition (exact)",
    "SIGMA_SB": "SI/CODATA exact value after 2019 SI redefinition",
    "BOLTZMANN_J_PER_K": "SI definition (exact) after the 2019 SI redefinition",
    "G": "CODATA 2018",
    "STANDARD_GRAVITY": "Conventional standard gravity (exact): 9.80665 m/s^2",

    # --- Time / epochs (conventions) ---
    "HOUR_S": "SI hour = 3600 s (definition)",
    "DAY_S": "SI day = 86400 s (definition)",
    "JULIAN_YEAR_DAYS": "Julian year convention (365.25 d)",
    "MJD_J2000_TT": "J2000 epoch: 2000-01-01 12:00:00 TT => MJD 51544.5",

    # --- Sun / solar system ---
    "R_SUN_MEAN": "IAU 2015 nominal solar radius",
    "AU": "IAU 2012 exact definition",
    "MU_SUN": "pre-DE440 GM of the Sun rounded to 12 digits (DE440 differs by 5.4e-12 relative)",
    "SOLAR_FLUX_1AU": "IAU 2015 Resolution B3 nominal total solar irradiance",
    "P_SUN_1AU": "Derived as SOLAR_FLUX_1AU / C_LIGHT",

    # --- Earth ---
    "MU_EARTH": "WGS-84 geocentric GM (retained project convention, not DE440)",
    "R_EARTH_EQUATORIAL": "WGS-84 standards",
    "R_EARTH_MEAN": "6371 km rounded spherical-Earth convention (WGS-84 R1 is 6371008.771 m)",
    "OMEGA_EARTH": "IERS/WGS-84 nominal Earth rotation rate",
    "F_EARTH": "NGA WGS-84 defining flattening: https://earth-info.nga.mil/?action=wgs84&dir=wgs84",
    "R_EARTH_POLAR": "Derived from WGS-84 equatorial radius and flattening",
    "R_EARTH_EQUATORIAL_EGM2008_M": (
        "EGM2008 reference radius, ICGEM EGM2008.gfc header (radius 6378136.3 m); "
        "distinct from WGS-84's R_EARTH_EQUATORIAL."
    ),
    "J2_EARTH_EGM2008": (
        "-sqrt(5) * C20 of ICGEM EGM2008.gfc (fully normalized, tide-free, "
        "C20 = -0.484165143790815e-3): https://icgem.gfz-potsdam.de/"
    ),

    # --- Mars / reference orbital distances ---
    "MU_MARS": "NAIF BODY499_GM: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "R_MARS_MEAN": "JPL: https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "R_MARS_EQUATORIAL": "NAIF BODY499_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_MARS_POLAR": "NAIF BODY499_RADII, averaged polar radius: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "MARS_SIDEREAL_ROTATION_S": "JPL sidereal period: https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "OMEGA_MARS": "Derived as TWO_PI / MARS_SIDEREAL_ROTATION_S",
    "MARS_SOL_S": (
        "NASA GISS Mars24 algorithm, eq. C-2 (1.0274912517 d; Allison & McEwen 2000, Planet. Space Sci. 48:215, "
        "as revised by Allison 2015): https://www.giss.nasa.gov/tools/mars24/help/algorithm.html"
    ),
    "EARTH_POLE_RA_J2000_DEG": (
        "IAU WGCCRE 2015 secular term, NAIF pck00011.tpc BODY399_POLE_RA[0]; "
        "Archinal et al. 2018, Celest. Mech. Dyn. Astr. 130:22, "
        "doi:10.1007/s10569-017-9805-5. Periodic and rate terms excluded."
    ),
    "EARTH_POLE_DEC_J2000_DEG": (
        "IAU WGCCRE 2015 secular term, NAIF pck00011.tpc BODY399_POLE_DEC[0]; "
        "Archinal et al. 2018. Exactly the J2000 z-axis at J2000.0."
    ),
    "MARS_POLE_RA_J2000_DEG": (
        "IAU WGCCRE 2015 secular term, NAIF pck00011.tpc BODY499_POLE_RA[0]; "
        "Archinal et al. 2018. Periodic terms excluded: 1.57 deg from the "
        "true IAU_MARS pole at J2000 (measured against SPICE pxform)."
    ),
    "MARS_POLE_DEC_J2000_DEG": (
        "IAU WGCCRE 2015 secular term, NAIF pck00011.tpc BODY499_POLE_DEC[0]; "
        "Archinal et al. 2018. Periodic terms excluded: see MARS_POLE_RA_J2000_DEG."
    ),
    "A_EARTH_MOON_BARYCENTER_J2000": "JPL table 1, EM Bary (not Earth center): https://ssd.jpl.nasa.gov/planets/approx_pos.html",
    "A_MARS_J2000": "JPL table 1, J2000 reference semimajor axis: https://ssd.jpl.nasa.gov/planets/approx_pos.html",
    "A_MOON_REFERENCE": "NASA approximate reference orbital distance: https://science.nasa.gov/moon/facts/",
    "OBLIQUITY_J2000_DEG": "IAU 2006 precession (Capitaine et al. 2003, P03): epsilon_0 = 84381.406 arcsec",

    # --- Other planets ---
    "MU_MERCURY": "NAIF BODY1_GM (Mercury; barycenter equals center): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "MU_VENUS": "NAIF BODY2_GM (Venus; barycenter equals center): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "MU_JUPITER_SYSTEM": "NAIF BODY5_GM, Jupiter system barycenter: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "MU_SATURN_SYSTEM": "NAIF BODY6_GM, Saturn system barycenter: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "R_MERCURY_MEAN": "JPL: https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "R_MERCURY_EQUATORIAL": "NAIF BODY199_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_MERCURY_POLAR": "NAIF BODY199_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_VENUS_MEAN": "JPL (spherical, equals NAIF BODY299_RADII): https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "R_JUPITER_MEAN": "JPL: https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "R_JUPITER_EQUATORIAL": "NAIF BODY599_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_JUPITER_POLAR": "NAIF BODY599_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_SATURN_MEAN": "JPL: https://ssd.jpl.nasa.gov/planets/phys_par.html",
    "R_SATURN_EQUATORIAL": "NAIF BODY699_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_SATURN_POLAR": "NAIF BODY699_RADII: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_MERCURY": "NAIF BODY199_PM rate (IAU 2015): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_VENUS": "NAIF BODY299_PM rate (IAU 2015, retrograde): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_JUPITER": "NAIF BODY599_PM rate (IAU 2015, System III): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_SATURN": "NAIF BODY699_PM rate (IAU 2015): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "A_MERCURY_J2000": "JPL table 1, J2000 reference semimajor axis: https://ssd.jpl.nasa.gov/planets/approx_pos.html",
    "A_VENUS_J2000": "JPL table 1, J2000 reference semimajor axis: https://ssd.jpl.nasa.gov/planets/approx_pos.html",
    "A_JUPITER_J2000": "JPL table 1, J2000 reference semimajor axis: https://ssd.jpl.nasa.gov/planets/approx_pos.html",
    "A_SATURN_J2000": "JPL table 1, J2000 reference semimajor axis: https://ssd.jpl.nasa.gov/planets/approx_pos.html",

    # --- Mars satellites ---
    "MU_PHOBOS": "NAIF BODY401_GM: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "MU_DEIMOS": "NAIF BODY402_GM: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/gm_de440.tpc",
    "R_PHOBOS_MEAN": "JPL satellite physical parameters (11.08 +/- 0.04 km): https://ssd.jpl.nasa.gov/sats/phys_par/",
    "R_PHOBOS_EQUATORIAL": "NAIF BODY401_RADII largest axis: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_PHOBOS_POLAR": "NAIF BODY401_RADII smallest axis: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_DEIMOS_MEAN": "JPL satellite physical parameters (6.2 +/- 0.24 km): https://ssd.jpl.nasa.gov/sats/phys_par/",
    "R_DEIMOS_EQUATORIAL": "NAIF BODY402_RADII largest axis: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "R_DEIMOS_POLAR": "NAIF BODY402_RADII smallest axis: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_PHOBOS": "NAIF BODY401_PM rate (synchronous): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "OMEGA_DEIMOS": "NAIF BODY402_PM rate (synchronous): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc",
    "A_PHOBOS_MAR099": "JPL mean orbital elements (MAR099, Laplace plane, 2000-01-01.5): https://ssd.jpl.nasa.gov/sats/elem/",
    "A_DEIMOS_MAR099": "JPL mean orbital elements (MAR099, Laplace plane, 2000-01-01.5): https://ssd.jpl.nasa.gov/sats/elem/",

    # --- Moon ---
    "MU_MOON": "JPL DE440 BODY301_GM truncated to 10 digits (9.3e-11 relative)",
    "R_MOON": "GRAIL gravity-field reference radius (JGGRX 1800F header 1738.0 km); LOLA uses 1737.4 km",
    "R_MOON_MEAN": "IAU mean lunar radius (pck00011 BODY301_RADII); the LOLA LDEM/LDAM OFFSET",
    "OMEGA_MOON": "Derived from lunar sidereal period (ω = 2π/T)",
})


# =============================================================================
# 8.                       PUBLIC API DEFINITION (__all__)
# =============================================================================

# Defines the symbols exported when using: from aerokit.comms.constants import *
__all__ = (
    "F_EARTH",
    "R_EARTH_POLAR",
    "MU_MARS",
    "R_MARS_MEAN",
    "R_MARS_EQUATORIAL",
    "R_MARS_POLAR",
    "MARS_SIDEREAL_ROTATION_S",
    "MARS_SOL_S",
    "OMEGA_MARS",
    "EARTH_POLE_RA_J2000_DEG",
    "EARTH_POLE_DEC_J2000_DEG",
    "MARS_POLE_RA_J2000_DEG",
    "MARS_POLE_DEC_J2000_DEG",
    "A_EARTH_MOON_BARYCENTER_J2000",
    "A_MARS_J2000",
    "A_MOON_REFERENCE",
    "OBLIQUITY_J2000_DEG",
    "MU_MERCURY",
    "MU_VENUS",
    "MU_JUPITER_SYSTEM",
    "MU_SATURN_SYSTEM",
    "R_MERCURY_MEAN",
    "R_MERCURY_EQUATORIAL",
    "R_MERCURY_POLAR",
    "R_VENUS_MEAN",
    "R_JUPITER_MEAN",
    "R_JUPITER_EQUATORIAL",
    "R_JUPITER_POLAR",
    "R_SATURN_MEAN",
    "R_SATURN_EQUATORIAL",
    "R_SATURN_POLAR",
    "OMEGA_MERCURY",
    "OMEGA_VENUS",
    "OMEGA_JUPITER",
    "OMEGA_SATURN",
    "A_MERCURY_J2000",
    "A_VENUS_J2000",
    "A_JUPITER_J2000",
    "A_SATURN_J2000",
    # 1. Universal & Physical Constants
    "C_LIGHT",                   # Speed of light in vacuum [m/s]
    "SIGMA_SB",                   # Stefan-Boltzmann constant [W m^-2 K^-4]
    "BOLTZMANN_J_PER_K",          # Boltzmann constant [J/K]
    "G",                         # Newtonian constant of gravitation [m^3/(kg*s^2)]
    "STANDARD_GRAVITY",          # Conventional standard gravity [m/s^2]

    # 2. Time & Epoch Standards
    "DAY_S",                     # Seconds in a Julian day [s]
    "JULIAN_YEAR_DAYS",          # Days in a Julian year (365.25) [day]
    "HOUR_S",                       # Seconds per hour
    "MJD_J2000_TT",                 # Modified Julian Date of J2000.0 epoch

    # 3. Lunar System (The Moon)
    "MU_MOON",                   # Lunar gravitational parameter GM [m^3/s^2]
    "R_MOON",                    # GRAIL gravity-field reference radius [m]
    "R_MOON_MEAN",               # Lunar mean volumetric radius [m]
    "OMEGA_MOON",                # Lunar mean rotation rate [rad/s]

    # 4. The Earth
    "MU_EARTH",                  # Earth gravitational parameter GM [m^3/s^2]
    "R_EARTH_EQUATORIAL",        # Earth equatorial radius (WGS-84) [m]
    "R_EARTH_MEAN",              # Earth mean radius [m]
    "OMEGA_EARTH",               # Earth mean angular velocity [rad/s]
    "R_EARTH_EQUATORIAL_EGM2008_M",  # Earth-J2 default semi-major axis (EGM2008) [m]
    "J2_EARTH_EGM2008",          # Earth-J2 perturbation default dynamical form factor [-]

    # 5. Solar Constants
    "MU_SUN",                    # Solar gravitational parameter GM [m^3/s^2]
    "R_SUN_MEAN",                # Solar nominal mean radius [m]
    "AU",                        # Astronomical Unit [m]
    "P_SUN_1AU",                 # Solar radiation pressure at 1 AU [N/m^2]
    "SOLAR_FLUX_1AU",            # Solar flux at 1 AU [W/m^2]

    # 6. Mathematics & Unit Conversions
    "PI",                        # π
    "TWO_PI",                    # 2π
    "HALF_PI",                   # π/2
    "DEG2RAD",                   # Degrees -> radians factor
    "RAD2DEG",                   # Radians -> degrees factor
    "KM_TO_M",                   # km -> m factor
    "M_TO_KM",                   # m -> km factor
    "KM3_TO_M3",                 # km^3 -> m^3 factor
    "M3_TO_KM3",                 # m^3 -> km^3 factor

    # 7. Numeric tolerances (scale-explicit)
    "NEARLY_UNIT",
    "EPS_1E6",
    "EPS_1E12",                  # generic small epsilon (angles, wrap, comparisons)
    "EPS_1E15",                  # norm / division guard epsilon
    "EPS_1E18",                  # squared-scale epsilon (e.g. r^2 near-origin)
    "EPS_1E24",
    "EPS_1E30",

    # 8. Project Metadata
    "CONSTANT_SOURCES",          # Scientific traceability mapping
)
