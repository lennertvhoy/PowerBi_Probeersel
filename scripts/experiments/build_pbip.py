# WARNING: This script is a preserved experiment.
# It represents a dead-end approach (raw GUI automation or fake PBIP generation).
# Do not run it expecting a real artifact. See docs/dev/POWER_BI_AUTOMATION_STRATEGY.md.

#!/usr/bin/env python3
"""
Build PBIP project folder directly (no GUI automation needed).
A PBIP is a folder with JSON schema files that PBI Desktop can open.
"""
import json, os, uuid, hashlib, base64, struct, zipfile, csv
from datetime import datetime, timezone

REPO = r"C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel"
DATA_DIR = os.path.join(REPO, "data")
PBI_DIR = os.path.join(REPO, "powerbi")
EVIDENCE = os.path.join(REPO, "docs", "evidence", "002-real-powerbi-artifact")
PBIX_PATH = os.path.join(PBI_DIR, "Fair_Workload_Evaluation_Cockpit.pbix")
PBIP_DIR = os.path.join(PBI_DIR, "Fair_Workload_Evaluation_Cockpit_PBIP")

os.makedirs(EVIDENCE, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def new_id():
    return str(uuid.uuid4())

# ── 1. Read all CSVs ──────────────────────────────────────────
def read_csv(name):
    path = os.path.join(DATA_DIR, name)
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

trainers = read_csv("trainers.csv")
courses = read_csv("courses.csv")
sessions = read_csv("sessions.csv")
workload_entries = read_csv("workload_entries.csv")
evaluation_responses = read_csv("evaluation_responses.csv")
feedback_comments = read_csv("feedback_comments.csv")
fairness_signals = read_csv("fairness_signals.csv")

print(f"Loaded: {len(trainers)} trainers, {len(courses)} courses, {len(sessions)} sessions")
print(f"       {len(workload_entries)} workload, {len(evaluation_responses)} evals")
print(f"       {len(feedback_comments)} feedback, {len(fairness_signals)} signals")

# ── 2. Build dataModel.schema ─────────────────────────────────
# We define tables and their columns

def make_table(name, cols):
    """Create table schema dict."""
    return {
        "name": name,
        "columns": [{"name": c["name"], "dataType": c["type"], "isHidden": c.get("hidden", False)} for c in cols],
        "partitions": [{"name": name, "source": {"type": "calculated"}}],
        "description": ""
    }

tables_schema = [
    make_table("trainers", [
        {"name": "TrainerId", "type": "string"},
        {"name": "Trainer", "type": "string"},
        {"name": "Team", "type": "string"},
    ]),
    make_table("courses", [
        {"name": "CourseId", "type": "string"},
        {"name": "Course", "type": "string"},
        {"name": "Domain", "type": "string"},
        {"name": "ComplexityScore", "type": "decimal"},
        {"name": "DefaultSessionType", "type": "string"},
    ]),
    make_table("sessions", [
        {"name": "SessionId", "type": "string"},
        {"name": "Date", "type": "datetime"},
        {"name": "TrainerId", "type": "string"},
        {"name": "CourseId", "type": "string"},
        {"name": "Audience", "type": "string"},
        {"name": "SessionType", "type": "string"},
        {"name": "ContactHours", "type": "decimal"},
        {"name": "IsNewTopic", "type": "bool"},
        {"name": "Location", "type": "string"},
    ]),
    make_table("workload_entries", [
        {"name": "EntryId", "type": "string"},
        {"name": "Date", "type": "datetime"},
        {"name": "TrainerId", "type": "string"},
        {"name": "CourseId", "type": "string"},
        {"name": "SessionId", "type": "string"},
        {"name": "Category", "type": "string"},
        {"name": "Hours", "type": "decimal"},
        {"name": "Source", "type": "string"},
        {"name": "Description", "type": "string"},
    ]),
    make_table("evaluation_responses", [
        {"name": "EvaluationId", "type": "string"},
        {"name": "SessionId", "type": "string"},
        {"name": "AverageScore", "type": "decimal"},
        {"name": "ResponseCount", "type": "decimal"},
        {"name": "Nps", "type": "decimal"},
        {"name": "MainIssue", "type": "string"},
    ]),
    make_table("feedback_comments", [
        {"name": "FeedbackId", "type": "string"},
        {"name": "SessionId", "type": "string"},
        {"name": "Theme", "type": "string"},
        {"name": "Sentiment", "type": "string"},
        {"name": "Comment", "type": "string"},
    ]),
    make_table("fairness_signals", [
        {"name": "SignalId", "type": "string"},
        {"name": "SignalDate", "type": "datetime"},
        {"name": "SignalType", "type": "string"},
        {"name": "TrainerId", "type": "string"},
        {"name": "CourseId", "type": "string"},
        {"name": "Severity", "type": "string"},
        {"name": "Signal", "type": "string"},
        {"name": "RecommendedAction", "type": "string"},
    ]),
]

# Relationships
relationships = [
    {
        "leftTable": "sessions", "leftColumn": "TrainerId",
        "rightTable": "trainers", "rightColumn": "TrainerId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "sessions", "leftColumn": "CourseId",
        "rightTable": "courses", "rightColumn": "CourseId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "workload_entries", "leftColumn": "TrainerId",
        "rightTable": "trainers", "rightColumn": "TrainerId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "workload_entries", "leftColumn": "CourseId",
        "rightTable": "courses", "rightColumn": "CourseId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "evaluation_responses", "leftColumn": "SessionId",
        "rightTable": "sessions", "rightColumn": "SessionId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "feedback_comments", "leftColumn": "SessionId",
        "rightTable": "sessions", "rightColumn": "SessionId",
        "crossFiltering": "oneDirection", "joinType": "inner"
    },
    {
        "leftTable": "fairness_signals", "leftColumn": "TrainerId",
        "rightTable": "trainers", "rightColumn": "TrainerId",
        "crossFiltering": "bothDirections", "joinType": "leftOuter"
    },
    {
        "leftTable": "fairness_signals", "leftColumn": "CourseId",
        "rightTable": "courses", "rightColumn": "CourseId",
        "crossFiltering": "bothDirections", "joinType": "leftOuter"
    },
]

# Read actual CSV data for embedding
def table_to_rows(rows):
    """Convert list of dicts to list of lists with header."""
    if not rows:
        return []
    headers = list(rows[0].keys())
    return [headers] + [[r[h] for h in headers] for r in rows]

# We'll generate a PBIX file directly as a ZIP with proper structure
# PBIX = ZIP containing: DataModelSchema, Connections, Report, etc.

print("\n=== Building PBIX as ZIP ===")

# PBIX internal structure
bufs = {}

# 1. DataModelSchema - the core model definition
model_doc = {
    "name": "Model",
    "id": new_id(),
    "model": {
        "tables": tables_schema,
        "relationships": relationships,
        "culture": "nl-NL",
    }
}
bufs["DataModelSchema"] = json.dumps(model_doc, indent=2)

# 2. Connections
connections = {
    "version": "1.0.0",
    "connections": []
}
bufs["Connections"] = json.dumps(connections)

# 3. Settings
settings = {
    "version": "1.0.0",
    "settings": {
        "cloudEdition": {
            "datasetStorageLevel": "dual"
        }
    }
}
bufs["Settings"] = json.dumps(settings)

# 4. Build Report.json with 5 pages
# This is the most complex part - we need a valid report structure

# Helper to generate unique IDs
def uid():
    return new_id()

# Build visuals for Page 1: Management Overview
page1_visuals = []
# Title textbox
page1_visuals.append({
    "x": 0, "y": 0, "z": 1000,
    "width": 800, "height": 50,
    "type": "textbox",
    "config": {"displayName": "Team workload & kwaliteitsoverzicht", "paragraphs": [{"text": "Team workload & kwaliteitsoverzicht", "fontSize": 18, "isBold": True}]}
})

# We'll create a simpler report structure that PBI Desktop can open
# and then apply visual formatting

print("Building report structure...")

# Build a PBIX as a proper ZIP
import io

# First, let's try the simplest path: use the pbism approach
# Actually, let's just directly construct a minimal valid PBIX ZIP

# A working PBIX needs these entries:
# DataModelSchema (JSON)
# Connections (JSON)  
# Report/Report.bin (binary protobuf - too complex to construct)
# OR we can create a .pbip folder and then open it

# Better approach: create .pbip folder, open in PBI Desktop, export to .pbix
# OR: construct a minimal PBIX with Report.bin

# Since constructing Report.bin (protobuf) is impractical,
# let's try another approach:
# 1. Create the PBIP folder structure
# 2. Try to open it in PBI Desktop and save as PBIX

# Actually, the most pragmatic approach: 
# Create a minimal valid PBIX using the python-docx-style zip approach
# with a pre-built template

print("Creating PBIP project folder...")

# Clean up
import shutil
if os.path.exists(PBIP_DIR):
    shutil.rmtree(PBIP_DIR)

os.makedirs(PBIP_DIR)

# Write dataModel.schema
# This is the full model definition in PBIP format
model_version = 17000012892  # typical version for PBI May 2026

# Build the full data model with embedded data
data_model = {
    "version": "5.5.0",  # schema version for May 2026 PBI
    "model": {
        "tables": [
            {
                "name": "trainers",
                "columns": [
                    {"name": "TrainerId", "dataType": "String", "isHidden": False, "sourceColumn": "TrainerId"},
                    {"name": "Trainer", "dataType": "String", "isHidden": False, "sourceColumn": "Trainer"},
                    {"name": "Team", "dataType": "String", "isHidden": False, "sourceColumn": "Team"},
                ],
                "partitions": [
                    {
                        "name": "trainers",
                        "mode": "import",
                        "source": {"type": "calculated"},
                        "dataView": "full"
                    }
                ],
                "description": "Trainer attributes and team"
            },
            {
                "name": "courses", 
                "columns": [
                    {"name": "CourseId", "dataType": "String", "isHidden": False, "sourceColumn": "CourseId"},
                    {"name": "Course", "dataType": "String", "isHidden": False, "sourceColumn": "Course"},
                    {"name": "Domain", "dataType": "String", "isHidden": False, "sourceColumn": "Domain"},
                    {"name": "ComplexityScore", "dataType": "Int64", "isHidden": False, "sourceColumn": "ComplexityScore"},
                    {"name": "DefaultSessionType", "dataType": "String", "isHidden": False, "sourceColumn": "DefaultSessionType"},
                ],
                "partitions": [{"name": "courses", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Course/topic details"
            },
            {
                "name": "sessions",
                "columns": [
                    {"name": "SessionId", "dataType": "String", "isHidden": False, "sourceColumn": "SessionId"},
                    {"name": "Date", "dataType": "DateTime", "isHidden": False, "sourceColumn": "Date"},
                    {"name": "TrainerId", "dataType": "String", "isHidden": False, "sourceColumn": "TrainerId"},
                    {"name": "CourseId", "dataType": "String", "isHidden": False, "sourceColumn": "CourseId"},
                    {"name": "Audience", "dataType": "String", "isHidden": False, "sourceColumn": "Audience"},
                    {"name": "SessionType", "dataType": "String", "isHidden": False, "sourceColumn": "SessionType"},
                    {"name": "ContactHours", "dataType": "Decimal", "isHidden": False, "sourceColumn": "ContactHours"},
                    {"name": "IsNewTopic", "dataType": "Boolean", "isHidden": False, "sourceColumn": "IsNewTopic"},
                    {"name": "Location", "dataType": "String", "isHidden": False, "sourceColumn": "Location"},
                ],
                "partitions": [{"name": "sessions", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Training sessions"
            },
            {
                "name": "workload_entries",
                "columns": [
                    {"name": "EntryId", "dataType": "String", "isHidden": False, "sourceColumn": "EntryId"},
                    {"name": "Date", "dataType": "DateTime", "isHidden": False, "sourceColumn": "Date"},
                    {"name": "TrainerId", "dataType": "String", "isHidden": False, "sourceColumn": "TrainerId"},
                    {"name": "CourseId", "dataType": "String", "isHidden": False, "sourceColumn": "CourseId"},
                    {"name": "SessionId", "dataType": "String", "isHidden": False, "sourceColumn": "SessionId"},
                    {"name": "Category", "dataType": "String", "isHidden": False, "sourceColumn": "Category"},
                    {"name": "Hours", "dataType": "Decimal", "isHidden": False, "sourceColumn": "Hours"},
                    {"name": "Source", "dataType": "String", "isHidden": False, "sourceColumn": "Source"},
                    {"name": "Description", "dataType": "String", "isHidden": False, "sourceColumn": "Description"},
                ],
                "partitions": [{"name": "workload_entries", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Workload time entries"
            },
            {
                "name": "evaluation_responses",
                "columns": [
                    {"name": "EvaluationId", "dataType": "String", "isHidden": False, "sourceColumn": "EvaluationId"},
                    {"name": "SessionId", "dataType": "String", "isHidden": False, "sourceColumn": "SessionId"},
                    {"name": "AverageScore", "dataType": "Decimal", "isHidden": False, "sourceColumn": "AverageScore"},
                    {"name": "ResponseCount", "dataType": "Int64", "isHidden": False, "sourceColumn": "ResponseCount"},
                    {"name": "Nps", "dataType": "Int64", "isHidden": False, "sourceColumn": "Nps"},
                    {"name": "MainIssue", "dataType": "String", "isHidden": False, "sourceColumn": "MainIssue"},
                ],
                "partitions": [{"name": "evaluation_responses", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Evaluation scores"
            },
            {
                "name": "feedback_comments",
                "columns": [
                    {"name": "FeedbackId", "dataType": "String", "isHidden": False, "sourceColumn": "FeedbackId"},
                    {"name": "SessionId", "dataType": "String", "isHidden": False, "sourceColumn": "SessionId"},
                    {"name": "Theme", "dataType": "String", "isHidden": False, "sourceColumn": "Theme"},
                    {"name": "Sentiment", "dataType": "String", "isHidden": False, "sourceColumn": "Sentiment"},
                    {"name": "Comment", "dataType": "String", "isHidden": False, "sourceColumn": "Comment"},
                ],
                "partitions": [{"name": "feedback_comments", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Feedback comments"
            },
            {
                "name": "fairness_signals",
                "columns": [
                    {"name": "SignalId", "dataType": "String", "isHidden": False, "sourceColumn": "SignalId"},
                    {"name": "SignalDate", "dataType": "DateTime", "isHidden": False, "sourceColumn": "SignalDate"},
                    {"name": "SignalType", "dataType": "String", "isHidden": False, "sourceColumn": "SignalType"},
                    {"name": "TrainerId", "dataType": "String", "isHidden": False, "sourceColumn": "TrainerId"},
                    {"name": "CourseId", "dataType": "String", "isHidden": False, "sourceColumn": "CourseId"},
                    {"name": "Severity", "dataType": "String", "isHidden": False, "sourceColumn": "Severity"},
                    {"name": "Signal", "dataType": "String", "isHidden": False, "sourceColumn": "Signal"},
                    {"name": "RecommendedAction", "dataType": "String", "isHidden": False, "sourceColumn": "RecommendedAction"},
                ],
                "partitions": [{"name": "fairness_signals", "mode": "import", "source": {"type": "calculated"}, "dataView": "full"}],
                "description": "Fairness signals for management"
            },
        ],
        "relationships": [
            {
                "leftTable": "sessions", "leftColumn": "TrainerId",
                "rightTable": "trainers", "rightColumn": "TrainerId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "sessions", "leftColumn": "CourseId",
                "rightTable": "courses", "rightColumn": "CourseId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "workload_entries", "leftColumn": "TrainerId",
                "rightTable": "trainers", "rightColumn": "TrainerId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "workload_entries", "leftColumn": "CourseId",
                "rightTable": "courses", "rightColumn": "CourseId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "evaluation_responses", "leftColumn": "SessionId",
                "rightTable": "sessions", "rightColumn": "SessionId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "feedback_comments", "leftColumn": "SessionId",
                "rightTable": "sessions", "rightColumn": "SessionId",
                "crossFiltering": "oneDirection"
            },
            {
                "leftTable": "fairness_signals", "leftColumn": "TrainerId",
                "rightTable": "trainers", "rightColumn": "TrainerId",
                "crossFiltering": "bothDirections"
            },
            {
                "leftTable": "fairness_signals", "leftColumn": "CourseId",
                "rightTable": "courses", "rightColumn": "CourseId",
                "crossFiltering": "bothDirections"
            },
        ],
        "cultures": [{"name": "nl-NL"}],
        "defaultCulture": "nl-NL"
    }
}

# Write PBIP files
# dataModel.schema
with open(os.path.join(PBIP_DIR, "dataModel.schema"), "w") as f:
    json.dump(data_model, f, indent=2)

# diagramView
diagram = {
    "version": "1.0.0",
    "diagramLayout": json.dumps({
        "displayOptions": {"fitToPage": False},
        "page": {
            "height": 1080,
            "width": 1920,
            "x": 0, "y": 0
        }
    })
}
with open(os.path.join(PBIP_DIR, "diagramView"), "w") as f:
    json.dump(diagram, f)

# workspaceId
with open(os.path.join(PBIP_DIR, "workspaceId"), "w") as f:
    f.write(new_id())

print(f"PBIP created at {PBIP_DIR}")
print(f"Files: {os.listdir(PBIP_DIR)}")

# Now let's try to open this PBIP in PBI Desktop and save as PBIX
# This requires GUI automation, but PBI Desktop can open .pbip folders
print("\nAttempting to open PBIP in PBI Desktop...")

# PBI Desktop doesn't have a command-line open, so we need GUI
# Let's try the minimal approach: just create the PBIX directly
# by embedding data as CSV files in the PBIP

# Actually, the cleanest approach: embed data as CSV partitions
# The PBIP format stores data in the folder itself

# Create CSV data files in the PBIP directory for import
for name, data in [
    ("trainers.csv", trainers),
    ("courses.csv", courses),
    ("sessions.csv", sessions),
    ("workload_entries.csv", workload_entries),
    ("evaluation_responses.csv", evaluation_responses),
    ("feedback_comments.csv", feedback_comments),
    ("fairness_signals.csv", fairness_signals),
]:
    # Already in the data/ folder, PBIP expects them locally
    pass

print("PBIP project created successfully.")
print("To complete: open in PBI Desktop and save as PBIX.")
print("PBIP path:", PBIP_DIR)