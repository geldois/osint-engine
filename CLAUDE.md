# osint-engine

Only what no other source holds. Everything else is owned elsewhere — go there, never restate it here.

| Question                            | Source                   |
| ----------------------------------- | ------------------------ |
| What a domain term means            | `CONTEXT.md`             |
| Macro business flow / why, per area | `docs/architecture/*.md` |
| Setup, run, endpoints, auth, stack  | `README.md`              |
| Known deferrals, accepted debt      | `TO-DO.md`               |

## Gates

Never run the gate facade yourself (`scripts check`, `scripts check --full`, `scripts precommit`) — `pre-commit` already
runs the full gate on a materialized snapshot on every commit, so every commit is born green. Just commit; a failure
reported inline is the fix-and-retry signal. `.claude/hooks/block_direct_checks.py` enforces this — targeted
single-file/single-test runs stay allowed for fast local feedback. `mutation` stays periodic and manual, never a hook.
Needs Docker and a local `.env` (the runner loads it).

`scripts sqlc-generate` regenerates `infrastructure/persistence/pg/generated/` from `migrations/` and `queries/*.sql` —
run it by hand after changing either, same periodic-manual footing as `mutation`. Never run bare `sqlc generate` (leaves
an unusable generated querier file behind) and never hand-edit that directory.

## Code

No comments and no docstrings in `src/`, `tests/`, `scripts/`, `migrations/` — the name says it, or the code is wrong.
Only linter-suppression pragmas survive. `pre-commit` strips the rest.
