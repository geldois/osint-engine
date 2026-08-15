from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, final

from httpx2 import URL, AsyncClient
from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.infrastructure.errors.external_credential_error import (
    ExternalCredentialRejectedError,
)

if TYPE_CHECKING:
    from httpx2 import HTTPStatusError

    from osint_engine.application.auth.external_credential import ExternalCredential

_logger = get_logger()

_CREDENTIAL_REJECTED_STATUS_CODES = frozenset({401})


class KipFlowFetcher:
    _API_KEY_HEADER: str = "X-API-Key"
    _BASE_URL: URL = URL("https://api.kipflow.io/")
    _PROVIDER: str = "kipflow"

    @final
    def __init_subclass__(cls, *, url_suffix: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls._BASE_URL = cls._BASE_URL.join(url=url_suffix)

    @abstractmethod
    def __init__(self, *, http_client: AsyncClient) -> None:
        self._http_client = http_client
        self._logger = _logger.bind(provider=self._PROVIDER)

    @final
    def _build_headers(self, *, credential: ExternalCredential) -> dict[str, str]:
        return {self._API_KEY_HEADER: credential.api_key}

    @final
    def _raise_for_credential_rejection(
        self, *, exception: HTTPStatusError, credential: ExternalCredential
    ) -> None:
        if exception.response.status_code in _CREDENTIAL_REJECTED_STATUS_CODES:
            raise ExternalCredentialRejectedError(
                username=credential.username, provider=Provider.KIPFLOW
            ) from exception
