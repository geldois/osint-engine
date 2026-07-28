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
from osint_engine.infrastructure.persistence.hybrid_uow import HybridUoW
from osint_engine.infrastructure.persistence.mem.mem_seeder import seed_mem_storage
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
from osint_engine.infrastructure.sources.brasilapi.endpoints.cnpj_v1_fetcher import (
    BrasilAPICNPJv1Fetcher,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.ceis_fetcher import (  # noqa: E501
    PortalTransparenciaCEISFetcher,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cnep_fetcher import (  # noqa: E501
    PortalTransparenciaCNEPFetcher,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cpf_fetcher import (  # noqa: E501
    PortalTransparenciaCPFFetcher,
)

if TYPE_CHECKING:
    from asyncpg import Pool
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings


def build_container(  # noqa: PLR0913
    *,
    settings: Settings,
    http_client: AsyncClient,
    pg_pool: Pool,
    external_credential_encryption_key: str | None = None,
    mem_storage: MemStorage | None = None,
    policies: Policies | None = None,
) -> Container:
    fetchers = Fetchers(
        ceis_fetcher=PortalTransparenciaCEISFetcher(http_client=http_client),
        cnep_fetcher=PortalTransparenciaCNEPFetcher(http_client=http_client),
        cnpj_fetcher=BrasilAPICNPJv1Fetcher(http_client=http_client),
        cpf_fetcher=PortalTransparenciaCPFFetcher(http_client=http_client),
    )

    pyjwt_service = PyJWTService(settings=settings)
    services = Services(jwt_service=pyjwt_service)

    mem_storage = mem_storage if mem_storage is not None else MemStorage()
    password_hasher = Argon2PasswordHasher()

    seed_mem_storage(
        settings=settings, mem_storage=mem_storage, password_hasher=password_hasher
    )

    external_credential_encryption_key = (
        external_credential_encryption_key
        if external_credential_encryption_key is not None
        else settings.external_credential_encryption_key
    )

    policies = (
        policies
        if policies is not None
        else Policies(
            revision_merge_policy=merge_by_filled_fields_policy,
            revision_selection_policy=select_current_by_newest_fetched,
        )
    )

    def uow_factory() -> HybridUoW:
        return HybridUoW(
            mem_storage=mem_storage,
            pg_pool=pg_pool,
            encryption_key=external_credential_encryption_key,
            revision_merge_policy=policies.revision_merge_policy,
            revision_selection_policy=policies.revision_selection_policy,
        )

    async def readiness_probe() -> None:
        """
        Prove the Postgres pool can actually round-trip a query; entering the
        HybridUoW alone doesn't (it only constructs the credential repository and
        acquires no connection until a query runs).
        """

        await pg_pool.execute("SELECT 1")  # pyright: ignore[reportUnknownMemberType]

    use_cases = UseCases(
        authenticate_user=partial(
            AuthenticateUser, uow_factory=uow_factory, password_hasher=password_hasher
        ),
        expand_by_ceis=partial(
            ExpandByCEIS, uow_factory=uow_factory, ceis_fetcher=fetchers.ceis_fetcher
        ),
        expand_by_cnep=partial(
            ExpandByCNEP, uow_factory=uow_factory, cnep_fetcher=fetchers.cnep_fetcher
        ),
        expand_by_cnpj=partial(
            ExpandByCNPJ, uow_factory=uow_factory, cnpj_fetcher=fetchers.cnpj_fetcher
        ),
        expand_by_cpf=partial(
            ExpandByCPF, uow_factory=uow_factory, cpf_fetcher=fetchers.cpf_fetcher
        ),
        list_external_credentials=partial(
            ListExternalCredentials, uow_factory=uow_factory
        ),
        save_external_credential=partial(
            SaveExternalCredential, uow_factory=uow_factory
        ),
    )

    return Container(
        settings=settings,
        fetchers=fetchers,
        policies=policies,
        readiness_probe=readiness_probe,
        services=services,
        uow_factory=uow_factory,
        use_cases=use_cases,
    )
