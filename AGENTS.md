# Agent Instructions — Power BI Agentic Harness

**If you are an AI agent reading this file: start here.**

This repository is the **Power BI Agentic Harness** — a structured documentation and workflow layer for AI-assisted Power BI development.

---

## First Step

Read [`docs/llm-orientation.md`](docs/llm-orientation.md) immediately.

That file contains:
- The recommended read order for all harness files
- A task-routing map (which skill, rules, and templates to load for each type of request)
- Canonical terminology you must use in all outputs
- Instruction precedence rules for resolving conflicts between documents
- The default operating model (review-and-propose by default)

For a machine-readable routing index, use [`docs/llm-index.json`](docs/llm-index.json).

---

## Core Principles

1. **Read safety rules before acting.** Always load `rules/safety-rules.md` before any task.
2. **Review and propose — do not apply changes without explicit user approval.**
3. **All findings must include a severity rating** (Critical / Warning / Informational).
4. **Ask before large or destructive operations.** Never drop data, publish to production, or modify live workspaces without explicit instruction.
5. **Use the harness files as your single source of truth.** Do not infer rules that are not documented here.

---

## Quick Task Routing

| What the user wants | Load first |
|---|---|
| Review semantic model structure | `.claude/skills/semantic-model-review/SKILL.md` |
| Review DAX measures | `.claude/skills/dax-review/SKILL.md` |
| Review report design / accessibility | `.claude/skills/report-review/SKILL.md` |
| Validate PBIP project structure | `.claude/skills/pbip-structure/SKILL.md` |
| Check naming conventions | `.claude/skills/naming-conventions/SKILL.md` |
| Run full pre-release assessment | `.claude/skills/release-readiness/SKILL.md` |
| Build report pages in a .pbix using Python | `docs/pbix-layout-format.md` |

For the complete routing table including rules, templates, and examples, see [`docs/llm-orientation.md`](docs/llm-orientation.md).

---

## What This Repository Is Not

- It is not a live Power BI environment. The agent cannot publish to the Power BI Service from this repository.
- It is not a dataset. Do not query data from here.
- It is not a standalone tool. It augments an MCP-connected agent workflow or a Copilot/Claude session.
