# Prompt Tests — Report Review Skill

This file contains validation scenarios for the `report-review` skill. Use these tests to confirm that the agent identifies design, accessibility, and custom visual risks without over-reporting.

---

## How to Use These Tests

For each scenario:
1. Recreate the report state described below, or provide the report JSON and screenshots as context
2. Issue the prompt shown
3. Compare the response against the expected output

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Missing visual title

### Report State
The Overview page contains a Card visual showing Average Order Value. The title is disabled and no alt text is configured.

### Prompt
```text
Review this report for accessibility issues.
```

### Expected Output

The agent should:
- Flag the missing title or alt text
- Classify the issue as **Warning**
- Recommend adding a visible title or alt text

### Pass Criteria
- [ ] Missing title or alt text identified
- [ ] Severity is Warning
- [ ] Accessible remedy suggested

---

## Test 002 — Excessive slicers on one page

### Report State
The Sales Detail page contains 7 visible slicers and 5 data visuals.

### Prompt
```text
Review this page for layout and usability issues.
```

### Expected Output

The agent should:
- Flag the page as overly dense from a filtering perspective
- Classify the issue as **Warning**
- Suggest consolidating slicers into a filter panel, bookmark, or dedicated filter area

### Pass Criteria
- [ ] Excessive slicer count identified
- [ ] Severity is Warning
- [ ] Consolidation or filter-panel remedy suggested

---

## Test 003 — Uncertified custom visual in UAT-bound report

### Report State
The Overview page contains a custom visual with a known AppSource GUID but no certification approval recorded for the project.

### Prompt
```text
We are preparing this report for UAT. Review it for any blockers.
```

### Expected Output

The agent should:
- Identify the custom visual and note that it is uncertified or unapproved
- Classify the issue as **Critical** or **Warning** based on the repository standard for the destination environment
- Defer final approval to human review
- Avoid claiming it has validated the internal JavaScript of the visual

### Pass Criteria
- [ ] Custom visual identified explicitly
- [ ] Certification or approval gap noted
- [ ] Human verification required
- [ ] No false claim of internal code inspection

---

## Test 004 — Clean report should not receive noise

### Report State
The report has 4 pages, each with 5 to 7 visuals, clear titles, a custom theme, no uncertified custom visuals, and correct alt text on images.

### Prompt
```text
Review this report and tell me if it is ready for publication.
```

### Expected Output

The agent should:
- Find no Critical issues
- Avoid inventing stylistic warnings without evidence
- Return a Ready or Ready with Warnings verdict only if minor informational items exist

### Pass Criteria
- [ ] No spurious Critical findings
- [ ] No invented layout warnings
- [ ] Verdict remains proportionate to the evidence

---

## Test 005 — Colour-only encoding of status

### Report State
An executive summary page uses only red and green dots to indicate KPI status, with no labels, icons, or text.

### Prompt
```text
Review this report for accessibility and executive-readability issues.
```

### Expected Output

The agent should:
- Identify colour-only encoding as an accessibility issue
- Classify it as **Warning**
- Suggest adding text labels, icons, or explicit status wording

### Pass Criteria
- [ ] Colour-only encoding identified
- [ ] Severity is Warning
- [ ] Non-colour alternative suggested

---

## Test 006 — "Show it now" with localhost mismatch

### Report State
The report can open, but the semantic model partitions point to a machine-specific SQL source (`localhost` on another developer machine). The current user does not have that local SQL instance.

### Prompt
```text
Show it now in Power BI.
```

### Expected Output

The agent should:
- Run or request a connection preflight before attempting immediate display actions
- Identify the localhost mismatch as an environment configuration issue
- Classify it as **Warning** unless credentials/secrets are exposed
- Provide exact fix steps (server/instance, database, credentials, refresh)
- Avoid looping into repeated render attempts with the same unresolved failure

### Pass Criteria
- [ ] Preflight-first behavior is followed
- [ ] Localhost mapping issue identified correctly
- [ ] Severity classification is proportional (Warning unless secret exposure)
- [ ] Remediation steps are explicit and actionable
- [ ] No repeated attempt loop without new environment input
