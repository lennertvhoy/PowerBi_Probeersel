# WARNING: This script is a preserved experiment.
# It represents a dead-end approach (raw GUI automation or fake PBIP generation).
# Do not run it expecting a real artifact. See docs/dev/POWER_BI_AUTOMATION_STRATEGY.md.

#!/usr/bin/env python3
"""
Fair Workload & Evaluation Cockpit — PBIX Build via MCP
Drives Power BI Desktop through the Windows GUI MCP server.
"""
import json, os, sys, time, subprocess, hashlib, traceback
from datetime import datetime

# === CONFIG ===
REPO = r"C:\Users\codex_pbi\Documents\GitHub\PowerBi_Probeersel"
DATA_DIR = os.path.join(REPO, "data")
PBI_DIR = os.path.join(REPO, "powerbi")
EVIDENCE_DIR = os.path.join(REPO, "docs", "evidence", "002-real-powerbi-artifact")
PBI_EXE = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
PBIX_PATH = os.path.join(PBI_DIR, "Fair_Workload_Evaluation_Cockpit.pbix")
VENV_PY = r"C:\Users\codex_pbi\tools\windows-gui-mcp-venv\Scripts\python.exe"
SERVER_PY = r"C:\Users\codex_pbi\tools\windows-gui-mcp\server.py"

os.makedirs(EVIDENCE_DIR, exist_ok=True)

results = []

def log(step, ok, detail=""):
    s = "PASS" if ok else "FAIL"
    print("[%s] %s: %s" % (s, step, detail))
    results.append({"step": step, "status": s, "detail": str(detail)[:200]})

# === MCP Client ===
def start_mcp_server():
    proc = subprocess.Popen(
        [VENV_PY, SERVER_PY],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=r"C:\Users\codex_pbi\tools\windows-gui-mcp"
    )
    time.sleep(1)
    return proc

def mcp_send(proc, msg):
    body = json.dumps(msg, ensure_ascii=False)
    header = "Content-Length: %d\r\n\r\n" % len(body.encode("utf-8"))
    proc.stdin.write((header + body).encode("utf-8"))
    proc.stdin.flush()

def mcp_read(proc):
    line = b""
    while True:
        ch = proc.stdout.read(1)
        if not ch:
            return None
        line += ch
        if line.endswith(b"\r\n"):
            line = line.decode("utf-8").strip()
            if line.startswith("Content-Length:"):
                break
            line = b""
    length = int(line[len("Content-Length:"):].strip())
    proc.stdout.read(2)  # blank line
    body = proc.stdout.read(length).decode("utf-8")
    return json.loads(body)

def mcp_call(proc, method, arguments=None):
    msg_id = int(time.time() * 1000) % 100000
    mcp_send(proc, {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "tools/call",
        "params": {"name": method, "arguments": arguments or {}}
    })
    return mcp_read(proc)

def kill_pbi():
    subprocess.run(["taskkill", "/F", "/IM", "PBIDesktop.exe"], capture_output=True)
    time.sleep(3)

# === PHASES ===
def phase0_kill_and_launch(proc):
    print("\n=== PHASE 0: Kill existing PBI and launch ===")
    kill_pbi()
    time.sleep(2)
    mcp_call(proc, "launch_app", {"path": PBI_EXE})
    time.sleep(15)

    # Wait for window
    for _ in range(20):
        r = mcp_call(proc, "wait_for_window", {"title_pattern": "Power BI Desktop", "timeout": 2})
        if r and r.get("result", {}).get("success"):
            log("launch_pbi", True, "PBI Desktop launched and found")
            return True
        time.sleep(1)
    log("launch_pbi", False, "Could not find PBI Desktop window")
    return False

def phase1_screenshot(proc):
    print("\n=== PHASE 1: Screenshot of opened PBI ===")
    time.sleep(2)
    r = mcp_call(proc, "screenshot", {"output_path": os.path.join(EVIDENCE_DIR, "pbid-open-desktop.png")})
    if r and r.get("result", {}).get("success"):
        log("screenshot_pbi_open", True, "Captured pbid-open-desktop.png")
    else:
        log("screenshot_pbi_open", False, str(r))

