# Manual dependency injection over FastAPI DI

## Status

Accepted

## Context

FastAPI ships a built-in dependency injection system based on `Depends()`. It is powerful and idiomatic within the
framework — it resolves function parameters at request time, supports async dependencies, and integrates with
OpenAPI's security schemes.

The project needed to wire together use cases, repositories, hashers, services, and fetchers — components that span
the domain, application, and infrastructure layers. The question was whether to use FastAPI's DI to manage this
graph or to build it manually.

## Decision

Use a manual composition root (`croot.py`) that constructs a frozen `Container` dataclass once at startup. FastAPI's
`Depends()` is allowed only at the interface layer for HTTP-specific concerns: extracting form data
(`OAuth2PasswordRequestForm`), and applying the JWT guard dependency to a router.

The `Container` is passed as a closure argument to every handler factory function (`build_get_cnpj_handler`,
`build_post_token_handler`, `build_jwt_guard`). The handler captures what it needs from the container at
construction time, not at request time.

See [ADR-0007](0007-in-memory-persistence-as-mvp-boundary.md) for why the container holds `uow_factory` rather
than a repository instance directly.

## Consequences

- The domain and application layers have no dependency on FastAPI. They can be exercised in pure pytest tests
  without spinning up an ASGI app or mocking framework internals.

- The composition graph is explicit and readable in a single file. There is no implicit resolution order, no
  circular dependency discovered at runtime, and no framework magic to debug.

- Handler factories are ordinary Python functions. Their dependencies appear in their signatures, not in decorator
  metadata — which makes them straightforward to trace and test.

- Adding a new dependency means updating `Container`, `croot.py`, and the relevant handler factory. There is no
  registry or auto-discovery; the cost of adding is proportional to the actual change.

- FastAPI's DI is not banned — it is scoped to the interface layer where its HTTP semantics (request lifecycle,
  form parsing, security schemes) add real value. Mixing it into the application layer would couple business logic
  to the framework.
