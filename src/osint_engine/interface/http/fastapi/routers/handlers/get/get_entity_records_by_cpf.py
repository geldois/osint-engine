from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.domain.services.sanitization import sanitize_cpf
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.entity_record_presenter import (
    entity_record_to_schema,
)
from osint_engine.interface.http.schemas.entity_record_schema import (  # noqa: TC001
    EntityRecordSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_entity_records_by_cpf_handler(
    *, container: Container
) -> Callable[[str, dict[str, object]], Awaitable[list[EntityRecordSchema]]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_entity_records_by_cpf(
        cpf: str,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[EntityRecordSchema]:
        del payload

        cpf = sanitize_cpf(cpf)

        use_case = container.use_cases.list_entity_records_by_cpf(cpf=cpf)

        records = await use_case.execute()

        return [entity_record_to_schema(record) for record in records]

    return get_entity_records_by_cpf
