from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest
import pytest_asyncio
from httpx2 import AsyncClient

from osint_engine.application.revision.policies.revision_merge_policy import (
    merge_by_filled_fields_policy,
)
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.config.container import Policies
from osint_engine.config.croot import build_container
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW

if TYPE_CHECKING:
    from collections.abc import Iterable

    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.config.settings import Settings
    from tests.conftest import MakeMemStorage, MakeUser

_NOOP_MERGE_POLICY_CALLED_MESSAGE = "_noop_merge_policy should not be called"
_NOOP_SELECTION_POLICY_CALLED_MESSAGE = "_noop_selection_policy should not be called"


# TEST DOUBLES


def _noop_merge_policy[Entity_: Entity[UUID]](
    _left: EntityRevision[Entity_], _right: EntityRevision[Entity_], /
) -> EntityRevision[Entity_]:
    """A distinct merge-policy identity marker; never invoked by these tests."""

    raise AssertionError(_NOOP_MERGE_POLICY_CALLED_MESSAGE)


def _noop_selection_policy[Entity_: Entity[UUID]](
    _entity_revisions: Iterable[EntityRevision[Entity_]], /
) -> EntityRevision[Entity_]:
    """A distinct selection-policy identity marker; never invoked by these tests."""

    raise AssertionError(_NOOP_SELECTION_POLICY_CALLED_MESSAGE)


@pytest_asyncio.fixture
async def http_client() -> AsyncClient:
    """A bare HTTP client; build_container never issues requests through it."""

    return AsyncClient()


# TESTS


class TestBuildContainerMemStorage:
    @pytest.mark.asyncio
    async def test_reuses_the_provided_mem_storage(
        self,
        settings: Settings,
        http_client: AsyncClient,
        make_mem_storage: MakeMemStorage,
        make_user: MakeUser,
        policies: Policies,
    ) -> None:
        user = make_user(username="seeded_user")
        mem_storage = make_mem_storage(users=[user])

        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=mem_storage,
            policies=policies,
        )

        async with container.uow_factory() as uow:
            found = await uow.users.find(username="seeded_user")

        assert found is user, (
            "build_container must reuse the caller-provided mem_storage "
            "instead of discarding it for a fresh one"
        )

    @pytest.mark.asyncio
    async def test_builds_a_fresh_mem_storage_when_none_is_provided(
        self,
        settings: Settings,
        http_client: AsyncClient,
        policies: Policies,
    ) -> None:
        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=None,
            policies=policies,
        )

        async with container.uow_factory() as uow:
            found = await uow.users.find(username="admin")

        assert found is not None, (
            "build_container must seed a fresh mem_storage when none is given, "
            "which populates the admin user"
        )


class TestBuildContainerPolicies:
    @pytest.mark.asyncio
    async def test_defaults_to_the_canonical_revision_policies_when_none_given(
        self,
        settings: Settings,
        http_client: AsyncClient,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=make_mem_storage(),
            policies=None,
        )

        uow = container.uow_factory()

        assert isinstance(uow, MemUoW)

        async with uow:
            assert uow.revision_merge_policy is merge_by_filled_fields_policy
            assert uow.revision_selection_policy is select_current_by_newest_fetched

    @pytest.mark.asyncio
    async def test_threads_the_provided_policies_into_the_uow_factory(
        self,
        settings: Settings,
        http_client: AsyncClient,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        custom_policies = Policies(
            revision_merge_policy=_noop_merge_policy,
            revision_selection_policy=_noop_selection_policy,
        )

        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=make_mem_storage(),
            policies=custom_policies,
        )

        assert container.policies is custom_policies

        uow = container.uow_factory()

        assert isinstance(uow, MemUoW)

        async with uow:
            assert uow.revision_merge_policy is _noop_merge_policy
            assert uow.revision_selection_policy is _noop_selection_policy


class TestBuildContainerWiring:
    @pytest.mark.asyncio
    async def test_wires_the_cnpj_fetcher_into_the_container(
        self,
        settings: Settings,
        http_client: AsyncClient,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=make_mem_storage(),
            policies=policies,
        )

        assert container.fetchers.cnpj_fetcher is not None

    @pytest.mark.asyncio
    async def test_uow_factory_produces_independent_working_uows(
        self,
        settings: Settings,
        http_client: AsyncClient,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        container = build_container(
            settings=settings,
            http_client=http_client,
            mem_storage=make_mem_storage(),
            policies=policies,
        )

        first_uow = container.uow_factory()
        second_uow = container.uow_factory()

        assert first_uow is not second_uow
