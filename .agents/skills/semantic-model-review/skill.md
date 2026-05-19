---
name: semantic-model-review
description: Use when reviewing a Power BI semantic model for structural correctness, relationship quality, and adherence to star schema principles. Invoke before release, after schema changes, or during model onboarding.
---

## What This Skill Does

- **Does:** Analyses the Power BI semantic model and produces a structured review report identifying structural, relational, and design issues that could cause incorrect aggregations, ambiguous filter propagation, or poor query performance.
- **When:** A developer requests a model review, before a release to production, when onboarding to an inherited model, or when investigating unexplained measure values or report errors.
- **Requires:** An open model in Power BI Desktop (via MCP) or PBIP model files on disk (`definition/model.bim` or TMDL files).
- **Produces:** A structured findings report with severity ratings covering table classification, relationships, star schema compliance, and Date table validation.
- **Does NOT:** Modify the model. All findings are proposals for the developer to act on.

# Semantic Model Review

## Overview

Analyse the Power BI semantic model and produce a structured review report. The goal is to identify structural, relational, and design issues that could cause incorrect aggregations, ambiguous filter propagation, or poor query performance.

**Core principle:** Detect and report issues. Do not modify the model. All findings are proposals for the developer to act on.

---

## When to Use

Use this skill when:
- A developer requests a model review ("review the model", "check the relationships")
- Preparing for a release to production
- Onboarding to an inherited or unfamiliar model
- Investigating unexplained measure values or report errors
- Running a release readiness check

---

## When Not to Use

- DAX measure quality (use the `dax-review` skill)
- Report visual layout (use the `report-review` skill)
- Naming convention checks (use the `naming-conventions` skill)

---

## Semantic Model Review Workflow

### Step 1: Gather Model Metadata

Use the MCP server to collect:
```
list_tables          → all tables in the model
list_relationships   → all relationships with cardinality and direction
list_columns         → columns per table (to assess grain and keys)
list_measures        → count of measures per table
```

If working from PBIP files, read:
- `definition/model.bim` or TMDL files in `definition/tables/`
- `definition/relationships.tmdl`

### Step 2: Classify Tables

For each table, classify it as one of:
- **Fact table** — large, contains numeric measures and foreign keys
- **Dimension table** — descriptive attributes, used to filter facts
- **Bridge table** — resolves many-to-many between dimensions (keys only)
- **Calculated table** — DAX-generated, flag purpose and risk
- **Unknown** — flag for human review

### Step 3: Review Relationships

For each relationship, check:

| Check | Rule | Severity if Violated |
|-------|------|----------------------|
| Cardinality is appropriate | Fact-to-dim should be many-to-one | Critical |
| Filter direction | Single direction preferred; bidirectional only if justified | Warning |
| No relationship chains between dimensions | Dimensions should not filter each other via chains | Warning |
| Many-to-many relationships | Must use bridge table; direct M:M requires justification | Critical |
| Inactive relationships | Must have a DAX measure using `USERELATIONSHIP` or be documented as intentional | Warning |
| Ambiguous filter paths | Two paths between same tables = ambiguous filters | Critical |

### Step 4: Validate Star Schema Compliance

Check:
- Is there a central fact table?
- Do all dimensions connect directly to the fact table?
- Are there snowflake structures (dimension-to-dimension chains)? Flag each one.
- Are there multiple fact tables? If so, verify conforming dimensions are shared correctly.

### Step 5: Check Date Table

- Is there a dedicated Date/Calendar dimension?
- Is it marked as a Date table in the model?
- Does it have contiguous dates covering the full data range?
- Are standard time intelligence columns present (Year, Month, Quarter, Week)?

### Step 6: Produce Report

Write the review output using the template in `templates/model-review-template.md`.

---

## Severity Definitions

| Severity | Definition |
|----------|------------|
| **Critical** | Causes incorrect results or blocks report use. Must be resolved before release. |
| **Warning** | May cause confusion, poor performance, or maintenance risk. Should be resolved. |
| **Informational** | Observation or best practice suggestion. Low urgency. |

---

## Example Finding

```
Finding: Bidirectional relationship between Sales and Product
Severity: Warning
Detail: The relationship between Sales[ProductKey] and Product[ProductKey] is set to bidirectional.
        This can cause ambiguous filter propagation if additional tables are connected to Product.
        Review whether bidirectional filtering is necessary, or restrict to single direction.
Suggested action: Change to single direction (Product filters Sales — dimension filters fact)
                  unless there is a specific requirement for Sales to filter Product.
```
