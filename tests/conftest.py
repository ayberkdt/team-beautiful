"""Shared pytest configuration for the aerokit test-suite."""
import matplotlib

matplotlib.use("Agg")

from aerokit import verification  # noqa: E402


def pytest_terminal_summary(terminalreporter):
    passed, total = verification.summary()
    terminalreporter.write_sep("-", f"aerokit numerical checks: {passed}/{total} passed")
