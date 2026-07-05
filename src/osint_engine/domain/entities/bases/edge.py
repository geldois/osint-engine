from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar, override
from uuid import UUID

from osint_engine.domain.entities.entity import Entity, IDType_co
from osint_engine.domain.errors.edge_error import SelfLoopEdgeError
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

SourceID_co = TypeVar("SourceID_co", bound=UUID, covariant=True)
TargetID_co = TypeVar("TargetID_co", bound=UUID, covariant=True)


class Edge(
    Entity[IDType_co],
    Generic[IDType_co, SourceID_co, TargetID_co],  # noqa: UP046
    namespace=EntityNAMESPACE.EDGE,
):
    source_id: SourceID_co
    target_id: TargetID_co

    @abstractmethod
    @override
    def __init__(
        self,
        *,
        identity_fields: frozenset[str] | None = None,
        source_id: SourceID_co,
        target_id: TargetID_co,
        **kwargs: object,
    ) -> None:
        """
        source_id and target_id are always included in identity calculation,
        regardless of identity_fields.
        """

        identity_fields = (
            identity_fields if identity_fields is not None else frozenset[str]()
        ) | frozenset({"source_id", "target_id"})

        if source_id == target_id:
            raise SelfLoopEdgeError(node_id=source_id)

        super().__init__(
            identity_fields=identity_fields,
            source_id=source_id,
            target_id=target_id,
            **kwargs,
        )
