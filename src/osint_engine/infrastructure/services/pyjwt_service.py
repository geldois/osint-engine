from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override

from jwt import PyJWTError, decode, encode  # pyright: ignore[reportUnknownVariableType]

from osint_engine.application.contracts.services.jwt_service import JWTService
from osint_engine.infrastructure.errors.token_error import InvalidTokenError

if TYPE_CHECKING:
    from osint_engine.config.settings import Settings


class PyJWTService(JWTService):
    _JWT_ALGORITHM = "HS256"

    def __init__(self, *, settings: Settings) -> None:
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.secret_key = settings.secret_key

    @property
    def algorithm(self) -> str:
        return self._JWT_ALGORITHM

    @override
    def create_access_token(
        self, *, username: str, role: str, expire_minutes: int | None = None
    ) -> str:
        minutes = (
            expire_minutes
            if expire_minutes is not None
            else self.access_token_expire_minutes
        )
        expiration_time = datetime.now(tz=UTC) + timedelta(minutes=minutes)

        return encode(
            payload={"exp": expiration_time, "sub": username, "role": role},
            key=self.secret_key,
            algorithm=self._JWT_ALGORITHM,
        )

    @override
    def decode_access_token(self, *, token: str) -> dict[str, object]:
        try:
            return decode(
                jwt=token, key=self.secret_key, algorithms=[self._JWT_ALGORITHM]
            )
        except PyJWTError as exception:
            raise InvalidTokenError(detail=str(exception)) from exception
