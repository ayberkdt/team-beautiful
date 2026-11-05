"""Mode S and ADS-B (1090 MHz extended squitter) decoding and encoding.

This is the "translate signal" layer for surveillance data: a 56- or 112-bit reply becomes a callsign, an altitude,
a squawk, a position or a velocity. Everything is pure Python on hex strings.

Bit numbering follows Sun (2021): bit 1 is the most significant bit of the message. A 112-bit extended squitter is
DF (1-5) | CA (6-8) | ICAO address (9-32) | ME (33-88) | parity PI (89-112). In DF4/5/20/21 the last 24 bits are
address/parity: CRC of the data XOR the aircraft address, so the CRC remainder of the whole message *is* the
address (no address is transmitted in clear).

Validated in ``tests/test_atc_modes.py`` against the worked examples printed in Sun (2021) and, independently,
against pyModeS 3.6.1 where it is installed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit.references import cite

__all__ = [
    "CHARSET", "crc24", "parity", "is_valid", "correct_single_bit", "df", "icao", "typecode", "me_field",
    "callsign", "altcode_to_ft", "alt12_to_ft", "idcode_to_squawk", "squawk_to_idcode", "gillham_encode",
    "ft_to_alt12", "cpr_nl", "AirbornePosition", "airborne_position", "cpr_global", "cpr_local", "cpr_encode",
    "Velocity", "airborne_velocity", "surveillance_altitude", "surveillance_squawk", "encode_df17",
    "encode_identification", "encode_position", "encode_velocity", "encode_df4", "encode_df5", "decode",
    "commb_identification", "SurfacePosition", "surface_position", "cpr_surface_global", "cpr_surface_local",
]

#: 6-bit AIS character set used by TC 1-4 identification messages (index = 6-bit value).
CHARSET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######"
_GENERATOR = 0x1FFF409        # x^24 + ... (25 bits); Mode S CRC-24


def _bits(msg: str) -> int:
    return len(msg) * 4


def _int(msg: str) -> int:
    msg = msg.strip()
    if len(msg) not in (14, 28):
        raise ValueError(f"Mode S message must be 14 or 28 hex characters, got {len(msg)}")
    return int(msg, 16)


def _field(msg: str, first: int, last: int) -> int:
    """Bits ``first``..``last`` (1-based, inclusive) of the message as an integer."""
    n = _bits(msg)
    return (_int(msg) >> (n - last)) & ((1 << (last - first + 1)) - 1)


@cite("sun_2021_1090riddle", "sun_2020_pymodes", note="CRC-24 generator 0x1FFF409, remainder of the whole message")
def crc24(value: int, nbits: int) -> int:
    """Remainder of polynomial division of an ``nbits``-bit integer by the Mode S generator (24-bit result).

    For a valid DF17/18 the remainder of the whole 112-bit message is 0; for DF4/5/20/21 it equals the aircraft
    address (possibly overlaid).
    """
    rem = value
    for shift in range(nbits - 25, -1, -1):
        if rem >> (shift + 24) & 1:
            rem ^= _GENERATOR << shift
    return rem & 0xFFFFFF


def parity(msg: str) -> int:
    """CRC remainder of the full message (0 for an error-free extended squitter)."""
    return crc24(_int(msg), _bits(msg))


def is_valid(msg: str) -> bool:
    """True if a DF17/18 message passes the CRC (remainder 0)."""
    return parity(msg) == 0


_SYNDROMES: dict[int, dict[int, int]] = {}


def _syndrome_table(nbits: int) -> dict[int, int]:
    if nbits not in _SYNDROMES:
        # flipping bit k (1-based) changes the remainder by crc24(1 << (nbits - k)); DF bits 1-5 are excluded so a
        # corrected message never changes format.
        _SYNDROMES[nbits] = {crc24(1 << (nbits - k), nbits): k for k in range(6, nbits + 1)}
    return _SYNDROMES[nbits]


def correct_single_bit(msg: str) -> tuple[str, int | None]:
    """Repair one flipped bit in a DF17/18 message using the CRC syndrome.

    Returns ``(message, bit)`` where ``bit`` is the 1-based position that was flipped, 0 if the message was
    already valid, or ``None`` if it cannot be repaired by a single-bit flip (then the message is returned
    unchanged and must be discarded).
    """
    n = _bits(msg)
    syn = parity(msg)
    if syn == 0:
        return msg, 0
    k = _syndrome_table(n).get(syn)
    if k is None:
        return msg, None
    fixed = _int(msg) ^ (1 << (n - k))
    return f"{fixed:0{len(msg)}X}", k


def df(msg: str) -> int:
    """Downlink format (bits 1-5; DF >= 24 all mean Comm-D and read as 24)."""
    v = _field(msg, 1, 5)
    return 24 if v >= 24 else v


def icao(msg: str) -> str:
    """24-bit aircraft address as 6 hex characters.

    DF11/17/18 carry it in bits 9-32; DF0/4/5/16/20/21 hide it in the address/parity field, recovered as the CRC
    remainder.
    """
    d = df(msg)
    if d in (11, 17, 18):
        return f"{_field(msg, 9, 32):06X}"
    if d in (0, 4, 5, 16, 20, 21):
        return f"{parity(msg):06X}"
    raise ValueError(f"no address recoverable from DF{d}")


def me_field(msg: str) -> int:
    """56-bit ME field of an extended squitter."""
    if df(msg) not in (17, 18):
        raise ValueError("ME field exists only in DF17/18")
    return _field(msg, 33, 88)


def typecode(msg: str) -> int:
    """ADS-B type code (first 5 bits of ME)."""
    return me_field(msg) >> 51


def _me_bits(me: int, first: int, last: int) -> int:
    return (me >> (56 - last)) & ((1 << (last - first + 1)) - 1)


@cite("sun_2021_1090riddle", note="Aircraft identification, TC 1-4, 8 x 6-bit characters")
def callsign(msg: str) -> str:
    """Callsign from a TC 1-4 identification message (trailing spaces and '#' fillers removed)."""
    tc = typecode(msg)
    if not 1 <= tc <= 4:
        raise ValueError(f"TC {tc} is not an identification message")
    me = me_field(msg)
    chars = "".join(CHARSET[_me_bits(me, 9 + 6 * i, 14 + 6 * i)] for i in range(8))
    return chars.replace("#", "").strip()


# --- altitude and identity codes ---------------------------------------------------------------------------

def _gray_to_int(n: int) -> int:
    out = 0
    while n:
        out ^= n
        n >>= 1
    return out


@cite("sun_2021_1090riddle", "sun_2020_pymodes", note="AC field C1 A1 C2 A2 C4 A4 M B1 Q B2 D2 B4 D4; Gillham rules")
def altcode_to_ft(ac: int) -> int | None:
    """Decode a 13-bit altitude code (DF0/4/16/20 AC field) to feet; ``None`` if unavailable or invalid.

    Q = 1: 25 ft steps, ``25 N - 1000``. Q = 0: Gillham (100 ft steps): bits re-ordered to
    D2 D4 A1 A2 A4 B1 B2 B4 | C1 C2 C4, both groups Gray-decoded, N100 in {0, 5, 6} invalid, 7 -> 5, odd N500
    reverses N100, ``500 N500 + 100 N100 - 1300``. M = 1 (metric) is returned as ``None``.
    """
    if not 0 <= ac < 1 << 13:
        raise ValueError("AC field is 13 bits")
    if ac == 0:
        return None
    m_bit = (ac >> 6) & 1
    q_bit = (ac >> 4) & 1
    if m_bit:
        return None
    if q_bit:
        n = ((ac >> 2) & 0x7E0) | ((ac >> 1) & 0x10) | (ac & 0xF)
        return 25 * n - 1000

    def b(pos: int) -> int:                 # pos 0..12, MSB first
        return (ac >> (12 - pos)) & 1

    c1, a1, c2, a2, c4, a4, b1, b2, d2, b4, d4 = (b(0), b(1), b(2), b(3), b(4), b(5), b(7), b(9), b(10),
                                                   b(11), b(12))
    g500 = (d2 << 7) | (d4 << 6) | (a1 << 5) | (a2 << 4) | (a4 << 3) | (b1 << 2) | (b2 << 1) | b4
    g100 = (c1 << 2) | (c2 << 1) | c4
    n500, n100 = _gray_to_int(g500), _gray_to_int(g100)
    if n100 in (0, 5, 6):
        return None
    if n100 == 7:
        n100 = 5
    if n500 % 2:
        n100 = 6 - n100
    return 500 * n500 + 100 * n100 - 1300


def alt12_to_ft(alt12: int) -> int | None:
    """Decode the 12-bit ADS-B altitude (TC 9-18): the 13-bit AC code without the M bit."""
    ac = ((alt12 & 0xFC0) << 1) | (alt12 & 0x3F)       # insert M = 0 between A4 and B1
    return altcode_to_ft(ac)


def _gillham_table() -> dict[int, int]:
    table: dict[int, int] = {}
    for code in range(1 << 13):
        if (code >> 6) & 1 or (code >> 4) & 1:      # M = 0, Q = 0 only
            continue
        alt = altcode_to_ft(code)
        if alt is not None and alt not in table:
            table[alt] = code
    return table


_GILLHAM: dict[int, int] | None = None


def gillham_encode(alt_ft: int) -> int:
    """13-bit Gillham AC code (M = Q = 0) for an altitude that is a multiple of 100 ft (-1000 ... 126 700 ft).

    Built by inverting :func:`altcode_to_ft` over all codes, so encoding and decoding cannot disagree.
    """
    global _GILLHAM
    if _GILLHAM is None:
        _GILLHAM = _gillham_table()
    if alt_ft not in _GILLHAM:
        raise ValueError(f"{alt_ft} ft has no Gillham code (needs a multiple of 100 ft in range)")
    return _GILLHAM[alt_ft]


def ft_to_alt12(alt_ft: float) -> int:
    """12-bit ADS-B altitude field with Q = 1 (25 ft resolution)."""
    n = int(round((alt_ft + 1000) / 25))
    if not 0 <= n < 1 << 11:
        raise ValueError("altitude outside the 25 ft code range")
    # 11-bit n -> 12 bits with Q (bit 8 of 12, value 0x10) set
    return ((n & 0x7F0) << 1) | 0x10 | (n & 0xF)


_ID_ORDER = ("C1", "A1", "C2", "A2", "C4", "A4", "X", "B1", "D1", "B2", "D2", "B4", "D4")


@cite("sun_2021_1090riddle", note="identity code C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4 -> A4A2A1 B4B2B1 C4C2C1 D4D2D1")
def idcode_to_squawk(ident: int) -> str:
    """Four octal digits (Mode A code / squawk) from a 13-bit identity field."""
    bits = {name: (ident >> (12 - i)) & 1 for i, name in enumerate(_ID_ORDER)}
    digits = []
    for letter in "ABCD":
        digits.append(str(4 * bits[f"{letter}4"] + 2 * bits[f"{letter}2"] + bits[f"{letter}1"]))
    return "".join(digits)


def squawk_to_idcode(squawk: str) -> int:
    """Inverse of :func:`idcode_to_squawk` (X = 0)."""
    if len(squawk) != 4 or any(ch not in "01234567" for ch in squawk):
        raise ValueError(f"squawk must be four octal digits, got {squawk!r}")
    bits = {"X": 0}
    for letter, ch in zip("ABCD", squawk):
        v = int(ch)
        bits[f"{letter}4"], bits[f"{letter}2"], bits[f"{letter}1"] = (v >> 2) & 1, (v >> 1) & 1, v & 1
    out = 0
    for name in _ID_ORDER:
        out = (out << 1) | bits[name]
    return out


def surveillance_altitude(msg: str) -> int | None:
    """Altitude [ft] from a DF0/4/16/20 reply (AC field, bits 20-32)."""
    if df(msg) not in (0, 4, 16, 20):
        raise ValueError("altitude reply must be DF0/4/16/20")
    return altcode_to_ft(_field(msg, 20, 32))


def surveillance_squawk(msg: str) -> str:
    """Squawk from a DF5/21 identity reply (ID field, bits 20-32)."""
    if df(msg) not in (5, 21):
        raise ValueError("identity reply must be DF5/21")
    return idcode_to_squawk(_field(msg, 20, 32))


@cite("sun_2021_1090riddle", note="Comm-B BDS 2,0: MB starts 0x20, then 8 six-bit characters")
def commb_identification(msg: str) -> str | None:
    """Callsign from a DF20/21 Comm-B reply carrying BDS 2,0 (``None`` if the MB field is not BDS 2,0).

    The aircraft address is not checked here (it is in the address/parity field, :func:`icao`).
    """
    if df(msg) not in (20, 21) or _bits(msg) != 112:
        raise ValueError("Comm-B identification needs a 112-bit DF20/21 reply")
    mb = _field(msg, 33, 88)
    if mb >> 48 != 0x20:
        return None
    chars = "".join(CHARSET[_me_bits(mb, 9 + 6 * i, 14 + 6 * i)] for i in range(8))
    if "#" in chars:
        return None
    return chars.strip()


# --- CPR position ------------------------------------------------------------------------------------------

NZ = 15
_CPR_SCALE = 1 << 17


@cite("sun_2021_1090riddle", note="NL(lat) = floor(2 pi / acos(1 - (1 - cos(pi/(2 NZ))) / cos^2(pi lat / 180))), NZ = 15")
def cpr_nl(lat: float) -> int:
    """Number of longitude zones at a latitude (1 ... 59)."""
    if abs(lat) >= 87.0:
        return 2 if abs(lat) == 87.0 else 1
    if lat == 0.0:
        return 59
    a = 1.0 - math.cos(math.pi / (2 * NZ))
    b = math.cos(math.pi * abs(lat) / 180.0) ** 2
    return int(math.floor(2 * math.pi / math.acos(1.0 - a / b)))


@dataclass(frozen=True)
class AirbornePosition:
    """Raw fields of a TC 9-18 airborne position message."""

    icao: str
    typecode: int
    altitude_ft: int | None
    odd: bool
    lat_cpr: float           # fraction 0..1
    lon_cpr: float


def airborne_position(msg: str) -> AirbornePosition:
    """Parse the raw CPR fields and barometric altitude of a TC 9-18 message."""
    tc = typecode(msg)
    if not 9 <= tc <= 18:
        raise ValueError(f"TC {tc} is not a barometric airborne position")
    me = me_field(msg)
    return AirbornePosition(icao(msg), tc, alt12_to_ft(_me_bits(me, 9, 20)), bool(_me_bits(me, 22, 22)),
                            _me_bits(me, 23, 39) / _CPR_SCALE, _me_bits(me, 40, 56) / _CPR_SCALE)


def _mod(x: float, y: float) -> float:
    return x - y * math.floor(x / y)


@cite("sun_2021_1090riddle", note="globally unambiguous decoding from an even/odd pair, j and m indices")
def cpr_global(even: AirbornePosition, odd: AirbornePosition, newest_is_odd: bool) -> tuple[float, float] | None:
    """Globally unambiguous position from one even and one odd frame.

    Returns ``None`` if the two frames straddle a longitude-zone boundary (NL differs): then wait for another pair.
    The frames must be close in time (the book uses 10 s); the caller enforces that.
    """
    if even.odd or not odd.odd:
        raise ValueError("need one even (F=0) and one odd (F=1) frame")
    dlat_e, dlat_o = 360.0 / 60, 360.0 / 59
    j = math.floor(59 * even.lat_cpr - 60 * odd.lat_cpr + 0.5)
    lat_e = dlat_e * (_mod(j, 60) + even.lat_cpr)
    lat_o = dlat_o * (_mod(j, 59) + odd.lat_cpr)
    if lat_e >= 270:
        lat_e -= 360
    if lat_o >= 270:
        lat_o -= 360
    if cpr_nl(lat_e) != cpr_nl(lat_o):
        return None
    if newest_is_odd:
        lat, nl = lat_o, cpr_nl(lat_o)
        ni = max(nl - 1, 1)
        m = math.floor(even.lon_cpr * (nl - 1) - odd.lon_cpr * nl + 0.5)
        lon = (360.0 / ni) * (_mod(m, ni) + odd.lon_cpr)
    else:
        lat, nl = lat_e, cpr_nl(lat_e)
        ni = max(nl, 1)
        m = math.floor(even.lon_cpr * (nl - 1) - odd.lon_cpr * nl + 0.5)
        lon = (360.0 / ni) * (_mod(m, ni) + even.lon_cpr)
    if lon >= 180:
        lon -= 360
    return lat, lon


@cite("sun_2021_1090riddle", note="locally unambiguous decoding with a reference within ~180 NM")
def cpr_local(frame: AirbornePosition, lat_ref: float, lon_ref: float) -> tuple[float, float]:
    """Position from a single frame and a nearby reference (receiver site or last track position)."""
    i = 1 if frame.odd else 0
    dlat = 360.0 / (60 - i)
    j = math.floor(lat_ref / dlat) + math.floor(_mod(lat_ref, dlat) / dlat - frame.lat_cpr + 0.5)
    lat = dlat * (j + frame.lat_cpr)
    nl = cpr_nl(lat)
    dlon = 360.0 / max(nl - i, 1)
    m = math.floor(lon_ref / dlon) + math.floor(_mod(lon_ref, dlon) / dlon - frame.lon_cpr + 0.5)
    return lat, dlon * (m + frame.lon_cpr)


def cpr_encode(lat: float, lon: float, odd: bool) -> tuple[int, int]:
    """17-bit airborne CPR (YZ, XZ) for a position.

    Written as the inverse of :func:`cpr_local`/:func:`cpr_global` (the encoding equations were not read from the
    standard in this session); correctness is shown by round trips in the tests, including reproducing the
    book's printed CPR values to within one count.
    """
    i = 1 if odd else 0
    dlat = 360.0 / (60 - i)
    yz = math.floor(_CPR_SCALE * _mod(lat, dlat) / dlat + 0.5)
    rlat = dlat * (yz / _CPR_SCALE + math.floor(lat / dlat))
    nl = cpr_nl(rlat)
    dlon = 360.0 / (nl - i) if nl - i > 0 else 360.0
    xz = math.floor(_CPR_SCALE * _mod(lon, dlon) / dlon + 0.5)
    return yz % _CPR_SCALE, xz % _CPR_SCALE



# --- surface position (TC 5-8) ---------------------------------------------------------------------------------

@dataclass(frozen=True)
class SurfacePosition:
    """Raw fields of a TC 5-8 surface position message."""

    icao: str
    typecode: int
    speed_kt: float | None        # from the MOV code (None = not available / reserved)
    track_deg: float | None       # None if the ground track status bit is 0
    odd: bool
    lat_cpr: float
    lon_cpr: float


def _movement_kt(mov: int) -> float | None:
    """MOV code -> ground speed [kt], lower edge of each quantisation band (Sun 2021 surface-position table)."""
    if mov == 0 or mov >= 125:
        return None
    if mov == 1:
        return 0.0
    for lo, hi, v0, step in ((2, 8, 0.125, 0.125), (9, 12, 1.0, 0.25), (13, 38, 2.0, 0.5), (39, 93, 15.0, 1.0),
                             (94, 108, 70.0, 2.0), (109, 123, 100.0, 5.0)):
        if lo <= mov <= hi:
            return v0 + (mov - lo) * step
    return 175.0                              # 124: >= 175 kt


@cite("sun_2021_1090riddle", note="surface position: MOV, ground track 360 n / 128, CPR with 90-degree zones")
def surface_position(msg: str) -> SurfacePosition:
    """Parse a TC 5-8 surface position message."""
    tc = typecode(msg)
    if not 5 <= tc <= 8:
        raise ValueError(f"TC {tc} is not a surface position")
    me = me_field(msg)
    trk = _me_bits(me, 14, 20) * 360.0 / 128 if _me_bits(me, 13, 13) else None
    return SurfacePosition(icao(msg), tc, _movement_kt(_me_bits(me, 6, 12)), trk, bool(_me_bits(me, 22, 22)),
                           _me_bits(me, 23, 39) / _CPR_SCALE, _me_bits(me, 40, 56) / _CPR_SCALE)


def _closest_lon(lon0: float, lon_ref: float) -> float:
    cands = [((lon0 + k * 90.0 + 180.0) % 360.0) - 180.0 for k in range(4)]
    return min(cands, key=lambda c: abs(((c - lon_ref + 180.0) % 360.0) - 180.0))


@cite("sun_2021_1090riddle", note="surface global decoding: 90-degree zones, north/south and 4 longitude candidates")
def cpr_surface_global(even: SurfacePosition, odd: SurfacePosition, newest_is_odd: bool, lat_ref: float,
                       lon_ref: float) -> tuple[float, float] | None:
    """Surface position from an even/odd pair; the reference (e.g. the airport, within 45 NM) resolves the
    north/south and 90-degree longitude ambiguities. ``None`` if the frames straddle a zone boundary."""
    if even.odd or not odd.odd:
        raise ValueError("need one even (F=0) and one odd (F=1) frame")
    dlat_e, dlat_o = 90.0 / 60, 90.0 / 59
    j = math.floor(59 * even.lat_cpr - 60 * odd.lat_cpr + 0.5)
    lat_e = dlat_e * (_mod(j, 60) + even.lat_cpr)
    lat_o = dlat_o * (_mod(j, 59) + odd.lat_cpr)
    lat_n = lat_o if newest_is_odd else lat_e
    lat = min((lat_n, lat_n - 90.0), key=lambda c: abs(c - lat_ref))
    if cpr_nl(lat_e) != cpr_nl(lat_o):
        return None
    nl = cpr_nl(lat)
    m = math.floor(even.lon_cpr * (nl - 1) - odd.lon_cpr * nl + 0.5)
    if newest_is_odd:
        ni = max(nl - 1, 1)
        lon0 = (90.0 / ni) * (_mod(m, ni) + odd.lon_cpr)
    else:
        ni = max(nl, 1)
        lon0 = (90.0 / ni) * (_mod(m, ni) + even.lon_cpr)
    return lat, _closest_lon(lon0, lon_ref)


@cite("sun_2021_1090riddle", note="surface local decoding, dLat = 90/(60 - i), reference within 45 NM")
def cpr_surface_local(frame: SurfacePosition, lat_ref: float, lon_ref: float) -> tuple[float, float]:
    """Surface position from one frame and a reference within 45 NM."""
    i = 1 if frame.odd else 0
    dlat = 90.0 / (60 - i)
    j = math.floor(lat_ref / dlat) + math.floor(_mod(lat_ref, dlat) / dlat - frame.lat_cpr + 0.5)
    lat = dlat * (j + frame.lat_cpr)
    dlon = 90.0 / max(cpr_nl(lat) - i, 1)
    m = math.floor(lon_ref / dlon) + math.floor(_mod(lon_ref, dlon) / dlon - frame.lon_cpr + 0.5)
    return lat, dlon * (m + frame.lon_cpr)


# --- velocity ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Velocity:
    """Decoded TC 19 airborne velocity."""

    icao: str
    subtype: int
    speed_kt: float | None
    angle_deg: float | None          # track (subtypes 1-2) or magnetic heading (3-4)
    vertical_rate_fpm: int | None
    speed_type: str                  # "GS", "IAS" or "TAS"
    vr_source: str                   # "GNSS" or "BARO"


@cite("sun_2021_1090riddle", note="TC 19 subtypes 1-4: Vx = +-(Vew - 1), Vy = +-(Vns - 1), VS = 64 (VR - 1)")
def airborne_velocity(msg: str) -> Velocity:
    """Decode a TC 19 airborne velocity message."""
    if typecode(msg) != 19:
        raise ValueError("not a TC 19 velocity message")
    me = me_field(msg)
    st = _me_bits(me, 6, 8)
    vr_raw, s_vr = _me_bits(me, 38, 46), _me_bits(me, 37, 37)
    vrate = None if vr_raw == 0 else (-1 if s_vr else 1) * 64 * (vr_raw - 1)
    src = "BARO" if _me_bits(me, 36, 36) else "GNSS"
    if st in (1, 2):
        mult = 4 if st == 2 else 1
        s_ew, v_ew = _me_bits(me, 14, 14), _me_bits(me, 15, 24)
        s_ns, v_ns = _me_bits(me, 25, 25), _me_bits(me, 26, 35)
        if v_ew == 0 or v_ns == 0:
            return Velocity(icao(msg), st, None, None, vrate, "GS", src)
        vx = mult * (v_ew - 1) * (-1 if s_ew else 1)
        vy = mult * (v_ns - 1) * (-1 if s_ns else 1)
        spd = math.hypot(vx, vy)
        trk = math.degrees(math.atan2(vx, vy)) % 360.0
        return Velocity(icao(msg), st, spd, trk, vrate, "GS", src)
    if st in (3, 4):
        mult = 4 if st == 4 else 1
        hdg = _me_bits(me, 15, 24) * 360.0 / 1024 if _me_bits(me, 14, 14) else None
        as_raw = _me_bits(me, 26, 35)
        airspeed: float | None = None if as_raw == 0 else float(mult * (as_raw - 1))
        return Velocity(icao(msg), st, airspeed, hdg, vrate, "TAS" if _me_bits(me, 25, 25) else "IAS", src)
    raise ValueError(f"velocity subtype {st} not defined")


# --- encoding (for synthetic traffic) ------------------------------------------------------------------------

def encode_df17(icao_hex: str, me: int, ca: int = 5, df_value: int = 17) -> str:
    """Assemble a 112-bit DF17/18 message with correct CRC parity."""
    addr = int(icao_hex, 16)
    if not 0 <= addr < 1 << 24 or not 0 <= me < 1 << 56:
        raise ValueError("address 24 bits, ME 56 bits")
    data = (df_value << 83) | (ca << 80) | (addr << 56) | me
    pi = crc24(data << 24, 112)
    return f"{(data << 24) | pi:028X}"


def encode_identification(icao_hex: str, cs: str, tc: int = 4, category: int = 0) -> str:
    """TC 1-4 identification message for a callsign of up to 8 characters (A-Z, 0-9, space)."""
    cs = cs.upper().ljust(8)[:8]
    me = (tc << 51) | (category << 48)
    for i, ch in enumerate(cs):
        idx = CHARSET.find(ch) if ch != " " else 32
        if idx < 0 or ch == "#":
            raise ValueError(f"character {ch!r} not in the ADS-B set")
        me |= idx << (42 - 6 * i)
    return encode_df17(icao_hex, me)


def encode_position(icao_hex: str, lat: float, lon: float, alt_ft: float, odd: bool, tc: int = 11) -> str:
    """TC 9-18 airborne position (Q = 1 altitude, surveillance status 0, time bit 0)."""
    yz, xz = cpr_encode(lat, lon, odd)
    me = (tc << 51) | (ft_to_alt12(alt_ft) << 36) | (int(odd) << 34) | (yz << 17) | xz
    return encode_df17(icao_hex, me)


def encode_velocity(icao_hex: str, ground_speed_kt: float, track_deg: float, vertical_rate_fpm: float) -> str:
    """TC 19 subtype 1 (subsonic ground speed) message, GNSS vertical-rate source, no GNSS-baro difference."""
    vx = ground_speed_kt * math.sin(math.radians(track_deg))
    vy = ground_speed_kt * math.cos(math.radians(track_deg))
    v_ew, v_ns = int(round(abs(vx))) + 1, int(round(abs(vy))) + 1
    vr = int(round(abs(vertical_rate_fpm) / 64)) + 1
    if max(v_ew, v_ns) > 1023 or vr > 511:
        raise ValueError("velocity outside subtype 1 range")
    me = ((19 << 51) | (1 << 48) | (int(vx < 0) << 42) | (v_ew << 32) | (int(vy < 0) << 31) | (v_ns << 21)
          | (int(vertical_rate_fpm < 0) << 19) | (vr << 10))
    return encode_df17(icao_hex, me)


def _encode_short(df_value: int, field13: int, icao_hex: str, fs: int = 0, dr: int = 0, um: int = 0) -> str:
    data = (df_value << 27) | (fs << 24) | (dr << 19) | (um << 13) | field13
    ap = crc24(data << 24, 56) ^ int(icao_hex, 16)
    return f"{(data << 24) | ap:014X}"


def encode_df4(icao_hex: str, alt_ft: int) -> str:
    """DF4 altitude reply (Gillham, 100 ft) with address/parity for ``icao_hex``."""
    return _encode_short(4, gillham_encode(alt_ft), icao_hex)


def encode_df5(icao_hex: str, squawk: str) -> str:
    """DF5 identity reply with address/parity for ``icao_hex``."""
    return _encode_short(5, squawk_to_idcode(squawk), icao_hex)


def decode(msg: str) -> dict:
    """Best-effort one-message decoder returning a flat dict (for the demo pipeline and the radar scope)."""
    out: dict = {"msg": msg.upper(), "df": df(msg)}
    d = out["df"]
    if d in (17, 18):
        fixed, bit = correct_single_bit(msg)
        out["crc_ok"] = bit == 0
        out["corrected_bit"] = bit if bit else None
        if bit is None:
            out["status"] = "CRC_FAIL"
            return out
        msg = fixed
        out["icao"] = icao(msg)
        tc = typecode(msg)
        out["tc"] = tc
        if 1 <= tc <= 4:
            out["callsign"] = callsign(msg)
        elif 9 <= tc <= 18:
            p = airborne_position(msg)
            out.update(altitude_ft=p.altitude_ft, odd=p.odd, lat_cpr=p.lat_cpr, lon_cpr=p.lon_cpr)
        elif tc == 19:
            v = airborne_velocity(msg)
            out.update(speed_kt=v.speed_kt, track_deg=v.angle_deg, vertical_rate_fpm=v.vertical_rate_fpm,
                       speed_type=v.speed_type)
        out["status"] = "OK"
    elif d in (0, 4, 16, 20):
        out.update(icao=icao(msg), altitude_ft=surveillance_altitude(msg), status="OK (address from parity)")
    elif d in (5, 21):
        out.update(icao=icao(msg), squawk=surveillance_squawk(msg), status="OK (address from parity)")
    else:
        out["status"] = "UNSUPPORTED_DF"
    return out
