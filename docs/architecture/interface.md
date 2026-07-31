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

## Decisions

Two competing rate-limiting libraries were tried; the first, more popular one was dropped after it conflicted with this
project's own request-logging middleware and was found to depend on an already-deprecated interior call with no upstream
fix — the replacement is far less battle-tested but has no such conflict and needed no workarounds to satisfy strict
type-checking.

Authorization deliberately lives beside authentication as its own dedicated check at this layer rather than inside each
individual workflow, keeping "is this caller who they claim to be" and "is this caller allowed to do this" as pure
interface-layer concerns instead of scattering the same role logic across every workflow that happens to need it.
