from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError
from osint_engine.domain.services.normalization import (
    normalize_address_number,
    normalize_str_to_digits_only,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

AddressID = NewType("AddressID", UUID)

_CEP_DIGIT_LENGTH = 8


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
