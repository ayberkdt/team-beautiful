"""Bundled data files (example models, CAD samples, material tables)."""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = DATA_DIR / "examples"


def example_path(*parts: str) -> Path:
    """Return the path of a bundled example file, e.g. ``example_path("cad", "box.stl")``."""
    path = EXAMPLES_DIR.joinpath(*parts).resolve()
    if EXAMPLES_DIR not in path.parents:
        raise ValueError(f"example path escapes the examples folder: {parts!r}")
    if not path.exists():
        raise FileNotFoundError(path)
    return path
