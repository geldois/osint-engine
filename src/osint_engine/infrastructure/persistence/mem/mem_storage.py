from __future__ import annotations

from collections import defaultdict
from copy import copy
from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING, final, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import Entity

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import (
        ExternalCredential,
        Provider,
    )
    from osint_engine.application.auth.user import User
    from osint_engine.application.consumption.entity_record import EntityRecord
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet


class MemStorage:
    edges: defaultdict[UUID, dict[UUID, EntityRevision[Edge[UUID, UUID, UUID]]]]
    entity_records: list[EntityRecord]
    external_credentials: dict[tuple[str, Provider], ExternalCredential]
    graphs: defaultdict[UUID, dict[UUID, EntityRevision[Graph]]]
    nodes: defaultdict[UUID, dict[UUID, EntityRevision[Node[UUID]]]]
    pattern_sets: dict[PatternSetID, TextPatternSet]
    users: dict[str, User]

    def __init__(  # noqa: PLR0913
        self,
        *,
        edges: defaultdict[UUID, dict[UUID, EntityRevision[Edge[UUID, UUID, UUID]]]]
        | None = None,
        entity_records: list[EntityRecord] | None = None,
        external_credentials: dict[tuple[str, Provider], ExternalCredential]
        | None = None,
        graphs: defaultdict[UUID, dict[UUID, EntityRevision[Graph]]] | None = None,
        nodes: defaultdict[UUID, dict[UUID, EntityRevision[Node[UUID]]]] | None = None,
        pattern_sets: dict[PatternSetID, TextPatternSet] | None = None,
        users: dict[str, User] | None = None,
    ) -> None:
        object.__setattr__(
            self, "edges", edges if edges is not None else defaultdict(dict)
        )
        object.__setattr__(
            self, "entity_records", entity_records if entity_records is not None else []
        )
        object.__setattr__(
            self,
            "external_credentials",
            external_credentials if external_credentials is not None else {},
        )
        object.__setattr__(
            self, "graphs", graphs if graphs is not None else defaultdict(dict)
        )
        object.__setattr__(
            self, "nodes", nodes if nodes is not None else defaultdict(dict)
        )
        object.__setattr__(
            self, "pattern_sets", pattern_sets if pattern_sets is not None else {}
        )
        object.__setattr__(self, "users", users if users is not None else {})

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError


class MemStorageSnapshot(MemStorage):
    _mem_storage: MemStorage

    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        object.__setattr__(self, "_mem_storage", mem_storage)

        super().__init__(
            edges=self.deepcopy_entity_storage(mem_storage.edges),
            entity_records=copy(mem_storage.entity_records),
            external_credentials=copy(mem_storage.external_credentials),
            graphs=self.deepcopy_entity_storage(mem_storage.graphs),
            nodes=self.deepcopy_entity_storage(mem_storage.nodes),
            pattern_sets=copy(mem_storage.pattern_sets),
            users=copy(mem_storage.users),
        )

    @staticmethod
    def deepcopy_entity_storage[Entity_: Entity[UUID]](
        entity_storage: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]], /
    ) -> defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]]:
        return defaultdict(
            dict,
            {
                entity_id: copy(entity_revisions)
                for entity_id, entity_revisions in entity_storage.items()
            },
        )

    def clear_snapshot(self) -> None:
        self.edges.clear()
        self.entity_records.clear()
        self.external_credentials.clear()
        self.graphs.clear()
        self.nodes.clear()
        self.pattern_sets.clear()
        self.users.clear()

    @staticmethod
    def _merge_entity_storage[Entity_: Entity[UUID]](
        *,
        into: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]],
        from_: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]],
    ) -> None:
        for entity_id, revisions in from_.items():
            into[entity_id].update(revisions)

    def commit_to_storage(self) -> None:
        self._merge_entity_storage(into=self._mem_storage.edges, from_=self.edges)
        self._mem_storage.entity_records.clear()
        self._mem_storage.entity_records.extend(self.entity_records)
        self._mem_storage.external_credentials.update(self.external_credentials)
        self._merge_entity_storage(into=self._mem_storage.graphs, from_=self.graphs)
        self._merge_entity_storage(into=self._mem_storage.nodes, from_=self.nodes)
        self._mem_storage.pattern_sets.update(self.pattern_sets)
        self._mem_storage.users.update(self.users)
