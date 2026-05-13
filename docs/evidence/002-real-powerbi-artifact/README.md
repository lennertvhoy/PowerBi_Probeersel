# Evidence: Real Power BI Desktop Artifact

Date: 2026-05-13

## Scope

This evidence folder will contain the real Power BI Desktop report artifact
built by the Windows GUI MCP agent.

## Current Status

**Not yet built.** The Windows GUI MCP agent is proven operational (see
`docs/evidence/003-windows-gui-agent/`) and the next coding-agent session will
build the full `.pbix` using the workflow defined in
`prompts/next-agent-prompt.md`.

## Expected Contents (after build)

- `pbid-open-desktop.png` — Power BI Desktop open with report
- `page1-management-overview.png`
- `page2-trainer-workload.png`
- `page3-vak-categorie.png`
- `page4-evaluatieanalyse.png`
- `page5-fairness-signals.png`
- `file_metadata.txt` — PBIX path, size, last write time
- `pbix-sha256.txt` — SHA256 hash of the PBIX file
- `README.md` — build summary and limitations

## Interrupted Prior Attempts

If any files from the Fedora/SPICE/WinRM attempts exist here, they are preserved
in the `interrupted-fedora-spice-attempts/` subfolder for reference.

## Build Tooling

- Windows GUI MCP Server (pywinauto + pyautogui)
- OpenCode 1.14.48 with local MCP config
- Power BI Desktop v2.153+