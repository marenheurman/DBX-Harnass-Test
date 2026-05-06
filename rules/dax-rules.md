# DAX Rules

These rules define the standards for writing, reviewing, and maintaining DAX measures in Power BI semantic models. They are applied by the `dax-review` skill.

---

## Core Principles

1. **Correctness above performance** — a fast but wrong measure is worse than a slow correct one
2. **Explicit context** — never rely on implicit or surprising filter context behaviour
3. **No silent errors** — measures must never return division errors, type errors, or blank values that appear as zeros without intent
4. **Readability** — DAX is business logic; it must be readable by a BI developer unfamiliar with the original implementation

---

## Division Safety

**Rule:** Never use the `/` operator for division without guarding against zero denominators.

```dax
-- ❌ Unsafe
Margin % = [Gross Profit] / [Total Sales]

-- ✅ Safe: returns BLANK when denominator is zero
Margin % = DIVIDE([Gross Profit], [Total Sales])

-- ✅ Safe: returns 0 when denominator is zero (if 0 is the correct business value)
Margin % = DIVIDE([Gross Profit], [Total Sales], 0)
```

- Use `BLANK()` as the alternate result when the measure is not applicable (most cases)
- Use `0` as the alternate result only when zero is a meaningful business value

---

## CALCULATE Usage

`CALCULATE` modifies filter context. Use it intentionally.

**Rules:**
- Do not write `CALCULATE([Measure])` with no filters — this is usually a mistake or redundant
- When using `ALL`, be explicit about whether you intend to remove user-applied slicer filters or only model-defined filters
  - `ALL(Table)` removes all filters from the table, including user slicers
  - `ALLSELECTED(Table)` preserves user slicer context and removes only row/column context
- When nesting `CALCULATE`, keep nesting to a maximum of 3 levels — extract intermediate measures instead

```dax
-- ❌ Too deeply nested — extract intermediate measures
Total YTD Adjusted =
CALCULATE(
    CALCULATE(
        CALCULATE(
            [Total Sales],
            DATESYTD('Date'[Date])
        ),
        REMOVEFILTERS(Territory)
    ),
    ExchangeRate[Currency] = "USD"
)

-- ✅ Better: use intermediate measures
_Sales YTD = CALCULATE([Total Sales], DATESYTD('Date'[Date]))
_Sales YTD All Territories = CALCULATE([_Sales YTD], REMOVEFILTERS(Territory))
Total YTD Adjusted = CALCULATE([_Sales YTD All Territories], ExchangeRate[Currency] = "USD")
```

---

## FILTER Usage

`FILTER` is a row iterator. It should be used when you need to apply a complex condition that cannot be expressed as a simple `CALCULATE` argument.

**Rules:**
- Prefer `CALCULATE([Measure], Table[Column] = value)` over `CALCULATE([Measure], FILTER(Table, Table[Column] = value))` for simple comparisons
- Avoid `FILTER(ALL(Table), ...)` unless you need to remove all existing filters on the table before applying the new filter condition — this is a common source of bugs

```dax
-- ❌ Inefficient for simple filter
High Value Orders = CALCULATE([Order Count], FILTER(Sales, Sales[Amount] > 10000))

-- ✅ Correct — let the engine optimise the filter argument
High Value Orders = CALCULATE([Order Count], Sales[Amount] > 10000)
```

---

## Iterator Performance

Iterators such as `SUMX`, `AVERAGEX`, `COUNTX`, and `FILTER` evaluate an expression for every row in the table passed as their first argument. When applied directly to large fact tables, this can produce slow query results and high memory consumption.

**Rules:**
- Prefer iterating over dimension tables rather than large fact tables where possible
- Use pre-aggregated base measures as the expression inside an iterator instead of referencing raw columns
- Avoid nesting one iterator inside another on the same large table

```dax
-- ❌ Slow — iterates every row in a multi-million row fact table
Avg Order Value = AVERAGEX(Sales, Sales[Quantity] * Sales[UnitPrice])

-- ✅ Better — iterate over the smaller Orders dimension, sum within each order first
Avg Order Value =
AVERAGEX(
    VALUES(Sales[OrderKey]),
    CALCULATE(SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]))
)
```

When in doubt, test query performance using Performance Analyser in Power BI Desktop before finalising an iterator-based measure

---

## REMOVEFILTERS vs ALL

Both `ALL` and `REMOVEFILTERS` can be used inside `CALCULATE` to clear existing filters. They behave differently in important cases.

**Rule:** Use `REMOVEFILTERS()` when the intent is to remove filters. Reserve `ALL()` for when you need to return a table of all values as a filter argument.

| Function | Primary purpose | Behaviour in CALCULATE |
|---|---|---|
| `ALL(Table)` | Return all rows of a table, ignoring filters | Clears filters AND returns a table — can cause unintended side effects |
| `REMOVEFILTERS(Table)` | Remove filters from a table or column | Clears filters only — intent is explicit and unambiguous |

