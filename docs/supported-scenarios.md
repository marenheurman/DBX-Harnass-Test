# Supported Scenarios

This document describes the tasks the **Power BI Agentic Harness** supports, which skill to invoke for each task, and what output to expect.

---

## Scenario 1: Semantic Model Review

**When to use:** Before releasing a new semantic model, after significant schema changes, when onboarding to an existing model, or when a model has unexplained report errors.

**Skill:** `.agents/skills/semantic-model-review/skill.md`

**What the agent does:**
- Lists all tables and classifies them as fact, dimension, or bridge
- Reviews all relationships for cardinality, filter direction, and ambiguity
- Identifies many-to-many relationships and flags risks
- Checks for inactive relationships and confirms they are intentional
- Validates that the model follows a star schema
- Flags snowflake structures and over-connected dimension chains
- Reports issues by severity: Critical / Warning / Informational

**Example prompt:**
```
Review the semantic model and produce a structured report using the model review template.
```

---

## Scenario 2: DAX Measure Review

**When to use:** When reviewing a new set of measures, auditing an inherited model, troubleshooting incorrect values, or enforcing DAX standards across a team.

**Skill:** `.agents/skills/dax-review/skill.md`

**What the agent does:**
- Lists all measures and their DAX expressions
- Checks for use of deprecated or unsafe functions (e.g. `FILTER` with `ALL` in the wrong context)
- Identifies measures that use implicit context transition risks
- Flags hardcoded values and magic numbers
- Checks for missing `DIVIDE` usage where division by zero is possible
- Validates measure naming against conventions
- Produces a structured findings report

**Example prompt:**
```
Review all measures in the Sales table and flag any that use FILTER(ALL(...)) incorrectly.
```

---

## Scenario 3: Report Review

**When to use:** Before publishing a report to end users, during a design review, or when accessibility or usability concerns are raised.

**Skill:** `.agents/skills/report-review/skill.md`

**What the agent does:**
- Reviews the report structure (pages, visuals, layout)
- Checks visual types against their data (e.g. multi-row card for single KPI)
- Flags overuse of slicers or unnecessary visual clutter
- Reviews tooltip usage and drill-through page setup
- Checks colour usage for accessibility (contrast, colour-blind-safe palettes)
- Validates that all visuals have titles
- Flags missing alt-text on images

**Example prompt:**
```
Review the Overview page and flag any visual design or accessibility issues.
```

---

## Scenario 4: PBIP Project Structure Analysis

**When to use:** When setting up a new PBIP project, migrating from PBIX to PBIP, or validating that a project is source-control-ready.

**Skill:** `.agents/skills/pbip-structure/skill.md`

**What the agent does:**
- Checks that the expected PBIP folder and file structure exists
- Validates that `.gitignore` excludes cache and lock files
- Checks that `model.bim` or TMDL files are present and well-formed
- Flags any embedded credentials or connection strings in partition expressions
- Confirms that the deployment pipeline configuration is present if required

**Example prompt:**
```
Check the PBIP project structure and confirm it is ready for source control.
```

---

## Scenario 5: Naming Convention Validation

**When to use:** When reviewing a model for consistency, onboarding a new contributor, or enforcing team standards after a merge.

**Skill:** `.agents/skills/naming-conventions/skill.md`

**What the agent does:**
- Lists all tables, columns, and measures
- Validates names against the conventions in this accelerator
- Flags violations with the actual name, the rule violated, and a suggested correction
- Produces a violations summary grouped by object type

**Example prompt:**
```
Check all measure names in the model for naming convention violations.
```

---

## Scenario 6: Release Readiness

**When to use:** Before deploying a model or report to a production workspace, before a client demo, or at the end of a sprint.

**Skill:** `.agents/skills/release-readiness/skill.md`

**What the agent does:**
- Runs all review skills in sequence (model, DAX, report, naming, PBIP structure)
- Produces a single consolidated readiness report
- Classifies the release as: Ready / Ready with Warnings / Blocked
- Blocked status requires at least one Critical issue to be resolved before release

**Example prompt:**
```
Run a full release readiness check and tell me if this model is safe to deploy.
```

---

## Scenario 7: Custom Visual Review

**When to use:** When a report contains one or more AppSource, organisational, or in-house custom visuals, before promoting the report to UAT or Production, or when a custom visual update has been applied.

**Skill:** `.agents/skills/report-review/skill.md` (custom visual checks are included in the report review workflow)

**What the agent does:**
- Reads the report JSON and identifies all custom visuals by name and GUID
- Classifies each visual as Certified AppSource, Organisational, or Unknown/Uncertified
- Flags any visuals that are uncertified or unrecognised as requiring human verification
- Checks that all data roles for each custom visual are populated
- Notes any custom visuals that appear to be outdated based on version metadata
- Defers rendering quality and behaviour assessment to human review

**What the agent does not do:**
- Inspect or execute the compiled JavaScript inside a custom visual package
- Validate the visual's output against business requirements
- Approve or certify a visual — this is always a human decision

**Example prompt:**
```
Review the report and identify all custom visuals. Flag any that are not certified
or do not have their data roles populated.
```

See [docs/custom-visuals.md](custom-visuals.md) for guidance on building and governing custom visuals.

---

## Out of Scope

The following scenarios are **not supported** by this accelerator and must be handled outside the agent workflow:

| Scenario | Reason |
|----------|--------|
| Publishing to Power BI Service | Requires human action; agent must not publish |
| Modifying production datasets | Out of scope for read-only agent design |
| Gateway configuration | Infrastructure concern outside model scope |
| Row-level security testing with real user credentials | Security risk |
| Automated refresh scheduling | Service-layer concern |
| Data source credential management | Credential security boundary |

---

## References

- [docs/architecture.md](architecture.md)
- [docs/governance.md](governance.md)
- [docs/custom-visuals.md](custom-visuals.md)
- [.agents/skills/semantic-model-review/skill.md](../.agents/skills/semantic-model-review/skill.md)
- [.agents/skills/dax-review/skill.md](../.agents/skills/dax-review/skill.md)
- [.agents/skills/report-review/skill.md](../.agents/skills/report-review/skill.md)
- Microsoft Learn: [Power BI Project (.pbip) overview](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- Microsoft Learn: [Power BI custom visuals overview](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals)
