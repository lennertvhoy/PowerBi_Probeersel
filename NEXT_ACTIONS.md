# NEXT_ACTIONS - Active Execution Queue

**Updated At:** 2026-05-15 15:10 CEST
**Execution Mode:** operating
**Max Items:** 10

## Active Work

### P1 [BL-AUTO-002] Create seed PBIP/PBIR project

Owner: coding agent + Windows GUI MCP agent.
Next action: open Power BI Desktop, enable PBIP/PBIR preview features if available, import `data/*.csv`, create relationships from `powerbi/model.md`, add DAX measures from `powerbi/measures.dax`, build one sample page, save as PBIP. Use `docs/demo/PBI_DESKTOP_BUILD_INSTRUCTIONS.md` as reference.
Exit criteria: Power BI Desktop opens the saved PBIP folder and renders the sample page. Folder is committed.

### P2 [BL-AUTO-003] TMDL semantic model generator

Owner: coding agent.
Next action: iterate `scripts/generate_tmdl_model.py` to produce valid TMDL that pbi-tools convert or Tabular Editor can consume without error. Validate against a seed PBIP once available.
Exit criteria: generated TMDL passes pbi-tools convert or Tabular Editor load without fatal errors.

### P3 [BL-001] Build Power BI MVP (remains open)

Owner: human + coding agent.
Next action: after seed PBIP exists and TMDL generator is validated, complete all five pages and save the accepted artifact. Do not mark complete until visual proof is captured.
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