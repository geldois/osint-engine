# osint-engine

Only what no other source holds. Everything else is owned elsewhere — go there, never restate it here.

| Question                            | Source                   |
| ----------------------------------- | ------------------------ |
| Macro business flow / why, per area | `docs/architecture/*.md` |
| Setup, run, endpoints, auth, stack  | `README.md`              |
| Known deferrals, accepted debt      | `TO-DO.md`               |

## Gates

Every commit, by anyone, runs the full gate through `.githooks/pre-commit` and is refused if anything fails. So: edit,
review the docs against the change and edit those too, run `uv run python -m scripts fix` (the only tool you run
routinely), stage everything, commit — code and docs together. Never run a linter, formatter, type-checker or test
yourself, not on one file and not on the whole repo; iterate from the hook's own failure output. The hook also refuses a
dirty tree, so nothing may be left unstaged or untracked at commit time. See README.md's Quality gates section for what
it runs. Needs Docker (the Postgres persistence tests use `testcontainers`) — no `.env` is required for `check`, only
for the periodic `scripts fixtures` refresh.

Docs are the only place a decision lives: after every change, check README.md, TO-DO.md and each
`docs/architecture/*.md` against it and fix whatever no longer tells the truth, in natural language, never citing a
function, class or type name — except in `TO-DO.md`, which exists to point at code and may name files and symbols. A
stop hook asks for this review after any turn that edited a file in this repo.

The README's mermaid diagram stays brutally summarized, semantic and lean: roughly a dozen nodes naming the main flows
and stores, never one node per route, use case, class or repository. If a change needs more than a node or an edge to
appear there, it belongs in prose, not in the graph.

`TO-DO.md` is the complete, current map of what remains — every deferral, workaround, accepted limit, placeholder and
unwired piece, each with the file it lives in, the cost of leaving it and the trigger to revisit. A gap found while
working goes there in the same commit; a gap closed comes out in the same commit.

Never hand-edit `infrastructure/persistence/pg/generated/` — see README.md's Run section for how to regenerate it. A new
fetcher against a free provider needs a matching case in `scripts/fixtures.py` — a test fails the commit when its
`url_suffix` isn't referenced there.

## Code

No comments and no docstrings anywhere in this repository, ever — not `src/`, `tests/`, `scripts/`, `migrations/`,
`.githooks/`, `.claude/`, `.github/`, nor any root-level config — the name says it, or the code is wrong, or the
decision belongs in `README.md`/`TO-DO.md`/`docs/architecture/*.md`/this file. The only exceptions are linter pragmas,
shell directives, shebangs, pinned-action version tags and the SQL loader's `-- name:` lines. The gate scans every
tracked file and fails the commit on any other.
