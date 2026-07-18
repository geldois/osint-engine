from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.normalization import (
    normalize_masked_document,
    normalize_str_to_digits_only,
)

PersonID = NewType("PersonID", UUID)

_CPF_LENGTH = 11


class Person(
    Node[PersonID], id_fields=frozenset({"cpf"}), namespace=EntityNAMESPACE.PERSON
):
    age_range: str | None
    cpf: str
    name: str

    @override
    def __init__(self, *, age_range: str | None, cpf: str, name: str) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> PersonID:
        cpf = kwargs["cpf"]

        if isinstance(cpf, str):
            masked = normalize_masked_document(value=cpf)

            if len(masked) != _CPF_LENGTH:
                raise EntityInvalidIdentifierError(
                    subject=cls,
                    field="cpf",
                    raw_value=cpf,
                    expected_length=_CPF_LENGTH,
                    actual_length=len(masked),
                )

            kwargs["cpf"] = normalize_str_to_digits_only(value=cpf)

        return super()._calculate_id(**kwargs)
