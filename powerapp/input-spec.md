# Power App Input Spec

## Purpose

A lightweight input app for trainers to register non-classroom workload when
Outlook categories are not precise enough.

## Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `TrainerId` | lookup/user | yes | Current trainer |
| `Date` | date | yes | Work date |
| `CourseId` | lookup | optional | Required when tied to a course |
| `Category` | choice | yes | Matches workload categories |
| `Hours` | decimal | yes | Quarter-hour precision |
| `Description` | text | optional | Short explanation |
| `IsNewTopic` | boolean | optional | Marks new learning/curriculum work |
| `Source` | choice | yes | Power App, Outlook, Import |

## Categories

- Lesgeven
- Voorbereiding
- Nazorg
- Administratie
- Materiaalontwikkeling
- Overleg
- Verplaatsing
- AI/innovatie

## UX Rules

- Default to the signed-in trainer.
- Keep entry under 30 seconds.
- Allow duplication of a previous entry.
- Show a weekly summary before submit.
- Avoid language that implies monitoring.

## Dataverse Candidate Tables

If the MVP becomes a Power Platform app, create:

- `fwc_trainer`
- `fwc_course`
- `fwc_session`
- `fwc_workloadentry`
- `fwc_evaluationresponse`
- `fwc_feedbackcomment`
- `fwc_fairnesssignal`
