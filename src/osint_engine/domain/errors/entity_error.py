from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.domain_error import DomainError

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.domain.entities.bases.entity import Entity


class EntityError(DomainError, error_code=None): ...


class EntityInvalidIDTypeError(EntityError, error_code="ENTITY_INVALID_ID_TYPE"):
    id_type: Callable[[UUID], UUID]
    subject: type

    @override
    def __init__(self, *, id_type: Callable[[UUID], UUID], subject: type) -> None:
        super().__init__(id_type=id_type, subject=subject)

    @override
    def _build_message(self) -> str:
        id_type_name = self.id_type.__name__
        base_name = self.subject.__base__.__name__ if self.subject.__base__ else "..."

        return (
            f"'{id_type_name}' type must be "
            f"'Callable[[UUID], {id_type_name}]' in: "
            f"{self.subject.__name__}({base_name}[{id_type_name}])"
        )


class EntityMissingIDTypeError(EntityError, error_code="ENTITY_MISSING_ID_TYPE"):
    subject: type

    @override
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'IDType' in: "
            f"class {self.subject.__name__}(Entity[IDType], ...)"
        )


class EntityMissingIDFieldsError(EntityError, error_code="ENTITY_MISSING_ID_FIELDS"):
    subject: type[Entity[UUID]]

    @override
    def __init__(self, *, subject: type[Entity[UUID]]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'id_fields' in: "
            f"class {self.subject.__name__}(..., id_fields=frozenset[str])"
        )


class EntityMissingNamespaceError(EntityError, error_code="ENTITY_MISSING_NAMESPACE"):
    subject: type[Entity[UUID]]

    @override
    def __init__(self, *, subject: type[Entity[UUID]]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'EntityNAMESPACE' in: "
            f"class {self.subject.__name__}(..., namespace=EntityNAMESPACE)"
        )


class EntityNonDeterministicValueError(
    EntityError, error_code="ENTITY_NON_DETERMINISTIC_VALUE"
):
    value: object

    @override
    def __init__(self, *, value: object) -> None:
        super().__init__(value=value)

    @override
    def _build_message(self) -> str:
        type_name = type(self.value).__name__

        return (
            f"'{type_name}' identity contract violation - "
            f"override '__str__' to ensure deterministic UUID generation: "
            f"class {type_name}: def __str__(self) -> str: ..."
        )


class EntityInvalidIDFieldError(EntityError, error_code="ENTITY_INVALID_ID_FIELD"):
    field: str
    subject: type[Entity[UUID]]
    valid_fields: dict[str, object]

    @override
    def __init__(
        self,
        *,
        field: str,
        subject: type[Entity[UUID]],
        valid_fields: dict[str, object],
    ) -> None:
        super().__init__(field=field, subject=subject, valid_fields=valid_fields)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.field}' identity contract violation - "
            f"'{self.field}' is not a declared attribute of '{self.subject.__name__}': "
            f"id_fields must be a subset of {set(self.valid_fields.keys())}"
        )


class EntityEmptyIDFieldNameError(EntityError, error_code="ENTITY_EMPTY_ID_FIELD_NAME"):
    subject: type[Entity[UUID]]

    @override
    def __init__(self, *, subject: type[Entity[UUID]]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"id_fields cannot contain empty strings: "
            f"pass non-empty field names as id_fields"
        )


class EntityNotFoundError(EntityError, error_code="ENTITY_NOT_FOUND"):
    entity_id: UUID
    subject: type[Entity[UUID]]

    @override
    def __init__(self, *, entity_id: UUID, subject: type[Entity[UUID]]) -> None:
        super().__init__(entity_id=entity_id, subject=subject)

    @override
    def _build_message(self) -> str:
        return f"'{self.subject.__name__}' with id '{self.entity_id}'"
