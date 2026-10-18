from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from tests.fakes.fetchers import (
    FakeCEAFFetcher,
    FakeCEISFetcher,
    FakeCEPIMFetcher,
    FakeCNEPFetcher,
    FakeCNPJFetcher,
    FakeCPFFetcher,
    FakeLegalProcessFetcher,
    FakePEPFetcher,
)

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.graphs import CompositeGraph
    from tests.fixtures.application import MakeEntityRevision
    from tests.fixtures.domain import MakeGraph

type MakeFakeCEAFFetcher = Callable[..., FakeCEAFFetcher]
type MakeFakeCEISFetcher = Callable[..., FakeCEISFetcher]
type MakeFakeCEPIMFetcher = Callable[..., FakeCEPIMFetcher]
type MakeFakeCNEPFetcher = Callable[..., FakeCNEPFetcher]
type MakeFakeCNPJFetcher = Callable[..., FakeCNPJFetcher]
type MakeFakeCPFFetcher = Callable[..., FakeCPFFetcher]
type MakeFakeLegalProcessFetcher = Callable[..., FakeLegalProcessFetcher]
type MakeFakePEPFetcher = Callable[..., FakePEPFetcher]


@pytest.fixture
def make_fake_cnpj_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNPJFetcher:

    def fake_cnpj_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCNPJFetcher:
        return FakeCNPJFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cnpj_fetcher


@pytest.fixture
def make_fake_cpf_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCPFFetcher:

    def fake_cpf_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCPFFetcher:
        return FakeCPFFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cpf_fetcher


@pytest.fixture
def make_fake_ceis_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCEISFetcher:

    def fake_ceis_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCEISFetcher:
        return FakeCEISFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_ceis_fetcher


@pytest.fixture
def make_fake_cnep_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCNEPFetcher:

    def fake_cnep_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCNEPFetcher:
        return FakeCNEPFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cnep_fetcher


@pytest.fixture
def make_fake_cepim_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCEPIMFetcher:

    def fake_cepim_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCEPIMFetcher:
        return FakeCEPIMFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_cepim_fetcher


@pytest.fixture
def make_fake_ceaf_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeCEAFFetcher:

    def fake_ceaf_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeCEAFFetcher:
        return FakeCEAFFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_ceaf_fetcher


@pytest.fixture
def make_fake_pep_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakePEPFetcher:

    def fake_pep_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakePEPFetcher:
        return FakePEPFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_pep_fetcher


@pytest.fixture
def make_fake_legal_process_fetcher(
    make_entity_revision: MakeEntityRevision, make_graph: MakeGraph
) -> MakeFakeLegalProcessFetcher:

    def fake_legal_process_fetcher(
        *, revision: EntityRevision[CompositeGraph] | None = None
    ) -> FakeLegalProcessFetcher:
        return FakeLegalProcessFetcher(
            revision=revision
            if revision is not None
            else make_entity_revision(entity=make_graph())
        )

    return fake_legal_process_fetcher
