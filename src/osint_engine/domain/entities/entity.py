from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from inspect import isabstract
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    final,
    get_args,
    get_origin,
)
from uuid import UUID, uuid4, uuid5

from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    MissingEntityIDTypeError,
    NonDeterministicValueEntityError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

IDType_co = TypeVar("IDType_co", bound=UUID, covariant=True)


def _validate_deterministic_str(*, value: object) -> None:
    if (
        type(value).__str__ is object.__str__
        and type(value).__repr__ is object.__repr__
    ):
        raise NonDeterministicValueEntityError(value=value)


def _validate_entity_id_type[IDType: UUID](*, subject: type[Entity[IDType]]) -> None:
    if not hasattr(subject, "id_type") and not isabstract(subject):
        raise MissingEntityIDTypeError(subject=subject)


class Entity(ABC, Generic[IDType_co]):  # noqa: UP046
    id: IDType_co

    @final
    def __init_subclass__(cls, *, namespace: EntityNAMESPACE, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

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
                raise InvalidEntityIDTypeError(subject=cls, id_type=candidate)

            probe = candidate(uuid4())

            if not isinstance(probe, UUID):
                raise InvalidEntityIDTypeError(subject=cls, id_type=candidate)

            cls.id_type: Callable[[UUID], IDType_co] = staticmethod(candidate)

        _validate_entity_id_type(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        object.__setattr__(self, "id", type(self).calculate_id(**kwargs))

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
    def calculate_id(cls, **kwargs: object) -> IDType_co:
        values: list[object] = []

        for value in kwargs.values():
            _validate_deterministic_str(value=value)

            values.append(value)

        values.sort(key=lambda v: (type(v).__name__, str(v)))

        return cls.id_type(
            uuid5(namespace=cls.namespace, name=json.dumps(values, default=str))
        )
