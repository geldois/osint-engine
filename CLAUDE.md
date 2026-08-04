# osint-engine

Only what no other source holds. Everything else is owned elsewhere — go there, never restate it here.

| Question                            | Source                   |
| ----------------------------------- | ------------------------ |
| Macro business flow / why, per area | `docs/architecture/*.md` |
| Setup, run, endpoints, auth, stack  | `README.md`              |
| Known deferrals, accepted debt      | `TO-DO.md`               |

## Gates

`uv run python -m scripts check` (fast) or `mutation`. `pre-commit` runs the full gate on a materialized snapshot, so
every commit is born green — just commit; a failure is the fix-and-retry signal. Needs Docker and a local `.env` (the
runner loads it).

## Code

No comments and no docstrings in `src/`, `tests/`, `scripts/`, `migrations/` — the name says it, or the code is wrong.
Only linter-suppression pragmas survive. `pre-commit` strips the rest.
