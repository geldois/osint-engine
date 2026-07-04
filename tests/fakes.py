from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

FakeEntityID = NewType("FakeEntityID", UUID)
FakeEdgeID = NewType("FakeEdgeID", UUID)
FakeNodeID = NewType("FakeNodeID", UUID)


class FakeEntity(Entity[FakeEntityID], namespace=EntityNAMESPACE.TEST):
    content: str

    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(identity_fields=None, content=content, **kwargs)


class FakeEdge(Edge[FakeEdgeID], namespace=EntityNAMESPACE.TEST_EDGE):
    content: str

    @override
    def __init__(
        self, *, source_id: UUID, target_id: UUID, content: str, **kwargs: object
    ) -> None:
        super().__init__(
            identity_fields=None,
            source_id=source_id,
            target_id=target_id,
            content=content,
            **kwargs,
        )


class FakeNode(Node[FakeNodeID], namespace=EntityNAMESPACE.TEST_NODE):
    content: str

    @override
    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(identity_fields=None, content=content, **kwargs)
