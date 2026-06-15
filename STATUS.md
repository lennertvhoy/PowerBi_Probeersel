# PowerBi_Probeersel Status

**Updated At:** 2026-06-04 11:20 CEST
**Execution Mode:** operating
**Project State:** browser_preview_built
**Public URL:** not configured

## Snapshot

- Project is the **Fair Workload & Evaluation Cockpit** demo.
- Goal: make invisible trainer work visible so workload, support and evaluation are discussed more fairly.
- MVP uses fictive CSV data, Power BI model/page specs, Power App input spec, Outlook category mapping and an optional AI feedback-summary layer.
- Canonical Power Platform skills remain under `skills/power-platform/` with adapters for Claude, Codex, Kimi and Gemini.
- A browser-verifiable Power BI design preview exists under `demo-preview/` and mirrors the five intended report pages using the fictive CSV data.
- Evidence for the preview is logged under `docs/evidence/001-powerbi-mvp-preview/`.

## Immediate Priorities

1. Build the real Power BI report from `data/` and `powerbi/` when Power BI Desktop/PBIP tooling is available.
2. Use `demo-preview/` and `docs/demo/MANAGER_WALKTHROUGH.md` for the manager story rehearsal.
3. Keep privacy/fairness framing explicit before using any real trainer data.

## Active Blockers

- No `.pbix` or `.pbip` report has been built yet; Power BI Desktop requires Windows and an interactive desktop. A prior Windows VM attempt was interrupted and the VM no longer exists.
- No real Outlook, Power App or evaluation-system integration is connected yet.
- Browser preview now covers all five page specs; no remaining visual gaps.

## Notes

- Keep `STATUS.md` short.
- Use `PROJECT_STATE.yaml` for structured truth.
- Use `BACKLOG.md` backlog IDs inside `NEXT_ACTIONS.md` when active items are added.
- Prove runtime identity before accepting user-facing behavior.
