# Report Build Patterns

Agent reference for all Power BI report and model build/edit scenarios.

Load this document after identifying the applicable pattern in `.agents/skills/report-build/skill.md`.

---

## Universal MCP Gotchas

Apply these rules whenever using MCP write operations on Import-mode models. These are universal â€” they apply on all machines and all Power BI versions, regardless of data source.

| Issue | Rule |
|---|---|
| `isKey` rejected on Import-mode tables | Never set `isKey: true` on columns in Import-mode tables. The Vertipaq engine manages row identity via an internal hidden RowNumber column. `isKey` is only valid for DirectQuery tables. This is a universal engine constraint â€” not specific to any SQL Server or installation. |
| M expression tables require explicit `columns` | When creating a table with `mExpression`, you must provide a `columns` array with full type definitions. The engine cannot auto-infer schema from M expressions. |
| Calculated tables must NOT have a `columns` array | When creating a table with `daxExpression`, do NOT include a `columns` property â€” the engine derives columns from the DAX. Including both causes an error. |
| `_Measures` table pattern | Create as a calculated table: `daxExpression: "DATATABLE(\"Placeholder\", STRING, {})"` with `isHidden: true`. No `columns` property. |
| Relationship names are auto-generated | The MCP server auto-generates relationship names from table and column names. This is expected â€” no action needed. |
| `continueOnError` in batch creates | When creating multiple tables in a single batch call, use `options: { continueOnError: true }` so a single failure does not roll back all other tables. |
| Refresh required after creation | After creating tables, always call `partition_operations â†’ Refresh` (type: `Full`) on all new tables before saving or building report pages. Without this, tables load empty. |
| User must save before Python | The user must save the `.pbix` in Power BI Desktop (Ctrl+S) before any Python script can read it. Prompt the user explicitly at this step and wait for their confirmation of the save path. |

---

## Pattern A â€” Build from Scratch

**Use when:** No existing `.pbix`, no PBIP project. Building a new semantic model and report from nothing.

---

### A.1 â€” Discover and Connect

```
connection_operations â†’ ListLocalInstances
```

If no instances are found, ask the user to open Power BI Desktop (File â†’ New) before continuing.

```
connection_operations â†’ Connect
  connectionString: <value from ListLocalInstances result>
```

---

### A.2 â€” Author the Model Manifest

Before creating any tables, document the intended model using `docs/model-manifest-template.json` as the base. Confirm exact names with the user â€” these names will be used verbatim in both MCP table/measure creation and in visual container JSON later.

Key fields to confirm:
- Measures table name (default: `_Measures`)
- All measure names with their format strings
- Dimension table names and the columns that will be used in visuals
- Fact table name and numeric columns

---

### A.3 â€” Create Tables

Use `table_operations â†’ Create`.

**Rules for M expression (Import) tables:**
- Provide both `mExpression` AND an explicit `columns` array
- Do NOT set `isKey: true` on any column â€” the engine manages keys automatically
- Set `summarizeBy: "none"` on key, text, and category columns
- Set `summarizeBy: "sum"` only on numeric fact columns that should aggregate
- Set `dataType` explicitly on every column â€” do not rely on inference

Example column definitions for a fact table:
```json
[
  { "dataType": "int64",   "name": "DealKey",     "sourceColumn": "DealKey",    "summarizeBy": "none" },
  { "dataType": "decimal", "name": "DealValue",   "sourceColumn": "DealValue",  "summarizeBy": "sum", "formatString": "\\$#,0" },
  { "dataType": "int64",   "name": "IsWon",       "sourceColumn": "IsWon",      "summarizeBy": "sum" }
]
```

**Rules for the `_Measures` calculated table:**
```json
{
  "daxExpression": "DATATABLE(\"Placeholder\", STRING, {})",
  "isHidden": true,
  "name": "_Measures"
}
```
No `columns` property. No `mExpression`. `isHidden: true` hides it from report view.

**Batch creates:** Use `options: { continueOnError: true }` so one failure does not block the others.

---

### A.4 â€” Create Relationships

Use `relationship_operations â†’ Create`.

