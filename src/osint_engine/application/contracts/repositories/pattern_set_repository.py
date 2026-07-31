from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet


class PatternSetRepository(ABC):
    @abstractmethod
    async def list(self) -> tuple[TextPatternSet, ...]:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, id_: PatternSetID) -> TextPatternSet:
        raise NotImplementedError
