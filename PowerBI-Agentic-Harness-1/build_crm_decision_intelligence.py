"""
build_crm_decision_intelligence.py
====================================
Generates a 5-page CRM Decision Intelligence report.

Source PBIX : crm20260331.pbix  (connected to AdventureWorksDW2022)
Output PBIX : crm_decision_intelligence_v1.pbix

Pages
-----
  1. Executive Dashboard     — Total KPIs + territory + YoY trend
  2. Customer Intelligence   — Customer KPIs + country breakdown + occupation
  3. Internet Sales          — Internet KPIs + trend by year + by product category
  4. Reseller & Channel      — Reseller KPIs + territory + business type
  5. Product Intelligence    — Product KPIs + category + sub-category

Model layout (AdventureWorksDW2022)
------------------------------------
  FactInternetSales  — hosts: Total Sales Amount, Internet Sales Amount,
                              Internet Gross Profit, Internet Gross Profit Margin,
                              Internet Order Count, Unique Customers
  FactResellerSales  — hosts: Reseller Sales Amount, Reseller Gross Profit,
                              Reseller Gross Profit Margin, Reseller Order Count

Decision Intelligence framing
------------------------------
  Page 1 — What happened overall?
  Page 2 — Who are our customers and where?
  Page 3 — How are internet sales performing?
  Page 4 — How are reseller channels performing?
  Page 5 — Which products are driving revenue?

See docs/pbix-layout-format.md for JSON schema reference.
"""

import zipfile
import json

# ── Paths ─────────────────────────────────────────────────────────────────────

PBIX_IN  = r"C:\Users\SNEVILLE\Power BI MCP Demo\Power BI File\crm20260331.pbix"
PBIX_OUT = r"C:\Users\SNEVILLE\Power BI MCP Demo\Power BI File\crm_decision_intelligence_v1.pbix"

# ── Source table / measure constants ─────────────────────────────────────────

INET = "FactInternetSales"   # table hosting internet sales measures
RESL = "FactResellerSales"   # table hosting reseller sales measures

# ── Canvas layout constants ───────────────────────────────────────────────────

CANVAS_W  = 1280
CANVAS_H  = 720
TITLE_H   = 48
CARD_H    = 100
CARD_W    = 294   # (1280 - 32 - 3*16) / 4 ≈ 294
CARD_Y    = TITLE_H + 16        # 64
CHART_Y   = CARD_Y + CARD_H + 16  # 180
CHART_H   = CANVAS_H - CHART_Y - 16  # 508
CHART_W_L = 612
CHART_W_R = 620
CHART_X_R = CHART_W_L + 32

card_xs = [16, 326, 636, 946]   # x positions for 4 cards

# ── Helpers ───────────────────────────────────────────────────────────────────

_vid_counter = 0


def uid() -> str:
    """Return next sequential visual name."""
    global _vid_counter
    _vid_counter += 1
    return f"vis{_vid_counter:04d}"


def _pos(x, y, z, w, h, tab):
    return {"x": x, "y": y, "z": z, "tabOrder": tab, "height": h, "width": w}


def _vc(x, y, w, h, tab, config_obj, query_obj=None, dt_obj=None):
    """Build a visual container with correctly double-serialised inner fields."""
    return {
        "x": x, "y": y, "z": 1000 + tab,
        "width": w, "height": h,
        "config":         json.dumps(config_obj),
        "filters":        "[]",
        "query":          json.dumps(query_obj) if query_obj else "",
        "dataTransforms": json.dumps(dt_obj)    if dt_obj    else "",
    }


