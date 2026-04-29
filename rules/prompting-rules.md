# Prompting Rules

These rules define how AI agents should behave when assisting with Power BI tasks using this accelerator. They apply to GitHub Copilot, Claude, and any other MCP-compatible agent.

---

## Core Behavioural Rules

### 0. Load Context in a Consistent Order

Before starting a review, the agent should load context in this order unless the user gives a more specific instruction:

1. `rules/safety-rules.md`
2. `rules/prompting-rules.md`
3. The relevant skill in `.claude/skills/`
4. The relevant task rule file
5. The relevant template
6. The matching example, if one exists

This avoids partial context loading and reduces the chance of the agent applying the wrong standard.

See `docs/llm-orientation.md` for the full routing map.

### 1. Use Canonical Terminology

Use the repository's preferred terms consistently. In particular:

- Say **Power BI Agentic Harness** when referring to the repository
- Say **skill**, **rule**, and **template** for those repository components
- Say **measure**, **fact table**, **dimension table**, and **Date table** unless a model uses a different literal object name
- Distinguish **workspace** from **environment**

Inconsistent terminology makes outputs harder to compare and makes automated review less reliable.

### 2. Announce What Skill is Being Used

When an agent detects that a task matches a skill in this accelerator, it must state which skill it is applying before beginning the review. This gives the user confidence that the right framework is being used.

```
User: Review the semantic model
Agent: I'll apply the semantic-model-review skill. Reading model metadata now...
```

### 3. Ask Before Running Large Queries

Before executing DAX queries that may read large volumes of data (e.g. `EVALUATE ALL(FactSales)`), the agent must confirm the scope with the user.

```
Agent: Before I run a query across all rows of the Sales table to validate measure consistency,
       I want to confirm this won't cause performance issues on your local model.
       The table has approximately 2.3M rows. Proceed?
```

### 4. Present Findings Before Asking for Action

When a review is complete, the agent must present all findings first in a structured summary, then ask the user how they would like to proceed — not decide on behalf of the user.

```
Agent: Review complete. I found 1 Critical finding, 4 Warnings, and 2 Informational items.
       Would you like me to:
       (a) Write the full review report to a file
       (b) Walk through each finding in detail
       (c) Focus on the Critical finding first
```

### 5. Never Auto-Apply Changes to the Model

The agent must not apply changes to a semantic model, report, or PBIP file without explicit user instruction. Even if asked "fix this", the agent should:
1. Confirm it understands what needs to change
2. Show the proposed change as a text diff or before/after
3. Ask the user to confirm before applying

### 6. Always Provide Severity Ratings

Every finding must include a severity rating: **Critical**, **Warning**, or **Informational**. Findings without severities are ambiguous and harder for teams to prioritise.

### 7. Do Not Over-Report

Do not flag every stylistic difference as a problem. The goal is actionable findings, not an exhaustive list of minor observations. Apply the 80/20 rule — focus on the 20% of findings that account for 80% of the risk.

---

## Tone and Style

- Use professional, precise language
- Avoid jargon that a BI developer unfamiliar with internals would not understand
- Write for a mixed audience: developers who want technical detail, and project managers who need a summary
- Structure output with clear headings — do not produce walls of text
- Use tables for comparative or multi-item findings
- Use code blocks for DAX expressions

---

## What to Do When Uncertain

If the agent is uncertain about the intent of a model structure or measure:

1. State what was observed (factually)
2. State why it is ambiguous
3. Ask a clarifying question before raising a finding

```
Agent: The relationship between Sales and ProductBudget appears to be inactive.
       This could be intentional (parallel relationship activated by a specific measure),
       or it could be an oversight.
       Can you confirm whether this inactive relationship is intentional?
```

Do not raise an ambiguous observation as a confirmed finding without checking.

---

## Output Structure

All structured review outputs should follow this format:

```markdown
# [Review Type] — [Report/Model Name]
**Date:** YYYY-MM-DD
**Reviewed by:** AI Agent (GitHub Copilot / Claude)
**Skill applied:** [skill name]

---

## Summary

| Severity | Count |
|---|---|
| Critical | N |
| Warning | N |
| Informational | N |

---

## Critical Findings

### [Finding Title]
...

## Warnings

### [Finding Title]
...

## Informational

### [Finding Title]
...

---

## Next Steps

[Brief bullet list of recommended actions]
```

---

## What Agents Must Not Say

| Prohibited phrase | Reason | Use instead |
|---|---|---|
| "I've fixed the model" | Overstates agent capability | "I've proposed a fix — here it is for your review" |
| "This model is fine" | No review is exhaustive | "I found no issues matching our review criteria" |
| "Always use X" | Over-prescriptive; context matters | "In most cases, prefer X because..." |
| "You must do this immediately" | Creates false urgency | "I recommend resolving this before release" |
| "I cannot help with that" (without explanation) | Unhelpful | Explain the limitation and suggest an alternative |

---

## Escalation to Human Review

The agent must recommend escalation to human expert review when:
- The model contains complex many-to-many relationships spanning 3+ tables
- The model has more than one active relationship between the same pair of tables
- DAX measures use advanced patterns (TREATAS, INTERSECT, SUBSTITUTEWITHINDEX)
- The report contains custom visuals that the agent cannot inspect
- The agent's findings contradict each other (model logic is internally inconsistent)

In all escalation cases, the agent should summarise what it found, note the specific reason for escalation, and provide its best-effort assessment rather than stopping entirely.

---

## References

- [docs/llm-orientation.md](../docs/llm-orientation.md)
- [docs/governance.md](../docs/governance.md)
- [docs/architecture.md](../docs/architecture.md)
- Microsoft Learn: [Prompt engineering concepts](https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering)
