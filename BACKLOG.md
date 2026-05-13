# BACKLOG - Strategic Roadmap

**Product:** Fair Workload & Evaluation Cockpit
**Execution Mode:** operating
**Updated At:** 2026-05-13

## Purpose

This backlog tracks medium-term work using stable backlog IDs.
Reference these IDs from `NEXT_ACTIONS.md`.

## NOW

- [BL-001] Build the first Power BI Desktop report from the prepared CSV data, model, measures and page specs. Status: partial; browser design preview exists + Windows GUI MCP agent proven, real `.pbix`/`.pbip` build in progress.
- [BL-006] Convert the Power BI report into a versionable PBIP project if the local Power BI toolchain supports it. Added after Windows GUI MCP agent setup.

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