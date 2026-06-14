# idtype-co-typevar-for-covariant-id-typing

## Status

Accepted

## Context

Each concrete entity declares its own `NewType` ID wrapping `UUID`:

```python
CompanyID = NewType("CompanyID", UUID)
PersonID  = NewType("PersonID",  UUID)
```

Edges carry a `source_id` and a `target_id`. Without type-level enforcement, nothing prevents a caller from passing a `PersonID` where a `CompanyID` is expected, or swapping source and target — both are `UUID` at runtime and the type-checker has no way to distinguish them unless the entity class itself is parameterized by its ID type.

Two approaches were considered:

1. **UUID5 subclasses.** Create a `class CompanyID(UUID): ...` for each entity type, making the distinction physical at runtime.
2. **`TypeVar` with `Generic`.** Make `Entity` generic in its ID type using a covariant `TypeVar`, and have each concrete class declare `Company(Node[CompanyID], ...)` at the class-statement level.

## Decision

Use a covariant `TypeVar` bound to `UUID`:

```python
IDType_co = TypeVar("IDType_co", bound=UUID, covariant=True)

class Entity(ABC, Generic[IDType_co]):
    id: IDType_co
```

Each concrete entity passes its `NewType` ID as the type argument:

```python
class Company(Node[CompanyID], namespace=EntityNAMESPACE.COMPANY): ...
```

UUID5 subclasses were rejected because:

- They allocate real `UUID` instances with a custom class at every construction site, adding memory overhead for a distinction that is purely semantic.
- `NewType` is lighter: it is a callable at runtime (just the identity function), exists only in the type-checker's world, and produces no additional allocations.
- Subclassing `UUID` (a C extension type) has subtle edge cases around `__new__` and pickling that are not worth introducing.

## Consequences

- **Static safety at zero runtime cost.** `mypy`/`pyright` enforces that a `Node[CompanyID]` cannot be substituted for a `Node[PersonID]`, and that edge source/target ID types match their declared constraints.
- **Covariance is intentional.** `IDType_co` is covariant so that `Entity[CompanyID]` is a subtype of `Entity[UUID]`, allowing generic repository interfaces to accept any entity while concrete repositories constrain to their specific type.
- **No runtime representation.** `NewType` IDs do not exist at runtime; all values are plain `UUID` instances. The type distinction is erased after the type-checker runs.
- **`__init_subclass__` validates the contract early.** The `Entity.__init_subclass__` hook inspects `__orig_bases__` to extract and verify the `IDType_co` argument when the class is defined, not when an instance is created. An invalid or missing ID type raises immediately at import time (see ADR-0002).
- **Almost everything in the domain is an `Entity`.** Nodes, edges, and graphs all inherit from `Entity[IDType_co]`, so the covariant parameterization propagates through the entire type hierarchy consistently.
