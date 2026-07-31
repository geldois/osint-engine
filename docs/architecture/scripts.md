# Scripts — what it does

This is the project's own developer-facing tooling — the quality gate runner, the git hook installer, and one-off
maintenance commands — kept entirely separate from the product itself so none of it ships in the deployed application.
One command runs the fast set of checks (formatting, linting, import-direction, static typing); a slower variant adds
the full automated test suite with coverage measurement. A completely separate, periodic command deliberately introduces
small mutations into the codebase and confirms the test suite actually catches them, as a check on the tests' own
effectiveness rather than just their pass/fail status — this one is never run as part of an ordinary commit, only on
demand.

Every commit and every local merge is validated in full, automatically, against an isolated copy of exactly what's
staged — never against whatever else happens to be sitting unstaged in the working copy — so nothing merges or lands
without every check already having passed. A missing required tool fails its check outright rather than being silently
skipped, so every environment has to be correctly and identically provisioned before it can commit anything, development
machine or CI runner alike. When something fails, the specific, actionable output of exactly what broke is always shown
directly, on every channel, rather than requiring anyone to go dig through a separate report by hand — though the
complete underlying record is still always written out for anything that does want to consume it programmatically.

## Decisions

Running every check against a snapshot deliberately isolated from the real working copy — materialized fresh at commit
time — replaced an off-the-shelf pre-commit framework entirely; the only thing that framework was actually providing
(running checks against exactly what's staged, ignoring unstaged noise) is fully covered by that isolation step on its
own, so keeping the extra framework around stopped earning its cost.

The mutation-testing tool was switched once already: the original choice achieves its speed by copying mutated code into
place and re-importing it, which broke under this project's own combination of test-collection plugins and strict async
test configuration; the replacement isolates every mutant in its own subprocess instead, trading raw speed for actually
working reliably here.
