from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.text_source_error import TextSourceEmptyError
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

TextSourceID = NewType("TextSourceID", UUID)


class TextSource(
    Node[TextSourceID],
    id_fields=frozenset({"text"}),
    namespace=EntityNAMESPACE.TEXT_SOURCE,
):
    text: str

    @override
    def __init__(self, *, text: str) -> None:
        if not text.strip():
            raise TextSourceEmptyError

        super().__init__(**own_init_kwargs(**locals()))
