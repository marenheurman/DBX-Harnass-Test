# Model Review — [Project Name]

**Date:** YYYY-MM-DD
**Reviewed by:** [AI Agent / Name]
**Skill applied:** semantic-model-review
**Model name:** [Name of the semantic model]
**Environment:** [Development / UAT / Production]

---

## Summary

| Review Area | Critical | Warnings | Informational |
|---|---|---|---|
| Table Classification | | | |
| Relationships | | | |
| Star Schema Compliance | | | |
| Date Table | | | |
| DAX Measures | | | |
| **TOTAL** | | | |

**Overall Verdict:** [BLOCKED / READY WITH WARNINGS / READY]

---

## Model Overview

**Total tables:** [N]
**Fact tables identified:** [List]
**Dimension tables identified:** [List]
**Bridge tables identified:** [List or None]
**Calculated tables identified:** [List or None]
**Total relationships:** [N]
**Total measures:** [N]

---

## Table Classification

| Table Name | Classification | Grain Statement | Notes |
|---|---|---|---|
| [TableName] | Fact / Dimension / Bridge / Calculated | [One row per...] | |

---

## Critical Findings

*List all Critical findings here. Leave this section blank (with "None") if no Critical findings exist.*

None.

---

### [Finding Title]

**Area:** [Relationships / Star Schema / Date Table / DAX / etc.]
**Object:** [Table, relationship, or measure name]
**Detail:**
[Describe the issue clearly. State what was found, why it is a problem, and what incorrect behaviour it could cause.]

**Suggested action:**
[State the recommended fix specifically enough that a developer can act on it without further investigation.]

---

## Warnings

*List all Warnings here.*

### [Warning Title]

**Area:** [Area]
**Object:** [Object name]
**Detail:** [Description]
**Suggested action:** [Recommendation]

---

## Informational

*List all Informational observations here.*

### [Observation Title]

**Area:** [Area]
**Object:** [Object name]
**Detail:** [Description]

---

## Relationship Map Summary

| Relationship | From Table | From Column | To Table | To Column | Cardinality | Direction | Active |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

---

## DAX Measure Findings

*(Complete this section when the review includes DAX analysis, or leave blank if a separate DAX review is being produced.)*

| Measure Name | Table | Issue | Severity | Suggested Fix |
|---|---|---|---|---|
| | | | | |

---

## Recommended Next Steps

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

---

## Sign-Off

| Role | Name | Date | Accepted? |
|---|---|---|---|
| Reviewing Developer | | | |
| BI Lead | | | |
| Project Manager | | | |

*"Accepted" means the findings have been reviewed and any remaining Warnings have been acknowledged as accepted risks.*
