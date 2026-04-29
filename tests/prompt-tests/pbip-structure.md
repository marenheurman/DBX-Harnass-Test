# Prompt Tests — PBIP Structure Skill

This file contains validation scenarios for the `pbip-structure` skill. Use these tests to confirm that the agent identifies structural integrity issues, source-control risks, and sensitive-content exposure in PBIP projects.

---

## How to Use These Tests

For each scenario:
1. Recreate the PBIP project structure described below, or provide the relevant files as context
2. Issue the prompt shown
3. Compare the response against the expected output

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Mixed model formats should be Critical

### Project State
The semantic model folder contains both `definition/model.bim` and `definition/database.tmdl`.

### Prompt
```text
Validate this PBIP project for source-control readiness.
```

### Expected Output

The agent should:
- Identify that both model formats are present
- Classify the issue as **Critical**
- Explain that a PBIP project should use one semantic model format consistently

### Pass Criteria
- [ ] Mixed format identified
- [ ] Severity is Critical
- [ ] Single-source-of-truth explanation provided

---

## Test 002 — Missing `.platform` file should be flagged

### Project State
`AdventureWorks.Report/` exists, but `.platform` is missing.

### Prompt
```text
Check whether this PBIP project is structurally valid.
```

### Expected Output

The agent should:
- Identify the missing `.platform` file
- Classify the issue as **Critical** or **Warning** based on the repository rule interpretation
- Explain why the file matters for project integrity

### Pass Criteria
- [ ] Missing `.platform` file identified
- [ ] Severity is proportionate
- [ ] Structural importance explained

---

## Test 003 — Embedded credential should be Critical

### Project State
`definition/tables/Sales.tmdl` contains `password=` in a partition expression.

### Prompt
```text
Scan this PBIP project for anything unsafe to commit.
```

### Expected Output

The agent should:
- Flag the credential exposure immediately
- Classify it as **Critical**
- Recommend removing and rotating the exposed credential

### Pass Criteria
- [ ] Credential exposure identified
- [ ] Severity is Critical
- [ ] Rotation and secure-storage remediation suggested

---

## Test 004 — Missing `.gitignore` entries should be Warning

### Project State
The repository has a `.gitignore`, but it does not exclude `.pbi/`, `*.lock`, or `*.pbix`.

### Prompt
```text
Review this PBIP project for source-control hygiene.
```

### Expected Output

The agent should:
- Identify the missing exclusions
- Classify them as **Warning**
- Suggest the specific patterns that should be added

### Pass Criteria
- [ ] Missing exclusions listed
- [ ] Severity is Warning
- [ ] Specific `.gitignore` patterns suggested

---

## Test 005 — Clean PBIP project should not receive false positives

### Project State
The project has one semantic model format, both `.platform` files, a valid report structure, no credentials, and a correct `.gitignore`.

### Prompt
```text
Validate this PBIP project before pull request.
```

### Expected Output

The agent should:
- Return no Critical findings
- Avoid inventing structural issues without evidence
- Confirm the project is ready for source control, optionally with minor informational notes only

### Pass Criteria
- [ ] No spurious Critical findings
- [ ] No invented file-integrity problems
- [ ] Verdict is proportionate to the clean state
