---
name: dax-review
description: Use when reviewing DAX measures for correctness, performance, safety, and adherence to team standards. Invoke during model development, before release, or when investigating incorrect measure values.
---

## What This Skill Does

- **Does:** Reviews DAX measures in a Power BI semantic model for correctness, performance, safety, and adherence to team standards.
- **When:** A developer asks for a DAX review, when measure values appear incorrect, or before releasing a model to production.
- **Requires:** An open model in Power BI Desktop (via MCP) or PBIP model files on disk.
- **Produces:** A structured findings report with severity ratings, covering division-by-zero risks, iterator performance, `CALCULATE` misuse, and team convention violations.
- **Does NOT:** Rewrite or fix measures — proposes corrections for the developer to apply. Does not review report visuals, model relationships, or file structure — use the `report-review`, `semantic-model-review`, or `pbip-structure` skill for those.

# DAX Review

## Overview

Analyse all DAX measures in the semantic model and produce a structured findings report. The goal is to identify measures that are incorrect, unsafe, poorly performing, or not following team standards.

**Core principle:** Review and report only. Do not rewrite measures without explicit instruction. Where rewriting is appropriate, always show both the original and the proposed version side by side.

---

## When to Use

Use this skill when:
- A developer requests a DAX review ("check the measures", "review DAX quality")
- Unexplained measure values are reported by users
- Preparing model for release to production
- Onboarding to an inherited model with unknown measure quality
- Running a release readiness check

---

## When Not to Use

- Relationship and topology issues (use `semantic-model-review`)
- Report visual layout (use `report-review`)
- Naming convention checks (use `naming-conventions`)

---

## DAX Review Workflow

### Step 1: Retrieve All Measures

Use the MCP server:
```
list_measures   → all measures with table, name, and DAX expression
```

Or from PBIP files: read `definition/measures.tmdl` or per-table TMDL files.

Group measures by table for structured review.

### Step 2: Check Each Measure

Apply the following checks to every measure:

#### Safety Checks

| Check | Rule | Severity |
|-------|------|----------|
| Division without DIVIDE | `[Numerator] / [Denominator]` is unsafe. Use `DIVIDE([Num], [Den], BLANK())` — use `0` only when zero is a meaningful business value | Critical |
| Hardcoded date values | Dates like `DATE(2023,1,1)` are brittle. Flag and suggest dynamic alternatives | Warning |
| Magic numbers | Unexplained numeric literals (e.g. `* 1.2`, `/ 52`) must be documented or extracted to a parameter | Warning |
| FILTER(ALL(...)) misuse | Using `FILTER(ALL(Table), condition)` when `CALCULATETABLE` with `REMOVEFILTERS` would be safer | Warning |
| Empty string comparisons | Comparing to `""` instead of `ISBLANK()` | Informational |

#### Context and Logic Checks

| Check | Rule | Severity |
|-------|------|----------|
| Implicit context transition | Measures called inside iterators (SUMX, AVERAGEX) without explicit `CALCULATE` | Warning |
| CALCULATE without clear filter argument | `CALCULATE([Measure])` with no filter: inside a row context (iterator) this triggers **context transition** which may be intentional; outside row context it is a no-op. Flag for review if intent is unclear | Warning |
| ALL vs ALLSELECTED | Using `ALL` where `ALLSELECTED` would preserve user slicer context | Warning |
| Time intelligence on non-Date table | `SAMEPERIODLASTYEAR`, `DATEADD` etc. used on a column that is not from a marked Date table | Warning |
| Row context without iterator | Referencing a column value directly in a measure body without an iterator | Critical |

#### Performance Checks

| Check | Rule | Severity |
|-------|------|----------|
| Deeply nested CALCULATE | More than 3 levels of nested CALCULATE — split into intermediate measures | Warning |
| Large SWITCH statements | SWITCH with more than 10 branches — consider lookup table approach | Informational |
| COUNTROWS(FILTER(...)) | Prefer `CALCULATE(COUNTROWS(...), filter condition)` for engine optimisation | Warning |
| Using VALUES() on high-cardinality columns | Can produce slow results; prefer `SELECTEDVALUE` or `HASONEVALUE` | Informational |

### Step 3: Validate Measure Naming

For each measure, check:
- Does the name clearly describe what it measures?
- Does it follow the naming convention? (see `naming-conventions` skill)
- Are units implied by the name where relevant (e.g. `Sales Amount`, `Margin %`, `Order Count`)?

### Step 4: Produce Report

Write the review output using the template in `templates/model-review-template.md` (DAX section).

---

## Severity Definitions

| Severity | Definition |
|----------|------------|
| **Critical** | Produces incorrect results or causes errors. Must be resolved before release. |
| **Warning** | Potential for incorrect results under certain filter contexts, or significant performance risk. Should be resolved. |
| **Informational** | Best practice suggestion. Low urgency but improves maintainability. |

---

## Example Finding

```
Measure: Profit Margin
Table: _Measures
DAX:
    Profit Margin = [Total Profit] / [Total Sales]

Finding: Division without DIVIDE function
Severity: Critical
Detail: If [Total Sales] evaluates to 0 or BLANK, this measure will return an error.
        This can cause visuals to show error values instead of blank or zero.
Suggested fix:
    Profit Margin = DIVIDE([Total Profit], [Total Sales], 0)
    -- Returns 0 when sales is zero; consider BLANK() instead of 0 depending on business requirements.
```

---

## Common DAX Patterns Reference

### Safe Division
```dax
Metric % = DIVIDE([Numerator Measure], [Denominator Measure], BLANK())
```

### Year-over-Year Comparison
```dax
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
```

### Running Total
```dax
Sales Running Total =
CALCULATE(
    [Total Sales],
    FILTER(
        ALL('Date'[Date]),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

### Safe Context-Aware Measure
```dax
Selected Year Sales =
IF(
    HASONEVALUE('Date'[Year]),
    CALCULATE([Total Sales], 'Date'[Year] = VALUES('Date'[Year])),
    [Total Sales]
)
```
