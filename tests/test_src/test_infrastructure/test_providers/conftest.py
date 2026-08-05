from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from osint_engine.infrastructure.providers.payload import Payload

type MakePayload = Callable[..., Payload]


@pytest.fixture
def make_payload() -> MakePayload:

    def payload(*, provider: str, data: dict[str, object] | Path) -> Payload:
        if isinstance(data, Path):
            with Path.open(data) as file:
                data_: dict[str, object] = json.load(file)

                return Payload(provider=provider, data=data_)

        return Payload(provider=provider, data=data)

    return payload
