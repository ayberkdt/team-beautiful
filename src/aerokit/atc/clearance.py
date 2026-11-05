"""ATC clearance parser: (ASR) text -> structured clearance with per-field confidence and ambiguity handling.

Design rules (safety, not style):

1. **Never upgrade confidence.** A field is ``CONFIRMED`` only if every word that produced it was heard with
   confidence >= ``hi``; one digit below ``lo`` masks that digit (``2?0``) and the value is not offered as a number.
2. **Never pick silently between readings.** If the n-best hypotheses (or a known homophone such as *two/to*,
   *four/for*) give different valid values for a safety-critical field, the field is ``AMBIGUOUS`` and lists the
   candidates; nothing is shown as "the" heading.
3. **Validate against phraseology and physics**: heading three digits 001-360, flight level three digits, squawk
   octal, frequency inside the VHF air band on a valid channel, QNH 900-1100 hPa, climb/descend direction vs current
   level. A failed check is ``INVALID`` with the reason.
4. **Callsign first.** An instruction addressed to another callsign is kept but marked ``NOT_FOR_US``.
5. Wind and other information ("wind two seven zero degrees") is parsed as information so its numbers can never be
   mistaken for an instruction.

The parser is deterministic and table-driven so its behaviour can be reviewed line by line; it is an advisory
prototype, not certified software.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any

from aerokit.references import cite

__all__ = ["Word", "Instruction", "Clearance", "tokenize", "parse", "parse_nbest", "readback_check",
           "ReadbackReport", "DIGITS", "NATO", "frequency_is_valid", "callsign_similarity", "DEFAULT_DESIGNATORS"]

DIGITS: Mapping[str, str] = {
    "zero": "0", "oh": "0", "one": "1", "wun": "1", "two": "2", "three": "3", "tree": "3",
    "four": "4", "fower": "4", "five": "5", "fife": "5", "six": "6", "seven": "7", "eight": "8", "ait": "8",
    "nine": "9", "niner": "9",
}
#: words an ASR may emit for a digit that are also ordinary words -> (digit, how suspicious)
HOMOPHONES: Mapping[str, str] = {"to": "2", "too": "2", "for": "4", "fore": "4", "won": "1", "ate": "8", "tu": "2"}
NATO: dict[str, str] = {w: w[0].upper() for w in (
    "alfa alpha bravo charlie delta echo foxtrot golf hotel india juliett juliet kilo lima mike november oscar papa "
    "quebec romeo sierra tango uniform victor whiskey xray yankee zulu").split()}
NATO["x-ray"] = "X"
#: synthetic telephony designators for the demo (real ones are not used: no verified table read in this session)
DEFAULT_DESIGNATORS: Mapping[str, str] = {"beetle": "BTL", "example": "EXA", "student": "STU", "nova": "NVA"}

CRITICAL = ("heading", "altitude", "flight_level", "speed", "squawk", "frequency", "qnh", "runway")


@dataclass(frozen=True)
class Word:
    """One recognised word with its recogniser confidence (1.0 for typed text)."""

    text: str
    conf: float = 1.0


@dataclass(frozen=True)
class Instruction:
    """One parsed element of a clearance."""

    kind: str                     # heading, altitude, flight_level, speed, squawk, frequency, qnh, runway, ...
    value: object                 # int / str / float, or None if not readable
    display: str                  # what a display may show, e.g. "HDG 270", "HDG 2?0"
    conf: float                   # min confidence of the words used
    status: str                   # CONFIRMED / LOW_CONFIDENCE / AMBIGUOUS / NOT_RECEIVED / INVALID / INFO
    words: str = ""               # the words that produced it
    detail: str = ""              # reason for a non-CONFIRMED status
    candidates: tuple = ()        # alternative values when AMBIGUOUS
    qualifier: str = ""           # e.g. "left", "right", "climb", "descend", "ILS", "land"


@dataclass(frozen=True)
class Clearance:
    """A parsed transmission."""

    callsign: str | None
    callsign_conf: float
    addressed_to_us: bool | None
    instructions: tuple[Instruction, ...]
    text: str
    unparsed: tuple[str, ...] = ()
    source: str = "VHF voice (ASR)"
    t_received: float | None = None
    msg_id: int | None = None
    partial: bool = False          # the audio monitor saw a dropout inside this transmission

    @property
    def status(self) -> str:
        """Worst instruction status (INFO ignored), or NOT_FOR_US / NO_CONTENT."""
        if self.addressed_to_us is False:
            return "NOT_FOR_US"
        order = ["CONFIRMED", "LOW_CONFIDENCE", "AMBIGUOUS", "NOT_RECEIVED", "INVALID"]
        st = [i.status for i in self.instructions if i.status != "INFO"]
        if not st:
            return "NO_CONTENT"
        return max(st, key=order.index)

    def get(self, kind: str) -> Instruction | None:
        for ins in self.instructions:
            if ins.kind == kind:
                return ins
        return None


# --- tokenising ---------------------------------------------------------------------------------------------

_NUMTOKEN = re.compile(r"^(fl)?(\d+)(?:[.,](\d+))?$")
#: token standing for audio the receiver did not get (dropout / blocked transmission); never a value
GAP = "<gap>"


def tokenize(text: str | Sequence[Word] | Sequence[tuple[str, float]]) -> list[Word]:
    """Normalise text or (word, confidence) pairs to lower-case :class:`Word` tokens.

    Numerals are split into digit tokens ("270" -> 2 7 0; "118.505" -> 1 1 8 decimal 5 0 5; "FL80" -> flight
    level 8 0) so typed text, ASR digits and spoken digits all go through the same path.
    """
    if isinstance(text, str):
        raw = [Word(w, 1.0) for w in re.split(r"[\s,;:!?]+", text.strip()) if w]
    else:
        raw = [w if isinstance(w, Word) else Word(str(w[0]), float(w[1])) for w in text]
    out: list[Word] = []
    for w in raw:
        if w.text.strip().lower() in ("<gap>", "[gap]", "<unk>", "..."):
            out.append(Word(GAP, 0.0))
            continue
        t = w.text.lower().strip(".'\"()")
        if not t:
            continue
        m = _NUMTOKEN.match(t)
        if m:
            if m.group(1):
                out += [Word("flight", w.conf), Word("level", w.conf)]
            out += [Word(d, w.conf) for d in m.group(2)]
            if m.group(3):
                out.append(Word("decimal", w.conf))
                out += [Word(d, w.conf) for d in m.group(3)]
            continue
        if t in ("ft", "feet"):
            t = "feet"
        if t in ("kts", "kt", "knot"):
            t = "knots"
        if t == "point":
            t = "decimal"
        t = {"descending": "descend", "climbing": "climb", "maintaining": "maintain"}.get(t, t)
        if t in ("x-ray",):
            t = "xray"
        out.append(Word(t, w.conf))
    return out


def _digit(w: Word, allow_homophones: bool) -> str | None:
    if w.text.isdigit() and len(w.text) == 1:
        return w.text
    if w.text in DIGITS:
        return DIGITS[w.text]
    if allow_homophones and w.text in HOMOPHONES:
        return HOMOPHONES[w.text]
    return None


@dataclass
class _Num:
    digits: list[str]
    confs: list[float]
    value: int
    n: int                         # tokens consumed
    words: str
    grouped: bool = False          # used "thousand"/"hundred"
    decimals: list[str] = field(default_factory=list)


def _read_number(toks: Sequence[Word], i: int, max_digits: int = 6, decimal: bool = False) -> _Num | None:
    """Read a spoken number at ``i``: digit-by-digit, optionally with thousand/hundred and a decimal part."""
    j = i
    digits: list[str] = []
    confs: list[float] = []
    value = 0
    grouped = False
    cur: list[str] = []
    while j < len(toks) and len(digits) < max_digits:
        d = _digit(toks[j], allow_homophones=False)
        if d is None:
            break
        cur.append(d)
        digits.append(d)
        confs.append(toks[j].conf)
        j += 1
        if j < len(toks) and toks[j].text in ("thousand", "hundred"):
            mult = 1000 if toks[j].text == "thousand" else 100
            value += int("".join(cur)) * mult
            confs.append(toks[j].conf)
            cur = []
            grouped = True
            j += 1
    if not digits:
        return None
    if cur:
        value = value + int("".join(cur)) if grouped else int("".join(cur))
    num = _Num(digits, confs, value, j - i, " ".join(t.text for t in toks[i:j]), grouped)
    if decimal and j < len(toks) and toks[j].text == "decimal":
        k = j + 1
        while k < len(toks) and len(num.decimals) < 3:
            d = _digit(toks[k], allow_homophones=False)
            if d is None:
                break
            num.decimals.append(d)
            num.confs.append(toks[k].conf)
            k += 1
        if num.decimals:
            num.confs.append(toks[j].conf)
            num.n = k - i
            num.words = " ".join(t.text for t in toks[i:k])
    return num


# --- validation -----------------------------------------------------------------------------------------------

@cite("icom_ica24_channels", note="25 kHz names .x00/.x25/.x50/.x75; 8.33 kHz names .x05/.x10/.x15 ...")
def frequency_is_valid(mhz_text: str) -> tuple[bool, str]:
    """VHF air-band voice channel check: 118.000-136.990 MHz, 25 kHz channel or 8.33 kHz channel *name*.

    8.33 kHz channel names end in .x05/.x10/.x15/.x30/.x35/.x40/.x55/.x60/.x65/.x80/.x85/.x90 and 25 kHz names in
    .x00/.x25/.x50/.x75 (Icom IC-A24 manual channel table for 118.000-118.105, read 2026-11-04; the pattern is
    assumed to repeat every 100 kHz).
    """
    try:
        f = float(mhz_text)
    except ValueError:
        return False, "not a number"
    if not 118.0 <= f <= 136.99 + 1e-9:
        return False, "outside 118.000-136.990 MHz"
    khz = int(round(f * 1000)) % 100
    if khz in (0, 25, 50, 75):
        return True, "25 kHz channel"
    if khz in (5, 10, 15, 30, 35, 40, 55, 60, 65, 80, 85, 90):
        return True, "8.33 kHz channel name"
    return False, "not a valid 25/8.33 kHz channel name"


@cite("icom_ica24_channels", note="118.010 -> 118.0083 MHz")
def channel_to_frequency(name: str) -> tuple[float, float]:
    """Operating frequency [MHz] and channel spacing [kHz] of a VHF channel *name* (what ATC says and the pilot dials).

    25 kHz names .x00/.x25/.x50/.x75 are the frequency itself; an 8.33 kHz name is offset from its 25 kHz block:
    118.005 -> 118.0000, 118.010 -> 118.0083, 118.015 -> 118.0167 (Icom IC-A24 manual channel table, read
    2026-11-04). "Translate signal" in its plainest form: the spoken number is a label, not the frequency.
    """
    ok, why = frequency_is_valid(name)
    if not ok:
        raise ValueError(f"{name}: {why}")
    khz = int(round(float(name) * 1000))
    block, rest = divmod(khz, 25)
    base = block * 25
    if rest == 0:
        return base / 1000.0, 25.0
    offset = {5: 0.0, 10: 25 / 3, 15: 50 / 3}[rest]
    return (base + offset) / 1000.0, 25 / 3


def _status_from_conf(confs: Sequence[float], hi: float, lo: float) -> str:
    c = min(confs) if confs else 1.0
    if c >= hi:
        return "CONFIRMED"
    return "LOW_CONFIDENCE"


def _masked(digits: Sequence[str], confs: Sequence[float], lo: float) -> str:
    return "".join(d if c >= lo else "?" for d, c in zip(digits, confs))


# --- the parser ----------------------------------------------------------------------------------------------

def _match(toks: Sequence[Word], i: int, phrase: str) -> int:
    """Length of ``phrase`` if it matches at ``i`` (0 otherwise)."""
    ws = phrase.split()
    if i + len(ws) > len(toks):
        return 0
    return len(ws) if all(toks[i + k].text == w for k, w in enumerate(ws)) else 0


def _parse_callsign(toks: Sequence[Word], designators: Mapping[str, str]) -> tuple[str | None, float, int]:
    if not toks or toks[0].text not in designators:
        return None, 0.0, 0
    cs = designators[toks[0].text]
    confs = [toks[0].conf]
    j = 1
    while j < len(toks) and len(cs) < 7:
        d = _digit(toks[j], allow_homophones=False)
        if d is None and toks[j].text in HOMOPHONES and j + 1 < len(toks) and \
                _digit(toks[j + 1], allow_homophones=False) is not None and len(cs) > len(designators[toks[0].text]):
            # "one to three": between callsign digits a homophone is probably a digit -- but we are not sure, so the
            # callsign confidence is capped below the 'unsure' line: the call is neither ours nor someone else's
            d = HOMOPHONES[toks[j].text]
            confs.append(0.49)
        if d is not None:
            cs += d
        elif toks[j].text in NATO:
            cs += NATO[toks[j].text]
        else:
            break
        confs.append(toks[j].conf)
        j += 1
    return cs, min(confs), j


def callsign_similarity(a: str, b: str) -> float:
    """Share of aligned characters that agree (same length) or 0 -- a simple flag for similar callsigns."""
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x == y for x, y in zip(a, b)) / len(a)


@cite("nigmatulina_2021_callsign", note="surveillance callsigns improve callsign recognition; here only to confirm")
def resolve_callsign(heard: str | None, surveillance: Iterable[str], min_similarity: float = 0.8) -> tuple[str | None, str]:
    """Match a recognised callsign against the callsigns surveillance says are present (ADS-B / Mode S ident).

    Returns ``(callsign, how)``: ``"exact"``, ``"surveillance-matched"`` (one and only one track within one
    character), ``"ambiguous"`` (several similar tracks -- the call-sign-similarity hazard; nothing is chosen) or
    ``"unknown"``. Using surveillance context is what lifted callsign recognition in the ATC speech literature
    (Nigmatulina et al. 2021, research note A_Nigmatulina2021_callsign_surveillance.md [D-ag]); here it may only
    *confirm* a single candidate, never pick among several.
    """
    pool = sorted({c.upper() for c in surveillance})
    if heard is None:
        return None, "unknown"
    if heard in pool:
        return heard, "exact"
    near = [c for c in pool if callsign_similarity(heard, c) >= min_similarity]
    if len(near) == 1:
        return near[0], "surveillance-matched"
    if len(near) > 1:
        return None, "ambiguous"
    return heard, "unknown"


def similar_callsigns(own: str, traffic: Iterable[str], min_similarity: float = 0.66) -> list[str]:
    """Other callsigns in the traffic picture that a listener could confuse with ``own`` (same length, >= 2/3 equal
    characters, or the same digits with another prefix)."""
    own = own.upper()
    out = []
    for c in sorted({t.upper() for t in traffic}):
        if c == own:
            continue
        same_digits = "".join(ch for ch in c if ch.isdigit()) == "".join(ch for ch in own if ch.isdigit()) != ""
        if callsign_similarity(own, c) >= min_similarity or same_digits:
            out.append(c)
    return out


def parse(text: str | Sequence[Word] | Sequence[tuple[str, float]], *, own_callsign: str | None = None,
          designators: Mapping[str, str] = DEFAULT_DESIGNATORS, current_altitude_ft: float | None = None,
          hi: float = 0.85, lo: float = 0.5, t_received: float | None = None, msg_id: int | None = None,
          source: str = "VHF voice (ASR)", known_runways: Iterable[str] | None = None,
          partial: bool = False) -> Clearance:
    """Parse one transmission.

    Parameters
    ----------
    text : str or sequence of (word, confidence)
        Typed/ASR text. Confidence 1.0 is assumed for plain text.
    own_callsign : str, optional
        e.g. ``"BTL123"``; sets :attr:`Clearance.addressed_to_us`.
    current_altitude_ft : float, optional
        Used to check that "climb" goes up and "descend" goes down.
    partial : bool
        The audio monitor saw a dropout inside this transmission: a value with too few digits is then NOT_RECEIVED
        (cut by the gap) rather than INVALID, and the display downgrades the rest to UNCONFIRMED.
    known_runways : iterable of str, optional
        Runways of the destination (navigation database / ATIS), e.g. ``("07L", "07R", "25L", "25R")``. A heard
        runway that does not exist there is INVALID -- this catches a recogniser that is *confidently* wrong.
    hi, lo : float
        Word-confidence thresholds: >= hi CONFIRMED, < lo masks the digit.
    """
    toks = tokenize(text)
    cs, cs_conf, i = _parse_callsign(toks, designators)
    if cs is None:                                   # readbacks often end with the callsign
        for k in range(1, len(toks)):
            if toks[k].text in designators:
                cs, cs_conf, n_cs = _parse_callsign(toks[k:], designators)
                toks = list(toks[:k]) + list(toks[k + n_cs:])
                break
    ins: list[Instruction] = []
    unparsed: list[str] = []
    pending_vertical = ""

    def add(kind, value, disp, confs, words, status=None, detail="", qual="", cands=()):
        st = status or _status_from_conf(confs, hi, lo)
        ins.append(Instruction(kind, value, disp, min(confs) if confs else 1.0, st, words, detail, tuple(cands),
                               qual))

    def number_field(kind: str, label: str, j: int, n_digits: tuple[int, ...], lo_v: int, hi_v: int,
                     confs0: list[float], words0: str, qual: str = "", unit: str = "", octal: bool = False):
        num = _read_number(toks, j, max_digits=max(n_digits))
        if num is None:
            add(kind, None, f"{label} NOT RECEIVED", confs0, words0, "NOT_RECEIVED",
                "keyword heard, value not received -- SAY AGAIN", qual)
            return j
        if j + num.n < len(toks) and toks[j + num.n].text == GAP:
            add(kind, None, f"{label} NOT RECEIVED", confs0 + num.confs, (words0 + " " + num.words).strip(),
                "NOT_RECEIVED", "value cut by a reception gap -- SAY AGAIN", qual)
            return j + num.n + 1
        confs = confs0 + num.confs
        words = (words0 + " " + num.words).strip()
        masked = _masked(num.digits, num.confs, lo)
        if "?" in masked:
            add(kind, None, f"{label} {masked}{unit}", confs, words, "LOW_CONFIDENCE",
                "a digit was heard with low confidence: SAY AGAIN", qual)
            return j + num.n
        if len(num.digits) not in n_digits and not num.grouped:
            if partial:
                add(kind, None, f"{label} NOT RECEIVED", confs, words, "NOT_RECEIVED",
                    f"only {len(num.digits)} digit(s) heard and the transmission had a dropout -- SAY AGAIN", qual)
            else:
                add(kind, None, f"{label} {''.join(num.digits)}?", confs, words, "INVALID",
                    f"expected {'/'.join(map(str, n_digits))} digits, heard {len(num.digits)}", qual)
            return j + num.n
        if octal and any(d in "89" for d in num.digits):
            add(kind, None, f"{label} {''.join(num.digits)}", confs, words, "INVALID", "squawk digits are 0-7", qual)
            return j + num.n
        v = num.value
        if not lo_v <= v <= hi_v:
            add(kind, None, f"{label} {v}{unit}", confs, words, "INVALID", f"outside {lo_v}-{hi_v}", qual)
            return j + num.n
        disp_v = "".join(num.digits) if kind in ("heading", "squawk", "flight_level") else str(v)
        add(kind, "".join(num.digits) if octal else v, f"{label} {disp_v}{unit}", confs, words, qual=qual)
        return j + num.n

    while i < len(toks):
        t = toks[i].text
        c = toks[i].conf
        # --- information, parsed so its numbers cannot become instructions
        if t == "wind":
            num1 = _read_number(toks, i + 1, max_digits=3)
            j = i + 1 + (num1.n if num1 else 0)
            if j < len(toks) and toks[j].text == "degrees":
                j += 1
            num2 = _read_number(toks, j, max_digits=2)
            j += num2.n if num2 else 0
            if j < len(toks) and toks[j].text == "knots":
                j += 1
            disp = f"WIND {num1.value if num1 else '---'}/{num2.value if num2 else '--'}"
            add("wind", (num1.value if num1 else None, num2.value if num2 else None), disp,
                [c] + (num1.confs if num1 else []) + (num2.confs if num2 else []),
                " ".join(w.text for w in toks[i:j]), "INFO")
            i = j
            continue
        # --- lateral
        n = _match(toks, i, "turn left heading") or _match(toks, i, "turn right heading")
        if n:
            qual = toks[i + 1].text
            i = number_field("heading", f"TURN {qual.upper()} HDG", i + n, (3,), 1, 360,
                             [w.conf for w in toks[i:i + n]], " ".join(w.text for w in toks[i:i + n]), qual)
            continue
        n = _match(toks, i, "fly heading") or _match(toks, i, "continue heading") or _match(toks, i, "heading")
        if n:
            i = number_field("heading", "HDG", i + n, (3,), 1, 360, [w.conf for w in toks[i:i + n]],
                             " ".join(w.text for w in toks[i:i + n]))
            continue
        # --- vertical
        if t in ("climb", "descend", "maintain"):
            pending_vertical = t if t != "maintain" else (pending_vertical or "maintain")
            j = i + 1
            if _match(toks, j, "and maintain"):
                j += 2
            confs0 = [w.conf for w in toks[i:j]]
            # "to" / "two" right after the verb: preposition or the first digit?
            hom = j < len(toks) and toks[j].text in ("to", "too", "two", "tu")
            if _match(toks, j + (1 if hom else 0), "flight level"):
                k = j + (1 if hom else 0) + 2
                i = number_field("flight_level", f"{pending_vertical.upper()} FL", k, (2, 3), 10, 660,
                                 confs0 + [w.conf for w in toks[j:k]], " ".join(w.text for w in toks[i:k]),
                                 pending_vertical)
                _check_direction(ins, current_altitude_ft)
                continue
            if hom:
                # Reading A: preposition "to". Reading B: the digit 2. Both valid and the word unsure -> AMBIGUOUS.
                num_a = _read_number(toks, j + 1)
                num_b = _read_number([Word("2", toks[j].conf)] + list(toks[j + 1:]), 0)
                ok_a = num_a is not None and num_a.grouped
                ok_b = num_b is not None and num_b.grouped and num_b.value <= 60000
                literal_is_digit = toks[j].text == "two"
                if (num_a is not None and num_b is not None and ok_a and ok_b and num_a.value != num_b.value
                        and toks[j].conf < hi):
                    end = j + 1 + num_a.n
                    if end < len(toks) and toks[end].text == "feet":
                        end += 1
                    add("altitude", None, f"{pending_vertical.upper()} {num_a.value} or {num_b.value} FT?",
                        confs0 + [toks[j].conf] + num_a.confs, " ".join(w.text for w in toks[i:end]), "AMBIGUOUS",
                        f"'{toks[j].text}' may be the preposition or the digit two", pending_vertical,
                        (num_a.value, num_b.value))
                    _check_direction(ins, current_altitude_ft)
                    i = end
                    continue
                if not literal_is_digit:
                    j += 1                      # treat as the preposition; the digit path below reads the rest
            num = _read_number(toks, j)
            if num is not None and (num.grouped or (j < len(toks) and _feet_follows(toks, j + num.n))):
                end = j + num.n
                if end < len(toks) and toks[end].text == "feet":
                    end += 1
                _add_altitude(add, num.value, confs0 + num.confs, " ".join(w.text for w in toks[i:end]),
                              pending_vertical, num, lo)
                _check_direction(ins, current_altitude_ft)
                i = end
                continue
            if t == "maintain" and (_match(toks, j, "speed") or (num is not None and _knots_follow(toks, j + num.n))):
                pass  # handled by the speed branch below
            else:
                if num is None:
                    if j < len(toks) and toks[j].text == GAP or j >= len(toks) or toks[j].text == "feet" or partial:
                        end = j + (1 if j < len(toks) and toks[j].text in (GAP, "feet") else 0)
                        add("altitude", None, f"{pending_vertical.upper()} NOT RECEIVED", confs0,
                            " ".join(w.text for w in toks[i:end]), "NOT_RECEIVED",
                            "level not received -- SAY AGAIN", pending_vertical)
                        i = max(end, i + 1)
                        continue
                    unparsed.append(t)
                    i += 1
                    continue
                add("altitude", None, f"{pending_vertical.upper()} {''.join(num.digits)}?", confs0 + num.confs,
                    " ".join(w.text for w in toks[i:j + num.n]), "INVALID", "level without 'feet', thousand or FL",
                    pending_vertical)
                i = j + num.n
                continue
        num0 = _read_number(toks, i) if _digit(toks[i], False) is not None else None
        if num0 is not None and (num0.grouped or _feet_follows(toks, i + num0.n)) and \
                (_feet_follows(toks, i + num0.n) or num0.value >= 1000):
            end = i + num0.n + (1 if _feet_follows(toks, i + num0.n) else 0)
            _add_altitude(add, num0.value, num0.confs, " ".join(w.text for w in toks[i:end]), pending_vertical,
                          num0, lo)
            i = end
            continue
        if _match(toks, i, "flight level"):
            i = number_field("flight_level", "FL", i + 2, (2, 3), 10, 660, [toks[i].conf, toks[i + 1].conf],
                             "flight level", pending_vertical)
            continue
        # --- speed
        n = (_match(toks, i, "reduce speed") or _match(toks, i, "increase speed") or _match(toks, i, "maintain speed")
             or _match(toks, i, "speed") or (_match(toks, i, "maintain") and 1))
        if n:
            j = i + n
            if j < len(toks) and toks[j].text in ("to",):
                j += 1
            num = _read_number(toks, j, max_digits=3)
            if num is not None and (n > 1 or toks[i].text == "speed" or _knots_follow(toks, j + num.n)):
                qual = toks[i].text if toks[i].text in ("reduce", "increase") else ""
                end = number_field("speed", "SPD", j, (2, 3), 60, 400, [w.conf for w in toks[i:j]],
                                   " ".join(w.text for w in toks[i:j]), qual, " KT")
                if end < len(toks) and toks[end].text == "knots":
                    end += 1
                i = end
                continue
        # --- transponder, frequency, pressure
        if t == "squawk":
            if i + 1 < len(toks) and toks[i + 1].text in ("ident", "standby", "mayday"):
                add("squawk_cmd", toks[i + 1].text, f"SQUAWK {toks[i + 1].text.upper()}", [c, toks[i + 1].conf],
                    f"squawk {toks[i + 1].text}")
                i += 2
                continue
            i = number_field("squawk", "SQK", i + 1, (4,), 0, 7777, [c], "squawk", octal=True)
            sq = ins[-1]
            if sq.status == "CONFIRMED" and sq.value in ("7500", "7600", "7700"):
                ins[-1] = replace(sq, detail="emergency code -- verify")
            continue
        if t in ("contact", "monitor"):
            j = i + 1
            unit_words: list[str] = []
            while j < len(toks) and _digit(toks[j], False) is None and len(unit_words) < 4 and toks[j].text != GAP:
                unit_words.append(toks[j].text)
                j += 1
            num = _read_number(toks, j, max_digits=3, decimal=True)
            words = " ".join(w.text for w in toks[i:j + (num.n if num else 0)])
            unit = " ".join(unit_words).upper()
            if num is None:
                add("frequency", None, f"{t.upper()} {unit} NOT RECEIVED".replace("  ", " "), [c], words,
                    "NOT_RECEIVED", "frequency not received -- SAY AGAIN", unit)
                i = j + (1 if j < len(toks) and toks[j].text == GAP else 0)
                continue
            masked = _masked(num.digits + num.decimals, num.confs[:len(num.digits) + len(num.decimals)], lo)
            ftxt = "".join(num.digits) + ("." + "".join(num.decimals) if num.decimals else "")
            if "?" in masked:
                add("frequency", None, f"{t.upper()} {unit} {masked[:3]}.{masked[3:]}", [c] + num.confs, words,
                    "LOW_CONFIDENCE", "a digit was heard with low confidence: SAY AGAIN", unit)
            else:
                ok, why = frequency_is_valid(ftxt)
                if ok:
                    add("frequency", ftxt, f"{t.upper()} {unit} {ftxt}", [c] + num.confs, words, qual=unit,
                        detail=why)
                else:
                    add("frequency", None, f"{t.upper()} {unit} {ftxt}?", [c] + num.confs, words, "INVALID", why,
                        unit)
            i = j + num.n
            continue
        if t == "qnh":
            i = number_field("qnh", "QNH", i + 1, (3, 4), 900, 1100, [c], "qnh")
            continue
        # --- runway / approach
        n = (_match(toks, i, "cleared ils approach runway") or _match(toks, i, "cleared ils runway")
             or _match(toks, i, "cleared to land runway") or _match(toks, i, "line up and wait runway")
             or _match(toks, i, "hold short runway") or _match(toks, i, "hold short of runway"))
        if n:
            words0 = " ".join(w.text for w in toks[i:i + n])
            qual = "ILS" if "ils" in words0 else ("LAND" if "land" in words0 else
                                                ("LINE UP" if "line" in words0 else "HOLD SHORT"))
            num = _read_number(toks, i + n, max_digits=2)
            j = i + n + (num.n if num else 0)
            side = ""
            if j < len(toks) and toks[j].text in ("left", "right", "center", "centre"):
                side = toks[j].text[0].upper()
                j += 1
            confs = [w.conf for w in toks[i:j]]
            if num is None:
                add("runway", None, f"{qual} RWY NOT RECEIVED", confs, words0, "NOT_RECEIVED",
                    "runway not received -- SAY AGAIN", qual)
                if j < len(toks) and toks[j].text == GAP:
                    j += 1
            elif "?" in _masked(num.digits, num.confs, lo):
                add("runway", None, f"{qual} RWY ??", confs, words0, "LOW_CONFIDENCE", "runway not readable", qual)
            elif not 1 <= num.value <= 36:
                add("runway", None, f"{qual} RWY {num.value}", confs, words0, "INVALID", "runway 01-36", qual)
            else:
                rw = f"{num.value:02d}{side}"
                if known_runways is not None and rw not in {r.upper() for r in known_runways}:
                    add("runway", None, f"{qual} RWY {rw}?", confs, " ".join(w.text for w in toks[i:j]), "INVALID",
                        f"runway {rw} does not exist at this aerodrome", qual)
                else:
                    add("runway", rw, f"{qual} RWY {rw}", confs, " ".join(w.text for w in toks[i:j]), qual=qual)
            i = j
            continue
        if _match(toks, i, "go around"):
            add("go_around", True, "GO AROUND", [c, toks[i + 1].conf], "go around")
            i += 2
            continue
        n = _match(toks, i, "proceed direct") or _match(toks, i, "direct to") or _match(toks, i, "direct")
        if n:
            j = i + n
            if j < len(toks):
                add("direct", toks[j].text.upper(), f"DCT {toks[j].text.upper()}", [w.conf for w in toks[i:j + 1]],
                    " ".join(w.text for w in toks[i:j + 1]))
                i = j + 1
                continue
        unparsed.append(t)
        i += 1

    addressed = None
    if own_callsign is not None:
        addressed = None if cs is None else (cs == own_callsign.upper())
    if cs is not None and cs_conf < lo:
        addressed = None
    return Clearance(cs, cs_conf, addressed, tuple(ins), " ".join(w.text for w in toks), tuple(unparsed), source,
                     t_received, msg_id, partial)


def _feet_follows(toks: Sequence[Word], j: int) -> bool:
    return j < len(toks) and toks[j].text == "feet"


def _knots_follow(toks: Sequence[Word], j: int) -> bool:
    return j < len(toks) and toks[j].text == "knots"


def _add_altitude(add, value, confs, words, qual, num: _Num, lo: float) -> None:
    masked = _masked(num.digits, num.confs[:len(num.digits)], lo) if num.digits else ""
    label = f"{qual.upper()} " if qual else ""
    if "?" in masked:
        add("altitude", None, f"{label}{masked} FT?", confs, words, "LOW_CONFIDENCE",
            "a digit was heard with low confidence: SAY AGAIN", qual)
    elif value % 100 or not -1000 <= value <= 60000:
        add("altitude", None, f"{label}{value} FT?", confs, words, "INVALID", "altitude must be a 100 ft multiple",
            qual)
    else:
        add("altitude", value, f"{label}{value} FT", confs, words, qual=qual)


def _check_direction(ins: list[Instruction], current_altitude_ft: float | None) -> None:
    if current_altitude_ft is None or not ins:
        return
    last = ins[-1]
    if last.status != "CONFIRMED" or last.kind not in ("altitude", "flight_level"):
        return
    if not isinstance(last.value, (int, float)):
        return
    target = last.value * 100 if last.kind == "flight_level" else last.value
    if (last.qualifier == "climb" and target <= current_altitude_ft) or \
       (last.qualifier == "descend" and target >= current_altitude_ft):
        ins[-1] = replace(last, status="INVALID",
                          detail=f"{last.qualifier} to {target} ft contradicts present {current_altitude_ft:.0f} ft")


def parse_nbest(hypotheses: Sequence[tuple[str | Sequence[Word], float]], **kw: Any) -> Clearance:
    """Parse several recogniser hypotheses (text, score) and merge them conservatively.

    The best hypothesis gives the structure. Any critical field whose value differs between hypotheses that
    parse validly becomes ``AMBIGUOUS`` with the candidate values -- the display must ask, not choose.
    """
    if not hypotheses:
        raise ValueError("no hypotheses")
    ranked = sorted(hypotheses, key=lambda h: -h[1])
    parsed = [parse(h, **kw) for h, _ in ranked]
    best = parsed[0]
    out: list[Instruction] = []
    for ins in best.instructions:
        if ins.kind not in CRITICAL or ins.status != "CONFIRMED":
            out.append(ins)
            continue
        vals = []
        for p in parsed:
            other = p.get(ins.kind)
            if other is not None and other.value is not None and other.value not in vals:
                vals.append(other.value)
        if len(vals) > 1:
            out.append(replace(ins, status="AMBIGUOUS", value=None, candidates=tuple(vals),
                               display=f"{ins.display.rsplit(' ', 1)[0]} {' / '.join(map(str, vals))}?",
                               detail="recogniser alternatives disagree"))
        else:
            out.append(ins)
    cs_values = {p.callsign for p in parsed if p.callsign}
    addressed = best.addressed_to_us if len(cs_values) <= 1 else None
    return replace(best, instructions=tuple(out), addressed_to_us=addressed)


# --- readback ------------------------------------------------------------------------------------------------

#: elements that must be read back: SERA.8015(e)(1) lists route clearances, runway instructions, runway in use,
#: altimeter settings, SSR codes, frequency instructions, level, heading and speed instructions and transition levels
#: (research agent, C_EASA_SERA_EAR.md [D-ag]); route and transition level are not parsed here)
READBACK_REQUIRED = ("heading", "altitude", "flight_level", "speed", "squawk", "frequency", "qnh", "runway")


@dataclass(frozen=True)
class ReadbackReport:
    ok: bool
    missing: tuple[str, ...]
    mismatched: tuple[tuple[str, object, object], ...]       # (kind, ATC value, readback value)
    callsign_ok: bool | None
    notes: tuple[str, ...] = ()


def readback_check(atc: Clearance, readback: Clearance) -> ReadbackReport:
    """Compare a pilot readback with the ATC clearance it answers ("hearback" assistant).

    A field counts as read back only if its value is equal; a readback value that is not CONFIRMED is reported
    as missing (the system cannot vouch for it).
    """
    missing, mism, notes = [], [], []
    for ins in atc.instructions:
        if ins.kind not in READBACK_REQUIRED:
            continue
        if ins.status != "CONFIRMED":
            notes.append(f"ATC {ins.kind} not confirmed by the recogniser -- check by ear")
            continue
        rb = readback.get(ins.kind)
        if rb is None or rb.status != "CONFIRMED":
            missing.append(ins.kind)
        elif rb.value != ins.value:
            mism.append((ins.kind, ins.value, rb.value))
        elif ins.qualifier and rb.qualifier and ins.qualifier != rb.qualifier:
            mism.append((ins.kind + "_direction", ins.qualifier, rb.qualifier))
    cs_ok = None
    if atc.callsign and readback.callsign:
        cs_ok = atc.callsign == readback.callsign
        if not cs_ok:
            notes.append(f"readback callsign {readback.callsign} differs from {atc.callsign}")
    return ReadbackReport(not missing and not mism and cs_ok is not False, tuple(missing), tuple(mism), cs_ok,
                          tuple(notes))


def words_with_conf(pairs: Iterable[tuple[str, float]]) -> list[Word]:
    """Helper: list of (word, conf) -> list of :class:`Word`."""
    return [Word(w, c) for w, c in pairs]


__all__ += ["words_with_conf", "READBACK_REQUIRED", "HOMOPHONES", "CRITICAL", "channel_to_frequency",
            "resolve_callsign", "similar_callsigns"]
