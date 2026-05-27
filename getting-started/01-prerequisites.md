# Step 1 — Prerequisites

Before you can use the Power BI Agentic Harness, you need the following tools installed on your machine.

> This guide is a summary. The full step-by-step prerequisites guide (including screenshots and troubleshooting tips) is in [docs/getting-started-copilot.md](../docs/getting-started-copilot.md).

---

## Required

| Tool | Minimum Version | Purpose |
|---|---|---|
| [VS Code](https://code.visualstudio.com) | Latest stable | Editor and Copilot host |
| [Python](https://www.python.org/downloads) | 3.10 or later | Runs the MCP server locally |
| [Git](https://git-scm.com/downloads) | Any recent | Clone this repository |
| GitHub Copilot licence | Individual / Business / Enterprise | Activates Copilot Chat in VS Code |
| [Power BI Desktop](https://powerbi.microsoft.com/desktop) | Latest | Live model operations via MCP |

## VS Code Extensions (install after VS Code)

Open VS Code → Extensions (`Ctrl+Shift+X`) and install:

- **GitHub Copilot**
- **GitHub Copilot Chat**

## Optional

| Tool | When needed |
|---|---|
| [pbi-tools](https://pbi.tools) | Only if building or modifying PBIP report pages programmatically |

---

## Clone This Repository

```bash
git clone <repository-url>
cd PowerBI-Agentic-Harness
code .
```

Open the cloned folder as your VS Code workspace before proceeding to Step 2.

---

## Verify Python

```bash
python --version
# Expected: Python 3.10.x or higher
```

---

**Next:** [Step 2 — Configure MCP](02-configure-mcp.md)
