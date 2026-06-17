#!/usr/bin/env python3
"""Generate a PBIP project with TMSL (model.bim) from repo CSVs and measures."""

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

    (OUTPUT / REPORT_FOLDER / "definition" / "pages").mkdir(parents=True, exist_ok=True)
    (OUTPUT / MODEL_FOLDER).mkdir(parents=True, exist_ok=True)
    (OUTPUT / MODEL_FOLDER / ".pbi").mkdir(parents=True, exist_ok=True)
    (OUTPUT / REPORT_FOLDER / ".pbi").mkdir(parents=True, exist_ok=True)

    pbip = {
        "version": "1.0",
        "artifacts": [{"report": {"path": REPORT_FOLDER}}],
        "settings": {"enableAutoRecovery": True},
    }
    (OUTPUT / f"{PROJECT_NAME}.pbip").write_text(json.dumps(pbip, indent=2), encoding="utf-8")

    (OUTPUT / ".gitignore").write_text(
        "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n", encoding="utf-8"
    )

    pbism = {"version": "1.0", "settings": {}}
    (OUTPUT / MODEL_FOLDER / "definition.pbism").write_text(
        json.dumps(pbism, indent=2), encoding="utf-8"
    )

    model_plat = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": PROJECT_NAME},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    (OUTPUT / MODEL_FOLDER / ".platform").write_text(
        json.dumps(model_plat, indent=2), encoding="utf-8"
    )

    pbir = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "1.0",
        "datasetReference": {"byPath": {"path": f"../{MODEL_FOLDER}"}},
    }
    (OUTPUT / REPORT_FOLDER / "definition.pbir").write_text(
        json.dumps(pbir, indent=2), encoding="utf-8"
    )

    report_plat = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": PROJECT_NAME},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    (OUTPUT / REPORT_FOLDER / ".platform").write_text(
        json.dumps(report_plat, indent=2), encoding="utf-8"
    )

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

    model_tables = []
    for t in tables:
        table_cols = []
        for col in t["columns"]:
            table_cols.append({
                "name": col["name"],
                "dataType": col["dataType"],
                "sourceColumn": col["sourceColumn"],
            })

        if t["name"] == "sessions":
            table_cols.append({
                "name": "Full Name",
                "dataType": "string",
                "kind": "calculatedColumn",
                "expression": "RELATED(trainers[Trainer])",
            })

        table_measures = []
        if t["name"] == "workload_entries":
            for m in measures:
                table_measures.append({
                    "name": m["name"],
                    "expression": m["expression"],
                })

        csv_file = str(DATA / f"{t['name']}.csv").replace("\\", "\\\\")
        m_expression = (
            f'let\n'
            f'    Source = Csv.Document(File.Contents("{csv_file}"), [Delimiter = ",", Columns = {t["col_count"]}, Encoding = 65001, QuoteStyle = QuoteStyle.None]),\n'
            f'    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])\n'
            f'in\n'
            f'    PromotedHeaders'
        )

        model_tables.append({
            "name": t["name"],
            "columns": table_cols,
            "measures": table_measures,
            "partitions": [
                {
                    "name": t["name"],
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": m_expression,
                    },
                }
            ],
        })

    rels = [
        ("sessions", "TrainerId", "trainers", "TrainerId", "oneToMany", "single"),
        ("sessions", "CourseId", "courses", "CourseId", "oneToMany", "single"),
        ("workload_entries", "TrainerId", "trainers", "TrainerId", "oneToMany", "single"),
        ("workload_entries", "CourseId", "courses", "CourseId", "oneToMany", "single"),
        ("evaluation_responses", "SessionId", "sessions", "SessionId", "oneToMany", "single"),
        ("feedback_comments", "SessionId", "sessions", "SessionId", "oneToMany", "single"),
        ("fairness_signals", "TrainerId", "trainers", "TrainerId", "oneToMany", "single"),
        ("fairness_signals", "CourseId", "courses", "CourseId", "oneToMany", "single"),
    ]
    model_relationships = []
    for i, (from_t, from_c, to_t, to_c, card, cross) in enumerate(rels, 1):
        model_relationships.append({
            "name": f"rel_{i:02d}",
            "fromTable": from_t,
            "fromColumn": from_c,
            "toTable": to_t,
            "toColumn": to_c,
            "cardinality": card,
            "crossFilteringBehavior": cross,
        })

    bim = {
        "name": PROJECT_NAME,
        "compatibilityLevel": 1600,
        "model": {
            "culture": "en-US",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "discourageImplicitMeasures": True,
            "sourceQueryCulture": "en-US",
            "tables": model_tables,
            "relationships": model_relationships,
        },
    }

    (OUTPUT / MODEL_FOLDER / "model.bim").write_text(
        json.dumps(bim, indent=2), encoding="utf-8"
    )

    diag = {"version": 1, "diagrams": []}
    (OUTPUT / MODEL_FOLDER / "diagramLayout.json").write_text(
        json.dumps(diag, indent=2), encoding="utf-8"
    )

    print(f"PBIP (TMSL) generated at: {OUTPUT}")
    for root, dirs, files in os.walk(OUTPUT):
        for f in files:
            fp = pathlib.Path(root) / f
            print(f"  {fp.relative_to(OUTPUT)} ({fp.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
