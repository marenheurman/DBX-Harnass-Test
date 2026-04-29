# Rule Tests — DAX Rule Checks

This file contains validation scenarios for the DAX rules defined in `rules/dax-rules.md` and enforced by the `dax-review` skill. Each scenario presents a DAX expression, identifies which rule it tests, and defines the expected agent response.

---

## How to Use These Tests

For each test:
1. Provide the DAX expression to the agent as context (or load it into a test model)
2. Issue the review prompt
3. Compare the agent output against the expected response

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Division without DIVIDE (Critical)

**Rule tested:** `dax-rules.md` — Division Safety

### DAX Expression Under Test
```dax
Return Rate % = [Returned Units] / [Total Units Sold]
```

### Prompt
```
Review this DAX measure for correctness and safety.
```

### Expected Agent Response
- Identify the unsafe division
- Classify as **Critical**
- Explain: if `[Total Units Sold]` is 0 or BLANK, the measure returns an error
- Propose a fix using `DIVIDE`:

```dax
Return Rate % = DIVIDE([Returned Units], [Total Units Sold], BLANK())
```

### Pass Criteria
- [ ] Issue identified as unsafe division
- [ ] Severity is Critical
- [ ] DIVIDE proposed with correct arguments
- [ ] BLANK() (not 0) recommended as the alternate result for a rate measure

---

## Test 002 — DIVIDE used correctly (should pass)

**Rule tested:** `dax-rules.md` — Division Safety (negative test)

### DAX Expression Under Test
```dax
Gross Margin % = DIVIDE([Gross Profit], [Total Sales], BLANK())
```

### Prompt
```
Review this DAX measure for correctness and safety.
```

### Expected Agent Response
- No issue found for division
- Mark as **Pass** with no findings
- Agent may note informational observations (e.g. display folder suggestion) but must not raise a false positive on the division

### Pass Criteria
- [ ] No Critical or Warning raised for the division pattern
- [ ] Agent does not incorrectly suggest DIVIDE on already-correct code

---

## Test 003 — Time intelligence on fact table column (Warning)

**Rule tested:** `dax-rules.md` — Time Intelligence Rules

### DAX Expression Under Test
```dax
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Sales[OrderDate]))
```

### Prompt
```
Review this DAX measure. The model has a marked Date table linked to Sales[OrderDateKey].
```

### Expected Agent Response
- Identify that `SAMEPERIODLASTYEAR` is applied to `Sales[OrderDate]` (a fact column), not the `Date` table
- Classify as **Warning**
- Explain the risk: month boundaries and gaps in fact table dates can cause incorrect period comparisons
- Propose fix:

```dax
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
```

### Pass Criteria
- [ ] Issue identified as time intelligence on non-Date-table column
- [ ] Severity is Warning
- [ ] Correct fix proposed using the marked Date table column

---

## Test 004 — Hardcoded year value (Warning)

**Rule tested:** `dax-rules.md` — Hardcoded Values and Magic Numbers

### DAX Expression Under Test
```dax
Sales 2024 Baseline = CALCULATE([Total Sales], 'Date'[Year] = 2024)
```

### Prompt
```
Review this measure for standards compliance.
```

### Expected Agent Response
- Flag the hardcoded year value `2024`
- Classify as **Warning**
- Explain: the measure becomes stale as the current year advances and requires manual update
- Suggest a dynamic alternative or a parameter:

```dax
-- Option A: Use a parameter or slicer instead of a hardcoded year
-- Option B: Reference a configuration table
Sales Baseline Year = CALCULATE([Total Sales], 'Date'[Year] = [_Baseline Year Parameter])
```

### Pass Criteria
- [ ] Hardcoded year identified
- [ ] Severity is Warning
- [ ] Dynamic alternative or parameter approach suggested

---

## Test 005 — FILTER(ALL(...)) removing user slicer context (Warning)

**Rule tested:** `dax-rules.md` — FILTER Usage

### DAX Expression Under Test
```dax
Enterprise Customers =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerKey]),
    FILTER(ALL(Customer), Customer[Segment] = "Enterprise")
)
```

### Prompt
```
Review this measure. The report has a Region slicer that should filter the customer count by region.
```

### Expected Agent Response
- Identify that `FILTER(ALL(Customer), ...)` removes all filters including the Region slicer
- Classify as **Warning**
- Explain: the user's Region slicer will not affect this measure's result at all — it will always return all Enterprise customers regardless of Region
- Propose fix that preserves user context:

```dax
Enterprise Customers =
CALCULATE(
    DISTINCTCOUNT(Sales[CustomerKey]),
    Customer[Segment] = "Enterprise"
)
```

### Pass Criteria
- [ ] `FILTER(ALL(...))` pattern identified as removing user filters
- [ ] Severity is Warning
- [ ] Simpler CALCULATE filter argument proposed
- [ ] Agent explains the slicer context impact

---

## Test 006 — Good measure formatting with VAR/RETURN (should pass)

**Rule tested:** `dax-rules.md` — Formatting Standards (negative test)

### DAX Expression Under Test
```dax
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

### Prompt
```
Review this measure for standards compliance and correctness.
```

### Expected Agent Response
- Confirm the measure is correctly formatted using VAR/RETURN
- Confirm DIVIDE is used safely
- Confirm ISBLANK guard is present
- No Critical or Warning findings
- At most one Informational suggestion (e.g. display folder)

### Pass Criteria
- [ ] No Critical or Warning findings raised
- [ ] VAR/RETURN pattern recognised as correct
- [ ] DIVIDE usage confirmed as safe
- [ ] Agent does not raise false positives

---

## Test 007 — Deeply nested CALCULATE (Warning)

**Rule tested:** `dax-rules.md` — CALCULATE Usage

### DAX Expression Under Test
```dax
Adjusted Margin =
CALCULATE(
    CALCULATE(
        CALCULATE(
            [Gross Margin %],
            REMOVEFILTERS(Territory)
        ),
        Sales[Channel] = "Online"
    ),
    'Date'[Year] = YEAR(TODAY())
)
```

### Prompt
```
Review this measure for correctness and maintainability.
```

### Expected Agent Response
- Identify the three levels of nested CALCULATE
- Classify as **Warning**
- Explain: deeply nested CALCULATE is hard to debug and maintain
- Suggest extracting intermediate measures:

```dax
_Margin All Territories = CALCULATE([Gross Margin %], REMOVEFILTERS(Territory))
_Online Margin = CALCULATE([_Margin All Territories], Sales[Channel] = "Online")
Adjusted Margin = CALCULATE([_Online Margin], 'Date'[Year] = YEAR(TODAY()))
```

### Pass Criteria
- [ ] Three levels of nesting identified
- [ ] Severity is Warning
- [ ] Intermediate measure refactor proposed
- [ ] Note: `YEAR(TODAY())` is acceptable — agent should not flag dynamic year as a hardcoded value
