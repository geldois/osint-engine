from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from structlog.stdlib import get_logger

# Exception composition root — see http_status_mapper.py for the rationale
# behind referencing infrastructure error types directly from interface.
from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.config.container import Container
from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.infrastructure.errors.infrastructure_error import (
    InfrastructureError,
)
from osint_engine.interface.errors.interface_error import InterfaceError
from osint_engine.interface.http.mappers.http_status_mapper import (
    HTTP_SERVER_ERROR,
    HTTP_UNAUTHORIZED,
    map_status_from_error,
)
from osint_engine.interface.http.schemas.error_schema import ErrorDebug, ErrorSchema
from osint_engine.observability.context import correlation_id

_logger = get_logger()


def build_error_handler(
    *, container: Container
) -> Callable[[Request, Exception], JSONResponse]:
    def handle_error(request: Request, exception: Exception) -> JSONResponse:
        status = map_status_from_error(exception)

        headers = (
            {"WWW-Authenticate": "Bearer"} if status == HTTP_UNAUTHORIZED else None
        )

        suitable_logger = _logger.info if status < HTTP_SERVER_ERROR else _logger.error
        suitable_logger(
            "http_exception",
            status=status,
            exc_type=type(exception).__name__,
            exc=str(exception),
            path=request.url.path,
        )

        detail = (
            str(exception) if status < HTTP_SERVER_ERROR else "Internal server error"
        )
        error_debug = (
            ErrorDebug(exc_type=type(exception).__name__)
            if container.settings.debug
            else None
        )
        error_code = (
            exception.error_code
            if isinstance(
                exception,
                (DomainError, ApplicationError, InfrastructureError, InterfaceError),
            )
            else None
        )
        error_schema = ErrorSchema(
            correlation_id=correlation_id.get(),
            debug=error_debug,
            detail=detail,
            method=request.method,
            path=request.url.path,
            type=error_code,
        )

        return JSONResponse(
            status_code=status,
            content=error_schema.model_dump(mode="json", exclude_none=True),
            headers=headers,
        )

    return handle_error
