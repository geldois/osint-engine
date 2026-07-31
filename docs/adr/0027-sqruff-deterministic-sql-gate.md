# sqruff as the deterministic SQL gate

## Status

Accepted

## Context

The repository has hand-authored SQL that no gate covered: the `gomigrate` up/down migrations and the raw parameterised
query files under `infrastructure/persistence/pg/queries`. Every other hand-authored structured document (json, toml,
yaml, markdown) is held to a deterministic, idempotent formatter by ADR 0026, but SQL was left to manual discipline, so
drift in spacing, keyword case, and layout could land uncaught and a reviewer paid the attention cost. The two realistic
tools are sqlfluff (Python, the incumbent) and sqruff (Rust, sqlfluff-compatible dialects and rules), and the raw query
files use `:name` colon-placeholder bind parameters, which a naive SQL parser reads as the colon operator and floods
with spurious spacing diagnostics.

## Decision

sqruff is added as the SQL linter/formatter, pinned via mise (`aqua:quarylabs/sqruff`) so it is provisioned identically
in every environment under the no-skip policy, and wired into the same three places as every other gate tool: a no-venv
`sqruff lint` gate that runs before env-sync (SQL needs no virtualenv), a per-edit autofix branch that runs `sqruff fix`
then injects only the residual `sqruff lint`, and the direct-run blocker so a bare full-tree `sqruff` run redirects to
the façade while a single-file run stays allowed. It is chosen over sqlfluff for the Rust-over-Python leaning (faster,
no interpreter, one dependency). The config in `.sqruff` sets `dialect = postgres` and, critically,
`templater = placeholder` with `param_style = colon` so the `:name` bind parameters in the query files are understood as
parameters rather than mis-parsed as operators; the default `raw` templater produced dozens of false LT01 spacing errors
on exactly those lines.

## Consequences

SQL now carries the same born-green guarantee as the rest of the tree, at essentially zero marginal token cost since the
per-edit hook fixes it silently. The cost is another pinned tool in the provisioning surface (mise must resolve the aqua
package in CI as well as locally, and its absence fails the gate rather than skipping), and a config coupling that is
easy to forget: the placeholder templater is correct only while the queries use colon-style parameters — a driver change
to `$1` positional or `%(name)s` styles would need `param_style` updated in lockstep or the linter would regress to
false positives. sqruff is younger than sqlfluff, so a rule or dialect gap would surface as a missed lint rather than a
wrong one, an acceptable failure mode for a formatter whose job is layout determinism, not deep semantic analysis.
