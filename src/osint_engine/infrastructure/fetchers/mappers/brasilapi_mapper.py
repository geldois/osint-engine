from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.edges.company_has_member import CompanyHasMember
from osint_engine.domain.entities.edges.company_has_phone import CompanyHasPhone
from osint_engine.domain.entities.edges.company_located_at import CompanyLocatedAt
from osint_engine.domain.entities.edges.person_owns_company import PersonOwnsCompany
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone

if TYPE_CHECKING:
    from osint_engine.infrastructure.fetchers.schemas.fetcher_schema import Schema

_PARTNER_IS_PERSON = 1


class BrasilAPICNPJMapper:
    @staticmethod
    def _is_person(*, partner: dict[str, object]) -> bool:
        return partner.get("identificador_de_socio") == _PARTNER_IS_PERSON

    @staticmethod
    def map(*, schema: Schema) -> Graph:

        # NODES


        address = Address(
            cep=schema.require(key="cep", exp_type=str),
            number=schema.require(key="numero", exp_type=str),
        )
        cnaes = {Cnae(code=str(schema.require(key="cnae_fiscal", exp_type=int)))} | {
            Cnae(code=str(schema.require(key="codigo", exp_type=int, ext_data=cnae)))
            for cnae in schema.require(
                key="cnaes_secundarios", exp_type=list[dict[str, object]]
            )
            if cnae
        }
        company = Company(
            activity_start_date=schema.require(
                key="data_inicio_atividade", exp_type=str
            ),
            cnpj=schema.require(key="cnpj", exp_type=str),
            is_headquarters=schema.require(
                key="identificador_matriz_filial", exp_type=int
            )
            == 1,
            legal_name=schema.require(key="razao_social", exp_type=str),
            legal_nature=schema.require(key="natureza_juridica", exp_type=str),
            registration_status=schema.require(
                key="descricao_situacao_cadastral", exp_type=str
            ),
            share_capital=schema.require(key="capital_social", exp_type=int),
            size_category=schema.require(key="porte", exp_type=str),
            trade_name=schema.require(key="nome_fantasia", exp_type=str),
        )
        email = (
            Email(address=schema.require(key="email", exp_type=str))
            if schema.optional(key="email", exp_type=str) is not None
            else None
        )
        persons = {
            Person(
                cpf=schema.require(
                    key="cnpj_cpf_do_socio", exp_type=str, ext_data=person
                ),
                name=schema.require(key="nome_socio", exp_type=str, ext_data=person),
            )
            for person in schema.require(key="qsa", exp_type=list[dict[str, object]])
            if person and BrasilAPICNPJMapper._is_person(partner=person)
        }
        phones = {
            Phone(number=number)
            for number in (
                schema.optional(key="ddd_telefone_1", exp_type=str),
                schema.optional(key="ddd_telefone_2", exp_type=str),
            )
            if number
        }

        nodes = {address, company} | cnaes | persons | phones

        if email is not None:
            nodes |= {email}


        # EDGES


        company_has_cnaes = {
            CompanyHasCnae(source_id=company.id, target_id=cnae.id) for cnae in cnaes
        }
        company_has_email = (
            CompanyHasEmail(source_id=company.id, target_id=email.id)
            if email is not None
            else None
        )
        company_has_members = {
            CompanyHasMember(source_id=company.id, target_id=person.id)
            for person in persons
        }
        company_has_phones = {
            CompanyHasPhone(source_id=company.id, target_id=phone.id)
            for phone in phones
        }
        company_located_at = CompanyLocatedAt(
            source_id=company.id, target_id=address.id
        )
        person_owns_companies = {
            PersonOwnsCompany(source_id=person.id, target_id=company.id)
            for person in persons
        }

        edges = (
            company_has_cnaes
            | company_has_members
            | company_has_phones
            | {company_located_at}
            | person_owns_companies
        )

        if company_has_email is not None:
            edges |= {company_has_email}


        # GRAPH


        return Graph(
            edges=frozenset(edges),
            nodes=frozenset(nodes),
            root_id=company.id,
        )
