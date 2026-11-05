"""Tests of aerokit.aero.stability: DATCOM slope (VT AOE 3104 answers), Raymer Table 6.4, neutral-point derivations."""
import math

from aerokit.aero import stability as St
from aerokit.verification import check, check_true, expect_error

VT5 = "VT AOE 3104 (Lutze) Problem Sheet 5 answer, 2003, DATCOM liftcurve table"
VT4 = "VT AOE 3104 (Lutze) Problem Sheet 4 answer, 2003, question 21"
MIT = "MIT 16.333 (How) Fall 2004 Lecture 2, pp. 2-6…2-10"
R64 = "Raymer 1992 Table 6.4, Scholz HAW TN TailSizing 2013 Table 2.3/2.4 pp. 51–52"


def test_datcom():
    check("DATCOM A = 4, Λ½ = 45°, M = 0 → 3.1416", St.CLa_datcom(4, 45, 0.0), 3.1416, rtol=2e-5, source=VT5)
    check("DATCOM A = 4, Λ½ = 45°, M = 0.5 → 3.2824", St.CLa_datcom(4, 45, 0.5), 3.2824, rtol=2e-5, source=VT5)
    check("DATCOM A = 4, Λ½ = 45°, M = 0.95 → 3.7832", St.CLa_datcom(4, 45, 0.95), 3.7832, rtol=2e-5, source=VT5)
    check("DATCOM A = 4, Λ½ = 0°, M = 0.7 → 4.5803", St.CLa_datcom(4, 0, 0.7), 4.5803, rtol=2e-5, source=VT5)
    check("DATCOM A = 4, Λ½ = 30°, M = 0.7 → 4.0651", St.CLa_datcom(4, 30, 0.7), 4.0651, rtol=2e-5, source=VT5)
    check("DATCOM A = 4, Λ½ = 75°, M = 0.7 → 1.4502", St.CLa_datcom(4, 75, 0.7), 1.4502, rtol=5e-5, source=VT5)
    check("sweep Λ_LE 30°, λ 0.5, A 6 → Λ½ = 24.997°", St.transform_sweep(30, 15 ** 2 / 37.5, 0.5, 0, 0.5),
          24.997, rtol=2e-5, source=VT4)
    check("sweep round trip ¼ → ½ → ¼", St.transform_sweep(St.transform_sweep(20, 8, 0.4, .25, .5), 8, 0.4,
                                                           .5, .25), 20.0, rtol=1e-12, source="derivation")
    check("A → ∞: CLα → cla (2-D)", St.CLa_datcom(1e7, 0, 0, 6.0), 6.0, rtol=1e-5, source="derivation: limit")
    check("A → 0: CLα → πA/2 (slender wing)", St.CLa_datcom(1e-4, 0, 0), math.pi * 1e-4 / 2, rtol=1e-6,
          source="derivation: limit (same as Jones slender-wing theory)")
    expect_error("M ≥ 1 raises", St.CLa_datcom, 6, 0, 1.0, error=ValueError)
    expect_error("A ≤ 0 raises", St.CLa_datcom, 0, 0, 0.3, error=ValueError)


def test_downwash():
    A = 8.0
    CLa_ll = 2 * math.pi * A / (A + 2)           # lifting line, elliptic
    check("dε/dα = 2CLα/(πA) → 4/(A+2) for elliptic", St.downwash_gradient(CLa_ll, A), 4 / (A + 2),
          rtol=1e-12, source=MIT + " + derivation")
    check("dε/dα formula", St.downwash_gradient(5.0, 7.0), 10 / (7 * math.pi), rtol=1e-12, source=MIT)


def test_tail_volume():
    check("Raymer GA single engine C_HT = 0.70", St.tail_volume("GA single engine")[0], 0.70, source=R64)
    check("Raymer GA single engine C_VT = 0.04", St.tail_volume("GA single engine")[1], 0.04, source=R64)
    check("Raymer GA twin engine C_HT = 0.80", St.tail_volume("GA twin engine")[0], 0.80, source=R64)
    check("Raymer GA twin engine C_VT = 0.07", St.tail_volume("GA twin engine")[1], 0.07, source=R64)
    check("Raymer sailplane C_HT = 0.50", St.tail_volume("sailplane")[0], 0.50, source=R64)
    check("Raymer sailplane C_VT = 0.02", St.tail_volume("sailplane")[1], 0.02, source=R64)
    check("Raymer jet transport C_HT = 1.00", St.tail_volume("jet transport")[0], 1.00, source=R64)
    check("Raymer jet transport C_VT = 0.09", St.tail_volume("jet transport")[1], 0.09, source=R64)
    check("Raymer jet fighter C_HT = 0.40", St.tail_volume("jet fighter")[0], 0.40, source=R64)
    check("Raymer twin turboprop C_VT = 0.08", St.tail_volume("twin turboprop")[1], 0.08, source=R64)
    S_h = St.horizontal_tail_area(0.70, 4.5, 16.0, 1.45)
    check("horizontal tail sizing round trip", St.horizontal_volume_coefficient(S_h, 4.5, 16.0, 1.45), 0.70,
          rtol=1e-12, source="derivation: Scholz TN Eq. 2.7")
    S_v = St.vertical_tail_area(0.04, 4.8, 16.0, 11.0)
    check("vertical tail sizing round trip", St.vertical_volume_coefficient(S_v, 4.8, 16.0, 11.0), 0.04,
          rtol=1e-12, source="derivation: Scholz TN Eq. 2.6")
    check("S_H = C_HT·c̄·S/l (numerical)", S_h, 0.70 * 1.45 * 16 / 4.5, rtol=1e-12, source=R64)
    expect_error("unknown aircraft type raises", St.tail_volume, "airship", error=KeyError)
    expect_error("tail arm ≤ 0 raises", St.horizontal_tail_area, 0.7, 0.0, 16, 1.4, error=ValueError)


