---
name: score-rubric
description: Use when evaluating an AI-generated semantic model output against the four-pillar rubric for structural integrity, semantic accuracy, relationship logic, and documentation. Invoke when comparing skill-assisted vs baseline Copilot responses, or when grading any generated model definition for quality assurance.
---

## What This Skill Does

- **Does:** Evaluates an AI-generated semantic model output by scoring it across four weighted pillars: structural integrity, semantic accuracy, relationship logic, and naming/documentation.
- **When:** Running a prompt evaluation comparing skill-assisted outputs against baseline outputs, or when a generated model needs a quality gate before being accepted.
- **Requires:** The generated model output as input — no live model connection is needed.
- **Produces:** A structured score report with per-pillar scores, a weighted total, and actionable justification for each score.
- **Does NOT:** Fix or rewrite the model. Does not evaluate report visuals or DAX measures — use the `report-review` or `dax-review` skill for those.

# Score Rubric

## Overview

Evaluate AI-generated semantic model outputs against a standardised four-pillar rubric. Produce a structured score report with per-pillar grades, a weighted total, and actionable justification for every score assigned.

**Core principle:** Assess and report only. Do not rewrite or fix the model. Score what is in the output, not what the author intended.

---

## When to Use

Use this skill when:
- Comparing AI-generated semantic model outputs (skill-assisted vs baseline Copilot)
- Running a prompt evaluation or A/B test on model generation quality
- Grading a generated model definition before accepting it into a project
- Auditing whether a generated model meets team standards

---

## When Not to Use

- Reviewing an existing, human-built semantic model (use `semantic-model-review`)
- Reviewing DAX measures for correctness or performance (use `dax-review`)
- Validating naming conventions in a live model (use `naming-conventions`)
- Reviewing report visuals or layout (use `report-review`)

---

## Scoring Tiers

| Score | Rating | Actionable Definition |
|---|---|---|
| 4 | Production-Ready | Perfect logic, fully documented, optimized performance, and passes all join tests |
| 3 | Minor Refactor | Technically accurate logic, but missing some descriptions or non-standard naming |
| 2 | Logic Issues | Functional code but contains semantic errors (e.g., wrong grain) that will lead to incorrect numbers |
| 1 | Structural Failure | Broken syntax, circular dependencies, or fundamental misunderstanding of the schema |
| 0 | Incomplete | Missing critical components or entirely hallucinated output |

---

## Weighted Pillars

| Pillar | Weight | Key Evaluation Points |
|---|---|---|
| A. Structural Integrity | 25% | Syntax correctness, valid references, schema adherence |
| B. Semantic Accuracy | 35% | Correct aggregations, dimension vs measure separation, grain correctness |
| C. Relationship Logic | 25% | Join cardinality (1:N), primary/foreign key alignment, no fan traps |
| D. Naming & Documentation | 15% | Human-readable names, field descriptions, metadata completeness |

**Formula:**

$$\text{Total} = (A \times 0.25) + (B \times 0.35) + (C \times 0.25) + (D \times 0.15)$$

---

## Score Rubric Workflow

### Step 1: Read the Output
Read the generated model output in full before scoring any pillar. Do not score incrementally — a full read ensures that issues in one section (e.g. a broken join discovered late) correctly affect earlier pillar scores.

### Step 2: Score Pillar A — Structural Integrity (25%)

| Score | Criteria |
|---|---|
| 4 | Perfect syntax; runs without modification; all references resolve |
| 3 | Syntax is valid but non-standard patterns used (e.g. inconsistent quoting) |
| 2 | Minor syntax errors (missing commas, casing issues) but logic is clear |
| 1 | Significant syntax errors that prevent execution without major edits |
| 0 | Total failure; broken structure or hallucinated language/syntax |

Checks to apply:
- Are all field references valid and resolvable?
- Are data types explicitly declared where required?
- Are there circular references or self-referencing fields?
- Does the output use the correct syntax for the target modeling layer (LookML, dbt, TMDL, etc.)?
- Does the structure comply with the rules in `rules/modeling-rules.md`?

### Step 3: Score Pillar B — Semantic Accuracy (35%)

| Score | Criteria |
|---|---|
| 4 | All aggregations match business intent; measures and dimensions are correctly separated; grain is explicit and correct |
| 3 | Aggregations are mostly correct; grain is implied but not documented |
| 2 | Logical errors present (e.g. summing a unit price, averaging a count, wrong grain) |
| 1 | Measures and dimensions confused; aggregation logic is unreliable |
| 0 | No distinction between metrics and attributes; output cannot produce correct numbers |

Checks to apply:
- Are SUM, AVG, COUNT, and COUNTD applied to the correct field types?
- Are price/rate fields averaged (not summed) when appropriate?
- Are count fields using COUNTD where distinct count is the business intent?
- Is the declared grain consistent with the fields present in the model?
- Are any fields that should be measures exposed as dimensions, or vice versa?
- Do aggregation patterns follow the rules in `rules/dax-rules.md` (Division Safety, CALCULATE Usage, Iterator Performance)?

