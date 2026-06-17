# Power BI Automation Strategy

**Updated:** 2026-05-15
**Status:** draft — programmatic PBIP generators created; Desktop opening blocked by preview feature

## A. Dead Ends / Low-Value Paths (Rejected)

| Path | Why Rejected |
|------|-------------|
| Raw coordinate-only pyautogui full report construction | Fragile, resolution-dependent, unmaintainable. Proven unreliable in 12/12 GUI tests for simple navigation; completely unsuitable for building five pages with visuals, relationships, and measures. |
| WinRM launching WPF Desktop UI | Over-engineered remote-desktop indirection. Windows GUI MCP is already local and proven. |
| Fake PBIP skeletons missing valid report definitions | Prior `scripts/build_pbip.py` produced a folder with `dataModel.schema` but no valid PBIR report pages, no embedded data, and no opening proof. Committing it as "done" would be fake completeness. |
| Pretending browser preview equals PBIX | The `demo-preview/` HTML/CSS preview is a stable design reference (BL-002 accepted). It is **not** a Power BI artifact and does not satisfy BL-001. |
| Committing incomplete PBIP as accepted | Programmatic PBIP skeletons were generated (TMDL and TMSL) with full model definitions, but Power BI Desktop did not open them. They were moved to `scripts/experiments/` and must not be marked complete until Desktop loads them successfully. |

## B. Useful Building Blocks Already Proven

