# Sample Prompts

This file provides example prompts for invoking each skill in this accelerator. Use these as starting points and adapt them to your specific model, report, or project.

---

## Semantic Model Review

### Basic model review
```
Review the semantic model and produce a structured report. Flag any relationship issues, missing Date table, or star schema violations. Use the model review template.
```

### Relationship-focused review
```
Focus only on the relationships in this model. List each one with its cardinality, filter direction, and whether it is active or inactive. Flag any that are bidirectional or many-to-many.
```

### Onboarding to an inherited model
```
I've just inherited this Power BI model and I'm not familiar with it. Walk me through the table structure, classify each table as fact, dimension, or bridge, and summarise the model topology.
```

### Checking for ambiguous filter paths
```
Check whether there are any tables connected by more than one active relationship path. Ambiguous filter paths can cause incorrect DAX measure results.
```

---

## DAX Review

### Full measure review
```
Review all measures in this model for correctness, safety, and standards compliance. Flag any measures that use direct division without DIVIDE, hardcoded values, or unsafe use of FILTER(ALL(...)).
```

### Review specific table
```
Review all measures in the [Sales] table. I'm particularly concerned about the year-over-year and year-to-date measures — confirm they are using the correct Date table and time intelligence functions.
```

### Investigate a specific measure
```
The [Profit Margin %] measure is returning incorrect values in some filter contexts. Review the DAX expression and explain what might be causing the unexpected results.
```

### Check for DIVIDE safety across all measures
```
Scan all measures in the model and identify any that perform division using the / operator without DIVIDE. List each one with its current expression and a suggested corrected version.
```

---

## Report Review

### Full report review
```
Review this report for visual design quality, accessibility, and standards compliance. Check all pages. Use the report review template for the output.
```

### Accessibility check only
```
Review this report specifically for accessibility issues. Check for missing titles, missing alt text, colour-only encoding, and font sizes below 10pt.
```

### Page-specific review
```
Review only the [Sales Overview] page. I want to know if it is too dense, whether the visual types are appropriate, and whether the slicer setup is correct.
```

### Pre-publish review
```
I'm about to publish this report to the UAT workspace. Do a quick review of the report and tell me if there are any blockers.
```

### Preflight before immediate display
```
Before you try to show anything in Power BI, run a preflight: validate Sql.Database server/instance and database mapping, credential mode, and refresh readiness. If a check fails, stop and give the exact fix steps.
```

---

## PBIP Structure Check

### Validate project before source control commit
```
Check the PBIP project structure and confirm it is ready to commit to source control. Flag any missing files, mismatched formats, or embedded credentials.
```

### Post-migration validation
```
I just migrated this project from PBIX to PBIP format. Validate the file structure and confirm that the semantic model and report definitions are correctly structured.
```

### Security scan of partition expressions
```
Scan all partition source expressions in the TMDL files for embedded credentials, passwords, or bearer tokens. Produce a list of any findings.
```

### See also

- [examples/sample-pbip-structure-review.md](sample-pbip-structure-review.md) — Example output of a PBIP structure validation

---

## Naming Convention Check

### Full naming review
```
Check all tables, columns, and measures in this model for naming convention violations. Produce a violations report grouped by object type.
```

### Measures only
```
Review only the measure names in this model. Flag any that use default names (like 'New Measure'), unclear abbreviations, or are missing unit indicators for percentage and currency measures.
```

### After a merge
```
A pull request was just merged from two contributors. Check whether any new table or column names introduced in the merge violate our naming conventions.
```

### See also

- [examples/sample-naming-conventions-review.md](sample-naming-conventions-review.md) — Example output of a naming convention review

---

## Release Readiness

### Full release readiness check
```
Run a full release readiness check before we deploy to production. Apply all skills (model, DAX, report, PBIP structure, naming). Produce a consolidated readiness report and give me a verdict: Ready, Ready with Warnings, or Blocked.
```

### Sprint-end quality gate
```
We're at the end of the sprint. Run a release readiness check and tell me what we need to fix before we can present this to the client next week.
```

### Quick pre-demo check
```
I have a client demo in 2 hours. Do a quick readiness check on the report and model — prioritise anything that could cause visuals to show errors or incorrect values.
```

### See also

- [examples/sample-release-readiness.md](sample-release-readiness.md) — Example consolidated readiness verdict and sign-off structure

---

## Custom Visual Review

### Identify all custom visuals in a report
```
Read the report JSON and identify all custom visuals. For each one, tell me the visual name, GUID, and whether it is Microsoft Certified, Organisational, or uncertified. Flag any that are not certified.
```

### Custom visual governance check before UAT promotion
```
We are about to promote this report to UAT. Check whether any custom visuals in the report are uncertified or have unpopulated data roles. List any blockers.
```

### Data role validation for a specific custom visual
```
The [CharticulatorVisual] custom visual on the Overview page has stopped rendering data. Check whether its data roles are populated and whether the field mappings are correct.
```

### See also

- [examples/sample-report-review.md](sample-report-review.md) — Example output of a full report review, including a custom visual finding
- [docs/custom-visuals.md](../docs/custom-visuals.md) — Governance, build guide, and agent limitations for custom visuals
