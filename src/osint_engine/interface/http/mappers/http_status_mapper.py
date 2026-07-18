# This module is the app's exception→HTTP-status composition root: it
# deliberately references every layer's error hierarchy (domain, application,
# infrastructure, interface) to translate raises into responses. It is the
# one place import direction runs outward-in rather than inward-out.
from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.application.errors.revision_error import RevisionError
from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.domain.errors.edge_error import EdgeSelfLoopError
from osint_engine.domain.errors.entity_error import (
    EntityError,
    EntityInvalidIdentifierError,
    EntityNotFoundError,
)
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphRootNotInNodesError,
)
from osint_engine.infrastructure.errors.data_source_error import (
    DataSourceError,
    UnexpectedFieldFormatError,
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.errors.token_error import InvalidTokenError, TokenError
from osint_engine.infrastructure.errors.uow_error import UoWError
from osint_engine.interface.errors.sanitization_error import SanitizationError
from osint_engine.interface.http.errors.schema_error import SchemaError

_STATUS_MAP: tuple[tuple[type[Exception], int], ...] = (
    (EntityNotFoundError, 404),
    (InvalidCredentialsError, 401),
    (InvalidTokenError, 401),
    (TokenError, 401),
    (SanitizationError, 422),
    (GraphHasNoNodesError, 422),
    (GraphRootNotInNodesError, 422),
    (EntityInvalidIdentifierError, 422),
    (EdgeSelfLoopError, 422),
    (RevisionError, 422),
    (UnexpectedFieldTypeError, 500),
    (UnexpectedPayloadError, 500),
    (UnexpectedFieldFormatError, 500),
    (DataSourceError, 502),
    (EntityError, 500),
    (SchemaError, 500),
    (UoWError, 500),
    (DomainError, 422),
)

HTTP_SERVER_ERROR = 500

HTTP_UNAUTHORIZED = 401


def map_status_from_error(error: Exception, /) -> int:
    return next(
        (s for exception_type, s in _STATUS_MAP if isinstance(error, exception_type)),
        500,
    )
