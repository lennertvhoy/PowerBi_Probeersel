#!/usr/bin/env python3
"""Generate a draft TMDL folder from repo CSV schema, model.md and measures.dax.

This is a skeleton generator. The output is NOT guaranteed to be a valid,
openable TMDL project until it is validated by pbi-tools convert or
Tabular Editor. It produces a starting point for semantic-model automation.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys
from datetime import datetime
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
POWERBI = ROOT / "powerbi"
DEFAULT_OUT = POWERBI / "tmdl_generated"


def infer_data_type(values: list[str]) -> str:
    """Heuristic to infer TMDL data type from a sample of values."""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "string"

    # Try int64
    try:
        for v in non_empty:
            int(v)
        return "int64"
    except ValueError:
        pass

    # Try double
    try:
        for v in non_empty:
            float(v)
        return "double"
    except ValueError:
        pass

    # Try dateTime (ISO-like or common date formats)
    date_patterns = [
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),
        re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"),
        re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    ]
    if all(any(p.match(v) for p in date_patterns) for v in non_empty):
        return "dateTime"

    # Try boolean
    if all(v.lower() in {"true", "false", "1", "0", "yes", "no"} for v in non_empty):
        return "boolean"

    return "string"


def read_csv_schema(name: str) -> dict[str, Any]:
    path = DATA / name
    if not path.exists():
        raise ValueError(f"Missing CSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    columns = []
    for field in fieldnames:
        sample = [row.get(field, "") for row in rows[:50]]
        dtype = infer_data_type(sample)
        columns.append({"name": field, "dataType": dtype, "sourceColumn": field})

    table_name = pathlib.Path(name).stem
    return {
        "name": table_name,
        "columns": columns,
        "row_count": len(rows),
    }


def parse_model_md() -> list[dict[str, str]]:
    """Parse relationships from powerbi/model.md."""
    path = POWERBI / "model.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    relationships = []
    # Match markdown table rows for relationships
    # Example: | `sessions[TrainerId]` | `trainers[TrainerId]` | many-to-one | single |
    rel_re = re.compile(
        r"\|\s*`?(\w+)\[(\w+)]`?\s*\|\s*`?(\w+)\[(\w+)]`?\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    )
    for match in rel_re.finditer(text):
        from_table, from_col, to_table, to_col, cardinality, direction = match.groups()
        relationships.append(
            {
                "from_table": from_table,
                "from_column": from_col,
                "to_table": to_table,
                "to_column": to_col,
                "cardinality": cardinality,
                "direction": direction,
            }
        )
    return relationships


def parse_measures_dax() -> list[dict[str, str]]:
    """Parse measures from powerbi/measures.dax.

    Measures are separated by blank lines. The first non-comment line is the name.
    """
    path = POWERBI / "measures.dax"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    measures = []
    for block in blocks:
        lines = block.splitlines()
        # Skip leading comment lines
        name_line = None
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("--"):
                name_line = stripped
                break
        if name_line and "=" in name_line:
            name = name_line.split("=")[0].strip()
            expression = block[block.index("=") + 1 :].strip()
            measures.append({"name": name, "expression": expression})
    return measures


def parse_calculated_columns() -> list[dict[str, str]]:
    """Return known calculated columns from build instructions."""
    # Derived from docs/demo/PBI_DESKTOP_BUILD_INSTRUCTIONS.md
    return [
        {
            "table": "sessions",
            "name": "Full Name",
            "expression": "RELATED(trainers[Trainer])",
        }
    ]


def escape_tmdl_name(name: str) -> str:
    """Escape a name for TMDL if it contains spaces or special chars."""
    if re.search(r"[^A-Za-z0-9_]", name):
        return f"'{name}'"
    return name


def write_tmdl(tables: list[dict[str, Any]], relationships: list[dict[str, str]], measures: list[dict[str, str]], calculated_columns: list[dict[str, str]], out_dir: pathlib.Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write database.tmdl
    db_path = out_dir / "database.tmdl"
    db_path.write_text(
        f"database FairWorkloadEvaluationCockpit\n    compatibilityLevel: 1600\n    model FairWorkloadEvaluationCockpit\n",
        encoding="utf-8",
    )

    # Write model.tmdl
    model_path = out_dir / "model.tmdl"
    model_lines = [
        "model FairWorkloadEvaluationCockpit",
        "    culture 'en-US'",
        "        linguaModel: en-US",
    ]
    for table in tables:
        model_lines.append(f"        translatedCaption: {table['name']}")
    model_lines.append("")
    model_path.write_text("\n".join(model_lines) + "\n", encoding="utf-8")

    # Write tables/*.tmdl
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(exist_ok=True)

    for table in tables:
        lines = [f"table {escape_tmdl_name(table['name'])}", ""]
        for col in table["columns"]:
            lines.append(f"    column {escape_tmdl_name(col['name'])}")
            lines.append(f"        dataType: {col['dataType']}")
            lines.append(f"        sourceColumn: {escape_tmdl_name(col['sourceColumn'])}")
            lines.append("")

        # Add calculated columns for this table
        for calc in calculated_columns:
            if calc["table"] == table["name"]:
                lines.append(f"    column {escape_tmdl_name(calc['name'])}")
                lines.append(f"        dataType: string")
                lines.append(f"        kind: calculatedColumn")
                lines.append(f"        expression: {calc['expression']}")
                lines.append("")

        # Add measures that belong to this table (heuristic: workload_entries gets most)
        # In real TMDL, measures are usually in the table they reference most.
        # We attach all measures to workload_entries as the primary fact table.
        if table["name"] == "workload_entries":
            for measure in measures:
                lines.append(f"    measure {escape_tmdl_name(measure['name'])}")
                lines.append(f"        expression: {measure['expression']}")
                lines.append("")

        lines.append(f"    partition {table['name']}")
        lines.append(f"        mode: import")
        lines.append(f"        source = CSV")
        lines.append("")

        tmdl_path = tables_dir / f"{table['name']}.tmdl"
        tmdl_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Write relationships.tmdl
    rel_path = out_dir / "relationships.tmdl"
    rel_lines = ["// Relationships derived from powerbi/model.md", ""]
    for rel in relationships:
        rel_lines.append(
            f"relationship {rel['from_table']}_{rel['from_column']}_to_{rel['to_table']}_{rel['to_column']}"
        )
        rel_lines.append(f"    fromColumn: {escape_tmdl_name(rel['from_table'])}.{escape_tmdl_name(rel['from_column'])}")
        rel_lines.append(f"    toColumn: {escape_tmdl_name(rel['to_table'])}.{escape_tmdl_name(rel['to_column'])}")
        rel_lines.append(f"    cardinality: {rel['cardinality'].replace('many-to-one', 'manyToOne')}")
        rel_lines.append("")
    rel_path.write_text("\n".join(rel_lines) + "\n", encoding="utf-8")

    print(f"TMDL draft written to: {out_dir}")
    print(f"  Tables: {len(tables)}")
    print(f"  Relationships: {len(relationships)}")
    print(f"  Measures: {len(measures)}")
    print(f"  Calculated columns: {len(calculated_columns)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate draft TMDL from repo specs")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args(argv or sys.argv[1:])

    out_dir = pathlib.Path(args.out).resolve()

    csvs = [
        "trainers.csv",
        "courses.csv",
        "sessions.csv",
        "workload_entries.csv",
        "evaluation_responses.csv",
        "feedback_comments.csv",
        "fairness_signals.csv",
    ]

    tables = [read_csv_schema(name) for name in csvs]
    relationships = parse_model_md()
    measures = parse_measures_dax()
    calculated_columns = parse_calculated_columns()

    write_tmdl(tables, relationships, measures, calculated_columns, out_dir)

    # Also write a manifest JSON for downstream tooling
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "generator": "scripts/generate_tmdl_model.py",
        "tables": [t["name"] for t in tables],
        "relationships": relationships,
        "measures": [m["name"] for m in measures],
        "calculated_columns": calculated_columns,
        "output_dir": str(out_dir),
        "warnings": [
            "This is a draft TMDL skeleton. Column data types are inferred heuristically.",
            "Partitions use placeholder 'CSV' source; real PBIP requires Mashup/Power Query definitions.",
            "Measures are attached to workload_entries table as a heuristic.",
            "Validate with pbi-tools convert or Tabular Editor before claiming production readiness.",
        ],
    }
    manifest_path = out_dir / "manifest.json"
    import json

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written to: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
