from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.conftest import MakePayload


@pytest.fixture
def brasilapi_cnpj_v1_valid_path() -> Path:
    return Path(__file__).parent / "responses" / "brasilapi_cnpj_v1_valid.json"


@pytest.fixture
def brasilapi_cnpj_v1_valid_payload(
    make_payload: MakePayload, brasilapi_cnpj_v1_valid_path: Path
) -> Payload:
    return make_payload(source="brasilapi", data=brasilapi_cnpj_v1_valid_path)
