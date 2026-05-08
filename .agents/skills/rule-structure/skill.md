---
name: rule-structure
description: Use when reviewing or preparing rule and governance documents for inclusion in the agentic harness. Converts long, unstructured prose into explicit, structured formats to improve human scanability and AI-agent parsing reliability.
---

## What This Skill Does

- **Does:** Converts prose-heavy rule and governance documents into structured formats (tables, numbered steps, bullet lists) and enforces uniform document layout.
- **When:** A rule file needs hardening for reliable AI-agent consumption, or document layout is inconsistent.
- **Requires:** Access to files in `rules/`, agent-consumed `docs/` files (listed in `docs/llm-index.json`), and all skill files in `.agents/skills/`.
- **Produces:** A normalised document, a change log, and an ambiguity register per file processed.
- **Does NOT:** Write, add, remove, or reorder rules. Does not evaluate whether rules are correct or well-designed.

# Rule Structure

## Overview

Analyse rule and governance documents and convert long, unstructured prose into explicit structured formats such as numbered steps, tables, bullet lists, and code blocks. The goal is to make rules, examples, and exceptions clearly distinguishable for both human readers and AI agents.

**Core principle:** Structured formats produce more consistent and predictable AI-agent behaviour than free-form prose. This skill restructures presentation only and must never change meaning, intent, or scope.

---

## Atomic Rule Principle

When restructuring:

- Each bullet list item must contain one independent rule only
- Each table row must represent one independent constraint, condition, definition, or prohibition
- Do not combine unrelated constraints into one structure item
- Do not split rules unless boundaries are explicitly present in the original text

---

## When to Use

Use this skill when:
- Rule files contain long paragraphs of continuous, unstructured text
- Documents are consumed by AI agents as part of the harness
- Fast human scanning and reliable agent parsing are required
- Preparing or maintaining safety rules, governance policies, or standards

---

## When Not to Use

Do not use this skill when:
- Writing, adding, or removing rules
- Changing rule semantics, intent, or emphasis
- Summarisation, compression, or paraphrasing
- Evaluating correctness or quality of rules
- Rewriting for tone or simplifying language
- Reorganising document hierarchy
- Inferring implied rules

---

## Standard Layouts

### Skill File Layout

All skill files in this harness must follow this section order. Flag deviations when processing skill files.

| Position | Section | Format | Required |
|---|---|---|---|
| 1 | YAML frontmatter | `---` block with `name`, `description` | Always |
| 2 | `## What This Skill Does` | Bullet list (Does / When / Requires / Produces / Does NOT) | Always |
| 3 | `# [Skill Title]` | H1 heading, matches skill name | Always |
| 4 | `## Overview` | Short prose + bold core principle | Always |
| 5 | `## When to Use` | Bullet list | Always |
| 6 | `## When Not to Use` | Bullet list with redirects | Always |
| 7 | `## [Skill] Workflow` | Numbered steps (H3 per step) | Always |
| 8 | Reference material | Tables (severity definitions, scoring, etc.) | When applicable |
| 9 | `## Examples` | Numbered, Before/After format | When applicable |

### Rule / Governance Document Layout

All files in `rules/` and agent-consumed `docs/` files must follow this section order where applicable. Flag deviations.

| Position | Section | Format | Required |
|---|---|---|---|
| 1 | `# [Document Title]` | H1 heading | Always |
| 2 | Purpose statement | 1–2 sentences: what this document governs | Always |
| 3 | Rule sections | H2 per topic; rules as bullet lists or tables | Always |
| 4 | Examples or illustrations | Code blocks or Before/After pairs | When applicable |
| 5 | Exceptions or caveats | Bullet list or table | When applicable |

---

## Rule Structure Workflow

### Step 1: Inspect Files

Read all files in the following locations and process each one:

- All files in `rules/` — apply **Rule / Governance Document Layout**
- All files in `docs/` that are consumed by AI agents — check `docs/llm-index.json` for the current list — apply **Rule / Governance Document Layout**
- All skill files in `.agents/skills/` — one `skill.md` per subdirectory — apply **Skill File Layout**
- If files have been added to any of these locations that are not yet listed in the index, include them

