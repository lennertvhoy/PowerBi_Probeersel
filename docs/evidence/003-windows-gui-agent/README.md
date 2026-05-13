# Evidence: Windows GUI Agent MCP Control

Date: 2026-05-13

## Scope

This evidence proves that a Python-based MCP server can control Windows desktop applications
(including Power BI Desktop) through pywinauto + pyautogui, making it available to OpenCode
as an MCP tool.

## Runtime Identity

- Repo path: `C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel`
- Branch at verification: `main`
- HEAD: `0e549a5` (synced with origin/main)
- MCP Server: `C:\Users\codex_pbi\tools\windows-gui-mcp\server.py`
- Python venv: `C:\Users\codex_pbi\tools\windows-gui-mcp-venv`
- OpenCode version: 1.14.48 (installed via Bun)

## Installed Tooling

| Package | Version / Path |
|---------|---------------|
| Python 3.12.10 | `C:\Users\codex_pbi\AppData\Local\Programs\Python\Python312\python.exe` |
| pywinauto | latest via pip in venv |
| pyautogui | latest via pip in venv |
| pillow | latest via pip in venv |
| mss | latest via pip in venv |
| pynput | latest via pip in venv |
| MCP server | Custom: `server.py` (stdio protocol, MCP 2024-11-05) |

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `list_windows` | List all top-level Windows with title/class/handle |
| `focus_window` | Focus a window by title substring match |
| `click_mouse` | Click at screen coordinates |
| `move_mouse` | Move mouse to coordinates |
| `type_text` | Type text via keyboard simulation |
| `press_key` | Press a single key |
| `hotkey` | Press a key combination (e.g., Alt+F) |
| `screenshot` | Capture full-screen screenshot to file |
| `wait_for_window` | Wait for a window by title (with timeout) |
| `get_ui_tree` | Dump UI automation tree (pywinauto UIA backend) |
| `get_mouse_position` | Get current mouse position |
| `launch_app` | Launch an application by path |

## OpenCode MCP Config

File: `%APPDATA%\opencode\opencode.jsonc`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "windows_gui": {
      "type": "local",
      "command": ["C:\\Users\\codex_pbi\\tools\\windows-gui-mcp-venv\\Scripts\\python.exe", "C:\\Users\\codex_pbi\\tools\\windows-gui-mcp\\server.py"],
      "transport": "stdio",
      "enabled": true
    }
  }
}
```

## Proof Results

### Notepad Smoke Test (Phase 4 — safe app)
- **list_windows**: PASS — 6 windows found
- **focus_notepad**: PASS — opened and focused Untitled - Notepad
- **type_text**: PASS — typed "Windows GUI MCP smoke test for Fair Workload Cockpit"
- **screenshot**: PASS — saved to `notepad-gui-mcp-smoke.png`
- **mouse_control**: PASS — moved and returned
- **powerbi_exists**: PASS — found at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`
- **hotkey**: PASS — Alt+F4 sent
- **Result**: 7/8 passed (ui_tree had API compatibility issue, fixed in v2)

### Power BI Desktop Control Test (Phase 5)
- **pbi_path**: PASS — executable found
- **launch_pbi**: PASS — launched successfully
- **discover_windows**: PASS — found "Untitled - Power BI Desktop" in window list
- **focus_pbi**: PASS — focused via title match
- **screenshot_pbi**: PASS — `powerbi-open.png`
- **keyboard_nav**: PASS — Alt+F opened File menu, Esc closed it
- **click_ribbon**: PASS — clicked at ribbon area
- **screenshot_menu**: PASS — `powerbi-menu-control.png`
- **type_in_pbi**: PASS — Ctrl+G opened Go To, typed "Test", Esc closed
- **screenshot_type**: PASS — `powerbi-type-test.png`
- **ui_tree**: PASS — listed top-level windows including "Untitled - Power BI Desktop"
- **close_pbi**: PASS — closed cleanly
- **Result**: 12/12 passed

## Control Level Assessment

| Level | Status |
|-------|--------|
| UIA semantic control | Partial (works for window listing, limited for child controls) |
| Screenshot/coordinate control | Full |
| Keyboard-only control | Full |
| Mouse + keyboard combo | Full |
| Overall verdict | **Reliable mixed-mode automation** |

## Screenshots

- `notepad-gui-mcp-smoke.png` — Notepad with typed text
- `powerbi-open.png` — Power BI Desktop open
- `powerbi-menu-control.png` — File menu interaction
- `powerbi-type-test.png` — Go To dialog with typed text

## Next Steps

- Use this MCP server from OpenCode for full Power BI report building
- Consider fixing `get_ui_tree` with `pywinauto.Application().connect()` for deeper UIA control
- Build PBIX via hybrid approach (coordinate clicks + keyboard + menu navigation)