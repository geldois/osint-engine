from typing import NewType

from osint_engine.domain.errors.domain_error import DomainError


class EntityError(DomainError, error_code=None): ...


class InvalidEntityIDTypeError(EntityError, error_code="ENTITY_INVALID_ID_TYPE"):
    subject: type
    id_type: NewType

    def __init__(self, *, subject: type, id_type: NewType) -> None:
        super().__init__(subject=subject, id_type=id_type)

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

    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'IDType' in: "
            f"class {self.subject.__name__}(Entity[IDType], ...)"
        )


class MissingEntityNAMESPACEError(EntityError, error_code="ENTITY_MISSING_NAMESPACE"):
    subject: type

    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'EntityNAMESPACE' in: "
            f"class {self.subject.__name__}(..., namespace=EntityNAMESPACE)"
        )
