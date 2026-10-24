from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

import pytest
from httpx2 import URL

from scripts.fixtures import (
    _refresh_by_identifier,  # pyright: ignore[reportPrivateUsage]
    _write_or_skip,  # pyright: ignore[reportPrivateUsage]
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class _FakeResponse:
    text: str
    status_code: int = 200
    _payload: object = field(default_factory=lambda: cast("object", {}))
    failure: Exception | None = None

    def json(self) -> object:
        return self._payload

    def raise_for_status(self) -> None:
        if self.failure is not None:
            raise self.failure


@dataclass
class _FakeClient:
    answers: list[_FakeResponse]
    calls: list[tuple[str, dict[str, str] | None]] = field(default_factory=list)

    def get(
        self,
        url: URL,
        *,
        headers: dict[str, str],  # noqa: ARG002
        params: dict[str, str] | None = None,
    ) -> _FakeResponse:
        self.calls.append((str(url), params))

        return self.answers[len(self.calls) - 1]


_URL = URL("https://example.org/api/x/1")
_BASE = URL("https://example.org/api/x/")


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


def _refresh(client: _FakeClient, destination: Path) -> str:
    return _refresh_by_identifier(
        client,
        base=_BASE,
        identifier="1",
        headers={},
        destination=destination,
    )


def test_an_identifier_that_answers_is_saved_without_listing(tmp_path: Path) -> None:
    client = _FakeClient([_FakeResponse(text='{"id": 1}', _payload={"id": 1})])

    message = _refresh(client, tmp_path / "x.json")

    assert (tmp_path / "x.json").read_text() == '{\n  "id": 1\n}'
    assert message == f"saved '{tmp_path}/x.json'"
    assert client.calls == [("https://example.org/api/x/1", None)]


def test_an_identifier_that_aged_out_falls_back_to_the_first_listed_record(
    tmp_path: Path,
) -> None:
    client = _FakeClient(
        [
            _FakeResponse(text=""),
            _FakeResponse(text="[]", _payload=[{"id": 7}, {"id": 8}]),
        ]
    )

    message = _refresh(client, tmp_path / "x.json")

    assert (tmp_path / "x.json").read_text() == '{\n  "id": 7\n}'
    assert "first listed record" in message
    assert client.calls[1] == ("https://example.org/api/x", {"pagina": "1"})


def test_an_aged_out_identifier_and_an_empty_listing_skips_the_fixture(
    tmp_path: Path,
) -> None:
    client = _FakeClient(
        [_FakeResponse(text=""), _FakeResponse(text="[]", _payload=[])]
    )

    message = _refresh(client, tmp_path / "x.json")

    assert not (tmp_path / "x.json").exists()
    assert "skipped" in message


def test_a_listing_that_is_not_a_list_is_never_taken_as_a_record(
    tmp_path: Path,
) -> None:
    client = _FakeClient(
        [_FakeResponse(text=""), _FakeResponse(text="{}", _payload={"id": 7})]
    )

    message = _refresh(client, tmp_path / "x.json")

    assert not (tmp_path / "x.json").exists()
    assert "skipped" in message


def test_the_fallback_never_overwrites_a_fixture_it_cannot_replace(
    tmp_path: Path,
) -> None:
    (tmp_path / "x.json").write_text('{"kept": true}')
    client = _FakeClient(
        [_FakeResponse(text=""), _FakeResponse(text="[]", _payload=[])]
    )

    _refresh(client, tmp_path / "x.json")

    assert (tmp_path / "x.json").read_text() == '{"kept": true}'


@pytest.mark.parametrize("failing_call", [0, 1])
def test_an_http_failure_on_either_call_is_raised_not_swallowed(
    tmp_path: Path, failing_call: int
) -> None:
    answers = [_FakeResponse(text=""), _FakeResponse(text="[]", _payload=[])]
    answers[failing_call] = _FakeResponse(
        text="", status_code=500, failure=RuntimeError("500")
    )

    with pytest.raises(RuntimeError, match="500"):
        _refresh(_FakeClient(answers), tmp_path / "x.json")
