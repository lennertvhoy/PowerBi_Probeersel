# PowerBi_Probeersel Status

**Updated At:** 2026-05-13 12:22 CEST
**Execution Mode:** operating
**Project State:** demo_mvp_defined
**Public URL:** not configured

## Snapshot

- Project is the **Fair Workload & Evaluation Cockpit** demo.
- Goal: make invisible trainer work visible so workload, support and evaluation are discussed more fairly.
- MVP uses fictive CSV data, Power BI model/page specs, Power App input spec, Outlook category mapping and an optional AI feedback-summary layer.
- Canonical Power Platform skills remain under `skills/power-platform/` with adapters for Claude, Codex, Kimi and Gemini.
- Bootstrap baseline is complete enough for operating mode; next work is building the Power BI report from the prepared assets.

## Immediate Priorities

1. Build the Power BI report from `data/` and `powerbi/`.
2. Validate the five report pages against the demo script.
3. Prepare one manager-ready walkthrough with privacy/fairness framing.

## Active Blockers

- No `.pbix` or `.pbip` report has been built yet.
- No real Outlook, Power App or evaluation-system integration is connected yet.

## Notes

- Keep `STATUS.md` short.
- Use `PROJECT_STATE.yaml` for structured truth.
- Use `BACKLOG.md` backlog IDs inside `NEXT_ACTIONS.md` when active items are added.
- Prove runtime identity before accepting user-facing behavior.
