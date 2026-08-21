from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, override

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
from osint_engine.application.contracts.services.kipflow_rate_limiter import (
    KipFlowRateLimiter,
)
from osint_engine.application.use_cases.expansion.expand_by_cpf_batch import (
    EstimateCPFBatch,
    ExpandByCPFBatch,
)
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.errors.provider_error import InsufficientCreditsError
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.config.container import Policies
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
    from tests.conftest import (
        MakeEntityRevision,
        MakeExternalCredential,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory

_CPF_1 = "10000000000"
_CPF_2 = "10000000001"
_CPF_3 = "10000000002"
_CPFS = (_CPF_1, _CPF_2, _CPF_3)


def _make_person(*, cpf: str) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    )


def _make_graph(*, cpf: str) -> Graph:
    person = _make_person(cpf=cpf)

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)


def _formatted_cpf(cpf: str, /) -> str:
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def _make_uow_factory(
    *, mem_storage: MemStorage, policies: Policies
) -> Callable[[], MemUoW]:
    def factory() -> MemUoW:
        return MemUoW(
            mem_storage=mem_storage,
            revision_merge_policy=policies.revision_merge_policy,
            revision_selection_policy=policies.revision_selection_policy,
        )

    return factory


class _ProgrammedCPFFetcher(CPFFetcher):
    def __init__(
        self, *, results: dict[str, EntityRevision[Graph] | None | BaseException]
    ) -> None:
        self.results = results
        self.calls: list[str] = []

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self.calls.append(cpf)
        result = self.results[cpf]

        if isinstance(result, BaseException):
            raise result

        return result


class _FakeRateLimiter(KipFlowRateLimiter):
    def __init__(self, *, wait_seconds: int = 0) -> None:
        self.wait_seconds = wait_seconds
        self.acquisitions: list[ExternalCredential] = []
        self.forecasts: list[int] = []

    @override
    async def acquire(self, *, credential: ExternalCredential) -> None:
        self.acquisitions.append(credential)

    @override
    async def wait_seconds_for(
        self, *, credential: ExternalCredential, count: int
    ) -> int:
        self.forecasts.append(count)

        return self.wait_seconds


