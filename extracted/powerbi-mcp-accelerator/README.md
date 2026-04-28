# Power BI MCP Accelerator

A collection of reusable skills, rules, templates, and governance guidelines for AI-assisted Power BI development. Designed for enterprise BI teams using GitHub Copilot, Claude, or other MCP-compatible coding agents.

---

## What This Accelerator Is

The **Power BI MCP Accelerator** provides a structured harness for using AI coding agents safely and effectively in Power BI projects. It does not replace Power BI tooling — it augments it by giving AI agents the right context, constraints, and workflows to assist with:

- Semantic model design and review
- DAX measure analysis and improvement
- Report and visual layout review
- PBIP project structure validation
- Naming convention enforcement
- Release readiness assessment

All agent interactions are designed to be **read-only and advisory by default**. Agents propose changes; humans approve and apply them. This principle is enforced throughout the skills, rules, and governance documentation.

---

## How MCP Agents Interact with Power BI

This accelerator is designed to work with the **Power BI Model MCP server**, which exposes a running Power BI semantic model (via Analysis Services) to AI agents through the Model Context Protocol.

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
powerbi-mcp-accelerator/
│
├── README.md                        ← You are here
│
├── docs/
│   ├── architecture.md              ← How agents connect to Power BI
│   ├── supported-scenarios.md       ← What tasks this accelerator supports
│   ├── governance.md                ← Enterprise governance principles
│   └── tooling-decision.md          ← When to use Copilot vs Claude vs other agents
│
├── .claude/
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
│   └── migration-checklist.md       ← Pre-migration and post-migration checklist
│
├── examples/
│   ├── sample-prompts.md            ← Example prompts to invoke each skill
│   ├── sample-model-review.md       ← Example model review output
│   └── sample-dax-review.md         ← Example DAX review output
│
└── tests/
    ├── prompt-tests/
    │   └── semantic-model-review.md ← Validation scenarios for model review skill
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

### With Claude (claude.ai or API)

Skills are stored in `.claude/skills/`. You can reference them directly in your system prompt, or tell Claude to fetch and follow the instructions in a specific skill file.

### Pointing to a Skill Explicitly

```
Follow the instructions in .claude/skills/dax-review/skill.md and review all measures in the Sales table.
```

---

## How to Extend This Repository

### Adding a New Skill

1. Create a folder under `.claude/skills/<skill-name>/`
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

This accelerator was built by Capgemini's Insights & Data practice. Contributions welcome from the Power BI community.
