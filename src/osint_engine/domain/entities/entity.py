from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from inspect import isabstract
from typing import TYPE_CHECKING, get_args, get_origin, override
from uuid import UUID, uuid4, uuid5

from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    MissingEntityIDTypeError,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from collections.abc import Callable


def _verify_entity_id_type[IDType: UUID](*, subject: type[Entity[IDType]]) -> None:
    if not hasattr(subject, "id_type") and not isabstract(subject):
        raise MissingEntityIDTypeError(subject=subject)


class Entity[IDType: UUID](ABC):
    id: IDType

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

            cls.id_type: Callable[[UUID], IDType] = staticmethod(candidate)

            return

        _verify_entity_id_type(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        object.__setattr__(self, "id", type(self).calculate_id(**kwargs))

        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.id == other.id

    def __hash__(self) -> int:
        return self.id.int

    @classmethod
    def calculate_id(cls, **kwargs: object) -> IDType:
        return cls.id_type(
            uuid5(
                namespace=cls.namespace,
                name=json.dumps(kwargs, sort_keys=True, default=str),
            )
        )


class Edge[IDType: UUID](Entity[IDType], namespace=EntityNAMESPACE.EDGE):
    @override
    @abstractmethod
    def __init__(self, *, source_id: UUID, target_id: UUID, **kwargs: object) -> None:
        super().__init__(source_id=source_id, target_id=target_id, **kwargs)


class Node[IDType: UUID](Entity[IDType], namespace=EntityNAMESPACE.NODE):
    @override
    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
