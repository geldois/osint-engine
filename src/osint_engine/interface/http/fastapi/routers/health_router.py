from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from structlog import get_logger

if TYPE_CHECKING:
    from osint_engine.config.container import Container

_HTTP_SERVICE_UNAVAILABLE = 503


def build_health_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/health", tags=["health"])

    async def liveness() -> dict[str, str]:

        return {"status": "ok"}

    async def readiness() -> JSONResponse:
        try:
            await container.readiness_probe()
        except Exception:  # noqa: BLE001
            get_logger().warning("health.readiness.failed", exc_info=True)

            return JSONResponse(
                status_code=_HTTP_SERVICE_UNAVAILABLE, content={"status": "not_ready"}
            )

        return JSONResponse(status_code=200, content={"status": "ready"})

    router.get(path="")(liveness)
    router.get(path="/ready")(readiness)

    return router
