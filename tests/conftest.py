from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from hypothesis import settings as hypothesis_settings
from hypothesis.configuration import set_hypothesis_home_dir
from hypothesis.database import DirectoryBasedExampleDatabase

if TYPE_CHECKING:
    from collections.abc import Generator

pytest_plugins = [
    "tests.fixtures.application",
    "tests.fixtures.domain",
    "tests.fixtures.git",
    "tests.fixtures.persistence",
    "tests.fixtures.postgres",
    "tests.fixtures.settings",
]

set_hypothesis_home_dir(".cache/hypothesis")
hypothesis_settings.register_profile(
    "osint_engine", database=DirectoryBasedExampleDatabase(".cache/hypothesis")
)
hypothesis_settings.load_profile("osint_engine")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,  # noqa: ARG001
    call: pytest.CallInfo[None],  # noqa: ARG001
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield

    if report.skipped and isinstance(report.longrepr, tuple):
        _, _, reason = report.longrepr
        report.outcome = "failed"
        report.longrepr = (
            f"{reason} — this suite allows no skips. Fix the environment (see "
            f"README: Setup), or commit with --no-verify and say why."
        )

    return report
