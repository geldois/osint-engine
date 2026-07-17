from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.normalization import normalize_str_to_digits_only

PersonID = NewType("PersonID", UUID)


class Person(
    Node[PersonID], id_fields=frozenset({"cpf"}), namespace=EntityNAMESPACE.PERSON
):
    age_range: str
    cpf: str
    name: str

    @override
    def __init__(self, *, age_range: str, cpf: str, name: str) -> None:
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
            kwargs["cpf"] = normalize_str_to_digits_only(value=cpf)

        return super()._calculate_id(**kwargs)
