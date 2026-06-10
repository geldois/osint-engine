from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.entity import Edge, Node


class Graph:
    edges: frozenset[Edge[UUID]]
    nodes: frozenset[Node[UUID]]
    root_id: UUID

    def __init__(
        self,
        *,
        edges: frozenset[Edge],  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
        nodes: frozenset[Node],  # pyright: ignore[reportMissingTypeArgument, reportUnknownParameterType]
        root_id: UUID,
    ) -> None:
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "root_id", root_id)

    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return (
            self.edges == other.edges
            and self.nodes == other.nodes
            and self.root_id == other.root_id
        )

    def __hash__(self) -> int:
        return hash((self.edges, self.nodes, self.root_id))
