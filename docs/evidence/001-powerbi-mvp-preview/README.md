# Evidence: Power BI MVP Browser Preview

Date: 2026-05-13

## Scope

This evidence folder covers the browser-verifiable design preview for the Fair
Workload & Evaluation Cockpit. It supports manager-demo rehearsal for BL-002 and
partial progress on BL-001.

## Runtime Identity

- Repo path: `/home/ff/Documents/Projects/PowerBi_Probeersel`
- Branch at verification: `main`
- Source HEAD at screenshot capture: `0319bff`
- Runtime: `python3 -m http.server 4173`
- URL: `http://127.0.0.1:4173/demo-preview/`
- Artifact rebuilt in this slice: yes, as `demo-preview/`

## Real Power BI Artifact

No `.pbix` or `.pbip` exists in this slice. Power BI Desktop/PBIP tooling was
not found in the Linux coding environment. See
`powerbi-tooling-probe.txt`.

## Screenshots

- `01-management-overview.png`
- `02-trainer-workload.png`
- `03-vak-categorie-analyse.png`
- `04-evaluatieanalyse.png`
- `05-fairness-signals.png`

## Validation Outputs

- `csv-validation.txt`
- `state-doc-validation.txt`
- `bootstrap-gate-validation.txt`
- `powerbi-tooling-probe.txt`

## Walkthrough Result

The preview supports the required manager story:

- contact hours alone are not the full workload
- preparation, nazorg, administratie, materiaalontwikkeling and innovation work
  are visible
- evaluation scores are shown with context and response counts
- lower scores are framed as signals for investigation, not trainer verdicts
- fairness signals are conversation aids, not automatic judgements
- fictive data is clearly labelled
