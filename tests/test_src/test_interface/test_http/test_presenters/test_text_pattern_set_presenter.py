from __future__ import annotations

from osint_engine.domain.value_objects.text_pattern import TextPatternName
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENTS_V1,
)
from osint_engine.interface.http.presenters.text_pattern_set_presenter import (
    text_pattern_catalog_to_schema,
)


class TestTextPatternCatalogPresenterPatterns:
    def test_lists_every_atomic_pattern_name(self) -> None:
        result = text_pattern_catalog_to_schema(
            patterns=tuple(TextPatternName), bundles=()
        )

        assert len(result.patterns) == len(TextPatternName)
        assert {p.name for p in result.patterns} == {p.name for p in TextPatternName}

    def test_does_not_expose_the_compiled_regex(self) -> None:
        result = text_pattern_catalog_to_schema(
            patterns=tuple(TextPatternName), bundles=()
        )

        assert "regex" not in str(result.model_dump())

    def test_cpf_loose_pattern_reports_cpf_as_a_covered_field(self) -> None:
        result = text_pattern_catalog_to_schema(
            patterns=(TextPatternName.CPF_LOOSE,), bundles=()
        )

        assert result.patterns[0].name == "CPF_LOOSE"
        assert result.patterns[0].node_type == "Person"
        assert result.patterns[0].fields == ["cpf"]


class TestTextPatternCatalogPresenterBundles:
    def test_lists_every_bundle_with_its_pattern_names(self) -> None:
        result = text_pattern_catalog_to_schema(
            patterns=(), bundles=(BRAZILIAN_DOCUMENTS_V1,)
        )

        assert len(result.bundles) == 1
        assert result.bundles[0].id == BRAZILIAN_DOCUMENTS_V1.id
        assert result.bundles[0].pattern_names == ["CPF_LOOSE"]

    def test_returns_empty_bundles_for_an_empty_input(self) -> None:
        result = text_pattern_catalog_to_schema(patterns=(), bundles=())

        assert result.bundles == []
