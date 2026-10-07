#!/bin/bash
marker="$CLAUDE_PROJECT_DIR/build/.docs-review-pending"
[ -f "$marker" ] || exit 0
rm -f "$marker"
grep -Eq '"stop_hook_active" *: *true' && exit 0
cat <<'JSON'
{"decision":"block","reason":"Files changed this turn. Before ending: review every doc against the change — README.md, TO-DO.md and each docs/architecture/*.md (and the sibling osint-studio repo's docs if the shared contract moved). Rewrite whatever no longer tells the truth, in natural language and never citing a function, class or type name (TO-DO.md may name code); keep the README mermaid diagram to a dozen semantic nodes; record any gap found in TO-DO.md; edit nothing if every doc still holds. Then, if the work is done, commit the code and its docs together."}
JSON
