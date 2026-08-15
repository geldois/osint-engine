from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.document_error import InvalidMaskedDocumentError
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError
from osint_engine.domain.services.normalization import normalize_masked_document
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonID = NewType("PersonID", UUID)

_CPF_LENGTH = 11


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
