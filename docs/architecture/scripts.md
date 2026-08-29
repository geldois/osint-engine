# Scripts — what it does

This is the project's own developer-facing tooling — the quality gate runner and one-off maintenance commands — kept
entirely separate from the product itself so none of it ships in the deployed application. One command runs the fast set
of checks (formatting, linting, import-direction, static typing); a slower variant adds the full automated test suite
with coverage measurement. A completely separate, periodic command deliberately introduces small mutations into the
codebase and confirms the test suite actually catches them, as a check on the tests' own effectiveness rather than just
their pass/fail status — this one is never run as part of an ordinary commit, only on demand.

Every commit and every local merge is validated in full, automatically, against the real working tree exactly as it sits
at that moment, whole repo, not a staged-only slice of it — so nothing merges or lands without every check already
having passed. A missing required tool fails its check outright rather than being silently skipped, so every environment
has to be correctly and identically provisioned before it can commit anything, development machine or CI runner alike.
When something fails, the specific, actionable output of exactly what broke is always shown directly, on every channel,
rather than requiring anyone to go dig through a separate report by hand — though the complete underlying record is
still always written out for anything that does want to consume it programmatically.

## Decisions

The git hooks are version-controlled files the repository points at directly, rather than generated into the
repository's private directory by an install command. What runs on every commit is therefore reviewable in history like
any other source file, and setting up a fresh clone is one configuration line instead of a command that could silently
never be run — which is exactly how this project spent a period with no hooks installed at all.

Formatters deliberately never run while an assistant is editing. Rewriting a file immediately after it was written
leaves the editor's own understanding of that file silently wrong and forces it to re-read the whole thing before the
next change. Everything mechanical is therefore applied exactly once, on the whole repo, right before the commit or
merge it gates — nothing about linting or type-checking surfaces any earlier than that, not even a violation no tool
could fix on its own; the commit or merge attempt is the first and only signal.

Fixing a file that was already staged rewrites its content on disk without touching the index, which would otherwise
leave the index holding the pre-fix version while the working tree moves on to the fixed one — an invisible
partial-stage split. The fixer re-adds any file that had a staged diff before it ran, so the index always ends up
holding exactly what the fixer produced. When the gate fails, holding it there would leave content the agent never
staged sitting in the index, so the runner resets the files it re-added before returning its verdict — a retry starts
from a clean index and can never commit a stale version of a rewritten file without explicitly re-staging it. A partial
commit's own select semantics leave the real index holding a rewritten file's pre-hook version even when the commit
succeeded, so `run_fix` records the files it actually rewrote — worktree content changed — in a gitignored marker
(`build/.gate-fixed-paths`, one `path<TAB>blob-sha` line each, the sha naming the pre-fix staged blob as the
deterministic restore pointer), and a `post-commit` hook resets exactly those whose worktree content now matches `HEAD`.
A stale index is synced without touching a staged next version of any other path, and a file staged-but-then-reverted in
the worktree is never in the marker — the fixer did not rewrite it — so no commit form can wipe the only copy of a
staged-only change. A file that gets reformatted without having been staged is left alone; it surfaces in `git status`
like any other drift and gets its own commit whenever that's convenient, never folded silently into whichever commit
happens to run next.

The check gate validates the real, current working tree, not an isolated snapshot of only what's staged. An earlier
design snapshotted the exact staged tree into a scratch directory before checking it, specifically so an unrelated,
half-finished file sitting unstaged elsewhere could never block an unrelated commit — but building that snapshot meant a
cold `uv sync` and a cold test run on every single attempt, since the scratch directory started with no virtual
environment every time. Real-working-tree cost is paid instead now: an unrelated broken file elsewhere in the tree can
block a commit until it's fixed too, in exchange for every gate run reusing the same synced environment and warm caches
the previous run already built.

A content hash of every tracked file is taken right after fixing, right before checking. If it matches the hash from the
previous time this ran, the check is skipped entirely and that run's exact recorded report is replayed instead — the
working tree provably hasn't changed since that result was produced, so re-running would only reproduce it. This is what
makes a long run of small, split commits cheap: the first commit in a batch pays for the real run, and every later one
that leaves the tree exactly as it was replays for free.

Within the fixer step itself, whatever can rewrite logic or structure always runs before whatever only reformats: a
fixer that introduces new code (an import rewrite, a lint autofix) can leave text that doesn't match the project's own
formatting, and nothing further in the sequence would normalize it if the formatter had already had its turn. Ruff's own
linter fixes run before its formatter for exactly this reason, even though the two are built by the same project and
rarely disagree — the ordering is a general safeguard against the fixer step ever leaving behind something the check
step would then fail on.

The mutation-testing tool was switched once already: the original choice achieves its speed by copying mutated code into
place and re-importing it, which broke under this project's own combination of test-collection plugins and strict async
test configuration; the replacement isolates every mutant in its own subprocess instead, trading raw speed for actually
working reliably here. Its own test command runs only the fast unit layer, no database container, since a mutant only an
end-to-end test would catch is an acceptable survivor for a check aimed at the pure domain/application logic.

Continuous integration provisions the exact same formatter/linter toolchain the local git hooks call, through the same
version manager, so neither drifts from the other. A fixture-refresh step and a container-registry login each depend on
a secret a forked repository's pull request never receives, and are skipped rather than failed in that one case — the
tests relying on either then fail on their own instead, rather than the job failing on a secret it was never going to
have.

Every tool's own cache or working-data directory is redirected under one gitignored root, rather than left at each
tool's own default location — the repository root otherwise accumulates one dot-directory per tool, none of them meant
for a person to ever open. The one exception is the project's own environment and its own generated report output,
neither of which is a third-party tool's cache in the same sense.

## Consequences

Because the git hooks are ordinary versioned files, any future change to what runs on commit is itself a reviewable diff
in this repository's own history, not a change to some install script nobody re-reads — but it also means a fresh clone
that skips the one setup line pointing git at them silently runs no hooks at all, with nothing at commit time itself
around to notice or complain.

Adding a future check to the sequence is one more entry in `gates.py`'s own tuple of gates, needing no orchestration
framework brought in for it — the git hook already runs everything directly, in order, against the one real working
tree.

The mutation tool's own switch to per-mutant process isolation means a future test-collection plugin or stricter runtime
mode is far less likely to break it the way the previous tool did, at the accepted ongoing cost of one subprocess launch
per mutant rather than an in-process reimport.

Redirecting every tool's cache under one root means a future tool added to this toolchain is one more subdirectory of
that same root, never a new dot-directory at the repository's own top level to remember to gitignore separately.
