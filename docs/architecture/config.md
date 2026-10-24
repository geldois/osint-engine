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

The architecture-direction check places this layer above infrastructure, so its one edge into infrastructure — wiring a
concrete implementation — is allowed by that order, with no exception written anywhere. A composition root has to import
the concrete implementations it assembles; a second rule keeps the interface from importing infrastructure directly and
lets it reach it only through this layer, so the real interface-to-infrastructure direction stays enforced everywhere
else in the codebase.

## Consequences

Every future dependency this layer wires becomes one more explicit line in the same one place, never a second resolution
mechanism competing with it — the wiring stays traceable exactly because nothing is ever allowed to resolve itself
outside it, no matter how small.

Having already routed one stateless, single-implementation capability through this layer sets the precedent for the next
one that looks just as harmless: it goes through wiring too, keeping the same one-place guarantee rather than
accumulating quiet, case-by-case exceptions that each seemed small on their own.

What allows this layer's edge into infrastructure is its place in the layer order, not an exception — a future concrete
implementation this layer wires in is imported directly from here and stays allowed by the same order, but nothing else
in the codebase inherits it: the interface still cannot reach infrastructure except through this layer, and a
similar-looking edge opened anywhere else still fails the check.