For each relationship:
```json
{
  "fromTable":              "<fact table>",
  "fromColumn":             "<foreign key column>",
  "fromCardinality":        "Many",
  "toTable":                "<dimension table>",
  "toColumn":               "<primary key column>",
  "toCardinality":          "One",
  "crossFilteringBehavior": "SingleDirection",
  "isActive":               true
}
```

Relationship names are auto-generated â€” this is expected behaviour.

---

### A.5 â€” Create Measures

Use `measure_operations â†’ Create`.

For each measure:
```json
{
  "tableName":     "_Measures",
  "name":          "Total Revenue",
  "expression":    "CALCULATE(SUM(FactDeals[DealValue]), FactDeals[IsWon] = 1)",
  "formatString":  "\\$#,0",
  "displayFolder": "Revenue"
}
```

Group related measures using `displayFolder`. Common format strings:
- Integer count: `"#,0"`
- Percentage: `"0.0%"`
- Currency: `"\\$#,0"`
- Decimal: `"#,0.00"`

---

### A.6 â€” Refresh Partitions

```
partition_operations â†’ Refresh (refreshType: "Full")
```

Refresh all data tables and the `_Measures` table. Without this, tables are empty when the file opens.

---

### A.7 â€” Prompt User to Save

**Stop and prompt the user:**

> "Please save the file in Power BI Desktop now (Ctrl+S). Once saved, provide the full file path so I can add the report pages."

Do not proceed to A.8 until the user confirms the save path.

---

### A.8 â€” Build Report Pages (Python ZIP)

With the confirmed `.pbix` path, generate a Python script using the helpers in `templates/build-report-template.py`.

Mandatory rules from `docs/pbix-layout-format.md`:

| Rule | Implementation |
|---|---|
| Encoding | `json.dumps(layout, ensure_ascii=False).encode("utf-16-le")` â€” no BOM |
| SecurityBindings | Write `b""` for this entry â€” stale hash causes "corrupted file" error |
| Never overwrite source | `PBIX_OUT` must be a different path from `PBIX_IN` |
| Double-serialise inner fields | `config`, `query`, `dataTransforms` in visual containers are JSON strings â€” always wrap with `json.dumps()` |
| Replace sections array | `layout["sections"] = new_sections` (for scratch build â€” all pages are new) |

Run the script. Provide the output path and a page/visual summary to the user.

---

## Pattern B â€” Add Pages to Existing Report

**Use when:** A `.pbix` exists with a working model and existing pages. Adding new pages without modifying existing ones.

### Key difference from Pattern A

Do NOT replace `layout["sections"]`. **Append** to the existing list:

```python
import zipfile, json

with zipfile.ZipFile(PBIX_IN, "r") as zf:
    raw = zf.read("Report/Layout").decode("utf-16-le")
layout = json.loads(raw)

# Find the highest existing ordinal so new pages follow on
max_ordinal = max(s.get("ordinal", 0) for s in layout["sections"]) if layout["sections"] else -1

for i, page in enumerate(new_pages):
    page["ordinal"] = max_ordinal + 1 + i
    page["id"]      = max_ordinal + 1 + i
    layout["sections"].append(page)

new_layout = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")

with zipfile.ZipFile(PBIX_IN, "r") as src, zipfile.ZipFile(PBIX_OUT, "w", zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        data = src.read(item.filename)
        if item.filename == "SecurityBindings":
            data = b""
        elif item.filename == "Report/Layout":
            data = new_layout
        dst.writestr(item, data)
```

### Steps

1. Confirm exact measure and column names from the live model (MCP `measure_operations â†’ List`, `table_operations â†’ List`) or from an existing manifest.
2. Build new page containers using `make_*` helpers from `templates/build-report-template.py`.
3. Load the existing layout, append pages (see above), write to new output file.
4. Apply all encoding rules from `docs/pbix-layout-format.md`.

---

## Pattern C â€” Edit Visuals on an Existing Page

**Use when:** A specific visual on an existing page needs to change â€” e.g. swap a measure, change chart type, resize, update a title.

### Steps

