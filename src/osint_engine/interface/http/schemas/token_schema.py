from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105
