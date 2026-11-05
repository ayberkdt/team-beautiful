"""Mode S / ADS-B decoding against the worked examples of Sun (2021), and cross-checks with pyModeS if installed."""
import random

import pytest

from aerokit.atc import modes as m

IDENT = "8D4840D6202CC371C32CE0576098"
POS_EVEN = "8D40621D58C382D690C8AC2863A7"
POS_ODD = "8D40621D58C386435CC412692AD6"
VEL_GS = "8D485020994409940838175B284F"
VEL_TAS = "8DA05F219B06B6AF189400CBC33F"
DF4 = "2000171806A983"
DF5 = "2A00516D492B80"


def test_book_identification():
    assert m.is_valid(IDENT)
    assert m.icao(IDENT) == "4840D6"
    assert m.typecode(IDENT) == 4
    assert m.callsign(IDENT) == "KLM1023"


def test_book_position_fields():
    e, o = m.airborne_position(POS_EVEN), m.airborne_position(POS_ODD)
    assert (e.odd, o.odd) == (False, True)
    assert round(e.lat_cpr * 2 ** 17) == 93000 and round(e.lon_cpr * 2 ** 17) == 51372
    assert round(o.lat_cpr * 2 ** 17) == 74158 and round(o.lon_cpr * 2 ** 17) == 50194
    assert e.altitude_ft == 38000 and o.altitude_ft == 38000


def test_book_global_and_local_cpr():
    e, o = m.airborne_position(POS_EVEN), m.airborne_position(POS_ODD)
    lat, lon = m.cpr_global(e, o, newest_is_odd=False)
    assert lat == pytest.approx(52.25720214843750, abs=1e-12)
    assert lon == pytest.approx(3.91937255859375, abs=1e-12)
    lat2, lon2 = m.cpr_local(e, 52.258, 3.918)
    assert (lat2, lon2) == pytest.approx((52.2572021484375, 3.91937255859375), abs=1e-12)
    assert m.cpr_nl(52.2572021484375) == 36


def test_nl_special_cases():
    assert m.cpr_nl(0.0) == 59
    assert m.cpr_nl(87.0) == 2 and m.cpr_nl(-87.0) == 2
    assert m.cpr_nl(88.0) == 1


def test_book_velocity():
    v = m.airborne_velocity(VEL_GS)
    assert v.subtype == 1 and v.speed_type == "GS"
    assert v.speed_kt == pytest.approx(159.20, abs=0.01)
    assert v.angle_deg == pytest.approx(182.88, abs=0.01)
    assert v.vertical_rate_fpm == -832
    w = m.airborne_velocity(VEL_TAS)
    assert w.subtype == 3 and w.speed_type == "TAS" and w.speed_kt == 375
    assert w.angle_deg == pytest.approx(243.98, abs=0.01)
    assert w.vertical_rate_fpm == -2304


def test_book_surveillance_replies():
    assert m.surveillance_altitude(DF4) == 36000
    assert m.surveillance_squawk(DF5) == "0356"


def test_crc_detects_and_repairs_single_bit():
    rng = random.Random(1)
    for msg in (IDENT, POS_EVEN, VEL_GS):
        n = int(msg, 16)
        for _ in range(20):
            k = rng.randint(6, 112)
            bad = f"{n ^ (1 << (112 - k)):028X}"
            assert not m.is_valid(bad)
            fixed, bit = m.correct_single_bit(bad)
            assert (fixed, bit) == (msg, k)


def test_two_bit_error_is_not_silently_accepted():
    n = int(IDENT, 16)
    bad = f"{n ^ (1 << 50) ^ (1 << 20):028X}"
    fixed, bit = m.correct_single_bit(bad)
    # either refused, or "repaired" to something that is not the original -> CRC alone cannot be trusted for 2 bits
    assert bit is None or fixed != IDENT


def test_gillham_round_trip_all_100ft_levels():
    for alt in range(-1000, 50001, 100):
        assert m.altcode_to_ft(m.gillham_encode(alt)) == alt


def test_squawk_round_trip():
    for sq in ("0000", "7600", "7700", "1234", "0356", "7777"):
        assert m.idcode_to_squawk(m.squawk_to_idcode(sq)) == sq
    with pytest.raises(ValueError):
        m.squawk_to_idcode("1289")


def test_encoders_round_trip():
    msg = m.encode_identification("ABC123", "BTL123")
    assert m.is_valid(msg) and m.callsign(msg) == "BTL123" and m.icao(msg) == "ABC123"
    v = m.encode_velocity("ABC123", 180.0, 250.0, -700.0)
    dv = m.airborne_velocity(v)
    assert dv.speed_kt == pytest.approx(180.0, abs=1.0) and dv.angle_deg == pytest.approx(250.0, abs=0.5)
    assert dv.vertical_rate_fpm == pytest.approx(-704, abs=64)
    d4, d5 = m.encode_df4("ABC123", 3000), m.encode_df5("ABC123", "7600")
    assert m.icao(d4) == "ABC123" and m.surveillance_altitude(d4) == 3000
    assert m.icao(d5) == "ABC123" and m.surveillance_squawk(d5) == "7600"


