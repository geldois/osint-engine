from __future__ import annotations

from decimal import Decimal

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.edge_schema import CompanyHasCnaeSchema
from osint_engine.interface.http.schemas.node_schema import CnaeSchema, CompanySchema


class TestGraphPresenterMapping:
    def test_graph_is_fully_mapped_to_schema(self) -> None:
        company = Company(
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
        cnae = Cnae(code="0101-3/01", description="Cultivo de arroz")
        edge = CompanyHasCnae(source_id=company.id, target_id=cnae.id)
        graph = Graph(
            nodes=frozenset({company, cnae}),
            edges=frozenset({edge}),
            root_id=company.id,
        )

        schema = graph_to_schema(graph)

        assert schema.root_id == company.id
        assert len(schema.nodes) == 2
        assert len(schema.edges) == 1
        assert any(isinstance(n, CompanySchema) for n in schema.nodes)
        assert any(isinstance(n, CnaeSchema) for n in schema.nodes)
        assert isinstance(schema.edges[0], CompanyHasCnaeSchema)
