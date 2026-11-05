"""Nominal constellations, GMST Earth rotation, visibility and multi-hop link chains (docs/07 §9 C1).

Independent references: the GPS SPS PS 2008 slot table (GEC and GHA columns), closed-form J2 rates and periods,
exact geometry of a geostationary satellite, and the linear-domain noise sum done by hand.
"""
from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from aerokit.comms import (CommunicationLink, CommunicationTerminal, FixedGainAntenna, FreeSpaceOnly, Receiver,
                           RfError, Transmitter)
from aerokit.comms.chain import Hop, evaluate_chain
from aerokit.comms.constants import J2_EARTH_EGM2008, MU_EARTH, OMEGA_EARTH, R_EARTH_EQUATORIAL_EGM2008_M
from aerokit.orbits import constellations as C
from aerokit.orbits import visibility as V
from aerokit.verification import check, check_true, expect_error

SPS = "GPS SPS PS 4th ed. (2008) Table 3.2-1"
DAY = datetime(2026, 11, 5, tzinfo=UTC)


# --- GPS table: GMST + propagation against the published ground-track crossings ---------------------------------
@pytest.mark.parametrize("slot", sorted(C.GPS_SLOTS))
def test_gps_ascending_crossing_longitude_matches_the_table(slot):
    """Propagate each slot back to its last ascending node and read its Earth-fixed longitude (two ascending nodes
    per sidereal day, 180° apart, so the GEC is compared modulo 180°)."""
    sat = next(s for s in C.gps_baseline_24() if s.name == f"GPS {slot}")
    _, dw, dM = sat.rates
    t_node = sat.epoch + timedelta(seconds=-sat.mean_anomaly / (dw + dM))
    r = sat.position_ecef(t_node)[0]
    check(f"{slot}: z at the node", r[2], 0.0, atol=1e-2)       # 26 560 km radius: 1e-2 m is round-off
    lon = math.degrees(math.atan2(r[1], r[0]))
    diff = (lon - C.GPS_GEC[slot] + 90.0) % 180.0 - 90.0
    check(f"{slot}: ascending-node longitude vs GEC (mod 180°)", diff, 0.0, atol=0.02, source=SPS)


def test_gmst_at_the_gps_epoch_matches_the_table_hour_angle():
    gha_s = (18 * 3600 + 36 * 60 + 14.4)
    got_s = math.degrees(C.gmst_rad(C.GPS_EPOCH)) / 15.0 * 3600.0
    # observed 1.1 s (0.005°): more than the table's 0.1 s rounding; UT1 − UTC is not modelled
    check("GMST82 at 00:00 UTC 1 July 1993 [s of time]", got_s, gha_s, atol=2.0, source=SPS + " note: GHA 18h36m14.4s")


def test_j2_rates_and_period_of_the_gps_orbit():
    g = C.gps_baseline_24()[0]
    n = math.sqrt(MU_EARTH / C.GPS_A ** 3)
    node = -1.5 * n * J2_EARTH_EGM2008 * (R_EARTH_EQUATORIAL_EGM2008_M / C.GPS_A) ** 2 * math.cos(math.radians(55))
    check("dΩ/dt = −3/2 n J2 (R/a)² cos i (circular)", g.rates[0], node, rtol=1e-12)
    per_day = math.degrees(g.rates[0]) * 86400
    check_true("J2-only node regression within 10 % of the published total (lunisolar not modelled)",
               abs(per_day / -0.04187 - 1) < 0.10, f"{per_day:.5f} vs -0.04187 deg/day",
               source="GPS SPS PS 2008 §3.2: mean nodal regression -0.04187 deg/day at 55°")
    check("two revolutions per sidereal day (stationary ground track)", g.period_s, math.pi / OMEGA_EARTH,
          rtol=5e-4, source="GPS SPS PS 2008 Table 3.2-3 note 2")


def test_galileo_table_is_walker_24_3_1():
    gal = {s.name.split()[1]: s for s in C.galileo_nominal_24()}
    w = C.walker("W", 24, 3, 1, C.GALILEO_A, C.GALILEO_I, C.GALILEO_EPOCH, raan0_deg=317.632)
    planes = {"A": 0, "B": 1, "C": 2}       # RAAN 317.632, 77.632 (= +120), 197.632 (= +240)
    for slot, s in gal.items():
        k = planes[slot[0]]
        ref = w[k * 8]                            # first satellite of the Walker plane with this RAAN
        check(f"Galileo {slot}: plane RAAN", math.degrees(s.raan) % 360, math.degrees(ref.raan) % 360, atol=1e-9)
        offset = (math.degrees(s.mean_anomaly - ref.mean_anomaly) - 0.153) % 45.0
        check(f"Galileo {slot}: in-plane phase is a multiple of 45° (+ the 15°·k Walker phasing)",
              min(offset, 45.0 - offset), 0.0, atol=1e-9, source="EUSPA GSC reference constellation")
    expect_error("T not divisible by P", C.walker, "x", 25, 3, 1, 3e7, 56.0, C.GALILEO_EPOCH, error=ValueError)


