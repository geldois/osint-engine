from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.text_ingestion.list_text_patterns import (
    ListTextPatterns,
)
from osint_engine.domain.value_objects.text_pattern import TextPatternName
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENTS_V1,
)

if TYPE_CHECKING:
    from tests.conftest import MakeMemStorage, MakeMemUoW
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


class TestListTextPatterns:
    @pytest.mark.asyncio
    async def test_returns_every_member_of_the_atomic_catalog(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = ListTextPatterns(uow_factory=make_mem_uow_factory())

        result = await use_case.execute()

        assert result.patterns == tuple(TextPatternName)

    @pytest.mark.asyncio
    async def test_returns_every_bundle_from_the_repository(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_storage = make_mem_storage(pattern_sets=[BRAZILIAN_DOCUMENTS_V1])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        use_case = ListTextPatterns(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        result = await use_case.execute()

        assert result.bundles == (BRAZILIAN_DOCUMENTS_V1,)

    @pytest.mark.asyncio
    async def test_returns_empty_bundles_when_none_are_seeded(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = ListTextPatterns(uow_factory=make_mem_uow_factory())

        result = await use_case.execute()

        assert result.bundles == ()
        assert result.patterns == tuple(TextPatternName)
