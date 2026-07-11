from __future__ import annotations

from uuid import uuid4

import pytest

from osint_engine.domain.errors.edge_error import EdgeSelfLoopError
from tests.fakes.domain import FakeEdge


class TestEdgeIdentity:
    def test_id_uses_source_and_target_by_default(
        self,
    ) -> None:
        source = uuid4()
        target = uuid4()

        edge_a = FakeEdge(
            identity_fields=None, source_id=source, target_id=target, content="edge_a"
        )
        edge_b = FakeEdge(
            identity_fields=None, source_id=source, target_id=target, content="edge_b"
        )

        assert edge_a.id == edge_b.id

    def test_edge_id_includes_additional_identity_fields_when_specified(self) -> None:
        source = uuid4()
        target = uuid4()

        edge_a = FakeEdge(
            identity_fields=frozenset({"content"}),
            source_id=source,
            target_id=target,
            content="edge_a",
        )
        edge_b = FakeEdge(
            identity_fields=frozenset({"content"}),
            source_id=source,
            target_id=target,
            content="edge_b",
        )

        assert edge_a.id != edge_b.id


class TestEdgeValidation:
    def test_raises_when_source_and_target_are_identical(self) -> None:
        node_id = uuid4()

        with pytest.raises(EdgeSelfLoopError) as exception:
            FakeEdge(source_id=node_id, target_id=node_id, content="test")

        assert str(node_id) in str(exception.value)
