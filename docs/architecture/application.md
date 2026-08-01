# Application — what it does

The application layer orchestrates the business workflows the product actually offers: expanding a person or company
from an official identifier into a graph of everything connected to it, ingesting free text to discover mentions of
known identifiers inside it, authenticating a user, and managing the credentials a caller needs to reach a paid external
data source. It depends only on the domain layer and on abstract contracts it defines itself — never on a concrete
database, a concrete HTTP framework, or a concrete external API client. Anything above this layer supplies a concrete
implementation of those contracts; this layer never knows or cares which one.

Every workflow that touches storage goes through a single transactional boundary that exposes every kind of stored
entity, plus credentials and users, uniformly, whether the underlying storage is an in-memory snapshot or a real
database. The moment data crosses in from an external source it gets wrapped together with when it was actually
retrieved, so provenance travels with the data itself instead of being reconstructed later; that wrapping happens at the
boundary that actually performed the fetch, not in the orchestrating workflow, so the workflow itself stays pure
sequencing with nothing to fake or freeze in a test.

Merging newly fetched data into what's already known is deliberately conservative: only content that's genuinely new or
has actually changed gets persisted, one policy decides which of two candidate versions of the same real-world subject
counts as current (by default, whichever was retrieved most recently), and a second policy decides how two versions of
the same subject get reconciled into one when both carry data worth keeping.

Text ingestion is a hard boundary by design: free text is scanned for patterns that look like an official identifier,
each candidate is validated with the same checksum rule that identifier format actually uses, and only a match against
something the system can deterministically resolve — never a fuzzy or probabilistic guess — is allowed to link into
existing data. A recognized identifier that isn't already known yet creates a minimal placeholder carrying nothing but
that identity, to be enriched later through the normal expansion workflow; a match against something already known only
ever adds a "mentioned in" relationship, and the existing record is never touched. Which set of recognition patterns
applies isn't fixed once at startup — a caller picks a pattern set per request, because different sources format the
same kind of identifier differently in free text, and locking one set in globally would mean a redeploy every time a new
source needs recognizing.

A separate, best-effort workflow runs after any expansion or ingestion produces a fresh batch of people or companies: it
compares each newly seen one's name against every person or company of the same kind already known, and where two carry
a distinct identity but a strongly similar name, it records a loose "might be the same real-world subject" relationship
alongside a similarity score — without ever touching, merging, or re-identifying either record. This is deliberately
separate from text ingestion's own resolution rule above, which stays exact-identifier-only; the two solve different
problems. An official identifier can itself be inconsistent across sources — one source may reveal only a partial,
masked form of the same identifier that another source knows in full — so the same real person or company can end up
recorded under two different identities with no shared identifier to resolve them by. Comparing names is the only signal
left in that situation, so it's kept explicitly probabilistic and advisory rather than folded into the identifier-based
resolution that everything else relies on.

## Decisions

Whether the component that receives freshly fetched data, or the workflow orchestrating the fetch, should be the one
stamping the retrieval instant was revisited once: stamping it in the orchestrating workflow was the fast, narrow fix at
the time, but it meant the timestamp recorded when the workflow got around to wrapping the data rather than the instant
it actually arrived, and it forced the workflow's own tests to freeze the clock just to assert a timestamp. Moving the
responsibility to the component that actually performs the fetch fixed both problems and left the workflow pure
orchestration again.

A transactional boundary spanning two different kinds of storage at once (an in-memory snapshot plus a real external
database) does not currently guarantee both sides succeed or fail together. This is accepted for now because no current
workflow writes to both kinds of storage in the same unit of work; the moment one does, this gap needs a real fix rather
than remaining a known, accepted edge case.

Whichever component discovers a real-world entity now always persists it individually as well as inside the bundle it
arrived in, specifically so anything else in the system can look that entity up on its own afterward. Persisting every
entity unconditionally on every merge was tried first and rejected: it caused an entity whose content hadn't actually
changed to still get re-stamped with the new retrieval's timestamp, which made the "pick whichever version is most
current" policy wrongly treat a stale re-fetch as the freshest version and silently discard the entity's true original
provenance. Checking each entity against what's already stored, and only touching what's genuinely new or changed, fixed
that.

The name-similarity workflow deliberately never merges or auto-resolves the two records it flags as possibly the same
subject; it only ever adds a new, clearly-marked "possible match" relationship carrying its similarity score, leaving
the actual judgment call to whoever reviews the graph afterward. Auto-merging on a name match alone was rejected
outright: name matching produces false positives by nature, and merging two records that turn out to be different real
people or companies is a much more damaging, harder-to-undo mistake than surfacing a match that a human has to
double-check.
