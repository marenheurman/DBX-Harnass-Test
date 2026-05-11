# Tooling Decision Guide

## Purpose

This document helps teams decide which AI agent tooling to use for a given Power BI task. It covers GitHub Copilot, Claude, and the Power BI Model MCP server, and provides guidance on when each is most appropriate.

---

## Tooling Overview

| Tool | Best For | Requires |
|------|----------|----------|
| GitHub Copilot Chat (VS Code) | Inline development assistance, PBIP file editing, DAX writing | Copilot licence, VS Code |
| GitHub Copilot + MCP | Live model inspection and review while in VS Code | Copilot licence, MCP server running |
| Claude (claude.ai) | Deep analysis, documentation writing, structured reviews | Claude subscription or API |
| Claude + MCP | Full skill-driven model and report reviews with live data | Claude API, MCP server running |
| Power BI Model MCP server alone | Exposing model metadata as readable context | Python environment |

---

## Decision Tree

```
What is the task?
│
├── Writing or editing DAX / TMDL / PBIP files inline?
│   └── Yes → Use GitHub Copilot inline in VS Code
│
├── Structured review (model, DAX quality, report design, release readiness)?
│   └── Yes → Use Claude or Copilot Chat with the relevant skill from .agents/skills/
│
├── Building or editing a Power BI report or semantic model programmatically?
│   └── Yes → Load .agents/skills/report-build/skill.md and identify scenario:
│
│       No existing model, no existing .pbix?
│       └── Pattern A: MCP model build (tables → relationships → measures → refresh)
│                      then Python ZIP (add report pages)
│                      Power BI Desktop must be open.
│
│       Existing .pbix, want to ADD new pages without touching existing ones?
│       └── Pattern B: Python ZIP — append to layout["sections"], preserve existing ordinals
│
│       Existing .pbix, want to EDIT a specific visual on an existing page?
│       └── Pattern C: Python ZIP — load layout, find page by displayName,
│                      find visual container by config.name, modify and re-serialise
│
│       Existing .pbix, want a COPY with targeted changes?
│       └── Pattern D: Python ZIP — copy all ZIP entries first,
│                      then apply modifications to the copy
│
│       Model already open in Desktop, only need to add/change measures or columns?
│       └── Pattern E: MCP write operations only (measure_operations, column_operations)
│                      No Python needed.
│
│       PBIP folder (source-controlled project) available?
│       └── Pattern F: Edit TMDL/JSON source files directly,
│                      then pbi-tools compile to produce updated .pbix
│
├── Documentation, planning, or design work?
│   └── Yes → Use Claude without MCP (filesystem context is sufficient)
│
└── Live model inspection or DAX query against real data?
    └── Yes → MCP read operations (table_operations → List, measure_operations → List,
               database_operations → ExportTMDL, etc.)
               Power BI Desktop must be open with the model loaded.
```

---

## NOTE: Python ZIP vs pbi-tools vs MCP — Summary

| Need | Use |
|------|-----|
| Add/modify report pages in a .pbix (no PBIP) | Python ZIP manipulation (docs/pbix-layout-format.md) |
| Add/modify report pages in a PBIP project | pbi-tools compile after editing source JSON |
| Extract a .pbix to editable PBIP source files | pbi-tools extract |
| Create or modify model objects (tables, measures, relationships) | MCP write operations — Power BI Desktop must be open |
| Live DAX query or model metadata read | MCP read operations |
| Review or validate (no changes) | Claude/Copilot with relevant skill, MCP read-only |

---

## GitHub Copilot

### Strengths
- Deeply integrated into VS Code editor experience
- Excellent for line-by-line DAX and TMDL code assistance
- Fast autocomplete for repetitive patterns
- Works well with PBIP file editing

### Limitations
- Context window smaller than Claude — less suitable for reviewing large models in one pass
- Less capable of producing long-form structured documentation
- In VS Code agent mode, Copilot reads `.agents/skills/` SKILL.md files with YAML frontmatter natively — the same skill format used throughout this repository

### Configuration
Configure the MCP server in `.vscode/mcp.json`. Copilot will discover and use MCP tools automatically in agent mode.

---

## Claude

### Strengths
- Large context window — can handle full model.bim files or many measures at once
- Strong at producing structured, consistent documentation output
- Excellent reasoning about complex DAX logic and model topology
- Reads `.agents/skills/` SKILL.md files natively

