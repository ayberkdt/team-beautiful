"""Primary and secondary surveillance radar: link budgets, detection probability, coverage.

PSR is a two-way echo (power falls as R^-4); SSR is two one-way links (interrogation up at 1030 MHz, reply down at
1090 MHz, each R^-2), which is why SSR reaches far with modest power and why it fails completely when the
transponder is off, while PSR still sees the airframe. One-way links reuse :func:`aerokit.approach.friis_received_power`
and :func:`aerokit.approach.thermal_noise_power` (read-only import).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats

from aerokit.approach import friis_received_power, thermal_noise_power
from aerokit.references import cite

__all__ = ["C", "psr_received_power", "psr_snr", "albersheim_snr_db", "pd_nonfluctuating", "pd_swerling1",
           "threshold_pfa", "radar_horizon_m", "SsrLink", "ssr_link", "hits_per_scan", "pd_m_of_n",
           "fruit_free_probability", "psr_range_for_pd"]

C = 299_792_458.0
K_EFFECTIVE_EARTH = 4.0 / 3.0
R_EARTH = 6_371_000.0


@cite("wikipedia_radar_2026", note="Pr = Pt Gt Ar sigma F^4 / ((4 pi)^2 R^4), Ar = G lambda^2 / (4 pi)")
def psr_received_power(p_tx_w: float, gain_dbi: float, frequency_hz: float, rcs_m2: float, range_m: float,
                       losses_db: float = 0.0, propagation_factor: float = 1.0) -> float:
    """Echo power [W] for a monostatic radar with the same antenna for transmit and receive."""
    if min(p_tx_w, frequency_hz, rcs_m2, range_m) <= 0:
        raise ValueError("power, frequency, RCS and range must be > 0")
    lam = C / frequency_hz
    g = 10 ** (gain_dbi / 10)
    return (p_tx_w * g * g * lam ** 2 * rcs_m2 * propagation_factor ** 4
            / ((4 * math.pi) ** 3 * range_m ** 4 * 10 ** (losses_db / 10)))


def psr_snr(p_tx_w: float, gain_dbi: float, frequency_hz: float, rcs_m2: float, range_m: float,
            bandwidth_hz: float, noise_figure_db: float, losses_db: float = 0.0, n_coherent: int = 1) -> float:
    """Linear SNR of one dwell (``n_coherent`` pulses integrated coherently)."""
    pr = psr_received_power(p_tx_w, gain_dbi, frequency_hz, rcs_m2, range_m, losses_db)
    return n_coherent * pr / thermal_noise_power(bandwidth_hz, noise_figure_db)


@cite("mathworks_albersheim", "richards_2005_radar",
      note="SNR_dB = -5 log10 N + (6.2 + 4.54 / sqrt(N + 0.44)) log10(A + 0.12 A B + 1.7 B)")
def albersheim_snr_db(pd: float, pfa: float, n: int = 1) -> float:
    """Required single-sample SNR [dB] for ``pd`` at ``pfa`` with ``n`` noncoherently integrated samples
    (nonfluctuating target, linear detector)."""
    if not (0 < pd < 1 and 0 < pfa < 1 and n >= 1):
        raise ValueError("0 < pd, pfa < 1 and n >= 1")
    a = math.log(0.62 / pfa)
    b = math.log(pd / (1 - pd))
    return -5 * math.log10(n) + (6.2 + 4.54 / math.sqrt(n + 0.44)) * math.log10(a + 0.12 * a * b + 1.7 * b)


def threshold_pfa(pfa: float) -> float:
    """Envelope threshold (noise std per quadrature = 1) giving ``pfa``: Pfa = exp(-T^2 / 2)."""
    return math.sqrt(-2 * math.log(pfa))


def pd_nonfluctuating(snr_linear: float, pfa: float) -> float:
    """Exact single-pulse Pd for a steady target (Swerling 0), envelope detector.

    Derivation: with unit noise per quadrature the squared envelope is non-central chi-square with 2 degrees of
    freedom and non-centrality 2 SNR; Pd = P(chi2' > T^2) (Marcum Q1). No literature value is used.
    """
    return float(stats.ncx2.sf(threshold_pfa(pfa) ** 2, 2, 2 * snr_linear))


def pd_swerling1(snr_linear: float, pfa: float) -> float:
    """Single-pulse Pd for a Rayleigh-fluctuating target (Swerling 1): Pd = Pfa^(1 / (1 + SNR)).

    Derivation: an exponentially distributed echo power plus noise is again exponential with mean (1 + SNR),
    so P(power > T) = exp(-T / (1 + SNR)) with exp(-T) = Pfa. Checked by Monte Carlo in the tests.
    """
    return pfa ** (1.0 / (1.0 + snr_linear))


def psr_range_for_pd(pd: float, pfa: float, ref_snr_linear: float, ref_range_m: float, swerling1: bool = True) -> float:
    """Range at which ``pd`` is reached, scaling a reference SNR with R^-4."""
    if swerling1:
        need = math.log(pfa) / math.log(pd) - 1.0
    else:
        need = 10 ** (albersheim_snr_db(pd, pfa) / 10)
    return ref_range_m * (ref_snr_linear / need) ** 0.25


@cite("wikipedia_radar_horizon", note="D = sqrt(2 k R_e h) per end, k = 4/3 for standard refraction")
def radar_horizon_m(h_radar_m: float, h_target_m: float = 0.0, k: float = K_EFFECTIVE_EARTH) -> float:
    """Line-of-sight range [m] between a radar at ``h_radar_m`` and a target at ``h_target_m`` (smooth earth)."""
    if h_radar_m < 0 or h_target_m < 0:
        raise ValueError("heights must be >= 0")
    re = k * R_EARTH
    return math.sqrt(2 * re * h_radar_m) + math.sqrt(2 * re * h_target_m)


@dataclass(frozen=True)
class SsrLink:
    """Both legs of an SSR exchange at one range."""

    range_m: float
    uplink_dbm: float           # interrogation power at the transponder antenna port
    uplink_margin_db: float     # over the transponder minimum triggering level
    downlink_dbm: float         # reply power at the ground receiver
    downlink_snr_db: float
    downlink_margin_db: float   # over the ground receiver sensitivity


def _dbm(p_w: float) -> float:
    return 10 * math.log10(p_w * 1e3)


def ssr_link(range_m: float, *, interrogator_w: float = 1000.0, ground_gain_dbi: float = 27.0,
             transponder_w: float = 250.0, aircraft_gain_dbi: float = 0.0, cable_losses_db: float = 3.0,
             transponder_mtl_dbm: float = -74.0, ground_sensitivity_dbm: float = -84.0,
             receiver_bw_hz: float = 8e6, receiver_nf_db: float = 4.0) -> SsrLink:
    """Uplink (1030 MHz) and downlink (1090 MHz) budget of one SSR exchange.

    All defaults are illustrative [Y] values for a demonstration, not equipment data; pass real ones when known.
    """
    up = friis_received_power(interrogator_w, ground_gain_dbi, aircraft_gain_dbi, 1030e6, range_m, cable_losses_db)
    down = friis_received_power(transponder_w, aircraft_gain_dbi, ground_gain_dbi, 1090e6, range_m, cable_losses_db)
    noise = thermal_noise_power(receiver_bw_hz, receiver_nf_db)
    return SsrLink(range_m, _dbm(up), _dbm(up) - transponder_mtl_dbm, _dbm(down), 10 * math.log10(down / noise),
                   _dbm(down) - ground_sensitivity_dbm)


def hits_per_scan(prf_hz: float, beamwidth_deg: float, scan_period_s: float) -> float:
    """Interrogations falling inside the 3 dB beam during one antenna sweep: PRF x dwell time."""
    return prf_hz * beamwidth_deg / (360.0 / scan_period_s)


def pd_m_of_n(p_single: float, n: int, m: int) -> float:
    """Probability that at least ``m`` of ``n`` independent replies are received (sliding-window detector)."""
    return float(stats.binom.sf(m - 1, n, p_single))


@cite("wikipedia_ssr_2026", note="garble = overlapping FRUIT; a Mode A/C reply lasts 20.3 us (+ SPI)")
def fruit_free_probability(fruit_rate_per_s: float, reply_length_us: float = 20.3) -> float:
    """Probability that no unsynchronised reply overlaps a wanted reply (Poisson FRUIT, overlap window 2 x length)."""
    return math.exp(-fruit_rate_per_s * 2 * reply_length_us * 1e-6)


def coverage_table(ranges_nm: np.ndarray, **kw: float) -> list[dict]:
    """SSR link margins over a range sweep (for the report)."""
    rows = []
    for r_nm in ranges_nm:
        lk = ssr_link(float(r_nm) * 1852.0, **kw)
        rows.append({"range_nm": float(r_nm), "uplink_margin_db": lk.uplink_margin_db,
                     "downlink_margin_db": lk.downlink_margin_db, "downlink_snr_db": lk.downlink_snr_db})
    return rows


__all__ += ["coverage_table"]
