---
name: naming-conventions
description: Use when validating or enforcing naming conventions for Power BI tables, columns, measures, and hierarchies. Invoke during model review, after a merge, or when onboarding to an inherited model.
---

## What This Skill Does

- **Does:** Validates names across the semantic model — tables, columns, measures, and hierarchies — against the conventions defined in this document and produces a structured violations report.
- **When:** A developer requests a naming check, after merging changes from multiple contributors, during onboarding to an inherited model, or when running a release readiness check.
- **Requires:** An open model in Power BI Desktop (via MCP) or PBIP model files on disk.
- **Produces:** A structured violations report grouped by severity and object type, with the exact object name, the rule violated, and a suggested correction for each finding.
- **Does NOT:** Rename objects in the model directly. The developer applies corrections.

# Naming Conventions

## Overview

Validate names across the semantic model — tables, columns, measures, and hierarchies — against the conventions defined in this document. Produce a structured violations report.

**Core principle:** Report violations with the exact object name, the rule violated, and a suggested correction. Do not rename objects in the model directly. The developer applies corrections.

---

## When to Use

Use this skill when:
- A developer requests a naming check ("check the naming", "validate conventions")
- Onboarding to an inherited model
- After merging changes from multiple contributors
- Running a release readiness check (called automatically by `release-readiness` skill)

---

## When Not to Use

- Reviewing model structure or relationships (use `semantic-model-review`)
- Reviewing DAX measure correctness or performance (use `dax-review`)
- Reviewing report visual design (use `report-review`)
- Validating PBIP project file structure (use `pbip-structure`)

---

## Naming Convention Reference

### Tables

| Object Type | Convention | Examples |
|-------------|------------|---------|
| Fact table | PascalCase, no prefix | `Sales`, `OrderLines`, `Inventory` |
| Dimension table | PascalCase, no prefix | `Customer`, `Product`, `Date`, `Territory` |
| Bridge table | PascalCase, noun describing the relationship | `CustomerSegmentBridge`, `ProductCategoryMap` |
| Calculated table | PascalCase, prefixed with `_` to group at bottom | `_DateTable`, `_MeasureSupport` |
| Parameter table | PascalCase, suffixed with `Parameter` or `Config` | `TopNParameter`, `CurrencyConfig` |
| Hidden support table | PascalCase, prefixed with `_` | `_RLSControl`, `_Disconnected` |

**Anti-patterns to avoid:**
- ❌ `tbl_Sales`, `DIM_Customer`, `FACT_Orders` — prefixes are unnecessary in Power BI
- ❌ `sales`, `customer` — lowercase table names are unconventional in Power BI
- ❌ `table1`, `Sheet1`, `Query1` — generic names from data source connection

---

### Columns

| Convention | Rule | Example |
|------------|------|---------|
| PascalCase | All words capitalised | `OrderDate`, `ProductCategory`, `CustomerKey` |
| No type suffixes | Do not suffix with `_ID`, `_KEY`, `_DT` | Use `CustomerID` not `Customer_ID_INT` |
| Boolean columns | Prefix with `Is` or `Has` | `IsActive`, `HasDiscount` |
| Date columns | Suffix with `Date` when it is a date | `OrderDate`, `ShipDate`, `BirthDate` |
| Surrogate keys | Suffix with `Key` | `CustomerKey`, `ProductKey` |
| Natural/business keys | Suffix with `ID` | `CustomerID`, `OrderNumber` |
| Flag/status columns | Be explicit | `OrderStatus` not just `Status` |

**Anti-patterns to avoid:**
- ❌ `customer_id` — snake_case is a database convention, not a Power BI convention
- ❌ `ORDERDATE` — all caps is not used in Power BI column names
- ❌ `Col1`, `Column A`, `Field_3` — generic names from flat files
- ❌ `Date` as a column name — reserved word in DAX

---

### Measures

| Convention | Rule | Example |
|------------|------|---------|
| Title Case | All words capitalised | `Total Sales`, `Profit Margin %`, `Order Count` |
| Include units when relevant | Append unit to distinguish measures of the same entity | `Sales Amount`, `Sales Quantity`, `Sales Margin %` |
| Percentage measures | Suffix with `%` or ` Pct` | `Gross Margin %`, `Return Rate Pct` |
| Year-over-year measures | Suffix with `LY` (Last Year) or `PY` (Prior Year) | `Sales LY`, `Profit PY` |
| Month-to-date measures | Suffix with `MTD` | `Sales MTD` |
| Year-to-date measures | Suffix with `YTD` | `Revenue YTD` |
| Rolling window measures | Include the window size | `Sales 3M Rolling`, `Orders 12M Rolling` |
| Helper / intermediate measures | Prefix with `_` to group and hide | `_Selected Year`, `_Filtered Customer Count` |

**Anti-patterns to avoid:**
- ❌ `measure1`, `New Measure`, `Copy of Total Sales` — default Power BI names
- ❌ `TotalSales`, `totalSales` — PascalCase or camelCase; use Title Case for readability
- ❌ `Sales/Revenue` — slash in measure names causes DAX parsing issues in some contexts
- ❌ `% Margin` — start the name with the entity, end with the unit: `Margin %`

---

### Hierarchies

| Convention | Rule | Example |
|------------|------|---------|
| PascalCase | All words capitalised | `Calendar Hierarchy`, `Product Hierarchy` |
| Describe the hierarchy path | Name should imply the drill path | `Year > Quarter > Month` → `Calendar Hierarchy` |
| Avoid generic names | Do not use `Hierarchy 1` | Use `Geography Hierarchy` |

---

## Naming Conventions Workflow

### Step 1: Retrieve All Object Names

```
list_tables     → all table names
list_columns    → all column names per table
list_measures   → all measure names per table
```

Or from PBIP files: read TMDL files for each table.

### Step 2: Apply Checks

For each object name:
- Check against the conventions in this document
- Record: Object type, Full name (Table[Column] or Table[Measure]), Rule violated, Suggested name

### Step 3: Produce Violations Report

Group violations by severity and object type:

```
CRITICAL (blocks release)
  - None

WARNINGS (<violations count>)
  Tables
    - "tbl_Sales" → violates: no prefix convention → suggested: "Sales"
  Measures
    - "measure1" → violates: descriptive name required → suggested: rename to describe what is measured

INFORMATIONAL
  Columns
    - "Date" in table "Sales" → reserved word in DAX → suggested: "OrderDate" or "SaleDate"
```

---

## Example Finding

```
Object: Measure — [New Measure] in table [_Measures]
Finding: Generic default measure name
Severity: Warning
Rule violated: Measure names must clearly describe what is measured
Suggested correction: Rename to reflect the business metric this measure calculates,
                      e.g., 'Total Sales Amount', 'Customer Count', 'Average Order Value'
```
