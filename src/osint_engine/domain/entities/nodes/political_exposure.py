from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PoliticalExposureID = NewType("PoliticalExposureID", UUID)


class PoliticalExposure(
    Node[PoliticalExposureID],
    id_fields=frozenset(
        {"cpf", "exercise_start_date", "function_description", "government_body_code"}
    ),
    namespace=EntityNAMESPACE.POLITICAL_EXPOSURE,
):
    cpf: str
    exercise_end_date: str | None
    exercise_start_date: str | None
    function_acronym: str | None
    function_description: str
    function_level: str | None
    government_body_code: str | None
    government_body_name: str
    grace_period_end_date: str | None

    @override
    def __init__(
        self,
        *,
        cpf: str,
        exercise_end_date: str | None,
        exercise_start_date: str | None,
        function_acronym: str | None,
        function_description: str,
        function_level: str | None,
        government_body_code: str | None,
        government_body_name: str,
        grace_period_end_date: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))
