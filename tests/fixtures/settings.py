from __future__ import annotations

from typing import Protocol

import pytest

from osint_engine.config.settings import Settings
from osint_engine.infrastructure.hashers.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
from tests.fakes.hashers import RecordingPasswordHasher


class MakeRecordingPasswordHasher(Protocol):
    def __call__(self, *, block_seconds: float) -> RecordingPasswordHasher: ...


@pytest.fixture(scope="session")
def argon2_password_hasher() -> Argon2PasswordHasher:

    return Argon2PasswordHasher()


@pytest.fixture
def events() -> list[str]:

    return []


@pytest.fixture
def make_recording_password_hasher(events: list[str]) -> MakeRecordingPasswordHasher:

    def recording_password_hasher(*, block_seconds: float) -> RecordingPasswordHasher:
        return RecordingPasswordHasher(events=events, block_seconds=block_seconds)

    return recording_password_hasher


@pytest.fixture(scope="session")
def pyjwt_service(settings: Settings) -> PyJWTService:

    return PyJWTService(
        access_token_expire_minutes=settings.access_token_expire_minutes,
        secret_key=settings.secret_key,
    )


@pytest.fixture(scope="session")
def settings() -> Settings:

    return Settings(
        access_token_expire_minutes=60,
        cors_origins=["http://localhost:3000"],
        database_url="postgresql://test:test@localhost:5432/test",
        debug=True,
        docs_redirect_root=False,
        external_credential_encryption_key=(
            "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
        ),
        fetcher_connect_timeout=15,
        fetcher_read_timeout=30,
        host="127.0.0.1",
        log_level="info",
        port=8000,
        secret_key="a-secret-key-with-at-least-32-bytes-for-hs256",
    )
