from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from functools import partial

    from osint_engine.application.contracts.fetchers.ceaf_fetcher import CEAFFetcher
    from osint_engine.application.contracts.fetchers.ceis_fetcher import CEISFetcher
    from osint_engine.application.contracts.fetchers.cepim_fetcher import CEPIMFetcher
    from osint_engine.application.contracts.fetchers.cnep_fetcher import CNEPFetcher
    from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.fetchers.legal_process_fetcher import (
        LegalProcessFetcher,
    )
    from osint_engine.application.contracts.fetchers.pep_fetcher import PEPFetcher
    from osint_engine.application.contracts.services.jwt_service import JWTService
    from osint_engine.application.contracts.services.kipflow_rate_limiter import (
        KipFlowRateLimiter,
    )
    from osint_engine.application.contracts.services.spreadsheet_reader import (
        ReadSpreadsheetText,
    )
    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.application.use_cases.authentication.authenticate_user import (
        AuthenticateUser,
    )
    from osint_engine.application.use_cases.consumption.list_entity_record_catalog import (  # noqa: E501
        ListEntityRecordCatalog,
    )
    from osint_engine.application.use_cases.consumption.list_entity_records_by_cpf import (  # noqa: E501
        ListEntityRecordsByCPF,
    )
    from osint_engine.application.use_cases.consumption.record_invalid_attempt import (
        RecordInvalidAttempt,
    )
    from osint_engine.application.use_cases.credentials.list_credentials import (
        ListExternalCredentials,
    )
    from osint_engine.application.use_cases.credentials.reveal_credential import (
        RevealExternalCredential,
    )
    from osint_engine.application.use_cases.credentials.save_credential import (
        SaveExternalCredential,
    )
    from osint_engine.application.use_cases.expansion.expand_by_ceaf import ExpandByCEAF
    from osint_engine.application.use_cases.expansion.expand_by_ceis import ExpandByCEIS
    from osint_engine.application.use_cases.expansion.expand_by_cepim import (
        ExpandByCEPIM,
    )
    from osint_engine.application.use_cases.expansion.expand_by_cnep import ExpandByCNEP
    from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ
    from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
    from osint_engine.application.use_cases.expansion.expand_by_cpf_batch import (
        EstimateCPFBatch,
        ExpandByCPFBatch,
    )
    from osint_engine.application.use_cases.expansion.expand_by_legal_process import (
        ExpandByLegalProcess,
    )
    from osint_engine.application.use_cases.expansion.expand_by_pep import ExpandByPEP
    from osint_engine.application.use_cases.history.list_edge_history import (
        ListEdgeHistory,
    )
    from osint_engine.application.use_cases.history.list_graph_catalog import (
        ListGraphCatalog,
    )
    from osint_engine.application.use_cases.history.list_graph_history import (
        ListGraphHistory,
    )
    from osint_engine.application.use_cases.history.list_node_history import (
        ListNodeHistory,
    )
    from osint_engine.application.use_cases.matching.find_possibly_matches import (
        FindPossiblyMatches,
    )
    from osint_engine.application.use_cases.text_ingestion.ingest_text import IngestText
    from osint_engine.application.use_cases.text_ingestion.list_text_patterns import (
        ListTextPatterns,
    )
    from osint_engine.config.settings import Settings


@dataclass(frozen=True, kw_only=True)
class Container:
    settings: Settings
    fetchers: Fetchers
    policies: Policies
    readiness_probe: Callable[[], Awaitable[None]]
    services: Services
    uow_factory: Callable[[], UoW]
    use_cases: UseCases


@dataclass(frozen=True, kw_only=True)
class Fetchers:
    ceaf_fetcher: CEAFFetcher
    ceis_fetcher: CEISFetcher
    cepim_fetcher: CEPIMFetcher
    cnep_fetcher: CNEPFetcher
    cnpj_fetcher: CNPJFetcher
    cpf_fetcher: CPFFetcher
    legal_process_fetcher: LegalProcessFetcher
    pep_fetcher: PEPFetcher


@dataclass(frozen=True, kw_only=True)
class Policies:
    revision_merge_policy: RevisionMergePolicy
    revision_selection_policy: RevisionSelectionPolicy


@dataclass(frozen=True, kw_only=True)
class Services:
    jwt_service: JWTService
    kipflow_rate_limiter: KipFlowRateLimiter
    read_spreadsheet_text: ReadSpreadsheetText
    spreadsheet_max_file_bytes: int


@dataclass(frozen=True, kw_only=True)
class UseCases:
    authenticate_user: partial[AuthenticateUser]
    expand_by_ceaf: partial[ExpandByCEAF]
    expand_by_ceis: partial[ExpandByCEIS]
    expand_by_cepim: partial[ExpandByCEPIM]
    expand_by_cnep: partial[ExpandByCNEP]
    expand_by_cnpj: partial[ExpandByCNPJ]
    expand_by_cpf: partial[ExpandByCPF]
    expand_by_cpf_batch: partial[ExpandByCPFBatch]
    expand_by_legal_process: partial[ExpandByLegalProcess]
    expand_by_pep: partial[ExpandByPEP]
    estimate_cpf_batch: partial[EstimateCPFBatch]
    find_possibly_matches: partial[FindPossiblyMatches]
    ingest_text: partial[IngestText]
    list_edge_history: partial[ListEdgeHistory]
    list_entity_record_catalog: partial[ListEntityRecordCatalog]
    list_entity_records_by_cpf: partial[ListEntityRecordsByCPF]
    list_external_credentials: partial[ListExternalCredentials]
    list_graph_catalog: partial[ListGraphCatalog]
    list_graph_history: partial[ListGraphHistory]
    list_node_history: partial[ListNodeHistory]
    list_text_patterns: partial[ListTextPatterns]
    record_invalid_attempt: partial[RecordInvalidAttempt]
    reveal_external_credential: partial[RevealExternalCredential]
    save_external_credential: partial[SaveExternalCredential]
