# Sample Naming Convention Review

This example shows the expected output of the `naming-conventions` skill for a fictional model with mixed naming quality.

---

## Review Output

| Field | Value |
|---|---|
| Model | AdventureWorks Sales |
| Review date | 2026-03-18 |
| Reviewed by | AI Agent (`naming-conventions` skill v1.0) |
| Scope | Tables, columns, measures, and hierarchies |

---

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| Warning | 7 |
| Informational | 2 |
| Overall verdict | Naming cleanup recommended before release |

---

## Warnings

### Tables

| Object | Issue | Suggested correction |
|---|---|---|
| `tbl_Sales` | Prefix `tbl_` violates table naming convention | `Sales` |
| `dim_customer` | Snake case and prefix both violate convention | `Customer` |
| `Query1` | Generic imported query name | Rename to the business entity represented |

---

### Columns

| Object | Issue | Suggested correction |
|---|---|---|
| `Sales[customer_id]` | Snake case and inconsistent key suffix | `CustomerID` |
| `Sales[Date]` | Reserved word in DAX and too generic | `OrderDate` |

---

### Measures

| Object | Issue | Suggested correction |
|---|---|---|
| `_Measures[New Measure]` | Default Power BI measure name | Rename to the actual business metric |
| `_Measures[TotalSales]` | PascalCase used instead of Title Case | `Total Sales` |

---

## Informational Findings

| Object | Observation | Suggested improvement |
|---|---|---|
| `_Measures[_Filtered Customer Count]` | Helper measure naming is valid | Consider hiding the measure if it is only used internally |
| `Date[Calendar Hierarchy]` | Hierarchy name is valid and descriptive | No change required |

---

## Recommended Next Steps

1. Rename generic imported tables before additional development continues.
2. Normalise key and date column naming across fact and dimension tables.
3. Review all existing measures for Title Case and explicit unit suffixes where relevant.
