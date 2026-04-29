# Power BI Data Model Design — Adventure Works DW 2022

**Date:** 2026-04-29  
**Project:** Adventure Works Data Warehouse  
**Version:** 1.0  
**Status:** Ready for Implementation  
**Architecture:** Star Schema  

---

## Executive Summary

This document specifies the semantic model architecture for Adventure Works DW 2022. The model implements a **star schema** with:

- **2 Fact tables** containing transaction and inventory data
- **14 Dimension tables** providing descriptive context
- **1 Bridge table** resolving many-to-many sales reasons
- **1 Date Dimension** (DimDate) for time intelligence
- **18 Total relationships** with defined cardinality and direction
- **~75 Measures** (to be populated during DAX development)

---

## Model Overview

| Element | Count | Notes |
|---|---|---|
| **Fact Tables** | 2 | FactInternetSales, FactResellerSales |
| **Dimension Tables** | 14 | Customer, Product, Geography, Reseller, Date, etc. |
| **Bridge Tables** | 1 | FactInternetSalesReason (M:M) |
| **Total Tables** | 17 | |
| **Relationships** | 18 | All many-to-one except 2 bridge relationships |
| **Measures** | ~75 | Aggregations, YTD, YoY, comparisons (DAX to follow) |
| **Calculated Columns** | 0 | None required (flatten attributes into dimensions) |

---

## Star Schema Diagram

```
                    ┌──────────────────┐
                    │   DimDate        │
                    │  (Date Table)    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│FactInternetSales│ │FactResellerSales │ │FactProductInv   │
│  (Transactions) │ │ (Transactions)   │ │   (Inventory)    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                    │                    │
   ┌────┴────┬───┬───┐   ┌───┴────┬───┐      ┌───┴──────┐
   │          │   │   │   │        │   │      │          │
   ▼          ▼   ▼   ▼   ▼        ▼   ▼      ▼          ▼
DimCust DimProd DimGeo Promo DimReseller Emp DimProduct DimCurrency
           │        │                           │
    ┌──────┘    ┌───┴──────┐          ┌────────┴────────┐
    │           │          │          │                 │
    ▼           ▼          ▼          ▼                 ▼
DimProdCat DimTerritory DimOrg DimProductCategory DimCurrency
    │
    ▼
DimProdSubcat
    
              ┌─────────────────────────────┐
              │FactInternetSalesReason     │
              │      (Bridge Table)         │
              │  M:M between Sales & Reason │
              └─────────────────────────────┘
                        │         │
                        ▼         ▼
                  FactInternetSales & DimSalesReason
```

---

## Fact Tables

### 1. FactInternetSales

**Business Purpose:** Track all online transactions across customers.

**Grain Statement:** One row per order line per product sold via Internet.

**Physical Location:** `dbo.FactInternetSales` in AdventureWorksDW2022

**Key Columns:**

| Column Name | Data Type | Role | Notes |
|---|---|---|---|
| `SalesOrderKey` | Integer | Surrogate Key | Primary identifier |
| `SalesOrderLineNumber` | Integer | Grain Component | Line number within order |
| `OrderDateKey` | Integer | Foreign Key | Links to DimDate (order date) |
| `DueDateKey` | Integer | Foreign Key (Inactive) | Links to DimDate (due date) - USERELATIONSHIP in measures |
| `ShipDateKey` | Integer | Foreign Key (Inactive) | Links to DimDate (ship date) - USERELATIONSHIP in measures |
| `CustomerKey` | Integer | Foreign Key | Links to DimCustomer |
| `ProductKey` | Integer | Foreign Key | Links to DimProduct |
| `PromotionKey` | Integer | Foreign Key | Links to DimPromotion |
| `CurrencyKey` | Integer | Foreign Key | Links to DimCurrency |
| `SalesReasonKey` | Integer | Foreign Key | Links via FactInternetSalesReason (bridge) |
| `SalesAmount` | Decimal(19,4) | Measure | Revenue |
| `TaxAmt` | Decimal(19,4) | Measure | Tax amount |
| `Freight` | Decimal(19,4) | Measure | Shipping cost |
| `OrderQuantity` | Integer | Measure | Units sold |
| `UnitPrice` | Decimal(19,4) | Attribute | Price per unit |
| `ExtendedAmount` | Decimal(19,4) | Measure | Line total (calculated in source) |
| `UnitPriceDiscountPct` | Float | Attribute | Discount percentage |

