# Harness — what it does

This is the editor/agent integration layer under `.claude/` — distinct from the developer-facing gate runner
`scripts.md` documents. It is deliberately tiny: one settings file holding a list of denied commands, with no hook and
no script. Nothing in it writes a file the agent might be holding in context.

## Decisions

The git hook runs every linter, formatter, type-checker and test on the whole repo for every commit, so the agent has no
reason to run the project's gate itself. The two gate commands, the full check and the comment-ban scan, are therefore
denied to the agent in the project's settings, directly and through the package runner with or without its sync step;
only the git hook and continuous integration run them, and the project's instructions say they are never run by the
agent even on request. Also denied is every commit, merge or push that skips the git hook. The fixer command is not
denied, because the project's instructions require the agent to run it before every commit.

The individual tools are not denied. The agent may run any linter, formatter, type-checker or test runner, on one file
or on the whole repo, only when the user explicitly asks for it or allows it in that message; the project's instructions
state this, and no setting enforces it. The gate commands stay exclusive to the hook because their whole-repo run is
what a commit is judged by.

A deny rule matches the command as written, so a wrapper shell or an absolute path to a tool can still get past it — a
guard against the usual form, not a security boundary.

The comment ban lives in the gate, not here. It used to be a per-edit hook that nudged on a comment as it was written or
read, which could only ever suggest; the gate now fails the commit, which is the only enforcement that cannot be
ignored. The same applies to the check tying a provider's endpoint to a recorded fixture case, now an ordinary test.

The review of the documentation against the code is a standing instruction in the project's instructions, written to be
done at the moment of each documentation write. It used to be a pair of hooks that marked the turn on any edit and
blocked the stop until the review was requested; they were retired because the instruction already holds the same duty
without any mechanism to go stale.

## Consequences

Because denied commands match text, an agent determined to run a gate command can still do so through a wrapper; the
guarantee that the gate runs only in the hook is held by the deny list in the usual case and by this repository's own
instructions beyond it. The permission to run the individual tools rests on the instructions alone, so it is exactly as
reliable as the agent following them.

The documentation review is a prompt, not a proof. Nothing mechanical can tell that a document has drifted from the
code, so fidelity depends on the review actually being done; the commit that follows carries code and documents
together.

## Open problems

- **The shared contract with `osint-studio` is written down nowhere.** The project's instructions ask to check that
  repo's docs when the contract moves, but no document says what the contract is or where its source of truth lives
