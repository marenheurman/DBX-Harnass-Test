# Power BI Agentic Harness

A collection of reusable skills, rules, templates, and governance guidelines for AI-assisted Power BI development. Designed for enterprise BI teams using GitHub Copilot, Claude, or other MCP-compatible coding agents.

---

> **Disclaimer — Please Read Before Use**
>
> The **Power BI Agentic Harness** is an evolving toolkit built on technologies that are new and rapidly changing. AI tooling, the Model Context Protocol (MCP), and Power BI platform capabilities are all actively developing — many versions and refinements will be made in the near future. This harness is **always evolving** and may change significantly between releases.
>
> **Use this harness at your own risk.** It is provided as-is, without warranty of any kind. Always test in non-production environments. Never apply agent-assisted changes to live data or reports without proper human review and approval.
>
> **Data guidance:** Only use open-source or publicly available, harmless data when working with this harness. Never connect agents to datasets containing sensitive, personal, confidential, or proprietary data without appropriate governance controls in place. The authors accept no liability for data loss, corruption, or misuse arising from use of this toolkit.

---

## What This Is

The **Power BI Agentic Harness** provides a structured harness for using AI coding agents safely and effectively in Power BI projects. It does not replace Power BI tooling — it augments it by giving AI agents the right context, constraints, and workflows to assist with:

- Semantic model design and review
- DAX measure analysis and improvement
- Report and visual layout review
- PBIP project structure validation
- Naming convention enforcement
- Release readiness assessment
- Custom visual evaluation and governance — see [docs/custom-visuals.md](docs/custom-visuals.md)

All agent interactions are designed to be **read-only and advisory by default**. Agents propose changes; humans approve and apply them. This principle is enforced throughout the skills, rules, and governance documentation.

---

## LLM Quick Start

If you are an AI agent or coding assistant reading this repository, start with [AGENTS.md](AGENTS.md). It provides a concise orientation and immediate task routing before you read anything else.

If you are using this repository with an LLM in a longer session, follow with [docs/llm-orientation.md](docs/llm-orientation.md).

That file provides:
- The recommended read order
- A task-to-file routing map
- Canonical terminology for consistent outputs
- Instruction precedence when multiple documents overlap

For automated tooling or lightweight agent bootstrapping, use [docs/llm-index.json](docs/llm-index.json).

This reduces ambiguity and helps the agent load the right context before responding.

---

## How MCP Agents Interact with Power BI

The **Power BI Agentic Harness** is designed to work with the **Power BI Model MCP server**, which exposes a running Power BI semantic model (via Analysis Services) to AI agents through the Model Context Protocol.

```
[AI Agent (Copilot / Claude)]
        │
        ▼
[MCP Server (Power BI Model)]
        │
        ▼
[Semantic Model (AS Engine)]
        │
        ▼
[Tables / Measures / Relationships / Partitions]
```

The agent can:
- Query model metadata (tables, columns, measures, relationships)
- Run DAX queries against the model
- Read PBIP project files (JSON-based semantic model and report definitions)
- Analyse model topology and flag issues

The agent **cannot** (and must not) directly publish to the Power BI Service, modify production workspaces, or push changes without human review.

See [docs/architecture.md](docs/architecture.md) for the full architecture overview.

---

## Repository Structure

```
powerbi-agentic-harness/
│
├── README.md                        ← You are here
├── AGENTS.md                        ← AI agent entry point — read this first
│
├── docs/
│   ├── architecture.md              ← How agents connect to Power BI
│   ├── supported-scenarios.md       ← What tasks this accelerator supports
│   ├── governance.md                ← Enterprise governance principles
│   ├── tooling-decision.md          ← When to use Copilot vs Claude vs other agents
│   ├── custom-visuals.md            ← Custom visual governance, build guide, and agent limits
│   ├── pbix-layout-format.md        ← Internal .pbix ZIP structure for programmatic report building
│   ├── model-manifest-template.json ← Template for documenting model field names for report scripts
│   ├── llm-index.json               ← Machine-readable routing and terminology index for LLMs
│   └── llm-orientation.md           ← Recommended read order, terminology, and routing for LLMs
│
├── .agents/
│   └── skills/
│       ├── semantic-model-review/   ← Full model topology and relationship review
│       ├── dax-review/              ← DAX measure quality and correctness
│       ├── report-review/           ← Visual layout, UX, and accessibility
│       ├── pbip-structure/          ← PBIP project file integrity checks
│       ├── naming-conventions/      ← Table, column, and measure naming rules
│       └── release-readiness/       ← Pre-deployment checklist
│
├── rules/
│   ├── safety-rules.md              ← What agents must never do
│   ├── modeling-rules.md            ← Star schema and relationship rules
│   ├── dax-rules.md                 ← DAX authoring standards
│   ├── report-rules.md              ← Visual and report design standards
│   ├── governance-rules.md          ← Workspace and deployment governance
│   └── prompting-rules.md           ← How agents should behave
│
├── templates/
│   ├── model-review-template.md     ← Structured output for model reviews
│   ├── report-review-template.md    ← Structured output for report reviews
│   ├── migration-checklist.md       ← Pre-migration and post-migration checklist
│   └── build-report-template.py    ← Python starter script for programmatic PBIX report page generation
│
├── examples/
│   ├── sample-prompts.md            ← Example prompts to invoke each skill
│   ├── sample-model-review.md       ← Example model review output
│   ├── sample-dax-review.md         ← Example DAX review output
│   ├── sample-report-review.md      ← Example report review output
│   ├── sample-pbip-structure-review.md ← Example PBIP structure review output
│   ├── sample-naming-conventions-review.md ← Example naming review output
│   └── sample-release-readiness.md  ← Example consolidated readiness output
│
└── tests/
        ├── prompt-tests/
        │   ├── semantic-model-review.md ← Validation scenarios for model review skill
        │   ├── pbip-structure.md        ← Validation scenarios for PBIP structure skill
        │   ├── report-review.md         ← Validation scenarios for report review skill
        │   ├── naming-conventions.md    ← Validation scenarios for naming review skill
        │   └── release-readiness.md     ← Validation scenarios for release readiness skill
        └── rule-tests/
                └── dax-rule-checks.md       ← Validation scenarios for DAX rules
```

