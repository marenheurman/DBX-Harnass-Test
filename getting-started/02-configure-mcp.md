# Step 2 — Configure the MCP Server

The Power BI Model MCP server is the bridge between GitHub Copilot and your open Power BI semantic model. Without it, skills that read model metadata (tables, measures, relationships) will not have access to your model.

---

## How It Works

```
[GitHub Copilot in VS Code]
        │
        ▼
[MCP Server — powerbi-mcp-server (Python)]
        │
        ▼
[Power BI Desktop — local Analysis Services engine]
        │
        ▼
[Your semantic model: tables, measures, relationships]
```

The MCP server runs locally on your machine. It does not connect to the Power BI Service or any cloud endpoint.

---

## Step 1 — Install the MCP Server Package

Open a terminal in VS Code and run:

```bash
pip install powerbi-mcp-server
```

Verify the installation:

```bash
python -m powerbi_mcp_server --help
```

---

## Step 2 — Create the MCP Configuration File

In your workspace root, create the folder `.vscode/` if it does not exist, then create the file `.vscode/mcp.json` with the following content:

```json
{
  "servers": {
    "powerbi-model": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "powerbi_mcp_server"]
    }
  }
}
```

> VS Code reads this file automatically when you open the workspace. No restart is required after saving.

---

## Step 3 — Open Your Model in Power BI Desktop

1. Open Power BI Desktop.
2. Open the `.pbix` or PBIP project you want to work with.
3. Leave Power BI Desktop running — the MCP server connects to the local Analysis Services instance that Power BI Desktop starts automatically.

> The model must be open and loaded before you run any MCP-dependent skill (model review, DAX review, etc.).

---

## Step 4 — Verify the Connection

In VS Code Copilot Chat, type:

```
List the tables in the open semantic model.
```

If the MCP server is connected, Copilot will return a list of tables from your model. If it fails, check:

- Is Power BI Desktop open with a model loaded?
- Is Python in your PATH (`python --version` in terminal)?
- Does `.vscode/mcp.json` exist in your workspace root?

---

## Tasks That Do Not Require MCP

The following skills work without a live model connection and do not require MCP:

| Skill | Works without MCP? |
|---|---|
| DAX review (from file) | Yes |
| Naming conventions review | Yes |
| PBIP structure review | Yes |
| Report review | Yes |
| Release readiness | Yes |
| Semantic model review (live) | **Requires MCP** |
| DAX query execution | **Requires MCP** |
| Report build (live compile) | **Requires MCP** |

---

**Next:** [Step 3 — Run Your First Prompt](03-first-prompt.md)
