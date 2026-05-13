# NEXT_ACTIONS - Active Execution Queue

**Updated At:** 2026-05-13 12:22 CEST
**Execution Mode:** operating
**Max Items:** 10

## Active Work

### P1 [BL-001] Build Power BI MVP

Owner: human + coding agent.
Next action: import `data/*.csv` into Power BI Desktop, create relationships from `powerbi/model.md`, add measures from `powerbi/measures.dax`, and build pages from `powerbi/pages.md`.
Exit criteria: a local `.pbix` or `.pbip` report exists with all five demo pages.

### P2 [BL-002] Validate manager demo flow

Owner: human + coding agent.
Next action: run through `docs/demo/DEMO_SCRIPT.md` using the report and confirm that the fairness message is clear.
Exit criteria: walkthrough notes and screenshots/evidence are logged under `docs/evidence/`.

## Queue Rules

- Keep this file short.
- List only active, open work.
- Remove completed items immediately.
- Every active item must reference a backlog ID like `[BL-001]`.
- Include owner, next action, and exit criteria when items exist.
