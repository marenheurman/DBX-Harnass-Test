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
Is the task about writing or editing DAX / TMDL / PBIP files?
├── Yes → Use GitHub Copilot inline in VS Code
└── No
    │
    Is the task a structured review (model, DAX quality, report, release)?
    ├── Yes → Use Claude or Copilot Chat with the relevant skill
    └── No
        │
        Is the task adding or modifying report pages in a .pbix file?
        ├── Yes — and you have a PBIP extract (folder structure)
        │         → Use `pbi-tools compile` after editing the JSON source files
        └── Yes — and you have only a .pbix file (no extract)
                  → Use Python ZIP manipulation
                    (see docs/pbix-layout-format.md and templates/build-report-template.py)
            │
            Is the model currently open in Power BI Desktop?
            ├── Yes → Use MCP-connected agent for live inspection
            └── No
                │
                Is the task documentation, planning, or design?
                └── Yes → Use Claude without MCP (filesystem context is sufficient)
```

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
- In VS Code agent mode, Copilot reads `.claude/skills/` SKILL.md files with YAML frontmatter natively — the same skill format used throughout this repository

### Configuration
Configure the MCP server in `.vscode/mcp.json`. Copilot will discover and use MCP tools automatically in agent mode.

---

## Claude

### Strengths
- Large context window — can handle full model.bim files or many measures at once
- Strong at producing structured, consistent documentation output
- Excellent reasoning about complex DAX logic and model topology
- Reads `.claude/skills/` SKILL.md files natively

### Limitations
- Not embedded in the VS Code editor flow — better suited for review tasks than inline editing
- Requires API access or claude.ai subscription
- MCP integration requires additional setup

### Configuration
Reference skills directly in your prompt:
```
Follow the instructions in .claude/skills/semantic-model-review/skill.md and review this model.
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
