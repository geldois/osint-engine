<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

This project has a knowledge graph. The global harness (`~/.claude/CLAUDE.md`,
Code Review Graph section) owns the "graph before Grep/Glob/Explore" mandate
and its enforcing hook — this section exists only for portability to clones
without that global config, and only wraps the graph's own tool table.

Fall back to Grep/Glob **only** when the graph doesn't cover what you need
(`Read` is never gated).

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
