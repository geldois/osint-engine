from __future__ import annotations

from dataclasses import dataclass
from os import environ, getenv

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    access_token_expire_minutes: int
    admin_password: str
    cors_origins: list[str]
    database_url: str
    debug: bool
    docs_redirect_root: bool
    external_credential_encryption_key: str
    fetcher_connect_timeout: float
    fetcher_read_timeout: float
    host: str
    log_level: str
    port: int
    secret_key: str
    viewer_token_expire_minutes: int

    @staticmethod
    def _load_access_token_expire_minutes() -> int:
        return int(getenv(key="ACCESS_TOKEN_EXPIRE_MINUTES", default="60"))

    @staticmethod
    def _load_admin_password() -> str:
        return environ["ADMIN_PASSWORD"]

    @staticmethod
    def _load_cors_origins() -> list[str]:
        return [
            origins.strip()
            for origins in getenv(
                key="CORS_ORIGINS", default="http://localhost:3000"
            ).split(",")
        ]

    @staticmethod
    def _load_database_url() -> str:
        return environ["DATABASE_URL"]

    @staticmethod
    def _load_debug() -> bool:
        return getenv(key="DEBUG", default="false").lower() == "true"

    @staticmethod
    def _load_docs_redirect_root() -> bool:
        return getenv(key="DOCS_REDIRECT_ROOT", default="false").lower() == "true"

    @staticmethod
    def _load_external_credential_encryption_key() -> str:
        return environ["EXTERNAL_CREDENTIAL_ENCRYPTION_KEY"]

    @staticmethod
    def _load_fetcher_connect_timeout() -> float:
        return float(getenv(key="FETCHER_CONNECT_TIMEOUT", default="15.0"))

    @staticmethod
    def _load_fetcher_read_timeout() -> float:
        return float(getenv(key="FETCHER_READ_TIMEOUT", default="30.0"))

    @staticmethod
    def _load_host() -> str:
        return getenv(key="HOST", default="127.0.0.1")

    @staticmethod
    def _load_log_level() -> str:
        return getenv(key="LOG_LEVEL", default="info")

    @staticmethod
    def _load_port() -> int:
        return int(getenv(key="PORT", default="8000"))

    @staticmethod
    def _load_secret_key() -> str:
        return environ["SECRET_KEY"]

    @staticmethod
    def _load_viewer_token_expire_minutes() -> int:
        return int(getenv(key="VIEWER_TOKEN_EXPIRE_MINUTES", default="20"))

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(dotenv_path=".env", interpolate=False)

        return cls(
            access_token_expire_minutes=cls._load_access_token_expire_minutes(),
            admin_password=cls._load_admin_password(),
            cors_origins=cls._load_cors_origins(),
            database_url=cls._load_database_url(),
            debug=cls._load_debug(),
            docs_redirect_root=cls._load_docs_redirect_root(),
            external_credential_encryption_key=(
                cls._load_external_credential_encryption_key()
            ),
            fetcher_connect_timeout=cls._load_fetcher_connect_timeout(),
            fetcher_read_timeout=cls._load_fetcher_read_timeout(),
            host=cls._load_host(),
            log_level=cls._load_log_level(),
            port=cls._load_port(),
            secret_key=cls._load_secret_key(),
            viewer_token_expire_minutes=cls._load_viewer_token_expire_minutes(),
        )
