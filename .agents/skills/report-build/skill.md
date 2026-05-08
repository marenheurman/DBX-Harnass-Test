---
name: report-build
description: Use when building or adding pages to a Power BI report programmatically using Python or pbi-tools. Invoke when a user asks to create visuals, add report pages, or generate a .pbix report from a model. Do NOT use for reviewing an existing report — use the report-review skill for that.
---

# Report Build

## Overview

Guide the agent through building Power BI report pages programmatically. There are two supported approaches depending on the source artefact available. The agent must determine which applies before writing any code.

**Core principle:** Always write to a new output file. Never overwrite the source `.pbix` in-place.

---

## When to Use

Use this skill when:
- A user asks to "create visuals", "add a report page", "build a dashboard", or "show it in Power BI"
- Generating a `.pbix` file from a semantic model
- Adding or replacing pages in an existing report programmatically
- Translating a layout design or wireframe into report JSON

Do NOT use for:
- Reviewing or auditing an existing report (use `report-review` skill)
- Publishing to the Power BI Service (out of scope — human action required)
- Modifying live production reports without explicit human sign-off

---

## Step 1: Determine the Build Approach

Before writing any code, ask or infer which source artefact is available:

| Source available | Correct approach |
|---|---|
| PBIP folder (`.SemanticModel/` and `.Report/` folders) | Edit the JSON report source files directly, then use `pbi-tools compile` to produce the `.pbix` |
| A `.pbix` file only (no PBIP extract) | Use Python `zipfile` to read the existing layout, add pages, zero `SecurityBindings`, and write a new output `.pbix` |
| No existing report, starting fresh | Use Python to build the full layout JSON and write a new `.pbix` using `templates/build-report-template.py` as the starter |

If uncertain, ask: *"Do you have a PBIP folder structure, or only a .pbix file?"*

---

## Step 2: Collect Model Manifest

Before building any visual, the agent must know the exact table and field names from the semantic model. Request or generate a model manifest following `docs/model-manifest-template.json`.

Minimum required for each visual:
- Measures table name (typically `_Measures`)
- Exact measure names as they appear in the model
- Dimension table names and column names for any category/axis fields

Do not guess or infer measure names. Incorrect names produce silently blank visuals.

---

## Step 3: Build Approach A — PBIP Source (pbi-tools)

Use this path when a PBIP folder structure is available.

### 3A.1 Extract (if starting from a .pbix)

```
pbi-tools extract -pbixPath "MyReport.pbix" -extractFolder "./MyReport.PBIP"
```

This produces editable JSON source files under `MyReport.PBIP/Report/`.

### 3A.2 Edit Report Page JSON

Each page is a JSON file under `<project>.Report/definition/pages/`. To add a page:
1. Create a new `<PageName>.json` file following the existing page structure.
2. Register the page in `definition/report.json` (add to the pages array).

### 3A.3 Compile Back to .pbix

```
pbi-tools compile -sourceFolder "./MyReport.PBIP" -outPath "./MyReport-updated.pbix" -overwrite
```

### 3A.4 Validate

Open the output `.pbix` in Power BI Desktop and verify each page renders correctly before sharing.

---

## Step 4: Build Approach B — Python ZIP Manipulation

Use this path when only a `.pbix` file is available. Reference `docs/pbix-layout-format.md` for the full technical schema and `templates/build-report-template.py` as the starter script.

### Critical rules (all mandatory — any violation causes a broken file):

| Rule | Detail |
|---|---|
| Encoding | Write `Report/Layout` as **UTF-16-LE without BOM**: `json.dumps(layout).encode("utf-16-le")` |
| SecurityBindings | Always zero out after modifying layout: write `b""` for the `SecurityBindings` entry |
| Never overwrite source | Set `PBIX_OUT` to a different path from `PBIX_IN` |
| Double-serialisation | `config`, `query`, and `dataTransforms` inside visual containers are **JSON strings**, not raw objects — always wrap with `json.dumps()` |
| Python version | Use `C:\Users\SNEVILLE\.local\bin\python3.14.exe` or `python3.14` |

### 4.1 Load Existing Layout

```python
import zipfile, json

with zipfile.ZipFile(PBIX_IN, "r") as z:
    raw = z.read("Report/Layout").decode("utf-16-le")
layout = json.loads(raw)
```

### 4.2 Build a New Page

Use the helper functions in `templates/build-report-template.py`:
- `make_textbox()` — page title or label
- `make_card()` — single KPI value
- `make_bar_chart()` — category vs measure bar chart
- `make_table()` — tabular data grid

Assemble a page (section) dict and append it to `layout["sections"]`.

### 4.3 Write the Output File

```python
with zipfile.ZipFile(PBIX_IN, "r") as src, zipfile.ZipFile(PBIX_OUT, "w", zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        data = src.read(item.filename)
        if item.filename == "SecurityBindings":
            data = b""
        elif item.filename == "Report/Layout":
            data = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")
        dst.writestr(item, data)
```

### 4.4 Validate

Open `PBIX_OUT` in Power BI Desktop. If the file opens but pages are blank, the most likely cause is incorrect measure names or a double-serialisation error in a visual container field.

---

## Step 5: Visual Design Constraints

When generating visuals programmatically, apply these minimums to avoid generating a report that immediately fails the `report-review` skill:

| Constraint | Rule |
|---|---|
| Every page must have a title textbox | Use `make_textbox()` at position y=0 across the top |
| No pie or donut charts with >3 slices | Use a bar chart instead |
| Every card or chart must have a named visual ID | Use `uid(n)` to generate unique visual names |
| Canvas size | Default to 1280 × 720 unless the user specifies otherwise |
| Measure names must match the model manifest exactly | Mismatches produce blank visuals with no error |
| Maximum ~8 visuals per page | Above this, the page will fail the report-review density check |

---

## Step 6: Output to the User

After building, always provide:
1. The full Python script (or PBIP page JSON) used to generate the report
2. The output file path
3. A brief summary of pages and visuals created
4. Any assumptions made about measure names or table names (for the developer to verify)

---

## References

- `docs/pbix-layout-format.md` — full PBIX ZIP schema, encoding rules, visual container structure
- `docs/tooling-decision.md` — when to use Python ZIP vs pbi-tools vs MCP
- `templates/build-report-template.py` — Python starter script with helper functions
- `docs/model-manifest-template.json` — template for capturing model field names before building
- `.agents/skills/report-review/skill.md` — use after building to validate the output report
- [pbi-tools documentation](https://pbi.tools) — CLI reference for extract and compile commands
