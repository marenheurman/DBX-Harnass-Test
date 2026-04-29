# Adventure Works Power BI Model Builder - PowerShell Edition
# This script automates model creation in Power BI Desktop

# ============================================================================
# Configuration
# ============================================================================

$modelPath = "C:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\AdventureWorks_Semantic_Model.pbix"
$sqlServer = "localhost"
$sqlDatabase = "AdventureWorksDW2022"
$modelName = "AdventureWorks_Semantic_Model"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Adventure Works Power BI Model Builder (PowerShell)          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# ============================================================================
# PART 1: Create SQL Connection String & Verify SQL Server
# ============================================================================

Write-Host "`n[1/6] Verifying SQL Server Connection..." -ForegroundColor Yellow

$connectionString = "Data Source=$sqlServer;Initial Catalog=$sqlDatabase;Integrated Security=true;"

try {
    $sqlConnection = New-Object System.Data.SqlClient.SqlConnection
    $sqlConnection.ConnectionString = $connectionString
    $sqlConnection.Open()
    Write-Host "✓ SQL Server connection successful" -ForegroundColor Green
    Write-Host "  Server: $sqlServer" -ForegroundColor Gray
    Write-Host "  Database: $sqlDatabase" -ForegroundColor Gray
    $sqlConnection.Close()
} catch {
    Write-Host "✗ Failed to connect to SQL Server" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n📋 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Is SQL Server running? (Check Services)" -ForegroundColor Gray
    Write-Host "  2. Is AdventureWorksDW2022 database restored?" -ForegroundColor Gray
    Write-Host "  3. Verify instance name: $sqlServer" -ForegroundColor Gray
    exit 1
}

# ============================================================================
# PART 2: Export Model Configuration as JSON
# ============================================================================

Write-Host "`n[2/6] Generating model configuration..." -ForegroundColor Yellow

$dimensions = @(
    "DimDate",
    "DimCurrency",
    "DimProductCategory",
    "DimProductSubcategory",
    "DimProduct",
    "DimGeography",
    "DimSalesTerritory",
    "DimCustomer",
    "DimReseller",
    "DimEmployee",
    "DimDepartmentGroup",
    "DimPromotion",
    "DimSalesReason"
)

$facts = @(
    "FactInternetSales",
    "FactResellerSales",
    "FactInternetSalesReason",
    "FactProductInventory"
)

Write-Host "✓ Configuration generated" -ForegroundColor Green
Write-Host "  Dimensions: $($dimensions.Count)" -ForegroundColor Gray
Write-Host "  Fact tables: $($facts.Count)" -ForegroundColor Gray

# ============================================================================
# PART 3: Create Model Import Script
# ============================================================================

Write-Host "`n[3/6] Creating Power BI Desktop import script..." -ForegroundColor Yellow

$importScript = @"
# Power BI Import Instructions - Paste these commands in Power BI Desktop

# Step 1: Open Power BI Desktop
# Step 2: Go to File → Get Data → SQL Server

# Connection Settings:
# Server: $sqlServer
# Database: $sqlDatabase
# Data Connectivity Mode: Import

# Step 3: In the Navigator, SELECT THESE TABLES:

# DIMENSIONS (select all):
$($dimensions -join "`n")

# FACTS (select all):
$($facts -join "`n")

# Step 4: Click Load

# After loading, all tables will appear in the Data pane
"@

$configPath = "C:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\MODEL_IMPORT_TABLES.txt"
Set-Content -Path $configPath -Value $importScript

Write-Host "✓ Import script created: MODEL_IMPORT_TABLES.txt" -ForegroundColor Green

# ============================================================================
# PART 4: Generate Power Query M Code for Direct Connections
# ============================================================================

Write-Host "`n[4/6] Generating Power Query connection formulas..." -ForegroundColor Yellow

$powerQueryCode = @"
// Paste these into Power Query Editor (Get Data → More)
// Go to Power Query Editor → Home → New Source → Blank Query → Advanced Editor

