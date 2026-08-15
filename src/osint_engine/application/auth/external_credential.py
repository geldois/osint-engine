from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass(eq=True, frozen=True, kw_only=True)
class ExternalCredential:
    api_key: str
    provider: Provider
    username: str


class Provider(StrEnum):
    KIPFLOW = "KIPFLOW"
    PORTAL_TRANSPARENCIA = "PORTAL_TRANSPARENCIA"
