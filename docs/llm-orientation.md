# LLM Orientation Guide

This document is the fastest way for an LLM or coding agent to understand how to use the Power BI Agentic Harness correctly.

Read this file before interpreting the rest of the repository.

If you need a machine-readable entrypoint, use `docs/llm-index.json`.

---

## What This Repository Is

The Power BI Agentic Harness is a documentation and workflow layer for AI-assisted Power BI work.

It provides:
- Skills for specific review tasks
- Rules that constrain behaviour and evaluation criteria
- Templates for structured output
- Examples that show expected prompts and report formats
- Governance documentation that defines safety boundaries

This repository is primarily advisory. By default, the agent should review, analyse, and propose. It should not assume permission to change production systems, publish reports, or handle credentials.

**Exception — Local Desktop Build context:** When the `report-build` skill is active and Power BI Desktop is running locally, MCP write operations (model creation and editing) and Python ZIP manipulation (report pages) are permitted with explicit user confirmation. See the Local Desktop Build context row in `rules/safety-rules.md`.

---

## Read Order for LLMs

Use this order unless the user gives a more specific instruction:

1. `README.md`
2. `rules/safety-rules.md`
3. `rules/prompting-rules.md`
4. The relevant skill in `.agents/skills/`
5. The matching rule file in `rules/`
6. The matching template in `templates/`
7. The matching example in `examples/`
8. The matching test in `tests/`, if present

This order matters:
- `README.md` explains scope and structure
- `safety-rules.md` defines hard boundaries
- `prompting-rules.md` defines response behaviour
- Skills define task-specific workflow
- Rules define what counts as good or bad
- Templates define output structure
- Examples and tests calibrate expected quality

---

## Task Routing Map

Use this table to decide which files to load.

| User Intent | Primary Skill | Supporting Rules | Output Template | Example |
|---|---|---|---|---|
| Review model structure or relationships | `.agents/skills/semantic-model-review/skill.md` | `rules/modeling-rules.md`, `rules/safety-rules.md`, `rules/prompting-rules.md` | `templates/model-review-template.md` | `examples/sample-model-review.md` |
| Review DAX measures | `.agents/skills/dax-review/skill.md` | `rules/dax-rules.md`, `rules/safety-rules.md`, `rules/prompting-rules.md` | `templates/model-review-template.md` | `examples/sample-dax-review.md` |
| Review report design or accessibility | `.agents/skills/report-review/skill.md` | `rules/report-rules.md`, `rules/safety-rules.md`, `rules/prompting-rules.md` | `templates/report-review-template.md` | `examples/sample-report-review.md` |
| Build or edit a report or semantic model (add pages, add measures, build from scratch) | `.agents/skills/report-build/skill.md` | `docs/report-build-patterns.md`, `docs/pbix-layout-format.md`, `docs/tooling-decision.md`, `rules/safety-rules.md` | `templates/build-report-template.py` | — |
| Validate PBIP project structure | `.agents/skills/pbip-structure/skill.md` | `rules/governance-rules.md`, `rules/safety-rules.md`, `rules/prompting-rules.md` | No dedicated template yet | `examples/sample-pbip-structure-review.md` |
| Check naming conventions | `.agents/skills/naming-conventions/skill.md` | Naming rules inside skill, plus `rules/prompting-rules.md` | No dedicated template yet | `examples/sample-naming-conventions-review.md` |
| Run full pre-release assessment | `.agents/skills/release-readiness/skill.md` | All relevant rule files | Consolidated report written by workflow | `examples/sample-release-readiness.md` |
| Review custom visuals in a report | `.agents/skills/report-review/skill.md` | `rules/report-rules.md`, `docs/custom-visuals.md`, `rules/safety-rules.md` | `templates/report-review-template.md` | `examples/sample-report-review.md` |
| **Build a complete new semantic model from scratch via MCP** | `.agents/prompts/model-build-agent.md` | `rules/safety-rules.md`, `.agents/skills/flat-file-ingestion/SKILL.md`, `.agents/skills/measure-table/SKILL.md`, `rules/dax-rules.md` | — | — |

---

## Canonical Terminology

Use these terms consistently.

| Preferred Term | Use It For | Avoid |
|---|---|---|
| Power BI Agentic Harness | Formal repository name | accelerator, toolkit, framework as the default name |
| skill | A task-specific instruction file in `.agents/skills/` | workflow file, skill file as the default term |
| rule | A normative guidance file in `rules/` | policy note, checklist, standard doc when referring to these files specifically |
| template | A structured output format in `templates/` | form, skeleton |
| measure | Power BI measure | metric, calculation as the default term |
| fact table | Central transactional table | fact |
| dimension table | Descriptive filter table | dimension |
| Date table | Generic concept for a dedicated date dimension | calendar table as the default term unless the model uses that exact table name |
| PBIP project | Power BI Project in source control | PBIP on its own when first introduced |
| workspace | Power BI Service workspace | environment when the Power BI Service object is meant |
| environment | Development, UAT, Production, local Desktop context | workspace when speaking broadly |

- If the model contains a table literally named `Date` or `Calendar`, keep that exact table name in code and findings.

---

## Behaviour Priorities

When instructions conflict, apply this precedence order:

1. `rules/safety-rules.md`
2. `docs/governance.md` and `rules/governance-rules.md` (if they conflict, `governance-rules.md` provides the specific operational rule; `governance.md` provides the broader principle)
3. `rules/prompting-rules.md`
4. The selected skill
5. The selected rule file
6. The selected template
7. Examples

- Never let an example override a safety or governance rule.

---

## Default Operating Model

Unless the user explicitly asks for something else:

- Review first
- Report findings with severity
- Ask before broad or expensive data access
- Propose changes before applying them
- Escalate ambiguity instead of guessing intent
- Treat custom visuals as partially inspectable only
- Treat production-adjacent operations as restricted

---

## What Not to Infer

Do not assume any of the following without evidence:

- A bidirectional relationship is intentional
- An inactive relationship is harmless
- A custom visual is approved just because it renders correctly
- A missing title or alt text is acceptable because the author probably intended it
- A PBIP structure is valid because the top-level folders exist
- A clean review means the project is defect-free

- If evidence is missing, state the uncertainty explicitly.

---

## Response Shape for Reviews

When producing a structured review, prefer this sequence:

1. Summary with severity counts
2. Critical findings
3. Warnings
4. Informational findings
5. Recommended next steps
6. Open questions or required human confirmation

- Do not bury Critical findings below general commentary.

---

## Recommended Future Improvements

These would make the repository even easier for LLMs to consume:

- Add dedicated templates for `pbip-structure`, `naming-conventions`, and `release-readiness`
- Standardise all skill files on `SKILL.md` or `skill.md` naming across the repo
- Expand the machine-readable index if the harness is later consumed by automated tooling beyond simple routing

---

## References

- `README.md`
- `docs/llm-index.json`
- `rules/safety-rules.md`
- `rules/prompting-rules.md`
- `docs/supported-scenarios.md`
- `docs/governance.md`
