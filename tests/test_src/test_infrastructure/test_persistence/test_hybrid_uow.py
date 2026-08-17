from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from osint_engine.infrastructure.errors.uow_error import (
    UoWAlreadyPreparedError,
    UoWNotPreparedError,
)
from osint_engine.infrastructure.persistence.hybrid_uow import HybridUoW
from osint_engine.infrastructure.persistence.pg.repositories.pg_external_credential_repository import (  # noqa: E501
    PgExternalCredentialRepository,
)

if TYPE_CHECKING:
    from asyncpg import Pool

    from osint_engine.config.container import Policies
    from osint_engine.config.settings import Settings
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
    from tests.conftest import (
        MakeEntityRevision,
        MakeExternalCredential,
        MakeFakeEdge,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
        MakeUser,
    )
    from tests.fakes.persistence import FakePgPool

_LIFECYCLE_ATTRIBUTES = (
    "edges",
    "external_credentials",
    "graphs",
    "nodes",
    "pattern_sets",
    "users",
)


def _make_hybrid_uow(
    *,
    mem_storage: MemStorage,
    fake_pg_pool: FakePgPool,
    settings: Settings,
    policies: Policies,
) -> HybridUoW:
    return HybridUoW(
        mem_storage=mem_storage,
        pg_pool=cast("Pool", fake_pg_pool),
        encryption_key=settings.external_credential_encryption_key,
        revision_merge_policy=policies.revision_merge_policy,
        revision_selection_policy=policies.revision_selection_policy,
    )


class TestHybridUoWContextLifecycle:
    @pytest.mark.asyncio
    async def test_repositories_exist_only_inside_context(
        self,
        make_mem_storage: MakeMemStorage,
        fake_pg_pool: FakePgPool,
        settings: Settings,
        policies: Policies,
    ) -> None:
        uow = _make_hybrid_uow(
            mem_storage=make_mem_storage(),
            fake_pg_pool=fake_pg_pool,
            settings=settings,
            policies=policies,
        )

        for attribute in _LIFECYCLE_ATTRIBUTES:
            assert not hasattr(uow, attribute)

        async with uow:
            for attribute in _LIFECYCLE_ATTRIBUTES:
                assert hasattr(uow, attribute)

        for attribute in _LIFECYCLE_ATTRIBUTES:
            assert not hasattr(uow, attribute)


class TestHybridUoWMemoryRepositories:
    @pytest.mark.asyncio
    async def test_commits_edges_graphs_nodes_and_users_to_memory(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        fake_pg_pool: FakePgPool,
        settings: Settings,
        policies: Policies,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = make_mem_storage()
        uow = _make_hybrid_uow(
            mem_storage=mem_storage,
            fake_pg_pool=fake_pg_pool,
            settings=settings,
            policies=policies,
        )

        async with uow:
            await uow.edges.merge(revision=make_entity_revision(entity=edge))
            await uow.graphs.merge(revision=make_entity_revision(entity=graph))
            await uow.nodes.merge(revision=make_entity_revision(entity=node_a))
            await uow.nodes.merge(revision=make_entity_revision(entity=node_b))
            await uow.users.save(user=user)

        assert edge.id in mem_storage.edges
        assert graph.id in mem_storage.graphs
        assert node_a.id in mem_storage.nodes
        assert node_b.id in mem_storage.nodes
        assert user.username in mem_storage.users

    @pytest.mark.asyncio
    async def test_rolls_back_all_memory_repositories_on_error(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        fake_pg_pool: FakePgPool,
        settings: Settings,
        policies: Policies,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = make_mem_storage()
        uow = _make_hybrid_uow(
            mem_storage=mem_storage,
            fake_pg_pool=fake_pg_pool,
            settings=settings,
            policies=policies,
        )

        async def run_transaction_with_error() -> None:
            async with uow:
                await uow.edges.merge(revision=make_entity_revision(entity=edge))
                await uow.graphs.merge(revision=make_entity_revision(entity=graph))
                await uow.nodes.merge(revision=make_entity_revision(entity=node_a))
                await uow.nodes.merge(revision=make_entity_revision(entity=node_b))
                await uow.users.save(user=user)

                raise RuntimeError

        with pytest.raises(RuntimeError):
            await run_transaction_with_error()

        assert edge.id not in mem_storage.edges
        assert graph.id not in mem_storage.graphs
        assert node_a.id not in mem_storage.nodes
        assert node_b.id not in mem_storage.nodes
        assert user.username not in mem_storage.users


class TestHybridUoWPostgresRepository:
    @pytest.mark.asyncio
    async def test_external_credentials_delegate_to_pg_repository(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        fake_pg_pool: FakePgPool,
        settings: Settings,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(api_key="plain-api-key")
        uow = _make_hybrid_uow(
            mem_storage=make_mem_storage(),
            fake_pg_pool=fake_pg_pool,
            settings=settings,
            policies=policies,
        )

        async with uow:
            assert isinstance(uow.external_credentials, PgExternalCredentialRepository)
            await uow.external_credentials.save(credential=credential)
            found = await uow.external_credentials.find(
                username=credential.username,
                provider=credential.provider,
            )

        stored = fake_pg_pool.external_credentials[
            (credential.username, credential.provider.value)
        ]

        assert found == credential
        assert stored != credential.api_key


class TestHybridUoWValidation:
    @pytest.mark.asyncio
    async def test_rejects_duplicate_prepare_and_unmatched_finish(
        self,
        make_mem_storage: MakeMemStorage,
        fake_pg_pool: FakePgPool,
        settings: Settings,
        policies: Policies,
    ) -> None:
        uow = _make_hybrid_uow(
            mem_storage=make_mem_storage(),
            fake_pg_pool=fake_pg_pool,
            settings=settings,
            policies=policies,
        )

        with pytest.raises(UoWAlreadyPreparedError):
            async with uow:
                await uow._prepare()  # pyright: ignore[reportPrivateUsage]

        with pytest.raises(UoWNotPreparedError):
            async with uow:
                await uow._finish()  # pyright: ignore[reportPrivateUsage]