### Step 4: Score Pillar C — Relationship Logic (25%)

| Score | Criteria |
|---|---|
| 4 | Explicit join types (Left/Inner); cardinality stated; no risk of fan traps or chasm traps |
| 3 | Joins are present and correct but join type or cardinality is not explicitly stated |
| 2 | Joins are present but cardinality is ambiguous or potentially incorrect |
| 1 | Joins are missing or implied; risk of incorrect aggregations across tables |
| 0 | Missing joins, circular dependencies, or joins that produce row multiplication |

Checks to apply:
- Are all join types (LEFT, INNER, FULL) explicitly declared?
- Is cardinality (1:N, N:1, 1:1) documented or inferable without ambiguity?
- Are foreign keys joining to primary keys (not to non-unique fields)?
- Would any join produce a fan trap (fact-to-fact join via a shared dimension)?
- Are there any tables with no join path to a fact table (orphaned dimensions)?
- Do relationships follow the cardinality and filter direction rules in `rules/modeling-rules.md` (Relationship Rules section)?

### Step 5: Score Pillar D — Naming & Documentation (15%)

| Score | Criteria |
|---|---|
| 4 | Agreed naming convention used consistently; every field has a human-readable label and description |
| 3 | Naming convention mostly followed; most fields labelled but descriptions sparse |
| 2 | Technical or system-generated names (e.g. `col_a1`, `fk_001`) with no descriptions |
| 1 | Inconsistent naming; mix of conventions within the same model |
| 0 | Cryptic, misleading, or entirely absent labels and descriptions |

Checks to apply:
- Is a single naming convention applied consistently (snake_case, camelCase, PascalCase)?
- Do field names describe what the field contains, not how it is stored?
- Are there descriptions for every measure and for dimensions where the name alone is insufficient?
- Are monetary fields labelled with currency (e.g. `revenue_usd`, not just `revenue`)?
- Are date fields clearly typed and named (e.g. `order_date`, not `date1`)?
- Do names comply with the conventions defined in `.agents/skills/naming-conventions/skill.md`?

### Step 6: Calculate the Weighted Score

Apply the formula:

$$\text{Total} = (A \times 0.25) + (B \times 0.35) + (C \times 0.25) + (D \times 0.15)$$

Map the result to the scoring tier:

| Weighted Score | Rating |
|---|---|
| 3.5 – 4.0 | Production-Ready |
| 2.5 – 3.4 | Minor Refactor |
| 1.5 – 2.4 | Logic Issues |
| 0.5 – 1.4 | Structural Failure |
| 0.0 – 0.4 | Incomplete |

### Step 7: Produce the Evaluation Report

Output the report in the following format — no deviation:

```markdown
## Semantic Model Evaluation Report

**Model evaluated:** [name or description of the output being evaluated]
**Evaluated by:** AI Agent (skill: score-rubric)
**Date:** YYYY-MM-DD

---

### Pillar Scores

| Pillar | Weight | Raw Score (0–4) | Weighted Contribution |
|---|---|---|---|
| A. Structural Integrity | 25% | [score] | [score × 0.25] |
| B. Semantic Accuracy | 35% | [score] | [score × 0.35] |
| C. Relationship Logic | 25% | [score] | [score × 0.25] |
| D. Naming & Documentation | 15% | [score] | [score × 0.15] |
| **Weighted Total** | | | **[total] / 4.0** |

**Rating:** [Production-Ready / Minor Refactor / Logic Issues / Structural Failure / Incomplete]

---

### Justification

#### A. Structural Integrity — [score]/4
[What is correct. What is broken. Specific line or field reference where possible.]

#### B. Semantic Accuracy — [score]/4
[What aggregations are correct. What is wrong and why it will produce incorrect numbers.]

#### C. Relationship Logic — [score]/4
[What joins are correct. What is missing, ambiguous, or risky.]

#### D. Naming & Documentation — [score]/4
[What naming is good. What is missing or non-standard.]

---

### Critical Findings

[Bullet list of the most important issues that must be fixed before this output can be used. Be specific: name the field, the table, the join, or the rule that is violated.]

### What Would Raise This Score

[Concrete, actionable list of exactly what needs to change to move from the current rating to the next tier.]
```

### Step 8: Comparison Mode (Optional)

When evaluating two outputs side by side (e.g. skill-assisted vs baseline), score each output independently using Steps 1–7, then produce an additional comparison section:

```markdown
### Side-by-Side Comparison

| Pillar | Output A (Baseline) | Output B (Skill-Assisted) | Delta |
|---|---|---|---|
| A. Structural Integrity | [score] | [score] | [+/- difference] |
| B. Semantic Accuracy | [score] | [score] | [+/- difference] |
| C. Relationship Logic | [score] | [score] | [+/- difference] |
| D. Naming & Documentation | [score] | [score] | [+/- difference] |
| **Weighted Total** | **[total]** | **[total]** | **[+/- difference]** |

### Where the Skill-Assisted Output Improved
[Specific improvements with field/table references]

### Where the Skill-Assisted Output Did Not Improve or Regressed
[Specific areas where baseline was equal or better]

### Verdict
[One-sentence summary: which output is closer to production-ready and why]
```