def test_neutral_point():
    CLaw, CLat, deda = 5.0, 4.0, 0.4
    np0 = St.neutral_point(0.25, CLaw, CLat, 0.0, 3.0, deda)
    check("tailless: NP = wing AC", np0["h_np"], 0.25, rtol=1e-12, source=MIT)
    n1 = St.neutral_point(0.25, CLaw, CLat, 0.15, 3.0, deda)
    n2 = St.neutral_point(0.25, CLaw, CLat, 0.25, 3.0, deda)
    check_true("NP moves aft as the tail grows", n2["h_np"] > n1["h_np"] > 0.25,
               f"{n1['h_np']:.4f} → {n2['h_np']:.4f}", source="derivation: h_NP is a weighted mean")
    expected = (5 * 0.25 + 0.15 * 4 * 0.6 * 3.0) / (5 + 0.15 * 4 * 0.6)
    check("NP numerical (weighted mean)", n1["h_np"], expected, rtol=1e-12, source=MIT)
    # CMα = CLαw(h − h_ac) − η V_H CLαt (1 − dε/dα) (MIT p. 2-8) must equal CLαT(h − h_NP)
    h = 0.30
    VH = 0.15 * (3.0 - h)
    Cma_direct = CLaw * (h - 0.25) - VH * CLat * (1 - deda)
    sm = St.static_margin(h, n1["h_np"], n1["CLa_T"])
    check("CMα = −CLαT·SM = direct sum", sm["Cma"], Cma_direct, rtol=1e-12, source=MIT + " p. 2-8 ↔ 2-9")
    check_true("h_cg < h_NP → stable", sm["stable"], source=MIT)
    ng = St.neutral_point(0.25, CLaw, CLat, 0.15, 3.0, deda, dCma_fuselage=0.2)
    check("fuselage ΔCMα moves NP forward by ΔCMα/CLαT", n1["h_np"] - ng["h_np"], 0.2 / n1["CLa_T"], rtol=1e-12,
          source="derivation")
    r = St.tail_size_sm(0.10, 0.30, 0.25, CLaw, CLat, 3.0, deda)
    check("SM-targeted tail sizing round trip", St.neutral_point(0.25, CLaw, CLat, r["St_S"], 3.0, deda)
          ["h_np"] - 0.30, 0.10, rtol=1e-9, source="derivation")
    check("NP: zero tail slope → NP = wing AC", St.neutral_point(0.27, CLaw, 0.0, 0.2, 3.0, deda)["h_np"], 0.27,
          rtol=1e-12, source="derivation")
    expect_error("dε/dα ≥ 1 raises", St.neutral_point, 0.25, 5, 4, 0.2, 3, 1.0, error=ValueError)
    expect_error("unreachable SM target raises", St.tail_size_sm, 5.0, 0.3, 0.25, 5, 4, 3.0, 0.4,
                 error=ValueError)


def test_trim():
    t = St.trim(0.5, -0.05, 0.30, 0.25, 0.18, 3.2, eta=0.9, CLt_max=0.6)
    check("trim: lift balance", t["CL_w"] + 0.9 * 0.18 * t["CL_t"], 0.5, rtol=1e-12, source="derivation")
    check("trim: moment balance = 0", -0.05 + t["CL_w"] * 0.05 - 0.9 * t["V_H"] * t["CL_t"], 0.0, atol=1e-14,
          source=MIT + " (CMt = −V_H η CLt)")
    t0 = St.trim(0.5, 0.0, 0.25, 0.25, 0.18, 3.2)
    check("h_cg = h_ac, Cm_ac = 0 → zero tail load", t0["CL_t"], 0.0, atol=1e-14, source="derivation")
    tb = St.trim(1.2, -0.12, 0.10, 0.25, 0.10, 3.0, CLt_max=0.5)
    check_true("trim limit exceeded at an extreme forward CG", not tb["trim_possible"], f"CL_t = {tb['CL_t']:.2f}",
               source="derivation: forward CG → larger tail load")
    expect_error("tail ahead of the CG raises", St.trim, 0.5, -0.05, 0.3, 0.25, 0.18, 0.2, error=ValueError)
