# PBIX Layout Format — Agent Reference

---

> **Legal and Support Disclaimer — Read Before Use**
>
> The `.pbix` file format is a **proprietary, undocumented Microsoft format**. The techniques described in this document — reading and writing the `Report/Layout` entry inside the `.pbix` ZIP archive — are **not officially supported by Microsoft** and are not part of any published API or SDK.
>
> **Key points:**
>
> - Microsoft has not published the internal schema for `Report/Layout` or the visual container JSON. The structures documented here were derived by inspection and may change between Power BI Desktop versions **without notice or deprecation warning**.
> - There is no guarantee that files produced using this approach will continue to open correctly after a Power BI Desktop update.
> - **pbi-tools** (referenced in this document) is a third-party open-source project maintained independently of Microsoft. It is not an official Microsoft tool and is not supported by Microsoft.
> - Programmatic PBIX manipulation should never be performed on live production reports without a full backup and explicit human sign-off.
> - Before adopting this technique in any commercial or regulated environment, **teams are responsible for verifying that this approach is consistent with their Microsoft licensing terms, their organisation's acceptable-use policy, and any applicable data governance requirements.** The authors of this harness make no warranty regarding legality, compatibility, or fitness for purpose.
>
> **If an officially supported alternative exists for your scenario, prefer it.** Use `pbi-tools extract` / `pbi-tools compile` for PBIP-based workflows, and use the Power BI REST API for service-side operations. Use the direct Python ZIP approach only when no documented alternative is available.

---

## Purpose

This document describes the internal structure of a `.pbix` file as it applies to programmatic report page creation with Python. It covers the ZIP archive format, character encoding requirements, visual container JSON schema, double-serialisation rules, and known failure modes.

This knowledge is required any time an agent needs to **add, modify, or replace report pages** in an existing `.pbix` file without using pbi-tools.

---

## When to Use This Approach vs pbi-tools

| Scenario | Use |
|---|---|
| Adding or modifying pages in an existing `.pbix` | Python ZIP manipulation (this document) |
| Compiling a full PBIP extract back to `.pbix` | `pbi-tools compile` |
| Extracting a `.pbix` to editable source files | `pbi-tools extract` |
| Reviewing model metadata live (tables, measures) | MCP server |

See `docs/tooling-decision.md` for the full updated decision tree.

---

## PBIX File Structure

A `.pbix` file is a ZIP archive. Opening it with `zipfile.ZipFile` gives access to all internal parts.

Key entries:

| Path inside ZIP | Contents |
|---|---|
| `Report/Layout` | JSON report definition (UTF-16-LE, no BOM) |
| `DataMashup` | M query / Power Query definitions |
| `SecurityBindings` | DPAPI-signed hash of the data model — must be zeroed after modifying Layout |
| `[Content_Types].xml` | MIME type declarations |
| `Version` | Single-line version number string |

---

## Critical: Encoding

`Report/Layout` is encoded as **UTF-16-LE without a BOM**.

If you write it as UTF-8 or UTF-16 with BOM, Power BI Desktop will open the file but report it as corrupted or display blank pages with no error message.

```python
# CORRECT
layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")

# WRONG — silent corruption
layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-8")
layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-16")  # adds BOM
```

---

## Critical: SecurityBindings

After modifying `Report/Layout`, the `SecurityBindings` entry is stale. If left unchanged, Power BI Desktop will refuse to open the file with a "file is corrupted or not a supported version" error.

**Always zero out `SecurityBindings`** when writing a modified PBIX:

```python
for item in source_zip.infolist():
    data = source_zip.read(item.filename)
    if item.filename == "SecurityBindings":
        data = b""                          # zero it out
    elif item.filename == "Report/Layout":
        data = new_layout_bytes             # your modified layout
    dest_zip.writestr(item, data)
```

---

## Critical: Never Overwrite the Source File

