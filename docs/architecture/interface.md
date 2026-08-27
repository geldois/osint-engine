# Interface — what it does

This layer is the only one allowed to know it's serving HTTP: every route, every request/response shape, every
authentication and authorization check, and the translation from an internal error into the right HTTP status and a
consistent error body all live here. A workflow above this layer never sees a request or a response — it only ever
receives already-validated input and returns a domain result; this layer's own presenters translate that result into the
shape a caller actually receives over the wire.

Authentication is a signed, self-contained token a caller presents on every request; nothing about a valid session lives
on the server between requests, so any instance handling a request can verify it alone, with no shared state to
coordinate. A second, separate check — layered on top of authentication, not merged into it — decides whether the
authenticated caller's role permits the specific route being called at all; some routes are open to a public,
credential-free caller for read-only access, while any route that changes data stays restricted to a privileged caller
only. Both checks fail with a distinct, clearly different status so a caller (or whoever's debugging a failure) can tell
"you're not who you say you are" apart from "you're allowed in, but not to this."

Every route that could be hit by unauthenticated or lightly-authenticated traffic is rate-limited in-memory, with a
different allowance for a privileged caller versus a public one on the very same route — protecting both a paid upstream
quota and the login route itself from being hammered. Every error that reaches this layer, regardless of which layer
actually raised it, is translated into one consistent response shape carrying a machine-readable error code and a
correlation id, so a caller never sees a raw stack trace or an inconsistent error format depending on which internal
component failed.

Every request handler is an ordinary function whose dependencies are visible in its own signature — assembled once, by
hand, when the process starts, rather than resolved automatically per request. That keeps the wiring traceable in one
place and keeps every layer below this one completely free of any framework dependency, testable in complete isolation
from an actual running web server.

The consumption log's own routes are restricted to the privileged role, the same guard the paid CPF route itself uses,
rather than the plain-authenticated guard most read routes accept — an entry names which CPF a specific caller looked up
and when, which is exactly the kind of data the rest of this layer treats as sensitive enough to gate.

## Decisions

Two competing rate-limiting libraries were tried; the first, more popular one was dropped after it conflicted with this
project's own request-logging middleware and was found to depend on an already-deprecated interior call with no upstream
fix — the replacement is far less battle-tested but has no such conflict and needed no workarounds to satisfy strict
type-checking.

Authorization deliberately lives beside authentication as its own dedicated check at this layer rather than inside each
individual workflow, keeping "is this caller who they claim to be" and "is this caller allowed to do this" as pure
interface-layer concerns instead of scattering the same role logic across every workflow that happens to need it.

A response now carries when its data was observed and where it came from, rather than only the data itself. The
information had always been recorded when a fetch happened and had always been used internally to decide which
observation counted as current, but the layer that shapes a response stripped it out before anything left the process —
so a caller receiving several observations of the same entity had no way to tell them apart or order them. The
provenance travels nested under one named object rather than smeared as loose fields across every entity in the payload,
because the concept already had a name in the project's own vocabulary and repeating four unrelated-looking keys on two
dozen entity shapes would have obscured it on both sides of the wire.

The identifier derived from an entity's complete content is now published beside the one derived only from its identity
fields. That exposes a piece of the internal identity model to callers, which was weighed and accepted: it is precisely
the key a caller needs to recognise that two observations of the same entity differ, or that two separate fetches
produced identical content, and it is derived deterministically rather than assigned, so it commits nothing that could
later shift underneath a caller.

Within a single response the same provenance is repeated on the graph and on every entity inside it, which is redundant
when read alone and stops being redundant the moment a caller accumulates several responses into one view — the point at
which knowing which fetch each part arrived from is the only thing that makes the accumulated view interpretable.

A handler that augments a graph after the workflow returns — attaching advisory cross-entity links computed at read time
— rebuilds the provenance wrapper around the augmented result rather than reporting the stored one, so the
content-derived identifier in a response always describes what that response actually contains.

## Consequences

Any future route added to this layer inherits the same authentication/authorization split automatically, rather than
needing its own hand-rolled check — a new workflow only has to declare which role may call it, not reimplement how that
gets enforced.

Publishing the content-derived identifier commits this layer to deriving it the same deterministic way indefinitely: a
caller may already depend on two fetches of unchanged content producing the same value, so changing how that identifier
is computed later is a breaking change for any such caller, not an internal refactor.

Because provenance is repeated on every entity inside a response rather than stated once for the whole payload, the
response grows by one small, fixed set of fields per entity — accepted since stating it once stops working the moment a
caller merges several responses into one accumulated view and needs to tell which part came from which fetch.

A future read-time step that adds its own cross-entity links has to follow the same rule the existing one does — rebuild
the provenance wrapper around whatever it actually returns — or the content-derived identifier in that response would
describe something other than what the caller actually received.