```dax
-- ❌ Using ALL when filter removal is the intent
All Customers Revenue = CALCULATE([Total Revenue], ALL(Customer))

-- ✅ Preferred — REMOVEFILTERS makes intent explicit
All Customers Revenue = CALCULATE([Total Revenue], REMOVEFILTERS(Customer))

-- ✅ ALL is appropriate here — passing a table of values as a filter
All Products In Table = CALCULATE([Total Revenue], FILTER(ALL(Product), Product[Colour] = "Red"))
```

---

## Context Transition

When a measure is called inside a row iterator (`SUMX`, `AVERAGEX`, etc.), each row creates a row context. Calling a measure inside that row context triggers a **context transition** — the row context is converted to an equivalent filter context.

This is powerful but can produce unexpected results with high-cardinality columns.

**Rules:**
- Always use explicit `CALCULATE([Measure])` when intentionally triggering context transition inside an iterator
- Columns used in a measure body must be aggregated (e.g. `SUM`, `MAX`, `MIN`) or evaluated within an iterator or context modifier — a bare column reference in a measure has no row context and will cause an error

```dax
-- ❌ Error — a bare column reference has no row context in a measure
Order Profit = Sales[Revenue] - Sales[Cost]

-- ❌ Redundant — this simply delegates to [Total Sales] and is not useful as a standalone measure.
-- It will not error, but it adds no value and can confuse developers.
Each Customer Sales = [Total Sales]

-- ✅ Correct — aggregate the columns explicitly in the measure body
Order Profit = SUM(Sales[Revenue]) - SUM(Sales[Cost])

-- ✅ Correct — iterate customers and trigger context transition for a per-row measure call
Each Customer Total = SUMX(Customer, CALCULATE([Total Sales]))
```

---

## Time Intelligence Rules

- All time intelligence functions (`SAMEPERIODLASTYEAR`, `DATEADD`, `DATESYTD`, etc.) must be applied to a column from a table that is **marked as a Date table** in the model
- Do not apply time intelligence to transaction date columns in fact tables
- Always test time intelligence measures with a year slicer and a month matrix to confirm correct period alignment
- `DATESYTD` defaults to calendar year (January 1). Pass the fiscal year end date as a second argument for fiscal year YTD

```dax
-- Fiscal year YTD ending 30 June
Revenue Fiscal YTD = CALCULATE([Total Revenue], DATESYTD('Date'[Date], "06-30"))
```

---

## Calculated Columns vs Measures

Calculated columns and measures serve different purposes. Mixing these up is a common source of model bloat, incorrect results, and poor performance.

**Rules:**
- **Calculated columns** must only contain row-level logic — operations that produce a value based on other columns in the same row
- **Aggregations** across multiple rows (sums, averages, counts, ratios) must always be implemented as measures
- Do not implement a calculated column to pre-aggregate data that should be calculated at query time by a measure
- Calculated columns consume model memory (they are materialised at refresh time); measures are computed on demand

```dax
-- ✅ Correct use of a calculated column: row-level arithmetic
-- In the Sales table, as a calculated column:
Line Total = Sales[Quantity] * Sales[UnitPrice]

-- ❌ Wrong: aggregation logic in a calculated column
-- This returns a wrong result — SUMX in a calc column iterates the full table for every row
Total Revenue (Wrong) = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])

-- ✅ Correct: aggregation belongs in a measure
Total Revenue = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
```

---

## Hardcoded Values and Magic Numbers

**Rules:**
- Do not hardcode year values, exchange rates, tax rates, or thresholds directly in measure expressions
- Numeric literals that represent business rules (e.g. `* 1.1` for a 10% markup) must be extracted to a named parameter table or configuration measure with a descriptive name
- Date literals (e.g. `DATE(2023, 1, 1)`) should use dynamic expressions or parameter tables instead

```dax
-- ❌ Magic number — what is 1.15?
Adjusted Revenue = [Total Sales] * 1.15

-- ✅ Named intermediate measure with clear purpose
_FX Adjustment Factor = 1.15  -- or from a parameter table
Adjusted Revenue = [Total Sales] * [_FX Adjustment Factor]
```

---

## Measure Organisation

- All measures should reside in either the relevant fact table or a dedicated measures table (commonly named `_Measures`)
- Do not scatter measures across dimension tables
- Group related measures by prefix or display folder:
  - `Sales | Total Sales`, `Sales | Sales YTD`, `Sales | Sales LY`
  - `Margin | Gross Margin`, `Margin | Gross Margin %`
- Helper / intermediate measures that are not intended for report use should be hidden and prefixed with `_`

---

## Measure Reuse

Complex measures should be built from simpler, reusable base measures rather than written as monolithic expressions. This principle reduces duplication, makes logic easier to audit, and ensures that a change to a core calculation propagates consistently across all dependent measures.

