---
name: release-readiness
description: Use when performing a full pre-release assessment of a Power BI semantic model and report. Runs all review skills in sequence and produces a consolidated readiness verdict. Invoke immediately before deploying to production.
---

# Release Readiness

## Overview

Run a full, consolidated quality assessment of a Power BI project by invoking all component skills in sequence. Produce a single readiness report that classifies the release as **Ready**, **Ready with Warnings**, or **Blocked**.

**Core principle:** This skill orchestrates other skills. Do not skip any step. Do not classify a release as Ready if any Critical finding is unresolved.

---

## When to Use

Use this skill when:
- Preparing to deploy a model or report to a production workspace
- Before presenting a model to a client or stakeholder for the first time
- At the end of a sprint as a quality gate
- When a BI lead requests a full sign-off review

---

## Readiness Classification

| Classification | Criteria |
|----------------|----------|
| **Blocked** | One or more Critical findings exist across any review area. Release must not proceed until resolved. |
| **Ready with Warnings** | No Critical findings. One or more Warnings exist. Release may proceed with documented accepted risks. |
| **Ready** | No Critical findings and no Warnings. All checks passed. |

---

## Release Readiness Workflow

### Step 1: Run Semantic Model Review

Follow the full instructions in `.agents/skills/semantic-model-review/skill.md`.

Collect all findings. Record count of Critical, Warning, and Informational items.

### Step 2: Run DAX Review

Follow the full instructions in `.agents/skills/dax-review/skill.md`.

Collect all findings. Record count of Critical, Warning, and Informational items.

### Step 3: Run Report Review

Follow the full instructions in `.agents/skills/report-review/skill.md`.

Collect all findings. Record count of Critical, Warning, and Informational items.

### Step 4: Run PBIP Structure Check

Follow the full instructions in `.agents/skills/pbip-structure/skill.md`.

Collect all findings. Record count of Critical, Warning, and Informational items.

### Step 5: Run Naming Convention Check

Follow the full instructions in `.agents/skills/naming-conventions/skill.md`.

Collect all findings. Record count of Critical, Warning, and Informational items.

### Step 6: Deduplicate and Resolve Conflicts

Before aggregating, review findings from all sub-skills for duplicates and contradictions:

- **Deduplication:** If the same object is flagged by two sub-skills (e.g., a measure flagged by both semantic-model-review and dax-review), keep the finding under the skill whose scope is the better fit and remove the duplicate. Attribute it to the owning skill.
- **Severity conflicts:** If two sub-skills assign different severities to the same issue, use the higher severity and note the discrepancy in the finding detail.
- **Contradictions:** If two sub-skills produce contradictory findings about the same object (e.g., one says a pattern is correct, the other flags it), escalate the contradiction to the Critical findings section with both positions stated and flag it for human review.

### Step 7: Aggregate Results

Produce a summary table:

| Review Area | Critical | Warnings | Informational |
|-------------|----------|----------|---------------|
| Semantic Model | 0 | 2 | 1 |
| DAX Measures | 1 | 3 | 0 |
| Report Design | 0 | 1 | 2 |
| PBIP Structure | 0 | 0 | 1 |
| Naming Conventions | 0 | 4 | 0 |
| **TOTAL** | **1** | **10** | **4** |

### Step 8: Determine Verdict

- If any Critical count is > 0: Verdict = **BLOCKED**
- If no Criticals but any Warnings: Verdict = **READY WITH WARNINGS**
- If no Criticals and no Warnings: Verdict = **READY**

### Step 9: Write Readiness Report

The report must include:

1. **Verdict** (large, prominent heading)
2. **Summary table** (from Step 7)
3. **Critical findings** (if any) — must be listed in full with remediation instructions
4. **Warning findings** — grouped by review area
5. **Accepted risk statement** (for Ready with Warnings) — if the BI lead accepts any Warnings, they must document this acceptance with their name and date
6. **Informational findings** — listed briefly
7. **Sign-off table**:

```
| Role         | Name | Date | Signature |
|---|---|---|---|
| Developer    |      |      |           |
| BI Lead      |      |      |           |
| Project Manager |   |      |           |
```

Save the report to `reviews/YYYY-MM-DD-release-readiness.md` in the project repository.

---

## Example Verdict Output

```
# Release Readiness Report
**Project:** Adventure Works Sales Model
**Date:** 2026-03-13
**Reviewed by:** GitHub Copilot (AI-assisted review)

---

## VERDICT: BLOCKED

One Critical finding must be resolved before this release proceeds.

---

## Summary

| Review Area | Critical | Warnings | Informational |
|---|---|---|---|
| Semantic Model | 0 | 2 | 1 |
| DAX Measures | 1 | 2 | 0 |
| Report Design | 0 | 1 | 1 |
| PBIP Structure | 0 | 0 | 0 |
| Naming Conventions | 0 | 3 | 0 |
| TOTAL | 1 | 8 | 2 |

---

## Critical Findings (must resolve before release)

### DAX — Profit Margin measure: Division without DIVIDE
The measure `[Profit Margin]` uses direct division: `[Total Profit] / [Total Sales]`.
If [Total Sales] is 0 or BLANK, this returns an error value, which will appear in all visuals
using this measure.

**Remediation:** Replace with `DIVIDE([Total Profit], [Total Sales], BLANK())`
```
