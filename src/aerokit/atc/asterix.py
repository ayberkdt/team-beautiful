"""ASTERIX Category 048 (monoradar target reports): encode and decode the items a radar plot carries.

This is how surveillance data actually travels from a radar station to the display system: a *data block*
``CAT (1 octet) | LEN (2 octets, whole block incl. CAT and LEN) | record | record ...``, each record starting with a
field specification (FSPEC) whose octets carry 7 presence bits for the items in User Application Profile order plus
an FX extension bit (EUROCONTROL SUR.ET1.ST05.2000-STD-04-01, Part 4, Ed. 1.15, sections 4.6-4.7 and the UAP table,
read 2026-11-04). Supported items (FRN in brackets):

========  =====  ==========================================================================================
I048/010  (1)    SAC, SIC                                                                         2 octets
I048/140  (2)    time of day, LSB 1/128 s                                                         3 octets
I048/020  (3)    target report descriptor, first part only: TYP, SIM, RDP, SPI, RAB               1 octet
I048/040  (4)    measured position, RHO LSB 1/256 NM, THETA LSB 360/2^16 deg                      4 octets
I048/070  (5)    Mode-3/A code: V, G, L, spare, 12 bits octal A4..D1                              2 octets
I048/090  (6)    flight level: V, G, 14 bits LSB 1/4 FL                                           2 octets
I048/220  (8)    24-bit aircraft address                                                          3 octets
I048/240  (9)    aircraft identification, 8 x 6-bit characters                                    6 octets
I048/161  (11)   track number (12 bits)                                                           2 octets
I048/200  (13)   ground speed LSB 2^-14 NM/s, heading LSB 360/2^16 deg                            4 octets
========  =====  ==========================================================================================

The flight level is written in two's complement for negative values (our assumption [Y]; the note giving the
allowed range was cut in the extracted text).
"""
from __future__ import annotations

from dataclasses import dataclass

from aerokit.atc.modes import CHARSET, idcode_to_squawk, squawk_to_idcode
from aerokit.references import cite

__all__ = ["Cat048Record", "encode_block", "decode_block", "TYP"]

TYP = {0: "no detection", 1: "single PSR", 2: "single SSR", 3: "SSR + PSR", 4: "Mode S all-call",
       5: "Mode S roll-call", 6: "Mode S all-call + PSR", 7: "Mode S roll-call + PSR"}


@dataclass
class Cat048Record:
    """One monoradar target report. ``None`` fields are not transmitted."""

    sac: int = 0
    sic: int = 1
    time_of_day_s: float | None = None
    typ: int | None = None               # see TYP
    simulated: bool = False
    spi: bool = False
    rho_nm: float | None = None
    theta_deg: float | None = None
    squawk: str | None = None            # four octal digits
    squawk_garbled: bool = False
    squawk_not_validated: bool = False
    flight_level: float | None = None    # FL (100 ft)
    address: str | None = None           # 6 hex characters
    callsign: str | None = None
    track_number: int | None = None
    ground_speed_kt: float | None = None
    heading_deg: float | None = None


_ORDER = (1, 2, 3, 4, 5, 6, 8, 9, 11, 13)       # FRNs this module writes


def _fspec(frns: list[int]) -> bytes:
    n_oct = (max(frns) - 1) // 7 + 1
    out = bytearray(n_oct)
    for f in frns:
        k, pos = divmod(f - 1, 7)
        out[k] |= 0x80 >> pos
    for k in range(n_oct - 1):
        out[k] |= 0x01
    return bytes(out)


def _encode_callsign(cs: str) -> bytes:
    cs = cs.upper().ljust(8)[:8]
    v = 0
    for ch in cs:
        idx = 32 if ch == " " else CHARSET.find(ch)
        if idx < 0 or ch == "#":
            raise ValueError(f"character {ch!r} not encodable")
        v = (v << 6) | idx
    return v.to_bytes(6, "big")