Always write to a **new output path**. Overwriting the source PBIX in-place while it is open in Power BI Desktop will corrupt the file and may also cause a ZIP write error in Python.

```python
PBIX_IN  = r"C:\path\to\source.pbix"
PBIX_OUT = r"C:\path\to\output.pbix"   # always a different file
```

---

## Layout JSON — Top-Level Structure

```json
{
  "id": 0,
  "resourcePackages": [...],
  "sections": [ <page>, <page>, ... ],
  "config": "{}",
  "layoutOptimization": 0
}
```

The `sections` array contains one object per report page.

---

## Page (Section) Object

```json
{
  "id": 0,
  "name": "unique-no-spaces",
  "displayName": "What Happened",
  "filters": "[]",
  "ordinal": 0,
  "config": "{}",
  "displayOption": 1,
  "width": 1280,
  "height": 720,
  "visualContainers": [ <visual>, <visual>, ... ]
}
```

| Field | Notes |
|---|---|
| `name` | Internal identifier — must be unique across all pages, no spaces |
| `displayName` | Tab label shown in Power BI Desktop |
| `displayOption` | `1` = Fit to page, `2` = Fit to width, `0` = Actual size |
| `width` / `height` | Canvas size in pixels. Default is 1280 × 720 |
| `filters` | Serialised JSON string, use `"[]"` for no filters |

---

## Visual Container Object

```json
{
  "x": 16,
  "y": 70,
  "z": 1001,
  "width": 297,
  "height": 110,
  "config": "<JSON string>",
  "filters": "[]",
  "query": "<JSON string>",
  "dataTransforms": "<JSON string>"
}
```

### Double-Serialisation Rule

`config`, `query`, and `dataTransforms` are **JSON objects serialised to strings** — they are NOT embedded raw objects. This is the single most common mistake when constructing visual containers programmatically.

```python
vc["config"]         = json.dumps(config_obj)          # ✓ string
vc["query"]          = json.dumps(query_obj)            # ✓ string
vc["dataTransforms"] = json.dumps(data_transforms_obj)  # ✓ string

vc["config"]         = config_obj   # ✗ this will break the visual silently
```

---

## `config` Object Structure

```json
{
  "name": "vis0001",
  "layouts": [{
    "id": 0,
    "position": {
      "x": 16, "y": 70, "z": 1001,
      "tabOrder": 1,
      "height": 110, "width": 297
    }
  }],
  "singleVisual": {
    "visualType": "card",
    "projections": {
      "Values": [{ "queryRef": "m.Total Sales", "active": false }]
    },
    "prototypeQuery": {
      "Version": 2,
      "From": [{ "Name": "m", "Entity": "_Measures", "Type": 0 }],
      "Select": [{
        "Measure": {
          "Expression": { "SourceRef": { "Source": "m" } },
          "Property": "Total Sales"
        },
        "Name": "m.Total Sales"
      }]
    }
  }
}
```

---

## Projections Key Names by Visual Type

The `projections` object uses different key names depending on the visual type. Using the wrong key silently produces a visual with no data.

| Visual Type (`visualType`) | Category axis key | Value / measure key |
|---|---|---|
| `card` | — | `"Values"` |
| `columnChart` | `"Category"` | `"Y"` |
| `barChart` | `"Category"` | `"Y"` |
| `lineChart` | `"Category"` | `"Y"` |
| `tableEx` | — | `"Values"` |
| `textbox` | — | — (no projections) |

---

## `query` Object Structure

```json
{
  "Commands": [{
    "SemanticQueryDataShapeCommand": {
      "Query": {
        "Version": 2,
        "From": [ { "Name": "m", "Entity": "_Measures", "Type": 0 } ],
        "Select": [{
          "Measure": {
            "Expression": { "SourceRef": { "Source": "m" } },
            "Property": "Total Sales"
          },
          "Name": "m.Total Sales"
        }]
      },
      "Binding": {
        "Primary": { "Groupings": [{ "Projections": [0] }] },
        "DataReduction": {
          "DataVolume": 3,
          "Primary": { "Window": { "Count": 1000 } }
        },
        "Version": 1
      },
      "ExecutionMetricsKind": 1
    }
  }]
}
```

