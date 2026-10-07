#!/bin/bash
marker="$CLAUDE_PROJECT_DIR/build/.docs-review-pending"
[ -f "$marker" ] || exit 0
rm -f "$marker"
grep -Eq '"stop_hook_active" *: *true' && exit 0
cat <<'JSON'
{"decision": "block", "reason": "Files changed this turn. Before ending, investigate every doc, do not merely read it: README.md, TO-DO.md and each docs/architecture/*.md (and the sibling osint-studio repo's docs if the shared contract moved). For every claim a doc makes (command, path, version, count, route, variable, behaviour, limit, rationale) search the code, config and workflows to confirm it still holds, and correct or delete whatever is wrong, outdated or deprecated, including what this change made stale without adding anything: remove each TO-DO bullet the change resolved, purge every mention of anything removed, recount counts and lists, delete diagram nodes for things that are gone. Record any open problem found in TO-DO.md. Write in natural language and never cite a function, class or type name (TO-DO.md may name code); keep the README mermaid diagram to a dozen semantic nodes. A doc left unchanged must be one you verified. Then, if the work is done, commit the code and its docs together."}
JSON
