#!/usr/bin/env python3
"""Report the current state of the Power BI automation pipeline."""

from __future__ import annotations

import csv
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
POWERBI = ROOT / "powerbi"
EVIDENCE = ROOT / "docs" / "evidence"

PBI_EXE = pathlib.Path(r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe")
TE_EXE = pathlib.Path(r"C:\Users\codex_pbi\tools\tabular-editor-2\TabularEditor.exe")
PBI_TOOLS_EXE = pathlib.Path(r"C:\Users\codex_pbi\tools\pbi-tools\pbi-tools.core.exe")

REQUIRED_CSVS = [
    "trainers.csv",
    "courses.csv",
    "sessions.csv",
    "workload_entries.csv",
    "evaluation_responses.csv",
    "feedback_comments.csv",
    "fairness_signals.csv",
]


def check_file(path: pathlib.Path) -> dict[str, Any]:
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return {"exists": exists, "size": size}


def check_pbix() -> dict[str, Any]:
    pbix = POWERBI / "Fair_Workload_Evaluation_Cockpit.pbix"
    return check_file(pbix)


def check_pbip() -> dict[str, Any]:
    pbip = POWERBI / "Fair_Workload_Evaluation_Cockpit_PBIP"
    report_def = pbip / "report.json"
    model_def = pbip / "definition.pbidataset"
    return {
        "folder_exists": pbip.exists(),
        "has_report_json": report_def.exists(),
        "has_model_definition": model_def.exists(),
        "note": "PBIR preview files may use different names; this checks common ones.",
    }


def check_csvs() -> dict[str, Any]:
    results = {}
    all_ok = True
    for name in REQUIRED_CSVS:
        path = DATA / name
        ok = path.exists()
        results[name] = ok
        if not ok:
            all_ok = False
    return {"all_exist": all_ok, "files": results}


def check_measures() -> dict[str, Any]:
    path = POWERBI / "measures.dax"
    if not path.exists():
        return {"exists": False, "measure_count": 0, "blocks": []}
    text = path.read_text(encoding="utf-8")
    # Measures are separated by blank lines; each starts with a name line
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    measures = []
    for b in blocks:
        first_line = b.splitlines()[0].strip()
        if first_line and not first_line.startswith("--"):
            measures.append(first_line)
    return {"exists": True, "measure_count": len(measures), "blocks": measures}


def check_theme() -> dict[str, Any]:
    path = POWERBI / "theme.json"
    if not path.exists():
        return {"exists": False, "valid_json": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"exists": True, "valid_json": True, "name": data.get("name", "")}
    except json.JSONDecodeError as e:
        return {"exists": True, "valid_json": False, "error": str(e)}


def check_pbi_desktop() -> dict[str, Any]:
    return {
        "exists": PBI_EXE.exists(),
        "path": str(PBI_EXE),
    }


def check_tabular_editor() -> dict[str, Any]:
    return {
        "exists": TE_EXE.exists(),
        "path": str(TE_EXE),
    }


def check_pbi_tools() -> dict[str, Any]:
    return {
        "exists": PBI_TOOLS_EXE.exists(),
        "path": str(PBI_TOOLS_EXE),
    }


def check_gh_ci() -> dict[str, Any] | None:
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--workflow", "Validate Template Docs", "--limit", "1", "--json", "databaseId,headSha,status,conclusion,url"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        runs = json.loads(result.stdout)
        if not runs:
            return None
        run = runs[0]
        return {
            "available": True,
            "run_id": run.get("databaseId"),
            "head_sha": run.get("headSha"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "url": run.get("url"),
        }
    except FileNotFoundError:
        return None


def determine_next_step(status: dict[str, Any]) -> str:
    if not status["csvs"]["all_exist"]:
        return "Fix missing CSV data files."
    if not status["pbi_desktop"]["exists"]:
        return "Install Power BI Desktop."
    if not status["pbip"]["folder_exists"]:
        return "Create seed PBIP/PBIR project in Power BI Desktop (BL-AUTO-002)."
    if not status["pbip"]["has_report_json"]:
        return "PBIP folder exists but lacks valid PBIR report definition; complete the seed project."
    if not status["tabular_editor"]["exists"]:
        return "Install Tabular Editor 2 for semantic model automation (BL-AUTO-004)."
    if not status["pbi_tools"]["exists"]:
        return "Install pbi-tools for extract/compile pipeline (BL-AUTO-004)."
    if not status["pbix"]["exists"]:
        return "Compile or save PBIX from the validated PBIP project (BL-001)."
    return "Pipeline appears complete; run Windows GUI smoke test (BL-AUTO-006)."


def main() -> int:
    status = {
        "pbix": check_pbix(),
        "pbip": check_pbip(),
        "csvs": check_csvs(),
        "measures": check_measures(),
        "theme": check_theme(),
        "pbi_desktop": check_pbi_desktop(),
        "tabular_editor": check_tabular_editor(),
        "pbi_tools": check_pbi_tools(),
        "ci": check_gh_ci(),
    }
    status["next_step"] = determine_next_step(status)

    print("=" * 60)
    print("POWER BI PIPELINE STATUS")
    print("=" * 60)

    print("\n--- Artifacts ---")
    pbix = status["pbix"]
    print(f"PBIX exists : {pbix['exists']} ({pbix['size']} bytes)")
    pbip = status["pbip"]
    print(f"PBIP folder : {pbip['folder_exists']}")
    print(f"  report.json      : {pbip['has_report_json']}")
    print(f"  model definition : {pbip['has_model_definition']}")

    print("\n--- Data ---")
    print(f"CSVs valid  : {status['csvs']['all_exist']}")
    for name, ok in status['csvs']['files'].items():
        print(f"  {name}: {'OK' if ok else 'MISSING'}")

    print("\n--- Specs ---")
    m = status["measures"]
    print(f"Measures file exists : {m['exists']} ({m['measure_count']} measures)")
    t = status["theme"]
    print(f"Theme exists         : {t['exists']} (valid JSON: {t['valid_json']})")

    print("\n--- Tooling ---")
    print(f"Power BI Desktop : {status['pbi_desktop']['exists']} ({status['pbi_desktop']['path']})")
    print(f"Tabular Editor 2 : {status['tabular_editor']['exists']} ({status['tabular_editor']['path']})")
    print(f"pbi-tools        : {status['pbi_tools']['exists']} ({status['pbi_tools']['path']})")

    print("\n--- CI ---")
    ci = status["ci"]
    if ci:
        print(f"GitHub CLI available : yes")
        print(f"Latest run ID        : {ci['run_id']}")
        print(f"Head SHA             : {ci['head_sha']}")
        print(f"Status               : {ci['status']}")
        print(f"Conclusion           : {ci['conclusion']}")
        print(f"URL                  : {ci['url']}")
    else:
        print("GitHub CLI available : no (install gh or check Actions in browser)")

    print("\n--- Next Missing Step ---")
    print(status["next_step"])

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