1. Load `Report/Layout` from the source `.pbix`.
2. Locate the target page by `displayName`:
```python
page = next(s for s in layout["sections"] if s["displayName"] == "Pipeline Overview")
```
3. Locate the target visual container. Identify by the `name` field inside the double-serialised `config` string, or by position:
```python
for vc in page["visualContainers"]:
    cfg = json.loads(vc["config"])
    if cfg.get("name") == "vis0003":
        # modify cfg here
        vc["config"] = json.dumps(cfg)  # re-serialise after edit
```
4. Update `config`, `query`, and `dataTransforms` as needed. All three must remain JSON strings (double-serialised).
5. Write the modified layout back â€” UTF-16-LE, zero SecurityBindings, new output path.

---

## Pattern D â€” Clone Report with Modifications

**Use when:** Creating a copy of an existing report with targeted changes â€” e.g. a regional variant, translated labels, an extra page, or a filter applied.

### Steps

1. Copy all ZIP entries verbatim to the output path first:
```python
with zipfile.ZipFile(PBIX_IN, "r") as src, zipfile.ZipFile(PBIX_OUT, "w", zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        dst.writestr(item, src.read(item.filename))
```
2. Open `PBIX_OUT` as the working file. Load `Report/Layout`.
3. Apply targeted modifications: add pages (append, not replace), edit specific visual containers, update display names.
4. Write the modified layout back into `PBIX_OUT` â€” since this is already the copy, it is safe to overwrite in a second pass.
5. Apply UTF-16-LE encoding and zero SecurityBindings on the second pass.

---

## Pattern E â€” Update Existing Model via MCP

**Use when:** Power BI Desktop is open with an existing model. Adding or modifying model objects only â€” no report page changes needed.

No Python required for this pattern.

### Adding a measure

```
measure_operations â†’ Create
  tableName:     "_Measures"
  name:          "New Measure Name"
  expression:    "CALCULATE(...)"
  formatString:  "#,0"
  displayFolder: "FolderName"
```

### Updating a measure expression

```
measure_operations â†’ Update
  name:       "Existing Measure Name"
  expression: "CALCULATE(...updated...)"
```

### Adding a column to an existing Import-mode table

```
column_operations â†’ Create
  tableName:    "FactDeals"
  name:         "NewColumn"
  dataType:     "string"
  sourceColumn: "NewColumn"
  summarizeBy:  "none"
```

Do NOT set `isKey: true`. See Universal MCP Gotchas above.

### After model changes

Run a calculate refresh so measures that depend on the changed objects update:
```
partition_operations â†’ Refresh (refreshType: "Calculate")
```

Prompt the user to save in Desktop when complete.

---

## Pattern F â€” Edit PBIP Project Source

**Use when:** A PBIP folder structure is available (`.SemanticModel/` and `.Report/` folders), typically in source control.

### Steps

1. Identify the project root â€” the folder containing `<ProjectName>.SemanticModel/` and `<ProjectName>.Report/`.
2. For model changes: edit TMDL files in `.SemanticModel/definition/`. Measures are in `measures.tmdl` or per-table `.tmdl` files. Relationships are in `relationships.tmdl`.
3. For report page changes: edit page JSON files in `.Report/definition/pages/`. Register new pages in `.Report/definition/report.json`.
4. Compile back to `.pbix`:
```
pbi-tools compile -sourceFolder "./MyReport.PBIP" -outPath "./MyReport-updated.pbix" -overwrite
```
5. Open the output in Power BI Desktop to validate before distributing.

See [pbi-tools documentation](https://pbi.tools) for the full CLI reference. Note: pbi-tools is a third-party open-source tool, not an official Microsoft product.

---

## References

- `docs/pbix-layout-format.md` â€” full PBIX ZIP schema, encoding rules, visual container structure
- `templates/build-report-template.py` â€” Python helper functions (make_textbox, make_card, make_chart, make_table, make_page)
- `docs/model-manifest-template.json` â€” template for capturing model field names
- `docs/tooling-decision.md` â€” decision guide for choosing between MCP, Python ZIP, and pbi-tools
- [pbi-tools documentation](https://pbi.tools) â€” CLI reference for extract and compile