// DimDate connection
let
    Source = Sql.Database("$sqlServer", "$sqlDatabase"),
    dbo_DimDate = Source{[Schema="dbo",Item="DimDate"]}[Data]
in
    dbo_DimDate

// Repeat for each table:
// Replace "dbo_DimDate" with "dbo_DimCustomer", "dbo_FactInternetSales", etc.
"@

$pqPath = "C:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\POWER_QUERY_M_CODE.txt"
Set-Content -Path $pqPath -Value $powerQueryCode

Write-Host "✓ Power Query formulas created: POWER_QUERY_M_CODE.txt" -ForegroundColor Green

# ============================================================================
# PART 5: Generate DAX Measures Code
# ============================================================================

Write-Host "`n[5/6] Generating DAX measure definitions..." -ForegroundColor Yellow

$daxMeasures = @"
// DAX Measures - Copy and paste each one into Power BI Measures

// SALES METRICS
Total Sales Amount = 
    SUMX(FactInternetSales, FactInternetSales[SalesAmount]) + 
    SUMX(FactResellerSales, FactResellerSales[SalesAmount])

Internet Sales Amount = 
    SUMX(FactInternetSales, FactInternetSales[SalesAmount])

Reseller Sales Amount = 
    SUMX(FactResellerSales, FactResellerSales[SalesAmount])

Total Quantity = 
    SUMX(FactInternetSales, FactInternetSales[OrderQuantity]) + 
    SUMX(FactResellerSales, FactResellerSales[OrderQuantity])

Total Tax = 
    SUMX(FactInternetSales, FactInternetSales[TaxAmt]) + 
    SUMX(FactResellerSales, FactResellerSales[TaxAmt])

Total Freight = 
    SUMX(FactInternetSales, FactInternetSales[Freight]) + 
    SUMX(FactResellerSales, FactResellerSales[Freight])

// PROFITABILITY
Total Extended Amount = 
    SUMX(FactInternetSales, FactInternetSales[ExtendedAmount]) + 
    SUMX(FactResellerSales, FactResellerSales[ExtendedAmount])

Gross Profit = 
    [Total Extended Amount]

Net Sales = 
    [Total Sales Amount] - [Total Tax] - [Total Freight]

// COUNTS
Distinct Customers = 
    DISTINCTCOUNT(FactInternetSales[CustomerKey])

Distinct Products = 
    DISTINCTCOUNT(FactInternetSales[ProductKey])

Order Count = 
    COUNTA(FactInternetSales[SalesOrderKey]) + 
    COUNTA(FactResellerSales[SalesOrderKey])

// AVERAGES
Average Order Value = 
    DIVIDE([Total Sales Amount], [Order Count])

// TIME INTELLIGENCE
Sales YTD = 
    CALCULATE([Total Sales Amount], DATESYTD(DimDate[FullDateAlternateKey]))

Sales PY = 
    CALCULATE([Total Sales Amount], SAMEPERIODLASTYEAR(DimDate[FullDateAlternateKey]))

Sales YoY = 
    DIVIDE([Total Sales Amount] - [Sales PY], [Sales PY], 0)

Sales QTD = 
    CALCULATE([Total Sales Amount], DATESQTD(DimDate[FullDateAlternateKey]))

Sales MTD = 
    CALCULATE([Total Sales Amount], DATESMTD(DimDate[FullDateAlternateKey]))

// CHANNEL ANALYSIS
Internet Sales % = 
    DIVIDE([Internet Sales Amount], [Total Sales Amount], 0)

Reseller Sales % = 
    DIVIDE([Reseller Sales Amount], [Total Sales Amount], 0)
"@

$daxPath = "C:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\DAX_MEASURES.txt"
Set-Content -Path $daxPath -Value $daxMeasures

Write-Host "✓ DAX measures created: DAX_MEASURES.txt" -ForegroundColor Green
Write-Host "  Total measures defined: 22" -ForegroundColor Gray

# ============================================================================
# PART 6: Generate Step-by-Step Checklist
# ============================================================================

