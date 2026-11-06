"""04_Venus/outputs/variants/v0_7_44p6kg: the 44.63 kg variant, written by 04_Venus/code/variants/venus_variant_v07.py."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "04_Venus" / "outputs"
VAR = OUTPUTS / "variants" / "v0_7_44p6kg"
VARIANT_SCRIPT = ROOT / "04_Venus" / "code" / "variants" / "venus_variant_v07.py"
MANIFEST = ROOT / "04_Venus" / "catalog" / "reorg_manifest.json"
BUDGET = OUTPUTS / "variants" / "budget_update" / "result.json"
TURBULENCE = ROOT / "04_Venus" / "literature" / "data" / "venus_turbulence_model.json"
TAGS = {"D", "D-ag", "K", "Y"}
PROMOTED = (VAR / "PROMOTED.json").is_file()

pytestmark = pytest.mark.skipif(not (VAR / "design.json").is_file(), reason="variant not generated")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def design() -> dict:
    return load(VAR / "design.json")


@pytest.fixture(scope="module")
def sim() -> dict:
    return load(VAR / "sim_params.json")


@pytest.fixture(scope="module")
def anchors() -> dict:
    return load(VAR / "baseline_hashes_before.json")


def key_paths(node: object, path: str = "") -> set[str]:
    """Every dict key, lists collapsed to ``[]`` (positional for the deployment steps, whose keys differ per step)."""
    out: set[str] = set()
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(f"{path}.{k}")
            out |= key_paths(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out |= key_paths(v, f"{path}[{i}]" if path == ".deployment_sequence" else f"{path}[]")
    return out


# mass --------------------------------------------------------------------------------------------------------------

def test_thirteen_components_sum_to_the_recommended_gross(design: dict) -> None:
    comps = design["vehicle"]["components"]
    assert len(comps) == 13
    total = sum(c["mass_kg"] for c in comps)
    assert total == pytest.approx(44.63, abs=5e-4)
    assert design["vehicle"]["total_mass_kg"] == 44.63
    assert round(load(BUDGET)["recommended_design"]["gross_kg"], 2) == 44.63


def test_components_are_the_budget_breakdown(design: dict) -> None:
    bd = load(BUDGET)["recommended_design"]["breakdown"]
    m = {c["id"]: c["mass_kg"] for c in design["vehicle"]["components"]}
    assert m["rotors"] == pytest.approx(bd["blades+hubs"] + bd["motors"] + bd["ESCs"], abs=1e-9)
    for cid, key in (("arms", "arms+hinges"), ("body", "vessel"), ("battery", "battery"), ("solar", "solar"),
                     ("payload", "payload"), ("avionics", "avionics"), ("antenna", "comms"), ("thermal", "thermal"),
                     ("coating", "coating"), ("attach", "attach"), ("wiring", "wiring"), ("contingency", "contingency")):
        assert m[cid] == bd[key], cid


def test_battery_is_1109_wh(design: dict, sim: dict) -> None:
    assert design["vehicle"]["performance_55km"]["battery_Wh"] == 1109.0
    assert "1109 Wh" in next(c for c in design["vehicle"]["components"] if c["id"] == "battery")["name"]
    assert round(sim["vehicle"]["power"]["battery_capacity"]["value"]) == 1109


# schema ------------------------------------------------------------------------------------------------------------

def test_design_keys_and_ids_unchanged(design: dict) -> None:
    base = load(_baseline_design())
    assert design["schema"] == base["schema"] == "venus_rotorcraft_design/1"
    assert design["version"] == "0.7"
    assert key_paths(design) == key_paths(base)
    assert [c["id"] for c in design["vehicle"]["components"]] == [c["id"] for c in base["vehicle"]["components"]]
    assert [c["label"] for c in design["vehicle"]["components"]] == [c["label"] for c in base["vehicle"]["components"]]
    assert [s["step"] for s in design["deployment_sequence"]] == [s["step"] for s in base["deployment_sequence"]]


def test_sim_keys_unchanged(sim: dict) -> None:
    base = load(_baseline_sim())
    assert sim["schema"] == base["schema"] and sim["version"] == "0.7"
    assert key_paths(sim) == key_paths(base)
    names = [x["name"] for x in sim["limits"]]
    assert names[:len(base["limits"])] == [x["name"] for x in base["limits"]]
    assert [f["name"] for f in sim["failure_modes"]] == [f["name"] for f in base["failure_modes"]]


def _baseline_design() -> Path:
    if PROMOTED:
        return Path(load(VAR / "PROMOTED.json")["anchor_dir"]) / "design.json"
    return OUTPUTS / "design.json"


def _baseline_sim() -> Path:
    if PROMOTED:
        return Path(load(VAR / "PROMOTED.json")["anchor_dir"]) / "sim_params.json"
    return OUTPUTS / "sim_params.json"


# baseline ----------------------------------------------------------------------------------------------------------

@pytest.mark.skipif(PROMOTED, reason="promoted on the user's yes: the baseline is meant to differ")
def test_baseline_files_unchanged(anchors: dict) -> None:
    assert len(anchors["files"]) >= 70
    now = {p.name: sha(p) for p in OUTPUTS.iterdir() if p.is_file()}
    assert now == anchors["files"]


def test_existing_scripts_unchanged(anchors: dict) -> None:
    """The anchor in outputs/ stays as written on 6 Nov. The reorganisation changed the scripts, so each one is checked
    in three steps: the manifest's old hash is the anchor, the moved file has the manifest's new hash, and undoing the
    listed path edits gives the anchored bytes again (venus_final was split: no undo, see final_split in the manifest)."""
    changes = load(MANIFEST)["script_anchor_changes"]
    assert set(changes) == set(anchors["scripts"])
    for name, digest in anchors["scripts"].items():
        entry = changes[name]
        assert entry["old_sha256"] == digest, name
        text = (ROOT / entry["new_path"]).read_bytes()
        assert hashlib.sha256(text).hexdigest() == entry["new_sha256"], name
        if entry["path_edits"] is None:
            assert name == "venus_final.py"
            continue
        for old, new in entry["path_edits"]:
            text = text.replace(new.encode(), old.encode())
        assert hashlib.sha256(text).hexdigest() == digest, name


# gust --------------------------------------------------------------------------------------------------------------

def test_gust_correlation_is_the_turbulence_model_value(sim: dict) -> None:
    g = sim["atmosphere_and_wind"]["vertical_gust_correlation"]
    tm = load(TURBULENCE)["component_A_mesoscale_convective_vertical_wind"]["lagrangian_time_scale"]
    assert g["value"] == 1500.0 == tm["value"]
    assert g["unit"] == "s" and g["tag"] == "K" and "[v0.7: was 80.0 in v0.6]" in g["source"]


def test_margin_figure_uses_the_new_gust() -> None:
    out = load(VAR / "result.json")
    g = out["variant"]["gust"]
    item = next(x for x in out["margins"] if x["item"].startswith("Thrust margin"))
    assert g["A_plus_C_loiter"]["tau_w_s"] < 1500.0 and g["A_only_hover_tau_1500s"]["tau_w_s"] == 1500
    assert item["ratio"] == pytest.approx(0.6 / g["A_plus_C_loiter"]["dT_peak_max_over_W"], rel=1e-9)


# mission -----------------------------------------------------------------------------------------------------------

def test_mission_matches_the_6_nov_profile(design: dict) -> None:
    ref = load(BUDGET)["recommended_cases"]["nominal"]
    ops = design["operations"]
    assert ops["solar_sustained_hours"] == round(ref["sun_h"], 1)
    assert ops["release_hour_angle_deg"] == round(ref["release_hour_angle_deg"], 1)
    assert ops["drift_distance_km"] == pytest.approx(ref["drift_km"], abs=0.5)
    ev = ops["events"]
    assert ev[0]["kind"] == "release" and ev[0]["altitude_km"] == 61.0
    assert ev[-1]["kind"] == "end" and ev[-1]["altitude_km"] == pytest.approx(50.4, abs=0.05)
    assert all(e["kind"] != "other" for e in ev)
    assert all(40.0 < e["altitude_km"] < 62.0 for e in ev)
    assert min(e["altitude_km"] for e in ev if "dive" in e["event"] and "sunset" not in e["event"] and "bottom" in e["event"]) > 52.0 - 0.2
    assert design["vehicle"]["performance_55km"]["loiter_electric_W"] == round(ref["loiter_W"], 0)
    assert design["vehicle"]["performance_55km"]["solar_sustains_loiter_above_mu0"] == round(ref["mu0_loiter"], 3)
    assert ops["series_hourly"][0]["altitude_km"] == 61.0


def test_deployment_sequence_says_the_6_nov_rules(design: dict) -> None:
    s = {x["step"]: x for x in design["deployment_sequence"]}
    assert "668 rpm" in s[8]["name"]
    assert "cos z >= 0.68" in s[8]["decision"]
    assert "1.5 m/s with 3.5 m/s forward" in s[9]["name"]
    assert s[9]["time_s"] - s[8]["time_s"] == pytest.approx(4020.0, abs=1.0)
    assert "52 km" in s[10]["name"] and "52 °C" in s[10]["name"]
    assert s[11]["altitude_km"] == 50.4
    text = json.dumps(design["deployment_sequence"], ensure_ascii=False) + design["operating_band"]["rationale"]
    assert "51 km" not in text and "3 m/s to" not in text


def test_no_stale_text_in_sim_params(sim: dict) -> None:
    text = json.dumps(sim["failure_modes"], ensure_ascii=False)
    for stale in ("0.595", "1.04 kWh", "~103 kWh", "~49 h", "> 50 degC", "51-58 km"):
        assert stale not in text, stale
    lim = {x["name"]: x for x in sim["limits"]}
    assert lim["science dive floor"]["value"] == 52.0
    assert lim["dive abort battery temperature"]["value"] == 52.0
    assert lim["release sun height, minimum cos z"]["value"] == 0.68


# sim_params contract and change marks -------------------------------------------------------------------------------

def _walk(node: object, path: str, out: list[tuple[str, dict]]) -> None:
    if isinstance(node, dict):
        if "value" in node:
            out.append((path, node))
        for k, v in node.items():
            if k != "value":
                _walk(v, f"{path}.{k}", out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]", out)


def test_every_value_has_unit_tag_source(sim: dict) -> None:
    vals: list[tuple[str, dict]] = []
    _walk(sim, "", vals)
    assert len(vals) > 30
    for path, v in vals:
        assert {"unit", "tag", "source"} <= set(v), path
        parts = {p.strip().split("(")[0].strip() for p in v["tag"].replace("+", "/").split("/")}
        assert parts & TAGS, (path, v["tag"])


def test_every_changed_scalar_is_marked(sim: dict) -> None:
    new: list[tuple[str, dict]] = []
    old: list[tuple[str, dict]] = []
    _walk(sim, "", new)
    _walk(load(_baseline_sim()), "", old)
    old_by = dict(old)
    changed = [p for p, v in new if p in old_by and old_by[p]["value"] != v["value"]]
    assert len(changed) >= 10
    for p, v in new:
        if p in changed:
            assert "[v0.7: was" in v["source"], p
    log = load(VAR / "sim_params_changes.json")
    assert all({"path", "old", "new", "unit", "tag", "source"} <= set(x) for x in log)
    assert len([x for x in log if x["unit"] != "table" and x["unit"] != "-"]) >= len(changed)
    readme = (VAR / "sim_params_README.md").read_text(encoding="utf-8")
    assert "v0.7 variant note" in readme and "1500" in readme


def test_atmosphere_table_not_touched(sim: dict) -> None:
    assert sim["atmosphere_and_wind"]["rows"] == load(_baseline_sim())["atmosphere_and_wind"]["rows"]


# figures, changes, promotion ------------------------------------------------------------------------------------------

def test_figures_audited() -> None:
    st = load(VAR / "figures_status.json")
    assert len(st) == 15
    done = {k: v for k, v in st.items() if v["regenerated"]}
    assert done and all(v["hata"] == 0 for v in done.values())
    assert all((VAR / f"{k}.{e}").is_file() for k in done for e in ("png", "pdf", "denetim.txt"))
    assert " 0 HATA" in (VAR / "vesper.tutarlilik.txt").read_text(encoding="utf-8").splitlines()[0]


def test_changes_file_is_complete() -> None:
    text = (VAR / "CHANGES.md").read_text(encoding="utf-8")
    for needle in ("--promote --yes", "vehicle.total_mass_kg", "vertical_gust_correlation", "which component takes each gram"):
        assert needle in text, needle
    assert "@@PROMOTION@@" not in text


def _script():
    sys.path.insert(0, str(VARIANT_SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("venus_variant_v07", VARIANT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["venus_variant_v07"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.skipif(PROMOTED, reason="already promoted")
def test_promotion_on_a_copy_anchors_then_copies(tmp_path: Path) -> None:
    scratch = Path("D:/tmp_ideathon")
    base = Path(tempfile.mkdtemp(dir=scratch)) if scratch.is_dir() else tmp_path
    try:
        outputs = base / "outputs"
        outputs.mkdir()
        for p in OUTPUTS.iterdir():
            if p.is_file():
                shutil.copy2(p, outputs / p.name)
        (outputs / "versions").mkdir()
        variant = base / "variant"
        shutil.copytree(VAR, variant)
        before = {p.name: sha(p) for p in outputs.iterdir() if p.is_file()}
        mod = _script()
        plan = mod.promote(variant, outputs, False)
        assert not list((outputs / "versions").iterdir())                 # dry run writes nothing
        assert {p.name: sha(p) for p in outputs.iterdir() if p.is_file()} == before
        assert "design.json" in plan["replaces"] and "CHANGES.md" not in plan["copy"]
        done = mod.promote(variant, outputs, True)
        anchor = Path(done["anchor_dir"])
        for name in done["replaces"]:
            assert sha(anchor / name) == before[name], name                # old state kept
            assert sha(outputs / name) == sha(variant / name), name        # new state in place
        assert load(outputs / "design.json")["version"] == "0.7"
        assert (variant / "PROMOTED.json").is_file()
        with pytest.raises(SystemExit):
            mod.promote(variant, outputs, True)                            # baseline moved: a second run is refused
    finally:
        shutil.rmtree(base, ignore_errors=True)
