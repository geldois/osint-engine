from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.config.settings import Settings

if TYPE_CHECKING:
    from pathlib import Path


def test_from_env_loads_postgres_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-password")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:password@database/app")
    monkeypatch.setenv(
        "EXTERNAL_CREDENTIAL_ENCRYPTION_KEY",
        "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    )
    monkeypatch.setenv("SECRET_KEY", "secret-key")

    settings = Settings.from_env()

    assert settings.database_url == "postgresql://user:password@database/app"
    assert (
        settings.external_credential_encryption_key
        == "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
    )


@pytest.mark.parametrize(
    "missing_variable",
    ["DATABASE_URL", "EXTERNAL_CREDENTIAL_ENCRYPTION_KEY"],
)
def test_from_env_requires_postgres_settings(
    missing_variable: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    environment = {
        "ADMIN_PASSWORD": "admin-password",
        "DATABASE_URL": "postgresql://user:password@database/app",
        "EXTERNAL_CREDENTIAL_ENCRYPTION_KEY": (
            "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
        ),
        "SECRET_KEY": "secret-key",
    }

    for key, value in environment.items():
        if key == missing_variable:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)

    with pytest.raises(KeyError, match=missing_variable):
        Settings.from_env()