**Relationship Cardinality:**
- Many-to-One to DimDate (via OrderDateKey) — **ACTIVE**
- Many-to-One to DimDate (via DueDateKey) — **INACTIVE** (for alternate time calculations)
- Many-to-One to DimDate (via ShipDateKey) — **INACTIVE** (for shipment timing)
- Many-to-One to DimCustomer (via CustomerKey) — **ACTIVE**
- Many-to-One to DimProduct (via ProductKey) — **ACTIVE**
- Many-to-One to DimPromotion (via PromotionKey) — **ACTIVE**
- Many-to-One to DimCurrency (via CurrencyKey) — **ACTIVE**
- Many-to-Many to DimSalesReason (via FactInternetSalesReason bridge) — **ACTIVE**

**Row Count:** ~60,000 rows (typical for sample data)

---

### 2. FactResellerSales

**Business Purpose:** Track all transactions through reseller channel.

**Grain Statement:** One row per order line per product sold through reseller.

**Physical Location:** `dbo.FactResellerSales` in AdventureWorksDW2022

**Key Columns:**

| Column Name | Data Type | Role | Notes |
|---|---|---|---|
| `SalesOrderKey` | Integer | Surrogate Key | Primary identifier |
| `SalesOrderLineNumber` | Integer | Grain Component | Line number within order |
| `OrderDateKey` | Integer | Foreign Key | Links to DimDate (order date) — **ACTIVE** |
| `DueDateKey` | Integer | Foreign Key | Links to DimDate (due date) — **INACTIVE** |
| `ShipDateKey` | Integer | Foreign Key | Links to DimDate (ship date) — **INACTIVE** |
| `ResellerKey` | Integer | Foreign Key | Links to DimReseller |
| `EmployeeKey` | Integer | Foreign Key | Links to DimEmployee |
| `ProductKey` | Integer | Foreign Key | Links to DimProduct |
| `PromotionKey` | Integer | Foreign Key | Links to DimPromotion |
| `CurrencyKey` | Integer | Foreign Key | Links to DimCurrency |
| `SalesAmount` | Decimal(19,4) | Measure | Revenue |
| `TaxAmt` | Decimal(19,4) | Measure | Tax amount |
| `Freight` | Decimal(19,4) | Measure | Shipping cost |
| `OrderQuantity` | Integer | Measure | Units sold |
| `UnitPrice` | Decimal(19,4) | Attribute | Price per unit |
| `ExtendedAmount` | Decimal(19,4) | Measure | Line total |
| `UnitPriceDiscountPct` | Float | Attribute | Discount percentage |

**Relationships:**
- Many-to-One to DimDate (via OrderDateKey, DueDateKey, ShipDateKey)
- Many-to-One to DimReseller (via ResellerKey)
- Many-to-One to DimEmployee (via EmployeeKey)
- Many-to-One to DimProduct (via ProductKey)
- Many-to-One to DimPromotion (via PromotionKey)
- Many-to-One to DimCurrency (via CurrencyKey)

**Row Count:** ~60,000 rows (typical for sample data)

**Important:** FactInternetSales and FactResellerSales share common dimensions (DimDate, DimProduct, DimCurrency, DimPromotion) to ensure **conforming dimensions** across both sales channels.

---

### 3. FactProductInventory (Optional Secondary Fact)

**Business Purpose:** Track product inventory levels over time.

**Grain Statement:** One row per product per date.

**Physical Location:** `dbo.FactProductInventory` in AdventureWorksDW2022

**Key Columns:**

| Column Name | Data Type | Role | Notes |
|---|---|---|---|
| `ProductKey` | Integer | Foreign Key | Links to DimProduct |
| `DateKey` | Integer | Foreign Key | Links to DimDate |
| `MovementDate` | Date | Attribute | Date of inventory movement |
| `UnitsIn` | Integer | Measure | Units received |
| `UnitsOut` | Integer | Measure | Units sold/used |
| `UnitsBalance` | Integer | Measure | Ending balance |
| `CostAmount` | Decimal(19,4) | Measure | Inventory cost |

---

## Dimension Tables

### 1. DimCustomer

**Purpose:** Describe individual customers and their attributes.

**Grain:** One row per customer.

