# PowerBi_Probeersel Status

**Updated At:** 2026-05-13 14:30 CEST
**Execution Mode:** operating
**Project State:** gui_agent_enabled

## Snapshot

- Project is the **Fair Workload & Evaluation Cockpit** demo.
- Goal: make invisible trainer work visible so workload, support and evaluation are discussed more fairly.
- MVP uses fictive CSV data, Power BI model/page specs, Power App input spec, Outlook category mapping and an optional AI feedback-summary layer.
- Canonical Power Platform skills remain under `skills/power-platform/` with adapters for Claude, Codex, Kimi and Gemini.
- A browser-verifiable Power BI design preview exists under `demo-preview/` and mirrors the five intended report pages using the fictive CSV data.
- Evidence for the preview is logged under `docs/evidence/001-powerbi-mvp-preview/`.
- **Windows GUI MCP agent is now operational** — Power BI Desktop can be launched, focused, interacted with via keyboard/mouse, and screenshotted from OpenCode.

## Immediate Priorities

1. Build the real Power BI report from `data/` and `powerbi/` using the Windows GUI MCP agent.
2. Use `demo-preview/` and `docs/demo/MANAGER_WALKTHROUGH.md` for the manager story rehearsal.
3. Keep privacy/fairness framing explicit before using any real trainer data.

## Active Blockers

- No `.pbix` or `.pbip` report has been built yet.
- No real Outlook, Power App or evaluation-system integration is connected yet.

## Infrastructure Milestones

- **Windows GUI MCP agent**: Proven working (12/12 tests passed). OpenCode can now control Windows apps via pywinauto + pyautogui. See `docs/evidence/003-windows-gui-agent/`.
- **Power BI Desktop**: Found at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`, controllable via MCP.

## Notes

- Keep `STATUS.md` short.
- Use `PROJECT_STATE.yaml` for structured truth.
- Use `BACKLOG.md` backlog IDs inside `NEXT_ACTIONS.md` when active items are added.
- Prove runtime identity before accepting user-facing behavior.