### Limitations
- Not embedded in the VS Code editor flow — better suited for review tasks than inline editing
- Requires API access or claude.ai subscription
- MCP integration requires additional setup

### Configuration
Reference skills directly in your prompt:
```
Follow the instructions in .agents/skills/semantic-model-review/skill.md and review this model.
```

---

## Power BI Model MCP Server

The MCP server is a Python process that connects to the Analysis Services engine embedded in Power BI Desktop (or Azure Analysis Services) and exposes model metadata as MCP tools.

### When to Run It
- When you want live inspection of a model that is open in Power BI Desktop
- When you want the agent to run actual DAX queries against real data
- When reviewing a model that cannot easily be exported to files

### When Not to Run It
- When working with committed PBIP files in source control (read the files directly)
- When the model is in the Power BI Service and you only need metadata (use REST API read-only access instead)

### Starting the Server
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Start the MCP server
python -m powerbi_mcp_server
```

The server will print the port it is listening on. Update `.vscode/mcp.json` if the port differs from the default.

---

## Recommended Configuration per Scenario

| Scenario | Recommended Tooling |
|----------|---------------------|
| Writing new DAX measures | Copilot inline (VS Code) |
| Reviewing DAX quality across all measures | Claude + MCP server |
| Reviewing model relationships | Claude + MCP server or Claude + model.bim file |
| Reviewing a report layout | Claude + PBIP report JSON files |
| Writing TMDL table definitions | Copilot inline (VS Code) |
| Release readiness check | Claude + MCP server + all skill files |
| Writing governance documentation | Claude (no MCP needed) |
| Pair-programming on a specific measure bug | Copilot inline (VS Code) |
| Adding report pages to a .pbix programmatically | Python (`templates/build-report-template.py`) |

---

## Programmatic Report Page Generation

When you need to add or modify report pages in a `.pbix` file and a full PBIP extract is not available, use **Python ZIP manipulation**.

> **Important:** This approach uses the undocumented internal structure of the `.pbix` format. It is **not officially supported by Microsoft**. See the full disclaimer in `docs/pbix-layout-format.md` before adopting this technique.

### When to Use pbi-tools vs Python ZIP

| Scenario | Recommended Approach |
|---|---|
| Full report rebuild from source-controlled PBIP | `pbi-tools compile` |
| Extracting a `.pbix` to inspect or version-control it | `pbi-tools extract` |
| Adding pages to an existing `.pbix` without a full extract | Python ZipFile + `templates/build-report-template.py` |
| Patching a single visual in an existing `.pbix` | Python ZipFile + `templates/build-report-template.py` |
| Reviewing report layout for quality/accessibility | MCP server + `report-review` skill |

### Python ZIP Approach — Quick Reference

| Resource | Location |
|---|---|
| Full technical reference | `docs/pbix-layout-format.md` |
| Starter script with helpers | `templates/build-report-template.py` |
| Model field name template | `docs/model-manifest-template.json` |

**Critical rules:**
1. Encode `Report/Layout` as **UTF-16-LE without BOM** — any other encoding silently corrupts the file.
2. **Zero out `SecurityBindings`** — leaving it stale causes a "corrupted file" error on open.
3. **Never write to the same path as the source `.pbix`** — always output to a new file.
4. **Double-serialise `config`, `query`, and `dataTransforms`** — these fields must be JSON strings, not raw objects.

### Projections Key Names by Visual Type

| Visual Type | Category key | Value key |
|---|---|---|
| `card` | — | `"Values"` |
| `columnChart` | `"Category"` | `"Y"` |
| `barChart` | `"Category"` | `"Y"` |
| `lineChart` | `"Category"` | `"Y"` |
| `tableEx` | — | `"Values"` |
| `textbox` | — | — |

---

## References

- Microsoft Learn: [Power BI Project (.pbip) overview](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- Microsoft Learn: [Power BI documentation home](https://learn.microsoft.com/power-bi/)
- [pbi-tools](https://pbi.tools)
- [docs/architecture.md](architecture.md)
- [docs/pbix-layout-format.md](pbix-layout-format.md)
- [templates/build-report-template.py](../templates/build-report-template.py)
- [docs/model-manifest-template.json](model-manifest-template.json)
