from __future__ import annotations

from abc import ABC, abstractmethod


class InfrastructureError(ABC, Exception):
    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

        super().__init__(self._build_message())

    @abstractmethod
    def _build_message(self) -> str: ...
