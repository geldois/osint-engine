from __future__ import annotations

import pytest

from osint_engine.domain.entities.nodes.text_source import TextSource
from osint_engine.domain.errors.text_source_error import TextSourceEmptyError


class TestTextSourceIdentity:
    def test_same_text_produces_the_same_id(self) -> None:
        first = TextSource(text="CPF 111.444.777-35")
        second = TextSource(text="CPF 111.444.777-35")

        assert first.id == second.id

    def test_different_text_produces_a_different_id(self) -> None:
        first = TextSource(text="CPF 111.444.777-35")
        second = TextSource(text="CPF 999.999.999-99")

        assert first.id != second.id

    def test_stores_the_raw_text(self) -> None:
        text_source = TextSource(text="raw text content")

        assert text_source.text == "raw text content"


class TestTextSourceValidation:
    def test_raises_for_empty_text(self) -> None:
        with pytest.raises(TextSourceEmptyError):
            TextSource(text="")

    def test_raises_for_whitespace_only_text(self) -> None:
        with pytest.raises(TextSourceEmptyError):
            TextSource(text="   \n\t  ")
