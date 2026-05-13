# Browser Preview

This folder contains a browser-verifiable Power BI design preview for the
Fair Workload & Evaluation Cockpit.

It is not a `.pbix` or `.pbip` file. It exists because Power BI Desktop/PBIP
tooling was not available in the Linux coding environment. The preview reads the
same fictive CSV files from `data/` and mirrors the five intended Power BI
pages:

1. Management Overview
2. Trainer Workload
3. Vak & Categorie Analyse
4. Evaluatieanalyse
5. Fairness Signals

Run locally from the repo root:

```bash
python3 -m http.server 4173
```

Then open:

```text
http://127.0.0.1:4173/demo-preview/
```
