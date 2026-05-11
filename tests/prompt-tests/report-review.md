# Prompt Tests — Report Review Skill

This file contains validation scenarios for the `report-review` skill. Use these tests to confirm that the agent reviews reports using the 4-section framework (Visual Design & Effectiveness, Accessibility & Readability, Interaction & Navigation Design, Data Integrity & Context) and identifies design, accessibility, and custom visual risks without over-reporting.

---

## How to Use These Tests

For each scenario:
1. Recreate the report state described below, or provide the report JSON and screenshots as context
2. Issue the prompt shown
3. Compare the response against the expected output

Tests are graded as: **Pass**, **Partial**, or **Fail**.

---

## Test 001 — Missing visual title (Section 2: Accessibility & Readability)

### Report State
The Overview page contains a Card visual showing Average Order Value. The title is disabled and no alt text is configured.

### Prompt
```text
Review this report for accessibility issues.
```

### Expected Output

The agent should:
- Place the finding under **Section 2: Accessibility & Readability**
- Flag the missing title or alt text as Warning
- Recommend adding a visible title or alt text

### Pass Criteria
- [ ] Finding placed in Accessibility & Readability section
- [ ] Severity is Warning
- [ ] Accessible remedy suggested

---

## Test 002 — Excessive slicers on one page (Section 3: Interaction & Navigation Design)

### Report State
The Sales Detail page contains 7 visible slicers and 5 data visuals.

### Prompt
```text
Review this page for layout and usability issues.
```

### Expected Output

The agent should:
- Place the finding under **Section 3: Interaction & Navigation Design**
- Flag the page as overly dense from a filtering perspective as Warning
- Suggest consolidating slicers into a filter panel, bookmark, or dedicated filter area

### Pass Criteria
- [ ] Finding placed in Interaction & Navigation Design section
- [ ] Excessive slicer count identified
- [ ] Severity is Warning
- [ ] Consolidation or filter-panel remedy suggested

---

## Test 003 — Uncertified custom visual in UAT-bound report (Section 4: Data Integrity & Context)

### Report State
The Overview page contains a custom visual with a known AppSource GUID but no certification approval recorded for the project.

### Prompt
```text
We are preparing this report for UAT. Review it for any blockers.
```

### Expected Output

The agent should:
- Place the finding under **Section 4: Data Integrity & Context**
- Identify the custom visual and note it is uncertified or unapproved
- Classify as Warning (or Critical if the destination environment requires certification)
- Defer final approval to human review
- Avoid claiming it has validated the internal JavaScript of the visual

### Pass Criteria
- [ ] Finding placed in Data Integrity & Context section
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
- Find no Critical issues across any of the four sections
- Avoid inventing stylistic warnings without evidence
- Return Ready, or Ready with Warnings only if genuine minor Informational items exist

### Pass Criteria
- [ ] No spurious Critical findings in any section
- [ ] No invented layout warnings
- [ ] Verdict is proportionate to the evidence
- [ ] Section summary table shows zero Critical counts

---

## Test 005 — Colour-only encoding of status (Section 2: Accessibility & Readability)

### Report State
An executive summary page uses only red and green dots to indicate KPI status, with no labels, icons, or text.

### Prompt
```text
Review this report for accessibility and executive-readability issues.
```

### Expected Output

The agent should:
- Place the finding under **Section 2: Accessibility & Readability**
- Identify colour-only encoding as a Warning
- Suggest adding text labels, icons, or explicit status wording alongside the colour

### Pass Criteria
- [ ] Finding placed in Accessibility & Readability section
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

---

## Test 007 — Section 1: Visual Design & Effectiveness

### Report State
A report page contains 12 visuals (too dense), some are multi-row cards with single values, a donut chart with 8 slices, and the page title is missing. Canvas size is consistent with other pages.

### Prompt
```text
Review this report for visual design issues and report findings organized by the 4 review sections.
```

### Expected Output

The agent should:
- Identify findings in the **Visual Design & Effectiveness** section
- Flag excessive visual count (12 > 8–10) as Warning
- Flag multi-row card with single value as Informational
- Flag donut chart with 8 slices as Critical
- Flag missing page title as Warning
- Organize output by section (not page-by-page)

### Pass Criteria
- [ ] Findings grouped under Visual Design & Effectiveness section
- [ ] Visual count, chart type, and title issues all identified
- [ ] Donut chart >3 slices rated Critical (not Warning)
- [ ] Output uses 4-section template structure

---

## Test 008 — Section 2: Accessibility & Readability

### Report State
Report page contains 5 visuals: a chart with no title, a KPI card using only red/green dot indicators (no labels), an image with no alt text, text in 8pt font, and a table with no visible column headers.

### Prompt
```text
Review this report specifically for accessibility and readability issues.
```

### Expected Output

The agent should:
- Identify findings in the **Accessibility & Readability** section
- Flag missing chart title as Warning
- Flag colour-only encoding (red/green dots) as Warning
- Flag missing alt text on image as Warning
- Flag 8pt font as Warning (below 10pt minimum)
- Note missing column headers (table readability issue)

### Pass Criteria
- [ ] All findings grouped under Accessibility & Readability section
- [ ] Missing titles, alt text, colour-only encoding, and small font flagged
- [ ] Severity is consistently Warning
- [ ] Remediation steps suggest specific fixes (e.g. add titles, add labels/icons, increase font size)

---

## Test 009 — Section 3: Interaction & Navigation Design

### Report State
Report has a detail page with 8 visible slicers, 4 are dropdowns with empty default selections that hide all data. Cross-filter interactions between visuals are all set to default. A drillthrough button is present but unlabelled.

### Prompt
```text
Review this report for slicer, filter, and navigation design issues.
```

### Expected Output

The agent should:
- Identify findings in the **Interaction & Navigation Design** section
- Flag excessive slicer count (8 > 4–5) as Warning
- Flag empty slicer defaults that hide data as Informational (or Warning if severe)
- Suggest consolidating slicers or applying sensible defaults
- Flag unlabelled drillthrough button as Warning or Informational

### Pass Criteria
- [ ] Findings grouped under Interaction & Navigation Design section
- [ ] Slicer count and default selection issues identified
- [ ] Unlabelled navigation element flagged
- [ ] Suggested actions are specific (e.g. consolidate to filter panel, add labels, set defaults)

---

## Test 010 — Section 4: Data Integrity & Context

### Report State
A dashboard page shows revenue totals without currency symbols, a YTD metric without indicating the year or period, and a table with BLANK rows that should not appear. A custom visual is used but not documented as approved in the project governance.

### Prompt
```text
Review this report for data labelling, context, and integrity issues.
```

### Expected Output

The agent should:
- Identify findings in the **Data Integrity & Context** section
- Flag missing currency symbols as Warning
- Flag missing time period context (YTD without year) as Warning
- Flag unexpected BLANK rows as Critical (data integrity issue)
- Flag undocumented custom visual as Warning (governance)

### Pass Criteria
- [ ] Findings grouped under Data Integrity & Context section
- [ ] Missing units/currency/time context flagged as Warning
- [ ] BLANK rows flagged as Critical
- [ ] Custom visual governance issue identified
- [ ] Suggested actions include adding labels and verifying visual approval
