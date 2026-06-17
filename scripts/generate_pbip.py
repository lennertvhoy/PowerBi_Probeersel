#!/usr/bin/env python3
"""Generate a PBIP project from repo CSVs, model.md, and measures.dax.

This creates a programmatically valid PBIP folder that Power BI Desktop
should open. It uses TMDL for the semantic model and PBIR-Legacy (report.json)
for the minimal report definition.
"""

import csv
import json
import os
import pathlib
import shutil
import uuid

REPO = pathlib.Path(__file__).resolve().parents[1]
DATA = REPO / "data"
POWERBI = REPO / "powerbi"
OUTPUT = POWERBI / "Fair_Workload_Evaluation_Cockpit_PBIP"

PROJECT_NAME = "Fair_Workload_Evaluation_Cockpit"
REPORT_FOLDER = f"{PROJECT_NAME}.Report"
MODEL_FOLDER = f"{PROJECT_NAME}.SemanticModel"


def csv_column_count(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return len(next(reader))


def infer_dtype(values):
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "string"
    try:
        for v in non_empty:
            int(v)
        return "int64"
    except ValueError:
        pass
    try:
        for v in non_empty:
            float(v)
        return "double"
    except ValueError:
        pass
    if all(v.lower() in {"true", "false", "1", "0", "yes", "no"} for v in non_empty):
        return "boolean"
    import re

    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if all(date_re.match(v) for v in non_empty):
        return "dateTime"
    return "string"


def read_csv_schema(name):
    path = DATA / name
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    columns = []
    for field in fieldnames:
        sample = [row.get(field, "") for row in rows[:50]]
        dtype = infer_dtype(sample)
        columns.append({"name": field, "dataType": dtype, "sourceColumn": field})
    return {
        "name": pathlib.Path(name).stem,
        "columns": columns,
        "row_count": len(rows),
        "col_count": len(fieldnames),
    }


def main():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    csvs = [
        "trainers.csv",
        "courses.csv",
        "sessions.csv",
        "workload_entries.csv",
        "evaluation_responses.csv",
        "feedback_comments.csv",
        "fairness_signals.csv",
    ]
    tables = [read_csv_schema(n) for n in csvs]

    # Folders
    (OUTPUT / REPORT_FOLDER / "definition" / "pages").mkdir(parents=True, exist_ok=True)
    (OUTPUT / MODEL_FOLDER / "definition" / "tables").mkdir(parents=True, exist_ok=True)
    (OUTPUT / MODEL_FOLDER / ".pbi").mkdir(parents=True, exist_ok=True)
    (OUTPUT / REPORT_FOLDER / ".pbi").mkdir(parents=True, exist_ok=True)

    # .pbip
    pbip = {
        "version": "1.0",
        "artifacts": [{"report": {"path": REPORT_FOLDER}}],
        "settings": {"enableAutoRecovery": True},
    }
    (OUTPUT / f"{PROJECT_NAME}.pbip").write_text(json.dumps(pbip, indent=2), encoding="utf-8")

    # .gitignore
    (OUTPUT / ".gitignore").write_text(
        "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n", encoding="utf-8"
    )

    # definition.pbism
    pbism = {"version": "4.0", "settings": {}}
    (OUTPUT / MODEL_FOLDER / "definition.pbism").write_text(
        json.dumps(pbism, indent=2), encoding="utf-8"
    )

    # .platform model
    model_plat = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": PROJECT_NAME},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    (OUTPUT / MODEL_FOLDER / ".platform").write_text(
        json.dumps(model_plat, indent=2), encoding="utf-8"
    )

    # definition.pbir
    pbir = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{MODEL_FOLDER}"}},
    }
    (OUTPUT / REPORT_FOLDER / "definition.pbir").write_text(
        json.dumps(pbir, indent=2), encoding="utf-8"
    )

    # .platform report
    report_plat = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": PROJECT_NAME},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    (OUTPUT / REPORT_FOLDER / ".platform").write_text(
        json.dumps(report_plat, indent=2), encoding="utf-8"
    )

    # report.json (PBIR-Legacy minimal)
    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU06",
                "reportVersionAtImport": "5.55",
                "type": "SharedResources",
            }
        },
        "config": {"version": 5, "defaultDrillFilterOtherVisuals": True},
        "objects": {},
    }
    (OUTPUT / REPORT_FOLDER / "report.json").write_text(
        json.dumps(report_json, indent=2), encoding="utf-8"
    )

    # database.tmdl
    db_tmdl = f"database {PROJECT_NAME}\n\tcompatibilityLevel: 1600\n"
    (OUTPUT / MODEL_FOLDER / "definition" / "database.tmdl").write_text(db_tmdl, encoding="utf-8")

    # model.tmdl
    model_lines = [
        "model Model",
        "\tculture: en-US",
        "\tdiscourageImplicitMeasures: true",
    ]
    for t in tables:
        model_lines.append(f"\ttable {t['name']}")
    model_tmdl = "\n".join(model_lines) + "\n"
    (OUTPUT / MODEL_FOLDER / "definition" / "model.tmdl").write_text(model_tmdl, encoding="utf-8")

    # expressions.tmdl
    data_path = str(DATA).replace("\\", "\\\\")
    expr_tmdl = f'expression DataPath = "{data_path}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]\n'
    (OUTPUT / MODEL_FOLDER / "definition" / "expressions.tmdl").write_text(
        expr_tmdl, encoding="utf-8"
    )

    # Parse measures
    measures_text = (POWERBI / "measures.dax").read_text(encoding="utf-8")
    measure_blocks = [b.strip() for b in measures_text.split("\n\n") if b.strip()]
    measures = []
    for block in measure_blocks:
        lines = block.splitlines()
        name_line = None
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("--"):
                name_line = stripped
                break
        if name_line and "=" in name_line:
            name = name_line.split("=")[0].strip()
            expr = "\n".join(lines[1:]).strip()
            measures.append({"name": name, "expression": expr})

    # tables/*.tmdl
    for t in tables:
        lines = [f"table {t['name']}", ""]
        for col in t["columns"]:
            lines.append(f"\tcolumn {col['name']}")
            lines.append(f"\t\tdataType: {col['dataType']}")
            lines.append(f"\t\tsourceColumn: {col['sourceColumn']}")
            lines.append("")

        if t["name"] == "workload_entries":
            for m in measures:
                lines.append(f"\tmeasure {m['name']}")
                lines.append(f"\t\texpression = {m['expression']}")
                lines.append("")

        if t["name"] == "sessions":
            lines.append("\tcolumn 'Full Name'")
            lines.append("\t\tdataType: string")
            lines.append("\t\tkind: calculatedColumn")
            lines.append("\t\texpression = RELATED(trainers[Trainer])")
            lines.append("")

        csv_file = str(DATA / f"{t['name']}.csv").replace("\\", "\\\\")
        lines.append(f"\tpartition {t['name']} = m")
        lines.append(f"\t\tmode: import")
        lines.append(f"\t\tsource =")
        lines.append(f"\t\t\tlet")
        lines.append(f"\t\t\t\tSource = Csv.Document(File.Contents(\"{csv_file}\"), [Delimiter = \",\", Columns = {t['col_count']}, Encoding = 65001, QuoteStyle = QuoteStyle.None]),")
        lines.append(f"\t\t\t\tPromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])")
        lines.append(f"\t\t\tin")
        lines.append(f"\t\t\t\tPromotedHeaders")
        lines.append("")

        tmdl_path = OUTPUT / MODEL_FOLDER / "definition" / "tables" / f"{t['name']}.tmdl"
        tmdl_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # relationships.tmdl
    rels = [
        ("sessions", "TrainerId", "trainers", "TrainerId", "manyToOne", "single"),
        ("sessions", "CourseId", "courses", "CourseId", "manyToOne", "single"),
        ("workload_entries", "TrainerId", "trainers", "TrainerId", "manyToOne", "single"),
        ("workload_entries", "CourseId", "courses", "CourseId", "manyToOne", "single"),
        ("evaluation_responses", "SessionId", "sessions", "SessionId", "manyToOne", "single"),
        ("feedback_comments", "SessionId", "sessions", "SessionId", "manyToOne", "single"),
        ("fairness_signals", "TrainerId", "trainers", "TrainerId", "manyToOne", "single"),
        ("fairness_signals", "CourseId", "courses", "CourseId", "manyToOne", "single"),
    ]
    rel_lines = ["// Relationships", ""]
    for i, (from_t, from_c, to_t, to_c, card, cross) in enumerate(rels, 1):
        rel_lines.append(f"relationship rel_{i:02d}")
        rel_lines.append(f"\tfromColumn: {from_t}.{from_c}")
        rel_lines.append(f"\ttoColumn: {to_t}.{to_c}")
        rel_lines.append(f"\tcardinality: {card}")
        rel_lines.append(f"\tcrossFilteringBehavior: {cross}")
        rel_lines.append("")
    (OUTPUT / MODEL_FOLDER / "definition" / "relationships.tmdl").write_text(
        "\n".join(rel_lines) + "\n", encoding="utf-8"
    )

    # diagramLayout.json
    diag = {"version": 1, "diagrams": []}
    (OUTPUT / MODEL_FOLDER / "diagramLayout.json").write_text(
        json.dumps(diag, indent=2), encoding="utf-8"
    )

    print(f"PBIP generated at: {OUTPUT}")
    for root, dirs, files in os.walk(OUTPUT):
        for f in files:
            fp = pathlib.Path(root) / f
            print(f"  {fp.relative_to(OUTPUT)} ({fp.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
