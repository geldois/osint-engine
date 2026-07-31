# Translates an exception into an HTTP status by reading its semantic
# ``ErrorCategory`` (a domain concept) rather than matching concrete error
# types. This keeps the dependency rule intact: the interface classifies errors
# from every layer without importing any outer layer's error classes.
from osint_engine.domain.errors.error_category import ErrorCategory

_CATEGORY_STATUS: dict[ErrorCategory, int] = {
    ErrorCategory.NOT_FOUND: 404,
    ErrorCategory.UNAUTHORIZED: 401,
    ErrorCategory.FORBIDDEN: 403,
    ErrorCategory.RATE_LIMITED: 429,
    ErrorCategory.INVALID_INPUT: 422,
    ErrorCategory.UPSTREAM_FAILURE: 502,
    ErrorCategory.INTERNAL: 500,
}

HTTP_SERVER_ERROR = 500

HTTP_UNAUTHORIZED = 401


def map_status_from_error(error: Exception, /) -> int:
    category = getattr(error, "category", None)

    if not isinstance(category, ErrorCategory):
        return HTTP_SERVER_ERROR

    return _CATEGORY_STATUS.get(category, HTTP_SERVER_ERROR)
