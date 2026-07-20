from __future__ import annotations

from pydantic import BaseModel

from osint_engine.application.auth.external_credential import Provider  # noqa: TC001


class ExternalCredentialSchema(BaseModel):
    api_key: str
    provider: Provider
