from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorDebug(BaseModel):
    exc_type: str


class ErrorSchema(BaseModel):
    correlation_id: UUID | None = None
    debug: ErrorDebug | None = None
    detail: str
    method: str
    path: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    type: str | None = None
