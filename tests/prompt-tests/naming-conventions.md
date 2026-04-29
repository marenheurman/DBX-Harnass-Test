# Prompt Tests — Naming Conventions Skill

This file contains validation scenarios for the `naming-conventions` skill. Use these tests to confirm that the agent enforces conventions consistently without flagging valid helper or hierarchy names incorrectly.

---

## How to Use These Tests

For each scenario:
1. Provide the relevant object names or load a model that matches the described state
2. Issue the prompt shown
3. Compare the response against the expected output

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Table prefix should be flagged

### Model State
The model contains a table named `tbl_Sales`.

### Prompt
```text
Check this model for naming convention violations.
```

### Expected Output

The agent should:
- Flag `tbl_Sales` as a naming violation
- Classify it as **Warning**
- Suggest `Sales` as the corrected table name

### Pass Criteria
- [ ] Prefix violation identified
- [ ] Severity is Warning
- [ ] Suggested correction provided

---

## Test 002 — Generic measure name should be flagged

### Model State
The `_Measures` table contains a measure named `New Measure`.

### Prompt
```text
Review measure names only.
```

### Expected Output

The agent should:
- Flag `New Measure` as generic and non-descriptive
- Classify it as **Warning**
- Ask for a business-specific rename rather than inventing a metric without context

### Pass Criteria
- [ ] Generic name identified
- [ ] Severity is Warning
- [ ] No fabricated business rename asserted as fact

---

## Test 003 — Reserved word column name should be flagged

### Model State
The `Sales` table contains a column named `Date`.

### Prompt
```text
Check all column names for convention issues.
```

### Expected Output

The agent should:
- Flag `Sales[Date]` as too generic and risky in DAX contexts
- Classify it as **Informational** or **Warning** depending on the severity framework used
- Suggest a more specific name such as `OrderDate` if the business meaning is known

### Pass Criteria
- [ ] `Date` column identified
- [ ] More specific naming suggested
- [ ] Severity remains proportionate

---

## Test 004 — Valid helper measure should pass

### Model State
The `_Measures` table contains `_Selected Year` and `_Filtered Customer Count`.

### Prompt
```text
Review measure names for naming convention violations.
```

### Expected Output

The agent should:
- Recognise the leading underscore as valid for helper measures
- Avoid flagging these names as violations

### Pass Criteria
- [ ] Helper naming pattern accepted
- [ ] No false positive raised

---

## Test 005 — Valid hierarchy name should pass

### Model State
The `Date` table contains `Calendar Hierarchy` and the `Geography` table contains `Geography Hierarchy`.

### Prompt
```text
Review hierarchy names in this model.
```

### Expected Output

The agent should:
- Accept both hierarchy names as valid
- Avoid replacing them with generic alternatives

### Pass Criteria
- [ ] Hierarchy names accepted
- [ ] No unnecessary rename suggested
