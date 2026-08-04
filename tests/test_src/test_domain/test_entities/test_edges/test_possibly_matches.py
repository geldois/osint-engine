from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from osint_engine.domain.entities.edges.possibly_matches import PossiblyMatches


class TestPossiblyMatchesCanonicalOrdering:
    def test_id_is_the_same_regardless_of_argument_order(self) -> None:
        left, right = sorted((uuid4(), uuid4()))

        forward = PossiblyMatches(
            source_id=left, target_id=right, confidence=Decimal("0.9")
        )
        backward = PossiblyMatches(
            source_id=right, target_id=left, confidence=Decimal("0.9")
        )

        assert forward.id == backward.id

    def test_stores_source_as_the_lexicographically_smaller_id(self) -> None:
        left, right = sorted((uuid4(), uuid4()))

        edge = PossiblyMatches(
            source_id=right, target_id=left, confidence=Decimal("0.5")
        )

        assert edge.source_id == left
        assert edge.target_id == right


class TestPossiblyMatchesIdentity:
    def test_confidence_is_not_part_of_identity(self) -> None:
        left, right = sorted((uuid4(), uuid4()))

        low = PossiblyMatches(
            source_id=left, target_id=right, confidence=Decimal("0.1")
        )
        high = PossiblyMatches(
            source_id=left, target_id=right, confidence=Decimal("0.9")
        )

        assert low.id == high.id
        assert low.content_id != high.content_id
