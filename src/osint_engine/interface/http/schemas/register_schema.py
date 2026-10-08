from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterSchema(BaseModel):
    username: str = Field(pattern=r"^[a-z0-9_-]{3,32}$")
    password: str = Field(min_length=8, max_length=128)
