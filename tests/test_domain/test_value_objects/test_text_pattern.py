from __future__ import annotations

import re

import pytest

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.text_pattern_error import FieldPatternGroupMismatchError
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import FieldPattern, TextPatternSet


class TestFieldPatternGroupValidation:
    def test_accepts_a_regex_whose_named_groups_match_id_fields_exactly(self) -> None:
        pattern = FieldPattern(node_type=Person, regex=re.compile(r"(?P<cpf>\d{11})"))

        assert pattern.node_type is Person

    def test_accepts_a_composite_regex_matching_a_multi_field_identity(self) -> None:
        pattern = FieldPattern(
            node_type=Address,
            regex=re.compile(r"(?P<cep>\d{8})-(?P<number>\d+)"),
        )

        assert frozenset(pattern.regex.groupindex) == Address.id_fields

    def test_raises_when_a_named_group_is_missing(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError):
            FieldPattern(node_type=Company, regex=re.compile(r"\d{14}"))

    def test_raises_when_a_named_group_does_not_belong_to_id_fields(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError):
            FieldPattern(node_type=Person, regex=re.compile(r"(?P<wrong_field>\d{11})"))

    def test_error_reports_expected_and_actual_groups(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError) as exc_info:
            FieldPattern(node_type=Person, regex=re.compile(r"(?P<wrong_field>\d{11})"))

        error = exc_info.value

        assert error.node_type is Person
        assert error.expected == Person.id_fields
        assert error.actual == frozenset({"wrong_field"})


class TestTextPatternSet:
    def test_holds_its_id_and_patterns(self) -> None:
        pattern = FieldPattern(node_type=Person, regex=re.compile(r"(?P<cpf>\d{11})"))
        pattern_set = TextPatternSet(id=PatternSetID("test_set"), patterns=(pattern,))

        assert pattern_set.id == "test_set"
        assert pattern_set.patterns == (pattern,)
