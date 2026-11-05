"""Safe file output.

Results are written atomically (temporary file in the target folder, then :func:`os.replace`), so
a crash never leaves a half-written report, and output paths are validated: no NUL or control
characters, no device names, an allowed suffix, and (optionally) the path must stay inside a
base directory — which blocks ``../`` traversal and symlink escapes when paths come from input
files rather than from the user typing them.
"""
from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path

__all__ = ["UnsafePathError", "safe_output_path", "write_text_atomic", "write_bytes_atomic"]

_WINDOWS_DEVICES = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}


class UnsafePathError(ValueError):
    """An output path was rejected."""


def safe_output_path(path: str | os.PathLike[str], suffixes: Iterable[str] | None = None,
                     base_dir: str | os.PathLike[str] | None = None) -> Path:
    """Validate and normalise an output path.

    Parameters
    ----------
    path : path-like
        Requested output file.
    suffixes : iterable of str, optional
        Allowed extensions (lower case, with dot). ``None`` allows any.
    base_dir : path-like, optional
        If given, the resolved path must lie inside this directory.

    Raises
    ------
    UnsafePathError
        Empty path, control characters, reserved device name, wrong suffix, a directory, or a
        location outside ``base_dir``.
    """
    raw = os.fspath(path)
    if not raw or not raw.strip():
        raise UnsafePathError("empty output path")
    if re.search(r"[\x00-\x1f]", raw):
        raise UnsafePathError("output path contains control characters")
    p = Path(raw).expanduser()
    if p.stem.lower().split(".")[0] in _WINDOWS_DEVICES:
        raise UnsafePathError(f"reserved device name: {p.name}")
    if suffixes is not None:
        allowed = {s.lower() for s in suffixes}
        if p.suffix.lower() not in allowed:
            raise UnsafePathError(f"output must end with one of {sorted(allowed)}: {p.name}")
    resolved = p.resolve()
    if resolved.exists() and resolved.is_dir():
        raise UnsafePathError(f"output path is a directory: {resolved}")
    if base_dir is not None:
        base = Path(base_dir).resolve()
        if resolved != base and base not in resolved.parents:
            raise UnsafePathError(f"output path escapes {base}: {resolved}")
    return resolved


def write_bytes_atomic(path: str | os.PathLike[str], data: bytes, **kwargs: object) -> Path:
    """Atomically write ``data``; ``kwargs`` go to :func:`safe_output_path`. Returns the path."""
    target = safe_output_path(path, **kwargs)  # type: ignore[arg-type]
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return target


def write_text_atomic(path: str | os.PathLike[str], text: str, encoding: str = "utf-8", **kwargs: object) -> Path:
    """Atomically write text (UTF-8, ``\\n`` line endings). Returns the path."""
    return write_bytes_atomic(path, text.encode(encoding), **kwargs)
