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
│  + skills from .agents/skills/  │
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
        "POWERBI_WORKSPACE_CONNECTION": "YOUR_SERVER_OR_INSTANCE",
        "POWERBI_MODEL_NAME": "YourModelName"
      }
    }
  }
}
```

Do not assume `localhost` is portable across machines. Use a shared SQL host when available, or require each developer to set a local value for `POWERBI_WORKSPACE_CONNECTION` in their own environment.

The MCP server exposes tools across two categories: **read** (safe for all environments) and **write** (requires environment confirmation before use — see `rules/safety-rules.md`).

### Read Operations

| Tool | Description |
|------|-------------|
| `connection_operations → ListLocalInstances` | Discovers running Power BI Desktop instances and their AS connection strings |
| `connection_operations → GetConnection` | Returns details of the current active connection |
| `table_operations → List` | Returns all tables in the model |
| `table_operations → Get` | Returns full definition of a single table |
| `measure_operations → List` | Returns all measures with their DAX expressions and format strings |
| `column_operations → List` | Returns columns for one or more tables |
| `relationship_operations → List` | Returns all relationships with cardinality and direction |
| `partition_operations → List` | Returns partition definitions for a table |
| `database_operations → ExportTMDL` | Exports the full model as TMDL (YAML-like format) |
| `database_operations → ExportTMSL` | Exports the full model as a TMSL JSON script |

### Write Operations

Write operations modify the live model in Power BI Desktop. Always confirm environment classification before using these.

| Tool | Description |
|------|-------------|
| `connection_operations → Connect` | Connects the MCP server to a running Power BI Desktop instance |
| `table_operations → Create` | Creates a new table (M expression or calculated DAX) with explicit column definitions |
| `table_operations → Update` | Updates table properties |
| `table_operations → Delete` | Deletes a table and optionally cascades to dependent objects |
| `table_operations → Rename` | Renames a table |
| `column_operations → Create` | Adds a column to an existing table |
| `column_operations → Update` | Updates column properties (data type, format string, summarizeBy, etc.) |
| `column_operations → Delete` | Removes a column |
| `column_operations → Rename` | Renames a column |
| `measure_operations → Create` | Creates a new DAX measure in a specified table |
| `measure_operations → Update` | Updates a measure expression, format string, or folder |
| `measure_operations → Delete` | Deletes a measure |
| `measure_operations → Move` | Moves a measure to a different table |
| `relationship_operations → Create` | Creates a new relationship between two tables |
| `relationship_operations → Update` | Updates relationship properties (cardinality, filter direction, active state) |
| `relationship_operations → Delete` | Removes a relationship |
| `relationship_operations → Activate/Deactivate` | Toggles a relationship between active and inactive |
| `partition_operations → Refresh` | Triggers a data refresh on one or more tables (Full, Calculate, DataOnly, etc.) |
| `database_operations → Update` | Updates top-level model properties |

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

| Context | Agent reads from | Agent writes to | Notes |
|---------|-----------------|-----------------|-------|
| Local development (PBIP) | Filesystem (PBIP JSON/TMDL) | Proposed changes only — developer applies manually | Safe for all environments |
| Power BI Desktop (live) | MCP server read operations | MCP server write operations (model only) + Python ZIP (report pages) | Write requires environment confirmation. MCP cannot write report pages — use Python ZIP for that. |
| Power BI Service (cloud) | REST API (read-only) | Never — requires human action in Service UI | See safety-rules.md |

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
