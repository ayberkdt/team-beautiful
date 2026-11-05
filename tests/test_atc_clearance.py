"""Clearance parser: the critical tests from the challenge notes (E3) plus phraseology validation."""
import pytest

from aerokit.atc.clearance import (Word, frequency_is_valid, parse, parse_nbest, readback_check, tokenize)

OWN = "BTL123"


def ins(c, kind):
    x = c.get(kind)
    assert x is not None, f"{kind} missing in {c.instructions}"
    return x


def test_clean_channel_example():
    c = parse("Beetle one two three, turn left heading two seven zero, descend and maintain three thousand feet",
              own_callsign=OWN, current_altitude_ft=5000)
    assert c.callsign == OWN and c.addressed_to_us is True and c.status == "CONFIRMED"
    h, a = ins(c, "heading"), ins(c, "altitude")
    assert (h.value, h.qualifier, h.display) == (270, "left", "TURN LEFT HDG 270")
    assert (a.value, a.qualifier) == (3000, "descend")


def test_typed_asr_text_with_numerals():
    c = parse("BTL123 TURN LEFT HEADING 270 DESCEND AND MAINTAIN 3000 FT", own_callsign=OWN,
              designators={"btl": "BTL"})
    # "BTL123" is one token -> split as letters? it is not a designator word; callsign unknown but values parse
    assert ins(c, "heading").value == 270
    assert ins(c, "altitude").value == 3000


def test_low_confidence_digit_is_masked_never_shown():
    words = [Word(w, 0.95) for w in "beetle one two three turn left heading two".split()]
    words += [Word("seven", 0.3), Word("zero", 0.95)]
    h = ins(parse(words, own_callsign=OWN), "heading")
    assert h.value is None and h.status == "LOW_CONFIDENCE" and "2?0" in h.display


def test_two_seven_zero_vs_two_zero_zero_nbest_is_ambiguous():
    c = parse_nbest([("beetle one two three heading two seven zero", 0.55),
                     ("beetle one two three heading two zero zero", 0.45)], own_callsign=OWN)
    h = ins(c, "heading")
    assert h.status == "AMBIGUOUS" and h.value is None and set(h.candidates) == {270, 200}


def test_nbest_agreement_stays_confirmed():
    c = parse_nbest([("beetle one two three heading two seven zero", 0.6),
                     ("beetle one two tree heading two seven zero", 0.4)], own_callsign=OWN)
    assert ins(c, "heading").status == "CONFIRMED"


def test_to_two_ambiguity():
    w = [Word(x, 0.95) for x in "beetle one two three descend".split()] + [Word("to", 0.6)] + \
        [Word(x, 0.95) for x in "five thousand".split()]
    a = ins(parse(w, own_callsign=OWN), "altitude")
    assert a.status == "AMBIGUOUS" and set(a.candidates) == {5000, 25000}
    a2 = ins(parse("beetle one two three descend to five thousand feet", own_callsign=OWN), "altitude")
    assert a2.status == "CONFIRMED" and a2.value == 5000


def test_callsign_mixup_flagged():
    c = parse("beetle one three two turn right heading zero nine zero", own_callsign=OWN)
    assert c.callsign == "BTL132" and c.addressed_to_us is False and c.status == "NOT_FOR_US"


def test_unsure_callsign_is_not_assumed_ours():
    w = [Word("beetle", 0.4)] + [Word(x, 0.9) for x in "one two three heading one two zero".split()]
    assert parse(w, own_callsign=OWN).addressed_to_us is None


@pytest.mark.parametrize("text,kind,reason", [
    ("beetle one two three heading three six five", "heading", "outside"),
    ("beetle one two three heading two seven", "heading", "digits"),
    ("beetle one two three squawk one two eight four", "squawk", "0-7"),
    ("beetle one two three contact approach one three seven decimal one zero zero", "frequency", "118.000"),
    ("beetle one two three contact tower one one eight decimal one two zero", "frequency", "channel"),
    ("beetle one two three qnh eight five zero", "qnh", "outside"),
])
def test_invalid_values_rejected(text, kind, reason):
    x = ins(parse(text, own_callsign=OWN), kind)
    assert x.status == "INVALID" and reason in x.detail


def test_direction_contradiction():
    x = ins(parse("beetle one two three climb flight level one two zero", own_callsign=OWN,
                  current_altitude_ft=15000), "flight_level")
    assert x.status == "INVALID" and "contradicts" in x.detail


def test_wind_numbers_never_become_heading():
    c = parse("beetle one two three cleared to land runway two five left wind two seven zero degrees one zero knots",
              own_callsign=OWN)
    assert c.get("heading") is None
    assert ins(c, "runway").value == "25L" and ins(c, "wind").value == (270, 10)


def test_frequency_and_squawk_and_qnh():
    c = parse("beetle one two three contact approach one one eight decimal five zero five squawk seven six zero zero "
              "qnh one zero one three", own_callsign=OWN)
    assert ins(c, "frequency").value == "118.505"
    sq = ins(c, "squawk")
    assert sq.value == "7600" and "emergency" in sq.detail
    assert ins(c, "qnh").value == 1013


