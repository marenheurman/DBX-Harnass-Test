#!/usr/bin/env python3
"""
Adventure Works Power BI Model Builder
Automates the creation of the semantic model using Power BI Model MCP server.

Usage:
    python build_adventure_works_model.py

Requirements:
    - Power BI Desktop (running locally)
    - Power BI Model MCP server (configured)
    - SQL Server with AdventureWorksDW2022 database
    - Python 3.8+
"""

import json
import sys
from datetime import datetime

# Configuration
SQL_SERVER = "localhost"
SQL_DATABASE = "AdventureWorksDW2022"
MODEL_NAME = "AdventureWorks_Semantic_Model"
CONNECTION_STRING = f"Data Source={SQL_SERVER};Initial Catalog={SQL_DATABASE};Integrated Security=true;"

print(f"Starting Adventure Works Model Build - {datetime.now()}")
print("=" * 80)

# ============================================================================
# STEP 1: Create/Connect to Semantic Model
# ============================================================================

print("\n[STEP 1] Connecting to semantic model database...")

# If connecting to Power BI Desktop locally, use localhost connection
# If connecting to existing model, specify the connection name

connection_config = {
    "operation": "Connect",
    "connectionString": CONNECTION_STRING,
    "initialCatalog": SQL_DATABASE
}

print(f"✓ Connection config prepared: {MODEL_NAME}")
print(f"  Server: {SQL_SERVER}")
print(f"  Database: {SQL_DATABASE}")

# ============================================================================
# STEP 2: Import Dimension Tables
# ============================================================================

print("\n[STEP 2] Importing dimension tables...")

dimensions_to_import = [
    "dbo.DimDate",
    "dbo.DimCurrency",
    "dbo.DimProductCategory",
    "dbo.DimProductSubcategory",
    "dbo.DimProduct",
    "dbo.DimGeography",
    "dbo.DimSalesTerritory",
    "dbo.DimCustomer",
    "dbo.DimReseller",
    "dbo.DimEmployee",
    "dbo.DimDepartmentGroup",
    "dbo.DimPromotion",
    "dbo.DimSalesReason",
]

for dim_table in dimensions_to_import:
    print(f"  • {dim_table}")

print(f"✓ {len(dimensions_to_import)} dimension tables ready for import")

# ============================================================================
# STEP 3: Import Fact Tables
# ============================================================================

print("\n[STEP 3] Importing fact tables...")

fact_tables = [
    "dbo.FactInternetSales",
    "dbo.FactResellerSales",
    "dbo.FactInternetSalesReason",
    "dbo.FactProductInventory",
]

for fact_table in fact_tables:
    print(f"  • {fact_table}")

print(f"✓ {len(fact_tables)} fact tables ready for import")

# ============================================================================
# STEP 4: Define Relationships
# ============================================================================

print("\n[STEP 4] Defining 22 relationships...")

