from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.value_objects.text_pattern import TextPatternName

if TYPE_CHECKING:
    from osint_engine.application.contracts.repositories.pattern_set_repository import (
        PatternSetRepository,
    )
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet

_logger = get_logger()


@dataclass(frozen=True, kw_only=True)
class TextPatternCatalog:
    patterns: tuple[TextPatternName, ...]
    bundles: tuple[TextPatternSet, ...]


class ListTextPatterns(Query[TextPatternCatalog]):
    pattern_set_repository: PatternSetRepository

    @override
    def __init__(self, *, pattern_set_repository: PatternSetRepository) -> None:
        super().__init__(pattern_set_repository=pattern_set_repository)

    @override
    async def execute(self) -> TextPatternCatalog:
        _logger.info("text_ingestion.list_patterns.start")

        bundles = await self.pattern_set_repository.list_bundles()

        catalog = TextPatternCatalog(patterns=tuple(TextPatternName), bundles=bundles)

        _logger.info(
            "text_ingestion.list_patterns.success",
            pattern_count=len(catalog.patterns),
            bundle_count=len(catalog.bundles),
        )

        return catalog
