#!/usr/bin/env python3
"""Validate the fictive demo CSV files used by the report preview."""

from __future__ import annotations

import csv
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED = {
    "trainers.csv": ["TrainerId", "Trainer", "Role", "Team"],
    "courses.csv": ["CourseId", "Course", "Domain", "ComplexityScore", "DefaultSessionType"],
    "sessions.csv": [
        "SessionId",
        "Date",
        "TrainerId",
        "CourseId",
        "Audience",
        "SessionType",
        "ContactHours",
        "IsNewTopic",
        "Location",
    ],
    "workload_entries.csv": [
        "EntryId",
        "Date",
        "TrainerId",
        "CourseId",
        "SessionId",
        "Category",
        "Hours",
        "Source",
        "Description",
    ],
    "evaluation_responses.csv": ["EvaluationId", "SessionId", "AverageScore", "ResponseCount", "Nps", "MainIssue"],
    "feedback_comments.csv": ["FeedbackId", "SessionId", "Theme", "Sentiment", "Comment"],
    "fairness_signals.csv": [
        "SignalId",
        "SignalDate",
        "SignalType",
        "TrainerId",
        "CourseId",
        "Severity",
        "Signal",
        "RecommendedAction",
    ],
}


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    path = DATA / name
    if not path.exists():
        raise ValueError(f"{path}: missing")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def require_reference(rows: list[dict[str, str]], key: str, valid: set[str], label: str) -> list[str]:
    errors: list[str] = []
    for row in rows:
        value = row.get(key, "")
        if value and value not in valid:
            errors.append(f"{label}: {key}={value} is not in referenced table")
    return errors


def main() -> int:
    errors: list[str] = []
    loaded: dict[str, list[dict[str, str]]] = {}

    for name, expected_columns in EXPECTED.items():
        try:
            columns, rows = read_csv(name)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        loaded[name] = rows
        if columns != expected_columns:
            errors.append(f"data/{name}: columns {columns} != expected {expected_columns}")
        if not rows:
            errors.append(f"data/{name}: no data rows")
        print(f"data/{name}: OK schema, {len(rows)} rows")

    if errors:
        print("\nFAILED before relationship checks")
        for error in errors:
            print(f"- {error}")
        return 1

    trainer_ids = {row["TrainerId"] for row in loaded["trainers.csv"]}
    course_ids = {row["CourseId"] for row in loaded["courses.csv"]}
    session_ids = {row["SessionId"] for row in loaded["sessions.csv"]}

    errors += require_reference(loaded["sessions.csv"], "TrainerId", trainer_ids, "sessions")
    errors += require_reference(loaded["sessions.csv"], "CourseId", course_ids, "sessions")
    errors += require_reference(loaded["workload_entries.csv"], "TrainerId", trainer_ids, "workload_entries")
    errors += require_reference(loaded["workload_entries.csv"], "CourseId", course_ids, "workload_entries")
    errors += require_reference(loaded["workload_entries.csv"], "SessionId", session_ids, "workload_entries")
    errors += require_reference(loaded["evaluation_responses.csv"], "SessionId", session_ids, "evaluation_responses")
    errors += require_reference(loaded["feedback_comments.csv"], "SessionId", session_ids, "feedback_comments")
    errors += require_reference(loaded["fairness_signals.csv"], "TrainerId", trainer_ids, "fairness_signals")
    errors += require_reference(loaded["fairness_signals.csv"], "CourseId", course_ids, "fairness_signals")

    for row in loaded["workload_entries.csv"]:
        try:
            hours = float(row["Hours"])
        except ValueError:
            errors.append(f"workload_entries: Hours is not numeric for {row['EntryId']}")
            continue
        if hours < 0:
            errors.append(f"workload_entries: negative Hours for {row['EntryId']}")

    for row in loaded["evaluation_responses.csv"]:
        score = float(row["AverageScore"])
        responses = int(row["ResponseCount"])
        if not 1 <= score <= 5:
            errors.append(f"evaluation_responses: AverageScore outside 1-5 for {row['EvaluationId']}")
        if responses <= 0:
            errors.append(f"evaluation_responses: ResponseCount must be positive for {row['EvaluationId']}")

    if errors:
        print("\nFAILED relationship/content checks")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Relationship checks: OK")
    print("Numeric checks: OK")
    print("Demo CSV validation: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
