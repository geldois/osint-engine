from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from osint_engine.config.settings import Settings
from osint_engine.interface.cli.commands import wait_db

if TYPE_CHECKING:
    from asyncpg import Connection


class _FakeConnection:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_wait_db_returns_once_postgres_is_reachable(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    connection = _FakeConnection()

    def from_env(_settings_type: type[Settings]) -> Settings:
        return settings

    async def connect(*, dsn: str) -> Connection:
        assert dsn == settings.database_url

        return cast("Connection", connection)

    monkeypatch.setattr(Settings, "from_env", classmethod(from_env))
    monkeypatch.setattr(wait_db.asyncpg, "connect", connect)

    await wait_db._wait_db()  # pyright: ignore[reportPrivateUsage]

    assert connection.closed


@pytest.mark.asyncio
async def test_wait_db_retries_until_postgres_accepts_connections(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    connection = _FakeConnection()
    attempts: list[None] = []
    sleeps: list[float] = []

    def from_env(_settings_type: type[Settings]) -> Settings:
        return settings

    async def connect(*, dsn: str) -> Connection:
        assert dsn == settings.database_url
        attempts.append(None)

        if len(attempts) < 3:
            raise OSError

        return cast("Connection", connection)

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(Settings, "from_env", classmethod(from_env))
    monkeypatch.setattr(wait_db.asyncpg, "connect", connect)
    monkeypatch.setattr(wait_db.asyncio, "sleep", sleep)

    await wait_db._wait_db()  # pyright: ignore[reportPrivateUsage]

    assert len(attempts) == 3
    assert sleeps == [wait_db._POLL_INTERVAL_SECONDS] * 2  # pyright: ignore[reportPrivateUsage]
    assert connection.closed


@pytest.mark.asyncio
async def test_wait_db_raises_timeout_error_when_postgres_never_becomes_reachable(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = iter([0.0, 0.0, wait_db._TIMEOUT_SECONDS])  # pyright: ignore[reportPrivateUsage]

    def from_env(_settings_type: type[Settings]) -> Settings:
        return settings

    async def connect(*, dsn: str) -> Connection:
        del dsn

        raise OSError

    async def sleep(seconds: float) -> None:
        del seconds

    def monotonic() -> float:
        return next(clock)

    monkeypatch.setattr(Settings, "from_env", classmethod(from_env))
    monkeypatch.setattr(wait_db.asyncpg, "connect", connect)
    monkeypatch.setattr(wait_db.asyncio, "sleep", sleep)
    monkeypatch.setattr(wait_db, "monotonic", monotonic)

    with pytest.raises(TimeoutError, match="Postgres did not become reachable"):
        await wait_db._wait_db()  # pyright: ignore[reportPrivateUsage]
