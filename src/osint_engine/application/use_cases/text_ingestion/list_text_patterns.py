from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.value_objects.text_pattern import TextPatternName

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet

_logger = get_logger()


@dataclass(frozen=True, kw_only=True)
class TextPatternCatalog:
    patterns: tuple[TextPatternName, ...]
    bundles: tuple[TextPatternSet, ...]


class ListTextPatterns(Query[TextPatternCatalog]):
    uow_factory: Callable[[], UoW]

    @override
    def __init__(self, *, uow_factory: Callable[[], UoW]) -> None:
        super().__init__(uow_factory=uow_factory)

    @override
    async def execute(self) -> TextPatternCatalog:
        _logger.info("text_ingestion.list_patterns.start")

        async with self.uow_factory() as uow:
            bundles = await uow.pattern_sets.list_bundles()

        catalog = TextPatternCatalog(patterns=tuple(TextPatternName), bundles=bundles)

        _logger.info(
            "text_ingestion.list_patterns.success",
            pattern_count=len(catalog.patterns),
            bundle_count=len(catalog.bundles),
        )

        return catalog
