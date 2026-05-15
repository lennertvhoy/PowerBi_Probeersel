# PowerBi_Probeersel Status

**Updated At:** 2026-05-15 17:05 CEST
**Execution Mode:** operating
**Project State:** pbip_seed_attempted

## Snapshot

- Project is the **Fair Workload & Evaluation Cockpit** demo.
- Goal: make invisible trainer work visible so workload, support and evaluation are discussed more fairly.
- MVP uses fictive CSV data, Power BI model/page specs, Power App input spec, Outlook category mapping and an optional AI feedback-summary layer.
- A browser-verifiable Power BI design preview exists under `demo-preview/`.
- **Windows GUI MCP agent proven operational** — see `docs/evidence/003-windows-gui-agent/`.
- **Programmatic PBIP generators created** — `scripts/generate_pbip.py` (TMDL) and `scripts/generate_bim_pbip.py` (TMSL) produce complete PBIP folder structures.
- **Power BI Desktop did not load the programmatic PBIP** — likely because the PBIP preview feature is not enabled; requires manual GUI step or registry change.

## Immediate Priorities

1. Enable PBIP preview feature in Power BI Desktop and verify programmatic PBIP opens.
2. Keep GitHub Actions green.
3. Complete the seed PBIP with one sample page once Desktop loads it.
4. Use `demo-preview/` for the manager story rehearsal.

## Active Blockers

- **PBIP preview feature not enabled** in Power BI Desktop. Programmatic PBIP folders are generated but Desktop opens them as "Untitled". Evidence: `docs/evidence/004-seed-pbip-pbir/`.
- No real `.pbix` or accepted `.pbip` report exists yet. BL-001 remains open.
- No real Outlook, Power App or evaluation-system integration is connected yet.

## Infrastructure Milestones

- **Windows GUI MCP agent**: Proven working (12/12 tests passed).
- **Power BI Desktop**: Version 2.153.1206.0 installed.
- **GitHub Actions**: Green on `aa3253a` (workflow "Validate Template Docs").
- **Tabular Editor 2.28.0** and **pbi-tools 1.2.0 Core** installed.

## Notes

- Keep `STATUS.md` short.
- Use `PROJECT_STATE.yaml` for structured truth.
- Use `BACKLOG.md` backlog IDs inside `NEXT_ACTIONS.md` when active items are added.
- Prove runtime identity before accepting user-facing behavior.
