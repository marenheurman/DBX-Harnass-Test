# Sample Model Review Output

This is an example of the output produced by the `semantic-model-review` skill. It is based on a fictional Adventure Works-style sales model.

---

# Model Review — Adventure Works Sales
**Date:** 2026-03-13
**Reviewed by:** GitHub Copilot (AI-assisted)
**Skill applied:** semantic-model-review
**Model name:** AdventureWorks Sales Model
**Environment:** Development

---

## Summary

| Review Area | Critical | Warnings | Informational |
|---|---|---|---|
| Table Classification | 0 | 0 | 1 |
| Relationships | 1 | 2 | 0 |
| Star Schema Compliance | 0 | 1 | 0 |
| Date Table | 0 | 1 | 0 |
| **TOTAL** | **1** | **4** | **1** |

**Overall Verdict:** BLOCKED

---

## Model Overview

**Total tables:** 9
**Fact tables identified:** Sales, SalesTargets
**Dimension tables identified:** Customer, Product, Date, Territory, Salesperson
**Bridge tables identified:** None
**Calculated tables identified:** _Measures
**Total relationships:** 8
**Total measures:** 24

---

## Table Classification

| Table Name | Classification | Grain Statement | Notes |
|---|---|---|---|
| Sales | Fact | One row per order line per product | |
| SalesTargets | Fact | One row per salesperson per month | |
| Customer | Dimension | One row per customer | |
| Product | Dimension | One row per product | |
| Date | Dimension (Date) | One row per calendar day | Marked as Date table ✅ |
| Territory | Dimension | One row per sales territory | |
| Salesperson | Dimension | One row per salesperson | |
| _Measures | Calculated | Measure container | Expected pattern ✅ |
| ProductCategory | Dimension | One row per product category | ⚠️ See snowflake warning below |

---

## Critical Findings

### Bidirectional relationship between Sales and Customer causes ambiguous filter propagation

**Area:** Relationships
**Object:** Sales → Customer (relationship ID: R-003)
**Detail:**
The relationship between `Sales[CustomerKey]` and `Customer[CustomerKey]` is configured as bidirectional. The `Customer` table is also connected to `Territory` via a one-to-many relationship.

This creates a potential ambiguous filter path: when a Territory filter is applied, it propagates bidirectionally through Customer and into Sales. However, Sales is also directly connected to Territory via a separate relationship (R-007). This means there are two active filter paths from Territory to Sales, which Power BI must resolve arbitrarily — this can cause incorrect aggregations in measures that use Territory filters.

**Suggested action:**
Change the Sales → Customer relationship to single direction (Sales is filtered by Customer; Customer does not filter Sales). Confirm that no measure relies on Customer being filtered from the Sales direction. If a specific reverse-filter scenario is needed, implement it with a `CROSSFILTER` function in the relevant measure rather than a model-wide bidirectional setting.

---

## Warnings

### Warning 1: Direct relationship between Sales and SalesTargets

**Area:** Star Schema Compliance
**Object:** Relationship between Sales[SalespersonKey] and SalesTargets[SalespersonKey]
**Detail:**
There is an active relationship directly between the `Sales` fact table and the `SalesTargets` fact table via `SalespersonKey`. This is a fact-to-fact relationship. Although Power BI allows this, it can produce unexpected filter behaviour when both tables are filtered simultaneously.

**Suggested action:**
Route the relationship through the `Salesperson` dimension. Both `Sales` and `SalesTargets` should connect many-to-one to `Salesperson`. Measures comparing actual vs target should use `CALCULATE` to filter both tables independently rather than relying on a cross-fact relationship.

---

### Warning 2: ProductCategory table creates a snowflake structure

**Area:** Star Schema Compliance
**Object:** Table: ProductCategory; Relationship: Product → ProductCategory
**Detail:**
The `ProductCategory` table is connected to `Product` (dimension-to-dimension). This creates a snowflake structure. In this pattern, Territory slicer filters propagate: Territory → Salesperson → (broken unless bridge is used). Meanwhile, category filtering must pass through Product → ProductCategory, adding an unnecessary join hop.

**Suggested action:**
Flatten `ProductCategory` attributes into the `Product` dimension table. Add `CategoryName` and `SubcategoryName` as columns in `Product`. Remove the `ProductCategory` table. This simplifies the model and eliminates the snowflake join.

---

### Warning 3: Date table does not extend to current year + 1

**Area:** Date Table
**Object:** Table: Date
**Detail:**
The `Date` table contains dates from 2018-01-01 to 2025-12-31. Future-dated entries beyond the current year are recommended so that year-to-date and rolling window measures do not break as the current date advances. As of 2026, the Date table does not cover the current year.

**Suggested action:**
Extend the Date table to include at least 2026 and 2027. If the Date table is generated by a DAX calculated table, update the expression to use `TODAY()` as the end boundary with a +1 year buffer.

---

## Informational

### Note 1: _Measures calculated table

**Area:** Table Classification
**Object:** Table: _Measures
**Detail:**
The `_Measures` table is a calculated table used as a measure container (a common and accepted pattern). It is hidden in the model. No action required.

---

### Note 2: Inactive relationship on Date table

**Area:** Relationships
**Object:** Inactive relationship: Sales[ShipDateKey] → Date[DateKey]
**Detail:**
There is an inactive relationship from `Sales[ShipDateKey]` to the `Date` table. This is expected if there is a measure using `USERELATIONSHIP` to calculate ship-date-based time intelligence. Confirm that a corresponding measure exists.

---

## Recommended Next Steps

1. **CRITICAL — Resolve immediately:** Change Sales → Customer relationship from bidirectional to single direction to eliminate the ambiguous filter path
2. Refactor `SalesTargets` to connect via `Salesperson` dimension rather than directly to `Sales`
3. Flatten `ProductCategory` into the `Product` dimension table
4. Extend `Date` table to cover 2026–2027

---

## Sign-Off

| Role | Name | Date | Accepted? |
|---|---|---|---|
| Reviewing Developer | | | |
| BI Lead | | | |
| Project Manager | | | |
