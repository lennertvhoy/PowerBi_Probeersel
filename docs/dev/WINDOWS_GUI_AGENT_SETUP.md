# Windows GUI Agent MCP Setup

Date: 2026-05-13

## Overview

This document describes the Windows GUI automation setup that enables
OpenCode to control Windows desktop applications (including Power BI Desktop)
through a local MCP server using pywinauto + pyautogui.

## Architecture

```
OpenCode (1.14.48, via Bun)
  └─ MCP local server: server.py (stdio transport)
       └─ Python venv: windows-gui-mcp-venv
            ├─ pywinauto (UIA backend)
            ├─ pyautogui (mouse/keyboard)
            ├─ mss (screenshots)
            ├─ pillow (image processing)
            └─ pynput (keyboard events)
```

## Installation

### Prerequisites (already installed)

- Python 3.12.10: `C:\Users\codex_pbi\AppData\Local\Programs\Python\Python312\python.exe`
- Git 2.54.0: `C:\Program Files\Git\cmd\git.exe`
- OpenCode 1.14.48: installed via Bun
- Power BI Desktop: `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`

### Python virtual environment

```powershell
cd "$env:USERPROFILE\tools"
mkdir windows-gui-mcp
& "C:\Users\codex_pbi\AppData\Local\Programs\Python\Python312\python.exe" -m venv windows-gui-mcp-venv
& "C:\Users\codex_pbi\tools\windows-gui-mcp-venv\Scripts\python.exe" -m pip install pywinauto pyautogui pillow mss pynput mcp
```

### MCP server

Location: `C:\Users\codex_pbi\tools\windows-gui-mcp\server.py`

Entry point: `& "C:\Users\codex_pbi\tools\windows-gui-mcp-venv\Scripts\python.exe" "C:\Users\codex_pbi\tools\windows-gui-mcp\server.py"`

## OpenCode Configuration

Config file: `%APPDATA%\opencode\opencode.jsonc`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "windows_gui": {
      "type": "local",
      "command": [
        "C:\\Users\\codex_pbi\\tools\\windows-gui-mcp-venv\\Scripts\\python.exe",
        "C:\\Users\\codex_pbi\\tools\\windows-gui-mcp\\server.py"
      ],
      "transport": "stdio",
      "enabled": true
    }
  }
}
```

## Available MCP Tools

| Tool | Params | Description |
|------|--------|-------------|
| `list_windows` | — | List all top-level windows (title, class, handle) |
| `focus_window` | title_pattern | Focus window by title substring match |
| `click_mouse` | x, y | Click at screen coordinates |
| `move_mouse` | x, y | Move mouse to coordinates |
| `type_text` | text | Type text via keyboard simulation |
| `press_key` | key | Press a single key |
| `hotkey` | keys[] | Press key combination |
| `screenshot` | output_path | Capture full-screen screenshot |
| `wait_for_window` | title_pattern, timeout | Wait for window by title |
| `get_ui_tree` | — | Dump UI automation tree |
| `get_mouse_position` | — | Get current mouse position |
| `launch_app` | path | Launch application by path |

## Known Limitations

1. **UIA child enumeration**: `children()` and `descendants()` throw on some pywinauto versions with newer Windows builds. `windows()` for top-level enumeration works reliably.
2. **No clipboard sharing**: The MCP server runs in a subprocess; clipboard access may need special permissions.
3. **Security context**: OpenCode and Power BI must run in the same user session (they do in this setup).
4. **Coordinate-based fallback**: When UIA semantic info is unavailable, screen-coordinate clicking works as a reliable fallback.

## Evidence

- Smoke test + Power BI control test: `docs/evidence/003-windows-gui-agent/`
- Screenshots: `powerbi-open.png`, `powerbi-menu-control.png`, `powerbi-type-test.png`, `notepad-gui-mcp-smoke.png`