# Step 3 — Run Your First Prompt

With prerequisites installed and MCP configured, you are ready to run your first AI-assisted task using a harness skill.

---

## Before You Start

- VS Code is open with this repository as your workspace
- GitHub Copilot Chat panel is visible (`Ctrl+Alt+I`)
- Power BI Desktop is open with a model loaded *(only needed for live model tasks)*

---

## How Skills Work

Skills are instruction files in `.agents/skills/`. When you reference a skill in your prompt, the agent loads it and follows its structured workflow. You do not need to manually open skill files — just describe your task naturally.

---

## Your First Three Prompts

### 1 — Review the semantic model (live, requires MCP)

```
Review the semantic model and flag any relationship issues or star schema violations.
```

The agent will use `.agents/skills/semantic-model-review/skill.md` and produce a structured findings report.

---

### 2 — Review a DAX measure (no MCP needed)

Paste a measure into chat:

```
Review this DAX measure for correctness and performance:

Sales YTD =
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)
```

The agent will use `.agents/skills/dax-review/skill.md` and flag any issues.

---

### 3 — Check naming conventions

```
Review the naming conventions in the open model and flag anything that does not follow enterprise standards.
```

The agent will use `.agents/skills/naming-conventions/skill.md`.

---

## Reading the Output

Every skill produces a structured report with:

| Section | What it contains |
|---|---|
| **Findings** | Each issue with a severity rating (Critical / Warning / Informational) |
| **Severity** | Critical = must fix before release. Warning = should fix. Informational = low urgency |
| **Suggested action** | Specific, actionable recommendation for each finding |

The agent **proposes** changes only. It will not modify your model, files, or reports without explicit instruction.

---

## Tips

- Be specific: `"Review the Sales table relationships"` gives better results than `"check the model"`.
- Reference files directly: `"Review the DAX in .agents/skills/dax-review/skill.md examples"`.
- If output is incomplete, ask: `"Continue the review from Step 3"`.
- For more example prompts see [examples/sample-prompts.md](../examples/sample-prompts.md).

---

**Next:** [Step 4 — Using Claude](04-using-claude.md) *(optional — if you prefer Claude over Copilot)*
