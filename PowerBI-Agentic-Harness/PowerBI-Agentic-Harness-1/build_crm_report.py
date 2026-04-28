"""
build_crm_report.py
===================
Generates a 3-page CRM report for crm20260331.pbix.

Pages
-----
  1. CRM Sales Overview  — 4 KPI cards + 2 charts (territory, category)
  2. Internet Sales       — 4 KPI cards + 2 charts (trend by year, by category)
  3. Reseller Performance — 4 KPI cards + 2 charts (territory, business type)

Model measure locations (confirmed from live model):
  FactInternetSales  → Internet Sales, Combined, Customers measures (15)
  FactResellerSales  → Reseller Sales measures (9)

See docs/pbix-layout-format.md for schema reference.
"""

import zipfile
import json

# ── Paths ─────────────────────────────────────────────────────────────────────

PBIX_IN  = r"C:\Users\SNEVILLE\Power BI MCP Demo\Power BI File\crm20260331.pbix"
PBIX_OUT = r"C:\Users\SNEVILLE\Power BI MCP Demo\Power BI File\crm20260331_v2.pbix"

# ── Helpers ───────────────────────────────────────────────────────────────────

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


def make_textbox(vid, x, y, w, h, text, tab=0,
                 font_size="24pt", color="#1a1a2e"):
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


def make_card(vid, x, y, w, h, measure_name, measures_table, tab=0):
    src = "m"
    qref = f"{src}.{measure_name}"
    from_c = [{"Name": src, "Entity": measures_table, "Type": 0}]
    select = [{
        "Measure": {"Expression": {"SourceRef": {"Source": src}},
                    "Property": measure_name},
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


def make_chart(vid, x, y, w, h, visual_type,
               cat_entity, cat_alias, cat_col,
               measure_name, measures_table, tab=0):
    cat_qref  = f"{cat_alias}.{cat_col}"
    meas_qref = f"m.{measure_name}"
    from_c = [
        {"Name": cat_alias, "Entity": cat_entity,     "Type": 0},
        {"Name": "m",       "Entity": measures_table, "Type": 0}
    ]
    select = [
        {"Column":  {"Expression": {"SourceRef": {"Source": cat_alias}},
                     "Property": cat_col},
         "Name": cat_qref},
        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}},
                     "Property": measure_name},
         "Name": meas_qref}
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


def make_page(page_name, display_name, ordinal, containers,
              width=1280, height=720):
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


# ── Page 1 — CRM Sales Overview ───────────────────────────────────────────────
# Layout: title | 4 KPI cards | col chart (territory) + bar chart (category)
# Canvas 1280 x 720
#   Title:     y=10, h=44
#   Cards:     y=70, h=100   (4 × w=294, gap=12, start x=16)
#   Charts:    y=190, h=500  (left w=612, right w=620, gap=16)

p1, t = [], 0

p1.append(make_textbox(uid(1), 16, 10, 900, 44,
                       "CRM Sales Overview", tab=t)); t += 1

# KPI row — all measures from FactInternetSales
INET = "FactInternetSales"
RESL = "FactResellerSales"
CARD_W, CARD_H, CARD_Y = 294, 100, 70
card_xs = [16, 326, 636, 946]

p1.append(make_card(uid(2),  card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Total Sales Amount", INET, tab=t)); t += 1
p1.append(make_card(uid(3),  card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Internet Sales Amount", INET, tab=t)); t += 1
p1.append(make_card(uid(4),  card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Reseller Sales Amount", RESL, tab=t)); t += 1
p1.append(make_card(uid(5),  card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Unique Customers", INET, tab=t)); t += 1

# Column chart — Total Sales by Territory Region
p1.append(make_chart(uid(6), 16, 190, 612, 500,
                     "columnChart",
                     "DimSalesTerritory", "st", "SalesTerritoryRegion",
                     "Total Sales Amount", INET, tab=t)); t += 1

# Bar chart — Total Sales by Product Category
p1.append(make_chart(uid(7), 644, 190, 620, 500,
                     "barChart",
                     "DimProductCategory", "pc", "EnglishProductCategoryName",
                     "Total Sales Amount", INET, tab=t)); t += 1

page1 = make_page("SalesOverview", "CRM Sales Overview", ordinal=0,
                  containers=p1)


# ── Page 2 — Internet Sales ───────────────────────────────────────────────────
# Layout: title | 4 KPI cards | line chart (trend by year) + col chart (category)

p2 = []

p2.append(make_textbox(uid(8), 16, 10, 900, 44,
                       "Internet Sales", tab=t)); t += 1

p2.append(make_card(uid(9),  card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Internet Sales Amount", INET, tab=t)); t += 1
p2.append(make_card(uid(10), card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Internet Gross Profit", INET, tab=t)); t += 1
p2.append(make_card(uid(11), card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Internet Gross Profit Margin", INET, tab=t)); t += 1
p2.append(make_card(uid(12), card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Internet Order Count", INET, tab=t)); t += 1

# Line chart — Internet Sales Amount trend by Calendar Year
p2.append(make_chart(uid(13), 16, 190, 612, 500,
                     "lineChart",
                     "DimDate", "dd", "CalendarYear",
                     "Internet Sales Amount", INET, tab=t)); t += 1

# Column chart — Internet Sales Amount by Product Category
p2.append(make_chart(uid(14), 644, 190, 620, 500,
                     "columnChart",
                     "DimProductCategory", "pc2", "EnglishProductCategoryName",
                     "Internet Sales Amount", INET, tab=t)); t += 1

page2 = make_page("InternetSales", "Internet Sales", ordinal=1,
                  containers=p2)


# ── Page 3 — Reseller Performance ────────────────────────────────────────────
# Layout: title | 4 KPI cards | col chart (territory) + bar chart (business type)

p3 = []

p3.append(make_textbox(uid(15), 16, 10, 900, 44,
                       "Reseller & Channel Performance", tab=t)); t += 1

p3.append(make_card(uid(16), card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Reseller Sales Amount", RESL, tab=t)); t += 1
p3.append(make_card(uid(17), card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Reseller Gross Profit", RESL, tab=t)); t += 1
p3.append(make_card(uid(18), card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Reseller Gross Profit Margin", RESL, tab=t)); t += 1
p3.append(make_card(uid(19), card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Reseller Order Count", RESL, tab=t)); t += 1

# Column chart — Reseller Sales by Territory
p3.append(make_chart(uid(20), 16, 190, 612, 500,
                     "columnChart",
                     "DimSalesTerritory", "st2", "SalesTerritoryRegion",
                     "Reseller Sales Amount", RESL, tab=t)); t += 1

# Bar chart — Reseller Sales by Business Type
p3.append(make_chart(uid(21), 644, 190, 620, 500,
                     "barChart",
                     "DimReseller", "rs", "BusinessType",
                     "Reseller Sales Amount", RESL, tab=t)); t += 1

page3 = make_page("ResellerPerf", "Reseller Performance", ordinal=2,
                  containers=p3)


# ── Write PBIX ────────────────────────────────────────────────────────────────

def build_pbix(pbix_in, pbix_out, sections):
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
    build_pbix(PBIX_IN, PBIX_OUT, [page1, page2, page3])
    print("Done. Open crm20260331_v2.pbix in Power BI Desktop.")
