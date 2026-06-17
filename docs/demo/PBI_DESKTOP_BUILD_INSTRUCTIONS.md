# Power BI Desktop — Manual Build Instructions
## Fair Workload & Evaluation Cockpit

Open this file on one screen, Power BI Desktop on the other.
Estimated time: 20–30 minutes.

---

## Step 0 — Launch Power BI Desktop

Open: `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`

Screenshot → `docs/evidence/002-real-powerbi-artifact/pbid-open-desktop.png`

---

## Step 1 — Import All 7 CSV Files

For each file: **Home → Get Data → Text/CSV → select file → Load**

| # | File | Table name (auto) |
|---|------|-------------------|
| 1 | `data\trainers.csv` | `trainers` |
| 2 | `data\courses.csv` | `courses` |
| 3 | `data\sessions.csv` | `sessions` |
| 4 | `data\workload_entries.csv` | `workload_entries` |
| 5 | `data\evaluation_responses.csv` | `evaluation_responses` |
| 6 | `data\feedback_comments.csv` | `feedback_comments` |
| 7 | `data\fairness_signals.csv` | `fairness_signals` |

Use first row as headers. All columns detected as Text or Whole Number is fine.
`Date` columns should be detected as Date.

---

## Step 2 — Create 8 Relationships

Go to **Model view** (left sidebar icon).

Drag or use **Manage Relationships → New**:

| From Table | From Column | To Table | To Column | Cardinality |
|---|---|---|---|---|
| `sessions` | `TrainerId` | `trainers` | `TrainerId` | Many:1 |
| `sessions` | `CourseId` | `courses` | `CourseId` | Many:1 |
| `workload_entries` | `TrainerId` | `trainers` | `TrainerId` | Many:1 |
| `workload_entries` | `CourseId` | `courses` | `CourseId` | Many:1 |
| `evaluation_responses` | `SessionId` | `sessions` | `SessionId` | Many:1 |
| `feedback_comments` | `SessionId` | `sessions` | `SessionId` | Many:1 |
| `fairness_signals` | `TrainerId` | `trainers` | `TrainerId` | Many:1 (nullable) |
| `fairness_signals` | `CourseId` | `courses` | `CourseId` | Many:1 (nullable) |

Switch back to **Report view**.

---

## Step 3 — Apply Theme

**File → Options and settings → Options → Current File → Theme → Import theme**

Select: `powerbi\theme.json`

This gives the blue/green/amber/red/purple color palette.

---

## Step 4 — Create DAX Measures

In the **Report view**, click on the report canvas, then use the **formula bar** at the top.

Create each measure in the **`workload_entries` table** (select it in the Fields pane first):

```
Total Workload Hours = SUM ( workload_entries[Hours] )

Contact Hours = CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Lesgeven" )

Preparation Hours = CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Voorbereiding" )

Aftercare Hours = CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Nazorg" )

Administration Hours = CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Administratie" )

Innovation Hours = CALCULATE ( [Total Workload Hours], workload_entries[Category] = "AI/innovatie" )

Prep Contact Ratio = DIVIDE ( [Preparation Hours], [Contact Hours] )

Invisible Work Hours = [Total Workload Hours] - [Contact Hours]

Visibility Gap % = DIVIDE ( [Invisible Work Hours], [Total Workload Hours] )

Average Evaluation Score = DIVIDE ( SUMX ( evaluation_responses, evaluation_responses[AverageScore] * evaluation_responses[ResponseCount] ), SUM ( evaluation_responses[ResponseCount] ) )

Total Responses = SUM ( evaluation_responses[ResponseCount] )

New Topic Sessions = CALCULATE ( COUNTROWS ( sessions ), sessions[IsNewTopic] = TRUE () )

Workload Score = VAR ComplexityLoad = AVERAGE ( courses[ComplexityScore] ) VAR PrepRatio = [Prep Contact Ratio] VAR Aftercare = [Aftercare Hours] RETURN [Total Workload Hours] + ( ComplexityLoad * 2 ) + ( PrepRatio * 5 ) + ( Aftercare * 0.5 )

Fairness Flag = VAR Gap = [Visibility Gap %] VAR Score = [Average Evaluation Score] VAR PrepRatio = [Prep Contact Ratio] RETURN SWITCH ( TRUE (), Gap >= 0.55, "Hoge werkdruk, lage zichtbaarheid", PrepRatio >= 0.8 && Score < 4.0, "Complex vak vraagt ondersteuning", [Aftercare Hours] >= 8, "Veel nazorg na sessie", [New Topic Sessions] >= 2, "Veel nieuwe onderwerpen", "Geen opvallend signaal" )
```

