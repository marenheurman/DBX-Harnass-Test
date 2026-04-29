# Sample DAX Review Output

This is an example of the output produced by the `dax-review` skill for a set of measures from a fictional Adventure Works-style sales model.

---

# DAX Review — Adventure Works Sales Model
**Date:** 2026-03-13
**Reviewed by:** GitHub Copilot (AI-assisted)
**Skill applied:** dax-review
**Scope:** All measures in the _Measures table
**Total measures reviewed:** 12

---

## Summary

| Severity | Count |
|---|---|
| Critical | 1 |
| Warning | 4 |
| Informational | 2 |

**Verdict:** BLOCKED — 1 Critical finding must be resolved before release.

---

## Critical Findings

### [Profit Margin %] — Division without DIVIDE

**Table:** _Measures
**DAX expression:**
```dax
Profit Margin % = [Total Profit] / [Total Sales]
```

**Issue:**
Direct division using `/` without `DIVIDE`. When `[Total Sales]` evaluates to `0` or `BLANK()` (which occurs for customers with no sales in the selected period), DAX returns a division error. This error propagates to every visual using this measure, causing table rows and chart points to display `(Blank)` or `Error` instead of a value.

This measure is used in 6 visuals across the Sales Overview and Regional Performance pages.

**Severity:** Critical — causes error values in production visuals

**Proposed fix:**
```dax
Profit Margin % =
DIVIDE(
    [Total Profit],
    [Total Sales],
    BLANK()
)
-- BLANK() is appropriate here: a product with zero sales has no calculable margin.
-- If 0% is the required business value for zero-sales periods, replace BLANK() with 0.
```

---

## Warnings

### Warning 1: [Sales LY] — Time intelligence applied to Sales table date column

**Table:** _Measures
**DAX expression:**
```dax
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Sales[OrderDate]))
```

**Issue:**
`SAMEPERIODLASTYEAR` is applied to `Sales[OrderDate]`, which is a column in the fact table, not the `Date` dimension table. Time intelligence functions behave unpredictably when applied to non-Date-table columns: they do not benefit from the marked Date table's contiguous date range logic, and results can differ from the values expected by users comparing against calendar month summaries.

**Severity:** Warning — may produce incorrect results in filtered contexts

**Proposed fix:**
```dax
Sales LY =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)
-- Ensure Sales[OrderDateKey] is related to Date[DateKey] via an active relationship.
```

---

### Warning 2: [Sales Target Achievement %] — Hardcoded threshold value

**Table:** _Measures
**DAX expression:**
```dax
Sales Target Achievement % =
IF(
    DIVIDE([Total Sales], [Sales Target]) >= 0.9,
    "On Track",
    "At Risk"
)
```

**Issue:**
The threshold value `0.9` (90%) is hardcoded directly in the measure. If the business changes the threshold definition, every related measure and visual must be manually updated. There is also no explanation inline for why 90% is the boundary.

**Severity:** Warning — maintainability risk, no documentation

**Proposed fix — option A (parameter table):**
Create a single-row parameter table `_Config` with a `TargetThreshold` row, then reference it:
```dax
Sales Target Achievement % =
VAR Threshold = CALCULATE(MAX(_Config[Value]), _Config[Parameter] = "TargetThreshold")
RETURN
    IF(DIVIDE([Total Sales], [Sales Target]) >= Threshold, "On Track", "At Risk")
```

**Proposed fix — option B (named hidden measure):**
```dax
_Target Threshold = 0.9  -- 90%: defined by Sales Ops; update here if threshold changes
Sales Target Achievement % =
IF(DIVIDE([Total Sales], [Sales Target]) >= [_Target Threshold], "On Track", "At Risk")
```

---

### Warning 3: [Customer Count Active] — FILTER(ALL(...)) misuse

**Table:** _Measures
**DAX expression:**
```dax
Customer Count Active =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerKey]),
    FILTER(ALL(Customer), Customer[Status] = "Active")
)
```

**Issue:**
`FILTER(ALL(Customer), ...)` removes all existing filters from the `Customer` table and applies only the `Status = "Active"` condition. This means any user-applied slicer on `Customer` (such as filtering by Region or Segment) will be ignored when this measure is evaluated. This is almost certainly not the intended behaviour.

**Severity:** Warning — user slicer context is silently ignored

**Proposed fix:**
```dax
Customer Count Active =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerKey]),
    Customer[Status] = "Active"
)
-- This preserves all user slicer filters on Customer while adding the Status condition.
```

---

### Warning 4: [Average Order Value] — Deeply nested CALCULATE

**Table:** _Measures
**DAX expression:**
```dax
Average Order Value =
CALCULATE(
    CALCULATE(
        CALCULATE(
            DIVIDE(SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]), DISTINCTCOUNT(Sales[OrderKey])),
            Sales[OrderType] = "Standard"
        ),
        REMOVEFILTERS(Territory)
    ),
    'Date'[Year] = 2025
)
```

**Issue:**
Three nested `CALCULATE` calls make this measure very difficult to read and maintain. The innermost calculation also hardcodes the year 2025, making it stale immediately.

**Severity:** Warning — maintainability and correctness risk

**Proposed fix — extract intermediate measures:**
```dax
_Standard Order Revenue =
CALCULATE(
    SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]),
    Sales[OrderType] = "Standard"
)

_Standard Order Count =
CALCULATE(
    DISTINCTCOUNT(Sales[OrderKey]),
    Sales[OrderType] = "Standard"
)

Average Order Value =
CALCULATE(
    DIVIDE([_Standard Order Revenue], [_Standard Order Count]),
    REMOVEFILTERS(Territory)
)
-- Note: Year = 2025 hardcode removed. Apply year filter via slicer or report filter instead.
```

---

## Informational

### Info 1: [Total Sales] — Consider adding a FORMAT display folder

**Table:** _Measures
**DAX expression:**
```dax
Total Sales = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
```

**Observation:**
The measure is correctly written. However, it has no display folder assigned. As the measure count grows, grouping measures into display folders (e.g. `Sales`, `Margin`, `Customer`, `Time Intelligence`) makes the field list easier to navigate for report developers.

---

### Info 2: [_Selected Salesperson] — Helper measure correctly hidden

**Table:** _Measures
**DAX expression:**
```dax
_Selected Salesperson = SELECTEDVALUE(Salesperson[SalespersonName], "All Salespeople")
```

**Observation:**
This helper measure is correctly prefixed with `_` and is hidden in the model. It follows the convention for intermediate measures not intended for use in report visuals. No action required.

---

## Measures Reviewed — Full List

| Measure | Table | Finding | Severity |
|---|---|---|---|
| Profit Margin % | _Measures | Division without DIVIDE | Critical |
| Sales LY | _Measures | Time intelligence on fact date column | Warning |
| Sales Target Achievement % | _Measures | Hardcoded threshold | Warning |
| Customer Count Active | _Measures | FILTER(ALL(...)) removes user context | Warning |
| Average Order Value | _Measures | Deeply nested CALCULATE + hardcoded year | Warning |
| Total Sales | _Measures | Consider display folder | Informational |
| _Selected Salesperson | _Measures | Correctly implemented helper measure | ✅ Pass |
| Total Profit | _Measures | No issues found | ✅ Pass |
| Order Count | _Measures | No issues found | ✅ Pass |
| Revenue YTD | _Measures | No issues found | ✅ Pass |
| Revenue MTD | _Measures | No issues found | ✅ Pass |
| Gross Margin % | _Measures | Uses DIVIDE correctly | ✅ Pass |