class TestEstimateCPFBatch:
    @pytest.mark.asyncio
    async def test_marks_every_valid_cpf_as_billable_when_none_were_fetched(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(),
            rate_limiter=_FakeRateLimiter(),
            cpfs=_CPFS,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == _CPFS
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_marks_a_kipflow_fetched_cpf_as_already_fetched(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="kipflow"
        )
        mem_storage = make_mem_storage(nodes=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            rate_limiter=_FakeRateLimiter(),
            cpfs=_CPFS,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == (_CPF_1,)
        assert billable == (_CPF_2, _CPF_3)
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_marks_a_text_ingestion_cpf_as_billable(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="text_ingestion"
        )
        mem_storage = make_mem_storage(nodes=[previous])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            rate_limiter=_FakeRateLimiter(),
            cpfs=_CPFS,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == _CPFS
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_returns_no_billable_when_every_cpf_was_fetched(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        previous = [
            make_entity_revision(entity=_make_person(cpf=cpf), provider="kipflow")
            for cpf in _CPFS
        ]
        mem_storage = make_mem_storage(nodes=previous)
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            rate_limiter=_FakeRateLimiter(),
            cpfs=_CPFS,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == _CPFS
        assert billable == ()
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_puts_every_invalid_cpf_in_the_invalid_bucket(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        cpfs = ("123", "abc", "1")

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(),
            rate_limiter=_FakeRateLimiter(),
            cpfs=cpfs,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == ()
        assert invalid == cpfs
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_estimates_a_single_cpf(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(),
            rate_limiter=_FakeRateLimiter(),
            cpfs=(_CPF_1,),
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == (_CPF_1,)
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("cpfs", "expected"),
        [
            pytest.param(
                (_CPF_1, _CPF_2, _CPF_1), (_CPF_1, _CPF_2), id="same-raw-value"
            ),
            pytest.param(
                (_CPF_1, _formatted_cpf(_CPF_1), _CPF_2),
                (_CPF_1, _CPF_2),
                id="same-cpf-formatted-later",
            ),
            pytest.param(
                (_formatted_cpf(_CPF_1), _CPF_1, _CPF_2),
                (_formatted_cpf(_CPF_1), _CPF_2),
                id="same-cpf-formatted-first",
            ),
        ],
    )
    async def test_repeated_cpfs_appear_once_at_their_first_position(
        self,
        make_mem_uow_factory: MakeMemUoWFactory,
        cpfs: tuple[str, ...],
        expected: tuple[str, ...],
    ) -> None:
        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(),
            rate_limiter=_FakeRateLimiter(),
            cpfs=cpfs,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == expected
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_reports_the_rate_limiter_forecast_for_the_billable_count(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="kipflow"
        )
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        rate_limiter = _FakeRateLimiter(wait_seconds=7)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            rate_limiter=rate_limiter,
            cpfs=_CPFS,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == (_CPF_1,)
        assert billable == (_CPF_2, _CPF_3)
        assert invalid == ()
        assert wait_seconds == 7
        assert rate_limiter.forecasts == [2]

    @pytest.mark.asyncio
    async def test_force_marks_every_valid_cpf_as_billable(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="kipflow"
        )
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            rate_limiter=_FakeRateLimiter(),
            cpfs=_CPFS,
            force=True,
            username="alice",
        )

        already_fetched, billable, invalid, wait_seconds = await use_case.execute()

        assert already_fetched == ()
        assert billable == _CPFS
        assert invalid == ()
        assert wait_seconds == 0

    @pytest.mark.asyncio
    async def test_reports_zero_wait_without_a_kipflow_credential(
        self, make_mem_uow_factory: MakeMemUoWFactory
    ) -> None:
        rate_limiter = _FakeRateLimiter(wait_seconds=7)

        use_case = EstimateCPFBatch(
            uow_factory=make_mem_uow_factory(),
            rate_limiter=rate_limiter,
            cpfs=_CPFS,
            username="alice",
        )

        _, _, _, wait_seconds = await use_case.execute()

        assert wait_seconds == 0
        assert rate_limiter.forecasts == []


class TestExpandByCPFBatch:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("failing_index", "expected_statuses"),
        [
            pytest.param(0, ["failed", "expanded", "expanded"], id="first-item-fails"),
            pytest.param(1, ["expanded", "failed", "expanded"], id="middle-item-fails"),
            pytest.param(2, ["expanded", "expanded", "failed"], id="last-item-fails"),
        ],
    )
    async def test_a_failed_item_keeps_the_others_expanded_and_merges_their_graphs(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
        failing_index: int,
        expected_statuses: list[str],
    ) -> None:
        results: dict[str, EntityRevision[Graph] | None | BaseException] = {
            cpf: make_entity_revision(entity=_make_graph(cpf=cpf)) for cpf in _CPFS
        }
        results[_CPFS[failing_index]] = InsufficientCreditsError(provider="kipflow")
        fetcher = _ProgrammedCPFFetcher(results=results)
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=_CPFS,
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        succeeding_cpfs = tuple(
            cpf for index, cpf in enumerate(_CPFS) if index != failing_index
        )

        assert revision is not None
        assert revision.entity.root_id == _make_person(cpf=succeeding_cpfs[0]).id
        assert revision.entity.nodes == frozenset(
            _make_person(cpf=cpf) for cpf in succeeding_cpfs
        )
        assert [status for _, status, _ in outcomes] == expected_statuses
        assert outcomes[failing_index] == (
            _CPFS[failing_index],
            "failed",
            "PROVIDER_INSUFFICIENT_CREDITS",
        )

    @pytest.mark.asyncio
    async def test_an_already_fetched_cpf_does_not_spend_an_external_call(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="kipflow"
        )
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        fetcher = _ProgrammedCPFFetcher(
            results={_CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1))}
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_CPF_1,),
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is None
        assert outcomes == ((_CPF_1, "already_fetched", "ENTITY_ALREADY_FETCHED"),)
        assert fetcher.calls == []

    @pytest.mark.asyncio
    async def test_force_refetches_an_already_fetched_cpf(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        previous = make_entity_revision(
            entity=_make_person(cpf=_CPF_1), provider="kipflow"
        )
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        fetcher = _ProgrammedCPFFetcher(
            results={_CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1))}
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_CPF_1,),
            force=True,
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is not None
        assert outcomes == ((_CPF_1, "expanded", None),)
        assert fetcher.calls == [_CPF_1]

    @pytest.mark.asyncio
    async def test_a_cpf_the_provider_does_not_know_is_empty(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(results={_CPF_1: None})

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_CPF_1,),
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is None
        assert outcomes == ((_CPF_1, "empty", None),)

    @pytest.mark.asyncio
    async def test_when_every_item_fails_the_result_has_no_graph(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(
            results={cpf: InsufficientCreditsError(provider="kipflow") for cpf in _CPFS}
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=_CPFS,
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is None
        assert [status for _, status, _ in outcomes] == ["failed", "failed", "failed"]
        assert all(
            error_code == "PROVIDER_INSUFFICIENT_CREDITS"
            for _, _, error_code in outcomes
        )

    @pytest.mark.asyncio
    async def test_an_invalid_cpf_never_reaches_the_fetcher(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(
            results={_CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1))}
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=("123", _CPF_1),
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is not None
        assert outcomes == (
            ("123", "invalid", None),
            (_CPF_1, "expanded", None),
        )
        assert fetcher.calls == [_CPF_1]

    @pytest.mark.asyncio
    async def test_outcomes_echo_the_input_string_not_the_sanitized_form(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(
            results={_CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1))}
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_formatted_cpf(_CPF_1),),
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is not None
        assert outcomes == ((_formatted_cpf(_CPF_1), "expanded", None),)

    @pytest.mark.asyncio
    async def test_outcomes_follow_the_deduplicated_input_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(
            results={
                _CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1)),
                _CPF_2: make_entity_revision(entity=_make_graph(cpf=_CPF_2)),
            }
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_CPF_1, _CPF_2, _CPF_1),
            username="alice",
        )

        revision, outcomes = await use_case.execute()

        assert revision is not None
        assert outcomes == (
            (_CPF_1, "expanded", None),
            (_CPF_2, "expanded", None),
        )

    @pytest.mark.asyncio
    async def test_graphs_sharing_a_node_merge_without_duplicating_it(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        person_a = _make_person(cpf=_CPF_1)
        person_b = _make_person(cpf=_CPF_2)
        shared = _make_person(cpf="10000000009")
        graph_a = Graph(
            edges=frozenset(), nodes=frozenset({person_a, shared}), root_id=person_a.id
        )
        graph_b = Graph(
            edges=frozenset(), nodes=frozenset({person_b, shared}), root_id=person_b.id
        )
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _ProgrammedCPFFetcher(
            results={
                _CPF_1: make_entity_revision(entity=graph_a),
                _CPF_2: make_entity_revision(entity=graph_b),
            }
        )

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=(_CPF_1, _CPF_2),
            username="alice",
        )

        revision, _ = await use_case.execute()

        assert revision is not None
        assert revision.entity.nodes == frozenset({person_a, person_b, shared})


