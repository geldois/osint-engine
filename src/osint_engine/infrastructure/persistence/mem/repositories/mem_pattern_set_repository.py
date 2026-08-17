from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.pattern_set_repository import (
    PatternSetRepository,
)
from osint_engine.application.errors.text_ingestion_error import (
    UnknownPatternNameError,
)
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import TextPatternName

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemPatternSetRepository(PatternSetRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.pattern_sets = mem_storage.pattern_sets

    @override
    async def list_bundles(self) -> tuple[TextPatternSet, ...]:
        return tuple(self.pattern_sets.values())

    @override
    async def resolve(self, *, names: frozenset[str]) -> frozenset[TextPatternName]:
        resolved: set[TextPatternName] = set()
        unknown: list[str] = []

        for name in names:
            bundle = self.pattern_sets.get(PatternSetID(name))

            if bundle is not None:
                resolved.update(bundle.patterns)
                continue

            try:
                resolved.add(TextPatternName[name])
            except KeyError:
                unknown.append(name)

        if unknown:
            raise UnknownPatternNameError(names=frozenset(unknown))

        return frozenset(resolved)
