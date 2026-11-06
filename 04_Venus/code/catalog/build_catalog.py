"""Write the 04_Venus catalogues (components, figures, scripts, literature, data files) from the files on disk.

    python 04_Venus/code/catalog/build_catalog.py           # writes 04_Venus/catalog/
    python 04_Venus/code/catalog/build_catalog.py --check   # exit 1 if a catalogue is out of date

Standard library only. Same inputs give the same bytes: no clock, no absolute paths, sorted walks.
"""
from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
VENUS = "04_Venus"
FOLDERS = ("pipeline", "analysis", "data", "variants", "catalog")
TOPICS = (("literature/atmosphere", "atmosfer"), ("literature/missions", "görevler"), ("literature/rotorcraft", "rotorlu hava aracı"),
          ("literature/engineering", "mühendislik"), ("literature/simulator", "simülatör"), ("reviews", "kontrol ve denetim"))
TAGS = ("D-ag", "D", "A", "K", "Y", "calc")
RUN = "python 04_Venus/code/"

# Commands, inputs and outputs read from each script's source. A new script without a row shows "yazılmadı".
SCRIPTS = {
    "venus_day.py": (RUN + "pipeline/venus_day.py --final", "`--final` ya da prova kartı (`prev_guess/04_Venus/cards/venus_rehearsal.json`)",
                     "`--final`: `venus_final.py` çıktıları. Kart: kartın yanında `out/<ad>/`"),
    "venus_final.py": (RUN + "pipeline/venus_final.py", "`trade_sizing.json`, `sensitivity.json`",
                       "`result.json`, `result.md`, F1–F15, `vesper.seti.json`, `vesper.tutarlilik.txt`, `vesper_for_simulator.json`, `design.json`, `entry_validation.*`"),
    "final_compute.py": ("doğrudan koşulmaz, `venus_final.py` çağırır", "`trade_sizing.json`, `sensitivity.json`, `entry_validation.json`", "bellekte sonuç sözlüğü"),
    "final_figures.py": ("doğrudan koşulmaz, `venus_final.py` çağırır", "sonuç sözlüğü", "F1–F15 (`png`, `pdf`, `denetim.txt`, `dw.json`), `vesper.seti.json`"),
    "final_sim.py": ("doğrudan koşulmaz, `venus_final.py` çağırır", "sonuç sözlüğü", "`vesper_for_simulator.json` içeriği"),
    "final_report.py": ("doğrudan koşulmaz, `venus_final.py` çağırır", "sonuç sözlüğü", "`result.md` metni"),
    "venus_design.py": (RUN + "pipeline/venus_design.py", "`aerokit.venus.design`", "`design.json`, `versions/design_v*.json`"),
    "venus_sim_params.py": (RUN + "pipeline/venus_sim_params.py", "`vesper_for_simulator.json`, `aerokit.venus`", "`sim_params.json`"),
    "venus_trade.py": (RUN + "analysis/venus_trade.py", "`aerokit.venus.sizing`", "`trade_sizing.json`"),
    "venus_sensitivity.py": (RUN + "analysis/venus_sensitivity.py", "`aerokit.venus`", "`sensitivity.json`"),
    "venus_crosscheck.py": (RUN + "analysis/venus_crosscheck.py", "`aerokit.venus`", "`crosscheck.json`, `crosscheck.md`"),
    "venus_entry_validation.py": (RUN + "analysis/venus_entry_validation.py", "`aerokit.venus`, tarihsel giriş tablosu (betiğin içinde)", "`entry_validation.json`, `entry_validation.md`"),
    "venus_budget_update.py": (RUN + "analysis/venus_budget_update.py", "`guc_egrisi.json` (Sunumatik), `literature/data/venus_turbulence_model.json`, `sim_runs/sim_points.json`",
                               "`variants/budget_update/` (`result.json`, `result.md`, B1–B3)"),
    "venus_pds_extract.py": ("python -I 04_Venus/code/data/venus_pds_extract.py <indirilenler>/atmo", "ham Pioneer Venus PDS tabloları", "`src/aerokit/venus/data/pv_profiles.json`"),
    "venus_variant_v07.py": (RUN + "variants/venus_variant_v07.py", "`variants/budget_update/`, `outputs/` tabanı", "`variants/v0_7_44p6kg/`"),
    "venus_short_demo.py": (RUN + "variants/venus_short_demo.py", "`guc_egrisi.json`, `variants/budget_update/result.json`", "`variants/short_demo/`"),
    "venus_short_demo_files.py": (RUN + "variants/venus_short_demo_files.py", "`guc_egrisi.json`, `venus_variant_v07.py`", "`variants/short_demo/files_0p5kg/`"),
    "build_catalog.py": (RUN + "catalog/build_catalog.py", "`outputs/`, `docs/25*.md`, `literature/`, `reviews/`, `code/`", "`catalog/` içindeki üretilmiş dosyalar"),
}

