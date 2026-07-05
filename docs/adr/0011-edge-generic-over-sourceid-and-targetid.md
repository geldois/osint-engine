# Three-TypeVar generic for Edge: IDType, SourceID, TargetID

## Status

Accepted

## Context

Before this decision, `Edge` declared `source_id` and `target_id` as plain `UUID`. As the domain grew with concrete
edges connecting distinct entity kinds — `PersonOwnsCompany` links a `PersonID` source to a `CompanyID` target,
`CompanyLocatedAt` links a `CompanyID` source to an `AddressID` target — the type system had no way to express that
the source and target of an edge carry semantically different identity types. Both fields were typed as the same
`UUID`, making it impossible for the type checker to catch a mismatched assignment or a caller passing the wrong ID
kind to a concrete edge constructor.

The alternative considered was keeping `source_id: UUID` and `target_id: UUID` and relying on naming conventions
and documentation to distinguish the two roles. This is cheaper to express but cannot be verified at compile time
and does not prevent accidental transposition of source and target when constructing a concrete edge.

## Decision

Introduce two independent covariant TypeVars — `SourceID_co` and `TargetID_co`, both bound to `UUID` — alongside
the existing `IDType_co`. `Edge` becomes `Generic[IDType_co, SourceID_co, TargetID_co]`. Each concrete edge
declares its own source and target ID types explicitly in its class signature. All consumers of `Edge` — abstract
repositories, in-memory repositories, presenters, schemas, and `MemStorage` — carry the full three-parameter
annotation.

A side-effect of distinct TypeVars is that when `SourceID_co` and `TargetID_co` are different concrete types, the
type system rules out self-loops structurally: a `CompanyID` can never equal a `PersonID`. For same-type edges
(e.g., a hypothetical `PersonKnowsPerson`) the runtime check added in the same change handles the remaining case.

## Consequences

- The full relational contract of each edge is expressed and verified at compile time rather than by convention.
- Concrete edge classes and all their consumers are more verbose; every annotation must carry all three type
  arguments. The verbosity is proportional to the precision gained.
- Assigning the wrong ID kind to a source or target is now a type error, not a silent data bug.
- The three-TypeVar form forces Graph and MemStorage to annotate edges as `Edge[UUID, UUID, UUID]` when operating
  on the abstract collection, which is less precise than the concrete type but correct and consistent with the
  existing pattern for `Node[UUID]`.