For charts with a category column and a measure, `Projections` should be `[0, 1]` and `DataReduction` should use `"Top"` instead of `"Window"`:

```json
"Binding": {
  "Primary": { "Groupings": [{ "Projections": [0, 1] }] },
  "DataReduction": {
    "DataVolume": 4,
    "Primary": { "Top": { "Count": 1000 } }
  },
  "Version": 1
}
```

---

## `dataTransforms` Object Structure

```json
{
  "queryMetadata": {
    "Select": [
      { "Restatement": "Total Sales", "Name": "m.Total Sales", "Type": 260 }
    ]
  },
  "visualElements": [
    { "name": "measure", "queryRef": "m.Total Sales", "dataCategory": 0 }
  ]
}
```

`Type` values:
- `260` — measure
- `1` — column

---

## Textbox Visuals

Textboxes use a different `config` structure. They have no `query` or `dataTransforms`.

```json
{
  "singleVisual": {
    "visualType": "textbox",
    "objects": {
      "general": [{
        "properties": {
          "paragraphs": [{
            "textRuns": [{
              "value": "Page Title",
              "textStyle": {
                "fontWeight": "bold",
                "fontSize": "20pt",
                "color": { "solid": { "color": "#1a1a2e" } }
              }
            }],
            "horizontalTextAlignment": "left"
          }]
        }
      }]
    }
  }
}
```

Set `query` and `dataTransforms` to empty string `""` for textboxes.

---

## Complete Python Pattern

```python
import zipfile
import json

PBIX_IN  = r"C:\path\to\source.pbix"
PBIX_OUT = r"C:\path\to\output.pbix"

# 1. Read existing layout
with zipfile.ZipFile(PBIX_IN, "r") as zf:
    raw = zf.read("Report/Layout")

layout = json.loads(raw.decode("utf-16-le"))

# 2. Build new section(s) and append
new_section = {
    "id": len(layout["sections"]),
    "name": "MyNewPage",
    "displayName": "My New Page",
    "filters": "[]",
    "ordinal": len(layout["sections"]),
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 720,
    "visualContainers": [ ]
}
layout["sections"].append(new_section)

# 3. Re-serialise as UTF-16-LE
new_layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")

# 4. Write new PBIX, zeroing SecurityBindings
with zipfile.ZipFile(PBIX_IN, "r") as src, \
     zipfile.ZipFile(PBIX_OUT, "w", zipfile.ZIP_DEFLATED) as dst:
    for item in src.infolist():
        data = src.read(item.filename)
        if item.filename == "SecurityBindings":
            data = b""
        elif item.filename == "Report/Layout":
            data = new_layout_bytes
        dst.writestr(item, data)

print(f"Written: {PBIX_OUT}")
```

---

## Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| "File is corrupted or not a supported version" | `SecurityBindings` not zeroed | Zero it out as shown above |
| Page appears but all visuals are blank | `config`/`query`/`dataTransforms` are raw objects, not strings | `json.dumps()` each one |
| Visual appears but shows no data | Wrong `projections` key name for the visual type | Check the projections key table above |
| Power BI says file is unreadable | Layout written as UTF-8 instead of UTF-16-LE | Use `.encode("utf-16-le")` |
| Measures not found | Measure name in query does not exactly match the name in the model | Check model manifest or MCP |

---

## References

- `templates/build-report-template.py` — starter Python script with helper functions
- `docs/model-manifest-template.json` — template for documenting your model's exact field names
- `docs/tooling-decision.md` — decision guide for when to use Python ZIP vs pbi-tools
- [pbi-tools](https://pbi.tools) — third-party open-source CLI for PBIP workflows (not a Microsoft product)
