# Semantic Data Model Scoring Rubric

Use this rubric when assigning a quality score to a Power BI semantic model during a model review. Apply it alongside the findings from `semantic-model-review/skill.md`. Score each pillar independently, then compute the weighted total.

---

## Pillar 1 — Architectural Integrity (30%)

| Criterion | Evaluation Question |
|---|---|
| Granularity | Does the model accurately represent the grain of the underlying fact tables? (e.g. one row per transaction vs one row per day) |
| Primary Keys | Are unique identifiers explicitly defined and verified? |
| Join Logic | Are joins correctly defined as 1:1, 1:N, or M:N? Does the model avoid Fan Traps and Chasm Traps? |
| DRY Principle | Is the logic modular? Does it avoid repeating SQL calculations across different measures? |

---

## Pillar 2 — Semantic Accuracy & Logic (30%)

| Criterion | Evaluation Question |
|---|---|
| Measures vs Dimensions | Are quantitative values (revenue, counts) correctly separated from qualitative attributes (dates, categories)? |
| Aggregation Consistency | Are measures using the correct functions? (e.g. `DISTINCTCOUNT` for active users rather than `SUM`) |
| Time Intelligence | Are date dimensions formatted for time-series analysis (YoY, MoM, YTD)? |
| Calculated Logic | Do complex business logic formulas (e.g. "Net Profit") align with the official business definition? |

---

## Pillar 3 — Usability & Metadata (20%)

| Criterion | Evaluation Question |
|---|---|
| Naming Conventions | Are names human-readable and consistent? (e.g. `total_order_amount` vs `amt_raw_x`) |
| Descriptions | Does every field have metadata explaining its source and purpose for the end-user? |
| Hidden Fields | Are internal keys, surrogate IDs, and technical "plumbing" columns hidden from the final reporting layer? |

---

## Pillar 4 — Performance & Security (20%)

| Criterion | Evaluation Question |
|---|---|
| Filter Optimisation | Does the model leverage partitioned columns or indexed fields for common filters? |
| Complexity | Are there unnecessary CTEs or nested subqueries that will degrade query performance? |
| Governance | Are sensitive fields (PII/PHI) appropriately flagged or excluded? |

---

## Scoring Tiers

| Score | Rating | Actionable Definition |
|---|---|---|
| 4 | Production-Ready | Perfect logic, fully documented, optimized performance, and passes all join tests |
| 3 | Minor Refactor | Technically accurate logic, but missing some descriptions or non-standard naming |
| 2 | Logic Issues | Functional code but contains semantic errors (e.g. wrong grain) that will lead to incorrect numbers |
| 1 | Structural Failure | Broken syntax, circular dependencies, or fundamental misunderstanding of the schema |
| 0 | Incomplete | Missing critical components or entirely hallucinated output |

---

## Weighted Calculation

Score each pillar on a scale of 0–4, then apply the formula:

$$\text{Total} = (P1 \times 0.30) + (P2 \times 0.30) + (P3 \times 0.20) + (P4 \times 0.20)$$

**Maximum score:** 4.0 (Production-Ready across all pillars)

---

## Detailed Grading Criteria

### [A] Structural Integrity
| Score | Criteria |
|---|---|
| 4 | Perfect syntax; runs without modification; all references resolve |
| 2 | Minor syntax errors (missing commas, casing issues) but logic is clear |
| 0 | Total failure; broken structure or hallucinated language |

### [B] Semantic Accuracy
| Score | Criteria |
|---|---|
| 4 | Aggregations match business intent; measures are not confused with dimensions |
| 2 | Logical errors present (e.g. summing a unit price instead of averaging it) |
| 0 | No distinction between metrics and attributes |

### [C] Relationship Logic
| Score | Criteria |
|---|---|
| 4 | Explicit join types (Left/Inner); cardinality stated; no risk of Fan Traps |
| 2 | Joins are present but cardinality is ambiguous |
| 0 | Missing joins, circular dependencies, or joins that produce row multiplication |

### [D] Naming & Documentation
| Score | Criteria |
|---|---|
| 4 | `total_revenue_usd` style naming with clear field descriptions throughout |
| 2 | Technical names (e.g. `col_a1`) with no descriptions |
| 0 | Cryptic or misleading labels |
