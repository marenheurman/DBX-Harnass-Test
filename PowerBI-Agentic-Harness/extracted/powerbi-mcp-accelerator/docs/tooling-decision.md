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
- Skills (instructions files) must be in `.github/copilot-instructions.md` or `.instructions.md` format for Copilot; `.claude/skills/` is for Claude

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
