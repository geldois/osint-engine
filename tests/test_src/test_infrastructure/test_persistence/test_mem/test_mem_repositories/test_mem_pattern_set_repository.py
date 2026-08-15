from __future__ import annotations

import pytest

from osint_engine.application.errors.text_ingestion_error import (
    UnknownPatternNameError,
)
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import (
    TextPatternName,
    TextPatternSet,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_pattern_set_repository import (  # noqa: E501
    MemPatternSetRepository,
)

_BUNDLE = TextPatternSet(
    id=PatternSetID("test_bundle"),
    patterns=frozenset({TextPatternName.CPF_LOOSE}),
)


class TestMemPatternSetRepositoryListBundles:
    @pytest.mark.asyncio
    async def test_returns_every_seeded_bundle(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_BUNDLE,))

        result = await repository.list_bundles()

        assert result == (_BUNDLE,)

    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_no_bundle_is_seeded(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=())

        result = await repository.list_bundles()

        assert result == ()


class TestMemPatternSetRepositoryResolve:
    @pytest.mark.asyncio
    async def test_resolves_a_bundle_name_to_its_patterns(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_BUNDLE,))

        result = await repository.resolve(names=frozenset({"test_bundle"}))

        assert result == frozenset({TextPatternName.CPF_LOOSE})

    @pytest.mark.asyncio
    async def test_resolves_an_atomic_name_without_any_bundle_involved(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=())

        result = await repository.resolve(names=frozenset({"CNPJ_LOOSE"}))

        assert result == frozenset({TextPatternName.CNPJ_LOOSE})

    @pytest.mark.asyncio
    async def test_resolves_a_mix_of_bundle_and_atomic_names_as_a_union(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_BUNDLE,))

        result = await repository.resolve(
            names=frozenset({"test_bundle", "CNPJ_LOOSE"})
        )

        assert result == frozenset(
            {TextPatternName.CPF_LOOSE, TextPatternName.CNPJ_LOOSE}
        )

    @pytest.mark.asyncio
    async def test_raises_for_a_single_unknown_name(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=(_BUNDLE,))

        with pytest.raises(UnknownPatternNameError) as exception:
            await repository.resolve(names=frozenset({"nao_existe", "CNPJ_LOOSE"}))

        assert exception.value.names == frozenset({"nao_existe"})

    @pytest.mark.asyncio
    async def test_reports_every_unknown_name_at_once(self) -> None:
        repository = MemPatternSetRepository(pattern_sets=())

        with pytest.raises(UnknownPatternNameError) as exception:
            await repository.resolve(names=frozenset({"nao_existe", "tambem_nao"}))

        assert exception.value.names == frozenset({"nao_existe", "tambem_nao"})