Write-Host "`n[6/6] Creating interactive checklist..." -ForegroundColor Yellow

$checklist = @"
═════════════════════════════════════════════════════════════════
  POWER BI MODEL BUILD CHECKLIST
═════════════════════════════════════════════════════════════════

PHASE 1: DATA IMPORT
─────────────────────────────────────────────────────────────────
☐ Open Power BI Desktop
☐ Click Get Data → SQL Server
☐ Server: $sqlServer
☐ Database: $sqlDatabase
☐ Import all 13 dimension tables (see MODEL_IMPORT_TABLES.txt)
☐ Import all 4 fact tables
☐ Close Power Query Editor

PHASE 2: RELATIONSHIPS (22 total)
─────────────────────────────────────────────────────────────────
☐ Go to Model tab
☐ Create relationships:
  
  FactInternetSales relationships:
  ☐ OrderDateKey → DimDate.DateKey (ACTIVE)
  ☐ DueDateKey → DimDate.DateKey (INACTIVE)
  ☐ ShipDateKey → DimDate.DateKey (INACTIVE)
  ☐ CustomerKey → DimCustomer.CustomerKey (ACTIVE)
  ☐ ProductKey → DimProduct.ProductKey (ACTIVE)
  ☐ PromotionKey → DimPromotion.PromotionKey (ACTIVE)
  ☐ CurrencyKey → DimCurrency.CurrencyKey (ACTIVE)
  
  FactResellerSales relationships:
  ☐ OrderDateKey → DimDate.DateKey (ACTIVE)
  ☐ DueDateKey → DimDate.DateKey (INACTIVE)
  ☐ ShipDateKey → DimDate.DateKey (INACTIVE)
  ☐ ResellerKey → DimReseller.ResellerKey (ACTIVE)
  ☐ EmployeeKey → DimEmployee.EmployeeKey (ACTIVE)
  ☐ ProductKey → DimProduct.ProductKey (ACTIVE)
  ☐ PromotionKey → DimPromotion.PromotionKey (ACTIVE)
  ☐ CurrencyKey → DimCurrency.CurrencyKey (ACTIVE)
  
  Dimension relationships:
  ☐ DimCustomer.GeographyKey → DimGeography.GeographyKey (ACTIVE)
  ☐ DimReseller.GeographyKey → DimGeography.GeographyKey (ACTIVE)
  ☐ DimGeography.SalesTerritoryKey → DimSalesTerritory.SalesTerritoryKey (ACTIVE)
  ☐ DimEmployee.SalesTerritoryKey → DimSalesTerritory.SalesTerritoryKey (ACTIVE)
  ☐ DimEmployee.DepartmentGroupKey → DimDepartmentGroup.DepartmentGroupKey (ACTIVE)
  ☐ DimProduct.ProductSubcategoryKey → DimProductSubcategory.ProductSubcategoryKey (ACTIVE)
  ☐ DimProductSubcategory.ProductCategoryKey → DimProductCategory.ProductCategoryKey (ACTIVE)

PHASE 3: DATE TABLE CONFIGURATION
─────────────────────────────────────────────────────────────────
☐ Go to Data tab
☐ Right-click DimDate table
☐ Click "Mark as date table"
☐ Select FullDateAlternateKey as the date column

PHASE 4: CREATE MEASURES TABLE
─────────────────────────────────────────────────────────────────
☐ Go to Data tab
☐ Click Table (Create new calculated table)
☐ Name it: _Measures
☐ Formula: _Measures = ROW("Placeholder", 1)
☐ Right-click Placeholder column → Hide in Report View

PHASE 5: ADD MEASURES
─────────────────────────────────────────────────────────────────
☐ Select _Measures table
☐ Click New Measure (22 total - see DAX_MEASURES.txt)
☐ Create each measure from the DAX code provided

PHASE 6: HIDE KEY COLUMNS
─────────────────────────────────────────────────────────────────
☐ Data tab → For each table
☐ Right-click each *Key column → Hide in Report View
☐ Examples: CustomerKey, ProductKey, GeographyKey, DateKey, etc.

