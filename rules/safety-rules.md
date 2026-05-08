# Safety Rules

These rules define what AI agents must never do when assisting with Power BI development. They take precedence over any other instruction, skill, or prompt.

---

## Environment Awareness

Before executing any model inspection, query, or review task, the agent must determine the environment it is operating against.

### Recognised Environments

| Environment | Description | Agent Behaviour |
|---|---|---|
| Local PBIP project | PBIP files on the developer's filesystem | Read-only file access permitted |
| Power BI Desktop (local) | Model open in Desktop, connected via local AS engine | Read-only MCP queries permitted |
| Power BI Desktop (live, build context) | Desktop open, build pattern active (Patterns A–E in report-build skill) | MCP write operations (tables, measures, relationships) and Python ZIP (report pages) permitted. Requires explicit user confirmation of environment before first write. User must save `.pbix` manually in Desktop. Agent must never overwrite the source file. |
| Development workspace | Power BI Service workspace classified as DEV | Read-only; write proposals only |
| Test / UAT workspace | Power BI Service workspace classified as UAT | Read-only; no agent writes |
| Production workspace | Power BI Service workspace classified as PROD | Strict read-only; no queries without explicit approval |

### Classification Failure — Default to Production

If the environment cannot be clearly determined from the project context, workspace name, or user instruction, the agent **must assume the environment is Production** and apply Production-level restrictions immediately. The agent must not proceed with any write or query operation until classification is confirmed by the user.

```
Agent: I cannot determine the workspace classification for this environment.
       I am applying Production-level restrictions until you confirm the environment.
       Please confirm: is this a Development, UAT, or Production workspace?
```

Classification must be re-confirmed at the start of each session. The agent must not carry forward a previous session's classification as an assumption.

---

## Absolute Prohibitions

The following actions are **forbidden** under all circumstances:

### 1. No Production Writes

Production environments are **always write-protected** for AI agents. Agents must never publish, push, deploy, or modify any artefact in a Power BI Service workspace classified as Production. This includes all of the following:

- Publishing a `.pbix` or PBIP project to a Production workspace
- Updating a semantic model (dataset) in a Production workspace via REST API or XMLA endpoint
- Overwriting any report page in a Production workspace
- Modifying Row Level Security roles in a live Production dataset
- Modifying or creating dataset refresh schedules in a Production workspace
- Triggering a dataset refresh in a Production workspace (manual, incremental, or scheduled)
- Promoting artefacts through Power BI Deployment Pipelines into the Production stage
- Modifying workspace settings, access roles, or capacity assignments in a Production workspace

If asked to perform any of the above, the agent must refuse and clearly state that production changes require a human to perform the action manually via Power BI Desktop, the Power BI Service UI, or an authorised deployment pipeline.

### 2. No Credential Handling

Agents must never:
- Ask the user to provide a Power BI bearer token, service principal secret, or password in a prompt
- Echo or log any credential value found in environment variables or files
- Write credential values to any file — including output files, logs, or documentation
- Store credentials in `.env` files that are tracked by source control

If a credential appears in a file being reviewed, the agent must flag it as a Critical security finding and redact the value in any output it produces.

### 3. No Autonomous Changes to Semantic Models

Agents must never:
- Rename tables, columns, or measures in a live model without explicit human instruction
- Delete relationships, measures, or columns
- Modify partition expressions or data source connections
- Change RLS roles or table permissions

All proposed changes must be written as text output for the developer to review and apply.

### 4. No Bulk Operations Without Confirmation

Agents must not run bulk DAX queries, bulk metadata reads, or iterative operations across all partitions of a large model without confirming the scope with the user first. Large query operations can slow or lock a local model.

### 5. No Sharing of Sensitive Data

If a DAX query executed against the model returns rows containing personally identifiable information (PII), financial records, or other sensitive data, the agent must:
- Not include example data rows in any output file
- Summarise the query result (row counts, column names) without reproducing the data
- Flag that the result contained potentially sensitive data

### 6. No Dataset Refresh Operations

Agents must never trigger dataset refresh operations in any Power BI Service workspace. This prohibition applies regardless of workspace classification and includes:

- Triggering a manual refresh via the Power BI REST API
- Initiating or modifying incremental refresh policies
- Modifying or creating refresh schedules
- Clearing the refresh cache

Refresh operations consume capacity resources, can impact the availability of production reports during execution, and may have downstream dependencies (such as paginated reports or downstream dataflows) that the agent cannot fully assess. All refresh operations must be initiated by a human.

### 7. No Gateway or Data Source Modifications

Agents must never modify gateway or data source configurations. This includes:

- Modifying on-premises data gateway configurations
- Adding, updating, or deleting data source credentials stored in a gateway
- Updating connection strings in partition expressions or data source definitions
- Rebinding a dataset to a different data source or gateway
- Changing the privacy level of a data source

These operations can break data refresh across all reports and datasets that depend on the affected gateway or data source, including reports the agent is not aware of. All gateway and data source changes must be performed by a human with appropriate gateway administrator permissions.

---

## Safe Operation Checklist

Before taking any action, the agent must confirm:

- [ ] **Environment classified:** Have I confirmed the workspace or project environment (Local / Dev / UAT / Production)?
- [ ] **Production restrictions applied:** If environment is Production or unknown, am I operating strictly read-only?
- [ ] **Read-only behaviour confirmed:** Am I reading, not writing, modifying, or triggering operations?
- [ ] **Proposed changes labelled:** Is any suggested change clearly presented as a proposal for human review, not an action I have taken?
- [ ] **Credentials redacted:** Does my output contain any credential values? (If yes, redact them before writing output)
- [ ] **Sensitive data excluded:** Does my output contain personal data, financial records, or other sensitive data rows? (If yes, summarise counts and column names only — do not reproduce the data)

---

## What Agents Are Permitted to Do

All permitted actions are strictly **read-only**. Agents may read, analyse, and propose — never modify, trigger, or deploy.

| Permitted Action | Notes |
|---|---|
| Read model metadata via MCP | Tables, columns, measures, relationships — read-only |
| Run read-only DAX queries | For review and validation purposes only; never writes or triggers refresh |
| Read PBIP files from the filesystem | Source-control-safe JSON/TMDL files; no writes |
| Write review reports as markdown files | In the project `reviews/` folder on the local filesystem only |
| Propose changes in structured text output | Developer reviews and applies the changes manually |
| Flag issues with severity ratings | As defined in each skill |
| Read workspace metadata via REST API (read) | Dataset names, report names, workspace members — read-only GET requests |

---

## References

- [docs/governance.md](../docs/governance.md)
- [rules/governance-rules.md](governance-rules.md)
- Microsoft Learn: [Power BI REST APIs](https://learn.microsoft.com/rest/api/power-bi/)
