from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

from structlog import get_logger

from osint_engine.observability.context import correlation_id

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import Request, Response


async def http_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    cid = uuid4()
    correlation_id.set(cid)

    _logger = get_logger()
    _logger.info("request.start", method=request.method, path=request.url.path)

    start = perf_counter()

    response = await call_next(request)

    _logger.info(
        "request.end",
        status=response.status_code,
        latency_ms=round((perf_counter() - start) * 1000, 2),
    )

    response.headers["X-Correlation-ID"] = str(correlation_id.get())

    return response
