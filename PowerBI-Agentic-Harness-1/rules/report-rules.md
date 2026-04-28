# Report Rules

These rules define the standards for Power BI report design. They are applied by the `report-review` skill and inform design decisions during report development.

---

## Core Principles

1. **Clarity over density** — users should not have to search for the key insight
2. **Consistency** — all pages in a report should follow the same layout conventions
3. **Accessibility** — reports must be usable by people with visual impairments
4. **Purpose-driven visuals** — every visual on a page must have a clear reason to exist
5. **Performance** — report load time matters; visual count and complexity must be managed

---

## Page Design

### Layout

- Every page must have a visible title text box at the top of the canvas
- The title must clearly state the purpose of the page (not generic names like "Page 1" or "Overview")
- Use a consistent header area across all pages (same height, same colour, same title format)
- Group related visuals visually: use background shapes, spacing, or grouping elements to indicate which visuals belong together
- Do not place visuals outside the canvas boundary — they will be invisible to end users

### Page Density

- Each page should include 4–6 KPI card visuals in a dedicated KPI row
- Aim for 5–6 additional meaningful visuals per page (charts, tables, matrices) beyond the KPI row
- A page with more than 10 visuals in total (KPI cards included) is almost always too dense — consider splitting into multiple pages with drill-through or bookmarks
- Use white space intentionally — it is not wasted space

### Navigation

- Multi-page reports must provide clear navigation: use a navigation menu, breadcrumbs, or page label conventions
- Use consistent page ordering: summary → detail is the standard flow
- Tooltip pages and drill-through pages must be named with a convention that makes them identifiable (e.g. `[Tooltip] Sales Detail`, `[Drillthrough] Customer Profile`)

---

## Visual Selection

Choose the right visual type for the data being shown:

| Use Case | Recommended Visual | Avoid |
|---|---|---|
| Single KPI (one number) | Card | Multi-Row Card |
| Comparison of 2–7 categories | Clustered Bar or Column Chart | Pie, Donut |
| Comparison of more than 7 categories | Horizontal Bar Chart (sorted) | Pie, Donut, Treemap |
| Trend over time | Line Chart | Column Chart if many time points |
| Part-to-whole with 2–3 parts | Clustered Bar or Stacked Bar | Pie, Donut |
| Correlation between two measures | Scatter Chart | N/A |
| Detailed tabular data | Table or Matrix | Scatter, Bar |
| Geographic distribution | Filled Map or Shape Map | If data is not geographic, do not use a map |
| Progress against a target | Gauge or KPI Visual | Pie Chart |

**Additional rules:**
- **Pie and donut charts are prohibited by default.** Do not use them.
- The only permitted exception is a **maximum of 3 categories/slices** where a bar or stacked chart would add disproportionate visual overhead relative to the insight. Even then, a bar or stacked chart remains the preferred choice. A pie or donut is acceptable only if the developer explicitly documents why a bar chart is unsuitable for that specific visual and layout.
- When a pie or donut is found during review, flag it as a **Warning** if it has 3 or fewer categories and no documented justification. If it has more than 3 categories, escalate it to **Critical**.
- Stacked charts must not have more than 5–6 stack segments — more than this is unreadable
- Do not use 3D visuals — they distort data perception
- Do not use waterfall charts as a default "variance" chart unless the data is genuinely a waterfall decomposition

---

## Slicer and Filter Rules

- Each page should have no more than 4–5 slicers visible at once — use a filter panel, pop-out overlay, or dedicated filter page for additional filters
- All slicers must have a clear label (panel header or title above)
- Slicer defaults must be reviewed — a slicer with no default selection should be intentional, not an oversight
- Cross-filter interactions between visuals must be explicitly configured — do not leave all visuals in their default "filter" interaction mode without reviewing the effect
- Report-level filters applied in the filter pane must be documented in the report review — end users may not see them

---

## Accessibility Rules

These rules support WCAG 2.1 AA compliance:

