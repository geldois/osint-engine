from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.document_error import InvalidMaskedDocumentError
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError
from osint_engine.domain.errors.text_source_error import TextSourceEmptyError
from osint_engine.domain.services.normalization import (
    normalize_address_number,
    normalize_masked_document,
    normalize_str_to_digits_only,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

AddressID = NewType("AddressID", UUID)
CnaeID = NewType("CnaeID", UUID)
CompanyID = NewType("CompanyID", UUID)
EmailID = NewType("EmailID", UUID)
LegalProcessID = NewType("LegalProcessID", UUID)
PersonID = NewType("PersonID", UUID)
PhoneID = NewType("PhoneID", UUID)
PoliticalExposureID = NewType("PoliticalExposureID", UUID)
SanctionID = NewType("SanctionID", UUID)
TextSourceID = NewType("TextSourceID", UUID)

_CEP_DIGIT_LENGTH = 8
_CNPJ_DIGIT_LENGTH = 14
_CPF_LENGTH = 11


class Address(
    Node[AddressID],
    id_fields=frozenset({"cep", "number"}),
    namespace=EntityNAMESPACE.ADDRESS,
):
    cep: str
    city: str | None
    complement: str | None
    neighborhood: str | None
    number: str
    state: str | None
    street: str | None

    @override
    def __init__(
        self,
        *,
        cep: str,
        city: str | None,
        complement: str | None,
        neighborhood: str | None,
        number: str,
        state: str | None,
        street: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> AddressID:
        cep = kwargs["cep"]
        number = kwargs["number"]

        if isinstance(cep, str):
            normalized = normalize_str_to_digits_only(value=cep)

            if len(normalized) != _CEP_DIGIT_LENGTH:
                raise EntityInvalidIdentifierError(
                    subject=cls,
                    field="cep",
                    raw_value=cep,
                    expected_length=_CEP_DIGIT_LENGTH,
                    actual_length=len(normalized),
                )

            kwargs["cep"] = normalized

        if isinstance(number, str):
            kwargs["number"] = normalize_address_number(value=number)

        return super()._calculate_id(**kwargs)


class Cnae(Node[CnaeID], id_fields=frozenset({"code"}), namespace=EntityNAMESPACE.CNAE):
    code: str
    description: str

    @override
    def __init__(self, *, code: str, description: str) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class Company(
    Node[CompanyID], id_fields=frozenset({"cnpj"}), namespace=EntityNAMESPACE.COMPANY
):
    activity_start_date: str | None
    cnpj: str
    is_headquarters: bool | None
    legal_name: str | None
    legal_nature: str | None
    registration_status: str | None
    registration_status_date: str | None
    registration_status_reason: str | None
    share_capital: Decimal | None
    size_category: str | None
    trade_name: str | None

    @override
    def __init__(
        self,
        *,
        activity_start_date: str | None,
        cnpj: str,
        is_headquarters: bool | None,
        legal_name: str | None,
        legal_nature: str | None,
        registration_status: str | None,
        registration_status_date: str | None,
        registration_status_reason: str | None,
        share_capital: Decimal | None,
        size_category: str | None,
        trade_name: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> CompanyID:
        cnpj = kwargs["cnpj"]

        if isinstance(cnpj, str):
            normalized = normalize_str_to_digits_only(value=cnpj)

            if len(normalized) != _CNPJ_DIGIT_LENGTH:
                raise EntityInvalidIdentifierError(
                    subject=cls,
                    field="cnpj",
                    raw_value=cnpj,
                    expected_length=_CNPJ_DIGIT_LENGTH,
                    actual_length=len(normalized),
                )

            kwargs["cnpj"] = normalized

        return super()._calculate_id(**kwargs)


class Email(
    Node[EmailID], id_fields=frozenset({"address"}), namespace=EntityNAMESPACE.EMAIL
):
    address: str

    @override
    def __init__(self, *, address: str) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class LegalProcess(
    Node[LegalProcessID],
    id_fields=frozenset({"process_number"}),
    namespace=EntityNAMESPACE.LEGAL_PROCESS,
):
    court: str | None
    current_status: str | None
    distribution_date: str | None
    execution_value: Decimal | None
    is_secret_of_justice: bool | None
    lawsuit_value: Decimal | None
    lawsuit_value_currency: str | None
    process_class: str | None
    process_number: str
    process_url: str | None
    state: str | None

    @override
    def __init__(
        self,
        *,
        court: str | None,
        current_status: str | None,
        distribution_date: str | None,
        execution_value: Decimal | None,
        is_secret_of_justice: bool | None,
        lawsuit_value: Decimal | None,
        lawsuit_value_currency: str | None,
        process_class: str | None,
        process_number: str,
        process_url: str | None,
        state: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class Person(
    Node[PersonID], id_fields=frozenset({"cpf"}), namespace=EntityNAMESPACE.PERSON
):
    age_range: str | None
    birthdate: str | None
    cpf: str
    name: str | None
    registration_date: str | None
    registration_status: str | None

    @override
    def __init__(
        self,
        *,
        age_range: str | None,
        birthdate: str | None,
        cpf: str,
        name: str | None,
        registration_date: str | None,
        registration_status: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> PersonID:
        cpf = kwargs["cpf"]

        if isinstance(cpf, str):
            try:
                masked = normalize_masked_document(
                    value=cpf, expected_length=_CPF_LENGTH
                )
            except InvalidMaskedDocumentError as error:
                raise EntityInvalidIdentifierError(
                    subject=cls,
                    field="cpf",
                    raw_value=cpf,
                    expected_length=_CPF_LENGTH,
                    actual_length=error.actual_length,
                ) from error

            kwargs["cpf"] = masked

        return super()._calculate_id(**kwargs)


class Phone(
    Node[PhoneID], id_fields=frozenset({"number"}), namespace=EntityNAMESPACE.PHONE
):
    number: str

    @override
    def __init__(self, *, number: str) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class PoliticalExposure(
    Node[PoliticalExposureID],
    id_fields=frozenset(
        {"cpf", "exercise_start_date", "function_description", "government_body_code"}
    ),
    namespace=EntityNAMESPACE.POLITICAL_EXPOSURE,
):
    cpf: str
    exercise_end_date: str | None
    exercise_start_date: str | None
    function_acronym: str | None
    function_description: str
    function_level: str | None
    government_body_code: str | None
    government_body_name: str
    grace_period_end_date: str | None

    @override
    def __init__(
        self,
        *,
        cpf: str,
        exercise_end_date: str | None,
        exercise_start_date: str | None,
        function_acronym: str | None,
        function_description: str,
        function_level: str | None,
        government_body_code: str | None,
        government_body_name: str,
        grace_period_end_date: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class Sanction(
    Node[SanctionID],
    id_fields=frozenset({"organ", "source_id"}),
    namespace=EntityNAMESPACE.SANCTION,
):
    end_date: str | None
    fine_amount: Decimal | None
    legal_basis: tuple[str, ...]
    organ: Literal["CEIS", "CNEP", "CEPIM", "CEAF"]
    process_number: str | None
    publication_date: str | None
    publication_link: str
    sanction_type: str
    sanctioning_body: str
    source_id: str
    start_date: str | None

    @override
    def __init__(
        self,
        *,
        end_date: str | None,
        fine_amount: Decimal | None,
        legal_basis: tuple[str, ...],
        organ: Literal["CEIS", "CNEP", "CEPIM", "CEAF"],
        process_number: str | None,
        publication_date: str | None,
        publication_link: str,
        sanction_type: str,
        sanctioning_body: str,
        source_id: str,
        start_date: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))


class TextSource(
    Node[TextSourceID],
    id_fields=frozenset({"text"}),
    namespace=EntityNAMESPACE.TEXT_SOURCE,
):
    text: str

    @override
    def __init__(self, *, text: str) -> None:
        if not text.strip():
            raise TextSourceEmptyError

        super().__init__(**own_init_kwargs(**locals()))
