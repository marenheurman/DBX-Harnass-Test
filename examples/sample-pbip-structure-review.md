# Sample PBIP Structure Review

This example shows the expected output of the `pbip-structure` skill for a fictional PBIP project called **AdventureWorks Sales**.

---

## Review Output

| Field | Value |
|---|---|
| Project | AdventureWorks Sales |
| Review date | 2026-03-18 |
| Reviewed by | AI Agent (`pbip-structure` skill v1.0) |
| Scope | Semantic model folder, report folder, `.gitignore`, and partition expressions |

---

## Summary

| Severity | Count |
|---|---|
| Critical | 2 |
| Warning | 3 |
| Informational | 1 |
| Overall verdict | Not safe to commit until Critical findings are resolved |

---

## Critical Findings

### CR-01 — Mixed semantic model formats detected

**File(s):**
- `AdventureWorks.SemanticModel/definition/model.bim`
- `AdventureWorks.SemanticModel/definition/database.tmdl`

**Detail:** The project contains both `model.bim` and `database.tmdl` as semantic model entry points. A PBIP project must use one model format consistently. Keeping both introduces ambiguity about which definition is authoritative and increases the risk of merge conflicts or publishing the wrong model state.

**Suggested action:** Remove the unused format and keep a single source of truth.

---

### CR-02 — Embedded credential found in partition expression

**File:** `AdventureWorks.SemanticModel/definition/tables/Sales.tmdl`

**Detail:** The partition source contains `password=` in the connection string. Credentials must never be committed to source control.

**Suggested action:**
1. Remove the credential from the file
2. Rotate the exposed credential immediately
3. Move authentication to a secure store or environment-based mechanism

---

## Warnings

### W-01 — `.gitignore` does not exclude local Power BI cache

**File:** `.gitignore`

**Detail:** The repository does not exclude `.pbi/`, which can introduce local cache noise and machine-specific changes.

**Suggested action:** Add `.pbi/` to `.gitignore`.

---

### W-02 — `relationships.tmdl` missing from TMDL project

**File:** `AdventureWorks.SemanticModel/definition/`

**Detail:** Table files exist under `definition/tables/`, but `relationships.tmdl` is missing. If the model contains relationships, this indicates an incomplete or corrupted export.

**Suggested action:** Re-export the PBIP project and confirm relationship metadata is present.

---

### W-03 — Report page manifest does not match page files

**File(s):**
- `AdventureWorks.Report/definition/report.json`
- `AdventureWorks.Report/definition/pages/`

**Detail:** `report.json` lists a page named `ExecutiveSummary`, but the corresponding page JSON file is not present. This suggests an incomplete rename or a deleted file that was not removed from the manifest.

**Suggested action:** Align `report.json` with the actual page files.

---

## Informational Findings

### I-01 — `roles.tmdl` not present

**File:** `AdventureWorks.SemanticModel/definition/`

**Detail:** No `roles.tmdl` file was found. This is acceptable if row-level security is not required for the project.

**Suggested action:** Confirm whether row-level security is intentionally out of scope.

---

## Recommended Next Steps

| Priority | Action | Owner |
|---|---|---|
| 1 | Remove mixed semantic model format and keep one entry point | BI Developer |
| 2 | Remove and rotate exposed credential | BI Developer / Data Engineer |
| 3 | Fix page manifest mismatch | BI Developer |
| 4 | Add missing `.gitignore` exclusions | BI Developer |
| 5 | Re-export or restore relationship metadata | BI Developer |