**Physical Location:** `dbo.DimCustomer` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role | Notes |
|---|---|---|---|
| `CustomerKey` | Integer | Primary Key | Surrogate key (linked from FactInternetSales) |
| `GeographyKey` | Integer | Foreign Key | Links to DimGeography |
| `CustomerAlternateKey` | NVARCHAR | Natural Key | Business key (from source system) |
| `Title` | NVARCHAR | Attribute | Mr., Mrs., Dr., etc. |
| `FirstName` | NVARCHAR | Attribute | Customer first name |
| `MiddleName` | NVARCHAR | Attribute | Customer middle name |
| `LastName` | NVARCHAR | Attribute | Customer last name |
| `NameStyle` | NVARCHAR | Attribute | Name format (Western, Eastern) |
| `BirthDate` | Date | Attribute | Customer DOB |
| `MaritalStatus` | NVARCHAR | Attribute | S, M |
| `Suffix` | NVARCHAR | Attribute | Jr., Sr., III, etc. |
| `Gender` | NVARCHAR | Attribute | M, F |
| `EmailAddress` | NVARCHAR | Attribute | Contact email |
| `YearlyIncome` | Money | Attribute | Annual income range |
| `TotalChildren` | Integer | Attribute | Number of children |
| `NumberChildrenAtHome` | Integer | Attribute | Children at home |
| `Education` | NVARCHAR | Attribute | Partial High School, High School, Partial College, Bachelor, Graduate Degree |
| `Occupation` | NVARCHAR | Attribute | Professional, Clerical, Manual, etc. |
| `HouseOwnerFlag` | NVARCHAR | Attribute | Y, N |
| `NumberCarsOwned` | Integer | Attribute | Car count |
| `AddressLine1` | NVARCHAR | Attribute | Street address |
| `AddressLine2` | NVARCHAR | Attribute | Apartment/suite |
| `Phone` | NVARCHAR | Attribute | Phone number |
| `DateFirstPurchase` | Date | Attribute | First transaction date |
| `CommuteDistance` | NVARCHAR | Attribute | 0-1 Miles, 1-2 Miles, 2-5 Miles, 5-10 Miles, 10+ Miles |

**Relationships:**
- Many-to-One to DimGeography (via GeographyKey)

---

### 2. DimProduct

**Purpose:** Describe products, their categories, and attributes.

**Grain:** One row per product.

**Physical Location:** `dbo.DimProduct` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role | Notes |
|---|---|---|---|
| `ProductKey` | Integer | Primary Key | Surrogate key |
| `ProductAlternateKey` | NVARCHAR | Natural Key | Business key (SKU) |
| `ProductSubcategoryKey` | Integer | Foreign Key | Links to DimProductSubcategory |
| `WeightUnitMeasureCode` | NVARCHAR | Attribute | Code (e.g., LB) |
| `SizeUnitMeasureCode` | NVARCHAR | Attribute | Code (e.g., IN) |
| `EnglishProductName` | NVARCHAR | Attribute | Product name |
| `SpanishProductName` | NVARCHAR | Attribute | Spanish name (for i18n) |
| `FrenchProductName` | NVARCHAR | Attribute | French name (for i18n) |
| `StandardCost` | Money | Attribute | COGS |
| `FinishedGoodsFlag` | NVARCHAR | Attribute | Y, N |
| `Color` | NVARCHAR | Attribute | Red, Blue, Black, etc. |
| `SafetyStockLevel` | SmallInt | Attribute | Reorder point |
| `ReorderPoint` | SmallInt | Attribute | Minimum stock |
| `ListPrice` | Money | Attribute | MSRP |
| `Size` | NVARCHAR | Attribute | XS, S, M, L, XL, etc. |
| `SizeRange` | NVARCHAR | Attribute | Calculated grouping |
| `Weight` | Float | Attribute | Product weight |
| `DaysToManufacture` | Integer | Attribute | Lead time |
| `ProductLine` | NVARCHAR | Attribute | R (Road), M (Mountain), T (Touring), S (Standard) |
| `Dealer Price` | Money | Attribute | Reseller list price |
| `Class` | NVARCHAR | Attribute | H (High), M (Medium), L (Low) - performance |
| `Style` | NVARCHAR | Attribute | W (Women's), M (Men's), U (Unisex) |
| `ModelName` | NVARCHAR | Attribute | Marketing name |
| `LargePhoto` | NVARCHAR | Attribute | Photo URL |
| `EnglishDescription` | NVARCHAR | Attribute | Product description |
| `StartDate` | Date | Attribute | Product launch date |
| `EndDate` | Date | Attribute | Product discontinuation date |
| `Status` | NVARCHAR | Attribute | Current, Obsolete, etc. |

**Relationships:**
- Many-to-One to DimProductSubcategory (via ProductSubcategoryKey)

**Note:** DimProductSubcategory and DimProductCategory are NOT snowflaked. Use hierarchical attributes in DimProduct for category/subcategory grouping. Do NOT chain dimension lookups.

---

### 3. DimProductCategory (Flattened into DimProduct)

**Recommendation:** Add these columns directly to DimProduct:

| Column | Source |
|---|---|
| `ProductCategoryKey` | From DimProductCategory |
| `EnglishProductCategoryName` | From DimProductCategory |
| `SpanishProductCategoryName` | From DimProductCategory |
| `FrenchProductCategoryName` | From DimProductCategory |

