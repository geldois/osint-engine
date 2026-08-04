from __future__ import annotations

import pytest

from osint_engine.application.use_cases.text_ingestion.list_text_pattern_sets import (
    ListTextPatternSets,
)
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENT_PATTERNS,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_pattern_set_repository import (  # noqa: E501
    MemPatternSetRepository,
)


class TestListTextPatternSets:
    @pytest.mark.asyncio
    async def test_returns_every_pattern_set_from_the_repository(self) -> None:
        repository = MemPatternSetRepository(
            pattern_sets=(BRAZILIAN_DOCUMENT_PATTERNS,)
        )
        use_case = ListTextPatternSets(pattern_set_repository=repository)

        result = await use_case.execute()

        assert result == (BRAZILIAN_DOCUMENT_PATTERNS,)

    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_no_pattern_sets_are_seeded(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=())
        use_case = ListTextPatternSets(pattern_set_repository=repository)

        result = await use_case.execute()

        assert result == ()
