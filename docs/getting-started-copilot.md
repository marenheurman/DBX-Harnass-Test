# Getting Started with the Power BI Agentic Harness (GitHub Copilot)

This guide walks you through setting up the Power BI Agentic Harness step by step, using GitHub Copilot in VS Code.

---

## Step 1 — Prerequisites

Before you start, make sure you have everything listed below installed and ready on your machine.

---

### VS Code

**What it is:** Visual Studio Code is the code editor where you will run GitHub Copilot and configure the MCP connection to your Power BI model.

**Why you need it:** All agent interactions — prompting Copilot, loading skills, and reading MCP tool output — happen inside VS Code. The harness is built and tested specifically for the VS Code environment.

**Where to get it:** [https://code.visualstudio.com](https://code.visualstudio.com)

Install the **GitHub Copilot** and **GitHub Copilot Chat** extensions from the VS Code Extensions Marketplace after installation.

---

### Python (3.10 or later)

**What it is:** Python is a programming language runtime. You do not need to write any Python code yourself — you just need it installed so the MCP server can run.

**Why you need it:** The Power BI Model MCP server is a Python process (`python -m powerbi_mcp_server`) that runs locally on your machine. It acts as the bridge between Copilot and your open Power BI model. Without Python, the MCP server cannot start.

**Where to get it:** [https://www.python.org/downloads](https://www.python.org/downloads)

Check your version after installation:

```
python --version
```

---

### Git

**What it is:** Git is a version control tool used to copy (clone) repositories from GitHub to your local machine.

**Why you need it:** You need Git to clone this repository so you have the skills, rules, and templates available locally in your workspace.

**Where to get it:** [https://git-scm.com/downloads](https://git-scm.com/downloads)

Once installed, clone the repository:

```
git clone <repository-url>
```

Open the cloned folder in VS Code as your workspace before proceeding to the next steps.

---

### GitHub Copilot Licence

**What it is:** A paid or trial subscription to GitHub Copilot that activates the AI assistant inside VS Code.

**Why you need it:** Copilot Chat — the AI panel you will use to prompt the harness skills — requires an active licence. Without it, the Copilot Chat panel will not be available.

**How to check:** Open VS Code and look for the Copilot icon in the status bar. If it shows as inactive or prompts you to sign in, follow the sign-in flow using your GitHub account. Your account must have an active Copilot Individual, Business, or Enterprise subscription.

**Where to manage your subscription:** [https://github.com/settings/copilot](https://github.com/settings/copilot)

---

### Power BI Desktop *(required for live model operations)*

**What it is:** Microsoft's Power BI report authoring tool, which includes a local Analysis Services engine.

**Why you need it:** When you use skills that read from or write to a live semantic model (such as model review, DAX review, or report build), the MCP server connects to a Power BI Desktop instance that must already be running on your machine with your model open.

> If you only intend to review PBIP source files or run documentation-only tasks, you can proceed without Power BI Desktop open. Live MCP operations require it.

**Where to get it:** Install from the Microsoft Store or download from [https://powerbi.microsoft.com/desktop](https://powerbi.microsoft.com/desktop)

---

### pbi-tools *(optional — only needed for PBIP report building)*

**What it is:** A command-line tool for extracting, compiling, and deploying Power BI PBIP project files.

**Why you need it:** Only required if you are building or modifying report pages using PBIP source files (Pattern F in the report-build skill). If you are working with `.pbix` files directly or only reviewing models, you do not need this.

**Where to get it:** [https://pbi.tools](https://pbi.tools)

---

## What's Next

Once all required prerequisites are in place, proceed to the next steps:

- **Step 2** — Configure the MCP server connection in `.vscode/mcp.json`
- **Step 3** — Open a model in Power BI Desktop and verify the MCP connection
- **Step 4** — Run your first Copilot prompt using a harness skill

See [docs/architecture.md](architecture.md) for a full overview of how the components connect.
