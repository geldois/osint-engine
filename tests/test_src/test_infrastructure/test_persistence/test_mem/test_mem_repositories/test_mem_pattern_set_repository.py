from __future__ import annotations

import re

import pytest

from osint_engine.application.errors.text_ingestion_error import (
    PatternSetNotFoundError,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import FieldPattern, TextPatternSet
from osint_engine.infrastructure.persistence.mem.repositories.mem_pattern_set_repository import (  # noqa: E501
    MemPatternSetRepository,
)

_PATTERN_SET = TextPatternSet(
    id=PatternSetID("test_set"),
    patterns=(FieldPattern(node_type=Person, regex=re.compile(r"(?P<cpf>\d{11})")),),
)


class TestMemPatternSetRepositoryList:
    @pytest.mark.asyncio
    async def test_returns_every_seeded_pattern_set(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_PATTERN_SET,))

        result = await repository.list()

        assert result == (_PATTERN_SET,)


class TestMemPatternSetRepositoryGet:
    @pytest.mark.asyncio
    async def test_returns_the_pattern_set_by_id(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_PATTERN_SET,))

        result = await repository.get(id_=_PATTERN_SET.id)

        assert result is _PATTERN_SET

    @pytest.mark.asyncio
    async def test_raises_for_an_unknown_id(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_PATTERN_SET,))

        with pytest.raises(PatternSetNotFoundError):
            await repository.get(id_=PatternSetID("unknown"))
