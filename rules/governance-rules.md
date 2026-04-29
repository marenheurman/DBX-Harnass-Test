# Governance Rules

These rules define the governance framework for AI-assisted Power BI development in enterprise environments. They apply to all projects that use the **Power BI Agentic Harness** and must be followed by all team members.

---

## Workspace Governance

### Workspace Classification

All Power BI workspaces must be assigned a classification before any agent-assisted development begins:

| Classification | Purpose | Change Control |
|---|---|---|
| **Development (DEV)** | Active development and experimentation | Developer discretion |
| **User Acceptance Testing (UAT)** | Pre-release validation by business users | BI Lead approval required |
| **Production (PROD)** | Live end-user-facing content | Change request and manager sign-off required |

The workspace classification must be documented in the project governance plan before the Power BI Agentic Harness tools are used.

### Who Can Deploy to Each Environment

| Role | DEV | UAT | PROD |
|---|---|---|---|
| BI Developer | Yes | With BI Lead approval | No |
| BI Lead | Yes | Yes | With manager sign-off |
| Project Manager | No | No | With BI Lead sign-off |
| AI Agent | Never directly | Never directly | Never directly |

---

## Source Control Requirements

- All Power BI projects assisted by this accelerator must be version-controlled as PBIP projects in a Git repository
- PBIX files must not be used as the primary versioned artefact
- The default branch must be protected: no direct pushes; all changes via pull request
- Each pull request must pass the following before merge:
  - Agent-produced model or DAX review (if semantic model changed)
  - At least one human reviewer approval
  - No unresolved Critical findings from agent review

---

## Review and Audit Trail

- All agent-produced review outputs must be saved to a `reviews/` folder in the project repository
- Review filenames must follow this convention: `YYYY-MM-DD-<review-type>.md`
- Review files must be committed to source control — they form part of the project audit trail
- A review file must not be deleted or amended without documenting the reason for the change

---

## Accepted Risks

When a release proceeds with outstanding Warnings (Ready with Warnings verdict), the accepting risk must be documented:

```markdown
## Accepted Risk Statement

Warning: [Description of warning]
Accepted by: [Name, Role]
Date: [YYYY-MM-DD]
Reason: [Why this warning is acceptable for this release]
Expected resolution: [Sprint / Date when this will be addressed]
```

This statement must be included in the release readiness report before go-live.

---

## Data Governance

### Personal Data

- Power BI models containing personal data must have Row-Level Security (RLS) implemented before UAT
- Agent DAX queries run without RLS filtering — findings must not be shared outside the development team
- PII must never appear in example data, documentation, or review output files
- All reports displaying personal data must be registered in the organisation's data inventory

### Sensitive Commercial Data

- Revenue, margin, and pricing data must be access-controlled via RLS or workspace permissions
- The agent's review output must not include sample data rows containing real commercial figures

### Regulatory Compliance

- Projects subject to GDPR, HIPAA, or other data regulations must complete a Data Protection Impact Assessment (DPIA) before go-live, regardless of agent review status
- The agent does not perform compliance assessment — this is a human responsibility

---

## Power BI Service Governance

- Workspace access must be managed via security groups, not individual user accounts
- Report embedding (Publish to Web) must be explicitly approved — it creates publicly accessible content
- Data refresh schedules must be documented and monitored
- Large datasets (>1 GB) in import mode require capacity planning before deployment to PROD
- Premium or Fabric capacity usage must be approved by the infrastructure team before provisioning

---

## Agent Governance

- The **Power BI Agentic Harness** may be updated as Power BI features evolve — teams must review the release notes of this repository before applying new skills or rules
- Skills must not be modified locally for a single project without also contributing the change back to the Power BI Agentic Harness via pull request
- If a skill produces consistently incorrect output for a specific organisation's context, raise an issue in the Power BI Agentic Harness repository rather than silently modifying the skill locally

---

## References

- Microsoft Learn: [Power BI deployment pipelines](https://learn.microsoft.com/power-bi/create-reports/deployment-pipelines-overview)
- Microsoft Learn: [Workspace roles in Power BI](https://learn.microsoft.com/power-bi/collaborate-share/service-roles-new-workspaces)
- Microsoft Learn: [Power BI guidance for governance](https://learn.microsoft.com/power-bi/guidance/powerbi-implementation-planning-governance)
- [docs/governance.md](../docs/governance.md)
