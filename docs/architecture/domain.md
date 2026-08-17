# Domain — what it does

The domain layer defines what a real-world entity is (a company, a person, an address, a phone, an email, a CNAE
classification, a sanction, a piece of ingested text) and how two entities relate to each other. Every entity's identity
is derived deterministically from its own content — the same real-world thing, described the same way, always produces
the same identifier, regardless of when or where it was constructed. Deduplication and idempotent re-processing follow
automatically: fetching the same subject twice never creates two competing records for the same real thing.

An entity refuses to exist in an invalid state. If a concrete type is missing something the base abstraction requires —
a namespace, a properly typed identifier — the mistake is caught the moment the class itself is defined, not the first
time someone tries to use it. The same fail-fast posture extends to relationships between entities: a relationship
connecting an entity to itself is rejected outright, and a graph containing a relationship that points at an entity the
graph doesn't actually hold is rejected too, both at the moment of construction, not later when something happens to
touch the bad data.

Identity is computed from only the fields that make an entity the entity it is, not from every attribute it happens to
carry. That separation matters because entities grow richer over time — new descriptive fields get added — without ever
changing what identity means for an already-existing kind of entity. A few identifying fields (a tax ID, a national ID
number) are normalized before identity is computed, so punctuation and formatting differences never split one real-world
subject into two identities. When such a field arrives partially hidden, the position of the hidden portion is part of
that identity, not just which digits are visible — two partially hidden values that happen to reveal the same digits in
different positions are treated as two different subjects, because nothing yet confirms they're the same one. The
original, unnormalized value the caller supplied is preserved untouched for display regardless.

Relationships between entities are modeled as their own first-class, strongly typed concept — one dedicated type per
kind of relationship (ownership, residency, membership, mention-in-text, sanction, and so on) rather than a single
generic connector, even where two relationships look structurally identical. Typing carries all the way down to which
kind of entity may sit on each end of a relationship, so connecting the wrong kinds of things together is caught before
the program ever runs, not discovered later as a data bug. Every module in this layer is free of any dependency on
frameworks, persistence technology, or transport concerns; it can be exercised in complete isolation.

## Decisions

An early attempt leaned on a generic, framework-provided base for entities to get equality and construction machinery
for free; it was abandoned because it could not fail fast the moment a concrete type broke the contract — a violation
only surfaced the first time an instance was actually built. A hand-written base with fail-fast validation replaced it
for exactly that reason.

Making one relationship generic across two entity kinds that happen to need the same shape (ownership by an individual
versus ownership by another entity) was considered and rejected: every other relationship in this layer already exists
as its own dedicated type, and a generic exception here would break that consistency rather than simplify it — the
accepted cost is a bit of repeated shape between the two, not a shared abstraction.

Normalizing an identifying field is decided individually, case by case, right where identity for that kind of entity is
computed, deliberately not centralized into one universal rule — at least one identifying-looking field genuinely cannot
be normalized the same way, since it can legitimately hold non-numeric content that a universal rule would silently
corrupt.

Collapsing a partially hidden identifying field down to just its visible digits, discarding where they sit, was
considered and rejected: two different real-world subjects can reveal the same digits by coincidence in different
positions, and merging their identities on that basis has no real grounding. The accepted cost is that two genuinely
identical subjects, hidden differently by different sources, are no longer recognized as the same one automatically —
relinking them is a deliberate, separate concern, not folded into identity.

A composite entity — one built from other entities — was found to have silently collapsed its own stable identity and
its content-derived id into the same value: every one of its own fields is also part of what makes it the composite it
is, leaving no attribute of its own to carry an "exact content" signal, and its calculation only ever consulted each
constituent's stable identity, never that constituent's own content. Two revisions built from the same constituents but
differing only in one constituent's non-identifying content — the common case being the same person re-fetched with a
different observed name — computed to the identical id, so a store keeping revisions by content id silently discarded
the older one instead of stacking both, undermining the very "distinct, stacked revisions" guarantee Application's
history relies on. The fix makes the composite's content-id derive from its constituents' own content-ids while its
stable identity keeps deriving from their identities alone, restoring the same separation every other entity already
has, one level removed.
