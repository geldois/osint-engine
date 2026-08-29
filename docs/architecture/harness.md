# Harness — what it does

This is the editor/agent integration layer under `.claude/` — distinct from the developer-facing gate façade
`scripts.md` documents, though it calls into that same façade's own tools. Five hooks, all read-only: none of them ever
rewrites a file the agent might be holding in context, so a fixer's rewrite can never leave that in-context copy
silently wrong.

## Decisions

No linter, type-checker, or test ever runs mid-turn, at any point — not per edit, not once at the end of a turn. An
earlier design ran the linter read-only after every edit and the type-checker once at the end of the turn, on the
reasoning that a type-checker mid-refactor reports cascading errors from code that doesn't exist yet. That reasoning
still holds, but there's a simpler reason none of it runs mid-turn anymore: the git hook runs the exact same tools, on
the whole repo, on every commit and merge attempt, so anything a mid-turn run could catch early, the commit attempt
catches anyway — one commit later, never earlier.

A comment or docstring is never auto-stripped, here or anywhere else — an AST-level rewrite carries edge cases (a
command-decorated function's own docstring serving as its help text, an f-string false positive) that could silently
corrupt a file nobody re-reads before it lands, and unlike a formatter this kind of fixer has no idempotency check to
catch its own mistake. A hook nudges instead, leaving the actual judgment call — remove it, rename instead, or move the
decision into this project's own documentation — to whoever is editing. This project deliberately widens that check
beyond the shipped source alone to every tracked, non-generated file in the repository — root configuration, CI
workflow, and this project's own tooling included — since every comment that used to live in one of those had a real
decision behind it, and that decision now lives in `README.md`, `TO-DO.md`, one of `docs/architecture/*.md`, this
project's own `CLAUDE.md`, or `CONTEXT.md` instead. A written change is checked against its own diff, so a comment
predating the edit is left alone until its own line is next touched; a plain file read has nothing to diff against, so
it is checked whole, surfacing a pre-existing one as a pattern not to imitate rather than as something newly introduced.

A separate check runs before every shell command and nudges — it does not block — away from running a linter, formatter,
type-checker, or test directly, redirecting to just committing instead: `pre-commit` and `pre-merge-commit` both already
run the full gate (`scripts precommit`) on every attempt and report any failure inline, so a direct run is pure
duplication of a guarantee already given, with nothing left for it to learn early. A compound shell statement — chained
commands, a subshell, a heredoc body — is split into its parts first, so a wrapped or piped call cannot slip past the
check.

A successful commit or merge doesn't guarantee the working tree is now clean — the fixer may have reformatted a file
that was never staged, or unrelated work may simply still be in progress. A nudge fires after every commit or merge that
isn't one the gate itself just blocked, and checks `git status` on its own: if anything is left, it asks whoever is
finishing the turn to judge whether that's leftover fix output deserving its own commit now, or a deliberate
work-in-progress being set aside for later — never deciding that automatically.

The end-of-turn pass nudges toward updating a touched area's own `docs/architecture/<area>.md` and the architecture
diagram in `README.md`, leaving the judgment of whether the change was actually semantic — versus a rename or a purely
mechanical refactor — to whoever is finishing the turn.

A narrower, project-specific check ties a new endpoint to this project's own recorded test fixtures: a provider fetcher
against a free source declaring an endpoint with no matching case in the fixture-recording script gets flagged, so a
newly-wired endpoint is never silently left without a recorded golden response. Silent otherwise, and silent by provider
name for the one paid source, whose fixtures are never recorded this way at all.

The hooks themselves are standalone scripts, each resolving a shared import from their own directory rather than the
project's, since that is how they actually run; the type checker's own configuration points at that directory as its own
root only so the import resolves, not to relax strictness there.

Read access to a handful of paths — lockfiles, generated changelogs, coverage output, recorded fixtures, every tool's
own cache directory, every flavor of `.env` — is denied outright: each is either pure token cost with nothing an agent
would act on, or a genuine secret.

## Consequences

Because the gate-façade check nudges rather than blocks, an agent that ignores the nudge can still run the full gate
directly — the guarantee that nothing self-verifies redundantly is now a convention this repository's own instructions
carry, not something the tool chain enforces by itself.

Widening the comment check to the whole repository, beyond this project's own general default of the shipped source
alone, means any future root-level configuration or workflow file that needs real explanatory prose has nowhere left to
put it inline — that decision has to be written down in one of this project's own documentation surfaces before the file
is touched, not alongside the line it would have explained.

The endpoint-fixture check only ever compares a literal value against the fixture-recording script's own text, so a
future rewrite of how that script names or looks up its own cases has to keep that literal recognizable there, or the
check goes silent without anyone having actually closed the coverage gap it exists to catch.

Since these hooks resolve their own shared import from their own directory rather than the project's package, they keep
running exactly the same way regardless of whether the project's own dependencies are installed at all — but it also
means a future addition to that shared import has to stay dependency-free, or every hook that imports it inherits
whatever that addition now requires.
