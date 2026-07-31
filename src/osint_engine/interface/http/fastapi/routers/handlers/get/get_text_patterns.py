from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.text_pattern_set_presenter import (
    text_pattern_set_to_schema,
)
from osint_engine.interface.http.schemas.text_ingestion_schema import (  # noqa: TC001
    TextPatternSetSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_text_patterns_handler(
    *, container: Container
) -> Callable[[dict[str, object]], Awaitable[list[TextPatternSetSchema]]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_text_patterns(
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[TextPatternSetSchema]:
        del payload

        use_case = container.use_cases.list_text_pattern_sets()

        pattern_sets = await use_case.execute()

        return [
            text_pattern_set_to_schema(pattern_set=pattern_set)
            for pattern_set in pattern_sets
        ]

    return get_text_patterns
