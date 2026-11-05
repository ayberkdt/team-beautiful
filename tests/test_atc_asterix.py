"""ASTERIX CAT048 encoder/decoder: hand-checked FSPEC, field layouts, round trip."""
import pytest

from aerokit.atc.asterix import Cat048Record, decode_block, encode_block, encode_record


def test_fspec_by_hand():
    # FRN 1-6 present -> 1111 1100 = 0xFC, no extension
    r = Cat048Record(time_of_day_s=0.0, typ=2, rho_nm=10, theta_deg=0, squawk="1200", flight_level=50)
    assert encode_record(r)[0] == 0xFC
    # FRN 1-6, 8, 9 -> first octet 0xFD (FX set), second octet 1100 0000 = 0xC0
    r2 = Cat048Record(time_of_day_s=0.0, typ=5, rho_nm=10, theta_deg=0, squawk="1200", flight_level=50,
                      address="4B1A23", callsign="BTL123")
    rec = encode_record(r2)
    assert rec[0] == 0xFD and rec[1] == 0xC0


def test_item_bytes_by_hand():
    r = Cat048Record(sac=0x19, sic=0x02, time_of_day_s=1.0, typ=2, rho_nm=1.0, theta_deg=90.0, squawk="7600",
                     flight_level=-1.0)
    rec = encode_record(r)
    assert rec[1:3] == bytes([0x19, 0x02])                 # SAC/SIC
    assert rec[3:6] == (128).to_bytes(3, "big")            # 1 s = 128 x 1/128 s
    assert rec[6] == 0b0100_0000                           # TYP = 2 (single SSR) in bits 8-6
    assert rec[7:11] == bytes([0x01, 0x00, 0x40, 0x00])    # RHO 256/256 NM, THETA 90 deg = 0x4000
    assert rec[11:13] == (0o7600).to_bytes(2, "big")
    assert rec[13:15] == (0x3FFC).to_bytes(2, "big")       # -4 quarter-FL in 14-bit two's complement


def test_round_trip_block():
    rs = [Cat048Record(sac=1, sic=2, time_of_day_s=43200.5, typ=5, spi=True, rho_nm=32.5, theta_deg=271.3,
                       squawk="4621", flight_level=57.25, address="4B1A23", callsign="BTL123", track_number=17,
                       ground_speed_kt=220.0, heading_deg=210.0),
          Cat048Record(typ=1, rho_nm=12.0, theta_deg=45.0)]
    blk = encode_block(rs)
    assert blk[0] == 48 and int.from_bytes(blk[1:3], "big") == len(blk)
    out = decode_block(blk)
    a = out[0]
    assert (a.sac, a.sic, a.typ, a.spi, a.squawk, a.address, a.callsign, a.track_number) == \
        (1, 2, 5, True, "4621", "4B1A23", "BTL123", 17)
    assert a.time_of_day_s == pytest.approx(43200.5, abs=1 / 128)
    assert a.rho_nm == pytest.approx(32.5, abs=1 / 256) and a.theta_deg == pytest.approx(271.3, abs=0.006)
    assert a.flight_level == pytest.approx(57.25) and a.ground_speed_kt == pytest.approx(220.0, abs=0.22)
    assert a.heading_deg == pytest.approx(210.0, abs=0.006)
    b = out[1]
    assert b.typ == 1 and b.squawk is None and b.callsign is None


def test_bad_inputs():
    with pytest.raises(ValueError):
        encode_record(Cat048Record(squawk="7800"))
    with pytest.raises(ValueError):
        decode_block(bytes([21, 0, 3]))



def test_cat021_fspec_and_round_trip():
    from aerokit.atc.asterix import Cat021Record, decode_cat021_block, encode_cat021_block, encode_cat021_record
    r = Cat021Record(sac=1, sic=2, track_number=17, time_pos_s=3600.25, lat=-33.9425, lon=151.1751,
                     address="7C1234", squawk="1200", flight_level=-12.5, ground_speed_kt=145.0,
                     track_angle_deg=342.0, callsign="QFA12")
    rec = encode_cat021_record(r)
    # FSPEC octet k holds FRN 7k+1..7k+7 in bits 8..2, bit 1 = FX:
    # FRN 1,2,3,5,6 -> 1110 110|1 ; FRN 11 -> 0001 000|1 ; FRN 19,21 -> 0000 101|1 ; FRN 26 -> 0000 100|1 ; FRN 29 -> 1000 000|0
    assert rec[:5] == bytes([0b11101101, 0b00010001, 0b00001011, 0b00001001, 0b10000000])
    out = decode_cat021_block(encode_cat021_block([r]))[0]
    assert (out.sac, out.sic, out.track_number, out.address, out.squawk, out.callsign) == (1, 2, 17, "7C1234",
                                                                                          "1200", "QFA12")
    assert out.lat == pytest.approx(-33.9425, abs=180 / 2 ** 23) and out.lon == pytest.approx(151.1751, abs=180 / 2 ** 23)
    assert out.flight_level == pytest.approx(-12.5) and out.ground_speed_kt == pytest.approx(145.0, abs=0.22)
    assert out.track_angle_deg == pytest.approx(342.0, abs=0.006) and out.time_pos_s == pytest.approx(3600.25)


def test_cat021_negative_coordinates_twos_complement():
    from aerokit.atc.asterix import Cat021Record, encode_cat021_record
    rec = encode_cat021_record(Cat021Record(lat=-90.0, lon=-180.0))
    # FSPEC: FRN 1,2,6 -> 0b11000100 ; then 010 (2 octets), 040 (1), 130 (6)
    assert rec[0] == 0b11000100
    lat = rec[4:7]
    assert lat == (-(1 << 22) & 0xFFFFFF).to_bytes(3, "big")         # -90 deg = -2^22 LSB
