from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.batch_presenter import (
    batch_estimate_to_schema,
    batch_result_to_schema,
)
from osint_engine.interface.http.schemas.batch_schema import (
    BatchCPFEstimateSchema,  # noqa: TC001
    BatchCPFRequestSchema,  # noqa: TC001
    BatchCPFResultSchema,  # noqa: TC001
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_cpf_batch_handler(
    *, container: Container
) -> Callable[
    [BatchCPFRequestSchema, dict[str, object]], Awaitable[BatchCPFResultSchema]
]:
    jwt_guard = build_jwt_guard(container=container)

    async def post_cpf_batch(
        body: BatchCPFRequestSchema,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> BatchCPFResultSchema:
        use_case = container.use_cases.expand_by_cpf_batch(
            cpfs=tuple(body.cpfs),
            force=body.force,
            username=str(payload["sub"]),
        )

        revision, outcomes = await use_case.execute()

        return batch_result_to_schema(revision, outcomes)

    return post_cpf_batch


def build_post_cpf_batch_estimate_handler(
    *, container: Container
) -> Callable[
    [BatchCPFRequestSchema, dict[str, object]], Awaitable[BatchCPFEstimateSchema]
]:
    jwt_guard = build_jwt_guard(container=container)

    async def post_cpf_batch_estimate(
        body: BatchCPFRequestSchema,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> BatchCPFEstimateSchema:
        use_case = container.use_cases.estimate_cpf_batch(
            cpfs=tuple(body.cpfs),
            force=body.force,
            username=str(payload["sub"]),
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        return batch_estimate_to_schema(
            already_fetched, billable, invalid, wait_seconds
        )

    return post_cpf_batch_estimate
