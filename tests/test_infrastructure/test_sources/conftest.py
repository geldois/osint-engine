from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from osint_engine.infrastructure.sources.payload import Payload

type MakePayload = Callable[..., Payload]


@pytest.fixture
def make_payload() -> MakePayload:
    """
    *,
    source: str,
    data: dict[str, object] | Path
    """

    def payload(*, source: str, data: dict[str, object] | Path) -> Payload:
        if isinstance(data, Path):
            with Path.open(data) as file:
                data_: dict[str, object] = json.load(file)

                return Payload(source=source, data=data_)

        return Payload(source=source, data=data)

    return payload