# --- geometry ------------------------------------------------------------------------------------------------
def test_geostationary_satellite_geometry():
    geo = C.geostationary(42.0, DAY)
    times = V.time_grid(DAY, DAY + timedelta(days=1), 3 * 3600)
    sub = V.GroundSite("sub-satellite point", 0.0, 42.0, 0.0, mask_deg=0.0)
    la = V.look_angles(geo, sub, times)
    check("GEO stays at zenith of its sub-point (24 h)", float(la.elevation_deg.min()), 90.0, atol=1e-3)
    check("range = a − R_e at the equator", float(la.range_m[0]),
          (MU_EARTH / OMEGA_EARTH ** 2) ** (1 / 3) - 6378137.0, rtol=1e-9)
    north = V.GroundSite("north", 40.0, 42.0)
    check("seen due south from a site north of it", float(V.look_angles(geo, north, DAY).azimuth_deg[0]), 180.0,
          atol=1e-6)
    east = V.GroundSite("east", 40.0, 60.0)
    az = float(V.look_angles(geo, east, DAY).azimuth_deg[0])
    check_true("seen south-west from a site north-east of it", 180.0 < az < 270.0, az)


def test_access_window_edges_sit_on_the_mask():
    site = V.GroundSite("Everest", 27.9881, 86.9250, 8000.0, mask_deg=10.0)
    sat = C.gps_baseline_24()[0]
    wins = V.access_windows(sat, site, DAY, DAY + timedelta(days=1), step_s=60.0, edge_tolerance_s=0.1)
    check_true("at least one pass per day", len(wins) >= 1, len(wins))
    for w in wins:
        for t in (w.start, w.end):
            if DAY < t < DAY + timedelta(days=1):
                check(f"edge elevation {t:%H:%M:%S}", float(V.look_angles(sat, site, t).elevation_deg[0]), 10.0,
                      atol=0.01)
        check_true("max elevation above the mask", w.max_elevation_deg >= 10.0)
    check_true("windows ordered and disjoint", all(a.end <= b.start for a, b in zip(wins, wins[1:], strict=False)))


@pytest.mark.parametrize("lat, lon", [(0.0, 0.0), (45.0, 30.0), (-35.0, 150.0), (70.0, -100.0)])
def test_gps_keeps_at_least_four_in_view(lat, lon):
    site = V.GroundSite("site", lat, lon, mask_deg=5.0)
    n = V.count_in_view(C.gps_baseline_24(), site, V.time_grid(DAY, DAY + timedelta(days=1), 600.0))
    check_true(f"≥ 4 GPS satellites above 5° at ({lat}, {lon}) all day (plausibility of the 24-slot design)",
               n.min() >= 4, f"min {n.min()}, max {n.max()}")


def test_common_view_of_a_geostationary_relay():
    geo = C.geostationary(0.0, DAY)
    times = V.time_grid(DAY, DAY + timedelta(hours=6), 1800)
    a, b = V.GroundSite("a", 10.0, -10.0), V.GroundSite("b", -20.0, 15.0)
    far = V.GroundSite("antipode", 0.0, 180.0)
    check("two sites in the footprint: relay always available", V.common_view([geo], a, b, times)[1], 1.0)
    check("a site behind the Earth: never", V.common_view([geo], a, far, times)[1], 0.0)


def test_states_are_consistent():
    geo = C.geostationary(10.0, DAY)
    h = 1.0
    fd = (geo.state_eci(DAY + timedelta(seconds=h))[0, :3] - geo.state_eci(DAY - timedelta(seconds=h))[0, :3]) / 2
    check("two-body velocity = d(position)/dt", float(np.linalg.norm(fd - geo.state_eci(DAY)[0, 3:])), 0.0, atol=1e-3)
    site = V.GroundSite("s", 30.0, 40.0, 500.0)
    st = V.site_state_eci(site, DAY)
    check("site |r| equals its ECEF radius", float(np.linalg.norm(st[:3])), float(np.linalg.norm(site.ecef)), rtol=1e-12)
    check("site velocity = ω_E × r", float(np.linalg.norm(st[3:])), OMEGA_EARTH * float(np.hypot(*site.ecef[:2])),
          rtol=1e-12)
    g = V.link_geometry(geo, site, DAY, uplink=True)
    check("link range = look-angle range", g.range_m, float(V.look_angles(geo, site, DAY).range_m[0]), rtol=1e-9)
    expect_error("naive datetime rejected", geo.state_eci, datetime(2026, 1, 1), error=ValueError)


