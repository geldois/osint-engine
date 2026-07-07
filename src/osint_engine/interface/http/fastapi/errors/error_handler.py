from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from structlog.stdlib import get_logger

from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.config.container import Container
from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.domain.errors.entity_error import EntityError, EntityNotFoundError
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphRootNotInNodesError,
)
from osint_engine.infrastructure.errors.data_source_error import (
    DataSourceError,
    DataSourceRequestError,
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.errors.token_error import InvalidTokenError
from osint_engine.infrastructure.errors.uow_error import UoWError
from osint_engine.interface.errors.interface_error import InterfaceError
from osint_engine.interface.errors.sanitization_error import SanitizationError
from osint_engine.interface.http.fastapi.errors.schema_error import SchemaError
from osint_engine.interface.http.fastapi.schemas.error_schema import (
    ErrorDebug,
    ErrorSchema,
)
from osint_engine.observability.context import correlation_id

_logger = get_logger()


def build_error_handler(  # noqa: C901
    *, container: Container
) -> Callable[[Request, Exception], JSONResponse]:
    def handle_error(request: Request, exception: Exception) -> JSONResponse:  # noqa: C901
        headers: dict[str, str] | None = None

        match exception:
            case EntityNotFoundError():
                status = 404
            case InvalidCredentialsError() | InvalidTokenError():
                status = 401
                headers = {"WWW-Authenticate": "Bearer"}
            case SanitizationError():
                status = 422
            case GraphHasNoNodesError() | GraphRootNotInNodesError():
                status = 422
            case DataSourceRequestError():
                status = 502
            case UnexpectedFieldTypeError() | UnexpectedPayloadError():
                status = 500
            case DataSourceError():
                status = 502
            case EntityError():
                status = 500
            case SchemaError() | UoWError():
                status = 500
            case DomainError():
                status = 422
            case _:
                status = 500

        exception_threshold = 500

        suitable_logger = (
            _logger.info if status < exception_threshold else _logger.error
        )
        suitable_logger(
            "http_exception",
            status=status,
            exc_type=type(exception).__name__,
            exc=str(exception),
            path=request.url.path,
        )

        error_debug = (
            ErrorDebug(exc_type=type(exception).__name__)
            if container.settings.debug
            else None
        )
        error_schema = ErrorSchema(
            correlation_id=correlation_id.get(),
            debug=error_debug,
            detail=str(exception),
            method=request.method,
            path=request.url.path,
            type=exception.error_code
            if isinstance(exception, (DomainError, InterfaceError))
            else None,
        )

        return JSONResponse(
            status_code=status,
            content=error_schema.model_dump(exclude_none=True),
            headers=headers,
        )

    return handle_error