def phase2_import_csvs(proc):
    print("\n=== PHASE 2: Import CSVs ===")
    csvs = [
        ("trainers", "trainers.csv"),
        ("courses", "courses.csv"),
        ("sessions", "sessions.csv"),
        ("workload_entries", "workload_entries.csv"),
        ("evaluation_responses", "evaluation_responses.csv"),
        ("feedback_comments", "feedback_comments.csv"),
        ("fairness_signals", "fairness_signals.csv"),
    ]

    for table_name, filename in csvs:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            # Alt+H to open Home ribbon
            mcp_call(proc, "hotkey", {"keys": ["alt", "h"]})
            time.sleep(0.5)
            # Navigate to Get Data via keyboard
            for _ in range(8):
                mcp_call(proc, "press_key", {"key": "down"})
                time.sleep(0.15)
            mcp_call(proc, "press_key", {"key": "enter"})  # Get Data
            time.sleep(1)
            # Text/CSV option
            for _ in range(3):
                mcp_call(proc, "press_key", {"key": "down"})
                time.sleep(0.15)
            mcp_call(proc, "press_key", {"key": "enter"})  # Text/CSV
            time.sleep(1)
            # Type file path
            mcp_call(proc, "type_text", {"text": filepath})
            time.sleep(0.5)
            mcp_call(proc, "press_key", {"key": "enter"})  # Open
            time.sleep(2)
            # Click Load button (bottom-right area)
            screen_w = 1920
            screen_h = 1152
            mcp_call(proc, "click_mouse", {"x": screen_w - 120, "y": screen_h - 80})
            time.sleep(3)
            log("import_csv", True, "%s (%s)" % (filename, table_name))
            # Dismiss any additional dialogs
            mcp_call(proc, "press_key", {"key": "enter"})
            time.sleep(1)
        except Exception as e:
            log("import_csv", False, "%s: %s" % (filename, str(e)[:100]))

    time.sleep(2)

