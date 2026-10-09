#!/bin/bash
[ -n "$CLAUDE_PROJECT_DIR" ] || exit 0
path=$(sed -n 's/.*"file_path" *: *"\([^"]*\)".*/\1/p' | head -n 1)
case "$path" in
/*)
  project=$(realpath -m "$CLAUDE_PROJECT_DIR")
  resolved=$(realpath -m "$path")
  case "$resolved" in
  "$project"/*) ;;
  *) exit 0 ;;
  esac
  ;;
esac
mkdir -p "$CLAUDE_PROJECT_DIR/build"
: >"$CLAUDE_PROJECT_DIR/build/.docs-review-pending"
