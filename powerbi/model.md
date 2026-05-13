# Power BI Model

## Tables

| Table | Grain | Purpose |
| --- | --- | --- |
| `trainers` | One row per trainer | Trainer attributes and team |
| `courses` | One row per course/topic | Subject complexity and category |
| `sessions` | One row per training session | Delivered training context |
| `workload_entries` | One row per time entry | Workload by trainer, category, course and date |
| `evaluation_responses` | One row per session response aggregate | Scores and response counts |
| `feedback_comments` | One row per feedback comment/theme | Open feedback for AI/theme analysis |
| `fairness_signals` | One row per generated signal | Management discussion prompts |

## Relationships

Create these relationships:

| From | To | Cardinality | Direction |
| --- | --- | --- | --- |
| `sessions[TrainerId]` | `trainers[TrainerId]` | many-to-one | single |
| `sessions[CourseId]` | `courses[CourseId]` | many-to-one | single |
| `workload_entries[TrainerId]` | `trainers[TrainerId]` | many-to-one | single |
| `workload_entries[CourseId]` | `courses[CourseId]` | many-to-one | single |
| `evaluation_responses[SessionId]` | `sessions[SessionId]` | many-to-one | single |
| `feedback_comments[SessionId]` | `sessions[SessionId]` | many-to-one | single |
| `fairness_signals[TrainerId]` | `trainers[TrainerId]` | many-to-one | single, nullable |
| `fairness_signals[CourseId]` | `courses[CourseId]` | many-to-one | single, nullable |

## Date Handling

For the MVP, use the date columns directly. Later, add a proper `Date` table and
mark it as a date table.

## Key Design Choice

Do not make `Trainer` the only performance lens. Trainer-level visuals must be
paired with course, target audience, session type, response count and workload
context.
