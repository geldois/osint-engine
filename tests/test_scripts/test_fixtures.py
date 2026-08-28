from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from httpx2 import URL

from scripts.fixtures import _write_or_skip  # pyright: ignore[reportPrivateUsage]

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class _FakeResponse:
    text: str
    status_code: int = 200
    _payload: dict[str, object] = field(default_factory=dict)

    def json(self) -> object:
        return self._payload


_URL = URL("https://example.org/api/x/1")


def test_saves_the_fixture_when_the_body_is_valid_json(tmp_path: Path) -> None:
    response = _FakeResponse(text='{"a": 1}', _payload={"a": 1})

    message = _write_or_skip(
        response=response, out_dir=tmp_path, filename="x.json", url=_URL
    )

    saved = tmp_path / "x.json"
    assert saved.read_text() == '{\n  "a": 1\n}'
    assert message == f"saved '{tmp_path}/x.json'"


def test_skips_without_raising_when_the_body_is_empty(tmp_path: Path) -> None:
    response = _FakeResponse(text="")

    message = _write_or_skip(
        response=response, out_dir=tmp_path, filename="x.json", url=_URL
    )

    assert not (tmp_path / "x.json").exists()
    assert "skipped" in message
    assert "empty body" in message


def test_skips_when_the_body_is_only_whitespace(tmp_path: Path) -> None:
    response = _FakeResponse(text="   \n")

    message = _write_or_skip(
        response=response, out_dir=tmp_path, filename="x.json", url=_URL
    )

    assert not (tmp_path / "x.json").exists()
    assert "skipped" in message


def test_skip_never_touches_a_fixture_already_on_disk(tmp_path: Path) -> None:
    existing = tmp_path / "x.json"
    existing.write_text('{"kept": true}')
    response = _FakeResponse(text="")

    _write_or_skip(response=response, out_dir=tmp_path, filename="x.json", url=_URL)

    assert existing.read_text() == '{"kept": true}'