# First match wins; patterns are relative to 04_Venus/.
PRODUCERS = (
    ("outputs/variants/budget_update/sim_runs/*", "elle: Sunumatik simülatör koşuları"),
    ("outputs/variants/budget_update/*", "`venus_budget_update.py`"),
    ("outputs/variants/v0_7_44p6kg/*", "`venus_variant_v07.py`"),
    ("outputs/variants/short_demo/*", "`venus_short_demo.py`"),
    ("outputs/versions/*", "`venus_design.py`"),
    ("outputs/design.json", "`venus_design.py`"),
    ("outputs/sim_params.json", "`venus_sim_params.py`"),
    ("outputs/sim_params_README.md", "elle"),
    ("outputs/cli_yasa_denetimi.md", "elle: UX denetim kaydı"),
    ("outputs/trade_sizing.json", "`venus_trade.py`"),
    ("outputs/sensitivity.json", "`venus_sensitivity.py`"),
    ("outputs/crosscheck.*", "`venus_crosscheck.py`"),
    ("outputs/entry_validation.*", "`venus_entry_validation.py`"),
    ("outputs/result.*", "`venus_final.py`"),
    ("outputs/vesper*", "`venus_final.py`"),
    ("outputs/F*", "`venus_final.py`"),
    ("literature/data/*", "elle: simülatör veri kitabı ajanı, 5 Kasım"),
)


def read(rel: str) -> str:
    return (ROOT / VENUS / rel).read_text(encoding="utf-8")


def load(rel: str) -> dict:
    return json.loads(read(rel))


def table(head: list[str], align: str, rows: list[list[str]]) -> list[str]:
    """Markdown table; ``align`` has one ``l`` or ``r`` per column."""
    bar = "|".join("---:" if a == "r" else "---" for a in align)
    return ["| " + " | ".join(head) + " |", f"|{bar}|"] + ["| " + " | ".join(r) + " |" for r in rows]


def cell(text: object) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def vec(v: list | None) -> str:
    return "—" if v is None else "[" + ", ".join(f"{x:.3f}" for x in v) + "]"


def pair(old: str, new: str) -> str:
    return cell(old) if old == new else f"{cell(old)} → {cell(new)}"


def delta(x: float | None) -> str:
    return "—" if x is None else "0.000" if x == 0 else f"{x:+.3f}"


def page(lines: list[str]) -> str:
    return "\n".join(lines).rstrip() + "\n"


# components --------------------------------------------------------------------------------------------------------

DESIGNS = (("v0.6", "outputs/design.json"), ("v0.7", "outputs/variants/v0_7_44p6kg/design.json"))
FIELDS = ("name", "mass_kg", "material", "colour", "position_m", "size_m")


