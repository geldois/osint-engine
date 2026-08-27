from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.osint_error import OsintError
from osint_engine.domain.errors.sanitization_error import InvalidCPFError
from osint_engine.domain.services.sanitization import sanitize_cpf

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.consumption.entity_record import ConsumptionOutcome
    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.services.kipflow_rate_limiter import (
        KipFlowRateLimiter,
    )
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()

_KIPFLOW_PROVIDER = "kipflow"
_MAX_CONCURRENT_EXPANSIONS = 5

type BatchOutcomeStatus = ConsumptionOutcome

type BatchOutcome = tuple[str, BatchOutcomeStatus, str | None]


class ExpandByCPFBatch(
    Query[tuple[EntityRevision[Graph] | None, tuple[BatchOutcome, ...]]]
):
    uow_factory: Callable[[], UoW]
    cpf_fetcher: CPFFetcher
    cpfs: tuple[str, ...]
    force: bool
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        cpf_fetcher: CPFFetcher,
        cpfs: tuple[str, ...],
        force: bool = False,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            cpf_fetcher=cpf_fetcher,
            cpfs=cpfs,
            force=force,
            username=username,
        )

    @override
    async def execute(
        self,
    ) -> tuple[EntityRevision[Graph] | None, tuple[BatchOutcome, ...]]:
        _logger.info(
            "cpf.batch.expansion.start", count=len(self.cpfs), force=self.force
        )

        raw_cpfs, sanitized_cpfs = _dedupe_and_sanitize(self.cpfs)
        semaphore = asyncio.Semaphore(_MAX_CONCURRENT_EXPANSIONS)

        results = await asyncio.gather(
            *(
                self._expand_one(cpf=cpf, semaphore=semaphore)
                for cpf in sanitized_cpfs
                if cpf is not None
            )
        )

        outcomes: list[BatchOutcome] = []
        revisions: list[EntityRevision[Graph]] = []
        result_index = 0

        for raw_cpf, sanitized in zip(raw_cpfs, sanitized_cpfs, strict=True):
            if sanitized is None:
                outcomes.append((raw_cpf, "invalid", None))
                continue

            status, error_code, revision = results[result_index]
            result_index += 1

            outcomes.append((raw_cpf, status, error_code))

            if revision is not None:
                revisions.append(revision)

        if not revisions:
            _logger.info("cpf.batch.expansion.no_graphs")

            return None, tuple(outcomes)

        merged = revisions[0].entity

        for revision in revisions[1:]:
            merged = merged.merge(other=revision.entity)

        _logger.info(
            "cpf.batch.expansion.success",
            expanded=len(revisions),
            outcomes=len(outcomes),
        )

        return replace(revisions[0], entity=merged), tuple(outcomes)

    async def _expand_one(
        self, *, cpf: str, semaphore: asyncio.Semaphore
    ) -> tuple[BatchOutcomeStatus, str | None, EntityRevision[Graph] | None]:
        async with semaphore:
            try:
                revision = await ExpandByCPF(
                    uow_factory=self.uow_factory,
                    cpf_fetcher=self.cpf_fetcher,
                    cpf=cpf,
                    force=self.force,
                    username=self.username,
                ).execute()
            except AlreadyFetchedError as error:
                return "already_fetched", _error_code(error), None
            except OsintError as error:
                return "failed", _error_code(error), None

            if revision is None:
                return "empty", None, None

            return "expanded", None, revision


class EstimateCPFBatch(
    Query[tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], int]]
):
    uow_factory: Callable[[], UoW]
    rate_limiter: KipFlowRateLimiter
    cpfs: tuple[str, ...]
    force: bool
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        rate_limiter: KipFlowRateLimiter,
        cpfs: tuple[str, ...],
        force: bool = False,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            rate_limiter=rate_limiter,
            cpfs=cpfs,
            force=force,
            username=username,
        )

    @override
    async def execute(
        self,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], int]:
        _logger.info("cpf.batch.estimate.start", count=len(self.cpfs), force=self.force)

        raw_cpfs, sanitized_cpfs = _dedupe_and_sanitize(self.cpfs)

        already_fetched: list[str] = []
        billable: list[str] = []
        invalid = [
            raw_cpf
            for raw_cpf, value in zip(raw_cpfs, sanitized_cpfs, strict=True)
            if value is None
        ]

        async with self.uow_factory() as uow:
            if self.force:
                billable.extend(
                    raw_cpf
                    for raw_cpf, cpf in zip(raw_cpfs, sanitized_cpfs, strict=True)
                    if cpf is not None
                )
            else:
                for raw_cpf, cpf in zip(raw_cpfs, sanitized_cpfs, strict=True):
                    if cpf is None:
                        continue

                    stub = Person(
                        age_range=None,
                        birthdate=None,
                        cpf=cpf,
                        name=None,
                        registration_date=None,
                        registration_status=None,
                    )

                    revisions = await uow.nodes.list_revisions(id_=stub.id)

                    previous = next(
                        (
                            revision
                            for revision in revisions
                            if revision.provider == _KIPFLOW_PROVIDER
                        ),
                        None,
                    )

                    bucket = already_fetched if previous is not None else billable
                    bucket.append(raw_cpf)

            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.KIPFLOW
            )

        wait_seconds = 0

        if credential is not None:
            wait_seconds = await self.rate_limiter.wait_seconds_for(
                credential=credential, count=len(billable)
            )

        return tuple(already_fetched), tuple(billable), tuple(invalid), wait_seconds


def _dedupe_and_sanitize(
    cpfs: tuple[str, ...], /
) -> tuple[list[str], list[str | None]]:
    seen: set[str] = set()
    raw_cpfs: list[str] = []
    sanitized_cpfs: list[str | None] = []

    for raw in cpfs:
        try:
            sanitized = sanitize_cpf(raw)
        except InvalidCPFError:
            sanitized = None

        key = raw if sanitized is None else sanitized

        if key in seen:
            continue

        seen.add(key)
        raw_cpfs.append(raw)
        sanitized_cpfs.append(sanitized)

    return raw_cpfs, sanitized_cpfs


def _error_code(error: Exception) -> str | None:
    return getattr(error, "error_code", None)
