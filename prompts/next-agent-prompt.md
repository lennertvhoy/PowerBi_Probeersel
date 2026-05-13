# Next Agent Prompt — BL-001: Build Real Power BI PBIX
# Issued by: CTO lane
# Date: 2026-05-13
# Status: ACTIVE — next coding agent session should execute this

You are the coding agent running directly inside the Windows 11 VM for the Fair Workload & Evaluation Cockpit project.

Repo:
- Windows path: C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel
- GitHub: https://github.com/lennertvhoy/PowerBi_Probeersel
- Branch: main
- Latest known pushed HEAD: 292bb75

Current truth:
- BL-002 browser-preview manager demo is accepted.
- Windows GUI automation / MCP setup is proven operational (12/12 tests passed).
- Power BI Desktop can be opened and controlled through the local Windows GUI MCP path.
- No .pbix exists yet.
- No .pbip exists yet.
- BL-001 remains PARTIAL until a real Power BI artifact exists and is visually checked.

Primary objective:
Use the proven Windows GUI MCP/computer-use tooling to build the real Power BI Desktop report artifact.

Required artifact:
- powerbi\Fair_Workload_Evaluation_Cockpit.pbix

Optional:
- .pbip only if Power BI Desktop supports it cleanly and it does not delay the .pbix.

Do not stop with "manual steps for Lennert." The GUI tools are proven. Build the report yourself unless a new precise blocker appears.

Critical rules:
- Work from latest origin/main.
- Do not commit secrets, credentials, installer files, temp files, or screenshots containing passwords.
- Do not mark BL-001 complete unless a real .pbix or .pbip exists, opens in Power BI Desktop, has five pages, and has screenshot evidence.
- If the GUI/MCP tool names differ from the previous handoff, inspect the available tools first. Do not invent tool names.
- Prefer robust keyboard/menu automation over fragile pixel-perfect clicks.
- Coordinate clicks are allowed as fallback because the previous handoff confirmed coordinate-based and keyboard automation are reliable.
- Do not waste time re-proving Notepad smoke tests unless the MCP server fails.

Known GUI/MCP setup from previous handoff:
- Python venv: C:\Users\codex_pbi\tools\windows-gui-mcp-venv
- MCP server: C:\Users\codex_pbi\tools\windows-gui-mcp\server.py
- OpenCode config: %APPDATA%\opencode\opencode.jsonc
- MCP server name: windows_gui
- Power BI Desktop control: previously passed 12/12
- Evidence from prior slice: docs\evidence\003-windows-gui-agent\

Available/expected GUI actions:
- launch_app, wait_for_window, focus_window, hotkey, type_text, click_mouse, screenshot, inspect UI tree

Phase 0 — sync and verify repo
Expected: HEAD at 292bb75 or newer, worktree clean.

Phase 1 — read project truth (all docs, CSVs, model, measures, pages, theme, preview screenshots)

Phase 2 — run validations:
python scripts\validate_demo_data.py
python scripts\check_state_docs.py
python scripts\check_state_docs.py --bootstrap-gate

Phase 3 — prepare evidence folder docs\evidence\002-real-powerbi-artifact\

Phase 4 — launch Power BI Desktop via MCP, capture pbid-open-desktop.png

Phase 5 — build the report per POWER_BI_DESKTOP_BUILD_CHECKLIST.md:
- Import 7 CSVs
- Create 8 relationships from powerbi\model.md
- Add all DAX measures from powerbi\measures.dax
- Apply theme from powerbi\theme.json

Phase 6 — create 5 pages from powerbi\pages.md using demo-preview\ as visual reference

Phase 7 — save powerbi\Fair_Workload_Evaluation_Cockpit.pbix

Phase 8 — capture 6 page screenshots + metadata (pbid-open-desktop.png, page1-5, file_metadata.txt, pbix-sha256.txt)

Phase 9 — update docs\evidence\002-real-powerbi-artifact\README.md

Phase 10 — update state docs (STATUS.md, PROJECT_STATE.yaml, NEXT_ACTIONS.md, BACKLOG.md, WORKLOG.md)

Phase 11 — final validation + commit + push

Final handoff must include:
1. PBIX exists (yes/no), path, size, SHA256
2. PBIP exists (yes/no)
3. All 6 screenshots captured
4. Validation results
5. BL-001 status: complete / partial / blocked (with reason)
6. Exact next step for Lennert