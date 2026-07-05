from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.entity_error import EntityError

if TYPE_CHECKING:
    from uuid import UUID


class GraphError(EntityError, error_code=None): ...


class HasNoNodesGraphError(GraphError, error_code="GRAPH_HAS_NO_NODES"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "A graph must have at least one node."


class RootNotInNodesGraphError(GraphError, error_code="GRAPH_ROOT_NOT_IN_NODES"):
    root_id: UUID

    @override
    def __init__(self, *, root_id: UUID) -> None:
        super().__init__(root_id=root_id)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.root_id}' is not present in the graph's nodes. "
            f"The root node must be part of the graph."
        )


class InconsistentGraphError(GraphError, error_code="GRAPH_INCONSISTENT"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return (
            "The graph is inconsistent: one or more edges reference nodes "
            "that do not exist in the graph."
        )
