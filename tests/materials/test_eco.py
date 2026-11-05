"""Family eco data (aerokit.materials.eco) and its use in the CO₂-weighted ranking."""
from aerokit.materials import eco as E
from aerokit.materials import selection as S
from aerokit.verification import check, check_true, expect_error

SRC = "Useful numbers for environmental studies (Ashby 2013 reproduction), read 2026-11-01"


def test_values_as_printed():
    check("Al primary 210 ± 10 MJ/kg (mid)", sum(E.FAMILIES["aluminium"].energy) / 2, 210, rtol=1e-12, source=SRC)
    check("Al primary CO₂ 12 kg/kg", E.co2_per_kg("7075-T6"), 12, rtol=1e-12, source=SRC)
    check("Ti alloy primary CO₂ 46.5 kg/kg", E.co2_per_kg("Ti-6Al-4V"), 46.5, rtol=1e-12, source=SRC)
    check("carbon fibre CO₂ 33–36 → mid 34.5", E.co2_per_kg("carbon_fibre"), 34.5, rtol=1e-12, source=SRC)
    check("autoclave 100–300 MJ/kg upper", E.SHAPING["autoclave_molding"][0][1], 300, rtol=1e-12, source=SRC)
    for k, f in E.FAMILIES.items():
        check_true(f"{k}: low ≤ high", f.energy[0] <= f.energy[1] and f.co2[0] <= f.co2[1])


def test_recycled_content_mix():
    check("50 % recycled Al = (12 + 2.1)/2", E.co2_per_kg("aluminium", recycled_content=0.5), 7.05, rtol=1e-12)
    expect_error("CFRP has no recycled route here", E.co2_per_kg, "carbon_fibre", recycled_content=0.2,
                 error=ValueError)


def test_composite_and_ranking():
    c = E.composite_co2_per_kg(0.6, "autoclave_molding")
    check("0.6·34.5 + 0.4·7.15 + 10 = 33.56", c, 0.6 * 34.5 + 0.4 * 7.15 + 10, rtol=1e-12)
    co2 = {k: E.co2_per_kg(k) for k in E.CATALOGUE_FAMILY}
    r = S.rank("tie_strong", list(E.CATALOGUE_FAMILY), co2_per_kg=co2)
    check_true("strong tie on CO₂: an aluminium alloy beats Ti-6Al-4V", r[0].name != "Ti-6Al-4V", r)
    expect_error("unknown family", E.family_of, "unobtainium", error=KeyError)
