---
name: report-review
description: Use when reviewing a Power BI report for visual design quality, usability, accessibility, and adherence to enterprise reporting standards. Invoke before publishing to end users or during design reviews.
---

# Report Review

## Overview

Analyse the Power BI report structure and visual design, and produce a structured findings report. The goal is to identify issues that could confuse end users, reduce accessibility, or violate enterprise design standards.

**Core principle:** Review and report only. Do not modify the report. All findings are proposals for the developer to act on.

---

## When to Use

Use this skill when:
- A developer requests a report review ("review the report", "check the visuals")
- Preparing to publish a report to end users
- Investigating user complaints about confusing or incorrect visuals
- Running a release readiness check

Do NOT use for:
- Semantic model issues (use `semantic-model-review`)
- DAX measure quality (use `dax-review`)

---

## Report Review Workflow

### Step 1: Read Report Structure

From PBIP files, read:
- `definition/report.json` — report-level settings and theme
- `definition/pages/*.json` — one file per report page

If using MCP tooling, request the report page and visual metadata from the available tools.

Identify:
- Number of pages
- Page names and order
- Visual types and counts per page

### Step 2: Review by Section

Apply checks across all four sections below. For each finding, record the page name, section, severity, and a specific suggested action.

#### Section 1: Visual Design & Effectiveness

Assess whether visuals are appropriate for their data and well-organised on the page.

| Check | Rule | Severity |
|-------|------|----------|
| Page has a clear title | Every page must have a visible title text box or descriptive header | Warning |
| Visual count per page | More than 8–10 visuals per page is typically too dense for comprehension | Warning |
| Logical visual grouping | Related visuals should be grouped by proximity or background containers | Informational |
| Consistent canvas size | All pages should use the same canvas size unless intentionally different (e.g. tooltip/drillthrough pages) | Informational |
| Pie or donut chart with >3 slices | Prohibited — exceeds readable slice count | Critical |
| Pie or donut chart with ≤3 slices | Strongly discouraged; flag unless a bar chart is demonstrably unsuitable | Warning |
| Multi-row card with a single value | Use a single-value card instead | Informational |
| Table visual with >15 columns | Unlikely to fit on standard screens without horizontal scrolling | Warning |
| Scatter chart axes unlabelled | Both axes must have clear, descriptive labels | Warning |
| No corporate theme applied | Flag if the default Power BI theme is in use with no customisation | Informational |

#### Section 2: Accessibility & Readability

Ensure the report is usable by the full audience, including those with visual or motor impairments.

| Check | Rule | Severity |
|-------|------|----------|
| Visuals missing meaningful titles | Every chart, table, and card must have a visible or screen-reader-accessible title | Warning |
| Images missing alt text | Any image visual must have descriptive alt text configured | Warning |
| Colour is the only encoding | Status or categories must not be conveyed by colour alone — add labels, icons, or patterns | Warning |
| Colour contrast below WCAG AA | Text and background must achieve a 4.5:1 contrast ratio | Warning |
| Font size below 10pt | All readable text must be 10pt or larger | Warning |
| Red/green only indicators | Red and green alone are indistinguishable for colour-blind users — add a secondary encoding | Warning |

#### Section 3: Interaction & Navigation Design

Verify that slicers, filters, and cross-visual interactions are configured intentionally and behave predictably.

| Check | Rule | Severity |
|-------|------|----------|
| More than 4–5 slicers on one page | Exceeds the threshold that typically reduces clarity | Warning |
| Slicer default causes blank view | An empty or unset slicer that hides all data by default creates a confusing first impression | Warning |
| Cross-filter interactions left as default | All cross-visual interactions must be explicitly configured | Warning |
| Hidden pages not labelled as such | Tooltip and drillthrough pages must be clearly labelled in the page name | Informational |
| Drillthrough or nav buttons unlabelled | Any navigation element must be discoverable and clearly labelled | Informational |
| Map visual present | Flag for governance review — Bing Maps data-sharing disclosure may be required | Warning |

#### Section 4: Data Integrity & Context

Confirm that data is presented accurately and with sufficient context for correct interpretation.

| Check | Rule | Severity |
|-------|------|----------|
| Visuals showing BLANK or ERROR | Unexpected blank or error states must be resolved before release | Critical |
| Incorrect totals or subtotals | Tables must show correct aggregations with no mismatched or missing totals | Critical |
| Units missing from measures | All measures must display units (%, £, $, K, M, etc.) to prevent misinterpretation | Warning |
| Inconsistent currency or percentage format | Use symbols consistently across comparable visuals on the same page | Warning |
| Time context not visible | Where time intelligence is used, the period (MTD, YTD, Last 12 Months, etc.) must be displayed | Warning |
| Date slicer defaults to full range | Large default date ranges increase first-render query load — verify the default is intentional | Informational |
| Refresh timestamp absent | If data is not live, display when it was last refreshed | Informational |

### Step 3: Custom Visual Review

For any non-built-in visual identified in Step 1, apply the custom visual governance rules in `rules/report-rules.md` and refer to `docs/custom-visuals.md` for full guidance. Record certification status and whether all data roles are populated. Agents **cannot** render, execute, or validate the visual's internal logic — defer behavioural and output-quality assessment to a human reviewer.

### Step 4: Produce Report

Write the review output using `templates/report-review-template.md`. Record findings in the relevant section. Conclude with an overall verdict:

| Verdict | Condition |
|---|---|
| **BLOCKED** | One or more Critical findings present |
| **READY WITH WARNINGS** | No Critical findings; one or more Warnings |
| **READY** | No Critical or Warning findings |

---

## Severity Definitions

| Severity | Definition |
|----------|------------|
| **Critical** | Incorrect data displayed or broken visual. Must be resolved before release. |
| **Warning** | Usability, accessibility, or design standard violated. Should be resolved. |
| **Informational** | Best practice suggestion. Low urgency. |

---

## Example Finding

```
Page: Sales Overview
Section: Visual Design & Effectiveness
Visual: Donut chart — Sales by Category
Finding: Pie/donut chart with 9 slices
Severity: Critical
Detail: The donut chart has 9 category slices, well above the 3-slice maximum.
        Slices become indistinguishable at this count, especially with similar hues.
Suggested action: Replace with a horizontal bar chart sorted by sales descending.
                  This makes ranking immediately clear and scales to more categories.
```
