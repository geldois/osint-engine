from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(eq=True, frozen=True, kw_only=True)
class User:
    hashed_password: str
    role: Role
    username: str


class Role(StrEnum):
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"