- **Windows GUI MCP agent**: Can launch, focus, screenshot, and keyboard-navigate Power BI Desktop. Evidence: `docs/evidence/003-windows-gui-agent/`.
- **Browser preview**: Stable five-page visual reference with real CSV data. Evidence: `docs/evidence/001-powerbi-mvp-preview/`.
- **CSV validation**: `scripts/validate_demo_data.py` deterministically checks schema, relationships, and numeric ranges.
- **Docs/state validation**: `scripts/check_state_docs.py` enforces hygiene.
- **Power BI Desktop**: Installed at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`, version `2.153.1206.0` (April 2026).
- **Repo specs**: `powerbi/model.md`, `powerbi/measures.dax`, `powerbi/pages.md`, `powerbi/theme.json` exist and are validated.

## C. Strategic Automation Target

Preferred pipeline architecture:

1. **Seed** a real PBIP/PBIR project using Power BI Desktop **once**.
2. **Store** the project in source control as PBIP/PBIR/TMDL, not just opaque PBIX.
3. **Generate/patch** semantic model definitions from repo specs (CSV schema + DAX measures).
4. **Generate/patch** report pages/visuals in PBIR JSON where feasible.
5. **Open** in Power BI Desktop to validate and render.
6. **Export/save** PBIX only as a release artifact, not as the primary source.
7. **CI** validates specs, schema, state docs, generated PBIP/PBIR structure, and browser preview.
8. **Windows GUI smoke test** validates Power BI Desktop can open the project and capture screenshots.

## D. Tools to Evaluate

| Tool | Role | Status |
|------|------|--------|
| Power BI Desktop PBIP/PBIR developer mode | Source-control-friendly project format. PBIR stores report structure as JSON files with public schemas. | **Partial** — programmatic generators created (TMDL + TMSL). Desktop did not load PBIP; likely requires preview feature enablement. See `docs/evidence/004-seed-pbip-pbir/`. |
| TMDL semantic model files | Human-readable tabular model definition. Supported by pbi-tools `convert` with `modelSerialization=Tmdl`. | **Pending** — need seed PBIP to extract and verify. |
| Tabular Editor 2.x free CLI | Connects to local Power BI Desktop model (`-L`), executes C# scripts for measures/calculated columns, exports BIM/TMDL. | **Installed and CLI-verified** (`2.28.0`). Full integration test pending seed PBIX. |
| pbi-tools CLI (Core) | Compiles PbixProj folders to PBIX/PBIT. Converts models to TMDL. Generates BIM. | **Installed and CLI-verified** (`1.2.0`). Requires .NET 8 runtime (installed). **Critical limitation:** `extract` action is absent in Core edition. `convert -overwrite` deletes invalid source folders. Full integration test pending seed PBIP. |
| DAX Studio | Model inspection and query validation. | **Not installed** — useful but not on critical path for pipeline automation. Can be added later. |
| ALM Toolkit | Compare/deploy models. | **Not evaluated** — only useful if multi-environment deployment is needed. |
| GitHub Actions + gh CLI | Remote closure gate for docs validation. | **Green** — `Validate Template Docs` passing on `ba19561`. |

## E. Recommended Roadmap

### BL-AUTO-001: Remote CI repair and Actions green gate
- **Status:** ✅ Complete. Workflow fixed in `ba19561`. Root cause: workflow expected bootstrap gate to fail because repo was assumed to be in bootstrap mode, but repo was already in operating mode.

### BL-AUTO-002: PBIP/PBIR seed project creation
- **Status:** Active. Programmatic generators created (`scripts/generate_pbip.py` for TMDL, `scripts/generate_bim_pbip.py` for TMSL). Generated folder moved to `scripts/experiments/pbip-tmsl-attempt/`.
- **Next action:** Enable PBIP preview feature in Power BI Desktop (File → Options → Preview features → "Power BI Project (.pbip) save option"). Then test whether the programmatic PBIP opens. If not, create a blank PBIP in Desktop and diff structures to find the gap.
- **Exit criteria:** Power BI Desktop opens the PBIP folder and loads the data model. Evidence screenshots captured. |

### BL-AUTO-003: TMDL semantic model generator
- **Status:** Partial. `scripts/generate_tmdl_model.py` produces draft TMDL. `scripts/generate_pbip.py` produces a full PBIP with TMDL and M partitions. `scripts/generate_bim_pbip.py` produces a full PBIP with TMSL (`model.bim`).
- **Next action:** Validate the generated PBIP against Power BI Desktop once PBIP preview is enabled. Iterate generators based on any loading errors.
- **Exit criteria:** Generated PBIP opens in Power BI Desktop without fatal errors. |

### BL-AUTO-004: Tabular Editor / pbi-tools evaluation with evidence
- **Status:** Partial — Tabular Editor CLI verified (`-?` works). pbi-tools Core verified but `extract` absent; `convert` safety issue discovered.
- **Next action:** Create seed PBIP in Desktop, then use Tabular Editor to connect to local Desktop and add a disposable measure; use pbi-tools `convert` (safely) to produce TMDL from the valid PBIP.
- **Exit criteria:** Evidence screenshots/logs captured in `docs/evidence/`.

### BL-AUTO-005: PBIR report JSON generator for five-page cockpit
- **Next action:** Generate PBIR JSON files for the five pages defined in `powerbi/pages.md`.
- **Exit criteria:** PBIR files are schema-valid and render correctly when opened in Power BI Desktop.

### BL-AUTO-006: Windows Power BI Desktop open/render/screenshot smoke
- **Next action:** Extend Windows GUI MCP scripts to open the PBIP project, wait for load, and capture per-page screenshots.
- **Exit criteria:** Automated smoke test produces evidence images for all five pages.

### BL-001: Real accepted artifact produced from the automated pipeline
- **Status:** Partial/open.
- **Exit criteria:** A `.pbix` or `.pbip` report exists with all five demo pages, has been visually verified via screenshot, and is reproducible from committed sources.

## Research Facts (Verified)

- PBIR is the current source-control-friendly report format, with report elements represented as JSON files and public schemas. ([Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format))
- PBIR/PBIP conversion still requires Power BI Desktop while the feature is in preview. ([Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview))
- TMDL is the right direction for semantic model automation. ([Microsoft Learn](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview))
- Power BI Desktop external tools can write to the semantic model through TOM. ([Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-external-tools))
- pbi-tools Core can compile PbixProj to PBIX/PBIT and convert to TMDL, but **`extract` is not available** in the Core edition. (Verified via `pbi-tools.core.exe --help` and direct experiment.)
- pbi-tools `convert -overwrite` on an invalid PbixProj folder **deletes the source folder**. The fake skeleton PBIP was destroyed during testing.
- Tabular Editor CLI can automate semantic-model changes, especially measures/calculated columns/model metadata. (Verified via `TabularEditor.exe -?`.)

## References

- Microsoft Learn: [Power BI Desktop projects (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- Microsoft Learn: [Create a Power BI report in enhanced report format](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format)
- Microsoft Learn: [Tabular Model Definition Language (TMDL)](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview)
- pbi-tools docs: <https://pbi.tools/>
- Tabular Editor docs: <https://docs.tabulareditor.com/>
