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
reported inline is the fix-and-retry signal. `.claude/hooks/block_direct_checks.py` nudges toward this rather than
blocking the call — targeted single-file/single-test runs stay allowed for fast local feedback. `mutation` stays
periodic and manual, never a hook. Needs Docker and a local `.env` (the runner loads it).

`scripts sqlc-generate` regenerates `infrastructure/persistence/pg/generated/` from `migrations/` and `queries/*.sql` —
run it by hand after changing either, same periodic-manual footing as `mutation`. Never run bare `sqlc generate` (leaves
an unusable generated querier file behind) and never hand-edit that directory.

A new fetcher against a free provider (KipFlow is paid, excluded on purpose) needs a matching case in
`scripts/fixtures.py` — `.claude/hooks/report_fixtures_coverage.py` nudges when its `url_suffix` isn't referenced there.

## Code

No comments and no docstrings anywhere in this repository, ever — not `src/`, `tests/`, `scripts/`, `migrations/`, not
`.claude/hooks/`, `.github/`, nor any root-level config — the name says it, or the code is wrong, or the decision
belongs in `README.md`/`TO-DO.md`/`docs/architecture/*.md`/this file/`CONTEXT.md`. Nothing strips one automatically:
writing it is the mistake, not leaving it in the file. `.claude/hooks/report_comments.py` nudges on any one introduced
this turn, or already sitting in a file just read, outside an allowlisted linter-suppression pragma.
