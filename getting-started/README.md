# Getting Started with the Power BI Agentic Harness

This guide walks a new team member through everything needed to go from a clean machine to running your first AI-assisted Power BI task with GitHub Copilot and the MCP server.

Follow the steps in order.

---

## Step 1 — Prerequisites

Install the following before continuing.

| Tool | Minimum version | Where to get it |
|---|---|---|
| [VS Code](https://code.visualstudio.com) | Latest stable | code.visualstudio.com |
| [Python](https://www.python.org/downloads) | 3.10 or later | python.org/downloads |
| [Git](https://git-scm.com/downloads) | Any recent | git-scm.com/downloads |
| GitHub Copilot licence | Individual / Business / Enterprise | [github.com/settings/copilot](https://github.com/settings/copilot) |
| [Power BI Desktop](https://powerbi.microsoft.com/desktop) | Latest | powerbi.microsoft.com/desktop |

After installing VS Code, add the two extensions from the Extensions Marketplace (`Ctrl+Shift+X`):
- **GitHub Copilot**
- **GitHub Copilot Chat**

Verify Python is on your PATH:

```bash
python --version
# Expected: Python 3.10.x or higher
```

---

## Step 2 — Clone the Harness Repo and Open It in VS Code

```bash
git clone https://github.com/marenheurman/DBX-Harnass-Test.git
cd DBX-Harnass-Test
code .
```

VS Code will open the repository as your workspace. All skill files, rules, and templates will be available locally from this point on.

---

## Step 3 — Install the Power BI Model MCP Server

Activate your virtual environment first (see Step 4), then install the package:

```bash
pip install powerbi-mcp-server
```

Verify the installation:

```bash
python -m powerbi_mcp_server --help
```

If the help text appears, the server is installed correctly.

---

## Step 4 — Create a Virtual Environment and Activate It

Create a `.venv` inside your workspace folder and activate it before installing any packages.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Your terminal prompt will change to show `(.venv)` when the environment is active. Run `pip install powerbi-mcp-server` (Step 3) inside this environment.

> Add `.venv/` to your `.gitignore` so it is not committed to the repository.

---

## Step 5 — Create the MCP Configuration File

Create the folder `.vscode/` in your workspace root if it does not exist, then create the file `.vscode/mcp.json` with the content below.

Replace `YOUR_MODEL_NAME` with the name of the semantic model you will be working with (this is the dataset name as it appears in Power BI Desktop).

```json
{
  "servers": {
    "powerbi-model": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "powerbi_mcp_server"],
      "env": {
        "POWERBI_MODEL_NAME": "YOUR_MODEL_NAME"
      }
    }
  }
}
```

Save the file. VS Code reads this configuration automatically — no restart is required.

> Do not commit `.vscode/mcp.json` to a shared repository if it contains a model name or environment-specific values. Add it to `.gitignore` or use a template copy.

---

## Step 6 — Start the MCP Server

With your virtual environment active, start the server from the VS Code integrated terminal:

```bash
python -m powerbi_mcp_server
```

The server will start and wait for connections. Leave this terminal running in the background while you work.

You should see output similar to:

```
Power BI MCP Server starting...
Waiting for connection from VS Code...
```

> If you see a port conflict or connection error, check that no other instance of the server is already running.

---

## Step 7 — Open Power BI Desktop with a Model

1. Open **Power BI Desktop**.
2. Open the `.pbix` file or PBIP project you want to work with.
3. Wait for the model to fully load (all tables visible in the Fields pane).
4. Leave Power BI Desktop running — the MCP server connects to the local Analysis Services instance that Power BI Desktop starts automatically in the background.

> The model must be open and loaded before sending any MCP-dependent prompt to Copilot.

---

## Step 8 — Open Copilot Chat and Verify MCP Tools

1. In VS Code, open Copilot Chat with `Ctrl+Alt+I`.
2. Switch to **Agent mode** by clicking the mode selector at the top of the chat panel and choosing **Agent**.
3. Click the **Tools** icon (or type `#`) to see the list of available tools.
4. You should see tools prefixed with `powerbi-model` in the list, for example:
   - `powerbi-model_table_operations`
   - `powerbi-model_measure_operations`
   - `powerbi-model_relationship_operations`

If the `powerbi-model` tools are not listed:
- Confirm the MCP server is still running in the terminal (Step 6)
- Confirm Power BI Desktop is open with a model loaded (Step 7)
- Check `.vscode/mcp.json` exists and has no JSON syntax errors
- Reload VS Code window: `Ctrl+Shift+P` → **Developer: Reload Window**

---

## Step 9 — Run Your First Prompt

With Copilot Chat open in Agent mode, type:

```
List the tables in the model.
```

Copilot will call the MCP server and return the table names from your open Power BI model.

If that works, try:

```
Review the semantic model and flag any relationship issues or star schema violations.
```

This runs the full `semantic-model-review` skill and produces a structured findings report.

---

## Quick Reference

| Resource | Location |
|---|---|
| Agent entry point (AI agents read this first) | [AGENTS.md](../AGENTS.md) |
| Architecture overview | [docs/architecture.md](../docs/architecture.md) |
| Skill list and task routing | [docs/llm-orientation.md](../docs/llm-orientation.md) |
| Example prompts for all skills | [examples/sample-prompts.md](../examples/sample-prompts.md) |
| Safety rules | [rules/safety-rules.md](../rules/safety-rules.md) |
| Using Claude instead of Copilot | [04-using-claude.md](04-using-claude.md) |
