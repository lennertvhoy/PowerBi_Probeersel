# BACKLOG - Strategic Roadmap

**Product:** Fair Workload & Evaluation Cockpit
**Execution Mode:** operating
**Updated At:** 2026-05-15

## Purpose

This backlog tracks medium-term work using stable backlog IDs.
Reference these IDs from `NEXT_ACTIONS.md`.

## NOW

- [BL-001] Build the first Power BI Desktop report from the prepared CSV data, model, measures and page specs. Status: partial; browser design preview exists + Windows GUI MCP agent proven, real `.pbix`/`.pbip` build in progress. **Not accepted until visual proof exists.**
- [BL-006] Convert the Power BI report into a versionable PBIP project if the local Power BI toolchain supports it. Status: partial; fake skeleton deleted by pbi-tools validation. Real seed PBIP pending GUI session.
- [BL-AUTO-001] Remote CI repair and Actions green gate. Status: complete; workflow passes on `ba19561`.
- [BL-AUTO-002] PBIP/PBIR seed project creation. Status: active; next step is GUI session to create real seed.
- [BL-AUTO-003] TMDL semantic model generator. Status: partial; skeleton created at `scripts/generate_tmdl_model.py`, needs validation against real PBIP.
- [BL-AUTO-004] Tabular Editor / pbi-tools evaluation with evidence. Status: tools installed and CLI verified; full integration test pending seed PBIP.
- [BL-AUTO-005] PBIR report JSON generator for five-page cockpit. Status: pending; depends on seed PBIP to understand PBIR structure.
- [BL-AUTO-006] Windows Power BI Desktop open/render/screenshot smoke. Status: pending; depends on accepted artifact.

## NEXT

- [BL-003] Add a simple Power App or Dataverse prototype for workload input.
- [BL-004] Add an Outlook import/enrichment path for calendar categories.
- [BL-005] Verify agent skill adapters in the actual CLIs the project will use.

## DONE

- [BL-002] Validate the demo story against the five-page flow and privacy/fairness framing. Evidence: `docs/evidence/001-powerbi-mvp-preview/`.
- **[NEW]** Windows GUI agent MCP control proven. Evidence: `docs/evidence/003-windows-gui-agent/`. OpenCode can now control Windows desktop apps (including Power BI Desktop) via pywinauto + pyautogui MCP server.

## LATER

- [BL-007] Replace fictive data with anonymized real sample data after privacy approval.

## WATCHLIST

- Queue bloat.
- Unverified claims.
- Dashboard being interpreted as trainer ranking instead of fairness/support signal.