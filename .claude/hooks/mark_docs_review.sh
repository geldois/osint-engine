#!/bin/bash
path=$(sed -n 's/.*"file_path" *: *"\([^"]*\)".*/\1/p' | head -n 1)
case "$path" in
/*)
  case "$path" in
  "$CLAUDE_PROJECT_DIR"/*) ;;
  *) exit 0 ;;
  esac
  ;;
esac
mkdir -p "$CLAUDE_PROJECT_DIR/build"
: >"$CLAUDE_PROJECT_DIR/build/.docs-review-pending"