class _RecordingMemUoW(MemUoW):
    def __init__(
        self,
        *,
        events: list[tuple[int, str]],
        instance_id: int,
        mem_storage: MemStorage,
        policies: Policies,
    ) -> None:
        super().__init__(
            mem_storage=mem_storage,
            revision_merge_policy=policies.revision_merge_policy,
            revision_selection_policy=policies.revision_selection_policy,
        )
        self._events = events
        self._instance_id = instance_id

    @override
    async def commit(self) -> None:
        self._events.append((self._instance_id, "commit"))

        await super().commit()

    @override
    async def rollback(self) -> None:
        self._events.append((self._instance_id, "rollback"))

        await super().rollback()


class TestExpandByCPFBatchIsolation:
    @pytest.mark.asyncio
    async def test_each_item_uses_its_own_uow_and_only_the_failed_item_rolls_back(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        events: list[tuple[int, str]] = []
        instance_counter = 0

        def uow_factory() -> _RecordingMemUoW:
            nonlocal instance_counter
            instance_counter += 1

            return _RecordingMemUoW(
                events=events,
                instance_id=instance_counter,
                mem_storage=mem_storage,
                policies=policies,
            )

        fetcher = _ProgrammedCPFFetcher(
            results={
                _CPF_1: make_entity_revision(entity=_make_graph(cpf=_CPF_1)),
                _CPF_2: InsufficientCreditsError(provider="kipflow"),
                _CPF_3: make_entity_revision(entity=_make_graph(cpf=_CPF_3)),
            }
        )

        use_case = ExpandByCPFBatch(
            uow_factory=uow_factory,
            cpf_fetcher=fetcher,
            cpfs=_CPFS,
            username="alice",
        )

        await use_case.execute()

        assert len(events) == 3
        assert len({instance_id for instance_id, _ in events}) == 3
        assert [event for _, event in events].count("commit") == 2
        assert [event for _, event in events].count("rollback") == 1


class _InFlightFetcher(CPFFetcher):
    def __init__(self, *, make_entity_revision: MakeEntityRevision) -> None:
        self._make_entity_revision = make_entity_revision
        self.in_flight = 0
        self.max_in_flight = 0

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph]:
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)

        await asyncio.sleep(0)

        self.in_flight -= 1

        return self._make_entity_revision(entity=_make_graph(cpf=cpf))


class TestExpandByCPFBatchConcurrency:
    @pytest.mark.asyncio
    async def test_never_runs_more_than_five_fetches_at_once_and_reaches_the_ceiling(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        policies: Policies,
    ) -> None:
        cpfs = tuple(f"100000000{i:02d}" for i in range(20))
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        fetcher = _InFlightFetcher(make_entity_revision=make_entity_revision)

        use_case = ExpandByCPFBatch(
            uow_factory=_make_uow_factory(mem_storage=mem_storage, policies=policies),
            cpf_fetcher=fetcher,
            cpfs=cpfs,
            username="alice",
        )

        await use_case.execute()

        assert fetcher.max_in_flight <= 5
        assert fetcher.max_in_flight == 5
