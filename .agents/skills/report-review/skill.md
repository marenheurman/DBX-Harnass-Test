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

### Step 2: Review Each Page

For each page, apply the following checks:

#### Structure and Layout

| Check | Rule | Severity |
|-------|------|----------|
| Page has a clear title | Every page must have a visible title text box | Warning |
| Logical visual grouping | Related visuals should be visually grouped (proximity or backgrounds) | Informational |
| Visual count | More than 8–10 visuals per page is typically too dense | Warning |
| Consistent canvas size | All pages should use the same canvas size unless intentionally different (e.g. tooltip pages) | Informational |
| Hidden pages labelled as such | Hidden pages (tooltip, drillthrough) must be clearly labelled in their page name | Informational |

#### Visual Type Checks

| Check | Rule | Severity |
|-------|------|----------|
| Pie or donut chart with more than 3 categories/slices | Prohibited — exceeds the maximum permitted slice count | Critical |
| Pie or donut chart with 3 or fewer categories/slices | Strongly discouraged; flag unless the developer has documented why a bar chart is unsuitable | Warning |
| Multi-row card with one value | Use card instead of multi-row card for single KPIs | Informational |
| Table visual with more than 15 columns | Unlikely to be readable on standard screens | Warning |
| Map visual present | Flag for governance review — maps may require Bing Maps data-sharing disclosure | Warning |
| Scatter chart axes unlabelled | Both axes on scatter charts must have clear labels | Warning |

#### Slicer and Filter Checks

| Check | Rule | Severity |
|-------|------|----------|
| Too many slicers on one page | More than 4–5 slicers typically reduces clarity | Warning |
| Slicer with no default selection impact | Verify that an empty slicer does not return all data unexpectedly | Informational |
| Cross-filter interactions not configured | All visual interactions should be intentionally configured, not left as default | Warning |

#### Accessibility Checks

| Check | Rule | Severity |
|-------|------|----------|
| Visuals missing titles | Every chart or table must have a visible or screen-reader-accessible title | Warning |
| Images missing alt text | Any image visual must have alt text configured | Warning |
| Colour-only encoding | Information should not be conveyed by colour alone (consider patterns or labels) | Warning |
| Low contrast colours | Text and background colours must meet WCAG AA contrast ratio (4.5:1 for normal text) | Warning |
| Font size below 10pt | Small text is inaccessible on standard screens | Warning |

#### Data Accuracy Checks

| Check | Rule | Severity |
|-------|------|----------|
| Visuals displaying BLANK or ERROR | Flag any visual where sample data shows blank or error states that are unexpected | Critical |
| Totals appearing where they should not | Tables with incorrect subtotals or grand totals not matching business expectations | Critical |
| Date slicer defaulting to maximum range | Verify that large date ranges do not cause excessive query load on first render | Informational |

### Step 3: Review Report Theme

- Is a corporate or project-approved theme applied?
- Are brand colours used consistently?
- Is the default Power BI theme being used (flag for review if no custom theme)?

### Step 4: Review Custom Visuals

If the report contains any non-built-in visuals, apply the custom visual governance rules in `rules/report-rules.md` (Custom Visual Rules section) and refer to `docs/custom-visuals.md` for full governance guidance. Agents can identify custom visuals and check data role population, but **cannot** render, execute, or validate the visual's internal logic. Defer behavioural and output-quality assessment to human review.

### Step 5: Produce Report

Write the review output using the template in `templates/report-review-template.md`.

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
Visual: Donut chart — Sales by Category
Finding: Pie/donut chart with 9 slices
Severity: Warning
Detail: The donut chart has 9 category slices, which is difficult to distinguish visually,
        especially with similar colours in the outer ring.
Suggested action: Replace with a horizontal bar chart sorted by sales descending.
                  This makes ranking immediately clear and scales to more categories.
```
