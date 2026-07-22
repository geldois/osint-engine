from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.edges.company_has_member import CompanyHasMember
from osint_engine.domain.entities.edges.company_has_phone import CompanyHasPhone
from osint_engine.domain.entities.edges.company_located_at import CompanyLocatedAt
from osint_engine.domain.entities.edges.company_owns_company import CompanyOwnsCompany
from osint_engine.domain.entities.edges.person_owns_company import PersonOwnsCompany
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company, CompanyID
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload


_PARTNER_IS_LEGAL_ENTITY = 1
_PARTNER_IS_PERSON = 2


def _is_person(*, partner: dict[str, object]) -> bool:
    return partner.get("identificador_de_socio") == _PARTNER_IS_PERSON


def _is_legal_entity(*, partner: dict[str, object]) -> bool:
    return partner.get("identificador_de_socio") == _PARTNER_IS_LEGAL_ENTITY


def _map_address(*, payload: Payload) -> Address | None:
    cep = payload.optional(key="cep", expected_type=str)
    numero = payload.optional(key="numero", expected_type=str)

    if not cep or not numero:
        return None

    return Address(
        cep=cep,
        city=payload.require(key="municipio", expected_type=str),
        complement=payload.require(key="complemento", expected_type=str),
        neighborhood=payload.require(key="bairro", expected_type=str),
        number=numero,
        state=payload.require(key="uf", expected_type=str),
        street=payload.require(key="logradouro", expected_type=str),
    )


def _map_secondary_cnae(*, payload: Payload) -> Cnae:
    return Cnae(
        code=str(payload.require(key="codigo", expected_type=int)),
        description=payload.require(key="descricao", expected_type=str),
    )


def _map_cnaes(*, payload: Payload) -> set[Cnae]:
    return {
        Cnae(
            code=str(payload.require(key="cnae_fiscal", expected_type=int)),
            description=payload.require(key="cnae_fiscal_descricao", expected_type=str),
        )
    } | {
        _map_secondary_cnae(payload=payload.scope(data=cnae))
        for cnae in payload.require(
            key="cnaes_secundarios", expected_type=list[dict[str, object]]
        )
        if cnae
    }


def _map_company(*, payload: Payload) -> Company:
    return Company(
        activity_start_date=payload.require(
            key="data_inicio_atividade", expected_type=str
        ),
        cnpj=payload.require(key="cnpj", expected_type=str),
        is_headquarters=payload.require(
            key="identificador_matriz_filial", expected_type=int
        )
        == 1,
        legal_name=payload.require(key="razao_social", expected_type=str),
        legal_nature=payload.require(key="natureza_juridica", expected_type=str),
        registration_status=payload.require(
            key="descricao_situacao_cadastral", expected_type=str
        ),
        registration_status_date=payload.require(
            key="data_situacao_cadastral", expected_type=str
        ),
        registration_status_reason=payload.require(
            key="descricao_motivo_situacao_cadastral", expected_type=str
        ),
        share_capital=payload.require(
            key="capital_social",
            expected_type=int | float,
            cast_to=lambda value: Decimal(str(value)),
        ),
        size_category=payload.require(key="porte", expected_type=str),
        trade_name=payload.require(key="nome_fantasia", expected_type=str),
    )


def _map_email(*, payload: Payload) -> Email | None:
    email = payload.optional(key="email", expected_type=str)

    if email is None:
        return None

    return Email(address=email)


def _map_phones(*, payload: Payload) -> set[Phone]:
    return {
        Phone(number=number)
        for number in (
            payload.optional(key="ddd_telefone_1", expected_type=str),
            payload.optional(key="ddd_telefone_2", expected_type=str),
        )
        if number
    }


def _map_person(*, payload: Payload) -> Person:
    return Person(
        age_range=payload.require(key="faixa_etaria", expected_type=str),
        cpf=payload.require(key="cnpj_cpf_do_socio", expected_type=str),
        name=payload.require(key="nome_socio", expected_type=str),
    )


def _map_persons_and_ownerships(
    *, payload: Payload, company_id: CompanyID
) -> tuple[set[Person], set[PersonOwnsCompany]]:
    persons: set[Person] = set()
    ownerships: set[PersonOwnsCompany] = set()

    for partner in payload.require(key="qsa", expected_type=list[dict[str, object]]):
        if not partner or not _is_person(partner=partner):
            continue

        partner_payload = payload.scope(data=partner)
        person = _map_person(payload=partner_payload)

        persons.add(person)

        ownerships.add(
            PersonOwnsCompany(
                entry_date=partner_payload.require(
                    key="data_entrada_sociedade", expected_type=str
                ),
                role=partner_payload.require(
                    key="qualificacao_socio", expected_type=str
                ),
                source_id=person.id,
                target_id=company_id,
            )
        )

    return persons, ownerships


def _map_company_stub(*, payload: Payload) -> Company:
    return Company(
        activity_start_date=None,
        cnpj=payload.require(key="cnpj_cpf_do_socio", expected_type=str),
        is_headquarters=None,
        legal_name=payload.require(key="nome_socio", expected_type=str),
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
    )


def _map_company_partners_and_ownerships(
    *, payload: Payload, company_id: CompanyID
) -> tuple[set[Company], set[CompanyOwnsCompany]]:
    companies: set[Company] = set()
    ownerships: set[CompanyOwnsCompany] = set()

    for partner in payload.require(key="qsa", expected_type=list[dict[str, object]]):
        if not partner or not _is_legal_entity(partner=partner):
            continue

        partner_payload = payload.scope(data=partner)
        partner_company = _map_company_stub(payload=partner_payload)

        companies.add(partner_company)

        ownerships.add(
            CompanyOwnsCompany(
                entry_date=partner_payload.require(
                    key="data_entrada_sociedade", expected_type=str
                ),
                role=partner_payload.require(
                    key="qualificacao_socio", expected_type=str
                ),
                source_id=partner_company.id,
                target_id=company_id,
            )
        )

    return companies, ownerships


def map_graph(*, payload: Payload) -> Graph:
    address = _map_address(payload=payload)
    cnaes = _map_cnaes(payload=payload)
    company = _map_company(payload=payload)
    email = _map_email(payload=payload)
    phones = _map_phones(payload=payload)
    persons, person_owns_companies = _map_persons_and_ownerships(
        payload=payload, company_id=company.id
    )
    owning_companies, company_owns_companies = _map_company_partners_and_ownerships(
        payload=payload, company_id=company.id
    )

    nodes = {company} | cnaes | persons | phones | owning_companies

    if address is not None:
        nodes |= {address}

    if email is not None:
        nodes |= {email}

    edges = (
        {CompanyHasCnae(source_id=company.id, target_id=cnae.id) for cnae in cnaes}
        | {
            CompanyHasMember(source_id=company.id, target_id=person.id)
            for person in persons
        }
        | {
            CompanyHasPhone(source_id=company.id, target_id=phone.id)
            for phone in phones
        }
        | person_owns_companies
        | company_owns_companies
    )

    if address is not None:
        edges |= {CompanyLocatedAt(source_id=company.id, target_id=address.id)}

    if email is not None:
        edges |= {CompanyHasEmail(source_id=company.id, target_id=email.id)}

    return Graph(edges=frozenset(edges), nodes=frozenset(nodes), root_id=company.id)
