from __future__ import annotations

from pydantic import BaseModel


class IngestTextRequestSchema(BaseModel):
    text: str
    pattern_set_id: str


class FieldPatternSummarySchema(BaseModel):
    node_type: str
    fields: list[str]


class TextPatternSetSchema(BaseModel):
    id: str
    patterns: list[FieldPatternSummarySchema]
