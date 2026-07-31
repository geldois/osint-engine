# osint-engine — Claude Code guidance

This file holds only what no other source does. Everything else is owned elsewhere — go there, never restate it here.

## Sources of truth

| Question                                                   | Source (use it, don't re-derive)                                        |
| ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| Structure, callers/callees, impact, tests-for, dead code   | the code-review-graph (query it — never grep/read-around to rebuild it) |
| A decision and its rationale ("why is it done this way?")  | `docs/adr/` (numbered ADRs)                                             |
| Setup, run, endpoints, API auth, stack, architecture prose | `README.md`                                                             |
| Known deferrals / accepted tech debt                       | `TO-DO.md`                                                              |

If an answer is in one of those, read it there. Only the operational rules below live here.

## Code-review-graph

Graph-first: consult it before `Grep`/`Glob`/`Explore` (a `PreToolUse` hook enforces this until the graph is queried
once this turn; `Read` is never gated). Key tools: `query_graph_tool` (callers/callees/imports/`tests_for`),
`semantic_search_nodes_tool`, `get_impact_radius_tool`, `detect_changes_tool`, `get_architecture_overview_tool`,
`refactor_tool` (renames, dead code). If it is stale or missing something, repair it (`code-review-graph update` /
`build`) — never fall back to grep for something the graph should model.

Never run `code-review-graph install`, `init`, or `uninstall`: they overwrite the committed, hand-tuned harness
(`.claude/`, `.mcp.json`, this file, the git hooks) and litter per-tool configs. A `PreToolUse` hook blocks them. Only
data commands are allowed — `build` (first build after clone), `update`, `serve` (what `.mcp.json` runs), `status`. If a
config was clobbered, `git restore` it — everything crg can overwrite is version-controlled.

## Quality gates

One façade: `uv run python -m scripts check` (fast) or `check --full` (adds pytest + branch coverage). A `PreToolUse`
hook blocks raw full-suite runs (`pytest`, `ruff`, `basedpyright`, `lint-imports`, `sqruff`, `cosmic-ray`) and redirects
here; a targeted single-file or single-test run is allowed. The same hook also blocks the agent from invoking
`check --full` directly — `pre-commit` already runs it on a materialized snapshot and reports failure inline, so just
commit; a failed commit is the fix-and-retry signal, not a reason to pre-run the gate by hand. Committing runs the full
gate on a materialized snapshot, so it needs Docker (testcontainers) and a local `.env` with the Portal key (the runner
loads it — no manual sourcing). Mutation: `uv run python -m scripts mutation`.
