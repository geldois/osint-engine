from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.domain_error import DomainError

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from osint_engine.domain.entities.entity import Entity


class EntityError(DomainError, error_code=None): ...


class InvalidEntityIDTypeError(EntityError, error_code="ENTITY_INVALID_ID_TYPE"):
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


class MissingEntityIDTypeError(EntityError, error_code="ENTITY_MISSING_ID_TYPE"):
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


class MissingEntityNAMESPACEError(EntityError, error_code="ENTITY_MISSING_NAMESPACE"):
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


class NotFoundEntityError(EntityError, error_code="ENTITY_NOT_FOUND"):
    entity_id: UUID
    subject: type[Entity[UUID]]

    @override
    def __init__(
        self,
        *,
        entity_id: UUID,
        subject: type[Entity[UUID]],
    ) -> None:
        super().__init__(entity_id=entity_id, subject=subject)

    @override
    def _build_message(self) -> str:
        return f"'{self.subject.__name__}' with id '{self.entity_id}'"
