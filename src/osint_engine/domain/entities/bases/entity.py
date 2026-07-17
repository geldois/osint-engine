from __future__ import annotations

import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal
from inspect import isabstract
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    Self,
    TypeGuard,
    TypeVar,
    final,
    get_args,
    get_origin,
)
from uuid import UUID, uuid4, uuid5

from osint_engine.domain.errors.entity_error import (
    EntityEmptyIDFieldNameError,
    EntityInvalidIDFieldError,
    EntityInvalidIDTypeError,
    EntityMissingIDFieldsError,
    EntityMissingIDTypeError,
    EntityNonDeterministicValueError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


IDType_co = TypeVar("IDType_co", bound=UUID, covariant=True)


_DETERMINISTIC_TYPES: tuple[type, ...] = (
    bool,
    datetime,
    Decimal,
    int,
    str,
    tuple,
    type(None),
    UUID,
)


def _is_tuple(*, value: object) -> TypeGuard[tuple[object, ...]]:
    return isinstance(value, tuple)


def _validate_deterministic_type(*, value: object) -> None:
    if type(value) not in _DETERMINISTIC_TYPES:
        raise EntityNonDeterministicValueError(value=value)

    if _is_tuple(value=value):
        for v in value:
            _validate_deterministic_type(value=v)


def _constructor_parameters(*, subject: type) -> dict[str, inspect.Parameter]:
    return {
        parameter_name: parameter
        for parameter_name, parameter in inspect.signature(
            obj=subject.__init__
        ).parameters.items()
        if parameter_name != "self"
        and parameter.kind
        not in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
    }


def _validate_entity_id_type[IDType: UUID](*, subject: type[Entity[IDType]]) -> None:
    if not hasattr(subject, "id_type") and not isabstract(subject):
        raise EntityMissingIDTypeError(subject=subject)


def _validate_id_fields(*, subject: type[Entity[UUID]]) -> None:
    for field in subject.id_fields:
        if not field:
            raise EntityEmptyIDFieldNameError(subject=subject)

        valid_fields = subject.init_parameters()

        if field not in valid_fields:
            raise EntityInvalidIDFieldError(
                field=field, subject=subject, valid_fields=valid_fields
            )


class Entity(ABC, Generic[IDType_co]):  # noqa: UP046
    content_id: IDType_co
    id: IDType_co
    id_fields: ClassVar[frozenset[str]]
    namespace: ClassVar[UUID]

    def __init_subclass__(
        cls,
        *,
        id_fields: frozenset[str] | None,
        namespace: EntityNAMESPACE,
        **kwargs: object,
    ) -> None:
        super().__init_subclass__(**kwargs)

        if id_fields is None and not isabstract(cls):
            raise EntityMissingIDFieldsError(subject=cls)

        if id_fields is not None:
            cls.id_fields = id_fields

            _validate_id_fields(subject=cls)

        cls.namespace = namespace.namespace

        for base in getattr(cls, "__orig_bases__", ()):
            origin = get_origin(base)

            if origin is None:
                continue

            if not (isinstance(origin, type) and issubclass(origin, Entity)):
                continue

            args = get_args(base)

            if not args:
                continue

            candidate = args[0]

            if not hasattr(candidate, "__supertype__"):
                continue

            if not issubclass(candidate.__supertype__, UUID):
                raise EntityInvalidIDTypeError(subject=cls, id_type=candidate)

            probe = candidate(uuid4())

            if not isinstance(probe, UUID):
                raise EntityInvalidIDTypeError(subject=cls, id_type=candidate)

            cls.id_type: Callable[[UUID], IDType_co] = staticmethod(candidate)

        _validate_entity_id_type(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        object.__setattr__(self, "content_id", self._calculate_id(**kwargs))

        identified_by = {field: kwargs[field] for field in self.id_fields}

        object.__setattr__(self, "id", self._calculate_id(**identified_by))

        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    @final
    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.id == other.id

    @final
    def __hash__(self) -> int:
        return self.id.int

    @classmethod
    def _calculate_id(cls, **kwargs: object) -> IDType_co:
        parameter_pairs: list[tuple[str, object]] = []

        for parameter_name, parameter in kwargs.items():
            _validate_deterministic_type(value=parameter)

            parameter_pairs.append((parameter_name, parameter))

        parameter_pairs.sort(key=lambda pair: (pair[0], str(pair[1])))

        return cls.id_type(
            uuid5(
                namespace=cls.namespace, name=json.dumps(parameter_pairs, default=str)
            )
        )

    @classmethod
    @final
    def init_parameters(cls) -> dict[str, object]:
        return dict(_constructor_parameters(subject=cls))

    @final
    def evolve(self, **changes: object) -> Self:
        return type(self)(**{**self.reconstruct_kwargs(), **changes})

    @final
    def reconstruct_kwargs(self) -> dict[str, object]:
        return {
            parameter_name: getattr(self, parameter_name)
            for parameter_name in _constructor_parameters(subject=type(self))
        }
