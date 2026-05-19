# Governance

This document defines the governance principles that apply when using AI agents in Power BI development. It is intended for BI leads, architects, and anyone responsible for the quality, security, and reliability of Power BI solutions in an enterprise environment.

These principles override any default agent behaviour. If there is a conflict between what an agent would do by default and what is stated here, the rules in this document take precedence.

---

## Core Governance Principles

### 1. Humans Approve All Changes

AI agents in this accelerator are advisory. They analyse, review, and propose — they never apply changes to production systems autonomously. Every change to a semantic model, report, or workspace must be reviewed and applied by a qualified human.

### 2. Production Workspaces Are Protected

No agent tool call, script, or automated process may modify a Power BI Service workspace that is classified as Production. Development and UAT workspaces may be modified by agents only when explicitly permitted by the workspace owner and documented in the project governance plan.

### 3. Credentials Are Never Handled by Agents

Power BI Service bearer tokens, data source credentials, gateway credentials, and service principal secrets must never be passed to an agent in a prompt, logged in output files, or stored in any file that is tracked by source control. Environment variables are the only permitted mechanism.

### 4. Source Control Is Mandatory for Agent-Assisted Projects

Any Power BI project that uses AI agent assistance must be stored as a PBIP project in source control. This ensures that all changes are traceable, reviewable, and reversible. PBIX-only workflows are not supported.

### 5. Reviews Are Documented

All agent-produced review outputs must be saved as markdown files in the project repository under a `reviews/` folder (or equivalent) with a date-stamped filename. This creates an audit trail of what was reviewed, what was found, and what action was taken.

### 6. Agent Output Is Not Ground Truth

Agent findings are a starting point for human review, not a definitive verdict. A Critical finding from an agent must be investigated by a human before being acted upon. A clean agent review does not guarantee a defect-free model or report.

---

## Workspace Classification

| Classification | Description | Agent Access |
|---|---|---|
| Development (DEV) | Active development workspace | Read allowed; write proposals only |
| User Acceptance Testing (UAT) | Pre-release validation | Read allowed; no agent writes |
| Production (PROD) | Live, end-user-facing | Read-only metadata inspection; no writes |

---

## Roles and Responsibilities

| Role | Responsibility |
|---|---|
| BI Developer | Uses agent skills for daily review and development tasks |
| BI Lead / Tech Lead | Reviews and approves agent-produced review reports before release |
| Data Architect | Owns modeling-rules.md and approves changes to star schema standards |
| Security / Governance Lead | Owns governance-rules.md and safety-rules.md |
| Project Manager | Ensures governance documentation is included in project deliverables |

---

## Change Control for This Accelerator

- Changes to the rules in this repository (`rules/`) must go through a pull request review involving at least one BI Lead and one Governance Lead.
- Changes to skills in `.agents/skills/` must include a corresponding update to `tests/` to validate the new or changed behaviour.

---

## Compliance Checkpoints

Include the following governance checkpoints in your project delivery lifecycle:

| Checkpoint | Timing | Agent Task |
|---|---|---|
| Model Architecture Review | End of design phase | Run semantic-model-review skill |
| DAX Quality Gate | Before UAT | Run dax-review skill |
| Report UX Review | Before user testing | Run report-review skill |
| Pre-Release Readiness | Before PROD deployment | Run release-readiness skill |
| Post-Release Audit | 2 weeks after go-live | Manual review against documented output |

---

## Data Sensitivity

When the semantic model contains personal data, sensitive commercial data, or data subject to regulatory compliance (GDPR, HIPAA, etc.):

- Ensure RLS is implemented and tested before any agent review — this ensures the agent can validate that RLS roles exist and are correctly defined, even though agent queries themselves bypass RLS
- Agent DAX queries run without RLS — findings may include data that is restricted for end users
- All agent output must be reviewed for sensitive values before sharing outside the development team
- Do not share agent output files externally without reviewing them for sensitive values
- Do not include example data rows containing real personal or commercial data in agent prompts

---

## References

- Microsoft Learn: [Power BI deployment pipelines](https://learn.microsoft.com/power-bi/create-reports/deployment-pipelines-overview)
- Microsoft Learn: [Workspace roles in Power BI](https://learn.microsoft.com/power-bi/collaborate-share/service-roles-new-workspaces)
- Microsoft Learn: [Power BI guidance for governance](https://learn.microsoft.com/power-bi/guidance/powerbi-implementation-planning-governance)
- [rules/governance-rules.md](../rules/governance-rules.md)
