from __future__ import annotations

import pytest

from osint_engine.application.use_cases.text_ingestion.list_text_patterns import (
    ListTextPatterns,
)
from osint_engine.domain.value_objects.text_pattern import TextPatternName
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENTS_V1,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_pattern_set_repository import (  # noqa: E501
    MemPatternSetRepository,
)


class TestListTextPatterns:
    @pytest.mark.asyncio
    async def test_returns_every_member_of_the_atomic_catalog(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(BRAZILIAN_DOCUMENTS_V1,))
        use_case = ListTextPatterns(pattern_set_repository=repository)

        result = await use_case.execute()

        assert result.patterns == tuple(TextPatternName)

    @pytest.mark.asyncio
    async def test_returns_every_bundle_from_the_repository(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(BRAZILIAN_DOCUMENTS_V1,))
        use_case = ListTextPatterns(pattern_set_repository=repository)

        result = await use_case.execute()

        assert result.bundles == (BRAZILIAN_DOCUMENTS_V1,)

    @pytest.mark.asyncio
    async def test_returns_empty_bundles_when_none_are_seeded(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=())
        use_case = ListTextPatterns(pattern_set_repository=repository)

        result = await use_case.execute()

        assert result.bundles == ()
        assert result.patterns == tuple(TextPatternName)
