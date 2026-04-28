# Sample Release Readiness Report

This example shows the consolidated output expected from the `release-readiness` skill.

---

# Release Readiness Report — AdventureWorks Sales

**Date:** 2026-03-18
**Reviewed by:** AI Agent (`release-readiness` skill v1.0)

---

## VERDICT: BLOCKED

One Critical issue was found in DAX and one Critical issue was found in PBIP structure. The release should not proceed until both are resolved.

---

## Summary

| Review Area | Critical | Warnings | Informational |
|---|---|---|---|
| Semantic Model | 0 | 2 | 1 |
| DAX Measures | 1 | 2 | 0 |
| Report Design | 0 | 1 | 2 |
| PBIP Structure | 1 | 2 | 1 |
| Naming Conventions | 0 | 3 | 1 |
| **TOTAL** | **2** | **10** | **5** |

---

## Critical Findings

### DAX — Profit Margin % uses direct division

**Detail:** `[Total Profit] / [Total Sales]` can return an error when sales is 0 or BLANK.

**Remediation:** Replace with `DIVIDE([Total Profit], [Total Sales], BLANK())`.

---

### PBIP Structure — Embedded credential in `Sales.tmdl`

**Detail:** A partition expression contains `password=`. This is not safe to commit or deploy.

**Remediation:** Remove the credential, rotate it, and move authentication to a secure store.

---

## Warning Findings

### Semantic Model

- Bidirectional relationship between `Sales` and `Customer`
- Snowflake chain from `Product` to `ProductSubcategory` to `ProductCategory`

### DAX Measures

- `Revenue LY` references `Sales[OrderDate]` instead of the marked Date table
- `Sales 2024 Baseline` contains a hardcoded year

### Report Design

- Overview page contains an uncertified custom visual that requires human approval before promotion

### PBIP Structure

- `.gitignore` does not exclude `.pbi/`
- `report.json` page list does not match the files under `definition/pages/`

### Naming Conventions

- `tbl_Sales` should be `Sales`
- `customer_id` should be `CustomerID`
- `New Measure` should be renamed to a business-specific measure name

---

## Informational Findings

- Date table is present and correctly marked
- Report uses the default Power BI theme
- No standalone images were found without alt text
- `roles.tmdl` is not present; confirm whether row-level security is out of scope
- Helper measures are correctly prefixed with `_`

---

## Accepted Risk Statement

This section should be completed only if the final verdict is Ready with Warnings.

```
I, <BI Lead Name>, accept the unresolved Warning findings listed in this report.
Reason for acceptance: <business justification>
Date: YYYY-MM-DD
```

---

## Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| Developer | | | |
| BI Lead | | | |
| Project Manager | | | |
