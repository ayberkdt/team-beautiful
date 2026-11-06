"""PREVIEW — geometry and loads only, no analysis. Deterministic checks of this package against what the film reads.

    python film_preview/validate_preview.py [--film-veri <copy>/film/veri/film-veri.json]

1. baslangic.stl: binary, triangles identical to the source (bytes 80..), closed 2-manifold (every undirected edge in
   exactly 2 triangles), consistently oriented (every directed edge once), outward (signed volume > 0), volume, bbox.
2. holes: setup holes vs derived/features.json (centre, diameter); ray-parity: every hole axis point is OUTSIDE the
   solid (it is a bore) and a point 5 mm beyond the bore wall is INSIDE (material around it).
3. yukler.json: every field hazirla.mjs reads (destekler silindir: merkez, eksen, yaricap, bas, son; kuvvetler: nokta,
   yon, buyukluk_N numeric) and an independent recomputation of direction / magnitude / moment from the set-up.
4. film.json: schema ansys-film/1, status not final, PREVIEW tag, no analysis numbers (materials names only, redesign /
   stress / density / print / eco null); lists every number the manifest carries.
5. (--film-veri) the output of a COPY of hazirla.mjs run on girdi.json: which shots the film skips, with the film's own
   rules (film/src/ana.mjs gerekVar, read 2026-11-05).
Exit 1 on any FAIL. Writes nothing; redirect stdout to keep a record.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASE = HERE.parent
fails: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def tri(p: Path) -> np.ndarray:
    b = p.read_bytes()
    n = struct.unpack_from("<I", b, 80)[0]
    check(len(b) == 84 + 50 * n, f"{p.name}: binary STL, {n} triangles, size {len(b)} = 84 + 50·n")
    rec = np.frombuffer(b, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
    return rec["v"].astype(np.float64)


def inside(T: np.ndarray, p) -> bool:
    """Ray parity along +x (Möller–Trumbore), slightly skewed ray to avoid edge hits."""
    o = np.asarray(p, float)
    d = np.array([1.0, 1.3e-5, 0.7e-5]); d /= np.linalg.norm(d)
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    h = np.cross(d, e2); a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-12
    f = np.where(ok, 1.0 / np.where(ok, a, 1.0), 0.0)
    s = o - v0; u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1); v = f * (q @ d); t = f * np.einsum("ij,ij->i", e2, q)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
    return bool(hit.sum() % 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--film-veri", default=None)
    g = ap.parse_args()
    film = json.loads((HERE / "film.json").read_text(encoding="utf-8"))
    girdi = json.loads((HERE / "girdi.json").read_text(encoding="utf-8"))
    L = json.loads((HERE / "yukler.json").read_text(encoding="utf-8"))
    setup = json.loads((CASE / "setup" / "setup_official_fixed_bores.json").read_text(encoding="utf-8"))
    feats = json.loads((CASE / "derived" / "features.json").read_text(encoding="utf-8"))

    print("1. baslangic.stl")
    T = tri(HERE / "baslangic.stl")
    src = CASE / film["_kaynak"]["baslangic.stl"]["source"]
    check((HERE / "baslangic.stl").read_bytes()[80:] == src.read_bytes()[80:], f"triangle payload identical to {src.relative_to(CASE).as_posix()}")
    P = T.reshape(-1, 3)
    key = np.round(P / 1e-4).astype(np.int64)                  # weld at 0.1 µm
    _, vid = np.unique(key, axis=0, return_inverse=True)
    F = vid.reshape(-1, 3)
    degen = int(((F[:, 0] == F[:, 1]) | (F[:, 1] == F[:, 2]) | (F[:, 0] == F[:, 2])).sum())
    check(degen == 0, f"degenerate triangles: {degen}")
    de = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    und = np.sort(de, axis=1)
    _, cu = np.unique(und, axis=0, return_counts=True)
    _, cd = np.unique(de, axis=0, return_counts=True)
    check(bool((cu == 2).all()), f"closed 2-manifold: {len(cu)} edges, open {(cu == 1).sum()}, >2 faces {(cu > 2).sum()}")
    check(bool((cd == 1).all()), f"consistent orientation: directed edges used twice {(cd > 1).sum()}")
    vol = float(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6.0)
    chi = len(np.unique(vid)) - len(cu) + len(F)
    print(f"        vertices {len(np.unique(vid))}, Euler characteristic {chi} (genus {(2 - chi) // 2}: 4 bolt bores + 2 pin bores -> 6 expected)")
    check(chi == 2 - 2 * 6, "topology: genus 6 (six through-holes)")
    check(vol > 0, f"outward normals: signed volume {vol / 1e9:.6f} m³")
    rho = film["_kaynak"]["baseline.mass_kg"]["density_kg_m3"]
    m = vol * 1e-9 * rho
    mo = film["baseline"]["mass_kg"]
    check(abs(m - mo) / mo < 0.005, f"volume × {rho:g} kg/m³ = {m:.3f} kg vs manifest baseline.mass_kg {mo:.3f} kg (organiser monitor), diff {100 * (m - mo) / mo:+.3f} %")
    lo, hi = P.min(0), P.max(0)
    ref_lo, ref_hi = [170.0, 30.0, 30.0], [831.01, 371.12, 321.37]   # setup/boundary_conditions.md §1
    check(np.allclose(lo, ref_lo, atol=0.05) and np.allclose(hi, ref_hi, atol=0.05),
          f"bbox [{', '.join(f'{v:.2f}' for v in lo)}] – [{', '.join(f'{v:.2f}' for v in hi)}] mm vs boundary_conditions.md §1")
    env = L["tasarim_alani"][0]
    check(np.allclose(env["min"], lo, atol=1e-3) and np.allclose(env["max"], hi, atol=1e-3), "yukler.json tasarim_alani = STL bbox")

    print("2. holes (setup vs features.json vs STL)")
    fh = [f for f in feats if f["kind"] == "hole" and f["diameter_mm"] < 100]
    for h in setup["holes"]:
        best = min(fh, key=lambda f: np.linalg.norm(np.subtract(f["center_mm"], h["center_mm"])))
        dc = float(np.linalg.norm(np.subtract(best["center_mm"], h["center_mm"])))
        ax = "xyz".index(h["axis"])
        check(dc < 0.05 and abs(best["diameter_mm"] - h["diameter_mm"]) < 0.1 and abs(best["axis"][ax]) == 1.0,
              f"{h['id']} {h['role']}: setup centre {h['center_mm']} Ø{h['diameter_mm']} ~ features face {best['face']} Ø{best['diameter_mm']} (Δ {dc:.3f} mm)")
        c = np.asarray(h["center_mm"], float)
        r_out = h["diameter_mm"] / 2 + 5.0
        side = [0, 0, 0]; side["xyz".index("x" if h["axis"] != "x" else "y")] = 1
        check(not inside(T, c) and inside(T, c + r_out * np.asarray(side)),
              f"{h['id']}: axis point outside the solid (bore), point {r_out:.0f} mm off-axis inside (material)")

    print("3. yukler.json (fields hazirla.mjs reads + recomputation from the set-up)")
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
    check(L.get("birim", "mm") == "mm", "birim mm")
    for d in L["destekler"]:
        check(d["tur"] == "silindir" and len(d["merkez"]) == 3 and len(d["eksen"]) == 3 and all(map(num, d["merkez"] + d["eksen"] + [d["yaricap"], d["bas"], d["son"]])),
              f"destek {d['ad']}: silindir fields numeric")
    holes = {h["id"]: h for h in setup["holes"]}
    sup_ids = [s["hole"] for s in setup["supports"]]
    check(len(L["destekler"]) == len(sup_ids) == 4, f"4 fixed bores ({', '.join(sup_ids)})")
    exp = []
    for c in setup["load_cases"]:
        for ld in c["loads"]:
            exp.append((c["name"].split()[0], holes[ld["hole"]]["center_mm"], ld.get("force_N"), ld.get("moment_Nm")))
    check(len(exp) == len(L["kuvvetler"]), f"{len(L['kuvvetler'])} load entries = set-up ({len(exp)})")
    for k, (lc, ctr, f, M) in zip(L["kuvvetler"], exp, strict=False):
        ok = k["durum"] == lc and np.allclose(k["nokta"], ctr) and num(k["buyukluk_N"]) and len(k["yon"]) == 3
        if f is not None:
            n = float(np.linalg.norm(f))
            ok &= abs(k["buyukluk_N"] - n) < 1e-6 and np.allclose(np.asarray(k["yon"]) * n, f, atol=1e-6)
            what = f"F {f} N"
        else:
            ok &= k["buyukluk_N"] == 0.0 and abs(k.get("moment_Nm", -1) - np.linalg.norm(M)) < 1e-9 and np.allclose(np.asarray(k["yon"]) * k["moment_Nm"], M)
            what = f"M {M} N·m (panel only, no arrow)"
        check(bool(ok), f"{lc} @ {ctr}: {what}")

    print("4. film.json / girdi.json")
    check(film.get("schema") == "ansys-film/1", "schema ansys-film/1")
    check(film.get("status") != "final", f"status '{film.get('status')}' (not final -> PROVISIONAL on screen)")
    tag = "PREVIEW — geometry and loads only, no analysis"
    check(all(tag in s for s in (film["card"], film["_preview"], girdi["_not"], L["_not"])), "PREVIEW tag in film.json card, girdi.json, yukler.json")
    check((HERE / "baslangic.stl").read_bytes()[:7] == b"PREVIEW", "PREVIEW tag in baslangic.stl header")
    check(all(v is None for v in film["redesign"].values()), "redesign: every field null")
    for k in ("density", "print", "stress", "eco_audit", "convergence", "crosscheck"):
        check(film.get(k) is None, f"{k}: null")
    check(all(set(m) <= {"name", "baseline", "catalogue_key"} for m in film["materials"]),
          f"materials: names (+ catalogue key) only ({', '.join(m['name'] + (' -> ' + m['catalogue_key'] if 'catalogue_key' in m else '') for m in film['materials'])})")
    catp = CASE / "catalogue" / "materials_catalogue.json"
    if catp.exists():
        ck = set(json.loads(catp.read_text(encoding="utf-8")).get("materials", {}))
        check(all(m.get("catalogue_key") in ck for m in film["materials"]), f"every catalogue_key exists in catalogue materials {sorted(ck)}")
    nums = []

    def walk(o, path):
        if isinstance(o, dict):
            for a, b in o.items():
                if not a.startswith("_"):
                    walk(b, f"{path}.{a}" if path else a)
        elif isinstance(o, list):
            for i, b in enumerate(o):
                walk(b, f"{path}[{i}]")
        elif num(o):
            nums.append((path, o))
    walk(film, "")
    print(f"        numbers in film.json outside _kaynak/_missing: {len(nums)}")
    for p_, v in nums:
        print(f"          {p_} = {v}")
    allowed = ("temperature_C", "baseline.mass_kg", "cad_setup.holes[")
    check(all(p_.startswith(allowed) for p_, _ in nums), "every number is temperature, baseline mass or CAD hole geometry")
    for k in ("ansys", "yukler"):
        check((HERE / girdi[k]).exists(), f"girdi.json {k} -> {girdi[k]} exists")
    check((HERE / girdi["geometri"]["dosya"]).exists() and girdi["geometri"]["yukari"] == "z" and girdi["geometri"]["hizala"] == "yok",
          "girdi.json geometri -> baslangic.stl, z up, no re-alignment (same frame as yukler.json)")
    cat = CASE / "catalogue" / "materials_catalogue.json"
    print(f"        catalogue {cat.relative_to(CASE).as_posix()}: {'present' if cat.exists() else 'not present'}; manifest link: {film.get('materials_catalogue')}")
    check((film.get("materials_catalogue") is not None) == cat.exists(), "catalogue link matches what exists now")

    if g.film_veri:
        print("5. hazirla.mjs output (copy) -> shots the film will build or skip (rules of film/src/ana.mjs gerekVar)")
        V = json.loads(Path(g.film_veri).read_text(encoding="utf-8"))
        AV = V.get("ansys") or {}
        ms = AV.get("malzemeler", [])
        rules = {
            "02 300 °C (egri)": any(m.get("egri") for m in ms) and num(AV.get("sicaklik_C")),
            "04 Printability (baski)": bool(AV.get("baski")),
            "05 Stress (gerilme)": bool(V.get("gerilme") or AV.get("secilen", -1) >= 0 or ((V.get("sonuc") or {}).get("adaylar"))
                                       or any(num(x) for x in ((V.get("alan") or {}).get("meta") or {}).get("kutle_kg", []))),
            "06 Materials (malzeme)": sum(num(m.get("kutle_kg")) for m in ms) >= 2,
            "07 Eco Audit (eko)": bool((AV.get("eko") or {}).get("taban")),
            "08 Cross-check (capraz)": len(AV.get("capraz") or []) >= 1,
        }
        print("        01 Baseline: always built")
        print("        03 Optimisation: always built (no 'gerek' rule) -> see README: illustrative removal from the BASELINE STL")
        for k, v in rules.items():
            print(f"        {k}: {'BUILT' if v else 'skipped'}")
        check(not any(rules.values()), "every analysis shot (02, 04–08) is skipped by the film itself")
        check(AV.get("durum") != "final", f"film-veri ansys.durum '{AV.get('durum')}' -> PROVISIONAL source line")
        check(V.get("gerilme") is None and V.get("alan") is None and V.get("sonuc") is None, "film-veri: no stress field, no density field, no result")
        print("        hazirla notes:   " + " | ".join(V.get("notlar", [])))
        print("        hazirla warnings: " + " | ".join(V.get("uyarilar", [])))
    print(f"\n{'FAIL: ' + str(len(fails)) if fails else 'ALL PASS'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