@cite("eurocontrol_asterix_cat048_2007", note="data block CAT/LEN/FSPEC, UAP FRN 1-13, item layouts and LSBs")
def encode_record(r: Cat048Record) -> bytes:
    """One CAT048 record (FSPEC + items), without CAT/LEN."""
    items: dict[int, bytes] = {1: bytes([r.sac & 0xFF, r.sic & 0xFF])}
    if r.time_of_day_s is not None:
        items[2] = (int(round(r.time_of_day_s * 128)) % (1 << 24)).to_bytes(3, "big")
    if r.typ is not None:
        items[3] = bytes([(r.typ & 7) << 5 | int(r.simulated) << 4 | int(r.spi) << 2])
    if r.rho_nm is not None and r.theta_deg is not None:
        rho = int(round(r.rho_nm * 256))
        if not 0 <= rho < 1 << 16:
            raise ValueError("RHO must be 0-256 NM")
        th = int(round((r.theta_deg % 360) * 65536 / 360)) % 65536
        items[4] = rho.to_bytes(2, "big") + th.to_bytes(2, "big")
    if r.squawk is not None:
        squawk_to_idcode(r.squawk)                  # raises on a non-octal squawk
        octal = int(r.squawk, 8)                    # I048/070 bits 12-1 = A4 A2 A1 B4 B2 B1 C4 C2 C1 D4 D2 D1
        items[5] = (int(r.squawk_not_validated) << 15 | int(r.squawk_garbled) << 14 | octal).to_bytes(2, "big")
    if r.flight_level is not None:
        q = int(round(r.flight_level * 4))
        if not -(1 << 13) <= q < 1 << 13:
            raise ValueError("flight level out of 14-bit range")
        items[6] = (q & 0x3FFF).to_bytes(2, "big")
    if r.address is not None:
        items[8] = int(r.address, 16).to_bytes(3, "big")
    if r.callsign is not None:
        items[9] = _encode_callsign(r.callsign)
    if r.track_number is not None:
        items[11] = (r.track_number & 0x0FFF).to_bytes(2, "big")
    if r.ground_speed_kt is not None and r.heading_deg is not None:
        gsp = int(round(r.ground_speed_kt / 3600 * (1 << 14)))
        hdg = int(round((r.heading_deg % 360) * 65536 / 360)) % 65536
        items[13] = gsp.to_bytes(2, "big") + hdg.to_bytes(2, "big")
    frns = sorted(items)
    return _fspec(frns) + b"".join(items[f] for f in frns)


def encode_block(records: list[Cat048Record]) -> bytes:
    """A CAT048 data block holding ``records``."""
    body = b"".join(encode_record(r) for r in records)
    n = 3 + len(body)
    if n > 0xFFFF:
        raise ValueError("data block too long")
    return bytes([48]) + n.to_bytes(2, "big") + body


_FIXED = {1: 2, 2: 3, 4: 4, 5: 2, 6: 2, 8: 3, 9: 6, 11: 2, 13: 4}


