from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from functools import partial

    from osint_engine.application.contracts.fetchers.ceis_fetcher import CEISFetcher
    from osint_engine.application.contracts.fetchers.cnep_fetcher import CNEPFetcher
    from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.services.jwt_service import JWTService
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
    from osint_engine.application.use_cases.credentials.list_credentials import (
        ListExternalCredentials,
    )
    from osint_engine.application.use_cases.credentials.save_credential import (
        SaveExternalCredential,
    )
    from osint_engine.application.use_cases.expansion.expand_by_ceis import ExpandByCEIS
    from osint_engine.application.use_cases.expansion.expand_by_cnep import ExpandByCNEP
    from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ
    from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
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
    ceis_fetcher: CEISFetcher
    cnep_fetcher: CNEPFetcher
    cnpj_fetcher: CNPJFetcher
    cpf_fetcher: CPFFetcher


@dataclass(frozen=True, kw_only=True)
class Policies:
    revision_merge_policy: RevisionMergePolicy
    revision_selection_policy: RevisionSelectionPolicy


@dataclass(frozen=True, kw_only=True)
class Services:
    jwt_service: JWTService


@dataclass(frozen=True, kw_only=True)
class UseCases:
    authenticate_user: partial[AuthenticateUser]
    expand_by_ceis: partial[ExpandByCEIS]
    expand_by_cnep: partial[ExpandByCNEP]
    expand_by_cnpj: partial[ExpandByCNPJ]
    expand_by_cpf: partial[ExpandByCPF]
    list_external_credentials: partial[ListExternalCredentials]
    save_external_credential: partial[SaveExternalCredential]
