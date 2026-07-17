from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal  # noqa: TC003
from inspect import isabstract
from typing import Annotated, ClassVar, Literal, get_origin, override
from uuid import UUID

from pydantic import BaseModel, Field

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.cnae import Cnae
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.email import Email
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.entities.nodes.phone import Phone
from osint_engine.domain.entities.nodes.sanction import Sanction
from osint_engine.interface.http.errors.schema_error import (
    DuplicateSchemaRegistrationError,
    MissingDiscriminatorFieldError,
    UnmappedTypeSchemaError,
)

# SCHEMAS


class NodeSchema[NodeType_co: Node[UUID]](ABC, BaseModel):
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
    def domain(cls) -> type[NodeType_co]: ...


class AddressSchema(NodeSchema[Address]):
    type: Literal["address"] = "address"

    cep: str
    city: str
    complement: str | None
    id: UUID
    neighborhood: str
    number: str
    state: str
    street: str

    @classmethod
    @override
    def domain(cls) -> type[Address]:
        return Address


class CnaeSchema(NodeSchema[Cnae]):
    type: Literal["cnae"] = "cnae"

    code: str
    description: str
    id: UUID

    @classmethod
    @override
    def domain(cls) -> type[Cnae]:
        return Cnae


class CompanySchema(NodeSchema[Company]):
    type: Literal["company"] = "company"

    activity_start_date: str | None
    cnpj: str
    id: UUID
    is_headquarters: bool | None
    legal_name: str | None
    legal_nature: str | None
    registration_status: str | None
    registration_status_date: str | None
    registration_status_reason: str | None
    share_capital: Decimal | None
    size_category: str | None
    trade_name: str | None

    @classmethod
    @override
    def domain(cls) -> type[Company]:
        return Company


class EmailSchema(NodeSchema[Email]):
    type: Literal["email"] = "email"

    address: str
    id: UUID

    @classmethod
    @override
    def domain(cls) -> type[Email]:
        return Email


class PersonSchema(NodeSchema[Person]):
    type: Literal["person"] = "person"

    age_range: str
    cpf: str
    id: UUID
    name: str

    @classmethod
    @override
    def domain(cls) -> type[Person]:
        return Person


class PhoneSchema(NodeSchema[Phone]):
    type: Literal["phone"] = "phone"

    id: UUID
    number: str

    @classmethod
    @override
    def domain(cls) -> type[Phone]:
        return Phone


class SanctionSchema(NodeSchema[Sanction]):
    type: Literal["sanction"] = "sanction"

    id: UUID
    organ: Literal["CEIS", "CNEP"]

    @classmethod
    @override
    def domain(cls) -> type[Sanction]:
        return Sanction


# UNION


NodeSchemaUnion = (
    AddressSchema
    | CnaeSchema
    | CompanySchema
    | EmailSchema
    | PersonSchema
    | PhoneSchema
    | SanctionSchema
)

NodeUnion = Annotated[NodeSchemaUnion, Field(discriminator="type")]


# REGISTRIES


class NodeSchemaRegistry:
    _REGISTRY: ClassVar[dict[type[Node[UUID]], type[NodeSchema[Node[UUID]]]]] = {}

    @classmethod
    def get_from_domain(
        cls, domain: type[Node[UUID]], /
    ) -> type[NodeSchema[Node[UUID]]]:
        if domain not in cls._REGISTRY:
            raise UnmappedTypeSchemaError(subject=domain)

        return cls._REGISTRY[domain]

    @classmethod
    def register(cls, schema: type[NodeSchema[Node[UUID]]], /) -> None:
        key = schema.domain()

        if key in cls._REGISTRY:
            raise DuplicateSchemaRegistrationError(
                subject=key, existing_schema=cls._REGISTRY[key]
            )

        cls._REGISTRY[key] = schema


NodeSchemaRegistry.register(AddressSchema)
NodeSchemaRegistry.register(CnaeSchema)
NodeSchemaRegistry.register(CompanySchema)
NodeSchemaRegistry.register(EmailSchema)
NodeSchemaRegistry.register(PersonSchema)
NodeSchemaRegistry.register(PhoneSchema)
NodeSchemaRegistry.register(SanctionSchema)
