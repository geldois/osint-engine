from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from osint_engine.application.revision.policies.revision_merge_policy import (
    merge_by_filled_fields_policy,
)
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.application.use_cases.authentication.authenticate_user import (
    AuthenticateUser,
)
from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ
from osint_engine.config.container import (
    Container,
    Fetchers,
    Policies,
    Services,
    UseCases,
)
from osint_engine.infrastructure.hashers.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from osint_engine.infrastructure.persistence.mem.mem_seeder import seed_mem_storage
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
from osint_engine.infrastructure.sources.brasilapi.endpoints.cnpj_v1_fetcher import (
    BrasilAPICNPJv1Fetcher,
)

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings


def build_container(
    *,
    settings: Settings,
    http_client: AsyncClient,
    mem_storage: MemStorage | None = None,
    policies: Policies | None = None,
) -> Container:
    fetchers = Fetchers(cnpj_fetcher=BrasilAPICNPJv1Fetcher(http_client=http_client))

    pyjwt_service = PyJWTService(settings=settings)
    services = Services(jwt_service=pyjwt_service)

    mem_storage = mem_storage if mem_storage is not None else MemStorage()
    password_hasher = Argon2PasswordHasher()

    seed_mem_storage(
        settings=settings, mem_storage=mem_storage, password_hasher=password_hasher
    )

    policies = (
        policies
        if policies is not None
        else Policies(
            revision_merge_policy=merge_by_filled_fields_policy,
            revision_selection_policy=select_current_by_newest_fetched,
        )
    )

    def uow_factory() -> MemUoW:
        return MemUoW(
            mem_storage=mem_storage,
            revision_merge_policy=policies.revision_merge_policy,
            revision_selection_policy=policies.revision_selection_policy,
        )

    use_cases = UseCases(
        authenticate_user=partial(
            AuthenticateUser, uow_factory=uow_factory, password_hasher=password_hasher
        ),
        expand_by_cnpj=partial(
            ExpandByCNPJ, uow_factory=uow_factory, cnpj_fetcher=fetchers.cnpj_fetcher
        ),
    )

    return Container(
        settings=settings,
        fetchers=fetchers,
        policies=policies,
        services=services,
        uow_factory=uow_factory,
        use_cases=use_cases,
    )
