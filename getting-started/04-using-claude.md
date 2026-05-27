# Step 4 — Using Claude

The harness works with Claude (claude.ai or API) as well as GitHub Copilot. This guide explains how to load skills when working with Claude.

---

## When to Use Claude Instead of Copilot

| Scenario | Best choice |
|---|---|
| Live model via MCP in VS Code | Copilot |
| Long-document analysis (large PBIP files, many measures) | Claude (larger context window) |
| Automated prompt evaluations and A/B testing | Claude API |
| Working outside VS Code (browser, scripts) | Claude |
| Either works fine | Your preference |

See [docs/tooling-decision.md](../docs/tooling-decision.md) for the full comparison.

---

## How to Load a Skill in Claude

### Option A — Paste the skill content directly

1. Open the skill file you need, e.g. `.agents/skills/dax-review/skill.md`
2. Copy the full file contents
3. Paste it into the Claude conversation as your system prompt or first user message
4. Then send your task

### Option B — Reference the skill by path

If Claude has access to your repository (e.g. via an API integration or project context), you can reference the skill directly:

```
Follow the instructions in .agents/skills/semantic-model-review/skill.md
and review the model definition in the file I am about to paste.
```

### Option C — Use the AGENTS.md entry point

For longer sessions, paste the contents of `AGENTS.md` first. It gives Claude the full task-routing map and tells it which skill to load for your request:

```
[paste AGENTS.md contents]

Now review the DAX measures in the following output and flag any issues.
```

---

## Rules Claude Must Follow

Before any task, instruct Claude to load the safety rules:

```
Before starting, read and follow rules/safety-rules.md.
```

Or paste the rules content directly. Key rules:

- Propose changes only — never apply them without explicit approval
- All findings must include a severity rating (Critical / Warning / Informational)
- Do not query, publish to, or modify live Power BI Service workspaces
- Do not infer rules that are not documented in the harness files

---

## Example — DAX Review with Claude

```
You are a Senior DAX Engineer. Follow the instructions in the skill below.

[paste .agents/skills/dax-review/skill.md]

Review the following DAX measure and produce a structured findings report:

Revenue YTD =
CALCULATE(
    [Total Revenue],
    DATESYTD('Date'[Date])
)
```

---

## Example — Semantic Model Review with Claude

```
You are a Senior Data Modeller. Follow the instructions below.

[paste rules/safety-rules.md]
[paste .agents/skills/semantic-model-review/skill.md]

The model definition is:
[paste model JSON or TMDL content]
```

---

**You are now set up.** Return to the [Getting Started overview](README.md) or go straight to [examples/sample-prompts.md](../examples/sample-prompts.md) for ready-to-use prompts.
