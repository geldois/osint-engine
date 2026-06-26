from __future__ import annotations

from dataclasses import FrozenInstanceError
from os import environ, getenv
from pathlib import Path


def _load_dotenv() -> None:
    path = Path(".env")

    if not path.exists():
        return

    with path.open(encoding="utf-8") as file:
        for line in file:
            ln = line.strip()

            if not ln or ln.startswith("#") or "=" not in ln:
                continue

            k, _, v = ln.partition("=")

            if not k or not (k[0].isalpha() or k[0] == "_"):
                continue

            k = k.strip().upper()
            v = v.strip()

            environ.setdefault(key=k, value=v)


class Settings:
    access_token_expire_minutes: int
    algorithm: str
    debug: bool
    fetcher_connect_timeout: float
    fetcher_read_timeout: float
    host: str
    log_level: str
    port: int
    secret_key: str

    def __init__(self) -> None:
        _load_dotenv()

        object.__setattr__(
            self,
            "access_token_expire_minutes",
            int(getenv(key="ACCESS_TOKEN_EXPIRE_MINUTES", default="60")),
        )
        object.__setattr__(self, "algorithm", getenv(key="ALGORITHM", default="HS256"))
        object.__setattr__(
            self, "debug", getenv(key="DEBUG", default="false").lower() == "true"
        )
        object.__setattr__(
            self,
            "fetcher_connect_timeout",
            float(getenv(key="FETCHER_CONNECT_TIMEOUT", default="15.0")),
        )
        object.__setattr__(
            self,
            "fetcher_read_timeout",
            float(getenv(key="FETCHER_READ_TIMEOUT", default="30.0")),
        )
        object.__setattr__(self, "host", getenv(key="HOST", default="127.0.0.1"))
        object.__setattr__(self, "log_level", getenv(key="LOG_LEVEL", default="info"))
        object.__setattr__(self, "port", int(getenv(key="PORT", default="8000")))
        object.__setattr__(self, "secret_key", environ["SECRET_KEY"])

    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError
