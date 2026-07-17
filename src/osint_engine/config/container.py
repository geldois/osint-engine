from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from functools import partial

    from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
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
    from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ
    from osint_engine.config.settings import Settings


@dataclass(frozen=True, kw_only=True)
class Container:
    settings: Settings
    fetchers: Fetchers
    policies: Policies
    services: Services
    uow_factory: Callable[[], UoW]
    use_cases: UseCases


@dataclass(frozen=True, kw_only=True)
class Fetchers:
    cnpj_fetcher: CNPJFetcher


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
    expand_by_cnpj: partial[ExpandByCNPJ]
