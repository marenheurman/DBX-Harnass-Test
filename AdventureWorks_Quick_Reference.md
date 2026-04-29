# Adventure Works Model — Quick Reference Card

**Print or bookmark this page for quick lookup while building the model.**

---

## Fact Tables at a Glance

| Fact Table | Grain | Approx. Rows | Primary Date |
|---|---|---|---|
| **FactInternetSales** | One per order line (Internet channel) | 60K | OrderDateKey |
| **FactResellerSales** | One per order line (Reseller channel) | 60K | OrderDateKey |
| **FactProductInventory** | One per product per date | 10K | DateKey |

---

## Dimension Tables at a Glance

| Dimension | Grain | Approx. Rows | Key Column | Notes |
|---|---|---|---|---|
| **DimDate** | One per calendar day | 3,600 | DateKey | MARKED AS DATE TABLE |
| **DimCustomer** | One per customer | 18K | CustomerKey | Links to DimGeography |
| **DimProduct** | One per product | 600 | ProductKey | Links to DimProductSubcategory |
| **DimProductSubcategory** | One per subcategory | 37 | ProductSubcategoryKey | Links to DimProductCategory |
| **DimProductCategory** | One per category | 4 | ProductCategoryKey | Top of hierarchy |
| **DimReseller** | One per reseller | 600 | ResellerKey | Links to DimGeography |
| **DimGeography** | One per location | 650 | GeographyKey | Links to DimSalesTerritory |
| **DimSalesTerritory** | One per sales region | 10 | SalesTerritoryKey | Regional grouping |
| **DimEmployee** | One per employee | 300 | EmployeeKey | Links to DimSalesTerritory, DimDepartmentGroup |
| **DimDepartmentGroup** | One per department | 12 | DepartmentGroupKey | Org grouping |
| **DimPromotion** | One per promotion | 16 | PromotionKey | Campaign/offer |
| **DimCurrency** | One per currency | 105 | CurrencyKey | Multi-currency support |
| **DimSalesReason** | One per reason type | 10 | SalesReasonKey | Why purchase? (via bridge) |

---

## Bridge Table

| Bridge Table | M:M Resolution | Notes |
|---|---|---|
| **FactInternetSalesReason** | FactInternetSales ↔ DimSalesReason | Multiple reasons per transaction |

---

## Relationships Checklist

### From FactInternetSales (✓ = Create)

- [ ] OrderDateKey → DimDate.DateKey (ACTIVE)
- [ ] DueDateKey → DimDate.DateKey (INACTIVE)
- [ ] ShipDateKey → DimDate.DateKey (INACTIVE)
- [ ] CustomerKey → DimCustomer.CustomerKey (ACTIVE)
- [ ] ProductKey → DimProduct.ProductKey (ACTIVE)
- [ ] PromotionKey → DimPromotion.PromotionKey (ACTIVE)
- [ ] CurrencyKey → DimCurrency.CurrencyKey (ACTIVE)
- [ ] (via bridge) → DimSalesReason (ACTIVE)

### From FactResellerSales

- [ ] OrderDateKey → DimDate.DateKey (ACTIVE)
- [ ] DueDateKey → DimDate.DateKey (INACTIVE)
- [ ] ShipDateKey → DimDate.DateKey (INACTIVE)
- [ ] ResellerKey → DimReseller.ResellerKey (ACTIVE)
- [ ] EmployeeKey → DimEmployee.EmployeeKey (ACTIVE)
- [ ] ProductKey → DimProduct.ProductKey (ACTIVE)
- [ ] PromotionKey → DimPromotion.PromotionKey (ACTIVE)
- [ ] CurrencyKey → DimCurrency.CurrencyKey (ACTIVE)

### From Dimensions

- [ ] DimCustomer.GeographyKey → DimGeography.GeographyKey (ACTIVE)
- [ ] DimReseller.GeographyKey → DimGeography.GeographyKey (ACTIVE)
- [ ] DimGeography.SalesTerritoryKey → DimSalesTerritory.SalesTerritoryKey (ACTIVE)
- [ ] DimEmployee.SalesTerritoryKey → DimSalesTerritory.SalesTerritoryKey (ACTIVE)
- [ ] DimEmployee.DepartmentGroupKey → DimDepartmentGroup.DepartmentGroupKey (ACTIVE)
- [ ] DimProduct.ProductSubcategoryKey → DimProductSubcategory.ProductSubcategoryKey (ACTIVE)
- [ ] DimProductSubcategory.ProductCategoryKey → DimProductCategory.ProductCategoryKey (ACTIVE)

### Bridge Relationships

- [ ] FactInternetSalesReason.SalesOrderKey → FactInternetSales.SalesOrderKey (ACTIVE)
- [ ] FactInternetSalesReason.SalesReasonKey → DimSalesReason.SalesReasonKey (ACTIVE)

---

## Key Columns to Hide (Right-Click → Hide in Report View)

All dimensions:
- [ ] `*Key` columns (all surrogate keys)
- [ ] `*AlternateKey` columns (except when used as natural key display)

