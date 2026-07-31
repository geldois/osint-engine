# Self-owned deterministic quality gates via a dev runner

## Status

Accepted

## Context

Quality tooling was installed but never enforced as a gate: `.pre-commit-config.yaml` ran only hygiene hooks
(large-files, merge-conflict, no-commit-to-main), and CI ran `pytest --cov` and uploaded the XML without failing on
lint, type, coverage, or architecture violations. `ruff select=ALL` and `basedpyright --strict` were configured but
non-binding decoration. No architecture check existed despite the project's central thesis being Clean Architecture with
a swappable persistence backend, so the layer-dependency direction was verified by trust, not by a script. The README
claimed "mutation testing" while `mutmut` was not even a dependency — a falsifiable public claim. Large diffs committed
in one pass had no guarantee that each commit was independently integral (lockfile in sync, tests passing, hygiene
clean), leaving per-commit integrity to discipline rather than mechanism. The goal is the Uncle-Bob delegation model:
deterministic gates running outside the LLM loop, so trust comes from scripts, not from reading every diff.

## Decision

A dev runner — a Typer app living outside `src/osint_engine/`, invoked as `uv run python -m scripts <cmd>` — becomes the
single source of truth for every gate, called identically by git hooks and CI so no gate definition is duplicated. Its
subcommands are siblings, not nested under `gates`: `check` (fast gates only), `check --full` (fast + full pytest
suite + branch coverage), `mutation` (cosmic-ray, periodic, never in a hook), `fixtures refresh` (regenerates golden
snapshots, extracted out of the product CLI), and `hooks install` (writes git hooks; fails without `.git`; idempotent).
`fixtures` is maintenance, not a pass/fail gate, so `check` never invokes it.

`cosmic-ray==8.4.6` is the mutation tool over `mutmut`: mutmut 3.x reaches its speed by copying mutants into a directory
and re-importing them, which collides with import-machinery-touching libraries (pytest plugins, strict asyncio,
testcontainers) — a problem previously hit in this project. cosmic-ray isolates each mutant in a subprocess via
declarative config and its own session db, trading raw speed for the integrity and reproducibility that matter for a
periodic job. `import-linter==2.13` enforces the layer contract `domain < application < infrastructure < interface` as
the deterministic arch-check, sub-second. The `pre-commit` framework is removed entirely: its only non-trivial service —
running gates against the exact staged snapshot despite partial staging — is dissolved by materializing the git index
into an isolated, freshly-synced snapshot and running the gates there, the same ephemeral-worktree family of primitive
that isolates the mutation run. `uv lock --check` and `dprint check` (a deterministic, idempotent markdown formatter,
via `mise`, over the opt-in canonical-docs allowlist in `dprint.json`) become gates so a commit that changes a
dependency without the lockfile, or leaves a canonical doc unformatted, fails. A required tool that is absent fails its
gate rather than being skipped, so every environment — dev and CI alike — must be correctly provisioned before any
commit can pass.

Integrity is enforced at the hook layer so no commit is born or published broken without relying on discipline.
`pre-commit` and `pre-merge-commit` both run `check --staged --full` on the materialized snapshot — the full suite with
branch coverage, not the fast subset — so every commit and every local merge is born full-green. Because each commit is
already validated in full at creation time, a separate `pre-push` replay of history (an earlier `verify-history` design)
is redundant and is not installed; the remote CI `pull_request` run is the second merge gate, and the local
`pre-merge-commit` covers merges made outside a PR. Output is two channels driven by the consumer: the terminal (a git
hook's stdout, human-facing) shows a single liveness ticker while gates run, then one verdict line — on failure it names
the failing gate(s) and points at the report, never the raw tool output; `build/reports/gates.json` (gitignored) is
always written with the complete structured per-gate record, read by tooling instead of re-running and re-parsing each
tool.

## Consequences

- The `pre-commit` framework dependency leaves the repo; the project now owns the ephemeral-worktree primitive
  (materialize index/tree, run gates, clean up on failure) — a small, testable amount of code traded for zero external
  framework and full control, aligned with the self-owned-harness philosophy.
- `refresh-fixtures` is removed from the product `osint_engine` CLI and moves to `python -m scripts fixtures refresh`;
  the CI `Refresh test fixtures` step and any caller must be updated, and the production wheel (`hatch build`) must
  exclude `scripts/` and all dev entrypoints so no dev tooling ships to end users.
- Running `check --staged --full` at pre-commit makes every commit expensive: the full suite spins a real Postgres via
  testcontainers and needs `PORTAL_TRANSPARENCIA_API_KEY` plus regenerated fixtures, so a commit cannot be made in an
  environment that cannot pass the full suite. This is the deliberate cost of born-full-green integrity; the escape
  hatch is an explicit `--no-verify` for a bootstrap commit, not a weaker default gate.
- A missing required tool fails its gate instead of skipping, which means CI must provision every gate's tooling —
  `mise` is added to `test.yml` so `dprint` (pinned in `.mise.toml`) is present; a forked PR without secrets still fails
  the tool-dependent gates rather than silently passing them.
- Coverage floor and mutation-score floor are left unpinned pending a measured baseline; the recommended policy is floor
  = current baseline, ratcheting upward only, so the gate never blocks on a number the suite cannot already meet.
- CI `test.yml` changes from running `pytest` directly to calling `python -m scripts check --full`, so lint, type,
  architecture, and coverage failures block the same way tests do; mutation runs as a separate periodic job.
- The README's mutation-testing claim must be corrected or made true once cosmic-ray is wired; until then the public
  claim stays falsifiable.
- Retroactively cleaning `ship-code`, agents, and skills that run these steps by hand is deferred to a `harness-auditor`
  pass after implementation, triggered only with explicit permission.
