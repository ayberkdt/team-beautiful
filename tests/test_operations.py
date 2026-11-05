"""Queues, runway capacity, peak-hour delay and ICAO per-passenger CO₂ (aerokit.operations)."""
import math

from aerokit import operations as O
from aerokit.verification import check, check_true, expect_error

PK = "Pollaczek–Khinchine / Erlang C (Wikipedia, read 2026-10-25)"


def test_single_server_queues():
    m = O.mm1(0.8, 1.0)
    check("M/M/1 W_q = ρ/(μ − λ)", m.Wq, 0.8 / 0.2, rtol=1e-12, source=PK)
    check("Little: L = λ W", m.L, 0.8 * m.W, rtol=1e-12)
    check("M/D/1 waits half as long as M/M/1", O.md1(0.8, 1.0).Wq, m.Wq / 2, rtol=1e-12)
    g = O.mg1(0.5, 1.0, 0.25)
    check("M/G/1 P-K with Var(S) = 0.25", g.Wq, (0.5 + 0.5 * 1.0 * 0.25) / (2 * 0.5), rtol=1e-12, source=PK)
    expect_error("ρ ≥ 1 has no steady state", O.mm1, 1.0, 1.0, error=ValueError)


def test_multi_server_queue():
    one = O.mmc(0.8, 1.0, 1)
    check("M/M/c with c = 1 equals M/M/1 (two formulas)", one.Wq, O.mm1(0.8, 1.0).Wq, rtol=1e-12)
    A, c = 2.0, 3
    top = A ** c / math.factorial(c) * c / (c - A)
    erl = top / (1 + A + A ** 2 / 2 + top)
    check("Erlang C, c = 3, A = 2 (by hand) = 4/9", O.erlang_c(3, 2.0), erl, rtol=1e-12, source=PK)
    check("… which is 4/9", erl, 4 / 9, rtol=1e-12)
    m = O.mmc(2.0, 1.0, 3)
    check("W = C/(cμ − λ) + 1/μ", m.W, erl / (3 - 2) + 1.0, rtol=1e-12, source=PK)
    check_true("adding a server cuts the wait", O.mmc(2.0, 1.0, 4).Wq < m.Wq)
    expect_error("λ ≥ cμ unstable", O.mmc, 3.0, 1.0, 3, error=ValueError)


def test_runway_capacity():
    check("mean separation 105 s → 34.3 movements/h", O.runway_capacity_per_hour([90, 120], [0.5, 0.5]),
          3600 / 105, rtol=1e-12)
    expect_error("fractions must sum to 1", O.runway_capacity_per_hour, [90, 120], [0.5, 0.6], error=ValueError)


def test_peak_queue_by_hand():
    p = O.peak_queue([30, 45, 50, 35, 20, 10], [40] * 6)
    check_true("queue 0, 5, 15, 10, 0, 0", p.queue == (0.0, 5.0, 15.0, 10.0, 0.0, 0.0), p.queue)
    check("trapezoid delay 2.5 + 10 + 12.5 + 5 = 30 movement-intervals", p.total_delay, 30.0, rtol=1e-12)
    check_true("clears at the end of interval 4", p.clears_after == 4, p.clears_after)
    check("conservation: served + final queue = demand", sum(p.served) + p.queue[-1], 190.0, rtol=1e-12)
    over = O.peak_queue([50] * 3, [40] * 3)
    check_true("overload never clears", over.clears_after is None and over.max_queue == 30.0)
    check_true("no queue: clears_after 0", O.peak_queue([10, 10], [40, 40]).clears_after == 0)


def test_icao_co2_per_passenger():
    v = O.co2_per_passenger_icao(5000.0, 0.9, 180.0, 0.8)
    check("3.16 × fuel × pax factor / (seats × load factor)", v, 3.16 * 5000 * 0.9 / (180 * 0.8), rtol=1e-12,
          source="ICAO CEC methodology v8 (2015)")
    expect_error("load factor > 1", O.co2_per_passenger_icao, 1.0, 0.9, 180.0, 1.2, error=ValueError)
