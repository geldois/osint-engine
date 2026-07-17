from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.normalization import (
    normalize_address_number,
    normalize_str_to_digits_only,
)

AddressID = NewType("AddressID", UUID)


class Address(
    Node[AddressID],
    id_fields=frozenset({"cep", "number"}),
    namespace=EntityNAMESPACE.ADDRESS,
):
    cep: str
    city: str
    complement: str | None
    neighborhood: str
    number: str
    state: str
    street: str

    @override
    def __init__(
        self,
        *,
        cep: str,
        city: str,
        complement: str | None,
        neighborhood: str,
        number: str,
        state: str,
        street: str,
    ) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> AddressID:
        cep = kwargs["cep"]
        number = kwargs["number"]

        if isinstance(cep, str):
            kwargs["cep"] = normalize_str_to_digits_only(value=cep)

        if isinstance(number, str):
            kwargs["number"] = normalize_address_number(value=number)

        return super()._calculate_id(**kwargs)
