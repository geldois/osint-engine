# Surface gate-failure detail on every channel

## Status

Accepted

## Context

ADR 0025's two-channel output kept the piped verdict to a single line — naming the failing gates and pointing at
`build/reports/gates.json` — on the premise that a machine consumer (CI, a subagent) would read the structured report
rather than have raw tool output dumped into its stream. In practice the dominant machine consumer is the agent driving
commits through a captured, non-TTY shell: on a failed pre-commit it received only the one-line verdict and then had to
open and parse `gates.json` by hand to see what broke. That manual JSON read is exactly the per-token cost the harness
exists to remove, and it recurred on every red commit. The considered alternative — a cheap dedicated agent that reads
the report and summarizes the failures — was rejected: it is an LLM indirection over a known, fixed JSON schema that a
deterministic printer already in the runner can emit for free, so it would add context and latency to obviate a cost the
runner should never have imposed.

## Decision

On failure the verdict line is now followed by each failing gate's own output, inline, on every channel including a pipe
— trimmed of runner noise (the `uv` `VIRTUAL_ENV` warning, blank edges) and tail-capped at a fixed line count so a long
pytest traceback cannot flood the committer's context. A green run is unchanged: one quiet line, so CI stays silent on
success and the live ticker still collapses to a single static line while gates run. `gates.json` is still always
written with the complete untrimmed per-gate record for any genuinely programmatic use. No report-reading agent is
introduced.

## Consequences

Whoever triggers a commit — a developer at a terminal or the agent through a captured shell — sees the actionable
failure directly and never reads the raw report or spawns a summarizer, which is the whole point. The cost is that a
failing piped run is no longer a single line: CI failure logs and captured agent output now carry the trimmed gate
output, which is a deliberate trade since a failing run is already something a human will read, and the tail-cap bounds
the volume. The trimming is heuristic — the `VIRTUAL_ENV` filter and the line cap are tuned to the current toolchain, so
a future tool with a different noise signature or a failure whose signal sits above the tail window would need the
`_actionable` helper adjusted; the untrimmed report remains the escape hatch when the inline slice is not enough.
