from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, final

from httpx2 import URL, AsyncClient
from structlog.stdlib import get_logger

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential

_logger = get_logger()


class PortalTransparenciaFetcher:
    _API_KEY_HEADER: str = "chave-api-dados"
    _BASE_URL: URL = URL("https://api.portaldatransparencia.gov.br/api-de-dados/")
    _SOURCE: str = "portal_transparencia"

    @final
    def __init_subclass__(cls, *, url_suffix: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls._BASE_URL = cls._BASE_URL.join(url=url_suffix)

    @abstractmethod
    def __init__(self, *, http_client: AsyncClient) -> None:
        self._http_client = http_client
        self._logger = _logger.bind(source=self._SOURCE)

    @final
    def _build_headers(self, *, credential: ExternalCredential) -> dict[str, str]:
        return {self._API_KEY_HEADER: credential.api_key}