# --- multi-hop chain -----------------------------------------------------------------------------------------
def _hop(range_m: float, name: str, visible: bool = True) -> Hop:
    from aerokit.comms import geometry_from_states
    tx = CommunicationTerminal("tx", transmitter=Transmitter(FixedGainAntenna(3.0), rf_power_w=5.0))
    rx = CommunicationTerminal("rx", receiver=Receiver(FixedGainAntenna(0.0), system_noise_temperature_k=500.0))
    link = CommunicationLink(name, tx, rx, frequency_hz=406.05e6, bandwidth_hz=10e3, propagation_models=(FreeSpaceOnly(),))
    geo = geometry_from_states(0.0, np.zeros(6), np.r_[range_m, 0, 0, 0, 0, 0],
                               visibility="VISIBLE" if visible else "BELOW_ELEVATION_MASK")
    return Hop(link, geo)


def test_transparent_chain_adds_noise_linearly():
    h = _hop(2.0e7, "up")
    single = evaluate_chain([h])
    two = evaluate_chain([h, _hop(2.0e7, "down")], "transparent", bit_rate_bps=400.0, required_ebn0_db=8.0)
    check("two equal transparent hops: C/N0 − 10 log10(2)", two.cn0_dbhz, single.cn0_dbhz - 10 * math.log10(2),
          atol=1e-9, source="1/(C/N0) = Σ 1/(C/N0)_i, by hand")
    check("Eb/N0 = C/N0 − 10 log10(R_b)", two.ebn0_db, two.cn0_dbhz - 10 * math.log10(400.0), atol=1e-9)
    check("margin = Eb/N0 − required", two.margin_db, two.ebn0_db - 8.0, atol=1e-12)
    check("light time is the sum", two.light_time_s, 2 * 2.0e7 / 299_792_458.0, rtol=1e-12)


def test_regenerative_chain_takes_the_weakest_hop():
    near, far = _hop(1.0e7, "near"), _hop(4.0e7, "far")
    r = evaluate_chain([near, far], "regenerative")
    check_true("the far hop limits", r.limiting_hop == 1)
    check("regenerative C/N0 = weakest hop", r.cn0_dbhz, r.hops[1].cn0_dbhz, atol=1e-12)
    t = evaluate_chain([near, far], "transparent")
    check_true("transparent is worse than regenerative", t.cn0_dbhz < r.cn0_dbhz, f"{t.cn0_dbhz} vs {r.cn0_dbhz}")
    check("far hop is 4× the range: 20 log10(4) dB weaker", r.hops[0].cn0_dbhz - r.hops[1].cn0_dbhz,
          20 * math.log10(4.0), atol=1e-9)


def test_chain_refusals():
    expect_error("empty chain", evaluate_chain, [], error=RfError)
    expect_error("hidden hop", evaluate_chain, [_hop(1e7, "x", visible=False)], error=RfError)
    expect_error("requirement without bit rate", evaluate_chain, [_hop(1e7, "x")], required_ebn0_db=5.0, error=RfError)
    expect_error("unknown relay", evaluate_chain, [_hop(1e7, "x")], "magic", error=RfError)


def test_beacon_to_command_centre_through_meosar():
    """Everest beacon → Galileo repeater → Kathmandu: pick a satellite in common view and chain the two hops."""
    beacon = V.GroundSite("Everest beacon", 27.9881, 86.9250, 8000.0, mask_deg=10.0)
    lut = V.GroundSite("Kathmandu", 27.7172, 85.3240, 1400.0, mask_deg=5.0)
    sats = C.galileo_nominal_24()
    up = [s for s in sats if V.look_angles(s, beacon, DAY).elevation_deg[0] >= 10 and
          V.look_angles(s, lut, DAY).elevation_deg[0] >= 5]
    check_true("a Galileo satellite is in common view", len(up) > 0)
    s = up[0]
    tx = CommunicationTerminal("beacon", transmitter=Transmitter(FixedGainAntenna(0.0), rf_power_w=5.0))
    rep = CommunicationTerminal("repeater", receiver=Receiver(FixedGainAntenna(0.0), system_noise_temperature_k=500.0))
    up_link = CommunicationLink("406 MHz up", tx, rep, frequency_hz=406.05e6, bandwidth_hz=10e3,
                                propagation_models=(FreeSpaceOnly(),))
    hops = [Hop(up_link, V.link_geometry(s, beacon, DAY, uplink=True))]
    r = evaluate_chain(hops, bit_rate_bps=400.0)
    rng = V.look_angles(s, beacon, DAY).range_m[0]
    fspl = 20 * math.log10(4 * math.pi * rng * 406.05e6 / 299_792_458.0)
    check("uplink free-space loss at the look-angle range", r.hops[0].free_space_path_loss_db, fspl, atol=1e-6)
    check_true("MEO uplink range between 19 000 and 30 000 km", 1.9e7 < rng < 3.0e7, rng)
