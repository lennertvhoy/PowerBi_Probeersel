# EVIDENCE_LOG.md

**Purpose:** Structured ledger of proof artifacts for user-facing claims.

## Entry Format

```yaml
- ID: EV-YYYY-MM-DD-001
  File: /absolute/path/to/artifact.png
  Title: short description
  Source/System: browser | api | test | log | screenshot
  Route/Page: optional route or URL
  Action: what was done
  Shows:
    - visible fact 1
    - visible fact 2
  Proves:
    - why the artifact matters
  Type: source-data | chatbot | gap | integration | docs-render-verification
  as_of: 2026-03-18T18:00:00+01:00
  Notes: optional context
```

## Guidance

- Link evidence to the specific claim it supports.
- Prefer durable artifact paths.
- Place saved artifacts under `docs/evidence/YYYY-MM-DD-<slug>/` when possible.
- Add timestamps for anything that may become stale.

## Entries

## EV-2026-05-13-001: Bootstrap scaffold and skill installation verification

```yaml
- ID: EV-2026-05-13-001
  File: command output in current Codex session
  Title: Bootstrap scaffold and skill installation verification
  Source/System: shell
  Route/Page: n/a
  Action: cloned source repositories, installed StateDD files, normalized skills to skills/power-platform, added adapter paths, removed nested .git folders and extracted source clone folders, initialized root git repo, inspected environment
  Shows:
    - only root .git remains under the workspace
    - nine SKILL.md files are present under skills/power-platform
    - Claude, Codex, and Kimi adapter paths point at the canonical skills
    - Gemini context files exist for workspace and extension use
    - root git repository is initialized on branch main with no commits yet
  Proves:
    - repository entered StateDD bootstrap mode
    - Power Platform skills were made available through platform-neutral canonical paths and common agent adapters
  Type: source-data
  as_of: 2026-05-13T12:25:00+02:00
  Notes: "Evidence is currently command-output based; no user-facing runtime exists yet."
```

## EV-2026-05-13-002: Demo baseline and bootstrap completion

```yaml
- ID: EV-2026-05-13-002
  File: repository files in current Codex session
  Title: Fair Workload & Evaluation Cockpit baseline
  Source/System: source-data
  Route/Page: n/a
  Action: added demo concept, fictive CSV data, Power BI model specs, DAX measures, page definitions, Power App input spec, Outlook mapping, AI summary concept, and updated StateDD mode to operating
  Shows:
    - product identity and MVP scope are recorded
    - demo data exists under data/
    - Power BI build instructions exist under docs/demo/BUILD_STEPS.md
    - report model and page specs exist under powerbi/
  Proves:
    - bootstrap product intake is complete enough to enter operating mode
    - next work can start from a concrete Power BI MVP backlog item
  Type: source-data
  as_of: 2026-05-13T12:45:00+02:00
  Notes: "No Power BI runtime artifact has been built or visually verified yet."
```

## EV-2026-05-13-003: Browser preview and manager walkthrough verification

```yaml
- ID: EV-2026-05-13-003
  File: /home/ff/Documents/Projects/PowerBi_Probeersel/docs/evidence/001-powerbi-mvp-preview/
  Title: Five-page browser preview for manager demo rehearsal
  Source/System: browser | shell
  Route/Page: http://127.0.0.1:4173/demo-preview/
  Action: served demo-preview with python3 -m http.server, captured five Playwright screenshots, ran CSV validation and state-doc validation
  Shows:
    - browser preview is explicitly labelled as Power BI design preview, not PBIX/PBIP
    - fictive data label is visible
    - all five intended report pages are represented
    - fairness signals are framed as conversation prompts, not trainer ranking
    - CSV schemas, relationships and numeric fields validate
  Proves:
    - BL-002 manager story can be rehearsed against a browser-verifiable artifact
    - BL-001 has a verified fallback preview but no accepted real Power BI artifact
  Type: docs-render-verification
  as_of: 2026-05-13T13:00:00+02:00
  Notes: "Power BI Desktop/PBIP tooling was not found; no .pbix or .pbip artifact exists in this slice."
```
