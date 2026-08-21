from __future__ import annotations

from datetime import UTC, datetime

import pytest

from osint_engine.interface.http.schemas.revision_schema import RevisionSchema


@pytest.fixture
def revision_schema() -> RevisionSchema:
    return RevisionSchema(
        fetched_at=datetime(year=2026, month=1, day=1, tzinfo=UTC),
        merged_at=None,
        provider="test_provider",
    )
