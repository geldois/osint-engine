# GraphRepository.merge cascades node/edge persistence, skipping unchanged content

## Status

Accepted

## Context

`uow.nodes`/`uow.edges` have existed on the `UoW` contract since early on, but no existing use case
(`ExpandByCNPJ`/`ExpandByCPF`/`ExpandByCNEP`/`ExpandByCEIS`) ever wrote to them directly — each only wraps the whole
assembled `Graph` in one `EntityRevision` and calls `uow.graphs.merge`, so a Person or Company first discovered inside a
CNPJ expansion was only ever reachable as part of that graph's own opaque blob, never by `uow.nodes.find(id_=...)` on
its own. Text ingestion's core mechanism — resolve an extracted identifier's deterministic id against what's already
known, before deciding stub-vs-link — depends entirely on that per-entity lookup actually returning something. Making
every existing use case write nodes/edges individually was considered and rejected in favor of fixing it once,
centrally, in `GraphRepository.merge` itself, so every present and future graph producer gets it for free.

## Decision

`MemGraphRepository.merge` now cascades `merge_many` over every node and edge the merged graph carries, individually
persisting each into `NodeRepository`/`EdgeRepository`. An unconditional cascade was implemented first and rejected
after review: re-stamping every node with the enclosing graph revision's own `fetched_at`/`source`, even entities whose
content hadn't changed since a prior fetch, made `revision_merge_policy`'s content-id-equality short-circuit pick the
fresh re-stamp as canonical on every single re-expansion of an already-known subject — silently discarding that entity's
true original provenance. The cascade now checks each node/edge's `(id, content_id)` against what's already stored
first, and only persists what's genuinely new or changed.

## Consequences

Nodes and edges first discovered through CNPJ/CPF/CNEP/CEIS expansion are now individually addressable, which is what
unblocks text ingestion's lookup and any future feature needing the same. The cost is one extra read per node/edge on
every graph merge, including the existing expansion use cases' hot path — a deliberate trade of a small, constant read
cost for correctness of provenance, not a regression introduced for its own sake. The invariant itself ("merging a graph
must cascade its nodes/edges, without corrupting unchanged ones") is documented on `GraphRepository`'s own docstring but
not structurally enforced by the contract's type signature — a future non-in-memory implementation (e.g. a Neo4j-backed
one, roadmap step 5) has to know to replicate this by reading that docstring, not because the type checker requires it.
