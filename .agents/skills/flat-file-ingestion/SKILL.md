---
name: flat-file-ingestion
description: Use when loading any uncontrolled flat or semi-structured data source (CSV, TSV, Excel export, SharePoint list export, BCP/SQL text export) into a Power BI semantic model via Power Query M. Applies defensive patterns to handle NULL text strings, European decimal formats, binary/noise columns, and blank key rows. Invoke before or during a model build whenever the data source is not a clean typed connector (SQL, dataflow, or live connection).
---

## What This Skill Does

- **Does:** Produces robust Power Query M partition expressions for CSV-sourced tables that load cleanly with zero partition errors, regardless of regional settings, source data quality, or schema noise.
- **When:** Any table in a model build is sourced from a flat file (CSV, TSV, text export from SQL Server or similar).
- **Requires:** Knowledge of the target table schema (column names and intended data types).
- **Produces:** A complete, hardened M expression for each partition, ready to apply via MCP `partition_operations Update`.
- **Does NOT:** Design the model schema or define relationships — use the `semantic-model-review` or `report-build` skills for that.

---

## When to Use

- During a model build (`report-build` skill) when the data source is flat files
- When a refresh produces `DataFormat.Error`, `OLE DB 0x80040E4E`, or row-level errors on CSV-sourced tables
- When inheriting a model with CSV sources that produce errors on refresh

---

## When Not to Use

- DirectQuery or live connection tables — M expressions do not apply
- Tables sourced from databases, APIs, or SharePoint lists with proper connectors
- DAX calculated tables

---

## The 5 Defensive Patterns

Apply all 5 patterns in sequence for every CSV-sourced partition.

---

### Pattern 1 — Whitelist Columns First (`Table.SelectColumns`)

Always select only the columns the model needs **before** any transformation.

**Why:** CSV exports often contain binary blobs (e.g. `LargePhoto`), multi-language duplicate columns, and source-system columns irrelevant to the model. These cause type inference failures and increase load time.

```powerquery
#"Kept Columns" = Table.SelectColumns(
    #"Promoted Headers",
    {"ProductKey", "EnglishProductName", "StandardCost", "ListPrice", "Color", "Status"}
)
```

**Rule:** Never transform a column that will not be used in the model. Select first, transform second.

---

### Pattern 2 — Replace `"NULL"` Text with True `null`

Always replace the literal string `"NULL"` across all columns before any type cast.

**Why:** SQL Server text exports write `NULL` as the text string `"NULL"` rather than an empty cell. `Number.From("NULL")` and `Date.From("NULL")` both throw `DataFormat.Error`.

```powerquery
#"Replace NULLs" = Table.ReplaceValue(
    #"Kept Columns",
    "NULL",
    null,
    Replacer.ReplaceValue,
    Table.ColumnNames(#"Kept Columns")
)
```

**Rule:** Always apply this step immediately after `Table.SelectColumns`, before any type transformation.

---

### Pattern 3 — Explicit Decimal Comma Handling for European CSVs

Never rely on the locale argument in `Table.TransformColumnTypes` for decimal conversion. Use explicit `Text.Replace` + `Number.FromText` instead.

**Why:** The locale argument in `TransformColumnTypes` is evaluated against Power BI Desktop's regional settings, which may differ from the file's locale. This causes silent failures or errors depending on the machine running the refresh.

```powerquery
// ❌ Unreliable — depends on Desktop locale settings
Table.TransformColumnTypes(source, {{"SalesAmount", type number}}, "nl-NL")

// ✅ Explicit — always works regardless of regional settings
#"Cast Numbers" = Table.TransformColumns(
    #"Replace NULLs",
    {
        {"SalesAmount",  each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"UnitPrice",    each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"TotalCost",    each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number}
    }
)
```

**Rule:** For any CSV that uses comma as the decimal separator, always use `Text.Replace(_, ",", ".")` before `Number.FromText`. Do not use the locale parameter in `TransformColumnTypes` for numeric columns.

---

### Pattern 4 — Safe Casting with `try ... otherwise null`

Wrap every individual column cast in `try ... otherwise null`.

**Why:** A single unconvertible cell value (e.g. an unexpected string in a number column) causes the entire partition to fail, resulting in zero rows loaded. `try ... otherwise null` demotes bad values to `null` instead of crashing the load.

```powerquery
// ❌ Unsafe — one bad value fails the entire partition
{"OrderQuantity", Int64.Type}

// ✅ Safe — bad values become null, partition still loads
{"OrderQuantity", each try Int64.From(_) otherwise null, Int64.Type}
```

Apply to all type casts:

```powerquery
#"Cast Keys" = Table.TransformColumns(#"Replace NULLs", {
    {"ProductKey",   each try Int64.From(_) otherwise null, Int64.Type},
    {"CustomerKey",  each try Int64.From(_) otherwise null, Int64.Type}
}),
#"Cast Numbers" = Table.TransformColumns(#"Cast Keys", {
    {"StandardCost", each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
    {"ListPrice",    each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number}
}),
#"Cast Dates" = Table.TransformColumns(#"Cast Numbers", {
    {"StartDate",    each try Date.From(_) otherwise null, type date},
    {"EndDate",      each try Date.From(_) otherwise null, type date}
})
```

