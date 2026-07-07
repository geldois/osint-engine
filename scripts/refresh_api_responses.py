"""
Refreshes API response fixtures used by infrastructure tests.

Run with: uv run python scripts/refresh_api_responses.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from httpx2 import URL, Client, Timeout

FETCHERS_DIR = Path("tests/test_infrastructure/test_fetchers")


class _BrasilAPI:
    API_NAME: str = "brasilapi/"
    BASE_URL: URL = URL("https://brasilapi.com.br/api/")
    CASES: dict[str, list[tuple[str, str]]] = {
        "cnpj/v1/": [("cnpj_v1_valid.json", "00.000.000/0001-91")]
    }


def _digits_only(value: str) -> str:
    return re.sub(r"\D", "", value)


def _build_http_client() -> Client:
    timeout = Timeout(
        timeout=None,
        connect=15,
        read=30,
    )

    return Client(timeout=timeout)


def main() -> None:
    apis = [_BrasilAPI]

    with _build_http_client() as client:
        for api in apis:
            out_dir = FETCHERS_DIR / "responses" / f"{api.API_NAME}"
            out_dir.mkdir(parents=True, exist_ok=True)

            for endpoint, cases in api.CASES.items():
                base = api.BASE_URL.join(url=endpoint)

                for filename, identifier in cases:
                    url = base.join(url=_digits_only(identifier))

                    response = client.get(url)
                    response.raise_for_status()

                    (out_dir / filename).write_text(
                        json.dumps(response.json(), ensure_ascii=False, indent=2)
                    )

                    print(f"saved '{out_dir}{filename}'")


if __name__ == "__main__":
    main()