Also add a **calculated column** in the `sessions` table:
```
Full Name = RELATED(trainers[Trainer])
```

**Rename columns** for cleaner labels:
- `trainers[Trainer]` → `Trainer Naam`
- `courses[Course]` → `Opleiding`
- `courses[Domain]` → `Domein`

---

## Step 5 — Page 1: Management Overview

**Page name:** `Management Overview`
**Title text box:** `Team workload & kwaliteitsoverzicht`

Add these visuals:

1. **KPI Card** — `Total Workload Hours` → format: no decimal, suffix " uur", top-left
2. **KPI Card** — `Contact Hours` → suffix " uur", beside #1
3. **KPI Card** — `Prep Contact Ratio` → format as percentage (%×100), in row
4. **KPI Card** — `Average Evaluation Score` → 1 decimal, in row
5. **KPI Card** — `Total Responses` → suffix " reacties", in row
6. **Stacked Bar Chart** — Axis: `workload_entries[Category]`, Values: `workload_entries[Hours]`, below KPIs
7. **Bar Chart** — Axis: `courses[Course]`, Values: `workload_entries[Hours]`, Top N = 5 (Top 5 heaviest courses)
8. **Bar Chart** — Axis: `feedback_comments[Theme]`, Values: Count of `FeedbackId`, Top N = 5 (Top 5 feedback themes)
9. **Table** — Columns: `SignalType`, `Signal`, `Severity`, `RecommendedAction` (from fairness_signals)
10. **Text box** (bottom, italic): *Dit maakt onzichtbaar trainerwerk zichtbaar.*

---

## Step 6 — Page 2: Trainer Workload

**Page name:** `Trainer Workload`
**Title:** `Werkdruk per trainer`

1. **Stacked Bar** — Axis: `trainers[Trainer]`, Legend: `workload_entries[Category]`, Values: `workload_entries[Hours]`
2. **Clustered Bar** — Axis: `trainers[Trainer]`, Values: Contact Hours, Preparation Hours, Aftercare Hours, Administration Hours
3. **Line Chart** — Axis: `workload_entries[Date]`, Values: `workload_entries[Hours]`, Legend: `trainers[Trainer]`
4. **Table** — Columns: Trainer, New Topic Sessions, Total Workload, Visibility Gap %
5. **Text box**: *Dit is geen trainer-ranking. Toont de verdeling van type werk per trainer.*

---

## Step 7 — Page 3: Vak & Categorie Analyse

**Page name:** `Vak & Categorie Analyse`
**Title:** `Welke opleidingen vragen de meeste tijd?`

1. **Bar Chart** — Top 10 courses by `Preparation Hours`
2. **Scatter Chart** — X: `Prep Contact Ratio`, Y: `Average Evaluation Score`, Details: `courses[Course]`
3. **Matrix** — Rows: `courses[Course]`, Columns: `workload_entries[Category]`, Values: `workload_entries[Hours]`
4. **Bar Chart** — Axis: `courses[Course]`, Values: `Aftercare Hours`
5. **Text box**: *Exchange Server vraagt structureel veel voorbereiding en nazorg. Dat wijst eerder naar complexiteit, materiaal of planning dan naar een individueel trainerprobleem.*

---

## Step 8 — Page 4: Evaluatieanalyse

**Page name:** `Evaluatieanalyse`
**Title:** `Evaluaties eerlijker interpreteren`

1. **Bar Chart** — Axis: `courses[Course]`, Values: `Average Evaluation Score`
2. **Bar Chart** — Axis: `trainers[Trainer]`, Values: `Average Evaluation Score`, Tooltip: `Total Responses`
3. **Matrix** — Rows: `sessions[Audience]`, Columns: `sessions[SessionType]`, Values: `Average Evaluation Score`
4. **Line Chart** — Axis: `sessions[Date]`, Values: `Average Evaluation Score`
5. **Table** — Columns: `Theme`, `Sentiment`, `Comment` (from feedback_comments)
6. **Text box**: *Een score is pas bruikbaar met context: vak, doelgroep, sessietype, complexiteit, responses en workload.*

