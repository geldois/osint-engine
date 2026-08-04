import type { Plugin } from "@opencode-ai/plugin"

/**
 * Project-local parity with .claude/hooks/. Two of the three Claude Code hooks
 * port; opencode has no end-of-turn event, so the per-turn basedpyright pass
 * has no equivalent here and stays at the commit gate.
 *
 * Like its Claude counterpart, nothing here writes to a file — a hook that
 * rewrites what the model just wrote leaves its in-context copy silently wrong.
 * Every fixer runs once, at pre-commit.
 */

/** Runner and flag tokens stripped before matching, so wrapping cannot bypass. */
const LEADING = /^(?:uv|uvx|run|python3?|npx|mise|exec|--?\S+)\s+/
const TOOL =
  /^(?:pytest|ruff check|ruff format|basedpyright|cosmic-ray|cr-rate|lint-imports|sqruff)\b/
const TARGETED_FILE = /\s\S+\.(?:py|sql)(?:\s|$)/

const REDIRECT =
  "Full lint/type/test/mutation runs go through the gate facade, not raw tools: " +
  "`uv run python -m scripts check` (fast) or `check --full`. It materialises the " +
  "staged snapshot, orders every gate, fails on a missing tool, and writes " +
  "build/reports/gates.json. Targeted single-file/single-test runs are not blocked."

const NO_PRERUN =
  "Don't pre-run `check --full` — `pre-commit` already runs `check --staged --full` " +
  "on a materialised snapshot for every commit and surfaces failures inline. Just " +
  "commit; if it fails, fix what's reported and commit again."

const MAX_REPORTED = 20

function isFullFacadeRun(normalized: string): boolean {
  const tokens = normalized.split(/\s+/)
  return tokens[0] === "scripts" && tokens[1] === "check" && tokens.slice(2).includes("--full")
}

function strip(command: string): string {
  let normalized = command
  for (let match = LEADING.exec(normalized); match; match = LEADING.exec(normalized)) {
    normalized = normalized.slice(match[0].length)
  }
  return normalized
}

type RuffViolation = {
  code?: string
  message?: string
  fix?: unknown
  location?: { row?: number }
}

export default (async ({ $, directory }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "bash") return
      const command = (output.args as { command?: unknown })?.command
      if (typeof command !== "string") return

      const normalized = strip(command)
      if (isFullFacadeRun(normalized)) throw new Error(NO_PRERUN)
      if (!TOOL.test(normalized)) return
      if (normalized.includes("::") || TARGETED_FILE.test(normalized)) return
      throw new Error(REDIRECT)
    },

    // opencode has no additionalContext channel, so the report rides back on
    // the tool's own output, which the model does read.
    "tool.execute.after": async (input, output) => {
      if (input.tool !== "edit" && input.tool !== "write") return
      const file = (input.args as { filePath?: unknown })?.filePath
      if (typeof file !== "string" || !file.endsWith(".py")) return

      // Fail-soft: an unactivated version manager degrades this to silence,
      // never to a broken turn. A missing tool is a hard failure at the gate.
      let parsed: unknown
      try {
        const result = await $`uv run --no-sync ruff check --output-format=json --force-exclude ${file}`
          .cwd(directory)
          .nothrow()
          .quiet()
        parsed = JSON.parse(result.text())
      } catch {
        return
      }
      if (!Array.isArray(parsed)) return

      // Only what ruff cannot fix itself; the pre-commit fix step silently
      // resolves the rest, so reporting it here would be pure token waste.
      const lines = (parsed as RuffViolation[])
        .filter((violation) => violation.fix == null)
        .slice(0, MAX_REPORTED)
        .map((violation) => `  ${violation.location?.row ?? ""}: ${violation.code} ${violation.message}`)

      if (lines.length > 0) {
        output.output += `\n\n[harness] ruff (not auto-fixable)\n${lines.join("\n")}`
      }
    },
  }
}) satisfies Plugin
