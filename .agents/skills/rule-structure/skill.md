---
name: rule-structure
description: Use when reviewing or preparing rule and governance documents for inclusion in the agentic harness. Converts long, unstructured prose into explicit, structured formats to improve human scanability and AI-agent parsing reliability.
---

## Overview

Analyse rule and governance documents and convert long, unstructured prose into explicit structured formats such as numbered steps, tables, bullet lists, and code blocks.
 
The goal is to make rules, examples, and exceptions clearly distinguishable for both human readers and AI agents.

- This skill restructures presentation only and must never change meaning, intent, or scope.

---

## Core Principle

Structured formats (tables, lists, steps) produce more consistent and predictable AI-agent behaviour than free-form prose.

---

## When to Use

Use this skill when:
- Rule files contain long paragraphs of continuous, unstructured text
- Documents are consumed by AI agents as part of the harness
- Fast human scanning and reliable agent parsing are required
- Preparing or maintaining safety rules, governance policies, or standards

Do not use this skill when:
- Writing, adding, or removing rules
- Changing rule semantics, intent, or emphasis
- Summarisation, compression, or paraphrasing
- Evaluating correctness or quality of rules

---

## Non-Goals

This skill does not:
- Rewrite for tone
- Simplify language
- Shorten content
- Improve grammar unless required for formatting
- Reorganise document hierarchy
- Infer implied rules

---

## Rule Structure Workflow

### Step 1: Inspect Files

Read all files in `rules/` and `docs/governance.md`, and go through each one.

Treat every section independently.

### Step 2: Detect Prose
A section must be selected for restructuring when ANY of the following conditions are met:
- More than 70% of the section content is prose paragraphs
- Lists contain embedded multi-sentence prose
- Rules, examples, and exceptions are mixed within a single paragraph
- Structural markers are inconsistent or incomplete (e.g. inline numbering, semicolons used as list separators, partial bullet lists)

- This detection rule is mandatory and not discretionary.
- If none of the above conditions are met, leave the section unchanged and move to the next.

### Step 3: Determine Role
Determine whether the prose primarily describes:
- A sequence of actions or steps
- Independent rules or constraints
- Properties, attributes, or comparisons
- Absolute prohibitions or safety rules
- Examples or illustrations
- Definitions or terms
- Conditional rules (if X then Y)
- A mix of the above types

- Do not interpret meaning beyond what is required to determine structure.

### Step 4: Apply Structure
Apply the following mandatory mapping:
- Sequence or process → Numbered list
- Independent rules or constraints → Bullet list
- Properties or comparisons → Table
- Absolute prohibitions or safety rules → Table (rule | description)
- Examples or illustrations → Code block
- Definitions or terms → Table (term | definition)
- Conditional rules → Table (condition | consequence)
- Mixed sections → Split into subsections per type, then apply the mapping to each subsection independently

- The structure must reflect the role of the content.

### Step 5: Preserve Meaning
When restructuring:
- Do not change wording unless required for formatting
- Do not split a single logical rule into multiple independent rules unless the original prose already expresses multiple distinct constraints
- Do not merge separate rules into one
- Do not remove exceptions or caveats
- Preserve absolute versus conditional language
- Light structural interpretation (such as separating clearly enumerated constraints, or extracting explicitly stated prohibitions into rows) is permitted when wording is explicit and non-conditional

- The transformation must be structural only.

> **Mandatory attention areas:** Apply extra care to the *Absolute Prohibitions* section in `safety-rules.md` and the *Core Governance Principles* section in `docs/governance.md`. These sections contain absolute prohibitions where structural changes carry the highest risk of altering perceived meaning.

### Step 6: Output
- Replace only the sections identified as prose-heavy
- Preserve file structure, headings, ordering, and existing structured content

For each file processed, produce the following three deliverables:

#### Normalized Document
The updated file with all qualifying prose-heavy sections replaced by explicit structured formats using Markdown lists, tables, and code blocks.

#### Change Log
Record every transformation applied using the following schema:

| Section | Original Form | New Form | Notes |
|---|---|---|---|
| *(section name)* | *(e.g. Prose)* | *(e.g. Table (rule \| description))* | *(e.g. Preserved conditional wording)* |

#### Ambiguity Register
For sections where structure choice was unclear, document using the following schema:

| Section | Ambiguity | Structure Chosen | Reason |
|---|---|---|---|
| *(section name)* | *(e.g. Mixed sequence and constraints)* | *(e.g. Numbered list)* | *(e.g. Sequence was dominant)* |

---

## Priority Hierarchy

When steps conflict, resolve in this order:

1. **Failure Conditions** — if restructuring requires semantic interpretation beyond what is explicitly stated, leave the section unchanged
2. **Step 5 (Preserve Meaning)** — always overrides structure choice; meaning is non-negotiable
3. **Step 4 (Apply Structure)** — mandatory when not overridden by Step 5
4. **Ambiguity Register** — when none of the above resolves the conflict, document the ambiguity and the choice made

---

## Agent Behavior Rules
- Structure only; never introduce or remove meaning
- No semantic changes; intent and scope must remain identical
- No rule merging; do not split a single logical rule unless the original prose already expresses multiple distinct constraints
- No removal of exceptions or caveats
- Explicit structure is mandatory when detection criteria are met
- Ambiguity must be surfaced explicitly, never guessed
- Primary objective is AI-agent behaviour consistency, not stylistic improvement

---

## Failure Conditions
- If restructuring requires interpretation of meaning, leave the section unchanged, add it to the Ambiguity Register, and explain why restructuring was unsafe
- If rule boundaries cannot be determined reliably, leave the section unchanged, add it to the Ambiguity Register, and explain why boundaries could not be established

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

**Change Log entry:** Absolute Prohibitions | Prose | Table (rule \| description) | Three distinct prohibitions identified and separated

---

### Example 2: Prose → Bullet List (Independent Constraints)

**Before:**

All measures must use DIVIDE instead of the division operator to prevent divide-by-zero errors. Measure names must be written in sentence case and must not include the table name as a prefix. Hardcoded values must not appear inside measure expressions.

**After:**

- All measures must use `DIVIDE` instead of the division operator to prevent divide-by-zero errors
- Measure names must be written in sentence case and must not include the table name as a prefix
- Hardcoded values must not appear inside measure expressions

**Change Log entry:** DAX Measure Standards | Prose | Bullet list | Three independent constraints; no sequence implied

---

### Example 3: Failure — Section Left Unchanged (Ambiguity Register)

**Before:**

The governance model should reflect the organisation's data culture, and where relevant, align with existing enterprise architecture decisions. Exceptions may apply in regulated environments.

**Situation:** The sentence contains a constraint ("align with enterprise architecture"), a conditional ("where relevant"), and an exception ("regulated environments") — but the rule boundary between the constraint and the exception is unclear. Restructuring would require interpreting what qualifies as a "regulated environment," which goes beyond structural analysis.

**Action:** Section left unchanged.

**Ambiguity Register entry:**

| Section | Ambiguity | Structure Chosen | Reason |
|---|---|---|---|
| Governance Model Alignment | Rule boundary between constraint and exception unclear; "regulated environments" requires interpretation | None — section left unchanged | Restructuring would require meaning interpretation; graceful degradation applied |

---

## Why It Matters
The harness is consumed by AI agents as much as by humans.
Structured text gives agents clear signals about what is a rule, what is an example, and what is an exception. Free-form prose obscures these distinctions and leads to inconsistent agent behaviour. This skill exists to eliminate that ambiguity.