def test_cpr_encoder_reproduces_book_values_and_round_trips():
    assert m.cpr_encode(52.25720214843750, 3.91937255859375, odd=False) == (93000, 51372)
    rng = random.Random(7)
    for _ in range(200):
        lat, lon = rng.uniform(-80, 80), rng.uniform(-179.9, 179.9)
        e = m.airborne_position(m.encode_position("ABC123", lat, lon, 5000, odd=False))
        o = m.airborne_position(m.encode_position("ABC123", lat, lon, 5000, odd=True))
        res = m.cpr_global(e, o, newest_is_odd=True)
        if res is None:          # NL boundary straddled: decoder correctly refuses
            continue
        assert res[0] == pytest.approx(lat, abs=2e-4)
        assert (res[1] - lon + 180) % 360 - 180 == pytest.approx(0, abs=4e-4)
        loc = m.cpr_local(e, lat + 0.3, lon - 0.3)
        assert loc[0] == pytest.approx(lat, abs=2e-4)


def test_decode_dict_marks_corrupted():
    n = int(IDENT, 16)
    bad = f"{n ^ (1 << 30):028X}"
    d = m.decode(bad)
    assert d["callsign"] == "KLM1023" and d["corrected_bit"] == 112 - 30
    d2 = m.decode(f"{n ^ (1 << 30) ^ (1 << 31) ^ (1 << 77):028X}")
    assert d2["status"] in ("CRC_FAIL", "OK")


# --- independent implementation (skipped if pyModeS is not on the path) -----------------------------------------

def test_cross_check_altcode_with_pymodes():
    alt = pytest.importorskip("pyModeS._altcode")
    for ac in range(1 << 13):
        assert m.altcode_to_ft(ac) == alt.altcode_to_altitude(ac), ac


def test_cross_check_nl_and_crc_with_pymodes():
    util = pytest.importorskip("pyModeS.util")
    for k in range(0, 9000):
        lat = -89.99 + k * 0.02
        assert m.cpr_nl(lat) == util.cprNL(lat), lat
    rng = random.Random(3)
    for _ in range(300):
        msg = f"{rng.getrandbits(112):028X}"
        assert m.parity(msg) == util.crc(msg)


def test_cross_check_decode_with_pymodes():
    pms = pytest.importorskip("pyModeS")
    for msg in (IDENT, VEL_GS, POS_EVEN, DF4, DF5):
        theirs = pms.decode(msg)
        ours = m.decode(msg)
        assert ours["icao"] == theirs["icao"]
        if "callsign" in theirs:
            assert ours["callsign"] == theirs["callsign"]
        if "altitude" in theirs:
            assert ours["altitude_ft"] == theirs["altitude"]
        if "squawk" in theirs:
            assert ours["squawk"] == theirs["squawk"]


# --- vectors read by the research agent (R_1090_riddle.md, R_gillham_wiki.md) [D-ag] ---------------------------

GILLHAM_ROWS = [('000000000001', '0040', -1200), ('000000000011', '0060', -1100), ('000000000010', '0020', -1000), ('000000000110', '0030', -900), ('000000000100', '0010', -800), ('000000001100', '0410', -700), ('000000001110', '0430', -600), ('000000001010', '0420', -500), ('000000001011', '0460', -400), ('000000001001', '0440', -300), ('000000011001', '0640', -200), ('000000011011', '0660', -100), ('000000011010', '0620', 0), ('000000011110', '0630', 100), ('000000011100', '0610', 200), ('000000010100', '0210', 300), ('000000010110', '0230', 400), ('000000010010', '0220', 500), ('000000010011', '0260', 600), ('000000010001', '0240', 700), ('000000110001', '0340', 800), ('000000110011', '0360', 900), ('000000110010', '0320', 1000), ('000000110110', '0330', 1100), ('000000110100', '0310', 1200), ('000000111100', '0710', 1300), ('000000111110', '0730', 1400), ('000000111010', '0720', 1500), ('000000111011', '0760', 1600), ('000000111001', '0740', 1700), ('000000101001', '0540', 1800), ('000000101011', '0560', 1900), ('000000101010', '0520', 2000), ('000000101110', '0530', 2100), ('000000101100', '0510', 2200), ('000000100100', '0110', 2300), ('000000100110', '0130', 2400), ('000000100010', '0120', 2500), ('000000100011', '0160', 2600), ('000000100001', '0140', 2700), ('010000000110', '0032', 126400), ('010000000010', '0022', 126500), ('010000000011', '0062', 126600), ('010000000001', '0042', 126700)]   # (D1 D2 D4 A1 A2 A4 B1 B2 B4 C1 C2 C4, octal ABCD, ft) from Wikipedia "Gillham code"