---

## Step 9 — Page 5: Fairness Signals

**Page name:** `Fairness Signals`
**Title:** `Signalen voor eerlijkere planning`

1. **Cards or Table** — Grouped by signal type, using `fairness_signals` data directly
   - Columns: SignalType, Severity, Signal, RecommendedAction
2. **Cards grouped by type:**
   - 🔴 Hoge werkdruk, lage zichtbaarheid
   - 🟡 Vak scoort laag bij meerdere trainers
   - 🟡 Veel nazorg na sessie
   - 🟡 Nieuwe cursus vraagt structureel meer voorbereiding
   - 🟢 Trainer draagt veel innovatie-uren
3. **Table** — Detail with RecommendedAction
4. **Text box** (prominent, bottom): *Signalen zijn startpunten voor gesprek, geen automatische oordelen.*
5. **Text box** (header/subtitle): *Fictieve data — geen echte Outlook-, Power App- of evaluatiesysteemintegratie*

---

## Step 10 — Required Labels (on all or specific pages)

Add as text boxes using **Insert → Text box**:

| Label | Where | Placement |
|---|---|---|
| `Fictieve data` | All pages (or at least first page prominently) | Top or bottom, clearly readable |
| `Gespreksinstrument, geen trainer-ranking` | Trainer Workload, Fairness Signals | Page header |
| `Dit maakt onzichtbaar trainerwerk zichtbaar` | Management Overview | Page header |
| `Geen echte Outlook-, Power App- of evaluatiesysteemintegratie` | All pages or footer | Subtitle/footer |

Font: Segoe UI, readable size.

---

## Step 11 — Save as PBIX

1. **File → Save As**
2. Navigate to: `C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel\powerbi\`
3. File name: `Fair_Workload_Evaluation_Cockpit.pbix`
4. Click **Save**

---

## Step 12 — Verify and Screenshot

Open the saved PBIX, navigate to each page, screenshot each one:

| Screenshot file | What to capture |
|---|---|
| `docs/evidence/002-real-powerbi-artifact/pbid-open-desktop.png` | PBI Desktop open with report |
| `docs/evidence/002-real-powerbi-artifact/page1-management-overview.png` | Page 1 full |
| `docs/evidence\002-real-powerbi-artifact\page2-trainer-workload.png` | Page 2 full |
| `docs/evidence\002-real-powerbi-artifact\page3-vak-categorie.png` | Page 3 full |
| `docs/evidence\002-real-powerbi-artifact\page4-evaluatieanalyse.png` | Page 4 full |
| `docs/evidence\002-real-powerbi-artifact\page5-fairness-signals.png` | Page 5 full |

---

## Step 13 — Metadata

In PowerShell:

```powershell
Get-Item .\powerbi\Fair_Workload_Evaluation_Cockpit.pbix | Format-List FullName,Length,LastWriteTime | Out-File .\docs\evidence\002-real-powerbi-artifact\file_metadata.txt -Encoding utf8

Get-FileHash .\powerbi\Fair_Workload_Evaluation_Cockpit.pbix -Algorithm SHA256 | Format-List | Out-File .\docs\evidence\002-real-powerbi-artifact\pbix-sha256.txt -Encoding utf8
```

---

## Step 14 — Update State Docs

- `STATUS.md`: Update project state
- `PROJECT_STATE.yaml`: Move BL-001 to complete
- `NEXT_ACTIONS.md`: Mark BL-001 done, move BL-006 to active
- `BACKLOG.md`: Move BL-001 to DONE
- `WORKLOG.md`: Log this build session
- `docs/evidence/002-real-powerbi-artifact/README.md`: Update with build summary and limitations

---

## Limitations to Document

- Fictive data only (no real trainer names or evaluations)
- No real Outlook integration
- No real Power App integration
- No real Dataverse integration
- No real evaluation-system integration
- Report is a demo artifact, not production-ready