from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.legal_process import LegalProcess
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone
from osint_engine.domain.entities.nodes.political_exposure import PoliticalExposure
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.domain.entities.nodes.text_source import TextSource
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.presenters.revision_presenter import (
    revision_to_schema,
)
from osint_engine.interface.http.schemas.node_schema import (
    AddressSchema,
    CnaeSchema,
    CompanySchema,
    EmailSchema,
    LegalProcessSchema,
    NodeSchemaUnion,
    PersonSchema,
    PhoneSchema,
    PoliticalExposureSchema,
    SanctionSchema,
    TextSourceSchema,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.interface.http.schemas.revision_schema import RevisionSchema


def address_to_schema(*, node: Address, revision: RevisionSchema) -> AddressSchema:
    return AddressSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        cep=node.cep,
        city=node.city,
        complement=node.complement,
        neighborhood=node.neighborhood,
        number=node.number,
        state=node.state,
        street=node.street,
    )


def cnae_to_schema(*, node: Cnae, revision: RevisionSchema) -> CnaeSchema:
    return CnaeSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        code=node.code,
        description=node.description,
    )


def company_to_schema(*, node: Company, revision: RevisionSchema) -> CompanySchema:
    return CompanySchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
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


def email_to_schema(*, node: Email, revision: RevisionSchema) -> EmailSchema:
    return EmailSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        address=node.address,
    )


def legal_process_to_schema(
    *, node: LegalProcess, revision: RevisionSchema
) -> LegalProcessSchema:
    return LegalProcessSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        court=node.court,
        current_status=node.current_status,
        distribution_date=node.distribution_date,
        execution_value=node.execution_value,
        is_secret_of_justice=node.is_secret_of_justice,
        lawsuit_value=node.lawsuit_value,
        lawsuit_value_currency=node.lawsuit_value_currency,
        process_class=node.process_class,
        process_number=node.process_number,
        process_url=node.process_url,
        state=node.state,
    )


def person_to_schema(*, node: Person, revision: RevisionSchema) -> PersonSchema:
    return PersonSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        age_range=node.age_range,
        birthdate=node.birthdate,
        cpf=node.cpf,
        name=node.name,
        registration_date=node.registration_date,
        registration_status=node.registration_status,
    )


def phone_to_schema(*, node: Phone, revision: RevisionSchema) -> PhoneSchema:
    return PhoneSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        number=node.number,
    )


def political_exposure_to_schema(
    *, node: PoliticalExposure, revision: RevisionSchema
) -> PoliticalExposureSchema:
    return PoliticalExposureSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        cpf=node.cpf,
        exercise_end_date=node.exercise_end_date,
        exercise_start_date=node.exercise_start_date,
        function_acronym=node.function_acronym,
        function_description=node.function_description,
        function_level=node.function_level,
        government_body_code=node.government_body_code,
        government_body_name=node.government_body_name,
        grace_period_end_date=node.grace_period_end_date,
    )


def sanction_to_schema(*, node: Sanction, revision: RevisionSchema) -> SanctionSchema:
    return SanctionSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        end_date=node.end_date,
        fine_amount=node.fine_amount,
        legal_basis=node.legal_basis,
        organ=node.organ,
        process_number=node.process_number,
        publication_date=node.publication_date,
        publication_link=node.publication_link,
        sanction_type=node.sanction_type,
        sanctioning_body=node.sanctioning_body,
        source_id=node.source_id,
        start_date=node.start_date,
    )


def text_source_to_schema(
    *, node: TextSource, revision: RevisionSchema
) -> TextSourceSchema:
    return TextSourceSchema(
        content_id=node.content_id,
        id=node.id,
        revision=revision,
        text=node.text,
    )


_NODE_MAP: dict[type[Node[UUID]], Callable[..., NodeSchemaUnion]] = {
    Address: address_to_schema,
    Cnae: cnae_to_schema,
    Company: company_to_schema,
    Email: email_to_schema,
    LegalProcess: legal_process_to_schema,
    Person: person_to_schema,
    Phone: phone_to_schema,
    PoliticalExposure: political_exposure_to_schema,
    Sanction: sanction_to_schema,
    TextSource: text_source_to_schema,
}


def node_to_schema(node: Node[UUID], /, *, revision: RevisionSchema) -> NodeSchemaUnion:
    try:
        return _NODE_MAP[type(node)](node=node, revision=revision)
    except KeyError:
        raise UnmappedTypeSchemaError(subject=type(node)) from None


def node_history_to_schema(
    revisions: tuple[EntityRevision[Node[UUID]], ...], /
) -> list[NodeSchemaUnion]:
    return [
        node_to_schema(revision.entity, revision=revision_to_schema(revision))
        for revision in revisions
    ]