Treat every section independently.

### Step 2: Detect Prose

A section must be selected for restructuring when ANY of the following conditions are met:

| Condition | Observable signal |
|---|---|
| Pure prose | The section contains no tables, no numbered lists, and no bullet lists |
| Overloaded list items | A list exists but one or more items contain two or more complete sentences |
| Long sentences | Any sentence exceeds ~30 words (approximately two printed lines). Long sentences reduce agent parsing reliability |
| Mixed content in one paragraph | Rules, examples, and exceptions appear in a single continuous paragraph with no structural separation |
| Inconsistent structural markers | Inline numbering ("1) ... 2) ..."), semicolons used as list separators, or a partial bullet list where some items are bulleted and others are inline prose |
| Layout non-conformance | The document does not follow the applicable Standard Layout defined in this skill |

### Decision Table

| Detection Result | Action |
|---|---|
| Pure prose detected | Restructure |
| Long sentence detected | Split structurally |
| Mixed content detected | Split by explicit type boundaries |
| Meaning risk detected | Preserve original |
| Ambiguous structure detected | Record in Ambiguity Register |
| Layout mismatch detected | Normalize layout |

Mandatory rules:

- This detection process is mandatory and not discretionary
- If none of the above conditions are met, leave the section unchanged
- Do not infer hidden structure that is not explicitly present

### Step 3: Apply Structure

For each qualifying section, match its content to the appropriate structure.

Mandatory mapping:

| Content Type | Required Structure |
|---|---|
| Sequence or process | Numbered list |
| Independent rules or constraints | Bullet list |
| Properties or comparisons | Table |
| Absolute prohibitions or safety rules | Table (rule \| description) |
| Examples or illustrations | Code block |
| Definitions or terms | Table (term \| definition) |
| Conditional rules | Table (condition \| consequence) |
| Long sentences | Split structurally, then apply appropriate format |
| Layout non-conformance | Normalize to Standard Layout |
| Mixed sections | Split only when type boundaries are explicit |

#### Long Sentence Splitting Rules

Split long sentences ONLY at explicit separators already present in the original text:

- "and"
- "or"
- Semicolons
- Inline numbering
- Commas separating independent clauses

Do not:

- Infer implied boundaries
- Rewrite wording
- Reorder constraints
- Introduce new grouping logic

#### Mixed Section Rules

- Split mixed sections only when boundaries between content types are explicit
- If subsection boundaries are ambiguous, preserve the original section
- Record unresolved ambiguity in the Ambiguity Register
- Never infer unstated subsection boundaries

#### Layout Normalization Rules

When layout non-conformance is detected:

- Reorder sections to match the applicable Standard Layout
- Add missing mandatory sections as placeholders only
- Preserve all existing content and ordering within sections

#### Placeholder Rules

Placeholders:

- Must contain only the exact comment: `<!-- TODO: fill -->`
- Must not contain inferred or generated content
- Must not be interpreted as existing policy or guidance

### Step 4: Preserve Meaning

When restructuring:

- Do not change wording unless required for formatting
- Do not split a single logical rule into multiple independent rules unless explicit boundaries already exist
- Do not merge separate rules into one
- Do not remove exceptions or caveats
- Preserve absolute versus conditional language
- Preserve ordering when ordering contributes to meaning
- Light structural interpretation is permitted only when wording is explicit and non-conditional

#### High-Risk Sections

Apply heightened review to any section containing:

- "must never"
- "is prohibited"
- "under no circumstances"

Flag the following files for additional caution:

| File | Section |
|---|---|
| `rules/safety-rules.md` | Absolute Prohibitions |
| `docs/governance.md` | Core Governance Principles |

If restructuring introduces semantic uncertainty:

- Preserve the original section unchanged
- Record the ambiguity in the Ambiguity Register

### Step 5: Output

Output requirements:

- Replace only sections identified as qualifying in Step 2
- Preserve existing headings, ordering, and already-structured content
- Deliver artefacts inline in this order:
  1. Normalized Document
  2. Change Log
  3. Ambiguity Register

Do not create separate files unless explicitly instructed.

#### Deliverables

