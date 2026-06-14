# dataclasses-as-entity-base

## Status

Superseded by [ADR-0002](0002-manual-entity-base-class.md)

## Context

During the initial modeling of the domain layer, Python dataclasses (`@dataclass(frozen=True)`) were chosen as the foundation for entity definitions. The intent was to leverage auto-generated `__init__`, `__eq__`, `__hash__`, and immutability enforcement without writing boilerplate.

All entity types — nodes, edges, and graphs — extended a common frozen dataclass base, with identity derived from a UUID field populated at construction time.

## Decision

Use `@dataclass(frozen=True)` as the entity abstraction. Fields are declared as class-level annotations; the dataclass machinery generates the constructor and equality protocol automatically.

## Consequences

- Field declaration and object construction are handled without manual code.
- `frozen=True` provides shallow immutability via `__setattr__` suppression.
- `__init_subclass__` does not interact with dataclass field resolution, so it cannot intercept invalid subclasses before instantiation. Contract violations (missing namespace, wrong ID type) surface only at runtime when the first instance is created, not at class-definition time.
- ID derivation logic was decoupled from the class itself, making it easy to construct entities with inconsistent or missing identifiers.
- No mechanism to enforce that every concrete entity declares its own deterministic ID strategy.
