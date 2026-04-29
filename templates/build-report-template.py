"""
build-report-template.py
========================
Starter template for adding report pages to an existing .pbix file.

DISCLAIMER
----------
This script manipulates the internal structure of a .pbix file directly.
The .pbix format is a proprietary, undocumented Microsoft format. This
approach is NOT officially supported by Microsoft and is not part of any
published API or SDK. The internal format may change between Power BI
Desktop versions without notice.

Before using this script in any commercial or regulated environment, teams
are responsible for verifying that this approach is consistent with their
Microsoft licensing terms and their organisation's acceptable-use policies.

See docs/pbix-layout-format.md for the full technical reference and
the complete legal disclaimer.

Usage
-----
  1. Set PBIX_IN and PBIX_OUT at the top.
  2. Define your pages using the make_* helper functions below.
  3. Append your pages to the `new_sections` list.
  4. Run the script — it writes a new PBIX file at PBIX_OUT.

Requirements:
  - Python 3.8+, stdlib only (zipfile, json).
  - Read docs/pbix-layout-format.md for a full explanation of the JSON schema.
  - Read docs/model-manifest-template.json, then create your own model manifest
    with exact table/column/measure names for your model.

Key rules (see pbix-layout-format.md for detail):
  - Report/Layout must be written as UTF-16-LE without BOM.
  - SecurityBindings must be zeroed or the file will appear corrupted.
  - config, query, and dataTransforms are JSON strings, not raw objects.
  - Never write to the same path as PBIX_IN — always use a new output path.
"""

import zipfile
import json

# ─── Paths ────────────────────────────────────────────────────────────────────

PBIX_IN  = r"C:\path\to\source.pbix"   # <-- change this
PBIX_OUT = r"C:\path\to\output.pbix"   # <-- change this (must be different)

# ─── Position / container helpers ─────────────────────────────────────────────

def uid(n: int) -> str:
    """Generate a padded visual name string, e.g. vis0001."""
    return f"vis{n:04d}"


def _pos(x: int, y: int, z: int, w: int, h: int, tab: int) -> dict:
    return {"x": x, "y": y, "z": z, "tabOrder": tab, "height": h, "width": w}


def _vc(x: int, y: int, w: int, h: int, tab: int,
        config_obj: dict, query_obj: dict = None, dt_obj: dict = None) -> dict:
    """Build a visual container dict with double-serialised inner fields."""
    return {
        "x": x,
        "y": y,
        "z": 1000 + tab,
        "width": w,
        "height": h,
        "config":         json.dumps(config_obj),
        "filters":        "[]",
        "query":          json.dumps(query_obj) if query_obj else "",
        "dataTransforms": json.dumps(dt_obj)    if dt_obj    else "",
    }

# ─── Textbox ──────────────────────────────────────────────────────────────────

def make_textbox(vid: str, x: int, y: int, w: int, h: int,
                 text: str, tab: int = 0,
                 font_size: str = "20pt", color: str = "#1a1a2e") -> dict:
    """
    Plain text label / page title.

    Args:
        vid:       Visual name, e.g. uid(1).
        x, y:      Top-left position on canvas (pixels).
        w, h:      Width and height (pixels).
        text:      Display text.
        tab:       Tab order (controls z-layering).
        font_size: CSS font size string, e.g. "20pt".
        color:     Hex colour string for text.
    """
    cfg = {
        "name": vid,
        "layouts": [{"id": 0, "position": _pos(x, y, 1000 + tab, w, h, tab)}],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": text,
                                "textStyle": {
                                    "fontWeight": "bold",
                                    "fontSize": font_size,
                                    "color": {"solid": {"color": color}}
                                }
                            }],
                            "horizontalTextAlignment": "left"
                        }]
                    }
                }]
            }
        }
    }
    return _vc(x, y, w, h, tab, cfg)  # query and dataTransforms left empty

# ─── Card (single measure KPI) ────────────────────────────────────────────────

