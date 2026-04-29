# Sample Report Review

This example shows the structured output produced by the `report-review` skill for a fictional **Adventure Works Sales Dashboard**.

---

## Review Output

| Field | Value |
|---|---|
| **Report name** | Adventure Works Sales Dashboard |
| **Pages reviewed** | 4 (Overview, Sales Detail, Product Analysis, \[Drillthrough\] Order Detail) |
| **Review date** | 2026-03-15 |
| **Reviewed by** | AI Agent (report-review skill v1.0) |
| **Reviewer** | *Pending human sign-off* |

---

## Summary

| Severity | Count |
|---|---|
| Critical | 3 |
| Warning | 2 |
| Informational | 3 |
| **Overall verdict** | **Not Ready — resolve Critical findings before UAT** |

---

## Report Overview

- 4 pages total: 1 summary page, 2 detail pages, 1 drill-through page
- 1 custom visual identified: `CharticulatorVisual` (AppSource — status: Uncertified)
- Report uses the default Power BI theme (no custom JSON theme applied)
- Navigation: tabs only — no button-based navigation panel

---

## Page Reviews

### Page 1: Overview

| # | Visual | Type | Issue |
|---|--------|------|-------|
| 1 | Total Sales | Card | ✅ Correct visual for single KPI |
| 2 | Sales by Region | Filled Map | ✅ Appropriate for geographic distribution |
| 3 | Sales vs Target | Pie Chart | 🔴 Pie chart used — prohibited (9 slices; maximum 3 permitted only in narrowly justified exceptions) |
| 4 | Year Selector | Slicer | ✅ Good — single select, has default |
| 5 | Top 10 Customers | Table | ✅ Top N applied — good performance practice |
| 6 | Sales Trend (YoY) | Line Chart (Charticulator) | 🔴 Uncertified custom visual used in report |

---

### Page 2: Sales Detail

| # | Visual | Type | Issue |
|---|--------|------|-------|
| 1 | Sales by Product Category | Clustered Bar | ✅ Good — sorted descending |
| 2 | Sales vs Budget by Month | Clustered Column | ✅ Appropriate comparison visual |
| 3 | Order Count | Card | ✅ Correct |
| 4 | Average Order Value | Card | ⚠️ No title visible on canvas |
| 5 | Channel Breakdown | Donut | 🔴 Donut chart used — prohibited (7 slices; maximum 3 permitted only in narrowly justified exceptions) |
| 6–11 | Product slicers (6 visible) | Slicers | ⚠️ 6 slicers on one page — exceeds recommended maximum of 4–5 |

---

### Page 3: Product Analysis

| # | Visual | Type | Issue |
|---|--------|------|-------|
| 1 | Revenue by Subcategory | Treemap | ℹ️ Over 40 leaf nodes — consider Top N filter or Horizontal Bar |
| 2 | Margin % vs Volume | Scatter Chart | ✅ Appropriate for correlation analysis |
| 3 | Product performance matrix | Matrix | ✅ Well-structured; row sorting applied |
| 4 | Category filter | Slicer | ✅ Clear label; default applied |

Page title is present but uses generic text "Products" — recommend updating to a descriptive purpose statement.

---

### Page \[Drillthrough\] Order Detail

| # | Visual | Type | Issue |
|---|--------|------|-------|
| 1 | Order header (ID, date, customer) | Multi-Row Card | ℹ️ Multi-Row Card is correct for grouped header fields |
| 2 | Line items | Table | ✅ All columns relevant; no unnecessary columns |
| Back button | Navigation button | ℹ️ Back button present — good drill-through practice |

---

## Critical Findings

### CR-01 — Uncertified Custom Visual in Report

**Visual:** Sales Trend (YoY) on Overview page
**Visual type:** Charticulator (CharticulatorVisual)
**Certification status:** AppSource — Uncertified (not Microsoft Certified)

**Detail:** This report is being prepared for UAT promotion. Per `rules/report-rules.md`, uncertified custom visuals require documented approval before use in UAT. The visual's GUID is present in the report JSON but no certification or approval entry was found in the project's visual inventory.

**Action required:**
1. Verify whether Charticulator is the correct visual for this use case — a standard Line Chart may serve the same purpose
2. If retaining the custom visual, obtain documented approval and add it to the project visual inventory before UAT promotion
3. Alternatively, replace with the built-in Line Chart and close this finding

---

### CR-02 — Pie Chart Prohibited (Overview)