def test_frequency_channel_rules():
    assert frequency_is_valid("118.000")[0] and frequency_is_valid("121.500")[0]
    assert frequency_is_valid("132.005")[0] and not frequency_is_valid("132.020")[0]
    assert not frequency_is_valid("117.950")[0] and not frequency_is_valid("137.000")[0]


def test_speed_and_ils():
    c = parse("beetle one two three reduce speed one eight zero knots cleared ils approach runway two five right",
              own_callsign=OWN)
    assert ins(c, "speed").value == 180 and ins(c, "runway").value == "25R"


def test_readback_mismatch_and_callsign():
    atc = parse("beetle one two three turn left heading two seven zero descend and maintain three thousand feet")
    good = parse("left heading two seven zero descending three thousand feet beetle one two three")
    bad = parse("left heading two six zero descending three thousand feet beetle one two three")
    short = parse("heading two seven zero beetle one three two")
    assert readback_check(atc, good).ok
    rb = readback_check(atc, bad)
    assert not rb.ok and rb.mismatched == (("heading", 270, 260),)
    rs = readback_check(atc, short)
    assert not rs.ok and rs.missing == ("altitude",) and rs.callsign_ok is False


def test_tokenize_numerals():
    assert [w.text for w in tokenize("FL80 118.505")] == ["flight", "level", "8", "0", "1", "1", "8", "decimal",
                                                          "5", "0", "5"]


def test_noise_words_do_not_create_instructions():
    c = parse("beetle one two three uh say again", own_callsign=OWN)
    assert c.instructions == () and c.status == "NO_CONTENT"


def test_channel_name_to_operating_frequency():
    from aerokit.atc.clearance import channel_to_frequency
    assert channel_to_frequency("118.010") == pytest.approx((118.008333, 25 / 3), abs=1e-5)
    assert channel_to_frequency("118.030") == pytest.approx((118.025, 25 / 3), abs=1e-9)
    assert channel_to_frequency("121.500") == (121.5, 25.0)
    with pytest.raises(ValueError):
        channel_to_frequency("118.020")


def test_callsign_surveillance_correlation():
    from aerokit.atc.clearance import resolve_callsign, similar_callsigns
    pool = ["BTL123", "EXA901", "NVA77"]
    assert resolve_callsign("BTL123", pool) == ("BTL123", "exact")
    assert resolve_callsign("BTL128", pool) == ("BTL123", "surveillance-matched")
    assert resolve_callsign("BTL128", pool + ["BTL122"]) == (None, "ambiguous")
    assert resolve_callsign("ZZZ999", pool) == ("ZZZ999", "unknown")
    assert similar_callsigns("BTL123", ["BTL132", "EXA123", "NVA77", "BTL123"]) == ["BTL132", "EXA123"]


def test_confidently_wrong_runway_caught_by_context():
    # real SAPI output on 4 Nov: "runway three five right" for 25R at utterance confidence 0.99
    c = parse("beetle one two three cleared ils approach runway three five right", own_callsign=OWN,
              known_runways=("07L", "07R", "25L", "25R"))
    r = ins(c, "runway")
    assert r.status == "INVALID" and "does not exist" in r.detail
    ok = parse("beetle one two three cleared ils approach runway two five right", own_callsign=OWN,
               known_runways=("07L", "07R", "25L", "25R"))
    assert ins(ok, "runway").value == "25R"



@pytest.mark.parametrize("text,kind", [
    ("beetle one two three descend and maintain <gap> feet", "altitude"),
    ("beetle one two three turn left heading two <gap> zero", "heading"),
    ("beetle one two three turn left heading <gap>", "heading"),
    ("beetle one two three contact approach <gap>", "frequency"),
    ("beetle one two three cleared ils approach runway <gap>", "runway"),
    ("beetle one two three squawk four <gap>", "squawk"),
    ("beetle one two three descend and maintain", "altitude"),
])
def test_missing_value_is_not_received_never_guessed(text, kind):
    c = parse(text, own_callsign=OWN)
    x = ins(c, kind)
    assert x.status == "NOT_RECEIVED" and x.value is None and "NOT RECEIVED" in x.display
    assert not any(ch.isdigit() for ch in x.display.split("NOT RECEIVED")[0].split()[-1])   # no partial number shown


def test_gap_does_not_hide_the_rest():
    c = parse("beetle one two three turn left heading <gap> descend and maintain three thousand feet", own_callsign=OWN)
    assert ins(c, "heading").status == "NOT_RECEIVED"
    assert ins(c, "altitude").value == 3000 and ins(c, "altitude").status == "CONFIRMED"



def test_homophone_inside_callsign_makes_it_unsure_not_someone_else():
    c = parse([("beetle", .9), ("one", .9), ("to", .9), ("three", .9), ("turn", .9), ("right", .9), ("heading", .9),
               ("one", .9), ("niner", .9), ("zero", .9)], own_callsign=OWN)
    assert c.callsign == "BTL123" and c.addressed_to_us is None
    clean = parse("beetle one two three turn right heading one niner zero", own_callsign=OWN)
    assert clean.addressed_to_us is True
