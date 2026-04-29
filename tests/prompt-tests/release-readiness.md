# Prompt Tests — Release Readiness Skill

This file contains validation scenarios for the `release-readiness` skill. Use these tests to confirm that the agent aggregates findings correctly and assigns the correct final verdict.

---

## How to Use These Tests

For each scenario:
1. Provide the component findings as context, or run the underlying review skills against a prepared model and report
2. Issue the readiness prompt
3. Compare the verdict and aggregation against the expected result

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Any Critical finding must block release

### Review State
- Semantic Model: 0 Critical, 2 Warnings
- DAX: 1 Critical, 1 Warning
- Report: 0 Critical, 0 Warnings
- PBIP Structure: 0 Critical, 1 Warning
- Naming: 0 Critical, 2 Warnings

### Prompt
```text
Run a release readiness assessment and give me the final verdict.
```

### Expected Output

The agent should:
- Aggregate the counts correctly
- Return **Blocked**
- Surface the Critical finding before warning-level commentary

### Pass Criteria
- [ ] Verdict is Blocked
- [ ] Critical finding is surfaced prominently
- [ ] Totals match the component findings

---

## Test 002 — Warnings only should produce Ready with Warnings

### Review State
- Semantic Model: 0 Critical, 1 Warning
- DAX: 0 Critical, 2 Warnings
- Report: 0 Critical, 1 Warning
- PBIP Structure: 0 Critical, 0 Warnings
- Naming: 0 Critical, 1 Warning

### Prompt
```text
Give me the release readiness verdict for this project.
```

### Expected Output

The agent should:
- Return **Ready with Warnings**
- Include an accepted-risk statement section
- Avoid overstating the project as fully ready

### Pass Criteria
- [ ] Verdict is Ready with Warnings
- [ ] Accepted-risk section included
- [ ] No false Ready verdict

---

## Test 003 — Clean project should produce Ready

### Review State
- Semantic Model: 0 Critical, 0 Warnings
- DAX: 0 Critical, 0 Warnings
- Report: 0 Critical, 0 Warnings
- PBIP Structure: 0 Critical, 0 Warnings
- Naming: 0 Critical, 0 Warnings

### Prompt
```text
Run a full release readiness review.
```

### Expected Output

The agent should:
- Return **Ready**
- Avoid inventing unresolved issues
- Present a concise summary with zero Critical and zero Warning findings

### Pass Criteria
- [ ] Verdict is Ready
- [ ] Zero Critical and Warning counts preserved
- [ ] No fabricated blockers added

---

## Test 004 — Contradictory child findings should be surfaced clearly

### Review State
- Semantic Model review says the Date table is missing
- DAX review says time intelligence measures correctly reference the marked Date table

### Prompt
```text
Run a release readiness review and highlight any contradictions.
```

### Expected Output

The agent should:
- Identify that the child findings contradict each other
- Escalate the contradiction for human review
- Avoid presenting a false sense of certainty in the final verdict

### Pass Criteria
- [ ] Contradiction explicitly noted
- [ ] Human review recommended
- [ ] Final summary reflects uncertainty rather than ignoring it
