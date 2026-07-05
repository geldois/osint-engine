from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.entity_error import EntityError

if TYPE_CHECKING:
    from uuid import UUID


class EdgeError(EntityError, error_code=None): ...


class SelfLoopEdgeError(EdgeError, error_code="EDGE_SELF_LOOP"):
    node_id: UUID

    @override
    def __init__(self, *, node_id: UUID) -> None:
        super().__init__(node_id=node_id)

    @override
    def _build_message(self) -> str:
        return (
            f"An edge cannot have the same source and target node. "
            f"Self-loop at node '{self.node_id}' is not allowed."
        )
