from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.value_objects.text_pattern import TextPatternSet

if TYPE_CHECKING:
    from osint_engine.application.contracts.repositories.pattern_set_repository import (
        PatternSetRepository,
    )

_logger = get_logger()


class ListTextPatternSets(Query[tuple[TextPatternSet, ...]]):
    pattern_set_repository: PatternSetRepository

    @override
    def __init__(self, *, pattern_set_repository: PatternSetRepository) -> None:
        super().__init__(pattern_set_repository=pattern_set_repository)

    @override
    async def execute(self) -> tuple[TextPatternSet, ...]:
        _logger.info("text_ingestion.list_patterns.start")

        pattern_sets = await self.pattern_set_repository.list()

        _logger.info(
            "text_ingestion.list_patterns.success", pattern_set_count=len(pattern_sets)
        )

        return pattern_sets
