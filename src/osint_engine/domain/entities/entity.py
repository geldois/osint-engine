from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from inspect import isabstract
from typing import TYPE_CHECKING, get_args, get_origin
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    MissingEntityIdentityContractError,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def _verify_id_type[IDType: UUID](*, subject: type[Entity[IDType]]) -> None:
    if not hasattr(subject, "id_type") and not isabstract(subject):
        raise MissingEntityIdentityContractError(subject=subject)


class Entity[IDType: UUID](ABC):
    __slots__ = ("id",)

    id: IDType

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

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

            cls.id_type: Callable[[UUID], IDType] = candidate

            return

        _verify_id_type(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        object.__setattr__(self, "id", self._calculate_id(**kwargs))

        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    def __setattr__(self, name: str, value: object) -> None:
        raise FrozenInstanceError

    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def _calculate_id(self, **kwargs: object) -> IDType:
        return type(self).id_type(
            uuid5(namespace=NAMESPACE_DNS, name=json.dumps(kwargs, sort_keys=True))
        )


class Edge[IDType: UUID](Entity[IDType]):
    __slots__ = ("source_id", "target_id")

    @abstractmethod
    def __init__(self, *, source_id: UUID, target_id: UUID, **kwargs: object) -> None:
        super().__init__(source_id=source_id, target_id=target_id, **kwargs)


class Node[IDType: UUID](Entity[IDType]): ...
