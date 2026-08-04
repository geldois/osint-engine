from __future__ import annotations

from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENT_PATTERNS,
)
from osint_engine.interface.http.presenters.text_pattern_set_presenter import (
    text_pattern_set_to_schema,
)


class TestTextPatternSetPresenter:
    def test_maps_id_and_every_pattern_s_covered_fields(self) -> None:
        result = text_pattern_set_to_schema(pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        assert result.id == BRAZILIAN_DOCUMENT_PATTERNS.id
        assert len(result.patterns) == len(BRAZILIAN_DOCUMENT_PATTERNS.patterns)

    def test_does_not_expose_the_compiled_regex(self) -> None:
        result = text_pattern_set_to_schema(pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        dumped = result.model_dump()

        assert "regex" not in str(dumped)

    def test_person_pattern_reports_cpf_as_a_covered_field(self) -> None:
        result = text_pattern_set_to_schema(pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        person_summary = next(p for p in result.patterns if p.node_type == "Person")

        assert person_summary.fields == ["cpf"]