**Visual:** Sales by Region — Pie Chart
**Rule:** Pie and donut charts are prohibited. The only permitted exception is 3 or fewer categories where a bar chart is explicitly documented as unsuitable. This chart has 9 slices and no such justification.

**Severity:** Critical

**Detail:** The pie chart on the Overview page displays 9 region slices. Pie and donut charts are not permitted in this organisation's reports. Even the narrow exception (≤3 slices, no suitable bar chart) does not apply here.

**Suggested fix:** Replace with a sorted Horizontal Bar Chart. Apply a Top 8 + Other grouping if visual density is a concern.

---

### CR-03 — Donut Chart Prohibited (Sales Detail)

**Visual:** Channel Breakdown — Donut
**Rule:** Pie and donut charts are prohibited. The only permitted exception is 3 or fewer categories where a bar chart is explicitly documented as unsuitable. This chart has 7 slices and no such justification.

**Severity:** Critical

**Detail:** 7 channels are displayed in a donut chart. Donut charts are not permitted in this organisation's reports.

**Suggested fix:** Replace with a Clustered Bar Chart sorted by channel share descending.

---

## Warnings

### W-01 — Missing Visual Title (Sales Detail — Average Order Value Card)

**Visual:** Average Order Value — Card
**Rule:** Every chart, table, and matrix must have a visible title or alt text configured.

**Detail:** The Average Order Value card has no title element enabled. Screen readers and export-to-PDF consumers will have no label for this value.

**Suggested fix:** Enable the card title in visual formatting and set it to "Average Order Value."

---

### W-02 — Excessive Slicers on Page (Sales Detail)

**Visual:** 6 slicers visible simultaneously
**Rule:** Each page should have no more than 4–5 slicers visible at once.

**Detail:** The Sales Detail page has 6 product-related slicers taking up approximately 30% of the canvas. This reduces the space available for data visuals and overwhelms the user.

**Suggested fix:** Consolidate related slicers into a collapsible filter panel or move secondary slicers to a dedicated filter bookmark.

---

## Informational Findings

### I-01 — No Custom Theme Applied

**Scope:** Report-level
**Rule:** Reports must use a custom JSON theme file, not the default Power BI theme.

**Detail:** The report uses the default Power BI theme. While this is not blocking, it means colours may not align with organisation branding and the theme is not source-controlled.

**Suggested action:** Create a custom theme JSON file aligned to the brand palette and apply it. Store the file in the PBIP project.

---

### I-02 — Treemap with Very High Node Count (Product Analysis)

**Visual:** Revenue by Subcategory — Treemap
**Detail:** Over 40 leaf nodes are present. Treemaps lose readability beyond ~15–20 nodes. Consider applying a Top N filter or switching to a sorted Horizontal Bar Chart.

---

### I-03 — Generic Page Title (Product Analysis)

**Page:** Product Analysis
**Detail:** The page title reads "Products." This is functional but not informative. Recommend a descriptive title such as "Product Revenue and Margin Analysis."

---

## Accessibility Checklist

| Check | Status | Notes |
|---|---|---|
| All visuals have titles or alt text | ⚠️ Partial | Average Order Value card missing title |
| Images have alt text | ✅ Pass | No standalone images on canvas |
| Information not conveyed by colour alone | ✅ Pass | Labels present on all chart segments |
| Font sizes meet minimum (10pt body, 12pt title) | ✅ Pass | Verified on all pages |
| No red/green only as positive/negative indicator | ✅ Pass | Icons used alongside colour |
| No flashing or animated visuals | ✅ Pass | No animation enabled |

---

## Recommended Next Steps

| Priority | Action | Owner |
|---|---|---|
| 1 (Critical) | Resolve CR-01 — certify or replace Charticulator visual before UAT | BI Developer |
| 2 (Critical) | Resolve CR-02 — replace pie chart (Overview) with Horizontal Bar Chart | BI Developer |
| 3 (Critical) | Resolve CR-03 — replace donut chart (Sales Detail) with Clustered Bar Chart | BI Developer |
| 4 | Fix W-01 — add title to Average Order Value card | BI Developer |
| 5 | Address W-02 — consolidate slicers on Sales Detail page | BI Developer |
| 6 | Apply custom JSON theme (I-01) | BI Developer |
| 7 | Update Overview page title to be more descriptive | BI Developer |

---

## Sign-Off

| Role | Name | Date | Status |
|---|---|---|---|
| BI Developer | | | Pending |
| BI Lead | | | Pending |
| Stakeholder | | | Pending |