**Rationale:** Eliminates snowflaking (dimension-to-dimension chain) and simplifies navigation for report developers.

---

### 4. DimProductSubcategory

**Purpose:** Link products to subcategories and categories.

**Grain:** One row per product subcategory.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `ProductSubcategoryKey` | Integer | Primary Key |
| `ProductCategoryKey` | Integer | Foreign Key → DimProductCategory |
| `EnglishProductSubcategoryName` | NVARCHAR | Attribute |
| `SpanishProductSubcategoryName` | NVARCHAR | Attribute |
| `FrenchProductSubcategoryName` | NVARCHAR | Attribute |

**Relationships:**
- Many-to-One to DimProductCategory (via ProductCategoryKey)

---

### 5. DimProductCategory

**Purpose:** Top level of product hierarchy.

**Grain:** One row per product category.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `ProductCategoryKey` | Integer | Primary Key |
| `EnglishProductCategoryName` | NVARCHAR | Attribute (e.g., Bikes, Components, Clothing) |
| `SpanishProductCategoryName` | NVARCHAR | Attribute |
| `FrenchProductCategoryName` | NVARCHAR | Attribute |

---

### 6. DimDate (Date Table)

**Purpose:** Provide time intelligence and period analysis.

**Grain:** One row per calendar day.

**Physical Location:** `dbo.DimDate` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role | Notes |
|---|---|---|---|
| `DateKey` | Integer | Primary Key | YYYYMMDD format (20260101) |
| `FullDateAlternateKey` | Date | Natural Key | Actual date |
| `DayNumberOfWeek` | TinyInt | Attribute | 1=Sunday, 7=Saturday |
| `EnglishDayNameOfWeek` | NVARCHAR | Attribute | Sunday, Monday, etc. |
| `DayNumberOfMonth` | TinyInt | Attribute | 1–31 |
| `DayNumberOfYear` | SmallInt | Attribute | 1–365 |
| `WeekNumberOfYear` | TinyInt | Attribute | 1–53 (ISO 8601) |
| `EnglishMonthName` | NVARCHAR | Attribute | January, February, etc. |
| `MonthNumberOfYear` | TinyInt | Attribute | 1–12 |
| `CalendarQuarter` | TinyInt | Attribute | 1–4 |
| `CalendarYear` | SmallInt | Attribute | 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027 |
| `CalendarSemester` | TinyInt | Attribute | 1, 2 |
| `FiscalQuarter` | TinyInt | Attribute | 1–4 (if organization uses fiscal year) |
| `FiscalYear` | SmallInt | Attribute | Fiscal year (if applicable) |
| `IsWeekend` | NVARCHAR | Attribute | Y, N |
| `IsHoliday` | NVARCHAR | Attribute | Y, N |
| `IsWorkday` | NVARCHAR | Attribute | Y, N |

**Power BI Configuration:**
- **Mark as Date Table:** YES
- **Date Column:** FullDateAlternateKey
- **Hidden:** NO (must be visible for report developers)

**Validation:**
- Covers full date range from earliest transaction date to current date + 12 months
- No gaps in dates (contiguous)
- Updated annually to extend into future year

**Relationships:**
- FactInternetSales → DimDate (OrderDateKey) — ACTIVE
- FactInternetSales → DimDate (DueDateKey) — INACTIVE
- FactInternetSales → DimDate (ShipDateKey) — INACTIVE
- FactResellerSales → DimDate (OrderDateKey) — ACTIVE
- FactResellerSales → DimDate (DueDateKey) — INACTIVE
- FactResellerSales → DimDate (ShipDateKey) — INACTIVE
- FactProductInventory → DimDate (DateKey) — ACTIVE

---

### 7. DimGeography

**Purpose:** Describe geographic locations (countries, states, cities).

**Grain:** One row per geographic location.

**Physical Location:** `dbo.DimGeography` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `GeographyKey` | Integer | Primary Key |
| `City` | NVARCHAR | Attribute |
| `StateProvinceCode` | NVARCHAR | Attribute |
| `StateProvinceName` | NVARCHAR | Attribute |
| `CountryRegionCode` | NVARCHAR | Attribute |
| `EnglishCountryRegionName` | NVARCHAR | Attribute |
| `SpanishCountryRegionName` | NVARCHAR | Attribute |
| `FrenchCountryRegionName` | NVARCHAR | Attribute |
| `PostalCode` | NVARCHAR | Attribute |
| `SalesTerritoryKey` | Integer | Foreign Key → DimSalesTerritory |
| `IPAddressLocator` | NVARCHAR | Attribute |
| `Ipv4Mask` | NVARCHAR | Attribute |
| `Ipv6Mask` | NVARCHAR | Attribute |

