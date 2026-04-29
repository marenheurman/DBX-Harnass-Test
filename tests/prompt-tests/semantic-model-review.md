# Prompt Tests — Semantic Model Review Skill

This file contains validation scenarios for the `semantic-model-review` skill. Each scenario describes a model state, the expected prompt behaviour, and the expected output. Use these when testing changes to the skill or onboarding new AI agent integrations.

---

## How to Use These Tests

For each scenario:
1. Set up your Power BI model to match the described state (or load the scenario description into the agent as context)
2. Issue the prompt shown
3. Compare the agent output against the expected output

Tests are graded as: **Pass** (matches expected), **Partial** (finds some issues but misses others), or **Fail** (incorrect or missing output).

---

## Test 001 — Bidirectional relationship detection

### Model State
The model contains two tables: `Sales` (fact) and `Customer` (dimension). The relationship between them is set to bidirectional. No other tables are connected to `Customer`.

### Prompt
```
Review the semantic model relationships and flag any potential issues.
```

### Expected Output

The agent should:
- Identify the bidirectional relationship between Sales and Customer
- Classify it as a **Warning** (not Critical, because no additional table is connected to Customer that would create an ambiguous second path)
- Explain that bidirectional filtering allows Customer to filter Sales, which may be intentional or may be unnecessary
- Suggest changing to single direction unless there is a specific requirement

### Pass Criteria
- [ ] Bidirectional relationship is mentioned by name
- [ ] Severity is Warning (not Critical for a single bidirectional without ambiguity)
- [ ] A remedy is suggested

---

## Test 002 — Many-to-many relationship without bridge table

### Model State
The model has a direct many-to-many relationship between `Sales[ProductKey]` and `Product[ProductKey]`, configured with M:M cardinality in Power BI.

### Prompt
```
Review the model and flag any relationship design issues.
```

### Expected Output

The agent should:
- Identify the M:M relationship
- Classify it as **Critical**
- Explain that M:M relationships can cause incorrect aggregations (double-counting, cross-filtering issues)
- Suggest introducing a bridge table or investigating whether the relationship should be many-to-one (indicating a potential data quality issue in the source data)

### Pass Criteria
- [ ] M:M relationship is identified
- [ ] Severity is Critical
- [ ] Agent mentions potential for incorrect aggregations
- [ ] Bridge table or data quality investigation is suggested as the remedy

---

## Test 003 — Missing Date table

### Model State
The model has a `Sales` fact table with `Sales[OrderDate]` as a date column. There is no separate `Date` dimension table. Time intelligence measures (`Sales LY`, `Revenue YTD`) exist referencing `Sales[OrderDate]`.

### Prompt
```
Review the model and assess whether time intelligence is set up correctly.
```

### Expected Output

The agent should:
- Identify the absence of a dedicated Date dimension table
- Classify this as **Critical** (time intelligence functions will not work correctly)
- Flag the time intelligence measures that reference `Sales[OrderDate]` directly
- Recommend creating a dedicated Date table, marking it as a Date table in Power BI, and linking it to `Sales[OrderDate]` via a relationship

### Pass Criteria
- [ ] Missing Date table identified
- [ ] Severity is Critical
- [ ] Affected measures are mentioned
- [ ] Recommended remedy includes a marked Date table

---

## Test 004 — Clean model (no issues expected)

### Model State
The model has:
- One fact table (`Sales`) connected many-to-one to dimensions (`Customer`, `Product`, `Date`, `Territory`)
- The `Date` table is marked as a Date table
- All relationships are single-direction, many-to-one
- No inactive relationships
- All relationships use surrogate keys

### Prompt
```
Review the semantic model and tell me if it's ready for release.
```

### Expected Output

The agent should:
- Classify all tables correctly (fact, dimensions)
- Find no Critical findings
- Find no Warning findings
- Return a verdict of **Ready** (or **Ready with Warnings** only if minor informational items are noted)
- Confirm the star schema structure is correct

### Pass Criteria
- [ ] No Critical findings raised
- [ ] No spurious Warnings raised for correct model design
- [ ] Verdict is Ready or Ready with Warnings (for informational items only)
- [ ] Star schema structure is correctly described

---

## Test 005 — Snowflake dimension chain

### Model State
The model has: `Sales` fact → `Product` dimension → `ProductSubcategory` dimension → `ProductCategory` dimension (a three-level snowflake chain).

### Prompt
```
Review the semantic model for star schema compliance.
```

### Expected Output

The agent should:
- Identify the snowflake chain (Product → ProductSubcategory → ProductCategory)
- Classify as **Warning**
- Explain that snowflake structures can cause ambiguous filter propagation and add unnecessary model complexity
- Suggest flattening: merge `SubcategoryName` and `CategoryName` into the `Product` dimension

### Pass Criteria
- [ ] Snowflake chain is identified with all three tables named
- [ ] Severity is Warning
- [ ] Flattening suggestion provided

---

## Test 006 — Inactive relationship with no corresponding USERELATIONSHIP measure

### Model State
The model has an inactive relationship from `Sales[ShipDateKey]` to `Date[DateKey]`. No DAX measure in the model uses `USERELATIONSHIP`. The active relationship from `Sales[OrderDateKey]` to `Date[DateKey]` is correct.

### Prompt
```
Review the model relationships including inactive ones.
```

### Expected Output

The agent should:
- Identify the inactive relationship
- Classify it as **Warning** (inactive with no documented usage)
- Flag that no `USERELATIONSHIP` measure was found for this relationship
- Suggest either creating the intended measure or removing the inactive relationship if it is not needed

### Pass Criteria
- [ ] Inactive relationship identified
- [ ] Absence of a corresponding USERELATIONSHIP measure noted
- [ ] Severity is Warning
- [ ] Action suggested: create the measure or remove the relationship
