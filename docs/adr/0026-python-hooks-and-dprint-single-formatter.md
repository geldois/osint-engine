# Python Claude Code hooks and dprint as the single structured-doc formatter

## Status

Accepted

## Context

The self-owned gates of ADR 0025 relied on two things that aged badly. The Claude Code hooks (per-edit autofix,
direct-run enforcement, plus the global safety hooks) were bash scripts parsing the event JSON with `jq`, and markdown
was gated by a markdownlint linter whose line-length rule is not auto-fixable, forcing manual token-costing reflows.
Bash hooks are hard to debug and evolve, depend on `jq` and bashisms, and are not portable to a contributor on macOS or
Windows without WSL; markdownlint gave semantic lint but at the cost of friction, and left json/toml/yaml with no
deterministic formatter at all. Both are the kind of enforcement that must run identically on every machine, so their
implementation medium is itself an architectural choice.

## Decision

Every Claude Code hook (local `.claude/hooks/` and global `~/.claude/hooks/`) is a stdlib-only Python script invoked as
`uv run --no-project python`, sharing a small `_hook_io` helper, reading stdin via `json`, and putting marker files
under `tempfile.gettempdir()`; `jq` and inline shell in `settings.json` are gone. `uv run` resolves the pinned
interpreter cross-OS so the only dependency is `uv`, never an ambient `python`/`python3`; Python is not pinned in
`.mise.toml` because `uv` already owns it via `.python-version`. The one shell exception is a POSIX `sh` SessionStart
guard that warns when `uv` is absent — by definition it cannot itself depend on `uv`. dprint becomes the single
deterministic formatter for every hand-authored structured doc (json, toml, yaml via the pretty_yaml plugin, markdown),
replacing markdownlint; one formatter per file type, never two, with `uv.lock` excluded so formatting never breaks
`uv lock --check`. A `PreToolUse` hook blocks `code-review-graph install|init|uninstall`, which regenerate and overwrite
the committed harness.

## Consequences

Hooks are now debuggable, typed, and covered by the project's own ruff and basedpyright gates, and portable to any OS
with `uv` installed. The cost is real latency: every tool call spawns `uv run --no-project python` (tens of
milliseconds), and if `uv` leaves the PATH the Claude Code hooks silently no-op — mitigated by the loud SessionStart
guard and a `command -v uv` preflight in the git-hook shim, but not eliminated. Choosing a formatter over a linter for
markdown trades away semantic lint (fenced-code language, image alt-text) for zero-friction reflow, deliberately.
Dropping markdownlint means its config is deleted repo-wide; ADRs are now formatted by dprint like every other doc. The
crg-reinstall block protects the committed configs at the agent layer only; a human in a raw terminal is guarded instead
by version control, since everything crg can overwrite is committed and a stray `init` is one `git restore` away.
