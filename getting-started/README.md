# Getting Started with the Power BI Agentic Harness

This guide takes you from "I have just cloned this repo" to "I am running my first skill" — one step at a time. Each step tells you exactly what to do, what success looks like, and what to do if something goes wrong.

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

**✅ Success looks like:** `python --version` prints `Python 3.10.x` or higher and `code .` opens VS Code with the Copilot icon visible in the status bar.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `python` is not recognised | Python not on PATH | Re-run the Python installer, check "Add to PATH", then restart your terminal |
| `python --version` shows 2.x | Old system Python | Install Python 3.10+; use `python3 --version` on macOS/Linux |
| Copilot icon missing in VS Code | Extension not installed or no licence | Install the **GitHub Copilot** extension; sign in to GitHub and verify your licence at [github.com/settings/copilot](https://github.com/settings/copilot) |

---

## Step 2 — Clone the Harness Repo and Open It in VS Code

```bash
git clone https://github.com/marenheurman/DBX-Harnass-Test.git
cd DBX-Harnass-Test
code .
```

VS Code will open the repository as your workspace. All skill files, rules, and templates will be available locally from this point on.

**✅ Success looks like:** VS Code opens with the folder tree showing `.agents/`, `docs/`, `rules/`, and `getting-started/` in the Explorer panel.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `git` is not recognised | Git not installed or not on PATH | Install Git from git-scm.com and restart your terminal |
| `code .` does nothing | VS Code not on PATH | Open VS Code, press `Ctrl+Shift+P`, run **Shell Command: Install 'code' command in PATH** |

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

**✅ Success looks like:** Running `python -m powerbi_mcp_server --help` prints usage instructions without errors.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `No module named powerbi_mcp_server` | Package not installed, or wrong Python / venv | Confirm your `.venv` is active (`(.venv)` in prompt), then re-run `pip install powerbi-mcp-server` |
| `pip` installs to the wrong Python | Multiple Python versions on machine | Use `python -m pip install powerbi-mcp-server` instead of bare `pip install` |

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

**✅ Success looks like:** Your terminal prompt shows `(.venv)` as a prefix, and `pip list` shows only a small set of base packages before you install anything.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then retry |
| `(.venv)` never appears | Wrong activation script for your shell | Use `Activate.ps1` in PowerShell, `activate.bat` in CMD, `source .venv/bin/activate` in bash/zsh |

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

**✅ Success looks like:** The file `.vscode/mcp.json` exists in your workspace root, opens without JSON errors, and `YOUR_MODEL_NAME` has been replaced with your actual model name.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| VS Code does not recognise the MCP config | File saved in wrong location | Confirm the file is at `.vscode/mcp.json` relative to the workspace root — not inside a subfolder |
| JSON parse error on save | Syntax mistake | Validate the file at [jsonlint.com](https://jsonlint.com) — common mistake is a trailing comma after the last property |

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

**✅ Success looks like:** The terminal shows `Power BI MCP Server starting...` and stays running without exiting. The cursor is held — this is expected. Do not close this terminal.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| `No module named powerbi_mcp_server` | Virtual environment not active | Run `.venv\Scripts\Activate.ps1` first, then retry |
| Server starts then immediately exits | Missing or invalid config | Check that `.vscode/mcp.json` exists and `POWERBI_MODEL_NAME` is filled in |
| Address already in use / port conflict | Another server instance is running | Close other terminals running the server, or restart VS Code |

---

## Step 7 — Open Power BI Desktop with a Model

1. Open **Power BI Desktop**.
2. Open the `.pbix` file or PBIP project you want to work with.
3. Wait for the model to fully load (all tables visible in the Fields pane).
4. Leave Power BI Desktop running — the MCP server connects to the local Analysis Services instance that Power BI Desktop starts automatically in the background.

> The model must be open and loaded before sending any MCP-dependent prompt to Copilot.

**✅ Success looks like:** The Fields pane in Power BI Desktop shows all tables and measures from your model. The status bar at the bottom shows no loading spinner.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| MCP returns empty table list | Model still loading | Wait until the Fields pane is fully populated, then retry the prompt |
| Wrong model returned | Multiple `.pbix` files open | Close other Power BI Desktop windows; only one model should be open |

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

**✅ Success looks like:** The Tools panel lists `powerbi-model_table_operations`, `powerbi-model_measure_operations`, and other `powerbi-model_*` tools. The Copilot mode selector shows **Agent**.

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| No `powerbi-model` tools visible | Copilot not in Agent mode | Click the mode selector at the top of the chat panel and switch from **Ask** or **Edit** to **Agent** |
| Tools list is empty | MCP server not running | Open a new terminal, activate `.venv`, and run `python -m powerbi_mcp_server` |
| Tools visible but all fail | Model name mismatch | Check `POWERBI_MODEL_NAME` in `.vscode/mcp.json` matches exactly what Power BI Desktop shows in the title bar |

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

**✅ Success looks like:** Copilot returns a formatted list of table names from your model for the first prompt. For the second prompt it returns a structured report with findings grouped by severity (Critical / Warning / Informational).

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| Copilot responds with generic text, not model data | Not in Agent mode, or MCP tools not called | Switch to Agent mode (Step 8); check the tool calls appear in the chat as expandable items |
| `I don't have access to your Power BI model` | MCP server stopped | Re-run `python -m powerbi_mcp_server` in a terminal with `.venv` active |
| Response is incomplete or cuts off | Long model — context limit reached | Ask Copilot to continue: `"Continue the review from Step 3"` |

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
