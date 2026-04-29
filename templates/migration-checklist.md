# Migration Checklist — Power BI

Use this checklist when migrating a Power BI solution from one format, environment, or tool to another. Complete each section before proceeding to the next phase.

---

## Migration Type

Check which migration type applies:

- [ ] PBIX → PBIP (source-control-ready project)
- [ ] Legacy BI tool → Power BI (e.g. SSRS, Tableau, Qlik)
- [ ] Power BI Desktop → Power BI Service deployment
- [ ] Development workspace → Production workspace
- [ ] Import mode → Direct Lake / DirectQuery

---

## Phase 1: Pre-Migration Assessment

### Source Inventory

- [ ] List all reports and datasets in scope
- [ ] Document current report owners and user groups
- [ ] Identify data sources and connection types (SQL Server, SharePoint, Excel, etc.)
- [ ] Identify data refresh schedules and gateway dependencies
- [ ] Document row-level security requirements

### Model Assessment

- [ ] Run semantic model review (use `semantic-model-review` skill)
- [ ] Run DAX review (use `dax-review` skill)
- [ ] Document all Critical and Warning findings
- [ ] Confirm which findings must be resolved before migration proceeds

### Report Assessment

- [ ] Run report review (use `report-review` skill)
- [ ] List all visuals that need to be recreated or redesigned
- [ ] Identify any dependency on deprecated or unsupported visual types

### Stakeholder Sign-Off

- [ ] Migration scope agreed with project sponsor
- [ ] Cutover date confirmed
- [ ] Rollback plan documented

---

## Phase 2: Environment Preparation

### Source Control

- [ ] PBIP project created in source control repository
- [ ] Branch protection rules applied to default branch
- [ ] `.gitignore` excludes PBIX, cache, and lock files (use `pbip-structure` skill to validate)
- [ ] Development and UAT workspaces created in Power BI Service

### Data Source Connectivity

- [ ] On-premises gateway configured and tested (if required)
- [ ] Data source credentials stored in gateway / environment variables (never in source files)
- [ ] Test refresh completed successfully in Development workspace

### Workspace Access

- [ ] Security groups created for workspace roles (Admin, Member, Contributor, Viewer)
- [ ] Access provisioned for development team
- [ ] End-user access confirmed for UAT workspace

---

## Phase 3: Migration Execution

### Semantic Model Migration

- [ ] Model recreated or imported as PBIP project
- [ ] All original measures recreated and validated
- [ ] Relationships validated against source model
- [ ] Date table present and marked
- [ ] RLS roles recreated and tested
- [ ] Agent model review re-run on migrated model — no new Critical findings

### Report Migration

- [ ] All pages recreated with equivalent visual coverage
- [ ] Measure-to-visual mappings validated against original reports
- [ ] Navigation, drill-through, and tooltip pages recreated
- [ ] Custom theme applied
- [ ] Agent report review re-run — no new Critical findings

### Data Validation

- [ ] Key measure values validated against source system (spot-check minimum 5 measures)
- [ ] Filtered and unfiltered totals validated
- [ ] Date range extremes validated (min date, max date)
- [ ] RLS validation completed — correct users see correct data

---

## Phase 4: UAT

- [ ] UAT workspace populated with migrated solution
- [ ] Business users notified of UAT period
- [ ] UAT test cases documented and shared
- [ ] Defects logged and prioritised
- [ ] All Critical defects resolved before proceeding
- [ ] UAT sign-off obtained from business owner

---

## Phase 5: Production Deployment

- [ ] Release readiness review completed (use `release-readiness` skill)
- [ ] Release readiness report saved to `reviews/` with date stamp
- [ ] No unresolved Critical findings
- [ ] Any accepted Warnings documented with name, date, and justification
- [ ] Production workspace access confirmed
- [ ] Deployment performed by authorised human (agent does not deploy to Production)
- [ ] Post-deployment smoke test completed (key visuals render, refresh succeeds)

---

## Phase 6: Cutover and Hypercare

- [ ] Old reports/datasets marked as deprecated (do not delete immediately)
- [ ] End users notified of new report location
- [ ] Data refresh schedule set and confirmed
- [ ] Hypercare period defined (recommended minimum 2 weeks)
- [ ] Support escalation path documented
- [ ] Old artefacts decommissioned after hypercare sign-off

---

## Post-Migration Review

- [ ] Agent release readiness review re-run 2 weeks after go-live
- [ ] Any new findings raised as backlog items
- [ ] Lessons learned documented for the next migration
