# Fail-fast error_code contract across layers

## Status

Accepted

## Context

Each layer (`domain`, `application`, `infrastructure`, `interface`) defines its own
exception base class (`DomainError`, `ApplicationError`, `InfrastructureError`,
`InterfaceError`). `DomainError` already used `__init_subclass__` to require a
`ClassVar[str | None] error_code` on every concrete subclass, raising immediately at
class-definition time when one was missing — the same fail-fast pattern used for the
entity base class (see [ADR-0002](0002-manual-entity-base-class.md)).

`ApplicationError` and `InfrastructureError` did not enforce this. A concrete subclass
could omit `error_code`, and the omission would only surface once that exception type
reached `interface/http/mappers/http_status_mapper.py` or the FastAPI error handler,
where `error_code` is read to populate the response body's `type` field — silently
producing `None` instead of a machine-readable identifier, discoverable only by
inspecting a live HTTP response.

## Decision

Extend the same `__init_subclass__` contract to `ApplicationError` and
`InfrastructureError`: every concrete (non-abstract) subclass must pass
`error_code="CODE"` in its class statement, or the import itself raises `TypeError`.
Abstract intermediate subclasses (no `__init__`/`_build_message` override) are exempt,
mirroring `DomainError`'s existing allowance for intermediate types like `EdgeError` or
`RevisionError`.

`InterfaceError` (`src/osint_engine/interface/errors/interface_error.py`) already
followed the same shape independently; this decision formalizes it as the single
convention all four layers share, rather than four independent implementations that
happen to look alike.

## Consequences

- A missing `error_code` fails at module import time, before any test runs and before
  any request reaches the error handler — consistent with the fail-fast posture
  established for entities.
- The four base classes (`DomainError`, `ApplicationError`, `InfrastructureError`,
  `InterfaceError`) are near-identical boilerplate (`__init_subclass__`, abstract
  `__init__`/`_build_message`) duplicated once per layer rather than shared through a
  common ancestor. This is deliberate: a shared base would cross layer boundaries the
  project otherwise enforces strictly, and the duplication is small and mechanical
  enough that four independent copies cost less than the coupling a shared base would
  introduce.
- `interface/http/mappers/http_status_mapper.py`, `interface/http/fastapi/error_handler.py`,
  and `interface/http/fastapi/fastapi.py` are the one place that legitimately imports
  from all four hierarchies at once — they are the app's exception-to-HTTP composition
  root, not a violation of layer direction (see inline comments in those files).
