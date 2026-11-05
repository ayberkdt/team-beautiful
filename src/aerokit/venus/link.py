"""Rotorcraft → relay-orbiter UHF link at Venus (reuses :mod:`aerokit.comms.rf`).

Geometry: a circular relay orbit of altitude ``h_orb`` above a vehicle at cloud altitude; slant range at elevation
``ε`` from the law of cosines on the sphere. Pass length for an overhead pass of a circular orbit (the drifting
vehicle moves at ~65 m/s, negligible against ~7 km/s orbital speed). Data rate: ``R_b = C/N0 − Eb/N0_req − margin``.

Sourced numbers (research notes, [D-ag]): VEVA sonde→gondola UHF 400 MHz, 1 W, 1 dBi / 1 dBi, 200 km, 500 kbps
(Cutts 1999); DAVINCI descent sphere → carrier S-band, 154 Mbit worst / 636 likely / 1.2 Gbit best in ~1 h; VEGA
balloon direct to Earth 1.668 GHz, 4.5 W, 4 bit/s; X-band absorptivity ≈ 0.005 dB/km at 50 km and ~0 above 53 km
(Akatsuki radio occultation) → the upward path from 55 km is essentially loss-free. Venus' microwave brightness
seen by a down-looking orbiter antenna raises its noise temperature — taken as 700 K total at UHF [Y, not sourced].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit import planetary as P
from aerokit.comms.rf import carrier_to_noise_density_dbhz, free_space_path_loss_db, linear_to_db, watts_to_dbw
from aerokit.references import cite
from aerokit.venus.entry import MU_VENUS

__all__ = ["slant_range", "pass_duration", "RelayLink", "link_rate", "pass_data_volume", "veva_check"]


def slant_range(h_vehicle: float, h_orbit: float, elevation_deg: float) -> float:
    """Distance [m] from a vehicle at ``h_vehicle`` to an orbiter at ``h_orbit`` seen at ``elevation_deg``."""
    Rv = P.VENUS_RADIUS + h_vehicle
    Ro = P.VENUS_RADIUS + h_orbit
    e = math.radians(elevation_deg)
    return -Rv * math.sin(e) + math.sqrt((Rv * math.sin(e)) ** 2 + Ro ** 2 - Rv ** 2)


def pass_duration(h_vehicle: float, h_orbit: float, min_elevation_deg: float = 10.0) -> float:
    """Length [s] of an overhead pass above ``min_elevation_deg`` (circular orbit, vehicle motion neglected)."""
    Rv = P.VENUS_RADIUS + h_vehicle
    Ro = P.VENUS_RADIUS + h_orbit
    e = math.radians(min_elevation_deg)
    central = math.acos(Rv * math.cos(e) / Ro) - e           # half-angle at the planet centre
    period = 2.0 * math.pi * math.sqrt(Ro ** 3 / MU_VENUS)
    return 2.0 * central / (2.0 * math.pi) * period


@dataclass(frozen=True)
class RelayLink:
    frequency_hz: float = 401.585e6       # Proximity-1 UHF return channel [Y]
    tx_power_W: float = 5.0
    tx_gain_dbi: float = 1.0              # crossed dipole over a ground plane, wide beam [Y]
    rx_gain_dbi: float = 6.0              # orbiter UHF helix [Y]
    rx_noise_K: float = 700.0             # receiver + hot Venus in the beam [Y]
    losses_db: float = 3.0                # cables, pointing, polarisation, implementation [Y]
    ebn0_req_db: float = 4.5              # rate-1/2 coded BPSK-class at 1e-6 BER [Y]
    margin_db: float = 3.0
    atmos_db_per_km: float = 0.0          # above 53 km ~0 (Akatsuki X-band, [D-ag]); UHF lower still


@cite("friis_1946", note="C/N0 = EIRP + G/T - L + 228.6 via aerokit.comms.rf")
def link_rate(link: RelayLink, range_m: float, path_in_atmosphere_km: float = 0.0) -> float:
    """Supported bit rate [bit/s] at slant range ``range_m``."""
    eirp = watts_to_dbw(link.tx_power_W) + link.tx_gain_dbi
    g_t = link.rx_gain_dbi - linear_to_db(link.rx_noise_K)
    loss = free_space_path_loss_db(range_m, link.frequency_hz) + link.losses_db + \
        link.atmos_db_per_km * path_in_atmosphere_km
    cn0 = carrier_to_noise_density_dbhz(eirp, g_t, loss)
    return 10 ** ((cn0 - link.ebn0_req_db - link.margin_db) / 10.0)


def pass_data_volume(link: RelayLink, h_vehicle: float, h_orbit: float, min_elevation_deg: float = 10.0,
                     steps: int = 200) -> tuple[float, float]:
    """(bits, seconds) in one overhead pass with an adaptive rate following the slant range."""
    T = pass_duration(h_vehicle, h_orbit, min_elevation_deg)
    Rv, Ro = P.VENUS_RADIUS + h_vehicle, P.VENUS_RADIUS + h_orbit
    period = 2.0 * math.pi * math.sqrt(Ro ** 3 / MU_VENUS)
    bits = 0.0
    dt = T / steps
    for k in range(steps):
        t = -T / 2 + (k + 0.5) * dt
        th = 2.0 * math.pi * t / period
        rng = math.sqrt(Rv ** 2 + Ro ** 2 - 2 * Rv * Ro * math.cos(th))
        bits += link_rate(link, rng) * dt
    return bits, T


def veva_check() -> float:
    """Eb/N0 margin [dB] of the VEVA link as published (400 MHz, 1 W, 1/1 dBi, 200 km, 500 kbps) with a 300 K
    receiver [Y] — a consistency check of the budget arithmetic, not a validation."""
    lk = RelayLink(400e6, 1.0, 1.0, 1.0, 300.0, 0.0, 0.0, 0.0)
    return 10 * math.log10(link_rate(lk, 200e3) / 500e3)
