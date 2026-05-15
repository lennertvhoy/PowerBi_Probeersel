# PowerBi_Probeersel Status

**Updated At:** 2026-05-15 15:10 CEST
**Execution Mode:** operating
**Project State:** automation_pipeline_defined

## Snapshot

- Project is the **Fair Workload & Evaluation Cockpit** demo.
- Goal: make invisible trainer work visible so workload, support and evaluation are discussed more fairly.
- MVP uses fictive CSV data, Power BI model/page specs, Power App input spec, Outlook category mapping and an optional AI feedback-summary layer.
- Canonical Power Platform skills remain under `skills/power-platform/` with adapters for Claude, Codex, Kimi and Gemini.
- A browser-verifiable Power BI design preview exists under `demo-preview/` and mirrors the five intended report pages using the fictive CSV data.
- Evidence for the preview is logged under `docs/evidence/001-powerbi-mvp-preview/`.
- **Windows GUI MCP agent is now operational** — Power BI Desktop can be launched, focused, interacted with via keyboard/mouse, and screenshotted from OpenCode.

## Immediate Priorities

1. Repair GitHub Actions green gate and keep it passing.
2. Define PBIP/PBIR/TMDL-first automation pipeline; reject GUI-only build as primary path.
3. Create seed PBIP/PBIR project in Power BI Desktop with preview features.
4. Use `demo-preview/` and `docs/demo/MANAGER_WALKTHROUGH.md` for the manager story rehearsal.
5. Keep privacy/fairness framing explicit before using any real trainer data.

## Active Blockers

- No real `.pbix` or `.pbip` report has been built yet. Prior fake skeleton was deleted by pbi-tools validation.
- PBIP/PBIR preview features not yet verified in Power BI Desktop.
- No real Outlook, Power App or evaluation-system integration is connected yet.
- Tabular Editor and pbi-tools installed but not yet integrated against a live model.

## Infrastructure Milestones

- **Windows GUI MCP agent**: Proven working (12/12 tests passed). OpenCode can now control Windows apps via pywinauto + pyautogui. See `docs/evidence/003-windows-gui-agent/`.
- **Power BI Desktop**: Found at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`, controllable via MCP.

## Notes

- Keep `STATUS.md` short.
- Use `PROJECT_STATE.yaml` for structured truth.
- Use `BACKLOG.md` backlog IDs inside `NEXT_ACTIONS.md` when active items are added.
- Prove runtime identity before accepting user-facing behavior.