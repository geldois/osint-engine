from fastapi import APIRouter

from osint_engine.config.container import Container
from osint_engine.interface.http.routers.handlers.get.get_cnpj import (
    build_get_cnpj_handler,
)


def build_cnpj_router(*, container: Container) -> APIRouter:
    router = APIRouter(prefix="/cnpj")

    router.get(path="/{cnpj}")(build_get_cnpj_handler(container=container))

    return router
