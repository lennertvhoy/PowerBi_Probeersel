# WORKLOG

**Purpose:** Append-only history for completed work.

Use this file for dated session notes, verification summaries, and references to evidence artifacts.

## 2026-05-13

- Initialized `/home/ff/Documents/Projects/PowerBi_Probeersel` with the StateDD template in bootstrap mode.
- Cloned `DanielKerridge/claude-code-power-platform-skills` and `lennertvhoy/StateDD_Template`.
- Removed `.git` folders from both cloned source directories.
- Installed Power Platform skill folders into `.claude/skills/`.
- Initialized a fresh root Git repository on branch `main`.
- Ran initial bootstrap inspection of system, repo structure, skills installation, Git metadata, and active listeners.
- Normalized Power Platform skills into canonical `skills/power-platform/`.
- Replaced Claude-only skill copy with symlink adapters for `.claude/skills/`, `.codex/skills/`, and `.kimi/plugins/`.
- Added Gemini CLI context through root `GEMINI.md` and `.gemini/extensions/power-platform-skills`.
- Added Codex UI metadata files under each skill's `agents/openai.yaml`.
- Removed extracted source clone directories after their contents were installed into canonical repo paths.
- Completed product bootstrap for the Fair Workload & Evaluation Cockpit.
- Added fictive trainer/course/session/workload/evaluation/feedback/fairness CSV data under `data/`.
- Added Power BI model, DAX measures, report page specs and theme under `powerbi/`.
- Added Power App input spec, Outlook category mapping, AI summary concept and manager demo docs.
- Switched repo contract from bootstrap mode to operating mode.
- Built a browser-verifiable Power BI design preview under `demo-preview/` because Power BI Desktop/PBIP tooling was not available in the Linux environment.
- Added `docs/demo/MANAGER_WALKTHROUGH.md` with 3-minute and 8-minute manager walkthroughs plus privacy/fairness answers.
- Added `scripts/validate_demo_data.py` and verified the fictive CSV schemas, relationships and numeric fields.
- Captured five preview screenshots and validation outputs under `docs/evidence/001-powerbi-mvp-preview/`.
- Marked BL-002 complete and BL-001 partial/open because no real `.pbix` or `.pbip` exists yet.

## 2026-05-13 (session 2 — Windows GUI Agent Enablement)

- Investigated host system: Windows VM with Python 3.12.10, Git 2.54.0, OpenCode 1.14.48 (via Bun).
- Installed system packages: pywinauto, pyautogui, pillow, mss, pynput, mcp in a dedicated venv at `C:\Users\codex_pbi\tools\windows-gui-mcp-venv`.
- Built custom Windows GUI MCP server (`tools/windows-gui-mcp/server.py`) exposing 12 tools: list_windows, focus_window, click_mouse, move_mouse, type_text, press_key, hotkey, screenshot, wait_for_window, get_ui_tree, get_mouse_position, launch_app.
- Configured OpenCode MCP in `%APPDATA%\opencode\opencode.jsonc` with local MCP server entry.
- Proved Notepad automation: opened Notepad, typed text, saved file, captured screenshot (7/8 smoke tests passed).
- Proved Power BI Desktop automation (12/12 tests passed):
  - Launched Power BI Desktop from Python subprocess.
  - Found and focused "Untitled - Power BI Desktop" window via UIA.
  - Captured screenshots of open state, File menu interaction, and keyboard input.
  - Verified keyboard navigation (Alt+F, Ctrl+G, type, Esc).
  - Verified mouse click on ribbon area.
  - Confirmed UI tree discovery working.
- Control level assessment: full keyboard + mouse + screenshot control; partial UIA semantic control.
- Added BL-006 for PBIP research.
- Updated STATUS.md, PROJECT_STATE.yaml, NEXT_ACTIONS.md, BACKLOG.md.
- Created `docs/evidence/003-windows-gui-agent/` with README.md + 4 evidence screenshots.