---
name: measure-table
description: Use when creating or reviewing the dedicated measures table in a Power BI semantic model. Covers when to create it, how to name and structure it, which base measures to always define first, how to layer derived measures on top, and how to organise measures into display folders. Invoke during any model build before creating DAX measures, or when reviewing an existing model for measure organisation.
---

## What This Skill Does

- **Does:** Defines the structure, naming, and content standards for the dedicated measures table in a Power BI semantic model. Produces a complete, ordered measure set from base measures up through derived KPI measures, organised into display folders.
- **When:** During a model build (invoke before writing any DAX), or when reviewing an existing model where measures are scattered across tables or inconsistently structured.
- **Requires:** Knowledge of the fact table(s) in the model and the business domain KPIs needed.
- **Produces:** A `_Measures` table definition and a complete ordered measure set with correct DAX, format strings, display folders, and descriptions.
- **Does NOT:** Review DAX correctness or performance in detail — use the `dax-review` skill for that.

---

## When to Use

- During any model build, after tables and relationships are defined and before any measures are written
- When inherited model has measures scattered across fact and dimension tables
- When running a release readiness check (called by `release-readiness` skill)
- When a business stakeholder requests new KPIs — use this skill to determine where and how to add them

---

## When Not to Use

- Reviewing detailed DAX logic, performance, or correctness (use `dax-review`)
- Reviewing report visual layout or measure usage in visuals (use `report-review`)

---

## Rule 1 — Always Use a Dedicated Measures Table

**Rule:** All measures must live in a single dedicated table named `_Measures`. Measures must never be placed directly on fact tables or dimension tables.

**Why:** Measures scattered across tables are hard to find, hard to govern, and confuse report developers. A single `_Measures` table makes the field pane predictable and enforces a clear separation between data (tables) and logic (measures).

**How to create it via MCP:**
```
Create a calculated DAX table:
  Name: _Measures
  Expression: ROW("Placeholder", BLANK())

Then immediately hide the auto-generated Placeholder column.
```

**Naming rule (from naming-conventions skill):**
- `_` prefix groups the table at the bottom of the field pane, below all data tables
- PascalCase: `_Measures` not `_measures` or `Measures`

---

## Rule 2 — Define Base Measures First

Base measures are simple, single-column aggregations. They must be defined before any derived measure references them.

**Required base measures for every fact table:**

| Pattern | Example | Format String |
|---|---|---|
| `SUM` of primary value column | `Total Sales` | `#,0.00` |
| `SUM` of cost/expense column | `Total Cost` | `#,0.00` |
| `COUNT` or `DISTINCTCOUNT` of transaction key | `Total Orders` | `#,0` |
| `SUM` of quantity column (if present) | `Total Quantity` | `#,0` |

**DAX pattern:**
```dax
Total Sales = SUM( FactTable[SalesAmount] )
Total Cost  = SUM( FactTable[TotalProductCost] )
Total Orders = DISTINCTCOUNT( FactTable[OrderNumber] )
Total Quantity = SUM( FactTable[OrderQuantity] )
```

**Rules:**
- Use `SUM` for additive numeric columns
- Use `DISTINCTCOUNT` for transaction/order counts — never `COUNT` on a key column
- Never reference another measure inside a base measure — base measures are leaf nodes
- Always assign a `formatString` — never leave it as the default

---

## Rule 3 — Layer Derived Measures on Top of Base Measures

Derived measures compute ratios, differences, or aggregations of base measures. They must reference base measures — never raw column references.

**Required derived measures for sales/revenue domains:**

| Measure | Expression | Format String |
|---|---|---|
| `Gross Profit` | `[Total Sales] - [Total Cost]` | `#,0.00` |
| `Gross Profit %` | `DIVIDE( [Gross Profit], [Total Sales] )` | `0.00%` |
| `Avg Order Value` | `DIVIDE( [Total Sales], [Total Orders] )` | `#,0.00` |

**DAX rules (from dax-rules.md):**
- Always use `DIVIDE([numerator], [denominator])` — never `/`
- `DIVIDE` returns `BLANK()` when denominator is zero — this is correct default behaviour
- Only use `DIVIDE([n], [d], 0)` when zero is a meaningful business value (rare)

```dax
-- ✅ Correct
Gross Profit %  = DIVIDE( [Gross Profit], [Total Sales] )

-- ❌ Unsafe
Gross Profit %  = [Gross Profit] / [Total Sales]
```

---

## Rule 4 — Time Intelligence Measures (when Date table is present)

If the model has a `Date` table marked as a Date table, add time intelligence measures for each primary value measure.

**Standard time intelligence set per KPI:**

| Measure | Expression |
|---|---|
| `Total Sales YTD` | `CALCULATE( [Total Sales], DATESYTD( 'Date'[Date] ) )` |
| `Total Sales PY` | `CALCULATE( [Total Sales], SAMEPERIODLASTYEAR( 'Date'[Date] ) )` |
| `Total Sales YoY` | `[Total Sales] - [Total Sales PY]` |
| `Total Sales YoY %` | `DIVIDE( [Total Sales YoY], [Total Sales PY] )` |

