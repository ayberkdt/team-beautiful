# Copied from Sidera (sidera.common.errors, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""The common base of every error Sidera raises on purpose.

Each subsystem keeps its own error type -- ``RfError``, ``LambertError``,
``EarthOrientationDataError`` and so on -- and each still derives from the
built-in it always did (``ValueError`` or ``RuntimeError``), so existing
``except ValueError`` handlers keep working. What this adds is one type a
caller can catch to mean "Sidera refused or failed", without listing every
subsystem::

    try:
        report = run_contact_request(request)
    except SideraError as error:
        print(f"analysis refused: {error}")

Bugs are not ``SideraError``: an ``IndexError`` or ``AttributeError`` from
inside the library is still a plain built-in, as it should be.
"""

from __future__ import annotations

__all__ = ["SideraError"]


class SideraError(Exception):
    """Base class for errors Sidera raises deliberately (invalid input, missing data, refused runs)."""
