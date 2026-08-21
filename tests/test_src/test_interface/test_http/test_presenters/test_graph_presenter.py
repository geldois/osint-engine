from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.interface.http.presenters.graph_presenter import (
    graph_to_schema,
    revision_to_schema,
)
from osint_engine.interface.http.schemas.edge_schema import CompanyHasCnaeSchema
from osint_engine.interface.http.schemas.node_schema import CnaeSchema, CompanySchema

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRevision

_COMPANY = Company(
    activity_start_date="2020-01-01",
    cnpj="11222333000181",
    is_headquarters=True,
    legal_name="Acme LTDA",
    legal_nature="206-2",
    registration_status="ATIVA",
    registration_status_date="2020-01-01",
    registration_status_reason="",
    share_capital=Decimal("10000.00"),
    size_category="MICRO",
    trade_name="Acme",
)
_CNAE = Cnae(code="0101-3/01", description="Cultivo de arroz")
_EDGE = CompanyHasCnae(source_id=_COMPANY.id, target_id=_CNAE.id)
_GRAPH = Graph(
    nodes=frozenset({_COMPANY, _CNAE}),
    edges=frozenset({_EDGE}),
    root_id=_COMPANY.id,
)


class TestGraphPresenterMapping:
    def test_graph_is_fully_mapped_to_schema(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH))

        assert schema.root_id == _COMPANY.id
        assert len(schema.nodes) == 2
        assert len(schema.edges) == 1
        assert any(isinstance(n, CompanySchema) for n in schema.nodes)
        assert any(isinstance(n, CnaeSchema) for n in schema.nodes)
        assert isinstance(schema.edges[0], CompanyHasCnaeSchema)


class TestGraphPresenterIdentity:
    def test_graph_carries_its_own_content_id(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH))

        assert schema.content_id == _GRAPH.content_id

    def test_every_node_and_edge_carries_its_own_content_id(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH))

        assert {node.content_id for node in schema.nodes} == {
            _COMPANY.content_id,
            _CNAE.content_id,
        }
        assert schema.edges[0].content_id == _EDGE.content_id

    def test_content_id_differs_from_id_for_an_entity_carrying_descriptive_fields(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH))
        company = next(n for n in schema.nodes if isinstance(n, CompanySchema))

        assert company.id == _COMPANY.id
        assert company.content_id != company.id


class TestGraphPresenterProvenance:
    def test_revision_is_carried_onto_the_graph(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        fetched_at = datetime(year=2026, month=3, day=4, tzinfo=UTC)
        merged_at = datetime(year=2026, month=3, day=5, tzinfo=UTC)
        revision = make_entity_revision(
            entity=_GRAPH,
            fetched_at=fetched_at,
            merged_at=merged_at,
            provider="brasilapi",
        )

        schema = graph_to_schema(revision)

        assert schema.revision.fetched_at == fetched_at
        assert schema.revision.merged_at == merged_at
        assert schema.revision.provider == "brasilapi"

    def test_unmerged_revision_reports_a_null_merge_time(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH, merged_at=None))

        assert schema.revision.merged_at is None

    def test_every_node_and_edge_repeats_the_graphs_own_revision(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(
            make_entity_revision(entity=_GRAPH, provider="brasilapi")
        )

        for node in schema.nodes:
            assert node.revision == schema.revision
        for edge in schema.edges:
            assert edge.revision == schema.revision

    def test_content_id_is_never_folded_into_the_revision(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        schema = graph_to_schema(make_entity_revision(entity=_GRAPH))

        assert set(schema.revision.model_dump()) == {
            "fetched_at",
            "merged_at",
            "provider",
        }


class TestRevisionPresenter:
    def test_revision_maps_exactly_its_three_provenance_fields(
        self, make_entity_revision: MakeEntityRevision
    ) -> None:
        fetched_at = datetime(year=2026, month=7, day=9, tzinfo=UTC)
        revision = make_entity_revision(
            entity=_GRAPH, fetched_at=fetched_at, provider="kipflow"
        )

        schema = revision_to_schema(revision)

        assert schema.fetched_at == fetched_at
        assert schema.merged_at is None
        assert schema.provider == "kipflow"
