"""Primary-radar signal processing on a range x azimuth x pulse grid: why MTI / MTD / CFAR / clutter maps exist.

One antenna scan is simulated at the I/Q level: every resolution cell gets a burst of ``n_pulses`` complex samples
(the coherent processing interval, CPI) of receiver noise, ground clutter, a wind-farm patch and aircraft echoes.
Four processing chains turn that into plots:

``fixed``      non-coherent integration of the burst, fixed threshold set for thermal noise only (legacy video)
``mti``        3-pulse canceller (1, -2, 1) -> integration -> cell-averaging CFAR along range
``mtd``        Doppler filter bank (windowed FFT over the burst) -> CA-CFAR per Doppler bin
``mtd_cmap``   MTD + a recursive **clutter map** per cell and Doppler bin (learns where clutter lives, scan by scan)

Sources and what is assumed:

* MTI cancels returns whose phase does not change from pulse to pulse; radial speeds whose phase turns a multiple of
  360 deg per pulse interval are blind (v_blind = lambda PRF / 2); phase jitter and clutter motion limit sub-clutter
  visibility to about 25 dB (Wikipedia "Moving target indication", read 2026-11-04).
* CA-CFAR estimates the noise floor from cells around the cell under test, skipping guard cells (Wikipedia "Constant
  false alarm rate", read 2026-11-04). The threshold multiplier for square-law detection of exponential noise with N
  reference cells, alpha = N (Pfa^(-1/N) - 1), is *derived* here (Pfa = E[exp(-alpha Z/N)] = (1 + alpha/N)^-N for
  Z ~ Gamma(N)) and checked by Monte Carlo in the tests.
* The sponsor's own PSR processing lists a 16-bin MTD, CFAR and wind-farm clutter handling (research note
  S_intersoft_ngsp_intro.md / S_intersoft_processing_whitepaper.md [D-ag]); our chains are teaching-size versions.
* Every clutter level, spectrum and patch below is an assumption [Y] chosen to show the mechanisms, not site data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from aerokit.references import cite

__all__ = ["PsrGrid", "ClutterScene", "Echo", "synthesize_scan", "cfar_alpha", "ca_cfar", "mti3", "mtd_bank",
           "ClutterMap", "process_scan", "Detection", "CHAINS", "blind_speed"]

C = 299_792_458.0
NM = 1852.0
CHAINS = ("fixed", "mti", "mtd", "mtd_cmap")


@dataclass(frozen=True)
class PsrGrid:
    """Resolution grid and waveform [Y]: 0.1 NM range bins to 60 NM, 300 azimuth cells (1.2 deg), 16 pulses/CPI."""

    range_bin_m: float = 0.1 * NM
    n_range: int = 600
    n_az: int = 300
    n_pulses: int = 16
    prf_hz: float = 1000.0
    freq_hz: float = 2.8e9

    @property
    def wavelength(self) -> float:
        return C / self.freq_hz

    @property
    def az_bin_deg(self) -> float:
        return 360.0 / self.n_az


@cite("wikipedia_mti_2026", note="blind radial speed: phase advances 360 deg per pulse interval")
def blind_speed(grid: PsrGrid) -> float:
    """First blind radial speed [m/s] of a constant-PRF MTI/MTD: lambda PRF / 2."""
    return grid.wavelength * grid.prf_hz / 2


@dataclass
class ClutterScene:
    """Fixed clutter of the site [Y]: a terrain region (near-zero Doppler) and a wind farm (Doppler spread)."""

    terrain_cnr_db: float = 45.0           # per-pulse clutter-to-noise ratio of a terrain cell (mean)
    terrain_fraction: float = 0.35         # share of cells inside the terrain region that carry clutter
    terrain_box: tuple[float, float, float, float] = (1.0, 12.0, 180.0, 330.0)   # NM min/max, az min/max deg
    jitter: float = 0.003                  # pulse-to-pulse amplitude decorrelation, -50 dB (limits MTI improvement)
    windfarm_cnr_db: float = 30.0
    windfarm_cells: tuple[tuple[int, int], ...] = ((150, 30), (151, 30), (152, 31), (150, 31), (153, 31))
    seed: int = 11
    _terrain: np.ndarray | None = field(default=None, repr=False)

    def terrain_power(self, grid: PsrGrid) -> np.ndarray:
        """Mean per-pulse clutter power per (range, az) cell; fixed for the site (drawn once)."""
        if self._terrain is None:
            rng = np.random.default_rng(self.seed)
            r = (np.arange(grid.n_range) + 0.5) * grid.range_bin_m / NM
            a = (np.arange(grid.n_az) + 0.5) * grid.az_bin_deg
            rr, aa = np.meshgrid(r, a, indexing="ij")
            r0, r1, a0, a1 = self.terrain_box
            inside = (rr >= r0) & (rr <= r1) & (aa >= a0) & (aa <= a1)
            on = inside & (rng.random(inside.shape) < self.terrain_fraction)
            p = np.zeros(inside.shape)
            p[on] = 10 ** (self.terrain_cnr_db / 10) * rng.lognormal(0.0, 1.0, int(on.sum()))
            self._terrain = p
        return self._terrain


@dataclass(frozen=True)
class Echo:
    """An aircraft echo for one scan."""

    range_m: float
    az_deg: float
    radial_speed_mps: float          # + receding
    snr_per_pulse: float             # mean, linear (Swerling 1: power exponential around it)


def synthesize_scan(grid: PsrGrid, scene: ClutterScene, echoes: list[Echo], rng: np.random.Generator) -> np.ndarray:
    """Complex I/Q cube [range, az, pulse] for one scan: unit-power noise + clutter + echoes."""
    nr, na, npl = grid.n_range, grid.n_az, grid.n_pulses
    z = (rng.standard_normal((nr, na, npl)) + 1j * rng.standard_normal((nr, na, npl))) * math.sqrt(0.5)
    z = z.astype(np.complex64)
    pc = scene.terrain_power(grid)
    ir, ia = np.nonzero(pc)
    if ir.size:
        scint = rng.lognormal(0.0, 0.25, ir.size)                       # scan-to-scan scintillation
        amp = np.sqrt(pc[ir, ia] * scint)
        ph = np.exp(1j * rng.uniform(0, 2 * np.pi, ir.size))
        jit = scene.jitter * (rng.standard_normal((ir.size, npl)) + 1j * rng.standard_normal((ir.size, npl)))
        z[ir, ia, :] += (amp * ph)[:, None] * (1.0 + jit)
    n = np.arange(npl)
    for (cr, ca) in scene.windfarm_cells:
        if cr < nr and ca < na:
            f = rng.uniform(-0.5, 0.5, 3) * grid.prf_hz                   # blade returns spread over the Doppler band
            sig = sum(np.exp(1j * (2 * np.pi * fk * n / grid.prf_hz + rng.uniform(0, 2 * np.pi))) for fk in f)
            z[cr, ca, :] += math.sqrt(10 ** (scene.windfarm_cnr_db / 10) / 3) * sig
    for e in echoes:
        cr, ca = int(e.range_m / grid.range_bin_m), int((e.az_deg % 360) / grid.az_bin_deg) % na
        if not 0 <= cr < nr:
            continue
        a = math.sqrt(rng.exponential(e.snr_per_pulse)) * np.exp(1j * rng.uniform(0, 2 * np.pi))
        fd = 2 * e.radial_speed_mps / grid.wavelength
        z[cr, ca, :] += a * np.exp(1j * 2 * np.pi * fd * n / grid.prf_hz)
    return z


def cfar_alpha(pfa: float, n_ref: int) -> float:
    """CA-CFAR multiplier for square-law exponential noise: alpha = N (Pfa^(-1/N) - 1) (derived; see module doc)."""
    return n_ref * (pfa ** (-1.0 / n_ref) - 1.0)


@cite("wikipedia_cfar_2026", note="cell averaging around the cell under test, guard cells excluded")
def ca_cfar(power: np.ndarray, pfa: float = 1e-6, n_ref: int = 16, n_guard: int = 2, looks: int = 1) -> np.ndarray:
    """Boolean detections of a cell-averaging CFAR along axis 0 (range), ``n_ref`` reference cells split evenly
    before and after the cell under test, ``n_guard`` guard cells on each side.

    ``looks`` = number of independent exponential samples averaged into each cell. The cell-under-test / reference-
    mean ratio of noise is then F(2L, 2NL)-distributed, so the threshold is its upper ``pfa`` quantile; for L = 1 this
    equals :func:`cfar_alpha` (checked in the tests)."""
    half = n_ref // 2
    k = np.zeros(2 * (half + n_guard) + 1)
    k[:half] = 1.0
    k[-half:] = 1.0
    pad = half + n_guard
    p = np.pad(power, [(pad, pad)] + [(0, 0)] * (power.ndim - 1), mode="reflect")
    cs = np.cumsum(p, axis=0)
    cs = np.concatenate([np.zeros((1,) + cs.shape[1:]), cs], axis=0)
    n = power.shape[0]
    lead = cs[half:half + n] - cs[0:n]                                   # cells [i-pad, i-pad+half)
    lag = cs[2 * pad + 1:2 * pad + 1 + n] - cs[2 * pad + 1 - half:2 * pad + 1 - half + n]
    noise = (lead + lag) / (2 * half)
    if looks == 1:
        thr = cfar_alpha(pfa, 2 * half)
    else:
        from scipy import stats
        thr = float(stats.f.isf(pfa, 2 * looks, 2 * looks * 2 * half))
    return power > thr * noise


@cite("wikipedia_mti_2026", note="successive pulses subtracted: stationary returns cancel")
def mti3(z: np.ndarray) -> np.ndarray:
    """3-pulse canceller (1, -2, 1) along the pulse axis; output has n_pulses - 2 samples."""
    return z[..., 2:] - 2 * z[..., 1:-1] + z[..., :-2]


def mtd_bank(z: np.ndarray) -> np.ndarray:
    """Doppler filter bank: Blackman-Harris-windowed FFT over pulses (low sidelobes, so strong zero-Doppler clutter does
    not leak into the moving-target bins); returns power [range, az, bin] normalised to unit noise per bin."""
    from scipy.signal.windows import blackmanharris
    w = blackmanharris(z.shape[-1]).astype(np.float32)
    spec = np.fft.fft(z * w, axis=-1)
    return (np.abs(spec) ** 2 / np.sum(w ** 2)).astype(np.float32)


@dataclass
class ClutterMap:
    """Recursive average of filter output power per cell and Doppler bin: m <- (1 - g) m + g p, updated every scan."""

    gain: float = 0.2
    m: np.ndarray | None = None

    def threshold_ok(self, p: np.ndarray, factor: float) -> np.ndarray:
        """True where the cell is NOT explained by learnt clutter (p > factor x map)."""
        if self.m is None:
            return np.ones(p.shape, bool)
        return p > factor * self.m

    def update(self, p: np.ndarray) -> None:
        self.m = p.copy() if self.m is None else (1 - self.gain) * self.m + self.gain * p


@dataclass(frozen=True)
class Detection:
    range_m: float
    az_deg: float
    cells: int
    peak: float


def _cluster(det: np.ndarray, power: np.ndarray, grid: PsrGrid) -> list[Detection]:
    """Group detected cells that touch (8-neighbourhood, azimuth wraps) into plots at the power-weighted centroid."""
    from scipy import ndimage
    lab, n = ndimage.label(det, structure=np.ones((3, 3)))
    if n == 0:
        return []
    out = []
    idx = ndimage.find_objects(lab)
    for k, sl in enumerate(idx, start=1):
        if sl is None:
            continue
        sub = lab[sl] == k
        pw = power[sl] * sub
        rr, aa = np.nonzero(sub)
        wts = pw[rr, aa]
        r = (sl[0].start + np.average(rr, weights=wts) + 0.5) * grid.range_bin_m
        a = (sl[1].start + np.average(aa, weights=wts) + 0.5) * grid.az_bin_deg
        out.append(Detection(float(r), float(a % 360), int(sub.sum()), float(wts.max())))
    return out


def process_scan(z: np.ndarray, grid: PsrGrid, chain: str, cmap: ClutterMap | None = None, pfa: float = 1e-6,
                 min_range_nm: float = 0.5) -> list[Detection]:
    """Run one processing chain on a scan cube and return plots."""
    if chain not in CHAINS:
        raise ValueError(f"chain must be one of {CHAINS}")
    if chain == "fixed":
        p = np.mean(np.abs(z) ** 2, axis=-1)
        n = z.shape[-1]
        # Gamma(n, 1/n) noise; threshold for pfa via the Wilson-Hilferty approximation of the chi-square quantile
        from scipy import stats
        thr = stats.gamma.isf(pfa, n, scale=1.0 / n)
        det = p > thr
        power = p
    elif chain == "mti":
        y = mti3(z)
        power = np.mean(np.abs(y) ** 2, axis=-1) / 6.0                   # (1,-2,1) has noise gain 6
        # n-2 canceller outputs overlap 3 pulses each -> about (n-2)/3 independent looks [Y]
        det = ca_cfar(power, pfa, looks=max(1, (z.shape[-1] - 2) // 3))
    else:
        spec = mtd_bank(z)
        det_b = ca_cfar(spec, pfa)
        nb = spec.shape[-1]
        zero = np.zeros(nb, bool)
        # zero-velocity filters: bins 0, +-1, +-2, +-3 -- the Blackman-Harris main lobe is about +-4 bins wide for
        # 16 pulses, so strong clutter fills +-3 bins (found when +-1 left ~200 false plots per scan)
        zero[[0, 1, 2, 3, nb - 3, nb - 2, nb - 1]] = True
        if chain == "mtd":
            det_b[..., zero] = False                                     # plain MTD: notch the zero-Doppler bins
        else:
            if cmap is None:
                raise ValueError("mtd_cmap needs a ClutterMap")
            # zero bins: clutter map instead of the notch (targets over clear ground stay visible); all bins:
            # anything the map has learnt as persistent (wind farm, jitter residue of strong clutter) is rejected
            det_b &= cmap.threshold_ok(spec, factor=-math.log(pfa))
            cmap.update(spec)
        det = det_b.any(axis=-1)
        power = spec.max(axis=-1)
    det[: int(min_range_nm * NM / grid.range_bin_m), :] = False
    return _cluster(det, power, grid)
