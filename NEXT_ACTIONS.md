# NEXT_ACTIONS - Active Execution Queue

**Updated At:** 2026-05-15 17:05 CEST
**Execution Mode:** operating
**Max Items:** 10

## Active Work

### P1 [BL-AUTO-002] Create seed PBIP/PBIR project

Owner: coding agent + Windows GUI MCP agent.
Next action: Enable PBIP preview feature in Power BI Desktop (File → Options → Preview features → "Power BI Project (.pbip) save option"). Then verify the programmatic PBIP at `scripts/experiments/pbip-tmsl-attempt/` opens. If not, create a blank PBIP from Desktop and diff the structures.
Exit criteria: Power BI Desktop opens the saved PBIP folder and renders data model. Evidence captured in `docs/evidence/004-seed-pbip-pbir/`.

### P2 [BL-AUTO-003] TMDL semantic model generator

Owner: coding agent.
Next action: Iterate `scripts/generate_tmdl_model.py` and `scripts/generate_bim_pbip.py` to produce valid files that Power BI Desktop loads once PBIP preview is enabled.
Exit criteria: Generated PBIP passes Desktop load without fatal errors.

### P3 [BL-001] Build Power BI MVP (remains open)

Owner: human + coding agent.
Next action: after seed PBIP exists and opens, complete all five pages and save the accepted artifact. Do not mark complete until visual proof is captured.
Exit criteria: a local `.pbix` or `.pbip` report exists with all five demo pages and has been visually verified.

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