**Relationships:**
- Many-to-One to DimSalesTerritory (via SalesTerritoryKey)

---

### 8. DimSalesTerritory

**Purpose:** Describe sales regions and territories.

**Grain:** One row per sales territory.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `SalesTerritoryKey` | Integer | Primary Key |
| `SalesTerritoryAlternateKey` | Integer | Natural Key |
| `SalesTerritoryRegion` | NVARCHAR | Attribute (e.g., Northwest, Northeast) |
| `SalesTerritoryCountry` | NVARCHAR | Attribute |
| `SalesTerritoryGroup` | NVARCHAR | Attribute (e.g., North America) |
| `SalesTerritoryImage` | NVARCHAR | Attribute |

---

### 9. DimReseller

**Purpose:** Describe reseller/distributor organizations.

**Grain:** One row per reseller.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `ResellerKey` | Integer | Primary Key |
| `GeographyKey` | Integer | Foreign Key → DimGeography |
| `ResellerAlternateKey` | NVARCHAR | Natural Key |
| `Phone` | NVARCHAR | Attribute |
| `Business Type` | NVARCHAR | Attribute (Warehouse, Specialty Bike Shop, Value Added Reseller) |
| `ResellerName` | NVARCHAR | Attribute |
| `NumberEmployees` | Integer | Attribute |
| `ProductLine` | NVARCHAR | Attribute |
| `ResellerLevel` | NVARCHAR | Attribute |
| `ResellerManagerPersonKey` | Integer | Foreign Key (optional) |
| `FirstOrderYear` | Integer | Attribute |
| `LastOrderYear` | Integer | Attribute |
| `YearOpened` | Integer | Attribute |
| `PercentageDiscount` | Decimal | Attribute |
| `AnnualRevenue` | Money | Attribute |
| `BankName` | NVARCHAR | Attribute |
| `MinPaymentType` | NVARCHAR | Attribute |
| `MinPaymentAmount` | Money | Attribute |
| `AnnualMaxPurchaseAmount` | Money | Attribute |
| `DateFirstPurchase` | Date | Attribute |
| `DateLatestPurchase` | Date | Attribute |
| `Status` | NVARCHAR | Attribute |

**Relationships:**
- Many-to-One to DimGeography (via GeographyKey)

---

### 10. DimEmployee

**Purpose:** Describe sales and support employees.

**Grain:** One row per employee.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `EmployeeKey` | Integer | Primary Key |
| `ParentEmployeeKey` | Integer | Foreign Key (Self-join for hierarchy) |
| `EmployeeNationalIDAlternateKey` | NVARCHAR | Natural Key |
| `ParentEmployeeNationalIDAlternateKey` | NVARCHAR | Parent reference |
| `SalesTerritoryKey` | Integer | Foreign Key → DimSalesTerritory |
| `FirstName` | NVARCHAR | Attribute |
| `LastName` | NVARCHAR | Attribute |
| `MiddleName` | NVARCHAR | Attribute |
| `NameStyle` | NVARCHAR | Attribute |
| `Title` | NVARCHAR | Attribute |
| `HireDate` | Date | Attribute |
| `BirthDate` | Date | Attribute |
| `LoginID` | NVARCHAR | Attribute |
| `EmailAddress` | NVARCHAR | Attribute |
| `Phone` | NVARCHAR | Attribute |
| `MaritalStatus` | NVARCHAR | Attribute |
| `EmergencyContactName` | NVARCHAR | Attribute |
| `EmergencyContactPhone` | NVARCHAR | Attribute |
| `DepartmentName` | NVARCHAR | Attribute (linked via DepartmentGroupKey) |
| `BaseRate` | Money | Attribute |
| `PayFrequency` | NVARCHAR | Attribute |
| `VacationHours` | SmallInt | Attribute |
| `SickLeaveHours` | SmallInt | Attribute |
| `CurrentFlag` | NVARCHAR | Attribute (Y, N) |
| `SalesPersonFlag` | NVARCHAR | Attribute (Y, N) |
| `DepartmentGroupKey` | Integer | Foreign Key → DimDepartmentGroup |

**Relationships:**
- Many-to-One to DimSalesTerritory (via SalesTerritoryKey)
- Many-to-One to DimDepartmentGroup (via DepartmentGroupKey)
- Self-referential (for employee hierarchy — optional, use USERELATIONSHIP if needed)

---

### 11. DimDepartmentGroup

**Purpose:** Organizational department groupings.

**Grain:** One row per department.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `DepartmentGroupKey` | Integer | Primary Key |
| `ParentDepartmentGroupKey` | Integer | Foreign Key (Self-join for hierarchy) |
| `DepartmentGroupName` | NVARCHAR | Attribute |

