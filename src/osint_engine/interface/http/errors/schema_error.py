from typing import override

from osint_engine.interface.errors.interface_error import InterfaceError


class SchemaError(InterfaceError): ...


class UnmappedTypeSchemaError(SchemaError):
    subject: type

    @override
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return f"'{self.subject.__name__}' has no schema mapping"


class MissingDiscriminatorFieldError(SchemaError):
    subject: type

    @override
    def __init__(self, *, subject: type) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' must define a 'type' field with a Literal value"
        )