def make_card(vid: str, x: int, y: int, w: int, h: int,
              measure_name: str, measures_table: str = "_Measures",
              tab: int = 0) -> dict:
    """
    Single-value KPI card showing one measure.

    Args:
        vid:            Visual name, e.g. uid(2).
        x, y, w, h:     Position and size.
        measure_name:   Exact measure name from _Measures table
                        (see docs/model-manifest-template.json, then your
                        project-specific model manifest).
        measures_table: Table that hosts the measure. Default: "_Measures".
        tab:            Tab order.
    """
    src_alias = "m"
    qref = f"{src_alias}.{measure_name}"
    from_c = [{"Name": src_alias, "Entity": measures_table, "Type": 0}]
    select = [{
        "Measure": {
            "Expression": {"SourceRef": {"Source": src_alias}},
            "Property": measure_name
        },
        "Name": qref
    }]
    cfg = {
        "name": vid,
        "layouts": [{"id": 0, "position": _pos(x, y, 1000 + tab, w, h, tab)}],
        "singleVisual": {
            "visualType": "card",
            "projections": {"Values": [{"queryRef": qref, "active": False}]},
            "prototypeQuery": {"Version": 2, "From": from_c, "Select": select}
        }
    }
    query = {"Commands": [{"SemanticQueryDataShapeCommand": {
        "Query":   {"Version": 2, "From": from_c, "Select": select},
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 1000}}},
            "Version": 1
        },
        "ExecutionMetricsKind": 1
    }}]}
    dt = {
        "queryMetadata": {
            "Select": [{"Restatement": measure_name, "Name": qref, "Type": 260}]
        },
        "visualElements": [{"name": "measure", "queryRef": qref, "dataCategory": 0}]
    }
    return _vc(x, y, w, h, tab, cfg, query, dt)

# ─── Column / Line / Bar chart (one category column + one measure) ─────────────

def make_chart(vid: str, x: int, y: int, w: int, h: int,
               visual_type: str,
               cat_entity: str, cat_alias: str, cat_col: str,
               measure_name: str, measures_table: str = "_Measures",
               tab: int = 0) -> dict:
    """
    Simple chart with one category and one measure.

    Args:
        vid:            Visual name.
        x, y, w, h:     Position and size.
        visual_type:    Power BI visual type string:
                          "columnChart", "barChart", "lineChart"
        cat_entity:     Table name for the category column,
                          e.g. "DimSalesTerritory".
        cat_alias:      Short alias for the category table, e.g. "t".
                          Must be unique within the page.
        cat_col:        Column name within cat_entity, e.g. "Region".
        measure_name:   Exact measure name (see model manifest).
        measures_table: Table hosting the measure. Default: "_Measures".
        tab:            Tab order.

    Projections key mapping:
        columnChart / barChart / lineChart -> Category + Y
    """
    cat_qref  = f"{cat_alias}.{cat_col}"
    meas_qref = f"m.{measure_name}"
    from_c = [
        {"Name": cat_alias, "Entity": cat_entity,      "Type": 0},
        {"Name": "m",       "Entity": measures_table,  "Type": 0}
    ]
    select = [
        {
            "Column": {
                "Expression": {"SourceRef": {"Source": cat_alias}},
                "Property": cat_col
            },
            "Name": cat_qref
        },
        {
            "Measure": {
                "Expression": {"SourceRef": {"Source": "m"}},
                "Property": measure_name
            },
            "Name": meas_qref
        }
    ]
    cfg = {
        "name": vid,
        "layouts": [{"id": 0, "position": _pos(x, y, 1000 + tab, w, h, tab)}],
        "singleVisual": {
            "visualType": visual_type,
            "projections": {
                "Category": [{"queryRef": cat_qref,  "active": False}],
                "Y":         [{"queryRef": meas_qref, "active": False}]
            },
            "prototypeQuery": {"Version": 2, "From": from_c, "Select": select}
        }
    }
    query = {"Commands": [{"SemanticQueryDataShapeCommand": {
        "Query":   {"Version": 2, "From": from_c, "Select": select},
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1]}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"Top": {"Count": 1000}}},
            "Version": 1
        },
        "ExecutionMetricsKind": 1
    }}]}
    dt = {
        "queryMetadata": {
            "Select": [
                {"Restatement": cat_col,      "Name": cat_qref,  "Type": 1},
                {"Restatement": measure_name, "Name": meas_qref, "Type": 260}
            ]
        },
        "visualElements": [
            {"name": "category", "queryRef": cat_qref,  "dataCategory": 0},
            {"name": "measure",  "queryRef": meas_qref, "dataCategory": 0}
        ]
    }
    return _vc(x, y, w, h, tab, cfg, query, dt)

# ─── Table visual (multiple columns and/or measures) ──────────────────────────