def make_textbox(x, y, w, h, text, tab,
                 font_size="22pt", color="#1a1a2e"):
    """Plain text page title."""
    v = uid()
    cfg = {
        "name": v,
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


def make_card(x, y, w, h, measure_name, measures_table, tab):
    """Single-value KPI card."""
    v = uid()
    src = "m"
    qref = f"{src}.{measure_name}"
    from_c = [{"Name": src, "Entity": measures_table, "Type": 0}]
    select = [{
        "Measure": {
            "Expression": {"SourceRef": {"Source": src}},
            "Property": measure_name
        },
        "Name": qref
    }]
    cfg = {
        "name": v,
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


def make_chart(x, y, w, h, visual_type,
               cat_entity, cat_alias, cat_col,
               measure_name, measures_table, tab):
    """
    Chart with one category dimension and one measure.
    visual_type: "columnChart" | "barChart" | "lineChart"
    """
    v = uid()
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
        "name": v,
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


def make_page(page_name, display_name, ordinal, containers):
    return {
        "id": ordinal,
        "name": page_name,
        "displayName": display_name,
        "filters": "[]",
        "ordinal": ordinal,
        "config": "{}",
        "displayOption": 1,
        "width": CANVAS_W,
        "height": CANVAS_H,
        "visualContainers": containers
    }


# =============================================================================
# PAGE 1 — Executive Dashboard
# What happened overall?
# KPIs: Total Sales Amount | Internet Sales Amount | Reseller Sales Amount | Unique Customers
# Charts: Total Sales by Territory Region | Internet Sales Trend by Year
# =============================================================================

t = 0   # global tab / z-order counter

p1 = []
p1.append(make_textbox(16, 10, 900, TITLE_H,
                       "CRM Decision Intelligence — Executive Dashboard", t)); t += 1

# KPI row
p1.append(make_card(card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Total Sales Amount", INET, t)); t += 1
p1.append(make_card(card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Internet Sales Amount", INET, t)); t += 1
p1.append(make_card(card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Reseller Sales Amount", RESL, t)); t += 1
p1.append(make_card(card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Unique Customers", INET, t)); t += 1

# Total Sales by Sales Territory Region
p1.append(make_chart(16, CHART_Y, CHART_W_L, CHART_H,
                     "columnChart",
                     "DimSalesTerritory", "st", "SalesTerritoryRegion",
                     "Total Sales Amount", INET, t)); t += 1

# Internet Sales Amount trend by Calendar Year
p1.append(make_chart(CHART_X_R, CHART_Y, CHART_W_R, CHART_H,
                     "lineChart",
                     "DimDate", "dd", "CalendarYear",
                     "Internet Sales Amount", INET, t)); t += 1

page1 = make_page("ExecutiveDashboard", "Executive Dashboard", ordinal=0, containers=p1)


# =============================================================================
# PAGE 2 — Customer Intelligence
# Who are our customers and where?
# KPIs: Unique Customers | Internet Order Count | Internet Sales Amount | Internet Gross Profit Margin
# Charts: Internet Sales by Country | Internet Sales by Customer Occupation
# =============================================================================

p2 = []
p2.append(make_textbox(16, 10, 900, TITLE_H,
                       "Customer Intelligence", t)); t += 1

p2.append(make_card(card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Unique Customers", INET, t)); t += 1
p2.append(make_card(card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Internet Order Count", INET, t)); t += 1
p2.append(make_card(card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Internet Sales Amount", INET, t)); t += 1
p2.append(make_card(card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Internet Gross Profit Margin", INET, t)); t += 1

# Internet Sales Amount by Country/Region
p2.append(make_chart(16, CHART_Y, CHART_W_L, CHART_H,
                     "barChart",
                     "DimGeography", "geo", "EnglishCountryRegionName",
                     "Internet Sales Amount", INET, t)); t += 1

# Internet Sales Amount by Customer Occupation
p2.append(make_chart(CHART_X_R, CHART_Y, CHART_W_R, CHART_H,
                     "columnChart",
                     "DimCustomer", "cust", "EnglishOccupation",
                     "Internet Sales Amount", INET, t)); t += 1

page2 = make_page("CustomerIntelligence", "Customer Intelligence", ordinal=1, containers=p2)


# =============================================================================
# PAGE 3 — Internet Sales Performance
# How are internet sales performing?
# KPIs: Internet Sales Amount | Internet Gross Profit | Internet Gross Profit Margin | Internet Order Count
# Charts: Internet Sales Amount by Year | Internet Sales by Product Category
# =============================================================================

p3 = []
p3.append(make_textbox(16, 10, 900, TITLE_H,
                       "Internet Sales Performance", t)); t += 1

p3.append(make_card(card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Internet Sales Amount", INET, t)); t += 1
p3.append(make_card(card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Internet Gross Profit", INET, t)); t += 1
p3.append(make_card(card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Internet Gross Profit Margin", INET, t)); t += 1
p3.append(make_card(card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Internet Order Count", INET, t)); t += 1

# Internet Sales Amount trend by Calendar Year
p3.append(make_chart(16, CHART_Y, CHART_W_L, CHART_H,
                     "lineChart",
                     "DimDate", "dd2", "CalendarYear",
                     "Internet Sales Amount", INET, t)); t += 1

# Internet Sales Amount by Product Category
p3.append(make_chart(CHART_X_R, CHART_Y, CHART_W_R, CHART_H,
                     "columnChart",
                     "DimProductCategory", "pc", "EnglishProductCategoryName",
                     "Internet Sales Amount", INET, t)); t += 1

page3 = make_page("InternetSales", "Internet Sales", ordinal=2, containers=p3)


# =============================================================================
# PAGE 4 — Reseller & Channel Performance
# How are reseller channels performing?
# KPIs: Reseller Sales Amount | Reseller Gross Profit | Reseller GP Margin | Reseller Order Count
# Charts: Reseller Sales by Territory | Reseller Sales by Business Type
# =============================================================================

p4 = []
p4.append(make_textbox(16, 10, 900, TITLE_H,
                       "Reseller & Channel Performance", t)); t += 1

p4.append(make_card(card_xs[0], CARD_Y, CARD_W, CARD_H,
                    "Reseller Sales Amount", RESL, t)); t += 1
p4.append(make_card(card_xs[1], CARD_Y, CARD_W, CARD_H,
                    "Reseller Gross Profit", RESL, t)); t += 1
p4.append(make_card(card_xs[2], CARD_Y, CARD_W, CARD_H,
                    "Reseller Gross Profit Margin", RESL, t)); t += 1
p4.append(make_card(card_xs[3], CARD_Y, CARD_W, CARD_H,
                    "Reseller Order Count", RESL, t)); t += 1

# Reseller Sales by Sales Territory Region
p4.append(make_chart(16, CHART_Y, CHART_W_L, CHART_H,
                     "columnChart",
                     "DimSalesTerritory", "st3", "SalesTerritoryRegion",
                     "Reseller Sales Amount", RESL, t)); t += 1

# Reseller Sales by Business Type
p4.append(make_chart(CHART_X_R, CHART_Y, CHART_W_R, CHART_H,
                     "barChart",
                     "DimReseller", "rs", "BusinessType",
                     "Reseller Sales Amount", RESL, t)); t += 1

page4 = make_page("ResellerChannel", "Reseller & Channel", ordinal=3, containers=p4)


# =============================================================================
# PAGE 5 — Product Intelligence
# Which products are driving revenue?
# KPIs: Internet Sales Amount | Reseller Sales Amount
# Charts: Internet Sales by Product Category | Internet Sales by Product Sub-category
# =============================================================================

p5 = []
p5.append(make_textbox(16, 10, 900, TITLE_H,
                       "Product Intelligence", t)); t += 1

# Wide KPI cards (2 only — centred)
WIDE_CARD_W = 600
p5.append(make_card(16,        CARD_Y, WIDE_CARD_W, CARD_H,
                    "Internet Sales Amount", INET, t)); t += 1
p5.append(make_card(CANVAS_W - WIDE_CARD_W - 16, CARD_Y, WIDE_CARD_W, CARD_H,
                    "Reseller Sales Amount", RESL, t)); t += 1

# Internet Sales by Product Category
p5.append(make_chart(16, CHART_Y, CHART_W_L, CHART_H,
                     "barChart",
                     "DimProductCategory", "pc2", "EnglishProductCategoryName",
                     "Internet Sales Amount", INET, t)); t += 1

# Internet Sales by Product Sub-category
p5.append(make_chart(CHART_X_R, CHART_Y, CHART_W_R, CHART_H,
                     "barChart",
                     "DimProductSubcategory", "psc", "EnglishProductSubcategoryName",
                     "Internet Sales Amount", INET, t)); t += 1

page5 = make_page("ProductIntelligence", "Product Intelligence", ordinal=4, containers=p5)


# =============================================================================
# WRITE PBIX
# =============================================================================

NEW_SECTIONS = [page1, page2, page3, page4, page5]


def build_pbix(pbix_in: str, pbix_out: str, sections: list) -> None:
    """
    Read source PBIX, replace all report sections, write to new path.
    - Report/Layout written as UTF-16-LE (no BOM).
    - SecurityBindings zeroed to prevent 'corrupted file' error.
    - Source file is never overwritten.
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
                data = b""                       # must zero — DPAPI hash is now stale
            elif item.filename == "Report/Layout":
                data = new_layout_bytes
            dst.writestr(item, data)

    page_names = [s["displayName"] for s in sections]
    print(f"[OK] Written: {pbix_out}")
    print(f"     Pages  : {', '.join(page_names)}")
    print(f"     Visuals: {sum(len(s['visualContainers']) for s in sections)} total")


if __name__ == "__main__":
    build_pbix(PBIX_IN, PBIX_OUT, NEW_SECTIONS)
