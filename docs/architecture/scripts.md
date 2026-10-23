# Scripts — what it does

This is the project's own developer-facing tooling — the quality gate runner and one-off maintenance commands — kept
entirely separate from the product itself so none of it ships in the deployed application. One command runs every check
the project owns: the ban on comments, formatting, linting, import direction, static typing, shell, Markdown and TOML
linting, and the full automated test suite with coverage. A second command applies every safe automatic fixer to the
whole repo. A completely separate, periodic command deliberately introduces small mutations into the codebase and
confirms the test suite actually catches them, as a check on the tests' own effectiveness rather than just their
pass/fail status — this one is never run as part of an ordinary commit, only on demand.

Every commit is validated in full, automatically, by the git hook, and continuous integration runs the very same
command. The release and image-publishing workflows call that same workflow first and do nothing unless it passes, so
nothing is published or deployed without every check having passed on the exact commit being shipped. A warning from any
tool counts as a failure, and so does a missing required tool, which fails its check outright rather than being silently
skipped. Each gate prints a header line and then its tool's own output, written straight to the terminal as the tool
runs and never captured, so it keeps the tool's own formatting and appears the moment the gate finishes; a closing
verdict line ends the run. There is no progress display and no separate report file to dig through. Each tool runs with
the least verbose output flags confirmed for its pinned version.

## Decisions

The git hook is a version-controlled file the repository points at directly, rather than generated into the repository's
private directory by an install command. What runs on every commit is therefore reviewable in history like any other
source file, and setting up a fresh clone is one configuration line instead of a command that could silently never be
run — which is exactly how this project spent a period with no hooks installed at all. Merge commits are forbidden by
configuration, so a commit is the only way anything enters history and one hook covers every path in.

The hook only verifies; it never rewrites anything. An earlier design fixed the whole repo inside the hook, re-staged
whatever it rewrote, replayed a cached result when the tree was unchanged and needed a second hook plus a marker file to
undo the residue of partial commits. All of that machinery existed to serve one convenience — never running a fixer by
hand — and each piece was a place for a subtle bug to hide in the one component whose only job is to be trustworthy. The
refusal tells the person the exact commands for both outcomes, commit everything or stash the rest. Fixing is now a
separate, explicit command run before committing, and the commit then finds nothing left to complain about. The cost is
one extra command per commit; the gain is a gate with no state and nothing to go stale.

The gate checks the real working tree, so the hook first refuses the commit when anything is unstaged or untracked.
Without that refusal a forgotten new file, or an edit left unstaged, could make the suite pass against code the commit
does not contain. The cost is that a partial commit needs the rest stashed, so a run of split commits pays for a full
gate each time; the gain is that what was tested is exactly what is committed. The check runs inside the shell hook
rather than the runner because the runner strips git's own environment variables, which are what make commits of
selected paths or of all tracked changes see the right index.

The comment ban is a gate rather than a nudge. A comment or docstring is never auto-stripped, since an AST-level rewrite
could silently corrupt a file, but a violation now fails the commit: every tracked file is scanned, whatever its type,
except generated code and the few kinds that have no comment syntax or are the point of the file (JSON, Markdown, the
lockfile, the licence and the interpreter version file), so a new kind of file is covered the day it is added, with a
closed allowlist for linter-suppression pragmas, shell directives, shebangs, pinned-action version tags and the
annotations the SQL query loader requires. A comment marker only counts when it starts a word, so shell argument-count
and length expansions are never mistaken for one.

The uv version is pinned exactly in the project manifest, read by the workflows and enforced by uv itself wherever it
runs, so a stale install fails loudly instead of drifting; the container image's tag and the release helper's pin are
the two other copies and are edited together. The runner syncs the environment once and then runs every tool without
re-syncing, so no gate can change the environment under another. Every linter, formatter and type-checker is a pinned
development dependency installed with that environment, so the only prerequisites of the gate are the package manager
and the container runtime the test suite already needs. Within the fixer, whatever can rewrite logic or structure always
runs before whatever only reformats: a fixer that introduces new code (an import rewrite, a lint autofix) can leave text
that doesn't match the project's own formatting, and nothing further in the sequence would normalize it if the formatter
had already had its turn.