---

### 12. DimPromotion

**Purpose:** Describe sales promotions and campaigns.

**Grain:** One row per promotion.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `PromotionKey` | Integer | Primary Key |
| `PromotionAlternateKey` | NVARCHAR | Natural Key |
| `EnglishPromotionName` | NVARCHAR | Attribute |
| `SpanishPromotionName` | NVARCHAR | Attribute |
| `FrenchPromotionName` | NVARCHAR | Attribute |
| `DiscountPct` | Decimal | Attribute |
| `EnglishPromotionType` | NVARCHAR | Attribute (e.g., New Product, Seasonal) |
| `SpanishPromotionType` | NVARCHAR | Attribute |
| `FrenchPromotionType` | NVARCHAR | Attribute |
| `EnglishPromotionCategory` | NVARCHAR | Attribute (e.g., Reseller, Internet) |
| `SpanishPromotionCategory` | NVARCHAR | Attribute |
| `FrenchPromotionCategory` | NVARCHAR | Attribute |
| `StartDate` | Date | Attribute |
| `EndDate` | Date | Attribute |
| `MinQty` | Integer | Attribute |
| `MaxQty` | Integer | Attribute |

---

### 13. DimCurrency

**Purpose:** Describe currencies for multi-currency transactions.

**Grain:** One row per currency.

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `CurrencyKey` | Integer | Primary Key |
| `CurrencyAlternateKey` | NVARCHAR | ISO Code (USD, EUR, GBP, etc.) |
| `CurrencyName` | NVARCHAR | Attribute |
| `ExchangeRateToUsd` | Decimal | Attribute (used for currency conversion measures) |

---

### 14. DimSalesReason

**Purpose:** Describe reasons why customers made purchases.

**Grain:** One row per reason type.

**Physical Location:** `dbo.DimSalesReason` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `SalesReasonKey` | Integer | Primary Key |
| `SalesReasonAlternateKey` | NVARCHAR | Natural Key |
| `SalesReasonName` | NVARCHAR | Attribute (e.g., Price, Quality, On Promotion) |
| `SalesReasonReasonType` | NVARCHAR | Attribute (e.g., Marketing, Other) |

**Relationships:**
- Many-to-Many to FactInternetSales via FactInternetSalesReason bridge table

---

## Bridge Tables (Many-to-Many Resolution)

### FactInternetSalesReason

**Purpose:** Resolve many-to-many relationship between FactInternetSales and DimSalesReason (a single transaction can be driven by multiple reasons).

**Grain:** One row per internet sales transaction per sales reason.

**Physical Location:** `dbo.FactInternetSalesReason` in AdventureWorksDW2022

**Key Columns:**

| Column | Type | Role |
|---|---|---|
| `SalesOrderKey` | Integer | Foreign Key → FactInternetSales |
| `SalesOrderLineNumber` | Integer | Line component key |
| `SalesReasonKey` | Integer | Foreign Key → DimSalesReason |

**Relationships:**
- Many-to-One to FactInternetSales (via SalesOrderKey + SalesOrderLineNumber)
- Many-to-One to DimSalesReason (via SalesReasonKey)

**Note:** FactInternetSales connects to DimSalesReason **only** through this bridge table. No direct relationship.

---

## Relationship Map