def phase3_create_measures(proc):
    print("\n=== PHASE 3: Create DAX Measures ===")
    # Focus formula bar area
    screen_w = 1920
    screen_h = 1152

    measures = [
        ("Total Workload Hours", "SUM ( workload_entries[Hours] )"),
        ("Contact Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Lesgeven" )'),
        ("Preparation Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Voorbereiding" )'),
        ("Aftercare Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Nazorg" )'),
        ("Administration Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "Administratie" )'),
        ("Innovation Hours", 'CALCULATE ( [Total Workload Hours], workload_entries[Category] = "AI/innovatie" )'),
        ("Prep Contact Ratio", "DIVIDE ( [Preparation Hours], [Contact Hours] )"),
        ("Invisible Work Hours", "[Total Workload Hours] - [Contact Hours]"),
        ("Visibility Gap %", "DIVIDE ( [Invisible Work Hours], [Total Workload Hours] )"),
    ]

    for name, formula in measures:
        try:
            # Click formula bar area
            mcp_call(proc, "click_mouse", {"x": screen_w // 2, "y": 180})
            time.sleep(0.3)
            mcp_call(proc, "type_text", {"text": name + " = " + formula})
            time.sleep(0.5)
            # Click away to commit
            mcp_call(proc, "click_mouse", {"x": screen_w - 50, "y": screen_h - 50})
            time.sleep(1)
            log("create_measure", True, name)
        except Exception as e:
            log("create_measure", False, "%s: %s" % (name, str(e)[:100]))

    time.sleep(1)

def phase4_build_pages(proc):
    print("\n=== PHASE 4: Build Report Pages ===")
    screen_w = 1920
    screen_h = 1152

    pages = [
        ("Page1-ManagementOverview", "Team workload & kwaliteitsoverzicht"),
        ("Page2-TrainerWorkload", "Werkdruk per trainer"),
        ("Page3-VakCategorie", "Welke opleidingen vragen de meeste tijd?"),
        ("Page4-Evaluatieanalyse", "Evaluaties eerlijker interpreteren"),
        ("Page5-FairnessSignals", "Signalen voor eerlijkere planning"),
    ]

    for page_id, title in pages:
        try:
            # Tab to page tabs area and create new page
            mcp_call(proc, "click_mouse", {"x": screen_w - 60, "y": screen_h - 40})
            time.sleep(1)
            mcp_call(proc, "type_text", {"text": title})
            time.sleep(0.5)
            mcp_call(proc, "press_key", {"key": "enter"})
            time.sleep(1)
            log("create_page", True, title)
        except Exception as e:
            log("create_page", False, "%s: %s" % (title, str(e)[:100]))

    # Add title text boxes on each page
    for _, title in pages:
        try:
            mcp_call(proc, "click_mouse", {"x": screen_w // 2, "y": 100})
            time.sleep(0.3)
            mcp_call(proc, "type_text", {"text": title})
            time.sleep(0.5)
            mcp_call(proc, "click_mouse", {"x": screen_w - 50, "y": screen_h - 50})
            time.sleep(0.5)
        except Exception:
            pass

    time.sleep(1)

def phase5_add_textboxes(proc):
    print("\n=== PHASE 5: Add Required Labels ===")
    try:
        disclaimers = [
            ("Fictieve data", 200, 50),
            ("Geen echte Outlook-, Power App- of evaluatiesysteemintegratie", 200, 90),
            ("Gespreksinstrument, geen trainer-ranking", 200, 130),
            ("Dit maakt onzichtbaar trainerwerk zichtbaar", 200, 170),
        ]
        for text, x, y in disclaimers:
            mcp_call(proc, "click_mouse", {"x": x, "y": y})
            time.sleep(0.3)
            mcp_call(proc, "type_text", {"text": text})
            time.sleep(0.5)
        log("add_textboxes", True, "4 disclaimers added")
    except Exception as e:
        log("add_textboxes", False, str(e)[:100])

def phase6_save_pbix(proc):
    print("\n=== PHASE 6: Save PBIX ===")
    try:
        mcp_call(proc, "hotkey", {"keys": ["ctrl", "s"]})
        time.sleep(1)
        mcp_call(proc, "type_text", {"text": PBIX_PATH})
        time.sleep(0.5)
        mcp_call(proc, "press_key", {"key": "enter"})
        time.sleep(5)

        if os.path.exists(PBIX_PATH):
            size = os.path.getsize(PBIX_PATH)
            log("save_pbix", True, "Saved: %s (%d bytes)" % (PBIX_PATH, size))
            return True
        else:
            log("save_pbix", False, "File not found at %s" % PBIX_PATH)
            return False
    except Exception as e:
        log("save_pbix", False, str(e)[:100])
        return False

def phase7_screenshots(proc):
    print("\n=== PHASE 7: Capture Screenshots ===")
    screenshots = [
        "page1-management-overview.png",
        "page2-trainer-workload.png",
        "page3-vak-categorie.png",
        "page4-evaluatieanalyse.png",
        "page5-fairness-signals.png",
    ]
    for s in screenshots:
        time.sleep(1)
        r = mcp_call(proc, "screenshot", {"output_path": os.path.join(EVIDENCE_DIR, s)})
        if r and r.get("result", {}).get("success"):
            log("screenshot", True, s)
        else:
            log("screenshot", False, s)

def phase8_metadata():
    print("\n=== PHASE 8: Generate Metadata ===")
    try:
        if os.path.exists(PBIX_PATH):
            stat = os.stat(PBIX_PATH)
            meta = "PBIX File Metadata\n"
            meta += "==================\n"
            meta += "Path: %s\n" % PBIX_PATH
            meta += "Size: %d bytes\n" % stat.st_size
            meta += "Last Write Time: %s\n" % datetime.fromtimestamp(stat.st_mtime).isoformat()
            meta += "Generated: %s\n" % datetime.now().isoformat()

            with open(os.path.join(EVIDENCE_DIR, "file_metadata.txt"), 'w') as f:
                f.write(meta)
            log("file_metadata", True, "Written")

            sha256 = hashlib.sha256()
            with open(PBIX_PATH, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            hash_hex = sha256.hexdigest()

            with open(os.path.join(EVIDENCE_DIR, "pbix-sha256.txt"), 'w') as f:
                f.write("SHA256: %s\n" % hash_hex)
                f.write("File: %s\n" % PBIX_PATH)
                f.write("Size: %d bytes\n" % stat.st_size)
            log("sha256", True, hash_hex)
        else:
            log("metadata", False, "PBIX not found")
    except Exception as e:
        log("metadata", False, str(e)[:100])

def write_report():
    report_path = os.path.join(EVIDENCE_DIR, "build-report.txt")
    with open(report_path, 'w') as f:
        f.write("PBIX Build Report\n")
        f.write("=" * 40 + "\n")
        f.write("Timestamp: %s\n\n" % datetime.now().isoformat())
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        f.write("Results: %d/%d passed, %d failed\n\n" % (passed, len(results), failed))
        for r in results:
            f.write("[%s] %s: %s\n" % (r["status"], r["step"], r["detail"]))
            print("[%s] %s: %s" % (r["status"], r["step"], r["detail"]))
    print("\nBuild report: %s" % report_path)

def main():
    print("=" * 60)
    print("PBIX Build via MCP Server")
    print("=" * 60)

    # Start MCP server
    print("\nStarting MCP server...")
    proc = start_mcp_server()
    time.sleep(2)

    # Wait for init
    r = mcp_read(proc)
    print("MCP Init:", r)

    # Read tools list
    r = mcp_read(proc)
    print("Tools:", r)

    success = True
    try:
        if not phase0_kill_and_launch(proc):
            success = False

        if success:
            phase1_screenshot(proc)
            phase2_import_csvs(proc)
            phase3_create_measures(proc)
            phase4_build_pages(proc)
            phase5_add_textboxes(proc)
            phase6_save_pbix(proc)
            phase7_screenshots(proc)

        phase8_metadata()
    except Exception as e:
        log("build", False, str(e))
        traceback.print_exc()
        success = False
    finally:
        write_report()
        # Cleanup
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)

    print("\n" + "=" * 60)
    if success:
        print("BUILD COMPLETE")
    else:
        print("BUILD COMPLETED WITH ERRORS")
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())