- Every chart, table, and matrix must have a title that is visible or available to screen readers via the `alt text` field in visual formatting
- Standalone images on the canvas must have alt text configured
- Information must not be conveyed by colour alone — use labels, patterns, shapes, or explicit indicators alongside colour
- Font size for body text and data labels must be a minimum of 10pt; titles minimum 12pt
- Avoid colour combinations that are inaccessible to colour-blind users — do not rely on red/green as the only differentiator between positive and negative values
  - Use icons, labels, or shapes in addition to colour for positive/negative indicators
- Do not use flashing or animated visuals that could trigger photosensitive responses

---

## Theme and Branding

- Reports must use a custom JSON theme file, not the default Power BI theme
- The theme file must define: primary colour palette, font family, background colour, and default visual settings
- All colours used in visuals must be sourced from the theme palette
- Do not hardcode colours directly in individual visual formatting settings — this breaks theme consistency

---

## Performance Rules

- Avoid using more than 10–15 custom visuals (AppSource) in a single report — each custom visual adds overhead
- Do not use a matrix or table that loads all rows without pagination or Top N filtering
- Apply `Top N` or date range filters to visuals that query large fact tables
- Avoid placing slicers that have no default selection on fact table columns with high cardinality (e.g., `Order Number`) — these will query the full column on page load
- Test report load time before release: a page should render in under 5 seconds under normal conditions

---

## Custom Visual Rules

Custom visuals introduce additional considerations beyond standard built-in visuals. Apply these rules whenever a report includes AppSource, organisational, or in-house custom visuals.

### Approval by Environment

See [docs/custom-visuals.md](../docs/custom-visuals.md) for the full environment-tier governance table. In summary: DEV permits all types for exploration; UAT permits Certified AppSource and Organisational (Uncertified requires documented approval); PROD permits Certified AppSource and Organisational only (In-house requires code review and sign-off).

### Usage Rules

- Prefer built-in visuals where they satisfy the requirement — only use a custom visual if it provides clear, quantifiable value over the built-in alternative
- Do not use more than 3–4 distinct custom visuals in a single report — visual variety adds cognitive load and maintenance overhead
- Ensure every custom visual used in a PROD report has a documented entry in the project's visual inventory (name, GUID, source, certification level, approval date)
- Custom visuals that have not been updated by their publisher in 12+ months should be flagged for review

### Security Review Checklist

The following must be confirmed before a custom visual is approved for UAT or PROD:

- [ ] Certification level verified (Certified / Organisational / In-house — not Uncertified from an unknown publisher)
- [ ] Visual does not make external network calls (check for `fetch`, `XMLHttpRequest` in source if in-house)
- [ ] Visual does not use `eval()` or dynamic code execution (in-house visuals only)
- [ ] Visual supplier listed in the project's approved vendor register (for regulated environments)
- [ ] Report does not rely on the custom visual for accessibility features that built-in visuals provide natively

### Agent Review Behaviour

When reviewing a report that contains a custom visual, the agent must:

1. Note the visual name and GUID from the report JSON
2. Classify it as Certified, Organisational, or Unknown/Uncertified
3. Flag Unknown or Uncertified visuals as requiring human verification before promotion
4. Check that the visual's data roles are populated — empty data roles suggest configuration issues
5. Defer any rendering, behaviour, or output quality assessment to human review

See [docs/custom-visuals.md](../docs/custom-visuals.md) for full governance guidance and SDK build instructions.

---

## References

- Microsoft Learn: [Create accessible reports in Power BI](https://learn.microsoft.com/power-bi/create-reports/desktop-accessibility-overview)
- Microsoft Learn: [Power BI report themes](https://learn.microsoft.com/power-bi/create-reports/desktop-report-themes)
- Microsoft Learn: [Report design guidance](https://learn.microsoft.com/power-bi/guidance/report-design)
- Microsoft Learn: [Power BI custom visuals overview](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals)
- [docs/custom-visuals.md](../docs/custom-visuals.md)
- [docs/governance.md](../docs/governance.md)
