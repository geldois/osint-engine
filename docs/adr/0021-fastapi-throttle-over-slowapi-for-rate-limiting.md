# fastapi-throttle over slowapi for rate limiting

## Status

Accepted

## Context

Exposing `POST /auth/viewer-token` and, through it, `GET /cnpj/{cnpj}` to unauthenticated demo traffic created two
concrete abuse surfaces: exhausting the upstream BrasilAPI quota, and brute-forcing the admin password on
`POST /auth/token`. Rate limiting needed to run in-memory (no Redis in scope, per ADR-0007) and differentiate limits
by caller role on the same route (`/cnpj/{cnpj}`: 60/min for `ADMIN`, 10/min for `VIEWER`, keyed off the decoded JWT
role rather than IP or username).

`slowapi` was the initial choice — it is the most widely used FastAPI rate limiter and supports per-route dynamic
`key_func`/`limit_value` callables, which fit the role-based differentiation directly. Two problems surfaced during
implementation: `SlowAPIASGIMiddleware`, required for the `@limiter.limit` decorator to inject rate-limit headers,
wraps responses the same way the project's own logging `BaseHTTPMiddleware` does — stacking the two produced an
`assert not response_started` failure on every error response, not just rate-limited ones. Separately, `slowapi`
0.1.10 (confirmed current via PyPI, the GitHub releases page, and the live `master` branch source) still calls the
deprecated `asyncio.iscoroutinefunction` internally, with no fix released or merged upstream.

## Decision

Switch to `fastapi-throttle`. It applies limits via a plain FastAPI `Depends()` dependency instead of a decorator, so
there is no second ASGI middleware layer to conflict with `handle_logging`. It ships full type hints (`py.typed`),
which resolved cleanly under `basedpyright --strict` with zero `pyright: ignore` needed anywhere in
`rate_limit.py` — `slowapi`'s partial stubs had required several. It has no external dependency beyond FastAPI
itself and no known deprecation warnings as of this writing.

`fastapi-throttle`'s `RateLimiter` takes a fixed `times`/`seconds` pair at construction, with no dynamic
per-request limit value. Differentiating `ADMIN` from `VIEWER` on `/cnpj/{cnpj}` therefore uses two separate
`RateLimiter` instances, each with a constant `key_func` (`"cnpj:ADMIN"` / `"cnpj:VIEWER"`) giving every caller of
that role one shared bucket; `build_cnpj_rate_limit` decodes the role once per request and calls whichever instance
applies. It also raises a bare `HTTPException` on limit exceeded rather than the project's own error hierarchy, so
`_translate_rate_limit_error` wraps every `RateLimiter` call and re-raises `RateLimitExceededError` (a new
`InterfaceError` subclass, `interface/errors/rate_limit_error.py`) carrying `retry_after_seconds` — keeping every 429
on the same `ErrorSchema`/`correlation_id` response shape as the rest of the API instead of the library's own
untagged `{"detail": ...}` body.

## Consequences

- Adding a third differentiated limit (a new role, or a limit that varies by something other than role) means adding
  another fixed `RateLimiter` instance and another branch in the dispatch function, not a single dynamic callable —
  more boilerplate than `slowapi`'s approach for that specific case, traded for avoiding the middleware conflict.
- `fastapi-throttle` is a small, single-maintainer project — far less battle-tested than `slowapi`. Acceptable for an
  MVP demo; worth re-evaluating if this deployment moves to sustained production traffic.
- Rate-limit state lives in a plain dict inside each `RateLimiter` instance, matching `slowapi`'s in-memory backend:
  it resets on restart and does not share state across multiple worker processes or replicas. Fine for a single
  Uvicorn process; a horizontally scaled deployment would need a shared backend regardless of which library is used.
- The translation layer (`_translate_rate_limit_error`) is a permanent maintenance seam — any future
  `fastapi-throttle` upgrade that changes its exception shape needs a matching update here.
