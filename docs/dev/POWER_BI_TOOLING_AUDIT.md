# Power BI Tooling Audit

**Updated:** 2026-05-14
**Auditor:** coding agent (Windows 11 VM)

## Summary

| Tool | Installed | Version | Path | Pipeline Role |
|------|-----------|---------|------|---------------|
| Power BI Desktop | Yes | 2.153.1206.0 | `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe` | Seed creator, validator, renderer |
| Tabular Editor 2 | Yes (portable) | 2.28.0 | `C:\Users\codex_pbi\tools\tabular-editor-2\TabularEditor.exe` | Semantic model automation |
| pbi-tools (Core) | Yes (portable) | 1.2.0 | `C:\Users\codex_pbi\tools\pbi-tools\pbi-tools.core.exe` | Compile PbixProj → PBIX/PBIT, convert to TMDL, generate BIM |
| DAX Studio | No | — | — | Optional query/model inspection |
| .NET 8 Runtime | Yes | 8.0.27 | `C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.27` | pbi-tools dependency |

---

## 1. Power BI Desktop

- **License:** Free (Microsoft)
- **Install path:** `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`
- **Version:** 2.153.1206.0 (April 2026)
- **PBIP support:** Available via preview features (to be verified)
- **PBIR support:** Available via enhanced report format preview (to be verified)
- **What it can automate:** Nothing headless. Must be launched via GUI or subprocess. Can open `.pbip` folders and `.pbix` files.
- **What it cannot automate:** No CLI for build/import/measure creation. All report construction requires UI interaction or external tools writing to the model.
- **Command tested:** `powershell -Command "(Get-ItemProperty '...').VersionInfo.FileVersion"`
- **Result:** `2.153.1206.0`
- **Pipeline role:** Seed PBIP creation (one-time), validation opener, screenshot smoke target.

## 2. Tabular Editor 2

- **License:** MIT (free/open source)
- **Install path:** `C:\Users\codex_pbi\tools\tabular-editor-2\TabularEditor.exe`
- **Version:** 2.28.0 (build 2.28.9557.26801)
- **Download source:** <https://github.com/TabularEditor/TabularEditor/releases/download/2.28.0/TabularEditor.Portable.zip>
- **What it can automate:**
  - Connect to local Power BI Desktop instance (`-L` / `-LOCAL`)
  - Execute C# scripts against the model (`-S`)
  - Save model as BIM, Folder, or TMDL (`-B`, `-F`, `-TMDL`)
  - Apply Best Practice Analyzer rules (`-A`, `-AX`)
  - Deploy to SSAS/Power BI Service (`-D`)
- **What it cannot automate:**
  - Report visuals/pages (that's PBIR territory)
  - Direct PBIX creation (only model metadata)
- **Command tested:** `TabularEditor.exe -?`
- **Result:** Help displayed successfully; CLI interface confirmed.
- **Pipeline role:** Semantic model automation — add measures, calculated columns, relationships, and export to TMDL.

## 3. pbi-tools

- **License:** AGPL-3.0 (free/open source)
- **Install path:** `C:\Users\codex_pbi\tools\pbi-tools\pbi-tools.core.exe`
- **Version:** 1.2.0 (TOM 19.87.7)
- **Download source:** <https://github.com/pbi-tools/pbi-tools/releases/download/1.2.0/pbi-tools.core.1.2.0_win-x64.zip>
- **Dependencies:** .NET 8 Runtime (installed 8.0.27 during audit)
- **What it can automate:**
  - `compile` — Generate PBIX/PBIT from PbixProj folder sources
  - `convert` — Convert PBIX/PBIP to TMDL or legacy PbixProj format
    - `export-data` — Dump table data from live Power BI Desktop to CSV
  - `info` — List installed Power BI Desktop versions and running instances
- **What it cannot automate:**
  - Cannot compile a data model directly to PBIX (only to PBIT; PBIX is thin-report only)
  - Cannot create visuals/pages (PBIR/TMDL only)
  - Requires .NET 8 runtime; .NET 10 alone is insufficient
- **Critical finding:** `extract` action is **not available** in the Core edition. Only `compile`, `convert`, `deploy`, `export-data`, `generate-bim`, `git`, `info`, `init` are present. Extraction requires the Desktop edition or manual PBIP save from Power BI Desktop.
- **Safety warning:** `convert` with `-overwrite` on an invalid/incomplete PbixProj folder **deletes the source folder**. The fake skeleton at `powerbi/Fair_Workload_Evaluation_Cockpit_PBIP/` was destroyed by this command during testing.
- **Command tested:** `pbi-tools.core.exe --help` (after .NET 8 runtime install)
- **Result:** Help displayed successfully. Verified `compile`, `convert`, `generate-bim` actions exist. Confirmed `extract` is absent.
- **Pipeline role:** Compile PbixProj sources to PBIX/PBIT, convert models to TMDL, generate BIM for CI validation. Extract is not available in Core edition; PBIP creation must come from Power BI Desktop.

## 4. DAX Studio

- **License:** Free (GPL-3.0)
- **Install path:** Not installed
- **Version available:** 3.5.2 via `winget install DaxStudio.DaxStudio`
- **What it can automate:**
  - Connect to local Power BI Desktop / SSAS
  - Run DAX queries and view results
  - Export query results
  - Inspect model metadata
- **What it cannot automate:**
  - No CLI automation for model changes
  - No PBIP/PBIR generation
- **Command tested:** `winget search "DAX Studio"` (installation skipped)
- **Result:** Found in winget repository.
- **Pipeline role:** Optional debugging/inspection tool. Not on critical path.

## 5. PBIP / PBIR Preview Feature Check

- **Power BI Desktop version:** 2.153.1206.0
- **Expected availability:** PBIP has been GA since 2023; PBIR (enhanced report format) is in preview as of 2024–2025.
- **Verification method:** Open Power BI Desktop → File → Options → Preview features → look for "Store reports using enhanced report format (PBIR)" and "Power BI Project (PBIP) save option".
- **Status:** **Not yet verified** — requires GUI session.

---

## Installation Log

```powershell
# Tabular Editor 2 (portable, no admin)
curl -L -o te2.zip https://github.com/TabularEditor/TabularEditor/releases/download/2.28.0/TabularEditor.Portable.zip
unzip -o te2.zip -d tabular-editor-2

# pbi-tools (portable, no admin)
curl -L -o pbi-tools.zip https://github.com/pbi-tools/pbi-tools/releases/download/1.2.0/pbi-tools.core.1.2.0_win-x64.zip
unzip -o pbi-tools.zip -d pbi-tools

# .NET 8 Runtime (required for pbi-tools; winget install, silent)
winget install Microsoft.DotNet.Runtime.8 --silent --accept-source-agreements --accept-package-agreements
```

## Next Steps

1. Verify PBIP/PBIR preview features are enabled in Power BI Desktop.
2. Create a seed PBIP from Power BI Desktop and test `pbi-tools convert` to TMDL.
3. Connect Tabular Editor to the seed PBIP's local model and script a measure addition.
4. Document exact commands that work in `scripts/` for reproducibility.
