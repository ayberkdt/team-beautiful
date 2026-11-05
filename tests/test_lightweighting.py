"""Light-weighting fuel factor, eco audit and payback (aerokit.design.sustainability)."""
import math

from aerokit.design import sustainability as SU
from aerokit.verification import check, check_true, expect_error


def test_fuel_factor_against_breguet():
    # Breguet at fixed range: W_i / W_f = e^k. Take k, a dry mass and an extra 100 kg, solve both directly.
    k, Wf, dm = 0.25, 6000.0, 100.0
    fuel = lambda w_end: w_end * (math.exp(k) - 1)
    f = 1 - math.exp(-k)
    check("Δfuel/Δm = f/(1 − f) equals Breguet re-solved", (fuel(Wf + dm) - fuel(Wf)) / dm,
          SU.fuel_per_kg_carried(f), rtol=1e-12)
    check("f = 0.2 → 0.25 kg fuel per kg", SU.fuel_per_kg_carried(0.2), 0.25, rtol=1e-12)
    expect_error("fuel fraction 1", SU.fuel_per_kg_carried, 1.0, error=ValueError)


def test_lightweighting_and_payback():
    lw = SU.lightweighting(10.0, 0.2, 20_000)
    check("10 kg × 0.25 = 2.5 kg fuel per flight", lw.fuel_per_mission_kg, 2.5, rtol=1e-12)
    check("lifetime CO₂ = 2.5 × 20 000 × 3.16", lw.lifetime_co2_kg, 2.5 * 20_000 * 3.16, rtol=1e-12)
    check("payback 790 kg extra / 7.9 kg per flight = 100 flights", SU.payback_missions(790.0, 2.5 * 3.16),
          100.0, rtol=1e-12)
    check_true("cleaner and lighter: payback 0", SU.payback_missions(-5.0, 1.0) == 0.0)
    check_true("never saves: inf", math.isinf(SU.payback_missions(5.0, 0.0)))


def test_eco_audit():
    a = SU.eco_audit(2.0, 10.0, manufacture_co2_per_kg=1.0, transport_co2_kg=0.5, use_co2_kg=100.0,
                     end_of_life_co2_per_kg=-4.0, buy_to_fly=5.0)
    check("material = 2 kg × 5 × 10", a.material, 100.0, rtol=1e-12)
    check("total = 100 + 10 + 0.5 + 100 − 8", a.total, 202.5, rtol=1e-12)
    check("shares sum to 1", sum(a.shares().values()), 1.0, rtol=1e-12)
    check_true("dominant phase by magnitude", a.dominant in ("material", "use"))
    expect_error("buy-to-fly < 1", SU.eco_audit, 1.0, 1.0, buy_to_fly=0.5, error=ValueError)
