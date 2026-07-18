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
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.domain.entities.bases.node import Node


class MemStorage:
    edges: defaultdict[UUID, dict[UUID, EntityRevision[Edge[UUID, UUID, UUID]]]]
    external_credentials: dict[tuple[str, Provider], ExternalCredential]
    graphs: defaultdict[UUID, dict[UUID, EntityRevision[Graph]]]
    nodes: defaultdict[UUID, dict[UUID, EntityRevision[Node[UUID]]]]
    users: dict[str, User]

    def __init__(
        self,
        *,
        edges: defaultdict[UUID, dict[UUID, EntityRevision[Edge[UUID, UUID, UUID]]]]
        | None = None,
        external_credentials: dict[tuple[str, Provider], ExternalCredential]
        | None = None,
        graphs: defaultdict[UUID, dict[UUID, EntityRevision[Graph]]] | None = None,
        nodes: defaultdict[UUID, dict[UUID, EntityRevision[Node[UUID]]]] | None = None,
        users: dict[str, User] | None = None,
    ) -> None:
        object.__setattr__(
            self, "edges", edges if edges is not None else defaultdict(dict)
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
        object.__setattr__(self, "users", users if users is not None else {})

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError


class MemStorageSnapshot(MemStorage):
    """
    Temporary working storage for a UoW transaction.
    Inherits MemStorage contracts (frozen, typed dicts).
    Changes are committed to the original storage on commit,
    or discarded on rollback.
    """

    _mem_storage: MemStorage

    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        object.__setattr__(self, "_mem_storage", mem_storage)

        super().__init__(
            edges=self.deepcopy_entity_storage(mem_storage.edges),
            external_credentials=copy(mem_storage.external_credentials),
            graphs=self.deepcopy_entity_storage(mem_storage.graphs),
            nodes=self.deepcopy_entity_storage(mem_storage.nodes),
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
        self.external_credentials.clear()
        self.graphs.clear()
        self.nodes.clear()
        self.users.clear()

    def commit_to_storage(self) -> None:
        self._mem_storage.edges.clear()
        self._mem_storage.edges.update(self.edges)

        self._mem_storage.external_credentials.clear()
        self._mem_storage.external_credentials.update(self.external_credentials)

        self._mem_storage.graphs.clear()
        self._mem_storage.graphs.update(self.graphs)

        self._mem_storage.nodes.clear()
        self._mem_storage.nodes.update(self.nodes)

        self._mem_storage.users.clear()
        self._mem_storage.users.update(self.users)
