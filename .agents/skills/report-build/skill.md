---
name: report-build
description: Use when building, editing, adding to, or cloning a Power BI report or semantic model programmatically. Covers all scenarios from scratch builds to targeted edits. Do NOT use for reviewing an existing report — use the report-review skill for that.
---

# Report Build

## Overview

Route the build request to the correct technical pattern. This skill identifies which scenario applies, then directs the agent to the detailed steps in `docs/report-build-patterns.md`.

**Core principle:** Always write to a new output file. Never overwrite the source `.pbix` in-place. Always read `rules/safety-rules.md` before any write operation.

---

## When to Use

Use this skill when:
- A user asks to "create a report", "build a dashboard", "add a page", "add visuals"
- Cloning an existing report with modifications
- Updating a semantic model (adding measures, columns, or tables)
- Building report layout from a design or wireframe

Do NOT use for:
- Reviewing or auditing an existing report → use `report-review` skill
- Publishing to the Power BI Service → human action required
- Querying or reading model data only → use MCP read tools directly
- Building or generating report pages programmatically from a review context → use `report-review` first, then return here

---

## Step 1: Safety Check

Before any write operation:
1. Read `rules/safety-rules.md`
2. Confirm the environment is not Production
3. If Power BI Desktop is open and MCP is connected, run `connection_operations → ListLocalInstances` to identify the active instance

If no Desktop instance is found and no `.pbix` or PBIP source is available, stop and ask the user to open Power BI Desktop first.

---

## Step 2: Identify Your Scenario

Answer these two questions, then find the matching row:

**Q1: Does a semantic model already exist?**
**Q2: Does a `.pbix` file or PBIP folder already exist?**

| Scenario | Model exists? | Source file exists? | Pattern in `docs/report-build-patterns.md` |
|---|---|---|---|
| Build everything from scratch | No | No | **Pattern A** — MCP model build + Python ZIP report |
| Add new pages to an existing report | Yes | Yes (.pbix) | **Pattern B** — Python ZIP append |
| Edit visuals on an existing page | Yes | Yes (.pbix) | **Pattern C** — Python ZIP modify |
| Clone a report and apply targeted changes | Yes | Yes (.pbix) | **Pattern D** — Python ZIP clone + edit |
| Update the model only (add measure / column / table) | Yes | Desktop open | **Pattern E** — MCP update |
| Edit source-controlled PBIP project files | Yes | Yes (PBIP folder) | **Pattern F** — PBIP + pbi-tools |

Load `docs/report-build-patterns.md` and follow the identified pattern in full.

---

## Step 3: Model Manifest

Before building or modifying any visual, exact table, column, and measure names must be confirmed. A single character difference produces a silently blank visual with no error message.

- **Pattern A (build from scratch):** Author the manifest *alongside* the model as part of Pattern A Step A.2 — do not wait until after tables are created.
- **All other patterns:** If a manifest already exists, use it. If not, derive names from the live model via MCP: `table_operations → List`, `column_operations → List`, `measure_operations → List`.

Use `docs/model-manifest-template.json` as the manifest format.

---

## Step 4: Execute the Pattern

Follow the full steps in `docs/report-build-patterns.md` for the identified pattern. Do not skip or abbreviate steps — each step addresses a known failure mode.

---

## Step 5: Output to the User

Always provide:
1. A summary of what was created or changed (pages, visuals, model objects)
2. The output file path(s)
3. Any assumptions made about field names or data values — flag these explicitly for the user to verify
4. A recommended next step (e.g. open in Desktop, run Refresh, run `report-review` skill)

---

## References

- `docs/report-build-patterns.md` — all 6 build/edit patterns with full technical detail and gotchas
- `docs/pbix-layout-format.md` — PBIX ZIP schema, encoding rules, visual container JSON structure
- `docs/tooling-decision.md` — when to use Python ZIP vs pbi-tools vs MCP
- `templates/build-report-template.py` — Python helper functions (make_card, make_chart, make_table, etc.)
- `docs/model-manifest-template.json` — template for capturing model field names before building
- `.agents/skills/report-review/skill.md` — use after building to validate the output report
- [pbi-tools documentation](https://pbi.tools) — CLI reference for extract and compile commands
