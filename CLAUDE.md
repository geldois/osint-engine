# osint-engine

Only what no other source holds. Everything else is owned elsewhere — go there, never restate it here.

| Question                                            | Source                   |
| --------------------------------------------------- | ------------------------ |
| Macro business flow / why / open problems, per area | `docs/architecture/*.md` |
| Setup, run, endpoints, auth, stack                  | `README.md`              |

## Gates

Every commit, by anyone, runs the full gate through `.githooks/pre-commit` and is refused if anything fails. So: edit,
review the docs against the change and edit those too, run `uv run python -m scripts fix` (the only tool you run
routinely), stage everything, commit — code and docs together. Any other linter, formatter, type-checker or test tool
(ruff, basedpyright, pytest and the rest) runs only when the user explicitly asks for it or allows it in that message,
never on your own initiative. `scripts check` and `scripts comments` are run only by the pre-commit hook and CI, never
by you, even if asked. The hook also refuses a dirty tree, so nothing may be left unstaged or untracked at commit time.
See README.md's Quality gates section for what it runs. Needs Docker (the Postgres persistence tests use
`testcontainers`) — no `.env` is required for `check`, only for the periodic `scripts fixtures` refresh.

Docs describe the repo exactly as it is and are the only place a decision lives. Mandatory before every commit: after
the last edit of the turn, investigate every doc, not merely read it: `README.md` and each `docs/architecture/*.md`,
Open problems sections included, and the sibling osint-studio repo's docs if the shared contract moved. For every claim
a doc makes (command, path, version, count, route, variable, behaviour, limit, rationale) search the code, config and
workflows to confirm it still holds, and correct or delete whatever is wrong, outdated or deprecated, including what
this change made stale without adding anything: remove each open problem the change resolved, purge every mention of
anything removed, recount counts and lists, delete diagram nodes for things that are gone. A doc left unchanged must be
one you verified. The investigation happens at the moment of each doc write, in the same step as the edit: read the code
the sentence describes right then, never from an earlier reading in the turn, because the tree changes under you. That
holds for a new Open problems entry as much as for any other claim: confirm the problem still exists immediately before
writing it down. The commit carries code and docs together. What is left to fix lives only in the `## Open problems`
section of the owning `docs/architecture/*.md`; that section alone may name files and symbols, the rest of
`docs/architecture/` never does, and a fact lives in one document only: a limit accepted by design is a Consequence,
never also an open problem. Those documents are written in natural language, never citing a function, class or type
name. The README names only what a person touches, such as commands, files, endpoints, response schemas and variables,
and points at the owner of any value a config or a fixture already holds, never repeating it.

Anything that needs fixing is tracked, always, and never left to be rediscovered: any bug, accidental behaviour (what
nobody chose), missing test coverage or lost intent found anywhere in the code, off the main flow or not, at any moment
and whatever its size, is written into the owning document's `## Open problems` the same turn it is seen, without being
asked. Finding it again later always costs more than recording it now. Only drift in the docs themselves outranks that:
it is never postponed, it is fixed in the same change.

The README's mermaid diagram stays brutally summarized, semantic and lean: roughly a dozen nodes naming the main flows
and stores, never one node per route, use case, class or repository. If a change needs more than a node or an edge to
appear there, it belongs in prose, not in the graph.

Never hand-edit `infrastructure/persistence/pg/generated/` — see README.md's Run section for how to regenerate it. A new
fetcher against a free provider needs a matching case in `scripts/fixtures.py` — a test fails the commit when its
`url_suffix` isn't referenced there.

## Tests

Every behaviour of this codebase is pinned by a regression test, and a change is not done while one remains: each
success path, each failure branch, the order of validations, the winner when two versions collide, the order of a paired
argument, and what a call must not touch. The coverage floor is a floor, never the goal. Every bug, drift or unintended
behaviour, once corrected, lands in the same change with a regression test that fails without the fix and is named for
the invariant it protects; an unintended behaviour kept on purpose is pinned as the decision. A missing or loose test
found anywhere is written in the same change, and recorded in the owning `## Open problems` only when it cannot be
written yet (a paid key, a design that is still undecided).

Pinning pays most where a wrong result is silent or costly: identity against content, where a test asserts the value
that measures what an entity holds and not only the one equality compares, with test entities whose two differ; whatever
spends money or cannot be undone, where a test proves it does not happen when it must not; and every boundary the system
crosses, read back through its public seam and never through an internal representation.

## Code

No comments and no docstrings anywhere in this repository, ever — not `src/`, `tests/`, `scripts/`, `migrations/`,
`.githooks/`, `.claude/`, `.github/`, nor any root-level config — the name says it, or the code is wrong, or the
decision belongs in `README.md`/`docs/architecture/*.md`/this file. The only exceptions are linter pragmas, shell
directives, shebangs, pinned-action version tags and the SQL loader's `-- name:` lines. The gate scans every tracked
file except generated code, JSON, Markdown, the lockfile, the licence and the interpreter version file, and fails the
commit on any other.
