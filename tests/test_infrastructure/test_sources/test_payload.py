from __future__ import annotations

import pytest

from osint_engine.infrastructure.errors.data_source_error import UnexpectedPayloadError
from osint_engine.infrastructure.sources.payload import Payload

# TESTS


class TestPayloadRequire:
    def test_raises_when_key_is_missing(self) -> None:
        payload = Payload(source="test", data={})

        with pytest.raises(UnexpectedPayloadError):
            payload.require(key="field", expected_type=str)


class TestPayloadOptional:
    def test_returns_none_when_key_is_absent(self) -> None:
        payload = Payload(source="test", data={})

        result = payload.optional(key="field", expected_type=str)

        assert result is None

    def test_returns_none_when_value_is_null(self) -> None:
        payload = Payload(source="test", data={"field": None})

        result = payload.optional(key="field", expected_type=str)

        assert result is None
