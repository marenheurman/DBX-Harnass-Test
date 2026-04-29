# Architecture

## Overview

This document describes how AI agents connect to and interact with Power BI in the context of the **Power BI Agentic Harness**. Understanding the architecture is essential for anyone configuring the tooling, writing new skills, or governing how AI is used in a Power BI project.

---

## Core Principle: Read First, Propose Second

All agent interactions with the Power BI model must follow a strict pattern:

1. **Read** metadata and data from the model via MCP
2. **Analyse** what was found against the rules in the Power BI Agentic Harness
3. **Propose** changes in structured written output
4. **Wait** for human review and approval before any change is applied

Agents must never directly modify a published Power BI dataset, report, or workspace without an explicit human action.

---

## Component Overview

```
┌─────────────────────────────────┐
│  Developer / BI Engineer        │
│  (VS Code, Claude, Copilot)     │
└──────────────┬──────────────────┘
               │ natural language prompt
               ▼
┌─────────────────────────────────┐
│  AI Agent                       │
│  (GitHub Copilot / Claude)      │
│  + skills from .claude/skills/  │
└──────────────┬──────────────────┘
               │ MCP tool calls
               ▼
┌─────────────────────────────────┐
│  Power BI Model MCP Server      │
│  (local process, TCP socket)    │
└──────────────┬──────────────────┘
               │ XMLA / TOM / DAX
               ▼
┌─────────────────────────────────┐
│  Analysis Services Engine       │
│  (embedded in Power BI Desktop  │
│   or Azure Analysis Services)   │
└──────────────┬──────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
 ┌──────────┐     ┌──────────────┐
 │ Tables   │     │  Measures    │
 │ Columns  │     │  Partitions  │
 │ Relations│     │  Roles       │
 └──────────┘     └──────────────┘
```

---

## MCP Server Configuration

The Power BI Model MCP server exposes the running semantic model as a set of readable tools. Configure it in `.vscode/mcp.json`:

```json
{
  "servers": {
    "powerbi-model": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "powerbi_mcp_server"],
      "env": {
        "POWERBI_WORKSPACE_CONNECTION": "localhost",
        "POWERBI_MODEL_NAME": "YourModelName"
      }
    }
  }
}
```

The server exposes MCP tools that allow the agent to:

| Tool | Description |
|------|-------------|
| `list_tables` | Returns all tables in the model |
| `list_measures` | Returns all measures with their DAX expressions |
| `list_relationships` | Returns all relationships with cardinality and direction |
| `list_columns` | Returns columns for a given table |
| `run_dax_query` | Executes a DAX query and returns results |
| `get_model_metadata` | Returns top-level model properties |
| `list_partitions` | Returns partition definitions for a table |

---

## PBIP File Structure

When working with Power BI Projects (PBIP), the agent can also read source files directly from the filesystem. A PBIP project exposes the semantic model and report as structured JSON.

```
MyReport.SemanticModel/
  definition/
    model.bim               ← Full TOM JSON (tables, measures, relationships)
    tables/
      Sales.tmdl            ← Table definitions in TMDL format
      Date.tmdl
    relationships.tmdl      ← Relationship definitions
    measures.tmdl           ← Shared measure definitions

MyReport.Report/
  definition/
    report.json             ← Report-level settings
    pages/
      Overview.json         ← Page-level visual definitions
```

The `pbip-structure` skill reads and validates these files.

---

## Local vs Service Architecture

| Context | Agent reads from | Agent writes to |
|---------|-----------------|-----------------|
| Local development (PBIP) | Filesystem (PBIP JSON/TMDL) | Proposed changes only — developer applies manually |
| Power BI Desktop (live) | MCP server (Analysis Services) | Proposed changes only — developer applies in Desktop |
| Power BI Service (cloud) | REST API (read-only) | Never — requires human action in Service |

---

## Security Boundaries

- The MCP server runs locally and is not exposed to the internet
- Bearer tokens for the Power BI Service (if used) must be stored in environment variables, never in source files
- The agent must not log, echo, or store credentials from environment variables
- Row-level security (RLS) roles must be defined in the model, not circumvented by agent queries
- Agent DAX queries run under the service account of the local AS engine — results may differ from end-user RLS-filtered results

See [governance.md](governance.md) and [rules/safety-rules.md](../rules/safety-rules.md) for full constraints.

---

## References

- Microsoft Learn: [Power BI Project (.pbip) overview](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- Microsoft Learn: [Tabular model overview](https://learn.microsoft.com/analysis-services/tabular-models/tabular-models)
- Microsoft Learn: [Power BI REST APIs](https://learn.microsoft.com/rest/api/power-bi/)
- [docs/governance.md](governance.md)
- [rules/safety-rules.md](../rules/safety-rules.md)