Do not average the two scores. The comparison is qualitative — the delta table and narrative sections are the deliverable.

---

## Agent Behaviour Rules
- Score every pillar independently before calculating the total — do not adjust a pillar score to make the total land on a round number
- Be specific in justifications — "naming is poor" is not sufficient; name the specific fields or patterns that are non-compliant
- Do not award partial credit for intent — score what is in the output, not what the author appeared to be trying to do
- A score of 4 in any pillar must be fully justified — defaulting to 4 when no issues are found is not sufficient; state positively what makes it production-ready
- If the output is ambiguous (e.g. the target modeling layer is unclear), state the assumption made before scoring

---

## Boundary Rules for Borderline Scores

When a pillar falls between two score levels, apply these tiebreakers:

| Situation | Rule |
|---|---|
| Issue affects correctness of query results | Round down |
| Issue is cosmetic or stylistic only | Round up |
| Issue affects some tables/fields but not others | Score based on the majority; note the exceptions in justification |
| Issue is present but documented by the author as intentional | Round up, but flag the documentation in justification |
| Unsure whether an issue is a defect or a design choice | Round down and explain the ambiguity in justification |

Additional guidance:
- If more than 50% of fields in a pillar meet the criteria for a given score, assign that score — do not average across individual fields
- A single Critical-severity issue (e.g. a fan trap, a circular dependency) caps that pillar at a maximum score of 2, regardless of how many other checks pass
- When the output covers multiple tables, score each table mentally, then assign the pillar score based on the weakest table — a model is only as strong as its weakest join

---

## Failure Conditions
- If the input is too incomplete to score any pillar, output a score of 0 for all pillars with a note explaining what is missing
- If the modeling layer or target platform cannot be determined, state the assumption and proceed — do not refuse to score

---

## Example Evaluation

The following is a worked example showing how an output scoring 2.65 (Minor Refactor) is evaluated:

**Input:** A generated TMDL semantic model for an e-commerce dataset with 3 fact tables (Orders, Returns, Web Sessions) and 4 dimensions (Customer, Product, Date, Store).

### Pillar Scores

| Pillar | Weight | Raw Score (0–4) | Weighted Contribution |
|---|---|---|---|
| A. Structural Integrity | 25% | 3 | 0.75 |
| B. Semantic Accuracy | 35% | 2 | 0.70 |
| C. Relationship Logic | 25% | 3 | 0.75 |
| D. Naming & Documentation | 15% | 3 | 0.45 |
| **Weighted Total** | | | **2.65 / 4.0** |

**Rating:** Minor Refactor

### Justification

#### A. Structural Integrity — 3/4
All table and column definitions use valid TMDL syntax. Data types are declared for all columns. One issue: the `Web Sessions` table uses inconsistent quoting for column names (`'session_id'` vs `session_id` without quotes). This does not break execution but is non-standard.

#### B. Semantic Accuracy — 2/4
`Total Revenue` correctly uses `SUMX(Orders, Orders[Quantity] * Orders[UnitPrice])`. However, `Avg Unit Price` is defined as `SUM(Product[UnitPrice])` instead of `AVERAGE(Product[UnitPrice])` — this will return incorrect values. The `Returns` table grain is not documented; the presence of both `OrderKey` and `LineItemKey` columns suggests the grain is one row per returned line item, but the `Return Count` measure uses `COUNTROWS(Returns)` without confirming this is the intended grain.

#### C. Relationship Logic — 3/4
All fact-to-dimension joins use Many-to-One cardinality with single-direction filtering, which is correct. Join types are not explicitly stated (LEFT vs INNER) — the agent assumes LEFT joins, which is the Power BI default, but this should be documented. No fan traps or orphaned dimensions detected.

#### D. Naming & Documentation — 3/4
Measure names use sentence case consistently (`Total Revenue`, `Return Rate %`). Most dimension columns have descriptions. Two gaps: the `Date` table columns `FY` and `FQ` are abbreviated without descriptions — `Financial Year` and `Financial Quarter` would be clearer. No currency suffix on monetary fields (`revenue` instead of `revenue_usd`).

### Critical Findings
- `Avg Unit Price` uses SUM instead of AVERAGE — will return incorrect values in any visual
- `Returns` table grain is undocumented — `Return Count` may double-count if grain assumption is wrong

### What Would Raise This Score
- Fix `Avg Unit Price` aggregation from SUM to AVERAGE → Pillar B rises to 3
- Document the grain of the `Returns` table → Pillar B rises to 3
- Add explicit join type declarations (LEFT/INNER) → Pillar C rises to 4
- Expand `FY`/`FQ` column names and add currency suffixes → Pillar D rises to 4
- With these changes, the weighted total would rise from 2.65 to approximately 3.50 (Production-Ready)
