from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from structlog.stdlib import get_logger

from osint_engine.application.errors.auth_error import InvalidCredentialsAuthError
from osint_engine.config.container import Container
from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.domain.errors.entity_error import EntityError, NotFoundEntityError
from osint_engine.domain.errors.graph_error import (
    HasNoNodesGraphError,
    RootNotInNodesGraphError,
)
from osint_engine.infrastructure.errors.auth_error import InvalidTokenAuthError
from osint_engine.infrastructure.errors.fetcher_error import (
    ExternalAPIFetcherError,
    FetcherError,
    UnexpectedFieldTypeFetcherError,
    UnexpectedSchemaFetcherError,
)
from osint_engine.infrastructure.errors.uow_error import (
    AlreadyPreparedUoWError,
    NotPreparedUoWError,
    UoWError,
)
from osint_engine.interface.http.errors.schema_error import (
    SchemaError,
    UnmappedTypeSchemaError,
)
from osint_engine.interface.http.schemas.error_schema import ErrorDebug, ErrorSchema
from osint_engine.observability.context import correlation_id

_logger = get_logger()


def build_error_handler(  # noqa: C901
    *, container: Container
) -> Callable[[Request, Exception], JSONResponse]:
    def handle_error(request: Request, exception: Exception) -> JSONResponse:
        headers: dict[str, str] | None = None

        match exception:
            case NotFoundEntityError():
                status = 404
            case InvalidCredentialsAuthError() | InvalidTokenAuthError():
                status = 401
                headers = {"WWW-Authenticate": "Bearer"}
            case HasNoNodesGraphError() | RootNotInNodesGraphError():
                status = 422
            case ExternalAPIFetcherError():
                status = 502
            case UnexpectedFieldTypeFetcherError() | UnexpectedSchemaFetcherError():
                status = 500
            case FetcherError():
                status = 502
            case EntityError():
                status = 500
            case (
                AlreadyPreparedUoWError()
                | NotPreparedUoWError()
                | UoWError()
                | UnmappedTypeSchemaError()
                | SchemaError()
            ):
                status = 500
            case DomainError():
                status = 422
            case _:
                status = 500

        exc_threshold = 500

        suitable_logger = _logger.info if status < exc_threshold else _logger.error
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
            type=exception.error_code if isinstance(exception, DomainError) else None,
        )

        return JSONResponse(
            status_code=status,
            content=error_schema.model_dump(exclude_none=True),
            headers=headers,
        )

    return handle_error
