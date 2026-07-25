---
name: refactor-safely
description: Pull graph-backed refactor-safety data (impact radius, dead code, rename previews) — a data source for a refactor, not a full implementation pipeline
---

## Refactor Safely

If your environment already has a fuller implementation pipeline (spec, convergence, review, docs, commit gates), use this skill only to source graph safety-data for it. Otherwise, use it standalone: plan and execute a refactor with graph-backed confidence.

### Steps

1. Use `refactor_tool` with mode="suggest" for community-driven refactoring suggestions.
2. Use `refactor_tool` with mode="dead_code" to find unreferenced code.
3. For renames, use `refactor_tool` with mode="rename" to preview all affected locations.
4. Use `apply_refactor_tool` with the refactor_id to apply renames.
5. After changes, run `detect_changes_tool` to verify the refactoring impact.

### Safety Checks

- Always preview before applying (rename mode gives you an edit list).
- Check `get_impact_radius_tool` before major refactors.
- Use `get_affected_flows_tool` to ensure no critical paths are broken.
- Run `find_large_functions` to identify decomposition targets.

## Token Efficiency Rules
- ALWAYS start with `get_minimal_context(task="<your task>")` before any other graph tool.
- Use `detail_level="minimal"` on all calls. Only escalate to "standard" when minimal is insufficient.
- Target: complete any review/debug/refactor task in ≤5 tool calls and ≤800 total output tokens.
