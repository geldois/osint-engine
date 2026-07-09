from typing import override

from osint_engine.interface.errors.interface_error import InterfaceError


class SchemaError(InterfaceError, error_code=None): ...


class UnmappedTypeSchemaError(SchemaError, error_code="SCHEMA_UNMAPPED_TYPE"):
    subject: type

    @override
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return f"'{self.subject.__name__}' has no schema mapping"


class MissingDiscriminatorFieldError(
    SchemaError, error_code="SCHEMA_MISSING_DISCRIMINATOR"
):
    subject: type

    @override
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' must define a 'type' field with a Literal value"
        )


class DuplicateSchemaRegistrationError(
    SchemaError, error_code="SCHEMA_DUPLICATE_REGISTRATION"
):
    subject: type
    existing_schema: type

    @override
    def __init__(self, *, subject: type, existing_schema: type) -> None:
        super().__init__(subject=subject, existing_schema=existing_schema)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' is already registered"
            f" with '{self.existing_schema.__name__}'"
        )