All facts:
- [ ] `SalesOrderLineNumber` (technical)

---

## Measures to Create (in _Measures table)

### Core Sales
- [ ] `Total Sales Amount` = SUM both fact tables
- [ ] `Internet Sales Amount` = SUM Internet only
- [ ] `Reseller Sales Amount` = SUM Reseller only
- [ ] `Total Quantity` = SUM quantities
- [ ] `Average Order Value` = Total Sales / Order Count

### Time Intelligence
- [ ] `Sales YTD` = Use DATESYTD
- [ ] `Sales PY` = Use SAMEPERIODLASTYEAR
- [ ] `Sales YoY` = (Current - PY) / PY

### Counts
- [ ] `Distinct Customers` = DISTINCTCOUNT
- [ ] `Distinct Products` = DISTINCTCOUNT
- [ ] `Order Count` = COUNTA

---

## Common Filtering Patterns

### Customer Analysis
- Slicer: DimCustomer[FirstName], [LastName], [Education], [Occupation]
- Visualize: [Total Sales Amount] by DimCustomer attributes

### Product Analysis
- Slicer: DimProductCategory[Name], then drill to DimProductSubcategory[Name], then DimProduct[Name]
- Visualize: [Total Sales Amount] by Product

### Channel Comparison
- Matrix: Rows = DimProduct, Values = [Internet Sales Amount], [Reseller Sales Amount]
- Shows product performance by channel

### Geographic Analysis
- Map or visual: DimGeography[City], DimSalesTerritory[Region]
- Filter: DimGeography[Country]
- Values: [Total Sales Amount]

### Time Trend
- Line chart: DimDate[CalendarYear] and [MonthNumberOfYear] on X-axis
- Values: [Sales YTD] or [Total Sales Amount]
- Use USERELATIONSHIP for alternate dates if needed

---

## Field List Organization

After setup, your field list should look like:

```
📊 _Measures (75 measures)
├── [Total Sales Amount]
├── [Internet Sales Amount]
├── [Reseller Sales Amount]
├── ... (other measures)

📁 DimDate (hidden fields except display columns)
├── FullDateAlternateKey
├── CalendarYear
├── MonthNumberOfYear
├── ... (other time attributes)

📁 DimCustomer
├── FirstName
├── LastName
├── EmailAddress
├── ... (other customer attributes)

📁 DimProduct
├── EnglishProductName
├── Color
├── ListPrice
├── ... (other product attributes)

📁 DimGeography
├── City
├── StateProvinceName
├── EnglishCountryRegionName
├── ... (other geographic attributes)

📁 DimSalesTerritory
├── SalesTerritoryRegion
├── SalesTerritoryCountry
├── ... (other territory attributes)

📁 DimPromotion
├── EnglishPromotionName
├── DiscountPct
├── ... (other promotion attributes)

📁 DimReseller
├── ResellerName
├── Business Type
├── ... (other reseller attributes)

📁 DimEmployee
├── FirstName
├── LastName
├── Title
├── ... (other employee attributes)

📁 FactInternetSales
├── SalesAmount
├── OrderQuantity
├── UnitPrice

📁 FactResellerSales
├── SalesAmount
├── OrderQuantity
├── UnitPrice
```

---

## SQL Connection String (for reference)

```
Data Source=localhost\[INSTANCE];Initial Catalog=AdventureWorksDW2022;Integrated Security=true;
```

Replace `[INSTANCE]` with your SQL instance name (e.g., `SQLEXPRESS` or `MSSQL2022`).

---

## Model Stats Target

- **Total tables:** 17 (14 dimensions + 2 facts + 1 bridge)
- **Total relationships:** 22
- **Date table:** DimDate (marked)
- **Inactive relationships:** 6 (DueDateKey and ShipDateKey × 3 fact tables)
- **Many-to-Many:** 1 (via bridge)
- **Total measures:** ~75 (after DAX phase)

---

## Validation Checklist

Before considering the model complete:

- [ ] All 22 relationships created and verified
- [ ] DimDate marked as Date table
- [ ] No ambiguous filter paths (no red X in Model view)
- [ ] All `*Key` columns hidden
- [ ] Core measures created and working
- [ ] Test visual shows correct totals
- [ ] Model exported to PBIP format
- [ ] No errors in Model tab

---

## Quick Test Queries (in DAX)

Copy-paste these into Power BI's "New Measure" to verify connectivity:

```dax
-- Test 1: Total sales from Internet
Internet Test = SUMX(FactInternetSales, FactInternetSales[SalesAmount])

-- Test 2: Total sales from Reseller
Reseller Test = SUMX(FactResellerSales, FactResellerSales[SalesAmount])

-- Test 3: Count of customers
Customer Test = COUNTA(FactInternetSales[CustomerKey])

-- Test 4: Check date range
Min Date = MIN(DimDate[FullDateAlternateKey])
Max Date = MAX(DimDate[FullDateAlternateKey])
```

If these return values, your model is connected and working! 🎉

---

**End of Quick Reference**