def components() -> tuple[str, str]:
    docs = [(tag, rel, load(rel)) for tag, rel in DESIGNS]
    a, b = ({c["id"]: c for c in d["vehicle"]["components"]} for _, _, d in docs)
    ids = list(a) + [i for i in b if i not in a]
    rows = []
    for i in ids:
        x, y = a.get(i), b.get(i)
        row = {"id": i, "label": (x or y)["label"], "tag": (x or y)["tag"]}
        for t, c in (("v0.6", x), ("v0.7", y)):
            row[t] = {k: c.get(k) for k in FIELDS} if c else None
        row["mass_delta_kg"] = round(y["mass_kg"] - x["mass_kg"], 3) if x and y else None
        rows.append(row)
    doc = {"schema": "venus_catalog_components/1",
           "sources": {t: {"file": f"{VENUS}/{rel}", "version": d["version"], "status": d["status"],
                           "total_mass_kg": d["vehicle"]["total_mass_kg"]} for t, rel, d in docs},
           "components": rows}
    known = [r for r in rows if r["mass_delta_kg"] is not None]
    top = max(known, key=lambda r: abs(r["mass_delta_kg"]))
    s6 = sum(r["v0.6"]["mass_kg"] for r in rows if r["v0.6"])
    s7 = sum(r["v0.7"]["mass_kg"] for r in rows if r["v0.7"])
    ma, mb = (d["vehicle"]["total_mass_kg"] for _, _, d in docs)
    lines = [f"# Bileşen kataloğu: v0.7, v0.6'dan {s7 - s6:+.3f} kg ağır; en büyük fark {top['id']} ({top['mass_delta_kg']:+.3f} kg)", "",
             "Kaynak: `outputs/design.json` (v0.6) ve `outputs/variants/v0_7_44p6kg/design.json` (v0.7, onaylanmadı). "
             "Sıra, `design.json` sırasıdır. Kütleler kaynaktaki 3 ondalıkla yazılır. "
             f"Toplam satırı bileşenlerin toplamıdır; `total_mass_kg` alanı v0.6'da {ma}, v0.7'de {mb} kg yazar.", "", "## Kütle", ""]
    body = [[f"`{r['id']}`", cell(r["label"]), cell(r["tag"]), f"{r['v0.6']['mass_kg']:.3f}" if r["v0.6"] else "—",
             f"{r['v0.7']['mass_kg']:.3f}" if r["v0.7"] else "—",
             delta(r["mass_delta_kg"])] for r in rows]
    body.append(["**toplam**", "", "", f"**{s6:.3f}**", f"**{s7:.3f}**", f"**{s7 - s6:+.3f}**"])
    lines += table(["id", "Etiket", "Veri türü", "v0.6 (kg)", "v0.7 (kg)", "Fark (kg)"], "lllrrr", body)
    same = "v0.7 sütunu v0.6'dan farklıysa dolu, aynıysa `=`."
    both = [(r, r["v0.6"] or r["v0.7"], r["v0.7"] or r["v0.6"]) for r in rows]
    lines += ["", "## Ad, malzeme, renk", "", same, ""]
    lines += table(["id", "Ad v0.6", "Ad v0.7", "Malzeme", "Renk"], "lllll",
                   [[f"`{r['id']}`", cell(x["name"]), "=" if x["name"] == y["name"] else cell(y["name"]), pair(x["material"], y["material"]),
                     pair(f"`{x['colour']}`", f"`{y['colour']}`")] for r, x, y in both])
    lines += ["", "## Konum ve boyut", "", f"Metre. Çerçeve: başlangıç gövde merkezi, x ileri, y sol, z yukarı. {same}", ""]
    lines += table(["id", "Konum v0.6", "Konum v0.7", "Boyut v0.6", "Boyut v0.7"], "lllll",
                   [[f"`{r['id']}`", vec(x["position_m"]), "=" if x["position_m"] == y["position_m"] else vec(y["position_m"]),
                     vec(x["size_m"]), "=" if x["size_m"] == y["size_m"] else vec(y["size_m"])] for r, x, y in both])
    return page(lines), json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


# figures -----------------------------------------------------------------------------------------------------------

CAPTION = re.compile(r"^\*\*([FB]\d+)\b[^*\n]*\*\*\s+\*(.+?)\*(?=\s|$)", re.M | re.S)


def captions() -> dict[str, str]:
    text = read("docs/25_lugus_venus_rotorcraft.md").replace("\r\n", "\n")
    return {m[1]: " ".join(m[2].split()) for m in CAPTION.finditer(text)}


def audit(rel: str) -> str:
    p = ROOT / VENUS / rel
    if not p.is_file():
        return "denetim dosyası yok"
    m = re.search(r"(\d+) HATA · (\d+) UYARI · (\d+) BİLGİ", p.read_text(encoding="utf-8"))
    return m[0] if m else "okunamadı"


def consistency(rel: str) -> str:
    return read(rel).splitlines()[0].partition(": ")[2]


def number(name: str) -> int:
    return int(re.match(r"[FB](\d+)", name)[1])


def stems(rel: str, prefix: str) -> list[str]:
    return sorted((p.stem for p in (ROOT / VENUS / rel).glob(f"{prefix}*.png")), key=number)


