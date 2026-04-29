# Implementation Guide — Building the Adventure Works Power BI Model

**Purpose:** Step-by-step instructions for implementing the model design in Power BI Desktop.

**Estimated Time:** 3-4 hours

---

## Prerequisites

- [ ] Power BI Desktop (latest version)
- [ ] AdventureWorksDW2022 database restored in SQL Server
- [ ] Network connectivity to SQL Server
- [ ] SQL Server credentials (Windows Auth or SQL Auth)
- [ ] The model design document (`AdventureWorks_Model_Design.md`)

---

## Phase 1: Data Source Connection

### Step 1.1: Create New Power BI Project

1. Open **Power BI Desktop**
2. Click **File** → **New**
3. Save the project as `AdventureWorks_Model.pbix`
4. Close the splash screen

### Step 1.2: Connect to SQL Server

1. Click **Get Data** (Home ribbon)
2. Select **SQL Server**
3. Enter connection details:
   - **Server:** `localhost` or `[YOUR-MACHINE-NAME]\[INSTANCE]`
   - **Database:** `AdventureWorksDW2022`
   - **Data Connectivity mode:** Keep default (Import)
4. Click **OK**
5. Select **Windows authentication** or **Database** (enter SQL credentials)
6. Click **Connect**

### Step 1.3: Select Tables to Import

The navigator window will show all tables. **Import in this order:**

#### Step 1: Import Dimension Tables First

Select these tables (hold Ctrl to multi-select):
```
dbo.DimDate
dbo.DimCurrency
dbo.DimProductCategory
dbo.DimProductSubcategory
dbo.DimProduct
dbo.DimGeography
dbo.DimSalesTerritory
dbo.DimCustomer
dbo.DimReseller
dbo.DimEmployee
dbo.DimDepartmentGroup
dbo.DimPromotion
dbo.DimSalesReason
```

Click **Load** (loads all at once).

#### Step 2: Import Fact and Bridge Tables

After dimensions load, click **Get Data** → **SQL Server** again.

Select these tables:
```
dbo.FactInternetSales
dbo.FactResellerSales
dbo.FactInternetSalesReason
dbo.FactProductInventory (optional)
```

Click **Load**.

**Why this order?** Dimensions should load first so Power BI can attempt auto-detection of relationships.

---

## Phase 2: Data Cleansing (In Power Query)

### Step 2.1: Clean DimDate

1. Right-click `DimDate` table in Data pane → **Edit Query**
2. Power Query Editor opens
3. Verify columns: You should see `DateKey`, `FullDateAlternateKey`, `DayNumberOfWeek`, etc.
4. Delete unnecessary columns:
   - Click column header → **Remove** (if any columns are not in the model design)
5. Rename columns for clarity (if needed):
   - Right-click column → **Rename**
   - Follow naming convention: `[CategoryName][Attribute]` (e.g., `CalendarYear`, `IsWeekend`)
6. Ensure data types:
   - `DateKey` = Whole Number
   - `FullDateAlternateKey` = Date
   - `CalendarYear`, `MonthNumberOfYear`, etc. = Whole Number
   - `EnglishDayNameOfWeek`, etc. = Text
7. Click **Close & Apply**

### Step 2.2: Clean Other Dimensions

Repeat similar steps for:
- `DimCustomer` — Ensure text fields are Text, dates are Date
- `DimProduct` — Verify numeric fields (ListPrice, StandardCost) are Decimal
- `DimGeography` — Check for any null values in required fields
- `DimReseller` — Ensure numeric fields are correct type
- `DimEmployee` — Verify date fields

**Quick Data Type Check:**
- All keys (`*Key`) = Whole Number
- All dates (`*Date`) = Date
- Numeric amounts (`Amount`, `Price`, `Cost`) = Decimal or Fixed Decimal
- Descriptive text = Text
- Flags (`Flag`) = Text (values: Y, N)

### Step 2.3: Clean Fact Tables

For `FactInternetSales`:
1. Edit Query
2. Verify columns match the design:
   - `SalesOrderKey`, `SalesOrderLineNumber` (keys)
   - `OrderDateKey`, `DueDateKey`, `ShipDateKey` (date foreign keys)
   - `CustomerKey`, `ProductKey`, `PromotionKey`, `CurrencyKey` (dimension keys)
   - `SalesAmount`, `TaxAmt`, `Freight`, `ExtendedAmount` (Decimal)
   - `OrderQuantity` (Whole Number)
