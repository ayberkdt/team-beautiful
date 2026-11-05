"""aerokit.bracket.matlist: organisers' material names → pool keys, never a silent guess."""
import pytest

from aerokit.bracket import matlist as ml


@pytest.mark.parametrize("entry,key,status", [
    ("Ti-6Al-4V", "ti64_lpbf", "alias"), ("ti6al4v", "ti64_lpbf", "alias"), ("UNS N07718", "in718_lpbf", "alias"),
    ("Alloy 718 (L-PBF)", "in718_lpbf", "alias"), ("17-4 PH stainless", "ss_17_4ph", "alias"),
    ("Structural Steel", "structural_steel", "alias"), ("Scalmaloy", "scalmalloy", "close"),
    ("Inconnel 718", "in718_lpbf", "close")])
def test_known_names(entry, key, status):
    r = ml.match(entry)
    assert (r["key"], r["status"]) == (key, status)


@pytest.mark.parametrize("entry", ["AlSi10Mg", "316L", "IN625", "Al 7075-T6", "titanium", "CFRP"])
def test_unknown_names_are_not_mapped(entry):
    r = ml.match(entry)
    assert r["key"] is None and r["status"] in ("unknown", "ambiguous")


def test_route_and_generic_notes():
    r = ml.match("Ti-6Al-4V wrought")
    assert r["key"] == "ti64_lpbf" and r["route_differs"]
    assert "generic" in ml.match("steel")["note"]
    assert not ml.resolve(["Ti-6Al-4V wrought"], strict=True)["ok"]


def test_read_csv_yaml_txt_and_resolve(tmp_path):
    (tmp_path / "m.csv").write_text("material,supplier\nTi-6Al-4V,X\nInconel 718,Y\n\nTi64,Z\n", encoding="utf-8")
    (tmp_path / "m.yaml").write_text("materials:\n  - name: 17-4PH\n  - Scalmalloy\n", encoding="utf-8")
    (tmp_path / "m.txt").write_text("# list\nStructural steel\nAlSi10Mg  # not in the pool\n", encoding="utf-8")
    r = ml.resolve(ml.read_list(tmp_path / "m.csv"))
    assert r["ok"] and r["keys"] == ["ti64_lpbf", "in718_lpbf"]                # Ti64 de-duplicated
    assert ml.resolve(ml.read_list(tmp_path / "m.yaml"))["keys"] == ["ss_17_4ph", "scalmalloy"]
    bad = ml.resolve(ml.read_list(tmp_path / "m.txt"))
    assert not bad["ok"] and bad["problems"][0]["entry"] == "AlSi10Mg"
    assert "| AlSi10Mg | unknown |" in ml.markdown(bad)
