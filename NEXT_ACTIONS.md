# NEXT_ACTIONS - Active Execution Queue

**Updated At:** 2026-05-13 14:30 CEST
**Execution Mode:** operating
**Max Items:** 10

## Active Work

### P1 [BL-001] Build Power BI MVP

Owner: human + coding agent (Windows GUI MCP agent now available).
Next action: use Windows GUI MCP agent + PBIP guidance to build real Power BI report. Import `data/*.csv`, create relationships from `powerbi/model.md`, add DAX measures from `powerbi/measures.dax`, build five pages from `powerbi/pages.md`. Use `demo-preview/` as the verified design reference.
Exit criteria: a local `.pbix` or `.pbip` report exists with all five demo pages and has been visually verified.

### P2 [BL-006] Convert to PBIP if supported

Owner: coding agent.
Next action: check if Power BI Desktop can save as PBIP. If yes, create PBIP project for versionable source-controlled report definition.
Exit criteria: PBIP directory exists under `powerbi/` or decision documented.

## Queue

- [BL-003] Add a simple Power App or Dataverse prototype for workload input.
- [BL-004] Add an Outlook import/enrichment path for calendar categories.
- [BL-005] Verify agent skill adapters in the actual CLIs the project will use.

## Queue Rules

- Keep this file short.
- List only active, open work.
- Remove completed items immediately.
- Every active item must reference a backlog ID like `[BL-001]`.
- Include owner, next action, and exit criteria when items exist.