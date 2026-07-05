# Self-loop rejection and graph consistency enforced at construction time

## Status

Accepted

## Context

Two structural invariants of the domain graph were unprotected:

First, an edge with identical source and target represents a self-referential relationship — a company that owns
itself, a person who resides at a person. No such relationship exists in the OSINT domain; all edges connect two
distinct real-world entities. Without an explicit guard, a caller could silently construct a valid-looking edge
object that violates this invariant.

Second, a `Graph` accepts a `frozenset` of edges and a `frozenset` of nodes, but nothing prevented constructing a
graph where an edge's `source_id` or `target_id` referenced a node not present in the graph's own node set. Such a
graph would pass all existing validation (non-empty node set, root in nodes) yet be internally inconsistent.

Two alternatives were considered for each invariant. For self-loops: enforce in each concrete edge subclass, or
enforce at the `Graph` level when adding edges. For graph inconsistency: enforce at the repository layer rather
than at `Graph.__init__`, deferring the check to write time.

## Decision

Self-loop detection is placed in `Edge.__init__` in the base class: if `source_id == target_id`, a
`SelfLoopEdgeError` is raised immediately at construction. Enforcing it in the base class rather than per-subclass
ensures no concrete edge can bypass the invariant, and a new edge type added in the future inherits the check for
free. Enforcing it at the `Graph` level would allow a self-referential `Edge` object to exist in isolation, only
failing if it ever entered a graph — a weaker guarantee.

Graph edge consistency is enforced in `Graph.__init__`: after the existing node-set and root checks, every edge's
`source_id` and `target_id` must be present in the graph's node ID set; a violation raises `InconsistentGraphError`.
Enforcing this at the repository layer would allow an inconsistent `Graph` aggregate to be constructed and
temporarily held in memory; placing it at the aggregate root boundary keeps the invariant as tight as possible.

The persistence layer is append-only and has no delete operation, so there is no risk of a graph becoming
inconsistent after its initial construction. The guard protects against erroneous construction, not against
post-construction mutation.

## Consequences

- A `SelfLoopEdgeError` or `InconsistentGraphError` is raised at the earliest possible moment — object
  construction — rather than at a later application layer boundary.
- No `Edge` object with `source_id == target_id` can exist anywhere in the system, including in test doubles.
  Test fakes that previously used equal UUIDs for convenience must be updated.
- The `Graph` aggregate is always internally consistent: every edge it holds references nodes that are also held
  within the same graph.
- Enforcing consistency at construction rather than the repository layer means the check runs even in tests that
  never touch persistence, which is the desired behaviour for a domain invariant.
