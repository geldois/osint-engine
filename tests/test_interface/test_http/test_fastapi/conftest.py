from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, Timeout

from osint_engine.config.croot import build_container
from osint_engine.config.settings import Settings
from osint_engine.interface.http.fastapi.fastapi import build_fastapi_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI

    from osint_engine.config.container import Container, Policies
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
    from tests.conftest import MakeMemStorage

type MakeContainer = Callable[..., Container]
type MakeSettings = Callable[..., Settings]


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client(settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """The shared HTTP client that outbound fetchers are built on."""

    timeout = Timeout(
        timeout=None,
        connect=settings.fetcher_connect_timeout,
        read=settings.fetcher_read_timeout,
    )

    async with AsyncClient(timeout=timeout) as http_client:
        yield http_client


@pytest.fixture
def make_settings(settings: Settings) -> MakeSettings:
    """
    *,
    access_token_expire_minutes: int | None = None,
    admin_password: str | None = None,
    cors_origins: list[str] | None = None,
    debug: bool | None = None,
    docs_redirect_root: bool | None = None,
    fetcher_connect_timeout: float | None = None,
    fetcher_read_timeout: float | None = None,
    host: str | None = None,
    log_level: str | None = None,
    port: int | None = None,
    secret_key: str | None = None
    """

    def settings_(
        *,
        access_token_expire_minutes: int | None = None,
        admin_password: str | None = None,
        cors_origins: list[str] | None = None,
        debug: bool | None = None,
        docs_redirect_root: bool | None = None,
        fetcher_connect_timeout: float | None = None,
        fetcher_read_timeout: float | None = None,
        host: str | None = None,
        log_level: str | None = None,
        port: int | None = None,
        secret_key: str | None = None,
    ) -> Settings:
        return Settings(
            access_token_expire_minutes=access_token_expire_minutes
            if access_token_expire_minutes is not None
            else settings.access_token_expire_minutes,
            admin_password=admin_password
            if admin_password is not None
            else settings.admin_password,
            cors_origins=cors_origins
            if cors_origins is not None
            else settings.cors_origins,
            debug=debug if debug is not None else settings.debug,
            docs_redirect_root=docs_redirect_root
            if docs_redirect_root is not None
            else settings.docs_redirect_root,
            fetcher_connect_timeout=fetcher_connect_timeout
            if fetcher_connect_timeout is not None
            else settings.fetcher_connect_timeout,
            fetcher_read_timeout=fetcher_read_timeout
            if fetcher_read_timeout is not None
            else settings.fetcher_read_timeout,
            host=host if host is not None else settings.host,
            log_level=log_level if log_level is not None else settings.log_level,
            port=port if port is not None else settings.port,
            secret_key=secret_key if secret_key is not None else settings.secret_key,
        )

    return settings_


@pytest.fixture
def make_container(
    settings: Settings,
    http_client: AsyncClient,
    make_mem_storage: MakeMemStorage,
    policies: Policies,
) -> MakeContainer:
    """
    *,
    settings: Settings | None = None,
    http_client: AsyncClient | None = None,
    mem_storage: MemStorage | None = None,
    policies: Policies | None = None
    """

    settings_ = settings
    http_client_ = http_client
    policies_ = policies

    def container_(
        *,
        settings: Settings | None = None,
        http_client: AsyncClient | None = None,
        mem_storage: MemStorage | None = None,
        policies: Policies | None = None,
    ) -> Container:
        return build_container(
            settings=settings if settings is not None else settings_,
            http_client=http_client if http_client is not None else http_client_,
            mem_storage=mem_storage if mem_storage is not None else make_mem_storage(),
            policies=policies if policies is not None else policies_,
        )

    return container_


@pytest.fixture
def container(make_container: MakeContainer) -> Container:
    """The canonical container over seeded in-memory storage."""

    return make_container()


@pytest.fixture
def fastapi_app(make_container: MakeContainer) -> FastAPI:
    """The application under test."""

    return build_fastapi_app(container=make_container())


@pytest_asyncio.fixture(loop_scope="session")
async def fastapi_app_client(
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client bound to the application under test."""

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client
