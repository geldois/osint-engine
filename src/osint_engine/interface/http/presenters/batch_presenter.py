from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.presenters.graph_presenter import graph_to_schema
from osint_engine.interface.http.schemas.batch_schema import (
    BatchCPFEstimateSchema,
    BatchCPFOutcomeSchema,
    BatchCPFResultSchema,
)

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.application.use_cases.expansion.expand_by_cpf_batch import (
        BatchOutcome,
    )
    from osint_engine.domain.entities.bases.graph import Graph


def batch_estimate_to_schema(
    already_fetched: tuple[str, ...],
    billable: tuple[str, ...],
    invalid: tuple[str, ...],
    wait_seconds: int,
    /,
) -> BatchCPFEstimateSchema:
    return BatchCPFEstimateSchema(
        already_fetched=list(already_fetched),
        billable=list(billable),
        invalid=list(invalid),
        wait_seconds=wait_seconds,
    )


def batch_result_to_schema(
    revision: EntityRevision[Graph] | None, outcomes: tuple[BatchOutcome, ...], /
) -> BatchCPFResultSchema:
    graph = graph_to_schema(revision) if revision is not None else None

    return BatchCPFResultSchema(
        graph=graph,
        outcomes=[
            BatchCPFOutcomeSchema(cpf=cpf, error_code=error_code, status=status)
            for cpf, status, error_code in outcomes
        ],
    )
