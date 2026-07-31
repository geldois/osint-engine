# Tests — what it does

The test suite mirrors the same layered structure the source code itself follows, so a test's location signals which
layer's contract it's actually validating. Layers that depend on nothing external (business rules, orchestration logic)
are exercised in complete isolation using lightweight hand-written stand-ins for their dependencies rather than a
mocking framework, kept in one shared location so the same stand-in isn't reimplemented per test file. A boundary that
actually depends on something external — a real database, in particular — is instead exercised against a real,
disposable instance of that same technology spun up just for the test run, because a stand-in could never have caught
certain classes of bug a real engine would, and one such bug did, in fact, previously slip past a stand-in undetected.

One invariant — that an aggregate's computed identity does not depend on the order its parts happen to be provided in —
cannot be verified by an ordinary example-based test at all, because the collection type the invariant concerns is
inherently unordered by definition; two "differently ordered" inputs built from an unordered collection are simply the
same object, so a test that only sees ordered inputs some other way would exercise a coincidence, not the actual
guarantee. A property-based approach that generates and tries every ordering systematically is the only way this
specific invariant can be verified at all, and it lives specifically at the one internal calculation the invariant is
actually about, deliberately bypassing the aggregate's own public entry point since that public path only ever accepts
the unordered collection the property needs to route around.

## Decisions

Faking the database-backed persistence boundary the same way every other test double is built elsewhere in the suite was
tried and abandoned: a fake can only ever be as correct as its author's own assumptions about how the real engine
behaves, and a real, if disposable, instance of the actual engine is the only thing that can catch a genuine query or
encryption defect — which one already had, going undetected under a fake until the real-engine layer was introduced.