The mutation-testing tool was switched once already: the original choice achieves its speed by copying mutated code into
place and re-importing it, which broke under this project's own combination of test-collection plugins and strict async
test configuration; the replacement isolates every mutant in its own subprocess instead, trading raw speed for actually
working reliably here. Its own test command runs only the fast unit layer, no database container, since a mutant only an
end-to-end test would catch is an acceptable survivor for a check aimed at the pure domain/application logic.

The container-registry login in continuous integration depends on a secret a forked repository's pull request never
receives, and is skipped rather than failed in that one case — the tests relying on it then fail on their own instead,
rather than the job failing on a secret it was never going to have.

Every tool's own cache or working-data directory is redirected under one gitignored root, rather than left at each
tool's own default location — the repository root otherwise accumulates one dot-directory per tool, none of them meant
for a person to ever open. The exceptions are the project's own environment and the mutation run's session database,
neither of which is a third-party tool's cache in the same sense.

Every linter, formatter and fixer a gate calls is a pinned development dependency of the project, installed by the same
environment sync as the code, never an image pulled or a binary expected on the host. A gate therefore behaves
identically on a fresh clone, in the hook and in continuous integration, and a tool version moves only through the
lockfile in a reviewable commit. A tool that could not be installed that way would need its alternatives weighed in the
open and written down here, or the absence of any alternative stated, before it joined a gate; a test fails the build
when a gate runs a tool the project does not declare. The workflow linter is declared too, but it is distributed as
source whose build downloads the linter's binary and checks it against a digest carried inside the package, so a sync
needs access to the code host and, on NixOS, the system certificate bundle exported to the environment. The one
deliberate exception is a plugin that a declared tool loads from its own configuration: dprint formats JSON and YAML
through plugins that it fetches from the npm registry, each pinned to an exact version in its own configuration file and
cached after the first run. They are part of that tool, not a second tool, so they stay out of the manifest, and the
cost is registry access on the first run of a fresh machine or runner.

Each file type has exactly one owner that both lints and formats it, so lint and fix share one parser and one
configuration: Markdown belongs to rumdl, TOML to tombi, and JSON and YAML to dprint, which stays only for the types no
native tool formats. rumdl was picked over the reference markdownlint implementation because it installs through the
same package manager as everything else instead of needing a Node runtime or a container, covers the same rules plus
more, and reflows paragraphs to the configured width with the exact output dprint used to produce; the cost is a younger
project still labelled beta, offset by pinning one exact version. tombi replaced dprint's TOML plugin because its linter
and formatter agree on table order, which the plugin never checked, and its schema for the project manifest ships inside
the tool, so linting needs no network. The generated lockfile is left out of the tools that would rewrite it.

The project manifest is also validated against the packaging standard's own schema, including license expressions and
trove classifiers, which a TOML linter cannot know.

YAML has two checks beyond its formatter. A linter keeps only the rules a formatter cannot see, such as duplicate keys
and values a YAML 1.1 parser would read as booleans, with every layout rule switched off so that it never disagrees with
dprint. Compose files and workflows are additionally validated against their published schemas, which ship inside the
validator, so the check needs no network and catches a misspelt key or a missing required field.

Workflows are held to one contract rather than reviewed by eye, because the gate can only read them, never run them. The
workflow linter checks syntax, expressions, runner labels and the shell inside every step, using the pinned shell linter
that the project already installs, so a step is judged by the same tool version as the committed scripts. The security
analyser runs offline, at its strictest persona that still avoids false positives, so the hook needs no token; the
audits that need the hosting API are left to a continuous-integration step that has one. Two of its audits are set aside
on purpose: the one demanding an explanatory comment on every permission, because the repository bans comments in every
file, and the one asking for the new in-repository call syntax, because the pinned workflow linter rejects it today.
Both settings live in the analyser's own configuration and are revisited when the linter learns the syntax. The
host-side commands of the deploy job are committed shell files executed through the action's script path, which puts
them under the shell linter and formatter and keeps every value out of text substitution.

