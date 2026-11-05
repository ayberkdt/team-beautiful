"""Temperature-aware fatigue screening of the bracket (limit-load cycles 0 → σ, R = 0) with knock-downs.

Corrected endurance amplitude (fully reversed):  Se(T) = Se,ref(R = −1) · k_surface · k_T
Applied equivalent amplitude:                    σar = max(Goodman with Ftu(T), SWT)   for σa = σm = σ/2
Margin:                                           Se(T) / σar   (> 1: the limit-load cycle is below the endurance)

* σ is the FE von Mises stress at limit load outside the hole zones (T10 where verified). It already contains the
  geometric stress concentration Kt of the FE model; the notch sensitivity is taken as q = 1 (Kf = Kt) — the
  conservative end [Y]: no Peterson/Neuber constant was read for these alloys.
* Se,ref: the material's endurance value and its test condition (R, cycles, surface) from :data:`ENDURANCE`;
  an R = 0.1 amplitude is converted to R = −1 with Goodman at room temperature [Y method choice].
* k_T: steel → Marin kd(T) (Budynas & Nisbett Sec. 6-9 polynomial, steels 40–540 °C, :func:`marin_kd`); other
  alloys → Ftu(T)/Ftu(20 °C) of our strength curves (endurance assumed to follow the ultimate strength) [Y].
* k_surface: AM parts keep the as-built surface except at machined bores; ratios as-built / machined from the same
  study (research_notes/Üç sapma alanı/A_titresim_yorulma.md §1–§2) where the reference was machined; 1 where the
  reference already is as-built or the part is machined (steel baseline).

A screening, not a fatigue analysis: no load spectrum, no damage sum, no residual stress or porosity statistics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aerokit.bracket import matdata
from aerokit.references import cite
from aerokit.structures.fatigue import equivalent_fully_reversed, marin_kd

__all__ = ["Endurance", "ENDURANCE", "screen", "markdown"]

_NOTE = "research_notes/Üç sapma alanı/A_titresim_yorulma.md"


@dataclass
class Endurance:
    value_Pa: float          # amplitude at the stated R and cycles
    R: float
    cycles: float
    surface: str             # surface of the reference specimens
    source: str
    tag: str
    k_surface: float         # factor to the bracket's (as-built AM / machined plate) surface
    k_surface_source: str


ENDURANCE: dict[str, Endurance] = {
    "structural_steel": Endurance(
        86.2e6, -1.0, 1e6, "ASME BPV VIII-2 design curve (smooth bar data with design margins)",
        "Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean", "D", 1.0,
        "machined from plate: reference surface kept [Y]"),
    "ti64_lpbf": Endurance(
        600e6, -1.0, 1e7, "milled + HIP 920 °C / 100 MPa",
        "pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3", "S", 175.0 / 600.0,
        f"HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), {_NOTE} §2 [S, ratio Y]"),
    "scalmalloy": Endurance(
        87e6, 0.1, 1e7, "turned, 325 °C / 4 h",
        "Musekamp et al. 2021, Metals 11:1961, Fig. 8 p. 11 (σa, R = 0.1)", "D", 41.0 / 87.0,
        f"as-built / turned, same study (Musekamp 41/87 MPa, R = 0.1), {_NOTE} §1b [D, ratio Y]"),
    "in718_lpbf": Endurance(
        298e6, -1.0, 1e7, "wrought STA (no L-PBF value found)",
        "pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7", "Y", 0.42,
        "no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]"),
}
"""Endurance references per pool material; 17-4PH has none (screen reports 'no data')."""


def _k_T(key: str, T: float) -> tuple[float, str, str]:
    m = matdata.get(key)
    if key == "structural_steel":
        return float(marin_kd(T)), "Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels)", "D"
    return m.Ftu_at(T) / m.Ftu_at(20.0), "Ftu(T)/Ftu(20 °C) of our strength curve", "Y"


@cite("budynas_nisbett_2015", "smith_watson_topper_1970", note="Marin kd, Goodman; SWT; knock-downs from the pool notes")
def screen(key: str, sigma_limit_Pa: float, T: float) -> dict[str, Any]:
    """Screening row for one material at limit-load stress ``sigma_limit_Pa`` and temperature ``T`` [°C]."""
    m = matdata.get(key)
    e = ENDURANCE.get(key)
    if e is None:
        return {"key": key, "material": m.name, "status": "no data", "note": "no endurance value in our sources"}
    Sut20 = m.Ftu_at(20.0)
    se_ref = e.value_Pa
    if e.R != -1.0:                                           # R = 0.1 amplitude → R = −1 (Goodman, 20 °C)
        sm = e.value_Pa * (1 + e.R) / (1 - e.R)
        se_ref = equivalent_fully_reversed(e.value_Pa, sm, "goodman", Sut=Sut20)
    kT, kT_src, kT_tag = _k_T(key, T)
    se = se_ref * e.k_surface * kT
    s = float(sigma_limit_Pa)
    try:
        good = equivalent_fully_reversed(s / 2, s / 2, "goodman", Sut=m.Ftu_at(T))
    except ValueError:
        good = float("inf")
    swt = equivalent_fully_reversed(s / 2, s / 2, "swt")
    sar = max(good, swt)
    return {"key": key, "material": m.name, "status": "ok" if se >= sar else "below", "sigma_limit_Pa": s,
            "se_ref_R-1_Pa": se_ref, "k_surface": e.k_surface, "k_T": kT, "se_T_Pa": se, "sigma_ar_goodman_Pa": good,
            "sigma_ar_swt_Pa": swt, "sigma_ar_Pa": sar, "margin": se / sar if sar > 0 else float("inf"),
            "margin_machined": se / e.k_surface / sar if sar > 0 else float("inf"),
            "cycles": e.cycles, "sources": {"endurance": f"{e.source} [{e.tag}]", "surface": e.k_surface_source,
                                            "temperature": f"{kT_src} [{kT_tag}]",
                                            "notch": "FE stress includes Kt; q = 1 (Kf = Kt) [Y]"}}


def markdown(rows: list[dict[str, Any]], T: float) -> str:
    s = (f"### Life screening at {T:g} °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)\n\n"
         "Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; "
         "σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the "
         "endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).\n\n"
         "| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | "
         "Margin | Margin, machined surface |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        if r["status"] == "no data":
            s += f"| {r['material'].split(' (')[0]} | {r.get('design', '—')} | — | — | — | — | — | — | {r['note']} | — |\n"
            continue
        s += (f"| {r['material'].split(' (')[0]} | {r.get('design', '—')} | {r['sigma_limit_Pa'] / 1e6:.4g} | "
              f"{r['se_ref_R-1_Pa'] / 1e6:.4g} | {r['k_surface']:.2f} | {r['k_T']:.3f} | {r['se_T_Pa'] / 1e6:.4g} | "
              f"{r['sigma_ar_Pa'] / 1e6:.4g} | {r['margin']:.2f} | {r['margin_machined']:.2f} |\n")
    srcs: dict[str, str] = {}
    for r in rows:
        for k, v in (r.get("sources") or {}).items():
            srcs.setdefault(f"{r['material'].split(' (')[0]} — {k}", v)
    s += "\nSources: " + "; ".join(f"{k}: {v}" for k, v in srcs.items()) + "\n\n"
    return s
