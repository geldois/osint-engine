"""
Refreshes API response fixtures used by infrastructure tests.

Run with: uv run osint-engine refresh-fixtures
(or directly: uv run python scripts/refresh_test_source_responses.py)

Portal da Transparência's endpoints require PORTAL_TRANSPARENCIA_API_KEY set in
the environment — request a key at https://api.portaldatransparencia.gov.br/.
"""

from __future__ import annotations

import json
import re
from os import getenv
from pathlib import Path

from httpx2 import URL, Client, Timeout

from osint_engine.config.dotenv import load_dotenv

SOURCES_DIR = Path("tests/test_infrastructure/test_sources")


def _require_env(key: str, /) -> str:
    value = getenv(key)

    if value is None:
        message = (
            f"{key} is not set. This script (unlike the app itself, which never "
            f"reads it) needs it to record real API fixtures — request a key at "
            f"https://api.portaldatransparencia.gov.br/ and set it in .env."
        )

        raise RuntimeError(message)

    return value


class _BrasilAPI:
    API_NAME: str = "brasilapi"
    BASE_URL: URL = URL("https://brasilapi.com.br/api/")
    CASES: dict[str, list[tuple[str, str]]] = {
        "cnpj/v1/": [(f"{API_NAME}_cnpj_v1.json", "00.000.000/0001-91")],
        "cep/v2/": [(f"{API_NAME}_cep_v2.json", "70040912")]
    }

    @staticmethod
    def headers() -> dict[str, str]:
        return {}


class _PortalTransparencia:
    API_NAME: str = "portal_transparencia"
    BASE_URL: URL = URL("https://api.portaldatransparencia.gov.br/api-de-dados/")
    # The real API only returns a single object (matching map_graph's
    # contract) from the by-id endpoint (GET .../cnep/{id}); the collection
    # endpoint (GET .../cnep?codigoSancionado=...) returns an array instead.
    # These ids must belong to a record that still exists — swap them if the
    # source record is ever delisted.
    CASES: dict[str, list[tuple[str, str]]] = {
        "cnep/": [(f"{API_NAME}_cnep.json", "359510")],
        "ceis/": [(f"{API_NAME}_ceis.json", "314300")],
    }
    # "/pf" is deliberately excluded from this refresh script: unlike CNPJ
    # (a business registration number) a CPF identifies an individual, and
    # this script's cases are meant to be shareable/re-runnable without
    # pinning a real person's document number in source control.

    @staticmethod
    def headers() -> dict[str, str]:
        return {"chave-api-dados": _require_env("PORTAL_TRANSPARENCIA_API_KEY")}


def _digits_only(value: str) -> str:
    return re.sub(r"\D", "", value)


def _build_http_client() -> Client:
    timeout = Timeout(timeout=None, connect=15, read=30)

    return Client(timeout=timeout)


def main() -> None:
    load_dotenv()

    apis = [_BrasilAPI, _PortalTransparencia]

    with _build_http_client() as client:
        for api in apis:
            out_dir = (
                SOURCES_DIR / f"test_{api.API_NAME}" / "test_endpoints" / "responses"
            )
            out_dir.mkdir(parents=True, exist_ok=True)

            for endpoint, cases in api.CASES.items():
                base = api.BASE_URL.join(url=endpoint)

                for filename, identifier in cases:
                    url = base.join(url=_digits_only(identifier))

                    response = client.get(url, headers=api.headers())
                    response.raise_for_status()

                    (out_dir / filename).write_text(
                        json.dumps(response.json(), ensure_ascii=False, indent=2)
                    )

                    print(f"saved '{out_dir}/{filename}'")


if __name__ == "__main__":
    main()