The set of files a gate or a tool touches is discovered, never listed by hand. The shell, compose and workflow files
come from the version control's own list of tracked files, so a new file enters its gate the moment it is added, with no
list to edit and no test needed to notice a forgotten entry; the comment ban inverts the default and scans every tracked
file, excluding a short closed set. What is generated, cached or vendored is already declared once in the ignore file,
and the formatters, the Markdown linter and the YAML linter read it instead of repeating it; the only exclusions left in
a tool's own configuration are tracked files that tool must not rewrite, the recorded API responses and the lockfile.
Which package installs each gate's executable is read from the environment's own metadata, not from a table.

Every value a tool enforces, such as line width, indentation and line endings, is written once, in that tool's own
configuration. The editor-neutral configuration file only mirrors them for editors that cannot read the tools, and a
test fails when any mirrored value differs from its owner, when the mirror carries a section matching no tracked file,
or when an editor-specific directory is committed.

## Consequences

Because the git hook is an ordinary versioned file, any future change to what runs on commit is itself a reviewable diff
in this repository's own history — but it also means a fresh clone that skips the one setup line pointing git at it
silently runs no hook at all. Continuous integration running the same command is what closes that gap, along with the
bypass flag, the rebase and the cherry-pick, none of which run the hook.

The JSON and YAML formatter downloads its plugins on first use, so the very first gate on a fresh machine needs network
access beyond the package index.

Refusing a dirty tree makes every commit a whole-tree event: unrelated half-finished work has to be stashed before an
unrelated commit can land.

Adding a future check is one more entry in the runner's own list of gates, needing no orchestration framework brought in
for it.

The mutation tool's own switch to per-mutant process isolation means a future test-collection plugin or stricter runtime
mode is far less likely to break it the way the previous tool did, at the accepted ongoing cost of one subprocess launch
per mutant rather than an in-process reimport.

Redirecting every tool's cache under one root means a future tool added to this toolchain is one more subdirectory of
that same root, never a new dot-directory at the repository's own top level to remember to gitignore separately.

## Open problems

- **The workflow analyser's online audits run nowhere.** The gate in `scripts/check.py` runs it offline, so audits that
  ask the hosting API about impostor commits, vulnerable actions and ref confusion are never executed. A step in
  `.github/workflows/test.yml` with a read-only token, running the analyser online, closes it; add it when pinned action
  versions need that cross-check
- **Two analyser audits are disabled or ignored for stated reasons that can lapse.** `.github/zizmor.yml` sets aside the
  permission-comment audit while comments are banned and the self-repository-syntax audit for the two workflows that
  call `test.yml`, because the pinned workflow linter rejects that syntax. Re-enable the second as soon as a pinned
  release of the linter accepts it
- **The uv version lives in four places**, all exactly `0.11.21`: `required-version` in `[tool.uv]` (the one the
  workflows read and that uv enforces everywhere it runs), the `Dockerfile`'s uv image tag and digest, and the two
  README setup steps that state it. A drifted copy in the first two fails loudly, but all four still move together
- **Ten gates run without a reduced-output flag.** `dprint`, `sqruff`, `basedpyright`, `shfmt`, `lint-imports`,
  `yamllint`, `check-jsonschema`, `validate-pyproject`, `actionlint` and `zizmor` (which only turns its progress off)
  print their full default output, because no flag cutting it was confirmed for the pinned versions (`lint-imports` 2.13
  lacks `--no-logo`, which later documentation lists). Check each tool's changelog on every bump
- **No test proves that a gate's tool still sees a terminal.** The tests run a real process through the runner and prove
  that its output reaches the terminal untouched and under its header, but the capture they use is not a terminal, so
  nothing proves the tool keeps the colors and layout it only emits to one
