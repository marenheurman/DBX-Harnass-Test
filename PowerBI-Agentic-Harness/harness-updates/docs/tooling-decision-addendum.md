# Tooling Decision — Addendum: PBIX Report Page Generation

## Purpose

This document supplements `tooling-decision.md` with guidance specific to **programmatic report page creation**. This scenario was not covered in the original decision guide.

Merge the content below into `tooling-decision.md` when updating the harness.

---

## Updated Decision Tree Addition

Insert this branch after the existing "Is the model currently open in Power BI Desktop?" node:

```
Is the task adding or modifying report pages in a .pbix file?
├── Yes — and you have a PBIP extract (folder structure)
│         → Use `pbi-tools compile` after editing the JSON source files
└── Yes — and you have only a .pbix file (no extract)
          → Use Python ZIP manipulation (see docs/pbix-layout-format.md)
              and templates/build-report-template.py
```

---

## When to Use pbi-tools vs Python ZIP

| Scenario | Recommended Approach |
|---|---|
| Full report rebuild from source-controlled PBIP | `pbi-tools compile` |
| Extracting a `.pbix` to inspect or version-control it | `pbi-tools extract` |
| Adding pages to an existing `.pbix` without a full extract | Python ZipFile + `build-report-template.py` |
| Patching a single visual in an existing `.pbix` | Python ZipFile + `build-report-template.py` |
| Reviewing report layout for quality/accessibility | MCP server + `report-review` skill |

---

## Python ZIP Approach — Quick Reference

Full documentation: `docs/pbix-layout-format.md`
Starter script:     `templates/build-report-template.py`
Model field names:  `docs/model-manifest.json`

### Critical Rules (do not skip)

1. **Encode `Report/Layout` as UTF-16-LE without BOM** — any other encoding silently corrupts the file.
2. **Zero out `SecurityBindings`** — leaving it stale causes a "corrupted file" error on open.
3. **Never write to the same path as the source `.pbix`** — always output to a new file.
4. **Double-serialise `config`, `query`, and `dataTransforms`** — these fields must be JSON strings, not raw objects.

### Projections Key Names

Different visual types use different key names in the `projections` object. Using the wrong key produces a blank-but-valid visual with no data.

| Visual Type | Category key | Value key |
|---|---|---|
| `card` | — | `"Values"` |
| `columnChart` | `"Category"` | `"Y"` |
| `barChart` | `"Category"` | `"Y"` |
| `lineChart` | `"Category"` | `"Y"` |
| `tableEx` | — | `"Values"` |
| `textbox` | — | — |

---

## Model Manifest — Why It Matters

When building report visuals programmatically, the agent must know exact field names. A one-character mismatch in a measure name causes the visual to render empty with no error.

The `docs/model-manifest.json` file was created to solve this. It lists:
- Every table and its columns
- Every measure with its display folder
- All relationships
- Column value notes for ML tables (e.g. `RiskBand` values: Low, Medium, High, Critical)

**Always consult `docs/model-manifest.json` before building report scripts**, instead of guessing column names.

---

## What Was Learned Building the CRM Decision Intelligence Report

This section records lessons from the first report build session (March 2026) for future agent runs.

### Lesson 1: `query` and `config` must be serialised strings

The single most common error. Both fields look like objects but must be passed through `json.dumps()`:

```python
vc["config"] = json.dumps(config_obj)   # ✓
vc["config"] = config_obj               # ✗ — blank visuals
```

### Lesson 2: The `prototypeQuery` inside `config` must match `query`

The `config` object contains its own copy of the query (`prototypeQuery`). If this diverges from the outer `query` field, the visual bindings break. The `From` and `Select` arrays should be identical in both places.

### Lesson 3: SecurityBindings error is easy to miss

Power BI Desktop's error message for a stale `SecurityBindings` is "this file appears to be corrupted" — which looks like a ZIP problem. It is not. Zero out the entry.

### Lesson 4: Alias collisions break charts

Each entity in the `From` array needs a unique alias within a single visual. If two visual containers on the same page happen to use the same alias for different entities, the second one may silently fail. Aliases only need to be unique per visual, not per page — but keeping them stable and descriptive (e.g. `"t"` for DimSalesTerritory, `"c"` for ChurnScores) avoids confusion.

### Lesson 5: ML table column names must be verified

Column names in `ChurnScores`, `CampaignActions`, and `RFM_Customers` come from the model build script and are not standard AdventureWorks names. They are documented in `docs/model-manifest.json`. Do not guess them.
