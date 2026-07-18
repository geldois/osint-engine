from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.stdlib import get_logger
from structlog.testing import LogCapture

from osint_engine.observability.context import correlation_id
from osint_engine.observability.structlog.config import configure_logging

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def _restore_structlog() -> Generator[None, None, None]:  # pyright: ignore[reportUnusedFunction]
    yield

    structlog.reset_defaults()
    correlation_id.set(None)


@pytest.fixture
def log_capture() -> LogCapture:
    configure_logging(debug=False)

    processors = structlog.get_config()["processors"]
    capture = LogCapture()
    structlog.configure(processors=[*processors[:-1], capture])

    return capture


# TESTS


class TestConfigureLoggingRendererSelection:
    def test_debug_mode_uses_console_renderer(self) -> None:
        configure_logging(debug=True)

        assert isinstance(structlog.get_config()["processors"][-1], ConsoleRenderer)

    def test_production_mode_uses_json_renderer(self) -> None:
        configure_logging(debug=False)

        assert isinstance(structlog.get_config()["processors"][-1], JSONRenderer)


class TestConfigureLoggingEventDictFields:
    def test_log_event_includes_level(self, log_capture: LogCapture) -> None:
        get_logger().info("event")

        assert "level" in log_capture.entries[0]

    def test_log_event_includes_level_number(self, log_capture: LogCapture) -> None:
        get_logger().info("event")

        assert "level_number" in log_capture.entries[0]

    def test_log_event_includes_timestamp(self, log_capture: LogCapture) -> None:
        get_logger().info("event")

        assert "timestamp" in log_capture.entries[0]

    def test_log_event_timestamp_is_iso8601_formatted(
        self, log_capture: LogCapture
    ) -> None:
        get_logger().info("event")

        timestamp = log_capture.entries[0]["timestamp"]

        assert isinstance(timestamp, str)

        datetime.fromisoformat(timestamp)

    def test_log_event_includes_correlation_id_when_set(
        self, log_capture: LogCapture
    ) -> None:
        cid = uuid4()
        correlation_id.set(cid)

        get_logger().info("event")

        entry = log_capture.entries[0]

        assert "correlation_id" in entry

        assert entry["correlation_id"] == str(cid)

    def test_log_event_omits_correlation_id_when_not_set(
        self, log_capture: LogCapture
    ) -> None:
        get_logger().info("event")

        assert "correlation_id" not in log_capture.entries[0]