def figures() -> str:
    cap = captions()
    base = [("outputs", s) for s in stems("outputs", "F")] + [("outputs/variants/budget_update", s) for s in stems("outputs/variants/budget_update", "B")]
    rows, clean = [], 0
    for folder, s in base:
        result = audit(f"{folder}/{s}.denetim.txt")
        clean += result.startswith("0 HATA")
        fid = s.split("_")[0]
        rows.append([fid, f"`{folder}/{s}.png`", cell(cap.get(fid, "doc 25'te altyazı yok")), result])
    lines = [f"# Figür kataloğu: {len(rows)} taban figürün {clean} tanesi denetimden 0 HATA ile geçti", "",
             "İddia metni `docs/25_lugus_venus_rotorcraft.md` altyazısından, denetim sonucu `*.denetim.txt` dosyasından okunur. "
             "Her figürün `pdf`, `denetim.txt` ve `dw.json` eşi aynı klasördedir.", "", "## Taban ve bütçe figürleri", ""]
    lines += table(["Figür", "Dosya", "İddia (doc 25)", "Denetim"], "llll", rows)
    lines += ["", "Set tutarlılığı:", "",
              f"- F1–F15: {consistency('outputs/vesper.tutarlilik.txt')}",
              f"- B1–B3: {consistency('outputs/variants/budget_update/budget.tutarlilik.txt')}"]
    var = "outputs/variants/v0_7_44p6kg"
    st = load(f"{var}/figures_status.json")
    rows = []
    for s in sorted(st, key=number):
        r = st[s]
        made = bool(r["regenerated"])
        rows.append([s.split("_")[0], f"`{var}/{s}.png`" if made else "—", "evet" if made else "hayır",
                     {True: "evet", False: "hayır"}.get(r.get("same_pixels_as_baseline"), "—"),
                     audit(f"{var}/{s}.denetim.txt") if made else "—"])
    done = sum(r[2] == "evet" for r in rows)
    lines += ["", f"## v0.7 varyant figürleri: {len(rows)} figürün {done} tanesi yeniden üretildi", "",
              "Kaynak: `figures_status.json`. Altyazı yoktur, iddia için aynı numaralı taban figüre bakın.", ""]
    lines += table(["Figür", "Dosya", "Üretildi", "Tabanla aynı piksel", "Denetim"], "lllll", rows)
    lines += ["", f"Set tutarlılığı: {consistency(var + '/vesper.tutarlilik.txt')}"]
    return page(lines)


# scripts -----------------------------------------------------------------------------------------------------------

def purpose(p: Path) -> str:
    doc = ast.get_docstring(ast.parse(p.read_text(encoding="utf-8")))
    return cell(doc.splitlines()[0]) if doc else "docstring yok"


def scripts() -> str:
    n = 0
    lines = []
    for folder in FOLDERS:
        rows = []
        for p in sorted((ROOT / VENUS / "code" / folder).glob("*.py")):
            cmd, src, out = SCRIPTS.get(p.name, ("yazılmadı", "yazılmadı", "yazılmadı"))
            rows.append([f"`{p.name}`", purpose(p), f"`{cmd}`" if cmd.startswith("python") else cmd, src, out])
        n += len(rows)
        lines += [f"## `code/{folder}/`", ""] + table(["Betik", "Amaç (docstring)", "Komut", "Girdi", "Çıktı"], "lllll", rows) + [""]
    head = [f"# Betik kataloğu: {n} Python dosyası, {len(FOLDERS)} klasör", "",
            "Komutlar proje kökünden koşulur. Girdi ve çıktı adları aksi yazmıyorsa `04_Venus/outputs/` altındadır. "
            "Klasörler iş akışı sırasındadır. Klasör içinde sıra alfabetiktir, çünkü ad ile aranır.", ""]
    return page(head + lines)


# literature --------------------------------------------------------------------------------------------------------

def title(text: str) -> str:
    return next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), "başlık yok")


def tag_summary(text: str) -> str:
    found = re.findall(r"\[(D-ag|D|A|K|Y|calc)\]", text)
    parts = [f"{t} {found.count(t)}" for t in TAGS if t in found]
    return " · ".join(parts) if parts else "—"


def literature() -> str:
    lines, counts = [], []
    for folder, topic in TOPICS:
        files = sorted(p for p in (ROOT / VENUS / folder).glob("*.md") if p.name != "README.md")
        rows = []
        for p in files:
            text = p.read_text(encoding="utf-8")
            rows.append([f"`{p.name}`", topic, cell(title(text)), tag_summary(text)])
        counts.append([f"`{folder}/`", topic, str(len(rows))])
        lines += [f"## `{folder}/`", ""] + table(["Dosya", "Konu", "Başlık", "Etiket sayısı"], "llll", rows) + [""]
    total = sum(int(c[2]) for c in counts)
    head = [f"# Literatür kataloğu: {total} not, {len(TOPICS)} klasör", "",
            "Başlık, dosyanın ilk `#` satırıdır. Etiket sayısı, notta geçen `[D-ag]`, `[D]`, `[A]`, `[K]`, `[Y]`, `[calc]` "
            "işaretlerini sayar. Etiketlerin anlamı `literature/README.md` dosyasındadır. "
            "`reviews/` literatür değildir: hesap kontrolleri, denetimler ve jüri soruları oradadır.", ""]
    head += table(["Klasör", "Konu", "Not"], "llr", counts) + [""]
    return page(head + lines)


