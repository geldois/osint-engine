# Harness — what it does

This is the editor/agent integration layer under `.claude/` — distinct from the developer-facing gate runner
`scripts.md` documents. It is deliberately tiny: a list of denied commands and two shell scripts. The scripts only ever
touch one marker file under the gitignored build directory, never a tracked file, and none of them rewrites a file the
agent might be holding in context.

## Decisions

No linter, formatter, type-checker or test is ever run by the agent. The git hook runs the exact same tools on the whole
repo for every commit, so a direct run is pure duplication of a guarantee already given. This used to be a hook that
nudged after the fact; it is now a list of denied commands in the project's settings, which blocks the call before it
runs and needs no code. Denied are the tools themselves, the project's check command and its comment-ban command,
directly and through the package runner with or without its sync step, including the test runner invoked as a module,
and every commit, merge or push that skips the git hook; the fix command is not denied, because the project's
instructions require the agent to run it before every commit. A deny rule matches the command as written, so a wrapper
shell or an absolute path to a tool can still get past it — a guard against the usual form, not a security boundary.

The comment ban lives in the gate, not here. It used to be a per-edit hook that nudged on a comment as it was written or
read, which could only ever suggest; the gate now fails the commit, which is the only enforcement that cannot be
ignored. The same applies to the check tying a provider's endpoint to a recorded fixture case, now an ordinary test, and
to the nudge after a commit about a dirty tree, which only existed to catch the residue of the old in-hook fixer.

Documentation is reviewed in every turn that changed anything. A hook marks the turn the moment any file inside this
repository is written (an edit elsewhere, such as the agent's own notes, marks nothing), and a second hook, at the end
of the turn, consumes that mark exactly once and blocks the stop with an instruction to investigate every document, not
merely read it: check each claim against the code and configuration, correct or delete whatever is wrong, outdated or
deprecated (including what the change made stale without adding anything, such as a debt entry it resolved), in natural
language and without naming code, then commit code and documents together. There is no list of paths that count inside
the repository: any edit, including to configuration, can invalidate a claim, and a list of exclusions is one more thing
to go stale. The marker rather than a live query of the repository is what makes the review fire even when the agent
committed during the turn and left a clean tree. The pass the review itself triggers must not trigger another, so the
second hook skips when it is already running on behalf of a previous block, after clearing the mark that review's own
edits set.

Whether a change was semantic or purely mechanical is a judgment the hook never makes; it only guarantees the question
is asked every time. A change made only through a shell command, such as a rename, a deletion or a code generation,
writes no mark, a deliberate gap.

Both scripts are `bash`, like the git hook, rather than a second language: the repository already requires a POSIX shell
for the git hook, which on Windows comes with Git for Windows, so the agent hooks add no new prerequisite. They locate
the marker through the project directory the editor exports, never the shell's current directory, which any earlier
change of directory can leave pointing at another repository, and compare resolved paths so a symlinked spelling of the
project directory still counts; with no project directory exported they do nothing.

## Consequences

Because denied commands match text, an agent determined to run a tool can still do so through a wrapper; the guarantee
that nothing self-verifies redundantly is held by the deny list in the usual case and by this repository's own
instructions beyond it.

The documentation review is a prompt, not a proof. Nothing mechanical can tell that a document has drifted from the
code, so fidelity depends on the review actually being done each turn; the hook guarantees it is requested, and the
commit that follows carries code and documents together.

The marker is shared by every session in the same checkout, so two agents working at once can consume each other's mark;
the review then still happens, just in the other session.
