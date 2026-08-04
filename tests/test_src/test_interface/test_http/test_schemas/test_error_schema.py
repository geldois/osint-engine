from __future__ import annotations

from datetime import UTC

from osint_engine.interface.http.schemas.error_schema import ErrorSchema


class TestErrorSchemaTimestamp:
    def test_timestamp_is_utc_aware(self) -> None:
        schema = ErrorSchema(detail="test", method="GET", path="/")

        assert schema.timestamp.tzinfo is UTC
