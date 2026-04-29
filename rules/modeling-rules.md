# Modeling Rules

These rules define the standards for Power BI semantic model design. They are applied by the `semantic-model-review` skill and inform the architecture decisions made during model development.

---

## Star Schema Principle

Always prefer a star schema structure:
- One or more **fact tables** in the center, containing events, transactions, or measurements
- Multiple **dimension tables** surrounding the facts, providing descriptive context
- Dimension tables filter fact tables — not each other, except via bridge tables

A model that follows this principle is predictable, performant, and easy for report developers to use.

---

## Fact Table Rules

Fact tables contain measurable events or transactions.

**Characteristics:**
- Large row counts (relative to dimensions)
- Numeric columns used for aggregation (amounts, quantities, counts)
- Foreign key columns pointing to dimension tables
- A single, clearly defined grain

**Rules:**
- Every fact table must have a documented grain statement. Example: `"One row per order line per product."`
- If the grain cannot be determined, flag as Critical — modeling risk
- Fact tables must connect to dimensions via many-to-one relationships (fact side = many)
- Fact tables should not connect directly to other fact tables via active relationships
- Measures should be defined against fact tables or a dedicated measures table (commonly named `_Measures`), not against dimension tables

---

## Dimension Table Rules

Dimension tables describe the entities used to filter and group fact data.

**Characteristics:**
- Smaller row counts (relative to facts)
- Descriptive text attributes and grouping hierarchies
- A primary key column used as the relationship join key

**Rules:**
- Dimension primary keys must be unique — no duplicate key values
- Dimensions should not be chained to other dimensions unless a bridge table is required
- Avoid snowflake structures: if a dimension's attribute could be a lookup, flatten it into the dimension table instead
- Calculated columns that simply look up a value from another table are a sign of snowflaking — flag for review

---

## Date Table Rules

Every model that requires time intelligence must have a dedicated Date dimension.

**Rules:**
- The Date table must be marked as a Date table in Power BI
- It must contain contiguous dates — no gaps — covering the full range of dates in the fact data plus sufficient future dates
- It must have a date column of type `Date` used as the relationship join
- Required columns: `Date`, `Year`, `Month`, `Month Number`, `Quarter`, `Week Number`, `Day of Week`, `Is Weekend`
- Recommended columns: `Month Year` (formatted as `Jan 2026`), `Financial Year`, `Financial Quarter`
- The Date table should not be connected to fact tables via a text date key (e.g. `YYYYMM`) — use a proper `Date` column

---

## Relationship Rules

**Cardinality:**
- Fact-to-dimension: Many-to-One (fact = many)
- Dimension-to-bridge: One-to-Many or Many-to-Many via bridge
- Never create a One-to-One relationship without documented justification — these usually indicate a modeling problem

**Filter Direction:**
- Default to single-direction filtering (dimension filters fact)
- Bidirectional relationships must be explicitly justified in a comment or documentation
- Bidirectional relationships between two tables that are both connected to a third table can cause ambiguous filters — flag as Critical

**Inactive Relationships:**
- Every inactive relationship must have a corresponding DAX measure using `USERELATIONSHIP` or be documented as reserved for future use
- Unexplained inactive relationships should be flagged as Warning

**Many-to-Many:**
- Direct many-to-many relationships (M:M cardinality) must be avoided unless:
  - A bridge table approach cannot achieve the same result
  - The performance implications are understood and accepted
- Direct M:M must be explicitly documented with the business justification in the model or a review note

---

## Calculated Tables

- Calculated tables must have a documented purpose
- Calculated tables that duplicate an existing dimension (e.g. a disconnected filtered copy of a dimension) must be justified
- Calculated tables used purely as parameter inputs (e.g. `TOPN` slicer values) are acceptable but must be clearly named
- Calculated tables derived from complex DAX should be reviewed for performance — prefer data source-level transformation where possible

---

## Anti-Patterns

| Anti-Pattern | Risk | Recommended Approach |
|---|---|---|
| Fact-to-fact relationship | Incorrect aggregations | Introduce a shared conforming dimension or use a bridge |
| Snowflaked dimension chain | Ambiguous filters, poor usability | Flatten the chain into a single dimension |
| Missing Date table | Time intelligence broken | Add a dedicated marked Date table |
| Bidirectional filter everywhere | Ambiguous context propagation | Use single-direction; apply bidirectional selectively |
| Measures on dimension tables | Context transition confusion | Move measures to a dedicated measures table or fact table |
| Direct M:M without bridge | Incorrect totals | Use bridge table to resolve |
| Dimension key is not unique | Relationship cannot be created | Deduplicate or aggregate dimension source data |

---

## References

- Microsoft Learn: [Star schema guidance](https://learn.microsoft.com/power-bi/guidance/star-schema)
- Microsoft Learn: [Many-to-many relationships in Power BI](https://learn.microsoft.com/power-bi/transform-model/desktop-many-to-many-relationships)
- Microsoft Learn: [Date tables in Power BI](https://learn.microsoft.com/power-bi/guidance/model-date-tables)
- [docs/architecture.md](../docs/architecture.md)
