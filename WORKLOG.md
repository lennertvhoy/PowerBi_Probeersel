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
  - Verified UI tree discovery working.
- Control level assessment: full keyboard + mouse + screenshot control; partial UIA semantic control.
- Added BL-006 for PBIP research.
- Updated STATUS.md, PROJECT_STATE.yaml, NEXT_ACTIONS.md, BACKLOG.md.
- Created `docs/evidence/003-windows-gui-agent/` with README.md + 4 evidence screenshots.

## 2026-05-14 – 2026-05-15 (session 3 — CI repair and Power BI automation pipeline)

- Verified repo sync: `main` at `ba19561`, clean with origin.
- Confirmed GitHub Actions "Validate Template Docs" is green on `ba19561` (run 25855938462, conclusion: success).
- Updated `docs/dev/POWER_BI_AUTOMATION_STRATEGY.md` with PBIP/PBIR/TMDL-first architecture, dead-end rejection, and automation roadmap (BL-AUTO-001 through BL-AUTO-006).
- Installed and verified Tabular Editor 2.28.0 portable (`C:\Users\codex_pbi\tools\tabular-editor-2\TabularEditor.exe`). CLI help confirmed.
- Installed and verified pbi-tools 1.2.0 Core (`C:\Users\codex_pbi\tools\pbi-tools\pbi-tools.core.exe`).
- Discovered critical pbi-tools Core limitation: `extract` action is absent. Only `compile`, `convert`, `deploy`, `export-data`, `generate-bim`, `git`, `info`, `init` are available.
- Discovered pbi-tools safety issue: `convert -overwrite` on an invalid PbixProj folder deletes the source folder. The fake skeleton at `powerbi/Fair_Workload_Evaluation_Cockpit_PBIP/` was destroyed during testing.
- Moved dead-end scripts (`build_pbix_direct.py`, `build_pbix_mcp.py`, `build_pbip.py`) to `scripts/experiments/` with warning comments.
- Created `scripts/powerbi_pipeline_status.py` to report pipeline health: PBIX/PBIP existence, CSV validation, measures/theme checks, tooling installation, next missing step.
- Created `scripts/generate_tmdl_model.py` — draft TMDL generator that parses CSV schema, `powerbi/model.md` relationships, and `powerbi/measures.dax` to produce a TMDL folder structure under `powerbi/tmdl_generated/`.
- Ran TMDL generator successfully: 7 tables, 8 relationships, 14 measures, 1 calculated column.
- Updated `docs/dev/POWER_BI_TOOLING_AUDIT.md` with corrected pbi-tools findings and safety warnings.
- Updated STATUS.md, PROJECT_STATE.yaml, NEXT_ACTIONS.md, BACKLOG.md to reflect automation lane and honest blocker state.
- Local validations passed: `validate_demo_data.py`, `check_state_docs.py`, `check_state_docs.py --bootstrap-gate`, `powerbi_pipeline_status.py`.

## 2026-05-15 (session 4 — PBIP seed creation attempt)

- Synced repo: `main` at `aa3253a`, equals `origin/main`.
- Verified GitHub Actions green on `aa3253a` (run 25919931093, conclusion: success).
- Installed GitHub CLI (`gh`) via winget for future CI verification.
- Resolved untracked files: deleted obsolete `scripts/ci_diagnostic.py` and `scripts/ci_trace.py`; added `python3.cmd` and `python3w.cmd` to `.gitignore`.
- Created `scripts/generate_pbip.py` — programmatic TMDL-based PBIP generator with M-expression CSV partitions, relationships, measures, calculated columns.
- Created `scripts/generate_bim_pbip.py` — programmatic TMSL-based PBIP generator (`model.bim`) with the same content.
- Moved the generated PBIP folder to `scripts/experiments/pbip-tmsl-attempt/` after verification failed.
- Attempted to open programmatic PBIP in Power BI Desktop via multiple methods:
  - Command-line argument launch
  - Explorer `start` command
  - File > Open dialog (Ctrl+O)
- Result: Power BI Desktop always opened as "Untitled - Power BI Desktop", never loading the PBIP.
- Root cause hypothesis: PBIP is still in preview and requires the preview feature to be explicitly enabled in Power BI Desktop Options. Microsoft docs confirm this.
- Evidence folder created: `docs/evidence/004-seed-pbip-pbir/README.md` with full attempt log, screenshots list, and next-step recommendation.
- Updated `scripts/powerbi_pipeline_status.py` to detect PBIP experiment folder and report preview-feature blocker.
- Updated `STATUS.md`, `PROJECT_STATE.yaml`, `NEXT_ACTIONS.md`, `BACKLOG.md`, `WORKLOG.md`.
- Updated `docs/dev/POWER_BI_AUTOMATION_STRATEGY.md` and `docs/dev/POWER_BI_TOOLING_AUDIT.md` with PBIP generation findings.
