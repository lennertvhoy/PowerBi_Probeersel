# Fair Workload & Evaluation Cockpit — Power BI Build Guide

This guide walks through building the real Power BI `.pbix` report from the CSV data
and specifications in this repo. Open this file on one screen and Power BI Desktop
on the other.

---

## Prerequisites

- Power BI Desktop v2.153 (or later) installed and running
- This repo cloned at `C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel`
- All seven CSV files present in `data\` folder

---

## Step 1 — Import All CSV Tables

For each file: **Home → Get Data → Text/CSV → select file → Load** (not Transform).

| # | File | Table name (auto-detected) |
|---|------|-----------------------------|
| 1 | `data\trainers.csv` | `trainers` |
| 2 | `data\courses.csv` | `courses` |
| 3 | `data\sessions.csv` | `sessions` |
| 4 | `data\workload_entries.csv` | `workload_entries` |
| 5 | `data\evaluation_responses.csv` | `evaluation_responses` |
| 6 | `data\feedback_comments.csv` | `feedback_comments` |
| 7 | `data\fairness_signals.csv` | `fairness_signals` |

Use first row as headers. All columns should be detected as Text or Whole Number.
`Date` in `sessions.csv` and `workload_entries.csv` should be detected as Date.

---

## Step 2 — Create Relationships

Go to **Model view** (left sidebar icon). Create these relationships:

| From Table | From Column | To Table | To Column | Cardinality | Cross-filter |
|------------|-------------|----------|-----------|-------------|--------------|
| `sessions` | `TrainerId` | `trainers` | `TrainerId` | Many:1 | Single |
| `sessions` | `CourseId` | `courses` | `CourseId` | Many:1 | Single |
| `workload_entries` | `TrainerId` | `trainers` | `TrainerId` | Many:1 | Single |
| `workload_entries` | `CourseId` | `courses` | `CourseId` | Many:1 | Single |
| `evaluation_responses` | `SessionId` | `sessions` | `SessionId` | Many:1 | Single |
| `feedback_comments` | `SessionId` | `sessions` | `SessionId` | Many:1 | Single |
| `fairness_signals` | `TrainerId` | `trainers` | `TrainerId` | Many:1 | Single (nullable) |
| `fairness_signals` | `CourseId` | `courses` | `CourseId` | Many:1 | Single (nullable) |

The TrainerId/CourseId in `fairness_signals` may be blank — that's expected.

---

## Step 3 — Import Theme

**File → Options and settings → Options → Current File → Theme → Import theme**
Select `powerbi\theme.json`.

This gives the report its color palette (blue/green/amber/red/purple) and fonts.

---

## Step 4 — Create DAX Measures

Open **DAX Editor** or use **New Measure** in the `workload_entries` table.
Paste each measure from the block below. Name them exactly as shown.

```dax
Total Workload Hours =
SUM ( workload_entries[Hours] )

Contact Hours =
CALCULATE (
    [Total Workload Hours],
    workload_entries[Category] = "Lesgeven"
)

Preparation Hours =
CALCULATE (
    [Total Workload Hours],
    workload_entries[Category] = "Voorbereiding"
)

Aftercare Hours =
CALCULATE (
    [Total Workload Hours],
    workload_entries[Category] = "Nazorg"
)

Administration Hours =
CALCULATE (
    [Total Workload Hours],
    workload_entries[Category] = "Administratie"
)

Innovation Hours =
CALCULATE (
    [Total Workload Hours],
    workload_entries[Category] = "AI/innovatie"
)

Prep Contact Ratio =
DIVIDE ( [Preparation Hours], [Contact Hours] )

Invisible Work Hours =
[Total Workload Hours] - [Contact Hours]

Visibility Gap % =
DIVIDE ( [Invisible Work Hours], [Total Workload Hours] )

Average Evaluation Score =
DIVIDE (
    SUMX ( evaluation_responses, evaluation_responses[AverageScore] * evaluation_responses[ResponseCount] ),
    SUM ( evaluation_responses[ResponseCount] )
)

Total Responses =
SUM ( evaluation_responses[ResponseCount] )

New Topic Sessions =
CALCULATE (
    COUNTROWS ( sessions ),
    sessions[IsNewTopic] = TRUE ()
)

Workload Score =
VAR ComplexityLoad =
    AVERAGE ( courses[ComplexityScore] )
VAR PrepRatio =
    [Prep Contact Ratio]
VAR Aftercare =
    [Aftercare Hours]
RETURN
    [Total Workload Hours]
        + ( ComplexityLoad * 2 )
        + ( PrepRatio * 5 )
        + ( Aftercare * 0.5 )

