#!/bin/bash
marker="$CLAUDE_PROJECT_DIR/build/.docs-review-pending"
[ -f "$marker" ] || exit 0
rm -f "$marker"
grep -Eq '"stop_hook_active" *: *true' && exit 0
cat <<'JSON'
{"decision": "block", "reason": "Files changed this turn. Before ending, investigate every doc, do not merely read it: README.md and each docs/architecture/*.md, Open problems sections included (and the sibling osint-studio repo's docs if the shared contract moved). For every claim a doc makes (command, path, version, count, route, variable, behaviour, limit, rationale) search the code, config and workflows to confirm it still holds, and correct or delete whatever is wrong, outdated or deprecated, including what this change made stale without adding anything: remove each open problem the change resolved, purge every mention of anything removed, recount counts and lists, delete diagram nodes for things that are gone. Record any open problem found in the Open problems section of the docs/architecture document that owns the code, and keep a fact in one document only: a limit accepted by design is a Consequence, never also an open problem. Write in natural language and never cite a function, class or type name (Open problems sections may name code); keep the README mermaid diagram to a dozen semantic nodes. A doc left unchanged must be one you verified. Then, if the work is done, commit the code and its docs together."}
JSON
