# Outlook Category Mapping

## Goal

Use Outlook calendar categories as low-friction input for workload analysis.
The MVP can import exported calendar data or manually prepared CSV rows.

## Suggested Categories

| Outlook Category | Workload Category | Example |
| --- | --- | --- |
| Training - Delivery | Lesgeven | Klassikale sessie, webinar, workshop |
| Training - Prep | Voorbereiding | Slides aanpassen, labo voorbereiden |
| Training - Aftercare | Nazorg | Vragen beantwoorden na opleiding |
| Training - Admin | Administratie | Evaluaties, aanwezigheden, planning |
| Training - Material | Materiaalontwikkeling | Nieuwe modules, oefeningen, labo's |
| Training - Meeting | Overleg | Klantafstemming, teammeeting |
| Training - Travel | Verplaatsing | Reistijd naar locatie |
| Training - Innovation | AI/innovatie | Demo's, automatisatie, Power BI-dashboard |

## Import Rule

If an Outlook item contains a course name in the subject, map it to `CourseId`.
If not, keep `CourseId` blank and let the Power App or import reviewer enrich it.

## AI Assist

AI may suggest:

- category
- course
- whether the item relates to a new topic
- short management summary

AI suggestions remain editable and should not be written as final truth without
human confirmation.