**Rules:**
- Define base measures for fundamental aggregations (`Total Sales`, `Total Cost`, `Order Count`) before building derived measures on top of them
- Derived measures should reference base measures, not duplicate their logic
- If the same expression appears in more than one measure, extract it into a named base measure or intermediate variable

```dax
-- ✅ Base measure — defined once
Total Sales = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])

-- ✅ Derived measures reference the base
Gross Profit = [Total Sales] - [Total Cost]
Gross Margin % = DIVIDE([Gross Profit], [Total Sales])
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))
Sales vs LY % = DIVIDE([Total Sales] - [Sales LY], [Sales LY])

-- ❌ Avoid — logic duplicated across measures, inconsistency risk
Gross Profit = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice]) - [Total Cost]
```

---

## Explicit Measures

Power BI creates **implicit measures** automatically when a numeric column is dragged into a visual — for example, an automatic `Sum of Sales Amount`. Implicit measures are not visible in the model field list, cannot have custom formatting or descriptions, and cannot be reused.

**Rule:** All aggregations used in reports must be defined as explicit named measures. Implicit measures must not be used in production reports.

---

**Rules:**
- Define a named measure for every aggregation that will appear in a visual
- Disable implicit measures on fact table numeric columns by marking them as `Hidden` or by defining the explicit measure and hiding the source column
- Numeric columns in fact tables that are only used as inputs to measures (not as standalone visuals) should be hidden from report view

```dax
-- ✅ Explicit measure — named, formatted, discoverable, reusable
Total Sales =
    SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
-- Format: Currency, 2 decimal places
-- Display folder: Sales
-- Description: Total sales revenue before discounts

-- ❌ Implicit measure — no formatting, no description, no reuse
-- (Sales[Revenue] column dragged directly into a visual — Power BI auto-creates "Sum of Revenue")
```

---

## Variable Usage

Use `VAR` and `RETURN` to store intermediate results within a measure. Variables improve readability, prevent repeated evaluation of the same sub-expression, and make complex logic easier to debug.

**Rules:**
- Use variables whenever the same sub-expression is referenced more than once within a measure
- Use variables to give meaningful names to intermediate values that would otherwise be anonymous inline expressions
- Variables are evaluated once at the point they are declared — they do not re-evaluate with each row in an iterator, which can also improve performance
- Always use `RETURN` to clearly separate variable declarations from the final expression

```dax
-- ❌ Without variables — expression repeated, harder to read and maintain
Sales vs Target % =
    IF(
        ISBLANK(CALCULATE([Total Sales], 'Date'[Year] = YEAR(TODAY()))),
        BLANK(),
        DIVIDE(
            CALCULATE([Total Sales], 'Date'[Year] = YEAR(TODAY())) -
            CALCULATE([Sales Target], 'Date'[Year] = YEAR(TODAY())),
            CALCULATE([Sales Target], 'Date'[Year] = YEAR(TODAY()))
        )
    )

-- ✅ With variables — each value computed once, intent is clear
Sales vs Target % =
VAR CurrentYearSales   = CALCULATE([Total Sales],    'Date'[Year] = YEAR(TODAY()))
VAR CurrentYearTarget  = CALCULATE([Sales Target],   'Date'[Year] = YEAR(TODAY()))
VAR Variance           = CurrentYearSales - CurrentYearTarget
RETURN
    IF(
        ISBLANK(CurrentYearTarget) || CurrentYearTarget = 0,
        BLANK(),
        DIVIDE(Variance, CurrentYearTarget)
    )
```

**Additional variable usage guidance:**
- Name variables descriptively — `SalesAmount` is better than `x` or `v1`
- Prefix variables with a capital letter or use camelCase to distinguish them from measure references: `VAR SalesAmt` vs `[Total Sales]`
- Do not use variables to store table expressions that are only needed once — inline them for clarity unless the table expression is complex
- Variables capture filter context at the point of declaration. Be aware that a `VAR` declared outside an iterator holds a scalar value, not a row-context-sensitive expression

---

## Formatting Standards

Format DAX expressions for readability:
- One argument per line for functions with multiple arguments
- Indent nested functions consistently (4 spaces or 1 tab)
- Use blank lines to separate logical blocks within a complex measure
- Use `--` inline comments to explain non-obvious logic

```dax
-- Good formatting example
Sales vs Target % =
VAR SalesAmount = [Total Sales]
VAR TargetAmount = [Sales Target]
RETURN
    IF(
        ISBLANK(TargetAmount) || TargetAmount = 0,
        BLANK(),
        DIVIDE(SalesAmount - TargetAmount, TargetAmount)
    )
```

---

## References

- Microsoft Learn: [DAX reference](https://learn.microsoft.com/dax/)
- Microsoft Learn: [CALCULATE function](https://learn.microsoft.com/dax/calculate-function-dax)
- Microsoft Learn: [DIVIDE function](https://learn.microsoft.com/dax/divide-function-dax)
- Microsoft Learn: [REMOVEFILTERS function](https://learn.microsoft.com/dax/removefilters-function-dax)