Fairness Flag =
VAR Gap = [Visibility Gap %]
VAR Score = [Average Evaluation Score]
VAR PrepRatio = [Prep Contact Ratio]
RETURN
    SWITCH (
        TRUE (),
        Gap >= 0.55, "Hoge werkdruk, lage zichtbaarheid",
        PrepRatio >= 0.8 && Score < 4.0, "Complex vak vraagt ondersteuning",
        [Aftercare Hours] >= 8, "Veel nazorg na sessie",
        [New Topic Sessions] >= 2, "Veel nieuwe onderwerpen",
        "Geen opvallend signaal"
    )
```

**Also create** a calculated column in `sessions` table:
```dax
Full Name = RELATED(trainers[Trainer])
```

And rename these columns for cleaner labels (optional but recommended):
- `trainers[Trainer]` → rename to `Trainer Naam`
- `courses[Course]` → rename to `Opleiding`
- `courses[Domain]` → rename to `Domein`

---

## Step 5 — Page 1: Management Overview

**Page name:** `Management Overview`
**Title text box:** `Team workload & kwaliteitsoverzicht`

### Visuals:

1. **KPI Card** — Total Workload Hours
   - Format: no decimal, suffix " uur"
   - Place in top-left

2. **KPI Card** — Contact Hours
   - Suffix " uur"
   - Place beside Total Workload

3. **KPI Card** — Prep/Contact Ratio
   - Display as percentage (multiply by 100 in format)
   - Place in row

4. **KPI Card** — Average Evaluation Score
   - Format: 1 decimal
   - Place in row

5. **KPI Card** — Total Responses
   - Suffix " reacties"
   - Place in row

6. **Stacked Bar Chart** — Hours by Category
   - Axis: `workload_entries[Category]`
   - Values: `workload_entries[Hours]`
   - Legend: Category
   - Place below KPI row

7. **Bar Chart** — Top 5 Heaviest Courses
   - Axis: `courses[Course]` (top 5 by workload)
   - Values: `workload_entries[Hours]`
   - Filter: Top N = 5

8. **Bar Chart** — Top 5 Feedback Themes
   - Axis: `feedback_comments[Theme]`
   - Values: Count of FeedbackId
   - Top N = 5

9. **Card / Table** — Current Fairness Signals
   - Table with `fairness_signals.csv` fields
   - Columns: SignalType, Signal, Severity, RecommendedAction
   - Or use Cards grouped by Severity

10. **Text box** (bottom, italic, smaller font):
    > *Dit maakt onzichtbaar trainerwerk zichtbaar.*

---

## Step 6 — Page 2: Trainer Workload

**Page name:** `Trainer Workload`
**Title:** `Werkdruk per trainer`

### Visuals:

1. **Stacked Bar** — Workload mix per trainer
   - Axis: `trainers[Trainer]`
   - Legend: `workload_entries[Category]`
   - Values: `workload_entries[Hours]`

2. **Clustered Bar** — Contact vs Prep vs Nazorg vs Admin
   - Axis: `trainers[Trainer]`
   - Values: Contact Hours, Preparation Hours, Aftercare Hours, Administration Hours

3. **Line Chart** — Workload by month
   - Axis: Date (from workload_entries)
   - Values: `workload_entries[Hours]`
   - Legend: `trainers[Trainer]`

4. **Table** — Trainer context table
   - Columns: Trainer, New Topic Sessions, Total Workload, Visibility Gap %
   - Or use matrix

5. **Text box** (visible disclaimer):
   > *Dit is geen trainer-ranking. Toont de verdeling van type werk per trainer.*

---

## Step 7 — Page 3: Vak & Categorie Analyse

**Page name:** `Vak & Categorie Analyse`
**Title:** `Welke opleidingen vragen de meeste tijd?`

### Visuals:

1. **Bar Chart** — Top 10 courses by preparation hours
   - Axis: `courses[Course]`
   - Values: `Preparation Hours`
   - Top N = 10

2. **Scatter Chart** — Prep/Contact ratio vs evaluation score
   - X axis: `Prep Contact Ratio`
   - Y axis: `Average Evaluation Score`
   - Details: `courses[Course]`

3. **Matrix** — Course × Work Category
   - Rows: `courses[Course]`
   - Columns: `workload_entries[Category]`
   - Values: `workload_entries[Hours]`

4. **Bar Chart** — Aftercare hours by course
   - Axis: `courses[Course]`
   - Values: `Aftercare Hours`

5. **Text box** (note):
   > *Exchange Server vraagt structureel veel voorbereiding en nazorg. Dat wijst eerder naar complexiteit, materiaal of planning dan naar een individueel trainerprobleem.*

---

## Step 8 — Page 4: Evaluatieanalyse

**Page name:** `Evaluatieanalyse`
**Title:** `Evaluaties eerlijker interpreteren`

### Visuals:

1. **Bar Chart** — Average score by course
   - Axis: `courses[Course]`
   - Values: `Average Evaluation Score`

2. **Bar/Column Chart** — Average score by trainer + response count
   - Axis: `trainers[Trainer]`
   - Values: `Average Evaluation Score`
   - Tooltip: `Total Responses`

3. **Matrix or Table** — Average score by audience and session type
   - Rows: `sessions[Audience]`
   - Columns: `sessions[SessionType]`
   - Values: `Average Evaluation Score`

4. **Line Chart** — Trend over time
   - Axis: `sessions[Date]`
   - Values: `Average Evaluation Score`

5. **Table** — Feedback theme table
   - Columns: Theme, Sentiment, Comment (sample)
   - From `feedback_comments.csv`

6. **Text box**:
   > *Een score is pas bruikbaar met context: vak, doelgroep, sessietype, complexiteit, responses en workload.*

---

## Step 9 — Page 5: Fairness Signals

**Page name:** `Fairness Signals`
**Title:** `Signalen voor eerlijkere planning`

### Visuals:

1. **Cards or Table** — Grouped by signal type
   - Use `fairness_signals.csv` data directly
   - Columns: SignalType, Severity, Signal, RecommendedAction

2. **Cards grouped by:**
   - 🔴 Hoge werkdruk, lage zichtbaarheid
   - 🟡 Vak scoort laag bij meerdere trainers
   - 🟡 Veel nazorg na sessie
   - 🟡 Nieuwe cursus vraagt structureel meer voorbereiding
   - 🟢 Trainer draagt veel innovatie-uren

3. **Table** — Detail with recommended management action
   - Show all signals with their RecommendedAction

4. **Text box** (prominent, bottom):
   > *Signalen zijn startpunten voor gesprek, geen automatische oordelen.*

5. **Text box** (header or subtitle):
   > *Fictieve data — geen echte Outlook-, Power App- of evaluatiesysteemintegratie*

---

## Step 10 — Required Labels and Disclaimers

Add these as **text boxes** on the indicated pages in a clearly visible way:

| Label | Page(s) | Placement |
|-------|---------|-----------|
| `Fictieve data` | **All pages** (or at least first page prominently) | Top or bottom, clearly readable |
| `Gespreksinstrument, geen trainer-ranking` | Trainer Workload, Fairness Signals | Page header or prominent text box |
| `Dit maakt onzichtbaar trainerwerk zichtbaar` | Management Overview | Page header or prominent text box |
| `Geen echte Outlook-, Power App- of evaluatiesysteemintegratie` | All pages or footer | Subtitle or footer |

Use **Insert → Text box** for each. Format in Segoe UI, readable size.

---

## Step 11 — Save

1. **File → Save As**
2. Navigate to: `C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel\powerbi\`
3. File name: `Fair_Workload_Evaluation_Cockpit.pbix`
4. Click **Save**

If Power BI offers `.pbip` project format, you may also save that to
`powerbi\Fair_Workload_Evaluation_Cockpit_PBIP\` but the `.pbix` is priority.

---

## Step 12 — Screenshots

Take the following screenshots (Snipping Tool works well):

| File | What to capture |
|------|-----------------|
| `docs/evidence/002-real-powerbi-artifact/pbid-open-desktop.png` | Power BI Desktop open with report |
| `docs/evidence/002-real-powerbi-artifact/page1-management-overview.png` | Page 1 in full |
| `docs/evidence/002-real-powerbi-artifact/page2-trainer-workload.png` | Page 2 in full |
| `docs/evidence/002-real-powerbi-artifact/page3-vak-categorie.png` | Page 3 in full |
| `docs/evidence/002-real-powerbi-artifact/page4-evaluatieanalyse.png` | Page 4 in full |
| `docs/evidence/002-real-powerbi-artifact/page5-fairness-signals.png` | Page 5 in full |

---

## Build Tips

- Use the browser preview screenshots in `docs/evidence/001-powerbi-mvp-preview/` as visual reference
- Don't chase pixel-perfect fidelity — functional and faithful to specs is the goal
- If a visual doesn't render as expected, check that the right fields are in the right wells
- The Fairness Signals page can use the direct CSV table since those signals are pre-generated
- Color scheme: blue primary (#2563EB), green (#059669), amber (#F59E0B), red (#DC2626), purple (#7C3AED)