3. Set correct data types
4. Check for NULL values in key columns (should be none)
5. Close & Apply

Repeat for `FactResellerSales` and `FactInternetSalesReason`.

---

## Phase 3: Relationships

### Step 3.1: Review Auto-Detected Relationships

1. In Power BI Desktop, go to **Model** tab (bottom of screen)
2. View the relationship diagram
3. Power BI should have auto-detected relationships from foreign keys
4. Verify auto-detected relationships against your design

### Step 3.2: Manually Create Missing Relationships

If any relationships are missing, manually create them:

1. **From FactInternetSales:**
   - Drag `OrderDateKey` from FactInternetSales → Drop on `DateKey` in DimDate
   - (Relationship created)

**Create these relationships by dragging:**

| From Table | From Column | To Table | To Column | Cardinality | Direction | Active |
|---|---|---|---|---|---|---|
| FactInternetSales | OrderDateKey | DimDate | DateKey | Many to One | Single | YES |
| FactInternetSales | DueDateKey | DimDate | DateKey | Many to One | Single | NO |
| FactInternetSales | ShipDateKey | DimDate | DateKey | Many to One | Single | NO |
| FactInternetSales | CustomerKey | DimCustomer | CustomerKey | Many to One | Single | YES |
| FactInternetSales | ProductKey | DimProduct | ProductKey | Many to One | Single | YES |
| FactInternetSales | PromotionKey | DimPromotion | PromotionKey | Many to One | Single | YES |
| FactInternetSales | CurrencyKey | DimCurrency | CurrencyKey | Many to One | Single | YES |
| FactResellerSales | OrderDateKey | DimDate | DateKey | Many to One | Single | YES |
| FactResellerSales | DueDateKey | DimDate | DateKey | Many to One | Single | NO |
| FactResellerSales | ShipDateKey | DimDate | DateKey | Many to One | Single | NO |
| FactResellerSales | ResellerKey | DimReseller | ResellerKey | Many to One | Single | YES |
| FactResellerSales | EmployeeKey | DimEmployee | EmployeeKey | Many to One | Single | YES |
| FactResellerSales | ProductKey | DimProduct | ProductKey | Many to One | Single | YES |
| FactResellerSales | PromotionKey | DimPromotion | PromotionKey | Many to One | Single | YES |
| FactResellerSales | CurrencyKey | DimCurrency | CurrencyKey | Many to One | Single | YES |
| DimCustomer | GeographyKey | DimGeography | GeographyKey | Many to One | Single | YES |
| DimReseller | GeographyKey | DimGeography | GeographyKey | Many to One | Single | YES |
| DimGeography | SalesTerritoryKey | DimSalesTerritory | SalesTerritoryKey | Many to One | Single | YES |
| DimEmployee | SalesTerritoryKey | DimSalesTerritory | SalesTerritoryKey | Many to One | Single | YES |
| DimEmployee | DepartmentGroupKey | DimDepartmentGroup | DepartmentGroupKey | Many to One | Single | YES |
| DimProduct | ProductSubcategoryKey | DimProductSubcategory | ProductSubcategoryKey | Many to One | Single | YES |
| DimProductSubcategory | ProductCategoryKey | DimProductCategory | ProductCategoryKey | Many to One | Single | YES |

**Bridge Table Relationships (Many-to-Many):**
| From Table | From Column | To Table | To Column | Cardinality |
|---|---|---|---|---|
| FactInternetSalesReason | SalesOrderKey | FactInternetSales | SalesOrderKey | Many to Many |
| FactInternetSalesReason | SalesReasonKey | DimSalesReason | SalesReasonKey | Many to One |

### Step 3.3: Set Relationship Properties

For each relationship, check:

1. **Right-click relationship line** → **Edit relationship**
2. Verify:
   - **Cardinality:** Many-to-One (or Many-to-Many for bridges)
   - **Cross filter direction:** Single (not bidirectional)
   - **Make this relationship active:** 
     - YES for primary date, customer, product relationships
     - NO for DueDateKey, ShipDateKey, alternate date paths
3. Click **OK**

### Step 3.4: Validate Relationships

1. Go to **Model** tab
2. Look for the relationship diagram
3. Verify:
   - All lines connect correctly
   - No relationship lines cross unnecessarily (cosmetic)
   - Inactive relationships show as dotted lines
   - No "circular" relationships (if present, review design)

**Check: Ambiguous Filter Paths**

Look for tables connected by TWO or more relationship paths:
- Example: If FactInternetSales connects to DimDate via both OrderDateKey AND DueDateKey (both active), that's ambiguous
- Fix: Make one INACTIVE (which we did)

