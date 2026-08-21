from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from osint_engine.interface.http.schemas.graph_schema import GraphSchema  # noqa: TC001


class BatchCPFRequestSchema(BaseModel):
    cpfs: list[str] = Field(min_length=1, max_length=50)
    force: bool = False


class BatchCPFEstimateSchema(BaseModel):
    already_fetched: list[str]
    billable: list[str]
    invalid: list[str]
    wait_seconds: int


type BatchCPFStatus = Literal[
    "already_fetched", "empty", "expanded", "failed", "invalid"
]


class BatchCPFOutcomeSchema(BaseModel):
    cpf: str
    error_code: str | None
    status: BatchCPFStatus


class BatchCPFResultSchema(BaseModel):
    graph: GraphSchema | None
    outcomes: list[BatchCPFOutcomeSchema]
