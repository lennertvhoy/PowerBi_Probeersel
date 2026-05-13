# Build Steps

## Power BI Desktop

1. Open Power BI Desktop.
2. Import each CSV from `data/`:
   - `trainers.csv`
   - `courses.csv`
   - `sessions.csv`
   - `workload_entries.csv`
   - `evaluation_responses.csv`
   - `feedback_comments.csv`
   - `fairness_signals.csv`
3. Create the relationships from `powerbi/model.md`.
4. Add the DAX measures from `powerbi/measures.dax`.
5. Build the five pages from `powerbi/pages.md`.
6. Use `powerbi/theme.json` as the report theme.

## Demo Data Refresh

The current CSV files are handcrafted demo data. Keep trainer names fictional or
approved for demo use. Do not connect real Outlook or evaluation data until the
privacy rules in `docs/demo/PRIVACY_FAIRNESS.md` are accepted.

## Suggested MVP Acceptance

- The five pages exist in Power BI Desktop.
- Exchange Server visibly shows high preparation/nazorg and lower scores across multiple trainers.
- AI voor productiviteit visibly shows high score and high preparation.
- Jarno's innovation/dashboard work is visible as real workload.
- Lennert's new-topic and nazorg workload is visible.
- Fairness Signals are phrased as conversation prompts, not verdicts.
