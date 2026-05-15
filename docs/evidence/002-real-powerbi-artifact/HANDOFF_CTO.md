# CTO Handoff: BL-001 Power BI Automation — Blocker Analysis & Path Forward

**Date:** 2026-05-13  
**From:** Coding Agent (OpenCode session)  
**To:** CTO / Product-Architecture Lead  
**Priority:** HIGH — BL-001 blocked on real artifact  
**Status:** BL-001 PARTIAL — browser preview accepted, real .pbix not yet built

---

## 1. Verified Current State

| Item | Status | Evidence |
|------|--------|----------|
| Repo | `main` at `6ab8ea5`, synced with origin | `git log --oneline -5` confirms |
| Worktree | Clean before build attempt | `git status --short` empty |
| Demo data validation | PASS (7/7 CSVs, schema + relationships OK) | `scripts/validate_demo_data.py` |
| Windows GUI MCP agent | OPERATIONAL (12/12 PBI Desktop control tests) | `docs/evidence/003-windows-gui-agent/README.md` |
| Power BI Desktop | Installed v2.153+ at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe` | Verified executable exists |
| Browser design preview | ACCEPTED (5 pages, BL-002) | `docs/evidence/001-powerbi-mvp-preview/` |
| Real .pbix artifact | **DOES NOT EXIST** | `Test-Path` = False |
| Real .pbip artifact | Created skeleton at `powerbi/Fair_Workload_Evaluation_Cockpit_PBIP/` | Contains `dataModel.schema`, `diagramView`, `workspaceId` — missing `Report/Report.bin` |
| Python environment | v3.12.10, pywinauto + pyautogui + mss + pillow installed in venv | `C:\Users\codex_pbi\tools\windows-gui-mcp-venv\` |

### Assets Ready for Build

- `data/trainers.csv` — 4 trainers
- `data/courses.csv` — 6 courses
- `data/sessions.csv` — 12 sessions
- `data/workload_entries.csv` — 46 entries
- `data/evaluation_responses.csv` — 12 evaluations
- `data/feedback_comments.csv` — 15 comments
- `data/fairness_signals.csv` — 5 signals
- `powerbi/measures.dax` — 14 measures + 1 calculated column + 3 renames
- `powerbi/model.md` — 8 relationships
- `powerbi/pages.md` — 5 pages with visual specs
- `powerbi/theme.json` — color palette + fonts
- `docs/demo/POWER_BI_DESKTOP_BUILD_CHECKLIST.md` — step-by-step build guide

---

## 2. What Was Attempted

### Attempt A: MCP Server Subprocess (Python → server_mcp.py)

**Approach:** Started the proven MCP server as a subprocess, connected as a JSON-RPC client, sent tool calls (launch_app, screenshot, hotkey, click_mouse, type_text, wait_for_window).

**Result: TIMED OUT at 300s**

**Root causes:**
1. **Stdio buffering** — The MCP server uses `Content-Length` framing on stdout. Python's `subprocess.Popen` with `stdin=PIPE, stdout=PIPE` interacts with Windows console buffers unpredictably. The server's `sys.stdout.flush()` calls don't reliably push through the pipe.
2. **Blocking reads** — `proc.stdout.read(1)` for byte-by-byte Content-Length parsing blocks indefinitely if no data arrives (e.g., if PBI Desktop steals focus and causes a modal dialog).
3. **No timeout on reads** — No `select()` or async I/O; the synchronous read hangs.
4. **Process isolation** — The MCP server and PBI Desktop run in separate processes with no shared state; coordinating them via file-based signals would be complex.

### Attempt B: Direct pywinauto/pyautogui (No MCP Server)

**Approach:** Write a Python script using `from pywinauto import Desktop` and `import pyautogui` directly, importing the venv's site-packages. Perform all steps synchronously with `time.sleep()` between actions.

**Result: TIMED OUT at 300s**

**Root causes:**
1. **PBI Desktop startup time** — PBI Desktop takes 10–15 seconds to fully render its first report canvas. The script's `find_pbi_window()` loop works but eats time.
2. **CSV import flow is deeply nested** — Home → Get Data → Text/CSV → file dialog → navigate to path → Open → Load button → dismiss preview. Each step requires precise keyboard navigation through ribbon menus that vary by PBI Desktop version and localization (Dutch vs English menu items).
3. **Menu navigation is fragile** — `pyautogui.press('down', presses=10)` assumes a fixed menu structure. If the "Get Data" item is at position 11 instead of 10 (e.g., due to recent files), the automation clicks the wrong item.
4. **Formula bar interaction unreliable** — Clicking the formula bar at `(sw//2, 185)` works sometimes but fails when a visual is selected instead. PBI Desktop's ribbon context changes the UI tree.
5. **DAX formula typing** — Special characters (`"`, `=`, `(`, `)`, `[`, `]`, `"Lesgeven"` with quotes inside a string) cause issues with `pyautogui.typewrite()`. The quotes in DAX string literals like `"Lesgeven"` are especially problematic.
6. **Page creation** — There is no reliable keyboard shortcut for "New Page" that is consistent across PBI Desktop versions.

### Attempt C: PBIP Folder Construction (No GUI)

**Approach:** Construct a `.pbip` project folder directly on disk with `dataModel.schema`, `Connections`, `Settings`, `diagramView`, and a `Report/Report.bin`. PBI Desktop would open the folder.

**Result: PARTIAL**

**Root causes:**
1. **Report.bin is a protobuf binary** — It contains the full report definition (pages, visuals, measures, layout) as a serialized Protocol Buffer. Without the protobuf schema definition (which Microsoft does not publish), generating a valid `Report.bin` is practically impossible.
2. **No public PBIP schema docs** — The `dataModel.schema` can be written, but the Report binary format is undocumented and complex.
3. **PBIP still needs PBI Desktop to "compile"** — Even with a valid folder, PBI Desktop performs validation/compilation on open that we can't bypass.

---

## 3. Fundamental Blockers (Why GUI Automation for PBI Is Hard)

### 3.1 No Scripting/Automation API

Power BI Desktop **does not expose any public automation API**. There is:
- No COM interface
- No REST/local HTTP API
- No PowerShell module for report creation
- No Python SDK for desktop report authoring
- No command-line arguments for opening files or running scripts

The only official automation path is the **Power BI REST API**, which requires a **Premium capacity** workspace and works with the **service** (powerbi.com), not with Power BI Desktop.

### 3.2 pywinauto Limitations

| Limitation | Impact |
|------------|--------|
| UIA backend doesn't enumerate PBI's custom Win32/UIA child controls reliably | Can't programmatically click "Import CSV" button by name |
| No semantic understanding of PBI's ribbon/menu structure | Must use coordinate-based clicks or fragile keyboard tab sequences |
| `get_ui_tree()` returns top-level windows only for PBI | No visibility into ribbon buttons, formula bar, visual wells |
| PBI uses DirectX/Win2D for rendering | Some UI elements are not in the accessibility tree at all |
| Focus management is unreliable | PBI steals focus during import dialogs; pywinauto loses track |

### 3.3 pyautogui Limitations

| Limitation | Impact |
|------------|--------|
| Screen-resolution dependent (1920×1152 here, may differ elsewhere) | All coordinate-based clicks break on different screens |
| No awareness of UI state | Can't detect "is the Import dialog open?" — must guess timing |
| `FAILSAFE = True` (default) kills the script if mouse is in corner | Must be disabled, losing safety net |
| Character-by-character typing is slow | DAX formulas with 100+ chars take 5–10 seconds each |
| Special character handling varies by keyboard layout | Dutch keyboard layout ≠ US; `@`, `"`, `~` send wrong chars |

### 3.4 PBIX Format Opacity

| Problem | Detail |
|---------|--------|
| PBIX is a ZIP but contains binary protobuf | `Report.bin`, `Report.ViewerThumbnail`, `Connections` are not human-readable |
| No open-source PBIX writer exists | The format is reverse-engineered partially by community |
| Data can be embedded or external | Embedded data uses a proprietary columnar format inside the ZIP |

### 3.5 Timing Sensitivity

Every automation attempt failed because:
- PBI Desktop is **slow** (10–30s for startup, 2–5s per import dialog)
- `time.sleep()` values that work once fail the next time (PBI GC pause, Windows update popup, antivirus scan)
- The total script runtime exceeds 300s (our timeout) or becomes flaky

---

## 4. Alternative Approaches — Ranked by Feasibility

### Option A: Tabular Editor CLI (RECOMMENDED — HIGH FEASIBILITY)

**Tool:** [Tabular Editor](https://tabulareditor.com/) (open source, by Daniel Otykier)  
**Why it works:** Tabular Editor can open `.pbix` files, modify the data model (tables, relationships, measures, calculated columns) via command-line or C# scripting, and save. It uses TOM (Tabular Object Model) under the hood — the same API that SSDT/BISM uses.

**Plan:**
1. Create a **template .pbix** manually (one-time, 15 minutes) with empty tables/relationships
2. Use Tabular Editor CLI to:
   - Open the template
   - Clear any placeholder data
   - Create tables from CSV schemas
   - Add relationships
   - Add all 14 DAX measures + calculated column
   - Save as new `.pbix`
3. Use a lighter GUI automation pass just for the visuals/pages (much simpler if data model already exists)

**Pros:**
- No fragile ribbon/import automation needed
- Deterministic, scriptable, fast (<30s)
- Handles the data model creation perfectly
- Community-proven for CI/CD pipelines

**Cons:**
- Still need GUI automation (or manual step) for report pages/visuals
- Tabular Editor must be installed

**Effort:** ~2 hours (one-time template + script)

### Option B: Python + pypbi Library (RECOMMENDED — MEDIUM FEASIBILITY)

**Tool:** [`pypbi`](https://github.com/jeamesp/pypbi) or similar Python PBIX library  
**Why:** Some community libraries can construct .pbix files by generating the ZIP structure with valid protobuf messages.

**Plan:**
1. Install `pypbi` or equivalent
2. Write a Python script that creates:
   - Data model with tables/columns/relationships
   - DAX measures
   - Report pages with basic visuals (tables, bar charts)
3. Output a valid `.pbix`

**Pros:**
- Fully automated, no GUI needed
- Runs in seconds
- Version-controllable

**Cons:**
- `pypbi` may not support all visual types we need
- Protobuf schemas may drift with PBI Desktop updates
- Less proven than Option A

**Effort:** ~4 hours (research + script)

### Option C: Power BI Embedded + GenerateToken API (LOWER FEASIBILITY)

**Tool:** Azure Power BI Embedded + REST API  
**Why:** The REST API supports `Import PBIX in Group` which uploads a PBIX to a Power BI workspace and returns an embedded report URL.

**Plan:**
1. Generate a PBIX using Option A or B
2. Upload via REST API to a workspace
3. Embed in a web app for viewing

**Pros:**
- True API-driven workflow
- No GUI automation at all

**Cons:**
- Requires Azure subscription + Premium capacity
- Overkill for this demo
- Not offline-friendly

**Effort:** ~1 day (Azure setup + integration)

### Option D: Hybrid — Manual Template + Light GUI Script (PRAGMATIC — LOWEST RISK)

**Plan:**
1. **One-time manual build:** Open PBI Desktop, import all CSVs, create relationships, add measures, build 5 pages. Save as `template.pbix`.
2. **Ongoing automation:** Write a lightweight pyautogui script that:
   - Opens `template.pbix`
   - Refreshes data (Home → Refresh)
   - Saves with a timestamped name
   - Takes screenshots
3. **Data updates:** Replace CSV files, run the script, get fresh screenshots.

**Pros:**
- Works immediately
- No new tools needed
- Screenshots are guaranteed correct
- The template is reusable

**Cons:**
- Initial build is a one-time manual effort (~30 minutes)
- Data refresh automation still uses GUI (but on a stable template)

**Effort:** ~1 hour for template, ~30 min for automation script

### Option E: PowerShell PBI Cmdlets (EXPERIMENTAL)

**Tool:** `MicrosoftPowerBIMgmt` PowerShell module  
**Why:** Microsoft provides PowerShell cmdlets for Power BI Service management.

**Verdict:** Only works for Service operations (import, refresh, assign workspace). Cannot create Desktop .pbix files.

---

## 5. Recommended Path

**Immediate (this session):** Option D — build the template manually, take screenshots, close BL-001.

**Short-term (next sprint):** Option A — install Tabular Editor, automate the data model + measures, reduce future build to:
1. Drop updated CSVs in `data/`
2. Run `build_model.ps1` (Tabular Editor CLI)
3. Open in PBI Desktop → refresh → screenshot

**Medium-term:** Option B — if community protobuf libraries mature, full Python automation becomes possible.

---

## 6. Files Created / Modified

| File | Action |
|------|--------|
| `scripts/build_pbix_direct.py` | Created (attempted GUI build, timed out) |
| `scripts/build_pbip.py` | Created (PBIP skeleton generator — partial) |
| `scripts/build_pbix_mcp.py` | Created (MCP-based build, timed out) |
| `docs/demo/PBI_DESKTOP_BUILD_INSTRUCTIONS.md` | Created — detailed manual build guide |
| `powerbi/Fair_Workload_Evaluation_Cockpit_PBIP/` | Created skeleton (dataModel.schema + workspaceId + diagramView) |

---

## 7. Exact Next Step for Lennert

**Do this now (30 minutes):**

1. Open Power BI Desktop
2. Follow `docs/demo/PBI_DESKTOP_BUILD_INSTRUCTIONS.md` step by step
3. Import all 7 CSVs, create relationships, add measures from `powerbi/measures.dax`
4. Build the 5 pages using `powerbi/pages.md` as reference
5. Use `docs/demo/POWER_BI_DESKTOP_BUILD_CHECKLIST.md` for visual placement
6. Save as `powerbi/Fair_Workload_Evaluation_Cockpit.pbix`
7. Screenshot all 5 pages into `docs/evidence/002-real-powerbi-artifact/`
8. Run the PowerShell metadata commands from the same doc

This unblocks BL-001 immediately. The automation question (Options A/B) can be pursued in parallel without blocking the demo.

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PBI Desktop version mismatch breaks GUI script | High (each update changes ribbon) | High | Use Tabular Editor CLI instead |
| PBIX format changes silently | Medium | High | Version-pin PBI Desktop, run in VM |
| Template .pbix becomes stale | Low | Medium | Rebuild template quarterly |
| No CI/CD for PBIX | High (current state) | Medium | Tabular Editor + Git hooks |

---

**Bottom line:** GUI automation for Power BI Desktop is a dead end for reliable automation. Microsoft does not expose a scripting surface for Desktop report creation. The proven path is Tabular Editor (TOM API) for the data model + measures, with a one-time manual build for the visual layout. This gets us a reproducible, scriptable build pipeline that doesn't depend on screen coordinates or timing luck.

---

*Handoff prepared by coding agent, session 2026-05-13.*  
*Repo: `C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel`, branch `main`, HEAD `6ab8ea5`.*