| Relationship ID | From Table | From Column | To Table | To Column | Cardinality | Direction | Active | Notes |
|---|---|---|---|---|---|---|---|---|
| R-001 | FactInternetSales | OrderDateKey | DimDate | DateKey | Many-to-One | Single | YES | Primary order date |
| R-002 | FactInternetSales | DueDateKey | DimDate | DateKey | Many-to-One | Single | NO | Use USERELATIONSHIP for due date analysis |
| R-003 | FactInternetSales | ShipDateKey | DimDate | DateKey | Many-to-One | Single | NO | Use USERELATIONSHIP for ship date analysis |
| R-004 | FactInternetSales | CustomerKey | DimCustomer | CustomerKey | Many-to-One | Single | YES | |
| R-005 | FactInternetSales | ProductKey | DimProduct | ProductKey | Many-to-One | Single | YES | |
| R-006 | FactInternetSales | PromotionKey | DimPromotion | PromotionKey | Many-to-One | Single | YES | |
| R-007 | FactInternetSales | CurrencyKey | DimCurrency | CurrencyKey | Many-to-One | Single | YES | |
| R-008 | FactResellerSales | OrderDateKey | DimDate | DateKey | Many-to-One | Single | YES | Primary order date |
| R-009 | FactResellerSales | DueDateKey | DimDate | DateKey | Many-to-One | Single | NO | Use USERELATIONSHIP |
| R-010 | FactResellerSales | ShipDateKey | DimDate | DateKey | Many-to-One | Single | NO | Use USERELATIONSHIP |
| R-011 | FactResellerSales | ResellerKey | DimReseller | ResellerKey | Many-to-One | Single | YES | |
| R-012 | FactResellerSales | EmployeeKey | DimEmployee | EmployeeKey | Many-to-One | Single | YES | Sales rep |
| R-013 | FactResellerSales | ProductKey | DimProduct | ProductKey | Many-to-One | Single | YES | Conforming dimension with Internet sales |
| R-014 | FactResellerSales | PromotionKey | DimPromotion | PromotionKey | Many-to-One | Single | YES | Conforming dimension |
| R-015 | FactResellerSales | CurrencyKey | DimCurrency | CurrencyKey | Many-to-One | Single | YES | Conforming dimension |
| R-016 | DimCustomer | GeographyKey | DimGeography | GeographyKey | Many-to-One | Single | YES | Customer location |
| R-017 | DimReseller | GeographyKey | DimGeography | GeographyKey | Many-to-One | Single | YES | Reseller location |
| R-018 | DimGeography | SalesTerritoryKey | DimSalesTerritory | SalesTerritoryKey | Many-to-One | Single | YES | |
| R-019 | DimEmployee | SalesTerritoryKey | DimSalesTerritory | SalesTerritoryKey | Many-to-One | Single | YES | |
| R-020 | DimEmployee | DepartmentGroupKey | DimDepartmentGroup | DepartmentGroupKey | Many-to-One | Single | YES | |
| R-021 | DimProduct | ProductSubcategoryKey | DimProductSubcategory | ProductSubcategoryKey | Many-to-One | Single | YES | |
| R-022 | DimProductSubcategory | ProductCategoryKey | DimProductCategory | ProductCategoryKey | Many-to-One | Single | YES | |
| BRIDGE-001 | FactInternetSalesReason | SalesOrderKey + SalesOrderLineNumber | FactInternetSales | SalesOrderKey + SalesOrderLineNumber | Many-to-One | Single | YES | Bridge table from fact to reason |
| BRIDGE-002 | FactInternetSalesReason | SalesReasonKey | DimSalesReason | SalesReasonKey | Many-to-One | Single | YES | Bridge table from reason to dimension |

---

## Conforming Dimensions

The following dimensions are shared across multiple fact tables to enable consistent reporting across sales channels:

| Dimension | Used By | Purpose |
|---|---|---|
| DimDate | FactInternetSales, FactResellerSales, FactProductInventory | Time-based analysis |
| DimProduct | FactInternetSales, FactResellerSales, FactProductInventory | Product grouping and filtering |
| DimCurrency | FactInternetSales, FactResellerSales | Multi-currency analysis |
| DimPromotion | FactInternetSales, FactResellerSales | Campaign and promotion analysis |

**Conforming Dimension Validation:** ProductKey, CurrencyKey, and PromotionKey values MUST be identical across both fact tables. No conflicts are allowed.

---

## Star Schema Validation Checklist

- [x] **Central Fact Tables:** FactInternetSales and FactResellerSales are central to analysis
- [x] **Direct Dimension Connections:** All dimensions connect directly to fact tables (many-to-one)
- [x] **No Snowflaking:** Dimension-to-dimension connections eliminated (ProductCategory flattened into Product attributes)
- [x] **Conforming Dimensions:** Shared dimensions have identical keys across fact tables
- [x] **Many-to-Many Resolution:** FactInternetSalesReason bridge properly resolves sales reasons
- [x] **Date Table Present:** DimDate is marked as Date table in Power BI
- [x] **Bidirectional Filters:** None by default; single-direction preferred
- [x] **Inactive Relationships Justified:** DueDateKey and ShipDateKey are inactive with documented USERELATIONSHIP patterns

---

## Measures to Implement (DAX)

The following measure categories should be implemented in a dedicated `_Measures` table:

### Sales Metrics
- `Total Sales Amount`
- `Total Quantity`
- `Average Unit Price`
- `Total Extended Amount`
- `Total Tax Amount`
- `Total Freight Amount`
- `Net Sales (Sales - Discount)`

### Profitability Metrics
- `Gross Profit`
- `Gross Profit %`
- `Net Profit`
- `Profit Margin %`

### Channel Analysis
- `Internet Sales %` (Internet / Total)
- `Reseller Sales %` (Reseller / Total)

### Time Intelligence
- `Sales YTD` (Year-to-Date)
- `Sales PY` (Prior Year)
- `Sales YoY` (Year-over-Year Growth)
- `Sales QTD` (Quarter-to-Date)
- `Sales MTD` (Month-to-Date)