---

## How to Use the Skills

### With GitHub Copilot (VS Code)

Once the Power BI Model MCP server is running and connected in `.vscode/mcp.json`, open Copilot Chat and use natural language prompts. The agent will automatically invoke the appropriate skill based on your request.

Example:
```
Review the semantic model and flag any relationship issues.
```

### Report Creation and pbi-tools CLI

Creating or modifying Power BI report layouts programmatically requires the **[pbi-tools](https://pbi.tools)** CLI from the pbi-tools open-source toolkit. pbi-tools provides command-line utilities for extracting, compiling, and deploying PBIP report files, and must be installed separately.

```
pbi-tools extract -pbixPath "MyReport.pbix" -extractFolder "./MyReport.PBIP"
```

Agent skills in this harness that propose report-level changes assume pbi-tools is available in the project environment. See the pbi-tools documentation for installation and usage.

### With Claude (claude.ai or API)

Skills are stored in `.agents/skills/`. You can reference them directly in your system prompt, or tell Claude to fetch and follow the instructions in a specific skill file.

### Pointing to a Skill Explicitly

```
Follow the instructions in .agents/skills/dax-review/skill.md and review all measures in the Sales table.
```

---

## How to Extend This Repository

### Adding a New Skill

1. Create a folder under `.agents/skills/<skill-name>/`
2. Add a `skill.md` file following the format of existing skills (YAML frontmatter + structured instructions)
3. Reference the skill from `docs/supported-scenarios.md`
4. Add an example prompt to `examples/sample-prompts.md`

### Adding Rules

Rules live in `rules/`. Add a new `.md` file or extend an existing one. Rules are referenced by skills and the agent should be instructed to follow them.

### Adding Templates

Templates in `templates/` define the structure of agent output documents. Agents should be instructed to write output using the appropriate template.

---

## How to Contribute

1. Fork or branch the repository
2. Add or update skills, rules, or documentation
3. Test your changes using the scenarios in `tests/`
4. Submit a pull request with a clear description of what changed and why
5. Ensure all rules remain consistent — a change to `modeling-rules.md` may require updates to the `semantic-model-review` skill

---

## Requirements

- Power BI Desktop (for working with PBIP files)
- Power BI Model MCP server (for live semantic model inspection)
- VS Code or VS Code Insiders
- GitHub Copilot licence **or** Claude API access
- Optional: Power BI Service workspace for deployment governance

---

## Authors and Maintainers

The **Power BI Agentic Harness** was built by Capgemini's Insights & Data practice. It is an active, evolving project — contributions, feedback, and issue reports are welcome via pull request. 

---

## References

- Microsoft Learn: [Power BI Project (.pbip) overview](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- Microsoft Learn: [Power BI accessibility overview](https://learn.microsoft.com/power-bi/create-reports/desktop-accessibility-overview)
- Microsoft Learn: [Power BI custom visuals overview](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals)
- [pbi-tools](https://pbi.tools)
- [AGENTS.md](AGENTS.md)
- [docs/architecture.md](docs/architecture.md)
- [docs/custom-visuals.md](docs/custom-visuals.md)
- [docs/pbix-layout-format.md](docs/pbix-layout-format.md)
- [docs/model-manifest-template.json](docs/model-manifest-template.json)
- [docs/llm-index.json](docs/llm-index.json)
- [docs/llm-orientation.md](docs/llm-orientation.md)
- [docs/tooling-decision.md](docs/tooling-decision.md)
