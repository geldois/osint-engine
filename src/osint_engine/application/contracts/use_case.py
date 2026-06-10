from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    async def execute(self) -> None:
        raise NotImplementedError


class Query[ReturnType: object](ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    async def execute(self) -> ReturnType:
        raise NotImplementedError
