from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, add_log_level_number

from osint_engine.observability.context import correlation_id

if TYPE_CHECKING:
    from structlog.typing import EventDict


def _add_correlation_id(
    logger: object,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: EventDict,
) -> EventDict:
    cid = correlation_id.get()

    if cid is not None:
        event_dict["correlation_id"] = str(cid)

    return event_dict


def configure_logging(*, debug: bool) -> None:
    renderer = ConsoleRenderer() if debug else JSONRenderer()

    structlog.configure(
        processors=[
            add_log_level,
            add_log_level_number,
            TimeStamper(fmt="iso"),
            _add_correlation_id,
            renderer,
        ]
    )