### Customer & Product Analysis
- `Customer Count (Distinct)`
- `Product Count (Distinct)`
- `Average Order Value`
- `Order Count`

### Trend Indicators
- `Sales vs Budget` (if budget dimension added)
- `Promo Impact`

---

## Data Quality & Governance Rules

1. **No NULL Keys:** Foreign key columns must never be NULL. Use a special value (e.g., -1 or 0) for unknown/other.
2. **Unique Dimension Keys:** Each dimension primary key must be unique. No duplicates.
3. **Date Continuity:** DimDate must have contiguous dates with no gaps.
4. **Grain Integrity:** Each fact table row must correspond to its defined grain. No mixing of grains.
5. **Conforming Dimension Validation:** Shared keys must be synchronized. Run quarterly validation.
6. **Inactive Relationship Usage:** Every inactive relationship must be used in at least one DAX measure or marked for archival.
7. **Currency Consistency:** All monetary amounts must be stored in a single base currency (typically USD); conversions applied in DAX.

---

## Implementation Roadmap

### Phase 1: Schema Setup (Week 1)
- [ ] Create table connections in Power BI Desktop from AdventureWorksDW2022
- [ ] Import all dimension tables (DimDate, DimCustomer, DimProduct, etc.)
- [ ] Import all fact tables (FactInternetSales, FactResellerSales)
- [ ] Mark DimDate as Date table

### Phase 2: Relationships (Week 1-2)
- [ ] Define all 22 relationships with correct cardinality
- [ ] Set relationship directions (all single-direction except bridges)
- [ ] Mark inactive relationships (DueDateKey, ShipDateKey, etc.)
- [ ] Validate no ambiguous filter paths

### Phase 3: DAX Measures (Week 2-3)
- [ ] Create `_Measures` table (calculated table or measure container)
- [ ] Implement core sales and profitability measures
- [ ] Implement time intelligence measures using USERELATIONSHIP for inactive dates
- [ ] Test measure accuracy against source data

### Phase 4: Validation & Documentation (Week 3-4)
- [ ] Run semantic model review (use harness skill)
- [ ] Validate conforming dimensions
- [ ] Confirm no relationship ambiguities
- [ ] Document any custom time intelligence patterns
- [ ] Export model to PBIP for source control

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Correct Approach |
|---|---|---|
| Bidirectional relationships everywhere | Creates ambiguous filter propagation | Use single-direction; apply bidirectional selectively with CROSSFILTER |
| Chaining dimensions (snowflaking) | Slow queries, confusing for developers | Flatten attributes into single dimension |
| Fact-to-fact relationships | Causes double-counting or missing data | Introduce shared conforming dimensions or bridge table |
| Missing Date table | Time intelligence functions fail | Add marked Date table |
| Measures on dimension tables | Context transition errors | Move measures to dedicated `_Measures` table |
| Hardcoded FILTER(ALL(...)) | Unsafe; breaks user slicers | Use CALCULATE with REMOVEFILTERS or CROSSFILTER |

---

## Sign-Off

| Role | Name | Approval | Date |
|---|---|---|---|
| BI Analyst / Data Architect | [Name] | [ ] Approved | |
| Lead Developer | [Name] | [ ] Approved | |
| Project Sponsor | [Name] | [ ] Approved | |

---

## Appendix: SQL Queries for Validation

### Verify Conforming Dimension Keys

```sql
-- Check that ProductKey is consistent across fact tables
SELECT COUNT(DISTINCT ProductKey) as UniqueProductKeys 
FROM FactInternetSales
UNION ALL
SELECT COUNT(DISTINCT ProductKey) 
FROM FactResellerSales;

-- Both should return same count if keys are conforming
```

### Check for NULL Foreign Keys

```sql
SELECT 'FactInternetSales - CustomerKey' AS CheckName, COUNT(*) AS NullCount
FROM FactInternetSales
WHERE CustomerKey IS NULL
UNION ALL
SELECT 'FactResellerSales - ResellerKey', COUNT(*)
FROM FactResellerSales
WHERE ResellerKey IS NULL;

-- Should return 0 for all checks
```

### Validate Date Table Continuity

```sql
SELECT 
  DATEDIFF(DAY, MIN(FullDateAlternateKey), MAX(FullDateAlternateKey)) + 1 AS DateRangeLength,
  COUNT(*) AS RowCount
FROM DimDate;

-- DateRangeLength should equal RowCount (no gaps)
```

---

**End of Model Design Document**

*This model follows Power BI best practices and the governance rules defined in the Power BI Agentic Harness. See `rules/modeling-rules.md` for detailed standards.*