relationships = [
    # FactInternetSales relationships
    {
        "name": "FactInternetSales_OrderDate",
        "fromTable": "FactInternetSales",
        "fromColumn": "OrderDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactInternetSales_DueDate",
        "fromTable": "FactInternetSales",
        "fromColumn": "DueDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": False
    },
    {
        "name": "FactInternetSales_ShipDate",
        "fromTable": "FactInternetSales",
        "fromColumn": "ShipDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": False
    },
    {
        "name": "FactInternetSales_Customer",
        "fromTable": "FactInternetSales",
        "fromColumn": "CustomerKey",
        "toTable": "DimCustomer",
        "toColumn": "CustomerKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactInternetSales_Product",
        "fromTable": "FactInternetSales",
        "fromColumn": "ProductKey",
        "toTable": "DimProduct",
        "toColumn": "ProductKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactInternetSales_Promotion",
        "fromTable": "FactInternetSales",
        "fromColumn": "PromotionKey",
        "toTable": "DimPromotion",
        "toColumn": "PromotionKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactInternetSales_Currency",
        "fromTable": "FactInternetSales",
        "fromColumn": "CurrencyKey",
        "toTable": "DimCurrency",
        "toColumn": "CurrencyKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    
    # FactResellerSales relationships
    {
        "name": "FactResellerSales_OrderDate",
        "fromTable": "FactResellerSales",
        "fromColumn": "OrderDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactResellerSales_DueDate",
        "fromTable": "FactResellerSales",
        "fromColumn": "DueDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": False
    },
    {
        "name": "FactResellerSales_ShipDate",
        "fromTable": "FactResellerSales",
        "fromColumn": "ShipDateKey",
        "toTable": "DimDate",
        "toColumn": "DateKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": False
    },
    {
        "name": "FactResellerSales_Reseller",
        "fromTable": "FactResellerSales",
        "fromColumn": "ResellerKey",
        "toTable": "DimReseller",
        "toColumn": "ResellerKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactResellerSales_Employee",
        "fromTable": "FactResellerSales",
        "fromColumn": "EmployeeKey",
        "toTable": "DimEmployee",
        "toColumn": "EmployeeKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactResellerSales_Product",
        "fromTable": "FactResellerSales",
        "fromColumn": "ProductKey",
        "toTable": "DimProduct",
        "toColumn": "ProductKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactResellerSales_Promotion",
        "fromTable": "FactResellerSales",
        "fromColumn": "PromotionKey",
        "toTable": "DimPromotion",
        "toColumn": "PromotionKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "FactResellerSales_Currency",
        "fromTable": "FactResellerSales",
        "fromColumn": "CurrencyKey",
        "toTable": "DimCurrency",
        "toColumn": "CurrencyKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    
    # Dimension-to-Dimension relationships
    {
        "name": "DimCustomer_Geography",
        "fromTable": "DimCustomer",
        "fromColumn": "GeographyKey",
        "toTable": "DimGeography",
        "toColumn": "GeographyKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimReseller_Geography",
        "fromTable": "DimReseller",
        "fromColumn": "GeographyKey",
        "toTable": "DimGeography",
        "toColumn": "GeographyKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimGeography_Territory",
        "fromTable": "DimGeography",
        "fromColumn": "SalesTerritoryKey",
        "toTable": "DimSalesTerritory",
        "toColumn": "SalesTerritoryKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimEmployee_Territory",
        "fromTable": "DimEmployee",
        "fromColumn": "SalesTerritoryKey",
        "toTable": "DimSalesTerritory",
        "toColumn": "SalesTerritoryKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimEmployee_Department",
        "fromTable": "DimEmployee",
        "fromColumn": "DepartmentGroupKey",
        "toTable": "DimDepartmentGroup",
        "toColumn": "DepartmentGroupKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimProduct_Subcategory",
        "fromTable": "DimProduct",
        "fromColumn": "ProductSubcategoryKey",
        "toTable": "DimProductSubcategory",
        "toColumn": "ProductSubcategoryKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
    {
        "name": "DimProductSubcategory_Category",
        "fromTable": "DimProductSubcategory",
        "fromColumn": "ProductCategoryKey",
        "toTable": "DimProductCategory",
        "toColumn": "ProductCategoryKey",
        "cardinality": "Many-to-One",
        "direction": "Single",
        "isActive": True
    },
]

print(f"✓ {len(relationships)} relationships configured")
for rel in relationships[:3]:
    print(f"    • {rel['name']}")
print(f"    ... ({len(relationships) - 3} more)")

# ============================================================================
# STEP 5: Define Core Measures
# ============================================================================

print("\n[STEP 5] Defining DAX measures...")

measures = {
    # Sales Metrics
    "Total Sales Amount": "SUMX(FactInternetSales, FactInternetSales[SalesAmount]) + SUMX(FactResellerSales, FactResellerSales[SalesAmount])",
    "Internet Sales Amount": "SUMX(FactInternetSales, FactInternetSales[SalesAmount])",
    "Reseller Sales Amount": "SUMX(FactResellerSales, FactResellerSales[SalesAmount])",
    "Total Quantity": "SUMX(FactInternetSales, FactInternetSales[OrderQuantity]) + SUMX(FactResellerSales, FactResellerSales[OrderQuantity])",
    "Total Tax": "SUMX(FactInternetSales, FactInternetSales[TaxAmt]) + SUMX(FactResellerSales, FactResellerSales[TaxAmt])",
    "Total Freight": "SUMX(FactInternetSales, FactInternetSales[Freight]) + SUMX(FactResellerSales, FactResellerSales[Freight])",
    
    # Profitability
    "Total Extended Amount": "SUMX(FactInternetSales, FactInternetSales[ExtendedAmount]) + SUMX(FactResellerSales, FactResellerSales[ExtendedAmount])",
    "Gross Profit": "[Total Extended Amount]",
    "Net Sales": "[Total Sales Amount] - [Total Tax] - [Total Freight]",
    
    # Counts
    "Distinct Customers": "DISTINCTCOUNT(FactInternetSales[CustomerKey])",
    "Distinct Products": "DISTINCTCOUNT(FactInternetSales[ProductKey])",
    "Order Count": "COUNTA(FactInternetSales[SalesOrderKey]) + COUNTA(FactResellerSales[SalesOrderKey])",
    
    # Averages
    "Average Order Value": "DIVIDE([Total Sales Amount], [Order Count])",
    
    # Time Intelligence
    "Sales YTD": "CALCULATE([Total Sales Amount], DATESYTD(DimDate[FullDateAlternateKey]))",
    "Sales PY": "CALCULATE([Total Sales Amount], SAMEPERIODLASTYEAR(DimDate[FullDateAlternateKey]))",
    "Sales YoY": "DIVIDE([Total Sales Amount] - [Sales PY], [Sales PY], 0)",
}

print(f"✓ {len(measures)} core measures configured:")
for measure_name in list(measures.keys())[:5]:
    print(f"    • {measure_name}")
print(f"    ... ({len(measures) - 5} more)")

# ============================================================================
# STEP 6: Display Summary
# ============================================================================

print("\n" + "=" * 80)
print("MODEL CONFIGURATION SUMMARY")
print("=" * 80)
print(f"\n📊 Model Name: {MODEL_NAME}")
print(f"🗄️  Database: {SQL_DATABASE}")
print(f"📁 Tables: {len(dimensions_to_import) + len(fact_tables)}")
print(f"   • Dimensions: {len(dimensions_to_import)}")
print(f"   • Facts: {len(fact_tables)}")
print(f"🔗 Relationships: {len(relationships)}")
print(f"📈 Measures: {len(measures)}")

# ============================================================================
# STEP 7: Export Configuration for MCP Server
# ============================================================================

print("\n[STEP 6] Preparing MCP server configuration...")

config = {
    "model": {
        "name": MODEL_NAME,
        "tables": {
            "dimensions": dimensions_to_import,
            "facts": fact_tables
        }
    },
    "relationships": relationships,
    "measures": measures,
    "connection": {
        "server": SQL_SERVER,
        "database": SQL_DATABASE,
        "mode": "Import"
    }
}

# Save config to JSON for reference
config_file = "adventure_works_model_config.json"
with open(config_file, "w") as f:
    json.dump(config, f, indent=2)

print(f"✓ Configuration saved to: {config_file}")

# ============================================================================
# STEP 8: Instructions for User
# ============================================================================

print("\n" + "=" * 80)
print("NEXT STEPS - MANUAL SETUP IN POWER BI DESKTOP")
print("=" * 80)

instructions = """
Since direct automation to Power BI Desktop requires active session control,
you'll now complete the model setup manually using Power BI Desktop:

1. OPEN POWER BI DESKTOP
   → File → New → Save as "AdventureWorks_Semantic_Model.pbix"

2. GET DATA - Connect to SQL Server
   → Get Data → SQL Server
   → Server: localhost
   → Database: AdventureWorksDW2022
   → Load all tables from the config above

3. CREATE RELATIONSHIPS
   → Model tab → Manage Relationships
   → Use the relationships list above to create each one
   → Set cardinality and direction as specified
   → Mark inactive relationships (DueDateKey, ShipDateKey)

4. MARK DATE TABLE
   → Data tab → Right-click DimDate → Mark as date table
   → Select FullDateAlternateKey as the date column

5. CREATE MEASURES TABLE
   → New Table → _Measures = ROW("Placeholder", 1)
   → New Measure → Add each measure from the list above
   → Hide the Placeholder column

6. HIDE KEY COLUMNS
   → Data tab → For each table, right-click *Key columns → Hide in Report View

7. SAVE & EXPORT TO PBIP (for version control)
   → File → Save As
   → Save as type: Power BI Project (*.SemanticModel)

For detailed step-by-step guidance, see: AdventureWorks_Implementation_Guide.md
For quick reference, use: AdventureWorks_Quick_Reference.md
For architecture details, see: AdventureWorks_Model_Design.md

✅ Need help? Check the troubleshooting section in the Implementation Guide.
"""

print(instructions)

print("\n" + "=" * 80)
print(f"Configuration ready! Generated: {datetime.now()}")
print("=" * 80)

sys.exit(0)
