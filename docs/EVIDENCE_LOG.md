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
