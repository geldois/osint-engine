from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import Entity, IDType_co
from osint_engine.domain.errors.edge_error import EdgeSelfLoopError
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

SourceID_co = TypeVar("SourceID_co", bound=UUID, covariant=True)
TargetID_co = TypeVar("TargetID_co", bound=UUID, covariant=True)


class Edge(
    Entity[IDType_co],
    Generic[IDType_co, SourceID_co, TargetID_co],  # noqa: UP046
    id_fields=frozenset({"source_id", "target_id"}),
    namespace=EntityNAMESPACE.EDGE,
):
    source_id: SourceID_co
    target_id: TargetID_co

    @override
    def __init_subclass__(
        cls,
        *,
        id_fields: frozenset[str] | None,
        namespace: EntityNAMESPACE,
        **kwargs: object,
    ) -> None:
        """
        source_id and target_id are always included in identity calculation,
        regardless of id_fields.
        """

        if id_fields is not None:
            cls.id_fields |= id_fields

        super().__init_subclass__(
            id_fields=cls.id_fields, namespace=namespace, **kwargs
        )

    @abstractmethod
    @override
    def __init__(
        self, *, source_id: SourceID_co, target_id: TargetID_co, **kwargs: object
    ) -> None:
        if source_id == target_id:
            raise EdgeSelfLoopError(node_id=source_id)

        super().__init__(source_id=source_id, target_id=target_id, **kwargs)
