from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.schemas.node_schema import (
    AddressSchema,
    CnaeSchema,
    CompanySchema,
    EmailSchema,
    NodeSchemaUnion,
    PersonSchema,
    PhoneSchema,
    SanctionSchema,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node


def address_to_schema(*, node: Address) -> AddressSchema:
    return AddressSchema(
        id=node.id,
        cep=node.cep,
        city=node.city,
        complement=node.complement,
        neighborhood=node.neighborhood,
        number=node.number,
        state=node.state,
        street=node.street,
    )


def cnae_to_schema(*, node: Cnae) -> CnaeSchema:
    return CnaeSchema(id=node.id, code=node.code, description=node.description)


def company_to_schema(*, node: Company) -> CompanySchema:
    return CompanySchema(
        id=node.id,
        activity_start_date=node.activity_start_date,
        cnpj=node.cnpj,
        is_headquarters=node.is_headquarters,
        legal_name=node.legal_name,
        legal_nature=node.legal_nature,
        registration_status=node.registration_status,
        registration_status_date=node.registration_status_date,
        registration_status_reason=node.registration_status_reason,
        share_capital=node.share_capital,
        size_category=node.size_category,
        trade_name=node.trade_name,
    )


def email_to_schema(*, node: Email) -> EmailSchema:
    return EmailSchema(id=node.id, address=node.address)


def person_to_schema(*, node: Person) -> PersonSchema:
    return PersonSchema(
        id=node.id, age_range=node.age_range, cpf=node.cpf, name=node.name
    )


def phone_to_schema(*, node: Phone) -> PhoneSchema:
    return PhoneSchema(id=node.id, number=node.number)


def sanction_to_schema(*, node: Sanction) -> SanctionSchema:
    return SanctionSchema(id=node.id, organ=node.organ)


_NODE_MAP: dict[type[Node[UUID]], Callable[..., NodeSchemaUnion]] = {
    Address: address_to_schema,
    Cnae: cnae_to_schema,
    Company: company_to_schema,
    Email: email_to_schema,
    Person: person_to_schema,
    Phone: phone_to_schema,
    Sanction: sanction_to_schema,
}


def node_to_schema(node: Node[UUID], /) -> NodeSchemaUnion:
    try:
        return _NODE_MAP[type(node)](node=node)
    except KeyError:
        raise UnmappedTypeSchemaError(subject=type(node)) from None