---

## Phase 4: Mark Date Table

1. Go to **Data** tab (left pane)
2. Right-click `DimDate` table → **Mark as date table**
3. In dialog:
   - **Date column:** Select `FullDateAlternateKey`
   - Click **OK**
4. The DimDate table now shows a calendar icon in the Data pane

---

## Phase 5: Create Measures Table

A dedicated table for measures improves organization and performance.

### Step 5.1: Create _Measures Table

1. Go to **Data** tab
2. **New Table** → Paste this formula:

```dax
_Measures = 
ROW(
    "Placeholder", 1
)
```

3. Press **Enter**
4. Rename the table to `_Measures` (it will auto-generate as a calculated table)

### Step 5.2: Hide the Placeholder Column

1. Right-click the `Placeholder` column → **Hide in Report View**
2. (This column won't appear in the field list)

### Step 5.3: Add Base Measures

1. Click `_Measures` table in Data pane
2. Click **New Measure** (Measure ribbon button, or right-click table → **New measure**)

**Add these core measures:**

```dax
-- Sales Metrics
Total Sales Amount = SUMX(FactInternetSales, FactInternetSales[SalesAmount]) + SUMX(FactResellerSales, FactResellerSales[SalesAmount])

Internet Sales Amount = SUMX(FactInternetSales, FactInternetSales[SalesAmount])

Reseller Sales Amount = SUMX(FactResellerSales, FactResellerSales[SalesAmount])

Total Quantity = SUMX(FactInternetSales, FactInternetSales[OrderQuantity]) + SUMX(FactResellerSales, FactResellerSales[OrderQuantity])

Total Tax = SUMX(FactInternetSales, FactInternetSales[TaxAmt]) + SUMX(FactResellerSales, FactResellerSales[TaxAmt])

Total Freight = SUMX(FactInternetSales, FactInternetSales[Freight]) + SUMX(FactResellerSales, FactResellerSales[Freight])

-- Profitability (assuming ExtendedAmount = Sales - Discounts)
Total Extended Amount = SUMX(FactInternetSales, FactInternetSales[ExtendedAmount]) + SUMX(FactResellerSales, FactResellerSales[ExtendedAmount])

Gross Profit = SUMX(FactInternetSales, FactInternetSales[ExtendedAmount]) + SUMX(FactResellerSales, FactResellerSales[ExtendedAmount])

Net Sales = [Total Sales Amount] - [Total Tax] - [Total Freight]

-- Counts
Distinct Customers = DISTINCTCOUNT(FactInternetSales[CustomerKey])

Distinct Products = DISTINCTCOUNT(FactInternetSales[ProductKey])

Order Count = COUNTA(FactInternetSales[SalesOrderKey]) + COUNTA(FactResellerSales[SalesOrderKey])

-- Averages
Average Order Value = DIVIDE([Total Sales Amount], [Order Count])

-- YTD Measures (using USERELATIONSHIP for inactive OrderDateKey)
Sales YTD = CALCULATE(
    [Total Sales Amount],
    DATESYTD(DimDate[FullDateAlternateKey])
)

-- Prior Year Comparison
Sales PY = CALCULATE(
    [Total Sales Amount],
    SAMEPERIODLASTYEAR(DimDate[FullDateAlternateKey])
)

-- YoY Growth
Sales YoY = DIVIDE(
    [Total Sales Amount] - [Sales PY],
    [Sales PY],
    0
)
```

3. After each formula, press **Enter** to save it
4. Each measure now appears in the `_Measures` table in the field list

---

## Phase 6: Hide Dimension Keys and Technical Columns

Users should not see surrogate keys in report filters.

1. **Data** tab → Select each dimension table
2. For each table, right-click the key column:
   - Example: In DimCustomer, right-click `CustomerKey`
   - → **Hide in Report View**
3. Hide all `*Key` columns (they're used internally only)
4. Hide these columns too:
   - `FactInternetSalesReason[SalesOrderLineNumber]` (technical)
   - Any `AlternateKey` columns (natural keys used for traceability only)

---

## Phase 7: Set Column Formatting

Improves report visuals automatically.

1. **Data** tab → Select dimension table
2. For each numeric column (that should show currency):
   - Click column header
   - In properties (right side), set:
     - **Format:** Currency ($ English)
     - **Decimal places:** 2
   - Example: DimPromotion[DiscountPct] → Set format to Percentage (0 decimal places)

3. For fact tables:
   - All `*Amount` columns → **Currency**
   - All `*Pct` columns → **Percentage**
   - All `*Quantity` columns → **Whole Number**
   - All date columns → **Date (format: M/d/yyyy or your regional standard)**

---

## Phase 8: Validate the Model

### Check 1: Run a Simple Query

1. **Report** tab (bottom)
2. Create a test visual:
   - Click **Card** visual
   - Drag `[Total Sales Amount]` from `_Measures` into the visual
   - You should see a sales total (e.g., $61.5M for full Adventure Works data)

### Check 2: Test Relationships

1. Create a **Matrix** visual:
   - Rows: Product Name (from DimProduct)
   - Values: Total Sales Amount
   - Filter by a specific geography (add filter from DimGeography)
   - Result: Should show products sold in that geography only
   - If results are wrong, you have a relationship issue

### Check 3: Test Inactive Date Relationships

1. Create a **Card** for shipped date sales:
   - New measure: 
   ```dax
   Sales by Ship Date = CALCULATE(
       [Total Sales Amount],
       USERELATIONSHIP(FactInternetSales[ShipDateKey], DimDate[DateKey])
   )
   ```
   - Add this measure to a visual
   - Filter by DimDate[Month/Year]
   - Should show correct values based on ship date, not order date

### Check 4: Review Relationships Diagram

1. **Model** tab
2. Verify all lines are present and correct
3. If any red X appears: **Relationship error** — resolve it

---

## Phase 9: Export to PBIP (Source Control Ready)

Once model is validated:

1. **File** → **Save As**
2. Choose location: `c:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\`
3. File name: `AdventureWorks_Semantic_Model`
4. **Save as type:** Power BI Project (*.SemanticModel)
5. Click **Save**

This converts the `.pbix` to a folder-based project structure:
```
AdventureWorks_Semantic_Model.SemanticModel/
├── .gitignore
├── definition/
│   ├── model.bim  (semantic model definition)
│   ├── tables/
│   │   ├── DimDate.tmdl
│   │   ├── DimCustomer.tmdl
│   │   ├── FactInternetSales.tmdl
│   │   └── ... (all tables)
│   └── relationships.tmdl
└── [Report files if included]
```

Now you can commit this to Git for version control.

---

## Phase 10: Run Model Review (Using Harness)

If you have the MCP Power BI server running:

1. Load the `.claude/skills/semantic-model-review/SKILL.md` from your harness
2. Ask the AI agent to review the model
3. The agent will:
   - Validate relationships
   - Check for ambiguous filters
   - Verify star schema compliance
   - Flag any issues
4. Address any Critical findings before publishing

---

## Troubleshooting

### Issue: "Table not found" error
**Cause:** Table name mismatch in relationship creation  
**Fix:** Verify table name is exactly `dbo.DimDate`, not `DimDate`

### Issue: Blank visuals in reports
**Cause:** Relationship cardinality mismatch or missing relationship  
**Fix:** Check Model tab; ensure all relationships are Many-to-One (except bridges)

### Issue: "Ambiguous relationship" warning
**Cause:** Two active relationships between same tables  
**Fix:** Set one to Inactive (right-click relationship → Edit → Toggle "Make this relationship active")

### Issue: YTD measures show no data
**Cause:** DimDate not marked as Date table, or DateKey format wrong  
**Fix:** 
1. Go to Model → Mark DimDate as Date Table
2. Ensure DateKey is formatted as YYYYMMDD (integer) or FullDateAlternateKey is Date type

### Issue: Relationship not appearing
**Cause:** Data types don't match (e.g., one is Int, other is BigInt)  
**Fix:** Edit Query for affected table; set both keys to same type (Whole Number)

---

## Performance Optimization (Optional)

If model gets large (>1GB):

1. **Use Direct Query for fact tables** (instead of Import)
   - This requires additional SQL Server setup
   - Only data requested flows over network

2. **Create aggregations** for common groupings
   - Example: Monthly sales totals pre-aggregated

3. **Hide unused columns** to reduce memory footprint

---

## Next Steps

1. ✅ Complete all phases above
2. ✅ Validate model with test visuals
3. ✅ Run semantic-model-review using harness skills
4. ✅ Publish to Power BI Service or Fabric workspace
5. ✅ Create reports using the model

---

**End of Implementation Guide**

For questions on model design, refer to `AdventureWorks_Model_Design.md`.  
For Power BI governance standards, see `rules/modeling-rules.md` in the harness.
