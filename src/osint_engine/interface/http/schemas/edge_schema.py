from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import isabstract
from typing import Annotated, ClassVar, Literal, get_origin, override
from uuid import UUID

from pydantic import BaseModel, Field

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.edges.company_has_cnae import CompanyHasCnae
from osint_engine.domain.entities.edges.company_has_email import CompanyHasEmail
from osint_engine.domain.entities.edges.company_has_member import CompanyHasMember
from osint_engine.domain.entities.edges.company_has_phone import CompanyHasPhone
from osint_engine.domain.entities.edges.company_located_at import CompanyLocatedAt
from osint_engine.domain.entities.edges.company_received_sanction import (
    CompanyReceivedSanction,
)
from osint_engine.domain.entities.edges.person_has_email import PersonHasEmail
from osint_engine.domain.entities.edges.person_has_phone import PersonHasPhone
from osint_engine.domain.entities.edges.person_owns_company import PersonOwnsCompany
from osint_engine.domain.entities.edges.person_received_sanction import (
    PersonReceivedSanction,
)
from osint_engine.domain.entities.edges.person_reside_at import PersonResideAt
from osint_engine.interface.http.errors.schema_error import (
    DuplicateSchemaRegistrationError,
    MissingDiscriminatorFieldError,
    UnmappedTypeSchemaError,
)

# SCHEMAS


class EdgeSchema[EdgeType_co: Edge[UUID, UUID, UUID]](ABC, BaseModel):
    id: UUID
    source_id: UUID
    target_id: UUID

    @classmethod
    @override
    def __pydantic_init_subclass__(cls, **kwargs: object) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        if isabstract(cls):
            return

        type_ = cls.model_fields.get("type")

        if type_ is None or get_origin(type_.annotation) is not Literal:
            raise MissingDiscriminatorFieldError(subject=cls)

    @classmethod
    @abstractmethod
    def domain(cls) -> type[EdgeType_co]: ...


class CompanyHasCnaeSchema(EdgeSchema[CompanyHasCnae]):
    type: Literal["company_has_cnae"] = "company_has_cnae"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasCnae]:
        return CompanyHasCnae


class CompanyHasEmailSchema(EdgeSchema[CompanyHasEmail]):
    type: Literal["company_has_email"] = "company_has_email"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasEmail]:
        return CompanyHasEmail


class CompanyHasMemberSchema(EdgeSchema[CompanyHasMember]):
    type: Literal["company_has_member"] = "company_has_member"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasMember]:
        return CompanyHasMember


class CompanyHasPhoneSchema(EdgeSchema[CompanyHasPhone]):
    type: Literal["company_has_phone"] = "company_has_phone"

    @classmethod
    @override
    def domain(cls) -> type[CompanyHasPhone]:
        return CompanyHasPhone


class CompanyLocatedAtSchema(EdgeSchema[CompanyLocatedAt]):
    type: Literal["company_located_at"] = "company_located_at"

    @classmethod
    @override
    def domain(cls) -> type[CompanyLocatedAt]:
        return CompanyLocatedAt


class CompanyReceivedSanctionSchema(EdgeSchema[CompanyReceivedSanction]):
    type: Literal["company_received_sanction"] = "company_received_sanction"

    @classmethod
    @override
    def domain(cls) -> type[CompanyReceivedSanction]:
        return CompanyReceivedSanction


class PersonHasEmailSchema(EdgeSchema[PersonHasEmail]):
    type: Literal["person_has_email"] = "person_has_email"

    @classmethod
    @override
    def domain(cls) -> type[PersonHasEmail]:
        return PersonHasEmail


class PersonHasPhoneSchema(EdgeSchema[PersonHasPhone]):
    type: Literal["person_has_phone"] = "person_has_phone"

    @classmethod
    @override
    def domain(cls) -> type[PersonHasPhone]:
        return PersonHasPhone


class PersonOwnsCompanySchema(EdgeSchema[PersonOwnsCompany]):
    type: Literal["person_owns_company"] = "person_owns_company"

    entry_date: str
    role: str

    @classmethod
    @override
    def domain(cls) -> type[PersonOwnsCompany]:
        return PersonOwnsCompany


class PersonReceivedSanctionSchema(EdgeSchema[PersonReceivedSanction]):
    type: Literal["person_received_sanction"] = "person_received_sanction"

    @classmethod
    @override
    def domain(cls) -> type[PersonReceivedSanction]:
        return PersonReceivedSanction


class PersonResideAtSchema(EdgeSchema[PersonResideAt]):
    type: Literal["person_reside_at"] = "person_reside_at"

    @classmethod
    @override
    def domain(cls) -> type[PersonResideAt]:
        return PersonResideAt


# UNION


EdgeSchemaUnion = (
    CompanyHasCnaeSchema
    | CompanyHasEmailSchema
    | CompanyHasMemberSchema
    | CompanyHasPhoneSchema
    | CompanyLocatedAtSchema
    | CompanyReceivedSanctionSchema
    | PersonHasEmailSchema
    | PersonHasPhoneSchema
    | PersonOwnsCompanySchema
    | PersonReceivedSanctionSchema
    | PersonResideAtSchema
)

EdgeUnion = Annotated[EdgeSchemaUnion, Field(discriminator="type")]


# REGISTRIES


class EdgeSchemaRegistry:
    _REGISTRY: ClassVar[
        dict[type[Edge[UUID, UUID, UUID]], type[EdgeSchema[Edge[UUID, UUID, UUID]]]]
    ] = {}

    @classmethod
    def get_from_domain(
        cls, domain: type[Edge[UUID, UUID, UUID]], /
    ) -> type[EdgeSchema[Edge[UUID, UUID, UUID]]]:
        if domain not in cls._REGISTRY:
            raise UnmappedTypeSchemaError(subject=domain)

        return cls._REGISTRY[domain]

    @classmethod
    def register(cls, schema: type[EdgeSchema[Edge[UUID, UUID, UUID]]], /) -> None:
        key = schema.domain()

        if key in cls._REGISTRY:
            raise DuplicateSchemaRegistrationError(
                subject=key, existing_schema=cls._REGISTRY[key]
            )

        cls._REGISTRY[key] = schema


EdgeSchemaRegistry.register(CompanyHasCnaeSchema)
EdgeSchemaRegistry.register(CompanyHasEmailSchema)
EdgeSchemaRegistry.register(CompanyHasMemberSchema)
EdgeSchemaRegistry.register(CompanyHasPhoneSchema)
EdgeSchemaRegistry.register(CompanyLocatedAtSchema)
EdgeSchemaRegistry.register(CompanyReceivedSanctionSchema)
EdgeSchemaRegistry.register(PersonHasEmailSchema)
EdgeSchemaRegistry.register(PersonHasPhoneSchema)
EdgeSchemaRegistry.register(PersonOwnsCompanySchema)
EdgeSchemaRegistry.register(PersonReceivedSanctionSchema)
EdgeSchemaRegistry.register(PersonResideAtSchema)
