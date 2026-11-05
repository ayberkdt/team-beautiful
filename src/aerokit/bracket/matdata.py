"""Candidate bracket materials with temperature-dependent stiffness and strength (20 °C and the working temperature).

Each property is a :class:`Prop` with value, unit, source and tag:
``D`` read from the primary source in this repository (MIL-HDBK-5J curves digitised in
:mod:`aerokit.materials.curves`, the pool JSON of :mod:`aerokit.materials.pool`), ``D-ag`` read from the
primary source by a research sub-agent on 2026-11-04 (URL in the source string), ``S`` secondary, ``Y`` our
assumption or proxy. Values between the tabulated temperatures are interpolated linearly; nothing is extrapolated
beyond the last tabulated temperature (an error is raised).

The structural steel record is the Ansys Engineering Data default "Structural Steel" (the challenge baseline):
its room-temperature values were read from a Workbench 23.1 Engineering Data export; Ansys gives no temperature
dependence for it, so its 300 °C factors come from MIL-HDBK-5J low-alloy steel curves (typical, ½ h exposure) —
a proxy, stated as such. EN 1993-1-2 (fire design) factors are kept beside them for a sensitivity check.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from aerokit.materials import curves
from aerokit.references import cite

__all__ = ["Prop", "Material", "CANDIDATES", "get", "names", "factor_table"]

def F_OF_C(c: float) -> float:
    """Degrees Fahrenheit of a Celsius temperature."""
    return c * 9.0 / 5.0 + 32.0


@dataclass(frozen=True)
class Prop:
    value: float
    unit: str
    source: str
    tag: str


@dataclass
class Material:
    """One candidate: room-temperature properties plus multiplicative factors vs temperature [°C]."""

    key: str
    name: str
    family: str                         # eco family / class
    route: str                          # manufacturing route assumed for the bracket
    am: bool                            # 3-D printable by a qualified powder-bed route
    rho: Prop                           # kg/m3
    E: Prop                             # Pa (room temperature)
    nu: Prop
    Fty: Prop                           # Pa (room temperature, 0.2 % proof)
    Ftu: Prop                           # Pa
    Tmax: Prop                          # °C, maximum service temperature quoted by a source
    co2: Prop                           # kg CO2e / kg, primary production (cradle to gate)
    energy: Prop                        # MJ / kg, primary production
    co2_recycled: Prop | None = None
    energy_recycled: Prop | None = None
    recycle_fraction: Prop | None = None
    cte: Prop | None = None             # 1/K
    k: Prop | None = None               # W/(m K)
    cp: Prop | None = None              # J/(kg K)
    price: Prop | None = None           # EUR/kg (stock or powder)
    fatigue: Prop | None = None         # Pa, endurance / 1e7 cycles where known
    T: tuple[float, ...] = (20.0, 300.0)
    kE: tuple[float, ...] = (1.0, 1.0)
    kFty: tuple[float, ...] = (1.0, 1.0)
    kFtu: tuple[float, ...] = (1.0, 1.0)
    k_source: str = ""
    k_tag: str = "Y"
    notes: list[str] = field(default_factory=list)

    def _f(self, ks: tuple[float, ...], T: float) -> float:
        if not self.T[0] - 1e-9 <= T <= self.T[-1] + 1e-9:
            raise ValueError(f"{self.key}: {T} °C outside the tabulated range {self.T[0]}-{self.T[-1]} °C")
        return float(np.interp(T, self.T, ks))

    def E_at(self, T: float) -> float:
        return self.E.value * self._f(self.kE, T)

    def Fty_at(self, T: float) -> float:
        return self.Fty.value * self._f(self.kFty, T)

    def Ftu_at(self, T: float) -> float:
        return self.Ftu.value * self._f(self.kFtu, T)

    def summary(self, T: float) -> dict[str, Any]:
        return {"key": self.key, "name": self.name, "route": self.route, "am": self.am,
                "rho_kg_m3": self.rho.value, "E_GPa": self.E_at(T) / 1e9, "Fty_MPa": self.Fty_at(T) / 1e6,
                "Ftu_MPa": self.Ftu_at(T) / 1e6, "Tmax_C": self.Tmax.value, "co2_kg_per_kg": self.co2.value,
                "T_C": T}


@cite("mil_hdbk_5j_2003", note="effect-of-temperature figures at 572 °F (300 °C)")
def _mil(fig: str, label: str, T_C: float) -> float:
    """Fraction (not percent) of the room-temperature value read from a digitised MIL-HDBK-5J figure."""
    return curves.curve_value(fig, label, F_OF_C(T_C)) / 100.0


def _two(fig: str, label: str, T_rt_F: float = 70.0) -> tuple[float, float]:
    """(factor at 20 °C, factor at 300 °C) normalised so that 20 °C ≡ 1 (the figures read ~100 % at 70-75 °F)."""
    c = next(cv for cv in curves.load_curve(fig).curves if cv.label == label)
    rt = curves.curve_value(fig, label, max(T_rt_F, c.x_range[0])) / 100.0     # first digitised point if > 70 F
    return 1.0, _mil(fig, label, 300.0) / rt


_POOL = "materials_pool.json (aerokit.materials.pool, built 2026-11-03; see the record's source string)"
_ASHBY = "Ashby 2013 via 'Useful numbers for environmental studies' reproduction"
_STEEL_XML = ("Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager "
              "tests/data/steel_eglass_air.xml (local copy read 2026-11-04)")


def _p(v: float, unit: str, src: str, tag: str) -> Prop:
    return Prop(float(v), unit, src, tag)


def _pool(name: str, prop: str, scale: float = 1.0, unit: str = "") -> Prop:
    from aerokit.materials import pool
    rec = pool.get(name)["properties"][prop]
    return Prop(float(rec["value"]) * scale, unit or rec["unit"], f"pool '{name}': {rec['source']}", rec["tag"])


def _build() -> dict[str, Material]:
    m: dict[str, Material] = {}
    # ---------------------------------------------------------------- structural steel (baseline)
    kFty = _two("2.3.1.1.1", "Fty")
    kFtu = _two("2.3.1.1.1", "Ftu")
    kE = _two("2.3.1.1.4", "E & Ec")
    m["structural_steel"] = Material(
        "structural_steel", "Structural Steel (Ansys Engineering Data default)", "carbon_steel",
        "machined from plate / welded", False,
        rho=_p(7850, "kg/m3", _STEEL_XML, "D"), E=_p(200e9, "Pa", _STEEL_XML, "D"),
        nu=_p(0.3, "-", _STEEL_XML, "D"), Fty=_p(250e6, "Pa", _STEEL_XML, "D"),
        Ftu=_p(460e6, "Pa", _STEEL_XML, "D"),
        Tmax=_p(400, "C", "EN 1993-1-2 Table 3.1: k_y = 1.000 up to 400 C (fire design, 2 % strain) [D-ag]", "Y"),
        co2=_p(1.8, "kg/kg", f"{_ASHBY}: low-carbon steel primary 1.8 kg CO2/kg (Ashby pp. 463-469) [D-ag]",
               "D-ag"),
        energy=_p(26.5, "MJ/kg", f"{_ASHBY}: low-carbon steel primary 25-28 MJ/kg, midpoint", "D-ag"),
        cte=_p(1.2e-5, "1/K", _STEEL_XML, "D"), k=_p(60.5, "W/mK", _STEEL_XML, "D"),
        cp=_p(434, "J/kgK", _STEEL_XML, "D"),
        price=_p(0.77, "EUR/kg", "SMM news 2026-08-03: NW European S235 plate 888 USD/t = 770 EUR/t EXW "
                                 "(news.metal.com 104039523, opened by sub-agent) [D-ag]; S235 as the proxy grade", "D-ag"),
        fatigue=_p(86.2e6, "Pa", f"{_STEEL_XML}: S-N at 1e6 cycles, zero mean (ASME BPV VIII-2 Table 5-110.1)",
                   "D"),
        kE=kE, kFty=(1.0, 153.0 / 235.0), kFtu=kFtu,
        k_source="Fty: EN 10028-2 minimum Rp0.2 of P235GH (t <= 16 mm) 153 MPa at 300 C vs 235 MPa at RT, ratio "
                 "0.651 (Salzgitter reproduction, read by sub-agent 2026-11-04) [D-ag]; E and Ftu: MIL-HDBK-5J "
                 "Fig. 2.3.1.1.4 / 2.3.1.1.1 AISI low-alloy steels at 572 F (proxy) [D curve, Y use]",
        k_tag="D-ag/Y",
        notes=["EN 1993-1-2 Table 3.1 at 300 C: k_y 1.000, k_p 0.613, k_E 0.800 (fire design; sensitivity) [D-ag]",
               f"MIL-HDBK-5J low-alloy Fty factor at 572 F would be {kFty[1]:.3f} (heat-treated alloy steels; "
               "not used: less conservative than EN 10028-2 for a structural carbon steel)",
               "E(300 C) cross-check: ASME B31.1 carbon steel 29.5 -> 26.7 Msi (ratio 0.905) via Engineering "
               "ToolBox, column reading ambiguous [D-ag]",
               "Not normally made by powder-bed AM: baseline route is machining from plate [Y]"])
    # ---------------------------------------------------------------- 17-4PH (AM and wrought)
    kFty = _two("2.6.9.2.1", "unlabeled", 77.6)
    kFtu = _two("2.6.9.2.1", "Ftu", 90.7)
    kE = _two("2.6.9.1.4", "E & E_C")
    m["ss_17_4ph"] = Material(
        "ss_17_4ph", "17-4PH H1025 (wrought data; L-PBF route)", "stainless_steel", "AM L-PBF + H1025 + HIP", True,
        rho=_pool("17-4PH H1025", "rho"), E=_pool("17-4PH H1025", "E", 1e9, "Pa"),
        nu=_p(0.272, "-", "assumed typical for martensitic stainless", "Y"),
        Fty=_pool("17-4PH H1025", "Fty", 1e6, "Pa"), Ftu=_pool("17-4PH H1025", "Ftu", 1e6, "Pa"),
        Tmax=_pool("17-4PH H1025", "Tmax"), co2=_pool("17-4PH H1025", "co2"),
        energy=_p(84.5, "MJ/kg", f"{_ASHBY}: stainless steel 81-88 MJ/kg (eco.FAMILIES)", "D"),
        co2_recycled=_p(0.73, "kg/kg", f"{_ASHBY} (eco.FAMILIES stainless)", "D"),
        kE=kE, kFty=kFty, kFtu=kFtu,
        k_source="MIL-HDBK-5J Fig. 2.6.9.2.1 (17-4PH bar H900-H1075; the unlabeled curve is Fty by elimination) "
                 "and Fig. 2.6.9.1.4 (E of H900, proxy for H1025) at 572 F",
        k_tag="D",
        notes=["Wrought allowables used for the AM route; L-PBF 17-4PH needs HIP + H1025 to approach them [Y]",
               "Cleveland-Cliffs 17-4PH bulletin (2021): 'good mechanical properties at temperatures up to 600 F'; "
               "H1150 after 1000 h at 600 F tested at 600 F: YS 814 MPa, UTS 848 MPa [D-ag]",
               "E at 300 C ~175 GPa (AISI 630 sheet, snippet only) agrees with the MIL factor 0.88 [S]"])
    # ---------------------------------------------------------------- Ti-6Al-4V L-PBF
    kFty = _two("5.4.1.1.1", "F_ty", 70.0)
    kFtu = _two("5.4.1.1.1", "F_tu", 70.0)
    m["ti64_lpbf"] = Material(
        "ti64_lpbf", "Ti-6Al-4V (L-PBF, stress relieved / HIP)", "titanium_alloy", "AM L-PBF + HIP", True,
        rho=_pool("Ti-6Al-4V L-PBF", "rho"), E=_pool("Ti-6Al-4V L-PBF", "E", 1e9, "Pa"),
        nu=_p(0.31, "-", "typical Ti-6Al-4V (MIL-HDBK-5J Table 5.4.1.0(b) not read here)", "Y"),
        Fty=_pool("Ti-6Al-4V L-PBF", "Fty", 1e6, "Pa"), Ftu=_pool("Ti-6Al-4V L-PBF", "Ftu", 1e6, "Pa"),
        Tmax=_pool("Ti-6Al-4V L-PBF", "Tmax"), co2=_pool("Ti-6Al-4V L-PBF", "co2"),
        energy=_p(685, "MJ/kg", f"{_ASHBY}: titanium alloys 650-720 MJ/kg (eco.FAMILIES)", "D"),
        co2_recycled=_p(5.2, "kg/kg", f"{_ASHBY} (eco.FAMILIES titanium)", "D"),
        fatigue=_pool("Ti-6Al-4V L-PBF", "fatigue", 1e6, "Pa"),
        price=_p(70.6, "EUR/kg", "Santiago-Herrera et al. 2023, Sustainability, Table 3: gas-atomised Ti-6Al-4V "
                                 "powder production cost 70.6 EUR/kg (opened by sub-agent; table columns slightly garbled)",
                 "D-ag"),
        kE=(1.0, 0.88), kFty=kFty, kFtu=kFtu,
        k_source="MIL-HDBK-5J Fig. 5.4.1.1.1 (annealed wrought Ti-6Al-4V, 1/2 h) at 572 F for Fty/Ftu; "
                 "E(300 C)/E(RT) = 0.88: TIMET 6-4 sheet Table 2 gives 107-122 GPa at 20 C and 95-111 at 230 C "
                 "(ratio ~0.90 at 230 C, extrapolated ~0.88 at 300 C); laser-DED data (Ivanov 2021) give 0.97 "
                 "[D-ag, range]",
        k_tag="D/D-ag",
        notes=["Wrought-annealed temperature factors applied to L-PBF room-temperature values [Y]",
               "Fty factor cross-checks at 300 C: TIMET Fig. 1 plot ~640/910 = 0.70, laser-DED (Ivanov 2021 Table 1) "
               "~775/1000 = 0.78 by interpolation; MIL 0.63 kept (conservative) [D-ag]",
               "EOS Ti64 ELI sheet (2014): max long-term operating temperature approx. 350 C [D-ag]"])
    # ---------------------------------------------------------------- Inconel 718 L-PBF
    m["in718_lpbf"] = Material(
        "in718_lpbf", "Inconel 718 (L-PBF, solution + double age)", "nickel_superalloy", "AM L-PBF + STA", True,
        rho=_pool("Inconel 718 L-PBF", "rho"), E=_pool("Inconel 718 L-PBF", "E", 1e9, "Pa"),
        nu=_p(0.29, "-", "typical nickel superalloy", "Y"),
        Fty=_pool("Inconel 718 L-PBF", "Fty", 1e6, "Pa"), Ftu=_pool("Inconel 718 L-PBF", "Ftu", 1e6, "Pa"),
        Tmax=_pool("Inconel 718 L-PBF", "Tmax"), co2=_pool("Inconel 718 L-PBF", "co2"),
        energy=_p(232.5, "MJ/kg", f"{_ASHBY}: nickel superalloys 221-244 MJ/kg (eco.FAMILIES)", "D"),
        co2_recycled=_p(2.14, "kg/kg", f"{_ASHBY} (eco.FAMILIES nickel)", "D"),
        kE=(1.0, 184.0 / 200.0), kFty=(1.0, 156.0 / 163.0), kFtu=(1.0, 183.5 / 198.0),
        k_source="Special Metals INCONEL 718 bulletin (2007): Table 4 E 29.0 -> 26.7 Msi at 600 F; Table 19 "
                 "(hot-rolled, annealed + aged) YS 163.0 -> 156.0 ksi, UTS 198.0 -> 183.5 ksi at 600 F (316 C, "
                 "used for 300 C: slightly conservative) [D-ag]; wrought ratios applied to L-PBF [Y]",
        k_tag="D-ag")
    # ---------------------------------------------------------------- Scalmalloy (shows why Al fails at 300 C)
    m["scalmalloy"] = Material(
        "scalmalloy", "Scalmalloy (Al-Mg-Sc, L-PBF)", "aluminium", "AM L-PBF + age", True,
        rho=_pool("Scalmalloy L-PBF", "rho"), E=_pool("Scalmalloy L-PBF", "E", 1e9, "Pa"),
        nu=_p(0.33, "-", "typical aluminium", "Y"),
        Fty=_pool("Scalmalloy L-PBF", "Fty", 1e6, "Pa"), Ftu=_pool("Scalmalloy L-PBF", "Ftu", 1e6, "Pa"),
        Tmax=_p(150, "C", "pool notes: yield 319 MPa at 150 C (Colibrium sheet via build_studies.py)", "S"),
        co2=_pool("Scalmalloy L-PBF", "co2"),
        energy=_p(210, "MJ/kg", f"{_ASHBY}: aluminium 200-220 MJ/kg (eco.FAMILIES)", "D"),
        kE=(1.0, 29.0 / 69.0), kFty=(1.0, 60.0 / 490.0), kFtu=(1.0, 103.0 / 520.0),
        k_source="Colibrium M2 Series 5 Al-Mg-Sc CMDS Rev B (2025-08-21), elevated-temperature table, DA, "
                 "horizontal: 300 C E 29 GPa, YS 60 MPa, UTS 103 MPa (RT E 69 GPa) [D-ag]", k_tag="D-ag",
        notes=["Kept in the comparison to show the 300 C screen: Al alloys lose most of their strength [S]"])
    return m


CANDIDATES: dict[str, Material] = _build()


def get(key: str) -> Material:
    if key not in CANDIDATES:
        raise KeyError(f"unknown material {key!r}; choose from {', '.join(CANDIDATES)}")
    return CANDIDATES[key]


def names() -> list[str]:
    return list(CANDIDATES)


def factor_table(T: float = 300.0) -> list[dict[str, Any]]:
    """Room temperature vs ``T`` values of every candidate with the factor sources."""
    rows = []
    for mt in CANDIDATES.values():
        rows.append({**mt.summary(T), "E_RT_GPa": mt.E.value / 1e9, "Fty_RT_MPa": mt.Fty.value / 1e6,
                     "kE": mt.E_at(T) / mt.E.value, "kFty": mt.Fty_at(T) / mt.Fty.value,
                     "factor_source": mt.k_source, "factor_tag": mt.k_tag})
    return rows
