from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.presenters.text_pattern_set_presenter import (
    text_pattern_catalog_to_schema,
)
from osint_engine.interface.http.schemas.text_ingestion_schema import (  # noqa: TC001
    TextPatternCatalogSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_text_patterns_handler(
    *, container: Container
) -> Callable[[dict[str, object]], Awaitable[TextPatternCatalogSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_text_patterns(
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> TextPatternCatalogSchema:
        del payload

        use_case = container.use_cases.list_text_patterns()

        catalog = await use_case.execute()

        return text_pattern_catalog_to_schema(
            patterns=catalog.patterns, bundles=catalog.bundles
        )

    return get_text_patterns