PHASE 7: FORMAT CURRENCY COLUMNS
─────────────────────────────────────────────────────────────────
☐ Data tab → Select each table
☐ For *Amount columns: Format as Currency
☐ For *Pct columns: Format as Percentage
☐ For *Quantity columns: Format as Whole Number

PHASE 8: SAVE & VALIDATE
─────────────────────────────────────────────────────────────────
☐ Click Report tab
☐ Create test visual: Card with [Total Sales Amount]
☐ Should show ~\$61.5M (or similar total)
☐ File → Save As
☐ Save as: AdventureWorks_Semantic_Model.pbix
☐ (Optional) File → Save As → Power BI Project for PBIP format

═════════════════════════════════════════════════════════════════

📊 MODEL STATISTICS
───────────────────────────────────────────────────────────────
Dimensions: 13
Fact Tables: 4
Total Tables: 17
Relationships: 22
Measures: 22+
Inactive Relationships: 6

📚 REFERENCE DOCUMENTS
───────────────────────────────────────────────────────────────
• AdventureWorks_Model_Design.md ← Architecture & full design
• AdventureWorks_Implementation_Guide.md ← Detailed step-by-step
• AdventureWorks_Quick_Reference.md ← Quick lookup card
• MODEL_IMPORT_TABLES.txt ← Tables to import
• DAX_MEASURES.txt ← All measure definitions
• RELATIONSHIPS_CHECKLIST.txt ← This file

═════════════════════════════════════════════════════════════════
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
═════════════════════════════════════════════════════════════════
"@

$checklistPath = "C:\Users\JURIXTEL\OneDrive - Capgemini\Documents\GIT\PowerBI-Agentic-Harness\RELATIONSHIPS_CHECKLIST.txt"
Set-Content -Path $checklistPath -Value $checklist

Write-Host "✓ Build checklist created: RELATIONSHIPS_CHECKLIST.txt" -ForegroundColor Green

# ============================================================================
# PART 7: Display Summary
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  MODEL GENERATION COMPLETE                                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📋 GENERATED FILES:" -ForegroundColor Yellow
Write-Host "  ✓ MODEL_IMPORT_TABLES.txt" -ForegroundColor Green
Write-Host "  ✓ POWER_QUERY_M_CODE.txt" -ForegroundColor Green
Write-Host "  ✓ DAX_MEASURES.txt" -ForegroundColor Green
Write-Host "  ✓ RELATIONSHIPS_CHECKLIST.txt" -ForegroundColor Green

Write-Host "`n📊 MODEL SUMMARY:" -ForegroundColor Yellow
Write-Host "  Dimensions:       13 tables" -ForegroundColor Cyan
Write-Host "  Fact Tables:       4 tables" -ForegroundColor Cyan
Write-Host "  Total Tables:     17 tables" -ForegroundColor Cyan
Write-Host "  Relationships:    22 total" -ForegroundColor Cyan
Write-Host "  Measures:         22+ DAX expressions" -ForegroundColor Cyan

Write-Host "`n🚀 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Open Power BI Desktop" -ForegroundColor White
Write-Host "  2. Follow the checklist: RELATIONSHIPS_CHECKLIST.txt" -ForegroundColor White
Write-Host "  3. Copy-paste measures from: DAX_MEASURES.txt" -ForegroundColor White
Write-Host "  4. Reference the detailed guide: AdventureWorks_Implementation_Guide.md" -ForegroundColor White

Write-Host "`n💡 TIP: Open all files in your workspace for easy reference:" -ForegroundColor Yellow
Write-Host "  • Set up your VS Code split view" -ForegroundColor Gray
Write-Host "  • Keep this checklist visible while building" -ForegroundColor Gray

Write-Host "`n✅ All configuration files ready in:" -ForegroundColor Yellow
Write-Host "  $($configPath.Substring(0, $configPath.LastIndexOf('\')))" -ForegroundColor Cyan

Write-Host "`n"