**Rule:** Never use `TransformColumnTypes` with a bare type (e.g. `Int64.Type`) for columns sourced from CSV without wrapping in `try ... otherwise null`.

---

### Pattern 5 — Remove Blank Surrogate Keys on Dimension Tables

Always filter out rows where the surrogate key is `null` from dimension tables after type casting.

**Why:** Power BI enforces uniqueness on the one-side of a Many-to-One relationship. A blank key value violates this constraint and causes a refresh error: *"Column contains blank values and this is not allowed for columns on the one side of a many-to-one relationship."*

```powerquery
#"Removed Blank Keys" = Table.SelectRows(
    #"Cast Keys",
    each [ProductKey] <> null
)
```

**Rule:** Apply this as the final step on every dimension table. Fact tables do not require this step unless a foreign key column is also used as a relationship key.

---

## Complete Example — Dimension Table

```powerquery
let
    Source = Csv.Document(
        File.Contents("C:\Data\DimProduct.csv"),
        [Delimiter=";", Encoding=1252, QuoteStyle=QuoteStyle.None]
    ),
    // Step 1 — Promote headers
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // Pattern 1 — Whitelist only model-relevant columns
    #"Kept Columns" = Table.SelectColumns(#"Promoted Headers",
        {"ProductKey","ProductAlternateKey","EnglishProductName",
         "StandardCost","ListPrice","Color","Size","ProductLine",
         "Class","Style","ModelName","StartDate","EndDate","Status"}
    ),

    // Pattern 2 — Replace "NULL" text with true null across all columns
    #"Replace NULLs" = Table.ReplaceValue(
        #"Kept Columns", "NULL", null,
        Replacer.ReplaceValue, Table.ColumnNames(#"Kept Columns")
    ),

    // Patterns 3 + 4 — Safe casting with explicit decimal handling
    #"Cast Keys" = Table.TransformColumns(#"Replace NULLs", {
        {"ProductKey", each try Int64.From(_) otherwise null, Int64.Type}
    }),
    #"Cast Numbers" = Table.TransformColumns(#"Cast Keys", {
        {"StandardCost", each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"ListPrice",    each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number}
    }),
    #"Cast Dates" = Table.TransformColumns(#"Cast Numbers", {
        {"StartDate", each try Date.From(_) otherwise null, type date},
        {"EndDate",   each try Date.From(_) otherwise null, type date}
    }),
    #"Cast Text" = Table.TransformColumnTypes(#"Cast Dates", {
        {"ProductAlternateKey", type text}, {"EnglishProductName", type text},
        {"Color", type text}, {"Size", type text}, {"ProductLine", type text},
        {"Class", type text}, {"Style", type text}, {"ModelName", type text},
        {"Status", type text}
    }),

    // Pattern 5 — Remove rows with blank surrogate key (dimension tables only)
    #"Removed Blank Keys" = Table.SelectRows(#"Cast Text", each [ProductKey] <> null)
in
    #"Removed Blank Keys"
```

---

## Complete Example — Fact Table

```powerquery
let
    Source = Csv.Document(
        File.Contents("C:\Data\FactInternetSales.csv"),
        [Delimiter=";", Encoding=1252, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // Pattern 2 — Replace "NULL" strings
    #"Replace NULLs" = Table.ReplaceValue(
        #"Promoted Headers", "NULL", null,
        Replacer.ReplaceValue, Table.ColumnNames(#"Promoted Headers")
    ),

    // Patterns 3 + 4 — Safe casting
    #"Cast Keys" = Table.TransformColumns(#"Replace NULLs", {
        {"ProductKey",        each try Int64.From(_) otherwise null, Int64.Type},
        {"CustomerKey",       each try Int64.From(_) otherwise null, Int64.Type},
        {"OrderDateKey",      each try Int64.From(_) otherwise null, Int64.Type},
        {"SalesTerritoryKey", each try Int64.From(_) otherwise null, Int64.Type},
        {"OrderQuantity",     each try Int64.From(_) otherwise null, Int64.Type}
    }),
    #"Cast Numbers" = Table.TransformColumns(#"Cast Keys", {
        {"SalesAmount",       each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"TotalProductCost",  each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"UnitPrice",         each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"TaxAmt",            each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number},
        {"Freight",           each try Number.FromText(Text.Replace(_, ",", "."), "en-US") otherwise null, type number}
    }),
    #"Cast Dates" = Table.TransformColumns(#"Cast Numbers", {
        {"OrderDate", each try Date.From(_) otherwise null, type date},
        {"DueDate",   each try Date.From(_) otherwise null, type date},
        {"ShipDate",  each try Date.From(_) otherwise null, type date}
    })
    // Note: no blank key filter on fact tables
in
    #"Cast Dates"
```

---

## Checklist

Before applying any CSV partition, confirm:

- [ ] `Table.SelectColumns` whitelists only model columns
- [ ] `Table.ReplaceValue("NULL", null)` applied across `Table.ColumnNames(...)`
- [ ] All numeric columns use `Text.Replace(_, ",", ".")` + `Number.FromText` — no locale in `TransformColumnTypes`
- [ ] All casts wrapped in `try ... otherwise null`
- [ ] Dimension tables have `Table.SelectRows([Key] <> null)` as the final step
- [ ] Fact tables do NOT have a blank key filter (foreign key nulls are valid)
