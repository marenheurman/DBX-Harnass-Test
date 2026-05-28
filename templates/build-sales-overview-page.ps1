# build-sales-overview-page.ps1
# ============================================================
# Appends a "Sales Overview" report page to an existing .pbix.
#
# Harness references:
#   docs/report-build-patterns.md  -> Pattern B (append, never replace)
#   docs/pbix-layout-format.md     -> UTF-16-LE, SecurityBindings zeroed
#   templates/build-report-template.py -> port of make_* helpers
#
# Model manifest (from live MCP inspection):
#   Measures table : _Measures
#   Measures       : Total Sales, Gross Profit, Total Orders, Gross Profit %
#   Dimensions     : Sales Territory[Region], Date[Calendar Year], Product[Product Line]
# ============================================================

$PBIX_IN  = "C:\Users\abarkhui\OneDrive - Capgemini\AgenticAI The Forge\AGenticAI Test 27-5.pbix"
$PBIX_OUT = "C:\Users\abarkhui\OneDrive - Capgemini\AgenticAI The Forge\AGenticAI Test 27-5 - Sales Overview.pbix"

# ─── Helper: visual position ─────────────────────────────────────────────────

function New-Pos($x, $y, $z, $w, $h, $tab) {
    @{ x = $x; y = $y; z = $z; tabOrder = $tab; height = $h; width = $w }
}

function New-VC($x, $y, $w, $h, $tab, $cfg, $qry = $null, $dt = $null) {
    @{
        x              = $x
        y              = $y
        z              = 1000 + $tab
        width          = $w
        height         = $h
        config         = ($cfg | ConvertTo-Json -Depth 30 -Compress)
        filters        = "[]"
        query          = if ($qry) { $qry | ConvertTo-Json -Depth 30 -Compress } else { "" }
        dataTransforms = if ($dt)  { $dt  | ConvertTo-Json -Depth 30 -Compress } else { "" }
    }
}

# ─── Textbox ─────────────────────────────────────────────────────────────────

function New-Textbox($vid, $x, $y, $w, $h, $text, $tab, $fontSize = "24pt", $color = "#1a1a2e") {
    $cfg = @{
        name    = $vid
        layouts = @(@{ id = 0; position = (New-Pos $x $y (1000 + $tab) $w $h $tab) })
        singleVisual = @{
            visualType = "textbox"
            objects = @{
                general = @(@{
                    properties = @{
                        paragraphs = @(@{
                            textRuns = @(@{
                                value     = $text
                                textStyle = @{
                                    fontWeight = "bold"
                                    fontSize   = $fontSize
                                    color      = @{ solid = @{ color = $color } }
                                }
                            })
                            horizontalTextAlignment = "left"
                        })
                    }
                })
            }
        }
    }
    New-VC $x $y $w $h $tab $cfg
}

# ─── Card ────────────────────────────────────────────────────────────────────

function New-Card($vid, $x, $y, $w, $h, $measureName, $tab, $measuresTable = "_Measures") {
    $qref    = "m.$measureName"
    $from_c  = @(@{ Name = "m"; Entity = $measuresTable; Type = 0 })
    $select  = @(@{
        Measure = @{
            Expression = @{ SourceRef = @{ Source = "m" } }
            Property   = $measureName
        }
        Name = $qref
    })
    $cfg = @{
        name    = $vid
        layouts = @(@{ id = 0; position = (New-Pos $x $y (1000 + $tab) $w $h $tab) })
        singleVisual = @{
            visualType   = "card"
            projections  = @{ Values = @(@{ queryRef = $qref; active = $false }) }
            prototypeQuery = @{ Version = 2; From = $from_c; Select = $select }
        }
    }
    $qry = @{ Commands = @(@{ SemanticQueryDataShapeCommand = @{
        Query   = @{ Version = 2; From = $from_c; Select = $select }
        Binding = @{
            Primary      = @{ Groupings = @(@{ Projections = @(0) }) }
            DataReduction = @{ DataVolume = 3; Primary = @{ Window = @{ Count = 1000 } } }
            Version      = 1
        }
        ExecutionMetricsKind = 1
    } }) }
    $dt = @{
        queryMetadata   = @{ Select = @(@{ Restatement = $measureName; Name = $qref; Type = 260 }) }
        visualElements  = @(@{ name = "measure"; queryRef = $qref; dataCategory = 0 })
    }
    New-VC $x $y $w $h $tab $cfg $qry $dt
}

# ─── Chart ───────────────────────────────────────────────────────────────────

