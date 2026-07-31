from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.pattern_set_repository import (
    PatternSetRepository,
)
from osint_engine.application.errors.text_ingestion_error import (
    PatternSetNotFoundError,
)

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet


class MemPatternSetRepository(PatternSetRepository):
    @override
    def __init__(self, *, pattern_sets: tuple[TextPatternSet, ...]) -> None:
        self._by_id = {pattern_set.id: pattern_set for pattern_set in pattern_sets}

    @override
    async def list(self) -> tuple[TextPatternSet, ...]:
        return tuple(self._by_id.values())

    @override
    async def get(self, *, id_: PatternSetID) -> TextPatternSet:
        found = self._by_id.get(id_)

        if found is None:
            raise PatternSetNotFoundError(pattern_set_id=id_)

        return found
