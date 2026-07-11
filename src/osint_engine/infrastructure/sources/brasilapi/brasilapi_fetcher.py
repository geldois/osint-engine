from __future__ import annotations

from abc import abstractmethod
from typing import final

from httpx2 import URL, AsyncClient
from structlog.stdlib import get_logger

_logger = get_logger()


class BrasilAPIFetcher:
    _BASE_URL: URL = URL("https://brasilapi.com.br/api/")
    _SOURCE: str = "brasilapi"

    @final
    def __init_subclass__(cls, *, url_suffix: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls._BASE_URL = cls._BASE_URL.join(url=url_suffix)

    @abstractmethod
    def __init__(self, *, http_client: AsyncClient) -> None:
        self._http_client = http_client
        self._logger = _logger.bind(source=self._SOURCE)
