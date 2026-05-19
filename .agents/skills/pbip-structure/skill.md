---
name: pbip-structure
description: Use when validating the structure of a Power BI Project (PBIP) for source-control readiness, file integrity, and correct project layout. Invoke when setting up a new project, migrating from PBIX, or validating before a pull request.
---

## What This Skill Does

- **Does:** Validates the structure and integrity of a Power BI Project (PBIP) to confirm it is correctly organised for source control, team collaboration, and automated deployment.
- **When:** Setting up a new PBIP project, migrating from PBIX format, validating before a pull request, or running a release readiness check.
- **Requires:** Access to PBIP project files on the filesystem.
- **Produces:** A structured findings report with file path, check that failed, severity, and suggested action for each finding.
- **Does NOT:** Create, modify, or delete project files. Reports findings and suggests corrections for the developer to apply.

# PBIP Project Structure Analysis

## Overview

Validate the structure and integrity of a Power BI Project (PBIP) to confirm it is correctly organised for source control, team collaboration, and automated deployment.

**Core principle:** Read and validate only. Do not create, modify, or delete project files. Report findings and suggest corrections for the developer to apply.

---

## When to Use

Use this skill when:
- Setting up a new PBIP project and confirming correct file layout
- Migrating from PBIX format to PBIP (source-control-ready) format
- Validating a project before a pull request or sprint review
- Investigating why a PBIP project cannot be opened or published correctly
- Running a release readiness check (called automatically by `release-readiness` skill)

---

## When Not to Use

- Reviewing the content of the semantic model (use `semantic-model-review`)
- Reviewing DAX quality (use `dax-review`)

---

## Expected PBIP Project Structure

A well-formed PBIP project should contain the following:

```
<ProjectName>.SemanticModel/
  .platform                           ← Platform metadata file (required)
  definition/
    model.bim                         ← Full TOM JSON (alternative to TMDL)
    OR
    database.tmdl                     ← TMDL entry point (if using TMDL format)
    tables/
      <TableName>.tmdl                ← One TMDL file per table
    relationships.tmdl                ← All relationships
    cultures.tmdl                     ← Optional: localisation
    roles.tmdl                        ← Optional: RLS roles

<ProjectName>.Report/
  .platform                           ← Platform metadata file (required)
  definition/
    report.json                       ← Report-level settings and theme
    pages/
      <PageName>.json                 ← One JSON file per report page

.gitignore                            ← Must exclude cache and lock files
```

---

## PBIP Structure Workflow

### Step 1: Check Top-Level Structure

- Does a `<Name>.SemanticModel/` folder exist?
- Does a `<Name>.Report/` folder exist?
- Are both `.platform` files present in the respective folders?

### Step 2: Validate Semantic Model Files

| Check | Rule | Severity |
|-------|------|----------|
| `model.bim` or `database.tmdl` present | One of these must exist as the model definition entry point | Critical |
| No mixed format | Do not mix `model.bim` and TMDL files for the same model | Critical |
| Table files present (TMDL) | At least one `tables/<Name>.tmdl` file expected | Warning |
| `relationships.tmdl` present (TMDL) | Required if relationships exist in the model | Warning |
| No embedded data in partitions | Partition `source` expressions must reference a data source, not contain embedded CSV/JSON data | Critical |
| No credentials in connection strings | Partition expressions must not contain usernames, passwords, or bearer tokens | Critical |

### Step 3: Validate Report Files

| Check | Rule | Severity |
|-------|------|----------|
| `report.json` present | Required for valid report definition | Critical |
| At least one page JSON file present | A report with no pages is invalid | Critical |
| Page filenames match report.json page list | Orphan or missing pages indicate file integrity issues | Warning |

### Step 4: Check .gitignore

Confirm the `.gitignore` file (at repo root or project folder) excludes:

```
*.pbix
.pbi/
*.lock
cache/
*.tmp
~$*
```

If no `.gitignore` exists, flag as Warning and provide a suggested file.

### Step 5: Check for Sensitive Content

Scan partition expressions and connection strings for:
- Passwords (`password=`, `pwd=`)
- Tokens (`bearer`, `token=`, `key=`)
- Hardcoded server names that differ from environment variable patterns
- Hardcoded usernames

Flag all findings as Critical.

### Step 6: Produce Report

List all findings with file path, check that failed, severity, and suggested action.

---

## Severity Definitions

| Severity | Definition |
|----------|------------|
| **Critical** | Project will not open, publish, or is not safe to commit to source control. Must be resolved immediately. |
| **Warning** | Project may work but is not correctly structured for collaboration or deployment. Should be resolved. |
| **Informational** | Structural suggestion or best practice. Low urgency. |

---

## Example Finding

```
File: AdventureWorks.SemanticModel/definition/tables/Sales.tmdl
Finding: Embedded credential in partition source expression
Severity: Critical
Detail: The partition source expression for the 'Sales' table contains the string 'password='.
        Credentials must never be stored in TMDL or model.bim files committed to source control.
Suggested action: Remove the credential, use an environment variable or Power BI gateway
                  credential store, and rotate the exposed credential immediately.
```

---

## Suggested .gitignore for PBIP Projects

```gitignore
# Power BI local cache files
.pbi/
*.lock
localSettings.json

# Temporary and OS files
*.tmp
~$*
Thumbs.db
.DS_Store

# Do not commit raw PBIX files (use PBIP instead)
*.pbix
```
