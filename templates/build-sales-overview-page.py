"""
build-sales-overview-page.py
============================
Adds a "Sales Overview" report page to an existing Adventure Works .pbix file.

Harness references applied:
  - docs/report-build-patterns.md  → Pattern B (append page, never replace)
  - docs/pbix-layout-format.md     → UTF-16-LE encoding, SecurityBindings zeroed
  - templates/build-report-template.py → make_* helper functions
  - .agents/skills/naming-conventions/SKILL.md → exact field names from live model

Model manifest (derived from live MCP inspection):
  Measures table : _Measures
  Measures used  : Total Sales, Gross Profit, Total Orders, Gross Profit %
  Dimensions     : Sales Territory[Region], Date[Calendar Year], Product[Product Line]

Canvas: 1280 x 720 px

Page layout
  Row 1  y=10  h=48   Page title
  Row 2  y=70  h=110  Four KPI cards (Total Sales | Gross Profit | Total Orders | Gross Profit %)
  Row 3  y=200 h=495  Three charts:
           - Clustered column: Total Sales by Region
           - Line chart      : Total Sales by Calendar Year
           - Bar chart       : Total Sales by Product Line

DISCLAIMER
----------
This script manipulates the internal structure of a .pbix file directly.
The .pbix format is a proprietary, undocumented Microsoft format.
See docs/pbix-layout-format.md for the full legal disclaimer before use.
"""

import zipfile
import json

# ─── CONFIGURE PATHS ──────────────────────────────────────────────────────────
# Update these two paths before running.

PBIX_IN  = r"C:\Users\abarkhui\OneDrive - Capgemini\AgenticAI The Forge\AGenticAI Test 27-5.pbix"
PBIX_OUT = r"C:\Users\abarkhui\OneDrive - Capgemini\AgenticAI The Forge\AGenticAI Test 27-5 - Sales Overview.pbix"

# ─── Position / container helpers (from build-report-template.py) ─────────────

def uid(n: int) -> str:
    return f"vis{n:04d}"

def _pos(x, y, z, w, h, tab):
    return {"x": x, "y": y, "z": z, "tabOrder": tab, "height": h, "width": w}

def _vc(x, y, w, h, tab, config_obj, query_obj=None, dt_obj=None):
    return {
        "x": x, "y": y, "z": 1000 + tab,
        "width": w, "height": h,
        "config":         json.dumps(config_obj),
        "filters":        "[]",
        "query":          json.dumps(query_obj) if query_obj else "",
        "dataTransforms": json.dumps(dt_obj)    if dt_obj    else "",
    }

# ─── make_textbox ─────────────────────────────────────────────────────────────

def make_textbox(vid, x, y, w, h, text, tab=0, font_size="20pt", color="#1a1a2e"):
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
    return _vc(x, y, w, h, tab, cfg)

# ─── make_card ────────────────────────────────────────────────────────────────

def make_card(vid, x, y, w, h, measure_name, measures_table="_Measures", tab=0):
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

# ─── make_chart ───────────────────────────────────────────────────────────────

def make_chart(vid, x, y, w, h, visual_type,
               cat_entity, cat_alias, cat_col,
               measure_name, measures_table="_Measures", tab=0):
    cat_qref  = f"{cat_alias}.{cat_col}"
    meas_qref = f"m.{measure_name}"
    from_c = [
        {"Name": cat_alias, "Entity": cat_entity,     "Type": 0},
        {"Name": "m",       "Entity": measures_table, "Type": 0}
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

# ─── make_page ────────────────────────────────────────────────────────────────

def make_page(page_name, display_name, ordinal, containers, width=1280, height=720):
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

# ─── BUILD SALES OVERVIEW PAGE ────────────────────────────────────────────────
# Canvas: 1280 x 720
# Layout:
#   Row 1 (y=010, h=048): Page title textbox
#   Row 2 (y=070, h=110): KPI cards — Total Sales | Gross Profit | Total Orders | Gross Profit %
#   Row 3 (y=200, h=495): Charts    — by Region (column) | by Year (line) | by Product Line (bar)

visuals = []
t = 0  # tab / z-order counter

# ── Row 1: Title ──────────────────────────────────────────────────────────────
visuals.append(
    make_textbox(uid(1), 16, 10, 1248, 48, "Sales Overview", tab=t,
                 font_size="24pt", color="#1a1a2e")
)
t += 1

# ── Row 2: KPI Cards ──────────────────────────────────────────────────────────
# Four cards, each 296px wide with 16px padding between, starting at x=16
CARD_W, CARD_H, CARD_Y = 296, 110, 70
card_specs = [
    ("Total Sales",    16),
    ("Gross Profit",   328),
    ("Total Orders",   640),
    ("Gross Profit %", 952),
]
for i, (measure, cx) in enumerate(card_specs):
    visuals.append(make_card(uid(2 + i), cx, CARD_Y, CARD_W, CARD_H, measure, tab=t))
    t += 1

# ── Row 3: Charts ─────────────────────────────────────────────────────────────
CHART_Y, CHART_H = 200, 495

# Clustered column — Total Sales by Region
visuals.append(
    make_chart(uid(6), 16, CHART_Y, 397, CHART_H,
               "columnChart",
               "Sales Territory", "st", "Region",
               "Total Sales", tab=t)
)
t += 1

# Line chart — Total Sales by Calendar Year
visuals.append(
    make_chart(uid(7), 429, CHART_Y, 397, CHART_H,
               "lineChart",
               "Date", "d", "Calendar Year",
               "Total Sales", tab=t)
)
t += 1

# Bar chart — Total Sales by Product Line
visuals.append(
    make_chart(uid(8), 842, CHART_Y, 422, CHART_H,
               "barChart",
               "Product", "p", "Product Line",
               "Total Sales", tab=t)
)
t += 1

sales_overview_page = make_page(
    page_name    = "SalesOverview",
    display_name = "Sales Overview",
    ordinal      = 0,
    containers   = visuals
)

# ─── WRITE PBIX (Pattern B — append, never replace existing pages) ────────────

def append_page(pbix_in: str, pbix_out: str, new_page: dict) -> None:
    """
    Load an existing PBIX layout, append one page, write to a new output file.
    Follows Pattern B from docs/report-build-patterns.md:
      - Never replaces existing sections
      - Assigns ordinal = max(existing) + 1
      - Zeroes SecurityBindings
      - Writes Report/Layout as UTF-16-LE without BOM
    """
    with zipfile.ZipFile(pbix_in, "r") as zf:
        raw = zf.read("Report/Layout").decode("utf-16-le")
    layout = json.loads(raw)

    existing = layout.get("sections", [])
    max_ordinal = max((s.get("ordinal", 0) for s in existing), default=-1)
    new_page["ordinal"] = max_ordinal + 1
    new_page["id"]      = max_ordinal + 1
    existing.append(new_page)
    layout["sections"] = existing

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

    print(f"[OK] Written: {pbix_out}")
    print(f"     Page   : {new_page['displayName']}")
    print(f"     Visuals: {len(new_page['visualContainers'])} containers")


if __name__ == "__main__":
    append_page(PBIX_IN, PBIX_OUT, sales_overview_page)