# data files --------------------------------------------------------------------------------------------------------

def producer(rel: str) -> str:
    return next((who for pat, who in PRODUCERS if fnmatch.fnmatch(rel, pat)), "bilinmiyor")


def data_files() -> str:
    base = ROOT / VENUS
    rows, total, unknown = [], 0, 0
    for top in ("outputs", "literature/data"):
        for p in sorted((q for q in (base / top).rglob("*") if q.is_file()), key=lambda q: q.relative_to(base).as_posix()):
            rel = p.relative_to(base).as_posix()
            raw = p.read_bytes()
            total += len(raw)
            who = producer(rel)
            unknown += who == "bilinmiyor"
            rows.append([f"`{rel}`", str(len(raw)), f"`{hashlib.sha256(raw).hexdigest()[:12]}`", who])
    lines = [f"# Veri dosyası kataloğu: {len(rows)} dosya, {total / 1e6:.1f} MB, üreticisi bilinmeyen {unknown}", "",
             "Sıra yola göredir, çünkü dosya yol ile aranır. `sha256` ilk 12 karakterdir.", ""]
    lines += table(["Dosya", "Boyut (bayt)", "sha256", "Üretici"], "lrll", rows)
    return page(lines)


# index -------------------------------------------------------------------------------------------------------------

def index() -> str:
    rows = [["`components.md`, `components.json`", "bileşenler: kütle, malzeme, renk, konum, boyut; v0.6 ile v0.7 yan yana", "bir bileşeni ararken"],
            ["`figures.md`", "F1–F15, B1–B3, varyant figürleri: dosya, iddia, denetim", "slayt ya da rapor için figür seçerken"],
            ["`scripts.md`", "her betik: amaç, komut, girdi, çıktı", "bir sonucu yeniden üretirken"],
            ["`literature.md`", "her not: dosya, konu, başlık, etiket sayısı", "kaynak ararken"],
            ["`data_files.md`", "`outputs/` ve `literature/data/`: boyut, sha256, üretici", "bir dosyanın nereden geldiğini ararken"],
            ["`parts_3d.md`, `parts_3d.json`", "3B mekanizmalar: görev, alt parça, kod, mesh sayısı; `code/visual/build_parts_catalog.mjs` üretir", "aracın bir parçasını ararken"],
            ["`reorg_manifest.json`", "6 Kasım taşıması: eski yol, yeni yol, hash, değişiklik nedeni; bir kez yazıldı, bu betik üretmez", "eski bir yolu ararken"],
            ["`baseline_hashes_before_2026-11-06.json`", "`outputs/` içindeki çapa dosyasının birebir kopyası", "çapanın eski değerine bakarken"]]
    lines = ["# Venüs kataloğu", "",
             "Bu klasör, Venüs çalışmasının dizinidir. Üretilen dosyaları elle değiştirmeyin.", ""]
    lines += table(["Dosya", "İçerik", "Ne zaman"], "lll", rows)
    lines += ["", "## Yeniden üretme", "", "Proje kökünden:", "", "```", RUN + "catalog/build_catalog.py", "```", "",
              "Denetlemek için sona `--check` ekleyin. `tests/test_venus_catalog.py` aynı karşılaştırmayı yapar. "
              "`outputs/`, `docs/25*.md`, `literature/`, `reviews/` ya da `code/` değişince katalog eskir. Bu komut onu günceller."]
    return page(lines)


def build() -> dict[str, str]:
    md, js = components()
    return {"README.md": index(), "components.md": md, "components.json": js, "figures.md": figures(), "scripts.md": scripts(),
            "literature.md": literature(), "data_files.md": data_files()}


def main(argv: list[str]) -> int:
    folder = ROOT / VENUS / "catalog"
    files = build()
    if "--check" in argv:
        stale = [n for n, t in files.items() if not (folder / n).is_file() or (folder / n).read_bytes() != t.encode("utf-8")]
        print(f"catalog out of date: {', '.join(stale)}; run without --check" if stale else f"catalog up to date ({len(files)} files)")
        return 1 if stale else 0
    folder.mkdir(exist_ok=True)
    for name, text in files.items():
        (folder / name).write_bytes(text.encode("utf-8"))
    print(f"catalog: wrote {len(files)} files to {VENUS}/catalog/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
