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

One test file loads its target module by file path rather than importing it normally: that module lives under a
dot-directory the test runner's own default configuration never collects into the project's package tree, and the module
it tests only ever runs standalone, never as part of this project's own tooling package.

A free provider's mapper is additionally checked against one real, live API response per source, on top of the
hand-crafted cases that already cover field mapping, null handling and graph shape — a stand-in built from a developer's
own understanding of the response can't catch that understanding drifting from what the source actually sends. That
check moved out of the ordinary suite and into the same periodic-manual footing already used for mutation testing:
running it on every commit means a source going temporarily empty or a hardcoded test id's own record aging out —
neither a defect in this codebase — fails CI for a change that never touched the provider at all, which happened twice
in one session. The hand-crafted cases stay in the ordinary suite; only the live-snapshot check moved.

Detecting a container runtime for the real-database layer is deliberately strict, not permissive: the client this layer
speaks to understands only the Docker API socket, never a CLI shim, so an installed alternative runtime exposed only
through a `docker`-named wrapper reads as no runtime at all and would otherwise silently skip every test that needs one.
An explicit runtime location is honored first, then a real Docker socket, then a known alternative-runtime socket
location — and failing to find any of those is left to raise on its own rather than becoming a caught, silent skip,
since a missing runtime is a documented setup requirement, not an optional path.

## Consequences

A test's own location keeps announcing which layer's contract it actually validates as the suite grows, so a future
contributor placing a new test can tell where it belongs from the existing structure alone, without needing this
document to explain it case by case.

Because the one property-based test bypasses the aggregate's own public entry point on purpose, a future change to that
public path doesn't automatically re-exercise the ordering invariant the property test protects — the internal
calculation it targets has to be kept in view separately, since the usual habit of only testing the public surface would
silently stop covering it.

The strict runtime-detection rule means a future environment running some other container tool entirely, under some
other socket location this check doesn't yet know about, fails loudly with a raised error rather than quietly skipping
every test that needs a real database — closing that gap for a new environment means teaching this one check about it,
not adding another skip somewhere else.
