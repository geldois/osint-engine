# Use case stamps revision fetched_at over fetcher-returned revisions

## Status

Accepted

## Context

The revision refactor changed the graph repository contract from `save(graph)` to
`merge(revision: EntityRevision[Graph])`, so a `Graph` produced by `CNPJFetcher.fetch` can no longer be persisted
directly — it must first be wrapped in an `EntityRevision` carrying a `fetched_at` timestamp. Two placements were
weighed for minting that revision. The fetcher could return `EntityRevision[Graph]` directly, on the argument that the
component performing the fetch owns the most honest `fetched_at`; this keeps timestamping at the I/O boundary and leaves
use cases as pure orchestration, but it ripples through the `CNPJFetcher` protocol, its `BrasilAPI` implementation, and
the `Query[Graph]` return semantics — surface the interrupted refactor never touched. Alternatively the use case could
stamp `datetime.now(UTC)` immediately after `fetch` returns, which keeps the change confined to the one call site that
actually broke.

## Decision

`ExpandByCNPJ.execute` mints `EntityRevision(entity=graph, fetched_at=datetime.now(tz=UTC), merged_at=None)` right after
awaiting the fetch and passes it to `graphs.merge`, leaving the fetcher contract returning a bare `Graph` and the
use case returning a bare `Graph`. The revision wrapper is treated as a persistence concern of the orchestrating
use case rather than a fetching concern, which bounds this refactor to completing what the diff already touched without
widening scope into the fetcher layer.

## Consequences

The change is minimal and the application boots and type-checks with no ripple into the fetcher protocol or its
implementation. The cost is that `now(UTC)` now lives in the use case, so `fetched_at` records when the use case wrapped
the graph rather than the instant the HTTP response was received — a negligible skew today but a real semantic
compromise if fetch latency ever becomes material or if multiple use cases begin persisting fetched graphs and duplicate
the stamping. Should either pressure arrive, the higher-ceiling alternative of a fetcher that returns
`EntityRevision[Graph]` remains open and would supersede this decision.