**Rules:**
- Time intelligence measures require the `Date` table to be marked as a Date table in Power BI
- Always use `DATESYTD` over `TOTALYTD` — it is more composable inside `CALCULATE`
- `PY` suffix = prior year, `YTD` suffix = year-to-date, `YoY` suffix = year-on-year delta

---

## Rule 5 — Display Folders

Every measure must be assigned to a display folder. Never leave measures at the root level of the `_Measures` table.

**Standard folder structure:**

| Folder | Contains |
|---|---|
| `Sales` | Base measures: `Total Sales`, `Total Orders`, `Total Quantity`, `Total Cost` |
| `Profitability` | Derived margin measures: `Gross Profit`, `Gross Profit %`, `Avg Order Value` |
| `Time Intelligence` | YTD, PY, YoY measures |
| `KPIs` | Composite or executive-level KPI measures |

**Rules:**
- Folder names are PascalCase
- A measure belongs to exactly one folder — do not duplicate across folders
- Intermediate/helper measures (prefixed with `_`) go in a `_Supporting` folder and should be hidden

---

## Rule 6 — Intermediate (Helper) Measures

Intermediate measures are used to simplify complex DAX. They must be:
- Prefixed with `_` (e.g. `_Sales Filtered`)
- Hidden from the report view (`isHidden: true`)
- Placed in a `_Supporting` display folder

```dax
-- Hidden intermediate measure
_Sales Filtered = CALCULATE( [Total Sales], Product[Status] = "Current" )

-- Visible derived measure that uses it
Active Product Sales = [_Sales Filtered]
```

---

## Rule 7 — Measure Naming Conventions

| Pattern | Convention | Example |
|---|---|---|
| Base aggregation | `Total [Thing]` | `Total Sales`, `Total Orders` |
| Ratio / percentage | `[Thing] %` | `Gross Profit %`, `Return Rate %` |
| Year-to-date | `[Measure] YTD` | `Total Sales YTD` |
| Prior year | `[Measure] PY` | `Total Sales PY` |
| Year-on-year delta | `[Measure] YoY` | `Total Sales YoY` |
| Year-on-year % | `[Measure] YoY %` | `Total Sales YoY %` |
| Average | `Avg [Thing]` | `Avg Order Value`, `Avg Basket Size` |
| Count | `Total [Things]` | `Total Orders`, `Total Customers` |
| Hidden intermediate | `_[Description]` | `_Sales Base`, `_Cost Adjusted` |

**Anti-patterns to avoid:**
- ❌ `SalesSum`, `SalesTotal` — direction of word order is inconsistent
- ❌ `Measure1`, `KPI_01` — non-descriptive
- ❌ `gross profit %` — lowercase
- ❌ `GrossProfit%` — no space before `%`

---

## Measure Creation Order (Mandatory Sequence)

Always create measures in this order. MCP `measure_operations Create` must follow this sequence because derived measures reference base measures:

```
1. Base measures      (SUM, DISTINCTCOUNT — no cross-measure references)
2. Derived measures   (reference base measures only)
3. Time intelligence  (reference base or derived measures)
4. KPI measures       (reference any of the above)
5. Hidden intermediates (if needed — created alongside the measures that need them)
```

---

## Complete Example — Internet Sales Domain

```dax
-- FOLDER: Sales (Base)
Total Sales    = SUM( InternetSales[SalesAmount] )
Total Cost     = SUM( InternetSales[TotalProductCost] )
Total Orders   = DISTINCTCOUNT( InternetSales[SalesOrderNumber] )
Total Quantity = SUM( InternetSales[OrderQuantity] )

-- FOLDER: Profitability (Derived)
Gross Profit   = [Total Sales] - [Total Cost]
Gross Profit % = DIVIDE( [Gross Profit], [Total Sales] )
Avg Order Value = DIVIDE( [Total Sales], [Total Orders] )

-- FOLDER: Time Intelligence
Total Sales YTD  = CALCULATE( [Total Sales], DATESYTD( 'Date'[FullDateAlternateKey] ) )
Total Sales PY   = CALCULATE( [Total Sales], SAMEPERIODLASTYEAR( 'Date'[FullDateAlternateKey] ) )
Total Sales YoY  = [Total Sales] - [Total Sales PY]
Total Sales YoY % = DIVIDE( [Total Sales YoY], [Total Sales PY] )
```

---

## Checklist

Before completing the measure table step of a model build, confirm:

- [ ] `_Measures` table exists as a calculated table with `ROW("Placeholder", BLANK())`
- [ ] Placeholder column is hidden
- [ ] All measures are in `_Measures` — none on fact or dimension tables
- [ ] Base measures created before derived measures
- [ ] All numeric measures have `formatString` assigned
- [ ] All percentage measures use `DIVIDE` — no `/` operator
- [ ] Every measure is in a display folder — none at root level
- [ ] Hidden intermediate measures are prefixed with `_` and set to `isHidden: true`
- [ ] Measure names follow the naming convention table above
- [ ] All measures have a `description` property explaining their business purpose