function New-Chart($vid, $x, $y, $w, $h, $visualType, $catEntity, $catAlias, $catCol, $measureName, $tab, $measuresTable = "_Measures") {
    $cqref   = "$catAlias.$catCol"
    $mqref   = "m.$measureName"
    $from_c  = @(
        @{ Name = $catAlias; Entity = $catEntity;     Type = 0 }
        @{ Name = "m";       Entity = $measuresTable; Type = 0 }
    )
    $select  = @(
        @{ Column  = @{ Expression = @{ SourceRef = @{ Source = $catAlias } }; Property = $catCol      }; Name = $cqref }
        @{ Measure = @{ Expression = @{ SourceRef = @{ Source = "m"       } }; Property = $measureName }; Name = $mqref }
    )
    $cfg = @{
        name    = $vid
        layouts = @(@{ id = 0; position = (New-Pos $x $y (1000 + $tab) $w $h $tab) })
        singleVisual = @{
            visualType  = $visualType
            projections = @{
                Category = @(@{ queryRef = $cqref; active = $false })
                Y        = @(@{ queryRef = $mqref; active = $false })
            }
            prototypeQuery = @{ Version = 2; From = $from_c; Select = $select }
        }
    }
    $qry = @{ Commands = @(@{ SemanticQueryDataShapeCommand = @{
        Query   = @{ Version = 2; From = $from_c; Select = $select }
        Binding = @{
            Primary      = @{ Groupings = @(@{ Projections = @(0, 1) }) }
            DataReduction = @{ DataVolume = 4; Primary = @{ Top = @{ Count = 1000 } } }
            Version      = 1
        }
        ExecutionMetricsKind = 1
    } }) }
    $dt = @{
        queryMetadata  = @{ Select = @(
            @{ Restatement = $catCol;      Name = $cqref; Type = 1   }
            @{ Restatement = $measureName; Name = $mqref; Type = 260 }
        )}
        visualElements = @(
            @{ name = "category"; queryRef = $cqref; dataCategory = 0 }
            @{ name = "measure";  queryRef = $mqref; dataCategory = 0 }
        )
    }
    New-VC $x $y $w $h $tab $cfg $qry $dt
}

# ─── BUILD PAGE ──────────────────────────────────────────────────────────────

$visuals = @()
$t = 0

# Row 1 — Title
$visuals += New-Textbox "vis0001" 16 10 1248 48 "Sales Overview" $t; $t++

# Row 2 — KPI cards (y=70, h=110)
$cards = @(
    @{ name = "Total Sales";    x = 16  }
    @{ name = "Gross Profit";   x = 328 }
    @{ name = "Total Orders";   x = 640 }
    @{ name = "Gross Profit %"; x = 952 }
)
$i = 2
foreach ($c in $cards) {
    $vid = "vis{0:D4}" -f $i
    $visuals += New-Card $vid $c.x 70 296 110 $c.name $t; $t++; $i++
}

# Row 3 — Charts (y=200, h=495)
$visuals += New-Chart "vis0006" 16  200 397 495 "columnChart" "Sales Territory" "st" "Region"       "Total Sales" $t; $t++
$visuals += New-Chart "vis0007" 429 200 397 495 "lineChart"   "Date"            "d"  "Calendar Year" "Total Sales" $t; $t++
$visuals += New-Chart "vis0008" 842 200 422 495 "barChart"    "Product"         "p"  "Product Line"  "Total Sales" $t; $t++

$page = @{
    id               = 0
    name             = "SalesOverview"
    displayName      = "Sales Overview"
    filters          = "[]"
    ordinal          = 0
    config           = "{}"
    displayOption    = 1
    width            = 1280
    height           = 720
    visualContainers = $visuals
}

# ─── WRITE PBIX (Pattern B) ──────────────────────────────────────────────────

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

Write-Host "Reading: $PBIX_IN"

$inStream  = [System.IO.File]::OpenRead($PBIX_IN)
$inZip     = [System.IO.Compression.ZipArchive]::new($inStream, [System.IO.Compression.ZipArchiveMode]::Read)

# Read and parse current layout
$layoutEntry = $inZip.GetEntry("Report/Layout")
$layoutReader = [System.IO.StreamReader]::new($layoutEntry.Open(), [System.Text.Encoding]::Unicode)
$layoutJson   = $layoutReader.ReadToEnd()
$layoutReader.Close()
$layout = $layoutJson | ConvertFrom-Json

# Determine next ordinal
$existing    = $layout.sections
$maxOrdinal  = if ($existing.Count -gt 0) { ($existing | Measure-Object -Property ordinal -Maximum).Maximum } else { -1 }
$page.ordinal = $maxOrdinal + 1
$page.id      = $maxOrdinal + 1

# Append page — convert to mutable list, add, convert back
$sectionsList = [System.Collections.Generic.List[object]]::new()
foreach ($s in $existing) { $sectionsList.Add($s) }
$sectionsList.Add($page)
$layout.sections = $sectionsList.ToArray()

# Serialise layout back to UTF-16-LE bytes
$newLayoutJson  = $layout | ConvertTo-Json -Depth 50 -Compress
$newLayoutBytes = [System.Text.Encoding]::Unicode.GetBytes($newLayoutJson)

# Write new PBIX
$outBytes  = [System.IO.MemoryStream]::new()
$outZip    = [System.IO.Compression.ZipArchive]::new($outBytes, [System.IO.Compression.ZipArchiveMode]::Create, $true)

foreach ($entry in $inZip.Entries) {
    $newEntry   = $outZip.CreateEntry($entry.FullName, [System.IO.Compression.CompressionLevel]::Optimal)
    $outStream  = $newEntry.Open()

    if ($entry.FullName -eq "SecurityBindings") {
        # Zero out — stale hash causes "corrupted file" error
        $outStream.Write([byte[]]@(), 0, 0)
    } elseif ($entry.FullName -eq "Report/Layout") {
        $outStream.Write($newLayoutBytes, 0, $newLayoutBytes.Length)
    } else {
        $srcStream = $entry.Open()
        $srcStream.CopyTo($outStream)
        $srcStream.Close()
    }
    $outStream.Close()
}

$outZip.Dispose()
$inZip.Dispose()
$inStream.Close()

# Write memory stream to file
[System.IO.File]::WriteAllBytes($PBIX_OUT, $outBytes.ToArray())

Write-Host "[OK] Written : $PBIX_OUT"
Write-Host "     Page    : $($page.displayName)"
Write-Host "     Visuals : $($visuals.Count) containers"
