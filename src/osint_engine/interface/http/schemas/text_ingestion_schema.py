from __future__ import annotations

from pydantic import BaseModel


class IngestTextRequestSchema(BaseModel):
    text: str
    patterns: list[str]


class TextPatternNameSchema(BaseModel):
    name: str
    node_type: str
    fields: list[str]


class TextPatternSetSchema(BaseModel):
    id: str
    pattern_names: list[str]


class TextPatternCatalogSchema(BaseModel):
    patterns: list[TextPatternNameSchema]
    bundles: list[TextPatternSetSchema]
