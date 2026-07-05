# Hypothesis for property-based graph ID stability testing

## Status

Accepted

## Context

The graph ID stability invariant — that `Graph._calculate_id` produces the same UUID regardless of the iteration
order of its input node and edge sets — is not testable by a conventional parametrised test using `frozenset`
inputs. A `frozenset` is unordered by definition, so constructing two `Graph` instances from the same elements in
"different orders" is a no-op: the frozensets are identical objects and the test is trivially true whether or not
the `sorted()` call inside `_calculate_id` is present.

The invariant only has meaning when the input sequences are ordered collections. In CPython, `frozenset` iteration
order depends on object hash values, which are randomised per process via `PYTHONHASHSEED`. Without a property-based
approach, a bug introduced by removing `sorted()` from `_calculate_id` would only be detectable across different
process restarts with different seeds — not within a single test run.

The alternative considered was a manual parametrised test that passes reversed lists directly to `_calculate_id`.
This would cover two orderings (forward and reversed) but misses the other permutations and does not document the
intent as a universal property.

## Decision

Use `hypothesis` with `st.permutations` to generate all permutations of the node and edge lists and pass them
directly to `Graph._calculate_id` as ordered sequences (not frozensets), bypassing the `frozenset` layer and
exercising the `sorted()` call directly. Hypothesis selects examples systematically and records the minimal
failing case if `sorted()` is ever removed.

`_calculate_id` is accessed as a class method rather than through `Graph.__init__` because the public constructor
requires `frozenset` inputs, which would make the test trivially vacuous. Accessing a private method in a test is
acceptable here because the method encapsulates a domain-critical algorithm — stable, deterministic UUID5 derivation
— that has no other reachable surface for this specific check.

`HealthCheck.function_scoped_fixture` is suppressed because the pytest fixtures involved (`make_node`, `make_edge`)
are pure factories with no mutable state — the hypothesis warning does not apply to stateless callables.

## Consequences

- Removing or reordering the `sorted()` call in `_calculate_id` will be caught by hypothesis regardless of
  `PYTHONHASHSEED`, making the test meaningful across process restarts.
- `hypothesis` enters the dependency tree. It is a mature library with no transitive runtime dependencies relevant
  to the application and negligible overhead.
- The test accesses a private method. If `_calculate_id` is renamed or its signature changes, the test breaks
  explicitly rather than silently, which is the desired behaviour for a test that guards an internal algorithm.
- The `HealthCheck` suppression is documented at the call site; it must be re-evaluated if the fixtures ever
  acquire mutable state.
