from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_role_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_entity_record_catalog import (  # noqa: E501
    build_get_entity_record_catalog_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.get.get_entity_records_by_cpf import (  # noqa: E501
    build_get_entity_records_by_cpf_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container

_ALLOWED_ROLES = frozenset({Role.ADMIN})


def build_consumption_router(*, container: Container) -> APIRouter:
    role_guard = build_role_guard(container=container, allowed_roles=_ALLOWED_ROLES)
    rate_limit = build_expansion_rate_limit(scope="consumption")

    router = APIRouter(
        prefix="/consumption",
        dependencies=[Depends(role_guard), Depends(rate_limit)],
    )

    router.get(path="")(build_get_entity_record_catalog_handler(container=container))

    router.get(path="/{cpf}")(
        build_get_entity_records_by_cpf_handler(container=container)
    )

    return router