def decode_block(data: bytes) -> list[Cat048Record]:
    """Decode a CAT048 data block written with the supported items (unknown items raise ``ValueError``)."""
    if len(data) < 3 or data[0] != 48:
        raise ValueError("not a CAT048 data block")
    n = int.from_bytes(data[1:3], "big")
    if n != len(data):
        raise ValueError(f"LEN {n} does not match {len(data)} octets")
    i, out = 3, []
    while i < n:
        frns = []
        k = 0
        while True:
            b = data[i]
            for pos in range(7):
                if b & (0x80 >> pos):
                    frns.append(7 * k + pos + 1)
            i += 1
            k += 1
            if not b & 1:
                break
        r = Cat048Record()
        for f in frns:
            if f == 3:                            # variable length: first part + extents while FX
                b = data[i]
                r.typ, r.simulated, r.spi = b >> 5, bool(b & 0x10), bool(b & 0x04)
                while data[i] & 1:
                    i += 1
                i += 1
                continue
            if f not in _FIXED:
                raise ValueError(f"FRN {f} not supported by this decoder")
            chunk = data[i:i + _FIXED[f]]
            i += _FIXED[f]
            v = int.from_bytes(chunk, "big")
            if f == 1:
                r.sac, r.sic = chunk[0], chunk[1]
            elif f == 2:
                r.time_of_day_s = v / 128
            elif f == 4:
                r.rho_nm, r.theta_deg = (v >> 16) / 256, (v & 0xFFFF) * 360 / 65536
            elif f == 5:
                r.squawk_not_validated, r.squawk_garbled = bool(v >> 15 & 1), bool(v >> 14 & 1)
                r.squawk = f"{v & 0x0FFF:04o}"
            elif f == 6:
                q = v & 0x3FFF
                r.flight_level = (q - (1 << 14) if q & 0x2000 else q) / 4
            elif f == 8:
                r.address = f"{v:06X}"
            elif f == 9:
                r.callsign = "".join(CHARSET[(v >> (42 - 6 * c)) & 0x3F] for c in range(8)).replace("#", "").strip()
            elif f == 11:
                r.track_number = v & 0x0FFF
            elif f == 13:
                r.ground_speed_kt, r.heading_deg = (v >> 16) / (1 << 14) * 3600, (v & 0xFFFF) * 360 / 65536
        out.append(r)
    return out


def squawk_bits_consistent(squawk: str) -> bool:
    """The octal field of I048/070 and the Mode A identity code describe the same pulses (sanity helper)."""
    return idcode_to_squawk(squawk_to_idcode(squawk)) == squawk


__all__ += ["encode_record", "squawk_bits_consistent"]



# --- CAT021: ADS-B target reports (edition 2.7, 2025-07-02, zoranbosnjak/asterix-specs rendering, read 2026-11-04) ---

@dataclass
class Cat021Record:
    """ADS-B report items: FRN 1 (010), 2 (040, first octet), 3 (161), 5 (071), 6 (130), 11 (080), 19 (070),
    21 (145), 26 (160), 29 (170). ``None`` fields are not transmitted."""

    sac: int = 0
    sic: int = 1
    atp: int = 0                          # address type [Y: 0 assumed to mean 24-bit ICAO address]
    arc: int = 0                          # altitude reporting capability [Y]
    track_number: int | None = None
    time_pos_s: float | None = None       # time of applicability for position, 1/128 s
    lat: float | None = None              # WGS-84, LSB 180/2^23 deg, two's complement
    lon: float | None = None
    address: str | None = None
    squawk: str | None = None
    flight_level: float | None = None     # LSB 1/4 FL, two's complement, -15..1500 FL
    ground_speed_kt: float | None = None  # GS LSB 2^-14 NM/s (15 bits), RE bit if out of range
    track_angle_deg: float | None = None  # TA LSB 360/2^16
    callsign: str | None = None


def _s24(v: float, lsb: float) -> bytes:
    q = int(round(v / lsb))
    if not -(1 << 23) <= q < 1 << 23:
        raise ValueError("value out of 24-bit range")
    return (q & 0xFFFFFF).to_bytes(3, "big")


def _from_s(v: int, bits: int) -> int:
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