def make_table(vid: str, x: int, y: int, w: int, h: int,
               columns: list, tab: int = 0) -> dict:
    """
    Multi-column table visual.

    Args:
        vid:     Visual name.
        x, y, w, h: Position and size.
        columns: List of tuples:
                   (entity_name, alias, column_name, is_measure)
                 Example:
                   [
                     ("DimCustomer",   "c",  "CustomerName",   False),
                     ("ChurnScores",   "cs", "RiskBand",        False),
                     ("CampaignActions","ca","ActionType",      False),
                     ("_Measures",     "m",  "Total Sales",     True),
                   ]
                 Aliases must be unique per entity. Columns from the same
                 entity should share the same alias.
        tab:     Tab order.
    """
    from_c = []
    seen   = {}
    for entity, alias, col, is_measure in columns:
        if alias not in seen:
            seen[alias] = entity
            from_c.append({"Name": alias, "Entity": entity, "Type": 0})

    select = []
    for entity, alias, col, is_measure in columns:
        qref = f"{alias}.{col}"
        if is_measure:
            select.append({
                "Measure": {
                    "Expression": {"SourceRef": {"Source": alias}},
                    "Property": col
                },
                "Name": qref
            })
        else:
            select.append({
                "Column": {
                    "Expression": {"SourceRef": {"Source": alias}},
                    "Property": col
                },
                "Name": qref
            })

    proj_vals = [{"queryRef": f"{alias}.{col}", "active": False}
                 for _, alias, col, _ in columns]

    cfg = {
        "name": vid,
        "layouts": [{"id": 0, "position": _pos(x, y, 1000 + tab, w, h, tab)}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {"Values": proj_vals},
            "prototypeQuery": {"Version": 2, "From": from_c, "Select": select}
        }
    }
    query = {"Commands": [{"SemanticQueryDataShapeCommand": {
        "Query":   {"Version": 2, "From": from_c, "Select": select},
        "Binding": {
            "Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
            "Version": 1
        },
        "ExecutionMetricsKind": 1
    }}]}
    dt = {
        "queryMetadata": {
            "Select": [
                {"Restatement": col, "Name": f"{alias}.{col}",
                 "Type": 260 if is_measure else 1}
                for _, alias, col, is_measure in columns
            ]
        },
        "visualElements": [
            {"name": f"col{i}", "queryRef": f"{alias}.{col}", "dataCategory": 0}
            for i, (_, alias, col, _) in enumerate(columns)
        ]
    }
    return _vc(x, y, w, h, tab, cfg, query, dt)

# ─── Page builder helper ───────────────────────────────────────────────────────

def make_page(page_name: str, display_name: str, ordinal: int,
              containers: list,
              width: int = 1280, height: int = 720) -> dict:
    """
    Wrap a list of visual containers into a page (section) object.

    Args:
        page_name:    Internal name — unique, no spaces.
        display_name: Tab label shown in Power BI Desktop.
        ordinal:      Page order (0-indexed).
        containers:   List of visual container dicts from make_* helpers.
        width/height: Canvas size in pixels. Default 1280 x 720.
    """
    return {
        "id": ordinal,
        "name": page_name,
        "displayName": display_name,
        "filters": "[]",
        "ordinal": ordinal,
        "config": "{}",
        "displayOption": 1,
        "width": width,
        "height": height,
        "visualContainers": containers
    }

# =============================================================================
# DEFINE YOUR PAGES HERE
# =============================================================================
# Replace / extend the example below with your own pages.
# Use uid(n) to generate unique visual names — increment n across all pages.

page1_visuals = []
t = 0   # tab counter — increment for each visual added to a page

# Page title
page1_visuals.append(
    make_textbox(uid(1), 16, 10, 1248, 48, "Page Title Here", tab=t)
); t += 1

# KPI card
page1_visuals.append(
    make_card(uid(2), 16, 70, 297, 110, "Total Sales", tab=t)
); t += 1

# Column chart — sales by territory
page1_visuals.append(
    make_chart(uid(3), 16, 200, 800, 480,
               "columnChart",
               "DimSalesTerritory", "t", "Region",
               "Total Sales", tab=t)
); t += 1

page1 = make_page("Page1", "My First Page", ordinal=0, containers=page1_visuals)

# Add more pages here:
# page2 = make_page("Page2", "My Second Page", ordinal=1, containers=[...])

new_sections = [page1]  # Add page2, page3, etc.

# =============================================================================
# WRITE PBIX
# =============================================================================

def build_pbix(pbix_in: str, pbix_out: str, sections: list) -> None:
    """
    Read an existing PBIX, replace its report pages, write a new PBIX.

    - Reads Report/Layout as UTF-16-LE.
    - Replaces the sections array entirely with `sections`.
    - Zeroes out SecurityBindings.
    - Writes output as UTF-16-LE.
    """
    with zipfile.ZipFile(pbix_in, "r") as zf:
        raw_layout = zf.read("Report/Layout")

    layout = json.loads(raw_layout.decode("utf-16-le"))
    layout["sections"] = sections

    new_layout_bytes = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")

    with zipfile.ZipFile(pbix_in, "r") as src, \
         zipfile.ZipFile(pbix_out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "SecurityBindings":
                data = b""
            elif item.filename == "Report/Layout":
                data = new_layout_bytes
            dst.writestr(item, data)

    print(f"Written: {pbix_out}")


if __name__ == "__main__":
    build_pbix(PBIX_IN, PBIX_OUT, new_sections)
