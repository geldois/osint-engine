from typing import NewType

from osint_engine.domain.errors.domain_error import DomainError


class EntityError(DomainError, error_code=None): ...


class MissingEntityIdentityContractError(
    EntityError, error_code="ENTITY_MISSING_IDENTITY_CONTRACT"
):
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'IDType' in: "
            f"class {self.subject.__name__}(Entity[IDType])"
        )


class InvalidEntityHierarchyError(EntityError, error_code="ENTITY_INVALID_HIERARCHY"):
    def __init__(self, *, subject: type, expected_base: type) -> None:
        self.expected_base = expected_base

        super().__init__(subject=subject)

    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' must inherit from "
            f"'{self.expected_base.__name__}' to use this decorator. "
            f"Fix: class {self.subject.__name__}"
            f"({self.expected_base.__name__}[IDType])"
        )


class InvalidEntityIDTypeError(EntityError, error_code="ENTITY_INVALID_ID_TYPE"):
    def __init__(self, *, subject: type, id_type: NewType) -> None:
        self.id_type = id_type

        super().__init__(subject=subject)

    def _build_message(self) -> str:
        id_type_name = self.id_type.__name__
        base_name = self.subject.__base__.__name__ if self.subject.__base__ else "..."

        return (
            f"'{id_type_name}' type must be "
            f"'Callable[[UUID], {id_type_name}]' in: "
            f"{self.subject.__name__}({base_name}[{id_type_name}])"
        )
