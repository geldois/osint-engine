# Config — what it does

This is the composition root — the one place, assembled once when the process starts, that decides which concrete
implementation satisfies each contract the layers above depend on: which persistence backend, which password hasher,
which token service, which provider adapters. Everything is wired together by hand into a single, frozen, explicit
structure passed down to whatever needs it; there is no automatic discovery and no hidden resolution order to reason
about — every wiring decision is visible in one place. Runtime configuration values (which secrets, which external
endpoints, which timeouts) are read once from the environment at startup and validated into a typed structure before
anything else in the process touches them.

## Decisions

A popular web framework's own built-in mechanism for resolving a request's dependencies automatically was considered for
wiring the whole application, and deliberately scoped down instead to only the narrow, framework-specific concerns at
the interface layer (reading form data, applying an authentication check to a route) — assembling everything else by
hand keeps every layer below the interface completely framework-free and keeps the wiring graph traceable in a single
place instead of resolved implicitly at request time.

Whether a pure, stateless capability ever justifies bypassing this wiring was tested once: reading an uploaded file's
raw bytes into text has exactly one implementation and no state to inject, so letting the interface-layer handler that
needs it import it directly looked harmless. It was routed through here instead, exposed the same way a real technical
capability is, because the value of assembling every dependency in one traceable place holds regardless of whether a
given dependency happens to have alternatives today — the moment one caller is allowed to reach past this layer because
"there's nothing to inject," every future caller with the same argument has precedent to do the same, and the one wiring
graph stops being complete.
