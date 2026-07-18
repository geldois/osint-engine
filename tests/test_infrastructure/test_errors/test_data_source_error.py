from __future__ import annotations

from osint_engine.infrastructure.errors.data_source_error import (
    UnexpectedFieldFormatError,
)

# TESTS


class TestUnexpectedFieldFormatError:
    def test_stores_all_reported_fields(self) -> None:
        error = UnexpectedFieldFormatError(
            source="portal_transparencia",
            key="valorMulta",
            raw_value="not-a-number",
            reason="not a valid pt-BR monetary amount",
        )

        assert error.source == "portal_transparencia"
        assert error.key == "valorMulta"
        assert error.raw_value == "not-a-number"
        assert error.reason == "not a valid pt-BR monetary amount"

    def test_message_reports_source_key_value_and_reason(self) -> None:
        error = UnexpectedFieldFormatError(
            source="portal_transparencia",
            key="valorMulta",
            raw_value="not-a-number",
            reason="not a valid pt-BR monetary amount",
        )

        message = str(error)

        assert "portal_transparencia" in message
        assert "valorMulta" in message
        assert "not-a-number" in message
        assert "not a valid pt-BR monetary amount" in message
