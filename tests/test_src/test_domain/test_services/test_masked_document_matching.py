from __future__ import annotations

from osint_engine.domain.services.masked_document_matching import (
    masked_document_overlap,
)


class TestMaskedDocumentOverlap:
    def test_overlaps_visible_digits_across_differently_masked_values(self) -> None:
        assert masked_document_overlap(left="***128734**", right="1**128734**") == 6

    def test_returns_none_when_no_visible_position_coincides(self) -> None:
        assert masked_document_overlap(left="***128734**", right="***999999**") is None

    def test_returns_none_when_any_visible_digit_diverges(self) -> None:
        assert masked_document_overlap(left="***123400**", right="111123499**") is None

    def test_returns_full_overlap_for_identical_complete_documents(self) -> None:
        assert masked_document_overlap(left="12312345678", right="12312345678") == 11

    def test_returns_minimum_overlap_at_the_boundary(self) -> None:
        assert masked_document_overlap(left="***1234****", right="1**1234****") == 4

    def test_returns_none_below_the_minimum_overlap(self) -> None:
        assert masked_document_overlap(left="***123*****", right="4**123*****") is None

    def test_returns_none_for_different_lengths_without_raising(self) -> None:
        assert masked_document_overlap(left="***128734**", right="***128734*") is None