##### Normalized Document

The updated document with qualifying prose-heavy sections replaced using structured Markdown formats.

##### Change Log

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| *(section name)* | *(e.g. Prose)* | *(e.g. Table (rule \| description))* | *(e.g. Preserved conditional wording)* |

##### Ambiguity Register

| Section | Ambiguity | Structure Chosen | Reason |
|---|---|---|---|
| *(section name)* | *(e.g. Mixed sequence and constraints)* | *(e.g. Numbered list)* | *(e.g. Sequence was dominant)* |

### Step 6: Validate and Confirm

#### Validation Checklist

- [ ] Every in-scope section evaluated against Step 2 criteria
- [ ] Every qualifying section restructured or logged
- [ ] No semantic meaning altered
- [ ] Change Log complete
- [ ] Ambiguity Register complete
- [ ] Existing structured content preserved
- [ ] No inferred rules introduced
- [ ] Layout normalization completed where required

If any validation item cannot be confirmed:

- State explicitly which condition failed
- Explain why confirmation could not be completed

---

## Priority Hierarchy

When steps conflict, resolve in this order:

| Priority | Rule |
|---|---|
| 0 | Explicit user instruction overrides layout preference unless meaning changes |
| 1 | Preserve Meaning overrides all structure choices |
| 2 | Apply Structure mappings when meaning is preserved |
| 3 | Record unresolved ambiguity in the Ambiguity Register |

---

## Examples

### Example 1: Prose → Table (Absolute Prohibition)

**Before:**

Agents must never publish to a production workspace, and they must never delete or overwrite data without explicit user approval. Credentials and secrets must never be embedded in any output.

**After:**

| Rule | Description |
|---|---|
| Never publish to production | Agents must not publish to a production workspace |
| Never delete or overwrite data | Explicit user approval is required before any destructive action |
| Never embed credentials | Secrets and credentials must not appear in any agent output |

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| Absolute Prohibitions | Prose | Table (rule \| description) | Three distinct prohibitions separated |

---

### Example 2: Prose → Bullet List (Independent Constraints)

**Before:**

All measures must use DIVIDE instead of the division operator to prevent divide-by-zero errors. Measure names must be written in sentence case and must not include the table name as a prefix. Hardcoded values must not appear inside measure expressions.

**After:**

- All measures must use `DIVIDE` instead of the division operator to prevent divide-by-zero errors
- Measure names must be written in sentence case and must not include the table name as a prefix
- Hardcoded values must not appear inside measure expressions

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| DAX Measure Standards | Prose | Bullet list | Three independent constraints; no sequence implied |

---

### Example 3: Failure — Section Left Unchanged

**Before:**

The governance model should reflect the organisation's data culture, and where relevant, align with existing enterprise architecture decisions. Exceptions may apply in regulated environments.

**Action:** Section left unchanged.

| Section | Ambiguity | Structure Chosen | Reason |
|---|---|---|---|
| Governance Model Alignment | Rule boundary between constraint and exception unclear | None — section left unchanged | Restructuring would require semantic interpretation |

---

### Example 4: Long Sentence → Bullet List

**Before:**

The agent must validate that all relationships use single-direction cross-filtering, that no bidirectional relationships exist without documented justification, and that inactive relationships have a corresponding USERELATIONSHIP measure defined in the model.

**After:**

- All relationships must use single-direction cross-filtering
- Bidirectional relationships must not exist without documented justification
- Inactive relationships must have a corresponding `USERELATIONSHIP` measure defined in the model

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| Relationship Rules | Long sentence (38 words) | Bullet list | Three constraints extracted; no meaning change |

---

### Example 5: Layout Non-Conformance

**Before (file structure):**

```
# Modeling Rules
## Fact Table Rules
## Dimension Table Rules
## Relationship Rules
```

**Issue:** Missing mandatory "Purpose statement" (position 2 in Rule / Governance Document Layout).

**After:**

```
# Modeling Rules
<!-- TODO: fill -->
## Fact Table Rules
## Dimension Table Rules
## Relationship Rules
```

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| Modeling Rules | Missing purpose statement | Added placeholder | Layout non-conformance; content not altered |


