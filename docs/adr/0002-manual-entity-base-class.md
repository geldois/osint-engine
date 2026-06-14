# manual-entity-base-class

## Status

Accepted — Supersedes [ADR-0001](0001-dataclasses-as-entity-base.md)

## Context

The dataclass-based approach (ADR-0001) exposed two structural problems:

1. **Late failure.** Contract violations — a concrete entity missing a namespace, or declaring an incompatible ID type — were only discoverable at the point the first instance was constructed. There was no mechanism to reject an invalid class at definition time.
2. **Loss of control over `__init__`.** Frozen dataclasses suppress `__setattr__` through their own generated machinery, which conflicts with a custom `__init__` that needs to call `object.__setattr__` to populate fields while also computing a deterministic identity before any field is set.

The domain model needed a fail-fast contract: if a class violates the entity protocol, the import itself should raise, not the first test that instantiates it.

## Decision

Replace the dataclass base with a hand-written `Entity` ABC that uses `__init_subclass__` to validate the entity protocol at class-definition time. Specifically:

- Every subclass must declare a `namespace` (passed as a keyword argument to the class statement via `EntityNAMESPACE`). This is validated in `__init_subclass__` and stored on the class.
- Every concrete (non-abstract) subclass must supply a typed `IDType` as the generic parameter of `Entity[IDType_co]`. The hook inspects `__orig_bases__` to extract and validate the type argument immediately when the class body is evaluated.
- Immutability is enforced by overriding `__setattr__` and `__delattr__` to raise `FrozenInstanceError`, mirroring the frozen dataclass behavior but under full control.
- `__init__` computes the deterministic identity via `calculate_id` before setting any field, then uses `object.__setattr__` to bypass the immutability guard during construction only.

`Node`, `Edge`, and `Graph` each declare their own intermediate namespaces (`EntityNAMESPACE.NODE`, `EntityNAMESPACE.EDGE`, `EntityNAMESPACE.GRAPH`), while concrete types declare domain-specific namespaces (`EntityNAMESPACE.COMPANY`, `EntityNAMESPACE.PERSON`, etc.).

## Consequences

- Invalid entity definitions fail at import time, not at test time. The domain is self-defending.
- ID derivation is centralized in `Entity.calculate_id` and cannot be bypassed or forgotten.
- `__eq__` and `__hash__` are implemented once on `Entity` using the deterministic ID, so all subclasses inherit correct identity semantics automatically.
- The class declaration syntax becomes slightly more verbose: `class Company(Node[CompanyID], namespace=EntityNAMESPACE.COMPANY)`, but the annotation is self-documenting.
- Removes the dependency on dataclass machinery entirely; the behavior of the entity lifecycle is explicit and readable in one file.