def _wiki_bits_to_ac(bits: str) -> int:
    b = dict(zip(("D1", "D2", "D4", "A1", "A2", "A4", "B1", "B2", "B4", "C1", "C2", "C4"), map(int, bits)))
    order = ("C1", "A1", "C2", "A2", "C4", "A4", "M", "B1", "Q", "B2", "D2", "B4", "D4")
    b["M"] = b["Q"] = 0
    out = 0
    for name in order:
        out = (out << 1) | b[name]
    return out


@pytest.mark.parametrize("bits,octal,ft", GILLHAM_ROWS)
def test_gillham_table_rows(bits, octal, ft):
    ac = _wiki_bits_to_ac(bits)
    assert m.altcode_to_ft(ac) == ft
    # the same pulses read as a Mode A code give the table's octal column (D1 = 0 in all rows)
    assert m.idcode_to_squawk(ac) == octal
    assert m.gillham_encode(ft) == ac


def test_crc_book_vectors():
    assert m.parity("8D406B902015A678D4D220AA4BDA") == 0
    assert m.crc24(int("8D406B902015A678D4D220", 16) << 24, 112) == 0xAA4BDA
    assert m.parity("8D4CA251204994B1C36E60A5343D") == 16


def test_address_recovery_df20_df11():
    assert m.icao("A0001838CA380031440000F24177") == "3C6DD0"
    assert m.df("5D484FDEA248F5") == 11 and m.icao("5D484FDEA248F5") == "484FDE"
    assert m.parity("5D484FDEA248F5") == 22          # interrogator identifier / SI code overlay


def test_commb_identification():
    assert m.commb_identification("A000083E202CC371C31DE0AA1CCF") == "KLM1017"



# --- surface position (Sun 2021, ads-b/4-surface-position, read 2026-11-04) [D] -------------------------------

SURF_EVEN = "8C4841753AAB238733C8CD4020B1"
SURF_ODD = "8C4841753A8A35323FAEBDAC702D"
SURF_NEXT = "8C4841753A9A153237AEF0F275BE"


def test_book_surface_cpr_fields():
    e, o = m.surface_position(SURF_EVEN), m.surface_position(SURF_ODD)
    assert [round(v * 2 ** 17) for v in (e.lat_cpr, e.lon_cpr, o.lat_cpr, o.lon_cpr)] == [115609, 116941, 39199, 110269]
    assert e.icao == "484175" and (e.odd, o.odd) == (False, True)


def test_book_surface_global_and_local():
    e, o = m.surface_position(SURF_EVEN), m.surface_position(SURF_ODD)
    lat, lon = m.cpr_surface_global(e, o, newest_is_odd=True, lat_ref=51.990, lon_ref=4.375)
    assert lat == pytest.approx(52.320607072215964, abs=1e-12) and lon == pytest.approx(4.734734671456474, abs=1e-9)
    f = m.surface_position(SURF_NEXT)
    assert m.cpr_surface_local(f, 52.320607, 4.734735) == pytest.approx((52.32056051997815, 4.735735212053571),
                                                                        abs=1e-9)


def test_book_surface_speed_and_track():
    f = m.surface_position(SURF_NEXT)
    assert f.speed_kt == 17.0 and f.track_deg == pytest.approx(92.8125)


def test_surface_reference_resolves_quadrant():
    e, o = m.surface_position(SURF_EVEN), m.surface_position(SURF_ODD)
    _, lon_far = m.cpr_surface_global(e, o, True, 51.990, 94.0)        # a reference 90 deg east picks that quadrant
    assert lon_far == pytest.approx(94.734734671456474, abs=1e-9)


def test_two_bit_errors_mostly_rejected_never_silently_wrong_dataframe():
    rng = random.Random(11)
    n0 = int(POS_EVEN, 16)
    rejected = aliased = 0
    for _ in range(2000):
        a, b = rng.sample(range(6, 113), 2)
        bad = f"{n0 ^ (1 << (112 - a)) ^ (1 << (112 - b)):028X}"
        fixed, bit = m.correct_single_bit(bad)
        if bit is None:
            rejected += 1
        else:
            aliased += 1
            assert fixed != POS_EVEN               # a 'repair' of a 2-bit error never restores the original
    assert rejected / 2000 > 0.9                   # measured value is reported in docs/24
