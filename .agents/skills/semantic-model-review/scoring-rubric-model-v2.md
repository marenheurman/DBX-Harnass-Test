# Semantic Data Model Scoring Rubric

> **Use this rubric when:** Reviewing a live, human-built Power BI semantic model — during a model review, after schema changes, or before release.
> For evaluating **AI-generated** model outputs (A/B tests, prompt quality), use `.agents/skills/score-rubric/scoring-rubric-v2.md` instead.

Apply this rubric alongside the findings from `semantic-model-review/skill.md`. Score each pillar independently, then compute the weighted total.

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

### Pillar 1 — Architectural Integrity

| Score | Criteria |
|---|---|
| 4 | Grain is explicit and correct; all PKs verified; joins are clean 1:N or 1:1 with no fan traps; logic is fully modular |
| 3 | Grain is correct but undocumented; joins are valid but cardinality not explicitly stated; minor duplication of logic across measures |
| 2 | Grain is ambiguous or incorrectly set; one or more joins risk fan traps; surrogate keys missing or inconsistent |
| 1 | Multiple broken or missing relationships; significant schema misunderstandings; model cannot produce reliable aggregations |
| 0 | No coherent schema; relationships absent or circular; model cannot function |

### Pillar 2 — Semantic Accuracy & Logic

| Score | Criteria |
|---|---|
| 4 | All aggregations match business intent; measures and dimensions correctly separated; time intelligence fully implemented |
| 3 | Aggregations mostly correct; time intelligence present but incomplete (e.g. YTD defined but no YoY); grain implied but not documented |
| 2 | Logical errors present (e.g. summing a unit price, averaging a count, wrong grain); business definitions not validated |
| 1 | Measures and dimensions confused; aggregation logic is unreliable; time intelligence absent where required |
| 0 | No distinction between metrics and attributes; model cannot produce correct numbers |

### Pillar 3 — Usability & Metadata

| Score | Criteria |
|---|---|
| 4 | Consistent naming convention throughout; every measure and ambiguous field has a description; all technical columns hidden |
| 3 | Naming mostly consistent with isolated exceptions; most fields described; majority of technical columns hidden |
| 2 | Technical or auto-generated names present (e.g. `Column1`); descriptions sparse; some plumbing columns visible to end users |
| 1 | Inconsistent naming across tables; mix of conventions; few or no descriptions; technical columns exposed |
| 0 | Cryptic, misleading, or entirely absent labels and descriptions; model is unusable by end users without documentation |

### Pillar 4 — Performance & Security

| Score | Criteria |
|---|---|
| 4 | Calculated columns minimised; iterators scoped correctly; no unnecessary complexity; PII/PHI addressed via RLS or exclusion |
| 3 | Minor performance inefficiencies (e.g. one or two avoidable calculated columns); sensitive fields flagged but not fully governed |
| 2 | Noticeable performance risks (e.g. large iterators on high-cardinality tables, nested CALCULATE); no PII governance present |
| 1 | Multiple high-cost patterns that will degrade report performance at scale; sensitive data exposed without restriction |
| 0 | Model is unacceptably slow or exposes PII/PHI with no governance controls |
