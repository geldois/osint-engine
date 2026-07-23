from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from osint_engine.config.settings import Settings
from osint_engine.interface.cli.commands import serve

if TYPE_CHECKING:
    from types import TracebackType

    from asyncpg import Pool
    from fastapi import FastAPI
    from httpx2 import AsyncClient

    from osint_engine.config.container import Container


class _AsyncResource[Resource]:
    def __init__(self, resource: Resource) -> None:
        self.resource = resource
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> Resource:
        self.entered = True
        return self.resource

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True


@pytest.mark.asyncio
async def test_serve_opens_both_resources_and_wires_hybrid_container(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    http_client = cast("AsyncClient", object())
    pg_pool = cast("Pool", object())
    container = cast("Container", object())
    fastapi_app = cast("FastAPI", object())
    http_resource = _AsyncResource(http_client)
    pg_resource = _AsyncResource(pg_pool)
    logging_debug_values: list[bool] = []
    served: list[tuple[FastAPI, Settings]] = []

    def from_env(_settings_type: type[Settings]) -> Settings:
        return settings

    def build_http_client(*, settings: Settings) -> _AsyncResource[AsyncClient]:
        assert settings is settings_fixture
        return http_resource

    def create_pool(*, dsn: str) -> _AsyncResource[Pool]:
        assert dsn == settings.database_url
        return pg_resource

    def configure_logging(*, debug: bool) -> None:
        logging_debug_values.append(debug)

    def build_container(
        *,
        settings: Settings,
        http_client: AsyncClient,
        pg_pool: Pool,
        external_credential_encryption_key: str,
    ) -> Container:
        assert settings is settings_fixture
        assert http_client is http_client_fixture
        assert pg_pool is pg_pool_fixture
        assert (
            external_credential_encryption_key
            == settings.external_credential_encryption_key
        )
        return container

    def build_fastapi_app(*, container: Container) -> FastAPI:
        assert container is container_fixture
        return fastapi_app

    async def serve_http(*, app: FastAPI, settings: Settings) -> None:
        served.append((app, settings))

    settings_fixture = settings
    http_client_fixture = http_client
    pg_pool_fixture = pg_pool
    container_fixture = container

    monkeypatch.setattr(Settings, "from_env", classmethod(from_env))
    monkeypatch.setattr(serve, "_build_http_client", build_http_client)
    monkeypatch.setattr(serve.asyncpg, "create_pool", create_pool)
    monkeypatch.setattr(serve, "configure_logging", configure_logging)
    monkeypatch.setattr(serve, "build_container", build_container)
    monkeypatch.setattr(serve, "build_fastapi_app", build_fastapi_app)
    monkeypatch.setattr(serve, "serve_http", serve_http)

    await serve._serve()  # pyright: ignore[reportPrivateUsage]

    assert http_resource.entered
    assert http_resource.exited
    assert pg_resource.entered
    assert pg_resource.exited
    assert logging_debug_values == [settings.debug]
    assert served == [(fastapi_app, settings)]
