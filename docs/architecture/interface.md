# Interface — what it does

This layer is the only one allowed to know it's serving HTTP: every route, every request/response shape, every
authentication and authorization check, and the translation from an internal error into the right HTTP status and a
consistent error body all live here. A workflow above this layer never sees a request or a response — it only ever
receives already-validated input and returns a domain result; this layer's own presenters translate that result into the
shape a caller actually receives over the wire.

Authentication is a signed, self-contained token a caller presents on every request; nothing about a valid session lives
on the server between requests, so any instance handling a request can verify it alone, with no shared state to
coordinate. There is no anonymous access and no seeded account: a caller creates their own account by choosing a
username and a password, receives a token right away, and is the only person who ever holds the provider keys saved
under that account. Every route except account creation, login and the health checks requires that token, and every
authenticated caller is allowed on all of them — what a caller can reach depends on which provider keys they saved, not
on a privilege level. A missing or invalid token fails with a distinct, clearly different status from an unmet
precondition such as a provider key that was never saved, so a caller (or whoever's debugging a failure) can tell
"you're not who you say you are" apart from "you're allowed in, but you haven't configured this yet."

Every route that could be hit by unauthenticated or lightly-authenticated traffic is rate-limited in-memory, with a flat
allowance per route that each authenticated caller spends separately (or per client address on the login and account
creation routes) — protecting each caller's own upstream quota, which is tied to their own key, and the login and signup
routes themselves from being hammered. The one route backed by a keyless upstream keeps a single bucket shared by
everyone instead, because all accounts' requests leave from this deployment's own address and per-account buckets would
let new accounts multiply the outbound rate. Every error that reaches this layer, regardless of which layer actually
raised it, is translated into one consistent response shape carrying a machine-readable error code and a correlation id,
so a caller never sees a raw stack trace or an inconsistent error format depending on which internal component failed.

Every request handler is an ordinary function whose dependencies are visible in its own signature — assembled once, by
hand, when the process starts, rather than resolved automatically per request. That keeps the wiring traceable in one
place and keeps every layer below this one completely free of any framework dependency, testable in complete isolation
from an actual running web server.

The consumption log's own routes only ever return the calling account's own entries — an entry names which CPF a
specific caller looked up and when, which is exactly the kind of data one caller must never see of another.

## Decisions

Two competing rate-limiting libraries were tried; the first, more popular one was dropped after it conflicted with this
project's own request-logging middleware and was found to depend on an already-deprecated interior call with no upstream
fix — the replacement is far less battle-tested but has no such conflict and needed no workarounds to satisfy strict
type-checking.

Roles were removed along with the seeded operator account and the credential-free visitor token. They existed to keep a
public demo caller away from routes that spent the operator's shared provider key; once every caller spends only their
own key there is nothing left for a role to protect, and keeping a privilege level with no distinct power would have
been complexity without a purpose. Self-service signup is open to anyone, bounded only by a per-address rate limit and
by the password-hashing cost; a registration code was weighed and left out as one more secret to manage, and is the
first thing to add if signup abuse ever shows up.

A response now carries when its data was observed and where it came from, rather than only the data itself. The
information had always been recorded when a fetch happened and had always been used internally to decide which
observation counted as current, but the layer that shapes a response stripped it out before anything left the process —
so a caller receiving several observations of the same entity had no way to tell them apart or order them. The
provenance travels nested under one named object rather than smeared as loose fields across every entity in the payload,
because the concept already had a name of its own and repeating four unrelated-looking keys on two dozen entity shapes
would have obscured it on both sides of the wire.

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

Any future route added to this layer inherits the same authentication check automatically, rather than needing its own
hand-rolled check — a new workflow only has to be mounted behind the same token check, not reimplement how that gets
enforced.

Publishing the content-derived identifier commits this layer to deriving it the same deterministic way indefinitely: a
caller may already depend on two fetches of unchanged content producing the same value, so changing how that identifier
is computed later is a breaking change for any such caller, not an internal refactor.

Because provenance is repeated on every entity inside a response rather than stated once for the whole payload, the
response grows by one small, fixed set of fields per entity — accepted since stating it once stops working the moment a
caller merges several responses into one accumulated view and needs to tell which part came from which fetch.

A future read-time step that adds its own cross-entity links has to follow the same rule the existing one does — rebuild
the provenance wrapper around whatever it actually returns — or the content-derived identifier in that response would
describe something other than what the caller actually received.