@cite("zoranbosnjak_asterix_specs_2026", note="CAT021 ed. 2.7 UAP and item layouts")
def encode_cat021_record(r: Cat021Record) -> bytes:
    items: dict[int, bytes] = {1: bytes([r.sac & 0xFF, r.sic & 0xFF]),
                               2: bytes([(r.atp & 7) << 5 | (r.arc & 3) << 3])}
    if r.track_number is not None:
        items[3] = (r.track_number & 0x0FFF).to_bytes(2, "big")
    if r.time_pos_s is not None:
        items[5] = (int(round(r.time_pos_s * 128)) % (1 << 24)).to_bytes(3, "big")
    if r.lat is not None and r.lon is not None:
        lsb = 180.0 / (1 << 23)
        items[6] = _s24(r.lat, lsb) + _s24(((r.lon + 180) % 360) - 180, lsb)
    if r.address is not None:
        items[11] = int(r.address, 16).to_bytes(3, "big")
    if r.squawk is not None:
        squawk_to_idcode(r.squawk)
        items[19] = int(r.squawk, 8).to_bytes(2, "big")
    if r.flight_level is not None:
        q = int(round(r.flight_level * 4))
        items[21] = (q & 0xFFFF).to_bytes(2, "big")
    if r.ground_speed_kt is not None and r.track_angle_deg is not None:
        gs = int(round(r.ground_speed_kt / 3600 * (1 << 14)))
        re = 0
        if gs >= 1 << 15:
            gs, re = (1 << 15) - 1, 1
        ta = int(round((r.track_angle_deg % 360) * 65536 / 360)) % 65536
        items[26] = ((re << 15) | gs).to_bytes(2, "big") + ta.to_bytes(2, "big")
    if r.callsign is not None:
        items[29] = _encode_callsign(r.callsign)
    frns = sorted(items)
    return _fspec(frns) + b"".join(items[f] for f in frns)


def encode_cat021_block(records: list[Cat021Record]) -> bytes:
    body = b"".join(encode_cat021_record(r) for r in records)
    return bytes([21]) + (3 + len(body)).to_bytes(2, "big") + body


_FIXED021 = {1: 2, 3: 2, 5: 3, 6: 6, 11: 3, 19: 2, 21: 2, 26: 4, 29: 6}


def decode_cat021_block(data: bytes) -> list[Cat021Record]:
    """Decode a CAT021 block written with the supported items (others raise ``ValueError``)."""
    if len(data) < 3 or data[0] != 21:
        raise ValueError("not a CAT021 data block")
    n = int.from_bytes(data[1:3], "big")
    if n != len(data):
        raise ValueError(f"LEN {n} does not match {len(data)} octets")
    i, out = 3, []
    lsb = 180.0 / (1 << 23)
    while i < n:
        frns, k = [], 0
        while True:
            b = data[i]
            frns += [7 * k + pos + 1 for pos in range(7) if b & (0x80 >> pos)]
            i += 1
            k += 1
            if not b & 1:
                break
        r = Cat021Record()
        for f in frns:
            if f == 2:
                b = data[i]
                r.atp, r.arc = b >> 5, (b >> 3) & 3
                while data[i] & 1:
                    i += 1
                i += 1
                continue
            if f not in _FIXED021:
                raise ValueError(f"FRN {f} not supported by this decoder")
            chunk = data[i:i + _FIXED021[f]]
            i += _FIXED021[f]
            v = int.from_bytes(chunk, "big")
            if f == 1:
                r.sac, r.sic = chunk[0], chunk[1]
            elif f == 3:
                r.track_number = v & 0x0FFF
            elif f == 5:
                r.time_pos_s = v / 128
            elif f == 6:
                r.lat = _from_s(v >> 24, 24) * lsb
                r.lon = _from_s(v & 0xFFFFFF, 24) * lsb
            elif f == 11:
                r.address = f"{v:06X}"
            elif f == 19:
                r.squawk = f"{v & 0x0FFF:04o}"
            elif f == 21:
                r.flight_level = _from_s(v, 16) / 4
            elif f == 26:
                r.ground_speed_kt = ((v >> 16) & 0x7FFF) / (1 << 14) * 3600
                r.track_angle_deg = (v & 0xFFFF) * 360 / 65536
            elif f == 29:
                r.callsign = "".join(CHARSET[(v >> (42 - 6 * c)) & 0x3F] for c in range(8)).replace("#", "").strip()
        out.append(r)
    return out


__all__ += ["Cat021Record", "encode_cat021_record", "encode_cat021_block", "decode_cat021_block"]
